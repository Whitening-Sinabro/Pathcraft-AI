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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
