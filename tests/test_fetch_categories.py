import json
from unittest.mock import Mock, patch

import requests
import pytest

from wcr_data_extraction import fetcher


def make_html() -> str:
    return """
    <div class='mini-wrapper' data-family='Alliance' data-speed='Slow'></div>
    <div class='mini-wrapper' data-family='Alliance,Undead' data-speed='Fast'></div>
    """


def make_units() -> list[dict]:
    return [
        {
            "id": "leader-unit",
            "names": {"en": "Leader Unit"},
            "faction_ids": ["alliance"],
            "type_id": "leader",
            "speed_id": "slow",
            "trait_ids": ["ambush"],
            "details": {},
        },
        {
            "id": "spell-unit",
            "names": {"en": "Spell Unit"},
            "faction_ids": ["alliance", "undead"],
            "type_id": "spell",
            "speed_id": "fast",
            "trait_ids": ["aoe"],
            "details": {},
        },
    ]


def test_fetch_categories_writes_json(tmp_path):
    html = make_html()
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(make_units()))

    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "cats.json"
        with patch.object(fetcher, "CATEGORIES_PATH", out_file), patch.object(
            fetcher,
            "OUT_PATH",
            units_path,
        ):
            fetcher.fetch_categories(session=mock_session)
    data = json.loads(out_file.read_text())
    faction_ids = {f["id"] for f in data["factions"]}
    assert {"alliance", "alliance-undead"} <= faction_ids
    type_ids = {t["id"] for t in data["types"]}
    assert type_ids == {"leader", "spell"}
    trait_ids = {t["id"] for t in data["traits"]}
    assert trait_ids == {"ambush", "aoe"}
    speed_ids = {s["id"] for s in data["speeds"]}
    assert {"slow", "fast"} <= speed_ids


def test_fetch_categories_preserves_translations(tmp_path):
    html = make_html()
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(make_units()))

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
        with patch.object(fetcher, "CATEGORIES_PATH", out_file), patch.object(
            fetcher,
            "OUT_PATH",
            units_path,
        ):
            fetcher.fetch_categories(session=mock_session)
    data = json.loads(out_file.read_text())
    alliance = next(x for x in data["factions"] if x["id"] == "alliance")
    assert alliance["names"]["de"] == "Allianz"


def test_fetch_categories_request_exception(tmp_path):
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("boom")
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(
            fetcher, "CATEGORIES_PATH", tmp_path / "c.json"
        ), patch.object(
            fetcher,
            "OUT_PATH",
            tmp_path / "units.json",
        ):
            with pytest.raises(fetcher.FetchError):
                fetcher.fetch_categories(session=mock_session)


def test_fetch_categories_http_error(tmp_path):
    mock_response = Mock(status_code=500, text="")
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with patch.object(
            fetcher, "CATEGORIES_PATH", tmp_path / "c.json"
        ), patch.object(
            fetcher,
            "OUT_PATH",
            tmp_path / "units.json",
        ):
            with pytest.raises(fetcher.FetchError):
                fetcher.fetch_categories(session=mock_session)


def test_fetch_categories_uses_trait_descriptions(tmp_path):
    html = make_html()
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(make_units()))

    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "cats.json"
        with patch.object(fetcher, "CATEGORIES_PATH", out_file), patch.object(
            fetcher,
            "OUT_PATH",
            units_path,
        ):
            fetcher.fetch_categories(
                session=mock_session, trait_desc_map={"ambush": "Ambush foes"}
            )
    data = json.loads(out_file.read_text())
    trait = next(t for t in data["traits"] if t["id"] == "ambush")
    assert trait["descriptions"]["en"] == "Ambush foes"


def test_fetch_categories_prefers_non_null_descriptions(tmp_path):
    html = make_html()
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(make_units()))

    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "cats.json"
        with patch.object(fetcher, "CATEGORIES_PATH", out_file), patch.object(
            fetcher,
            "OUT_PATH",
            units_path,
        ):
            fetcher.fetch_categories(
                session=mock_session, trait_desc_map={"ambush": "Ambush foes"}
            )
    data = json.loads(out_file.read_text())
    trait = next(t for t in data["traits"] if t["id"] == "ambush")
    assert trait["descriptions"]["en"] == "Ambush foes"
