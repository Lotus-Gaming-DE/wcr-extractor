# Warcraft Rumble Data Extractor
[![Coverage Status](https://img.shields.io/badge/coverage-90%25-brightgreen)](https://github.com)

Dieses Skript lädt die aktuellen Minis von [method.gg](https://www.method.gg/warcraft-rumble/minis) und speichert sie als `data/units.json`.
Der Scraper durchsucht alle `div.mini-wrapper` Elemente auf der Übersichtsseite und ruft anschließend die jeweilige Detailseite auf.
Neben den Basisdaten werden dadurch auch Schaden, Lebenspunkte, DPS, Geschwindigkeit und Traits sowie weitere Details erfasst.
Zauber oder stationäre Einheiten besitzen keinen Geschwindigkeitswert; in der JSON-Datei erscheint daher `"speed": null` und auch `speed_id` ist `null`.
Falls das `speed`-Attribut den Wert `"Stationary"` trägt, wird dieser ebenfalls als fehlende Geschwindigkeit behandelt und als `null` gespeichert.
Bei allen anderen Einheiten wird `speed` weggelassen; stattdessen verweist `speed_id` auf die jeweilige Geschwindigkeitskategorie.

## Setup

```bash
./setup.sh
python -m wcr_data_extraction.cli \
  --output data/units.json \
  --categories data/categories.json \
  --timeout 10 \
  --workers 4
```

## Quickstart

1. Install dependencies: `./setup.sh --dev` for development or without `--dev`
   for runtime only.
2. Run `python -m wcr_data_extraction.cli` to download the data.
3. The results are written to `data/units.json` and `data/categories.json`.

``--output`` legt den Pfad der Ergebnisdatei fest. ``--categories`` bestimmt die
Kategorien-Definitionen. ``--timeout`` setzt das HTTP-Timeout in Sekunden und
``--workers`` steuert die Anzahl paralleler Downloads. Ohne Angaben werden die
obigen Standardwerte verwendet.

`setup.sh` installiert die Bibliotheken aus `requirements.txt`. Mit
`./setup.sh --dev` werden zusätzlich die Entwicklerwerkzeuge aus
`requirements-dev.txt` installiert. Das Skript nutzt `python3 -m pip`, um
Warnungen beim Ausführen als Root zu vermeiden.

Der Aufruf legt die Dateien `data/units.json` und `data/categories.json` an.
Tritt beim Abrufen ein Netzwerkfehler auf oder antwortet der Server mit einem
HTTP-Status ungleich `200`, wird eine `FetchError`-Exception ausgelöst. Das
Hauptprogramm fängt diese ab, schreibt eine Fehlermeldung in das Log und
beendet sich mit dem Code `1`. Alle HTTP-Anfragen verwenden einen gemeinsamen
`requests.Session` mit automatischen Retries und brechen nach zehn Sekunden
ohne Antwort mit einem Timeout ab.
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
      "core_trait": {"attack_id": "aoe", "type_id": "melee"},
      "stats": {},
      "traits": [],
      "talents": [
        {"name": {"en": "Hold the Line"}, "description": {"en": "..."}}
      ],
      "advanced_info": "..."
    }
  }
]
```

Bei jedem Push wird zudem ein GitHub Actions Workflow ausgeführt, der die Dateien
`data/units.json` und `data/categories.json` automatisch aktualisiert.
Trait descriptions are stored in `data/categories.json` under the `descriptions` field.
The `core_trait` object of each unit lists `attack_id` and `type_id`,
which map to the same trait IDs used in `trait_ids`.
The helper function `fetch_unit_details()` expects the category mappings as a
dictionary argument so that callers can load the data only once with
`load_categories()` and reuse it across multiple units.

Das optionale Feld `army_bonus_slots` listet die Boni, die eine Einheit in der
unteren Reihe des Armeefensters gewähren kann. Sind solche Angaben vorhanden,
werden sie aus `advanced_info` entfernt und in `army_bonus_slots` gespeichert.


## Logging

Die Skripte verwenden das Modul `logging`. Über das Argument `--log-level` oder
die Umgebungsvariable `LOG_LEVEL` lässt sich die gewünschte Protokollstufe
festlegen. Standardmäßig wird auf `INFO` geloggt.

## Tests

Die Tests lassen sich mit [pytest](https://pytest.org) ausführen:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Bei jedem Push und für Pull Requests führt ein GitHub Actions Workflow
(`ci.yml`) `flake8` und `pytest` aus, um sicherzustellen, dass Linting und
Tests fehlerfrei durchlaufen.

## Formatting

Code style is enforced with [Black](https://black.readthedocs.io/) and
[Flake8](https://flake8.pycqa.org/). Install the development dependencies
with:

```bash
pip install -r requirements-dev.txt
```

Run the formatters before committing:

```bash
black scripts tests
flake8
```

## Updating dependencies

The versions in `requirements.txt` and `requirements-dev.txt` are pinned.
To update a package, run `pip install -U <package>` and then freeze the
current version into the appropriate requirements file.  After adjusting the
files, execute the test suite:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Commit the updated requirements together with any code changes.
The repository can also be kept up to date automatically via Dependabot.

## Contributing translations

The names of factions and other categories are defined in
`data/categories.json`. Each entry contains an `id` and a `names`
dictionary with language codes as keys. Split-leader factions such as
"Alliance & Undead" appear here as well. Traits also have a `descriptions` dictionary for
localized text. Unit names and talent information in `data/units.json`
use the same structure: every textual field is a dictionary keyed by
language code.
The scraper currently reads only the English values (`names["en"]`), but you can
provide translations for additional languages. To contribute a translation,
add a new language key anywhere a `names` or `descriptions` dictionary appears.
For example:

```json
{ "id": "alliance", "names": { "en": "Alliance", "de": "Allianz" } }
```

Please keep the English text intact so the parser can continue to resolve the
categories correctly.

Wird `scripts/fetch_method.py` erneut ausgeführt, liest der Scraper die
bestehende Datei `data/units.json` ein und prüft für jede Mini, ob sich
relevante Werte geändert haben. Nur geänderte Einheiten werden aktualisiert,
unveränderte Datensätze bleiben unverändert erhalten. Dabei übernimmt das
Skript alle vorhandenen Sprachschlüssel (außer `en`) automatisch, sodass eigene
Übersetzungen nicht nach jedem Update neu eingetragen werden müssen.

Trait descriptions are stored in the same file.  Each trait entry has a
``descriptions`` object with language codes as keys.  The unit data only lists
trait IDs in ``details['traits']``; refer to ``categories.json`` to look up the
text.

## License

This project is licensed under the [MIT License](LICENSE).
