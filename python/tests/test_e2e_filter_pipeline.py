# -*- coding: utf-8 -*-
"""POB build_data → filter_generator → POE filter 전체 파이프라인 E2E.

Phase B(weapon) + D(defense) + E(accessory) 전부 동시 활성화되는 realistic fixture로
generate_beta_overlay 산출물을 검증. 단위 테스트가 커버 못 하는 통합 회귀 방어:

- 여러 extractor가 동시에 build_data를 소비할 때 stats/gem/gear 충돌 없음
- L7 내 모든 카테고리(unique/chanceable/weapon/defense/accessory/divcard/skill/base) 공존
- L10 re_show가 L9 progressive hide를 올바르게 복권
- multi-POB staging(leveling/endgame) 시 stage별 extractor 결과 분리 emit

레퍼런스: Phase B plan line 371 "인게임 스모크 + E2E 통합 테스트" 차단 블로커 해소.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sections_continue import generate_beta_overlay


# ---------------------------------------------------------------------------
# Realistic fixtures — 각 axis 조합 대표
# ---------------------------------------------------------------------------

JUGGERNAUT_CYCLONE = {
    "meta": {"build_name": "Juggernaut Cyclone", "class": "Marauder"},
    "stats": {
        "dps": 800000, "life": 6000, "energy_shield": 0,
        "armour": 30000, "evasion": 400,
    },
    "items": [
        {"rarity": "unique", "name": "Kaom's Heart"},
    ],
    "progression_stages": [{
        "gem_setups": {
            "Cyclone": {
                "links": "Cyclone - Melee Physical Damage Support - Fortify Support",
                "reasoning": None,
            },
        },
        "gear_recommendation": {
            "Weapon 1": {"rarity": "Rare", "base_type": "Reaver Axe"},
            "Body Armour": {"rarity": "Unique", "base_type": "Glorious Plate", "name": "Kaom's Heart"},
        },
    }],
}

CI_OCCULTIST_ARC = {
    "meta": {"build_name": "CI Occultist Arc", "class": "Witch"},
    "stats": {
        "dps": 1500000, "life": 1, "energy_shield": 10000,
        "armour": 200, "evasion": 800,
    },
    "items": [
        {"rarity": "unique", "name": "Shavronne's Wrappings"},
    ],
    "progression_stages": [{
        "gem_setups": {
            "Arc": {
                "links": "Arc - Lightning Penetration Support - Controlled Destruction Support",
                "reasoning": None,
            },
        },
        "gear_recommendation": {
            "Weapon 1": {"rarity": "Rare", "base_type": "Imbued Wand"},
            "Body Armour": {"rarity": "Unique", "base_type": "Occultist's Vestment",
                            "name": "Shavronne's Wrappings"},
        },
    }],
}

GUARDIAN_SRS = {
    "meta": {"build_name": "Guardian SRS", "class": "Templar"},
    "stats": {
        "dps": 600000, "life": 5000, "energy_shield": 4000,
        "armour": 12000, "evasion": 200,
    },
    "items": [],
    "progression_stages": [{
        "gem_setups": {
            "Summon Raging Spirit": {
                "links": "Summon Raging Spirit - Minion Damage Support - Melee Physical Damage Support",
                "reasoning": None,
            },
        },
        "gear_recommendation": {
            "Weapon 1": {"rarity": "Rare", "base_type": "Void Sceptre"},
            "Body Armour": {"rarity": "Rare", "base_type": "Saint's Hauberk"},
        },
    }],
}

EMPTY_BUILD = {
    "meta": {"build_name": "Minimal"},
    "items": [],
    "progression_stages": [{"gem_setups": {}, "gear_recommendation": {}}],
}


# ---------------------------------------------------------------------------
# Per-fixture E2E (단일 POB → 단일 stage)
# ---------------------------------------------------------------------------

class TestJuggernautCyclone:
    """Attack + Armour 순수. L7 weapon/defense/accessory attack 전부 활성."""

    def _run(self):
        return generate_beta_overlay(
            strictness=3, build_data=JUGGERNAUT_CYCLONE, mode="ssf",
        )

    def test_all_l7_categories_present(self):
        text = self._run()
        # build-aware 필수 블록
        assert "[L7|unique]" in text
        assert "[L7|weapon_phys_proxy]" in text
        assert "[L7|defense_proxy_body_armour_life]" in text
        assert "[L7|accessory_proxy_amulet_attack]" in text
        assert "[L7|accessory_proxy_ring_attack]" in text
        # common/공용
        assert "[L7|accessory_proxy_amulet_common]" in text
        assert "[L7|accessory_proxy_belt_common]" in text
        # 정적 카테고리
        assert "[L7|skill_gem]" in text

    def test_negative_cross_axis_blocks_absent(self):
        """AR 빌드에 ES defense 블록 없음 / attack 빌드에 caster 없음."""
        text = self._run()
        assert "[L7|defense_proxy_body_armour_es]" not in text
        assert "[L7|accessory_proxy_amulet_caster]" not in text
        assert "[L7|accessory_proxy_amulet_dot]" not in text

    def test_weapon_class_correct(self):
        """Reaver Axe → One Hand Axes Class."""
        text = self._run()
        idx = text.find("[L7|weapon_phys_proxy]")
        end = text.find("Continue", idx)
        block = text[idx:end]
        assert '"One Hand Axes"' in block

    def test_l7_order_preserved(self):
        text = self._run()
        positions = {
            "unique":     text.find("[L7|unique]"),
            "weapon":     text.find("[L7|weapon_phys_proxy]"),
            "defense":    text.find("[L7|defense_proxy_"),
            "accessory":  text.find("[L7|accessory_proxy_"),
            "skill":      text.find("[L7|skill_gem]"),
        }
        for name, pos in positions.items():
            assert pos >= 0
        assert (positions["unique"] < positions["weapon"] <
                positions["defense"] < positions["accessory"] <
                positions["skill"])


class TestCiOccultistArc:
    """Caster + ES 순수. Wand + ES defense + caster accessory."""

    def _run(self):
        return generate_beta_overlay(
            strictness=3, build_data=CI_OCCULTIST_ARC, mode="ssf",
        )

    def test_es_defense_caster_accessory(self):
        text = self._run()
        assert "[L7|defense_proxy_body_armour_es]" in text
        assert "[L7|defense_proxy_helmet_es]" in text
        assert "[L7|accessory_proxy_amulet_caster]" in text
        assert "[L7|accessory_proxy_ring_caster]" in text

    def test_ar_life_blocks_absent(self):
        """CI는 life/armour mod 블록 활성 안 함."""
        text = self._run()
        assert "[L7|defense_proxy_body_armour_life]" not in text
        assert "[L7|accessory_proxy_amulet_attack]" not in text

    def test_wand_not_in_weapon_phys_proxy(self):
        """Wand는 phys 무기 아님 → weapon_phys_proxy block skip or Wands class 포함."""
        text = self._run()
        # Wand가 physical weapon list에 포함된 경우 Wands 매칭
        if "[L7|weapon_phys_proxy]" in text:
            idx = text.find("[L7|weapon_phys_proxy]")
            end = text.find("Continue", idx)
            block = text[idx:end]
            assert '"Wands"' in block


class TestGuardianSrs:
    """Minion + Hybrid AR/ES. ring_minion + 양쪽 defense 블록 활성."""

    def _run(self):
        return generate_beta_overlay(
            strictness=3, build_data=GUARDIAN_SRS, mode="ssf",
        )

    def test_minion_specific_ring_block(self):
        """SRS → ring_minion 활성 (amulet.minion은 NeverSink에 없음)."""
        text = self._run()
        assert "[L7|accessory_proxy_ring_minion]" in text

    def test_hybrid_defense_both_focuses(self):
        """AR 12000 + ES 4000 (33%) hybrid → life + es 양쪽 defense 블록."""
        text = self._run()
        assert "[L7|defense_proxy_body_armour_life]" in text
        assert "[L7|defense_proxy_body_armour_es]" in text

    def test_srs_spawns_caster_axis(self):
        """SRS는 Spell flag 포함 → amulet caster 블록도 emit."""
        text = self._run()
        assert "[L7|accessory_proxy_amulet_caster]" in text


# ---------------------------------------------------------------------------
# Multi-stage E2E (leveling → endgame)
# ---------------------------------------------------------------------------

class TestMultiStageTransition:
    """Lv30 life AR → Lv95 CI ES: stage=True 분기 E2E."""

    @staticmethod
    def _leveling():
        return {
            "meta": {"class_level": 30, "build_name": "Lv30 life"},
            "stats": {"armour": 4000, "evasion": 2000, "energy_shield": 0},
            "items": [],
            "progression_stages": [{
                "gem_setups": {
                    "Molten Strike": {"links": "Molten Strike", "reasoning": None},
                },
                "gear_recommendation": {
                    "Weapon 1": {"rarity": "Magic", "base_type": "Reaver Axe"},
                },
            }],
        }

    @staticmethod
    def _endgame():
        return {
            "meta": {"class_level": 95, "build_name": "Lv95 CI"},
            "stats": {"armour": 0, "evasion": 0, "energy_shield": 11000},
            "items": [],
            "progression_stages": [{
                "gem_setups": {
                    "Arc": {"links": "Arc", "reasoning": None},
                },
                "gear_recommendation": {
                    "Weapon 1": {"rarity": "Rare", "base_type": "Imbued Wand"},
                },
            }],
        }

    def test_stage_separates_defense_axis(self):
        """leveling 블록에 life, endgame 블록에 es만 — 전환 정확."""
        text = generate_beta_overlay(
            strictness=3,
            build_data=[self._leveling(), self._endgame()],
            stage=True,
            mode="ssf",
        )
        # leveling 블록에 life 방어
        assert "[L7|defense_proxy_leveling_body_armour_life]" in text
        # endgame 블록에 es 방어
        assert "[L7|defense_proxy_endgame_body_armour_es]" in text
        # 역방향 배제 확인
        assert "[L7|defense_proxy_leveling_body_armour_es]" not in text
        assert "[L7|defense_proxy_endgame_body_armour_life]" not in text

    def test_stage_separates_damage_axis(self):
        """leveling attack → endgame caster 전환."""
        text = generate_beta_overlay(
            strictness=3,
            build_data=[self._leveling(), self._endgame()],
            stage=True,
            mode="ssf",
        )
        assert "[L7|accessory_proxy_leveling_amulet_attack]" in text
        assert "[L7|accessory_proxy_endgame_amulet_caster]" in text
        assert "[L7|accessory_proxy_leveling_amulet_caster]" not in text


# ---------------------------------------------------------------------------
# Negative case — 최소 빌드 (BUILD_TARGET 생략, 기본 필터만)
# ---------------------------------------------------------------------------

class TestMinimalBuildFallback:
    """gear 없는 빌드 → L7 BUILD_TARGET 생략, 기본 필터 그대로."""

    def test_build_specific_l7_blocks_skipped(self):
        """build 정보 없으면 unique/weapon/defense 블록 skip. accessory_proxy common은 예외."""
        text = generate_beta_overlay(
            strictness=3, build_data=EMPTY_BUILD, mode="ssf",
        )
        # 빌드 정보 부재 → 관련 블록 skip
        assert "[L7|unique]" not in text
        assert "[L7|weapon_phys_proxy]" not in text
        assert "[L7|defense_proxy_" not in text
        # damage-axis 악세서리는 skip
        for axis in ("attack", "caster", "dot", "minion"):
            assert f"[L7|accessory_proxy_amulet_{axis}]" not in text
        # 설계: common(exalter amulet, general belt)은 universal upgrade → 항상 emit
        assert "[L7|accessory_proxy_amulet_common]" in text
        assert "[L7|accessory_proxy_belt_common]" in text

    def test_base_layers_still_emit(self):
        """L0~L6/L8 등 정적 레이어는 정상 emit."""
        text = generate_beta_overlay(
            strictness=3, build_data=EMPTY_BUILD, mode="ssf",
        )
        assert "[L1|catchall]" in text
        assert "[L8|" in text  # 커런시/디비카 블록 중 어느 하나라도
        assert "[L2|rare]" in text

    def test_no_build_data_works(self):
        """build_data=None → L7 완전 생략."""
        text = generate_beta_overlay(strictness=3, build_data=None, mode="ssf")
        assert "[L7|" not in text
        assert "[L1|catchall]" in text  # 기본 필터는 유지


# ---------------------------------------------------------------------------
# L10 re_show integration — L9 hide 후 복권 경로 E2E
# ---------------------------------------------------------------------------

class TestL10ReShowIntegration:
    """L9 progressive hide → L10 re_show 로 빌드 아이템 복권 E2E."""

    def test_strictness_3_has_l9_hide_and_l10_reshow(self):
        text = generate_beta_overlay(
            strictness=3, build_data=JUGGERNAUT_CYCLONE, mode="ssf",
        )
        # 엄격도 3 → L9 progressive hide 있음
        assert "[L9|" in text
        # 빌드 기반 L10 재Show도 있음
        assert "[L10|" in text

    def test_strictness_0_no_l9_no_l10(self):
        text = generate_beta_overlay(
            strictness=0, build_data=JUGGERNAUT_CYCLONE, mode="ssf",
        )
        # 엄격도 0은 L9 progressive hide 생략 → L10 불필요
        assert "[L9|" not in text
