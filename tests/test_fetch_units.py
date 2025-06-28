from unittest.mock import Mock, patch

from wcr_data_extraction import fetcher


def test_fetch_unit_details_adds_missing_trait_description():
    html = """
        <div class=\"mini-section\">
            <h2>Traits</h2>
            <div class=\"mini-trait-tile\">
                <div class=\"detail-info\">Brambles</div>
                <div class=\"mini-talent__description\">Root foes for 3s</div>
            </div>
        </div>
    """
    mock_response = Mock(status_code=200, text=html)

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session), patch(
        "wcr_data_extraction.fetcher.load_categories",
        return_value={
            "faction": {},
            "type": {},
            "trait": {"Brambles": "brambles"},
            "speed": {},
            "trait_desc": {"brambles": None},
        },
    ):
        cats = fetcher.load_categories()
        details = fetcher.fetch_unit_details(
            "https://example.com/unit", cats, session=mock_session
        )
        mock_session.get.assert_called_once_with(
            "https://example.com/unit",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )

    assert details["trait_descriptions"] == {"brambles": "Root foes for 3s"}
