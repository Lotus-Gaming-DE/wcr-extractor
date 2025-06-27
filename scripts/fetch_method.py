"""Wrapper for the ``wcr_data_extraction`` CLI.

This script provides a stable entry point for fetching unit and category data.
All command line arguments are passed directly to :mod:`wcr_data_extraction.cli`.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction import cli  # noqa: E402
from wcr_data_extraction import fetcher  # noqa: E402
from wcr_data_extraction.fetcher import (  # noqa: E402
    fetch_units,
    fetch_categories,
    configure_structlog,
    FetchError,
    logger,
)

DEFAULT_UNITS_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "export" / "units.json"
)
DEFAULT_CATEGORIES_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "export" / "categories.json"
)


def _load_json(path: Path) -> object | None:
    """Return JSON data from ``path`` if it exists."""

    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return None


def _dump_sorted(data: object) -> str:
    return json.dumps(data, sort_keys=True, ensure_ascii=False)


def main(argv: List[str] | None = None) -> None:
    """Execute the extractor CLI.

    Parameters are forwarded directly to :mod:`wcr_data_extraction.cli`. Use
    ``--help`` to see available options.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", action="store_true", help="Show help message")
    args, rest = parser.parse_known_args(argv)
    if args.help:
        cli.main(["--help"])
        return

    cli.OUT_PATH = DEFAULT_UNITS_PATH
    cli.CATEGORIES_PATH = DEFAULT_CATEGORIES_PATH
    fetcher.OUT_PATH = DEFAULT_UNITS_PATH
    fetcher.CATEGORIES_PATH = DEFAULT_CATEGORIES_PATH
    parsed = cli.parse_args(rest)
    configure_structlog(parsed.log_level, Path(parsed.log_file))
    logger.info("Starting fetch")

    cats_path = Path(parsed.categories)
    units_path = Path(parsed.output)

    cats_tmp = cats_path.with_suffix(".tmp")
    try:
        fetch_categories(
            out_path=cats_tmp,
            timeout=parsed.timeout,
            existing_path=cats_path,
            units_path=units_path,
        )
        new_cats = _load_json(cats_tmp) or {}
        logger.info("%s category items fetched", sum(len(v) for v in new_cats.values()))
    except FetchError as exc:
        logger.warning("Fetching categories failed: %s", exc)
        cats_tmp.unlink(missing_ok=True)
        return

    existing_cats = _load_json(cats_path) or {}
    if _dump_sorted(existing_cats) == _dump_sorted(new_cats):
        logger.info("No changes detected for categories")
        cats_tmp.unlink(missing_ok=True)
    else:
        cats_tmp.replace(cats_path)
        logger.info("Categories updated at %s", cats_path)

    units_tmp = units_path.with_suffix(".tmp")
    try:
        fetch_units(
            out_path=units_tmp,
            categories_path=cats_path,
            timeout=parsed.timeout,
            max_workers=parsed.workers,
            existing_path=units_path,
        )
        new_units = _load_json(units_tmp) or []
        logger.info("%s units fetched", len(new_units))
    except FetchError as exc:
        logger.warning("Fetching units failed: %s", exc)
        units_tmp.unlink(missing_ok=True)
        return

    existing_units = _load_json(units_path) or []
    if _dump_sorted(existing_units) == _dump_sorted(new_units):
        logger.info("No changes detected for units")
        units_tmp.unlink(missing_ok=True)
    else:
        units_tmp.replace(units_path)
        logger.info("Units updated at %s", units_path)

    cats_tmp = cats_path.with_suffix(".tmp")
    try:
        fetch_categories(
            out_path=cats_tmp,
            timeout=parsed.timeout,
            existing_path=cats_path,
            units_path=units_path,
        )
        new_cats = _load_json(cats_tmp) or {}
        logger.info("%s category items fetched", sum(len(v) for v in new_cats.values()))
    except FetchError as exc:
        logger.warning("Fetching categories failed: %s", exc)
        cats_tmp.unlink(missing_ok=True)
        return

    existing_cats = _load_json(cats_path) or {}
    if _dump_sorted(existing_cats) == _dump_sorted(new_cats):
        logger.info("No changes detected for categories")
        cats_tmp.unlink(missing_ok=True)
    else:
        cats_tmp.replace(cats_path)
        logger.info("Categories updated at %s", cats_path)


if __name__ == "__main__":
    main()
