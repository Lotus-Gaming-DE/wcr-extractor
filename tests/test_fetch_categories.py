import json
from unittest.mock import Mock, patch

import requests

import pytest

from wcr_data_extraction import fetcher


def make_html():
    return """
    <div class='mini-wrapper' data-family='Alliance' data-speed='Slow'></div>
    <div class='mini-wrapper' data-family='Alliance,Undead' data-speed='Fast'></div>
    <div class='filter__type'>
        <input data-for='type' data-value='Leader'/>
        <input data-for='type' data-value='Spell'/>
    </div>
    <div class='filter__trait'>
        <input data-for='traits' data-value='Ambush'/>
        <input data-for='traits' data-value='AoE'/>
    </div>
    """


def test_fetch_categories_writes_json(tmp_path):
    html = make_html()
    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "cats.json"
        with patch.object(fetcher, "CATEGORIES_PATH", out_file):
            fetcher.fetch_categories(session=mock_session)
    data = json.loads(out_file.read_text())
    faction_ids = {f["id"] for f in data["factions"]}
    assert "alliance" in faction_ids
    assert "alliance-undead" in faction_ids
    type_ids = {t["id"] for t in data["types"]}
    assert type_ids == {"leader", "spell"}
    trait_ids = {t["id"] for t in data["traits"]}
    assert trait_ids == {"ambush", "aoe"}
    speed_ids = {s["id"] for s in data["speeds"]}
    assert speed_ids == {"slow", "fast"}


def test_fetch_categories_preserves_translations(tmp_path):
    html = make_html()
    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    existing = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance", "de": "Allianz"}}],
        "types": [],
        "traits": [],
        "speeds": [],
    }
    out_file = tmp_path / "cats.json"
    out_file.write_text(json.dumps(existing))
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(fetcher, "CATEGORIES_PATH", out_file):
            fetcher.fetch_categories(session=mock_session)
    data = json.loads(out_file.read_text())
    alliance = next(x for x in data["factions"] if x["id"] == "alliance")
    assert alliance["names"]["de"] == "Allianz"


def test_fetch_categories_request_exception(tmp_path):
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("boom")
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(fetcher, "CATEGORIES_PATH", tmp_path / "c.json"):
            with pytest.raises(fetcher.FetchError):
                fetcher.fetch_categories(session=mock_session)


def test_fetch_categories_http_error(tmp_path):
    mock_response = Mock(status_code=500, text="")
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(fetcher, "CATEGORIES_PATH", tmp_path / "c.json"):
            with pytest.raises(fetcher.FetchError):
                fetcher.fetch_categories(session=mock_session)


def test_fetch_categories_skips_when_unchanged(tmp_path):
    html = make_html()
    expected = {
        "factions": [
            {"id": "alliance", "names": {"en": "Alliance"}},
            {"id": "alliance-undead", "names": {"en": "Alliance & Undead"}},
        ],
        "types": [
            {"id": "leader", "names": {"en": "Leader"}},
            {"id": "spell", "names": {"en": "Spell"}},
        ],
        "traits": [
            {"id": "ambush", "names": {"en": "Ambush"}},
            {"id": "aoe", "names": {"en": "AoE"}},
        ],
        "speeds": [
            {"id": "fast", "names": {"en": "Fast"}},
            {"id": "slow", "names": {"en": "Slow"}},
        ],
    }
    out_file = tmp_path / "cats.json"
    out_file.write_text(json.dumps(expected))
    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(fetcher, "CATEGORIES_PATH", out_file):
            with patch("wcr_data_extraction.fetcher.json.dump") as dump_mock:
                fetcher.fetch_categories(session=mock_session)
                dump_mock.assert_not_called()
