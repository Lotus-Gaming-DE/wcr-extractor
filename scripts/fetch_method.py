"""Fetch minis and categories from method.gg.

This script downloads unit and category data from the Method.gg website and
stores the JSON results under ``tmp_data``. Existing files are only replaced if
new data differs from the current content. This prevents overwriting manually
translated information.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction.fetcher import (  # noqa: E402
    FetchError,
    configure_structlog,
    fetch_categories,
    fetch_units,
    logger,
)


UNITS_FILE = Path("tmp_data/units.json")
CATEGORIES_FILE = Path("tmp_data/categories.json")
LOG_FILE = Path(f"logs/runtime-{datetime.now():%Y-%m-%d-%H}.json")


def _load_json(path: Path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _has_changed(tmp: Path, dest: Path) -> bool:
    if not dest.exists():
        return True
    try:
        new = json.dumps(_load_json(tmp), sort_keys=True, ensure_ascii=False)
        old = json.dumps(_load_json(dest), sort_keys=True, ensure_ascii=False)
        return new != old
    except Exception as exc:  # pragma: no cover - should not happen
        logger.warning("Comparison failed for %s and %s: %s", tmp, dest, exc)
        return True


def _finalize(tmp: Path, dest: Path, label: str) -> None:
    if _has_changed(tmp, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp.replace(dest)
        logger.info("Updated %s", dest)
    else:
        logger.info("No changes detected for %s", dest.name)
        tmp.unlink()


def main(argv: List[str] | None = None) -> None:
    """Fetch minis and categories from Method.gg."""

    parser = argparse.ArgumentParser(description="Fetch data from Method.gg")
    parser.parse_args(argv)

    configure_structlog("INFO", LOG_FILE)
    logger.info("Starting fetch")

    tmp_dir = Path("tmp_data")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_categories = tmp_dir / "categories.tmp"
    tmp_units = tmp_dir / "units.tmp"

    try:
        fetch_categories(out_path=tmp_categories, timeout=10)
        cats = _load_json(tmp_categories)
        total_cats = sum(len(v) for v in cats.values())
        logger.info("Fetched %s category items", total_cats)
        _finalize(tmp_categories, CATEGORIES_FILE, "categories")
    except FetchError as exc:
        logger.warning("Failed to fetch categories: %s", exc)
        if tmp_categories.exists():
            tmp_categories.unlink()
        return

    try:
        fetch_units(
            out_path=tmp_units,
            categories_path=CATEGORIES_FILE,
            timeout=10,
            max_workers=1,
        )
        units = _load_json(tmp_units)
        logger.info("Fetched %s units", len(units))
        _finalize(tmp_units, UNITS_FILE, "units")
    except FetchError as exc:
        logger.warning("Failed to fetch units: %s", exc)
        if tmp_units.exists():
            tmp_units.unlink()


if __name__ == "__main__":
    main()
