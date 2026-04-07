# -*- coding: utf-8 -*-
"""
3.28.0 전체 패치노트 파싱 — 섹션별 구조화
사용자가 제공한 원본 텍스트를 섹션별로 분류하여 JSON 저장
"""

import json
import re
import sys
import logging
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("patch_parser")
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "patch_notes"

# 3.28.0 섹션 헤더 (Return to top으로 구분)
SECTION_HEADERS = [
    "The Mirage Challenge League",
    "New Content and Features",
    "Endgame Changes",
    "Atlas Passive Tree Changes",
    "Keepers of the Flame as a Core League",
    "Harbinger Removed as a Core League",
    "League Changes",
    "Player Changes",
    "Skill Gem Changes",
    "Vaal Gem Changes",
    "Support Gem Changes",
    "Ascendancy Changes",
    "Bloodline Changes",
    "Passive Skill Tree Changes",
    "Unique Item Changes",
    "Item Changes",
    "Ruthless-specific Changes",
    "Monster Changes",
    "Quest Reward Changes",
    "User Interface and Quality of Life Changes",
    "Microtransaction Updates",
    "Bug Fixes",
]


def parse_patch_text(text: str) -> dict:
    """전체 패치노트 텍스트를 섹션별로 분류"""

    # 포럼 네비게이션/댓글 제거
    cutoffs = [
        "Posted by Stacey_GGG",
        "Last edited by",
        "Posted by\nninepoe",
    ]
    for cutoff in cutoffs:
        idx = text.find(cutoff)
        if idx > 0:
            text = text[:idx]

    # "Return to top" 기준으로 섹션 분리
    sections = {}
    current_section = "preamble"
    current_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if stripped == "Return to top":
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_lines = []
            continue

        # 섹션 헤더 매칭
        matched = False
        for header in SECTION_HEADERS:
            if stripped == header:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = header
                current_lines = []
                matched = True
                break

        if not matched and stripped:
            current_lines.append(stripped)

    # 마지막 섹션
    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def extract_bullet_points(text: str) -> list[str]:
    """텍스트에서 변경사항 라인 추출"""
    points = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 설명문이 아닌 변경사항 라인
        if len(line) > 10:
            points.append(line)
    return points


def classify_skill_change(line: str) -> dict:
    """스킬 변경 라인을 buff/nerf/change로 분류"""
    lower = line.lower()

    change_type = "change"
    if any(w in lower for w in [
        "increased", "now deals", "more damage", "now has",
        "added a new", "now also", "now grants", "now fires",
        "now provides", "can now", "now have"
    ]):
        change_type = "buff"
    if any(w in lower for w in [
        "decreased", "reduced", "less damage", "no longer has",
        "no longer grants", "can no longer", "removed", "lowered",
        "has been removed", "now has a limit"
    ]):
        change_type = "nerf"

    return {"raw": line, "type": change_type}


def build_structured_data(sections: dict) -> dict:
    """섹션 데이터를 AI 코치용 구조화 데이터로 변환"""

    result = {
        "version": "3.28.0",
        "league": "Mirage",
        "sections": {},
        "coach_summary": {},
    }

    # 원본 섹션 저장
    for key, text in sections.items():
        if key == "preamble":
            continue
        result["sections"][key] = extract_bullet_points(text)

    # AI 코치용 요약 생성
    summary = result["coach_summary"]

    # 엔드게임 변경 (아틀라스, 맵, 보이드스톤)
    summary["endgame_changes"] = result["sections"].get("Endgame Changes", [])

    # 아틀라스 패시브
    summary["atlas_passive_changes"] = result["sections"].get("Atlas Passive Tree Changes", [])

    # 스킬 젬 변경 → buff/nerf 분류
    skill_lines = result["sections"].get("Skill Gem Changes", [])
    skill_changes = [classify_skill_change(line) for line in skill_lines]
    summary["skill_buffs"] = [c for c in skill_changes if c["type"] == "buff"]
    summary["skill_nerfs"] = [c for c in skill_changes if c["type"] == "nerf"]
    summary["skill_other"] = [c for c in skill_changes if c["type"] == "change"]

    # 보조 젬 변경
    summary["support_gem_changes"] = result["sections"].get("Support Gem Changes", [])

    # 전직 변경
    summary["ascendancy_changes"] = result["sections"].get("Ascendancy Changes", [])

    # 고유 아이템 변경
    summary["unique_item_changes"] = result["sections"].get("Unique Item Changes", [])

    # 아이템/화폐 변경
    summary["item_currency_changes"] = result["sections"].get("Item Changes", [])

    # 리그 메카닉 변경
    summary["league_mechanic_changes"] = result["sections"].get("League Changes", [])

    # 신규 콘텐츠
    summary["new_content"] = result["sections"].get("New Content and Features", [])

    # 플레이어 변경
    summary["player_changes"] = result["sections"].get("Player Changes", [])

    # 퀘스트 보상
    summary["quest_reward_changes"] = result["sections"].get("Quest Reward Changes", [])

    # 혈맹 변경
    summary["bloodline_changes"] = result["sections"].get("Bloodline Changes", [])

    # 패시브 트리 변경
    summary["passive_tree_changes"] = result["sections"].get("Passive Skill Tree Changes", [])

    # 미라지 리그 메카닉
    summary["mirage_mechanic"] = result["sections"].get("The Mirage Challenge League", [])

    # Breach 코어화
    summary["breach_core_changes"] = result["sections"].get("Keepers of the Flame as a Core League", [])

    # Harbinger 제거
    summary["harbinger_removal"] = result["sections"].get("Harbinger Removed as a Core League", [])

    # 핵심 수치 요약
    summary["key_numbers"] = {
        "total_skill_buffs": len(summary["skill_buffs"]),
        "total_skill_nerfs": len(summary["skill_nerfs"]),
        "total_endgame_changes": len(summary["endgame_changes"]),
        "total_atlas_passive_changes": len(summary["atlas_passive_changes"]),
        "total_unique_changes": len(summary["unique_item_changes"]),
    }

    return result


def main():
    input_file = DATA_DIR / "raw_3_28_0_full.txt"

    if not input_file.exists():
        logger.error(f"입력 파일 없음: {input_file}")
        logger.info("data/patch_notes/raw_3_28_0_full.txt에 전체 패치노트 텍스트를 저장하세요.")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    logger.info(f"원본 텍스트 길이: {len(text)} 자")

    # 섹션 파싱
    sections = parse_patch_text(text)
    logger.info(f"섹션 {len(sections)}개 파싱 완료")
    for key, val in sections.items():
        logger.info(f"  {key}: {len(val)} 자")

    # 구조화
    structured = build_structured_data(sections)

    # 전체 데이터 저장
    output_file = DATA_DIR / "patch_3_28_0_full.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    logger.info(f"전체 데이터 저장: {output_file}")

    # 코치 요약만 별도 저장 (기존 summary_3_28_0.json 대체)
    summary_file = DATA_DIR / "summary_3_28_0.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(structured["coach_summary"], f, ensure_ascii=False, indent=2)
    logger.info(f"코치 요약 저장: {summary_file}")

    # 수치 출력
    nums = structured["coach_summary"]["key_numbers"]
    logger.info(f"\n=== 3.28.0 패치노트 요약 ===")
    logger.info(f"스킬 버프: {nums['total_skill_buffs']}건")
    logger.info(f"스킬 너프: {nums['total_skill_nerfs']}건")
    logger.info(f"엔드게임 변경: {nums['total_endgame_changes']}건")
    logger.info(f"아틀라스 패시브 변경: {nums['total_atlas_passive_changes']}건")
    logger.info(f"고유 아이템 변경: {nums['total_unique_changes']}건")


if __name__ == "__main__":
    main()
