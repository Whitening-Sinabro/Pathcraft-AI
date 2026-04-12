# -*- coding: utf-8 -*-
"""PathcraftAI Aurora Glow — 장비/기어 관련 섹션.

링크/소켓, 인플루언스, 이국적 베이스, 크래프팅 매트릭스,
ID 모드, 엔드게임 레어, Perfection, Memory Strand,
Heist, Replica/Foulborn, Cluster Jewel 등.
"""

from sections_core import (
    make_show_block, make_hide_block, make_restex_block, _q,
)


# ---------------------------------------------------------------------------
# 6링크 / 5링크 / 6소켓 / 화이트소켓
# ---------------------------------------------------------------------------

SIXLINK_HIGH_BASES = [
    # Cobalt [[0100]] 참조: 48종 고급 방어구/무기 베이스
    "Astral Plate", "Assassin's Garb", "Vaal Regalia", "Zodiac Leather",
    "Sadist Garb", "Carnal Armour", "Saint's Hauberk", "Glorious Plate",
    "Gladiator Plate", "Full Dragonscale", "General's Brigandine",
    "Triumphant Lamellar", "Destiny Leather", "Occultist's Vestment",
    "Lacquered Garb", "Full Wyrmscale", "Saintly Chainmail",
    "Bone Helmet", "Fingerless Silk Gloves", "Gripped Gloves",
    "Spiked Gloves", "Two-Toned Boots", "Sorcerer Boots",
    "Titanium Spirit Shield", "Fossilised Spirit Shield",
    "Ivory Spirit Shield", "Archon Kite Shield",
    "Spine Bow", "Thicket Bow", "Imperial Bow", "Harbinger Bow",
    "Jewelled Foil", "Opal Wand", "Profane Wand", "Void Sceptre",
    "Opal Sceptre", "Samite Helmet", "Hubris Circlet",
    "Eclipse Staff", "Judgement Staff", "Imperial Claw",
    "Ambusher", "Siege Axe", "Vaal Hatchet", "Fleshripper",
    "Exquisite Blade", "Vaal Axe", "Maraketh Bow",
]


def generate_links_sockets_section() -> str:
    """6링크/5링크/6소켓/화이트소켓 섹션.

    Cobalt [[0100]] + [[1400]] 참조:
    - 6L 고급: ilvl >= 75, 비부패/비미러 → P1 Keystone
    - 6L 기타: 전체 → P2
    - 6소켓 화이트: 2H → P1 Keystone
    - 5L 레벨링: AL <= 67 → P3
    - 5L+6소켓: → P4
    - 5L 엔드게임: AL >= 68 → P5
    - 6소켓: H4/H3 → P6
    """
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Links & Sockets\n"
        "#" + "=" * 79 + "\n"
    )

    names_str = " ".join(f'"{n}"' for n in SIXLINK_HIGH_BASES)

    # ── 6L 고급 베이스 (비부패, 비미러, ilvl >= 75) ──
    blocks.append(make_show_block(
        comment=f"6-Link High Base ({len(SIXLINK_HIGH_BASES)} types)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'LinkedSockets 6',
            'ItemLevel >= 75',
            'Rarity Normal Magic Rare',
            f'BaseType == {names_str}',
        ],
        category="links",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── 6L 기타 ──
    blocks.append(make_show_block(
        comment="6-Link any",
        conditions=[
            'LinkedSockets 6',
            'Rarity Normal Magic Rare',
        ],
        category="links",
        tier="P2_CORE",
    ))

    # ── 6소켓 화이트 (양손 무기) ──
    blocks.append(make_show_block(
        comment="6-Socket White (2H weapons)",
        conditions=[
            'Sockets >= 6WWWWWW',
            'Rarity Normal Magic Rare',
            'Class "Bows" "Staves" "Two Hand Axes" "Two Hand Maces"'
            ' "Two Hand Swords" "Warstaves"',
        ],
        category="links",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── 5L 레벨링 (AreaLevel <= 67) ──
    blocks.append(make_show_block(
        comment="5-Link Leveling",
        conditions=[
            'LinkedSockets >= 5',
            'Rarity Normal Magic Rare',
            'AreaLevel <= 67',
        ],
        category="links",
        tier="P3_USEFUL",
    ))

    # ── 5L + 6소켓 (엔드게임) ──
    blocks.append(make_show_block(
        comment="5-Link 6-Socket",
        conditions=[
            'LinkedSockets >= 5',
            'Sockets >= 6',
            'Rarity Normal Magic Rare',
        ],
        category="links",
        tier="P4_SUPPORT",
    ))

    # ── 5L 엔드게임 ──
    blocks.append(make_show_block(
        comment="5-Link Endgame",
        conditions=[
            'LinkedSockets >= 5',
            'Rarity Normal Magic Rare',
            'AreaLevel >= 68',
        ],
        category="links",
        tier="P5_MINOR",
    ))

    # ── 6소켓 Height 4 (Body Armour) ──
    blocks.append(make_show_block(
        comment="6-Socket Height 4",
        conditions=[
            'Sockets >= 6',
            'Height 4',
            'Rarity Normal Magic Rare',
        ],
        category="links",
        tier="P6_LOW",
        is_build_target=False,
    ))

    # ── 6소켓 Height 3 (2H 무기) ──
    blocks.append(make_show_block(
        comment="6-Socket Height 3",
        conditions=[
            'Sockets >= 6',
            'Height 3',
            'Rarity Normal Magic Rare',
        ],
        category="links",
        tier="P6_LOW",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Influenced Bases [[0300-0400]]
# ---------------------------------------------------------------------------

INFLUENCE_TYPES = [
    "Shaper", "Elder", "Crusader", "Hunter", "Redeemer", "Warlord",
]


def generate_influenced_section() -> str:
    """인플루언스 베이스 섹션 (Shaper/Elder/Crusader/Hunter/Redeemer/Warlord + Eldritch)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Influenced Bases [[0300-0400]]\n"
        "#" + "=" * 79 + "\n"
    )

    influence_str = " ".join(f'"{i}"' for i in INFLUENCE_TYPES)

    # ── P1: ilvl >= 86, Rare, any influence ──
    blocks.append(make_show_block(
        comment="Influenced Rare ilvl86+",
        conditions=[
            f'HasInfluence {influence_str}',
            'Rarity Rare',
            'ItemLevel >= 86',
        ],
        category="base",
        tier="P1_KEYSTONE",
    ))

    # ── P2: ilvl >= 84, Rare, any influence ──
    blocks.append(make_show_block(
        comment="Influenced Rare ilvl84+",
        conditions=[
            f'HasInfluence {influence_str}',
            'Rarity Rare',
            'ItemLevel >= 84',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── P3: ilvl >= 80, Rare, any influence ──
    blocks.append(make_show_block(
        comment="Influenced Rare ilvl80+",
        conditions=[
            f'HasInfluence {influence_str}',
            'Rarity Rare',
            'ItemLevel >= 80',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── P3: Searing Exarch / Eater of Worlds implicit ──
    blocks.append(make_show_block(
        comment="Searing Exarch Implicit",
        conditions=[
            'HasSearingExarchImplicit >= 1',
            'Rarity Rare',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    blocks.append(make_show_block(
        comment="Eater of Worlds Implicit",
        conditions=[
            'HasEaterOfWorldsImplicit >= 1',
            'Rarity Rare',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Exotic Bases [[0500]]
# ---------------------------------------------------------------------------

HEIST_BASES = [
    "Fingerless Silk Gloves", "Spiked Gloves", "Gripped Gloves",
    "Bone Helmet", "Two-Toned Boots",
]

RITUAL_BASES = [
    "Astral Plate", "Vaal Regalia", "Assassin's Garb",
    "Saintly Chainmail", "Zodiac Leather",
]

EXPEDITION_BASES = [
    "Runic Hatchet", "Runic Crown", "Runic Gauntlets",
    "Runic Sabatons", "Runic Sollerets",
]

LAKE_RINGS = [
    "Dusk Ring", "Gloam Ring", "Penumbra Ring", "Shadowed Ring", "Tenebrous Ring",
]

SPECIAL_BELTS = [
    "Stygian Vise",
]

EXOTIC_T1_BASES = HEIST_BASES + SPECIAL_BELTS
EXOTIC_T2_BASES = RITUAL_BASES
EXOTIC_T3_BASES = EXPEDITION_BASES + LAKE_RINGS


def generate_exotic_bases_section() -> str:
    """특수 베이스 섹션 (Heist, Ritual, Expedition, Stygian 등)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Exotic Bases [[0500]]\n"
        "#" + "=" * 79 + "\n"
    )

    t1_str = " ".join(f'"{n}"' for n in EXOTIC_T1_BASES)
    blocks.append(make_show_block(
        comment=f"Exotic T1 Base ({len(EXOTIC_T1_BASES)} types)",
        conditions=[
            f'BaseType == {t1_str}',
            'Rarity Normal Magic Rare',
            'ItemLevel >= 82',
        ],
        category="base",
        tier="P1_KEYSTONE",
    ))

    t2_str = " ".join(f'"{n}"' for n in EXOTIC_T2_BASES)
    blocks.append(make_show_block(
        comment=f"Exotic T2 Base ({len(EXOTIC_T2_BASES)} types)",
        conditions=[
            f'BaseType == {t2_str}',
            'Rarity Normal Magic Rare',
            'ItemLevel >= 84',
        ],
        category="base",
        tier="P2_CORE",
    ))

    t3_str = " ".join(f'"{n}"' for n in EXOTIC_T3_BASES)
    blocks.append(make_show_block(
        comment=f"Exotic T3 Base ({len(EXOTIC_T3_BASES)} types)",
        conditions=[
            f'BaseType == {t3_str}',
            'Rarity Normal Magic Rare',
            'ItemLevel >= 80',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Exotic Classes [[1200]]
# ---------------------------------------------------------------------------

def generate_exotic_classes_section() -> str:
    """특수 클래스 섹션 (Voidstones, Trinkets, Fishing, Pieces, Relics)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Exotic Classes [[1200]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── P1 Keystone: Voidstones ──
    blocks.append(make_show_block(
        comment="Voidstones",
        conditions=[
            'Class "Atlas Upgrade Items"',
        ],
        category="unique",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── P1 Keystone: Trinkets ──
    blocks.append(make_show_block(
        comment="Trinkets (Heist)",
        conditions=[
            'Class "Trinkets"',
        ],
        category="unique",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── P1 Keystone: Fishing Rods ──
    blocks.append(make_show_block(
        comment="Fishing Rods",
        conditions=[
            'Class "Fishing Rods"',
        ],
        category="unique",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── P1 Keystone: Pieces (Harbinger items) ──
    blocks.append(make_show_block(
        comment="Pieces (Harbinger)",
        conditions=[
            'Class "Pieces"',
        ],
        category="unique",
        tier="P1_KEYSTONE",
        keystone=True,
    ))

    # ── P2: Relics (Sanctum) Unique ──
    blocks.append(make_show_block(
        comment="Relics (Sanctum) Unique",
        conditions=[
            'Class "Relics"',
            'Rarity Unique',
        ],
        category="unique",
        tier="P2_CORE",
    ))

    # ── P3: Relics (Sanctum) Rare ──
    blocks.append(make_show_block(
        comment="Relics (Sanctum) Rare",
        conditions=[
            'Class "Relics"',
            'Rarity Rare',
        ],
        category="unique",
        tier="P3_USEFUL",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Exotic Variations [[1300]]
# ---------------------------------------------------------------------------

def generate_exotic_variations_section() -> str:
    """특수 변형 섹션 (Synthesised, Fractured, Enchanted, Crucible)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Exotic Variations [[1300]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── AnyEnchantment: P1→P3 by ilvl ──
    blocks.append(make_show_block(
        comment="Enchanted ilvl86+",
        conditions=[
            'AnyEnchantment True',
            'Rarity Rare',
            'ItemLevel >= 86',
        ],
        category="base",
        tier="P1_KEYSTONE",
    ))

    blocks.append(make_show_block(
        comment="Enchanted ilvl80+",
        conditions=[
            'AnyEnchantment True',
            'Rarity Rare',
            'ItemLevel >= 80',
        ],
        category="base",
        tier="P2_CORE",
    ))

    blocks.append(make_show_block(
        comment="Enchanted any",
        conditions=[
            'AnyEnchantment True',
            'Rarity Normal Magic Rare',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── SynthesisedItem: P2→P4 ──
    blocks.append(make_show_block(
        comment="Synthesised ilvl86+",
        conditions=[
            'SynthesisedItem True',
            'Rarity Rare',
            'ItemLevel >= 86',
        ],
        category="base",
        tier="P2_CORE",
    ))

    blocks.append(make_show_block(
        comment="Synthesised ilvl80+",
        conditions=[
            'SynthesisedItem True',
            'Rarity Rare',
            'ItemLevel >= 80',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    blocks.append(make_show_block(
        comment="Synthesised any Rare",
        conditions=[
            'SynthesisedItem True',
            'Rarity Rare',
        ],
        category="base",
        tier="P4_SUPPORT",
    ))

    # ── FracturedItem: P2→P4 ──
    blocks.append(make_show_block(
        comment="Fractured ilvl86+",
        conditions=[
            'FracturedItem True',
            'Rarity Rare',
            'ItemLevel >= 86',
        ],
        category="base",
        tier="P2_CORE",
    ))

    blocks.append(make_show_block(
        comment="Fractured ilvl80+",
        conditions=[
            'FracturedItem True',
            'Rarity Rare',
            'ItemLevel >= 80',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    blocks.append(make_show_block(
        comment="Fractured any Rare",
        conditions=[
            'FracturedItem True',
            'Rarity Rare',
        ],
        category="base",
        tier="P4_SUPPORT",
    ))

    # ── HasCruciblePassiveTree: P4 ──
    blocks.append(make_show_block(
        comment="Crucible Passive Tree",
        conditions=[
            'HasCruciblePassiveTree True',
        ],
        category="base",
        tier="P4_SUPPORT",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Crafting Matrix [[2300]]
# ---------------------------------------------------------------------------

CRAFTING_T1_BASES = [
    "Crystal Belt", "Stygian Vise", "Opal Ring", "Vermillion Ring",
    "Steel Ring", "Bone Helmet", "Fingerless Silk Gloves",
    "Spiked Gloves", "Gripped Gloves", "Two-Toned Boots",
    "Vaal Regalia", "Astral Plate", "Assassin's Garb",
    "Hubris Circlet", "Sorcerer Boots", "Titanium Spirit Shield",
    "Fossilised Spirit Shield", "Ivory Spirit Shield",
]

CRAFTING_T2_BASES = [
    "Samite Helmet", "Archon Kite Shield", "Saintly Chainmail",
    "Zodiac Leather", "Sadist Garb", "Carnal Armour",
    "Saint's Hauberk", "Glorious Plate", "Gladiator Plate",
    "Full Dragonscale", "General's Brigandine",
    "Triumphant Lamellar", "Destiny Leather",
    "Occultist's Vestment", "Lacquered Garb",
    "Eclipse Staff", "Judgement Staff",
    "Jewelled Foil", "Opal Wand", "Profane Wand",
    "Void Sceptre", "Opal Sceptre",
    "Spine Bow", "Thicket Bow", "Imperial Bow", "Harbinger Bow",
    "Ambusher", "Imperial Claw", "Siege Axe",
    "Vaal Hatchet", "Fleshripper", "Exquisite Blade",
]


def generate_crafting_matrix_section() -> str:
    """크래프팅 매트릭스 섹션 (비부패/비미러 고ilvl 베이스)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Crafting Matrix [[2300]]\n"
        "#" + "=" * 79 + "\n"
    )

    t1_str = " ".join(f'"{n}"' for n in CRAFTING_T1_BASES)
    t2_str = " ".join(f'"{n}"' for n in CRAFTING_T2_BASES)

    base_conditions = [
        'Mirrored False',
        'Corrupted False',
        'Rarity Normal Magic Rare',
    ]

    # ── T1 bases by ilvl ──
    for ilvl, tier in [(86, "P1_KEYSTONE"), (85, "P2_CORE"),
                       (84, "P3_USEFUL"), (83, "P4_SUPPORT")]:
        blocks.append(make_show_block(
            comment=f"Crafting T1 Base ilvl{ilvl}+ ({len(CRAFTING_T1_BASES)} types)",
            conditions=base_conditions + [
                f'ItemLevel >= {ilvl}',
                f'BaseType == {t1_str}',
            ],
            category="base",
            tier=tier,
        ))

    # ── T2 bases by ilvl ──
    for ilvl, tier in [(86, "P2_CORE"), (85, "P3_USEFUL"),
                       (84, "P4_SUPPORT"), (83, "P5_MINOR")]:
        blocks.append(make_show_block(
            comment=f"Crafting T2 Base ilvl{ilvl}+ ({len(CRAFTING_T2_BASES)} types)",
            conditions=base_conditions + [
                f'ItemLevel >= {ilvl}',
                f'BaseType == {t2_str}',
            ],
            category="base",
            tier=tier,
        ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Chancing Section [[2400]]
# ---------------------------------------------------------------------------

CHANCING_TARGETS = [
    ("Heavy Belt", "Headhunter"),
    ("Leather Belt", "Mageblood"),
    ("Champion Kite Shield", "Aegis Aurora"),
]


def generate_chancing_section() -> str:
    """찬싱 대상 베이스 섹션 (Normal, 비부패/비미러)."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Chancing Targets [[2400]]\n"
        "#" + "=" * 79 + "\n"
    )

    names = [base for base, _ in CHANCING_TARGETS]
    names_str = " ".join(f'"{n}"' for n in names)
    labels = ", ".join(f"{base}→{target}" for base, target in CHANCING_TARGETS)

    blocks.append(make_show_block(
        comment=f"Chancing targets ({labels})",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Rarity Normal',
            f'BaseType == {names_str}',
        ],
        category="unique",
        tier="P5_MINOR",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Group C: HasExplicitMod-based ID Mod Filtering [[0600-0800]]
# ---------------------------------------------------------------------------

# Weapon classes used across multiple ID mod blocks
_WEAPON_CLASSES = (
    '"Bows" "Claws" "Daggers" "One Hand Axes" "One Hand Maces" '
    '"One Hand Swords" "Thrusting One Hand Swords" "Two Hand Axes" '
    '"Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"'
)

_CASTER_WEAPON_CLASSES = '"Rune Daggers" "Sceptres" "Wands"'

# Exclude patterns for low-tier mods (Cobalt standard)
_EXCLUDE_PHYS_LOW = (
    'HasExplicitMod =0 "Heavy" "Serrated" "Wicked" "Vicious" '
    '"Glinting" "Burnished" "Polished" "Honed" "of Needling" "of Skill"'
)
_EXCLUDE_LIFE_LOW = 'HasExplicitMod =0 "Hale" "Healthy" "Sanguine"'
_EXCLUDE_CASTER_LOW = (
    'HasExplicitMod =0 "Heated" "Smouldering" "Smoking" "Frosted" '
    '"Chilled" "Icy" "Humming" "Buzzing" "Snapping" "Apprentice\'s" '
    '"Adept\'s" "Scholar\'s" "Searing" "Sizzling" "Blistering" '
    '"Bitter" "Biting" "Alpine" "Charged" "Hissing" "Bolting" "of Talent"'
)
_EXCLUDE_BOOTS_LIFE_LOW = (
    'HasExplicitMod =0 "Runner\'s" "Sprinter\'s" "Stallion\'s" '
    '"Hale" "Healthy" "Sanguine"'
)


def generate_id_mod_section() -> str:
    """HasExplicitMod 기반 ID 모드 필터링 섹션 [[0600-0800]].

    Cobalt 필터의 물리/캐스터/이동속도 부츠/아뮬렛/탑밸류 싱글 모드를
    PathcraftAI Aurora 스타일로 변환.
    """
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI ID Mod Filtering [[0600-0800]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── [0601] Physical weapons: 3+ good phys mods ──
    blocks.append(make_show_block(
        comment="ID Phys Weapon (Merciless/Tyrannical + 3 support)",
        conditions=[
            'Identified True',
            'DropLevel >= 50',
            'Rarity Rare',
            f'Class == {_WEAPON_CLASSES}',
            'HasExplicitMod "Merciless" "Tyrannical" "Cruel" '
            '"of the Underground" "Subterranean" "of Many" '
            '"of Tacati" "Tacati\'s"',
            'HasExplicitMod >=3 "Merciless" "Tyrannical" "Flaring" '
            '"Dictator\'s" "Emperor\'s" "of Celebration" "of Incision" '
            '"of Dissolution" "of Destruction" "of the Underground" '
            '"Subterranean" "of Many" "of Tacati" "Tacati\'s" "Veil"',
            _EXCLUDE_PHYS_LOW,
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0601] Physical weapons pure: uncorrupted, 2+ good phys mods ──
    blocks.append(make_show_block(
        comment="ID Phys Weapon Pure (uncorr, 2+ support)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'DropLevel >= 50',
            'Rarity Rare',
            f'Class == {_WEAPON_CLASSES}',
            'HasExplicitMod "Merciless" "Tyrannical" "Cruel" '
            '"of the Underground" "Subterranean" "of Many" '
            '"of Tacati" "Tacati\'s"',
            'HasExplicitMod >=2 "Merciless" "Tyrannical" "Flaring" '
            '"Dictator\'s" "Emperor\'s" "of Celebration" "of Incision" '
            '"of Dissolution" "of Destruction" "of the Underground" '
            '"Subterranean" "of Many" "of Tacati" "Tacati\'s" "Veil"',
            _EXCLUDE_PHYS_LOW,
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── [0605] Caster weapons: fire/cold/light/phys/chaos combined ──
    blocks.append(make_show_block(
        comment="ID Caster Weapon (all elements, 4+ mods)",
        conditions=[
            'Identified True',
            'Rarity Rare',
            f'Class == {_CASTER_WEAPON_CLASSES}',
            'HasExplicitMod "Martinet\'s" "Matatl\'s" "Tacati" '
            '"Topotante\'s" "of the Underground" "Subterranean" '
            '"of Many" "Magister\'s" "Empress\'s" "Queen\'s" '
            '"Lithomancer\'s" "Runic" "Glyphic" "Incanter\'s"',
            'HasExplicitMod >=4 "Martinet\'s" "Matatl\'s" "Tacati" '
            '"Topotante\'s" "of the Underground" "Subterranean" '
            '"of Many" "Magister\'s" "Empress\'s" "Queen\'s" '
            '"Lithomancer\'s" "Runic" "Glyphic" "Incanter\'s" '
            '"Electrocuting" "Discharging" "Entombing" "Polar" '
            '"Cremating" "Blasting" "of Unmaking" "of Ruin" '
            '"of Calamity" "of Finesse" "of Sortilege" '
            '"of Destruction" "of Ferocity" "of Fury" '
            '"Lich\'s" "Archmage\'s" "Mage\'s" "Zaffre" "Blue" '
            '"of Dissolution" "of Melting" "of the Essence" '
            '"Essences" "of Tacati" "of Puhuarte" "Veil"',
            _EXCLUDE_CASTER_LOW,
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0608] Boots life-based: MS + life + good suffixes ──
    blocks.append(make_show_block(
        comment="ID Boots Life (MS + life + res, 4+ mods)",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'Class == "Boots"',
            'HasExplicitMod "Athlete\'s" "Hellion\'s" "Cheetah\'s" '
            '"of Nullification" "Matatl\'s" "of the Underground" '
            '"Subterranean" "Elevated "',
            'HasExplicitMod >=4 "Athlete\'s" "Hellion\'s" "Cheetah\'s" '
            '"of Nullification" "Matatl\'s" "of the Underground" '
            '"Subterranean" "Elevated " '
            '"of the Godslayer" "of the Gods" "of the Blur" '
            '"of the Wind" "of the Polymath" "of the Genius" '
            '"of Bameth" "of Exile" "of Expulsion" "of Eviction" '
            '"of Abjuration" "of Revoking" "of Everlasting" '
            '"of Youth" "of Vivification" "Virile" "Rotund" '
            '"of the Essence" "Essences" "of Tacati" "of Puhuarte" "Veil" '
            '"Abbot\'s" "Prior\'s" "Ram\'s" "Fawn\'s" '
            '"Nautilus\'s" "Urchin\'s"',
            _EXCLUDE_BOOTS_LIFE_LOW,
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0611] Amulet Exalter's (single mod, very valuable) ──
    blocks.append(make_show_block(
        comment="ID Amulet Exalter's",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'Class == "Amulets"',
            'HasExplicitMod "Exalter\'s"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0611] Amulet caster combo (1 core + 4 total) ──
    blocks.append(make_show_block(
        comment="ID Amulet Caster (core + 4 mods)",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'Class == "Amulets"',
            'HasExplicitMod "Athlete\'s" "Virile" "Rotund" '
            '"Dazzling" "of the Underground" "Subterranean" '
            '"Xopec\'s" "of Guatelitzi" "Guatelitzi\'s" '
            '"of Puhuarte" "Exalter\'s" "Vulcanist\'s" '
            '"Rimedweller\'s" "Stormbrewer\'s" "Behemoth\'s" '
            '"Provocateur\'s" "of Destruction" "of Dissolution" '
            '"of the Multiverse" "Unassailable"',
            'HasExplicitMod >=4 "of the Essence" "Essences" '
            '"of Tacati" "of Puhuarte" "Veil" '
            '"of the Underground" "Subterranean" '
            '"Xopec\'s" "of Guatelitzi" "Guatelitzi\'s" '
            '"Exalter\'s" "Vulcanist\'s" "Rimedweller\'s" '
            '"Stormbrewer\'s" "Behemoth\'s" "Provocateur\'s" '
            '"of the Godslayer" "of the Gods" "of the Titan" '
            '"of the Leviathan" "of the Blur" "of the Wind" '
            '"of the Phantom" "of the Jaguar" "of the Polymath" '
            '"of the Genius" "of the Virtuoso" "of the Savant" '
            '"of Bameth" "of Exile" "of Expulsion" "of Eviction" '
            '"of Nirvana" "of Euphoria" "Impregnable" "Vaporous" '
            '"Unassailable" "Athlete\'s" "Virile" "Rotund" '
            '"Ultramarine" "Dazzling" "Resplendent" "Perandus\'" '
            '"of Legerdemain" "of Expertise" "Wizard\'s" '
            '"Thaumaturgist\'s" "Zaffre" "of Immolation" "of Flames" '
            '"of Floe" "of Rime" "of Discharge" "of Voltage" '
            '"of Dissolution" "of Melting" "of Destruction" '
            '"of Ferocity" "of Fury" "of Incision" "of Penetrating"',
            _EXCLUDE_LIFE_LOW,
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── [0801] Top Value Single Mod: Merciless (phys weapons) ──
    blocks.append(make_show_block(
        comment="ID Single Mod Merciless (T1 phys)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Normal Magic Rare',
            f'Class == {_WEAPON_CLASSES}',
            'HasExplicitMod >=1 "Merciless"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0801] Top Value: Magister's / Martinet's (caster) ──
    blocks.append(make_show_block(
        comment="ID Single Mod Magister's/Martinet's (T1 caster)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Normal Magic Rare',
            f'Class == {_CASTER_WEAPON_CLASSES} "Shields"',
            'HasExplicitMod >=1 "Magister\'s" "Martinet\'s"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0801] Top Value: of Many (additional projectiles) ──
    blocks.append(make_show_block(
        comment="ID Single Mod of Many (extra proj)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Normal Magic Rare',
            'Class == "Bows" "Wands"',
            'HasExplicitMod >=1 "of Many"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0801] Top Value: Exalter's / Vulcanist's etc (amulets) ──
    blocks.append(make_show_block(
        comment="ID Single Mod Exalter's+ (T1 amulet)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Normal Magic Rare',
            'Class == "Amulets"',
            'HasExplicitMod >=1 "Exalter\'s" "Vulcanist\'s" '
            '"Rimedweller\'s" "Stormbrewer\'s" "Behemoth\'s" '
            '"Provocateur\'s" "of Dissolution"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [0803] Flask double-mod: life flask bleed + catalysed ──
    blocks.append(make_show_block(
        comment="ID Flask Bleed+Catalysed (Life)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'BaseType == "Divine Life Flask" "Eternal Life Flask"',
            'HasExplicitMod >=2 "of Assuaging" "of Allaying" '
            '"Catalysed" "Panicked" "Bubbling" "Cautious" '
            '"Flagellant\'s" "Perpetual"',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── [0803] Flask double-mod: utility flask good combo ──
    blocks.append(make_show_block(
        comment="ID Flask Double-Mod (Utility)",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'BaseType == "Amethyst Flask" "Basalt Flask" "Bismuth Flask" '
            '"Diamond Flask" "Gold Flask" "Granite Flask" "Iron Flask" '
            '"Jade Flask" "Quartz Flask" "Quicksilver Flask" '
            '"Ruby Flask" "Sapphire Flask" "Silver Flask" '
            '"Stibnite Flask" "Sulphur Flask" "Topaz Flask"',
            'HasExplicitMod >=2 "of the Owl" "of the Armadillo" '
            '"of the Impala" "of the Cheetah" "of the Sanderling" '
            '"of Incision" "of the Eel" "of the Penguin" '
            '"of the Starfish" "of the Iguana" "Perpetual" '
            '"Surgeon\'s" "Flagellant\'s" "Alchemist\'s" '
            '"Experimenter\'s" "Chemist\'s"',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Exotic Mods Filtering [[1100]]
# ---------------------------------------------------------------------------

def generate_exotic_mods_section() -> str:
    """이국적 모드 필터링 섹션 [[1100]].

    Cobalt 필터의 Veiled/Incursion/Delve/Warband/Essence/Crafting/
    Necropolis/Bestiary/Mercenary 모드를 PathcraftAI Aurora 스타일로 변환.
    """
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Exotic Mods [[1100]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── [1101] Fractured + Veiled (highest value) ──
    blocks.append(make_show_block(
        comment="Exotic Fractured+Veiled",
        conditions=[
            'FracturedItem True',
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "Veil"',
        ],
        category="base",
        tier="P1_KEYSTONE",
    ))

    # ── [1101] Fractured + Incursion mods ──
    blocks.append(make_show_block(
        comment="Exotic Fractured+Incursion",
        conditions=[
            'FracturedItem True',
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "Citaqualotl" "Guatelitzi" "Matatl" '
            '"Puhuarte" "Tacati" "Topotante" "Xopec"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1101] Dual veiled (prefix + suffix) ──
    blocks.append(make_show_block(
        comment="Exotic Dual Veiled",
        conditions=[
            'Mirrored False',
            'Corrupted False',
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "Veiled"',
            'HasExplicitMod "of the Veil"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1102] Incursion: speed boots (Matatl's) ──
    blocks.append(make_show_block(
        comment="Exotic Incursion Speed Boots",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'Class == "Boots"',
            'HasExplicitMod "Matatl\'s"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1102] Incursion: caster weapons ──
    blocks.append(make_show_block(
        comment="Exotic Incursion Caster Weapon",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'Class == "Rune Daggers" "Sceptres" "Shields" "Staves" "Wands"',
            'HasExplicitMod "Matatl\'s" "Tacati" "Topotante\'s"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1102] Incursion: jewelry ──
    blocks.append(make_show_block(
        comment="Exotic Incursion Jewelry",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'Class == "Amulets" "Belts" "Rings"',
            'HasExplicitMod "Citaqualotl" "Guatelitzi" "Matatl" '
            '"Puhuarte" "Tacati" "Topotante" "Xopec"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1102] Incursion: attack weapons (Tacati) ──
    blocks.append(make_show_block(
        comment="Exotic Incursion Attack Weapon",
        conditions=[
            'Identified True',
            'Rarity Rare',
            f'Class == {_WEAPON_CLASSES}',
            'HasExplicitMod "of Tacati" "Tacati\'s"',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── [1102] Incursion: catch-all rare ──
    blocks.append(make_show_block(
        comment="Exotic Incursion Any Rare",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "Citaqualotl" "Guatelitzi" "Matatl" '
            '"Puhuarte" "Tacati" "Topotante" "Xopec"',
        ],
        category="base",
        tier="P4_SUPPORT",
    ))

    # ── [1105] Delve: fractured (highest tier) ──
    blocks.append(make_show_block(
        comment="Exotic Delve Fractured",
        conditions=[
            'FracturedItem True',
            'Identified True',
            'Rarity Normal Magic Rare',
            'HasExplicitMod "of the Underground" "Subterranean"',
        ],
        category="base",
        tier="P1_KEYSTONE",
    ))

    # ── [1105] Delve: regular ──
    blocks.append(make_show_block(
        comment="Exotic Delve Mod",
        conditions=[
            'Identified True',
            'Rarity Normal Magic Rare',
            'HasExplicitMod "of the Underground" "Subterranean"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1105] Mercenary: armor/jewelry ──
    blocks.append(make_show_block(
        comment="Exotic Mercenary (Armor/Jewelry)",
        conditions=[
            'Identified True',
            'Rarity Normal Magic Rare',
            'Class == "Amulets" "Belts" "Body Armours" "Boots" '
            '"Gloves" "Helmets" "Quivers" "Rings" "Shields"',
            'HasExplicitMod "Infamous" "of Infamy"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1105] Mercenary: weapons ──
    blocks.append(make_show_block(
        comment="Exotic Mercenary (Weapons)",
        conditions=[
            'Identified True',
            'Rarity Normal Magic Rare',
            f'Class == {_WEAPON_CLASSES} "Rune Daggers" "Sceptres" "Staves"',
            'HasExplicitMod "Infamous"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1103] Necropolis: Haunted mods ──
    blocks.append(make_show_block(
        comment="Exotic Necropolis (Haunted)",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "Haunted" "of Haunting"',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── [1104] Bestiary: Farrul/Fenumus (valuable) ──
    blocks.append(make_show_block(
        comment="Exotic Bestiary Valuable (Farrul/Fenumus)",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "of Farrul" "of Fenumus"',
        ],
        category="base",
        tier="P2_CORE",
    ))

    # ── [1104] Bestiary: Craiceann/Saqawal (lesser) ──
    blocks.append(make_show_block(
        comment="Exotic Bestiary Other (Craiceann/Saqawal)",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "of Craiceann" "of Saqawal"',
        ],
        category="base",
        tier="P3_USEFUL",
    ))

    # ── [1105] Warband mods ──
    blocks.append(make_show_block(
        comment="Exotic Warband Mods",
        conditions=[
            'Identified True',
            'Rarity Normal Magic Rare',
            'HasExplicitMod "Betrayer\'s" "Brinerot" "Deceiver\'s" '
            '"Mutewind" "Redblade" "Turncoat\'s"',
        ],
        category="base",
        tier="P4_SUPPORT",
    ))

    # ── [1105] Essence mods ──
    blocks.append(make_show_block(
        comment="Exotic Essence Mods",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "of the Essence" "Essences"',
        ],
        category="base",
        tier="P4_SUPPORT",
        is_build_target=False,
    ))

    # ── [1105] Crafting mods (bench) ──
    blocks.append(make_show_block(
        comment="Exotic Crafting Mods",
        conditions=[
            'Identified True',
            'Rarity Rare',
            'HasExplicitMod "of Crafting" "of Spellcraft" "of Weaponcraft"',
        ],
        category="base",
        tier="P4_SUPPORT",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Endgame Rare Section [[1600-2100]]
# ---------------------------------------------------------------------------

# Breach ring bases (Cobalt [[1900]])
_BREACH_RINGS = [
    "Cryonic Ring", "Enthalpic Ring", "Formless Ring",
    "Fugitive Ring", "Organic Ring", "Synaptic Ring",
]

# Talisman bases (for anointed checks)
_TALISMAN_BASES = [
    "Ashscale Talisman", "Avian Twins Talisman", "Bonespire Talisman",
    "Breakrib Talisman", "Clutching Talisman", "Deadhand Talisman",
    "Deep One Talisman", "Fangjaw Talisman", "Horned Talisman",
    "Lone Antler Talisman", "Longtooth Talisman", "Rotfeather Talisman",
    "Spinefuse Talisman", "Three Rat Talisman", "Wereclaw Talisman",
    "Writhing Talisman",
]

# Endgame rare jewelry tiers (Cobalt [[2100]])
_AMURING_T1 = [
    "Agate Amulet", "Amethyst Ring", "Cerulean Ring", "Citrine Amulet",
    "Onyx Amulet", "Opal Ring", "Prismatic Ring", "Turquoise Amulet",
    "Two-Stone Ring", "Vermillion Ring",
]

_AMURING_T2 = [
    "Amber Amulet", "Blue Pearl Amulet", "Bone Ring", "Coral Ring",
    "Diamond Ring", "Iolite Ring", "Jade Amulet", "Lapis Amulet",
    "Marble Amulet", "Ruby Ring", "Sapphire Ring", "Steel Ring",
    "Topaz Ring", "Unset Ring",
]

_AMURING_T3 = [
    "Coral Amulet", "Gold Amulet", "Gold Ring", "Iron Ring",
    "Moonstone Ring", "Paua Amulet", "Paua Ring", "Seaglass Amulet",
]

_BELT_T1 = ["Stygian Vise"]
_BELT_T2 = ["Crystal Belt", "Heavy Belt", "Leather Belt", "Vanguard Belt"]
_BELT_T3 = ["Chain Belt", "Cloth Belt", "Rustic Sash", "Studded Belt"]

# All gear classes for hide rules
_ALL_GEAR_CLASSES = (
    '"Amulets" "Belts" "Body Armours" "Boots" "Bows" "Claws" '
    '"Daggers" "Gloves" "Helmets" "One Hand Axes" "One Hand Maces" '
    '"One Hand Swords" "Quivers" "Rings" "Rune Daggers" "Sceptres" '
    '"Shields" "Staves" "Thrusting One Hand Swords" "Two Hand Axes" '
    '"Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"'
)

# Non-jewelry gear classes (for remaining rares)
_NONJEWELRY_CLASSES = (
    '"Body Armours" "Boots" "Bows" "Claws" "Daggers" "Gloves" '
    '"Helmets" "One Hand Axes" "One Hand Maces" "One Hand Swords" '
    '"Quivers" "Rune Daggers" "Sceptres" "Shields" "Staves" '
    '"Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces" '
    '"Two Hand Swords" "Wands" "Warstaves"'
)


def generate_endgame_rare_section() -> str:
    """엔드게임 레어 섹션 [[1600-2100]].

    Cobalt 필터의 Breach rings, 탈리스만, 아뮬렛/링/벨트 티어,
    부패/미러 숨기기, 잔여 레어 티어를 PathcraftAI Aurora로 변환.
    """
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Endgame Rare [[1600-2100]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── [[1900]] Breach Rings: high ilvl ──
    breach_str = " ".join(f'"{n}"' for n in _BREACH_RINGS)
    blocks.append(make_show_block(
        comment="Breach Ring ilvl82+",
        conditions=[
            'ItemLevel >= 82',
            'Rarity Normal Magic Rare',
            'Class == "Rings"',
            f'BaseType == {breach_str}',
        ],
        category="jewel",
        tier="P2_CORE",
    ))

    blocks.append(make_show_block(
        comment="Breach Ring ilvl68+",
        conditions=[
            'ItemLevel >= 68',
            'Rarity Normal Magic Rare',
            'Class == "Rings"',
            f'BaseType == {breach_str}',
        ],
        category="jewel",
        tier="P3_USEFUL",
    ))

    # ── [[1900]] Anointed Talismans: good bases ──
    talisman_str = " ".join(f'"{n}"' for n in _TALISMAN_BASES)
    blocks.append(make_show_block(
        comment="Anointed Talisman (good base)",
        conditions=[
            'AnyEnchantment True',
            'ItemLevel >= 68',
            'Rarity Rare',
            'Class == "Amulets"',
            f'BaseType == {talisman_str}',
        ],
        category="jewel",
        tier="P3_USEFUL",
    ))

    # ── Anointed Talisman: any base fallback ──
    blocks.append(make_show_block(
        comment="Anointed Talisman (any base)",
        conditions=[
            'AnyEnchantment True',
            'ItemLevel >= 68',
            'Rarity Rare',
            'Class == "Amulets"',
            'BaseType "Talisman"',
        ],
        category="jewel",
        tier="P4_SUPPORT",
        is_build_target=False,
    ))

    # ── [[2000]] Hide corrupted unidentified rares ──
    blocks.append(make_hide_block(
        comment="Hide corrupted unID rares",
        conditions=[
            'Corrupted True',
            'Identified False',
            'CorruptedMods 0',
            'ItemLevel >= 68',
            'Rarity Rare',
            f'Class == {_NONJEWELRY_CLASSES}',
        ],
    ))

    # ── [[2000]] Hide mirrored unidentified rares ──
    blocks.append(make_hide_block(
        comment="Hide mirrored unID rares",
        conditions=[
            'Mirrored True',
            'Identified False',
            'CorruptedMods 0',
            'ItemLevel >= 68',
            'Rarity Rare',
            f'Class == {_NONJEWELRY_CLASSES}',
        ],
    ))

    # ── [[2100]] Amulets/Rings by BaseType tier ──
    for tier_list, p_tier, label in [
        (_AMURING_T1, "P2_CORE",    "Amuring T1"),
        (_AMURING_T2, "P3_USEFUL",  "Amuring T2"),
        (_AMURING_T3, "P4_SUPPORT", "Amuring T3"),
    ]:
        names_str = " ".join(f'"{n}"' for n in tier_list)
        blocks.append(make_show_block(
            comment=f"Endgame {label} ({len(tier_list)} types)",
            conditions=[
                'ItemLevel >= 68',
                'Rarity Rare',
                'Class == "Amulets" "Rings"',
                f'BaseType == {names_str}',
            ],
            category="jewel",
            tier=p_tier,
        ))

    # ── [[2100]] Belts by BaseType tier ──
    for tier_list, p_tier, label in [
        (_BELT_T1, "P2_CORE",    "Belt T1"),
        (_BELT_T2, "P3_USEFUL",  "Belt T2"),
        (_BELT_T3, "P4_SUPPORT", "Belt T3"),
    ]:
        names_str = " ".join(f'"{n}"' for n in tier_list)
        blocks.append(make_show_block(
            comment=f"Endgame {label} ({len(tier_list)} types)",
            conditions=[
                'ItemLevel >= 68',
                'Rarity Rare',
                'Class == "Belts"',
                f'BaseType == {names_str}',
            ],
            category="jewel",
            tier=p_tier,
        ))

    # ── Remaining rares fallback (non-jewelry gear) ──
    blocks.append(make_show_block(
        comment="Endgame Rare Gear Fallback",
        conditions=[
            'ItemLevel >= 68',
            'Rarity Rare',
            f'Class == {_NONJEWELRY_CLASSES}',
        ],
        category="base",
        tier="P5_MINOR",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Misc Rules [[2600]]
# ---------------------------------------------------------------------------

def generate_misc_rules_section() -> str:
    """기타 규칙 섹션 [[2600]].

    Cobalt 필터의 RGB 레시피 + 잔여 레어 캐치올.
    """
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Misc Rules [[2600]]\n"
        "#" + "=" * 79 + "\n"
    )

    # ── [2601] RGB recipe: 2x2 items ──
    blocks.append(make_show_block(
        comment="RGB Recipe Small (2x2)",
        conditions=[
            'Width 2',
            'Height 2',
            'Rarity Normal Magic Rare',
            'SocketGroup "RGB"',
            'AreaLevel >= 68',
            'AreaLevel <= 83',
        ],
        category="base",
        tier="P6_LOW",
        is_build_target=False,
    ))

    # ── [2601] RGB recipe: 1xN items ──
    blocks.append(make_show_block(
        comment="RGB Recipe Small (1xN)",
        conditions=[
            'Width 1',
            'Height <= 4',
            'Rarity Normal Magic Rare',
            'SocketGroup "RGB"',
            'AreaLevel >= 68',
            'AreaLevel <= 83',
        ],
        category="base",
        tier="P6_LOW",
        is_build_target=False,
    ))

    # ── [2602] Remaining rares catch-all ──
    blocks.append(make_show_block(
        comment="Remaining Rares Catch-All",
        conditions=[
            'ItemLevel >= 68',
            'Rarity Rare',
            f'Class == {_ALL_GEAR_CLASSES}',
        ],
        category="base",
        tier="P6_LOW",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Perfection / Overquality — Cobalt [[0900]] [0901]
# ---------------------------------------------------------------------------

PERFECTION_ARMOR_T1 = [
    "Bone Helmet", "Fingerless Silk Gloves", "Gripped Gloves", "Spiked Gloves",
    "Two-Toned Boots", "Sorcerer Boots", "Titanium Spirit Shield",
    "Fossilised Spirit Shield", "Archon Kite Shield",
]

PERFECTION_WEAPON_T1 = [
    "Artillery Quiver", "Battered Foil", "Broadhead Arrow Quiver",
    "Convoking Wand", "Copper Kris", "Despot Axe", "Feathered Arrow Quiver",
    "Gemini Claw", "Golden Kris", "Imperial Claw", "Imperial Skean",
    "Jewelled Foil", "Kinetic Wand", "Opal Sceptre", "Opal Wand",
    "Platinum Kris", "Primal Arrow Quiver", "Profane Wand", "Prophecy Wand",
    "Reaver Axe", "Reaver Sword", "Reflex Bow", "Short Bow", "Siege Axe",
    "Spine Bow", "Thicket Bow", "Vaal Axe", "Void Sceptre", "Whalebone Rapier",
]

PERFECTION_WEAPON_T2 = [
    "Ambusher", "Basket Rapier", "Behemoth Mace", "Citadel Bow",
    "Convening Wand", "Corsair Sword", "Eclipse Staff", "Eternal Sword",
    "Exquisite Blade", "Ezomyte Blade", "Ezomyte Staff", "Fleshripper",
    "Grove Bow", "Harbinger Bow", "Heavy Arrow Quiver", "Imperial Bow",
    "Judgement Staff", "Karui Chopper", "Karui Sceptre", "Legion Hammer",
    "Maraketh Bow", "Meatgrinder", "Piledriver", "Royal Axe", "Runic Hatchet",
    "Sai", "Sambar Sceptre", "Spiraled Foil", "Sundering Axe",
    "Vile Arrow Quiver",
]

ALL_GEAR_CLASSES = (
    'Class "Amulets" "Belts" "Body Armours" "Boots" "Bows" "Claws" "Daggers"'
    ' "Gloves" "Helmets" "One Hand Axes" "One Hand Maces" "One Hand Swords"'
    ' "Quivers" "Rings" "Rune Daggers" "Sceptres" "Shields" "Staves"'
    ' "Thrusting One Hand Swords" "Two Hand Axes" "Two Hand Maces"'
    ' "Two Hand Swords" "Wands" "Warstaves"'
)

MEMORY_T1_BASES = [
    "Agate Amulet", "Amethyst Ring", "Cerulean Ring", "Citrine Amulet",
    "Crystal Belt", "Iolite Ring", "Onyx Amulet", "Opal Ring",
    "Prismatic Ring", "Steel Ring", "Stygian Vise", "Turquoise Amulet",
    "Two-Stone Ring", "Vermillion Ring",
    "Conquest Lamellar", "Divine Crown", "Giantslayer Helmet",
    "Haunted Bascinet", "Leviathan Gauntlets", "Leviathan Greaves",
    "Majestic Pelt", "Necrotic Armour", "Paladin Boots", "Paladin Gloves",
    "Phantom Boots", "Phantom Mitts", "Royal Plate", "Sacred Chainmail",
    "Sacrificial Garb", "Syndicate's Garb", "Torturer's Mask",
    "Twilight Regalia", "Velour Boots", "Velour Gloves",
    "Warlock Boots", "Warlock Gloves", "Wyvernscale Boots",
    "Wyvernscale Gauntlets",
]


def generate_perfection_section() -> str:
    """Perfection/Overquality. Cobalt [[0900]] [0901]."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Perfection & Overquality\n"
        "#" + "=" * 79 + "\n"
    )

    armor_str = " ".join(f'"{n}"' for n in PERFECTION_ARMOR_T1)
    wt1_str = " ".join(f'"{n}"' for n in PERFECTION_WEAPON_T1)
    wt2_str = " ".join(f'"{n}"' for n in PERFECTION_WEAPON_T2)

    blocks.append(make_show_block(
        comment="Perfection Chancing Base Q26+",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 26',
                    'BaseType == "Riveted Boots" "Steel Kite Shield"'],
        category="base", tier="P1_KEYSTONE", keystone=True,
    ))
    blocks.append(make_show_block(
        comment=f"Perfection Armor T1 Q28+",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 28',
                    'Class "Body Armours" "Boots" "Gloves" "Helmets" "Shields"',
                    f'BaseType == {armor_str}'],
        category="base", tier="P1_KEYSTONE",
    ))
    blocks.append(make_show_block(
        comment="Perfection Armor T1 Q24+",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 24',
                    'Class "Body Armours" "Boots" "Gloves" "Helmets" "Shields"',
                    f'BaseType == {armor_str}'],
        category="base", tier="P2_CORE",
    ))
    blocks.append(make_show_block(
        comment="Perfection Weapon T1 Q28+ ilvl83",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 28',
                    'ItemLevel >= 83', f'BaseType == {wt1_str}'],
        category="base", tier="P1_KEYSTONE",
    ))
    blocks.append(make_show_block(
        comment="Perfection Weapon T2 Q28+ ilvl83",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 28',
                    'ItemLevel >= 83', f'BaseType == {wt2_str}'],
        category="base", tier="P2_CORE",
    ))
    blocks.append(make_show_block(
        comment="Perfection Weapon T1 Q24+ ilvl83",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 24',
                    'ItemLevel >= 83', f'BaseType == {wt1_str}'],
        category="base", tier="P2_CORE",
    ))
    blocks.append(make_show_block(
        comment="Perfection Weapon T2 Q24+ ilvl83",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 24',
                    'ItemLevel >= 83', f'BaseType == {wt2_str}'],
        category="base", tier="P3_USEFUL",
    ))
    blocks.append(make_show_block(
        comment="Perfection Any Q30+",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 30',
                    ALL_GEAR_CLASSES],
        category="base", tier="P3_USEFUL",
    ))
    blocks.append(make_show_block(
        comment="Perfection Any Q26+",
        conditions=['Mirrored False', 'Corrupted False', 'Quality >= 26',
                    ALL_GEAR_CLASSES],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))

    return "\n".join(blocks)


def generate_memory_strand_section() -> str:
    """Memory Strand 장비. Cobalt [[0900]] [0902]."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Memory Strand Gear\n"
        "#" + "=" * 79 + "\n"
    )

    t1_str = " ".join(f'"{n}"' for n in MEMORY_T1_BASES)

    blocks.append(make_show_block(
        comment="Memory Strand Fractured",
        conditions=['FracturedItem True', 'Mirrored False', 'Corrupted False',
                    'MemoryStrands >= 1', 'Rarity Normal Magic Rare'],
        category="base", tier="P1_KEYSTONE", keystone=True,
    ))
    blocks.append(make_show_block(
        comment="Memory Strand Veiled",
        conditions=['Mirrored False', 'Corrupted False', 'Identified True',
                    'MemoryStrands >= 1', 'Rarity Normal Magic Rare',
                    'HasExplicitMod "Veil"'],
        category="base", tier="P1_KEYSTONE", keystone=True,
    ))
    blocks.append(make_show_block(
        comment=f"Memory Strand T1 High (>= 60)",
        conditions=['Mirrored False', 'Corrupted False',
                    'MemoryStrands >= 60', 'Rarity Normal Magic Rare',
                    f'BaseType == {t1_str}'],
        category="base", tier="P1_KEYSTONE",
    ))
    blocks.append(make_show_block(
        comment="Memory Strand T1 (>= 1)",
        conditions=['Mirrored False', 'Corrupted False',
                    'MemoryStrands >= 1', 'Rarity Normal Magic Rare',
                    f'BaseType == {t1_str}'],
        category="base", tier="P3_USEFUL",
    ))
    blocks.append(make_show_block(
        comment="Memory Strand Any High (>= 70)",
        conditions=['Mirrored False', 'Corrupted False',
                    'MemoryStrands >= 70', 'Rarity Normal Magic Rare'],
        category="base", tier="P4_SUPPORT", is_build_target=False,
    ))
    blocks.append(make_show_block(
        comment="Memory Strand Any (>= 1)",
        conditions=['Mirrored False', 'Corrupted False',
                    'MemoryStrands >= 1', 'Rarity Normal Magic Rare'],
        category="base", tier="P5_MINOR", is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Heist Gear [[2900]] — Cobalt [2901]~[2904]
# ---------------------------------------------------------------------------

HEIST_CLOAK_T1 = ["Whisper-woven Cloak"]
HEIST_CLOAK_T2 = ["Hooded Cloak"]

HEIST_BROOCH_T1 = ["Foliate Brooch"]
HEIST_BROOCH_T2 = ["Enamel Brooch"]

HEIST_GEAR_T1 = [
    "Burst Band", "Obsidian Sharpening Stone", "Precise Arrowhead",
]
HEIST_GEAR_T2 = [
    "Aggregator Charm", "Fine Sharpening Stone",
    "Fragmenting Arrowhead", "Hollowpoint Arrowhead",
]

HEIST_TOOL_T1 = [
    "Grandmaster Keyring", "Master Lockpick",
    "Regicide Disguise Kit", "Silkweave Sole",
    "Steel Bracers", "Thaumaturgical Sensing Charm",
    "Thaumaturgical Ward", "Thaumetic Blowtorch",
    "Thaumetic Flashpowder",
]
HEIST_TOOL_T2 = [
    "Azurite Flashpowder", "Espionage Disguise Kit",
    "Fine Lockpick", "Polished Sensing Charm",
    "Runed Bracers", "Shining Ward",
    "Skeleton Keyring", "Standard Lockpick",
    "Sulphur Blowtorch", "Winged Sole",
]


def generate_heist_section() -> str:
    """Cobalt [[2900]] Heist Gear — Cloaks/Brooches/Gear/Tools."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Heist Gear [[2900]]\n"
        "#" + "=" * 79 + "\n"
    )

    _HEIST_CATS = [
        # (class_name, t1_bases, t2_bases, highlevel_ilvl)
        ("Heist Cloaks",   HEIST_CLOAK_T1,  HEIST_CLOAK_T2,  83),
        ("Heist Brooches", HEIST_BROOCH_T1, HEIST_BROOCH_T2, 84),
        ("Heist Gear",     HEIST_GEAR_T1,   HEIST_GEAR_T2,   83),
        ("Heist Tools",    HEIST_TOOL_T1,   HEIST_TOOL_T2,   83),
    ]

    rarity = 'Rarity Normal Magic Rare'

    for cls_name, t1, t2, ilvl_hi in _HEIST_CATS:
        cls_cond = f'Class == "{cls_name}"'

        # t1highlevel (ilvl >= N)
        blocks.append(make_show_block(
            comment=f"{cls_name} T1 ilvl{ilvl_hi}+ [{len(t1)}]",
            conditions=[
                f'ItemLevel >= {ilvl_hi}',
                rarity, cls_cond,
                f'BaseType == {_q(t1)}',
            ],
            category="base", tier="P2_CORE", is_build_target=False,
        ))
        # t1 (any ilvl)
        blocks.append(make_show_block(
            comment=f"{cls_name} T1 [{len(t1)}]",
            conditions=[rarity, cls_cond, f'BaseType == {_q(t1)}'],
            category="base", tier="P3_USEFUL", is_build_target=False,
        ))
        # t2
        blocks.append(make_show_block(
            comment=f"{cls_name} T2 [{len(t2)}]",
            conditions=[rarity, cls_cond, f'BaseType == {_q(t2)}'],
            category="base", tier="P4_SUPPORT", is_build_target=False,
        ))
        # t3any (catch-all for the class)
        blocks.append(make_show_block(
            comment=f"{cls_name} any",
            conditions=[rarity, cls_cond],
            category="base", tier="P5_MINOR", is_build_target=False,
        ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Replica & Foulborn [[3100]]
# ---------------------------------------------------------------------------

REPLICA_T1 = [
    "Chain Belt", "Ebony Tower Shield", "Great Crown",
    "Leather Belt", "Maelstr\u00f6m Staff", "Soldier Boots",
    "Terror Maul", "Triumphant Lamellar", "Turquoise Amulet",
]
REPLICA_T2 = [
    "Assassin's Boots", "Blood Raiment", "Great Mallet",
    "Imperial Bow", "Leather Hood", "Ornate Quiver",
    "Sage Wand", "Shadow Sceptre", "Siege Axe",
    "Sorcerer Gloves", "Spidersilk Robe", "Synthesised Map",
    "Tornado Wand", "Vaal Claw", "Vaal Gauntlets", "Void Sceptre",
]
REPLICA_MULTI = ["Carnal Armour"]
REPLICA_T3 = [
    "Arcanist Gloves", "Arcanist Slippers", "Blasting Wand",
    "Boot Knife", "Bronzescale Boots", "Calling Wand",
    "Cloth Belt", "Cobalt Jewel", "Crimson Jewel",
    "Crusader Chainmail", "Death Bow", "Decimation Bow",
    "Elder Sword", "Elegant Ringmail", "Eternal Sword",
    "Ezomyte Axe", "Ezomyte Burgonet", "Ezomyte Dagger",
    "Festival Mask", "Glorious Plate", "Gnarled Branch",
    "Gold Amulet", "Granite Flask", "Great Helmet",
    "Grinning Fetish", "Gut Ripper", "Heavy Belt",
    "Infernal Sword", "Jade Amulet", "Jasper Chopper",
    "Lacquered Buckler", "Laminated Kite Shield",
    "Murder Boots", "Nailed Fist", "Onyx Amulet",
    "Opal Wand", "Ornate Mace", "Paua Amulet",
    "Paua Ring", "Royal Skean", "Ruby Ring",
    "Rustic Sash", "Samite Gloves", "Sanctified Mana Flask",
    "Sapphire Ring", "Satin Gloves", "Shagreen Boots",
    "Short Bow", "Silk Slippers", "Sinner Tricorne",
    "Spike-Point Arrow Quiver", "Stibnite Flask", "Stiletto",
    "Sulphur Flask", "Titan Greaves", "Unset Ring",
    "Vaal Rapier", "Viridian Jewel", "War Sword",
    "Zealot Gloves", "Zodiac Leather",
]

FOULBORN_T1 = [
    "Champion Kite Shield", "Fishing Rod", "Paua Amulet",
    "Prophecy Wand", "Sorcerer Boots", "Steel Kite Shield",
    "Wyrmscale Doublet",
]
FOULBORN_T2 = [
    "Astral Plate", "Desert Brigandine", "Gavel",
    "Gladiator Plate", "Lunaris Circlet", "Ornate Quiver",
    "Rawhide Boots", "Somatic Wand", "Titanium Spirit Shield",
]
FOULBORN_MULTI = [
    "Crimson Jewel", "Elegant Round Shield", "Heavy Belt",
    "Imperial Claw", "Lacquered Garb", "Leather Belt",
    "Sage's Robe", "Spidersilk Robe", "Two-Stone Ring",
    "Viridian Jewel",
]
FOULBORN_T3 = [
    "Abyssal Axe", "Agate Amulet", "Amber Amulet",
    "Amethyst Ring", "Ancient Spirit Shield",
    "Archon Kite Shield", "Assassin Bow", "Assassin's Garb",
    "Assassin's Mitts", "Blunt Arrow Quiver",
    "Branded Kite Shield", "Bronzescale Gauntlets",
    "Buckskin Tunic", "Calling Wand", "Carnal Mitts",
    "Chain Belt", "Chain Gloves", "Citadel Bow",
    "Clasped Mitts", "Close Helmet", "Cloth Belt",
    "Cobalt Jewel", "Conjurer Gloves", "Copper Plate",
    "Corrugated Buckler", "Crusader Chainmail",
    "Crusader Gloves", "Crusader Plate", "Crystal Belt",
    "Cutlass", "Cutthroat's Garb", "Death Bow",
    "Deerskin Gloves", "Destiny Leather",
    "Destroyer Regalia", "Devout Chainmail", "Diamond Ring",
    "Dragonscale Boots", "Etched Greatsword", "Eternal Sword",
    "Exquisite Leather", "Ezomyte Burgonet",
    "Ezomyte Tower Shield", "Fiend Dagger",
    "Full Wyrmscale", "Gilded Sallet", "Goat's Horn",
    "Goathide Boots", "Gold Ring", "Golden Mask",
    "Golden Plate", "Great Helmet", "Harlequin Mask",
    "Harmonic Spirit Shield", "Holy Chainmail",
    "Hubris Circlet", "Iron Circlet", "Iron Ring",
    "Ironscale Gauntlets", "Ironwood Buckler",
    "Jade Amulet", "Jasper Chopper", "Jewelled Foil",
    "Karui Chopper", "Karui Sceptre", "Kinetic Wand",
    "Lapis Amulet", "Lathi", "Leather Cap",
    "Leather Hood", "Legion Boots", "Legion Gloves",
    "Lion Sword", "Majestic Plate", "Midnight Blade",
    "Military Staff", "Mind Cage", "Moonstone Ring",
    "Mosaic Kite Shield", "Murder Mitts",
    "Necromancer Silks", "Nightmare Bascinet",
    "Nubuck Boots", "Occultist's Vestment", "Omen Wand",
    "Onyx Amulet", "Opal Wand", "Ornate Mace",
    "Penetrating Arrow Quiver", "Pinnacle Tower Shield",
    "Plate Vest", "Platinum Sceptre", "Praetor Crown",
    "Prismatic Ring", "Ranger Bow", "Raven Mask",
    "Reaver Sword", "Regicide Mask", "Reinforced Greaves",
    "Royal Axe", "Royal Bow", "Royal Burgonet",
    "Ruby Ring", "Sadist Garb", "Saintly Chainmail",
    "Samite Gloves", "Sapphire Ring", "Scholar's Robe",
    "Serpentine Staff", "Short Bow", "Silk Gloves",
    "Silken Hood", "Silken Vest", "Sinner Tricorne",
    "Soldier Boots", "Spike-Point Arrow Quiver",
    "Spiraled Wand", "Steel Gauntlets", "Steelhead",
    "Steelscale Gauntlets", "Strapped Mitts",
    "Studded Belt", "Tarnished Spirit Shield",
    "Terror Claw", "Terror Maul", "Thresher Claw",
    "Timeworn Claw", "Titan Gauntlets", "Titan Greaves",
    "Tomahawk", "Topaz Ring", "Triumphant Lamellar",
    "Turquoise Amulet", "Two-Point Arrow Quiver",
    "Vaal Axe", "Vaal Blade", "Vaal Gauntlets",
    "Vaal Sceptre", "Vaal Spirit Shield",
    "Varnished Coat", "Vile Staff", "War Buckler",
    "Widowsilk Robe", "Wool Gloves",
    "Wyrmscale Gauntlets", "Zealot Helmet", "Zodiac Leather",
]


def generate_replica_foulborn_section() -> str:
    """Cobalt [[3100]] Replica & Foulborn Uniques."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Replica & Foulborn [[3100]]\n"
        "#" + "=" * 79 + "\n"
    )

    # --- Replicas ---
    for tier_items, ptier, label in [
        (REPLICA_T1,    "P1_KEYSTONE", "Replica T1"),
        (REPLICA_T2,    "P2_CORE",     "Replica T2"),
        (REPLICA_MULTI, "P3_USEFUL",   "Replica Multi"),
        (REPLICA_T3,    "P4_SUPPORT",  "Replica T3"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[
                'Replica True', 'Rarity Unique',
                f'BaseType == {_q(tier_items)}',
            ],
            category="unique", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block(
        "Replica restex", ['Replica True', 'Rarity Unique'],
    ))

    # --- Foulborn ---
    for tier_items, ptier, label in [
        (FOULBORN_T1,    "P1_KEYSTONE", "Foulborn T1"),
        (FOULBORN_T2,    "P2_CORE",     "Foulborn T2"),
        (FOULBORN_MULTI, "P3_USEFUL",   "Foulborn Multi"),
        (FOULBORN_T3,    "P4_SUPPORT",  "Foulborn T3"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[
                'Foulborn True', 'Rarity Unique',
                f'BaseType == {_q(tier_items)}',
            ],
            category="unique", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block(
        "Foulborn restex", ['Foulborn True', 'Rarity Unique'],
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Cluster Jewel 경제 기반 — Cobalt [[2805-2806]]
# ---------------------------------------------------------------------------

def generate_cluster_jewel_section() -> str:
    """Cluster Jewel 경제 기반 티어링. Cobalt [[2805-2806]]."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Cluster Jewels\n"
        "#" + "=" * 79 + "\n"
    )

    # T1 경제 — 특정 인챈트 (Minion Damage 12패시브, Reservation Efficiency 3패시브)
    blocks.append(make_show_block(
        comment="Cluster T1 Large Minion Damage ilvl84",
        conditions=['ItemLevel >= 84', 'Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum 12',
                    'BaseType == "Large Cluster Jewel"',
                    'EnchantmentPassiveNode "Minion Damage"'],
        category="jewel", tier="P1_KEYSTONE", keystone=True,
    ))
    blocks.append(make_show_block(
        comment="Cluster T1 Small Reservation ilvl84",
        conditions=['ItemLevel >= 84', 'Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum 3',
                    'BaseType == "Small Cluster Jewel"',
                    'EnchantmentPassiveNode "Reservation Efficiency"'],
        category="jewel", tier="P1_KEYSTONE", keystone=True,
    ))

    # 일반 Large optimal (ilvl84, 8-12 패시브)
    blocks.append(make_show_block(
        comment="Cluster Large Optimal ilvl84 (12 passive)",
        conditions=['ItemLevel >= 84', 'Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum >= 12',
                    'BaseType == "Large Cluster Jewel"'],
        category="jewel", tier="P2_CORE",
    ))
    blocks.append(make_show_block(
        comment="Cluster Large Optimal ilvl84 (<=8 passive)",
        conditions=['ItemLevel >= 84', 'Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum <= 8',
                    'BaseType == "Large Cluster Jewel"'],
        category="jewel", tier="P2_CORE",
    ))

    # Large 일반
    blocks.append(make_show_block(
        comment="Cluster Large any",
        conditions=['Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum <= 8',
                    'BaseType == "Large Cluster Jewel"'],
        category="jewel", tier="P4_SUPPORT",
    ))

    # Medium optimal ilvl84
    blocks.append(make_show_block(
        comment="Cluster Medium Optimal ilvl84",
        conditions=['ItemLevel >= 84', 'Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum <= 5',
                    'BaseType == "Medium Cluster Jewel"'],
        category="jewel", tier="P2_CORE",
    ))
    # Medium 일반
    blocks.append(make_show_block(
        comment="Cluster Medium any",
        conditions=['Rarity Normal Magic Rare',
                    'EnchantmentPassiveNum <= 5',
                    'BaseType == "Medium Cluster Jewel"'],
        category="jewel", tier="P4_SUPPORT",
    ))

    # Small ilvl84
    blocks.append(make_show_block(
        comment="Cluster Small ilvl84",
        conditions=['ItemLevel >= 84', 'Rarity Normal Magic Rare',
                    'BaseType == "Small Cluster Jewel"'],
        category="jewel", tier="P3_USEFUL",
    ))
    # Small 일반
    blocks.append(make_show_block(
        comment="Cluster Small any",
        conditions=['Rarity Normal Magic Rare',
                    'BaseType == "Small Cluster Jewel"'],
        category="jewel", tier="P5_MINOR",
    ))

    return "\n".join(blocks)
