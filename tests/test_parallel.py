from unittest.mock import patch, Mock

from wcr_data_extraction import fetcher  # noqa: E402


def test_fetch_units_uses_max_workers(tmp_path):
    html = "<div class='mini-wrapper'></div>"
    mock_response = Mock(status_code=200, text=html)

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session), patch(
        "concurrent.futures.ThreadPoolExecutor"
    ) as executor_mock, patch.object(fetcher, "OUT_PATH", tmp_path / "u.json"):
        executor = executor_mock.return_value.__enter__.return_value
        executor.map.return_value = []
        fetcher.fetch_units(max_workers=5, session=mock_session)
        executor_mock.assert_called_once_with(max_workers=5)
        mock_session.get.assert_called_once_with(
            fetcher.BASE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
