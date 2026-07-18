# -*- coding: utf-8 -*-
"""Item mod text normalization tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from item_mod_semantics import parse_item_mod_lines, parse_item_raw_text, summarize_item_mods  # noqa: E402


def test_parse_item_mod_lines_classifies_numeric_defense_and_suffix_pressure():
    mods = parse_item_mod_lines([
        "+120 to maximum Life",
        "+45% to Fire Resistance",
        "{crafted}+35% to Cold Resistance",
        "12% chance to Suppress Spell Damage",
    ], rarity="Rare")

    summary = summarize_item_mods(mods)

    assert mods[0]["likely_affix_generation"] == "prefix"
    assert mods[1]["likely_affix_generation"] == "suffix"
    assert mods[2]["source"] == "crafted"
    assert mods[2]["likely_affix_generation"] == "suffix"
    assert "suppression" in mods[3]["categories"]
    assert summary["numeric_totals"]["maximum_life"] == 120
    assert summary["numeric_totals"]["fire_resistance"] == 45
    assert summary["numeric_totals"]["cold_resistance"] == 35
    assert summary["numeric_totals"]["spell_suppression"] == 12
    assert summary["likely_generation_counts"]["suffix"] == 3


def test_parse_item_raw_text_preserves_implicit_crafted_and_unique_sources():
    parsed = parse_item_raw_text("""Rarity: UNIQUE
Storm Secret
Topaz Ring
--------
Implicits: 1
+25% to Lightning Resistance
--------
Herald of Thunder also creates a storm when you Shock an Enemy
{crafted}+10% to all Elemental Resistances
""")

    mods = parsed["mods"]
    summary = summarize_item_mods(mods)

    assert mods[0]["source"] == "implicit"
    assert mods[0]["numeric_totals"]["lightning_resistance"] == 25
    assert mods[1]["source"] == "unique"
    assert mods[1]["likely_affix_generation"] == "unique_modifier"
    assert mods[2]["source"] == "crafted"
    assert summary["numeric_totals"]["fire_resistance"] == 10
    assert summary["numeric_totals"]["cold_resistance"] == 10
    assert summary["numeric_totals"]["lightning_resistance"] == 35
