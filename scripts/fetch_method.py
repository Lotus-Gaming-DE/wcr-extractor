import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://www.method.gg/warcraft-rumble/minis"
OUT_PATH = Path(__file__).parent.parent / "data" / "units.json"


def fetch_units():
    """Fetch the minis list from method.gg and return it as a list of dicts."""
    """Download minis from method.gg and store them as JSON.

    The function retrieves the minis overview from ``method.gg`` and parses
    name, faction, type, cost and image for each entry. All collected units
    are written to ``data/units.json``. The file will be created if it does
    not exist and overwritten otherwise.

    Returns:
        None: Writes the JSON file and prints progress information.
    """

    print(f"Starte Abruf von {BASE_URL} ...")
    response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select("div.mini-wrapper")

    all_units = []

    for card in cards:
        name = card.get("data-name", "?")
        faction = card.get("data-family", "?")
        unit_type = card.get("data-type", "?")
        cost_attr = card.get("data-cost")
        cost = int(cost_attr) if cost_attr is not None else None
        image_elem = card.select_one("img")
        image_url = image_elem["src"] if image_elem else None

        unit_id = name.lower().replace(" ", "-")

        all_units.append({
            "id": unit_id,
            "name": name,
            "faction": faction,
            "type": unit_type,
            "cost": cost,
            "image": image_url
        })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_units, f, indent=2, ensure_ascii=False)

    print(f"{len(all_units)} Einheiten gespeichert in {OUT_PATH}")


if __name__ == "__main__":
    fetch_units()
