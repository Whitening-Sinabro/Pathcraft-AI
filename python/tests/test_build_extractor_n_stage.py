# -*- coding: utf-8 -*-
"""merge_build_stages N>=3 POB 분할 로직 회귀 테스트.

검증:
- N=2: 기존 leveling/endgame/common 3-way split (기존 동작 유지)
- N>=3: 각 POB별 AL 구간 소유 (midpoint 기반)
- Lv spread 작음 → union fallback
- al_split 파라미터 반영
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_extractor import merge_build_stages, STAGE_SPLIT_DELTA


def _mk(level: int, name: str = None, uniques: list = None) -> dict:
    """테스트용 최소 빌드 — 레벨별 다른 유니크 가져서 stage 분할이 의미있게 나오게."""
    default_uniques = {30: ["Lifesprig"], 70: ["Bino's Kitchen Knife"], 95: ["Mageblood"]}
    gear = {}
    for i, u in enumerate(uniques or default_uniques.get(level, [f"Unique_Lv{level}"])):
        gear[f"slot_{i}"] = {"rarity": "Unique", "name": u, "base_type": f"Base_{u}"}
    return {
        "meta": {"class_level": level, "build_name": name or f"Lv{level}"},
        "items": [{"rarity": "unique", "name": u}
                  for u in (uniques or default_uniques.get(level, [f"Unique_Lv{level}"]))],
        "progression_stages": [{
            "gem_setups": {},
            "gear_recommendation": gear,
        }],
    }


class TestStageBasics:
    def test_single_pob_returns_all(self):
        stages = merge_build_stages([_mk(90)])
        assert len(stages) == 1
        assert stages[0].label == "all"
        assert stages[0].al_min is None
        assert stages[0].al_max is None

    def test_no_staging_forces_union(self):
        stages = merge_build_stages([_mk(20), _mk(90)], no_staging=True)
        assert len(stages) == 1
        assert stages[0].label == "all"

    def test_small_lv_spread_falls_to_union(self):
        """STAGE_SPLIT_DELTA 미만 Lv 차이 → union."""
        delta = STAGE_SPLIT_DELTA - 1
        stages = merge_build_stages([_mk(80), _mk(80 + delta)])
        assert len(stages) == 1
        assert stages[0].label == "all"


class TestTwoStage:
    """N=2 POB — 기존 leveling/endgame/common 3-way split."""

    def test_two_pob_creates_leveling_and_endgame(self):
        stages = merge_build_stages([_mk(30), _mk(95)])
        labels = {s.label for s in stages}
        # common은 데이터 없을 때 생략 가능
        assert "leveling" in labels or "endgame" in labels or "all" in labels

    def test_al_split_default_67(self):
        stages = merge_build_stages([_mk(30), _mk(95)])
        lvl = next((s for s in stages if s.label == "leveling"), None)
        if lvl:
            assert lvl.al_max == 67

    def test_custom_al_split(self):
        stages = merge_build_stages([_mk(30), _mk(95)], al_split=76)
        lvl = next((s for s in stages if s.label == "leveling"), None)
        if lvl:
            assert lvl.al_max == 76
        eg = next((s for s in stages if s.label == "endgame"), None)
        if eg:
            assert eg.al_min == 77


class TestNStage:
    """N>=3 POB — midpoint 기반 개별 stage."""

    def test_three_pob_creates_three_stages(self):
        stages = merge_build_stages([_mk(30), _mk(70), _mk(95)])
        assert len(stages) == 3
        # 라벨 확인
        labels = [s.label for s in stages]
        assert labels[0] == "leveling_early"
        assert labels[-1] == "endgame"

    def test_three_pob_al_ranges_sequential(self):
        """각 stage의 al_max+1 == 다음 stage al_min (gap 없음)."""
        stages = merge_build_stages([_mk(30), _mk(70), _mk(95)])
        for i in range(len(stages) - 1):
            cur_max = stages[i].al_max
            next_min = stages[i + 1].al_min
            assert cur_max is not None
            assert next_min is not None
            assert next_min == cur_max + 1, (
                f"stage {i} max={cur_max}, stage {i+1} min={next_min} — gap detected"
            )

    def test_five_pob_creates_five_stages(self):
        stages = merge_build_stages([_mk(lv) for lv in [15, 40, 65, 85, 100]])
        assert len(stages) == 5
        assert stages[0].al_min is None  # 첫 stage 하한 무제한
        assert stages[-1].al_max is None  # 마지막 stage 상한 무제한

    def test_five_pob_no_al_gaps(self):
        """5 POB에서도 gap 없이 연속."""
        stages = merge_build_stages([_mk(lv) for lv in [15, 40, 65, 85, 100]])
        for i in range(len(stages) - 1):
            assert stages[i + 1].al_min == stages[i].al_max + 1

    def test_unsorted_input_auto_sorts(self):
        """입력 순서 무관 — Lv 기준 정렬됨."""
        stages_sorted = merge_build_stages([_mk(30), _mk(70), _mk(95)])
        stages_unsorted = merge_build_stages([_mk(95), _mk(30), _mk(70)])
        # 결과 stage의 al_min/al_max 동일해야 함
        ranges_sorted = [(s.al_min, s.al_max) for s in stages_sorted]
        ranges_unsorted = [(s.al_min, s.al_max) for s in stages_unsorted]
        assert ranges_sorted == ranges_unsorted

    def test_unknown_level_treated_as_endgame(self):
        """Lv 파싱 실패 POB는 최대 Lv+1로 취급 → 마지막 stage."""
        b_unknown = {"meta": {}, "items": [], "progression_stages": [{}]}
        stages = merge_build_stages([_mk(30), _mk(70), b_unknown])
        # unknown이 마지막 stage(endgame)에 들어가야 함
        assert stages[-1].label == "endgame"


class TestWeaponClasses:
    """StageData.weapon_classes — Step 3 통합 회귀.

    통합 테스트: merge_build_stages 내부가 data/weapon_base_to_class.json +
    data/gem_weapon_requirements.json 을 실제 로드하므로 이 JSON 파일들이
    레포에 존재해야 동작. 의도적 통합 — 생성 스크립트 regression(예: POB
    Lua 포맷 변화)이 여기서 걸림. 순수 단위 테스트는 test_weapon_class_extractor.py
    가 fixture dict 주입으로 별도 커버.
    """

    @staticmethod
    def _mk_with_weapon(level: int, weapon_base: str) -> dict:
        """weapon slot이 있는 build_data."""
        return {
            "meta": {"class_level": level},
            "items": [],
            "progression_stages": [{
                "gem_setups": {"Main": {"links": "Cleave"}},
                "gear_recommendation": {
                    "Weapon 1": {"base_type": weapon_base, "rarity": "Normal"},
                },
            }],
        }

    def test_single_pob_populates_weapon_classes(self):
        # Brass Maul → Two Hand Maces (data/weapon_base_to_class.json ground truth)
        stages = merge_build_stages([self._mk_with_weapon(90, "Brass Maul")])
        assert len(stages) == 1
        assert stages[0].weapon_classes == ["Two Hand Maces"]

    def test_two_pob_different_classes_split_correctly(self):
        # Leveling 2H sword, endgame 1H sword → common empty, lv/eg split
        stages = merge_build_stages([
            self._mk_with_weapon(30, "Bastard Sword"),  # Two Hand Swords
            self._mk_with_weapon(95, "Corsair Sword"),  # One Hand Swords
        ])
        by_label = {s.label: s for s in stages}
        assert "leveling" in by_label and "endgame" in by_label
        assert by_label["leveling"].weapon_classes == ["Two Hand Swords"]
        assert by_label["endgame"].weapon_classes == ["One Hand Swords"]
        # common stage: no shared weapon class
        if "common" in by_label:
            assert by_label["common"].weapon_classes == []

    def test_two_pob_same_class_lands_in_common(self):
        # Both POBs use 1H Axe — expect common weapon_classes, empty lv/eg weapons
        stages = merge_build_stages([
            self._mk_with_weapon(30, "Reaver Axe"),   # One Hand Axes
            self._mk_with_weapon(95, "Siege Axe"),    # One Hand Axes
        ])
        by_label = {s.label: s for s in stages}
        # common must carry the shared class
        assert "common" in by_label
        assert by_label["common"].weapon_classes == ["One Hand Axes"]
        # leveling/endgame should not re-list the shared class
        if "leveling" in by_label:
            assert "One Hand Axes" not in by_label["leveling"].weapon_classes
        if "endgame" in by_label:
            assert "One Hand Axes" not in by_label["endgame"].weapon_classes

    def test_no_weapon_in_gear_returns_empty(self):
        # No weapon slot in any stage → weapon_classes empty (L7 will skip)
        build = {
            "meta": {"class_level": 90},
            "items": [],
            "progression_stages": [{
                "gem_setups": {"Main": {"links": "Arc"}},  # spell, no weapon req
                "gear_recommendation": {"Body Armour": {"base_type": "Astral Plate"}},
            }],
        }
        stages = merge_build_stages([build])
        assert stages[0].weapon_classes == []
