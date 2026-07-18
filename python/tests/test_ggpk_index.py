# -*- coding: utf-8 -*-
"""Unified GGPK + derived DB index tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game_data_provider import GameData  # noqa: E402
from ggpk_index import GGPKIndex  # noqa: E402


def test_catalog_contains_raw_and_derived_dbs():
    index = GGPKIndex(game="poe1")
    catalog = index.build_catalog()

    assert catalog["games"]["poe1"]["tables"]["BaseItemTypes"]["rows"] > 0
    assert catalog["games"]["poe2"]["tables"]["SkillGems"]["rows"] > 0
    assert "valid_gems.json" in catalog["derived"]
    assert "unique_tiers.json" in catalog["derived"]
    assert "atlas_farming_knowledge.json" in catalog["derived"]
    assert catalog["derived"]["gem_taxonomy_adversarial_audit.latest.json"]["kind"] == "gems"
    assert catalog["derived"]["poe1_season_research_3_29_reliquarian.json"]["kind"] == "season_research"
    assert catalog["derived"]["poe1_reliquarian_build_shells_3_29.json"]["kind"] == "season_research"
    assert catalog["derived"]["ggpk_derived/poe1_item_mod_derivation_manifest.json"]["kind"] == "items_and_mods"
    assert catalog["derived"]["builds/scion_reliquarian_hot_autobomber_3_29.profile.json"]["kind"] == "builds"
    assert catalog["derived"]["patch_notes/patch_3_29_0.json"]["kind"] == "patch_notes"
    assert catalog["derived"]["patch_notes/poe1_3_27_3_29_patch_history_context.json"]["kind"] == "patch_notes"
    assert catalog["derived"]["patch_notes/poe1_3_29_0_patch_delta_index.json"]["kind"] == "patch_notes"
    assert catalog["derived"]["patch_notes/poe1_3_29_0_early_patch_adjustment_policy.json"]["kind"] == "patch_notes"
    assert catalog["derived"]["poe1_3_29_information_intake_plan.json"]["kind"] == "operations"


def test_poe1_gem_and_unique_lookup_uses_derived_mapping():
    index = GGPKIndex(game="poe1")

    fireball = index.get_gem("Fireball")
    assert fireball is not None
    assert fireball["name"] == "Fireball"
    assert fireball["valid_gem"] is True
    assert fireball["metadata_id"] == "Metadata/Items/Gems/SkillGemFireball"
    assert fireball["required_level"] == 5

    tabula = index.get_item("Tabula Rasa")
    assert tabula is not None
    assert tabula["name"] == "Tabula Rasa"
    assert tabula["unique_base"] == "Simple Robe"
    assert tabula["base_type"] == "Simple Robe"


def test_poe2_branch_uses_poe2_tables_and_derived_uniques():
    index = GGPKIndex(game="poe2")

    twister = index.get_gem("Twister")
    assert twister is not None
    assert twister["valid_gem"] is True
    assert twister["source"].startswith("poe2:")

    unique = index.get_item("Ab Aeterno")
    assert unique is not None
    assert unique["source"] == "poe2:uniques_poe2"


def test_mod_and_passive_lookup_are_available():
    index = GGPKIndex(game="poe1")

    mods = index.find_mods("Strength1")
    assert mods
    assert mods[0]["Id"] == "Strength1"

    passives = index.find_passives("Resolute Technique")
    assert passives
    assert any(p.get("IsKeystone") for p in passives)

    lava_lash = index.get_passive_by_graph_id(30439)
    assert lava_lash is not None
    assert lava_lash["name"] == "Lava Lash"
    assert lava_lash["is_notable"] is True
    assert lava_lash["stats"]
    assert "30% increased Fire Damage with Attack Skills" in lava_lash["display_stats"]
    by_stat_key = {row["stats_key"]: row for row in lava_lash["stat_semantics"]}
    assert by_stat_key[6149]["text"] == "30% increased Fire Damage with Attack Skills"
    assert by_stat_key[3955]["text"] == "Damage with Weapons Penetrates 8% Fire Resistance"
    assert {"damage", "fire", "attack", "penetration"}.issubset(set(lava_lash["stat_categories"]))

    armour_display = index.get_passive_by_graph_id(36489)
    assert armour_display is not None
    assert armour_display["name"] == "Armour Display"
    assert armour_display["source"] == "poe1:PassiveSkills"

    # URL node ids are unsigned u16; GGPK can store the same graph id signed.
    signed_lookup = index.get_passive_by_graph_id(33919)  # 33919 - 65536 = -31617
    assert signed_lookup is not None
    assert signed_lookup["graph_id"] == -31617


def test_item_mod_candidates_are_resolved_from_base_tags_and_inferred_class_tags():
    index = GGPKIndex(game="poe1")

    dagger = index.get_item_mod_candidates("Pneumatic Dagger", item_level=100)
    assert dagger is not None
    assert "weapon" in dagger["item"]["effective_tags"]
    assert "dagger" in dagger["item"]["effective_tags"]
    suffix_names = {row["name"] for row in dagger["mods"]["suffix"]}
    assert "of Celebration" in suffix_names

    body = index.get_item_mod_candidates("Vaal Regalia", item_level=100)
    assert body is not None
    assert "body_armour" in body["item"]["effective_tags"]
    prefix_names = {row["name"] for row in body["mods"]["prefix"]}
    assert "Fecund" in prefix_names


def test_game_data_provider_includes_integrated_context():
    gd = GameData(game="poe1")
    build = {
        "meta": {"class": "Witch"},
        "items": [{"rarity": "Unique", "name": "Tabula Rasa"}],
        "progression_stages": [{
            "gem_setups": {
                "Fireball": {"links": "Fireball - Combustion Support"}
            },
            "gear_recommendation": {
                "Body Armour": {
                    "rarity": "Rare",
                    "name": "Rare Vaal Regalia",
                    "base_type": "Vaal Regalia",
                    "mods": [
                        "+120 to maximum Life",
                        "+45% to Fire Resistance",
                        "12% chance to Suppress Spell Damage",
                    ],
                }
            },
        }],
    }

    context = gd.build_context_for_coach(build)
    assert "통합 GGPK/기존 DB 조회 결과" in context
    assert "Tabula Rasa" in context
    assert "Fireball" in context
    assert "Combustion Support" in context

    marker = "통합 GGPK/기존 DB 조회 결과 (raw game_data + derived data; 확인된 사실만 사용):"
    payload_text = context.split(marker, 1)[1].strip()
    payload = json.loads(payload_text)
    assert payload["catalog"]["raw_tables"]["BaseItemTypes"] > 0
    assert "valid_gems.json" in payload["catalog"]["derived_dbs"]
    assert payload["build_instance_coach_brief"]["main_skill"] == "Fireball"
    assert payload["build_instance_coach_brief"]["gear_numeric_totals"]["maximum_life"] == 120
    assert payload["build_instance_coach_brief"]["rare_likely_suffix_mods"] == 2
    assert payload["build_instance_summary"]["identity"]["class"] == "Witch"
    assert payload["build_instance_summary"]["main_skill_group"]["active_gem"] == "Fireball"
    assert payload["build_instance_summary"]["raw_available"] is False
    assert payload["build_instance_summary"]["item_mod_summary"]["numeric_totals"]["maximum_life"] == 120
    assert payload["build_instance_summary"]["item_mod_summary"]["numeric_totals"]["fire_resistance"] == 45
    assert payload["build_instance_summary"]["item_mod_summary"]["numeric_totals"]["spell_suppression"] == 12
    assert payload["build_instance_summary"]["slot_mod_summaries"][0]["slot"] == "Body Armour"
    assert payload["build_instance_summary"]["slot_mod_summaries"][0]["affix_pressure"]["likely_suffix_mods"] == 2
