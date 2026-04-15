# -*- coding: utf-8 -*-
"""PathcraftAI Syndicate Advisor — POB 빌드 데이터 기반 Syndicate 레이아웃 추천.

휴리스틱 기반 (빌드 특성 매칭 → 사전 정의된 레이아웃 중 최적 선택).
AI API 호출 없이 수십 ms 내 응답.

사용법:
    python syndicate_advisor.py build.json
    python syndicate_advisor.py - < build.json  # stdin
"""

import json
import sys
import logging
from pathlib import Path

logger = logging.getLogger("syndicate_advisor")


def _load_layouts() -> list[dict]:
    path = Path(__file__).resolve().parent.parent / "data" / "syndicate_layouts.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("layouts", [])


def _detect_build_needs(build_data: dict) -> dict[str, int]:
    """빌드 데이터에서 니즈 점수 추출 — 각 전략 카테고리별 0~10 가중치."""
    needs = {
        "veiled_craft": 3,       # 기본값 — 모든 빌드가 웬만큼 필요
        "currency_farm": 5,      # 기본 커런시 파밍 니즈
        "scarab_farming": 2,
        "jewelry_crafting": 3,
        "gem_leveling": 2,
    }

    # items 기반: rare 장비 많으면 veiled/jewelry craft 높게
    items = build_data.get("items", [])
    rare_count = sum(1 for i in items if isinstance(i, dict) and i.get("rarity", "").lower() == "rare")
    if rare_count >= 4:
        needs["veiled_craft"] += 2
        needs["jewelry_crafting"] += 2

    # 유니크 의존도 높으면 currency_farm 높게 (유니크 구매/교환)
    unique_count = sum(1 for i in items if isinstance(i, dict) and i.get("rarity", "").lower() == "unique")
    if unique_count >= 5:
        needs["currency_farm"] += 3

    # 빌드 노트/이름 — Mageblood/Headhunter 등 고가 유니크 → currency_farm 극대
    meta = build_data.get("meta", {})
    name = str(meta.get("build_name", "")).lower()
    high_value_uniques = ("mageblood", "headhunter", "ashes of the stars",
                         "forbidden flame", "forbidden flesh", "omniscience")
    for hv in high_value_uniques:
        if hv in name:
            needs["currency_farm"] += 5
            break

    # 스킬 젬 수 많으면 gem_leveling 니즈 있음
    progression = build_data.get("progression_stages", [])
    if progression:
        gem_setups = progression[-1].get("gem_setups", {}) if isinstance(progression[-1], dict) else {}
        total_gems = sum(
            len(v) if isinstance(v, list) else len(v.get("links", "").split(" - ")) if isinstance(v, dict) else 0
            for v in gem_setups.values()
        )
        if total_gems >= 8:
            needs["gem_leveling"] += 2

    # Awakened 젬 감지 — 젬 경험치 파밍 니즈
    progression_str = json.dumps(progression, ensure_ascii=False).lower()
    if "awakened" in progression_str:
        needs["gem_leveling"] += 4

    return needs


def recommend_layout(build_data: dict) -> dict:
    """빌드 데이터 기반으로 가장 적합한 Syndicate 레이아웃 선택 + 이유."""
    layouts = _load_layouts()
    if not layouts:
        return {
            "layout_id": "",
            "layout_name": "",
            "reason": "레이아웃 데이터 없음",
            "needs": {},
            "candidates": [],
        }

    needs = _detect_build_needs(build_data)

    # 각 레이아웃의 priority 키에 해당하는 needs 점수로 랭킹
    scored = []
    for layout in layouts:
        priority = layout.get("priority", "")
        # priority가 복합일 수 있음 (e.g., "currency + veiled craft")
        score = 0
        for need_key, need_val in needs.items():
            if need_key.replace("_", " ") in priority or need_key in priority:
                score += need_val
        # fallback: priority 텍스트 매칭
        if score == 0:
            if "currency" in priority.lower():
                score = needs.get("currency_farm", 0)
            elif "veiled" in priority.lower() or "craft" in priority.lower():
                score = needs.get("veiled_craft", 0)
            elif "scarab" in priority.lower():
                score = needs.get("scarab_farming", 0)
            elif "jewelry" in priority.lower() or "jewel" in priority.lower():
                score = needs.get("jewelry_crafting", 0)
            elif "gem" in priority.lower():
                score = needs.get("gem_leveling", 0)
        scored.append((score, layout))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0][1] if scored else layouts[0]

    # 추천 이유 생성
    top_needs = sorted(needs.items(), key=lambda x: x[1], reverse=True)[:2]
    need_labels = {
        "veiled_craft": "Veiled 크래프팅",
        "currency_farm": "커런시 파밍",
        "scarab_farming": "스카라브 파밍",
        "jewelry_crafting": "쥬얼리 크래프팅",
        "gem_leveling": "젬 레벨업/품질",
    }
    reason_parts = [
        f"빌드 특성상 {need_labels.get(n, n)} 니즈 높음 (점수 {v})"
        for n, v in top_needs
    ]
    reason = " | ".join(reason_parts) + f" → {top.get('name', '')} 추천"

    return {
        "layout_id": top.get("id", ""),
        "layout_name": top.get("name", ""),
        "reason": reason,
        "needs": needs,
        "candidates": [
            {"layout_id": l.get("id"), "name": l.get("name"), "score": s}
            for s, l in scored
        ],
    }


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: syndicate_advisor.py <build.json | ->"},
                         ensure_ascii=False))
        sys.exit(2)

    arg = sys.argv[1]
    if arg == "-":
        build_data = json.load(sys.stdin)
    else:
        with open(arg, "r", encoding="utf-8") as f:
            build_data = json.load(f)

    result = recommend_layout(build_data)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
