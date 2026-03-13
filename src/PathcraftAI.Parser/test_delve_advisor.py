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
# calc_safe_depth
# ──────────────────────────────────────

def test_life_build_low():
    """낮은 라이프 → 안전 깊이 150"""
    r = calc_safe_depth(life=1500, es=0)
    assert r["build_type"] == "life"
    assert r["safe_max_depth"] == 150


def test_life_build_mid():
    """라이프 3000 → 안전 깊이 300"""
    r = calc_safe_depth(life=3000, es=0)
    assert r["build_type"] == "life"
    assert r["safe_max_depth"] == 300


def test_life_build_high():
    """라이프 8000+ → 안전 깊이 900"""
    r = calc_safe_depth(life=9000, es=0)
    assert r["build_type"] == "life"
    assert r["safe_max_depth"] == 900


def test_es_build():
    """ES가 life의 2배 이상 → ES 빌드, 깊이 1.5배"""
    r = calc_safe_depth(life=1000, es=5000)
    assert r["build_type"] == "es"
    assert r["safe_max_depth"] == 750  # 500 * 1.5


def test_hybrid_build():
    """ES가 life보다 크지만 2배 미만 → 하이브리드"""
    r = calc_safe_depth(life=3000, es=4000)
    assert r["build_type"] == "hybrid"
    # effective = 3000 + 4000*0.5 = 5000 → 500
    assert r["safe_max_depth"] == 500


def test_zhp_flag():
    """안전 깊이 >= 1000이면 ZHP 권장"""
    r = calc_safe_depth(life=8000, es=20000)
    assert r["build_type"] == "es"
    assert r["needs_zhp"] is True


def test_zhp_not_needed():
    """안전 깊이 < 1000이면 ZHP 불필요"""
    r = calc_safe_depth(life=3000, es=0)
    assert r["needs_zhp"] is False


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
