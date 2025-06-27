"""Wrapper for the ``wcr_data_extraction`` CLI.

This script provides a stable entry point for fetching unit and category data.
All command line arguments are passed directly to :mod:`wcr_data_extraction.cli`.
"""

import argparse
from pathlib import Path
import sys
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction import cli  # noqa: E402
from wcr_data_extraction.fetcher import (  # noqa: E402
    fetch_units,
    fetch_categories,
    configure_structlog,
    FetchError,
    logger,
)


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

    parsed = cli.parse_args(rest)
    configure_structlog(parsed.log_level, Path(parsed.log_file))
    try:
        logger.info("Starting fetch")
        fetch_categories(out_path=Path(parsed.categories), timeout=parsed.timeout)
        fetch_units(
            out_path=Path(parsed.output),
            categories_path=Path(parsed.categories),
            timeout=parsed.timeout,
            max_workers=parsed.workers,
        )
    except FetchError as exc:
        logger.error("Fehler beim Abrufen: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
