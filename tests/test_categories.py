from unittest.mock import patch


from wcr_data_extraction import fetcher  # noqa: E402


def test_load_categories_logs_warning(tmp_path, caplog):
    bad_file = tmp_path / "cats.json"
    bad_file.write_text("{bad}")
    with patch.object(fetcher, "logger") as mock_logger:
        fetcher.configure_structlog("WARNING")
        cats = fetcher.load_categories(bad_file)
        mock_logger.warning.assert_called()
        assert "Could not read categories" in mock_logger.warning.call_args[0][0]
    assert cats["faction"] == {}


def test_load_categories_logs_unreadable(tmp_path, caplog):
    bad_file = tmp_path / "cats.json"
    bad_file.write_text("{}")
    with patch("builtins.open", side_effect=OSError("fail")):
        with patch.object(fetcher, "logger") as mock_logger:
            fetcher.configure_structlog("WARNING")
            cats = fetcher.load_categories(bad_file)
            mock_logger.warning.assert_called()
            assert "Could not read categories" in mock_logger.warning.call_args[0][0]
    assert cats["trait"] == {}
