# -*- coding: utf-8 -*-
"""3.29 patch-note DB, numeric deltas, and early-season overlay policy."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from build_coach import load_patch_derivative_context  # noqa: E402

PATCH_DIR = ROOT / "data" / "patch_notes"
PATCH_PATH = PATCH_DIR / "patch_3_29_0.json"
SUMMARY_PATH = PATCH_DIR / "summary_3_29_0.json"
DELTA_PATH = PATCH_DIR / "poe1_3_29_0_patch_delta_index.json"
POLICY_PATH = PATCH_DIR / "poe1_3_29_0_early_patch_adjustment_policy.json"
OFFICIAL_URL = "https://www.pathofexile.com/forum/view-thread/3985332"


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_329_patch_notes_are_collected_from_official_forum():
    data = _load(PATCH_PATH)

    assert data["version"] == "3.29.0"
    assert data["patch_type"] == "major"
    assert data["url"] == OFFICIAL_URL
    assert "Curse of the Allflame" in data["title"]
    assert "Skill Gem Changes" in data["sections"]
    assert "Endgame Changes" in data["sections"]
    assert "Atlas Passive Tree Changes" in data["sections"]
    assert len(data["sections"]["Skill Gem Changes"]) >= 100


def test_329_summary_exposes_coach_relevant_sections():
    summary = _load(SUMMARY_PATH)

    assert summary["version"] == "3.29.0"
    assert summary["key_numbers"]["total_sections"] >= 15
    assert len(summary["skill_buffs"]) >= 50
    assert summary["endgame_changes"]
    assert summary["atlas_passive_changes"]
    assert summary["ascendancy_changes"]


def test_329_delta_index_preserves_numeric_previous_values():
    delta = _load(DELTA_PATH)

    assert delta["dataset_kind"] == "poe1_patch_delta_index"
    assert delta["version"] == "3.29.0"
    assert delta["source_url"] == OFFICIAL_URL
    assert delta["summary"]["entry_count"] >= 350
    assert delta["summary"]["numeric_delta_count"] >= 200
    assert delta["summary"]["domain_counts"]["skill_gem"] >= 100
    assert delta["summary"]["high_impact_watchlist"]["allflame_loop_lines"] >= 10
    assert delta["summary"]["high_impact_watchlist"]["skill_number_lines"] >= 150

    arc = next(
        entry
        for entry in delta["entries"]
        if entry["domain"] == "skill_gem" and entry["entity"] == "Arc"
    )
    assert arc["numeric_delta"]["has_previous"] is True
    assert any(row["number"] == "0.6" for row in arc["numeric_delta"]["current"])
    assert any(row["number"] == "0.7" for row in arc["numeric_delta"]["previous"])
    assert "skill_numbers" in arc["watch_tags"]


def test_329_adjustment_policy_handles_repeated_ggpk_updates():
    policy = _load(POLICY_PATH)

    assert policy["dataset_kind"] == "poe1_early_season_patch_adjustment_policy"
    stages = {row["stage"] for row in policy["patch_flow"]}
    assert "post_launch_ggpk_refresh" in stages
    assert any("versioned snapshot" in rule for rule in policy["ggpk_snapshot_rules"])
    assert any("server-only" in rule for rule in policy["ggpk_snapshot_rules"])

    target_tables = {row["table"] for row in policy["ggpk_diff_targets"]}
    assert {
        "SkillGems",
        "ActiveSkills",
        "BaseItemTypes",
        "Mods",
        "PassiveSkills",
        "Ascendancy",
        "Maps",
        "QuestRewards",
        "Scarabs",
    }.issubset(target_tables)

    required = set(policy["required_overlay_fields"])
    assert {"ggpk_snapshot_id", "ggpk_table", "ggpk_row_key"}.issubset(required)


def test_build_coach_loads_patch_derivative_context():
    context = load_patch_derivative_context()

    assert context["dataset_kind"] == "poe1_patch_derivative_context"
    assert context["version"] == "3.29.0"
    assert context["delta_summary"]["numeric_delta_count"] >= 200
    assert context["ggpk_snapshot_rules"]
    assert context["ggpk_diff_targets"]
