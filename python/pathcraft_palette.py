# -*- coding: utf-8 -*-
"""PathcraftAI Aurora Glow Palette — loot filter overlay style constants.

설계 원칙 (Aurora Glow):
1. 카테고리 색은 Sanavi/NeverSink 네이티브와 구분되는 독자 팔레트 (Aurora 테마)
2. Dark Tint 배경: 카테고리별 어두운 틴트 배경 — 오로라가 밤하늘 위에서 빛나는 느낌.
   상위 티어일수록 배경 glow가 강해지고 (높은 alpha), 하위는 배경이 거의 사라짐.
3. Edge Glow 보더: 보더는 텍스트보다 밝은 톤 — 빛의 테두리 효과.
   NeverSink의 "보더 = 텍스트색" 컨벤션 탈피.
4. PathcraftAI 시그니처 = PlayEffect Cyan + MinimapIcon Cyan
5. 사운드: Sanavi 관례 유지
6. 아이콘 shape: PathcraftAI 독자 매핑
7. P1 = 45 (max), P2~P6 점진 감소 (42→34). 가치 구분은 색 + 배경 glow + 폰트.
8. Gold 카테고리는 시그니처 VFX 제외 (빌드 타겟 아닌 드랍 자원)
"""

import colorsys

# ---------------------------------------------------------------------------
# 카테고리 색 — Aurora 팔레트
# ---------------------------------------------------------------------------
# 각 값은 "R G B" 형식 문자열 (POE 필터 문법 그대로 삽입 가능)

CATEGORY_COLORS: dict[str, str] = {
    "gold":      "255 240 150",  # Lemonade     — POE Kingsmarch Gold 드랍
    "currency":  "255 64 120",   # Hot Coral    — Mirror/Divine/Chaos 오브
    "unique":    "255 150 50",   # Tangerine    — 유니크 아이템
    "divcard":   "200 100 255",  # Electric Lavender — 디비니 카드
    "gem":       "150 255 100",  # Chartreuse   — 스킬/서포트 젬
    "base":      "100 220 255",  # Turquoise    — 크래프팅/Chanceable 베이스
    "jewel":     "255 140 200",  # Bubblegum    — 쥬얼
    "fragment":  "230 200 255",  # Lavender Mist — 맵 프래그먼트
    "links":     "255 50 50",    # Crimson      — 6링크/5링크 고가 아이템
}

# ---------------------------------------------------------------------------
# 티어별 색 그라데이션 — 각 카테고리별로 P1~P6 톤 이동
# ---------------------------------------------------------------------------

CURRENCY_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "255 64 120",   # Hot Coral
    "P2_CORE":     "255 100 100",  # Coral Red
    "P3_USEFUL":   "255 140 70",   # Orange-Red
    "P4_SUPPORT":  "230 90 95",    # Faded Coral
    "P5_MINOR":    "200 80 85",    # Dim Coral
    "P6_LOW":      "170 70 75",    # Dark Coral
}

UNIQUE_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "255 150 50",   # Tangerine
    "P2_CORE":     "255 180 80",   # Bright Orange
    "P3_USEFUL":   "255 200 110",  # Peach
    "P4_SUPPORT":  "220 130 50",   # Warm Orange
    "P5_MINOR":    "190 110 45",   # Dim Orange
    "P6_LOW":      "160 95 40",    # Dark Orange
}

DIVCARD_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "200 100 255",  # Electric Lavender
    "P2_CORE":     "220 140 255",  # Light Lavender
    "P3_USEFUL":   "180 100 220",  # Violet
    "P4_SUPPORT":  "150 80 190",   # Muted Lavender
    "P5_MINOR":    "125 65 165",   # Dim Lavender
    "P6_LOW":      "105 55 140",   # Dark Lavender
}

GEM_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "150 255 100",  # Chartreuse
    "P2_CORE":     "180 255 120",  # Light Lime
    "P3_USEFUL":   "120 220 80",   # Grass Green
    "P4_SUPPORT":  "105 190 70",   # Forest Green
    "P5_MINOR":    "85 160 55",    # Dim Green
    "P6_LOW":      "70 135 45",    # Dark Green
}

BASE_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "100 220 255",  # Turquoise
    "P2_CORE":     "130 230 255",  # Sky Turquoise
    "P3_USEFUL":   "90 200 240",   # Steel Blue
    "P4_SUPPORT":  "75 175 215",   # Soft Turquoise
    "P5_MINOR":    "60 145 185",   # Dim Turquoise
    "P6_LOW":      "50 120 155",   # Dark Turquoise
}

JEWEL_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "255 140 200",  # Bubblegum
    "P2_CORE":     "255 170 220",  # Soft Pink
    "P3_USEFUL":   "230 120 180",  # Rose
    "P4_SUPPORT":  "210 110 170",  # Deep Rose
    "P5_MINOR":    "180 90 145",   # Dim Rose
    "P6_LOW":      "150 75 125",   # Dark Rose
}

LINKS_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "255 50 50",    # Crimson       — ilvl 85+ 6L
    "P2_CORE":     "255 90 70",    # Bright Red    — ilvl 83+ 6L
    "P3_USEFUL":   "235 75 60",    # Warm Red      — ilvl 76+ 6L
    "P4_SUPPORT":  "210 65 55",    # Faded Red     — ilvl 68+ 6L / 5L 상위
    "P5_MINOR":    "185 60 50",    # Dim Red       — 5L 일반
    "P6_LOW":      "160 55 45",    # Dark Red      — 6소켓
}

GOLD_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "255 240 150",  # Lemonade       — 5000+ 최상급 더미
    "P2_CORE":     "255 220 100",  # Bright Gold    — 2500+
    "P3_USEFUL":   "230 190 75",   # Warm Gold      — 1000+
    "P4_SUPPORT":  "200 160 60",   # Antique Gold   — 100+
    "P5_MINOR":    "170 135 50",   # Dim Gold       — 1+
    "P6_LOW":      "140 110 40",   # Dark Gold
}

FRAGMENT_TIER_COLORS: dict[str, str] = {
    "P1_KEYSTONE": "230 200 255",  # Lavender Mist
    "P2_CORE":     "210 180 240",  # Soft Lavender
    "P3_USEFUL":   "180 160 220",  # Dim Lavender
    "P4_SUPPORT":  "160 140 210",  # Soft Violet
    "P5_MINOR":    "135 115 185",  # Dim Violet
    "P6_LOW":      "115 100 165",  # Dark Violet
}

# 카테고리 → 티어 색 dict 매핑
TIER_COLORS_BY_CATEGORY: dict[str, dict[str, str]] = {
    "currency": CURRENCY_TIER_COLORS,
    "unique":   UNIQUE_TIER_COLORS,
    "divcard":  DIVCARD_TIER_COLORS,
    "gem":      GEM_TIER_COLORS,
    "base":     BASE_TIER_COLORS,
    "jewel":    JEWEL_TIER_COLORS,
    "fragment": FRAGMENT_TIER_COLORS,
    "links":    LINKS_TIER_COLORS,
    "gold":     GOLD_TIER_COLORS,
}


# ---------------------------------------------------------------------------
# 모드별 Currency 티어 매핑 (Trade / SSF / HCSSF)
# ---------------------------------------------------------------------------

CURRENCY_TIERS_TRADE: dict[str, list[str]] = {
    "P1_KEYSTONE": [
        "Mirror of Kalandra", "Mirror Shard",
        "Divine Orb", "Awakener's Orb", "Sacred Orb",
        "Hinekora's Lock", "Reflecting Mist",
    ],
    "P2_CORE": [
        "Exalted Orb", "Orb of Annulment",
        "Eldritch Chaos Orb", "Eldritch Orb of Annulment",
        "Crusader's Exalted Orb", "Hunter's Exalted Orb",
        "Redeemer's Exalted Orb", "Warlord's Exalted Orb",
        "Blessing of Chayula", "Blessing of Uul-Netol",
    ],
    "P3_USEFUL": [
        "Chaos Orb", "Regal Orb", "Vaal Orb",
        "Ancient Orb", "Orb of Alchemy",
        "Harbinger's Orb", "Orb of Scouring",
        "Tainted Chaos Orb", "Tainted Divine Teardrop",
    ],
    "P4_SUPPORT": [
        "Orb of Fusing", "Jeweller's Orb",
        "Cartographer's Chisel", "Blessed Orb",
        "Orb of Binding", "Orb of Horizons",
    ],
    "P5_MINOR": [
        "Chromatic Orb", "Glassblower's Bauble",
        "Orb of Chance", "Orb of Regret",
        "Orb of Alteration", "Gemcutter's Prism",
    ],
    "P6_LOW": [
        "Orb of Augmentation", "Orb of Transmutation",
        "Armourer's Scrap", "Blacksmith's Whetstone",
        "Scroll of Wisdom", "Portal Scroll",
        "Alchemy Shard", "Alteration Shard",
        "Regal Shard", "Chaos Shard",
    ],
}

CURRENCY_TIERS_SSF: dict[str, list[str]] = {
    "P1_KEYSTONE": [
        "Orb of Alchemy", "Chaos Orb", "Orb of Fusing",
        "Divine Orb", "Awakener's Orb",
        "Mirror of Kalandra",
    ],
    "P2_CORE": [
        "Exalted Orb", "Orb of Annulment", "Regal Orb",
        "Orb of Scouring", "Vaal Orb",
        "Harbinger's Orb", "Sacred Orb",
        "Ancient Orb",
    ],
    "P3_USEFUL": [
        "Blessed Orb", "Orb of Binding", "Jeweller's Orb",
        "Cartographer's Chisel", "Gemcutter's Prism",
        "Orb of Horizons", "Mirror Shard",
    ],
    "P4_SUPPORT": [
        "Orb of Chance", "Orb of Regret",
        "Exalted Shard", "Ancient Shard",
        "Annulment Shard", "Orb of Alteration",
    ],
    "P5_MINOR": [
        "Chromatic Orb", "Glassblower's Bauble",
        "Orb of Augmentation", "Blacksmith's Whetstone",
        "Armourer's Scrap", "Binding Shard",
    ],
    "P6_LOW": [
        "Orb of Transmutation", "Scroll of Wisdom", "Portal Scroll",
        "Alchemy Shard", "Alteration Shard", "Regal Shard",
        "Chaos Shard", "Scroll Fragment",
    ],
}

CURRENCY_TIERS_HCSSF: dict[str, list[str]] = {
    "P1_KEYSTONE": [
        "Orb of Alchemy", "Chaos Orb", "Orb of Fusing",
        "Orb of Scouring", "Orb of Annulment",
        "Awakener's Orb",
    ],
    "P2_CORE": [
        "Regal Orb", "Divine Orb",
        "Blessed Orb", "Vaal Orb",
        "Exalted Orb", "Harbinger's Orb",
        "Mirror of Kalandra",
    ],
    "P3_USEFUL": [
        "Orb of Binding", "Jeweller's Orb",
        "Cartographer's Chisel", "Sacred Orb",
        "Gemcutter's Prism", "Ancient Orb",
        "Orb of Horizons",
    ],
    "P4_SUPPORT": [
        "Orb of Chance", "Orb of Regret",
        "Exalted Shard", "Mirror Shard", "Ancient Shard",
        "Annulment Shard",
    ],
    "P5_MINOR": [
        "Chromatic Orb", "Glassblower's Bauble",
        "Orb of Alteration", "Orb of Augmentation",
        "Armourer's Scrap", "Blacksmith's Whetstone",
    ],
    "P6_LOW": [
        "Orb of Transmutation", "Scroll of Wisdom", "Portal Scroll",
        "Alchemy Shard", "Alteration Shard", "Regal Shard",
        "Chaos Shard",
    ],
}

CURRENCY_TIERS_BY_MODE: dict[str, dict[str, list[str]]] = {
    "trade": CURRENCY_TIERS_TRADE,
    "ssf":   CURRENCY_TIERS_SSF,
    "hcssf": CURRENCY_TIERS_HCSSF,
}

VALID_MODES = tuple(CURRENCY_TIERS_BY_MODE.keys())
DEFAULT_MODE = "ssf"


def get_currency_tiers(mode: str = DEFAULT_MODE) -> dict[str, list[str]]:
    """주어진 모드의 Currency P-tier → BaseType 리스트 반환."""
    if mode not in CURRENCY_TIERS_BY_MODE:
        raise ValueError(
            f"알 수 없는 모드: {mode!r}. 유효: {VALID_MODES}"
        )
    return CURRENCY_TIERS_BY_MODE[mode]


# ---------------------------------------------------------------------------
# 색 변환 유틸리티
# ---------------------------------------------------------------------------

def _rgb_string(r: float, g: float, b: float) -> str:
    """0~1 float RGB → POE 필터용 'R G B' 문자열."""
    return f"{int(round(r * 255))} {int(round(g * 255))} {int(round(b * 255))}"


def _parse_rgb_string(rgb_str: str) -> tuple[int, int, int]:
    """'255 64 120' → (255, 64, 120)."""
    parts = rgb_str.strip().split()
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def _make_dark_tint(rgb_str: str) -> str:
    """카테고리 시드 색 → 배경 틴트.

    Cobalt 참조: 배경이 완전 검정이 아니라 카테고리 색이 느껴지는 어두운 색.
    L=0.18, S=원본의 60%까지 유지 → 인게임에서 카테고리 식별 가능.
    """
    r8, g8, b8 = _parse_rgb_string(rgb_str)
    r, g, b = r8 / 255.0, g8 / 255.0, b8 / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    dark_l = 0.32
    dark_s = min(s, 0.65)
    nr, ng, nb = colorsys.hls_to_rgb(h, dark_l, dark_s)
    return _rgb_string(nr, ng, nb)


def _brighten_color(rgb_str: str, l_boost: float = 0.15, s_boost: float = 0.10) -> str:
    """티어 텍스트 색 → Edge Glow 보더 색 (텍스트보다 밝게)."""
    r8, g8, b8 = _parse_rgb_string(rgb_str)
    r, g, b = r8 / 255.0, g8 / 255.0, b8 / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    new_l = min(0.92, l + l_boost)
    new_s = min(1.0, s + s_boost)
    nr, ng, nb = colorsys.hls_to_rgb(h, new_l, new_s)
    return _rgb_string(nr, ng, nb)


# ---------------------------------------------------------------------------
# 시드 색 → 티어 그라데이션 생성 (유저 커스터마이징 기반)
# ---------------------------------------------------------------------------

def generate_tier_gradient(
    seed_rgb: str | tuple[int, int, int],
    n_tiers: int = 6,
    hue_shift: float = 0.04,
    lightness_drop: float = 0.25,
    saturation_drop: float = 0.35,
) -> dict[str, str]:
    """시드 RGB 색에서 P1~P6 티어 그라데이션 생성.

    Args:
        seed_rgb: 시드 색. "R G B" 문자열 또는 (R, G, B) 튜플 (0~255).
        n_tiers: 생성할 티어 수 (기본 6 = P1~P6).
        hue_shift: 티어당 hue 이동량.
        lightness_drop: P1→P_N 까지 lightness 총 감소량.
        saturation_drop: P1→P_N 까지 saturation 총 감소량.

    Returns:
        `{"P1_KEYSTONE": "r g b", "P2_CORE": "r g b", ...}` dict
    """
    if isinstance(seed_rgb, str):
        r8, g8, b8 = _parse_rgb_string(seed_rgb)
    else:
        r8, g8, b8 = seed_rgb

    r, g, b = r8 / 255.0, g8 / 255.0, b8 / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    p_tier_names = ("P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
                    "P4_SUPPORT", "P5_MINOR", "P6_LOW")[:n_tiers]

    result: dict[str, str] = {}
    for i, tier in enumerate(p_tier_names):
        factor = i / max(1, n_tiers - 1)
        new_h = (h + factor * hue_shift) % 1.0
        new_l = max(0.15, l - factor * lightness_drop)
        new_s = max(0.20, s - factor * saturation_drop)
        nr, ng, nb = colorsys.hls_to_rgb(new_h, new_l, new_s)
        result[tier] = _rgb_string(nr, ng, nb)
    return result


def generate_theme_palette(
    category_seeds: dict[str, str],
) -> dict[str, dict[str, str]]:
    """여러 카테고리의 시드 색을 받아서 전체 팔레트 생성.

    Args:
        category_seeds: 카테고리 이름 → 시드 RGB 문자열 dict.

    Returns:
        `{category: {tier: rgb_str}}` 이중 dict.
    """
    return {
        cat: generate_tier_gradient(seed)
        for cat, seed in category_seeds.items()
    }


# ---------------------------------------------------------------------------
# 카테고리별 사람이 읽기 쉬운 이름 (주석/로그용)
# ---------------------------------------------------------------------------

CATEGORY_NAMES: dict[str, str] = {
    "gold":     "Lemonade",
    "currency": "Hot Coral",
    "unique":   "Tangerine",
    "divcard":  "Electric Lavender",
    "gem":      "Chartreuse",
    "base":     "Turquoise",
    "jewel":    "Bubblegum",
    "fragment": "Lavender Mist",
    "links":    "Crimson",
}

# ---------------------------------------------------------------------------
# 아이콘 shape 매핑 — PathcraftAI 독자 정의
# ---------------------------------------------------------------------------
# NeverSink/Sanavi와 별개. 미니맵에서 카테고리 즉시 식별용.

CATEGORY_SHAPES: dict[str, str] = {
    "gold":     "Raindrop",   # 흐르는 재화
    "currency": "Diamond",    # 가치 있는 보석
    "unique":   "Star",       # 특별한 아이템
    "divcard":  "Moon",       # 점술/운명
    "gem":      "Hexagon",    # 결정 구조
    "base":     "Square",     # 견고한 기반
    "jewel":    "Kite",       # 작은 보석
    "fragment": "Cross",      # 조각/교차
    "links":    "Pentagon",   # 링크/소켓 특수
}

# ---------------------------------------------------------------------------
# 시그니처 — Cyan VFX (양쪽 베이스 필터 모두 미사용 영역)
# ---------------------------------------------------------------------------

SIGNATURE_EFFECT = "Cyan"
SIGNATURE_EFFECT_TEMP = "Cyan Temp"
SIGNATURE_ICON_COLOR = "Cyan"

# ---------------------------------------------------------------------------
# Keystone 배경 — Royal Crimson (극소수 아이템 전용)
# ---------------------------------------------------------------------------

KEYSTONE_BG = "180 20 70"

# ---------------------------------------------------------------------------
# 폰트 스케일 — 가치 티어 6단계
# ---------------------------------------------------------------------------

FONT_SIZES = {
    "P1_KEYSTONE":  45,  # max — Keystone급
    "P2_CORE":      42,
    "P3_USEFUL":    40,
    "P4_SUPPORT":   38,
    "P5_MINOR":     36,
    "P6_LOW":       34,
}

# ---------------------------------------------------------------------------
# Gold StackSize 기반 폰트 스케일 (POE Kingsmarch Gold 전용)
# ---------------------------------------------------------------------------

GOLD_STACK_FONTS = [
    (5000, 45), (2000, 42), (1000, 40), (500, 38), (200, 36),
    (100, 34), (50, 33), (20, 32), (1, 32),
]

# ---------------------------------------------------------------------------
# 알림 사운드 — Sanavi 관례 유지
# ---------------------------------------------------------------------------

ALERT_SOUNDS = {
    "P1_KEYSTONE": "6 300",
    "P2_CORE":     "1 300",
    "P3_USEFUL":   "2 300",
    "P4_SUPPORT":  "3 300",
    "P5_MINOR":    None,
    "P6_LOW":      None,
}

# ---------------------------------------------------------------------------
# Aurora Glow 배경 시스템 — Dark Tint + 티어별 Alpha
# ---------------------------------------------------------------------------
# 오로라 보레알리스: 어둠 위에서 빛이 번지는 느낌.
# 상위 티어일수록 glow가 강하고 (높은 alpha), 하위는 빛이 꺼짐.

TIER_BG_ALPHA: dict[str, int] = {
    "P1_KEYSTONE": 255,
    "P2_CORE":     245,
    "P3_USEFUL":   235,
    "P4_SUPPORT":  220,
    "P5_MINOR":    200,
    "P6_LOW":      180,
}

# 카테고리별 배경 Dark Tint (시드 색에서 자동 계산)
CATEGORY_BG_TINTS: dict[str, str] = {
    cat: _make_dark_tint(color) for cat, color in CATEGORY_COLORS.items()
}


# ---------------------------------------------------------------------------
# 색 조회 API
# ---------------------------------------------------------------------------

def get_color(category: str, tier: str | None = None) -> str:
    """카테고리 텍스트 색 반환.

    tier 인자가 주어지고 해당 카테고리에 티어 테이블이 있으면 티어 색 반환.
    없으면 CATEGORY_COLORS의 기본 색 fallback.
    """
    if tier and category in TIER_COLORS_BY_CATEGORY:
        tier_dict = TIER_COLORS_BY_CATEGORY[category]
        if tier in tier_dict:
            return tier_dict[tier]
    return CATEGORY_COLORS.get(category, CATEGORY_COLORS["unique"])


def get_shape(category: str) -> str:
    return CATEGORY_SHAPES.get(category, "Diamond")


def get_bg_color(category: str, tier: str) -> str:
    """카테고리 + 티어 → 배경 'R G B A' 문자열 (Dark Tint + tier alpha)."""
    tint = CATEGORY_BG_TINTS.get(category, "20 15 30")
    alpha = TIER_BG_ALPHA.get(tier, 170)
    return f"{tint} {alpha}"


def get_border_color(category: str, tier: str) -> str:
    """카테고리 + 티어 → Edge Glow 보더 'R G B' 문자열 (텍스트보다 밝게)."""
    text_color = get_color(category, tier)
    return _brighten_color(text_color)


_ICON_SIZE_BY_TIER = {
    "P1_KEYSTONE": 0, "P2_CORE": 0, "P3_USEFUL": 1,
    "P4_SUPPORT": 2, "P5_MINOR": 2, "P6_LOW": 2,
}
