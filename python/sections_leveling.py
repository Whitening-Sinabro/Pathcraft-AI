# -*- coding: utf-8 -*-
"""PathcraftAI Aurora Glow — 레벨링 + 맵 + 기타 섹션.

레벨링 플라스크, 레벨링 레어/노말, 맵, 유사 맵, 스카랍,
아이돌, 엔드게임 플라스크, 최종 안전망 섹션.
"""

from sections_core import (
    make_show_block, make_hide_block, make_restex_block, _q,
)


# ---------------------------------------------------------------------------
# Leveling Flasks [[4900-5100]]
# ---------------------------------------------------------------------------

LIFE_FLASKS = [
    ("Small Life Flask",       9),
    ("Medium Life Flask",     12),
    ("Large Life Flask",      18),
    ("Greater Life Flask",    24),
    ("Grand Life Flask",      30),
    ("Giant Life Flask",      36),
    ("Colossal Life Flask",   42),
    ("Sacred Life Flask",     48),
    ("Hallowed Life Flask",   52),
    ("Sanctified Life Flask", 58),
    ("Divine Life Flask",     65),
    ("Eternal Life Flask",    68),
]

MANA_FLASKS = [
    ("Small Mana Flask",       9),
    ("Medium Mana Flask",     12),
    ("Large Mana Flask",      18),
    ("Greater Mana Flask",    24),
    ("Grand Mana Flask",      30),
    ("Giant Mana Flask",      36),
    ("Colossal Mana Flask",   42),
    ("Sacred Mana Flask",     48),
    ("Hallowed Mana Flask",   52),
    ("Sanctified Mana Flask", 58),
    ("Divine Mana Flask",     65),
    ("Eternal Mana Flask",    68),
]

HYBRID_FLASKS = [
    ("Small Hybrid Flask",     15),
    ("Medium Hybrid Flask",    25),
    ("Large Hybrid Flask",     35),
    ("Colossal Hybrid Flask",  45),
    ("Sacred Hybrid Flask",    55),
    ("Hallowed Hybrid Flask",  65),
]

UTILITY_FLASKS = [
    "Quicksilver Flask",
    "Granite Flask",
    "Jade Flask",
    "Quartz Flask",
    "Stibnite Flask",
    "Sulphur Flask",
    "Silver Flask",
    "Bismuth Flask",
    "Amethyst Flask",
    "Ruby Flask",
    "Sapphire Flask",
    "Topaz Flask",
    "Aquamarine Flask",
    "Basalt Flask",
    "Diamond Flask",
    "Corundum Flask",
    "Gold Flask",
]


def generate_leveling_flasks_section() -> str:
    """레벨링 플라스크 섹션 (AreaLevel 기반 단계적 숨기기 + 유틸리티)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Leveling Flasks [[4900-5100]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── Utility flasks: Quicksilver special ──
    blocks.append(make_show_block(
        comment="Quicksilver Flask (always show leveling)",
        conditions=[
            'Class "Utility Flasks"',
            'BaseType == "Quicksilver Flask"',
            'AreaLevel <= 67',
        ],
        category="base",
        tier="P3_USEFUL",
        is_build_target=False,
    ))

    # ── Utility flasks: all ──
    utility_str = " ".join(f'"{n}"' for n in UTILITY_FLASKS)
    blocks.append(make_show_block(
        comment=f"Utility Flasks ({len(UTILITY_FLASKS)} types)",
        conditions=[
            'Class "Utility Flasks"',
            f'BaseType == {utility_str}',
        ],
        category="base",
        tier="P4_SUPPORT",
        is_build_target=False,
    ))

    # ── Life flasks: Show current tier, Hide outdated ──
    blocks.append("# Life Flasks — progressive show/hide by AreaLevel")
    for flask_name, cutoff in reversed(LIFE_FLASKS):
        blocks.append(make_show_block(
            comment=f"Life Flask: {flask_name} (until AL {cutoff})",
            conditions=[
                'Class "Life Flasks"',
                f'BaseType == "{flask_name}"',
                f'AreaLevel <= {cutoff}',
            ],
            category="base",
            tier="P5_MINOR",
            is_build_target=False,
        ))

    for flask_name, cutoff in LIFE_FLASKS:
        blocks.append(make_hide_block(
            comment=f"Hide outdated {flask_name} (AL > {cutoff})",
            conditions=[
                'Class "Life Flasks"',
                f'BaseType == "{flask_name}"',
                f'AreaLevel >= {cutoff + 1}',
            ],
        ))

    # ── Mana flasks: same pattern ──
    blocks.append("# Mana Flasks — progressive show/hide by AreaLevel")
    for flask_name, cutoff in reversed(MANA_FLASKS):
        blocks.append(make_show_block(
            comment=f"Mana Flask: {flask_name} (until AL {cutoff})",
            conditions=[
                'Class "Mana Flasks"',
                f'BaseType == "{flask_name}"',
                f'AreaLevel <= {cutoff}',
            ],
            category="base",
            tier="P5_MINOR",
            is_build_target=False,
        ))

    for flask_name, cutoff in MANA_FLASKS:
        blocks.append(make_hide_block(
            comment=f"Hide outdated {flask_name} (AL > {cutoff})",
            conditions=[
                'Class "Mana Flasks"',
                f'BaseType == "{flask_name}"',
                f'AreaLevel >= {cutoff + 1}',
            ],
        ))

    # ── Hybrid flasks ──
    blocks.append("# Hybrid Flasks — progressive show/hide by AreaLevel")
    for flask_name, cutoff in reversed(HYBRID_FLASKS):
        blocks.append(make_show_block(
            comment=f"Hybrid Flask: {flask_name} (until AL {cutoff})",
            conditions=[
                'Class "Hybrid Flasks"',
                f'BaseType == "{flask_name}"',
                f'AreaLevel <= {cutoff}',
            ],
            category="base",
            tier="P6_LOW",
            is_build_target=False,
        ))

    for flask_name, cutoff in HYBRID_FLASKS:
        blocks.append(make_hide_block(
            comment=f"Hide outdated {flask_name} (AL > {cutoff})",
            conditions=[
                'Class "Hybrid Flasks"',
                f'BaseType == "{flask_name}"',
                f'AreaLevel >= {cutoff + 1}',
            ],
        ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Leveling Rares — Cobalt [[5200]]
# ---------------------------------------------------------------------------

WEAPON_TIERS: list[tuple[int | None, int]] = [
    (None, 25), (10, 30), (15, 35), (20, 45),
    (25, 55), (30, 60), (35, 65), (40, 70),
]

ALL_GEAR_CLS = (
    '"Amulets" "Belts" "Body Armours" "Boots" "Bows" "Claws" "Daggers"'
    ' "Gloves" "Helmets" "One Hand Axes" "One Hand Maces" "One Hand Swords"'
    ' "Quivers" "Rings" "Rune Daggers" "Sceptres" "Shields" "Staves"'
    ' "Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces"'
    ' "Two Hand Swords" "Wands" "Warstaves"'
)


def generate_leveling_rares_section() -> str:
    """레벨링 레어 아이템. Cobalt [[5200]]."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Leveling Rares\n"
        "#" + "=" * 79 + "\n"
    )

    # 4링크 레어
    blocks.append(make_show_block(
        comment="Leveling 4-Link Rare",
        conditions=['LinkedSockets >= 4', 'ItemLevel <= 67', 'Rarity Rare'],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))

    # 이동속도 부츠
    blocks.append(make_show_block(
        comment="Leveling MS Boots High",
        conditions=['ItemLevel <= 67', 'Rarity Normal Magic Rare',
                    'Class == "Boots"',
                    "HasExplicitMod \"Cheetah's\" \"Gazelle's\" \"Stallion's\""],
        category="base", tier="P3_USEFUL",
    ))
    blocks.append(make_show_block(
        comment="Leveling MS Boots Low (AL<=40)",
        conditions=['ItemLevel <= 67', 'Rarity Normal Magic Rare',
                    'Class == "Boots"',
                    "HasExplicitMod \"Sprinter's\" \"Runner's\"",
                    'AreaLevel <= 40'],
        category="base", tier="P3_USEFUL",
    ))

    # 베일드 레벨링
    blocks.append(make_show_block(
        comment="Leveling Veiled",
        conditions=['Identified True', 'ItemLevel <= 67',
                    'Rarity Normal Magic Rare', 'HasExplicitMod "Veil"'],
        category="base", tier="P4_SUPPORT",
    ))

    # 미니언 장비
    blocks.append(make_show_block(
        comment="Leveling Minion Gear",
        conditions=['Rarity Rare',
                    'BaseType == "Bone Ring" "Bone Spirit Shield"'
                    ' "Calling Wand" "Convening Wand"'
                    ' "Fossilised Spirit Shield" "Ivory Spirit Shield"'],
        category="jewel", tier="P4_SUPPORT", is_build_target=False,
    ))

    # 악세서리
    blocks.append(make_show_block(
        comment="Leveling Rare Jewellery",
        conditions=['Rarity Rare', 'Class == "Amulets" "Belts" "Rings"'],
        category="jewel", tier="P3_USEFUL", is_build_target=False,
    ))

    # 방어구
    blocks.append(make_show_block(
        comment="Leveling Rare Boots",
        conditions=['Rarity Rare', 'Class == "Boots"'],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Rare Armor (Gloves/Helmets)",
        conditions=['Rarity Rare', 'Class == "Gloves" "Helmets"'],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Rare Body/Shields",
        conditions=['Rarity Rare',
                    'Class == "Body Armours" "Shields"'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Rare Quivers",
        conditions=['Rarity Rare', 'Class == "Quivers"'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    # 캐스터 무기
    blocks.append(make_show_block(
        comment="Leveling Rare Caster Weapons",
        conditions=['Rarity Rare',
                    'Class == "Rune Daggers" "Sceptres" "Staves" "Wands"'],
        category="gem", tier="P5_MINOR", is_build_target=False,
    ))

    # 궁수 8단계
    for i, (drop_lvl, area_max) in enumerate(WEAPON_TIERS):
        conds: list[str] = []
        if drop_lvl is not None:
            conds.append(f'DropLevel >= {drop_lvl}')
        conds.extend(['Rarity Rare', 'Class == "Bows"',
                       f'AreaLevel <= {area_max}'])
        blocks.append(make_show_block(
            comment=f"Leveling Bow L{i+1} (AL<={area_max})",
            conditions=conds,
            category="base", tier="P5_MINOR", is_build_target=False,
        ))

    # 근접 2H 8단계
    m2h = '"Two Hand Axes" "Two Hand Maces" "Two Hand Swords" "Warstaves"'
    for i, (drop_lvl, area_max) in enumerate(WEAPON_TIERS):
        conds = []
        if drop_lvl is not None:
            conds.append(f'DropLevel >= {drop_lvl}')
        conds.extend(['Rarity Rare', f'Class == {m2h}',
                       f'AreaLevel <= {area_max}'])
        blocks.append(make_show_block(
            comment=f"Leveling 2H L{i+1} (AL<={area_max})",
            conditions=conds,
            category="base", tier="P5_MINOR", is_build_target=False,
        ))

    # 근접 1H 8단계
    m1h = ('"Claws" "Daggers" "One Hand Axes" "One Hand Maces"'
           ' "One Hand Swords" "Thrusting One Hand Swords"')
    for i, (drop_lvl, area_max) in enumerate(WEAPON_TIERS):
        conds = []
        if drop_lvl is not None:
            conds.append(f'DropLevel >= {drop_lvl}')
        conds.extend(['Rarity Rare', f'Class == {m1h}',
                       f'AreaLevel <= {area_max}'])
        blocks.append(make_show_block(
            comment=f"Leveling 1H L{i+1} (AL<={area_max})",
            conditions=conds,
            category="base", tier="P5_MINOR", is_build_target=False,
        ))

    # 아웃레벨 레어
    for max_ilvl, min_area in [(68, 42), (44, 24), (26, 16), (18, 1)]:
        blocks.append(make_show_block(
            comment=f"Outdated Rare (ilvl<={max_ilvl} AL>={min_area})",
            conditions=[f'ItemLevel <= {max_ilvl}', 'Rarity Rare',
                        f'Class == {ALL_GEAR_CLS}',
                        f'AreaLevel >= {min_area}'],
            category="base", tier="P6_LOW", is_build_target=False,
        ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Leveling Magic/Normal — Cobalt [[5300]]
# ---------------------------------------------------------------------------

# 무기 진행 15단계 슬라이딩 윈도우 (DropLevel/ItemLevel)
WEAPON_PROG_TIERS: list[tuple[int, int]] = [
    (5, 9), (11, 15), (15, 18), (18, 22), (22, 26), (26, 30), (30, 34),
    (34, 40), (40, 44), (44, 48), (48, 52), (52, 56), (56, 60), (60, 64),
    (64, 68),
]

ALL_WEAPON_CLS = (
    '"Bows" "Claws" "Daggers" "One Hand Axes" "One Hand Maces"'
    ' "One Hand Swords" "Thrusting One Hand Swords" "Two Hand Axes"'
    ' "Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"'
)


def generate_leveling_normals_section() -> str:
    """레벨링 매직/노말 아이템. Cobalt [[5300]]."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Leveling Normal & Magic\n"
        "#" + "=" * 79 + "\n"
    )

    # [5301] 4링크 노말/매직
    blocks.append(make_show_block(
        comment="Leveling 4-Link Normal/Magic",
        conditions=['LinkedSockets >= 4', 'Rarity Normal Magic'],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))

    # RGB 레시피 (소형)
    blocks.append(make_show_block(
        comment="Leveling RGB 2x2",
        conditions=['Width 2', 'Height 2', 'Rarity Normal Magic',
                    'SocketGroup "RGB"'],
        category="base", tier="P6_LOW", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling RGB 1xN",
        conditions=['Width 1', 'Height <= 4', 'Rarity Normal Magic',
                    'SocketGroup "RGB"'],
        category="base", tier="P6_LOW", is_build_target=False,
    ))

    # 3링크
    blocks.append(make_show_block(
        comment="Leveling 3-Link Early (AL<=16)",
        conditions=['LinkedSockets >= 3', 'Rarity Normal Magic',
                    'AreaLevel <= 16'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling 3-Link (AL<=28)",
        conditions=['LinkedSockets >= 3', 'Rarity Normal Magic',
                    'AreaLevel <= 28'],
        category="base", tier="P6_LOW", is_build_target=False,
    ))

    # Act1 특수 아이템
    blocks.append(make_show_block(
        comment="Leveling Act1 Caster Wands (3S Magic)",
        conditions=['Sockets >= 3', 'Rarity Magic',
                    'Class == "Sceptres" "Wands"', 'AreaLevel <= 16'],
        category="gem", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Act1 Craft Rings",
        conditions=['Rarity Normal Magic',
                    'BaseType == "Iron Ring" "Ruby Ring" "Sapphire Ring"'
                    ' "Topaz Ring" "Two-Stone Ring"',
                    'AreaLevel <= 16'],
        category="jewel", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Act1 Jewellery",
        conditions=['Rarity Normal Magic',
                    'BaseType == "Amber Amulet" "Chain Belt" "Coral Ring"'
                    ' "Jade Amulet" "Lapis Amulet" "Leather Belt"',
                    'AreaLevel <= 16'],
        category="jewel", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Act1 Boots",
        conditions=['Rarity Magic', 'Class == "Boots"', 'AreaLevel <= 16'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Act1 Quivers",
        conditions=['Rarity Normal Magic', 'Class == "Quivers"',
                    'AreaLevel <= 16'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    # Act2 크래프팅
    blocks.append(make_show_block(
        comment="Leveling Act2 Craft Rings",
        conditions=['Rarity Normal Magic',
                    'BaseType == "Iron Ring" "Ruby Ring" "Sapphire Ring"'
                    ' "Topaz Ring" "Two-Stone Ring"',
                    'AreaLevel >= 16', 'AreaLevel <= 24'],
        category="jewel", tier="P6_LOW", is_build_target=False,
    ))

    # 후반 액트 유용 아이템
    blocks.append(make_show_block(
        comment="Leveling Phys Quivers",
        conditions=['Rarity Normal Magic',
                    'BaseType == "Broadhead Arrow Quiver"'
                    ' "Heavy Arrow Quiver"'],
        category="base", tier="P6_LOW", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Fire Resist (Ruby Ring)",
        conditions=['Rarity Normal Magic', 'BaseType == "Ruby Ring"',
                    'AreaLevel >= 24', 'AreaLevel <= 51'],
        category="jewel", tier="P6_LOW", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Crafting Bases",
        conditions=['Rarity Normal Magic',
                    'BaseType == "Leather Belt" "Onyx Amulet"'
                    ' "Prismatic Ring" "Two-Stone Ring"',
                    'AreaLevel >= 24'],
        category="jewel", tier="P6_LOW", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling Minion Wands",
        conditions=['Rarity Normal Magic',
                    'BaseType == "Bone Ring" "Calling Wand"'
                    ' "Convening Wand" "Convoking Wand"'],
        category="jewel", tier="P6_LOW", is_build_target=False,
    ))

    # [5302] 초반 노말
    blocks.append(make_show_block(
        comment="Leveling Normal Body (AL 2-9)",
        conditions=['Rarity Normal', 'Class == "Body Armours"',
                    'AreaLevel >= 2', 'AreaLevel <= 9'],
        category="base", tier="P6_LOW", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling 3-Socket Gear (AL<=9)",
        conditions=['Sockets >= 3', 'Rarity Normal Magic',
                    'Class == "Boots" "Gloves" "Helmets" "Sceptres"'
                    ' "Shields" "Wands"',
                    'AreaLevel <= 9'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Leveling First Areas (AL<=4)",
        conditions=['Rarity Normal', 'AreaLevel <= 4'],
        category="base", tier="P6_LOW", is_build_target=False,
    ))

    # [5303] 무기 진행 15단계
    for i, (drop_min, ilvl_max) in enumerate(WEAPON_PROG_TIERS):
        blocks.append(make_show_block(
            comment=f"Weapon Prog R{i+1:02d} (DL>={drop_min} IL<={ilvl_max})",
            conditions=[
                'Sockets >= 3',
                f'ItemLevel <= {ilvl_max}',
                f'DropLevel >= {drop_min}',
                'Rarity Normal',
                f'Class == {ALL_WEAPON_CLS}',
            ],
            category="base", tier="P6_LOW", is_build_target=False,
        ))

    # [5304] 완드 진행
    for base, area_max in [("Somatic Wand", 24), ("Blasting Wand", 50),
                           ("Kinetic Wand", 67)]:
        blocks.append(make_show_block(
            comment=f"Wand Prog {base} (AL<={area_max})",
            conditions=['Rarity Normal', 'Class == "Wands"',
                        f'BaseType == "{base}"', f'AreaLevel <= {area_max}'],
            category="base", tier="P6_LOW", is_build_target=False,
        ))

    # [5305] 매직 숨김
    blocks.append(make_hide_block(
        "Hide Large Magic (AL>=16)",
        ['Width >= 2', 'Height >= 3', 'Rarity Magic',
         f'Class == {ALL_GEAR_CLS}', 'AreaLevel >= 16'],
    ))
    blocks.append(make_hide_block(
        "Hide Medium Magic (AL>=24)",
        ['Height > 1', 'Rarity Magic',
         f'Class == {ALL_GEAR_CLS}', 'AreaLevel >= 24'],
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Maps Section [[3200-3300]]
# ---------------------------------------------------------------------------

SPECIAL_MAP_BASES = [
    "Vaal Temple Map",
]


def generate_maps_section() -> str:
    """맵 섹션 (특수 맵 + 티어별 진행)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Maps [[3200-3300]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── P1 Keystone: Unique Maps ──
    blocks.append(make_show_block(
        comment="Unique Maps",
        conditions=[
            'Class "Maps"',
            'Rarity Unique',
        ],
        category="fragment",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── P1 Keystone: Uber Blighted Maps ──
    blocks.append(make_show_block(
        comment="Uber Blighted Maps",
        conditions=[
            'Class "Maps"',
            'BlightedMap True',
            'UberBlightedMap True',
        ],
        category="fragment",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── P2: Blighted Maps ──
    blocks.append(make_show_block(
        comment="Blighted Maps",
        conditions=[
            'Class "Maps"',
            'BlightedMap True',
        ],
        category="fragment",
        tier="P2_CORE",
    ))

    # ── P1: Vaal Temple / special bases ──
    special_str = " ".join(f'"{n}"' for n in SPECIAL_MAP_BASES)
    blocks.append(make_show_block(
        comment="Special Maps (Vaal Temple)",
        conditions=[
            'Class "Maps"',
            f'BaseType == {special_str}',
        ],
        category="fragment",
        tier="P1_KEYSTONE",
    ))

    # ── Map tier progression ──
    blocks.append(make_show_block(
        comment="Maps T16-T14",
        conditions=[
            'Class "Maps"',
            'MapTier >= 14',
        ],
        category="fragment",
        tier="P1_KEYSTONE",
    ))

    blocks.append(make_show_block(
        comment="Maps T13-T11",
        conditions=[
            'Class "Maps"',
            'MapTier >= 11',
        ],
        category="fragment",
        tier="P2_CORE",
    ))

    blocks.append(make_show_block(
        comment="Maps T10-T6",
        conditions=[
            'Class "Maps"',
            'MapTier >= 6',
        ],
        category="fragment",
        tier="P3_USEFUL",
    ))

    blocks.append(make_show_block(
        comment="Maps T5-T1",
        conditions=[
            'Class "Maps"',
            'MapTier >= 1',
        ],
        category="fragment",
        tier="P4_SUPPORT",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Pseudo Maps [[3400]]
# ---------------------------------------------------------------------------

def generate_pseudo_maps_section() -> str:
    """유사 맵 섹션 (Expedition Logbook, Heist, Sanctum)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Pseudo Maps [[3400]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── P1: Expedition Logbook ──
    blocks.append(make_show_block(
        comment="Expedition Logbook",
        conditions=[
            'Class "Expedition Logbooks"',
        ],
        category="fragment",
        tier="P1_KEYSTONE",
    ))

    # ── P2: Heist Blueprints ──
    blocks.append(make_show_block(
        comment="Heist Blueprint",
        conditions=[
            'Class "Blueprints"',
        ],
        category="fragment",
        tier="P2_CORE",
    ))

    # ── P3: Heist Contracts ──
    blocks.append(make_show_block(
        comment="Heist Contract",
        conditions=[
            'Class "Contracts"',
        ],
        category="fragment",
        tier="P3_USEFUL",
    ))

    # ── P3: Sanctum Research ──
    blocks.append(make_show_block(
        comment="Sanctum Research (Forbidden Sanctum)",
        conditions=[
            'Class == "Sanctum Research"',
        ],
        category="fragment",
        tier="P3_USEFUL",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Scarab 개별 티어 — Cobalt [[3500]] scarabs
# ---------------------------------------------------------------------------

SCARAB_T1 = [
    "Allflame Ember of the Ethereal", "Allflame Ember of the Gilded",
    "Ambush Scarab of Containment", "Horned Scarab of Awakening",
    "Horned Scarab of Bloodlines", "Horned Scarab of Pandemonium",
    "Horned Scarab of Preservation",
]

SCARAB_T2 = [
    "Allflame Ember of Kulemak", "Anarchy Scarab of the Exceptional",
    "Blight Scarab of Invigoration", "Cartography Scarab of Risk",
    "Divination Scarab of Pilfering", "Domination Scarab of Terrors",
    "Essence Scarab of Calcification", "Harvest Scarab of Cornucopia",
    "Horned Scarab of Glittering", "Kalguuran Scarab of Enriching",
    "The Black Barya", "Ultimatum Scarab of Catalysing",
]

SCARAB_T5 = [
    "Abyss Scarab of Profound Depth", "Allflame Ember of Resplendence",
    "Allflame Ember of the Wildwood", "Delirium Scarab of Mania",
    "Scarab of Radiant Storms", "Torment Scarab",
]

SCARAB_T6 = [
    "Allflame Ember of Toads", "Betrayal Scarab of the Allflame",
]


def generate_scarab_tiers_section() -> str:
    """Scarab 개별 티어. Cobalt [[3500]]."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Scarab Tiers\n"
        "#" + "=" * 79 + "\n"
    )

    cls = 'Class "Map Fragments" "Misc Map Items"'

    # T1
    blocks.append(make_show_block(
        comment=f"Scarab T1 ({len(SCARAB_T1)} types)",
        conditions=[cls, f'BaseType == {_q(SCARAB_T1)}'],
        category="fragment", tier="P1_KEYSTONE", keystone=True,
    ))
    # T2
    blocks.append(make_show_block(
        comment=f"Scarab T2 ({len(SCARAB_T2)} types)",
        conditions=[cls, f'BaseType == {_q(SCARAB_T2)}'],
        category="fragment", tier="P2_CORE",
    ))
    # T3 stacked >= 3 (broad list — use partial match)
    blocks.append(make_show_block(
        comment="Scarab T3 Stacked (>=3)",
        conditions=['StackSize >= 3', cls, 'BaseType "Scarab" "Allflame"'],
        category="fragment", tier="P3_USEFUL",
    ))
    # T5
    blocks.append(make_show_block(
        comment=f"Scarab T5 ({len(SCARAB_T5)} types)",
        conditions=[cls, f'BaseType == {_q(SCARAB_T5)}'],
        category="fragment", tier="P5_MINOR", is_build_target=False,
    ))
    # T6
    blocks.append(make_show_block(
        comment=f"Scarab T6 ({len(SCARAB_T6)} types)",
        conditions=[cls, f'BaseType == {_q(SCARAB_T6)}'],
        category="fragment", tier="P6_LOW", is_build_target=False,
    ))
    # RestEx
    blocks.append(make_restex_block(
        "Scarab restex", [cls, 'BaseType "Scarab"'],
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Idols [[4500]] — Event Leagues Only
# ---------------------------------------------------------------------------

IDOL_TYPES = [
    "Minor Idol",     # 1x3
    "Kamasan Idol",   # 1x2
    "Totemic Idol",   # 1x3
    "Noble Idol",     # 2x1
    "Burial Idol",    # 3x1
    "Conqueror Idol", # 2x2
]


def generate_idols_section() -> str:
    """Cobalt [[4500]] Idols (Event Leagues Only)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Idols [[4500]] (Event Leagues)\n"
        "#" + "=" * 79 + "\n"
    )

    for idol in IDOL_TYPES:
        rare_tier = "P1_KEYSTONE" if idol == "Conqueror Idol" else "P3_USEFUL"
        blocks.append(make_show_block(
            comment=f"{idol} Rare",
            conditions=['Rarity Rare', f'BaseType == "{idol}"'],
            category="jewel", tier=rare_tier, is_build_target=False,
        ))
        blocks.append(make_show_block(
            comment=f"{idol} Magic",
            conditions=['Rarity Magic', f'BaseType == "{idol}"'],
            category="jewel", tier="P5_MINOR", is_build_target=False,
        ))

    # Normal idols catch-all
    blocks.append(make_show_block(
        comment="Idol Normal (catch-all)",
        conditions=['Rarity Normal', 'Class == "Idols"'],
        category="jewel", tier="P6_LOW", is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Endgame Flasks & Tinctures [[2500]]
# ---------------------------------------------------------------------------

ENDGAME_UTILITY_FLASKS = [
    "Amethyst Flask", "Basalt Flask", "Bismuth Flask",
    "Diamond Flask", "Gold Flask", "Granite Flask",
    "Iron Flask", "Jade Flask", "Quartz Flask",
    "Quicksilver Flask", "Ruby Flask", "Sapphire Flask",
    "Silver Flask", "Stibnite Flask", "Sulphur Flask",
    "Topaz Flask",
]

ENDGAME_LIFE_MANA_FLASKS = [
    "Divine Life Flask", "Divine Mana Flask",
    "Eternal Life Flask", "Eternal Mana Flask",
    "Hallowed Hybrid Flask",
]


def generate_endgame_flasks_section() -> str:
    """Cobalt [[2500]] Endgame Flasks & Tinctures."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Endgame Flasks [[2500]]\n"
        "#" + "=" * 79 + "\n"
    )

    rarity_nm = 'Rarity Normal Magic'
    area68 = 'AreaLevel >= 68'
    uncorr = 'Mirrored False'
    uncorr2 = 'Corrupted False'

    # --- Overquality Tinctures ---
    blocks.append(make_show_block(
        comment="Tincture Overquality Q26+ ilvl82+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 26', 'ItemLevel >= 82',
            rarity_nm, 'Class == "Tinctures"', area68,
        ],
        category="base", tier="P1_KEYSTONE", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Tincture Overquality Q21+ ilvl82+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 21', 'ItemLevel >= 82',
            rarity_nm, 'Class == "Tinctures"', area68,
        ],
        category="base", tier="P2_CORE", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Tincture ilvl85+",
        conditions=[
            'ItemLevel >= 85', rarity_nm,
            'Class == "Tinctures"', area68,
        ],
        category="base", tier="P3_USEFUL", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Tincture ilvl82+",
        conditions=[
            'ItemLevel >= 82', rarity_nm,
            'Class == "Tinctures"', area68,
        ],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Tincture any",
        conditions=[rarity_nm, 'Class == "Tinctures"', area68],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    # --- Overquality Corrupted Utility Flasks ---
    blocks.append(make_show_block(
        comment="Utility Flask Overqual Corrupted Q30+",
        conditions=[
            'Corrupted True', 'Quality >= 30', 'Rarity Magic',
            'Class == "Utility Flasks"',
            f'BaseType == {_q(ENDGAME_UTILITY_FLASKS)}',
            area68,
        ],
        category="base", tier="P3_USEFUL", is_build_target=False,
    ))

    # --- Overquality Utility Flasks ---
    blocks.append(make_show_block(
        comment="Utility Flask Overqual Q26+ ilvl84+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 26', 'ItemLevel >= 84',
            rarity_nm, 'Class == "Utility Flasks"', area68,
        ],
        category="base", tier="P1_KEYSTONE", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Utility Flask Overqual Q21+ ilvl82+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 21', 'ItemLevel >= 82',
            rarity_nm, 'Class == "Utility Flasks"',
            f'BaseType == {_q(ENDGAME_UTILITY_FLASKS)}',
            area68,
        ],
        category="base", tier="P2_CORE", is_build_target=False,
    ))

    # --- Overquality Life/Mana Flasks ---
    blocks.append(make_show_block(
        comment="Life/Mana Flask Overqual Q30+ ilvl82+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 30', 'ItemLevel >= 82',
            rarity_nm,
            f'BaseType == {_q(ENDGAME_LIFE_MANA_FLASKS)}',
            area68,
        ],
        category="base", tier="P1_KEYSTONE", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Life/Mana Flask Overqual Q21+ ilvl82+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 21', 'ItemLevel >= 82',
            rarity_nm,
            f'BaseType == {_q(ENDGAME_LIFE_MANA_FLASKS)}',
            area68,
        ],
        category="base", tier="P2_CORE", is_build_target=False,
    ))

    # --- Utility Flasks by ilvl ---
    blocks.append(make_show_block(
        comment="Utility Flask ilvl85+",
        conditions=[
            uncorr, uncorr2, 'ItemLevel >= 85',
            rarity_nm, 'Class == "Utility Flasks"',
            f'BaseType == {_q(ENDGAME_UTILITY_FLASKS)}',
            area68,
        ],
        category="base", tier="P3_USEFUL", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Utility Flask ilvl84+",
        conditions=[
            uncorr, uncorr2, 'ItemLevel >= 84',
            rarity_nm, 'Class == "Utility Flasks"',
            f'BaseType == {_q(ENDGAME_UTILITY_FLASKS)}',
            area68,
        ],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Utility Flask ilvl82+",
        conditions=[
            uncorr, uncorr2, 'ItemLevel >= 82',
            rarity_nm, 'Class == "Utility Flasks"', area68,
        ],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    # --- Life/Mana Q10+ ilvl82+ ---
    blocks.append(make_show_block(
        comment="Life/Mana Flask Q10+ ilvl82+",
        conditions=[
            uncorr, uncorr2, 'Quality >= 10', 'ItemLevel >= 82',
            rarity_nm,
            'Class == "Life Flasks" "Mana Flasks"',
            f'BaseType == {_q(ENDGAME_LIFE_MANA_FLASKS)}',
            area68,
        ],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    # --- Any Q20+ flask ---
    blocks.append(make_show_block(
        comment="Any Flask Q20+ Normal",
        conditions=[
            'Quality >= 20', 'Rarity Normal',
            'Class == "Hybrid Flasks" "Life Flasks" "Mana Flasks" "Utility Flasks"',
            area68,
        ],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Final Safety Section [[5306-5307]]
# ---------------------------------------------------------------------------

HIDE_GEAR_CLASSES = [
    "Amulets", "Rings", "Belts",
    "Gloves", "Boots", "Body Armours", "Helmets",
    "Shields", "Quivers",
    "Bows", "Claws", "Daggers",
    "One Hand Axes", "One Hand Maces", "One Hand Swords",
    "Sceptres", "Staves", "Warstaves", "Wands",
    "Two Hand Axes", "Two Hand Maces", "Two Hand Swords",
    "Rune Daggers", "Thrusting One Hand Swords",
]


def generate_final_safety_section() -> str:
    """최종 안전망 — 나머지 장비 Hide + 미지 아이템 RestEx."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Final Safety [[5306-5307]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── Hide all remaining gear ──
    classes_str = " ".join(f'"{c}"' for c in HIDE_GEAR_CLASSES)
    blocks.append(make_hide_block(
        comment=f"Hide remaining gear ({len(HIDE_GEAR_CLASSES)} classes)",
        conditions=[
            f'Class {classes_str}',
            'Rarity Normal Magic Rare',
        ],
    ))

    # ── RestEx: anything truly unknown ──
    blocks.append(make_restex_block(
        comment="Unknown items (final safety net)",
        conditions=[],
    ))

    return "\n".join(blocks)
