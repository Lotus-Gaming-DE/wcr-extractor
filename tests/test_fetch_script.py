import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts import fetch_method  # noqa: E402


def test_script_updates_files(tmp_path):
    cats_file = tmp_path / "cats.json"
    units_file = tmp_path / "units.json"

    def fake_fetch_categories(out_path, timeout):
        Path(out_path).write_text(
            json.dumps({"factions": [], "types": [], "traits": [], "speeds": []})
        )

    def fake_fetch_units(out_path, categories_path, timeout, max_workers):
        Path(out_path).write_text(json.dumps([{"id": "foo"}]))

    with patch.object(fetch_method, "CATEGORIES_FILE", cats_file), patch.object(
        fetch_method,
        "UNITS_FILE",
        units_file,
    ), patch.object(fetch_method, "configure_structlog"), patch.object(
        fetch_method,
        "fetch_categories",
        side_effect=fake_fetch_categories,
    ) as fc, patch.object(
        fetch_method,
        "fetch_units",
        side_effect=fake_fetch_units,
    ) as fu:
        fetch_method.main([])

    assert json.loads(cats_file.read_text()) == {
        "factions": [],
        "types": [],
        "traits": [],
        "speeds": [],
    }
    assert json.loads(units_file.read_text()) == [{"id": "foo"}]
    fc.assert_called_once()
    fu.assert_called_once()
    call_kwargs = fu.call_args.kwargs
    assert Path(call_kwargs["out_path"]).name == "units.tmp"
    assert call_kwargs["categories_path"] == cats_file
    assert call_kwargs["timeout"] == 10
    assert call_kwargs["max_workers"] == 1


def test_script_skips_when_no_changes(tmp_path):
    cats_file = tmp_path / "cats.json"
    units_file = tmp_path / "units.json"
    cats_file.write_text(json.dumps({"factions": []}))
    units_file.write_text(json.dumps([]))

    def fake_fetch_categories(out_path, timeout):
        Path(out_path).write_text(cats_file.read_text())

    def fake_fetch_units(out_path, categories_path, timeout, max_workers):
        Path(out_path).write_text(units_file.read_text())

    with patch.object(fetch_method, "CATEGORIES_FILE", cats_file), patch.object(
        fetch_method,
        "UNITS_FILE",
        units_file,
    ), patch.object(fetch_method, "logger") as log, patch.object(
        fetch_method,
        "configure_structlog",
    ), patch.object(
        fetch_method,
        "fetch_categories",
        side_effect=fake_fetch_categories,
    ), patch.object(
        fetch_method,
        "fetch_units",
        side_effect=fake_fetch_units,
    ):
        fetch_method.main([])
        assert log.info.call_args_list[-1].args[0].startswith("No changes detected")
