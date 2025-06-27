import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts import fetch_method  # noqa: E402


def test_script_invokes_fetchers():
    base = Path(fetch_method.__file__).resolve().parents[1]
    units = base / "tmp_data" / "units.json"
    cats = base / "tmp_data" / "categories.json"
    with patch.object(fetch_method, "configure_structlog") as conf, patch.object(
        fetch_method, "fetch_categories"
    ) as fc, patch.object(fetch_method, "fetch_units") as fu:
        fetch_method.main()
        conf.assert_called_once_with("INFO")
        fc.assert_called_once_with(out_path=cats, timeout=10)
        fu.assert_called_once_with(
            out_path=units,
            categories_path=cats,
            timeout=10,
            max_workers=4,
        )
