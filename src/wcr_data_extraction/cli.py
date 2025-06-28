"""Command line interface for the Warcraft Rumble data extractor."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .fetcher import (
    fetch_units,
    fetch_categories,
    OUT_PATH,
    CATEGORIES_PATH,
    FetchError,
    logger,
    configure_structlog,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return parsed CLI arguments."""

    def positive_int(value: str) -> int:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("must be >0")
        return ivalue

    parser = argparse.ArgumentParser(description="Fetch minis from method.gg")
    parser.add_argument(
        "--output", default=str(OUT_PATH), help="Path to write units JSON"
    )
    parser.add_argument(
        "--categories", default=str(CATEGORIES_PATH), help="Path to categories JSON"
    )
    parser.add_argument(
        "--timeout", type=positive_int, default=10, help="HTTP timeout in seconds"
    )
    parser.add_argument(
        "--workers", type=positive_int, default=1, help="Number of parallel workers"
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument(
        "--log-file",
        default=f"logs/runtime-{datetime.now():%Y-%m-%d-%H}.json",
        help="Path to the log file (stored under logs/)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the command line."""

    args = parse_args(argv)
    configure_structlog(args.log_level, Path(args.log_file))
    try:
        trait_descs = fetch_units(
            out_path=Path(args.output),
            categories_path=Path(args.categories),
            timeout=args.timeout,
            max_workers=args.workers,
        )
        fetch_categories(
            out_path=Path(args.categories),
            timeout=args.timeout,
            existing_path=Path(args.categories),
            units_path=Path(args.output),
            trait_desc_map=trait_descs,
        )
    except FetchError as exc:
        logger.error("Fehler beim Abrufen: %s", exc)
        sys.exit(1)
