from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts import fetch_method


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
            fetch_method.main([])
            conf.assert_called_once_with("INFO", Path(args.log_file))
            fc.assert_called_once_with(out_path=Path(args.categories), timeout=5)
            fu.assert_called_once_with(
                out_path=Path(args.output),
                categories_path=Path(args.categories),
                timeout=5,
                max_workers=2,
            )
