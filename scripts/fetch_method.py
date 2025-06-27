"""Fetch Warcraft Rumble data from method.gg.

This script downloads unit and category information and stores the results in
``tmp_data/units.json`` and ``tmp_data/categories.json``. Existing files are only
replaced when the downloaded content differs so that manual translations are
preserved.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from bs4 import BeautifulSoup
import requests

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction.fetcher import (  # noqa: E402
    BASE_URL,
    FetchError,
    fetch_units,
    configure_structlog,
    create_session,
    logger,
)


TMP_DIR = Path("tmp_data")
UNITS_PATH = TMP_DIR / "units.json"
CATEGORIES_PATH = TMP_DIR / "categories.json"


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return None


def scrape_categories(existing: dict | None, *, timeout: int = 10) -> dict:
    """Return category data from Method.gg preserving translations."""
    sess = create_session()
    try:
        logger.info("Fetching categories from %s", BASE_URL)
        try:
            response = sess.get(
                BASE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout
            )
        except requests.RequestException as exc:  # pragma: no cover - network
            raise FetchError(f"Error fetching {BASE_URL}: {exc}") from exc
        if response.status_code != 200:
            raise FetchError(
                f"Error fetching {BASE_URL}: Status {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")
        minis = soup.select("div.mini-wrapper")
        factions_raw: set[str] = set()
        speeds_raw: set[str] = set()
        for mini in minis:
            fam = mini.get("data-family")
            if fam:
                factions_raw.add(fam.strip())
            spd = mini.get("data-speed")
            if spd and spd not in ("", "Znull"):
                speeds_raw.add(spd.strip())

        types_raw = {
            inp.get("data-value", "").strip()
            for inp in soup.select(".filter__type input[data-for='type']")
            if inp.get("data-value")
        }
        traits_raw = {
            inp.get("data-value", "").strip()
            for inp in soup.select(".filter__trait input[data-for='traits']")
            if inp.get("data-value")
        }

        existing = existing or {}

        def build_items(name: str, values: set[str]) -> list[dict]:
            items: list[dict] = []
            existing_map = {item.get("id"): item for item in existing.get(name, [])}
            for val in sorted(values):
                parts = [p.strip() for p in val.split(",")]
                cat_id = "-".join(p.lower() for p in parts)
                en_name = " & ".join(parts)
                item = existing_map.get(cat_id, {"id": cat_id, "names": {}})
                names = item.get("names", {})
                names["en"] = en_name
                item["names"] = names
                items.append(item)
            return items

        data = {
            "factions": build_items("factions", factions_raw),
            "types": build_items("types", types_raw),
            "traits": build_items("traits", traits_raw),
            "speeds": build_items("speeds", speeds_raw),
        }
        total = sum(len(v) for v in data.values())
        logger.info("%s category items found", total)
        return data
    finally:
        sess.close()


def dump_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def save_if_changed(new_data: Any, path: Path, description: str) -> None:
    old = load_json(path)
    if json.dumps(old, sort_keys=True, ensure_ascii=False) == json.dumps(
        new_data, sort_keys=True, ensure_ascii=False
    ):
        logger.info("No changes detected for %s", description)
        return
    dump_json(new_data, path)
    logger.info("Updated %s", description)


def fetch_and_save(timeout: int = 10, workers: int = 4) -> None:
    logger.info("Starting fetch")
    existing_categories = load_json(CATEGORIES_PATH) or {}
    categories = scrape_categories(existing_categories, timeout=timeout)
    save_if_changed(categories, CATEGORIES_PATH, "categories")

    tmp_units = UNITS_PATH.with_suffix(".new")
    fetch_units(
        out_path=tmp_units,
        categories_path=CATEGORIES_PATH,
        timeout=timeout,
        max_workers=workers,
    )
    new_units = load_json(tmp_units) or []
    save_if_changed(new_units, UNITS_PATH, "units")
    tmp_units.unlink(missing_ok=True)
    logger.info("%s units processed", len(new_units))


def main(argv: list[str] | None = None) -> None:
    """Fetch and save units and categories from method.gg."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout")
    parser.add_argument(
        "--workers", type=int, default=4, help="Parallel workers for unit details"
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument(
        "--log-file",
        default=str(Path("logs") / "runtime.log"),
        help="Path to the log file",
    )
    args = parser.parse_args(argv)

    configure_structlog(args.log_level, Path(args.log_file))
    try:
        fetch_and_save(timeout=args.timeout, workers=args.workers)
    except FetchError as exc:
        logger.error("Fehler beim Abrufen: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
