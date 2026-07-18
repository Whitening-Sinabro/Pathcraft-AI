# -*- coding: utf-8 -*-
"""Deterministic BuildInstance readiness screening tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_instance import build_instance_from_pob_data  # noqa: E402


def test_readiness_flags_storm_secret_hot_autobomber_gates():
    build_data = {
        "meta": {
            "build_name": "Scion Reliquarian Lvl 92",
            "class": "Scion",
            "ascendancy": "Reliquarian",
            "version": "3.29",
            "has_xml_stats": True,
        },
        "stats": {
            "dps": 1200000,
            "life": 4300,
            "energy_shield": 900,
            "ehp": 5200,
            "resistances": {"fire": 75, "cold": 75, "lightning": 75, "chaos": -20},
        },
        "progression_stages": [{
            "gem_setups": {
                "Main": {"links": "Herald of Thunder - Lightning Penetration Support"},
            },
            "gear_recommendation": {
                "Ring 1": {
                    "name": "Storm Secret",
                    "rarity": "Unique",
                    "base_type": "Topaz Ring",
                    "mods": ["Take 250 Lightning Damage when Herald of Thunder Hits an Enemy"],
                },
                "Ring 2": {
                    "name": "Storm Secret",
                    "rarity": "Unique",
                    "base_type": "Topaz Ring",
                    "mods": ["Take 250 Lightning Damage when Herald of Thunder Hits an Enemy"],
                },
                "Body Armour": {
                    "name": "Rare Vaal Regalia",
                    "rarity": "Rare",
                    "base_type": "Vaal Regalia",
                    "mods": [
                        "+120 to maximum Life",
                        "+45% to Fire Resistance",
                        "12% chance to Suppress Spell Damage",
                    ],
                },
            },
        }],
    }

    instance = build_instance_from_pob_data(build_data)
    readiness = instance["readiness"]

    assert readiness["shell"]["tags"] == [
        "scion_reliquarian",
        "herald_of_thunder",
        "hot_autobomber_candidate",
        "double_storm_secret",
    ]
    assert readiness["defense"]["status"] == "blocked_until_verified"
    assert "partial_spell_suppression_from_gear:12" in readiness["defense"]["reasons"]
    assert "storm_secret_self_damage_without_recovery_signal:2" in readiness["defense"]["reasons"]
    assert readiness["gear"]["status"] == "caution"
    assert "high_unique_jewellery_suffix_pressure:Ring 1,Ring 2" in readiness["gear"]["reasons"]
    assert readiness["bossing"]["status"] == "blocked_until_verified"
    assert "missing_explicit_boss_shock_starter" in readiness["bossing"]["reasons"]
    assert readiness["mapping"]["status"] == "unknown_runtime_inputs"
    assert readiness["mapping"]["phase_screen"] == "red_map_candidate_screen"
    assert readiness["overall"]["status"] == "blocked_until_verified"


def test_readiness_boss_gate_relaxes_when_storm_brand_starter_exists():
    build_data = {
        "meta": {"build_name": "Scion Reliquarian Lvl 92", "class": "Scion", "ascendancy": "Reliquarian"},
        "stats": {
            "dps": 1200000,
            "life": 5000,
            "energy_shield": 1200,
            "ehp": 6200,
            "resistances": {"fire": 75, "cold": 75, "lightning": 75, "chaos": 20},
        },
        "progression_stages": [{
            "gem_setups": {
                "Main": {"links": "Herald of Thunder - Lightning Penetration Support"},
                "Boss Shock Starter": {"links": "Storm Brand - Faster Casting Support"},
            },
            "gear_recommendation": {
                "Ring 1": {
                    "name": "Storm Secret",
                    "rarity": "Unique",
                    "base_type": "Topaz Ring",
                    "mods": ["Take 250 Lightning Damage when Herald of Thunder Hits an Enemy"],
                },
                "Body Armour": {
                    "name": "Rare Vaal Regalia",
                    "rarity": "Rare",
                    "base_type": "Vaal Regalia",
                    "mods": ["+120 to maximum Life", "Regenerate 100 Life per second"],
                },
            },
        }],
    }

    readiness = build_instance_from_pob_data(build_data)["readiness"]

    assert readiness["bossing"]["status"] == "caution"
    assert "boss_shock_starter_present_but_uptime_unmeasured" in readiness["bossing"]["reasons"]
    assert "missing_explicit_boss_shock_starter" not in readiness["bossing"]["reasons"]
