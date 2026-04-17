# -*- coding: utf-8 -*-
"""damage_type_extractor 단위 테스트 (E3)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from damage_type_extractor import (  # noqa: E402
    classify_damage_axes_from_gems,
    extract_build_damage_types,
    load_gem_damage_types,
    DAMAGE_AXES,
)


# ---------------------------------------------------------------------------
# classify_damage_axes_from_gems — 순수 함수, fixture 주입
# ---------------------------------------------------------------------------

_FIXTURE_GEM_TYPES = {
    "Cyclone": {"attack": True, "caster": False, "dot": False, "minion": False},
    "Arc": {"attack": False, "caster": True, "dot": False, "minion": False},
    "Righteous Fire": {"attack": False, "caster": True, "dot": True, "minion": False},
    "Summon Raging Spirit": {"attack": False, "caster": True, "dot": False, "minion": True},
    "Melee Physical Damage Support": {
        "attack": False, "caster": False, "dot": False, "minion": False,
    },
}


class TestClassifyDamageAxes:
    def test_empty_gems_returns_empty(self):
        assert classify_damage_axes_from_gems([], _FIXTURE_GEM_TYPES) == frozenset()

    def test_empty_types_returns_empty(self):
        assert classify_damage_axes_from_gems(["Cyclone"], {}) == frozenset()

    def test_cyclone_only_attack(self):
        """순수 attack — Cyclone."""
        assert classify_damage_axes_from_gems(
            ["Cyclone"], _FIXTURE_GEM_TYPES,
        ) == frozenset({"attack"})

    def test_arc_only_caster(self):
        """순수 caster — Arc."""
        assert classify_damage_axes_from_gems(
            ["Arc"], _FIXTURE_GEM_TYPES,
        ) == frozenset({"caster"})

    def test_righteous_fire_caster_plus_dot(self):
        """RF = Spell + DamageOverTime → 두 axis 모두."""
        assert classify_damage_axes_from_gems(
            ["Righteous Fire"], _FIXTURE_GEM_TYPES,
        ) == frozenset({"caster", "dot"})

    def test_srs_caster_plus_minion(self):
        """SRS = Spell + CreatesMinion → 두 axis 모두."""
        assert classify_damage_axes_from_gems(
            ["Summon Raging Spirit"], _FIXTURE_GEM_TYPES,
        ) == frozenset({"caster", "minion"})

    def test_union_across_multiple_skills(self):
        """여러 메인 스킬 → axis union."""
        result = classify_damage_axes_from_gems(
            ["Cyclone", "Arc"], _FIXTURE_GEM_TYPES,
        )
        assert result == frozenset({"attack", "caster"})

    def test_support_gem_with_no_axis_ignored(self):
        """damage axis flag 모두 false인 gem(support/aura) → 무시."""
        result = classify_damage_axes_from_gems(
            ["Cyclone", "Melee Physical Damage Support"], _FIXTURE_GEM_TYPES,
        )
        assert result == frozenset({"attack"})

    def test_unknown_gem_silently_skipped(self):
        """dict에 없는 gem → 조용히 skip (false positive 회피)."""
        result = classify_damage_axes_from_gems(
            ["Cyclone", "UnknownSkillX"], _FIXTURE_GEM_TYPES,
        )
        assert result == frozenset({"attack"})


class TestExtractBuildDamageTypes:
    def test_none_build_returns_empty(self):
        assert extract_build_damage_types(None, {}) == frozenset()

    def test_no_gem_setups_returns_empty(self):
        build = {"progression_stages": [{"gem_setups": {}, "gear_recommendation": {}}]}
        assert extract_build_damage_types(build, _FIXTURE_GEM_TYPES) == frozenset()

    def test_reads_pob_parser_schema(self):
        """pob_parser gem_setups 스키마 소비 — label + links 모두 탐색."""
        build = {
            "progression_stages": [{
                "gem_setups": {
                    "Cyclone": {"links": "Cyclone - Melee Physical Damage Support", "reasoning": None},
                },
                "gear_recommendation": {},
            }],
        }
        assert extract_build_damage_types(build, _FIXTURE_GEM_TYPES) == frozenset({"attack"})

    def test_rf_build_returns_caster_dot(self):
        """RF 빌드 — label과 links 모두에 Righteous Fire."""
        build = {
            "progression_stages": [{
                "gem_setups": {
                    "Righteous Fire": {"links": "Righteous Fire - Arc", "reasoning": None},
                },
                "gear_recommendation": {},
            }],
        }
        assert extract_build_damage_types(build, _FIXTURE_GEM_TYPES) == frozenset(
            {"caster", "dot"}  # RF caster+dot union Arc caster → {caster, dot}
        )


class TestLoadGemDamageTypes:
    """실제 JSON 로드 테스트 (graceful degradation 포함)."""

    def test_file_missing_returns_empty(self, tmp_path):
        result = load_gem_damage_types(tmp_path / "missing.json")
        assert result == {}

    def test_malformed_json_returns_empty(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        assert load_gem_damage_types(bad) == {}

    def test_valid_json_returns_gems_section(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "_meta": {"source": "test"},
            "gems": {
                "Cyclone": {"attack": True, "caster": False, "dot": False, "minion": False},
            },
        }), encoding="utf-8")
        result = load_gem_damage_types(good)
        assert "Cyclone" in result
        assert result["Cyclone"]["attack"] is True
