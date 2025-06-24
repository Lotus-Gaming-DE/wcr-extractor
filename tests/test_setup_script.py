from pathlib import Path


def test_setup_script_has_dev_flag():
    content = Path("setup.sh").read_text()
    assert "--dev" in content
