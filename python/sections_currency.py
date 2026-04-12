# -*- coding: utf-8 -*-
"""PathcraftAI Aurora Glow — 커런시 관련 섹션.

커런시 스택, 레벨링 커런시, Lifeforce, 스플린터, 특수 커런시 섹션.
"""

from sections_core import (
    make_show_block, make_hide_block, make_restex_block,
    make_currency_stack_block,
    _promote_tier, _find_currency_tier, _q,
    _TIER_ORDER, CURRENCY_STACK_THRESHOLDS, SUPPLY_STACK_THRESHOLDS,
    SUPPLY_CURRENCIES,
    get_currency_tiers, DEFAULT_MODE,
)


# ---------------------------------------------------------------------------
# 커런시 스택 섹션
# ---------------------------------------------------------------------------

def generate_currency_stack_section(mode: str = DEFAULT_MODE) -> str:
    """모드별 커런시 스택 기반 필터 섹션 전체 생성."""
    tiers = get_currency_tiers(mode)
    supply_set = set(SUPPLY_CURRENCIES)
    blocks: list[str] = []

    blocks.append(
        "#" + "=" * 79 + "\n"
        f"# PathcraftAI Currency Stack Rules (Mode: {mode.upper()})\n"
        "#" + "=" * 79 + "\n"
    )

    for min_stack, promotion in SUPPLY_STACK_THRESHOLDS:
        for name in SUPPLY_CURRENCIES:
            base = _find_currency_tier(name, mode)
            promoted = _promote_tier(base, promotion)
            blocks.append(make_show_block(
                comment=f"{name} Stack>={min_stack} ({base}→{promoted})",
                conditions=[
                    'Class "Currency"',
                    f'BaseType == "{name}"',
                    f'StackSize >= {min_stack}',
                ],
                category="currency",
                tier=promoted,
                is_build_target=False,
            ))

    for min_stack, promotion in CURRENCY_STACK_THRESHOLDS:
        for tier_name in _TIER_ORDER[1:]:
            tier_items = tiers.get(tier_name, [])
            non_supply = [i for i in tier_items if i not in supply_set]
            if not non_supply:
                continue
            blocks.append(make_currency_stack_block(
                currency_names=non_supply,
                base_tier=tier_name,
                min_stack=min_stack,
                promotion=promotion,
            ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# 레벨링 커런시 (AreaLevel <= 67)
# ---------------------------------------------------------------------------

# 구조: {"items": list[str], "tier": str}
LEVELING_CURRENCIES: dict[str, dict] = {
    "high": {
        "items": ["Orb of Binding", "Orb of Chance"],
        "tier": "P3_USEFUL",
    },
    "mid": {
        "items": ["Orb of Alteration", "Orb of Transmutation"],
        "tier": "P4_SUPPORT",
    },
    "low": {
        "items": ["Armourer's Scrap", "Blacksmith's Whetstone", "Chromatic Orb"],
        "tier": "P4_SUPPORT",
    },
    "aug": {
        "items": ["Orb of Augmentation"],
        "tier": "P5_MINOR",
    },
}


def generate_leveling_currency_section() -> str:
    """레벨링 구간(AreaLevel <= 67) 커런시 하이라이트 섹션."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Leveling Currency (AreaLevel <= 67)\n"
        "#" + "=" * 79 + "\n"
    )

    for group_name, group in LEVELING_CURRENCIES.items():
        items = group["items"]
        tier = group["tier"]
        names_str = " ".join(f'"{n}"' for n in items)
        blocks.append(make_show_block(
            comment=f"Leveling {group_name} ({len(items)} types)",
            conditions=[
                'Class "Currency" "Stackable Currency"',
                f'BaseType == {names_str}',
                'AreaLevel <= 67',
            ],
            category="currency",
            tier=tier,
            is_build_target=False,
        ))

    blocks.append(make_show_block(
        comment="Leveling Portal Scroll",
        conditions=[
            'Class "Currency" "Stackable Currency"',
            'BaseType == "Portal Scroll"',
            'AreaLevel <= 67',
        ],
        category="currency",
        tier="P6_LOW",
        is_build_target=False,
    ))

    blocks.append(make_show_block(
        comment="Leveling Scroll of Wisdom",
        conditions=[
            'Class "Currency" "Stackable Currency"',
            'BaseType == "Scroll of Wisdom"',
            'AreaLevel <= 67',
        ],
        category="currency",
        tier="P6_LOW",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Lifeforce StackSize 6단계
# ---------------------------------------------------------------------------

LIFEFORCE_BASES = [
    "Primal Crystallised Lifeforce",
    "Vivid Crystallised Lifeforce",
    "Wild Crystallised Lifeforce",
]

LIFEFORCE_STACK_THRESHOLDS: list[tuple[int, str]] = [
    (4000, "P1_KEYSTONE"),
    (500,  "P2_CORE"),
    (250,  "P3_USEFUL"),
    (45,   "P4_SUPPORT"),
    (20,   "P5_MINOR"),
]


def generate_lifeforce_section() -> str:
    """Crystallised Lifeforce 스택 기반 6단계 섹션."""
    blocks: list[str] = []
    names_str = " ".join(f'"{n}"' for n in LIFEFORCE_BASES)

    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Lifeforce (Harvest)\n"
        "#" + "=" * 79 + "\n"
    )

    for min_stack, tier in LIFEFORCE_STACK_THRESHOLDS:
        blocks.append(make_show_block(
            comment=f"Lifeforce Stack>={min_stack} ({tier})",
            conditions=[
                'Class "Stackable Currency"',
                f'BaseType == {names_str}',
                f'StackSize >= {min_stack}',
            ],
            category="currency",
            tier=tier,
            is_build_target=False,
        ))

    blocks.append(make_show_block(
        comment="Lifeforce any (fallback)",
        conditions=[
            'Class "Stackable Currency"',
            f'BaseType == {names_str}',
        ],
        category="currency",
        tier="P6_LOW",
        is_build_target=False,
    ))

    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# 스플린터 StackSize (Breach/Legion/Simulacrum)
# ---------------------------------------------------------------------------

SPLINTER_HIGH = [
    "Splinter of Xoph", "Splinter of Tul", "Splinter of Esh",
    "Splinter of Uul-Netol", "Splinter of Chayula",
]

SPLINTER_LOW = [
    "Timeless Eternal Empire Splinter", "Timeless Karui Splinter",
    "Timeless Maraketh Splinter", "Timeless Templar Splinter",
    "Timeless Vaal Splinter",
]

SPLINTER_HIGH_THRESHOLDS: list[tuple[int, str]] = [
    (80, "P1_KEYSTONE"),
    (25, "P2_CORE"),
    (10, "P3_USEFUL"),
    (5,  "P4_SUPPORT"),
    (2,  "P5_MINOR"),
]

SPLINTER_LOW_THRESHOLDS: list[tuple[int, str]] = [
    (66, "P1_KEYSTONE"),
    (25, "P2_CORE"),
    (10, "P3_USEFUL"),
    (5,  "P4_SUPPORT"),
    (2,  "P5_MINOR"),
]

SIMULACRUM_THRESHOLDS: list[tuple[int, str]] = [
    (150, "P1_KEYSTONE"),
    (60,  "P2_CORE"),
    (20,  "P3_USEFUL"),
    (3,   "P4_SUPPORT"),
]


def _generate_splinter_blocks(
    names: list[str],
    thresholds: list[tuple[int, str]],
    label: str,
) -> list[str]:
    """스플린터 계열 스택 블록 생성."""
    blocks: list[str] = []
    names_str = " ".join(f'"{n}"' for n in names)
    for min_stack, tier in thresholds:
        blocks.append(make_show_block(
            comment=f"{label} Stack>={min_stack} ({tier})",
            conditions=[
                'Class "Stackable Currency"',
                f'BaseType == {names_str}',
                f'StackSize >= {min_stack}',
            ],
            category="fragment",
            tier=tier,
            is_build_target=False,
        ))
    blocks.append(make_show_block(
        comment=f"{label} single",
        conditions=[
            'Class "Stackable Currency"',
            f'BaseType == {names_str}',
        ],
        category="fragment",
        tier="P6_LOW",
        is_build_target=False,
    ))
    return blocks


def generate_splinter_section() -> str:
    """Breach/Legion/Simulacrum 스플린터 스택 기반 섹션."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Splinters (Breach/Legion/Simulacrum)\n"
        "#" + "=" * 79 + "\n"
    )

    blocks.extend(_generate_splinter_blocks(
        SPLINTER_HIGH, SPLINTER_HIGH_THRESHOLDS, "Breach Splinter"))
    blocks.extend(_generate_splinter_blocks(
        SPLINTER_LOW, SPLINTER_LOW_THRESHOLDS, "Legion Splinter"))
    blocks.extend(_generate_splinter_blocks(
        ["Simulacrum Splinter"], SIMULACRUM_THRESHOLDS, "Simulacrum"))

    return "\n".join(blocks)


# ===========================================================================
# Special Currency [[4000]] — Cobalt [4001]~[4008]
# ===========================================================================

# [4001] Vials
VIALS_T2 = [
    "Vial of Sacrifice", "Vial of Summoning",
    "Vial of the Ghost", "Vial of Transcendence",
]
VIALS_T3 = [
    "Vial of Awakening", "Vial of Consequence",
    "Vial of Dominance", "Vial of Fate", "Vial of the Ritual",
]

# [4002] Delirium Orbs
DELIRIUM_T2 = ["Skittering Delirium Orb"]
DELIRIUM_T3 = [
    "Abyssal Delirium Orb", "Armoursmith's Delirium Orb",
    "Blacksmith's Delirium Orb", "Blighted Delirium Orb",
    "Cartographer's Delirium Orb", "Diviner's Delirium Orb",
    "Fine Delirium Orb", "Fossilised Delirium Orb",
    "Fragmented Delirium Orb", "Jeweller's Delirium Orb",
    "Singular Delirium Orb", "Thaumaturge's Delirium Orb",
    "Timeless Delirium Orb", "Whispering Delirium Orb",
]

# [4003] Fossils & Resonators
FOSSIL_T1 = ["Faceted Fossil", "Hollow Fossil"]
FOSSIL_T2 = [
    "Fractured Fossil", "Glyphic Fossil",
    "Prime Chaotic Resonator", "Sanctified Fossil",
]
FOSSIL_T3 = ["Shuddering Fossil"]
FOSSIL_T4 = [
    "Corroded Fossil", "Fundamental Fossil",
    "Potent Chaotic Resonator", "Powerful Chaotic Resonator",
    "Primitive Chaotic Resonator", "Tangled Fossil",
]
FOSSIL_T5 = [
    "Aberrant Fossil", "Aetheric Fossil", "Bloodstained Fossil",
    "Bound Fossil", "Deft Fossil", "Dense Fossil", "Frigid Fossil",
    "Gilded Fossil", "Jagged Fossil", "Lucent Fossil",
    "Metallic Fossil", "Opulent Fossil", "Prismatic Fossil",
    "Pristine Fossil", "Scorched Fossil", "Serrated Fossil",
]
FOSSIL_EXHIDE = [
    "Aberrant Fossil", "Aetheric Fossil", "Bloodstained Fossil",
    "Bound Fossil", "Corroded Fossil", "Deft Fossil", "Dense Fossil",
    "Faceted Fossil", "Fractured Fossil", "Frigid Fossil",
    "Fundamental Fossil", "Gilded Fossil", "Glyphic Fossil",
    "Hollow Fossil", "Jagged Fossil", "Lucent Fossil",
    "Metallic Fossil", "Opulent Fossil",
    "Potent Chaotic Resonator", "Powerful Chaotic Resonator",
    "Prime Chaotic Resonator", "Primitive Chaotic Resonator",
    "Prismatic Fossil", "Pristine Fossil", "Sanctified Fossil",
    "Scorched Fossil", "Serrated Fossil", "Shuddering Fossil",
    "Tangled Fossil",
]

# [4004] Oils
OIL_T1 = ["Golden Oil", "Prismatic Oil", "Tainted Oil"]
OIL_T2 = ["Opalescent Oil", "Silver Oil"]
OIL_T3 = [
    "Black Oil", "Crimson Oil", "Indigo Oil",
    "Reflective Oil", "Violet Oil",
]
OIL_T4 = ["Amber Oil", "Azure Oil", "Teal Oil", "Verdant Oil"]
OIL_T5 = ["Clear Oil", "Sepia Oil"]
OIL_EXHIDE = [
    "Amber Oil", "Azure Oil", "Black Oil", "Clear Oil", "Crimson Oil",
    "Golden Oil", "Indigo Oil", "Opalescent Oil", "Prismatic Oil",
    "Reflective Oil", "Sepia Oil", "Silver Oil", "Tainted Oil",
    "Teal Oil", "Verdant Oil", "Violet Oil",
]

# [4005] Runes/Runegrafts
RUNE_T1 = ["Runegraft of Gemcraft"]
RUNE_T2 = [
    "Runegraft of Connection", "Runegraft of Consecration",
    "Runegraft of Fury", "Runegraft of Rallying",
    "Runegraft of Resurgence", "Runegraft of Rotblood",
    "Runegraft of Suffering", "Runegraft of the Agile",
    "Runegraft of the Angler", "Runegraft of the Fortress",
    "Runegraft of the Imbued", "Runegraft of the Spellbound",
]
RUNE_T3 = [
    "Runegraft of the Soulwick", "Runegraft of the Warp",
    "Runegraft of the Witchmark",
]
RUNE_T4 = [
    "Runegraft of Refraction", "Runegraft of Stability",
    "Runegraft of Treachery",
]
RUNE_T5 = [
    "Runegraft of Bellows", "Runegraft of Blasphemy",
    "Runegraft of Loyalty", "Runegraft of Quaffing",
    "Runegraft of Restitching", "Runegraft of the Bound",
    "Runegraft of the Combatant", "Runegraft of the Jeweller",
    "Runegraft of the Novamark", "Runegraft of the River",
    "Runegraft of the Sinistral", "Runegraft of Time",
]

# [4006] Corpses
CORPSE_T1 = ["Perfect Forest Tiger", "Perfect Warlord"]
CORPSE_T2 = [
    "Perfect Adherent of Zarokh", "Perfect Astral Lich",
    "Perfect Blasphemer", "Perfect Blood Demon",
    "Perfect Conjuror of Rot", "Perfect Dancing Sword",
    "Perfect Dark Marionette", "Perfect Dark Reaper",
    "Perfect Druidic Alchemist", "Perfect Eldritch Eye",
    "Perfect Fiery Cannibal", "Perfect Forest Warrior",
    "Perfect Frozen Cannibal", "Perfect Guardian Turtle",
    "Perfect Half-remembered Goliath", "Perfect Hulking Miscreation",
    "Perfect Hydra", "Perfect Judgemental Spirit",
    "Perfect Meatsack", "Perfect Naval Officer",
    "Perfect Needle Horror", "Perfect Pain Artist",
    "Perfect Primal Demiurge", "Perfect Primal Thunderbird",
    "Perfect Runic Skeleton", "Perfect Sanguimancer Demon",
    "Perfect Sawblade Horror", "Perfect Serpent Warrior",
    "Perfect Shadow Construct", "Perfect Slashing Horror",
    "Perfect Spider Matriarch", "Perfect Spirit of Fortune",
]
CORPSE_T3 = [
    "Adherent of Zarokh", "Astral Lich", "Blasphemer", "Blood Demon",
    "Conjuror of Rot", "Dancing Sword", "Dark Marionette", "Dark Reaper",
    "Druidic Alchemist", "Eldritch Eye", "Fiery Cannibal",
    "Forest Tiger", "Forest Warrior", "Frozen Cannibal",
    "Guardian Turtle", "Half-remembered Goliath",
    "Hulking Miscreation", "Hydra",
    "Imperfect Adherent of Zarokh", "Imperfect Astral Lich",
    "Imperfect Conjuror of Rot", "Judgemental Spirit",
    "Meatsack", "Naval Officer", "Needle Horror", "Pain Artist",
    "Primal Demiurge", "Primal Thunderbird", "Runic Skeleton",
    "Sanguimancer Demon", "Sawblade Horror", "Serpent Warrior",
    "Shadow Construct", "Slashing Horror", "Spider Matriarch",
    "Spirit of Fortune", "Warlord",
]
CORPSE_T4 = [
    "Imperfect Blasphemer", "Imperfect Blood Demon",
    "Imperfect Dancing Sword", "Imperfect Dark Marionette",
    "Imperfect Dark Reaper", "Imperfect Druidic Alchemist",
    "Imperfect Eldritch Eye", "Imperfect Fiery Cannibal",
    "Imperfect Forest Tiger", "Imperfect Forest Warrior",
    "Imperfect Frozen Cannibal", "Imperfect Guardian Turtle",
    "Imperfect Half-remembered Goliath",
    "Imperfect Hulking Miscreation", "Imperfect Hydra",
    "Imperfect Judgemental Spirit", "Imperfect Meatsack",
    "Imperfect Naval Officer", "Imperfect Needle Horror",
    "Imperfect Pain Artist", "Imperfect Primal Demiurge",
    "Imperfect Primal Thunderbird", "Imperfect Runic Skeleton",
    "Imperfect Sanguimancer Demon", "Imperfect Sawblade Horror",
    "Imperfect Serpent Warrior", "Imperfect Shadow Construct",
    "Imperfect Slashing Horror", "Imperfect Spider Matriarch",
    "Imperfect Spirit of Fortune", "Imperfect Warlord",
]

# [4007] Essences
ESSENCE_T2 = [
    "Deafening Essence of Anger", "Deafening Essence of Anguish",
    "Deafening Essence of Contempt", "Deafening Essence of Doubt",
    "Deafening Essence of Dread", "Deafening Essence of Envy",
    "Deafening Essence of Fear", "Deafening Essence of Greed",
    "Deafening Essence of Hatred", "Deafening Essence of Loathing",
    "Deafening Essence of Misery", "Deafening Essence of Rage",
    "Deafening Essence of Scorn", "Deafening Essence of Sorrow",
    "Deafening Essence of Spite", "Deafening Essence of Suffering",
    "Deafening Essence of Torment", "Deafening Essence of Woe",
    "Deafening Essence of Wrath", "Deafening Essence of Zeal",
    "Essence of Delirium", "Essence of Desolation",
    "Essence of Horror", "Essence of Hysteria", "Essence of Insanity",
]
ESSENCE_T3 = [
    "Shrieking Essence of Anger", "Shrieking Essence of Anguish",
    "Shrieking Essence of Contempt", "Shrieking Essence of Doubt",
    "Shrieking Essence of Dread", "Shrieking Essence of Envy",
    "Shrieking Essence of Fear", "Shrieking Essence of Greed",
    "Shrieking Essence of Hatred", "Shrieking Essence of Loathing",
    "Shrieking Essence of Misery", "Shrieking Essence of Rage",
    "Shrieking Essence of Scorn", "Shrieking Essence of Sorrow",
    "Shrieking Essence of Spite", "Shrieking Essence of Suffering",
    "Shrieking Essence of Torment", "Shrieking Essence of Woe",
    "Shrieking Essence of Wrath", "Shrieking Essence of Zeal",
]
ESSENCE_T4 = [
    "Remnant of Corruption",
    "Screaming Essence of Anger", "Screaming Essence of Anguish",
    "Screaming Essence of Contempt", "Screaming Essence of Doubt",
    "Screaming Essence of Dread", "Screaming Essence of Envy",
    "Screaming Essence of Fear", "Screaming Essence of Greed",
    "Screaming Essence of Hatred", "Screaming Essence of Loathing",
    "Screaming Essence of Misery", "Screaming Essence of Rage",
    "Screaming Essence of Scorn", "Screaming Essence of Sorrow",
    "Screaming Essence of Spite", "Screaming Essence of Suffering",
    "Screaming Essence of Torment", "Screaming Essence of Woe",
    "Screaming Essence of Wrath", "Screaming Essence of Zeal",
]
ESSENCE_T5 = [
    "Wailing Essence of Anger", "Wailing Essence of Anguish",
    "Wailing Essence of Contempt", "Wailing Essence of Doubt",
    "Wailing Essence of Fear", "Wailing Essence of Greed",
    "Wailing Essence of Hatred", "Wailing Essence of Loathing",
    "Wailing Essence of Rage", "Wailing Essence of Sorrow",
    "Wailing Essence of Spite", "Wailing Essence of Suffering",
    "Wailing Essence of Torment", "Wailing Essence of Woe",
    "Wailing Essence of Wrath", "Wailing Essence of Zeal",
]
ESSENCE_T6 = [
    "Muttering Essence of Anger", "Muttering Essence of Contempt",
    "Muttering Essence of Fear", "Muttering Essence of Greed",
    "Muttering Essence of Hatred", "Muttering Essence of Sorrow",
    "Muttering Essence of Torment", "Muttering Essence of Woe",
    "Weeping Essence of Anger", "Weeping Essence of Contempt",
    "Weeping Essence of Doubt", "Weeping Essence of Fear",
    "Weeping Essence of Greed", "Weeping Essence of Hatred",
    "Weeping Essence of Rage", "Weeping Essence of Sorrow",
    "Weeping Essence of Suffering", "Weeping Essence of Torment",
    "Weeping Essence of Woe", "Weeping Essence of Wrath",
    "Whispering Essence of Contempt", "Whispering Essence of Greed",
    "Whispering Essence of Hatred", "Whispering Essence of Woe",
]

# [4008] Omens
OMEN_T1 = [
    "Omen of Amelioration", "Omen of Blanching",
    "Omen of Connections", "Omen of Fortune",
]
OMEN_T2 = ["Omen of Brilliance"]
OMEN_T4 = ["Omen of Death-dancing", "Omen of the Jeweller"]
OMEN_T5 = [
    "Omen of Adrenaline", "Omen of Death's Door",
    "Omen of Refreshment", "Omen of Return",
    "Omen of the Soul Devourer",
]

# [4008] Tattoos
TATTOO_T1 = [
    "Journey Tattoo of the Body", "Journey Tattoo of the Mind",
    "Tattoo of the Arohongui Shaman",
    "Tattoo of the Ngamahu Warmonger",
    "Tattoo of the Ramako Shaman",
    "Tattoo of the Valako Shieldbearer",
]
TATTOO_T2 = [
    "Journey Tattoo of the Soul",
    "Tattoo of the Arohongui Moonwarden",
    "Tattoo of the Arohongui Scout",
    "Tattoo of the Arohongui Warmonger",
    "Tattoo of the Arohongui Warrior",
    "Tattoo of the Hinekora Storyteller",
    "Tattoo of the Hinekora Warrior",
    "Tattoo of the Ngamahu Firewalker",
    "Tattoo of the Ramako Fleetfoot",
    "Tattoo of the Rongokurai Turtle",
    "Tattoo of the Tawhoa Shaman",
]
TATTOO_T3 = [
    "Tattoo of the Hinekora Warmonger",
    "Tattoo of the Ngamahu Shaman",
    "Tattoo of the Ngamahu Warrior",
    "Tattoo of the Ngamahu Woodcarver",
    "Tattoo of the Tukohama Warcaller",
    "Tattoo of the Valako Scout",
    "Tattoo of the Valako Shaman",
    "Tattoo of the Valako Stormrider",
    "Tattoo of the Valako Warrior",
]
TATTOO_T4 = [
    "Tattoo of the Hinekora Deathwarden",
    "Tattoo of the Hinekora Shaman",
    "Tattoo of the Kitava Blood Drinker",
    "Tattoo of the Kitava Heart Eater",
    "Tattoo of the Kitava Rebel",
    "Tattoo of the Kitava Shaman",
    "Tattoo of the Kitava Warrior",
    "Tattoo of the Ramako Archer",
    "Tattoo of the Ramako Scout",
    "Tattoo of the Ramako Sniper",
    "Tattoo of the Rongokurai Brute",
    "Tattoo of the Rongokurai Goliath",
    "Tattoo of the Rongokurai Guard",
    "Tattoo of the Rongokurai Warrior",
    "Tattoo of the Tasalio Bladedancer",
    "Tattoo of the Tasalio Scout",
    "Tattoo of the Tasalio Shaman",
    "Tattoo of the Tasalio Tideshifter",
    "Tattoo of the Tasalio Warrior",
    "Tattoo of the Tawhoa Herbalist",
    "Tattoo of the Tawhoa Naturalist",
    "Tattoo of the Tawhoa Scout",
    "Tattoo of the Tawhoa Warrior",
    "Tattoo of the Tukohama Brawler",
    "Tattoo of the Tukohama Shaman",
    "Tattoo of the Tukohama Warmonger",
    "Tattoo of the Tukohama Warrior",
]


def generate_special_currency_section() -> str:
    """Cobalt [[4000]] Special Currency — Vials/DeliriumOrbs/Fossils/Oils/
    Runes/Corpses/Essences/Omens/Tattoos."""
    blocks: list[str] = []
    blocks.append(
        "#" + "=" * 79 + "\n"
        "# PathcraftAI Special Currency [[4000]]\n"
        "#" + "=" * 79 + "\n"
    )

    cls_sc = 'Class == "Stackable Currency"'

    # --- [4001] Vials (t1 empty in Cobalt) ---
    for tier_items, ptier, label in [
        (VIALS_T2, "P2_CORE",   "Vials T2"),
        (VIALS_T3, "P3_USEFUL", "Vials T3"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block("Vials restex", [cls_sc, 'BaseType "Vial of"']))

    # --- [4002] Delirium Orbs ---
    for tier_items, ptier, label in [
        (DELIRIUM_T2, "P2_CORE",   "Delirium Orbs T2"),
        (DELIRIUM_T3, "P3_USEFUL", "Delirium Orbs T3"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block(
        "Delirium Orbs restex", [cls_sc, 'BaseType "Delirium Orb"'],
    ))

    # --- [4003] Fossils & Resonators ---
    cls_fossil = 'Class == "Delve Stackable Socketable Currency" "Stackable Currency"'
    for tier_items, ptier, label in [
        (FOSSIL_T1, "P1_KEYSTONE", "Fossil T1"),
        (FOSSIL_T2, "P2_CORE",     "Fossil T2"),
        (FOSSIL_T3, "P3_USEFUL",   "Fossil T3"),
        (FOSSIL_T4, "P4_SUPPORT",  "Fossil T4"),
        (FOSSIL_T5, "P5_MINOR",    "Fossil T5"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_fossil, f'BaseType == {_q(tier_items)}'],
            category="fragment", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_hide_block(
        "Fossil exhide",
        [cls_fossil, f'BaseType == {_q(FOSSIL_EXHIDE)}'],
    ))
    blocks.append(make_restex_block(
        "Fossil restex",
        [cls_fossil, 'BaseType "Fossil" "Resonator"'],
    ))

    # --- [4004] Oils ---
    for tier_items, ptier, label in [
        (OIL_T1, "P1_KEYSTONE", "Oil T1"),
        (OIL_T2, "P2_CORE",     "Oil T2"),
        (OIL_T3, "P3_USEFUL",   "Oil T3"),
        (OIL_T4, "P4_SUPPORT",  "Oil T4"),
        (OIL_T5, "P5_MINOR",    "Oil T5"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_hide_block(
        "Oil exhide",
        [cls_sc, f'BaseType == {_q(OIL_EXHIDE)}'],
    ))
    blocks.append(make_restex_block("Oil restex", [cls_sc, 'BaseType "Oil"']))

    # --- [4005] Runes/Runegrafts ---
    for tier_items, ptier, label in [
        (RUNE_T1, "P1_KEYSTONE", "Runegraft T1"),
        (RUNE_T2, "P2_CORE",     "Runegraft T2"),
        (RUNE_T3, "P3_USEFUL",   "Runegraft T3"),
        (RUNE_T4, "P4_SUPPORT",  "Runegraft T4"),
        (RUNE_T5, "P5_MINOR",    "Runegraft T5"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block(
        "Runegraft restex", [cls_sc, 'BaseType "Runegraft"'],
    ))

    # --- [4006] Corpses ---
    cls_corpse = 'Class == "Corpses"'
    for tier_items, ptier, label in [
        (CORPSE_T1, "P1_KEYSTONE", "Corpse T1"),
        (CORPSE_T2, "P2_CORE",     "Corpse T2"),
        (CORPSE_T3, "P3_USEFUL",   "Corpse T3"),
        (CORPSE_T4, "P4_SUPPORT",  "Corpse T4"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_corpse, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block("Corpse restex", [cls_corpse]))

    # --- [4007] Essences ---
    for tier_items, ptier, label in [
        (ESSENCE_T2, "P2_CORE",    "Essence T2"),
        (ESSENCE_T3, "P3_USEFUL",  "Essence T3"),
        (ESSENCE_T4, "P4_SUPPORT", "Essence T4"),
        (ESSENCE_T5, "P5_MINOR",   "Essence T5"),
        (ESSENCE_T6, "P6_LOW",     "Essence T6"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_hide_block(
        "Essence exhide",
        [cls_sc, 'BaseType "Essence of" "Remnant of Corruption"'],
    ))
    blocks.append(make_restex_block(
        "Essence restex", [cls_sc, 'BaseType "Essence of"'],
    ))

    # --- [4008] Omens ---
    for tier_items, ptier, label in [
        (OMEN_T1, "P1_KEYSTONE", "Omen T1"),
        (OMEN_T2, "P2_CORE",     "Omen T2"),
        (OMEN_T4, "P4_SUPPORT",  "Omen T4"),
        (OMEN_T5, "P5_MINOR",    "Omen T5"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block(
        "Omen restex", [cls_sc, 'BaseType "Omen of"'],
    ))

    # --- [4008] Tattoos ---
    for tier_items, ptier, label in [
        (TATTOO_T1, "P1_KEYSTONE", "Tattoo T1"),
        (TATTOO_T2, "P2_CORE",     "Tattoo T2"),
        (TATTOO_T3, "P3_USEFUL",   "Tattoo T3"),
        (TATTOO_T4, "P4_SUPPORT",  "Tattoo T4"),
    ]:
        blocks.append(make_show_block(
            comment=f"{label} [{len(tier_items)}]",
            conditions=[cls_sc, f'BaseType == {_q(tier_items)}'],
            category="currency", tier=ptier, is_build_target=False,
        ))
    blocks.append(make_restex_block(
        "Tattoo restex", [cls_sc, 'BaseType "Tattoo of"'],
    ))

    return "\n".join(blocks)
