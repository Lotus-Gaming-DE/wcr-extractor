# Warcraft Rumble Data Extractor

Dieses Skript lädt die aktuellen Minis von [method.gg](https://www.method.gg/warcraft-rumble/minis) und speichert sie als `data/units.json`.

## Setup

```bash
pip install -r requirements.txt
python scripts/fetch_method.py
```

Bei jedem Push wird zudem ein GitHub Actions Workflow ausgeführt, der die Datei `data/units.json` automatisch aktualisiert.

## Tests

Die Tests lassen sich mit [pytest](https://pytest.org) ausführen:

```bash
pip install -r requirements.txt
pytest
```
