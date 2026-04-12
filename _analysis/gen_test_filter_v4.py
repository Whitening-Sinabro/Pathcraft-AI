# -*- coding: utf-8 -*-
"""Aurora v4 — Sanavi 실제 tier 데이터 기반 테스트 필터 생성.

이전 v3가 Unique/Gem/Jewel/Fragment 조건을 수동으로 만들었던 문제 수정.
sanavi_tier_data.json 의 실제 BaseType 리스트로 모든 카테고리 tier rule 작성.
"""
import sys, json, os
sys.path.insert(0, 'D:/Pathcraft-AI/python')
sys.stdout.reconfigure(encoding='utf-8')

if 'pathcraft_palette' in sys.modules:
    del sys.modules['pathcraft_palette']
from pathcraft_palette import (
    GOLD_STACK_FONTS, TIER_COLORS_BY_CATEGORY, CATEGORY_COLORS, CATEGORY_SHAPES,
    get_currency_tiers, get_bg_color, VALID_MODES, DEFAULT_MODE,
)
from pathcraft_sections import (
    make_show_block, make_gold_block, make_restex_block,
    generate_currency_stack_section, generate_leveling_currency_section,
    generate_lifeforce_section, generate_splinter_section,
    generate_links_sockets_section,
    generate_influenced_section, generate_exotic_bases_section,
    generate_exotic_classes_section, generate_exotic_variations_section,
    generate_crafting_matrix_section, generate_chancing_section,
    generate_maps_section, generate_pseudo_maps_section,
    generate_leveling_flasks_section, generate_final_safety_section,
    generate_id_mod_section, generate_exotic_mods_section,
    generate_endgame_rare_section, generate_misc_rules_section,
    # Group B
    generate_heist_section, generate_replica_foulborn_section,
    generate_special_currency_section, generate_idols_section,
    generate_endgame_flasks_section,
    # Perfection + Memory Strand
    generate_perfection_section, generate_memory_strand_section,
    # Leveling Rares + Normals
    generate_leveling_rares_section, generate_leveling_normals_section,
    # Scarab + Cluster
    generate_scarab_tiers_section, generate_cluster_jewel_section,
    # Strictness
    apply_strictness, STRICTNESS_LEVELS,
)

# 모드 결정: MODE 환경변수 (trade | ssf | hcssf) — 기본 ssf
MODE = os.environ.get("MODE", DEFAULT_MODE).lower()
if MODE not in VALID_MODES:
    raise ValueError(f"MODE 환경변수는 {VALID_MODES} 중 하나여야 함. 받음: {MODE!r}")

# Sanavi 실제 tier 데이터 로드
with open('D:/Pathcraft-AI/data/sanavi_tier_data.json', 'r', encoding='utf-8') as f:
    sanavi = json.load(f)

# NeverSink rules JSON (currency/divcard 정제된 리스트)
with open('D:/Pathcraft-AI/data/neversink_filter_rules.json', 'r', encoding='utf-8') as f:
    ns_rules = json.load(f)


# ---------------------------------------------------------------------------
# Sanavi tier → PathcraftAI P-tier 매핑
# ---------------------------------------------------------------------------
# 각 카테고리의 주요 tier만 선정 (Sanavi는 너무 세분화됨)

TIER_MAPPING = {
    "uniques": [
        # (sanavi_tier, p_tier, label)
        # Note: hideable/hideable2 는 의도적으로 제외 — Sanavi 원본 dim 스타일 유지
        # (Aurora로 오버라이드하면 "빌드 타겟 오염" 발생)
        ("t1",        "P1_KEYSTONE", "T1 Mirror-tier (Mageblood/HH/Headhunter base)"),
        ("t2",        "P2_CORE",     "T2 High Value"),
        ("t3",        "P3_USEFUL",   "T3 Useful"),
        ("t3boss",    "P4_SUPPORT",  "T3 Boss Drop"),
    ],
    "gems": [
        ("t1",                  "P1_KEYSTONE", "T1 Awakened (Empower/Enhance/Enlighten)"),
        ("t2",                  "P2_CORE",     "T2 High Value Support"),
        ("vaal20",              "P2_CORE",     "Vaal Gem 20Q"),
        ("anyexceptionalqual",  "P3_USEFUL",   "Exceptional Quality"),
        ("2023",                "P3_USEFUL",   "Level 20+ Q23"),
        ("2120",                "P4_SUPPORT",  "Level 21 Q20"),
        ("t3",                  "P5_MINOR",    "T3 Low"),
    ],
    "divination": [
        ("t1",   "P1_KEYSTONE", "T1 Top (The Apothecary/Doctor)"),
        ("t2",   "P2_CORE",     "T2 High"),
        ("t3",   "P3_USEFUL",   "T3 Good"),
        ("t4",   "P4_SUPPORT",  "T4 Medium"),
        ("t4c",  "P4_SUPPORT",  "T4 Common"),
        ("t5",   "P5_MINOR",    "T5 Low"),
        ("t5c",  "P6_LOW",      "T5 Lowest"),
    ],
    "fragments": [
        ("t1", "P1_KEYSTONE", "T1 Sacred Blossom/Maven"),
        ("t2", "P2_CORE",     "T2 High"),
        ("t3", "P3_USEFUL",   "T3 Good"),
        ("t4", "P4_SUPPORT",  "T4 Medium"),
        ("t5", "P5_MINOR",    "T5 Low"),
        ("t6", "P6_LOW",      "T6 Lowest"),
    ],
    "currency": [
        ("t1exalted", "P1_KEYSTONE", "T1 Mirror-tier (Awakener/Mirror Shard)"),
        ("t2divine",  "P2_CORE",     "T2 Divine-tier"),
        ("t2",        "P3_USEFUL",   "T3 Mid-high"),
        ("t3",        "P3_USEFUL",   "T3 Chaos/Annul"),
        ("t4",        "P4_SUPPORT",  "T4 Alch/Vaal"),
        ("t5",        "P5_MINOR",    "T5 Blessed/Bauble"),
        ("t6",        "P6_LOW",      "T6 Chance/Chromatic"),
        ("t7",        "P6_LOW",      "T7 Shards"),
    ],
}


def quoted(names):
    return " ".join(f'"{n}"' for n in names)


def get_sanavi_items(category: str, tier: str, limit: int = 30) -> list[str]:
    """Sanavi tier 데이터에서 아이템 리스트 반환 (limit 적용)."""
    cat_data = sanavi.get(category, {})
    items = cat_data.get(tier, [])
    return items[:limit] if items else []


# ---------------------------------------------------------------------------
# 필터 생성
# ---------------------------------------------------------------------------

blocks = []
blocks.append(
    "#" + "=" * 110 + "\n"
    f"# PathcraftAI Aurora Palette - Reality Test Filter v4 (MODE={MODE})\n"
    "# Source: Sanavi tier data + mode-specific currency tiers\n"
    f"# Mode priority: {'Trade economy' if MODE == 'trade' else 'SSF crafting' if MODE == 'ssf' else 'HCSSF survival'}\n"
    f"# Usage: POE Esc -> Options -> UI -> Filter dropdown 'PathcraftAI_Aurora_{MODE.upper()}'\n"
    "#" + "=" * 110 + "\n"
)

# ============================================================
# Gold — StackSize tiers (완전 커버리지)
# ============================================================
blocks.append("# [AURORA] Gold - StackSize tiers (>= semantics)")
for min_stack, font in GOLD_STACK_FONTS:
    if min_stack > 0:
        blocks.append(make_gold_block(min_stack, font))
# Gold 최종 catch-all (보더 없음)
from pathcraft_palette import get_bg_color
gold_bg = get_bg_color("gold", "P6_LOW")
blocks.append(
    "Show # PathcraftAI: Gold Stack any (fallback)\n"
    "\tBaseType == \"Gold\"\n"
    f"\tSetFontSize {GOLD_STACK_FONTS[-1][1]}\n"
    f"\tSetTextColor {CATEGORY_COLORS['gold']} 255\n"
    f"\tSetBackgroundColor {gold_bg}\n"
    f"\tMinimapIcon 2 Yellow {CATEGORY_SHAPES['gold']}\n"
)

# ============================================================
# Links & Sockets — 6링크/5링크/6소켓/화이트소켓
# ============================================================
blocks.append(generate_links_sockets_section())

# ============================================================
# Influenced Bases [[0300-0400]] — Shaper/Elder/Crusader/Hunter/Redeemer/Warlord
# ============================================================
blocks.append(generate_influenced_section())

# ============================================================
# Exotic Bases [[0500]] — Heist/Ritual/Expedition/Stygian
# ============================================================
blocks.append(generate_exotic_bases_section())

# ============================================================
# ID Mod Filtering [[0600-0800]] — HasExplicitMod 기반 ID 모드
# ============================================================
blocks.append(generate_id_mod_section())

# ============================================================
# Currency — 모드별 BaseType 리스트 기반 (Trade/SSF/HCSSF)
# ============================================================
mode_currency_tiers = get_currency_tiers(MODE)
blocks.append(f"# [AURORA] Currency - Hot Coral gradient ({MODE.upper()} priority)")
for p_tier in ("P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
               "P4_SUPPORT", "P5_MINOR", "P6_LOW"):
    items = mode_currency_tiers.get(p_tier, [])
    if not items:
        continue
    # 티어 한글 레이블
    tier_label = {
        "P1_KEYSTONE": "T1 Keystone",
        "P2_CORE":     "T2 Core",
        "P3_USEFUL":   "T3 Useful",
        "P4_SUPPORT":  "T4 Support",
        "P5_MINOR":    "T5 Minor",
        "P6_LOW":      "T6 Low",
    }[p_tier]
    blocks.append(make_show_block(
        f"Currency {tier_label} ({MODE}) [{len(items)} types]",
        ['Class "Currency" "Stackable Currency"', f'BaseType == {quoted(items)}'],
        category='currency', tier=p_tier,
    ))

# ============================================================
# Currency Stack — 스택 기반 티어 승격 (>= 3, >= 6, 보급품 >= 3/5/10)
# ============================================================
blocks.append(generate_currency_stack_section(MODE))

# ============================================================
# Exotic Classes [[1200]] — Voidstones/Trinkets/Fishing/Pieces/Relics
# ============================================================
blocks.append(generate_exotic_classes_section())

# ============================================================
# Exotic Variations [[1300]] — Synthesised/Fractured/Enchanted/Crucible
# ============================================================
blocks.append(generate_exotic_variations_section())

# ============================================================
# Perfection & Overquality [[0900]] [0901]
# ============================================================
blocks.append(generate_perfection_section())

# ============================================================
# Memory Strand Gear [[0900]] [0902]
# ============================================================
blocks.append(generate_memory_strand_section())

# ============================================================
# Exotic Mods [[1100]] — Veiled/Incursion/Delve/Warband/Essence
# ============================================================
blocks.append(generate_exotic_mods_section())

# ============================================================
# Unique — Sanavi tier 데이터 기반 (t1/t2/t3/t3boss/hideable/hideable2)
# ============================================================
blocks.append("# [AURORA] Unique - Tangerine gradient (Sanavi tier data)")
# 특수: Keystone 베이스 (multispecialhigh = Heavy Belt 등 핵심 unique base)
items = get_sanavi_items("uniques", "multispecialhigh", limit=30)
if items:
    blocks.append(make_show_block(
        f"Unique KEYSTONE multi-high base [{len(items)} types]",
        ['Rarity Unique', f'BaseType == {quoted(items)}'],
        category='unique', tier='P1_KEYSTONE', keystone=True,
    ))
for sanavi_tier, p_tier, label in TIER_MAPPING["uniques"]:
    items = get_sanavi_items("uniques", sanavi_tier, limit=30)
    if not items:
        continue
    blocks.append(make_show_block(
        f"Unique {label} [{len(sanavi.get('uniques', {}).get(sanavi_tier, []))} types]",
        ['Rarity Unique', f'BaseType == {quoted(items)}'],
        category='unique', tier=p_tier,
    ))
# 최종 fallback (매핑 안 된 유니크)
blocks.append(make_show_block(
    "Unique any (fallback)",
    ['Rarity Unique'],
    category='unique', tier='P4_SUPPORT',
))

# ============================================================
# Divination Card — Sanavi tier 데이터 기반
# ============================================================
blocks.append("# [AURORA] Divination Card - Electric Lavender gradient (Sanavi tier data)")

# HCSSF 모드: HC 경제 기반 디비카 T1 오버라이드 (생존/크래프팅 카드 승격)
if MODE == "hcssf":
    hc_div_path = 'D:/Pathcraft-AI/data/hc_divcard_tiers.json'
    if os.path.exists(hc_div_path):
        with open(hc_div_path, 'r', encoding='utf-8') as f:
            hc_div = json.load(f)
        hc_t1 = hc_div.get("t1", [])
        if hc_t1:
            blocks.append(make_show_block(
                f"HCSSF HC-T1 Div Card Override ({len(hc_t1)} types)",
                ['Class "Divination Cards"', f'BaseType == {quoted(hc_t1[:30])}'],
                category='divcard', tier='P1_KEYSTONE', keystone=True,
            ))

for sanavi_tier, p_tier, label in TIER_MAPPING["divination"]:
    items = get_sanavi_items("divination", sanavi_tier, limit=30)
    if not items:
        continue
    blocks.append(make_show_block(
        f"Div Card {label} [{len(sanavi.get('divination', {}).get(sanavi_tier, []))} types]",
        ['Class "Divination Cards"', f'BaseType == {quoted(items)}'],
        category='divcard', tier=p_tier,
    ))
blocks.append(make_show_block(
    "Div Card fallback (any remaining)",
    ['Class "Divination Cards"'],
    category='divcard', tier='P6_LOW',
))

# ============================================================
# Gem — Sanavi tier 데이터 기반
# ============================================================
blocks.append("# [AURORA] Gem - Chartreuse gradient (Sanavi tier data)")
for sanavi_tier, p_tier, label in TIER_MAPPING["gems"]:
    items = get_sanavi_items("gems", sanavi_tier, limit=30)
    if not items:
        continue
    blocks.append(make_show_block(
        f"Gem {label} [{len(sanavi.get('gems', {}).get(sanavi_tier, []))} types]",
        ['Class "Skill Gems" "Support Gems"', f'BaseType == {quoted(items)}'],
        category='gem', tier=p_tier,
    ))
blocks.append(make_show_block(
    "Gem any (fallback)",
    ['Class "Skill Gems" "Support Gems"'],
    category='gem', tier='P5_MINOR',
))

# ============================================================
# Jewel — Sanavi tier 데이터 (cluster + abyss)
# ============================================================
blocks.append("# [AURORA] Jewel - Bubblegum gradient (Sanavi tier data)")
# Cluster Jewel high tier
for tier_key, p_tier, label in [
    ("highlarge",  "P1_KEYSTONE", "Large Cluster High"),
    ("highmedium", "P2_CORE",     "Medium Cluster High"),
    ("highsmall",  "P3_USEFUL",   "Small Cluster High"),
]:
    items = get_sanavi_items("jewels", tier_key, limit=10)
    if items:
        blocks.append(make_show_block(
            f"Jewel {label}",
            ['Rarity Rare', 'ItemLevel >= 84', f'BaseType == {quoted(items)}'],
            category='jewel', tier=p_tier,
        ))
# Abyss Jewel
blocks.append(make_show_block(
    "Jewel Abyss high ilvl",
    ['Rarity Rare', 'Class "Abyss Jewels"', 'ItemLevel >= 84'],
    category='jewel', tier='P2_CORE',
))
# Corrupted 1 mod
items = get_sanavi_items("jewels", "1modcorrupted", limit=10)
if items:
    blocks.append(make_show_block(
        "Jewel 1-mod corrupted",
        ['Rarity Rare', 'Corrupted True', 'CorruptedMods 1', f'BaseType == {quoted(items)}'],
        category='jewel', tier='P3_USEFUL',
    ))
blocks.append(make_show_block(
    "Jewel any Rare (fallback)",
    ['Rarity Rare', 'Class "Jewels" "Abyss Jewels"'],
    category='jewel', tier='P4_SUPPORT',
))

# ============================================================
# Cluster Jewels [[2805-2806]] — 경제 기반 티어링
# ============================================================
blocks.append(generate_cluster_jewel_section())

# ============================================================
# Endgame Rare [[1600-2100]] — Breach rings/Talismans/Jewelry/Belts
# ============================================================
blocks.append(generate_endgame_rare_section())

# ============================================================
# Crafting Matrix [[2300]] — 고ilvl 비부패/비미러 크래프팅 베이스
# ============================================================
blocks.append(generate_crafting_matrix_section())

# ============================================================
# Chancing Targets [[2400]] — Headhunter/Mageblood/Aegis Aurora
# ============================================================
blocks.append(generate_chancing_section())

# ============================================================
# Misc Rules [[2600]] — RGB Recipe + Remaining Rares
# ============================================================
blocks.append(generate_misc_rules_section())

# ============================================================
# Maps [[3200-3300]] — 특수 맵 + 티어별 진행
# ============================================================
blocks.append(generate_maps_section())

# ============================================================
# Pseudo Maps [[3400]] — Expedition/Heist/Sanctum
# ============================================================
blocks.append(generate_pseudo_maps_section())

# ============================================================
# Scarab Tiers [[3500]] — 개별 스카라브 티어링
# ============================================================
blocks.append(generate_scarab_tiers_section())

# ============================================================
# Fragment — Sanavi tier 데이터 기반
# ============================================================
blocks.append("# [AURORA] Fragment - Lavender Mist gradient (Sanavi tier data)")
for sanavi_tier, p_tier, label in TIER_MAPPING["fragments"]:
    items = get_sanavi_items("fragments", sanavi_tier, limit=30)
    if not items:
        continue
    blocks.append(make_show_block(
        f"Fragment {label} [{len(sanavi.get('fragments', {}).get(sanavi_tier, []))} types]",
        [f'BaseType == {quoted(items)}'],
        category='fragment', tier=p_tier,
    ))
blocks.append(make_show_block(
    "Fragment any (fallback)",
    ['Class "Map Fragments" "Misc Map Items"'],
    category='fragment', tier='P4_SUPPORT',
))

# ============================================================
# Lifeforce — Harvest (StackSize 6단계)
# ============================================================
blocks.append(generate_lifeforce_section())

# ============================================================
# Splinters — Breach/Legion/Simulacrum (StackSize 단계별)
# ============================================================
blocks.append(generate_splinter_section())

# ============================================================
# Leveling Currency — AreaLevel <= 67 전용 하이라이트
# ============================================================
blocks.append(generate_leveling_currency_section())

# ============================================================
# Leveling Flasks [[4900-5100]] — AreaLevel 기반 단계적 플라스크
# ============================================================
blocks.append(generate_leveling_flasks_section())

# ============================================================
# Leveling Rares [[5200]] — 무기/방어구/악세 레벨링 진행
# ============================================================
blocks.append(generate_leveling_rares_section())

# ============================================================
# Leveling Normal/Magic [[5300]] — 4링크/RGB/3링크/Act1/무기진행/매직숨김
# ============================================================
blocks.append(generate_leveling_normals_section())

# ============================================================
# Final Safety [[5306-5307]] — 나머지 장비 Hide + RestEx
# ============================================================
blocks.append(generate_final_safety_section())

# ============================================================
# Heist Gear [[2900]] — Cloaks/Brooches/Gear/Tools
# ============================================================
blocks.append(generate_heist_section())

# ============================================================
# Replica & Foulborn [[3100]] — Replica/Foulborn Uniques
# ============================================================
blocks.append(generate_replica_foulborn_section())

# ============================================================
# Special Currency [[4000]] — Vials/Delirium/Fossils/Oils/Runes/
#   Corpses/Essences/Omens/Tattoos
# ============================================================
blocks.append(generate_special_currency_section())

# ============================================================
# Idols [[4500]] — Event Leagues Only
# ============================================================
blocks.append(generate_idols_section())

# ============================================================
# Endgame Flasks [[2500]] — Overquality/Utility/Life-Mana
# ============================================================
blocks.append(generate_endgame_flasks_section())

# ============================================================
# RestEx 안전망 — 카테고리별 미분류 아이템 캐치올
# ============================================================
blocks.append("# [AURORA] RestEx Safety Net — 미분류 아이템 경고")
restex_categories = [
    ("Unique restex", ['Rarity Unique']),
    ("Currency restex", ['Class "Currency" "Stackable Currency"']),
    ("Divination restex", ['Class "Divination Cards"']),
    ("Gem restex", ['Class "Skill Gems" "Support Gems"']),
    ("Map restex", ['Class "Maps"']),
    ("Fragment restex", ['Class "Map Fragments" "Misc Map Items"']),
]
for label, conds in restex_categories:
    blocks.append(make_restex_block(label, conds))

# ============================================================
# Aurora 오버레이 생성 + Sanavi 베이스 병합
# ============================================================
# Strictness 는 STRICTNESS env var 로 오버라이드 가능 (기본 3_Strict)
from filter_merge import find_sanavi_filter, apply_overlay_to_file, POE_FILTER_DIR
from pathlib import Path

strictness = int(os.environ.get("STRICTNESS", "3"))
sanavi_base = find_sanavi_filter(strictness)
if not sanavi_base:
    raise RuntimeError(
        f"Sanavi strictness={strictness} 필터를 찾을 수 없습니다. "
        f"설치 경로: {POE_FILTER_DIR}"
    )

overlay_header = (
    "#" + "=" * 110 + "\n"
    f"# === PathcraftAI Aurora Overlay MODE={MODE.upper()} (merged onto {sanavi_base.name}) ===\n"
    "#" + "=" * 110 + "\n"
)
# 엄격도: STRICTNESS 환경변수 (0=Regular, 1=Strict, 2=VeryStrict, 3=Uber, 4=Uber+)
strictness_level = int(os.environ.get("STRICTNESS", "0"))
strictness_names = {0: "Regular", 1: "Strict", 2: "VeryStrict", 3: "UberStrict", 4: "UberPlus"}
strictness_name = strictness_names.get(strictness_level, f"S{strictness_level}")

raw_overlay = overlay_header + "\n".join(blocks) + "\n"
overlay_content = apply_strictness(raw_overlay, strictness_level)

suffix = f"_{strictness_name}" if strictness_level > 0 else ""
output_path = POE_FILTER_DIR / f"PathcraftAI_Aurora_{MODE.upper()}{suffix}.filter"
apply_overlay_to_file(sanavi_base, overlay_content, output_path)

# 아래 코드가 filter_content 를 참조하므로 유지
with open(output_path, "r", encoding="utf-8") as f:
    filter_content = f.read()

size = os.path.getsize(output_path)
line_count = filter_content.count('\n')

# Show 블록 개수 집계
import re
show_blocks = re.findall(r'Show[^\n]*\n(?:\t[^\n]*\n?)+', filter_content)
print(f"Generated: {size:,} bytes / {line_count} lines / {len(show_blocks)} Show blocks")

# 카테고리별 블록 수
from collections import Counter
cat_counts = Counter()
for b in show_blocks:
    m = re.search(r'# PathcraftAI: (\w+)', b)
    if m:
        cat_counts[m.group(1)] += 1
print(f"Blocks per category: {dict(cat_counts)}")

# 각 카테고리 P-tier 검증
print("\n=== Sanavi 데이터 → PathcraftAI P-tier 매핑 검증 ===")
for cat, mapping in TIER_MAPPING.items():
    print(f"\n{cat}:")
    for sanavi_tier, p_tier, label in mapping:
        total = len(sanavi.get(cat, {}).get(sanavi_tier, []))
        used = min(total, 30)
        print(f"  {sanavi_tier:25} → {p_tier:15} [{used}/{total}]")
