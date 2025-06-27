# Warcraft Rumble Data Extractor

Simple scraper that downloads minis and category data from [method.gg](https://www.method.gg/warcraft-rumble/minis). Results are written to `data/units.json` and `data/categories.json`, both ignored by Git.

## Setup

```bash
./setup.sh             # install runtime requirements
./setup.sh --dev       # additionally install development tools
```
The script aborts with an error message if installation fails.

Copy `.env.example` to `.env` if you need to define environment variables. None are required by default.

### Environment variables

`SNYK_TOKEN`, `RAILWAY_TOKEN`, `RAILWAY_PROJECT` and `RAILWAY_SERVICE` are used
by the GitHub Actions workflows for security scanning and fetching Railway
logs. Leave them empty if you do not use those features.

## Usage

```bash
python -m wcr_data_extraction.cli \
  --output data/units.json \
  --categories data/categories.json \
  --timeout 10 \
  --workers 4 \
  --log-level INFO \
  --log-file logs/runtime-YYYY-MM-DD-HH.json
```

`--timeout` and `--workers` must be positive integers. Results are written atomically so existing files stay intact on errors.

## Utility Scripts

- `python scripts/fetch_method.py` – fetches units and categories from method.gg. Existing files are only overwritten when the downloaded data differs. Run with `--help` to see available options; arguments mirror the CLI.

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
python -m wcr_data_extraction.cli --output data/units.json --categories data/categories.json
```

The `railway_logs` workflow streams service logs with
`npx railway logs --service <service> --project <project> --env production --json --follow`
and uploads them as artifacts.

## Contributing translations

Names and trait descriptions are defined in your local `data/categories.json`. Add new language keys in the `names` or `descriptions` objects, keeping the English text intact. Running `scripts/fetch_method.py` preserves existing translations in `units.json`.
The script compares downloaded data with the current files and only writes an update when changes are detected.

## License

This project is licensed under the [MIT License](LICENSE).
