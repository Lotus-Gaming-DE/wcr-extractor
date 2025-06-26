# Warcraft Rumble Data Extractor
[![Coverage Status](https://img.shields.io/badge/coverage-94%25-brightgreen)](https://github.com)

Simple scraper that downloads minis from [method.gg](https://www.method.gg/warcraft-rumble/minis)
and stores them in `data/units.json`. Categories for factions, types, traits and
speeds are read from `data/categories.json`.

## Setup

```bash
./setup.sh             # installs runtime requirements
./setup.sh --dev       # installs dev tools as well
```

Copy `.env.example` to `.env` if you need to define environment variables (none
are required by default).

## Usage

```bash
python -m wcr_data_extraction.cli \
  --output data/units.json \
  --categories data/categories.json \
  --timeout 10 \
  --workers 4 \
  --log-level INFO
```

`--timeout` and `--workers` accept positive integers. Data is fetched with a
shared `requests.Session` that retries failed requests and applies the given
timeout. Results are written atomically so existing files stay intact on errors.

Example snippet from `units.json`:

```json
[
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
    "details": {
      "core_trait": {"attack_id": "aoe", "type_id": "melee"},
      "stats": {},
      "traits": [],
      "talents": [],
      "advanced_info": "..."
    }
  }
]
```

A GitHub Actions workflow updates `data/units.json` on every push to `main`.
`categories.json` is static and must be edited manually when categories change.

## Logging

Structured JSON logs are configured via `configure_structlog()` or the
`--log-level` option. When a log file is provided, messages are written to
`logs/wcr.log` with rotation. Internal logs are English while user-facing
errors are in German.

## Development

Formatting, linting and dependency checks are enforced via
[pre-commit](https://pre-commit.com/):

```bash
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```
Running `pre-commit` formats the code, lints it with Black, Ruff and
Flake8, scans the requirements with `pip-audit` and creates an SBOM via
`cyclonedx-bom` which is saved as `sbom.xml`.

Run the tests with:

```bash
pytest  # runs with --cov=. and fails after 60s if a test hangs
```

CI executes `pre-commit` and the test suite with coverage ≥90 %.
A scheduled workflow performs a Snyk security scan.
Dependabot checks Python requirements every day (GitHub Actions weekly) and its pull
requests trigger the full CI pipeline with linting, testing and `pip-audit`.

## Deployment

Deploy the extractor to [Railway](https://railway.app/) to automate data updates.
Create a Railway project linked to this repository and set the start command
to run the CLI, e.g.:

```bash
python -m wcr_data_extraction.cli --output data/units.json --categories data/categories.json
```

The CI workflow streams the service logs with
`railway logs --follow > logs/latest_railway.log` and uploads the log file as an
artifact so you can inspect the deployment output.

## Contributing translations

Names and trait descriptions are defined in `data/categories.json`.
Add new language keys in the `names` or `descriptions` objects, keeping the
English text intact. Running `scripts/fetch_method.py` preserves existing
translations in `units.json`.

## License

This project is licensed under the [MIT License](LICENSE).
