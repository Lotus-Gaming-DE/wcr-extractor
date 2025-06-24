"""Command line interface for the Warcraft Rumble data extractor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .fetcher import (
    fetch_units,
    OUT_PATH,
    CATEGORIES_PATH,
    FetchError,
    logger,
    configure_structlog,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""

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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the command line."""

    args = parse_args(argv)
    configure_structlog(args.log_level)
    try:
        fetch_units(
            out_path=Path(args.output),
            categories_path=Path(args.categories),
            timeout=args.timeout,
            max_workers=args.workers,
        )
    except FetchError as exc:
        logger.error("Fehler beim Abrufen: %s", exc)
        sys.exit(1)
