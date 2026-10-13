"""Parser for Bharat-Rakshak's public Indian Air Force units index.

The index includes several kinds of IAF units.  This module deliberately
extracts only entries in the ``Flying Units`` section that are labelled as a
Squadron (or ``Sqn``), rather than incorrectly importing flights, radar units,
or missile units as squadrons.
"""
from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup, Tag

SOURCE_URL = "https://bharat-rakshak.com/indianairforce/database/units/"
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
SQUADRON_NAME_RE = re.compile(r"\b(?:squadron|sqn)\.?$", re.IGNORECASE)


def _normalise_text(value: str) -> str:
    return " ".join(value.split())


def _squadron_id(name: str) -> str:
    """Create a short, stable primary key suitable for the existing schema."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    digest = hashlib.sha1(name.casefold().encode("utf-8")).hexdigest()[:6]
    return f"iaf-{slug[:21].rstrip('-')}-{digest}"


def _find_section_heading(soup: BeautifulSoup, title: str) -> Tag:
    heading = soup.find(
        lambda tag: isinstance(tag, Tag)
        and tag.name in HEADING_TAGS
        and _normalise_text(tag.get_text(" ", strip=True)).casefold() == title.casefold()
    )
    # The source has used both heading wrappers and directly linked section
    # labels over time, so accept either representation.
    if not heading:
        heading = soup.find(
            lambda tag: isinstance(tag, Tag)
            and tag.name == "a"
            and _normalise_text(tag.get_text(" ", strip=True)).casefold() == title.casefold()
        )
    if not heading:
        raise ValueError(f"Could not find the {title!r} section heading.")
    return heading


def parse_iaf_squadrons(html: str) -> list[dict[str, str]]:
    """Return the named IAF flying squadrons from the public units index."""
    soup = BeautifulSoup(html, "html.parser")
    start = _find_section_heading(soup, "Flying Units")
    end = _find_section_heading(soup, "Missile Units")

    role = ""
    squadrons: list[dict[str, str]] = []
    seen_names: set[str] = set()
    for tag in start.find_all_next():
        if tag is end:
            break
        if not isinstance(tag, Tag):
            continue
        if tag.name in HEADING_TAGS:
            role = _normalise_text(tag.get_text(" ", strip=True))
            continue
        if tag.name != "a":
            continue
        name = _normalise_text(tag.get_text(" ", strip=True))
        name_key = name.casefold()
        if not SQUADRON_NAME_RE.search(name) or name_key in seen_names:
            continue
        seen_names.add(name_key)
        squadrons.append({
            "squadron_id": _squadron_id(name),
            "name": name,
            "operational_role": role,
        })

    if not squadrons:
        raise ValueError("The Flying Units section contained no squadron records.")
    return squadrons
