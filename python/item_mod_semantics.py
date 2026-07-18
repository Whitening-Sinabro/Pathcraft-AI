# -*- coding: utf-8 -*-
"""Normalize readable PoB item mod lines into build-analysis signals."""

from __future__ import annotations

import re
from typing import Any


SIGNED_INT_RE = re.compile(r"(?<![\d.])(?P<num>[+-]?\d+)(?:\.\d+)?(?![\d.])")
TAG_RE = re.compile(r"^\{(?P<tag>[^}]+)\}")

ITEM_TEXT_SKIP_PREFIXES = (
    "Rarity:",
    "Unique ID:",
    "Item Level:",
    "LevelReq:",
    "Quality:",
    "Sockets:",
    "Requirements:",
    "Level:",
    "Str:",
    "Dex:",
    "Int:",
    "BasePercentile",
    "Synthesised Item",
    "Fractured Item",
    "Mirrored",
    "Split",
    "Corrupted",
)

ITEM_TEXT_SKIP_LINES = {
    "",
    "--------",
    "Requirements:",
    "Sockets:",
    "Unidentified",
}

PREFIX_CATEGORY_HINTS = {
    "maximum_life",
    "energy_shield",
    "armour",
    "evasion",
    "ward",
    "physical_damage",
    "elemental_damage",
    "spell_damage",
    "attack_damage",
    "gem_level",
}

SUFFIX_CATEGORY_HINTS = {
    "resistance",
    "fire_resistance",
    "cold_resistance",
    "lightning_resistance",
    "chaos_resistance",
    "all_elemental_resistance",
    "attribute",
    "strength",
    "dexterity",
    "intelligence",
    "all_attributes",
    "suppression",
    "attack_speed",
    "cast_speed",
    "critical",
    "accuracy",
    "ailment_avoidance",
}

NUMERIC_TOTAL_KEYS = (
    "maximum_life",
    "maximum_energy_shield",
    "fire_resistance",
    "cold_resistance",
    "lightning_resistance",
    "chaos_resistance",
    "strength",
    "dexterity",
    "intelligence",
    "spell_suppression",
    "movement_speed",
)


def _first_signed_int(text: str) -> int | None:
    match = SIGNED_INT_RE.search(text)
    if not match:
        return None
    return int(float(match.group("num")))


def _strip_pob_tags(line: str) -> tuple[list[str], str]:
    tags: list[str] = []
    rest = line.strip()
    while True:
        match = TAG_RE.match(rest)
        if not match:
            break
        tags.append(match.group("tag").strip().casefold())
        rest = rest[match.end():].strip()
    return tags, rest


def _source_from_tags(tags: list[str], fallback: str) -> str:
    joined = " ".join(tags)
    if "crafted" in joined:
        return "crafted"
    if "fractured" in joined:
        return "fractured"
    if "implicit" in joined:
        return "implicit"
    if "enchant" in joined:
        return "enchant"
    if "synth" in joined:
        return "synthesised"
    return fallback


def classify_item_mod_text(text: str) -> list[str]:
    lower = str(text or "").casefold()
    categories: list[str] = []

    def add(category: str) -> None:
        if category not in categories:
            categories.append(category)

    if "maximum life" in lower:
        add("maximum_life")
        add("life")
    elif " life" in f" {lower}":
        add("life")

    if "energy shield" in lower:
        add("energy_shield")
    if "armour" in lower:
        add("armour")
    if "evasion" in lower:
        add("evasion")
    if "ward" in lower:
        add("ward")

    if "fire resistance" in lower:
        add("fire_resistance")
        add("fire")
        add("resistance")
    if "cold resistance" in lower:
        add("cold_resistance")
        add("cold")
        add("resistance")
    if "lightning resistance" in lower:
        add("lightning_resistance")
        add("lightning")
        add("resistance")
    if "chaos resistance" in lower:
        add("chaos_resistance")
        add("chaos")
        add("resistance")
    if "all elemental resistances" in lower or "elemental resistances" in lower:
        add("all_elemental_resistance")
        add("elemental")
        add("resistance")
    elif "resistance" in lower or "resistances" in lower:
        add("resistance")

    if "strength" in lower:
        add("strength")
        add("attribute")
    if "dexterity" in lower:
        add("dexterity")
        add("attribute")
    if "intelligence" in lower:
        add("intelligence")
        add("attribute")
    if "all attributes" in lower or "attributes" in lower:
        add("all_attributes")
        add("attribute")

    if "suppress spell damage" in lower or "spell suppression" in lower:
        add("suppression")
    if "movement speed" in lower:
        add("movement_speed")
        add("speed")
    if "attack speed" in lower:
        add("attack_speed")
        add("speed")
    if "cast speed" in lower:
        add("cast_speed")
        add("speed")
    if "critical" in lower or "crit" in lower:
        add("critical")
    if "accuracy" in lower:
        add("accuracy")
    if "avoid" in lower and any(word in lower for word in ("ailment", "ignite", "shock", "freeze", "chill")):
        add("ailment_avoidance")

    if "physical damage" in lower:
        add("physical_damage")
        add("physical")
        add("damage")
    if "elemental damage" in lower:
        add("elemental_damage")
        add("elemental")
        add("damage")
    if "spell damage" in lower and "suppress spell damage" not in lower:
        add("spell_damage")
        add("spell")
        add("damage")
    if "attack" in lower:
        add("attack")
        if "damage" in lower:
            add("attack_damage")
            add("damage")
    if "damage" in lower:
        add("damage")
    if "projectile" in lower:
        add("projectile")
    if "minion" in lower:
        add("minion")
    if "socketed" in lower or "gem" in lower or "gems" in lower:
        add("gem_level" if "level" in lower else "gem")
    if "reservation" in lower or "reserved" in lower:
        add("reservation")
    if "flask" in lower:
        add("flask")
    if "leech" in lower:
        add("leech")
    if "regenerate" in lower or "regeneration" in lower:
        add("regeneration")

    return categories


def extract_item_mod_numeric_totals(text: str) -> dict[str, int]:
    lower = str(text or "").casefold()
    value = _first_signed_int(text)
    if value is None:
        return {}

    totals: dict[str, int] = {}
    if "maximum life" in lower:
        totals["maximum_life"] = value
    if "maximum energy shield" in lower:
        totals["maximum_energy_shield"] = value
    if "fire resistance" in lower:
        totals["fire_resistance"] = value
    if "cold resistance" in lower:
        totals["cold_resistance"] = value
    if "lightning resistance" in lower:
        totals["lightning_resistance"] = value
    if "chaos resistance" in lower:
        totals["chaos_resistance"] = value
    if "all elemental resistances" in lower or "elemental resistances" in lower:
        totals["fire_resistance"] = totals.get("fire_resistance", 0) + value
        totals["cold_resistance"] = totals.get("cold_resistance", 0) + value
        totals["lightning_resistance"] = totals.get("lightning_resistance", 0) + value
    if "all attributes" in lower or "attributes" in lower:
        totals["strength"] = totals.get("strength", 0) + value
        totals["dexterity"] = totals.get("dexterity", 0) + value
        totals["intelligence"] = totals.get("intelligence", 0) + value
    else:
        if "strength" in lower:
            totals["strength"] = value
        if "dexterity" in lower:
            totals["dexterity"] = value
        if "intelligence" in lower:
            totals["intelligence"] = value
    if "suppress spell damage" in lower or "spell suppression" in lower:
        totals["spell_suppression"] = value
    if "movement speed" in lower:
        totals["movement_speed"] = value
    return totals


def likely_affix_generation(categories: list[str], source: str, rarity: str = "") -> str:
    if source in {"implicit", "enchant", "synthesised"}:
        return source
    if source == "unique":
        return "unique_modifier"
    if rarity.casefold() == "unique" and source == "explicit":
        return "unique_modifier"
    category_set = set(categories)
    has_prefix = bool(category_set & PREFIX_CATEGORY_HINTS)
    has_suffix = bool(category_set & SUFFIX_CATEGORY_HINTS)
    if has_suffix and not has_prefix:
        return "suffix"
    if has_prefix and not has_suffix:
        return "prefix"
    if has_prefix and has_suffix:
        return "mixed_or_veiled"
    if source == "crafted":
        return "crafted_unknown"
    if source == "fractured":
        return "fractured_unknown"
    return "unknown"


def parse_item_mod_line(
    line: str,
    *,
    source: str = "explicit",
    rarity: str = "",
    index: int = 0,
) -> dict[str, Any] | None:
    tags, clean = _strip_pob_tags(line)
    clean = clean.strip()
    if not clean:
        return None
    resolved_source = _source_from_tags(tags, source)
    if rarity.casefold() == "unique" and resolved_source == "explicit":
        resolved_source = "unique"
    categories = classify_item_mod_text(clean)
    numeric_totals = extract_item_mod_numeric_totals(clean)
    return {
        "index": index,
        "text": clean,
        "raw_text": line,
        "tags": tags,
        "source": resolved_source,
        "categories": categories,
        "numeric_totals": numeric_totals,
        "likely_affix_generation": likely_affix_generation(categories, resolved_source, rarity),
    }


def parse_item_mod_lines(lines: list[str], *, rarity: str = "") -> list[dict[str, Any]]:
    mods: list[dict[str, Any]] = []
    for idx, line in enumerate(lines):
        parsed = parse_item_mod_line(str(line), rarity=rarity, index=idx)
        if parsed is not None:
            mods.append(parsed)
    return mods


def parse_item_raw_text(raw_text: str, *, rarity_hint: str = "") -> dict[str, Any]:
    lines = [line.strip() for line in str(raw_text or "").splitlines()]
    non_empty = [line for line in lines if line and line != "--------"]
    rarity = rarity_hint
    name = ""
    base_type = ""
    if non_empty and non_empty[0].casefold().startswith("rarity:"):
        rarity = non_empty[0].split(":", 1)[1].strip().title()
    if len(non_empty) > 1:
        name = non_empty[1]
    if len(non_empty) > 2:
        base_type = non_empty[2]

    header_remaining = 3 if non_empty and non_empty[0].casefold().startswith("rarity:") else 0
    implicit_remaining = 0
    mods: list[dict[str, Any]] = []
    non_empty_seen = 0
    for line in lines:
        if line and line != "--------":
            non_empty_seen += 1
        if non_empty_seen <= header_remaining:
            continue
        if line in ITEM_TEXT_SKIP_LINES:
            continue
        if any(line.startswith(prefix) for prefix in ITEM_TEXT_SKIP_PREFIXES):
            continue
        if line.startswith("Implicits:"):
            implicit_remaining = _first_signed_int(line) or 0
            continue
        tags, clean = _strip_pob_tags(line)
        if not clean:
            continue
        source = _source_from_tags(tags, "explicit")
        if source == "explicit" and implicit_remaining > 0:
            source = "implicit"
            implicit_remaining -= 1
        parsed = parse_item_mod_line(
            line,
            source=source,
            rarity=rarity,
            index=len(mods),
        )
        if parsed is not None:
            mods.append(parsed)

    return {
        "rarity": rarity,
        "name": name,
        "base_type": base_type,
        "mods": mods,
        "line_count": len(lines),
    }


def summarize_item_mods(mods: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    generation_counts: dict[str, int] = {}
    numeric_totals: dict[str, int] = {key: 0 for key in NUMERIC_TOTAL_KEYS}

    for mod in mods:
        source = str(mod.get("source") or "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
        generation = str(mod.get("likely_affix_generation") or "unknown")
        generation_counts[generation] = generation_counts.get(generation, 0) + 1
        for category in mod.get("categories") or []:
            category_counts[category] = category_counts.get(category, 0) + 1
        for key, value in (mod.get("numeric_totals") or {}).items():
            if key in numeric_totals:
                numeric_totals[key] += int(value or 0)

    return {
        "mod_count": len(mods),
        "source_counts": dict(sorted(source_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "likely_generation_counts": dict(sorted(generation_counts.items())),
        "numeric_totals": {key: value for key, value in numeric_totals.items() if value != 0},
    }


__all__ = [
    "classify_item_mod_text",
    "extract_item_mod_numeric_totals",
    "likely_affix_generation",
    "parse_item_mod_line",
    "parse_item_mod_lines",
    "parse_item_raw_text",
    "summarize_item_mods",
]
