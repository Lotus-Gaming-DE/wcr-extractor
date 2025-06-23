import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts import fetch_method


def test_is_unit_changed_identical():
    unit = {
        "names": {"en": "Footman"},
        "faction_ids": ["alliance"],
        "type_id": "troop",
        "cost": 2,
        "image": "footman.png",
        "damage": 10,
        "health": 20,
        "dps": 5.0,
        "speed_id": "slow",
        "trait_ids": ["melee"],
        "details": {},
    }
    assert fetch_method.is_unit_changed(unit, unit.copy()) is False


def test_is_unit_changed_field_differs():
    old = {
        "names": {"en": "Footman"},
        "faction_ids": ["alliance"],
        "type_id": "troop",
        "cost": 2,
        "image": "footman.png",
        "damage": 10,
        "health": 20,
        "dps": 5.0,
        "speed_id": "slow",
        "trait_ids": ["melee"],
        "details": {},
    }
    new = old.copy()
    new["cost"] = 3
    assert fetch_method.is_unit_changed(old, new) is True


def test_is_unit_changed_translation_changed():
    old = {
        "names": {"en": "Footman", "de": "Fu\u00dfmann"},
        "faction_ids": ["alliance"],
        "type_id": "troop",
        "cost": 2,
        "image": "footman.png",
        "damage": 10,
        "health": 20,
        "dps": 5.0,
        "speed_id": "slow",
        "trait_ids": ["melee"],
        "details": {},
    }
    new = {
        **old,
        "names": {"en": "Footman", "fr": "Fantassin"},
    }
    assert fetch_method.is_unit_changed(old, new) is False
