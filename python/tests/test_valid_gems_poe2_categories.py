# -*- coding: utf-8 -*-
"""POE2 valid_gems_poe2.json 카테고리 완전성 회귀 가드.

조사 결과 (GGPK 2026-04-22 poe2 0.4.0d):
- Awakened gem: 0건. SkillGems.Awakened 필드는 1103 행 전부 sentinel
  (-72340172838076674). POE2 0.4.x 에 Awakened 메커닉 없음.
- Vaal gem: 0건. SkillGems.IsVaalVariant=False 전부,
  VaalVariant_BaseItemType 전부 sentinel.
- Meta gem (GemType=2, 42행 중 유효 36행): Cast on X / Cast when X / Totem.
  현재 valid_gems_poe2.json `active` 카테고리에 36건 전부 포함.
  consumer (coach_normalizer/_load_valid_gems, coach_validator/_get_valid_gems)
  가 active+support+spirit 을 평탄화하므로 기능적 누락 없음.

이 테스트는 미래 POE2 GGPK 업데이트가 위 가정을 깨면 즉시 실패하도록 고정.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_GEMS_PATH = REPO_ROOT / "data" / "game_data_poe2" / "SkillGems.json"
BASE_ITEMS_PATH = REPO_ROOT / "data" / "game_data_poe2" / "BaseItemTypes.json"
VALID_GEMS_PATH = REPO_ROOT / "data" / "valid_gems_poe2.json"

# POE2 Awakened/VaalVariant_BaseItemType 'no value' sentinel (8 byte signed -1 류).
# GGPK extractor 가 빈 KeyForeign / Optional<int64> 를 0xFEFEFEFEFEFEFEFE 로 표기.
SENTINEL = -72340172838076674


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def skill_gems() -> list[dict]:
    return _load(SKILL_GEMS_PATH)


@pytest.fixture(scope="module")
def base_items() -> list[dict]:
    return _load(BASE_ITEMS_PATH)


@pytest.fixture(scope="module")
def valid_gems() -> dict:
    return json.loads(VALID_GEMS_PATH.read_text(encoding="utf-8"))


class TestNoAwakenedGemsInPoe2:
    """POE2 0.4.x 에 Awakened 메커닉 없음 — 미래 추가 시 즉시 탐지."""

    def test_awakened_field_sentinel_only(self, skill_gems: list[dict]) -> None:
        non_sentinel = [g for g in skill_gems if g.get("Awakened") != SENTINEL]
        assert not non_sentinel, (
            f"POE2 SkillGems.Awakened 가 sentinel 외 값을 가진 행 발견: {len(non_sentinel)}건. "
            "Awakened 메커닉 도입 가능성 — valid_gems_poe2.json 에 awakened 카테고리 추가 검토."
        )


class TestNoVaalGemsInPoe2:
    """POE2 0.4.x 에 Vaal variant gem 없음 — 미래 추가 시 즉시 탐지."""

    def test_is_vaal_variant_all_false(self, skill_gems: list[dict]) -> None:
        vaal_true = [g for g in skill_gems if g.get("IsVaalVariant") is True]
        assert not vaal_true, (
            f"POE2 SkillGems.IsVaalVariant=True 행 발견: {len(vaal_true)}건. "
            "Vaal gem 도입 가능성 — valid_gems_poe2.json 에 vaal 카테고리 추가 검토."
        )

    def test_vaal_variant_base_item_type_sentinel_only(
        self, skill_gems: list[dict],
    ) -> None:
        non_sentinel = [
            g for g in skill_gems
            if g.get("VaalVariant_BaseItemType") != SENTINEL
        ]
        assert not non_sentinel, (
            f"POE2 SkillGems.VaalVariant_BaseItemType 가 sentinel 외 값을 가진 행 발견: "
            f"{len(non_sentinel)}건. Vaal variant 매핑 도입 가능성."
        )


class TestMetaGemsInActiveCategory:
    """GemType=2 (Cast on X / Totem 등 메타 젬) 은 valid_gems active 에 포함.

    consumer 가 active+support+spirit flatten 하므로 정상. 본 테스트는
    카테고리 분류가 묵시적으로 변경되어 메타 젬이 누락되면 알림.
    """

    def _meta_gem_names(
        self, skill_gems: list[dict], base_items: list[dict],
    ) -> set[str]:
        names: set[str] = set()
        for g in skill_gems:
            if g.get("GemType") != 2:
                continue
            idx = g.get("BaseItemType")
            if not isinstance(idx, int) or not (0 <= idx < len(base_items)):
                continue
            name = (base_items[idx].get("Name") or "").strip()
            if name and "[DNT" not in name:
                names.add(name)
        return names

    def test_all_meta_gems_present_in_valid_gems(
        self,
        skill_gems: list[dict],
        base_items: list[dict],
        valid_gems: dict,
    ) -> None:
        meta_names = self._meta_gem_names(skill_gems, base_items)
        all_buckets: set[str] = set()
        for bucket in ("active", "support", "spirit", "meta"):
            for entry in valid_gems.get(bucket, []) or []:
                if isinstance(entry, dict):
                    n = (entry.get("name") or "").strip()
                    if n:
                        all_buckets.add(n)
        missing = meta_names - all_buckets
        assert not missing, (
            f"GemType=2 메타 젬 {len(missing)}건이 valid_gems_poe2.json 어느 카테고리에도 없음: "
            f"{sorted(missing)[:5]}"
        )

    def test_meta_gem_count_matches_finding(
        self, skill_gems: list[dict], base_items: list[dict],
    ) -> None:
        """조사 시점 (2026-04-25) 메타 젬 36건 — 큰 변동 시 재조사 필요.

        하한 30 / 상한 60 — POE2 0.4.x 패치 자연 변동 허용 폭. 범위 벗어나면
        새 카테고리 (예: Lineage / Limit Break 류) 도입 가능성 탐지.
        """
        meta_count = len(self._meta_gem_names(skill_gems, base_items))
        assert 30 <= meta_count <= 60, (
            f"GemType=2 메타 젬 수 변동 큼: {meta_count} (조사 시 36). "
            "POE2 0.4.x 패치로 카테고리 변경 가능성 재조사 필요."
        )
