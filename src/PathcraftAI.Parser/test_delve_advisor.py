# -*- coding: utf-8 -*-
"""Delve Currency Advisor 테스트"""
import json
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from delve_advisor import (
    calc_safe_depth,
    get_fossil_recommendations,
    get_session_strategy,
    _get_priority,
    FOSSILS_BY_BIOME,
)


# ──────────────────────────────────────
# calc_safe_depth (종합 스탯 기반)
# ──────────────────────────────────────

def _make_stats(**overrides):
    """테스트용 기본 스탯 생성"""
    base = {
        "life": 5000, "energy_shield": 0, "ehp": 0,
        "armour": 0, "evasion": 0, "block": 0, "spell_block": 0,
        "dps": 500000,
        "resistances": {"fire": 75, "cold": 75, "lightning": 75, "chaos": 0},
    }
    base.update(overrides)
    return base


def test_low_ehp_low_depth():
    """낮은 EHP → 낮은 안전 깊이"""
    r = calc_safe_depth(_make_stats(life=1500, dps=100000))
    assert r["build_type"] == "life"
    assert r["safe_max_depth"] < 200


def test_mid_ehp_mid_depth():
    """중간 EHP → 중간 깊이"""
    r = calc_safe_depth(_make_stats(life=5000))
    assert 150 < r["safe_max_depth"] < 500


def test_high_ehp_high_depth():
    """높은 EHP + 방어 레이어 → 높은 깊이"""
    r = calc_safe_depth(_make_stats(
        life=8000, ehp=50000, armour=30000, block=60,
        dps=5000000, resistances={"fire": 80, "cold": 80, "lightning": 80, "chaos": 60}
    ))
    assert r["safe_max_depth"] >= 700


def test_es_build_type():
    """ES > life*2 → ES 빌드"""
    r = calc_safe_depth(_make_stats(life=1000, energy_shield=5000))
    assert r["build_type"] == "es"


def test_hybrid_build_type():
    """ES > life but < life*2 → 하이브리드"""
    r = calc_safe_depth(_make_stats(life=3000, energy_shield=4000))
    assert r["build_type"] == "hybrid"


def test_armor_bonus():
    """높은 아머 → 깊이 증가"""
    base = calc_safe_depth(_make_stats())
    armored = calc_safe_depth(_make_stats(armour=30000))
    assert armored["safe_max_depth"] > base["safe_max_depth"]


def test_block_bonus():
    """높은 블록 → 깊이 증가"""
    base = calc_safe_depth(_make_stats())
    blocked = calc_safe_depth(_make_stats(block=60))
    assert blocked["safe_max_depth"] > base["safe_max_depth"]


def test_dps_bonus():
    """높은 DPS → 깊이 증가"""
    low_dps = calc_safe_depth(_make_stats(dps=50000))
    high_dps = calc_safe_depth(_make_stats(dps=10000000))
    assert high_dps["safe_max_depth"] > low_dps["safe_max_depth"]


def test_negative_chaos_penalty():
    """카오스 저항 음수 → 깊이 감소"""
    pos = calc_safe_depth(_make_stats(
        resistances={"fire": 75, "cold": 75, "lightning": 75, "chaos": 30}
    ))
    neg = calc_safe_depth(_make_stats(
        resistances={"fire": 75, "cold": 75, "lightning": 75, "chaos": -60}
    ))
    assert neg["safe_max_depth"] < pos["safe_max_depth"]


def test_uncapped_res_penalty():
    """원소 저항 미캡 → 큰 깊이 감소"""
    capped = calc_safe_depth(_make_stats())
    uncapped = calc_safe_depth(_make_stats(
        resistances={"fire": 50, "cold": 50, "lightning": 50, "chaos": 0}
    ))
    assert uncapped["safe_max_depth"] < capped["safe_max_depth"]


def test_defense_details_populated():
    """방어 상세 정보가 채워지는지 확인"""
    r = calc_safe_depth(_make_stats(armour=30000, dps=10000000))
    details = r["defense_details"]
    stat_names = [d["stat"] for d in details]
    assert "아머" in stat_names
    assert "DPS" in stat_names


def test_zhp_flag():
    """안전 깊이 >= 1000이면 ZHP 권장"""
    r = calc_safe_depth(_make_stats(
        life=8000, energy_shield=20000, ehp=100000,
        armour=40000, block=70, dps=20000000,
        resistances={"fire": 80, "cold": 80, "lightning": 80, "chaos": 70}
    ))
    assert r["needs_zhp"] is True


def test_zhp_not_needed():
    """안전 깊이 < 1000이면 ZHP 불필요"""
    r = calc_safe_depth(_make_stats(life=3000, dps=100000))
    assert r["needs_zhp"] is False


def test_farming_depth_capped_at_500():
    """보상 스케일링이 ~500 캡이므로 추천 파밍은 500 이하"""
    r = calc_safe_depth(_make_stats(
        life=8000, armour=30000, dps=10000000,
        resistances={"fire": 80, "cold": 80, "lightning": 80, "chaos": 60}
    ))
    assert r["recommended_farming_depth"] <= 500


def test_depth_clamped():
    """최소 50, 최대 1500"""
    low = calc_safe_depth(_make_stats(life=0, dps=0))
    assert low["safe_max_depth"] >= 50
    high = calc_safe_depth(_make_stats(
        life=50000, energy_shield=50000, ehp=200000,
        armour=50000, evasion=50000, block=75, spell_block=60,
        dps=50000000,
        resistances={"fire": 85, "cold": 85, "lightning": 85, "chaos": 80}
    ))
    assert high["safe_max_depth"] <= 1500


# ──────────────────────────────────────
# _get_priority
# ──────────────────────────────────────

def test_priority_high():
    assert _get_priority(25) == "high"


def test_priority_medium():
    assert _get_priority(10) == "medium"


def test_priority_low():
    assert _get_priority(2) == "low"


def test_priority_unknown():
    assert _get_priority(None) == "unknown"


# ──────────────────────────────────────
# get_fossil_recommendations
# ──────────────────────────────────────

def test_fossil_recommendations_no_prices():
    """가격 없어도 추천 리스트 반환"""
    fossils = get_fossil_recommendations(300, {})
    assert len(fossils) > 0
    assert len(fossils) <= 10
    for f in fossils:
        assert "name" in f
        assert "biome" in f
        assert "priority" in f


def test_fossil_recommendations_with_prices():
    """가격 있으면 높은 순 정렬"""
    prices = {"Gilded": 50, "Metallic": 2, "Dense": 15}
    fossils = get_fossil_recommendations(500, prices)
    priced = [f for f in fossils if f["chaos_value"] is not None]
    assert priced[0]["name"] == "Gilded"
    assert priced[0]["priority"] == "high"


def test_fossil_dedup():
    """중복 화석 제거 (Pristine은 Mines + Magma 둘 다)"""
    fossils = get_fossil_recommendations(500, {})
    names = [f["name"] for f in fossils]
    assert len(names) == len(set(names))


# ──────────────────────────────────────
# get_session_strategy
# ──────────────────────────────────────

def test_session_strategy_safe():
    """현재 깊이 < 안전 깊이 → 경고 없음"""
    fossils = [{"name": "Gilded", "biome": "Fungal Caverns", "chaos_value": 50, "priority": "high"}]
    s = get_session_strategy(200, 500, fossils)
    assert s["warning"] is None
    assert s["recommended_depth"] <= 500
    assert s["nodes_per_session"] > 0


def test_session_strategy_danger():
    """현재 깊이 >= 안전 깊이 → 경고"""
    fossils = []
    s = get_session_strategy(500, 300, fossils)
    assert s["warning"] is not None
    assert "500" in s["warning"]


def test_session_strategy_target_biomes():
    """고가치 화석 바이옴 추천"""
    fossils = [
        {"name": "Gilded", "biome": "Fungal Caverns", "chaos_value": 50, "priority": "high"},
        {"name": "Sanctified", "biome": "Petrified Forest", "chaos_value": 30, "priority": "high"},
    ]
    s = get_session_strategy(300, 500, fossils)
    assert "Fungal Caverns" in s["target_biomes"]


# ──────────────────────────────────────
# CLI E2E
# ──────────────────────────────────────

def test_cli_dummy_code():
    """CLI 더미 코드 → JSON 출력, 크래시 없음"""
    result = subprocess.run(
        [sys.executable, "delve_advisor.py", "--pob", "__CODE__dummy", "--depth", "200"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
        timeout=30,
    )
    assert result.returncode == 0
    out = result.stdout
    start = out.index("{")
    end = out.rindex("}") + 1
    data = json.loads(out[start:end])
    assert "depth_analysis" in data
    assert "defense_details" in data["depth_analysis"]
    assert "fossils" in data
    assert "session_strategy" in data


def test_cli_real_pob():
    """CLI 실제 POB 코드 → 빌드 정보 추출"""
    code_file = os.path.join(os.path.dirname(__file__), "test_pob_code.txt")
    if not os.path.exists(code_file):
        return  # 테스트 데이터 없으면 스킵

    with open(code_file) as f:
        code = f.read().strip()

    result = subprocess.run(
        [sys.executable, "delve_advisor.py", "--pob", f"__CODE__{code}", "--depth", "300"],
        capture_output=True, text=True, cwd=os.path.dirname(__file__),
        timeout=30,
    )
    assert result.returncode == 0
    out = result.stdout
    start = out.index("{")
    end = out.rindex("}") + 1
    data = json.loads(out[start:end])

    assert data["build"]["class"] != ""
    assert data["stats"]["life"] > 0
    assert data["depth_analysis"]["safe_max_depth"] > 0
    assert "defense_details" in data["depth_analysis"]
