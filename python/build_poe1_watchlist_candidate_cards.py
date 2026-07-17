# -*- coding: utf-8 -*-
"""Build player-facing watchlist cards for user-considered PoE1 build ideas.

These cards are deliberately separate from the representative recommendation
pool. They surface interesting lanes for research/practice without promoting
them as default recommendations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cws_guide_loader import load_cws_card


ROOT = Path(__file__).resolve().parent.parent
EXPANDED_QUEUE_PATH = ROOT / "data" / "build_corpus_expanded_collection_queue_v1.json"
LUMINARY_PATH = ROOT / "data" / "poe1_3_29_luminary_merc_link_intake_v1.json"
OUTPUT_PATH = ROOT / "data" / "poe1_watchlist_candidate_cards.latest.json"

FOCUS_CANDIDATE_IDS = [
    "3.28_exsanguinate_reap_mines_trickster",
    "3.28_poison_carrion_golem_witch",
    "3.28_ignite_slamentalist_elementalist",
    "3.28_righteous_cold_dot_autobomber_elementalist",
    "3.29_reliquarian_dawnbreaker_rf",
    "3.29_reliquarian_hot_autobomber",
    "3.29_reliquarian_blight_contagion",
    "3.29_reliquarian_static_strike",
    "3.29_reliquarian_lightning_strike",
    "3.29_reliquarian_gloomfang_wander",
    "3.29_reliquarian_black_cane_spell",
    "3.29_reliquarian_sacred_chalice_bladefall",
]

LABEL_OVERRIDES = {
    "3.28_exsanguinate_reap_mines_trickster": "연습해도 됨",
    "3.28_poison_carrion_golem_witch": "연습해도 됨",
    "3.28_ignite_slamentalist_elementalist": "연습해도 됨",
    "3.28_righteous_cold_dot_autobomber_elementalist": "손봐야 가능",
}

REASON_OVERRIDES = {
    "3.28_exsanguinate_reap_mines_trickster": (
        "Cptn Garbage/FearlessDumb0 계열 Exsanguinate Miner 라인입니다. "
        "3.29 마인 보조 수치 재검증 전까지는 기본 추천이 아니라 연습 후보로 둡니다."
    ),
    "3.28_poison_carrion_golem_witch": (
        "토리센세가 이번 시즌 준비 중이라고 제보된 소환수 라인입니다. "
        "현재 시즌 PoB를 확보하면 우선 승격 검토합니다."
    ),
    "3.28_ignite_slamentalist_elementalist": (
        "Master T 쪽 Witch ignite/slam 전환 라인입니다. "
        "레벨링 흐름은 참고하되 3.29 최종 수치와 패시브를 다시 봐야 합니다."
    ),
    "3.28_righteous_cold_dot_autobomber_elementalist": (
        "Master T Righteous Cold DoT Autobomber 전환 후보입니다. "
        "엔드게임 전환용으로 보고, 스타터 추천과는 분리합니다."
    ),
}

LANE_LABELS = {
    "trap_mine_totem": "마인/토템",
    "minion_trigger_autobomber_special": "소환수/트리거",
    "melee_strike_slam": "근접/슬램",
    "dot_ailment_dot": "DoT/상태이상",
    "spell_hit_brand_selfcast": "주문/브랜드",
    "bow_projectile_attack_mapper": "활/투사체",
    "cws": "CWS",
    "luminary_link": "루미너리 링크",
}

NEXT_STEP_LABELS = {
    "find_or_archive_pob": "PoB/PoBB 원본 확보",
    "normalize_two_state_snapshots": "레벨링/맵핑 상태 분리",
    "run_build_instance_readiness": "3.29 패치 영향 검증",
    "record_beginner_failure_lens": "초보자 실패 포인트 기록",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _queue_candidates(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for patch in queue.get("patches", []):
        for candidate in patch.get("candidates", []):
            rows[candidate["candidate_id"]] = candidate
    return rows


def _source_cards(source_registry: dict[str, Any], source_refs: list[str]) -> list[dict[str, Any]]:
    cards = []
    for source_id in source_refs:
        source = source_registry.get(source_id, {})
        url = source.get("url")
        if isinstance(url, str) and url.startswith("C:\\"):
            url = None
        cards.append({
            "source_id": source_id,
            "label": source.get("label", source_id),
            "url": url,
            "family": source.get("family", "unknown"),
        })
    return cards


def _candidate_label(candidate: dict[str, Any]) -> str:
    candidate_id = candidate["candidate_id"]
    if candidate_id in LABEL_OVERRIDES:
        return LABEL_OVERRIDES[candidate_id]
    if candidate.get("patch") == "3.29":
        return "구경만"
    if candidate.get("collection_role") == "failure_edge_case":
        return "손봐야 가능"
    return "연습해도 됨"


def _candidate_reason(candidate: dict[str, Any]) -> str:
    candidate_id = candidate["candidate_id"]
    if candidate_id in REASON_OVERRIDES:
        return REASON_OVERRIDES[candidate_id]
    if candidate.get("patch") == "3.29":
        return "3.29 신규/복귀 메커니즘 후보라 PoB, 패시브, 실제 플레이 확인 전까지 관찰 대상으로 둡니다."
    return "과거 시즌 자료 기반 후보입니다. 현재 패치에서 직접 PoB와 패시브를 다시 확인해야 합니다."


def _public_candidate(candidate: dict[str, Any], source_registry: dict[str, Any]) -> dict[str, Any]:
    source_refs = candidate.get("source_refs") or []
    sources = _source_cards(source_registry, source_refs)
    return {
        "candidate_id": candidate["candidate_id"],
        "display_name": candidate["display_name"],
        "patch": candidate.get("patch"),
        "main_skill": candidate.get("main_skill"),
        "class_name": candidate.get("class_name"),
        "ascendancy": candidate.get("ascendancy"),
        "lane_id": candidate.get("lane_id"),
        "lane_label": LANE_LABELS.get(candidate.get("lane_id"), candidate.get("lane_id")),
        "player_label": _candidate_label(candidate),
        "default_recommendation": False,
        "reason": _candidate_reason(candidate),
        "tags": [
            candidate.get("patch"),
            LANE_LABELS.get(candidate.get("lane_id"), candidate.get("lane_id")),
            candidate.get("class_name"),
            candidate.get("ascendancy"),
        ],
        "source_count": len(sources),
        "sources": sources[:5],
        "next_actions": [
            NEXT_STEP_LABELS.get(step, step)
            for step in candidate.get("required_next_steps", [])[:4]
        ],
    }


def _luminary_cards(luminary: dict[str, Any]) -> list[dict[str, Any]]:
    selected = {
        "destructive_link_crit_merc",
        "intuitive_link_trigger_merc",
    }
    cards = []
    for hypothesis in luminary.get("link_skill_hypotheses", []):
        if hypothesis.get("hypothesis_id") not in selected:
            continue
        cards.append({
            "candidate_id": f"3.29_luminary_{hypothesis['hypothesis_id']}",
            "display_name": hypothesis.get("label"),
            "patch": "3.29",
            "main_skill": "Link Skill",
            "class_name": "Scion",
            "ascendancy": "Luminary",
            "lane_id": "luminary_link",
            "lane_label": LANE_LABELS["luminary_link"],
            "player_label": "구경만",
            "default_recommendation": False,
            "reason": f"{hypothesis.get('risk')} 노드명, 용병 스킬, PoB 지원이 확인되기 전까지 관찰 후보입니다.",
            "tags": ["3.29", "Luminary", "Mercenary", "Link"],
            "source_count": 1,
            "sources": [{
                "source_id": "user_luminary_notes",
                "label": "사용자 제공 Luminary 메모 요약",
                "url": None,
                "family": "user_notes",
            }],
            "next_actions": [
                "루미너리 노드명 확인",
                "용병 스킬/장비 제한 확인",
                "PoB 지원 여부 확인",
            ],
        })
    return cards


def build_watchlist_candidate_cards() -> dict[str, Any]:
    queue = _load_json(EXPANDED_QUEUE_PATH)
    luminary = _load_json(LUMINARY_PATH)
    source_registry = queue.get("source_registry", {})
    candidates = _queue_candidates(queue)

    cards = [
        _public_candidate(candidates[candidate_id], source_registry)
        for candidate_id in FOCUS_CANDIDATE_IDS
        if candidate_id in candidates
    ]

    # CWS card now comes from the canonical external-guide JSON, not a hardcoded dict.
    cards.append(load_cws_card())

    cards.extend(_luminary_cards(luminary))

    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_watchlist_candidate_cards",
        "generated_at": "2026-07-17",
        "summary": {
            "card_count": len(cards),
            "default_recommendation_count": sum(1 for card in cards if card["default_recommendation"]),
            "source": "expanded_collection_queue_plus_user_focus_lanes",
        },
        "cards": cards,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    payload = build_watchlist_candidate_cards()
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
