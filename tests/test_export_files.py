from pathlib import Path
import json


def test_export_files_exist_and_valid():
    for fname in ["units.json", "categories.json"]:
        fpath = Path("data/export") / fname
        assert fpath.exists(), f"{fname} missing"
        content = fpath.read_text().strip()
        assert content.startswith("{") or content.startswith(
            "["
        ), f"{fname} looks invalid"
        json.loads(content)
