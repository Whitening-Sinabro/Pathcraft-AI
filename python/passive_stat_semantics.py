# -*- coding: utf-8 -*-
"""Recover readable passive stat semantics from skilltree export text."""

from __future__ import annotations

import re
from typing import Any


STAT_CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("life", ("life",)),
    ("energy_shield", ("energy shield",)),
    ("ward", ("ward",)),
    ("armour", ("armour",)),
    ("evasion", ("evasion",)),
    ("suppression", ("suppress",)),
    ("block", ("block",)),
    ("resistance", ("resistance", "resistances")),
    ("maximum_resistance", ("maximum fire resistance", "maximum cold resistance", "maximum lightning resistance", "maximum elemental resistance", "maximum chaos resistance", "maximum resistance")),
    ("fire", ("fire", "ignite", "burning")),
    ("cold", ("cold", "freeze", "frozen", "chill")),
    ("lightning", ("lightning", "shock")),
    ("chaos", ("chaos", "poison", "wither")),
    ("physical", ("physical",)),
    ("elemental", ("elemental",)),
    ("damage", ("damage", "dps")),
    ("damage_over_time", ("damage over time", "dot")),
    ("attack", ("attack", "attacks")),
    ("spell", ("spell", "spells")),
    ("minion", ("minion", "minions", "spectre", "spectres", "zombie", "raging spirit", "phantasm")),
    ("weapon", ("weapon", "weapons", "sword", "axe", "mace", "staff", "dagger", "claw", "bow", "wand")),
    ("melee", ("melee",)),
    ("projectile", ("projectile", "projectiles")),
    ("critical", ("critical", "crit")),
    ("speed", ("speed",)),
    ("penetration", ("penetrates", "penetration")),
    ("ailment", ("ailment", "ailments", "ignite", "shock", "freeze", "chill", "bleed", "poison")),
    ("bleed", ("bleed", "bleeding")),
    ("poison", ("poison",)),
    ("ignite", ("ignite", "burning")),
    ("shock", ("shock",)),
    ("freeze_chill", ("freeze", "frozen", "chill")),
    ("recovery", ("recover", "recovery", "restore", "restoration", "regenerate", "regeneration", "leech")),
    ("leech", ("leech",)),
    ("regeneration", ("regenerate", "regeneration")),
    ("mana", ("mana",)),
    ("reservation", ("reservation", "reserved", "reserve")),
    ("aura", ("aura", "auras")),
    ("curse", ("curse", "curses", "hex")),
    ("charge", ("charge", "charges", "power charge", "frenzy charge", "endurance charge")),
    ("flask", ("flask", "flasks")),
    ("attribute", ("strength", "dexterity", "intelligence", "attributes")),
    ("movement", ("movement",)),
    ("warcry", ("warcry", "warcried")),
    ("totem", ("totem", "totems")),
    ("brand", ("brand", "brands")),
    ("trap_mine", ("trap", "traps", "mine", "mines")),
    ("explosion", ("explode", "explodes", "explosion")),
    ("gem", ("gem", "gems")),
]

NUMBER_RE = re.compile(r"(?<![\d.])-?\d+(?:\.\d+)?(?![\d.])")


def classify_stat_text(text: str) -> list[str]:
    """Return deterministic coarse categories for a passive stat line."""
    lower = str(text or "").casefold()
    categories: list[str] = []
    for category, needles in STAT_CATEGORY_RULES:
        if any(needle in lower for needle in needles):
            categories.append(category)
    return categories


def _line_contains_value(line: str, value: int) -> bool:
    if value == 0:
        return False
    wanted = str(abs(value))
    for match in NUMBER_RE.finditer(line):
        raw = match.group(0)
        try:
            number = float(raw)
        except ValueError:
            continue
        if number.is_integer() and str(abs(int(number))) == wanted:
            return True
    return False


def _align_stat_texts(
    stat_values: list[dict[str, int]],
    display_stats: list[str],
) -> list[dict[str, Any]]:
    used: set[int] = set()
    aligned: list[dict[str, Any]] = []
    for idx, stat in enumerate(stat_values):
        value = int(stat.get("value") or 0)
        text = None
        for line_index, line in enumerate(display_stats):
            if line_index in used:
                continue
            if _line_contains_value(line, value):
                text = line
                used.add(line_index)
                break
        if text is None and len(display_stats) == len(stat_values) and idx < len(display_stats) and idx not in used:
            text = display_stats[idx]
            used.add(idx)
        if text is None and len(display_stats) == 1 and len(stat_values) == 1:
            text = display_stats[0]
            used.add(0)
        aligned.append({
            "stats_key": stat.get("stats_key"),
            "value": value,
            "text": text,
            "categories": classify_stat_text(text or ""),
            "text_match": "matched" if text else "unresolved",
        })
    return aligned


def passive_node_stat_semantics(
    *,
    graph_id: int | str,
    stat_values: list[dict[str, int]] | None,
    tree_node: dict[str, Any] | None,
) -> dict[str, Any]:
    display_stats = [
        str(line)
        for line in ((tree_node or {}).get("stats") or [])
        if str(line).strip()
    ]
    stat_values = stat_values or []
    stat_semantics = _align_stat_texts(stat_values, display_stats)
    categories: list[str] = []
    for line in display_stats:
        for category in classify_stat_text(line):
            if category not in categories:
                categories.append(category)
    return {
        "graph_id": graph_id,
        "display_stats": display_stats,
        "stat_semantics": stat_semantics,
        "stat_categories": categories,
        "stat_text_source": "skilltree-export:data.json:nodes.stats" if display_stats else "none",
        "stats_key_resolution": (
            "aligned_by_value_or_fallback"
            if stat_semantics
            else "no_numeric_stats_keys"
            if display_stats
            else "no_display_stats"
        ),
    }


__all__ = ["classify_stat_text", "passive_node_stat_semantics"]
