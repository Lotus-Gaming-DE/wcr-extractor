from pathlib import Path
from unittest.mock import patch

from wcr_data_extraction import fetcher  # noqa: E402


def _setup_logging(tmp_path, monkeypatch):
    (tmp_path / "dummy").mkdir()
    monkeypatch.setattr(Path, "resolve", lambda self: tmp_path / "dummy" / "fetcher.py")
    fetcher.configure_logging("WARNING")
    log_path = tmp_path / "logs" / "app.log"
    return log_path


def test_load_categories_logs_warning(tmp_path, monkeypatch):
    bad_file = tmp_path / "cats.json"
    bad_file.write_text("{bad}")
    log_file = _setup_logging(tmp_path, monkeypatch)
    cats = fetcher.load_categories(bad_file)
    for h in fetcher.logging.getLogger().handlers:
        h.flush()
    assert log_file.exists()
    assert cats["faction"] == {}


def test_load_categories_logs_unreadable(tmp_path, monkeypatch):
    bad_file = tmp_path / "cats.json"
    bad_file.write_text("{}")
    log_file = _setup_logging(tmp_path, monkeypatch)
    with patch("builtins.open", side_effect=OSError("fail")):
        cats = fetcher.load_categories(bad_file)
    for h in fetcher.logging.getLogger().handlers:
        h.flush()
    assert log_file.exists()
    assert cats["trait"] == {}
