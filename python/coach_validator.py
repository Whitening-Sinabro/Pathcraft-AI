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


def _load_valid_gems(game: str = "poe1") -> set[str]:
    """유효 젬 이름 set (대소문자 무시 키). hallucination 탐지용.

    POE1: data/valid_gems.json {"gems": [...]}
    POE2: data/valid_gems_poe2.json {"active"/"support"/"spirit": [{name, ...}]}
    """
    if game == "poe2":
        path = Path(__file__).resolve().parent.parent / "data" / "valid_gems_poe2.json"
        if not path.exists():
            return set()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"valid_gems_poe2.json 로드 실패: {e}")
            return set()
        names: set[str] = set()
        for bucket in ("active", "support", "spirit"):
            for entry in data.get(bucket, []) or []:
                if isinstance(entry, dict):
                    n = entry.get("name")
                    if isinstance(n, str) and n.strip():
                        names.add(n.strip().lower())
        return names

    # POE1 기본 경로
    path = Path(__file__).resolve().parent.parent / "data" / "valid_gems.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"valid_gems.json 로드 실패: {e}")
        return set()
    gems = data.get("gems", [])
    if not isinstance(gems, list):
        return set()
    return {g.strip().lower() for g in gems if isinstance(g, str) and g.strip()}


_VALID_GEMS_BY_GAME: dict[str, set[str]] = {}


def _get_valid_gems(game: str = "poe1") -> set[str]:
    if game not in _VALID_GEMS_BY_GAME:
        _VALID_GEMS_BY_GAME[game] = _load_valid_gems(game)
    return _VALID_GEMS_BY_GAME[game]


def _extract_gem_strings(obj: Any, out: list[str]) -> None:
    """결과 JSON 재귀 순회 — 'gems' 배열 + main_skill/change 문자열에서 젬 이름 추출.
    경계: str/list/dict만 탐색. 숫자/None 스킵."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            # 'gems' 배열은 젬 이름 리스트
            if key == "gems" and isinstance(val, list):
                for g in val:
                    if isinstance(g, str) and g.strip():
                        out.append(g.strip())
            # main_skill/change는 "A - B - C" 형태
            elif key in ("main_skill", "change") and isinstance(val, str):
                # " - " 또는 "," 로 쪼갬
                for part in val.replace(",", " - ").split(" - "):
                    part = part.strip()
                    if part and len(part) < 60:  # 젬 이름 길이 합리 제한
                        out.append(part)
            else:
                _extract_gem_strings(val, out)
    elif isinstance(obj, list):
        for item in obj:
            _extract_gem_strings(item, out)


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


def validate_coach_output(
    result: dict,
    build_data: dict | None = None,
    game: str = "poe1",
) -> list[str]:
    """Coach 결과 JSON 검증. 경고 메시지 리스트 반환 (빈 리스트 = OK).

    game="poe1": 기존 검증 (스키마 + 범위 + quest_rewards cross-check + POE1 valid_gems 젬 대조)
    game="poe2": 스키마 + 범위 + POE2 valid_gems 젬 대조. quest_rewards 는 POE2 구조 미확정으로 skip.
    """
    warnings: list[str] = []

    # 1. 스키마 — 필수 필드 + 타입 (POE2 는 일부 필드 다름, 경고 레벨로만)
    if game == "poe1":
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in result:
                warnings.append(f"[스키마] 필수 필드 누락: {field}")
            elif not isinstance(result[field], expected_type):
                warnings.append(
                    f"[스키마] {field} 타입 불일치: "
                    f"기대 {expected_type.__name__}, 실제 {type(result[field]).__name__}"
                )

    # 2. build_rating 값 범위 (1~5) — 양 게임 공통 (POE2 JSON 스키마도 rating 유지)
    rating = result.get("build_rating", {})
    if isinstance(rating, dict):
        for key, val in rating.items():
            if isinstance(val, (int, float)) and not (1 <= val <= 5):
                warnings.append(f"[범위] build_rating.{key}={val} (1~5 기대)")

    # 3. skill_transitions 레벨 범위 + quest_rewards cross-check (POE1 전용, POE2 는 퀘스트 구조 다름)
    lvl_skills = result.get("leveling_skills", {})
    transitions = lvl_skills.get("skill_transitions", [])
    if isinstance(transitions, list) and game == "poe1":
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

    # 5. 젬 이름 hallucination 검증 — 게임별 valid_gems 대조
    valid_gems = _get_valid_gems(game)
    if valid_gems:
        gem_candidates: list[str] = []
        _extract_gem_strings(result, gem_candidates)
        # 중복 제거 + 정규화된 비교 (대소문자 무시, 선후 공백 제거)
        seen_invalid: set[str] = set()
        # False positive 억제용 stopword — gem이 아닌 설명 토큰
        STOPWORDS = {
            "and", "or", "with", "to", "vs", "into", "via", "at", "on",
            "4-link", "5-link", "6-link", "4l", "5l", "6l",
            "메인스킬", "서포트1", "서포트2", "서포트3", "서포트4", "서포트5",
            "final", "main", "support", "skill", "gem", "final combo", "최종 조합",
        }
        for cand in gem_candidates:
            norm = cand.strip().lower()
            if not norm or norm in STOPWORDS or norm in seen_invalid:
                continue
            # 숫자만 / 2글자 이하는 젬 이름 아닐 가능성 높음
            if len(norm) < 3 or norm.replace("-", "").replace(" ", "").isdigit():
                continue
            # valid 젬이면 통과
            if norm in valid_gems:
                continue
            # 일반화된 표현 허용 (예: "메인스킬") — 한글/이모지 포함이면 설명 텍스트로 간주
            if any(ord(c) > 127 for c in norm):
                continue
            # 괄호 포함 주석 (예: "Firestorm (4L)") — 괄호 앞 부분만 재검사
            paren = norm.split("(")[0].strip()
            if paren and paren != norm and paren in valid_gems:
                continue
            seen_invalid.add(norm)
            game_label = "POE2" if game == "poe2" else "POE1"
            warnings.append(f"[젬] '{cand}' — {game_label} valid_gems 에 없음 (hallucination 의심)")

    return warnings


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Coach output validator")
    ap.add_argument("coach_result", help="coach JSON output 파일")
    ap.add_argument("build", nargs="?", help="(선택) 빌드 JSON (quest cross-check 용)")
    ap.add_argument("--game", choices=["poe1", "poe2"], default="poe1")
    args = ap.parse_args()

    with open(args.coach_result, encoding="utf-8") as f:
        result = json.load(f)
    build_data = None
    if args.build:
        with open(args.build, encoding="utf-8") as f:
            build_data = json.load(f)
    warnings = validate_coach_output(result, build_data, game=args.game)
    if warnings:
        print(f"⚠️ {len(warnings)}개 경고:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✅ 검증 통과 (경고 없음)")
