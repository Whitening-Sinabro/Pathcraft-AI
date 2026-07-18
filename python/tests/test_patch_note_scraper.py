# -*- coding: utf-8 -*-
"""patch_note_scraper 순수 함수 유닛 테스트"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from patch_note_scraper import (
    extract_version,
    classify_patch_type,
    classify_change,
    parse_sections,
    extract_lines,
    classify_section_domain,
    extract_entity_name,
    extract_numeric_delta,
    build_patch_delta_index,
    build_early_patch_adjustment_policy,
)


class TestExtractVersion:
    def test_major_patch(self):
        assert extract_version("Content Update 3.28.0 — Path of Exile: Mirage") == "3.28.0"

    def test_minor_patch(self):
        assert extract_version("3.28.0b Patch Notes") == "3.28.0b"

    def test_hotfix(self):
        assert extract_version("3.28.0 Hotfix 15") == "3.28.0-hotfix15"

    def test_hotfix_with_letter(self):
        assert extract_version("3.28.0e Hotfix 3") == "3.28.0e-hotfix3"

    def test_no_version(self):
        assert extract_version("Code of Conduct") == ""

    def test_old_version(self):
        assert extract_version("3.25.3f Patch Notes") == "3.25.3f"


class TestClassifyPatchType:
    def test_major(self):
        assert classify_patch_type("Content Update 3.28.0 — Path of Exile: Mirage") == "major"

    def test_minor(self):
        assert classify_patch_type("3.28.0b Patch Notes") == "minor"

    def test_hotfix(self):
        assert classify_patch_type("3.28.0 Hotfix 15") == "hotfix"

    def test_hotfix_with_letter(self):
        assert classify_patch_type("3.28.0e Hotfix 3") == "hotfix"


class TestClassifyChange:
    def test_buff(self):
        assert classify_change("Storm Brand now deals 150-449 Lightning Damage") == "buff"

    def test_nerf(self):
        assert classify_change("Cartographer's Chisels can no longer be obtained") == "nerf"

    def test_change(self):
        assert classify_change("The Templar now wakes on the Twilight Strand") == "change"

    def test_added_is_buff(self):
        assert classify_change("Added a new Strength/Intelligence Skill Gem") == "buff"

    def test_removed_is_nerf(self):
        assert classify_change("Shadow Shaping has been removed") == "nerf"

    def test_reduced_is_nerf(self):
        assert classify_change("Reduced the damage dealt by Rusty Crusher") == "nerf"

    def test_increased_is_buff(self):
        assert classify_change("Now has 32% more Area of Effect") == "buff"


class TestParseSections:
    def test_splits_by_return_to_top(self):
        text = """The Mirage Challenge League
Some league content here.
Return to top
New Content and Features
New stuff here.
Return to top
Skill Gem Changes
Storm Brand now deals more damage."""

        sections = parse_sections(text)
        assert "The Mirage Challenge League" in sections
        assert "New Content and Features" in sections
        assert "Skill Gem Changes" in sections
        assert "Some league content here." in sections["The Mirage Challenge League"]

    def test_handles_no_sections(self):
        text = "Just some random text without headers."
        sections = parse_sections(text)
        assert "preamble" in sections

    def test_empty_text(self):
        sections = parse_sections("")
        assert len(sections) == 0 or all(v == "" for v in sections.values())


class TestExtractLines:
    def test_filters_short_lines(self):
        text = "Short\nThis is a meaningful line of text\nNo"
        lines = extract_lines(text)
        assert len(lines) == 1
        assert "meaningful" in lines[0]

    def test_strips_whitespace(self):
        text = "  Some content with spaces  \n  Another line  "
        lines = extract_lines(text)
        assert all(l == l.strip() for l in lines)


class TestPatchDeltaIndex:
    def test_section_domain_mapping(self):
        assert classify_section_domain("Skill Gem Changes") == "skill_gem"
        assert classify_section_domain("Atlas Passive Tree Changes") == "atlas"
        assert classify_section_domain("The Curse of the Allflame Challenge League") == "challenge_league"

    def test_extracts_entity_from_colon_line(self):
        line = "Arc: Now has a Cast time of 0.6 seconds (previously 0.7)."
        assert extract_entity_name(line) == "Arc"

    def test_extracts_current_and_previous_numbers(self):
        line = "Arc: Now has a Cast time of 0.6 seconds (previously 0.7), and the base Mana Cost has been increased by 25% at all gem levels."
        delta = extract_numeric_delta(line)
        assert delta["has_previous"] is True
        assert {"raw": "0.6 seconds", "number": "0.6", "unit": "seconds"} in delta["current"]
        assert {"raw": "25%", "number": "25", "unit": "%"} in delta["current"]
        assert {"raw": "0.7", "number": "0.7", "unit": ""} in delta["previous"]
        assert delta["pairing"] == "unpaired_review_required"

    def test_build_patch_delta_index_summarizes_domains(self):
        patch = {
            "version": "3.29.0",
            "title": "Content Update 3.29.0 — Path of Exile: Curse of the Allflame",
            "patch_type": "major",
            "url": "https://www.pathofexile.com/forum/view-thread/3985332",
            "sections": {
                "Skill Gem Changes": [
                    "Arc: Now has a Cast time of 0.6 seconds (previously 0.7).",
                ],
                "Atlas Passive Tree Changes": [
                    "The Notable grants your Tier 14+ Maps 4% chance to drop a Scrying Orb on completion.",
                ],
            },
        }
        index = build_patch_delta_index(patch)
        assert index["dataset_kind"] == "poe1_patch_delta_index"
        assert index["summary"]["entry_count"] == 2
        assert index["summary"]["numeric_domain_counts"]["skill_gem"] == 1
        assert index["entries"][0]["entity"] == "Arc"
        assert "skill_numbers" in index["entries"][0]["watch_tags"]
        assert "atlas" in index["entries"][1]["watch_tags"]

    def test_early_patch_adjustment_policy_preserves_overlay_rules(self):
        policy = build_early_patch_adjustment_policy(
            "3.29.0",
            "https://www.pathofexile.com/forum/view-thread/3985332",
        )
        assert policy["dataset_kind"] == "poe1_early_season_patch_adjustment_policy"
        assert policy["base_version"] == "3.29.0"
        stages = {row["stage"] for row in policy["patch_flow"]}
        assert {
            "base_patch_notes",
            "launch_client_ggpk",
            "post_launch_ggpk_refresh",
            "day0_hotfix",
            "minor_patch",
        }.issubset(stages)
        assert "effective_value_source" in policy["required_overlay_fields"]
        assert "ggpk_snapshot_id" in policy["required_overlay_fields"]
        assert "ggpk_table" in policy["required_overlay_fields"]
        assert "ggpk_row_key" in policy["required_overlay_fields"]
        assert any("Never mutate the base patch note entry" in rule for rule in policy["numeric_overlay_rules"])
        assert any("versioned snapshot" in rule for rule in policy["ggpk_snapshot_rules"])
        target_tables = {row["table"] for row in policy["ggpk_diff_targets"]}
        assert {"SkillGems", "ActiveSkills", "BaseItemTypes", "Mods", "PassiveSkills", "Maps"}.issubset(target_tables)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
