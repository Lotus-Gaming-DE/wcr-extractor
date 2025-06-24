import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import structlog  # noqa: E402
from wcr_data_extraction import fetcher  # noqa: E402


def test_configure_structlog_json(caplog):
    fetcher.configure_structlog("INFO")
    logger = structlog.get_logger("test")
    with caplog.at_level("INFO"):
        logger.info("hello", foo="bar")
    assert '"event": "hello"' in caplog.text
    assert '"foo": "bar"' in caplog.text
