import json
import sys
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts import fetch_method


def test_fetch_units_writes_json(tmp_path):
    html = """
        <div class="mini-wrapper">
          <div class="mini-card">
            <div class="mini-card__name">Footman</div>
            <div class="mini-card__faction">Alliance</div>
            <div class="mini-card__type">Troop</div>
            <div class="mini-card__elixir">2</div>
            <img src="footman.png"/>
          </div>
        </div>
    """
    mock_response = Mock(status_code=200, text=html)
    with patch("scripts.fetch_method.requests.get", return_value=mock_response):
        out_file = tmp_path / "units.json"
        with patch.object(fetch_method, "OUT_PATH", out_file):
            fetch_method.fetch_units()
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))

    assert data == [{
        "id": "footman",
        "name": "Footman",
        "faction": "Alliance",
        "type": "Troop",
        "cost": 2,
        "image": "footman.png",
    }]
