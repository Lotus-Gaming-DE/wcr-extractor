import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
import requests


from wcr_data_extraction import fetcher  # noqa: E402


def test_fetch_units_writes_json(tmp_path):
    html = (
        "<div class='mini-wrapper' data-name='Footman' data-family='Alliance' "
        "data-type='Troop' data-cost='2' data-damage='10' data-health='20' "
        "data-dps='5' data-speed='Slow' data-traits='Melee,One-Target'>"
        "<a class='mini-link' href='/warcraft-rumble/minis/footman'>"
        "<img src='footman.png' />"
        "</a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)

    categories = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance"}}],
        "types": [{"id": "troop", "names": {"en": "Troop"}}],
        "traits": [
            {
                "id": "melee",
                "names": {"en": "Melee"},
                "descriptions": {"en": "Attacks enemies at close range."},
            },
            {
                "id": "one-target",
                "names": {"en": "One-Target"},
                "descriptions": {"en": "Attacks a single enemy at a time."},
            },
        ],
        "speeds": [{"id": "slow", "names": {"en": "Slow"}}],
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        cat_file = tmp_path / "categories.json"
        cat_file.write_text(json.dumps(categories))
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
            "army_bonus_slots": ["Cycle"],
        }
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "CATEGORIES_PATH", cat_file
        ), patch.object(fetcher, "fetch_unit_details", return_value=dummy_details):
            fetcher.fetch_units(session=mock_session)
            mock_session.get.assert_called_once_with(
                fetcher.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data == [
        {
            "id": "footman",
            "names": {"en": "Footman"},
            "faction_ids": ["alliance"],
            "type_id": "troop",
            "cost": 2,
            "image": "footman.png",
            "damage": 10,
            "health": 20,
            "dps": 5.0,
            "speed_id": "slow",
            "trait_ids": ["melee", "one-target"],
            "details": dummy_details,
        }
    ]


def test_fetch_units_preserves_translations(tmp_path):
    html = (
        "<div class='mini-wrapper' data-name='Footman' data-family='Alliance' "
        "data-type='Troop' data-cost='2' data-damage='10' data-health='20' "
        "data-dps='5' data-speed='Slow' data-traits='Melee,One-Target'>"
        "<a class='mini-link' href='/warcraft-rumble/minis/footman'>"
        "<img src='footman.png' />"
        "</a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)

    categories = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance"}}],
        "types": [{"id": "troop", "names": {"en": "Troop"}}],
        "traits": [],
        "speeds": [{"id": "slow", "names": {"en": "Slow"}}],
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        cat_file = tmp_path / "categories.json"
        cat_file.write_text(json.dumps(categories))
        existing = [
            {
                "id": "footman",
                "names": {"en": "Old", "de": "Fußmann"},
            }
        ]
        out_file.write_text(json.dumps(existing))
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
        }
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "CATEGORIES_PATH", cat_file
        ), patch.object(fetcher, "fetch_unit_details", return_value=dummy_details):
            fetcher.fetch_units(session=mock_session)
            mock_session.get.assert_called_once_with(
                fetcher.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            data = json.loads(out_file.read_text(encoding="utf-8"))

    assert data[0]["names"] == {"en": "Footman", "de": "Fußmann"}


def test_fetch_units_skips_unchanged_unit(tmp_path):
    html = (
        "<div class='mini-wrapper' data-name='Footman' data-family='Alliance' "
        "data-type='Troop' data-cost='2' data-damage='10' data-health='20' "
        "data-dps='5' data-speed='Slow' data-traits='Melee'>"
        "<a class='mini-link' href='/warcraft-rumble/minis/footman'>"
        "<img src='footman.png' />"
        "</a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)

    categories = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance"}}],
        "types": [{"id": "troop", "names": {"en": "Troop"}}],
        "traits": [{"id": "melee", "names": {"en": "Melee"}}],
        "speeds": [{"id": "slow", "names": {"en": "Slow"}}],
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        cat_file = tmp_path / "categories.json"
        cat_file.write_text(json.dumps(categories))
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
        }
        existing = [
            {
                "id": "footman",
                "names": {"en": "Footman", "de": "Fußmann"},
                "faction_ids": ["alliance"],
                "type_id": "troop",
                "cost": 2,
                "image": "footman.png",
                "damage": 10,
                "health": 20,
                "dps": 5.0,
                "speed_id": "slow",
                "trait_ids": ["melee"],
                "details": dummy_details,
            }
        ]
        out_file.write_text(json.dumps(existing))
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "CATEGORIES_PATH", cat_file
        ), patch.object(fetcher, "fetch_unit_details", return_value=dummy_details):
            fetcher.fetch_units(session=mock_session)
            mock_session.get.assert_called_once_with(
                fetcher.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            data = json.loads(out_file.read_text(encoding="utf-8"))

    assert data == existing


def test_fetch_units_skips_write_when_identical(tmp_path):
    html = (
        "<div class='mini-wrapper' data-name='Footman' data-family='Alliance' "
        "data-type='Troop' data-cost='2' data-damage='10' data-health='20' "
        "data-dps='5' data-speed='Slow' data-traits='Melee'>"
        "<a class='mini-link' href='/warcraft-rumble/minis/footman'>"
        "<img src='footman.png' />"
        "</a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)

    categories = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance"}}],
        "types": [{"id": "troop", "names": {"en": "Troop"}}],
        "traits": [{"id": "melee", "names": {"en": "Melee"}}],
        "speeds": [{"id": "slow", "names": {"en": "Slow"}}],
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        cat_file = tmp_path / "categories.json"
        cat_file.write_text(json.dumps(categories))
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
        }
        existing = [
            {
                "id": "footman",
                "names": {"en": "Footman", "de": "Fußmann"},
                "faction_ids": ["alliance"],
                "type_id": "troop",
                "cost": 2,
                "image": "footman.png",
                "damage": 10,
                "health": 20,
                "dps": 5.0,
                "speed_id": "slow",
                "trait_ids": ["melee"],
                "details": dummy_details,
            }
        ]
        out_file.write_text(json.dumps(existing))
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "CATEGORIES_PATH", cat_file
        ), patch.object(
            fetcher, "fetch_unit_details", return_value=dummy_details
        ), patch(
            "wcr_data_extraction.fetcher.json.dump"
        ) as dump_mock:
            fetcher.fetch_units(session=mock_session)
            dump_mock.assert_not_called()


def test_fetch_units_updates_changed_unit(tmp_path):
    html = (
        "<div class='mini-wrapper' data-name='Footman' data-family='Alliance' "
        "data-type='Troop' data-cost='3' data-damage='10' data-health='20' "
        "data-dps='5' data-speed='Slow' data-traits='Melee'>"
        "<a class='mini-link' href='/warcraft-rumble/minis/footman'>"
        "<img src='footman.png' />"
        "</a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)

    categories = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance"}}],
        "types": [{"id": "troop", "names": {"en": "Troop"}}],
        "traits": [{"id": "melee", "names": {"en": "Melee"}}],
        "speeds": [{"id": "slow", "names": {"en": "Slow"}}],
    }

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        cat_file = tmp_path / "categories.json"
        cat_file.write_text(json.dumps(categories))
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
        }
        existing = [
            {
                "id": "footman",
                "names": {"en": "Footman", "de": "Fußmann"},
                "faction_ids": ["alliance"],
                "type_id": "troop",
                "cost": 2,
                "image": "footman.png",
                "damage": 10,
                "health": 20,
                "dps": 5.0,
                "speed_id": "slow",
                "trait_ids": ["melee"],
                "details": dummy_details,
            }
        ]
        out_file.write_text(json.dumps(existing))
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "CATEGORIES_PATH", cat_file
        ), patch.object(fetcher, "fetch_unit_details", return_value=dummy_details):
            fetcher.fetch_units(session=mock_session)
            mock_session.get.assert_called_once_with(
                fetcher.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            data = json.loads(out_file.read_text(encoding="utf-8"))

    assert data[0]["cost"] == 3
    assert data[0]["names"]["de"] == "Fußmann"


@pytest.mark.parametrize("speed_value", ["", "Znull", fetcher.STATIONARY])
def test_fetch_units_handles_missing_speed_id(tmp_path, speed_value):
    html = (
        f"<div class='mini-wrapper' data-name='Spell' data-family='Beast' "
        f"data-type='Spell' data-cost='1' data-damage='0' data-health='0' "
        f"data-dps='0' data-speed='{speed_value}' data-traits=''>"
        "<a class='mini-link' href='/warcraft-rumble/minis/spell'></a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
        }
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "fetch_unit_details", return_value=dummy_details
        ):
            fetcher.fetch_units(session=mock_session)
            mock_session.get.assert_called_once_with(
                fetcher.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data[0]["speed_id"] is None
    if speed_value == fetcher.STATIONARY:
        assert data[0]["speed"] is None


@pytest.mark.parametrize("speed_value", ["", "Znull", fetcher.STATIONARY])
def test_speed_id_is_none_when_speed_empty_or_znull(tmp_path, speed_value):
    """Ensure speed_id is None when the speed attribute is empty, 'Znull' or
    'Stationary'."""
    html = (
        f"<div class='mini-wrapper' data-name='Spell' data-family='Beast' "
        f"data-type='Spell' data-cost='1' data-damage='0' data-health='0' "
        f"data-dps='0' data-speed='{speed_value}' data-traits=''>"
        "<a class='mini-link' href='/warcraft-rumble/minis/spell'></a>"
        "</div>"
    )
    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        dummy_details = {
            "core_trait": {},
            "stats": {},
            "traits": [],
            "talents": [],
            "advanced_info": "info",
        }
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "fetch_unit_details", return_value=dummy_details
        ):
            fetcher.fetch_units(session=mock_session)
            mock_session.get.assert_called_once_with(
                fetcher.BASE_URL,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data[0]["speed_id"] is None


def test_fetch_unit_details_army_bonus_slots_removed():
    html = """
        <div class=\"mini-section\">
            <h2>Advanced Mini Information</h2>
            <div class=\"mini-content\">
                <p>Available army bonus slots for the bottom row</p>
                <p>Cycle</p>
                <p>Tank</p>
                <p>Without a Wildcard slot, Cairne cannot buff</p>
                <p>Shockwave applies a 1-second Stun</p>
            </div>
        </div>
    """

    mock_response = Mock(status_code=200, text=html)

    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        cats = fetcher.load_categories()
        details = fetcher.fetch_unit_details(
            "https://example.com/unit", cats, session=mock_session
        )
        mock_session.get.assert_called_once_with(
            "https://example.com/unit",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )

    assert details["army_bonus_slots"] == ["Cycle", "Tank"]
    assert details["advanced_info"] == (
        "Without a Wildcard slot, Cairne cannot buff\nShockwave applies a 1-second Stun"
    )
    assert "Available army bonus slots" not in details["advanced_info"]


def test_fetch_unit_details_returns_trait_ids():
    html = """
        <div class=\"mini-section\">
            <h2>Traits</h2>
            <div class=\"mini-trait-tile\">
                <div class=\"detail-info\">Tank</div>
                <div class=\"mini-talent__description\">High health unit.</div>
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
            "trait": {"Tank": "tank"},
            "speed": {},
            "trait_desc": {"tank": "desc"},
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

    assert details["traits"] == ["tank"]


def test_fetch_unit_details_core_trait_ids():
    html = """
        <div class=\"mini-section\">
            <h2>Mini Information</h2>
            <div class=\"mini-details-tile\">
                <div class=\"detail-label\">Core Trait Attack</div>
                <div class=\"detail-info\">AoE</div>
            </div>
            <div class=\"mini-details-tile\">
                <div class=\"detail-label\">Core Trait Type</div>
                <div class=\"detail-info\">Melee</div>
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
            "trait": {"AoE": "aoe", "Melee": "melee"},
            "speed": {},
            "trait_desc": {},
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

    assert details["core_trait"] == {"attack_id": "aoe", "type_id": "melee"}


def test_fetch_unit_details_request_exception():
    """Die Funktion soll bei Netzwerkfehlern mit Code 1 beenden."""
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("boom")
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with pytest.raises(fetcher.FetchError) as excinfo:
            cats = fetcher.load_categories()
            fetcher.fetch_unit_details(
                "https://example.com/unit", cats, session=mock_session
            )
        mock_session.get.assert_called_once_with(
            "https://example.com/unit",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
    assert "Error fetching" in str(excinfo.value)


def test_fetch_unit_details_http_error():
    """Bei HTTP-Fehlern soll eine FetchError mit Statuscode entstehen."""
    mock_response = Mock(status_code=404, text="not found")
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        with pytest.raises(fetcher.FetchError) as excinfo:
            cats = fetcher.load_categories()
            fetcher.fetch_unit_details(
                "https://example.com/unit", cats, session=mock_session
            )
        mock_session.get.assert_called_once_with(
            "https://example.com/unit",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
    assert "Status 404" in str(excinfo.value)


def test_fetch_units_request_exception(tmp_path):
    """Die Funktion soll bei Netzwerkfehlern mit Code 1 beenden."""
    mock_session = Mock()
    mock_session.get.side_effect = requests.RequestException("boom")
    with patch.object(
        fetcher, "create_session", return_value=mock_session
    ), patch.object(fetcher, "OUT_PATH", tmp_path / "units.json"):
        with pytest.raises(fetcher.FetchError) as excinfo:
            fetcher.fetch_units(session=mock_session)
        mock_session.get.assert_called_once_with(
            fetcher.BASE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
    assert "Error fetching" in str(excinfo.value)


def test_fetch_units_http_error(tmp_path):
    """Die Funktion soll bei HTTP-Fehlern eine FetchError werfen."""
    mock_response = Mock(status_code=500, text="")
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(
        fetcher, "create_session", return_value=mock_session
    ), patch.object(fetcher, "OUT_PATH", tmp_path / "units.json"):
        with pytest.raises(fetcher.FetchError) as excinfo:
            fetcher.fetch_units(session=mock_session)
        mock_session.get.assert_called_once_with(
            fetcher.BASE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
    assert "Status 500" in str(excinfo.value)


def test_session_retry_adapter():
    assert fetcher.adapter.max_retries.total == 3


def test_fetch_units_atomic_write(tmp_path):
    html = "<div class='mini-wrapper'></div>"
    mock_response = Mock(status_code=200, text=html)
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    with patch.object(fetcher, "create_session", return_value=mock_session):
        out_file = tmp_path / "units.json"
        out_file.write_text("old")
        with patch.object(fetcher, "OUT_PATH", out_file), patch.object(
            fetcher, "fetch_unit_details", return_value={}
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
        ):
            with patch("json.dump", side_effect=ValueError("boom")):
                with pytest.raises(ValueError):
                    fetcher.fetch_units(session=mock_session)
        assert out_file.read_text() == "old"
