# Warcraft Rumble Data Extractor

Dieses Skript lädt die aktuellen Minis von [method.gg](https://www.method.gg/warcraft-rumble/minis) und speichert sie als `data/units.json`.
Der Scraper durchsucht dabei alle `div.mini-wrapper` Elemente auf der Minis-Liste und ruft anschließend die jeweilige Detailseite auf.
Neben den Basisdaten werden dadurch auch Schaden, Lebenspunkte, DPS,
Geschwindigkeit und Traits sowie weitere Detailinformationen erfasst.
Zauber oder stationäre Einheiten besitzen keinen Geschwindigkeitswert; in der
JSON-Datei erscheint daher `"speed": null` und auch `speed_id` ist `null`.
Bei allen anderen Einheiten wird `speed` weggelassen; stattdessen verweist
`speed_id` auf die jeweilige Geschwindigkeitskategorie.

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
    "names": {"en": "Footman"},
    "damage": 10,
    "health": 20,
    "dps": 5.0,
    "speed_id": "slow",
    "type_id": "troop",
    "faction_ids": ["alliance"],
    "trait_ids": ["melee", "one-target"],
    "details": {
      "core_trait": {},
      "stats": {},
      "traits": [],
      "talents": [
        {"names": {"en": "Hold the Line"}, "description": "..."}
      ],
      "advanced_info": "..."
    }
  }
]
```

Bei jedem Push wird zudem ein GitHub Actions Workflow ausgeführt, der die Dateien
`data/units.json` und `data/categories.json` automatisch aktualisiert.
Trait descriptions are stored in `data/categories.json` under the `descriptions` field.

Das optionale Feld `army_bonus_slots` listet die Boni, die eine Einheit in der
unteren Reihe des Armeefensters gewähren kann. Sind solche Angaben vorhanden,
werden sie aus `advanced_info` entfernt und in `army_bonus_slots` gespeichert.

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
dictionary with language codes as keys. Traits also have a `descriptions`
dictionary for localized text. Unit and talent names in `data/units.json`
use the same structure.
The scraper currently reads only the English values (`names["en"]`), but you can
provide translations for additional languages. To contribute a translation,
add a new language key anywhere a `names` or `descriptions` dictionary appears.
For example:

```json
{ "id": "alliance", "names": { "en": "Alliance", "de": "Allianz" } }
```

Please keep the English text intact so the parser can continue to resolve the
categories correctly.
