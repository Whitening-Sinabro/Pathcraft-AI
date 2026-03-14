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
# 델브 깊이 계산 상수
# 3.19 리밸런스 기준: 깊이 500 ≈ 이전 1000
# 보상 스케일링은 ~500에서 멈춤
# ────────────────────────────────────────────
ZHP_TRANSITION_DEPTH = 1000

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


def calc_safe_depth(stats: dict) -> dict:
    """종합 방어 스탯 기반 안전 깊이 계산

    고려 요소: EHP, 아머, 회피, 블록, 저항, DPS
    3.19 리밸런스: 깊이 500 ≈ 이전 1000, 보상은 ~500 캡
    """
    life = stats.get("life", 0)
    es = stats.get("energy_shield", 0)
    ehp = stats.get("ehp", 0)
    armour = stats.get("armour", 0)
    evasion = stats.get("evasion", 0)
    block = stats.get("block", 0)
    spell_block = stats.get("spell_block", 0)
    resistances = stats.get("resistances", {})
    dps = stats.get("dps", 0)

    # ── 빌드 타입 판단 ──
    if es > life * 2:
        build_type = "es"
    elif es > life:
        build_type = "hybrid"
    else:
        build_type = "life"

    # ── 1. EHP 기반 기본 깊이 (연속 함수) ──
    effective_pool = ehp if ehp > 0 else (life + es)

    if effective_pool <= 0:
        base_depth = 50
    elif effective_pool < 3000:
        base_depth = 50 + (effective_pool / 3000) * 100
    elif effective_pool < 10000:
        base_depth = 150 + (effective_pool - 3000) / 7000 * 150
    elif effective_pool < 30000:
        base_depth = 300 + (effective_pool - 10000) / 20000 * 200
    elif effective_pool < 80000:
        base_depth = 500 + (effective_pool - 30000) / 50000 * 200
    else:
        base_depth = 700 + min(300, (effective_pool - 80000) / 100000 * 300)

    # ── 2. 방어 레이어 보너스 ──
    defense_bonus = 0
    defense_details = []

    # 아머 (물리 경감)
    if armour >= 30000:
        defense_bonus += 80
        defense_details.append({"stat": "아머", "value": armour, "grade": "S"})
    elif armour >= 15000:
        defense_bonus += 40
        defense_details.append({"stat": "아머", "value": armour, "grade": "A"})
    elif armour >= 5000:
        defense_bonus += 15
        defense_details.append({"stat": "아머", "value": armour, "grade": "B"})

    # 회피
    if evasion >= 30000:
        defense_bonus += 60
        defense_details.append({"stat": "회피", "value": evasion, "grade": "S"})
    elif evasion >= 15000:
        defense_bonus += 30
        defense_details.append({"stat": "회피", "value": evasion, "grade": "A"})
    elif evasion >= 5000:
        defense_bonus += 10
        defense_details.append({"stat": "회피", "value": evasion, "grade": "B"})

    # 블록
    if block >= 60:
        defense_bonus += 80
        defense_details.append({"stat": "블록", "value": block, "grade": "S"})
    elif block >= 40:
        defense_bonus += 40
        defense_details.append({"stat": "블록", "value": block, "grade": "A"})
    elif block >= 20:
        defense_bonus += 10
        defense_details.append({"stat": "블록", "value": block, "grade": "B"})

    # 주문 블록
    if spell_block >= 50:
        defense_bonus += 50
        defense_details.append({"stat": "주문 블록", "value": spell_block, "grade": "S"})
    elif spell_block >= 30:
        defense_bonus += 25
        defense_details.append({"stat": "주문 블록", "value": spell_block, "grade": "A"})

    # ── 3. 저항 보너스/패널티 ──
    res_bonus = 0
    fire = resistances.get("fire", 75)
    cold = resistances.get("cold", 75)
    light = resistances.get("lightning", 75)
    chaos = resistances.get("chaos", 0)

    # 원소 저항: 캡 미달 시 큰 패널티
    for name, val in [("화염", fire), ("냉기", cold), ("번개", light)]:
        if val >= 80:
            res_bonus += 10
        elif val < 75:
            res_bonus -= 40
            defense_details.append({"stat": f"{name} 저항", "value": val, "grade": "F"})

    # 카오스 저항: 깊은 델브에서 매우 중요
    if chaos >= 60:
        res_bonus += 30
        defense_details.append({"stat": "카오스 저항", "value": chaos, "grade": "S"})
    elif chaos >= 20:
        res_bonus += 10
        defense_details.append({"stat": "카오스 저항", "value": chaos, "grade": "B"})
    elif chaos < 0:
        res_bonus -= 40
        defense_details.append({"stat": "카오스 저항", "value": chaos, "grade": "F"})

    # ── 4. DPS 보너스 (킬속도 = 안전) ──
    dps_bonus = 0
    if dps >= 10_000_000:
        dps_bonus = 80
        defense_details.append({"stat": "DPS", "value": dps, "grade": "S"})
    elif dps >= 3_000_000:
        dps_bonus = 40
        defense_details.append({"stat": "DPS", "value": dps, "grade": "A"})
    elif dps >= 1_000_000:
        dps_bonus = 20
        defense_details.append({"stat": "DPS", "value": dps, "grade": "B"})
    elif dps >= 200_000:
        dps_bonus = 5
    elif dps > 0 and dps < 100_000:
        dps_bonus = -20
        defense_details.append({"stat": "DPS", "value": dps, "grade": "F"})

    # ── 최종 계산 ──
    total_bonus = defense_bonus + res_bonus + dps_bonus
    safe_depth = int(base_depth + total_bonus)
    safe_depth = max(50, min(safe_depth, 1500))

    # 파밍 추천 깊이 (보상은 ~500 캡)
    if safe_depth >= 500:
        farming_rec = 500
    else:
        farming_rec = safe_depth

    return {
        "build_type": build_type,
        "effective_pool": int(effective_pool),
        "safe_max_depth": safe_depth,
        "recommended_farming_depth": farming_rec,
        "defense_score": total_bonus,
        "defense_details": defense_details,
        "zhp_transition_depth": ZHP_TRANSITION_DEPTH,
        "needs_zhp": safe_depth >= ZHP_TRANSITION_DEPTH,
    }


def _check_https_available() -> bool:
    """HTTPS 연결 가능 여부 빠른 확인 (1초 타임아웃)"""
    import socket, ssl
    try:
        s = socket.create_connection(("poe.ninja", 443), timeout=1)
        ctx = ssl.create_default_context()
        ss = ctx.wrap_socket(s, server_hostname="poe.ninja")
        ss.close()
        return True
    except Exception:
        return False


def fetch_fossil_prices(league: str = None) -> dict:
    """poe.ninja에서 화석 가격 fetch (실패 시 빈 dict)"""
    try:
        # HTTPS 차단 환경이면 즉시 스킵 (VPN/백신 등)
        if not _check_https_available():
            print("[Delve] HTTPS 차단 감지 → 화석 가격 스킵", file=sys.stderr)
            return {}

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
            # 테스트용 직접 코드 입력
            code = pob_url[8:]
            xml = decode_pob_code(code)
        elif pob_url.startswith(("http://", "https://", "pobb.in", "pastebin.com")):
            # URL → fetch
            print(f"[Delve] URL 모드: {pob_url[:80]}", file=sys.stderr)
            raw = get_pob_code_from_url(pob_url)
            if raw is None:
                raise ValueError(f"POB URL 접속 실패: {pob_url[:80]}")
            if raw.startswith("__XML_DIRECT__"):
                xml = raw[14:]
            else:
                xml = decode_pob_code(raw)
        else:
            # base64 POB 코드 직접 입력
            print(f"[Delve] 코드 모드 (길이: {len(pob_url)})", file=sys.stderr)
            xml = decode_pob_code(pob_url)

        result = parse_pob_xml(xml, pob_url)
        if result:
            build_info = result.get("meta", {})
            stats = result.get("stats", {})
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {"error": f"POB 파싱 실패: {str(e)}"}

    life = stats.get("life", 0)
    es = stats.get("energy_shield", 0)
    res = stats.get("resistances", {})

    # 2. 안전 깊이 계산 (전체 스탯 기반)
    depth_info = calc_safe_depth(stats)

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
            "armour": stats.get("armour", 0),
            "evasion": stats.get("evasion", 0),
            "block": stats.get("block", 0),
            "spell_block": stats.get("spell_block", 0),
        },
        "depth_analysis": {
            "current_depth": current_depth,
            "build_type": depth_info["build_type"],
            "effective_pool": depth_info["effective_pool"],
            "safe_max_depth": depth_info["safe_max_depth"],
            "recommended_farming_depth": depth_info["recommended_farming_depth"],
            "defense_score": depth_info["defense_score"],
            "defense_details": depth_info["defense_details"],
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
    parser.add_argument("--pob", required=True, help="POB URL, base64 code, or '-' to read from stdin")
    parser.add_argument("--depth", type=int, default=100, help="현재 델브 깊이")
    args = parser.parse_args()

    pob_input = args.pob
    if pob_input == "-":
        pob_input = sys.stdin.read().strip()

    result = run(pob_input, args.depth)

    # stdout에 JSON만 출력 (WPF가 파싱)
    print(json.dumps(result, ensure_ascii=False, indent=2))
