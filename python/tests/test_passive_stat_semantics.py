# -*- coding: utf-8 -*-
"""Passive stat text/category recovery tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passive_stat_semantics import classify_stat_text, passive_node_stat_semantics  # noqa: E402


def test_classify_stat_text_extracts_coarse_lens_categories():
    categories = classify_stat_text("Damage with Weapons Penetrates 8% Fire Resistance")

    assert "damage" in categories
    assert "weapon" in categories
    assert "fire" in categories
    assert "resistance" in categories
    assert "penetration" in categories


def test_passive_node_stat_semantics_aligns_by_numeric_value_before_position():
    semantic = passive_node_stat_semantics(
        graph_id=30439,
        stat_values=[
            {"stats_key": 6149, "value": 30},
            {"stats_key": 3955, "value": 8},
        ],
        tree_node={
            "stats": [
                "Damage with Weapons Penetrates 8% Fire Resistance",
                "30% increased Fire Damage with Attack Skills",
            ],
        },
    )

    by_key = {row["stats_key"]: row for row in semantic["stat_semantics"]}
    assert by_key[6149]["text"] == "30% increased Fire Damage with Attack Skills"
    assert by_key[3955]["text"] == "Damage with Weapons Penetrates 8% Fire Resistance"
    assert "attack" in by_key[6149]["categories"]
    assert "penetration" in by_key[3955]["categories"]
    assert {"damage", "fire", "attack", "penetration"}.issubset(set(semantic["stat_categories"]))
