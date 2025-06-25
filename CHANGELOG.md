# Changelog

## [Unreleased]
### Added
- Command-line interface for `fetch_method.py` with `--output`, `--categories` and `--timeout` options.
- New unit tests for CLI parsing.
- Development requirements file and optional `--dev` flag for `setup.sh`.
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
- Tests for the new behaviors.
- Structured JSON logging via `configure_structlog`.
- Pre-commit configuration and CI integration.
- Security scan workflow using Snyk.
- Unit tests for structured logging.
- Package moved to `src/` layout.
- `.env.example` and log rotation support.
- Central `tests/conftest.py` and pytest-timeout with 60s default.
- CI uploads Railway logs as artifacts.
- Fix newline at end of `data/units.json` causing pre-commit failure.
- Unit test ensuring sessions close when created.
- Dependabot configuration for automated dependency updates.

### Changed
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
