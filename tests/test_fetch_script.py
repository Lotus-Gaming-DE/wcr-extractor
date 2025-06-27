from pathlib import Path
from unittest.mock import patch
import json

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts import fetch_method  # noqa: E402


def test_main_invokes_fetch_and_save(tmp_path):
    log_file = tmp_path / "log.json"
    with patch.object(fetch_method, "fetch_and_save") as fas, patch.object(
        fetch_method, "configure_structlog"
    ) as conf:
        fetch_method.main(
            [
                "--timeout",
                "7",
                "--workers",
                "3",
                "--log-level",
                "DEBUG",
                "--log-file",
                str(log_file),
            ]
        )
        conf.assert_called_once_with("DEBUG", log_file)
        fas.assert_called_once_with(timeout=7, workers=3)


def test_save_if_changed(tmp_path):
    path = tmp_path / "data.json"
    data = {"a": 1}
    fetch_method.dump_json(data, path)
    mtime = path.stat().st_mtime
    fetch_method.save_if_changed({"a": 1}, path, "desc")
    assert path.stat().st_mtime == mtime
    fetch_method.save_if_changed({"a": 2}, path, "desc")
    assert json.loads(path.read_text()) == {"a": 2}


def test_fetch_and_save_writes_files(tmp_path):
    cat_path = tmp_path / "categories.json"
    unit_path = tmp_path / "units.json"
    with patch.object(fetch_method, "CATEGORIES_PATH", cat_path), patch.object(
        fetch_method, "UNITS_PATH", unit_path
    ), patch.object(
        fetch_method, "scrape_categories", return_value={"factions": []}
    ) as sc, patch.object(
        fetch_method, "fetch_units"
    ) as fu:

        def fake_fetch_units(out_path, categories_path, timeout, max_workers):
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump([{"id": "a"}], f)

        fu.side_effect = fake_fetch_units
        fetch_method.fetch_and_save(timeout=1, workers=1)
        sc.assert_called_once()
        fu.assert_called_once_with(
            out_path=unit_path.with_suffix(".new"),
            categories_path=cat_path,
            timeout=1,
            max_workers=1,
        )
        assert json.loads(cat_path.read_text()) == {"factions": []}
        assert json.loads(unit_path.read_text())[0]["id"] == "a"
