import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))

import scripts.fetch_method as fetch_method  # noqa: E402


def test_parse_args_defaults(tmp_path):
    with patch.object(fetch_method, "OUT_PATH", tmp_path / "units.json"), patch.object(
        fetch_method, "CATEGORIES_PATH", tmp_path / "categories.json"
    ):
        args = fetch_method.parse_args([])
        assert Path(args.output) == tmp_path / "units.json"
        assert Path(args.categories) == tmp_path / "categories.json"
        assert args.timeout == 10


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
    with patch.object(fetch_method, "fetch_units") as mock_fetch:
        fetch_method.main(args)
        mock_fetch.assert_called_once_with(
            out_path=Path(args[1]),
            categories_path=Path(args[3]),
            timeout=7,
        )
