import json
import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts import fetch_method


def test_fetch_units_writes_json(tmp_path):
    html = """
        <div class="mini-wrapper" data-name="Footman" data-family="Alliance" data-type="Troop" data-cost="2" data-damage="10" data-health="20" data-dps="5" data-speed="Slow" data-traits="Melee,One-Target">
            <a class="mini-link" href="/warcraft-rumble/minis/footman">
                <img src="footman.png" />
            </a>
        </div>
    """
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

    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
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
        with patch.object(fetch_method, "OUT_PATH", out_file), \
             patch.object(fetch_method, "CATEGORIES_PATH", cat_file), \
             patch.object(fetch_method, "fetch_unit_details", return_value=dummy_details):
            fetch_method.fetch_units()
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data == [{
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
    }]


def test_fetch_units_preserves_translations(tmp_path):
    html = """
        <div class=\"mini-wrapper\" data-name=\"Footman\" data-family=\"Alliance\" data-type=\"Troop\" data-cost=\"2\" data-damage=\"10\" data-health=\"20\" data-dps=\"5\" data-speed=\"Slow\" data-traits=\"Melee,One-Target\">
            <a class=\"mini-link\" href=\"/warcraft-rumble/minis/footman\">
                <img src=\"footman.png\" />
            </a>
        </div>
    """
    mock_response = Mock(status_code=200, text=html)

    categories = {
        "factions": [{"id": "alliance", "names": {"en": "Alliance"}}],
        "types": [{"id": "troop", "names": {"en": "Troop"}}],
        "traits": [],
        "speeds": [{"id": "slow", "names": {"en": "Slow"}}],
    }

    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
        out_file = tmp_path / "units.json"
        cat_file = tmp_path / "categories.json"
        cat_file.write_text(json.dumps(categories))
        existing = [{
            "id": "footman",
            "names": {"en": "Old", "de": "Fußmann"},
        }]
        out_file.write_text(json.dumps(existing))
        dummy_details = {"core_trait": {}, "stats": {}, "traits": [], "talents": [], "advanced_info": "info"}
        with patch.object(fetch_method, "OUT_PATH", out_file), \
             patch.object(fetch_method, "CATEGORIES_PATH", cat_file), \
             patch.object(fetch_method, "fetch_unit_details", return_value=dummy_details):
            fetch_method.fetch_units()
            data = json.loads(out_file.read_text(encoding="utf-8"))

    assert data[0]["names"] == {"en": "Footman", "de": "Fußmann"}


@pytest.mark.parametrize("speed_value", ["", "Znull"])
def test_fetch_units_handles_missing_speed_id(tmp_path, speed_value):
    html = f"""
        <div class=\"mini-wrapper\" data-name=\"Spell\" data-family=\"Beast\" data-type=\"Spell\" data-cost=\"1\" data-damage=\"0\" data-health=\"0\" data-dps=\"0\" data-speed=\"{speed_value}\" data-traits=\"\">
            <a class=\"mini-link\" href=\"/warcraft-rumble/minis/spell\"></a>
        </div>
    """
    mock_response = Mock(status_code=200, text=html)
    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
        out_file = tmp_path / "units.json"
        dummy_details = {"core_trait": {}, "stats": {}, "traits": [], "talents": [], "advanced_info": "info"}
        with patch.object(fetch_method, "OUT_PATH", out_file), \
             patch.object(fetch_method, "fetch_unit_details", return_value=dummy_details):
            fetch_method.fetch_units()
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data[0]["speed_id"] is None


@pytest.mark.parametrize("speed_value", ["", "Znull"])
def test_speed_id_is_none_when_speed_empty_or_znull(tmp_path, speed_value):
    """Ensure speed_id is None when the speed attribute is empty or 'Znull'."""
    html = f"""
        <div class=\"mini-wrapper\" data-name=\"Spell\" data-family=\"Beast\" da
ta-type=\"Spell\" data-cost=\"1\" data-damage=\"0\" data-health=\"0\" data-dps=\"0\" data-speed=\"{speed_value}\" data-traits=\"\">
            <a class=\"mini-link\" href=\"/warcraft-rumble/minis/spell\"></a>
        </div>
    """
    mock_response = Mock(status_code=200, text=html)
    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
        out_file = tmp_path / "units.json"
        dummy_details = {"core_trait": {}, "stats": {}, "traits": [], "talents": [], "advanced_info": "info"}
        with patch.object(fetch_method, "OUT_PATH", out_file), \
             patch.object(fetch_method, "fetch_unit_details", return_value=dummy_details):
            fetch_method.fetch_units()
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

    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
        details = fetch_method.fetch_unit_details("url")

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

    with patch("scripts.fetch_method.requests.get", return_value=mock_response), \
         patch(
             "scripts.fetch_method.load_categories",
             return_value={
                 "faction": {},
                 "type": {},
                 "trait": {"Tank": "tank"},
                 "speed": {},
                 "trait_desc": {"tank": "desc"},
             },
         ):
        details = fetch_method.fetch_unit_details("url")

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

    with patch("scripts.fetch_method.requests.get", return_value=mock_response), \
         patch(
             "scripts.fetch_method.load_categories",
             return_value={
                 "faction": {},
                 "type": {},
                 "trait": {"AoE": "aoe", "Melee": "melee"},
                 "speed": {},
                 "trait_desc": {},
             },
         ):
        details = fetch_method.fetch_unit_details("url")

    assert details["core_trait"] == {"attack_id": "aoe", "type_id": "melee"}
