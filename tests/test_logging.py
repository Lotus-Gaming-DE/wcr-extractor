from pathlib import Path

from wcr_data_extraction.fetcher import configure_logging, logger


def test_configure_logging_creates_log_file(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    monkeypatch.chdir(tmp_path)
    # patch module path to use tmp location
    (tmp_path / "dummy").mkdir()
    monkeypatch.setattr(Path, "resolve", lambda self: tmp_path / "dummy" / "fetcher.py")
    configure_logging("INFO")
    log_file = log_dir / "app.log"
    logger.info("test")
    import logging

    for h in logging.getLogger().handlers:
        h.flush()
    assert log_file.exists()
