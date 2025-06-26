# Warcraft Rumble Data Extractor

Simple scraper that downloads minis from [method.gg](https://www.method.gg/warcraft-rumble/minis). The result is written to `data/units.json` which is ignored by Git. Optionally you can provide a category mapping in `data/categories.json`.

## Setup

```bash
./setup.sh             # install runtime requirements
./setup.sh --dev       # additionally install development tools
```

Copy `.env.example` to `.env` if you need to define environment variables. None are required by default.

### Environment variables

`SNYK_TOKEN` and `RAILWAY_TOKEN` are used by the GitHub Actions workflows for
security scanning and fetching Railway logs. Leave them empty if you do not use
those features.

## Usage

```bash
python -m wcr_data_extraction.cli \
  --output data/units.json \
  --categories data/categories.json \
  --timeout 10 \
  --workers 4 \
  --log-level INFO \
  --log-file logs/wcr.log
```

`--timeout` and `--workers` must be positive integers. Results are written atomically so existing files stay intact on errors.

## Utility Scripts

- `python scripts/fetch_method.py` – wrapper around the main CLI. All arguments are forwarded as-is.

## Logging

Structured JSON logs are configured via `configure_structlog()` or the `--log-level` option. By default logs are written to `logs/wcr.log` with rotation. Internal logs are in English while user-facing errors are in German.

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

The `railway_logs` workflow streams service logs with `railway logs --follow` and uploads them as artifacts.

## Contributing translations

Names and trait descriptions are defined in your local `data/categories.json`. Add new language keys in the `names` or `descriptions` objects, keeping the English text intact. Running `scripts/fetch_method.py` preserves existing translations in `units.json`.

## License

This project is licensed under the [MIT License](LICENSE).
