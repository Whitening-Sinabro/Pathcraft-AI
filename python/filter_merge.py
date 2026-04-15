# -*- coding: utf-8 -*-
"""POE 필터 병합 유틸 (레거시).

Sanavi/NeverSink 베이스 필터의 `# [[0100]]` OVERRIDE 마커 앞에 오버레이를 삽입한다.
현재 β Continue 아키텍처는 standalone 필터라 쓰이지 않음 — _analysis 스크립트 잔존 의존용.
"""
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

POE_FILTER_DIR = Path.home() / "Documents" / "My Games" / "Path of Exile"
OVERRIDE_MARKER = "# [[0100]]"

STRICTNESS_NAMES = {
    0: "0_Soft",
    1: "1_Regular",
    2: "2_Semi-Strict",
    3: "3_Strict",
    4: "4_Very Strict",
    5: "5_Uber Strict",
    6: "6_Uber Plus Strict",
}


class FilterMergeError(RuntimeError):
    """필터 병합 중 발생한 에러."""


def find_sanavi_filter(strictness: int = 3) -> Optional[Path]:
    """Sanavi 필터 자동 탐지.

    환경변수 `SANAVI_PATH`가 설정돼 있으면 이를 우선 사용한다.
    strictness 인자로 특정 엄격도 선택.
    """
    env_path = os.environ.get("SANAVI_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    name = STRICTNESS_NAMES.get(strictness, STRICTNESS_NAMES[3])
    path = POE_FILTER_DIR / f"Sanavi_{name}.filter"
    if path.exists():
        return path

    # fallback: 설치된 아무 Sanavi 필터
    for p in sorted(POE_FILTER_DIR.glob("Sanavi_*.filter")):
        return p
    return None


def merge_overlay_into_base(
    base_content: str,
    overlay_content: str,
    marker: str = OVERRIDE_MARKER,
    strict_marker: bool = True,
) -> str:
    """베이스 필터 텍스트에 오버레이를 삽입.

    Args:
        base_content: Sanavi/NeverSink 베이스 필터 전체 텍스트
        overlay_content: 삽입할 PathcraftAI 오버레이 블록 텍스트
        marker: 삽입 위치 마커 (기본 `# [[0100]]`)
        strict_marker: True면 마커 없을 때 FilterMergeError raise, False면 맨 앞에 삽입

    Returns:
        병합된 필터 텍스트
    """
    insert_pos = base_content.find(marker)
    if insert_pos < 0:
        if strict_marker:
            raise FilterMergeError(
                f"베이스 필터에서 '{marker}' 마커를 찾을 수 없습니다"
            )
        logger.warning("마커 '%s' 없음, 맨 앞에 삽입", marker)
        return overlay_content + "\n" + base_content

    return base_content[:insert_pos] + overlay_content + "\n" + base_content[insert_pos:]


def apply_overlay_to_file(
    base_path: Path,
    overlay_content: str,
    output_path: Path,
    marker: str = OVERRIDE_MARKER,
) -> int:
    """베이스 필터 파일을 읽고 오버레이 삽입 후 저장.

    Returns:
        최종 병합 파일의 라인 수
    """
    if not base_path.exists():
        raise FileNotFoundError(f"베이스 필터 없음: {base_path}")

    with open(base_path, "r", encoding="utf-8") as f:
        base_content = f.read()

    merged = merge_overlay_into_base(base_content, overlay_content, marker=marker)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(merged)

    line_count = merged.count("\n")
    logger.info("필터 병합: %s (%d줄)", output_path, line_count)
    return line_count
