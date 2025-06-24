from pathlib import Path


def test_setup_script_has_dev_flag():
    content = Path("setup.sh").read_text()
    assert "--dev" in content


def test_fetch_method_script_has_shebang():
    first_line = Path("scripts/fetch_method.py").read_text().splitlines()[0]
    assert first_line.startswith("#!/usr/bin/env python3")
