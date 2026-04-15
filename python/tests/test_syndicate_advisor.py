# -*- coding: utf-8 -*-
"""Syndicate Advisor 회귀 테스트 — 빌드 특성 → 레이아웃 추천 매핑 검증."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from syndicate_advisor import recommend_layout, _detect_build_needs


def _mk_build(name: str = "Test", level: int = 90,
              items: list | None = None,
              gem_setups: dict | None = None) -> dict:
    return {
        "meta": {"build_name": name, "class_level": level, "class": "Templar"},
        "items": items or [],
        "progression_stages": [{
            "gem_setups": gem_setups or {},
            "gear_recommendation": {},
        }],
    }


class TestSyndicateNeeds:
    """빌드 특성 → 니즈 점수 계산."""

    def test_default_needs(self):
        """빈 빌드 — 기본 가중치만."""
        needs = _detect_build_needs(_mk_build())
        assert needs["currency_farm"] == 5  # base
        assert needs["veiled_craft"] == 3
        assert needs["gem_leveling"] == 2

    def test_mageblood_boosts_currency(self):
        """Mageblood 이름 감지 → currency_farm +5."""
        needs = _detect_build_needs(_mk_build(name="Mageblood Inquisitor"))
        assert needs["currency_farm"] >= 10

    def test_headhunter_boosts_currency(self):
        needs = _detect_build_needs(_mk_build(name="HeadHunter Deadeye"))
        assert needs["currency_farm"] >= 10

    def test_rare_heavy_boosts_craft(self):
        """Rare 장비 4+ → veiled/jewelry craft 증가."""
        items = [{"rarity": "rare"} for _ in range(5)]
        needs = _detect_build_needs(_mk_build(items=items))
        assert needs["veiled_craft"] >= 5
        assert needs["jewelry_crafting"] >= 5

    def test_awakened_gem_boosts_gem_leveling(self):
        """progression에 'awakened' 키워드 → gem_leveling +4."""
        gems = {"Awakened Fork": {"links": "Awakened Fork Support"}}
        needs = _detect_build_needs(_mk_build(gem_setups=gems))
        assert needs["gem_leveling"] >= 6


class TestSyndicateRecommendation:
    """빌드 → 최적 레이아웃 추천."""

    def test_mageblood_picks_currency_layout(self):
        """Mageblood는 SS22 또는 Aisling (currency 관련) 추천."""
        rec = recommend_layout(_mk_build(name="Mageblood Gladiator"))
        assert rec["layout_id"] in ("ss22", "aisling_fixed", "jewelry_craft")
        assert "커런시" in rec["reason"] or "Veiled" in rec["reason"]

    def test_returns_valid_layout_id(self):
        """어떤 빌드든 유효한 layout_id 반환."""
        rec = recommend_layout(_mk_build())
        assert rec["layout_id"] != ""
        assert rec["layout_name"] != ""
        assert "needs" in rec
        assert "candidates" in rec

    def test_candidates_sorted_desc(self):
        """candidates는 score 내림차순."""
        rec = recommend_layout(_mk_build(name="Mageblood"))
        scores = [c["score"] for c in rec["candidates"]]
        assert scores == sorted(scores, reverse=True)

    def test_empty_build_still_returns_fallback(self):
        """빈 빌드도 에러 없이 fallback 레이아웃 반환."""
        rec = recommend_layout({"meta": {}, "items": [], "progression_stages": []})
        assert rec["layout_id"] != ""  # 레이아웃 DB에서 첫 번째라도 반환
