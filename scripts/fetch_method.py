"""Wrapper for the ``wcr_data_extraction`` CLI.

This script provides a stable entry point for fetching unit data. All command
line arguments are passed directly to :mod:`wcr_data_extraction.cli`.
"""

import argparse
from pathlib import Path
import sys
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction import cli  # noqa: E402


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
    else:
        cli.main(rest)


if __name__ == "__main__":
    main()
