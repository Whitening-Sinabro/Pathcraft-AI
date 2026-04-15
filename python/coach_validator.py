# -*- coding: utf-8 -*-
"""AI Coach 출력 검증 — hallucination 자동 탐지.

검증 항목:
1. 스키마 — 필수 필드 존재, 타입 일치
2. quest_rewards cross-check — skill_transitions의 level/change가
   실제 퀘스트 보상 젬/레벨과 일치하는지
3. 값 범위 — build_rating 1~5, level 1~100 등

경고만 발생, 출력은 보존 (UI에서 "⚠️ AI 생성 데이터" 뱃지 표시 가능).
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("coach_validator")


def _load_quest_rewards() -> dict:
    path = Path(__file__).resolve().parent.parent / "data" / "quest_rewards.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


# 퀘스트 보상 젬 → {gem_name: {class: [quest_name, npc, act, min_level]}} 역인덱스
_GEM_QUEST_INDEX: dict = {}
_INDEX_BUILT = False


def _build_gem_quest_index():
    global _INDEX_BUILT, _GEM_QUEST_INDEX
    if _INDEX_BUILT:
        return
    qr = _load_quest_rewards()
    quests = qr.get("quests", [])
    for q in quests:
        rewards = q.get("rewards", {})
        # quest 레벨 추정 — POE Wiki 기준 일반 퀘스트 레벨 mapping
        # Enemy at the Gate=1, Mercy Mission=2(Lv8 gem avail), Breaking Some Eggs=2(Lv18),
        # A Fixture of Fate=3(Lv28), Piety=5(Lv38), Ribbon Spool=3(Lv31)
        quest_lv_map = {
            "Enemy at the Gate": 2, "Mercy Mission": 8, "Breaking Some Eggs": 18,
            "The Caged Brute": 8, "The Siren's Cadence": 10,
            "Intruders in Black": 12, "Through Sacred Ground": 14, "Way Forward": 16,
            "Sharp and Cruel": 16, "Ribbon Spool": 31,
            "A Fixture of Fate": 28, "Piety's Pets": 38, "Victario's Secrets": 38,
            "Lost in Love": 28, "Death to Purity": 48,
        }
        approx_level = quest_lv_map.get(q.get("name", ""), q.get("act", 1) * 5)
        for cls, gems in rewards.items():
            if not isinstance(gems, list):
                continue
            for gem in gems:
                if gem not in _GEM_QUEST_INDEX:
                    _GEM_QUEST_INDEX[gem] = []
                _GEM_QUEST_INDEX[gem].append({
                    "class": cls, "quest": q.get("name"),
                    "act": q.get("act"), "approx_level": approx_level,
                })
    _INDEX_BUILT = True


REQUIRED_FIELDS = {
    "build_summary": str, "tier": str,
    "strengths": list, "weaknesses": list,
    "leveling_guide": dict,
    "leveling_skills": dict,
    "build_rating": dict,
    "gear_progression": list,
}


def validate_coach_output(result: dict, build_data: dict | None = None) -> list[str]:
    """Coach 결과 JSON 검증. 경고 메시지 리스트 반환 (빈 리스트 = OK)."""
    warnings: list[str] = []

    # 1. 스키마 — 필수 필드 + 타입
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in result:
            warnings.append(f"[스키마] 필수 필드 누락: {field}")
        elif not isinstance(result[field], expected_type):
            warnings.append(
                f"[스키마] {field} 타입 불일치: "
                f"기대 {expected_type.__name__}, 실제 {type(result[field]).__name__}"
            )

    # 2. build_rating 값 범위 (1~5)
    rating = result.get("build_rating", {})
    if isinstance(rating, dict):
        for key, val in rating.items():
            if isinstance(val, (int, float)) and not (1 <= val <= 5):
                warnings.append(f"[범위] build_rating.{key}={val} (1~5 기대)")

    # 3. skill_transitions 레벨 범위 + quest_rewards cross-check
    lvl_skills = result.get("leveling_skills", {})
    transitions = lvl_skills.get("skill_transitions", [])
    if isinstance(transitions, list):
        _build_gem_quest_index()
        build_class = (build_data or {}).get("meta", {}).get("class", "")
        for i, t in enumerate(transitions):
            if not isinstance(t, dict):
                continue
            lv = t.get("level")
            if isinstance(lv, (int, float)) and not (1 <= lv <= 100):
                warnings.append(f"[범위] skill_transitions[{i}].level={lv} (1~100 기대)")

            # change 필드에서 젬 이름 추출해 실제 퀘스트 레벨과 비교
            change = t.get("change", "")
            if isinstance(change, str) and isinstance(lv, (int, float)):
                for gem_name, quest_info_list in _GEM_QUEST_INDEX.items():
                    if gem_name.lower() in change.lower():
                        # 해당 클래스 보상인지 확인
                        class_matches = [
                            qi for qi in quest_info_list
                            if not build_class or qi["class"] == build_class
                        ]
                        if not class_matches:
                            warnings.append(
                                f"[퀘스트] '{gem_name}'은 {build_class} 클래스 퀘스트 보상 아님"
                            )
                            break
                        # 권장 레벨과 5 이상 차이면 경고
                        for qi in class_matches:
                            if abs(lv - qi["approx_level"]) >= 8:
                                warnings.append(
                                    f"[퀘스트] skill_transitions[{i}] Lv.{lv} '{gem_name}' — "
                                    f"실제 퀘스트 '{qi['quest']}' 보상은 Lv ~{qi['approx_level']} "
                                    f"(차이 {abs(int(lv) - qi['approx_level'])})"
                                )
                            break
                        break

    # 4. tier 값 유효성
    tier = result.get("tier", "")
    if isinstance(tier, str) and tier and tier not in ("S", "A", "B", "C", "D", "F"):
        warnings.append(f"[값] tier='{tier}' (S/A/B/C/D/F 기대)")

    return warnings


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: coach_validator.py <coach_result.json> [build.json]")
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        result = json.load(f)
    build_data = None
    if len(sys.argv) >= 3:
        with open(sys.argv[2], encoding="utf-8") as f:
            build_data = json.load(f)
    warnings = validate_coach_output(result, build_data)
    if warnings:
        print(f"⚠️ {len(warnings)}개 경고:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✅ 검증 통과 (경고 없음)")
