# -*- coding: utf-8 -*-
"""defense_type_extractor 단위 테스트 (D1)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from defense_type_extractor import (  # noqa: E402
    classify_defence_from_stats,
    extract_build_defence_types,
    DEFAULT_HYBRID_THRESHOLD,
)


class TestClassifyDefenceFromStats:
    def test_all_zero_returns_empty(self):
        """모든 수치 0 → 빈 집합 (빌드 미완성)."""
        assert classify_defence_from_stats(0, 0, 0) == frozenset()

    def test_negative_treated_as_zero(self):
        """음수도 방어적으로 빈 집합."""
        assert classify_defence_from_stats(-100, 0, 0) == frozenset()

    def test_pure_armour_marauder(self):
        """Juggernaut 30000 armour, 0 ev, 200 ES → {"ar"} (ES는 임계 미만)."""
        # 200 < 30000 * 0.3 = 9000
        assert classify_defence_from_stats(30000, 0, 200) == frozenset({"ar"})

    def test_pure_evasion_raider(self):
        """Raider 18000 ev, 100 armour, 0 ES → {"ev"}."""
        assert classify_defence_from_stats(100, 18000, 0) == frozenset({"ev"})

    def test_pure_es_ci_witch(self):
        """CI Witch 8000 ES, 0 armour, 0 ev → {"es"}."""
        assert classify_defence_from_stats(0, 0, 8000) == frozenset({"es"})

    def test_hybrid_ar_ev_duelist(self):
        """Gladiator 15000 armour + 12000 ev → {"ar", "ev"} (12000 > 4500)."""
        result = classify_defence_from_stats(15000, 12000, 0)
        assert result == frozenset({"ar", "ev"})

    def test_hybrid_es_ev_trickster(self):
        """Trickster 6000 ES + 5000 ev → {"es", "ev"}."""
        result = classify_defence_from_stats(0, 5000, 6000)
        assert result == frozenset({"es", "ev"})

    def test_triple_hybrid(self):
        """세 속성 모두 주속성의 30% 이상 → 세 axis 모두 포함."""
        result = classify_defence_from_stats(10000, 5000, 4000)
        # 5000 >= 3000, 4000 >= 3000
        assert result == frozenset({"ar", "ev", "es"})

    def test_below_threshold_excluded(self):
        """주속성의 30% 미만 부속성은 제외."""
        # 10000 armour, 2000 ev (20% — threshold 3000 미만 → 제외), 0 ES
        result = classify_defence_from_stats(10000, 2000, 0)
        assert result == frozenset({"ar"})

    def test_custom_threshold(self):
        """hybrid_threshold 파라미터 조정 동작."""
        # 10000 armour + 2000 ev (20%)
        # threshold 0.15로 낮추면 ev 포함
        result = classify_defence_from_stats(10000, 2000, 0, hybrid_threshold=0.15)
        assert result == frozenset({"ar", "ev"})


class TestExtractBuildDefenceTypes:
    def test_none_build_returns_empty(self):
        """None 입력 방어적 처리."""
        assert extract_build_defence_types(None) == frozenset()

    def test_empty_dict_returns_empty(self):
        """stats 키 없는 dict."""
        assert extract_build_defence_types({}) == frozenset()

    def test_stats_non_dict_returns_empty(self):
        """stats가 dict 아닌 경우 (스키마 손상)."""
        assert extract_build_defence_types({"stats": "broken"}) == frozenset()

    def test_reads_pob_parser_schema(self):
        """pob_parser.py:348-358 schema 직접 소비."""
        build = {
            "stats": {
                "dps": 50000,
                "life": 5000,
                "energy_shield": 0,
                "armour": 25000,
                "evasion": 500,
            }
        }
        assert extract_build_defence_types(build) == frozenset({"ar"})

    def test_missing_field_treated_as_zero(self):
        """stats에 일부 방어 필드 누락 시 0으로 처리."""
        build = {"stats": {"armour": 20000}}  # ev, es 누락
        assert extract_build_defence_types(build) == frozenset({"ar"})

    def test_none_value_treated_as_zero(self):
        """stats 필드가 None인 경우 0 처리 (pobapi 실패 케이스)."""
        build = {"stats": {"armour": None, "evasion": 10000, "energy_shield": 0}}
        assert extract_build_defence_types(build) == frozenset({"ev"})
