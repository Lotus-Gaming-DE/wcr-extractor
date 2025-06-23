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

Der Aufruf legt die Dateien `data/units.json` und `data/categories.json` an.
`units.json` enthält die Minis, `categories.json` die verfügbaren Fraktionen,
Typen, Traits und Geschwindigkeiten.
Ein Auszug aus `units.json` könnte folgendermaßen aussehen:

```json
[
  {
    "id": "footman",
    "name": "Footman",
    "damage": 10,
    "health": 20,
    "dps": 5.0,
    "speed_id": "slow",
    "type_id": "troop",
    "faction_ids": ["alliance"],
    "trait_ids": ["melee", "one-target"],
    "details": {"core_trait": {}, "stats": {}, "traits": [], "talents": [], "advanced_info": "..."}
  }
]
```

Bei jedem Push wird zudem ein GitHub Actions Workflow ausgeführt, der die Dateien
`data/units.json` und `data/categories.json` automatisch aktualisiert.
    "speed": "Slow",
    "traits": ["Melee", "One-Target"],
    "details": {
      "core_trait": {},
      "stats": {},
      "traits": [],
      "talents": [],
      "advanced_info": "...",
      "army_bonus_slots": []
    }
  }
]
```

Das optionale Feld `army_bonus_slots` enthält eine Liste der Boni, die eine
Einheit in der unteren Reihe des Armeefensters gewähren kann, sofern diese
Information auf der Detailseite vorhanden ist.

Bei jedem Push wird zudem ein GitHub Actions Workflow ausgeführt, der die Datei `data/units.json` automatisch aktualisiert.

## Tests

Die Tests lassen sich mit [pytest](https://pytest.org) ausführen:

```bash
pip install -r requirements.txt
pytest
```

## Contributing translations

The names of factions and other categories are defined in
`data/categories.json`.  Each entry contains an `id` and a `names`
dictionary with language codes as keys.  The scraper currently reads only the
English value (`names["en"]`), but you can provide translations for additional
languages.  To contribute a translation, add or update the appropriate
language key.  For example:

```json
{ "id": "alliance", "names": { "en": "Alliance", "de": "Allianz" } }
```

Please keep the English text intact so the parser can continue to resolve the
categories correctly.
