import structlog
from wcr_data_extraction import fetcher


def test_configure_structlog_json(tmp_path):
    log_file = tmp_path / "wcr.log"
    fetcher.configure_structlog("INFO", log_file)
    logger = structlog.get_logger("test")
    logger.info("hello", foo="bar")
    contents = log_file.read_text()
    assert '"event": "hello"' in contents
    assert '"foo": "bar"' in contents


def test_configure_structlog_file(tmp_path):
    log_file = tmp_path / "wcr.log"
    fetcher.configure_structlog("INFO", log_file)
    logger = structlog.get_logger("file")
    logger.info("msg", num=1)
    contents = log_file.read_text()
    assert '"event": "msg"' in contents
    assert '"num": 1' in contents
