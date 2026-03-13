# -*- coding: utf-8 -*-
"""
Delve Currency Advisor
POB 링크 + 현재 깊이 → 안전 파밍 깊이 + 가치 화석 + 세션 전략
"""

import json
import os
import sys
import argparse

# ────────────────────────────────────────────
# 깊이별 안전 기준 (탱 빌드 경험칙)
# ────────────────────────────────────────────
LIFE_DEPTH_TABLE = [
    (8000, 900),
    (6000, 700),
    (4000, 500),
    (2000, 300),
    (0,    150),
]

ES_MULTIPLIER = 1.5  # ES 빌드는 같은 수치에서 1.5배 더 깊이 가능
ZHP_TRANSITION_DEPTH = 1000  # 이 깊이 이상은 ZHP 권장

# 바이옴별 화석 (farming_mechanics.json 기반)
FOSSILS_BY_BIOME = {
    "Mines":            ["Metallic", "Serrated", "Pristine", "Aetheric"],
    "Fungal Caverns":   ["Dense", "Aberrant", "Corroded", "Gilded"],
    "Petrified Forest": ["Bound", "Jagged", "Sanctified"],
    "Frozen Hollow":    ["Frigid", "Prismatic", "Shuddering"],
    "Magma Fissure":    ["Scorched", "Pristine", "Fundamental"],
}

# 깊이별 주요 바이옴 (모든 바이옴은 모든 깊이에서 등장하지만 일반 가이드)
DEPTH_BIOME_TIPS = {
    150: "Mines 위주. Metallic/Serrated 기본 파밍.",
    300: "Fungal Caverns 추가. Gilded 고가치.",
    500: "Petrified Forest 접근. Sanctified 고가치.",
    700: "Frozen Hollow 안정. Prismatic 고가치.",
    900: "전 바이옴 접근 가능. ZHP 전환 고려 시점.",
}


def get_data_dir():
    return os.path.join(os.path.dirname(__file__), "data")


def get_game_data_dir():
    return os.path.join(os.path.dirname(__file__), "game_data")


def calc_safe_depth(life: int, es: int) -> dict:
    """생명력/ES 기반 안전 깊이 계산"""
    # 탱 빌드 판단: ES가 life보다 3배 이상이면 ES 빌드
    effective = life
    build_type = "life"
    if es > life * 2:
        effective = es
        build_type = "es"
    elif es > life:
        effective = life + es * 0.5
        build_type = "hybrid"

    safe = 150
    for threshold, depth in LIFE_DEPTH_TABLE:
        if effective >= threshold:
            safe = depth
            break

    if build_type == "es":
        safe = int(safe * ES_MULTIPLIER)

    return {
        "build_type": build_type,
        "effective_pool": int(effective),
        "safe_max_depth": safe,
        "zhp_transition_depth": ZHP_TRANSITION_DEPTH,
        "needs_zhp": safe >= ZHP_TRANSITION_DEPTH,
    }


def fetch_fossil_prices(league: str = None) -> dict:
    """poe.ninja에서 화석 가격 fetch (실패 시 빈 dict)"""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from poe_ninja_fetcher import fetch_category_data, get_latest_temp_league

        if not league:
            league = get_latest_temp_league()

        data = fetch_category_data(league, "fossils", "Fossil")
        if not data or "items" not in data:
            return {}

        prices = {}
        for item in data["items"]:
            name = item.get("name", "")
            chaos = item.get("chaosValue") or item.get("chaos") or 0
            if name and chaos:
                prices[name] = round(float(chaos), 1)
        return prices
    except Exception:
        return {}


def get_fossil_recommendations(safe_depth: int, fossil_prices: dict) -> list:
    """깊이에서 나오는 화석 + 현재 가격 조합"""
    results = []

    for biome, fossils in FOSSILS_BY_BIOME.items():
        for fossil in fossils:
            price = fossil_prices.get(fossil, None)
            results.append({
                "name": fossil,
                "biome": biome,
                "chaos_value": price,
                "priority": _get_priority(price),
            })

    # 중복 화석 제거 (Pristine은 Mines/Magma 둘 다 나옴)
    seen = {}
    deduped = []
    for r in results:
        key = r["name"]
        if key not in seen:
            seen[key] = True
            deduped.append(r)

    # 가격 높은 순 정렬 (가격 없는 건 뒤로)
    deduped.sort(key=lambda x: x["chaos_value"] if x["chaos_value"] else -1, reverse=True)
    return deduped[:10]  # 상위 10개


def _get_priority(price) -> str:
    if price is None:
        return "unknown"
    if price >= 20:
        return "high"
    if price >= 5:
        return "medium"
    return "low"


def get_session_strategy(current_depth: int, safe_depth: int, fossils: list) -> dict:
    """짧은 세션 기준 파밍 전략"""
    # 추천 파밍 깊이: 안전 범위의 80% (여유 있게)
    recommended = min(safe_depth, max(current_depth, int(safe_depth * 0.8)))

    # 고가치 화석
    high_value = [f for f in fossils if f["priority"] == "high"]
    target_biomes = list(set(f["biome"] for f in high_value[:3]))

    # 술파이트 효율 (기본 1,200 기준)
    sulphite_per_node = 120  # 평균
    nodes_per_session = 1200 // sulphite_per_node

    if current_depth >= safe_depth:
        warning = f"현재 깊이({current_depth})가 안전 범위({safe_depth}) 근접. 장비 업그레이드 또는 ZHP 전환 고려."
    else:
        warning = None

    return {
        "recommended_depth": recommended,
        "sulphite_base": 1200,
        "nodes_per_session": nodes_per_session,
        "target_biomes": target_biomes if target_biomes else list(FOSSILS_BY_BIOME.keys())[:2],
        "priority_order": "화석 노드 → 구역 보스 → 일반 길",
        "warning": warning,
    }


def run(pob_url: str, current_depth: int) -> dict:
    """메인 실행 함수"""
    # 1. POB 파싱
    build_info = {}
    stats = {}
    try:
        from pob_parser import get_pob_code_from_url, decode_pob_code, parse_pob_xml

        if pob_url.startswith("__CODE__"):
            # 직접 코드 입력
            code = pob_url[8:]
            xml = decode_pob_code(code)
        else:
            raw = get_pob_code_from_url(pob_url)
            if raw is None:
                raise ValueError("POB URL 접속 실패")
            if raw.startswith("__XML_DIRECT__"):
                xml = raw[14:]
            else:
                xml = decode_pob_code(raw)

        result = parse_pob_xml(xml, pob_url)
        if result:
            build_info = result.get("meta", {})
            stats = result.get("stats", {})
    except Exception as e:
        return {"error": f"POB 파싱 실패: {str(e)}"}

    life = stats.get("life", 0)
    es = stats.get("energy_shield", 0)
    res = stats.get("resistances", {})

    # 2. 안전 깊이 계산
    depth_info = calc_safe_depth(life, es)

    # 3. 화석 가격
    fossil_prices = fetch_fossil_prices()

    # 4. 화석 추천
    fossils = get_fossil_recommendations(depth_info["safe_max_depth"], fossil_prices)

    # 5. 세션 전략
    strategy = get_session_strategy(current_depth, depth_info["safe_max_depth"], fossils)

    # 6. 깊이 팁
    depth_tip = ""
    for depth_key in sorted(DEPTH_BIOME_TIPS.keys()):
        if depth_info["safe_max_depth"] <= depth_key:
            depth_tip = DEPTH_BIOME_TIPS[depth_key]
            break
    if not depth_tip:
        depth_tip = DEPTH_BIOME_TIPS[900]

    return {
        "build": {
            "name": build_info.get("build_name", "Unknown"),
            "class": build_info.get("class", ""),
            "ascendancy": build_info.get("ascendancy", ""),
        },
        "stats": {
            "life": life,
            "energy_shield": es,
            "resistances": res,
            "dps": stats.get("dps", 0),
        },
        "depth_analysis": {
            "current_depth": current_depth,
            "build_type": depth_info["build_type"],
            "effective_pool": depth_info["effective_pool"],
            "safe_max_depth": depth_info["safe_max_depth"],
            "zhp_recommended_at": depth_info["zhp_transition_depth"],
            "needs_zhp_now": depth_info["needs_zhp"],
            "depth_tip": depth_tip,
        },
        "fossils": fossils,
        "session_strategy": strategy,
        "prices_available": len(fossil_prices) > 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delve Currency Advisor")
    parser.add_argument("--pob", required=True, help="POB URL or __CODE__<base64>")
    parser.add_argument("--depth", type=int, default=100, help="현재 델브 깊이")
    args = parser.parse_args()

    result = run(args.pob, args.depth)

    # stdout에 JSON만 출력 (WPF가 파싱)
    print(json.dumps(result, ensure_ascii=False, indent=2))
