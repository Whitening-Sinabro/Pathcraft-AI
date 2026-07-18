# -*- coding: utf-8 -*-
"""Regression tests for build-profile progression normalizer."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_profile_normalizer import build_normalized_progression  # noqa: E402


def _make_build() -> dict:
    stage = {
        "stage_name": "Final Build",
        "pob_link": "https://pobb.in/example-la",
        "passive_tree_url": "https://www.pathofexile.com/passive-skill-tree/final",
        "passive_tree_options": [
            {
                "id": "1",
                "title": "LvLing Tree lvl 12",
                "url": "https://www.pathofexile.com/passive-skill-tree/lvl12",
                "active": False,
            },
            {
                "id": "2",
                "title": "Final Tree",
                "url": "https://www.pathofexile.com/passive-skill-tree/final",
                "active": True,
            },
        ],
        "gem_setups": {
            "Main Clear": {
                "links": "Lightning Arrow - Trinity Support - Inspiration Support - Returning Projectiles Support",
                "reasoning": None,
            },
            "Auras": {
                "links": "Wrath - Herald of Ice - Grace",
                "reasoning": None,
            },
            "Guard": {
                "links": "Steelskin - Automation",
                "reasoning": None,
            },
            "Mobility": {
                "links": "Flame Dash",
                "reasoning": None,
            },
        },
        "alternate_gem_sets": {
            "Act 1": {
                "Act Start": {
                    "links": "Caustic Arrow - Pierce Support",
                    "reasoning": None,
                },
                "Aura": {
                    "links": "Precision",
                    "reasoning": None,
                },
            },
            "Act 2": {
                "Act Leveling": {
                    "links": "Rain of Arrows - Mirage Archer Support",
                    "reasoning": None,
                },
                "Utility": {
                    "links": "Flame Dash - Sniper's Mark",
                    "reasoning": None,
                },
            },
            "Lvl70 after 3rd lab": {
                "Transition": {
                    "links": "Lightning Arrow - Trinity Support - Inspiration Support - Returning Projectiles Support",
                    "reasoning": None,
                },
                "Auras": {
                    "links": "Wrath - Grace",
                    "reasoning": None,
                },
                "Guard": {
                    "links": "Steelskin",
                    "reasoning": None,
                },
            },
        },
        "gear_recommendation": {
            "Weapon 1": {
                "name": "Early Rare Bow",
                "mods": ["Adds Lightning Damage"],
            },
            "Body Armour": {
                "name": "Mid Six-Link Armour",
                "mods": ["+90 to maximum Life"],
            },
            "Amulet": {
                "name": "Late Crit Amulet",
                "mods": ["+30% to Global Critical Strike Multiplier"],
            },
        },
    }
    return {
        "meta": {
            "build_name": "Ranger Deadeye Lvl 90",
            "class": "Ranger",
            "ascendancy": "Deadeye",
            "pob_link": "https://pobb.in/example-la",
            "version": "3.25",
        },
        "stats": {
            "dps": 4000000,
            "life": 4300,
            "energy_shield": 0,
            "resistances": {"fire": 75, "cold": 75, "lightning": 75, "chaos": 0},
        },
        "progression_stages": [stage],
    }


def test_normalizer_derives_campaign_aura_passive_and_gear_plans_from_build_data():
    progression = build_normalized_progression(
        _make_build(),
        None,
        leveling_confidence="near_confirmed",
        leveling_skill="Caustic Arrow",
        main_skill="Lightning Arrow",
        transition_points_seed=[],
    )

    assert progression["campaign_plan"][0]["stage"] == "act_1"
    assert progression["campaign_plan"][0]["main_skill"] == "Caustic Arrow"
    assert progression["campaign_plan"][1]["stage"] == "act_2"
    assert progression["campaign_plan"][1]["main_skill"] == "Rain of Arrows"
    assert progression["campaign_plan"][2]["stage"] == "early_maps"
    assert progression["campaign_plan"][2]["main_skill"] == "Lightning Arrow"

    assert progression["aura_plan"][0]["auras"] == ["Precision"]
    assert any(step["stage"] == "final_build" and "Grace" in step["auras"] for step in progression["aura_plan"])

    assert progression["passive_plan"][0]["tree_url"].endswith("lvl12")
    assert progression["passive_plan"][1]["active"] is True
    assert progression["passive_plan"][1]["tree_url"].endswith("final")

    gear_stages = {item["stage"] for item in progression["gear_stages"]}
    assert {"early_maps", "midgame", "late_endgame"}.issubset(gear_stages)

    transitions = progression["transition_points"]
    assert any(t["from_skill"] == "Caustic Arrow" and t["to_skill"] == "Rain of Arrows" for t in transitions)
    assert any(t["from_skill"] == "Rain of Arrows" and t["to_skill"] == "Lightning Arrow" for t in transitions)


def test_normalizer_prefers_coach_campaign_aura_and_gear_data_when_available():
    coach_data = {
        "leveling_skills": {
            "recommended": {
                "name": "Stormblast Mine",
                "links_progression": [
                    {"level_range": "1-11", "gems": ["Stormblast Mine", "Swift Assembly Support"]},
                    {"level_range": "12-27", "gems": ["Arc", "Added Lightning Damage Support"]},
                    {"level_range": "28+", "gems": ["Ball Lightning", "Spell Echo Support"]},
                ],
            }
        },
        "aura_utility_progression": [
            {
                "phase": "Act 1-3",
                "auras": ["Clarity"],
                "heralds": [],
                "utility": ["Flame Dash"],
                "guard": "",
                "reason": "mana sustain",
            },
            {
                "phase": "Act 4-10",
                "auras": ["Wrath"],
                "heralds": ["Herald of Thunder"],
                "utility": ["Flame Dash"],
                "guard": "Steelskin",
                "reason": "final skill online",
            },
        ],
        "gear_progression": [
            {
                "slot": "Weapon",
                "phases": [
                    {
                        "phase": "Act 4-10",
                        "item": "Rare Wand",
                        "key_stats": ["+1 lightning gems"],
                        "acquisition": "vendor recipe",
                        "priority": "high",
                    }
                ],
            }
        ],
        "passive_priority": ["spell damage", "reservation", "life"],
    }

    progression = build_normalized_progression(
        _make_build(),
        coach_data,
        leveling_confidence="confirmed",
        leveling_skill="Stormblast Mine",
        main_skill="Ball Lightning",
        transition_points_seed=[{"level": 28, "change": "Stormblast Mine to Ball Lightning", "reason": "core skill online"}],
    )

    assert progression["campaign_plan"][0]["source"] == "coach_data"
    assert progression["campaign_plan"][0]["main_skill"] == "Stormblast Mine"
    assert progression["aura_plan"][1]["auras"] == ["Wrath", "Herald of Thunder"]
    assert progression["gear_stages"][0]["source"] == "coach_data"
    assert progression["gear_stages"][0]["stage"] == "act_4_10"
    assert progression["passive_plan"][-1]["priorities"] == ["spell damage", "reservation", "life"]
    assert any(t["level"] == 28 and t["to_skill"] == "Ball Lightning" for t in progression["transition_points"])
