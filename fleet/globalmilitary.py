"""Parser for the public GlobalMilitary Indian Air Force inventory page.

This is HTML scraping, not an API client. Keep requests infrequent and retain the
source URL and timestamp with every resulting snapshot.
"""
import re
from datetime import datetime

from bs4 import BeautifulSoup

SOURCE_URL = "https://www.globalmilitary.net/air_forces/ind/"
EMPTY_VALUES = {"", "-", "—", "–", "n/a"}


def _number(value, signed=False):
    value = value.strip().replace(",", "")
    if value.lower() in EMPTY_VALUES:
        return None
    cleaned = re.sub(r"[^0-9+-]", "", value)
    if not cleaned or not any(character.isdigit() for character in cleaned):
        return None
    return int(cleaned) if signed else int(cleaned.lstrip("+"))


def parse_iaf_inventory(html: str) -> tuple[dict, list[dict]]:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    update_match = re.search(r"Updated\s+(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", page_text)
    total_match = re.search(r"operates\s+([\d,]+)\s+military aircraft", page_text, re.I)
    ordered_match = re.search(r"([\d,]+)\s+more aircraft on order", page_text, re.I)
    metadata = {
        "source_updated_on": None if not update_match else datetime.strptime(update_match.group(1), "%d %b %Y").date(),
        "active_aircraft_total": _number(total_match.group(1)) if total_match else None,
        "aircraft_on_order_total": _number(ordered_match.group(1)) if ordered_match else None,
    }
    heading = soup.find(lambda tag: tag.name in {"h2", "h3"} and tag.get_text(" ", strip=True) == "Indian Air Force")
    if not heading:
        raise ValueError("Could not find the Indian Air Force inventory heading.")
    table = heading.find_next("table")
    if not table:
        raise ValueError("Could not find the Indian Air Force inventory table.")

    category = None
    aircraft = []
    for row in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        # The live table can include a leading empty cell used for presentation.
        # Remove it only when there are more cells than the documented six columns.
        if len(cells) > 6 and not cells[0]:
            cells = cells[1:]
        if len(cells) == 1:
            category = cells[0]
        elif len(cells) >= 6 and cells[0].lower() != "aircraft":
            aircraft.append({
                "category": category or "Other", "name": cells[0], "origin": cells[1],
                "model_year": _number(cells[2]), "active": _number(cells[3]),
                "yoy_change": _number(cells[4], signed=True), "ordered": _number(cells[5]),
            })
    if not aircraft:
        raise ValueError("The inventory table was found but had no aircraft records.")
    return metadata, aircraft
