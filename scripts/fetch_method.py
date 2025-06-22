import os
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://www.method.gg/warcraft-rumble/minis"
OUT_PATH = Path(__file__).parent.parent / "data" / "units.json"


def fetch_units():
    print(f"Starte Abruf von {BASE_URL} ...")
    response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select(".mini-card")

    all_units = []

    for card in cards:
        name_elem = card.select_one(".mini-card__name")
        faction_elem = card.select_one(".mini-card__faction")
        type_elem = card.select_one(".mini-card__type")
        cost_elem = card.select_one(".mini-card__elixir")
        image_elem = card.select_one("img")

        name = name_elem.text.strip() if name_elem else "?"
        faction = faction_elem.text.strip() if faction_elem else "?"
        unit_type = type_elem.text.strip() if type_elem else "?"
        cost = int(cost_elem.text.strip()) if cost_elem else None
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
