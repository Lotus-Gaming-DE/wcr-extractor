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

### Changed
- GitHub Actions workflow uses explicit paths when updating data.
- Pinned package versions in `requirements.txt` and `requirements-dev.txt`.
- `fetch_unit_details` accepts a `categories` dict instead of a file path.
- `fetch_units` loads categories once via `load_categories` and passes them to
  `fetch_unit_details`.
- `fetch_unit_details` and `fetch_units` werfen nun auch bei HTTP-Statuscodes
  ungleich `200` eine `FetchError` mit dem jeweiligen Statuscode.
- `setup.sh` now uses `python3 -m pip`.

