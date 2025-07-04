# Changelog

## [Unreleased]
### Added
- Automated export of JSON files to `data/export/`
- GitHub Actions workflow to push data to the `wcr-api` repository
- JSON validation and export file tests
- Workflow `railway_logs.yml` streams deployment logs.
- SBOM uploaded as a CI artifact.
- `scripts/fetch_method.py` now exposes a `main()` function.
- Command-line interface for `fetch_method.py` with `--output`, `--categories` and `--timeout` options.
- New unit tests for CLI parsing.
- Development requirements file and optional `--dev` flag for `setup.sh`.
- Automatic fetching of category data to `categories.json`.
- Section in README on updating dependencies.
- Package refactored into `wcr_data_extraction` with `cli` module.
- Parallel download support via `--workers`.
- Retry logic now includes exponential backoff.
- Coverage badge in README and CI enforces >90% coverage.
- Logging configuration via `configure_logging()`.
- Validation for positive integer arguments `--timeout` and `--workers`.
- Atomic writes when saving `units.json`.
- Warning logs when `load_categories` fails to read the file.
- Helper `create_session` for injecting custom HTTP sessions.
- Validation in publish workflow ensures JSON files are non-empty and valid.
- Requirements now include explicit `urllib3` dependency.
- `setup.sh` fails fast on installation errors.
- Tests for the new behaviors.
- Structured JSON logging via `configure_structlog`.
- Pre-commit configuration and CI integration.
- SBOM generation via `cyclonedx-bom` and CI archiving.
- Security scan workflow using Snyk.
- Unit tests for structured logging.
- Package moved to `src/` layout.
- `.env.example` and log rotation support.
- Central `tests/conftest.py` and pytest-timeout with 60s default.
- CI uploads Railway logs as artifacts.
- Unit test ensuring sessions close when created.
- Dependabot configuration for automated dependency updates.
- Dependabot now checks Python dependencies daily and its pull requests run
  the complete CI pipeline.

### Changed
- `scripts/fetch_method.py` now skips writing `units.json` and `categories.json` when no changes are detected.
- `scripts/fetch_method.py` defaults to `data/` for units and categories.
- Removed tracked `data/` directory and added it to `.gitignore`.
- GitHub Actions workflow uses explicit paths when updating data.
- Pinned package versions in `requirements.txt` and `requirements-dev.txt`.
- `fetch_unit_details` accepts a `categories` dict instead of a file path.
- `fetch_units` loads categories once via `load_categories` and passes them to
  `fetch_unit_details`.
- `fetch_unit_details` and `fetch_units` werfen nun auch bei HTTP-Statuscodes
  ungleich `200` eine `FetchError` mit dem jeweiligen Statuscode.
- `setup.sh` now uses `python3 -m pip`.
- CI caches dependencies and runs pre-commit.
- CI now runs on Dependabot pull requests.
- README regenerated with updated instructions.
- CLI error messages are now in German.
- Requirements updated with `structlog`, `pre-commit` and `ruff`.
- Sessions created in `fetch_units` are now closed reliably.
- README and CHANGELOG brought in line with the global structure.
- Clarified example environment file and added explanatory comments.
- CI: Skip Snyk test in forked PRs to prevent missing-secret auth errors.
- Hourly log rotation with `TimedRotatingFileHandler`.
- Default log file name `runtime-<YYYY-MM-DD-HH>.json`.
- Wrapper script now uses `argparse` and supports `--help`.
- Workflows use `npx` for Railway CLI and include project/service IDs.
- Security workflow runs CodeQL and TruffleHog scans.
- Dependabot auto-merge workflow.
- GitHub Actions workflow to auto-publish `units.json` and `categories.json` into `data/` if changed
- `fetch_categories` derives `types`, `traits` and `speeds` from `units.json` instead of HTML filters.
- CLI now writes `categories.json` alongside `units.json`.
- Update workflow to use default export paths and upload extractor logs.
- README now displays a CI coverage badge.
- README clarifies that `API_REPO_TOKEN` must have push rights to `wcr-api` and
  that the publish workflow fails without it.

### Fixed
- `fetch_unit_details` now stores trait descriptions when categories contain
  `null` values.
