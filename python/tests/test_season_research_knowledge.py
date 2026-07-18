# -*- coding: utf-8 -*-
"""Season research DB integrity tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_coach import build_season_research_context  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
RESEARCH_PATH = ROOT / "data" / "poe1_season_research_3_29_reliquarian.json"
SHELL_PATH = ROOT / "data" / "poe1_reliquarian_build_shells_3_29.json"


def _load_research() -> dict:
    return json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))


def _load_shells() -> dict:
    return json.loads(SHELL_PATH.read_text(encoding="utf-8"))


def test_reliquarian_research_has_required_lenses():
    data = _load_research()

    assert data["dataset_kind"] == "poe1_season_research"
    assert data["league"]["patch"] == "3.29"
    assert data["league"]["research_status"] == "pre_patch_notes_hypothesis"

    lenses = data["lenses"]
    assert lenses["official_node_lens"]
    assert lenses["skill_fact_lens"]
    assert lenses["offensive_gem_lens"]
    assert lenses["support_gem_lens"]
    assert lenses["farming_lens"]
    assert lenses["candidate_branch_lens"]
    assert lenses["uncertainty_lens"]

    branch_ids = {row["branch_id"] for row in lenses["candidate_branch_lens"]}
    assert {
        "hot_autobomber",
        "static_strike_ngamahu",
        "gloomfang_bow",
        "black_cane_arakaali_spell_hybrid",
        "blight_of_contagion_fallback",
    } <= branch_ids


def test_reliquarian_shell_research_keeps_autobomber_constraints_explicit():
    data = _load_shells()

    assert data["dataset_kind"] == "poe1_reliquarian_build_shell_research"
    shell_by_id = {row["id"]: row for row in data["shells"]}
    assert "dawnbreaker_fire_conversion_defense" in shell_by_id
    assert shell_by_id["dawnbreaker_fire_conversion_defense"]["priority"] == "very_high"
    assert shell_by_id["dawnbreaker_fire_conversion_defense"]["entry_path"]["primary_entry"] == "left_9_oclock"
    assert shell_by_id["apostate_life_stacking_shell"]["entry_path"]["primary_entry"] == "left_9_oclock"
    assert "t16_math_required" in shell_by_id["apostate_life_stacking_shell"]["coach_tags"]
    assert any("-1080" in line for line in shell_by_id["apostate_life_stacking_shell"]["breakpoints"])
    assert shell_by_id["arakaali_poison_attack_shell"]["entry_path"]["direct_from_center"] is False
    assert shell_by_id["arakaali_poison_attack_shell"]["entry_path"]["requires_prior_side_path"] is True
    assert shell_by_id["black_cane_phantasmal_might_spell_shell"]["entry_path"]["allowed_prior_paths"] == [
        "left_9_oclock",
        "right_3_oclock",
    ]
    assert "hot_autobomber_unproven" in shell_by_id["fidelitas_attack_herald_shock_shell"]["coach_tags"]
    assert "not_autobomber_core" in shell_by_id["al_dhih_warcry_explode_niche"]["coach_tags"]
    assert "warcry-gated" in data["autobomber_relevance"]["warcry_explode_verdict"]
    assert any(item["id"] == "top_not_direct_from_center" for item in data["global_constraints"])
    assert data["t16_average_mapping_lens"]["required_inputs"] == [
        "passive_tree_state",
        "item_state",
        "map_mod_policy",
        "player_operation_load",
        "single_target_patch",
        "recovery_and_ailment_state",
    ]
    t16_gates = {
        row["shell_id"]: row
        for row in data["t16_average_mapping_lens"]["shell_specific_t16_gates"]
    }
    assert "Pneumatic Dagger" in t16_gates["arakaali_poison_attack_shell"]["item_gate"]
    assert "Storm Secret" in t16_gates["fidelitas_attack_herald_shock_shell"]["item_gate"]
    assert "Rathpith Globe" in t16_gates["apostate_life_stacking_shell"]["item_gate"]
    assert data["mod_readiness_lens"]["status"] == "item_mod_candidate_query_available_shell_specific_partial"
    assert {
        "python/ggpk_index.py#get_item_mod_candidates",
        "data/game_data/Mods.json",
    } <= {
        source["path"] for source in data["mod_readiness_lens"]["available_data_sources"]
    }
    shell_mods = {
        row["shell_id"]: row
        for row in data["mod_readiness_lens"]["shell_mod_requirements_draft"]
    }
    assert "maximum fire resistance sources" in shell_mods["dawnbreaker_fire_conversion_defense"]["rare_affix_groups"]
    assert "high Energy Shield prefixes on armour slots" in shell_mods["apostate_life_stacking_shell"]["rare_affix_groups"]
    assert "Pneumatic Dagger or equivalent elemental-to-poison enabler if using elemental attacks" in shell_mods["arakaali_poison_attack_shell"]["mandatory_uniques_or_effects"]
    assert "Storm Secret only for pure Herald of Thunder autobomber variants" in shell_mods["fidelitas_attack_herald_shock_shell"]["mandatory_uniques_or_effects"]


def test_offensive_gem_lens_points_at_local_active_skills():
    data = _load_research()
    active_skills = json.loads((ROOT / "data" / "game_data" / "ActiveSkills.json").read_text(encoding="utf-8"))
    active_ids = {row["Id"] for row in active_skills}

    branch_ids = {row["branch_id"] for row in data["lenses"]["candidate_branch_lens"]}
    offensive_branch_ids = {row["branch_id"] for row in data["lenses"]["offensive_gem_lens"]}
    assert branch_ids <= offensive_branch_ids

    for row in data["lenses"]["offensive_gem_lens"]:
        candidates = []
        for field in (
            "primary_offense_gems",
            "secondary_offense_gems",
            "enabler_offense_gems",
            "carrier_gems",
            "fallback_offense_gems",
            "rejected_or_lower_priority_active_gems",
        ):
            candidates.extend(row.get(field, []))
        assert candidates, row["branch_id"]
        for candidate in candidates:
            active_id = candidate.get("local_active_skill_id")
            if active_id:
                assert active_id in active_ids, f"{active_id} missing for {candidate['skill']}"

    static_branch = next(row for row in data["lenses"]["offensive_gem_lens"] if row["branch_id"] == "static_strike_ngamahu")
    molten = next(row for row in static_branch["secondary_offense_gems"] if row["skill"] == "Molten Burst")
    assert molten["socketable_gem"] is False


def test_support_candidates_are_valid_poe1_support_gems():
    data = _load_research()
    valid_data = json.loads((ROOT / "data" / "valid_gems.json").read_text(encoding="utf-8"))
    valid_gems = set(valid_data["gems"])

    for row in data["lenses"]["support_gem_lens"]:
        candidates = row.get("safe_candidate_supports", []) + row.get("conditional_candidate_supports", [])
        assert candidates, row["branch_id"]
        for support in candidates:
            assert support in valid_gems, f"{support} missing for {row['branch_id']}"


def test_skill_fact_lens_points_at_local_active_skills():
    data = _load_research()
    active_skills = json.loads((ROOT / "data" / "game_data" / "ActiveSkills.json").read_text(encoding="utf-8"))
    active_ids = {row["Id"] for row in active_skills}

    for row in data["lenses"]["skill_fact_lens"]:
        assert row["local_active_skill_id"] in active_ids
        assert row["active_skill_type_ids"], row["canonical_skill"]

    blight = next(row for row in data["lenses"]["skill_fact_lens"] if row["canonical_skill"] == "Blight of Contagion")
    assert blight["local_active_skill_id"] == "blight_alt_x"
    assert blight["supportability_override"]["state"] == "active_skill_confirmed_but_not_in_local_skillgems_table"


def test_build_coach_season_context_scoped_to_scion_reliquarian():
    build = {
        "meta": {
            "build_name": "Scion Reliquarian test",
            "class": "Scion",
            "ascendancy": "Reliquarian",
        },
        "progression_stages": [{
            "gem_setups": {
                "Herald of Thunder": {"links": "Herald of Thunder - Lightning Penetration Support"}
            }
        }],
    }

    context = build_season_research_context(build)

    assert context["dataset_kind"] == "poe1_season_research"
    assert context["match"]["scoped_character"] is True
    assert "hot_autobomber" in context["match"]["selected_branch_ids"]
    assert any(row["branch_id"] == "hot_autobomber" for row in context["offensive_gem_lens"])
    assert any(
        gem["skill"] == "Herald of Thunder"
        for row in context["offensive_gem_lens"]
        for gem in row.get("primary_offense_gems", [])
    )
    taxonomy_by_name = {row["name"]: row for row in context["gem_taxonomy_lens"]}
    assert taxonomy_by_name["Herald of Thunder"]["gem_kind"] == "active_gem"
    assert taxonomy_by_name["Molten Burst"]["socketable"] is False
    assert taxonomy_by_name["Blight of Contagion"]["gem_kind"] == "active_transfigured_or_valid_active"
    assert any(row["main_skill"] == "Herald of Thunder" for row in context["support_gem_lens"])
    assert "community_build_shell_lens" in context
    shell_by_id = {
        row["id"]: row
        for row in context["community_build_shell_lens"]["shells"]
    }
    assert "dawnbreaker_fire_conversion_defense" in shell_by_id
    assert "hot_autobomber_unproven" in shell_by_id["fidelitas_attack_herald_shock_shell"]["coach_tags"]
    assert context["community_build_shell_lens"]["t16_average_mapping_lens"]["evaluation_metrics"]
    assert context["community_build_shell_lens"]["mod_readiness_lens"]["status"] == "item_mod_candidate_query_available_shell_specific_partial"
    assert context["uncertainty_lens"]


def test_build_coach_season_context_matches_offensive_gem_branch_without_rejected_noise():
    build = {
        "meta": {
            "build_name": "Blight test",
            "class": "Shadow",
            "ascendancy": "Trickster",
        },
        "progression_stages": [{
            "gem_setups": {
                "Blight of Contagion": {"links": "Blight of Contagion - Void Manipulation Support"}
            }
        }],
    }

    context = build_season_research_context(build)

    assert context["match"]["scoped_character"] is False
    assert context["match"]["selected_branch_ids"] == ["blight_of_contagion_fallback"]
    assert "hot_autobomber" not in context["match"]["selected_branch_ids"]


def test_build_coach_season_context_skips_unrelated_builds():
    build = {
        "meta": {
            "build_name": "Unrelated Witch",
            "class": "Witch",
            "ascendancy": "Elementalist",
        },
        "progression_stages": [{
            "gem_setups": {
                "Fireball": {"links": "Fireball - Combustion Support"}
            }
        }],
    }

    assert build_season_research_context(build) == {}
