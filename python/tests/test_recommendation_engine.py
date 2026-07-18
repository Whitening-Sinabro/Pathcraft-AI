# -*- coding: utf-8 -*-
"""End-to-end tests for inferred build-profile recommendation pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recommendation_engine import (  # noqa: E402
    extract_main_skill,
    infer_build_profile,
    recommend_from_build_data,
)


def _make_build(
    *,
    class_name: str,
    ascendancy: str,
    main_label: str,
    main_links: str,
    alt_label: str | None = None,
    alt_links: str | None = None,
    life: int = 4200,
    dps: int = 2_500_000,
    pob_link: str = "https://pobb.in/example",
) -> dict:
    stage = {
        "stage_name": "Final Build",
        "gem_setups": {
            main_label: {"links": main_links, "reasoning": None},
            "Auras": {"links": "Wrath - Grace", "reasoning": None},
            "Guard": {"links": "Steelskin", "reasoning": None},
            "Mobility": {"links": "Flame Dash", "reasoning": None},
        },
        "alternate_gem_sets": {},
        "gear_recommendation": {
            "Weapon 1": {"name": "Early Rare Weapon", "mods": ["Adds Damage"]},
            "Body Armour": {"name": "Late Endgame Armour", "mods": ["+100 Life"]},
        },
        "passive_tree_url": "https://www.pathofexile.com/passive-skill-tree/sample-final",
        "passive_tree_options": [
            {
                "id": "1",
                "title": "Act 3 Tree",
                "url": "https://www.pathofexile.com/passive-skill-tree/sample-act3",
                "active": False,
            },
            {
                "id": "2",
                "title": "Final Tree",
                "url": "https://www.pathofexile.com/passive-skill-tree/sample-final",
                "active": True,
            },
        ],
    }
    if alt_label and alt_links:
        stage["alternate_gem_sets"][alt_label] = {alt_label: {"links": alt_links, "reasoning": None}}
    return {
        "meta": {
            "build_name": f"{class_name} {ascendancy} Lvl 90",
            "class": class_name,
            "ascendancy": ascendancy,
            "pob_link": pob_link,
            "version": "3.25",
        },
        "stats": {
            "dps": dps,
            "life": life,
            "energy_shield": 0,
            "resistances": {"fire": 75, "cold": 75, "lightning": 75, "chaos": 0},
        },
        "progression_stages": [stage],
    }


def _make_user_state(
    *,
    class_name: str = "Ranger",
    ascendancy: str = "Deadeye",
    desired_skill: str = "Lightning Arrow",
    max_input_style: str = "1_click_plus_movement",
    liquid_divines: float = 3.0,
    character_locked: bool = True,
) -> dict:
    return {
        "character_state": {
            "patch": "3.25",
            "class_name": class_name,
            "ascendancy": ascendancy,
            "level": 88,
            "character_locked": character_locked,
        },
        "currency_state": {
            "liquid_divines": liquid_divines,
            "liquid_chaos": 200,
            "owned_uniques": [],
        },
        "preferences": {
            "desired_main_skill": desired_skill,
            "max_input_style": max_input_style,
            "target_contents": ["mapping"],
            "trade_mode": "trade_league_start",
            "death_tolerance": "medium",
            "respec_tolerance_points": 24,
        },
        "constraints": {
            "must_use_skill": desired_skill,
            "forbidden_skills": [],
            "require_confirmed_leveling": False,
            "forbid_reroll": True,
        },
    }


def test_extract_main_skill_prefers_primary_main_setup():
    build = _make_build(
        class_name="Ranger",
        ascendancy="Deadeye",
        main_label="Main Clear",
        main_links="Lightning Arrow - Trinity Support - Inspiration Support - Returning Projectiles Support",
        alt_label="Auras",
        alt_links="Wrath - Grace",
    )

    assert extract_main_skill(build) == "Lightning Arrow"


def test_extract_main_skill_uses_taxonomy_for_herald_damage_setup():
    build = _make_build(
        class_name="Scion",
        ascendancy="Reliquarian",
        main_label="Herald of Thunder",
        main_links="Herald of Thunder - Lightning Penetration Support - Added Lightning Damage Support",
        alt_label="Auras",
        alt_links="Wrath - Grace",
    )

    assert extract_main_skill(build) == "Herald of Thunder"

    profile = infer_build_profile(build)
    assert profile["identity"]["main_skill"] == "Herald of Thunder"
    assert profile["identity"]["damage_tags"] == ["spell"]
    assert profile["availability"]["mandatory_transfigured_gems"] == []


def test_infer_build_profile_keeps_barrage_active_not_support_alias():
    build = _make_build(
        class_name="Ranger",
        ascendancy="Deadeye",
        main_label="Main",
        main_links="Barrage - Added Lightning Damage - Barrage Support",
    )

    profile = infer_build_profile(build)

    assert profile["identity"]["main_skill"] == "Barrage"
    assert profile["identity"]["damage_tags"] == ["attack"]


def test_infer_build_profile_uses_taxonomy_for_transfigured_requirement():
    build = _make_build(
        class_name="Scion",
        ascendancy="Reliquarian",
        main_label="Main",
        main_links="Blight of Contagion - Void Manipulation Support - Efficacy Support",
    )

    profile = infer_build_profile(build)

    assert profile["identity"]["main_skill"] == "Blight of Contagion"
    assert profile["availability"]["mandatory_transfigured_gems"] == ["Blight of Contagion"]


def test_infer_build_profile_exposes_structured_progression_plan():
    build = _make_build(
        class_name="Ranger",
        ascendancy="Deadeye",
        main_label="Main Clear",
        main_links="Lightning Arrow - Trinity Support - Inspiration Support",
        alt_label="Act 2",
        alt_links="Rain of Arrows - Mirage Archer Support - Added Cold Damage Support",
    )

    profile = infer_build_profile(build)

    assert profile["identity"]["main_skill"] == "Lightning Arrow"
    assert profile["identity"]["leveling_skill"] == "Rain of Arrows"
    assert profile["progression"]["leveling_confidence"] == "near_confirmed"
    assert profile["progression"]["campaign_plan"][0]["main_skill"] == "Rain of Arrows"
    assert any(step["stage"] == "final_build" for step in profile["progression"]["aura_plan"])
    assert profile["progression"]["passive_plan"][-1]["tree_url"].endswith("sample-final")
    assert profile["progression"]["gear_stages"]


def test_recommendation_pipeline_prefers_exact_matching_build():
    la_build = _make_build(
        class_name="Ranger",
        ascendancy="Deadeye",
        main_label="Main Clear",
        main_links="Lightning Arrow - Trinity Support - Inspiration Support",
        alt_label="Act 2",
        alt_links="Rain of Arrows - Mirage Archer Support",
        dps=4_000_000,
    )
    boneshatter_build = _make_build(
        class_name="Marauder",
        ascendancy="Juggernaut",
        main_label="Main",
        main_links="Boneshatter - Brutality Support - Fortify Support",
        dps=3_000_000,
        pob_link="https://pobb.in/boneshatter",
    )

    user_state = _make_user_state()
    result = recommend_from_build_data([la_build, boneshatter_build], user_state)

    assert result["recommendation"]["selected_plan"] == "A"
    assert result["recommendation"]["selected_build_name"].startswith("Ranger Deadeye")
    assert result["recommendation"]["selected_build_id"].endswith("lightning_arrow_deadeye")
    assert result["recommendation"]["deterministic_guards"]
    assert result["recommendation"]["verification_loop"]["recommended_plan"] == "A"


def test_recommendation_pipeline_falls_back_to_plan_c_proxy():
    boneshatter_build = _make_build(
        class_name="Marauder",
        ascendancy="Juggernaut",
        main_label="Main",
        main_links="Boneshatter - Brutality Support - Fortify Support",
        dps=3_000_000,
        pob_link="https://pobb.in/boneshatter",
    )

    user_state = _make_user_state(
        class_name="Marauder",
        ascendancy="Juggernaut",
        desired_skill="Lightning Arrow",
        max_input_style="1_click",
        liquid_divines=5.0,
        character_locked=False,
    )
    result = recommend_from_build_data([boneshatter_build], user_state)

    assert result["recommendation"]["selected_plan"] == "C"
    assert result["recommendation"]["selected_build_id"].endswith("boneshatter_juggernaut")
    assert result["recommendation"]["ai_policy"]["mode"] == "proxy_only"
    assert result["recommendation"]["verification_loop"]["loop_state"] == "escalate_to_proxy"


def test_confirmed_leveling_when_coach_payload_is_complete():
    build = _make_build(
        class_name="Templar",
        ascendancy="Hierophant",
        main_label="Main",
        main_links="Shock Nova of Procession - Spell Echo Support - Lightning Penetration Support",
    )
    coach_data = {
        "leveling_skills": {
            "recommended": {
                "name": "Stormblast Mine",
                "links_progression": [
                    {"level_range": "1-8", "gems": ["Stormblast Mine"]},
                    {"level_range": "8-18", "gems": ["Stormblast Mine", "Swift Assembly Support"]},
                ],
            },
            "skill_transitions": [
                {"level": 28, "change": "Stormblast Mine to Shock Nova of Procession", "reason": "core skill online"},
            ],
        },
        "aura_utility_progression": [
            {"phase": "Act 1", "auras": ["Clarity"], "heralds": [], "reservation_total": "34%", "utility": ["Flame Dash"], "guard": "", "reason": "mana sustain"},
            {"phase": "Act 2", "auras": ["Clarity"], "heralds": [], "reservation_total": "34%", "utility": ["Flame Dash"], "guard": "", "reason": "mana sustain"},
            {"phase": "Act 3", "auras": ["Clarity"], "heralds": [], "reservation_total": "34%", "utility": ["Flame Dash"], "guard": "", "reason": "mana sustain"},
            {"phase": "Act 4-6", "auras": ["Wrath"], "heralds": [], "reservation_total": "50%", "utility": ["Flame Dash"], "guard": "Steelskin", "reason": "core damage aura"},
            {"phase": "Act 7-10", "auras": ["Wrath"], "heralds": ["Herald of Thunder"], "reservation_total": "75%", "utility": ["Flame Dash"], "guard": "Steelskin", "reason": "campaign finish"},
        ],
        "variant_snapshots": [
            {"phase": "Act 1-3"},
            {"phase": "Act 4-6"},
            {"phase": "Act 7-10"},
            {"phase": "White Maps"},
            {"phase": "Yellow Maps"},
        ],
        "gear_progression": [
            {
                "slot": "Weapon",
                "phases": [
                    {"phase": "Act 4-6", "item": "Rare Wand", "key_stats": ["spell damage"], "acquisition": "vendor", "priority": "high"},
                    {"phase": "Act 7-10", "item": "+1 Lightning Wand", "key_stats": ["+1 lightning gems"], "acquisition": "craft", "priority": "high"},
                ],
            }
        ],
    }

    profile = infer_build_profile(build, coach_data)

    assert profile["identity"]["leveling_skill"] == "Stormblast Mine"
    assert profile["progression"]["leveling_confidence"] == "confirmed"
    assert profile["progression"]["campaign_plan"][0]["source"] == "coach_data"
    assert any(t["level"] == 28 for t in profile["progression"]["transition_points"])


def test_recommendation_pipeline_blocks_cross_class_proxy_without_explicit_reroll_branch():
    la_build = _make_build(
        class_name="Ranger",
        ascendancy="Deadeye",
        main_label="Main Clear",
        main_links="Lightning Arrow - Trinity Support - Inspiration Support",
        dps=4_000_000,
    )

    user_state = _make_user_state(
        class_name="Templar",
        ascendancy="Hierophant",
        desired_skill="Ball Lightning",
        max_input_style="1_click_plus_movement",
        liquid_divines=40.0,
        character_locked=False,
    )
    result = recommend_from_build_data([la_build], user_state)

    assert result["recommendation"]["selected_plan"] == "D"
    assert result["recommendation"]["response_layers"]["user_message"]["template_id"] == "plan_d_proxy_scope_block"
    assert result["recommendation"]["blocking_candidate"] is not None
