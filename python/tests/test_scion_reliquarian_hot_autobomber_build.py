# -*- coding: utf-8 -*-
"""Regression checks for the curated Scion Reliquarian HoT project build."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_coach import build_season_research_context  # noqa: E402
from build_extractor import detect_build_type, extract_build_gems  # noqa: E402
from recommendation_engine import extract_main_skill, infer_build_profile  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "data" / "builds" / "scion_reliquarian_hot_autobomber_3_29.build.json"
COACH_PATH = ROOT / "data" / "builds" / "scion_reliquarian_hot_autobomber_3_29.coach.json"
PROFILE_PATH = ROOT / "data" / "builds" / "scion_reliquarian_hot_autobomber_3_29.profile.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_scion_reliquarian_hot_build_extracts_primary_identity():
    build = _load(BUILD_PATH)

    skills, supports = extract_build_gems(build)

    assert extract_main_skill(build) == "Herald of Thunder"
    assert detect_build_type(build) == "spell"
    assert build["fallback_branch_id"] == "blight_of_contagion_fallback"
    assert "Herald of Thunder" in skills
    assert "Blight of Contagion" not in skills
    assert "Lightning Penetration Support" in supports


def test_scion_reliquarian_hot_build_profile_keeps_project_build_constraints():
    build = _load(BUILD_PATH)
    coach = _load(COACH_PATH)
    profile = infer_build_profile(build, coach, representative_status="hold", patch="3.29")

    assert profile["build_id"] == "3_29_herald_of_thunder_reliquarian"
    assert profile["identity"]["class_name"] == "Scion"
    assert profile["identity"]["ascendancy"] == "Reliquarian"
    assert profile["identity"]["main_skill"] == "Herald of Thunder"
    assert profile["identity"]["leveling_skill"] == "Stormblast Mine"
    assert profile["confidence"]["representative_build_status"] == "hold"
    assert profile["progression"]["leveling_confidence"] == "confirmed"
    assert profile["availability"]["league_start_viable"] is False
    assert profile["availability"]["ssf_viable"] == "low"
    assert profile["availability"]["mandatory_uniques"] == ["Storm Secret"]
    assert profile["availability"]["mandatory_transfigured_gems"] == []
    assert any(
        item["to_skill"] == "Blight of Contagion"
        for item in profile["progression"]["transition_points"]
    )


def test_generated_scion_reliquarian_hot_profile_matches_current_inference():
    build = _load(BUILD_PATH)
    coach = _load(COACH_PATH)
    generated = _load(PROFILE_PATH)
    current = infer_build_profile(build, coach, representative_status="hold", patch="3.29")

    assert generated["build_id"] == current["build_id"]
    assert generated["identity"] == current["identity"]
    assert generated["availability"] == current["availability"]
    assert generated["progression"]["transition_points"] == current["progression"]["transition_points"]


def test_scion_reliquarian_hot_build_injects_season_research_context():
    build = _load(BUILD_PATH)
    context = build_season_research_context(build)

    assert context["match"]["scoped_character"] is True
    assert "hot_autobomber" in context["match"]["selected_branch_ids"]
    assert "blight_of_contagion_fallback" in context["match"]["selected_branch_ids"]
    taxonomy_by_name = {row["name"]: row for row in context["gem_taxonomy_lens"]}
    assert taxonomy_by_name["Herald of Thunder"]["socketable"] is True
    assert taxonomy_by_name["Blight of Contagion"]["socketable"] is True
