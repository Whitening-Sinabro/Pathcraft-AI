# -*- coding: utf-8 -*-
"""
빌드 기반 아이템 필터 생성기

Sanavi(NeverSink) 베이스 필터 위에 빌드 오버레이를 생성.
POB 빌드 데이터에서 필요한 젬/베이스/커런시를 추출하고 하이라이트.

사용법:
    python filter_generator.py build.json --base "Sanavi_3_Strict.filter" --out "MyBuild.filter"
    python filter_generator.py build.json  # 오버레이만 출력
"""

import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger("filter_gen")

# POE 필터 디렉토리
POE_FILTER_DIR = Path.home() / "Documents" / "My Games" / "Path of Exile"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class FilterStyle:
    """필터 스타일 프리셋."""

    # 빌드 핵심 아이템 (빨강 강조)
    BUILD_CORE = {
        "font_size": 45,
        "text_color": "255 255 255 255",
        "border_color": "255 40 0 255",
        "bg_color": "100 0 0 240",
        "sound": "6 300",
        "effect": "Red",
        "icon": "1 Red Star",
    }

    # 빌드 유용 아이템 (파랑 강조)
    BUILD_USEFUL = {
        "font_size": 40,
        "text_color": "255 255 255 255",
        "border_color": "30 144 255 255",
        "bg_color": "0 30 80 220",
        "sound": "3 200",
        "effect": "Blue Temp",
        "icon": "1 Blue Circle",
    }

    # 고가 커런시 (골드 강조)
    CURRENCY_HIGH = {
        "font_size": 45,
        "text_color": "255 215 0 255",
        "border_color": "255 215 0 255",
        "bg_color": "40 30 0 255",
        "sound": "1 300",
        "effect": "Yellow",
        "icon": "0 Yellow Diamond",
    }

    # 밸류 아이템 (초록 강조)
    VALUE = {
        "font_size": 38,
        "text_color": "180 255 180 255",
        "border_color": "100 200 100 255",
        "bg_color": "0 40 0 200",
        "effect": "Green Temp",
        "icon": "2 Green Triangle",
    }


def make_show_block(comment: str, conditions: list[str], style: dict) -> str:
    """Show 블록 생성."""
    lines = [f"Show # PathcraftAI: {comment}"]
    for cond in conditions:
        lines.append(f"\t{cond}")
    lines.append(f"\tSetFontSize {style['font_size']}")
    lines.append(f"\tSetTextColor {style['text_color']}")
    lines.append(f"\tSetBorderColor {style['border_color']}")
    lines.append(f"\tSetBackgroundColor {style['bg_color']}")
    if "sound" in style:
        lines.append(f"\tPlayAlertSound {style['sound']}")
    if "effect" in style:
        lines.append(f"\tPlayEffect {style['effect']}")
    if "icon" in style:
        lines.append(f"\tMinimapIcon {style['icon']}")
    lines.append("")
    return "\n".join(lines)


def extract_build_gems(build_data: dict) -> tuple[list[str], list[str]]:
    """빌드에서 사용하는 스킬젬/서포트젬 이름 추출."""
    skills = set()
    supports = set()

    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gem_setups = stage.get("gem_setups", {})
        for setup_name, links in gem_setups.items():
            skills.add(setup_name)
            if isinstance(links, list):
                for link in links:
                    if isinstance(link, str):
                        supports.add(link)
                    elif isinstance(link, dict):
                        name = link.get("name", link.get("gem", ""))
                        if name:
                            if "Support" in name:
                                supports.add(name)
                            else:
                                skills.add(name)

    return sorted(skills), sorted(supports)


def extract_build_bases(build_data: dict) -> list[str]:
    """빌드 장비에서 베이스 타입 추출."""
    bases = set()
    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if isinstance(slot_data, dict):
                    base = slot_data.get("base_type", slot_data.get("base", ""))
                    if base:
                        bases.add(base)
    return sorted(bases)


def detect_build_type(build_data: dict) -> str:
    """빌드 타입 감지 (spell/attack/minion/dot)."""
    gems = " ".join(extract_build_gems(build_data)[0]).lower()
    if any(k in gems for k in ["raise zombie", "raise spectre", "summon", "animate"]):
        return "minion"
    if any(k in gems for k in ["blight", "contagion", "essence drain", "toxic rain", "caustic"]):
        return "dot"
    if any(k in gems for k in ["cyclone", "lacerate", "lightning arrow", "tornado shot"]):
        return "attack"
    return "spell"


def generate_overlay(build_data: dict) -> str:
    """빌드 오버레이 필터 룰 생성."""
    skills, supports = extract_build_gems(build_data)
    bases = extract_build_bases(build_data)
    build_name = build_data.get("meta", {}).get("build_name", "Unknown Build")
    build_class = build_data.get("meta", {}).get("class", "")
    build_type = detect_build_type(build_data)

    blocks = []

    # 헤더
    blocks.append(f"""#===============================================================================================================
# PathcraftAI Build Filter Overlay
# Build: {build_name}
# Class: {build_class} ({build_type})
# Generated by PathcraftAI filter_generator
#===============================================================================================================
""")

    # 1. 빌드 핵심 스킬 젬
    if skills:
        all_gems = [f'"{g}"' for g in skills]
        blocks.append(make_show_block(
            f"빌드 핵심 스킬 ({len(skills)}개)",
            [
                'Class "Skill Gems"',
                f'BaseType == {" ".join(all_gems)}',
            ],
            FilterStyle.BUILD_CORE,
        ))

    # 2. 빌드 서포트 젬
    if supports:
        # "Support" suffix 제거해서 BaseType 매칭
        support_names = [f'"{s}"' for s in supports]
        blocks.append(make_show_block(
            f"빌드 서포트 젬 ({len(supports)}개)",
            [
                'Class "Support Gems"',
                f'BaseType == {" ".join(support_names)}',
            ],
            FilterStyle.BUILD_USEFUL,
        ))

    # 3. 빌드 장비 베이스
    if bases:
        base_names = [f'"{b}"' for b in bases]
        blocks.append(make_show_block(
            f"빌드 장비 베이스 ({len(bases)}개)",
            [
                'Rarity Rare',
                f'BaseType == {" ".join(base_names)}',
                'ItemLevel >= 75',
            ],
            FilterStyle.BUILD_USEFUL,
        ))

    # 4. 빌드 타입별 크래프팅 베이스
    crafting_bases = get_crafting_bases(build_type)
    if crafting_bases:
        craft_names = [f'"{b}"' for b in crafting_bases]
        blocks.append(make_show_block(
            f"크래프팅 베이스 ({build_type})",
            [
                'Rarity Normal Rare',
                f'BaseType == {" ".join(craft_names)}',
                'ItemLevel >= 82',
            ],
            FilterStyle.VALUE,
        ))

    # 5. 고가 커런시 (neversink_filter_rules.json에서)
    currency_rules = load_currency_tiers()
    if currency_rules:
        for tier_name, tier_items in currency_rules.items():
            if tier_name in ("t1_mirror_divine", "t2_exalted"):
                item_names = [f'"{c}"' for c in tier_items]
                blocks.append(make_show_block(
                    f"커런시 {tier_name}",
                    [
                        'Class "Currency"',
                        f'BaseType == {" ".join(item_names)}',
                    ],
                    FilterStyle.CURRENCY_HIGH,
                ))

    return "\n".join(blocks)


def get_crafting_bases(build_type: str) -> list[str]:
    """빌드 타입별 크래프팅 베이스 목록."""
    common = ["Vaal Regalia", "Astral Plate", "Zodiac Leather", "Titanium Spirit Shield",
              "Fingerless Silk Gloves", "Sorcerer Boots", "Two-Toned Boots", "Bone Helmet",
              "Crystal Belt", "Stygian Vise", "Marble Amulet", "Opal Ring", "Vermillion Ring"]

    type_specific = {
        "spell": ["Profane Wand", "Opal Sceptre", "Void Sceptre", "Samite Helmet"],
        "attack": ["Siege Axe", "Jewelled Foil", "Ambusher", "Imperial Claw", "Thicket Bow", "Spine Bow"],
        "dot": ["Profane Wand", "Opal Sceptre", "Short Bow"],
        "minion": ["Convoking Wand", "Bone Helmet", "Fossilised Spirit Shield"],
    }

    return common + type_specific.get(build_type, [])


def load_currency_tiers() -> dict:
    """neversink_filter_rules.json에서 커런시 티어 로드."""
    filepath = DATA_DIR / "neversink_filter_rules.json"
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("currency_tiers", {})


def apply_overlay(base_filter_path: Path, overlay: str, output_path: Path):
    """베이스 필터에 오버레이를 삽입."""
    with open(base_filter_path, "r", encoding="utf-8") as f:
        base_content = f.read()

    # Override Area ([[0100]]) 바로 앞에 삽입
    marker = "# [[0100]]"
    insert_pos = base_content.find(marker)

    if insert_pos > 0:
        result = base_content[:insert_pos] + overlay + "\n" + base_content[insert_pos:]
    else:
        # 마커 못 찾으면 맨 앞에 삽입
        result = overlay + "\n" + base_content

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    logger.info("필터 생성: %s (%d줄)", output_path, result.count("\n"))


def find_sanavi_filter(strictness: int = 3) -> Optional[Path]:
    """Sanavi 필터 자동 탐지."""
    strictness_names = {
        0: "0_Soft", 1: "1_Regular", 2: "2_Semi-Strict",
        3: "3_Strict", 4: "4_Very Strict", 5: "5_Uber Strict",
        6: "6_Uber Plus Strict",
    }
    name = strictness_names.get(strictness, "3_Strict")
    path = POE_FILTER_DIR / f"Sanavi_{name}.filter"
    if path.exists():
        return path

    # 아무 Sanavi 필터라도 찾기
    for p in POE_FILTER_DIR.glob("Sanavi_*.filter"):
        return p
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="PathcraftAI Build Filter Generator")
    ap.add_argument("build_json", help="POB 빌드 JSON 파일 경로 또는 '-' (stdin)")
    ap.add_argument("--base", help="베이스 필터 경로 (기본: Sanavi_3_Strict)")
    ap.add_argument("--out", help="출력 필터 경로 (기본: stdout 오버레이만)")
    ap.add_argument("--strictness", type=int, default=3, help="Sanavi 필터 엄격도 (0-6, 기본: 3)")
    args = ap.parse_args()

    # 빌드 데이터 로드
    if args.build_json == "-":
        build_data = json.load(sys.stdin)
    else:
        with open(args.build_json, "r", encoding="utf-8") as f:
            build_data = json.load(f)

    # 오버레이 생성
    overlay = generate_overlay(build_data)

    if args.out:
        # 베이스 필터에 오버레이 적용
        base_path = Path(args.base) if args.base else find_sanavi_filter(args.strictness)
        if not base_path or not base_path.exists():
            logger.error("베이스 필터 없음: %s", base_path)
            sys.exit(1)

        output_path = Path(args.out)
        apply_overlay(base_path, overlay, output_path)
        logger.info("완료: %s", output_path)
    else:
        # 오버레이만 stdout 출력
        print(overlay)
