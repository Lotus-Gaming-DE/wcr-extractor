"""Backwards-compatible wrapper script for the data extraction CLI."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
