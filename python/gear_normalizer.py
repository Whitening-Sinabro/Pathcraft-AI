# -*- coding: utf-8 -*-
"""AI Coach 출력 gear 정식화 (Normalizer) — Phase H3.

LLM 출력의 유니크/베이스 이름(약칭/오타/hallucination)을 canonical 로 교체한다.
슬롯명(`Helmet`/`Body Armour` 등)도 정식화한다.

데이터 소스 (ground truth):
  - data/unique_base_mapping.json: 642 POE1 유니크 이름
  - data/game_data/BaseItemTypes.json: 4196 고유 베이스 이름
  - data/gear_aliases.json: 약칭 alias + canonical 슬롯명

정규화 우선순위 (normalize_item):
  1. Alias (gear_aliases.json uniques/bases)
  2. Unique exact (case-insensitive)
  3. Base exact (case-insensitive)
  4. Fuzzy (유니크만, cutoff 0.88)
  5. 설명성 텍스트 감지 → 경고 생략 (rare/with/any/레어/매직 등)
  6. Unmatched → 원본 유지 + 경고

대상 필드 (coach_quality_backlog.md H3):
  - gear_progression[].phases[].item
  - gear_progression[].slot
  - key_items[].name / alternatives[] / slot

False positive 방지: 설명성 문구("Rare Helmet with life") 는 자연어라 경고 생략.
"""

from difflib import get_close_matches
import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("gear_normalizer")

UNIQUE_FUZZY_CUTOFF = 0.88  # 유니크는 642개 후보라 gem 보다 엄격
MIN_LEN_FOR_WARN = 3

# 설명성 텍스트 키워드 — 이 단어 포함 시 아이템 매칭 시도 후 실패해도 경고 생략
# (영문 자연어) "rare", "magic", "any", "with", "or", "generic"
# (한국어) 한국어 문자 포함 시 자동 설명으로 간주
DESCRIPTIVE_ASCII_KEYWORDS = frozenset([
    "rare", "magic", "any", "with", "or", "generic", "suitable",
    "appropriate", "placeholder", "tbd", "ilvl",
])


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def _load_unique_names() -> list[str]:
    path = _data_dir() / "unique_base_mapping.json"
    if not path.exists():
        logger.warning("unique_base_mapping.json 없음")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"unique_base_mapping.json 로드 실패: {e}")
        return []
    mapping = data.get("unique_to_base", {})
    return [k for k in mapping if isinstance(k, str) and k.strip()]


def _load_base_names() -> list[str]:
    path = _data_dir() / "game_data" / "BaseItemTypes.json"
    if not path.exists():
        logger.warning("BaseItemTypes.json 없음")
        return []
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"BaseItemTypes.json 로드 실패: {e}")
        return []
    names: set[str] = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        n = r.get("Name", "")
        if isinstance(n, str) and n.strip():
            names.add(n.strip())
    return sorted(names)


def _load_gear_aliases() -> dict:
    path = _data_dir() / "gear_aliases.json"
    if not path.exists():
        return {"uniques": {}, "bases": {}, "slots": {}, "canonical_slots": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"gear_aliases.json 로드 실패: {e}")
        return {"uniques": {}, "bases": {}, "slots": {}, "canonical_slots": []}


_UNIQUES: list[str] | None = None
_UNIQUE_LOWER: dict[str, str] | None = None
_BASES: list[str] | None = None
_BASE_LOWER: dict[str, str] | None = None
_ALIASES: dict | None = None
_UNIQUE_ALIAS_LOWER: dict[str, str] | None = None  # A2 — 사전 소문자 맵
_BASE_ALIAS_LOWER: dict[str, str] | None = None
_SLOT_LOWER: dict[str, str] | None = None
_CANONICAL_SLOTS: set[str] | None = None


def _ensure_loaded() -> None:
    global _UNIQUES, _UNIQUE_LOWER, _BASES, _BASE_LOWER
    global _ALIASES, _UNIQUE_ALIAS_LOWER, _BASE_ALIAS_LOWER
    global _SLOT_LOWER, _CANONICAL_SLOTS
    if _UNIQUES is not None:
        return
    _UNIQUES = _load_unique_names()
    _UNIQUE_LOWER = {u.strip().lower(): u for u in _UNIQUES}
    _BASES = _load_base_names()
    _BASE_LOWER = {b.strip().lower(): b for b in _BASES}

    # H5-1 drift check — valid_gems _meta 경유 BaseItemTypes SHA 비교
    try:
        from data_integrity import check_base_item_drift
        vg_path = _data_dir() / "valid_gems.json"
        if vg_path.exists():
            try:
                vg_data = json.loads(vg_path.read_text(encoding="utf-8"))
                check_base_item_drift(vg_data.get("_meta"), "gear_normalizer")
            except (json.JSONDecodeError, OSError):
                pass
    except ImportError:
        pass

    _ALIASES = _load_gear_aliases()
    # A2 — alias 소문자 맵 사전 계산 (호출 시 comprehension 재생성 방지)
    _UNIQUE_ALIAS_LOWER = {
        k.strip().lower(): v
        for k, v in _ALIASES.get("uniques", {}).items()
        if isinstance(k, str) and isinstance(v, str) and k.strip()
    }
    _BASE_ALIAS_LOWER = {
        k.strip().lower(): v
        for k, v in _ALIASES.get("bases", {}).items()
        if isinstance(k, str) and isinstance(v, str) and k.strip()
    }
    slots = _ALIASES.get("slots", {})
    _SLOT_LOWER = {
        k.strip().lower(): v
        for k, v in slots.items()
        if isinstance(k, str) and isinstance(v, str)
    }
    _CANONICAL_SLOTS = set(_ALIASES.get("canonical_slots", []))


def _reset_caches() -> None:
    """테스트 전용."""
    global _UNIQUES, _UNIQUE_LOWER, _BASES, _BASE_LOWER
    global _ALIASES, _UNIQUE_ALIAS_LOWER, _BASE_ALIAS_LOWER
    global _SLOT_LOWER, _CANONICAL_SLOTS
    _UNIQUES = _UNIQUE_LOWER = _BASES = _BASE_LOWER = None
    _ALIASES = _UNIQUE_ALIAS_LOWER = _BASE_ALIAS_LOWER = None
    _SLOT_LOWER = _CANONICAL_SLOTS = None


# ---------- item ----------


_PAREN_RE = re.compile(r"\s*\([^)]*\)\s*$")


def _strip_annotations(text: str) -> str:
    """끝의 괄호 주석 제거 ("Tabula Rasa (6L)" → "Tabula Rasa").

    중간 괄호는 보존(변종 이름 가능성). 끝의 (...) 만 1회 제거.
    """
    return _PAREN_RE.sub("", text).strip()


def _is_descriptive(text: str) -> bool:
    """자연어 설명 문구 여부."""
    if any(ord(c) > 127 for c in text):
        return True  # 한국어/이모지 = 설명 간주
    words = re.findall(r"[A-Za-z]+", text.lower())
    if any(w in DESCRIPTIVE_ASCII_KEYWORDS for w in words):
        return True
    # "Rare Helmet", "Any Boots" 같은 패턴: 길이 대비 단어 수 많음 (설명)
    return False


def normalize_item(name: str) -> tuple[str | None, str]:
    """유니크/베이스 이름 → (canonical, match_type).

    match_type:
      'alias_unique' / 'alias_base' / 'exact_unique' / 'exact_base' / 'fuzzy_unique' /
      'descriptive' (자연어 설명, 교정 안 함, 경고 생략 신호) /
      'unmatched' (매칭 실패, 원본 유지 + 경고)
    """
    if not isinstance(name, str) or not name.strip():
        return None, "unmatched"

    _ensure_loaded()
    raw = name.strip()
    stripped = _strip_annotations(raw)
    key = stripped.lower()

    # 1. alias (unique 우선) — A2 최적화: 사전 계산된 소문자 맵 사용
    for alias_lower, alias_type, canon_lookup in (
        (_UNIQUE_ALIAS_LOWER, "alias_unique", _UNIQUE_LOWER),
        (_BASE_ALIAS_LOWER, "alias_base", _BASE_LOWER),
    ):
        if not alias_lower or key not in alias_lower:
            continue
        canon = alias_lower[key]
        canon_key = canon.strip().lower()
        if canon_lookup and canon_key in canon_lookup:
            return canon_lookup[canon_key], alias_type
        logger.warning(
            "%s alias 대상 '%s'이 데이터에 없음 — 스킵: %s", alias_type, canon, raw
        )

    # 2. exact unique
    if _UNIQUE_LOWER and key in _UNIQUE_LOWER:
        return _UNIQUE_LOWER[key], "exact_unique"

    # 3. exact base
    if _BASE_LOWER and key in _BASE_LOWER:
        return _BASE_LOWER[key], "exact_base"

    # 4. descriptive → 매칭 안 하고 신호
    if _is_descriptive(stripped):
        return None, "descriptive"

    # 5. fuzzy (unique 만)
    if _UNIQUES:
        matches = get_close_matches(stripped, _UNIQUES, n=1, cutoff=UNIQUE_FUZZY_CUTOFF)
        if matches:
            return matches[0], "fuzzy_unique"

    return None, "unmatched"


# ---------- slot ----------


def normalize_slot(slot: str) -> tuple[str | None, str]:
    """슬롯명 정식화.

    match_type: 'exact' / 'alias' / 'descriptive' (한국어 등) / 'unmatched'
    """
    if not isinstance(slot, str) or not slot.strip():
        return None, "unmatched"

    _ensure_loaded()
    raw = slot.strip()
    key = raw.lower()

    if _CANONICAL_SLOTS and raw in _CANONICAL_SLOTS:
        return raw, "exact"
    if _SLOT_LOWER and key in _SLOT_LOWER:
        return _SLOT_LOWER[key], "alias"
    if any(ord(c) > 127 for c in raw):
        return None, "descriptive"
    return None, "unmatched"


# ---------- coach output ----------


def normalize_gear(result: dict) -> tuple[list[str], list[dict]]:
    """Coach JSON 인플레이스 gear 정규화. (경고, trace) 반환.

    대상:
      gear_progression[].slot
      gear_progression[].phases[].item
      key_items[].slot / name / alternatives[]
    """
    warnings: list[str] = []
    trace: list[dict] = []

    if not isinstance(result, dict):
        return warnings, trace

    gp = result.get("gear_progression")
    if isinstance(gp, list):
        for i, slot_group in enumerate(gp):
            if not isinstance(slot_group, dict):
                continue
            _norm_slot_inplace(slot_group, f"gear_progression[{i}].slot", warnings, trace)
            phases = slot_group.get("phases")
            if isinstance(phases, list):
                for j, ph in enumerate(phases):
                    if not isinstance(ph, dict):
                        continue
                    path = f"gear_progression[{i}].phases[{j}].item"
                    _norm_item_inplace(ph, "item", path, warnings, trace)

    key_items = result.get("key_items")
    if isinstance(key_items, list):
        for i, ki in enumerate(key_items):
            if not isinstance(ki, dict):
                continue
            _norm_slot_inplace(ki, f"key_items[{i}].slot", warnings, trace)
            _norm_item_inplace(ki, "name", f"key_items[{i}].name", warnings, trace)
            alts = ki.get("alternatives")
            if isinstance(alts, list):
                for k, alt in enumerate(alts):
                    if not isinstance(alt, str) or not alt.strip():
                        continue
                    path = f"key_items[{i}].alternatives[{k}]"
                    new_val, mt = normalize_item(alt)
                    _record_item_outcome(alts, k, alt, new_val, mt, path, warnings, trace)

    return warnings, trace


def _norm_item_inplace(
    block: dict, key: str, path: str,
    warnings: list[str], trace: list[dict],
) -> None:
    val = block.get(key)
    if not isinstance(val, str) or not val.strip():
        return
    canon, mt = normalize_item(val)
    _record_item_outcome(block, key, val, canon, mt, path, warnings, trace)


def _norm_slot_inplace(
    block: dict, path: str,
    warnings: list[str], trace: list[dict],
) -> None:
    val = block.get("slot")
    if not isinstance(val, str) or not val.strip():
        return
    canon, mt = normalize_slot(val)
    if canon is None:
        if mt == "descriptive":
            return  # 한국어/설명 — 교정/경고 생략
        warnings.append(f"[정규화] 슬롯 {path} '{val}' — 매칭 실패 (원본 유지)")
        return
    if canon == val:
        return  # 이미 canonical
    block["slot"] = canon
    trace.append({"field": path, "from": val, "to": canon, "match_type": f"slot_{mt}"})
    logger.info("slot 정규화: %s '%s' → '%s' (%s)", path, val, canon, mt)


def _record_item_outcome(
    container, key, original: str, canon: str | None, match_type: str,
    path: str, warnings: list[str], trace: list[dict],
) -> None:
    if canon is None:
        if match_type == "descriptive":
            return  # 자연어 설명 — 조용히 패스
        warnings.append(f"[정규화] 아이템 {path} '{original}' — 매칭 실패 (원본 유지)")
        return
    if canon == original.strip():
        return  # 이미 canonical (또는 공백만 차이)
    container[key] = canon
    trace.append({
        "field": path,
        "from": original,
        "to": canon,
        "match_type": match_type,
    })
    logger.info("item 정규화: %s '%s' → '%s' (%s)", path, original, canon, match_type)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logger.error("usage: gear_normalizer.py <coach_result.json>")
        sys.exit(2)
    logging.basicConfig(level=logging.INFO)
    with open(sys.argv[1], encoding="utf-8") as f:
        result = json.load(f)
    warnings, trace = normalize_gear(result)
    logger.info("gear 정규화 완료. 경고 %d / 교정 %d", len(warnings), len(trace))
    for w in warnings:
        logger.info("  - %s", w)
    for t in trace:
        logger.info("  ✎ %s: %r -> %r (%s)", t["field"], t["from"], t["to"], t["match_type"])
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
