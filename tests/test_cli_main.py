import runpy
from unittest.mock import patch

import pytest


@pytest.mark.usefixtures("tmp_path")
def test_cli_entrypoint_invokes_main(tmp_path):
    with patch("wcr_data_extraction.fetcher.fetch_units") as mock_fetch, patch(
        "wcr_data_extraction.fetcher.configure_logging"
    ) as mock_conf, patch("sys.argv", ["wcr_data_extraction.cli"]):
        runpy.run_module("wcr_data_extraction.cli", run_name="__main__")
        mock_conf.assert_called_once()
        mock_fetch.assert_called_once()
