"""Fetch Warcraft Rumble data from method.gg and store it in ``tmp_data/``.

This script downloads unit and category information without requiring any
command-line arguments. Output files are only overwritten when the fetched
content differs from the existing data so that manual translations remain
intact.
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction.fetcher import (  # noqa: E402
    fetch_units,
    fetch_categories,
    configure_structlog,
    FetchError,
    logger,
)


def main() -> None:
    """Fetch minis and categories to ``tmp_data/``."""
    base_dir = Path(__file__).resolve().parents[1]
    out_dir = base_dir / "tmp_data"
    units_path = out_dir / "units.json"
    categories_path = out_dir / "categories.json"

    configure_structlog("INFO")
    logger.info("Starting fetch")

    try:
        cat_data = fetch_categories(out_path=categories_path, timeout=10)
        unit_data = fetch_units(
            out_path=units_path,
            categories_path=categories_path,
            timeout=10,
            max_workers=4,
        )
        logger.info(
            "Fetched %s units and %s category entries",
            len(unit_data),
            sum(len(v) for v in cat_data.values()),
        )
    except FetchError as exc:
        logger.warning("Fetch failed: %s", exc)


if __name__ == "__main__":
    main()
