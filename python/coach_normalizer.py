# -*- coding: utf-8 -*-
"""AI Coach 출력 정식화 (Normalizer) — Phase H2.

LLM 출력의 젬 이름(약칭/변형/대소문자/오타)을 valid_gems.json canonical 이름으로 교체한다.

단계 (우선순위):
1. Alias — data/gem_aliases.json 명시적 매핑 (큐레이팅된 의도 반영)
2. Exact (case-insensitive) — 대소문자만 표준화
3. Fuzzy (difflib, cutoff 0.85) — 오타/유사어 자동 교정
4. Unmatched — 원본 유지 + 경고

Alias 우선 이유: valid_gems.json 은 BaseItemTypes 전체(953)를 담고 있어 "Ruthless"
같은 단축 명이 존재(BaseItem 내부 row)한다. 하지만 LLM 코치 출력 문맥에서 "ruthless"
는 거의 항상 Support 의미다. 명시 alias 가 있으면 그 의도를 따른다.

False positive 방지: cutoff 임계 미달은 교정하지 않음. alias 맵은 valid_gems 검증 완료.

대상 필드 (coach_quality_backlog.md H2):
- leveling_skills.recommended.name / links_progression[].gems
- leveling_skills.options[].name / links_progression[].gems
- leveling_skills.skill_transitions[].change (구분자 보존)

build_coach.py 에서 validator 직전 삽입. 정규화 후 검증이라 hallucination 경고 대폭 감소.
"""

from difflib import get_close_matches
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("coach_normalizer")

FUZZY_CUTOFF = 0.85


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def _load_valid_gems() -> list[str]:
    path = _data_dir() / "valid_gems.json"
    if not path.exists():
        logger.warning("valid_gems.json 없음 — normalizer 비활성")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"valid_gems.json 로드 실패: {e}")
        return []
    # H5-1 drift check — BaseItemTypes 변경 시 refresh 안내
    try:
        from data_integrity import check_base_item_drift
        check_base_item_drift(data.get("_meta"), "coach_normalizer")
    except ImportError:
        pass
    gems = data.get("gems", [])
    return [g for g in gems if isinstance(g, str) and g.strip()]


def _load_aliases() -> dict[str, str]:
    path = _data_dir() / "gem_aliases.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"gem_aliases.json 로드 실패: {e}")
        return {}
    aliases = data.get("aliases", {})
    return {
        k.strip().lower(): v
        for k, v in aliases.items()
        if isinstance(k, str) and isinstance(v, str) and k.strip()
    }


_VALID_GEMS: list[str] | None = None
_LOWER_TO_CANON: dict[str, str] | None = None
_ALIASES: dict[str, str] | None = None


def _ensure_loaded() -> tuple[list[str], dict[str, str], dict[str, str]]:
    global _VALID_GEMS, _LOWER_TO_CANON, _ALIASES
    if _VALID_GEMS is None:
        _VALID_GEMS = _load_valid_gems()
        _LOWER_TO_CANON = {g.strip().lower(): g for g in _VALID_GEMS}
        _ALIASES = _load_aliases()
    return _VALID_GEMS, _LOWER_TO_CANON, _ALIASES  # type: ignore[return-value]


def _reset_caches() -> None:
    """테스트 전용 — 데이터 파일 교체 후 재로드 강제."""
    global _VALID_GEMS, _LOWER_TO_CANON, _ALIASES
    _VALID_GEMS = None
    _LOWER_TO_CANON = None
    _ALIASES = None


def normalize_gem(name: str) -> tuple[str | None, str]:
    """젬 이름 → (canonical, match_type).

    match_type:
      'alias'     — gem_aliases.json 명시 매핑 (최우선: 큐레이팅된 의도)
      'exact'     — 대소문자 무시 완전 일치 (canonical 대소문자로 표준화)
      'fuzzy'     — difflib 근사 매칭 (cutoff 0.85)
      'unmatched' — 매칭 실패 (canonical=None)
    """
    if not isinstance(name, str) or not name.strip():
        return None, "unmatched"

    valid_gems, lower_map, aliases = _ensure_loaded()
    if not valid_gems:
        return None, "unmatched"

    raw = name.strip()
    key = raw.lower()

    # 1. alias — valid_gems 와 공통 키가 있어도 alias 우선
    # 이유: LLM 출력에서 "ruthless" 는 Support 의미, BaseItem row "Ruthless" 가 아님
    if key in aliases:
        canon = aliases[key]
        canon_key = canon.strip().lower()
        if canon_key in lower_map:
            return lower_map[canon_key], "alias"
        logger.warning(
            "alias 대상 '%s'이 valid_gems에 없음 — 스킵: %s -> %s", canon, raw, canon
        )

    # 2. exact (case-insensitive)
    if key in lower_map:
        return lower_map[key], "exact"

    # 3. fuzzy
    matches = get_close_matches(raw, valid_gems, n=1, cutoff=FUZZY_CUTOFF)
    if matches:
        return matches[0], "fuzzy"

    return None, "unmatched"


def normalize_gem_list(
    gems: list,
    trace: list[dict] | None = None,
    path: str = "",
) -> tuple[list, list[str]]:
    """젬 배열 정규화. (교체된 리스트, 경고 리스트) 반환. 비-str 요소는 그대로 통과.

    L2 Strict allowlist (Phase H6): valid_gems/alias/fuzzy 어느 것에도 매칭되지
    않으면 **배열에서 제거** (pass-through 금지). hallucination 젬이 UI까지
    관통하던 pass-through 허점 차단. change 필드는 자연어라 적용 제외.

    trace 가 주어지면 교정/드롭 이력을 {field, from, to, match_type} 로 기록.
    드롭은 match_type='dropped', to=None.
    """
    warnings: list[str] = []
    out: list = []
    for i, g in enumerate(gems):
        if not isinstance(g, str):
            out.append(g)
            continue
        canon, match_type = normalize_gem(g)
        if canon is None:
            # L2: pass-through 제거, 배열에서 drop
            warnings.append(f"[차단] 젬 '{g}' — valid_gems 미존재로 배열에서 제거")
            logger.warning("젬 drop: '%s' (unmatched, allowlist 밖)", g)
            if trace is not None:
                trace.append({
                    "field": f"{path}[{i}]" if path else f"[{i}]",
                    "from": g,
                    "to": None,
                    "match_type": "dropped",
                })
            continue
        out.append(canon)
        changed = match_type != "exact" or canon != g.strip()
        if changed:
            logger.info("젬 정규화: '%s' → '%s' (%s)", g, canon, match_type)
            if trace is not None:
                trace.append({
                    "field": f"{path}[{i}]" if path else f"[{i}]",
                    "from": g,
                    "to": canon,
                    "match_type": match_type,
                })
    return out, warnings


def normalize_change_field(
    change: str,
    trace: list[dict] | None = None,
    path: str = "",
) -> tuple[str, list[str]]:
    """skill_transitions[].change 필드. 구분자 보존하며 각 토큰 정규화.

    우선순위: ' - ' > ', '. 둘 다 없으면 단일 토큰.
    trace 가 주어지면 실제 교정된 토큰을 {field, from, to, match_type} 로 기록.
    """
    if not isinstance(change, str) or not change.strip():
        return change, []

    warnings: list[str] = []
    if " - " in change:
        parts = [p.strip() for p in change.split(" - ")]
        sep = " - "
    elif "," in change:
        parts = [p.strip() for p in change.split(",")]
        sep = ", "
    else:
        parts = [change.strip()]
        sep = ""

    normalized_parts: list[str] = []
    for i, part in enumerate(parts):
        if not part:
            normalized_parts.append(part)
            continue
        canon, match_type = normalize_gem(part)
        if canon is None:
            normalized_parts.append(part)
            # change 문구는 설명 텍스트 혼합 가능 (예: "Cleave로 전환") — 경고 약화
            # 한국어/이모지(non-ASCII) 포함이면 설명 텍스트로 간주, 경고 생략
            # (validator.py:216 동일 패턴)
            if len(part) >= 3 and all(ord(c) < 128 for c in part):
                warnings.append(f"[정규화] change '{part}' — 젬 매칭 실패 (원본 유지)")
            continue
        normalized_parts.append(canon)
        changed = match_type != "exact" or canon != part
        if changed:
            logger.info("change 정규화: '%s' → '%s' (%s)", part, canon, match_type)
            if trace is not None:
                trace.append({
                    "field": f"{path}#{i}" if path else f"[{i}]",
                    "from": part,
                    "to": canon,
                    "match_type": match_type,
                })

    new_change = sep.join(normalized_parts) if sep else (normalized_parts[0] if normalized_parts else change)
    return new_change, warnings


def normalize_coach_output(result: dict) -> tuple[list[str], list[dict]]:
    """Coach JSON 인플레이스 정규화. (경고 리스트, trace 리스트) 반환.

    trace: 자동 교정된 필드 이력. {field, from, to, match_type} 각 항목.
           UI/디버깅에서 "무엇이 어떻게 바뀌었는지" 보이기 위함.
    대상:
      leveling_skills.recommended.name / links_progression[].gems
      leveling_skills.options[].name / links_progression[].gems
      leveling_skills.skill_transitions[].change
    """
    all_warnings: list[str] = []
    trace: list[dict] = []

    if not isinstance(result, dict):
        return all_warnings, trace

    lvl_skills = result.get("leveling_skills")
    if not isinstance(lvl_skills, dict):
        return all_warnings, trace

    all_warnings.extend(_normalize_skill_block(
        lvl_skills.get("recommended"), "leveling_skills.recommended", trace
    ))

    options = lvl_skills.get("options")
    if isinstance(options, list):
        for i, opt in enumerate(options):
            all_warnings.extend(_normalize_skill_block(
                opt, f"leveling_skills.options[{i}]", trace
            ))

    transitions = lvl_skills.get("skill_transitions")
    if isinstance(transitions, list):
        for i, t in enumerate(transitions):
            if not isinstance(t, dict):
                continue
            change = t.get("change")
            if isinstance(change, str):
                path = f"leveling_skills.skill_transitions[{i}].change"
                new_change, ws = normalize_change_field(change, trace=trace, path=path)
                t["change"] = new_change
                for w in ws:
                    all_warnings.append(w.replace(
                        "change '", f"skill_transitions[{i}].change '"
                    ))

    return all_warnings, trace


def _normalize_skill_block(block: Any, label: str, trace: list[dict]) -> list[str]:
    """recommended / options[i] 공용 — name + links_progression.gems 정규화.

    trace 에 교정 이력 누적.
    """
    warnings: list[str] = []
    if not isinstance(block, dict):
        return warnings

    name = block.get("name")
    if isinstance(name, str) and name.strip():
        canon, match_type = normalize_gem(name)
        if canon is None:
            warnings.append(f"[정규화] {label}.name '{name}' — 매칭 실패 (원본 유지)")
        else:
            block["name"] = canon
            changed = match_type != "exact" or canon != name.strip()
            if changed:
                logger.info("%s.name 정규화: '%s' → '%s' (%s)", label, name, canon, match_type)
                trace.append({
                    "field": f"{label}.name",
                    "from": name,
                    "to": canon,
                    "match_type": match_type,
                })

    lp = block.get("links_progression")
    if isinstance(lp, list):
        for j, prog in enumerate(lp):
            if not isinstance(prog, dict):
                continue
            gems = prog.get("gems")
            if isinstance(gems, list):
                new_gems, ws = normalize_gem_list(
                    gems, trace=trace, path=f"{label}.links_progression[{j}].gems"
                )
                prog["gems"] = new_gems
                for w in ws:
                    warnings.append(w.replace(
                        "젬 '", f"{label}.links_progression[{j}] 젬 '"
                    ))

    return warnings


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logger.error("usage: coach_normalizer.py <coach_result.json>")
        sys.exit(2)
    logging.basicConfig(level=logging.INFO)
    with open(sys.argv[1], encoding="utf-8") as f:
        result = json.load(f)
    warnings, trace = normalize_coach_output(result)
    logger.info("정규화 완료. 경고 %d건 / 교정 %d건", len(warnings), len(trace))
    for w in warnings:
        logger.info("  - %s", w)
    for t in trace:
        logger.info("  ✎ %s: %r -> %r (%s)", t["field"], t["from"], t["to"], t["match_type"])
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
