# -*- coding: utf-8 -*-
"""캐릭터 방어 축 분류 (Phase D).

pob_parser가 반환하는 캐릭터 최종 방어 수치(armour/evasion/energy_shield)를
기반으로 빌드가 실제 의존하는 defence axis 집합을 결정한다.

설계:
- per-slot이 아닌 character-level aggregate 사용.
  이유: CI Witch가 Carnal Armour(AR/EV base) 착용해도 실효 armour=0이면
  AR mod 강조는 노이즈. base_type 기반 분류는 잘못된 시그널.
- ratio-based: 최대값 axis = 주속성. 주속성의 hybrid_threshold 이상 = 부속성 포함.
- 반환: frozenset[{"ar", "ev", "es"}]

소비처:
- `build_extractor.StageData.defence_types` (D3)
- `sections_continue.layer_build_target` 내 defense_proxy 블록 (D4)

Note: POE 원어는 "defence"(UK). 내부 변수 일관성을 위해 `defence_*`를 사용하되,
파일명/산출물은 영어 표준 `defense_*` (UX naming)를 사용한다.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFENCE_AXES: tuple[str, ...] = ("ar", "ev", "es")
DEFAULT_HYBRID_THRESHOLD = 0.3


def classify_defence_from_stats(
    armour: int,
    evasion: int,
    energy_shield: int,
    hybrid_threshold: float = DEFAULT_HYBRID_THRESHOLD,
) -> frozenset[str]:
    """캐릭터 방어 수치 → defence axis 집합.

    Args:
        armour: 최종 armour 수치 (pob_parser.stats.armour)
        evasion: 최종 evasion 수치
        energy_shield: 최종 ES 수치
        hybrid_threshold: 주속성 대비 부속성 비율 (기본 0.3 = 30%)

    Returns:
        {"ar", "ev", "es"}의 서브셋. 모든 수치 0이면 빈 frozenset.

    Rules:
        - 모든 수치 ≤ 0 → 빈 집합 (빌드 미완성 / stats 누락)
        - 주속성 = 최대값의 axis
        - 부속성 포함 조건: 값 >= 주속성 * hybrid_threshold AND 값 > 0
    """
    stats: dict[str, int] = {"ar": armour, "ev": evasion, "es": energy_shield}
    max_val = max(stats.values())
    if max_val <= 0:
        return frozenset()

    threshold = max_val * hybrid_threshold
    return frozenset(
        axis for axis, val in stats.items()
        if val > 0 and val >= threshold
    )


def extract_build_defence_types(
    build_data: Optional[dict],
    hybrid_threshold: float = DEFAULT_HYBRID_THRESHOLD,
) -> frozenset[str]:
    """build_data (pob_parser 출력)에서 defence axis 집합 추출.

    Args:
        build_data: pob_parser가 반환한 dict (top-level "stats" 키 기대)
        hybrid_threshold: 하이브리드 판정 임계값

    Returns:
        frozenset[str] - empty set if stats missing or all zero.
    """
    if not build_data:
        return frozenset()

    stats = build_data.get("stats")
    if not isinstance(stats, dict):
        logger.debug("build_data.stats 없음 또는 비-dict — defence_types 빈 집합")
        return frozenset()

    armour = int(stats.get("armour", 0) or 0)
    evasion = int(stats.get("evasion", 0) or 0)
    energy_shield = int(stats.get("energy_shield", 0) or 0)

    return classify_defence_from_stats(
        armour=armour,
        evasion=evasion,
        energy_shield=energy_shield,
        hybrid_threshold=hybrid_threshold,
    )
