import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

CATEGORIES_PATH = Path(__file__).parent.parent / "data" / "categories.json"

BASE_URL = "https://www.method.gg/warcraft-rumble/minis"
OUT_PATH = Path(__file__).parent.parent / "data" / "units.json"
CATEGORIES_PATH = Path(__file__).parent.parent / "data" / "categories.json"


def load_categories() -> dict:
    """Load category mappings from :data:`CATEGORIES_PATH`."""
    with open(CATEGORIES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    def to_map(items):
        return {item["names"]["en"]: item["id"] for item in items}

    return {
        "faction": to_map(data.get("factions", [])),
        "type": to_map(data.get("types", [])),
        "trait": to_map(data.get("traits", [])),
        "speed": to_map(data.get("speeds", [])),
    }


def load_categories() -> list:
    """Load known categories from :data:`data/categories.json`."""

    if not CATEGORIES_PATH.exists():
        return []
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_CATEGORIES = load_categories()
_CATEGORIES_EN = {c.get("names", {}).get("en"): c for c in _CATEGORIES if c.get("names")}


def resolve_category(name: str) -> str:
    """Return the English label for a category.

    If the category is unknown, the input string is returned.  This allows
    additional languages to be added in ``categories.json`` without changing
    the scraping logic.
    """

    entry = _CATEGORIES_EN.get(name)
    return entry["names"]["en"] if entry else name


def fetch_unit_details(url: str) -> dict:
    """Fetch and parse the details page for a single mini.

    The returned dictionary contains the sections ``core_trait``,
    ``stats``, ``traits``, ``talents`` and ``advanced_info`` extracted
    from the detail page.
    """

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
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
        for tile in info_section.select(".mini-details-tile"):
            label_elem = tile.select_one(".detail-label")
            info_elem = tile.select_one(".detail-info")
            label = label_elem.get_text(strip=True) if label_elem else None
            value = info_elem.get_text(strip=True) if info_elem else None
            if label and label.startswith("Core Trait"):
                if "Attack" in label:
                    core_trait["attack"] = value
                elif "Type" in label:
                    core_trait["type"] = value
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
        for tile in traits_section.select(".mini-trait-tile"):
            name_elem = tile.select_one(".detail-info")
            desc_elem = tile.select_one(".mini-talent__description")
            name = name_elem.get_text(strip=True) if name_elem else None
            desc = desc_elem.get_text(strip=True) if desc_elem else None
            if name:
                traits.append({"name": name, "description": desc})
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
                talents.append({"name": name, "description": desc})
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
                    del lines[idx + 1 : j]
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
    JSON-Datei erscheint dieser daher als ``null``.
    All collected units are written to ``data/units.json``. The file will be
    created if it does not exist and overwritten otherwise.

    Returns:
        None: Writes the JSON file and prints progress information.
    """

    print(f"Starte Abruf von {BASE_URL} ...")
    response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("div.mini-wrapper")

    cats = load_categories()
    all_units = []

    for card in cards:
        name = card.get("data-name", "?")
        raw_factions = card.get("data-family", "?")
        factions = [resolve_category(f.strip()) for f in raw_factions.split(',') if f.strip()]
        faction = ",".join(factions)
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
        if speed_attr is None or speed_attr.strip() == "" or speed_attr == "Znull":
            speed = None
        else:
            speed = speed_attr
        speed_val = card.get("data-speed")
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
        speed_id = cats["speed"].get(speed_val, speed_val.lower()) if speed_val else None

        unit_data = {
            "id": unit_id,
            "name": name,
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

        all_units.append(unit_data)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_units, f, indent=2, ensure_ascii=False)

    print(f"{len(all_units)} Einheiten gespeichert in {OUT_PATH}")


if __name__ == "__main__":
    fetch_units()
