# -*- coding: utf-8 -*-
"""
빌드 기반 아이템 필터 생성기

Sanavi(NeverSink) 베이스 필터 위에 빌드 오버레이를 생성.
POB 빌드 데이터에서 필요한 젬/베이스/커런시를 추출하고 하이라이트.
디비니 카드, 유니크, chanceable 베이스까지 포함.

사용법:
    python filter_generator.py build.json --base "Sanavi_3_Strict.filter" --out "MyBuild.filter"
    python filter_generator.py build.json  # 오버레이만 출력
    python filter_generator.py build.json --coaching coach.json --strictness 3
"""

import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Optional

from filter_merge import (
    POE_FILTER_DIR,
    apply_overlay_to_file,
    find_sanavi_filter as _find_sanavi_filter_shared,
)
from pathcraft_sections import make_show_block as aurora_show_block
from sections_continue import generate_beta_overlay

logger = logging.getLogger("filter_gen")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# FilterStyle 클래스 제거됨 — Aurora Glow 팔레트 사용 (aurora_show_block)


# 유니크 → 디비니 카드 매핑 (빌드 타겟용)
UNIQUE_TO_DIVCARD: dict[str, list[dict]] = {
    "Death's Oath": [{"card": "The Oath", "stack": 6}],
    "Shavronne's Wrappings": [{"card": "The Offering", "stack": 8}],
    "Headhunter": [{"card": "The Doctor", "stack": 8}, {"card": "The Fiend", "stack": 11}],
    "Mageblood": [{"card": "The Apothecary", "stack": 13}],
    "Aegis Aurora": [{"card": "The Gladiator", "stack": 5}],
    "Kaom's Heart": [{"card": "The King's Heart", "stack": 8}],
    "The Squire": [{"card": "The Shieldbearer", "stack": 13}],
    "Ashes of the Stars": [{"card": "The Enlightened", "stack": 6}],
    "Nimis": [{"card": "The Rabbit's Foot", "stack": 9}],
    "Badge of the Brotherhood": [{"card": "Brotherhood in Exile", "stack": 5}],
    "Inpulsa's Broken Heart": [{"card": "The Spark and the Flame", "stack": 7}],
    "Cospri's Malice": [{"card": "The Wolven King's Bite", "stack": 8}],
    "Hyrri's Ire": [{"card": "The Wind", "stack": 10}],
    "Tabula Rasa": [{"card": "Humility", "stack": 9}],
    "Skin of the Loyal": [{"card": "The Sacrifice", "stack": 9}],
    "Replica Farruls Fur": [{"card": "The Cheater", "stack": 5}],
    "The Brass Dome": [{"card": "The Mountain", "stack": 8}],
    "Cloak of Defiance": [{"card": "The Easy Stroll", "stack": 5}],
    "Queen of the Forest": [{"card": "The Wolf", "stack": 5}],
    "Doryani's Prototype": [{"card": "Doryani's Epiphany", "stack": 5}],
    "Forbidden Shako": [{"card": "The Dragon's Heart", "stack": 10}],
}

# 유니크 → chanceable 베이스 매핑 (자주 쓰이는 것만)
UNIQUE_TO_BASE: dict[str, str] = {
    "Tabula Rasa": "Simple Robe",
    "Goldrim": "Leather Cap",
    "Wanderlust": "Wool Shoes",
    "Lifesprig": "Driftwood Wand",
    "Praxis": "Paua Ring",
    "Le Heup of All": "Iron Ring",
    "Berek's Grip": "Two-Stone Ring",
    "Berek's Pass": "Two-Stone Ring",
    "Berek's Respite": "Two-Stone Ring",
    "Aegis Aurora": "Champion Kite Shield",
    "Death's Oath": "Astral Plate",
    "Shavronne's Wrappings": "Occultist's Vestment",
    "Inpulsa's Broken Heart": "Sadist Garb",
    "Cospri's Malice": "Jewelled Foil",
    "Hyrri's Ire": "Zodiac Leather",
    "The Brass Dome": "Gladiator Plate",
    "Queen of the Forest": "Destiny Leather",
    "Cloak of Defiance": "Lacquered Garb",
    "Doryani's Prototype": "Saint's Hauberk",
    "Mageblood": "Heavy Belt",
    "Headhunter": "Leather Belt",
    "Kaom's Heart": "Glorious Plate",
}


def make_hide_block(comment: str, conditions: list[str]) -> str:
    """Hide 블록 생성."""
    lines = [f"Hide # PathcraftAI: {comment}"]
    for cond in conditions:
        lines.append(f"\t{cond}")
    lines.append("")
    return "\n".join(lines)


def extract_build_uniques(
    build_data: dict,
    coaching_data: Optional[dict] = None,
) -> list[str]:
    """빌드에서 사용하는 유니크 아이템 이름 추출.

    소스 우선순위:
    1. coaching_data의 key_items (AI 코치가 식별한 핵심 장비)
    2. build_data의 progression_stages에서 gear 정보
    """
    uniques = set()

    # 코칭 결과에서 추출
    if coaching_data:
        for item in coaching_data.get("key_items", []):
            name = item.get("name", "")
            if name:
                uniques.add(name)

    # 빌드 데이터에서 유니크 장비 추출
    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if isinstance(slot_data, dict):
                    name = slot_data.get("name", slot_data.get("item", ""))
                    rarity = slot_data.get("rarity", "")
                    if name and rarity.lower() == "unique":
                        uniques.add(name)

    # items 필드에서도 추출 (POB 직접 파싱 결과)
    for item in build_data.get("items", []):
        if isinstance(item, dict):
            if item.get("rarity", "").lower() == "unique":
                name = item.get("name", "")
                if name:
                    uniques.add(name)

    return sorted(uniques)


def get_target_divcards(unique_names: list[str]) -> list[dict]:
    """유니크 아이템 목록에서 타겟 디비니 카드 추출."""
    cards = []
    seen = set()
    for uname in unique_names:
        for entry in UNIQUE_TO_DIVCARD.get(uname, []):
            card_name = entry["card"]
            if card_name not in seen:
                seen.add(card_name)
                cards.append({
                    "card": card_name,
                    "stack": entry["stack"],
                    "target_unique": uname,
                })
    return cards


def get_chanceable_bases(unique_names: list[str]) -> list[dict]:
    """유니크 아이템 목록에서 chanceable 베이스 추출."""
    bases = []
    seen = set()
    for uname in unique_names:
        base = UNIQUE_TO_BASE.get(uname)
        if base and base not in seen:
            seen.add(base)
            bases.append({"base": base, "unique": uname})
    return bases


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


def generate_overlay(
    build_data: dict,
    coaching_data: Optional[dict] = None,
    strictness: int = 3,
) -> str:
    """빌드 오버레이 필터 룰 생성.

    Args:
        build_data: POB 파싱 결과 JSON
        coaching_data: AI 코치 결과 JSON (디비카/유니크 강화용)
        strictness: 엄격도 (0=Soft ~ 4=Very Strict)
    """
    skills, supports = extract_build_gems(build_data)
    bases = extract_build_bases(build_data)
    uniques = extract_build_uniques(build_data, coaching_data)
    build_name = build_data.get("meta", {}).get("build_name", "Unknown Build")
    build_class = build_data.get("meta", {}).get("class", "")
    build_type = detect_build_type(build_data)

    strictness_label = {
        0: "Soft", 1: "Regular", 2: "Semi-Strict", 3: "Strict", 4: "Very Strict",
    }.get(strictness, "Strict")

    blocks = []

    # 헤더
    blocks.append(f"""#===============================================================================================================
# PathcraftAI Build Filter Overlay
# Build: {build_name}
# Class: {build_class} ({build_type})
# Strictness: {strictness_label} ({strictness})
# Uniques: {', '.join(uniques[:5])}{'...' if len(uniques) > 5 else ''}
# Generated by PathcraftAI filter_generator
#===============================================================================================================
""")

    # ── Section 1: 빌드 타겟 디비니 카드 ──
    target_cards = get_target_divcards(uniques)
    if target_cards:
        card_names = [f'"{c["card"]}"' for c in target_cards]
        card_comment = ", ".join(
            f'{c["card"]}→{c["target_unique"]}' for c in target_cards
        )
        blocks.append(aurora_show_block(
            f"빌드 타겟 디비카 ({card_comment})",
            ['Class "Divination Cards"',
             f'BaseType == {" ".join(card_names)}'],
            category="divcard", tier="P1_KEYSTONE", keystone=True,
        ))

    # ── Section 2: 고가 디비니 카드 (neversink 티어) ──
    divcard_tiers = load_divcard_tiers()
    for tier_name, aurora_tier in [
        ("t1_top", "P1_KEYSTONE"),
        ("t2_high", "P2_CORE"),
    ]:
        tier_cards = divcard_tiers.get(tier_name, [])
        target_names = {c["card"] for c in target_cards}
        tier_cards = [c for c in tier_cards if c not in target_names]
        if tier_cards:
            names = [f'"{c}"' for c in tier_cards]
            blocks.append(aurora_show_block(
                f"고가 디비카 {tier_name} ({len(tier_cards)}개)",
                ['Class "Divination Cards"',
                 f'BaseType == {" ".join(names)}'],
                category="divcard", tier=aurora_tier,
            ))

    # ── Section 3: 빌드 유니크 아이템 ──
    if uniques:
        unique_names = [f'"{u}"' for u in uniques]
        blocks.append(aurora_show_block(
            f"빌드 유니크 ({len(uniques)}개)",
            ['Rarity Unique',
             f'BaseType == {" ".join(unique_names)}'],
            category="unique", tier="P1_KEYSTONE", keystone=True,
        ))

    # ── Section 4: Chanceable 베이스 ──
    chanceable = get_chanceable_bases(uniques)
    if chanceable:
        base_names = [f'"{c["base"]}"' for c in chanceable]
        blocks.append(aurora_show_block(
            f"Chanceable 베이스 ({len(chanceable)}개)",
            ['Rarity Normal',
             f'BaseType == {" ".join(base_names)}'],
            category="unique", tier="P5_MINOR", is_build_target=False,
        ))

    # ── Section 5: 빌드 핵심 스킬 젬 ──
    if skills:
        all_gems = [f'"{g}"' for g in skills]
        blocks.append(aurora_show_block(
            f"빌드 핵심 스킬 ({len(skills)}개)",
            ['Class "Skill Gems"',
             f'BaseType == {" ".join(all_gems)}'],
            category="gem", tier="P1_KEYSTONE",
        ))

    # ── Section 6: 빌드 서포트 젬 ──
    if supports:
        support_names = [f'"{s}"' for s in supports]
        blocks.append(aurora_show_block(
            f"빌드 서포트 젬 ({len(supports)}개)",
            ['Class "Support Gems"',
             f'BaseType == {" ".join(support_names)}'],
            category="gem", tier="P2_CORE",
        ))

    # ── Section 7: 빌드 장비 베이스 ──
    if bases:
        base_names = [f'"{b}"' for b in bases]
        blocks.append(aurora_show_block(
            f"빌드 장비 베이스 ({len(bases)}개)",
            ['Rarity Rare',
             f'BaseType == {" ".join(base_names)}',
             'ItemLevel >= 75'],
            category="base", tier="P2_CORE",
        ))

    # ── Section 8: 빌드 타입별 크래프팅 베이스 ──
    crafting_bases = get_crafting_bases(build_type)
    if crafting_bases:
        craft_names = [f'"{b}"' for b in crafting_bases]
        blocks.append(aurora_show_block(
            f"크래프팅 베이스 ({build_type})",
            ['Rarity Normal Rare',
             f'BaseType == {" ".join(craft_names)}',
             'ItemLevel >= 82'],
            category="base", tier="P3_USEFUL",
        ))

    # ── Section 9: 고가 커런시 ──
    currency_rules = load_currency_tiers()
    if currency_rules:
        for tier_name, tier_items in currency_rules.items():
            aurora_tier = {"t1_mirror_divine": "P1_KEYSTONE",
                           "t2_exalted": "P2_CORE"}.get(tier_name)
            if aurora_tier:
                item_names = [f'"{c}"' for c in tier_items]
                blocks.append(aurora_show_block(
                    f"커런시 {tier_name}",
                    ['Class "Currency"',
                     f'BaseType == {" ".join(item_names)}'],
                    category="currency", tier=aurora_tier,
                ))

    # ── Section 10: 엄격도별 Hide 블록 ──
    hide_blocks = generate_hide_blocks(strictness, currency_rules)
    blocks.extend(hide_blocks)

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


def load_divcard_tiers() -> dict:
    """neversink_filter_rules.json에서 디비니 카드 티어 로드."""
    filepath = DATA_DIR / "neversink_filter_rules.json"
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("divination_cards", {})


def generate_hide_blocks(strictness: int, currency_rules: dict) -> list[str]:
    """엄격도별 Hide 블록 생성.

    엄격도 레벨:
    0 (Soft)        — Hide 없음, 전부 표시
    1 (Regular)     — 노말 무기/방어구 Hide (ilvl < 고정)
    2 (Semi-Strict) — + 매직 무기/방어구 Hide, 낮은 플라스크
    3 (Strict)      — + 저가 커런시 숨김, 레어 무기 제한
    4 (Very Strict) — + 대부분 레어 숨김, 디비카 t5 숨김
    """
    if strictness <= 0:
        return []

    blocks = []
    blocks.append("""
#===============================================================================================================
# PathcraftAI Strictness Hide Rules
#===============================================================================================================
""")

    # ── 레벨 1+: 노말 무기/방어구 숨김 ──
    if strictness >= 1:
        blocks.append(make_hide_block(
            "노말 무기/방어구 (링크 없음)",
            [
                'Rarity Normal',
                'Class "Body Armours" "Helmets" "Gloves" "Boots" "Shields"'
                ' "Axes" "Bows" "Claws" "Daggers" "Maces" "Sceptres"'
                ' "Staves" "Swords" "Wands" "Warstaves" "Rune Daggers"',
                'LinkedSockets < 5',
                'AreaLevel >= 68',
            ],
        ))

    # ── 레벨 2+: 매직 무기/방어구 + 낮은 플라스크 ──
    if strictness >= 2:
        blocks.append(make_hide_block(
            "매직 무기/방어구 (링크 없음)",
            [
                'Rarity Magic',
                'Class "Body Armours" "Helmets" "Gloves" "Boots" "Shields"'
                ' "Axes" "Bows" "Claws" "Daggers" "Maces" "Sceptres"'
                ' "Staves" "Swords" "Wands" "Warstaves" "Rune Daggers"',
                'LinkedSockets < 5',
                'AreaLevel >= 68',
            ],
        ))
        blocks.append(make_hide_block(
            "낮은 레벨 플라스크",
            [
                'Class "Life Flasks" "Mana Flasks" "Hybrid Flasks"',
                'AreaLevel >= 68',
                'ItemLevel < 65',
            ],
        ))

    # ── 레벨 3+: 저가 커런시 숨김, 레어 무기 제한 ──
    if strictness >= 3:
        low_currency = currency_rules.get("t7_chance", [])
        if low_currency:
            names = [f'"{c}"' for c in low_currency]
            blocks.append(make_hide_block(
                "저가 커런시 (맵 구간)",
                [
                    'Class "Currency"',
                    f'BaseType == {" ".join(names)}',
                    'AreaLevel >= 75',
                ],
            ))
        blocks.append(make_hide_block(
            "레어 무기 (낮은 ilvl)",
            [
                'Rarity Rare',
                'Class "Axes" "Bows" "Claws" "Daggers" "Maces" "Sceptres"'
                ' "Staves" "Swords" "Wands" "Warstaves" "Rune Daggers"',
                'ItemLevel < 75',
                'AreaLevel >= 68',
            ],
        ))

    # ── 레벨 4+: 대부분 레어 숨김, t5 디비카 숨김 ──
    if strictness >= 4:
        blocks.append(make_hide_block(
            "레어 방어구 (낮은 ilvl)",
            [
                'Rarity Rare',
                'Class "Body Armours" "Helmets" "Gloves" "Boots" "Shields"',
                'ItemLevel < 75',
                'AreaLevel >= 75',
            ],
        ))
        divcard_tiers = load_divcard_tiers()
        common_cards = divcard_tiers.get("t5_common", [])
        if common_cards:
            names = [f'"{c}"' for c in common_cards]
            blocks.append(make_hide_block(
                "저가 디비카 (t5)",
                [
                    'Class "Divination Cards"',
                    f'BaseType == {" ".join(names)}',
                ],
            ))

    return blocks


def apply_overlay(base_filter_path: Path, overlay: str, output_path: Path) -> None:
    """베이스 필터에 오버레이를 삽입 (filter_merge 위임)."""
    apply_overlay_to_file(base_filter_path, overlay, output_path)


def find_sanavi_filter(strictness: int = 3) -> Optional[Path]:
    """Sanavi 필터 자동 탐지 (filter_merge 위임)."""
    return _find_sanavi_filter_shared(strictness)


def generate_filter_json(
    build_data: dict,
    coaching_data: Optional[dict] = None,
    strictness: int = 3,
) -> dict:
    """Tauri 호출용: 필터 생성 결과를 JSON으로 반환."""
    overlay = generate_overlay(build_data, coaching_data, strictness)
    uniques = extract_build_uniques(build_data, coaching_data)
    target_cards = get_target_divcards(uniques)
    chanceable = get_chanceable_bases(uniques)

    return {
        "overlay": overlay,
        "stats": {
            "unique_count": len(uniques),
            "divcard_count": len(target_cards),
            "chanceable_count": len(chanceable),
            "strictness": strictness,
        },
        "uniques": uniques,
        "target_divcards": target_cards,
        "chanceable_bases": chanceable,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="PathcraftAI Build Filter Generator")
    ap.add_argument("build_json", nargs="?", default=None,
                    help="POB 빌드 JSON 파일 경로 또는 '-' (stdin). --arch continue에서는 생략 가능")
    ap.add_argument("--coaching", help="AI 코치 결과 JSON 파일 (디비카/유니크 강화용)")
    ap.add_argument("--base", help="베이스 필터 경로 (기본: Sanavi_3_Strict)")
    ap.add_argument("--out", help="출력 필터 경로 (기본: stdout 오버레이만)")
    ap.add_argument("--strictness", type=int, default=3,
                    help="엄격도 (0=Soft, 1=Regular, 2=Semi-Strict, 3=Strict, 4=Very Strict)")
    ap.add_argument("--json", action="store_true", help="JSON 형태로 출력 (Tauri용)")
    ap.add_argument("--arch", choices=("aurora", "continue"), default="aurora",
                    help="필터 아키텍처 (aurora=기존 오버레이, continue=β 레이어 체인)")
    args = ap.parse_args()

    # β Continue 경로 — 빌드 데이터 옵셔널, 독립 필터 출력
    if args.arch == "continue":
        if args.json:
            logger.error("β continue는 --json 미지원 (β-5b 예정)")
            sys.exit(2)
        if args.base:
            logger.warning("β continue는 --base 미지원 (standalone 필터), 무시됨")
        if args.strictness < 0 or args.strictness > 4:
            logger.error("--strictness는 0~4 범위 (실제: %d)", args.strictness)
            sys.exit(2)

        # 빌드 데이터 로드 (옵셔널)
        build_data: Optional[dict] = None
        coaching_data: Optional[dict] = None
        if args.build_json:
            if args.build_json == "-":
                build_data = json.load(sys.stdin)
            else:
                with open(args.build_json, "r", encoding="utf-8") as f:
                    build_data = json.load(f)
        if args.coaching:
            with open(args.coaching, "r", encoding="utf-8") as f:
                coaching_data = json.load(f)

        overlay = generate_beta_overlay(
            strictness=args.strictness,
            build_data=build_data,
            coaching_data=coaching_data,
        )
        if args.out:
            Path(args.out).write_text(overlay, encoding="utf-8")
            logger.info("β Continue 필터 출력: %s", args.out)
        else:
            print(overlay)
        sys.exit(0)

    # Aurora 경로는 빌드 데이터 필수
    if args.build_json is None:
        logger.error("aurora 아키텍처는 build_json 인자가 필요합니다")
        sys.exit(2)

    # 빌드 데이터 로드
    if args.build_json == "-":
        build_data = json.load(sys.stdin)
    else:
        with open(args.build_json, "r", encoding="utf-8") as f:
            build_data = json.load(f)

    # 코칭 데이터 로드
    coaching_data = None
    if args.coaching:
        with open(args.coaching, "r", encoding="utf-8") as f:
            coaching_data = json.load(f)

    if args.json:
        # JSON 출력 (Tauri 연동용)
        result = generate_filter_json(build_data, coaching_data, args.strictness)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.out:
        # 베이스 필터에 오버레이 적용
        overlay = generate_overlay(build_data, coaching_data, args.strictness)
        base_path = Path(args.base) if args.base else find_sanavi_filter(args.strictness)
        if not base_path or not base_path.exists():
            logger.error("베이스 필터 없음: %s", base_path)
            sys.exit(1)

        output_path = Path(args.out)
        apply_overlay(base_path, overlay, output_path)
        logger.info("완료: %s", output_path)
    else:
        # 오버레이만 stdout 출력
        overlay = generate_overlay(build_data, coaching_data, args.strictness)
        print(overlay)
