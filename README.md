# Warcraft Rumble Data Extractor

![coverage](https://github.com/Lotus-Gaming-DE/wcr-extractor/actions/workflows/ci.yml/badge.svg)

Simple scraper that downloads minis and category data from [method.gg](https://www.method.gg/warcraft-rumble/minis). Results are written to `data/export/units.json` and `data/export/categories.json` by default, both ignored by Git except for these two files.

## Setup

```bash
./setup.sh             # install runtime requirements
./setup.sh --dev       # additionally install development tools
```
The script aborts with an error message if installation fails.

Copy `.env.example` to `.env` if you need to define environment variables. None are required by default.

### Environment variables

`SNYK_TOKEN`, `RAILWAY_TOKEN`, `RAILWAY_PROJECT` and `RAILWAY_SERVICE` are used
by the GitHub Actions workflows for security scanning and fetching Railway logs.
`API_REPO_TOKEN` must be a GitHub token with push rights to
[`wcr-api`](https://github.com/Lotus-Gaming-DE/wcr-api); without it, the
publish workflow will fail. Leave them empty if you do not use those features.

## Usage

```bash
python -m wcr_data_extraction.cli \
  --output data/export/units.json \
  --categories data/export/categories.json \
  --timeout 10 \
  --workers 4 \
  --log-level INFO \
  --log-file logs/runtime-YYYY-MM-DD-HH.json
```

`--timeout` and `--workers` must be positive integers. Results are written atomically so existing files stay intact on errors.

## Utility Scripts

- `python scripts/fetch_method.py` – fetches units and categories from method.gg. Existing files are only overwritten when the downloaded data differs. Run with `--help` to see available options; arguments mirror the CLI.

## 📤 Data Export

Extracted unit data is automatically saved to `data/export/units.json` and `categories.json`.

A GitHub Actions workflow publishes these files to the public API repo [`wcr-api`](https://github.com/Lotus-Gaming-DE/wcr-api) on every push to `main`.

To enable this workflow, you must define a repository secret named `API_REPO_TOKEN` with write access to the API repository.

## Logging

Structured JSON logs are configured via `configure_structlog()` or the `--log-level` option. By default logs are written to `logs/runtime-<YYYY-MM-DD-HH>.json` with hourly rotation. Internal logs are in English while user-facing errors are in German.

## Development

Formatting, linting and dependency checks are enforced via [pre-commit](https://pre-commit.com/):

```bash
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

CI runs pre-commit, executes the test suite (`pytest --cov=.`), generates an SBOM with `cyclonedx-py` and runs Snyk when the `SNYK_TOKEN` secret is available. Dependabot keeps Python and GitHub Actions dependencies up to date.

## Tests

```bash
pytest  # runs with --cov=. and fails after 60s if a test hangs
```

Coverage must remain above 90 %.

## Deployment

Deploy the extractor to [Railway](https://railway.app/). Set the start command to run the CLI, for example:

```bash
python -m wcr_data_extraction.cli --output data/export/units.json --categories data/export/categories.json
```

The `railway_logs` workflow streams service logs with
`npx railway logs --service <service> --project <project> --env production --json --follow`
and uploads them as artifacts.

## Contributing translations

Names and trait descriptions are defined in your local `data/categories.json`. Add new language keys in the `names` or `descriptions` objects, keeping the English text intact. Running `scripts/fetch_method.py` preserves existing translations in `units.json`.
The script compares downloaded data with the current files and only writes an update when changes are detected.

## License

This project is licensed under the [MIT License](LICENSE).
