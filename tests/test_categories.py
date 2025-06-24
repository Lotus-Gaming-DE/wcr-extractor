from pathlib import Path
from unittest.mock import patch

import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from wcr_data_extraction import fetcher  # noqa: E402


def test_load_categories_logs_warning(tmp_path, caplog):
    bad_file = tmp_path / "cats.json"
    bad_file.write_text("{bad}")
    fetcher.configure_structlog("WARNING")
    with caplog.at_level("WARNING"):
        cats = fetcher.load_categories(bad_file)
    assert "Could not read categories" in caplog.text
    assert cats["faction"] == {}


def test_load_categories_logs_unreadable(tmp_path, caplog):
    bad_file = tmp_path / "cats.json"
    bad_file.write_text("{}")
    with patch("builtins.open", side_effect=OSError("fail")):
        fetcher.configure_structlog("WARNING")
        with caplog.at_level("WARNING"):
            cats = fetcher.load_categories(bad_file)
    assert "Could not read categories" in caplog.text
    assert cats["trait"] == {}
