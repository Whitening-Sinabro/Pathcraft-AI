# -*- coding: utf-8 -*-
"""PathcraftAI Aurora Glow — 코어 빌딩 블록 + 엄격도 시스템.

Show/Hide 블록 생성 함수, 티어 승격, 엄격도 패턴 매칭 등
모든 섹션 모듈이 공유하는 기반 기능.
"""

from pathcraft_palette import (
    CATEGORY_COLORS, CATEGORY_SHAPES, CATEGORY_BG_TINTS,
    FONT_SIZES, ALERT_SOUNDS, GOLD_STACK_FONTS,
    SIGNATURE_EFFECT, SIGNATURE_ICON_COLOR, KEYSTONE_BG,
    TIER_BG_ALPHA,
    VALID_MODES, DEFAULT_MODE,
    get_color, get_shape, get_bg_color, get_border_color, get_currency_tiers,
    _brighten_color, _ICON_SIZE_BY_TIER,
)

# Explicit __all__ to ensure underscore-prefixed helpers are re-exported
# by `from sections_core import *` in the facade.
__all__ = [
    # Strictness
    "STRICTNESS_LEVELS", "STRICTNESS_REMOVE_PATTERNS", "STRICTNESS_HIDE_PATTERNS",
    "apply_strictness",
    # Tier system
    "_TIER_ORDER", "_promote_tier", "_find_currency_tier",
    "CURRENCY_STACK_THRESHOLDS", "SUPPLY_STACK_THRESHOLDS", "SUPPLY_CURRENCIES",
    # Block builders
    "make_show_block", "make_gold_block", "make_restex_block", "make_hide_block",
    "make_currency_stack_block",
    # RestEx constants
    "RESTEX_TEXT", "RESTEX_BORDER", "RESTEX_BG", "RESTEX_FONT",
    "RESTEX_SOUND", "RESTEX_EFFECT",
    # Helper
    "_q",
]


# ---------------------------------------------------------------------------
# 엄격도 시스템 — Cobalt 5단계 diff 기반
# ---------------------------------------------------------------------------
# 0=Regular, 1=Strict, 2=VeryStrict, 3=UberStrict, 4=UberPlus
# 각 패턴은 "이 문자열이 Show 블록 주석에 포함되면 해당 엄격도 이상에서 제거"

STRICTNESS_LEVELS = {
    "regular": 0,
    "strict": 1,
    "verystrict": 2,
    "uberstrict": 3,
    "uberplus": 4,
}

# (min_strictness, comment_pattern) — 이 패턴이 블록 주석에 포함되면
# min_strictness 이상에서 해당 Show 블록을 제거(주석 처리)
# Cobalt 5파일 diff에서 추출한 전환 데이터
STRICTNESS_REMOVE_PATTERNS: list[tuple[int, str]] = [
    # === Strict (1) 이상에서 제거 ===
    (1, "Weapon Prog"),       # 무기 진행 15단계
    (1, "Wand Prog"),         # 완드 진행
    (1, "Leveling RGB"),      # 레벨링 RGB
    (1, "Leveling Phys Quivers"),
    (1, "Leveling Fire Resist"),
    (1, "Leveling Crafting Bases"),
    (1, "Leveling Minion Wands"),
    (1, "Leveling Act2"),
    (1, "Outdated Rare"),     # 아웃레벨 레어 (underlevel)
    (1, "Leveling Normal Body"),
    (1, "Leveling First Areas"),
    (1, "RGB 2x2"),           # 엔드게임 RGB
    (1, "RGB 1xN"),

    # === VeryStrict (2) 이상에서 제거 ===
    (2, "Leveling 3-Link"),
    (2, "Leveling 3-Socket"),
    (2, "5-Link Endgame"),
    (2, "6-Socket Height"),
    (2, "Crucible"),
    (2, "Remaining Rare"),

    # === UberStrict (3) 이상에서 제거 ===
    (3, "Leveling Rare"),      # 모든 레벨링 레어
    (3, "Leveling MS Boots"),
    (3, "Leveling Veiled"),
    (3, "Leveling 4-Link"),
    (3, "Leveling Act1"),
    (3, "5-Link"),             # 5링크 전부
    (3, "Crafting Matrix"),
    (3, "Chancing"),
    (3, "Memory Strand T1 (>= 1)"),
    (3, "Memory Strand Any"),
    (3, "Cluster Large any"),
    (3, "Cluster Medium any"),
    (3, "Cluster Small any"),
    (3, "Endgame Rare"),       # 엔드게임 레어 전반

    # === UberPlus (4) 이상에서 제거 ===
    (4, "ID Mod"),             # ID 모드 전부
    (4, "Exotic Mods"),        # 이국적 모드
    (4, "Scarab T5"),
    (4, "Scarab T6"),
    (4, "Idol"),               # 아이돌 매직
    (4, "Cluster T1"),
    (4, "Cluster Large Optimal"),
    (4, "Cluster Medium Optimal"),
    (4, "Perfection Any Q26"),
]

# (min_strictness, comment_pattern) — Show → Hide로 전환
STRICTNESS_HIDE_PATTERNS: list[tuple[int, str]] = [
    # === Strict (1) 이상에서 Hide ===
    (1, "커런시 스택>=3 (P6_LOW"),  # 보급품 3x 스택 (Wisdom, Portal)
    (1, "Scroll of Wisdom Stack>=3"),
    (1, "Portal Scroll Stack>=3"),

    # === VeryStrict (2) 이상에서 Hide ===
    (2, "Div Card fallback"),
    (2, "Scroll of Wisdom Stack>=5"),
    (2, "Portal Scroll Stack>=5"),

    # === UberStrict (3) 이상에서 Hide ===
    (3, "Leveling Scroll of Wisdom"),
    (3, "Leveling Portal Scroll"),
    (3, "Lifeforce any (fallback)"),

    # === UberPlus (4) 이상에서 Hide ===
    (4, "Scarab T5"),
    (4, "Scarab T6"),
    (4, "Fragment any (fallback)"),
    (4, "Gem any (fallback)"),
]


def apply_strictness(filter_content: str, strictness: int = 0) -> str:
    """필터 내용에 엄격도를 적용.

    strictness 0 = Regular (변경 없음)
    strictness 1 = Strict
    strictness 2 = Very Strict
    strictness 3 = Uber Strict
    strictness 4 = Uber+ Strict

    Show 블록을 주석 주석 패턴 매칭으로 제거하거나 Hide로 전환.
    """
    if strictness <= 0:
        return filter_content

    lines = filter_content.split("\n")
    result: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Show 블록 시작 감지
        if line.startswith("Show # PathcraftAI"):
            comment = line

            # 블록 전체 수집
            block_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("\t"):
                block_lines.append(lines[i])
                i += 1

            # 제거 패턴 체크
            removed = False
            for min_s, pattern in STRICTNESS_REMOVE_PATTERNS:
                if strictness >= min_s and pattern in comment:
                    # 블록 제거 (주석 처리)
                    removed = True
                    break

            if removed:
                continue  # 블록 스킵

            # Hide 전환 패턴 체크
            hidden = False
            for min_s, pattern in STRICTNESS_HIDE_PATTERNS:
                if strictness >= min_s and pattern in comment:
                    hidden = True
                    break

            if hidden:
                # Show → Hide 전환
                block_lines[0] = block_lines[0].replace("Show #", "Hide #", 1)
                # 사운드/이펙트/아이콘 제거
                block_lines = [
                    bl for bl in block_lines
                    if not any(kw in bl for kw in
                               ["PlayAlertSound", "PlayEffect",
                                "MinimapIcon"])
                ]
                block_lines.append("\tDisableDropSound True")

            result.extend(block_lines)
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


# ---------------------------------------------------------------------------
# 티어 승격 시스템
# ---------------------------------------------------------------------------

_TIER_ORDER = ("P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
               "P4_SUPPORT", "P5_MINOR", "P6_LOW")

# 일반 커런시: (min_stack, 승격 단계) — 내림차순
CURRENCY_STACK_THRESHOLDS: list[tuple[int, int]] = [
    (6, 2),
    (3, 1),
]

# 보급품 4종 전용
SUPPLY_STACK_THRESHOLDS: list[tuple[int, int]] = [
    (10, 3),
    (5,  2),
    (3,  1),
]

SUPPLY_CURRENCIES: list[str] = [
    "Orb of Transmutation",
    "Orb of Augmentation",
    "Portal Scroll",
    "Scroll of Wisdom",
]


def _promote_tier(base_tier: str, levels: int) -> str:
    """티어를 N단계 승격. P1 이상 불가."""
    if base_tier not in _TIER_ORDER:
        return base_tier
    idx = _TIER_ORDER.index(base_tier)
    return _TIER_ORDER[max(0, idx - levels)]


def _find_currency_tier(currency_name: str, mode: str = DEFAULT_MODE) -> str:
    """커런시의 기본 티어를 모드별 매핑에서 찾음."""
    tiers = get_currency_tiers(mode)
    for tier_name, items in tiers.items():
        if currency_name in items:
            return tier_name
    return "P6_LOW"


# ---------------------------------------------------------------------------
# Show/Hide 블록 생성 — Aurora Glow 스타일
# ---------------------------------------------------------------------------

def make_show_block(
    comment: str,
    conditions: list[str],
    category: str,
    tier: str = "P2_CORE",
    keystone: bool = False,
    is_build_target: bool = True,
) -> str:
    """PathcraftAI Aurora Glow Show 블록 생성."""
    color = get_color(category, tier)
    shape = get_shape(category)
    font = FONT_SIZES.get(tier, FONT_SIZES["P2_CORE"])
    sound = ALERT_SOUNDS.get(tier)

    if category == "gold":
        is_build_target = False

    if keystone:
        border = _brighten_color(KEYSTONE_BG, l_boost=0.35, s_boost=0.15)
        bg = f"{KEYSTONE_BG} 240"
    else:
        border = get_border_color(category, tier)
        bg = get_bg_color(category, tier)

    lines = [f"Show # PathcraftAI: {comment}"]
    for cond in conditions:
        lines.append(f"\t{cond}")
    lines.append(f"\tSetFontSize {font}")
    lines.append(f"\tSetTextColor {color} 255")
    lines.append(f"\tSetBorderColor {border} 255")
    lines.append(f"\tSetBackgroundColor {bg}")
    if sound:
        lines.append(f"\tPlayAlertSound {sound}")
    if is_build_target:
        lines.append(f"\tPlayEffect {SIGNATURE_EFFECT}")
        icon_size = _ICON_SIZE_BY_TIER.get(tier, 1)
        lines.append(f"\tMinimapIcon {icon_size} {SIGNATURE_ICON_COLOR} {shape}")
    lines.append("")
    return "\n".join(lines)


def make_gold_block(min_stack: int, font: int) -> str:
    """Gold 드랍 StackSize 기반 Show 블록. 보더 없음."""
    gold_color = CATEGORY_COLORS["gold"]
    gold_bg = get_bg_color("gold", "P4_SUPPORT")
    return "\n".join([
        f"Show # PathcraftAI: Gold Stack >= {min_stack}",
        f'\tBaseType == "Gold"',
        f"\tStackSize >= {min_stack}",
        f"\tSetFontSize {font}",
        f"\tSetTextColor {gold_color} 255",
        f"\tSetBackgroundColor {gold_bg}",
        f"\tMinimapIcon 2 Yellow {CATEGORY_SHAPES['gold']}",
        "",
    ])


# ---------------------------------------------------------------------------
# RestEx 안전망
# ---------------------------------------------------------------------------

RESTEX_TEXT = "255 0 255"
RESTEX_BORDER = "255 0 255"
RESTEX_BG = "100 0 100 240"
RESTEX_FONT = 45
RESTEX_SOUND = "3 300"
RESTEX_EFFECT = "Pink"


def make_restex_block(comment: str, conditions: list[str]) -> str:
    """미분류 아이템 캐치올 Show 블록 (경고색)."""
    lines = [f"Show # PathcraftAI RestEx: {comment}"]
    for cond in conditions:
        lines.append(f"\t{cond}")
    lines.append(f"\tSetFontSize {RESTEX_FONT}")
    lines.append(f"\tSetTextColor {RESTEX_TEXT} 255")
    lines.append(f"\tSetBorderColor {RESTEX_BORDER} 255")
    lines.append(f"\tSetBackgroundColor {RESTEX_BG}")
    lines.append(f"\tPlayAlertSound {RESTEX_SOUND}")
    lines.append(f"\tPlayEffect {RESTEX_EFFECT}")
    lines.append(f"\tMinimapIcon 0 Pink Circle")
    lines.append("")
    return "\n".join(lines)


def make_hide_block(comment: str, conditions: list[str]) -> str:
    """Hide 블록 생성."""
    lines = [f"Hide # PathcraftAI: {comment}"]
    for cond in conditions:
        lines.append(f"\t{cond}")
    lines.append("\tSetFontSize 18")
    lines.append("\tSetBorderColor 0 0 0 0")
    lines.append("\tSetBackgroundColor 20 20 0 0")
    lines.append("\tDisableDropSound True")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 커런시 스택 블록
# ---------------------------------------------------------------------------

def make_currency_stack_block(
    currency_names: list[str],
    base_tier: str,
    min_stack: int,
    promotion: int,
) -> str:
    """스택 >= min_stack 일 때 승격된 티어로 커런시 Show 블록 생성."""
    promoted = _promote_tier(base_tier, promotion)
    names_str = " ".join(f'"{n}"' for n in currency_names)
    return make_show_block(
        comment=f"커런시 스택>={min_stack} ({base_tier}→{promoted})",
        conditions=[
            'Class "Currency" "Stackable Currency"',
            f'BaseType == {names_str}',
            f'StackSize >= {min_stack}',
        ],
        category="currency",
        tier=promoted,
        is_build_target=False,
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _q(names: list[str]) -> str:
    """Return space-joined double-quoted BaseType string."""
    return " ".join(f'"{n}"' for n in names)
