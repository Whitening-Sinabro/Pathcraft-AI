"""import_poe2_planner_files: shaping and ground-truth checks for third-party .build files."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from import_poe2_planner_files import normalize, validate  # noqa: E402

TREE = {"melee17", "marauder_brute_notable1", "attributes82"}
GEMS = {
    "SkillGemShockwaveTotem": "Metadata/Items/Gems/SkillGemShockwaveTotem",
    "SupportGemMartialTempo": "Metadata/Items/Gem/SupportGemMartialTempo",
}


def ninja_export() -> dict:
    """The poe.ninja dialog output: no level_interval, no inventory, no link."""
    return {
        "name": "SkadooshShoutedHard",
        "author": "poe.ninja",
        "ascendancy": "Warrior2",
        "passives": [{"id": "melee17"}, {"id": "attributes82", "weapon_set": 1}],
        "skills": [{"id": "Metadata/Items/Gems/SkillGemShockwaveTotem",
                    "support_skills": [{"id": "Metadata/Items/Gems/SupportGemMartialTempo"}]}],
    }


def test_normalize_gives_creator_shape():
    out = normalize(ninja_export(), "Warbringer Lv24 - Skadoosh", "Skadoosh", "https://x")
    assert list(out) == ["author", "link", "ascendancy", "inventory_slots", "name", "passives", "skills"]
    assert out["inventory_slots"] == []
    assert list(out["skills"][0]) == ["id", "level_interval", "support_skills"]
    assert out["skills"][0]["level_interval"] == [1, 100]
    # every support carries level_interval, like the creator originals
    assert out["skills"][0]["support_skills"][0] == {
        "id": "Metadata/Items/Gems/SupportGemMartialTempo", "level_interval": [1, 100]}
    assert out["passives"][1]["weapon_set"] == 1
    assert out["author"] == "Skadoosh" and out["link"] == "https://x"


def test_normalize_drops_empty_support_skills_key():
    src = ninja_export()
    src["skills"].append({"id": "Metadata/Items/Gems/SkillGemShockwaveTotem", "support_skills": []})
    src["skills"].append({"id": "Metadata/Items/Gems/SkillGemShockwaveTotem"})
    out = normalize(src, "n", "a", "")
    assert "support_skills" not in out["skills"][1]
    assert "support_skills" not in out["skills"][2]


def test_normalize_is_identity_on_a_creator_original():
    original = {
        "author": "Skadoosh", "link": "https://g", "ascendancy": "Warrior2",
        "inventory_slots": [{"inventory_id": "Weapon1", "additional_text": "Smithing Hammer",
                             "level_interval": [4, 100]}],
        "name": "Level 1 - 10 - Skadoosh's Warrior Leveli",
        "passives": [{"id": "melee17"}],
        "skills": [{"id": "Metadata/Items/Gems/SkillGemShockwaveTotem", "level_interval": [6, 100],
                    "support_skills": [{"id": "Metadata/Items/Gem/SupportGemMartialTempo",
                                        "level_interval": [1, 100]}]},
                   {"id": "Metadata/Items/Gems/SkillGemShockwaveTotem", "level_interval": [1, 100]}],
    }
    out = normalize(original, "Warbringer Lv01-10 - Skadoosh", "Skadoosh", "https://g")
    for key in ("passives", "skills", "inventory_slots", "ascendancy", "author", "link"):
        assert out[key] == original[key], key


def test_normalize_keeps_existing_level_interval():
    src = ninja_export()
    src["skills"][0]["level_interval"] = [6, 100]
    out = normalize(src, "n", "a", "")
    assert out["skills"][0]["level_interval"] == [6, 100]


def test_normalize_rejects_names_the_planner_would_truncate():
    with pytest.raises(ValueError):
        normalize(ninja_export(), "x" * 41, "a", "")


def test_validate_clean_file_repairs_gem_segment_only():
    out = normalize(ninja_export(), "n", "a", "")
    assert validate(out, TREE, GEMS) == []
    # the support was written with /Gems/ but the GGPK table says /Gem/
    assert out["skills"][0]["support_skills"][0]["id"] == "Metadata/Items/Gem/SupportGemMartialTempo"


def test_validate_flags_unknown_passive():
    src = ninja_export()
    src["passives"].append({"id": "no_such_node"})
    problems = validate(normalize(src, "n", "a", ""), TREE, GEMS)
    assert any("no_such_node" in p for p in problems)


def test_validate_lets_a_gem_the_table_never_heard_of_through():
    """표는 GGPK 0.4.0d 다. 0.5.5 젬(전직이 주는 VirtuousBarrier 등)은 표에 없다.
    부재를 실패로 다루면 제작자 원본 플래너도 못 들어온다 — 실제로 6개가 그렇다."""
    src = ninja_export()
    src["skills"].append({"id": "Metadata/Items/Gems/SkillGemAscendancyVirtuousBarrier"})
    problems = validate(normalize(src, "n", "a", ""), TREE, GEMS)
    assert problems == []


def test_validate_flags_non_gem_path():
    src = ninja_export()
    src["skills"][0]["id"] = "SkillGemShockwaveTotem"
    problems = validate(normalize(src, "n", "a", ""), TREE, GEMS)
    assert problems and "not a Metadata gem path" in problems[0]
