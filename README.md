# Warcraft Rumble Data Extractor

Dieses Skript lädt die aktuellen Minis von [method.gg](https://www.method.gg/warcraft-rumble/minis) und speichert sie als `data/units.json`.
Der Scraper durchsucht dabei alle `div.mini-wrapper` Elemente auf der Minis-Liste und ruft anschließend die jeweilige Detailseite auf.
Neben den Basisdaten werden dadurch auch Schaden, Lebenspunkte, DPS, Geschwindigkeit und Traits sowie weitere Detailinformationen erfasst.
Zauber oder stationäre Einheiten besitzen keinen Geschwindigkeitswert; das Feld wird in der JSON-Datei daher als `null` gespeichert.

## Setup

```bash
pip install -r requirements.txt
python scripts/fetch_method.py
```

Der Aufruf legt die Datei `data/units.json` an, die alle Minis mit ihren
zusätzlichen Feldern enthält. Ein Auszug könnte folgendermaßen aussehen:

```json
[
  {
    "id": "footman",
    "name": "Footman",
    "damage": 10,
    "health": 20,
    "dps": 5.0,
    "speed": "Slow",
    "traits": ["Melee", "One-Target"],
    "details": {"core_trait": {}, "stats": {}, "traits": [], "talents": [], "advanced_info": "..."}
  }
]
```

Bei jedem Push wird zudem ein GitHub Actions Workflow ausgeführt, der die Datei `data/units.json` automatisch aktualisiert.

## Tests

Die Tests lassen sich mit [pytest](https://pytest.org) ausführen:

```bash
pip install -r requirements.txt
pytest
```
