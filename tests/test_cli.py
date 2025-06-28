from pathlib import Path
from unittest.mock import patch
import pytest


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
        assert Path(args.log_file).parent == Path("logs")
        assert Path(args.log_file).name.startswith("runtime-")


def test_main_invokes_fetchers(tmp_path):
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
    with patch.object(cli, "configure_structlog") as mock_conf, patch.object(
        cli,
        "fetch_units",
    ) as mock_units, patch.object(cli, "fetch_categories") as mock_cats:
        mock_units.return_value = {"ambush": "desc"}
        cli.main(args)
        called_path = mock_conf.call_args.args[1]
        assert called_path.parent == Path("logs")
        assert called_path.name.startswith("runtime-")
        mock_units.assert_called_once_with(
            out_path=Path(args[1]),
            categories_path=Path(args[3]),
            timeout=7,
            max_workers=1,
        )
        mock_cats.assert_called_once_with(
            out_path=Path(args[3]),
            timeout=7,
            existing_path=Path(args[3]),
            units_path=Path(args[1]),
            trait_desc_map=mock_units.return_value,
        )


def test_parse_args_invalid_timeout():
    with pytest.raises(SystemExit):
        cli.parse_args(["--timeout", "0"])


def test_parse_args_invalid_workers():
    with pytest.raises(SystemExit):
        cli.parse_args(["--workers", "-1"])
