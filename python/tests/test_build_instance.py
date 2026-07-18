# -*- coding: utf-8 -*-
"""BuildInstance normalization tests."""

from __future__ import annotations

import sys
import base64
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_instance import build_instance_from_pob_data  # noqa: E402
from recommend_from_pob import load_build_data_from_pob_url  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent


def _make_synthetic_tree_token(node_ids: list[int], mastery_effects: dict[int, int] | None = None) -> str:
    mastery_effects = mastery_effects or {}
    payload = bytearray()
    payload.extend(struct.pack(">I", 6))
    payload.extend(bytes([5, 2, 0, len(node_ids)]))
    for node_id in node_ids:
        payload.extend(struct.pack(">H", node_id))
    payload.append(0)
    payload.append(len(mastery_effects))
    for node_id, effect_id in mastery_effects.items():
        payload.extend(struct.pack(">H", effect_id))
        payload.extend(struct.pack(">H", node_id))
    return base64.urlsafe_b64encode(bytes(payload)).decode("ascii").rstrip("=")


def test_build_instance_from_sample_pob_splits_identity_gems_tree_and_calcs():
    sample_xml = ROOT / "data" / "samples" / "recommendation_runner_sample.xml"
    build_data = load_build_data_from_pob_url(sample_xml.as_uri())

    instance = build_data["build_instance"]

    assert instance["identity"]["class"] == "Ranger"
    assert instance["identity"]["ascendancy"] == "Deadeye"
    assert instance["identity"]["level"] == 90
    assert instance["gem_state"]["main_skill_group"]["active_gem"] == "Lightning Arrow"
    assert instance["gem_state"]["main_skill_group"]["support_gems"] == [
        "Trinity Support",
        "Inspiration Support",
        "Returning Projectiles Support",
    ]
    assert any(
        group["active_gem"] == "Rain of Arrows" and group["source"] == "alternate"
        for group in instance["gem_state"]["skill_groups"]
    )
    assert instance["tree_state"]["active_tree_url"].endswith("/sample")
    assert instance["calc_state"]["dps"] == 4000000
    assert instance["calc_state"]["flags"]["elemental_res_capped"] is True
    assert "average_t16_clear_time_seconds" in instance["lenses"]["t16_readiness_inputs"]["missing_runtime_inputs"]


def test_build_instance_connects_rare_bases_to_ggpk_affix_context_and_tracks_unique_pressure():
    build_data = {
        "meta": {
            "build_name": "Scion Reliquarian Lvl 92",
            "class": "Scion",
            "ascendancy": "Reliquarian",
            "pob_link": "file:///sample.xml",
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
            "stage_name": "Final Build",
            "passive_tree_url": "https://www.pathofexile.com/passive-skill-tree/"
            + _make_synthetic_tree_token([30439, 18663, 26725], mastery_effects={30439: 678}),
            "gem_setups": {
                "Main": {"links": "Herald of Thunder - Lightning Penetration Support - Elemental Focus Support"}
            },
            "gear_recommendation": {
                "Ring 1": {
                    "name": "Storm Secret",
                    "rarity": "Unique",
                    "base_type": "Topaz Ring",
                    "mods": ["Take 250 Lightning Damage when Herald of Thunder Hits an Enemy"],
                },
                "Ring 2": {"name": "Storm Secret", "rarity": "Unique", "base_type": "Topaz Ring", "mods": []},
                "Body Armour": {
                    "name": "Rare Vaal Regalia",
                    "rarity": "Rare",
                    "base_type": "Vaal Regalia",
                    "mods": [
                        "+120 to maximum Life",
                        "+45% to Fire Resistance",
                        "{crafted}+35% to Cold Resistance",
                        "12% chance to Suppress Spell Damage",
                    ],
                },
                "Weapon 1": {
                    "name": "Rare Pneumatic Dagger",
                    "rarity": "Rare",
                    "base_type": "Pneumatic Dagger",
                    "mods": ["Adds 10 to 20 Lightning Damage to Attacks"],
                },
            },
        }],
    }

    instance = build_instance_from_pob_data(build_data)
    slots = {item["slot"]: item for item in instance["item_state"]["slots"]}

    assert instance["item_state"]["gear_pressure"]["unique_jewellery_slots"] == ["Ring 1", "Ring 2"]
    assert instance["gem_state"]["main_skill_group"]["active_gem"] == "Herald of Thunder"
    assert instance["gem_state"]["main_skill_group"]["role"] == "reservation_damage"
    assert slots["Ring 1"]["ggpk_mod_context"]["join_status"] == "unique_slot_locked"
    assert slots["Ring 1"]["mod_state"][0]["likely_affix_generation"] == "unique_modifier"
    assert slots["Body Armour"]["ggpk_mod_context"]["join_status"] == "resolved"
    assert slots["Body Armour"]["ggpk_mod_context"]["affix_candidate_counts"]["prefix"] > 0
    assert "body_armour" in slots["Body Armour"]["ggpk_mod_context"]["effective_tags"]
    assert slots["Body Armour"]["mod_summary"]["numeric_totals"]["maximum_life"] == 120
    assert slots["Body Armour"]["mod_summary"]["numeric_totals"]["fire_resistance"] == 45
    assert slots["Body Armour"]["mod_summary"]["numeric_totals"]["cold_resistance"] == 35
    assert slots["Body Armour"]["mod_summary"]["numeric_totals"]["spell_suppression"] == 12
    assert slots["Body Armour"]["affix_pressure"]["likely_suffix_mods"] == 3
    assert slots["Body Armour"]["affix_pressure"]["candidate_pool_status"] == "suffix_pool_available"
    assert slots["Weapon 1"]["ggpk_mod_context"]["affix_candidate_counts"]["suffix"] > 0
    assert "dagger" in slots["Weapon 1"]["ggpk_mod_context"]["effective_tags"]
    assert instance["lenses"]["gear_pressure"]["suffix_pressure_signals"]["unique_jewellery_slots"] == 2
    assert instance["item_state"]["mod_summary"]["numeric_totals"]["maximum_life"] == 120
    assert instance["item_state"]["gear_pressure"]["rare_likely_suffix_mods"] >= 3
    assert instance["readiness"]["defense"]["status"] == "blocked_until_verified"
    assert "storm_secret_self_damage_without_recovery_signal:2" in instance["readiness"]["defense"]["reasons"]
    assert instance["readiness"]["bossing"]["status"] == "blocked_until_verified"
    assert "missing_explicit_boss_shock_starter" in instance["readiness"]["bossing"]["reasons"]
    assert instance["readiness"]["mapping"]["status"] == "unknown_runtime_inputs"
    assert instance["tree_state"]["parse_status"] == "decoded_and_mapped_official_tree_url"
    assert instance["tree_state"]["allocated_passives"] == ["30439", "18663", "26725"]
    assert instance["tree_state"]["notables"][0]["node_id"] == "30439"
    assert instance["tree_state"]["notables"][0]["name"] == "Lava Lash"
    assert "fire" in instance["tree_state"]["notables"][0]["stat_categories"]
    assert "attack" in instance["tree_state"]["notables"][0]["stat_categories"]
    assert instance["tree_state"]["keystones"][0]["node_id"] == "18663"
    assert instance["tree_state"]["keystones"][0]["name"] == "Minion Instability"
    assert "minion" in instance["tree_state"]["keystones"][0]["stat_categories"]
    assert instance["tree_state"]["jewel_sockets"] == [{"node_id": "26725", "name": "Basic Jewel Socket", "id": "jewel_slot1956"}]
    assert instance["tree_state"]["stat_category_counts"]["fire"] >= 1
    assert instance["tree_state"]["stat_category_counts"]["damage"] >= 1
    assert instance["tree_state"]["masteries"] == [{
        "node_id": "30439",
        "effect_id": "678",
        "node_name": "Lava Lash",
        "node_found": True,
    }]
    assert instance["tree_state"]["graph_summary"]["class_start_id"] == "61525"
    assert instance["tree_state"]["graph_summary"]["allocated_count"] == 3
