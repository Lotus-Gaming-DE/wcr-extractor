import json
from pathlib import Path
import sys

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.method.gg/warcraft-rumble/minis"
OUT_PATH = Path(__file__).parent.parent / "data" / "units.json"
CATEGORIES_PATH = Path(__file__).parent.parent / "data" / "categories.json"
# Value used by method.gg for immobile units.
STATIONARY = "Stationary"


def load_categories() -> dict:
    """Return mappings for category lookups.

    Besides the existing English name-to-ID maps, the returned dictionary
    contains a ``trait_desc`` mapping from trait IDs to their English
    descriptions.  ``CATEGORIES_PATH`` must point to the JSON file with the
    category definitions.
    """

    if not CATEGORIES_PATH.exists():
        return {
            "faction": {},
            "type": {},
            "trait": {},
            "speed": {},
            "trait_desc": {},
        }

    with open(CATEGORIES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    def to_map(items):
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


def load_existing_units() -> dict:
    """Return existing units indexed by ``id`` if the JSON file exists."""

    if not OUT_PATH.exists():
        return {}
    try:
        with open(OUT_PATH, encoding="utf-8") as f:
            units = json.load(f)
        return {unit.get("id"): unit for unit in units}
    except (json.JSONDecodeError, OSError):
        return {}


def is_unit_changed(old: dict, new: dict) -> bool:
    """Return ``True`` if relevant fields differ between two units."""

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





def fetch_unit_details(url: str) -> dict:
    """Fetch and parse the details page for a single mini.

    The returned dictionary contains the sections ``core_trait``, ``stats``,
    ``traits``, ``talents`` and ``advanced_info`` extracted from the detail
    page. ``core_trait`` stores ``attack_id`` and ``type_id`` which reference
    trait IDs from ``data/categories.json``. ``traits`` contains only trait IDs
    which are resolved via category lookups.  The mapping data is loaded once at
    the start of this function using :func:`load_categories`.  Talent names and
    descriptions are stored as language dictionaries, e.g. ``{"name": {"en":
    "Fresh Meat"}}``.  If present, the optional ``army_bonus_slots`` field lists
    the available army bonus slots for the bottom row and those lines are
    removed from ``advanced_info``.  Wenn beim Abruf ein Netzwerkfehler
    auftritt, gibt die Funktion eine Fehlermeldung aus und beendet das Skript
    mit dem Rückgabecode ``1``.
    """

    cats = load_categories()

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as exc:
        print(f"Fehler beim Abrufen von {url}: {exc}")
        sys.exit(1)
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    def find_section(title: str):
        h2 = soup.find("h2", string=lambda t: t and t.strip() == title)
        return h2.find_parent(class_="mini-section") if h2 else None

    details = {}

    # Core Trait information is located in the "Mini Information" block
    info_section = find_section("Mini Information")
    core_trait = {}
    if info_section:
        cat_map = cats["trait"]
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
    stats = {}
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
    traits = []
    if traits_section:
        cat_map = cats["trait"]
        for tile in traits_section.select(".mini-trait-tile"):
            name_elem = tile.select_one(".detail-info")
            name = name_elem.get_text(strip=True) if name_elem else None
            if name:
                traits.append(cat_map.get(name, name.lower().replace(" ", "-")))
    if traits:
        details["traits"] = traits

    # Talents section
    talents_section = find_section("Talents")
    talents = []
    if talents_section:
        for tile in talents_section.select(".mini-trait-tile"):
            name_elem = tile.select_one(".detail-info")
            desc_elem = tile.select_one(".mini-talent__description")
            name = name_elem.get_text(strip=True) if name_elem else None
            desc = desc_elem.get_text(strip=True) if desc_elem else None
            if name:
                talent = {"name": {"en": name}}
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

def fetch_units():
    """Fetch the minis list from method.gg and return it as a list of dicts."""
    """Download minis from method.gg and store them as JSON.

    The function retrieves the minis overview from ``method.gg`` and parses
    name, faction, type, cost, image as well as damage, health, dps, speed
    and traits for each entry. For every mini the corresponding detail page
    is fetched via :func:`fetch_unit_details` and merged into the output.
    Spells oder stationäre Einheiten besitzen keinen ``speed``-Wert; in der
    JSON-Datei erscheint dieser daher als ``null``. Ihr ``speed_id``-Eintrag
    ist ebenfalls ``null``.
    The unit name is stored in a ``names`` dictionary with language codes as
    keys.  Existing entries from ``data/units.json`` are loaded and compared
    to the scraped data. Only minis with changed values are updated in the
    output; unchanged entries remain verbatim. The file will be created if it
    does not exist.  Scheitert der Abruf der Übersichtsseite aufgrund
    eines Netzwerkfehlers, gibt die Funktion eine Meldung aus und beendet
    das Skript mit dem Rückgabecode ``1``.

    Returns:
        None: Writes the JSON file and prints progress information.
    """

    print(f"Starte Abruf von {BASE_URL} ...")
    try:
        response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as exc:
        print(f"Fehler beim Abrufen von {BASE_URL}: {exc}")
        sys.exit(1)
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("div.mini-wrapper")

    cats = load_categories()
    scraped_units = []
    existing_units = load_existing_units()

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
            # Treat "Stationary" the same as a missing speed value
            speed = None
            speed_val = None
        else:
            speed = speed_attr
            speed_val = speed_attr
        traits_attr = card.get("data-traits", "")
        trait_names = [t.strip() for t in traits_attr.split(",") if t.strip()]

        link = card.select_one("a.mini-link")
        url = f"https://www.method.gg{link['href']}" if link else None
        image_elem = card.select_one("img")
        image_url = image_elem["src"] if image_elem else None

        unit_id = (
            link["href"].split("/")[-1] if link else name
        ).lower().replace(" ", "-")

        details = fetch_unit_details(url) if url else {}

        faction_ids = [cats["faction"].get(f, f.lower()) for f in faction_val.split(",") if f]
        trait_ids = [cats["trait"].get(t, t.lower().replace(" ", "-")) for t in trait_names]
        type_id = cats["type"].get(unit_type, unit_type.lower())
        if speed_val and speed_val != "Stationary":
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

        old_names = old.get("names", {}) if old else {}
        for lang, text in old_names.items():
            if lang != "en" and lang not in unit["names"]:
                unit["names"][lang] = text
        result_units.append(unit)

    for uid, old_unit in existing_units.items():
        if uid not in seen:
            result_units.append(old_unit)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result_units, f, indent=2, ensure_ascii=False)

    print(f"{len(result_units)} Einheiten gespeichert in {OUT_PATH}")


if __name__ == "__main__":
    fetch_units()
