"""Functions to fetch Warcraft Rumble unit data from method.gg."""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
import structlog
from pathlib import Path
from typing import Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

BASE_URL = "https://www.method.gg/warcraft-rumble/minis"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "units.json"
CATEGORIES_PATH = Path(__file__).resolve().parent / "data" / "categories.json"
STATIONARY = "Stationary"

# HTTP session with retry logic and backoff
_retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=_retry)

_session: requests.Session | None = None


def create_session() -> requests.Session:
    """Return a configured ``requests.Session`` with retry logic."""

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _get_session() -> requests.Session:
    """Return a global session instance to reuse connections."""
    global _session
    if _session is None:
        _session = create_session()
    return _session


def configure_structlog(level: str, log_file: str | Path | None = None) -> None:
    """Configure structured logging with the given level.

    If ``log_file`` is provided, logs are also written there with rotation.
    """

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
        )

    logging.basicConfig(
        level=level.upper(), format="%(message)s", handlers=handlers, force=True
    )
    structlog.configure(
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level.upper())
        ),
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )


logger = structlog.get_logger(__name__)


class FetchError(Exception):
    """Raised when fetching data from method.gg fails."""


def load_categories(categories_path: Path | str | None = None) -> dict:
    """Return mappings for category lookups."""

    path = Path(categories_path or CATEGORIES_PATH)
    if not path.exists():
        return {
            "faction": {},
            "type": {},
            "trait": {},
            "speed": {},
            "trait_desc": {},
        }
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read categories from %s: %s", path, exc)
        return {
            "faction": {},
            "type": {},
            "trait": {},
            "speed": {},
            "trait_desc": {},
        }

    def to_map(items: Iterable[dict]) -> dict:
        return {item["names"]["en"]: item["id"] for item in items}

    trait_desc = {
        item["id"]: item.get("descriptions", {}).get("en")
        for item in data.get("traits", [])
    }

    return {
        "faction": to_map(data.get("factions", [])),
        "type": to_map(data.get("types", [])),
        "trait": to_map(data.get("traits", [])),
        "speed": to_map(data.get("speeds", [])),
        "trait_desc": trait_desc,
    }


def load_existing_units(out_path: Path | str | None = None) -> dict:
    """Return existing units indexed by ``id`` if the JSON file exists."""

    path = Path(out_path or OUT_PATH)
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            units = json.load(f)
        return {unit.get("id"): unit for unit in units}
    except (json.JSONDecodeError, OSError):
        return {}


def is_unit_changed(old: dict, new: dict) -> bool:
    """Return ``True`` if relevant fields differ between two units."""
    # Only compare fields that affect gameplay. Translations are ignored.

    compare_keys = [
        "faction_ids",
        "type_id",
        "cost",
        "image",
        "damage",
        "health",
        "dps",
        "speed_id",
        "trait_ids",
        "details",
    ]
    if old.get("names", {}).get("en") != new.get("names", {}).get("en"):
        return True
    return any(old.get(k) != new.get(k) for k in compare_keys)


def fetch_unit_details(
    url: str,
    categories: dict,
    *,
    timeout: int = 10,
    session: requests.Session | None = None,
) -> dict:
    """Fetch and parse the details page for a single mini."""

    if not url.startswith("https://"):
        raise FetchError(f"Insecure URL not allowed: {url}")

    sess = session or _get_session()

    try:
        response = sess.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
    except requests.RequestException as exc:
        raise FetchError(f"Error fetching {url}: {exc}") from exc
    if response.status_code != 200:
        raise FetchError(f"Error fetching {url}: Status {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    def find_section(title: str):
        h2 = soup.find("h2", string=lambda t: t and t.strip() == title)
        return h2.find_parent(class_="mini-section") if h2 else None

    details: dict = {}

    # Core Trait information is located in the "Mini Information" block
    info_section = find_section("Mini Information")
    core_trait: dict = {}
    if info_section:
        cat_map = categories["trait"]
        for tile in info_section.select(".mini-details-tile"):
            label_elem = tile.select_one(".detail-label")
            info_elem = tile.select_one(".detail-info")
            label = label_elem.get_text(strip=True) if label_elem else None
            value = info_elem.get_text(strip=True) if info_elem else None
            if label and value and label.startswith("Core Trait"):
                trait_id = cat_map.get(value, value.lower().replace(" ", "-"))
                if "Attack" in label:
                    core_trait["attack_id"] = trait_id
                elif "Type" in label:
                    core_trait["type_id"] = trait_id
    if core_trait:
        details["core_trait"] = core_trait

    # Stats section
    stats_section = find_section("Stats")
    stats: dict = {}
    if stats_section:
        for tile in stats_section.select(".mini-details-tile"):
            label_elem = tile.select_one(".detail-label")
            info_elem = tile.select_one(".detail-info") or tile.select_one(
                ".mini-stats__upgrade.detail-info"
            )
            label = label_elem.get_text(strip=True) if label_elem else None
            value = info_elem.get_text(strip=True) if info_elem else None
            if label and value:
                stats[label] = value
    if stats:
        details["stats"] = stats

    # Traits section
    traits_section = find_section("Traits")
    traits: list[str] = []
    if traits_section:
        cat_map = categories["trait"]
        for tile in traits_section.select(".mini-trait-tile"):
            name_elem = tile.select_one(".detail-info")
            name = name_elem.get_text(strip=True) if name_elem else None
            if name:
                traits.append(cat_map.get(name, name.lower().replace(" ", "-")))
    if traits:
        details["traits"] = traits

    # Talents section
    talents_section = find_section("Talents")
    talents: list[dict] = []
    if talents_section:
        for tile in talents_section.select(".mini-trait-tile"):
            name_elem = tile.select_one(".detail-info")
            desc_elem = tile.select_one(".mini-talent__description")
            name = name_elem.get_text(strip=True) if name_elem else None
            desc = desc_elem.get_text(strip=True) if desc_elem else None
            if name:
                talent: dict = {"name": {"en": name}}
                if desc:
                    talent["description"] = {"en": desc}
                talents.append(talent)
    if talents:
        details["talents"] = talents

    # Advanced Mini Information section
    adv_section = find_section("Advanced Mini Information")
    if adv_section:
        content = adv_section.select_one(".mini-content")
        if content:
            adv_text = content.get_text("\n", strip=True)
            lines = adv_text.splitlines()
            prefix = "Available army bonus slots for the bottom row"
            army_bonus_slots = []
            # Extract the slot list and remove it from the remaining text
            for idx, line in enumerate(lines):
                if line.startswith(prefix):
                    j = idx + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if next_line == "" or next_line.startswith("Without"):
                            break
                        army_bonus_slots.append(next_line.strip())
                        j += 1
                    del lines[idx:j]
                    break
            details["advanced_info"] = "\n".join(lines)
            if army_bonus_slots:
                details["army_bonus_slots"] = army_bonus_slots

    return details


def fetch_units(
    *,
    out_path: Path | str | None = None,
    categories_path: Path | str | None = None,
    timeout: int = 10,
    max_workers: int = 1,
    session: requests.Session | None = None,
) -> None:
    """Download minis from method.gg and store them as JSON."""

    if not BASE_URL.startswith("https://"):
        raise FetchError("BASE_URL must use HTTPS")

    out_path = Path(out_path or OUT_PATH)
    categories_path = Path(categories_path or CATEGORIES_PATH)

    created_session = False
    if session is None:
        sess = create_session()
        created_session = True
    else:
        sess = session

    try:
        logger.info("Fetching overview from %s", BASE_URL)
        try:
            response = sess.get(
                BASE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout
            )
        except requests.RequestException as exc:
            raise FetchError(f"Error fetching {BASE_URL}: {exc}") from exc
        if response.status_code != 200:
            raise FetchError(
                f"Error fetching {BASE_URL}: Status {response.status_code}"
            )

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.select("div.mini-wrapper")

        cats = load_categories(categories_path)
        scraped_units = []
        existing_units = load_existing_units(out_path)

        from concurrent.futures import ThreadPoolExecutor

        # Fetch detail pages in parallel to speed up scraping
        def fetch(card) -> tuple[str, dict]:
            link = card.select_one("a.mini-link")
            url = f"https://www.method.gg{link['href']}" if link else None
            unit_id = (
                (link["href"].split("/")[-1] if link else card.get("data-name", "?"))
                .lower()
                .replace(" ", "-")
            )
            details = (
                fetch_unit_details(url, cats, timeout=timeout, session=sess)
                if url
                else {}
            )
            logger.info("Fetched %s", unit_id)
            return unit_id, details

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            detail_results = list(executor.map(fetch, cards))

        details_map = {uid: det for uid, det in detail_results}

        for card in cards:
            name = card.get("data-name", "?")
            faction_val = card.get("data-family", "?")
            unit_type = card.get("data-type", "?")
            cost_attr = card.get("data-cost")
            cost = int(cost_attr) if cost_attr is not None else None

            damage_attr = card.get("data-damage")
            damage = int(float(damage_attr)) if damage_attr is not None else None
            health_attr = card.get("data-health")
            health = int(float(health_attr)) if health_attr is not None else None
            dps_attr = card.get("data-dps")
            dps = float(dps_attr) if dps_attr is not None else None
            speed_attr = card.get("data-speed")
            if (
                speed_attr is None
                or speed_attr.strip() == ""
                or speed_attr == "Znull"
                or speed_attr == STATIONARY
            ):
                speed = None
                speed_val = None
            else:
                speed = speed_attr
                speed_val = speed_attr
            traits_attr = card.get("data-traits", "")
            trait_names = [t.strip() for t in traits_attr.split(",") if t.strip()]

            link = card.select_one("a.mini-link")
            image_elem = card.select_one("img")
            image_url = image_elem["src"] if image_elem else None

            unit_id = (
                (link["href"].split("/")[-1] if link else name)
                .lower()
                .replace(" ", "-")
            )

            details = details_map.get(unit_id, {})

            faction_ids = [
                cats["faction"].get(f, f.lower()) for f in faction_val.split(",") if f
            ]
            trait_ids = [
                cats["trait"].get(t, t.lower().replace(" ", "-")) for t in trait_names
            ]
            type_id = cats["type"].get(unit_type, unit_type.lower())
            if speed_val and speed_val != STATIONARY:
                speed_id = cats["speed"].get(speed_val, speed_val.lower())
            else:
                speed_id = None

            unit_data = {
                "id": unit_id,
                "names": {"en": name},
                "faction_ids": faction_ids,
                "type_id": type_id,
                "cost": cost,
                "image": image_url,
                "damage": damage,
                "health": health,
                "dps": dps,
                "speed_id": speed_id,
                "trait_ids": trait_ids,
                "details": details,
            }
            if speed is None:
                unit_data["speed"] = None

            scraped_units.append(unit_data)

        result_units = []
        seen = set()
        for unit in scraped_units:
            old = existing_units.get(unit["id"])
            seen.add(unit["id"])
            if old and not is_unit_changed(old, unit):
                result_units.append(old)
                continue

            # Preserve translations from the previous file so they are not lost
            old_names = old.get("names", {}) if old else {}
            for lang, text in old_names.items():
                if lang != "en" and lang not in unit["names"]:
                    unit["names"][lang] = text
            result_units.append(unit)

        for uid, old_unit in existing_units.items():
            if uid not in seen:
                result_units.append(old_unit)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = out_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(result_units, f, indent=2, ensure_ascii=False)
            f.write("\n")
        tmp_path.replace(out_path)

        logger.info("%s units saved to %s", len(result_units), out_path)
    finally:
        if created_session:
            sess.close()
