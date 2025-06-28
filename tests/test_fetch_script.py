import sys
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts import fetch_method  # noqa: E402


def test_script_invokes_fetchers(tmp_path):
    args = Namespace(
        output=str(tmp_path / "u.json"),
        categories=str(tmp_path / "c.json"),
        timeout=5,
        workers=2,
        log_level="INFO",
        log_file=str(tmp_path / "log.json"),
    )
    with patch.object(fetch_method.cli, "parse_args", return_value=args):
        with patch.object(fetch_method, "configure_structlog") as conf, patch.object(
            fetch_method, "fetch_categories"
        ) as fc, patch.object(fetch_method, "fetch_units") as fu:
            fu.return_value = {"ambush": "desc"}
            fetch_method.main([])
            conf.assert_called_once_with("INFO", Path(args.log_file))
            unit_tmp = Path(args.output).with_suffix(".tmp")
            fu.assert_called_once_with(
                out_path=unit_tmp,
                categories_path=Path(args.categories),
                timeout=5,
                max_workers=2,
                existing_path=Path(args.output),
            )
            cat_tmp = Path(args.categories).with_suffix(".tmp")
            fc.assert_called_once_with(
                out_path=cat_tmp,
                timeout=5,
                existing_path=Path(args.categories),
                units_path=Path(args.output),
                trait_desc_map=fu.return_value,
            )


def test_no_overwrite_when_unchanged(tmp_path):
    units_file = tmp_path / "units.json"
    cats_file = tmp_path / "cats.json"
    units_file.write_text("[]")
    cats_file.write_text("{}")

    args = Namespace(
        output=str(units_file),
        categories=str(cats_file),
        timeout=5,
        workers=1,
        log_level="INFO",
        log_file=str(tmp_path / "log.json"),
    )

    def write_same(out_path, **_):
        Path(out_path).write_text(
            units_file.read_text() if "unit" in str(out_path) else cats_file.read_text()
        )

    with patch.object(fetch_method.cli, "parse_args", return_value=args):
        with patch.object(fetch_method, "configure_structlog"), patch.object(
            fetch_method,
            "fetch_categories",
            side_effect=write_same,
        ), patch.object(
            fetch_method,
            "fetch_units",
            side_effect=lambda *a, **k: (write_same(*a, **k) or {}),
        ):
            fetch_method.main([])
            # temp files removed
            assert units_file.read_text() == "[]"
            assert cats_file.read_text() == "{}"
