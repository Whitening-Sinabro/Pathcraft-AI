# -*- coding: utf-8 -*-
"""Adversarial checks for POE1 gem taxonomy and downstream consumers.

These tests intentionally attack the failure modes that make build advice look
plausible while using the wrong gem class: support aliases, active/support name
collisions, triggered-only skills, utility setups, and season research context.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_coach import build_season_research_context  # noqa: E402
from build_extractor import detect_build_type, extract_build_gems  # noqa: E402
from gem_taxonomy import (  # noqa: E402
    damage_flags_for,
    get_gem_entry,
    is_active_gem,
    is_support_gem,
    resolve_gem_name,
    weapon_requirements_for,
)
from recommendation_engine import extract_main_skill, infer_build_profile  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "data" / "poe1_gem_taxonomy.latest.json"


def _load_taxonomy() -> dict:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


def _build(gem_setups: dict[str, str], *, class_name: str = "Scion", ascendancy: str = "Reliquarian") -> dict:
    return {
        "meta": {
            "build_name": f"{class_name} {ascendancy} adversarial check",
            "class": class_name,
            "ascendancy": ascendancy,
            "version": "3.29",
        },
        "progression_stages": [{
            "gem_setups": {
                label: {"links": links, "reasoning": None}
                for label, links in gem_setups.items()
            }
        }],
    }


def test_lens_1_source_integrity_support_aliases_are_never_socketable_actives():
    entries = _load_taxonomy()["entries"]

    for name, entry in entries.items():
        kind = entry["gem_kind"]
        alias_target = entry.get("support_alias_of")

        if kind in {"support_alias", "active_skill_only_and_support_alias"}:
            assert alias_target in entries, f"{name} points at missing support alias target"
            assert entries[alias_target]["gem_kind"] == "support_gem", name
            assert entries[alias_target]["socketable"] is True, name
            assert entry["socketable"] is False, name

        if kind == "support_gem":
            assert entry["offense_class"] == "support_not_active", name
            assert alias_target is None, name

        if kind in {"active_gem", "active_transfigured_or_valid_active"}:
            assert alias_target is None, name
            assert entry["socketable"] is True, name


def test_lens_2_name_collision_resolver_keeps_real_active_and_support_aliases_separate():
    assert resolve_gem_name("Barrage") == "Barrage"
    assert resolve_gem_name("Barrage", allow_support_alias=False) == "Barrage"
    assert is_active_gem("Barrage", socketable_only=True)
    assert not is_support_gem("Barrage")

    assert is_support_gem("Barrage Support")
    assert resolve_gem_name("Barrage Support") == "Barrage Support"

    assert resolve_gem_name("Added Lightning Damage") == "Added Lightning Damage Support"
    assert resolve_gem_name("Added Lightning Damage", allow_support_alias=False) is None
    assert not is_active_gem("Added Lightning Damage")

    assert resolve_gem_name("Summon Phantasm") == "Summon Phantasm Support"
    assert resolve_gem_name("Summon Phantasm", allow_support_alias=False) is None
    assert not is_active_gem("Summon Phantasm", socketable_only=True)


def test_lens_3_socketability_blocks_triggered_or_granted_skills_from_main_extraction():
    build = _build({
        "Main": "Static Strike - Shockwave Support - Faster Attacks Support",
        "Trigger Package": "Molten Burst - Greater Multiple Projectiles Support",
        "Minion Trigger": "Raise Spiders - Minion Damage Support",
        "Phantasm Support Alias": "Summon Phantasm - Minion Damage Support",
    })

    skills, supports = extract_build_gems(build)

    assert extract_main_skill(build) == "Static Strike"
    assert detect_build_type(build) == "attack"
    assert "Static Strike" in skills
    assert "Molten Burst" not in skills
    assert "Raise Spiders" not in skills
    assert "Summon Phantasm" not in skills
    assert "Summon Phantasm Support" in supports


def test_lens_4_contextual_main_skill_scoring_resists_utility_and_support_noise():
    build = _build(
        {
            "Auras": "Wrath - Grace - Herald of Thunder - Added Lightning Damage",
            "Movement": "Flame Dash - Arcane Surge",
            "Guard": "Steelskin - Increased Duration Support",
            "Main Clear": "Barrage - Added Lightning Damage - Barrage Support",
        },
        class_name="Ranger",
        ascendancy="Deadeye",
    )

    assert extract_main_skill(build) == "Barrage"
    assert detect_build_type(build) == "attack"

    profile = infer_build_profile(build)
    assert profile["identity"]["main_skill"] == "Barrage"
    assert profile["identity"]["damage_tags"] == ["attack"]
    assert "Bows" in weapon_requirements_for("Barrage")
    assert damage_flags_for("Barrage")["attack"] is True


def test_lens_5_season_research_context_must_cross_check_taxonomy_before_ai_explanation():
    build = _build({
        "Herald of Thunder": "Herald of Thunder - Lightning Penetration Support - Added Lightning Damage Support",
        "Static Strike Carrier": "Static Strike - Shockwave Support - Faster Attacks Support",
        "Blight Fallback": "Blight of Contagion - Void Manipulation Support - Efficacy Support",
    })

    context = build_season_research_context(build)

    assert context["match"]["scoped_character"] is True
    assert {
        "hot_autobomber",
        "static_strike_ngamahu",
        "blight_of_contagion_fallback",
    } <= set(context["match"]["selected_branch_ids"])

    taxonomy_by_name = {row["name"]: row for row in context["gem_taxonomy_lens"]}
    for name in ("Herald of Thunder", "Static Strike", "Blight of Contagion"):
        entry = taxonomy_by_name[name]
        assert entry["socketable"] is True, name
        assert entry["offense_class"] == "offensive_active", name

    assert taxonomy_by_name["Molten Burst"]["socketable"] is False
    assert taxonomy_by_name["Molten Burst"]["gem_kind"] == "active_skill_only"

    for row in context["offensive_gem_lens"]:
        for field in (
            "primary_offense_gems",
            "secondary_offense_gems",
            "enabler_offense_gems",
            "carrier_gems",
            "fallback_offense_gems",
        ):
            for candidate in row.get(field, []):
                name = candidate["skill"]
                entry = get_gem_entry(name)
                assert entry is not None, f"{name} missing from taxonomy lens source"
                if candidate.get("socketable_gem") is True:
                    assert entry["socketable"] is True, name
