import json
import sys
from pathlib import Path
from unittest.mock import patch, Mock

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
    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
        out_file = tmp_path / "units.json"
        dummy_details = {"core_trait": {}, "stats": {}, "traits": [], "talents": [], "advanced_info": "info"}
        with patch.object(fetch_method, "OUT_PATH", out_file), \
             patch.object(fetch_method, "fetch_unit_details", return_value=dummy_details):
            fetch_method.fetch_units()
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data == [{
        "id": "footman",
        "name": "Footman",
        "faction": "Alliance",
        "type": "Troop",
        "cost": 2,
        "image": "footman.png",
        "damage": 10,
        "health": 20,
        "dps": 5.0,
        "speed": "Slow",
        "traits": ["Melee", "One-Target"],
        "details": dummy_details,
    }]
