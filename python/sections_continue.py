# -*- coding: utf-8 -*-
"""PathcraftAI β Continue 체인 빌더.

Wreckers식 Continue 캐스케이드. 각 레이어는 단일 관심사만 수정.
설계: .claude/status/continue_architecture.md
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

__all__ = [
    "LAYER_NAMES", "LAYER_HARD_HIDE", "LAYER_CATCH_ALL",
    "LAYER_DEFAULT_RARITY", "LAYER_SOCKET_BORDER",
    "LAYER_SPECIAL_BASE", "LAYER_CORRUPT_BORDER", "LAYER_T1_BORDER",
    "LAYER_BUILD_TARGET", "LAYER_CATEGORY_SHOW",
    "LAYER_PROGRESSIVE_HIDE", "LAYER_RE_SHOW", "LAYER_ENDGAME_RARE",
    "LAYER_REST_EX",
    "make_layer_block", "LayerStyle",
    "load_t1_bases", "T1Bases", "style_from_palette",
    "layer_catch_all", "layer_default_rarity",
    "layer_socket_border", "layer_corrupt_border", "layer_t1_border",
    "layer_hard_hide", "layer_progressive_hide",
    "layer_currency", "layer_maps", "layer_divcards",
    "layer_build_target", "layer_re_show",
    "load_progressive_hide", "ProgressiveHideData",
    "load_category_data", "CategoryData",
    "generate_beta_overlay",
]


# ---------------------------------------------------------------------------
# Layer constants
# ---------------------------------------------------------------------------

LAYER_HARD_HIDE         = 0   # Scroll Fragment 등 절대 숨김
LAYER_CATCH_ALL         = 1   # 오렌지 미분류 안전망
LAYER_DEFAULT_RARITY    = 2   # Normal/Magic/Rare/Unique 기본 색
LAYER_SOCKET_BORDER     = 3   # Chromatic RGB, Jeweller 6S
LAYER_SPECIAL_BASE      = 4   # 특수 베이스 오렌지 복원
LAYER_CORRUPT_BORDER    = 5   # 부패/타락/미러
LAYER_T1_BORDER         = 6   # ilvl>=86 + 크래프팅 베이스
LAYER_BUILD_TARGET      = 7   # POB 빌드 타겟
LAYER_CATEGORY_SHOW     = 8   # 커런시/젬/플라스크/맵/디비카/유니크 최종 스타일
LAYER_PROGRESSIVE_HIDE  = 9   # AL 기반 단계적 Hide
LAYER_RE_SHOW           = 10  # Jewel/Flask/Tincture 예외 Show
LAYER_ENDGAME_RARE      = 11  # 엔드게임 레어 필터
LAYER_REST_EX           = 12  # 미분류 최종 안전망

LAYER_NAMES: dict[int, str] = {
    LAYER_HARD_HIDE:        "hard_hide",
    LAYER_CATCH_ALL:        "catch_all",
    LAYER_DEFAULT_RARITY:   "default_rarity",
    LAYER_SOCKET_BORDER:    "socket_border",
    LAYER_SPECIAL_BASE:     "special_base",
    LAYER_CORRUPT_BORDER:   "corrupt_border",
    LAYER_T1_BORDER:        "t1_border",
    LAYER_BUILD_TARGET:     "build_target",
    LAYER_CATEGORY_SHOW:    "category_show",
    LAYER_PROGRESSIVE_HIDE: "progressive_hide",
    LAYER_RE_SHOW:          "re_show",
    LAYER_ENDGAME_RARE:     "endgame_rare",
    LAYER_REST_EX:          "rest_ex",
}


# ---------------------------------------------------------------------------
# LayerStyle — 부분 스타일 덮어쓰기
# ---------------------------------------------------------------------------

class LayerStyle:
    """Continue 레이어 스타일. None 필드는 출력 안 함 (이전 레이어 값 유지).

    포맷 규칙:
      text/border   — "R G B" 또는 "R G B A"
      bg            — "R G B" 또는 "R G B A" (A 권장)
      font          — int
      sound         — "ID VOL" (예: "12 300")
      effect        — "Color" 또는 "Color Temp" (예: "Cyan", "Red Temp")
      icon          — "SIZE COLOR SHAPE" (예: "0 Yellow Star")
      disable_drop  — True면 DisableDropSound True 추가
    """
    __slots__ = ("text", "border", "bg", "font",
                 "sound", "effect", "icon", "disable_drop")

    def __init__(
        self,
        text: Optional[str] = None,
        border: Optional[str] = None,
        bg: Optional[str] = None,
        font: Optional[int] = None,
        sound: Optional[str] = None,
        effect: Optional[str] = None,
        icon: Optional[str] = None,
        disable_drop: bool = False,
    ) -> None:
        self.text = text
        self.border = border
        self.bg = bg
        self.font = font
        self.sound = sound
        self.effect = effect
        self.icon = icon
        self.disable_drop = disable_drop

    def emit_lines(self) -> list[str]:
        out: list[str] = []
        if self.font is not None:
            out.append(f"\tSetFontSize {self.font}")
        if self.text is not None:
            out.append(f"\tSetTextColor {_pad_alpha(self.text)}")
        if self.border is not None:
            out.append(f"\tSetBorderColor {_pad_alpha(self.border)}")
        if self.bg is not None:
            out.append(f"\tSetBackgroundColor {self.bg}")
        if self.sound is not None:
            out.append(f"\tPlayAlertSound {self.sound}")
        if self.effect is not None:
            out.append(f"\tPlayEffect {self.effect}")
        if self.icon is not None:
            out.append(f"\tMinimapIcon {self.icon}")
        if self.disable_drop:
            out.append("\tDisableDropSound True")
        return out


def _pad_alpha(rgb: str) -> str:
    """RGB 3토큰이면 알파 255 추가. 이미 4토큰이면 그대로."""
    parts = rgb.split()
    if len(parts) == 3:
        return f"{rgb} 255"
    return rgb


# ---------------------------------------------------------------------------
# Block builder
# ---------------------------------------------------------------------------

def make_layer_block(
    layer: int,
    comment: str,
    conditions: list[str],
    style: "LayerStyle",
    action: str = "Show",
    continue_: bool = True,
    category_tag: Optional[str] = None,
) -> str:
    """Continue 레이어 블록 생성.

    주석 포맷: `{action} # PathcraftAI [L{n}|{category}] {comment}`
    이 형식은 디버그/엄격도 패턴 매칭에 사용됨.
    """
    if action not in ("Show", "Hide"):
        raise ValueError(f"action must be Show|Hide, got {action!r}")
    if layer not in LAYER_NAMES:
        raise ValueError(f"unknown layer {layer}")

    tag = f"L{layer}"
    if category_tag:
        tag = f"{tag}|{category_tag}"
    header = f"{action} # PathcraftAI [{tag}] {comment}"

    lines: list[str] = [header]
    for cond in conditions:
        lines.append(f"\t{cond}")
    lines.extend(style.emit_lines())
    if continue_:
        lines.append("\tContinue")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# T1 크래프팅 베이스 로더
# ---------------------------------------------------------------------------
#
# 설계 결정: Class 조건 사용 안 함. BaseType은 POE에서 유일하므로 BaseType 매칭만으로 충분.
# 카테고리(wands, body_armour, amulets...)는 주석/디버그 용도로만 보존.

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


_DEFAULT_INFLUENCE_TYPES = (
    "Shaper", "Elder", "Crusader", "Hunter", "Redeemer", "Warlord",
)


@dataclass(frozen=True)
class T1Bases:
    """T1 크래프팅 베이스 로드 결과.

    Attributes:
        categories: JSON 키(wands, body_armour, amulets...) → BaseType 리스트.
                    카테고리 경계는 블록 주석/디버그용. 블록 생성은 BaseType만 사용.
        ilvl_threshold: T1 판정 ItemLevel 임계값 (JSON _meta에서 로드).
        influence_types: Conqueror 영향력 타입 튜플 (JSON _meta에서 로드).
                         HasInfluence 조건 생성에 사용.
        has_influence_all: Influenced 베이스 전부 포함 플래그.
                           True면 별도 Show 블록 (HasInfluence Any)으로 소비.
    """
    categories: dict[str, list[str]] = field(default_factory=dict)
    ilvl_threshold: int = 86
    influence_types: tuple[str, ...] = _DEFAULT_INFLUENCE_TYPES
    has_influence_all: bool = False

    def all_bases(self) -> list[str]:
        """평탄화된 BaseType 전체 리스트 (중복 제거, 정렬)."""
        seen: set[str] = set()
        for bases in self.categories.values():
            seen.update(bases)
        return sorted(seen)


def load_t1_bases(filepath: Optional[Path] = None) -> T1Bases:
    """T1 베이스 JSON 로드.

    Raises:
        FileNotFoundError: JSON 파일 없음
        json.JSONDecodeError: 파싱 실패
    """
    path = filepath if filepath is not None else _DATA_DIR / "t1_craft_bases.json"
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    categories: dict[str, list[str]] = {}

    weapons = raw.get("weapons", {})
    for weapon_cat, bases in weapons.items():
        if isinstance(bases, list) and bases:
            categories[weapon_cat] = list(bases)

    for armor_cat in ("body_armour", "helmets", "gloves", "boots", "shields"):
        bases = raw.get(armor_cat)
        if isinstance(bases, list) and bases:
            categories[armor_cat] = list(bases)

    jewelry = raw.get("jewelry", {})
    for jewel_cat, bases in jewelry.items():
        if isinstance(bases, list) and bases:
            categories[jewel_cat] = list(bases)

    meta = raw.get("_meta", {})
    ilvl_threshold = int(meta.get("ilvl_threshold", 86))
    influence_list = meta.get("influence_types", list(_DEFAULT_INFLUENCE_TYPES))
    influence_types = tuple(str(x) for x in influence_list)
    has_influence_all = bool(raw.get("has_influence_all", False))

    return T1Bases(
        categories=categories,
        ilvl_threshold=ilvl_threshold,
        influence_types=influence_types,
        has_influence_all=has_influence_all,
    )


# ---------------------------------------------------------------------------
# Palette → LayerStyle 팩토리
# ---------------------------------------------------------------------------

def style_from_palette(
    category: str,
    tier: str = "P2_CORE",
    **overrides,
) -> LayerStyle:
    """pathcraft_palette의 카테고리×티어 매핑을 LayerStyle로 변환.

    overrides로 개별 필드 덮어쓰기 가능 (예: border="255 255 0").
    임포트 순환 방지를 위해 함수 내부에서 pathcraft_palette import.
    """
    from pathcraft_palette import (
        get_color, get_border_color, get_bg_color,
        FONT_SIZES, ALERT_SOUNDS,
    )

    base = {
        "text":   get_color(category, tier),
        "border": get_border_color(category, tier),
        "bg":     get_bg_color(category, tier),
        "font":   FONT_SIZES.get(tier),
        "sound":  ALERT_SOUNDS.get(tier),
    }
    base.update(overrides)
    return LayerStyle(**{k: v for k, v in base.items() if v is not None})


# ---------------------------------------------------------------------------
# L1: Catch-All (오렌지 미분류 안전망)
# ---------------------------------------------------------------------------

CATCH_ALL_COLOR = "255 123 0"   # Wreckers Orange
CATCH_ALL_BG = "0 0 0 255"
CATCH_ALL_FONT = 35


def layer_catch_all() -> str:
    """L1 Catch-All — 맨 위에서 모든 아이템에 오렌지 기본 스타일.

    필터가 모르는 아이템 = 오렌지. 이후 레이어에서 덮어씌워짐.
    """
    return make_layer_block(
        LAYER_CATCH_ALL,
        "모든 아이템 오렌지 안전망 (미분류 표시)",
        conditions=[],
        style=LayerStyle(
            text=CATCH_ALL_COLOR,
            border=CATCH_ALL_COLOR,
            bg=CATCH_ALL_BG,
            font=CATCH_ALL_FONT,
            icon="2 Orange UpsideDownHouse",
        ),
        category_tag="catchall",
    )


# ---------------------------------------------------------------------------
# L2: Default Rarity (POE 표준 레어리티 색)
# ---------------------------------------------------------------------------
#
# L1 오렌지 위에 레어리티 기본색을 덮어씌워 POE 관례 유지.
# L8 CATEGORY_SHOW에서 카테고리별 Aurora 팔레트로 최종 덮어씀.

_DEFAULT_RARITY_STYLES: list[tuple[str, str, str, str]] = [
    # (rarity, tag, text_color, border_color)
    ("Normal", "normal", "200 200 200", "120 120 120"),  # Off-white
    ("Magic",  "magic",  "136 136 255", "80 80 200"),    # POE blue
    ("Rare",   "rare",   "255 255 119", "180 180 60"),   # POE yellow
    ("Unique", "unique", "175 96 37",   "255 120 40"),   # POE brown + 밝은 오렌지 보더
]

_DEFAULT_RARITY_FONT = 32


def layer_default_rarity() -> str:
    """L2 Default Rarity — Normal/Magic/Rare/Unique 각각 POE 표준색.

    오렌지 위에 레어리티 색 오버라이드. 다음 레이어(소켓/부패/T1)에서
    보더/이펙트 덧입혀짐.
    """
    blocks: list[str] = []
    for rarity, tag, text, border in _DEFAULT_RARITY_STYLES:
        blocks.append(make_layer_block(
            LAYER_DEFAULT_RARITY,
            f"레어리티 기본 {rarity}",
            conditions=[f"Rarity {rarity}"],
            style=LayerStyle(
                text=text,
                border=border,
                font=_DEFAULT_RARITY_FONT,
            ),
            category_tag=tag,
        ))
    return "".join(blocks)


# ---------------------------------------------------------------------------
# L3: Socket Border (Chromatic RGB / Jeweller 6-socket 핑크)
# ---------------------------------------------------------------------------

_SOCKET_PINK = "255 0 200"


def layer_socket_border() -> str:
    """L3 Socket Border — 6소켓/RGB 링크 핑크 보더 (벤더 레시피 가치).

    - 6소켓 (Jeweller's Orb 레시피 7개)
    - RGB 링크 (Chromatic Orb 레시피)
    """
    blocks: list[str] = []

    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "6소켓 (Jeweller's Orb 레시피)",
        conditions=["Sockets >= 6"],
        style=LayerStyle(
            border=_SOCKET_PINK,
            effect="Pink",
            icon="2 Pink Cross",
        ),
        category_tag="jeweller",
    ))

    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "RGB 링크 (Chromatic Orb 레시피)",
        conditions=["SocketGroup RGB"],
        style=LayerStyle(
            border=_SOCKET_PINK,
        ),
        category_tag="chromatic",
    ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L5: Corrupt Border (부패/미러 빨강)
# ---------------------------------------------------------------------------

_CORRUPT_RED = "200 0 0"


def layer_corrupt_border() -> str:
    """L5 Corrupt Border — 부패/미러 빨강 보더 + PlayEffect Red."""
    blocks: list[str] = []

    blocks.append(make_layer_block(
        LAYER_CORRUPT_BORDER,
        "부패 아이템 (Vaal/Temple)",
        conditions=["Corrupted True"],
        style=LayerStyle(
            border=_CORRUPT_RED,
            effect="Red Temp",
        ),
        category_tag="corrupted",
    ))

    blocks.append(make_layer_block(
        LAYER_CORRUPT_BORDER,
        "미러 복사 아이템",
        conditions=["Mirrored True"],
        style=LayerStyle(
            border=_CORRUPT_RED,
            effect="Red",
        ),
        category_tag="mirrored",
    ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L6: T1 Border (ilvl>=86 크래프팅 베이스 + Influenced)
# ---------------------------------------------------------------------------

_T1_YELLOW = "255 255 0"


def layer_t1_border() -> str:
    """L6 T1 Border — ilvl>=86 크래프팅 가치 베이스 + Influenced 전부.

    카테고리별로 블록을 분리 (debug 가독성 + POE 엔진 per-item 평가 최적화).
    Influenced는 베이스 무관 별도 블록.
    """
    bases = load_t1_bases()
    blocks: list[str] = []

    style = LayerStyle(
        border=_T1_YELLOW,
        effect="Yellow",
        icon="0 Yellow Star",
    )

    for category, items in bases.categories.items():
        quoted = " ".join(f'"{b}"' for b in items)
        blocks.append(make_layer_block(
            LAYER_T1_BORDER,
            f"T1 크래프팅 {category} (ilvl>={bases.ilvl_threshold})",
            conditions=[
                "Rarity Rare",
                f"BaseType == {quoted}",
                f"ItemLevel >= {bases.ilvl_threshold}",
            ],
            style=style,
            category_tag=category,
        ))

    if bases.has_influence_all:
        influence_cond = "HasInfluence " + " ".join(bases.influence_types)
        blocks.append(make_layer_block(
            LAYER_T1_BORDER,
            f"Influenced 레어 전체 (ilvl>={bases.ilvl_threshold})",
            conditions=[
                "Rarity Rare",
                influence_cond,
                f"ItemLevel >= {bases.ilvl_threshold}",
            ],
            style=style,
            category_tag="influenced",
        ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L0 HARD_HIDE / L9 PROGRESSIVE_HIDE 데이터 로더
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProgressiveHideData:
    """progressive_hide.json 로드 결과."""
    always_hide: tuple[str, ...] = ()
    supply_currency_items: tuple[str, ...] = ()
    supply_stages: tuple[tuple[int, int], ...] = ()  # (min_al, max_stack)
    normal_all_al: int = 14
    magic_all_al: int = 24
    gem_hide_al: int = 45
    flask_hide_al: int = 73
    leveling_bases_early: tuple[tuple[str, int], ...] = ()    # (base, hide_above_al)
    equipment_bases_midgame: tuple[tuple[str, int], ...] = ()
    endgame_supplies: tuple[tuple[str, int], ...] = ()


def load_progressive_hide(filepath: Optional[Path] = None) -> ProgressiveHideData:
    """progressive_hide.json 로드."""
    path = filepath if filepath is not None else _DATA_DIR / "progressive_hide.json"
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    supply = raw.get("supply_currency", {})
    supply_items = tuple(supply.get("items", []))
    supply_stages = tuple(
        (int(s["min_area_level"]), int(s["max_stack_size"]))
        for s in supply.get("stages", [])
    )

    def _pairs(key: str) -> tuple[tuple[str, int], ...]:
        return tuple(
            (str(item["base"]), int(item["hide_above_al"]))
            for item in raw.get(key, {}).get("items", [])
        )

    return ProgressiveHideData(
        always_hide=tuple(raw.get("always_hide", {}).get("items", [])),
        supply_currency_items=supply_items,
        supply_stages=supply_stages,
        normal_all_al=int(raw.get("normal_all", {}).get("min_area_level", 14)),
        magic_all_al=int(raw.get("magic_all", {}).get("min_area_level", 24)),
        gem_hide_al=int(raw.get("gem_hide", {}).get("min_area_level", 45)),
        flask_hide_al=int(raw.get("flask_hide", {}).get("min_area_level", 73)),
        leveling_bases_early=_pairs("leveling_bases_early"),
        equipment_bases_midgame=_pairs("equipment_bases_midgame"),
        endgame_supplies=_pairs("endgame_supplies"),
    )


# ---------------------------------------------------------------------------
# L0: Hard Hide (Scroll Fragment 등 절대 숨김)
# ---------------------------------------------------------------------------

def layer_hard_hide(data: Optional[ProgressiveHideData] = None) -> str:
    """L0 Hard Hide — 모든 레벨/엄격도에서 즉시 숨김. Continue 없음.

    Scroll Fragment, Alteration/Transmutation/Alchemy Shard 등 가치 0.
    """
    d = data if data is not None else load_progressive_hide()
    if not d.always_hide:
        return ""
    quoted = " ".join(f'"{b}"' for b in d.always_hide)
    return make_layer_block(
        LAYER_HARD_HIDE,
        f"절대 숨김 ({len(d.always_hide)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=LayerStyle(disable_drop=True),
        action="Hide",
        continue_=False,
        category_tag="always",
    )


# ---------------------------------------------------------------------------
# L9: Progressive Hide (AL 기반 단계적 숨김 + 엄격도 게이트)
# ---------------------------------------------------------------------------
#
# 엄격도 매핑 (strictness → 활성화 되는 규칙):
#   0 (Regular)   — 없음 (L0 HARD_HIDE만)
#   1 (Strict)    — Normal AL>=14, Supply AL>=64 stack<=1
#   2 (VeryStrict)— + Magic AL>=24, Supply AL>=68 stack<=2, Gem AL>=45, 레벨링 초반 bases
#   3 (UberStrict)— + Supply AL>=73 stack<=3, Flask AL>=73, 중후반 bases
#   4 (UberPlus)  — + Supply AL>=78/83 stacks<=4/5, 엔드게임 소모품

_STRICTNESS_SUPPLY_INDEX = {
    # strictness → 해당 단계 인덱스까지 활성 (supply_stages 리스트 기준)
    0: -1,
    1: 0,    # AL>=64 stack<=1
    2: 1,    # + AL>=68 stack<=2
    3: 2,    # + AL>=73 stack<=3
    4: 4,    # + AL>=78 stack<=4, + AL>=83 stack<=5
}


def _hide_block(
    comment: str,
    conditions: list[str],
    category_tag: str,
    continue_: bool = True,
) -> str:
    """Hide 블록 헬퍼 (disable_drop True 기본)."""
    return make_layer_block(
        LAYER_PROGRESSIVE_HIDE,
        comment,
        conditions=conditions,
        style=LayerStyle(disable_drop=True),
        action="Hide",
        continue_=continue_,
        category_tag=category_tag,
    )


def layer_progressive_hide(
    strictness: int = 3,
    data: Optional[ProgressiveHideData] = None,
) -> str:
    """L9 Progressive Hide — AL 기반 단계적 숨김.

    strictness 0: 모든 블록 비활성 (빈 문자열 반환)
    strictness 1~4: 표 참조 (각 레벨마다 Hide 블록 누적).
    모든 Hide 블록은 Continue 포함 → L10 RE_SHOW에서 예외 재Show 가능.
    """
    if strictness not in _STRICTNESS_SUPPLY_INDEX:
        raise ValueError(
            f"strictness must be 0~4, got {strictness}"
        )
    if strictness <= 0:
        return ""
    d = data if data is not None else load_progressive_hide()
    blocks: list[str] = []

    # Supply currency StackSize 단계
    supply_idx = _STRICTNESS_SUPPLY_INDEX[strictness]
    if supply_idx >= 0 and d.supply_currency_items and d.supply_stages:
        quoted = " ".join(f'"{b}"' for b in d.supply_currency_items)
        for i, (min_al, max_stack) in enumerate(d.supply_stages):
            if i > supply_idx:
                break
            blocks.append(_hide_block(
                f"보급품 AL>={min_al} StackSize<={max_stack}",
                conditions=[
                    f"BaseType == {quoted}",
                    f"AreaLevel >= {min_al}",
                    f"StackSize <= {max_stack}",
                ],
                category_tag="supply",
            ))

    # Normal 전체 (AL >= 14)
    if strictness >= 1:
        blocks.append(_hide_block(
            f"Normal 전체 AL>={d.normal_all_al}",
            conditions=[
                "Rarity Normal",
                f"AreaLevel >= {d.normal_all_al}",
            ],
            category_tag="normal_all",
        ))

    # Magic 전체 (AL >= 24)
    if strictness >= 2:
        blocks.append(_hide_block(
            f"Magic 전체 AL>={d.magic_all_al}",
            conditions=[
                "Rarity Magic",
                f"AreaLevel >= {d.magic_all_al}",
            ],
            category_tag="magic_all",
        ))

    # 레벨링 초반 베이스 (strictness >= 2)
    if strictness >= 2:
        for base, hide_al in d.leveling_bases_early:
            blocks.append(_hide_block(
                f"레벨링 초반 {base} AL>={hide_al}",
                conditions=[
                    f'BaseType == "{base}"',
                    f"AreaLevel >= {hide_al}",
                ],
                category_tag="level_early",
            ))

    # Gem Hide (AL >= 45, strictness >= 2)
    if strictness >= 2:
        blocks.append(_hide_block(
            f"기본 젬 AL>={d.gem_hide_al}",
            conditions=[
                'Class "Skill Gems" "Support Gems"',
                f"AreaLevel >= {d.gem_hide_al}",
                "Quality 0",
                "Corrupted False",
            ],
            category_tag="gem",
        ))

    # 중후반 장비 베이스 (strictness >= 3)
    if strictness >= 3:
        for base, hide_al in d.equipment_bases_midgame:
            blocks.append(_hide_block(
                f"중후반 {base} AL>={hide_al}",
                conditions=[
                    f'BaseType == "{base}"',
                    f"AreaLevel >= {hide_al}",
                ],
                category_tag="level_mid",
            ))

    # Flask (AL >= 73, strictness >= 3)
    if strictness >= 3:
        blocks.append(_hide_block(
            f"기본 Life/Mana/Hybrid 플라스크 AL>={d.flask_hide_al}",
            conditions=[
                'Class "Life Flasks" "Mana Flasks" "Hybrid Flasks"',
                f"AreaLevel >= {d.flask_hide_al}",
                "Rarity Normal",
            ],
            category_tag="flask",
        ))

    # 엔드게임 소모품 (strictness >= 4)
    if strictness >= 4:
        for base, hide_al in d.endgame_supplies:
            blocks.append(_hide_block(
                f"엔드게임 소모품 {base} AL>={hide_al}",
                conditions=[
                    f'BaseType == "{base}"',
                    f"AreaLevel >= {hide_al}",
                ],
                category_tag="endgame_supply",
            ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L8 CATEGORY_SHOW 데이터 로더
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CategoryData:
    """neversink_filter_rules.json 로드 결과 (커런시/디비카 티어)."""
    currency_tiers: dict[str, list[str]] = field(default_factory=dict)
    divcard_tiers: dict[str, list[str]] = field(default_factory=dict)


def load_category_data(filepath: Optional[Path] = None) -> CategoryData:
    """neversink_filter_rules.json 로드."""
    path = filepath if filepath is not None else _DATA_DIR / "neversink_filter_rules.json"
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return CategoryData(
        currency_tiers={k: list(v) for k, v in raw.get("currency_tiers", {}).items()},
        divcard_tiers={k: list(v) for k, v in raw.get("divination_cards", {}).items()},
    )


# ---------------------------------------------------------------------------
# L8: Currency (커런시 티어)
# ---------------------------------------------------------------------------
#
# 티어 → 팔레트 티어 매핑. neversink 데이터 구조 그대로 따름.

_CURRENCY_TIER_MAP: dict[str, str] = {
    "t1_mirror_divine": "P1_KEYSTONE",
    "t2_exalted":       "P2_CORE",
    "t3_annulment":     "P3_USEFUL",
    "t4_chaos":         "P4_SUPPORT",
    "t5_alchemy":       "P5_MINOR",
    "t7_chance":        "P6_LOW",
}


def layer_currency(data: Optional[CategoryData] = None) -> str:
    """L8 Currency — neversink 티어별 Show 블록. 종료 (Continue 없음).

    t1_mirror_divine → P1 (Hot Coral + Star)
    t7_chance → P6 (저가)
    """
    d = data if data is not None else load_category_data()
    blocks: list[str] = []

    for tier_name, bases in d.currency_tiers.items():
        palette_tier = _CURRENCY_TIER_MAP.get(tier_name)
        if palette_tier is None or not bases:
            continue
        style = style_from_palette("currency", palette_tier)
        # 아이콘/이펙트는 P1/P2만 — 저가 커런시는 무음 조용히
        if palette_tier in ("P1_KEYSTONE", "P2_CORE"):
            style.effect = "Cyan"
            style.icon = "0 Cyan Cross" if palette_tier == "P1_KEYSTONE" else "1 Cyan Cross"

        quoted = " ".join(f'"{b}"' for b in bases)
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"커런시 {tier_name} ({len(bases)}종)",
            conditions=[
                'Class "Currency" "Map Fragments" "Scarabs" "Delirium Orbs"',
                f'BaseType == {quoted}',
            ],
            style=style,
            continue_=False,
            category_tag=f"currency_{tier_name}",
        ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L8: Maps (티어 4단계)
# ---------------------------------------------------------------------------
#
# T1-5 화이트, T6-10 옐로우, T11-15 레드, T16+ 레드 + 화이트 배경.
# Wreckers 관례. MapTier 범위 조건 AND 조합.

# (tag, conditions, style_kwargs) — style_kwargs는 매 호출마다 새 LayerStyle 생성
# (모듈 레벨 LayerStyle 인스턴스 공유 오염 방지)
_MAP_TIER_SPECS: list[tuple[str, list[str], dict]] = [
    (
        "white", ["MapTier <= 5"],
        {"text": "255 255 255", "border": "180 180 180",
         "bg": "0 0 0 220", "font": 32, "icon": "1 White Circle"},
    ),
    (
        "yellow", ["MapTier >= 6", "MapTier <= 10"],
        {"text": "255 255 0", "border": "200 200 40",
         "bg": "0 0 0 220", "font": 36, "icon": "1 Yellow Circle",
         "effect": "Yellow"},
    ),
    (
        "red", ["MapTier >= 11", "MapTier <= 15"],
        {"text": "255 60 60", "border": "220 60 60",
         "bg": "0 0 0 220", "font": 40, "icon": "0 Red Circle",
         "effect": "Red"},
    ),
    (
        "t16plus", ["MapTier >= 16"],
        {"text": "255 60 60", "border": "255 100 100",
         "bg": "255 255 255 220", "font": 45, "icon": "0 Red Star",
         "effect": "Red", "sound": "1 300"},
    ),
]


def layer_maps() -> str:
    """L8 Maps — 티어 4단계 색상. 종료."""
    blocks: list[str] = []
    for tag, conds, style_kwargs in _MAP_TIER_SPECS:
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"맵 {tag}",
            conditions=['Class "Maps"', *conds],
            style=LayerStyle(**style_kwargs),
            continue_=False,
            category_tag=f"map_{tag}",
        ))
    return "".join(blocks)


# ---------------------------------------------------------------------------
# L8: Divination Cards (5 티어)
# ---------------------------------------------------------------------------

_DIVCARD_TIER_MAP: dict[str, str] = {
    "t1_top":    "P1_KEYSTONE",
    "t2_high":   "P2_CORE",
    "t3_good":   "P3_USEFUL",
    "t4_medium": "P4_SUPPORT",
    "t5_common": "P5_MINOR",
}


def layer_divcards(data: Optional[CategoryData] = None) -> str:
    """L8 Divination Cards — neversink 5 티어. 종료."""
    d = data if data is not None else load_category_data()
    blocks: list[str] = []

    for tier_name, cards in d.divcard_tiers.items():
        palette_tier = _DIVCARD_TIER_MAP.get(tier_name)
        if palette_tier is None or not cards:
            continue
        style = style_from_palette("divcard", palette_tier)
        if palette_tier == "P1_KEYSTONE":
            style.effect = "Purple"
            style.icon = "0 Purple Square"
        elif palette_tier == "P2_CORE":
            style.icon = "1 Purple Square"

        quoted = " ".join(f'"{c}"' for c in cards)
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"디비카 {tier_name} ({len(cards)}종)",
            conditions=[
                'Class "Divination Cards"',
                f'BaseType == {quoted}',
            ],
            style=style,
            continue_=False,
            category_tag=f"divcard_{tier_name}",
        ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L7: Build Target (POB 빌드 기반 Cyan 하이라이트)
# ---------------------------------------------------------------------------
#
# 빌드 필수 아이템에 PathcraftAI Cyan 시그니처 덧입히기.
# 스타일만 오버라이드 (Continue=True) → L8 CATEGORY_SHOW가 덮어쓰기도 함.
# L10 RE_SHOW와 함께 쓰여 "L9 Hide 방어 + 시각 강조" 역할 분담.

_BUILD_CYAN = "100 220 255"  # Aurora 팔레트 base 색


def layer_build_target(
    build_data: Optional[dict] = None,
    coaching_data: Optional[dict] = None,
) -> str:
    """L7 Build Target — 빌드 유니크/디비카/chanceable/젬/베이스 하이라이트.

    build_data=None이면 빈 문자열 반환 (β-4 이하 호환).
    """
    if not build_data:
        return ""

    # 지연 임포트 (순환 의존 회피)
    from build_extractor import (
        extract_build_uniques, get_target_divcards, get_chanceable_bases,
        extract_build_gems, extract_build_bases,
    )

    uniques = extract_build_uniques(build_data, coaching_data)
    target_cards = get_target_divcards(uniques)
    chanceable = get_chanceable_bases(uniques)
    skills, supports = extract_build_gems(build_data)
    bases = extract_build_bases(build_data)

    blocks: list[str] = []

    def _cyan_style(icon: str, font: int = 42) -> LayerStyle:
        return LayerStyle(
            border=_BUILD_CYAN,
            font=font,
            effect="Cyan",
            icon=icon,
        )

    if uniques:
        quoted = " ".join(f'"{u}"' for u in uniques)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 유니크 ({len(uniques)}종)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=_cyan_style("0 Cyan Star", font=45),
            category_tag="unique",
        ))

    if target_cards:
        names = " ".join(f'"{c["card"]}"' for c in target_cards)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 타겟 디비카 ({len(target_cards)}종)",
            conditions=['Class "Divination Cards"', f"BaseType == {names}"],
            style=_cyan_style("0 Cyan Square", font=42),
            category_tag="divcard",
        ))

    if chanceable:
        names = " ".join(f'"{c["base"]}"' for c in chanceable)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"Chanceable 베이스 ({len(chanceable)}종)",
            conditions=["Rarity Normal", f"BaseType == {names}"],
            style=_cyan_style("0 Cyan Circle", font=40),
            category_tag="chanceable",
        ))

    if skills:
        names = " ".join(f'"{g}"' for g in skills)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 스킬 젬 ({len(skills)}종)",
            conditions=['Class "Skill Gems" "Active Skill Gems"', f"BaseType == {names}"],
            style=_cyan_style("0 Cyan Hexagon", font=42),
            category_tag="skill_gem",
        ))

    if supports:
        names = " ".join(f'"{s}"' for s in supports)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 서포트 젬 ({len(supports)}종)",
            conditions=['Class "Support Skill Gems"', f"BaseType == {names}"],
            style=_cyan_style("1 Cyan Hexagon", font=38),
            category_tag="support_gem",
        ))

    if bases:
        names = " ".join(f'"{b}"' for b in bases)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 장비 베이스 ({len(bases)}종)",
            conditions=["Rarity Rare", f"BaseType == {names}", "ItemLevel >= 75"],
            style=_cyan_style("1 Cyan Square", font=40),
            category_tag="base",
        ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L10: Re-Show (L9 Hide 방어)
# ---------------------------------------------------------------------------
#
# POE Continue 시맨틱: 마지막 매칭 블록의 Show/Hide가 최종.
# L9에서 Rarity Normal AL>=14 Hide 매칭되면 chanceable Normal 베이스도 숨겨짐.
# L10은 Continue=False Show로 최종 결정을 Show로 확정.

_RESHOW_CYAN_TEXT = "100 220 255"
_RESHOW_CYAN_BG = "0 40 60 220"


def layer_re_show(
    build_data: Optional[dict] = None,
    coaching_data: Optional[dict] = None,
) -> str:
    """L10 Re-Show — 빌드 타겟 중 L9가 숨길 수 있는 것들 재Show.

    - Chanceable Normal 베이스 (L9 Normal AL>=14 Hide 방어)
    - 빌드 Magic 베이스 (향후 L9 확장 대비)

    build_data=None이면 빈 문자열 반환.
    """
    if not build_data:
        return ""

    from build_extractor import (
        extract_build_uniques, get_chanceable_bases, extract_build_bases,
    )

    uniques = extract_build_uniques(build_data, coaching_data)
    chanceable = get_chanceable_bases(uniques)
    bases = extract_build_bases(build_data)

    blocks: list[str] = []

    def _reshow_style(icon: str, font: int = 38) -> LayerStyle:
        return LayerStyle(
            text=_RESHOW_CYAN_TEXT,
            border=_RESHOW_CYAN_TEXT,
            bg=_RESHOW_CYAN_BG,
            font=font,
            effect="Cyan",
            icon=icon,
        )

    if chanceable:
        names = " ".join(f'"{c["base"]}"' for c in chanceable)
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"Chanceable Normal 재Show ({len(chanceable)}종)",
            conditions=["Rarity Normal", f"BaseType == {names}"],
            style=_reshow_style("0 Cyan Circle", font=40),
            continue_=False,
            category_tag="chanceable",
        ))

    if bases:
        names = " ".join(f'"{b}"' for b in bases)
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"빌드 Magic 베이스 재Show ({len(bases)}종, ilvl>=60)",
            conditions=["Rarity Magic", f"BaseType == {names}", "ItemLevel >= 60"],
            style=_reshow_style("1 Cyan Square", font=36),
            continue_=False,
            category_tag="base_magic",
        ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# β 오버레이 조립
# ---------------------------------------------------------------------------

_BETA_HEADER = """#===============================================================================================================
# PathcraftAI β Continue Chain Filter
# Arch: continue (Wreckers-style cascading layers)
# Layer order: 0 HARD_HIDE → 1 CATCH_ALL → 2 DEFAULT_RARITY → 3 SOCKET → 4 SPECIAL → 5 CORRUPT → 6 T1 → 7 BUILD → 8 CATEGORY → 9 PROG_HIDE → 10 RE_SHOW → 11 ENDGAME → 12 REST_EX
#===============================================================================================================

"""


def generate_beta_overlay(
    strictness: int = 3,
    build_data: Optional[dict] = None,
    coaching_data: Optional[dict] = None,
) -> str:
    """β 아키텍처 오버레이 생성. L0~L10 전 레이어.

    build_data/coaching_data 없으면 L7 BUILD_TARGET, L10 RE_SHOW 비활성.
    """
    parts: list[str] = [_BETA_HEADER]
    parts.append(layer_hard_hide())
    parts.append(layer_catch_all())
    parts.append(layer_default_rarity())
    parts.append(layer_socket_border())
    parts.append(layer_corrupt_border())
    parts.append(layer_t1_border())
    # L7 BUILD_TARGET — 빌드 데이터 있을 때만
    parts.append(layer_build_target(build_data, coaching_data))
    # L8 CATEGORY_SHOW — 최종 스타일, Continue 없음
    parts.append(layer_currency())
    parts.append(layer_maps())
    parts.append(layer_divcards())
    # L9 PROGRESSIVE_HIDE
    parts.append(layer_progressive_hide(strictness))
    # L10 RE_SHOW — 빌드 타겟 L9 Hide 방어
    parts.append(layer_re_show(build_data, coaching_data))
    return "".join(parts)
