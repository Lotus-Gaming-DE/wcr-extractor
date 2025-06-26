"""Wrapper for the ``wcr_data_extraction`` CLI.

This script provides a stable entry point for fetching unit data. All command
line arguments are passed directly to :mod:`wcr_data_extraction.cli`.
"""

from pathlib import Path
import sys
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction import cli  # noqa: E402


def main(argv: List[str] | None = None) -> None:
    """Execute the CLI with the given arguments."""
    cli.main(argv)


if __name__ == "__main__":
    main()
