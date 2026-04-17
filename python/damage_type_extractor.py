# -*- coding: utf-8 -*-
"""빌드 damage axis 분류 (Phase E3).

gem_setups의 active skill gems → data/gem_damage_types.json lookup →
frozenset[str] ⊆ {"attack", "caster", "dot", "minion"}.

설계:
- pob_parser가 skill tag 파싱 안 함 → gem name lookup만 가능.
- 소스: POB Lua `skillTypes` 실측 기반 (E2 생성).
- 메인 스킬 판별 없이 **모든 active skill gem axis union**.
  - 근거: Phase B weapon_class_extractor도 전체 gem union. 동일 철학.
  - 부작용: Cyclone + Vitality(aura, Spell flag) 빌드 → attack + caster 활성.
    버프 용도 아우라는 axis 오염 가능. 현재 허용 (over-broad는 드롭 강조 추가만 유발).
- 파일 누락 시 graceful degradation: logger.warning + 빈 frozenset.

소비처:
- `build_extractor.StageData.damage_types` (E5)
- `sections_continue.layer_build_target` 내 accessory_proxy 블록 (E6)

반환: frozenset[str]. 메인 스킬 없거나 파일 없으면 빈 frozenset.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DAMAGE_AXES: tuple[str, ...] = ("attack", "caster", "dot", "minion")

_GEM_DAMAGE_TYPES_CACHE: Optional[dict] = None


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data"


def load_gem_damage_types(filepath: Optional[Path] = None) -> dict[str, dict[str, bool]]:
    """data/gem_damage_types.json 로드 → {gem_name: {axis: bool}}.

    파일 없거나 스키마 손상 시 빈 dict. 소비처는 빈 dict → 빈 damage_types 유도.
    """
    global _GEM_DAMAGE_TYPES_CACHE
    if _GEM_DAMAGE_TYPES_CACHE is not None and filepath is None:
        return _GEM_DAMAGE_TYPES_CACHE
    path = filepath if filepath is not None else _data_dir() / "gem_damage_types.json"
    if not path.exists():
        logger.warning("gem_damage_types.json not found at %s — damage_types 빈 집합", path)
        result: dict[str, dict[str, bool]] = {}
    else:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            result = raw.get("gems", {}) or {}
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("gem_damage_types.json 로드 실패: %s — damage_types 빈 집합", e)
            result = {}
    if filepath is None:
        _GEM_DAMAGE_TYPES_CACHE = result
    return result


def _iter_build_skill_gems(build_data: dict) -> list[str]:
    """build_data.progression_stages[*].gem_setups 에서 gem 이름 리스트 추출.

    pob_parser gem_setups 스키마: `{label: {"links": "gem1 - gem2 - ...", "reasoning": None}}`
    links 문자열을 " - "로 split. label(= 첫 gem, 메인 스킬 이름)도 포함.
    """
    stages = build_data.get("progression_stages") or []
    if not isinstance(stages, list):
        return []
    names: list[str] = []
    for stage in stages:
        if not isinstance(stage, dict):
            continue
        gem_setups = stage.get("gem_setups") or {}
        if not isinstance(gem_setups, dict):
            continue
        for label, entry in gem_setups.items():
            # label은 보통 메인 스킬 이름
            if isinstance(label, str) and label.strip():
                names.append(label.strip())
            # links 안의 모든 젬도 union
            if isinstance(entry, dict):
                links = entry.get("links")
                if isinstance(links, str):
                    for g in links.split(" - "):
                        g = g.strip()
                        if g:
                            names.append(g)
    return names


def classify_damage_axes_from_gems(
    gem_names: list[str],
    gem_damage_types: dict[str, dict[str, bool]],
) -> frozenset[str]:
    """Gem 이름 리스트 → damage axis frozenset.

    Support gem 필터링 없음 — gem_damage_types.json 생성 시 이미 support는
    대부분 damage axis flag 없어서 누락됨 (auras/buffs only). 결과적으로 조용히 걸러짐.

    Args:
        gem_names: build의 모든 스킬 젬 (active + supports 혼재 가능)
        gem_damage_types: load_gem_damage_types() 결과

    Returns:
        {"attack", "caster", "dot", "minion"}의 서브셋. lookup miss 시 빈 frozenset.
    """
    if not gem_names or not gem_damage_types:
        return frozenset()
    result: set[str] = set()
    for gem in gem_names:
        axes = gem_damage_types.get(gem)
        if not axes:
            continue
        for axis in DAMAGE_AXES:
            if axes.get(axis):
                result.add(axis)
    return frozenset(result)


def extract_build_damage_types(
    build_data: Optional[dict],
    gem_damage_types: Optional[dict[str, dict[str, bool]]] = None,
) -> frozenset[str]:
    """build_data → damage axis frozenset.

    Args:
        build_data: pob_parser 출력
        gem_damage_types: 주입식 (테스트용). None이면 JSON 로드.

    Returns:
        frozenset[str] ⊆ {"attack", "caster", "dot", "minion"}. 비면 accessory_proxy
        common 블록만 emit.
    """
    if not build_data:
        return frozenset()
    if gem_damage_types is None:
        gem_damage_types = load_gem_damage_types()
    gem_names = _iter_build_skill_gems(build_data)
    return classify_damage_axes_from_gems(gem_names, gem_damage_types)
