from unittest.mock import Mock, patch

from wcr_data_extraction import fetcher


def test_fetch_units_closes_created_session(tmp_path):
    mock_session = Mock()
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = "<div></div>"
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(fetcher, "OUT_PATH", tmp_path / "u.json"), patch.object(
            fetcher, "CATEGORIES_PATH", tmp_path / "c.json"
        ), patch.object(
            fetcher,
            "load_categories",
            return_value={
                "faction": {},
                "type": {},
                "trait": {},
                "speed": {},
                "trait_desc": {},
            },
        ), patch.object(
            fetcher, "fetch_unit_details", return_value={}
        ):
            fetcher.fetch_units()
    mock_session.close.assert_called_once()


def test_fetch_categories_closes_created_session(tmp_path):
    mock_session = Mock()
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = "<div></div>"
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(
            fetcher, "CATEGORIES_PATH", tmp_path / "c.json"
        ), patch.object(
            fetcher,
            "OUT_PATH",
            tmp_path / "units.json",
        ):
            fetcher.fetch_categories()
    mock_session.close.assert_called_once()
