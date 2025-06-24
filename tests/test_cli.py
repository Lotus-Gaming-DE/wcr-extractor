import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

from wcr_data_extraction import cli  # noqa: E402


def test_parse_args_defaults(tmp_path):
    with patch.object(cli, "OUT_PATH", tmp_path / "units.json"), patch.object(
        cli, "CATEGORIES_PATH", tmp_path / "categories.json"
    ):
        args = cli.parse_args([])
        assert Path(args.output) == tmp_path / "units.json"
        assert Path(args.categories) == tmp_path / "categories.json"
        assert args.timeout == 10
        assert args.workers == 1


def test_main_invokes_fetch_units(tmp_path):
    args = [
        "--output",
        str(tmp_path / "u.json"),
        "--categories",
        str(tmp_path / "c.json"),
        "--timeout",
        "7",
        "--log-level",
        "DEBUG",
    ]
    with patch.object(cli, "fetch_units") as mock_fetch:
        cli.main(args)
        mock_fetch.assert_called_once_with(
            out_path=Path(args[1]),
            categories_path=Path(args[3]),
            timeout=7,
            max_workers=1,
        )
