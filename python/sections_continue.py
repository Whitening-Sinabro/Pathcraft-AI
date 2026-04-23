# -*- coding: utf-8 -*-
"""PathcraftAI β Continue 체인 빌더.

Wreckers식 Continue 캐스케이드. 각 레이어는 단일 관심사만 수정.
설계: .claude/status/continue_architecture.md
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

__all__ = [
    "LAYER_NAMES", "LAYER_HARD_HIDE", "LAYER_CATCH_ALL",
    "LAYER_DEFAULT_RARITY", "LAYER_SOCKET_BORDER",
    "LAYER_SPECIAL_BASE",
    "LAYER_CORRUPT_BORDER", "LAYER_T1_BORDER",
    "LAYER_BUILD_TARGET", "LAYER_CATEGORY_SHOW",
    "LAYER_PROGRESSIVE_HIDE", "LAYER_RE_SHOW",
    "LAYER_ENDGAME_RARE",
    "LAYER_REST_EX",
    "VALID_MODES",
    "make_layer_block", "LayerStyle",
    "load_t1_bases", "T1Bases", "style_from_palette",
    "layer_catch_all", "layer_default_rarity",
    "layer_socket_border", "layer_special_base",
    "layer_corrupt_border", "layer_t1_border",
    "layer_hard_hide", "layer_progressive_hide",
    "layer_currency", "layer_maps", "layer_divcards",
    "layer_stacked_currency", "layer_map_fragments", "layer_endgame_content",
    "layer_lifeforce", "layer_splinters", "layer_scarabs",
    "layer_gems_quality", "layer_ssf_currency_extras",
    "layer_endgame_rare", "layer_endgame_rare_hide", "layer_uniques",
    "layer_gold", "layer_flasks_quality", "layer_heist", "layer_quest_items",
    "layer_special_maps", "layer_jewels",
    "layer_special_uniques", "layer_influenced_extra",
    "layer_special_modifiers", "layer_hcssf_safety",
    "layer_id_mod_filtering", "layer_leveling_supplies",
    "layer_basic_orbs",
    "layer_build_target", "layer_re_show",
    "load_progressive_hide", "ProgressiveHideData",
    "load_category_data", "CategoryData",
    "load_ggpk_items", "GGPKItems",
    "generate_beta_overlay",
]

VALID_MODES = ("trade", "ssf", "hcssf")


# ---------------------------------------------------------------------------
# Layer constants
# ---------------------------------------------------------------------------

LAYER_HARD_HIDE         = 0   # Scroll Fragment 등 절대 숨김
LAYER_CATCH_ALL         = 1   # 오렌지 미분류 안전망
LAYER_DEFAULT_RARITY    = 2   # Normal/Magic/Rare/Unique 기본 색
LAYER_SOCKET_BORDER     = 3   # Chromatic RGB, Jeweller 6S
LAYER_SPECIAL_BASE      = 4   # Wreckers 오렌지 복원 (특수 BaseType)
LAYER_CORRUPT_BORDER    = 5   # 부패/타락/미러
LAYER_T1_BORDER         = 6   # ilvl>=86 + 크래프팅 베이스
LAYER_BUILD_TARGET      = 7   # POB 빌드 타겟
LAYER_CATEGORY_SHOW     = 8   # 커런시/젬/플라스크/맵/디비카/유니크 최종 스타일
LAYER_PROGRESSIVE_HIDE  = 9   # AL 기반 단계적 Hide
LAYER_RE_SHOW           = 10  # Jewel/Flask/Tincture 예외 Show
LAYER_ENDGAME_RARE      = 11  # Cobalt 스타일 엔드게임 레어 Hide
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
      custom_sound  — (filename, volume) 튜플. 예: ("6Link.mp3", 300)
                      → CustomAlertSound "6Link.mp3" 300
      effect        — "Color" 또는 "Color Temp" (예: "Cyan", "Red Temp")
      icon          — "SIZE COLOR SHAPE" (예: "0 Yellow Star")
      disable_drop  — True면 DisableDropSound True 추가
    """
    __slots__ = ("text", "border", "bg", "font",
                 "sound", "custom_sound", "effect", "icon", "disable_drop")

    def __init__(
        self,
        text: Optional[str] = None,
        border: Optional[str] = None,
        bg: Optional[str] = None,
        font: Optional[int] = None,
        sound: Optional[str] = None,
        custom_sound: "Optional[tuple[str, int]]" = None,
        effect: Optional[str] = None,
        icon: Optional[str] = None,
        disable_drop: bool = False,
    ) -> None:
        self.text = text
        self.border = border
        self.bg = bg
        self.font = font
        self.sound = sound
        self.custom_sound = custom_sound
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
        if self.custom_sound is not None:
            fname, vol = self.custom_sound
            out.append(f'\tCustomAlertSound "{fname}" {vol}')
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


# ---------------------------------------------------------------------------
# POE1/POE2 ItemClass 매핑 — D5 2단계 (필터 생성 게임 분기)
# ---------------------------------------------------------------------------
#
# POE1 하드코딩 Class 상수를 game 인자에 따라 POE2 로 변환한다.
# 매핑 소스: data/item_class_map_poe2.json (NeverSink POE2 필터 0.9.1 ground truth)
# POE2 변경점:
#   - Shields → Shields + Bucklers (분할)
#   - Warstaves → Quarterstaves (rename)
#   - Claws/Daggers/Rune Daggers/One Hand Axes/Swords/Thrusting Swords/
#     Two Hand Axes/Swords → 미릴리스 (drop)

_ITEM_CLASS_MAP_POE2_CACHE: Optional[dict] = None


def _load_item_class_map_poe2() -> dict:
    global _ITEM_CLASS_MAP_POE2_CACHE
    if _ITEM_CLASS_MAP_POE2_CACHE is not None:
        return _ITEM_CLASS_MAP_POE2_CACHE
    path = _DATA_DIR / "item_class_map_poe2.json"
    if not path.exists():
        logger.warning("item_class_map_poe2.json 미발견: %s — POE2 클래스 매핑은 빈 결과", path)
        _ITEM_CLASS_MAP_POE2_CACHE = {}
        return _ITEM_CLASS_MAP_POE2_CACHE
    _ITEM_CLASS_MAP_POE2_CACHE = json.loads(path.read_text(encoding="utf-8"))
    return _ITEM_CLASS_MAP_POE2_CACHE


# L9 blanket Normal/Magic hide 용. 기존 layer_progressive_hide 내부 _EQUIP_CLASSES 원본.
_POE1_EQUIP_CLASSES: tuple[str, ...] = (
    "Body Armours", "Helmets", "Gloves", "Boots", "Shields",
    "Amulets", "Belts", "Rings", "Quivers",
    "One Hand Axes", "One Hand Maces", "One Hand Swords", "Thrusting One Hand Swords",
    "Two Hand Axes", "Two Hand Maces", "Two Hand Swords",
    "Bows", "Claws", "Daggers", "Rune Daggers", "Sceptres", "Staves", "Wands", "Warstaves",
)

# L11 layer_endgame_rare / endgame_rare_hide Normal·Magic blanket 용. 알파벳 정렬된 24 classes.
_POE1_RARE_EQUIP_CLASSES: tuple[str, ...] = (
    "Amulets", "Belts", "Body Armours", "Boots", "Bows", "Claws", "Daggers",
    "Gloves", "Helmets", "One Hand Axes", "One Hand Maces", "One Hand Swords",
    "Quivers", "Rings", "Rune Daggers", "Sceptres", "Shields", "Staves",
    "Thrusting One Hand Swords", "Two Hand Axes", "Two Hand Maces", "Two Hand Swords",
    "Wands", "Warstaves",
)

# [[2000]] Amulets/Belts/Rings 제외 no-implicit 레어 대상.
_POE1_ENDGAME_RARE_NOIMPL: tuple[str, ...] = (
    "Body Armours", "Boots", "Bows", "Claws", "Daggers",
    "Gloves", "Helmets", "One Hand Axes", "One Hand Maces", "One Hand Swords",
    "Quivers", "Rune Daggers", "Sceptres", "Shields", "Staves",
    "Thrusting One Hand Swords", "Two Hand Axes", "Two Hand Maces", "Two Hand Swords",
    "Wands", "Warstaves",
)

# [[2200]] 4-slot droplevel hide. POE1/POE2 공통.
_POE1_DROPLEVEL_HIDE: tuple[str, ...] = ("Body Armours", "Boots", "Gloves", "Helmets")

# L10 Re-Show 용. Wreckers Levelling Help 의 1H/2H 무기·4-slot 방어구.
_POE1_WEAPON_1H: tuple[str, ...] = (
    "Claws", "Daggers", "One Hand Axes", "One Hand Maces",
    "One Hand Swords", "Rune Daggers", "Sceptres", "Shields",
    "Thrusting One Hand Swords", "Wands",
)
_POE1_WEAPON_2H: tuple[str, ...] = (
    "Bows", "Staves", "Two Hand Axes", "Two Hand Maces",
    "Two Hand Swords", "Warstaves",
)
_POE1_ARMOR_4SLOT: tuple[str, ...] = ("Body Armours", "Boots", "Gloves", "Helmets")

# L10 T1 보더 재Show. Wreckers L172 메인 장비 (Rings/Gloves/Helmets 제외 21 classes).
_POE1_T1_RESHOW_RING_GLOVE_HELM: tuple[str, ...] = ("Rings", "Gloves", "Helmets")
_POE1_T1_RESHOW_MAIN_EQUIP: tuple[str, ...] = (
    "Amulets", "Belts", "Body Armours", "Boots", "Bows", "Claws", "Daggers",
    "One Hand Axes", "One Hand Maces", "One Hand Swords", "Quivers", "Rune Daggers",
    "Sceptres", "Shields", "Staves", "Thrusting One Hand Swords", "Two Hand Axes",
    "Two Hand Maces", "Two Hand Swords", "Wands", "Warstaves",
)


def _map_poe1_classes(poe1_classes: "tuple[str, ...] | list[str]", game: str) -> list[str]:
    """POE1 클래스 → 지정 게임의 클래스.

    - game="poe1": 입력 그대로.
    - game="poe2": poe1_to_poe2 맵 적용. 빈 매핑(Claws 등)은 drop.
                   Shields → [Shields, Bucklers] 다중 매핑은 순서 보존해 확장.
    """
    if game == "poe1":
        return list(poe1_classes)
    if game != "poe2":
        raise ValueError(f"unsupported game: {game!r}")
    mapping = _load_item_class_map_poe2().get("poe1_to_poe2", {})
    out: list[str] = []
    seen: set[str] = set()
    for c in poe1_classes:
        for mapped in mapping.get(c, []):
            if mapped and mapped not in seen:
                seen.add(mapped)
                out.append(mapped)
    return out


def _join_classes_quoted(classes: "list[str] | tuple[str, ...]") -> str:
    return " ".join(f'"{c}"' for c in classes)


def _equip_classes_for(game: str = "poe1") -> str:
    """L9 blanket Normal/Magic hide 용. 'Class {...}' 의 뒷부분 (Class 키워드 없음)."""
    return _join_classes_quoted(_map_poe1_classes(_POE1_EQUIP_CLASSES, game))


def _rare_equip_exact_for(game: str = "poe1") -> str:
    """L11 layer_endgame_rare 용 'Class == "..." "..." ' 조건 full string."""
    classes = _map_poe1_classes(_POE1_RARE_EQUIP_CLASSES, game)
    return "Class == " + _join_classes_quoted(classes)


def _endgame_rare_equip_for(game: str = "poe1") -> str:
    """layer_endgame_rare_hide Normal/Magic blanket용 클래스 문자열. Class == prefix 없음."""
    return _join_classes_quoted(_map_poe1_classes(_POE1_RARE_EQUIP_CLASSES, game))


def _endgame_rare_noimpl_for(game: str = "poe1") -> str:
    """Amulets/Belts/Rings 제외 no-implicit 레어 클래스 문자열."""
    return _join_classes_quoted(_map_poe1_classes(_POE1_ENDGAME_RARE_NOIMPL, game))


def _droplevel_hide_for(game: str = "poe1") -> str:
    """[[2200]] 4-slot droplevel hide 클래스 문자열."""
    return _join_classes_quoted(_map_poe1_classes(_POE1_DROPLEVEL_HIDE, game))


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

_DEFAULT_RARITY_STYLES: "list[tuple[str, str, str, str, int]]" = [
    # (rarity, tag, text_color, border_color, font_size)
    # 폰트는 Aurora 팔레트 하한(P6=34) 이상으로 설정 — 카테고리 매치 없는 아이템도 기본 가독성 확보.
    # Rarity별 차등: Normal<Magic<Rare<Unique (중요도 순).
    ("Normal", "normal", "200 200 200", "120 120 120", 36),  # Off-white, P5 수준
    ("Magic",  "magic",  "136 136 255", "80 80 200",   38),  # POE blue, P4 수준
    ("Rare",   "rare",   "255 255 119", "180 180 60",  40),  # POE yellow, P3 수준
    ("Unique", "unique", "175 96 37",   "255 120 40",  42),  # POE brown + orange, P2 수준
]


def layer_default_rarity() -> str:
    """L2 Default Rarity — Normal/Magic/Rare/Unique 각각 POE 표준색 + Rarity별 폰트.

    오렌지 위에 레어리티 색 오버라이드. 다음 레이어(소켓/부패/T1)에서
    보더/이펙트 덧입혀짐. 폰트 36/38/40/42로 Aurora 팔레트 P5~P2 정렬.
    """
    blocks: list[str] = []
    for rarity, tag, text, border, font_sz in _DEFAULT_RARITY_STYLES:
        blocks.append(make_layer_block(
            LAYER_DEFAULT_RARITY,
            f"레어리티 기본 {rarity} (font {font_sz})",
            conditions=[f"Rarity {rarity}"],
            style=LayerStyle(
                text=text,
                border=border,
                font=font_sz,
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

    Wreckers L2417~2444 4블록 구조 이식 — AreaLevel + 크기 제한으로 엔드게임 인벤 오염 방지.
    - RGB 캠페인 (AL<68) — 전체 크기
    - RGB 옐로우맵 이하 (AL<81) — 소형만 (H<=3, W=1)
    - 6소켓 화이트맵 이하 (AL<78) — 전체 크기
    - 6소켓 레드맵 구간 (AL 78~82) — 소형만 (H<=3, W<=2)
    - AL>82(T16+)에서는 RGB/6소켓 무표시 = 인벤 여유
    """
    blocks: list[str] = []

    # RGB 캠페인 — AL<68 전체 크기
    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "RGB 캠페인 (AL<68, Chromatic Orb 레시피)",
        conditions=["AreaLevel < 68", "SocketGroup RGB"],
        style=LayerStyle(border=_SOCKET_PINK),
        category_tag="chromatic_campaign",
    ))

    # RGB 옐로우맵 이하 소형만 — AL<81, 1x3 이하
    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "RGB 옐로우맵 소형 (AL<81, H<=3 W=1)",
        conditions=[
            "AreaLevel < 81",
            "SocketGroup RGB",
            "Height <= 3",
            "Width = 1",
        ],
        style=LayerStyle(border=_SOCKET_PINK),
        category_tag="chromatic_small",
    ))

    # 6소켓 화이트맵 이하 전체 — AL<78
    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "6소켓 화이트맵 이하 (AL<78, Jeweller's Orb 레시피)",
        conditions=["AreaLevel < 78", "Sockets >= 6"],
        style=LayerStyle(
            border=_SOCKET_PINK,
            effect="Pink",
            icon="2 Pink Cross",
        ),
        category_tag="jeweller_campaign",
    ))

    # 6소켓 레드맵 소형만 — AL 78~82, 2x3 이하
    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "6소켓 레드맵 소형 (AL 78~82, H<=3 W<=2)",
        conditions=[
            "AreaLevel >= 78",
            "AreaLevel <= 82",
            "Sockets >= 6",
            "Height <= 3",
            "Width <= 2",
        ],
        style=LayerStyle(
            border=_SOCKET_PINK,
            effect="Pink",
            icon="2 Pink Cross",
        ),
        category_tag="jeweller_small",
    ))

    # Epic 6-Link Corrupted — Wreckers L2457 Red 보더 parity.
    # Corrupted 블록이 uncorrupted Epic보다 먼저 와야 함 (POE 필터는 top-down,
    # 첫 Continue=False가 승리). 순서 반전 시 uncorrupted가 모든 6L을 잡음.
    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "Epic 6-Link 부패 (Red border, Wreckers L2457)",
        conditions=["LinkedSockets >= 6", "Corrupted True"],
        style=LayerStyle(
            font=45,
            text="255 255 255",
            border="200 0 0",   # Red (부패 시각 신호)
            bg="200 0 0 255",
            effect="Red",
            icon="0 Pink Star",
            custom_sound=("6Link.mp3", 300),
        ),
        continue_=False,
        category_tag="epic_6link_corrupted",
    ))

    # Epic 6-Link uncorrupted (Wreckers L2446 + Sanavi 6l) — PathcraftAI 스타일.
    # 디자인: 빨간 BG + 흰 텍스트 + 핑크 보더/Star + Sanavi CustomAlertSound "6Link.mp3"
    # Continue=False (최종 Show) — L9/L11 cascade로부터 보호. 6-Link Rare는 SSF 연간
    # 최대 이벤트급 드롭이므로 캐스케이드 원칙 예외 정당.
    blocks.append(make_layer_block(
        LAYER_SOCKET_BORDER,
        "Epic 6-Link (Rare/Magic/Normal, Sanavi 사운드)",
        conditions=["LinkedSockets >= 6"],
        style=LayerStyle(
            font=45,
            text="255 255 255",
            border=_SOCKET_PINK,
            bg="200 0 0 255",
            effect="Red",
            icon="0 Pink Star",
            custom_sound=("6Link.mp3", 300),
        ),
        continue_=False,
        category_tag="epic_6link",
    ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L4: Special Base (Wreckers 오렌지 복원 — 특수 BaseType)
# ---------------------------------------------------------------------------
#
# 레퍼런스: Wreckers SSF Filter L146 "Catch All, 'WTF is that?!' items,
# new items, items with unique mods, & special BaseTypes".
# L2 DEFAULT_RARITY가 Normal/Magic/Rare를 White/Blue/Yellow로 덮어쓴 뒤,
# 특수 베이스만 다시 Orange 텍스트로 복원 — 드롭 시 즉시 눈에 띄게.

_SPECIAL_BASE_ORANGE = "255 123 0"

# Wreckers L148 원본 BaseType 목록. Jewel/Trinket 등 클래스별 섞여 있음 —
# 레퍼런스 철학상 단일 블록으로 유지 (추가/삭제는 Wreckers 업데이트 따라).
_WRECKERS_SPECIAL_BASES = (
    "Disapprobation Axe", "Psychotic Axe", "Foundry Bow", "Solarine Bow",
    "Malign Fangs", "Void Fangs", "Pressurised Dagger", "Pneumatic Dagger",
    "Flashfire Blade", "Infernal Blade", "Fishing Rod",
    "Crack Mace", "Boom Mace",
    "Oscillating Sceptre", "Stabilising Sceptre", "Alternating Sceptre",
    "Reciprocation Staff", "Battery Staff",
    "Potentiality Rod", "Eventuality Rod",
    "Capricious Spiritblade", "Anarchic Spiritblade",
    "Blasting Blade", "Banishing Blade",
    "Calling Wand", "Congregator Wand", "Convening Wand",
    "Accumulator Wand", "Convoking Wand",
    "Magmatic Tower Shield", "Heat-attuned Tower Shield",
    "Polar Buckler", "Cold-attuned Buckler",
    "Bone Spirit Shield", "Ivory Spirit Shield", "Subsuming Spirit Shield",
    "Fossilised Spirit Shield", "Transfer-attuned Spirit Shield",
    "Sorrow Mask", "Atonement Mask", "Penitent Mask",
    "Imp Crown", "Demon Crown", "Bone Helmet", "Archdemon Crown",
    "Gale Crown", "Winter Crown", "Blizzard Crown",
    "Grasping Mail", "Sacrificial Garb",
    "Preserving Gauntlets", "Guarding Gauntlets", "Spiked Gloves",
    "Thwarting Gauntlets", "Tinker Gloves", "Apprentice Gloves",
    "Gripped Gloves", "Trapsetter Gloves", "Leyline Gloves",
    "Aetherwind Gloves", "Nexus Gloves", "Apothecary's Gloves",
    "Basemetal Treads", "Darksteel Treads", "Brimstone Treads",
    "Cloudwhisper Boots", "Windbreak Boots", "Stormrider Boots",
    "Duskwalk Slippers", "Nightwind Slippers", "Dreamquest Slippers",
    "Two-Toned Boots", "Fugitive Boots",
    "Focused Amulet", "Simplex Amulet", "Astrolabe Amulet",
    "Marble Amulet", "Seaglass Amulet", "Blue Pearl Amulet",
    "Undying Flesh Talisman", "Rot Head Talisman",
    "Stygian Vise", "Micro-Distillery Belt", "Mechanical Belt",
    "Vanguard Belt", "Crystal Belt", "Mechalarm Belt",
    "Cogwork Ring", "Composite Ring", "Dusk Ring", "Geodesic Ring",
    "Gloam Ring", "Helical Ring", "Manifold Ring", "Nameless Ring",
    "Penumbra Ring", "Ratcheting Ring", "Shadowed Ring", "Tenebrous Ring",
    "Bone Ring", "Prismatic Ring", "Cerulean Ring", "Iolite Ring",
    "Opal Ring", "Steel Ring", "Vermillion Ring",
    "Cobalt Jewel", "Ghastly Eye Jewel",
    "Thief's Trinket",
)


def layer_special_base() -> str:
    """L4 Special Base — Wreckers식 특수 BaseType 오렌지 텍스트 복원.

    L2 DEFAULT_RARITY의 White/Blue/Yellow 텍스트 위에 Orange를 덮어씌워
    희귀·신규 베이스가 인벤토리에서 즉시 구별되게 한다.
    """
    quoted = " ".join(f'"{b}"' for b in _WRECKERS_SPECIAL_BASES)
    block = make_layer_block(
        LAYER_SPECIAL_BASE,
        "Wreckers 특수 BaseType (오렌지 복원)",
        conditions=[f"BaseType == {quoted}"],
        style=LayerStyle(text=_SPECIAL_BASE_ORANGE),
        category_tag="wreckers_special",
    )
    return block


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
    """L6 T1 Border — ilvl>=86 크래프팅 가치 베이스.

    NeverSink/Wreckers 표준: **모든 클래스 같은 흰색 보더 + 별**.
    클래스 그룹별 색 차별은 레퍼런스 패턴 아님 (ItemLevel/Tier/Property로 차별).
    """
    bases = load_t1_bases()
    blocks: list[str] = []

    # 통일 스타일 (NeverSink/Wreckers 표준)
    style = LayerStyle(
        border="255 255 255",  # 흰색 (NeverSink/Wreckers 일치)
        effect="White",
        icon="0 White Star",
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
            # Influenced는 추가 강조 — 흰색 + 검정 배경 + 사운드
            style=LayerStyle(border="255 255 255", bg="50 50 50 240",
                             effect="White", icon="0 White Star",
                             sound="2 300"),
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

# L7 weapon_phys_proxy: strictness → HasExplicitMod count 하한.
# 0~1은 NeverSink 'weapon_physpure' 대응(관대 + Mirrored/Corrupted 배제),
# 2+는 NeverSink 'weapon_phys' 대응(엄격).
# 레퍼런스: _analysis/neversink_weaponphys_rules.md
_STRICTNESS_WEAPON_MOD_COUNT: dict[int, int] = {0: 2, 1: 2, 2: 3, 3: 3, 4: 3}


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
    mode: str = "ssf",
    game: str = "poe1",
) -> str:
    """L9 Progressive Hide — AL 기반 단계적 숨김.

    strictness 0: 모든 블록 비활성 (빈 문자열 반환)
    strictness 1~4: 표 참조 (각 레벨마다 Hide 블록 누적).
    모든 Hide 블록은 Continue 포함 → L10 RE_SHOW에서 예외 재Show 가능.

    mode (SSF/HCSSF vs Trade): SSF/HCSSF는 bare 젬 숨기지 않음 (대체스킬/벤더 가치).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")
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

    # Normal/Magic 전체 — 장비 클래스만 대상 (젬/맵/커런시/디비카/프래그먼트/퀘스트 아이템 제외)
    # NeverSink 관례: blanket Rarity hide는 Class 제약 필수. 안 그러면 젬/커런시까지 숨겨짐.
    equip_classes = _equip_classes_for(game)
    if strictness >= 1:
        blocks.append(_hide_block(
            f"Normal 장비 AL>={d.normal_all_al}",
            conditions=[
                "Rarity Normal",
                f"Class {equip_classes}",
                f"AreaLevel >= {d.normal_all_al}",
            ],
            category_tag="normal_all",
        ))

    # Magic 전체 (AL >= 24) — 동일한 장비 클래스 제약
    if strictness >= 2:
        blocks.append(_hide_block(
            f"Magic 장비 AL>={d.magic_all_al}",
            conditions=[
                "Rarity Magic",
                f"Class {equip_classes}",
                f"AreaLevel >= {d.magic_all_al}",
            ],
            category_tag="magic_all",
        ))

    # 레벨링 초반 베이스 (strictness >= 2)
    # Rarity Normal Magic 제약 필수 — unique_tiers.json에 Simple Robe/Leather Cap/Crude Bow/
    # Rawhide Boots 등 7종 leveling base가 유니크 base로 존재. Rarity 제약 없으면 Unique
    # Goldrim/Tabula/Redbeak/Wanderlust 등이 L8 unique Show+Continue 뒤 L9 Hide로 덮임.
    if strictness >= 2:
        for base, hide_al in d.leveling_bases_early:
            blocks.append(_hide_block(
                f"레벨링 초반 {base} AL>={hide_al}",
                conditions=[
                    "Rarity Normal Magic",
                    f'BaseType == "{base}"',
                    f"AreaLevel >= {hide_al}",
                ],
                category_tag="level_early",
            ))

    # Gem Hide — 모드별 정책:
    # - Trade: strictness >= 2부터 bare 젬 숨김 (구매 대체 가능)
    # - SSF/HCSSF: 젬 전체 유지 (대체 스킬·레벨링·벤더 레시피 가치)
    if mode == "trade" and strictness >= 2:
        blocks.append(_hide_block(
            f"기본 젬 AL>={d.gem_hide_al} (trade)",
            conditions=[
                'Class == "Skill Gems" "Support Gems"',
                f"AreaLevel >= {d.gem_hide_al}",
                "Quality 0",
                "Corrupted False",
            ],
            category_tag="gem",
        ))

    # 중후반 장비 베이스 (strictness >= 3)
    # Rarity Normal Magic 제약 — level_early와 동일 이유. Astral Plate/Crusader Plate/
    # Devout Chainmail 등 60+종이 유니크 base. Rarity 없으면 맵핑 구간 Unique 드롭 숨김.
    if strictness >= 3:
        for base, hide_al in d.equipment_bases_midgame:
            blocks.append(_hide_block(
                f"중후반 {base} AL>={hide_al}",
                conditions=[
                    "Rarity Normal Magic",
                    f'BaseType == "{base}"',
                    f"AreaLevel >= {hide_al}",
                ],
                category_tag="level_mid",
            ))

    # Flask (AL >= 73, strictness >= 3). POE2 에는 Hybrid Flasks 없음 — Life/Mana 만.
    if strictness >= 3:
        if game == "poe1":
            flask_classes = 'Class "Life Flasks" "Mana Flasks" "Hybrid Flasks"'
            flask_label = "Life/Mana/Hybrid"
        else:
            flask_classes = 'Class "Life Flasks" "Mana Flasks"'
            flask_label = "Life/Mana"
        blocks.append(_hide_block(
            f"기본 {flask_label} 플라스크 AL>={d.flask_hide_al}",
            conditions=[
                flask_classes,
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


def layer_currency(data: Optional[CategoryData] = None, mode: str = "ssf") -> str:
    """L8 Currency — **모드별** 티어 (Trade/SSF/HCSSF 우선순위 다름).

    pathcraft_palette.get_currency_tiers(mode) 사용:
    - Trade: Mirror/Divine 최상, Chaos 중간 (구매 가능 커런시 우선)
    - SSF: Alch/Chaos/Fusing 최상 (자급자족 크래프팅 핵심)
    - HCSSF: Alch/Scouring/Annulment 최상 (생존 + 안전한 크래프팅)
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")
    if data is not None:
        # 명시적 data 전달 시 (테스트용) — 기존 동작 유지
        currency_source = data.currency_tiers
        tier_map = _CURRENCY_TIER_MAP
    else:
        # 모드별 팔레트 사용
        from pathcraft_palette import get_currency_tiers
        mode_tiers = get_currency_tiers(mode)
        # palette 티어를 NeverSink 티어 형식으로 매핑 (역매핑)
        currency_source = {f"{k.lower()}_palette": v for k, v in mode_tiers.items()}
        tier_map = {f"{k.lower()}_palette": k for k in mode_tiers}

    # Leveling supplies + 기본 크래프팅 오브 — layer_leveling_supplies / layer_basic_orbs가 별도 처리
    # 주의: Armourer's Scrap / Blacksmith's Whetstone은 currency tier(P5_MINOR/P6_LOW)에 등록되어
    # 전 AL에서 layer_currency가 처리. leveling_supplies는 Wisdom/Portal만 전담.
    LEVELING_SUPPLY_BASES = {
        "Scroll of Wisdom", "Portal Scroll",
        # T5 Tan
        "Orb of Transmutation", "Orb of Augmentation", "Orb of Alteration", "Chromatic Orb",
        # T4 Yellow
        "Orb of Chance", "Jeweller's Orb",
        # T3 Yellow-Orange
        "Orb of Fusing", "Blessed Orb", "Glassblower's Bauble",
        "Orb of Unmaking", "Orb of Binding", "Regal Orb",
        # T2 Orange
        "Exalted Orb", "Chaos Orb", "Orb of Scouring",
        "Orb of Regret", "Vaal Orb", "Gemcutter's Prism", "Orb of Annulment",
        # T1 Max — layer_basic_orbs T1 MAX 블록이 처리 (Cobalt convention)
        "Divine Orb", "Mirror of Kalandra", "Mirror Shard", "Sacred Orb",
        "Awakener's Orb",
    }

    blocks: list[str] = []
    for tier_name, bases in currency_source.items():
        palette_tier = tier_map.get(tier_name)
        if palette_tier is None or not bases:
            continue
        # leveling supplies 제외 (별도 layer 전담)
        bases = [b for b in bases if b not in LEVELING_SUPPLY_BASES]
        if not bases:
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
                'Class "Currency" "Map Fragments"',
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


def _load_hc_divcard_override(filepath: Optional[Path] = None) -> dict[str, list[str]]:
    """HCSSF T1/T2 override 데이터 로드 (hc_divcard_tiers.json).

    파일 없거나 손상 시 빈 override 반환 (SC 흐름 유지).
    """
    path = filepath if filepath is not None else _DATA_DIR / "hc_divcard_tiers.json"
    if not path.exists():
        logger.warning("hc_divcard_tiers.json not found at %s — HCSSF override 비활성", path)
        return {"t1_override": [], "t2_override": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("hc_divcard_tiers.json 로드 실패: %s — HCSSF override 비활성", e)
        return {"t1_override": [], "t2_override": []}
    return {
        "t1_override": list(raw.get("t1_override", [])),
        "t2_override": list(raw.get("t2_override", [])),
    }


def _hc_override_block(palette_tier: str, label: str, cards: list[str], tag: str) -> str:
    """HCSSF T1/T2 override 단일 블록 생성."""
    style = style_from_palette("divcard", palette_tier)
    if palette_tier == "P1_KEYSTONE":
        style.effect = "Purple"
        style.icon = "0 Purple Square"
    elif palette_tier == "P2_CORE":
        style.icon = "1 Purple Square"
    quoted = " ".join(f'"{c}"' for c in cards)
    return make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"디비카 {label} ({len(cards)}종)",
        conditions=[
            'Class "Divination Cards"',
            f'BaseType == {quoted}',
        ],
        style=style,
        continue_=False,
        category_tag=tag,
    )


def layer_divcards(data: Optional[CategoryData] = None, mode: str = "ssf") -> str:
    """L8 Divination Cards — neversink 5 티어.

    HCSSF 모드에서는 앞에 HC 경제 기반 T1/T2 override 블록을 삽입 (keystone/core).
    override 카드는 첫 매치로 소비되고 뒤의 SC 5티어 흐름에는 영향 없음.
    """
    d = data if data is not None else load_category_data()
    blocks: list[str] = []

    if mode == "hcssf":
        hc = _load_hc_divcard_override()
        for key, palette_tier, label in (
            ("t1_override", "P1_KEYSTONE", "HC-T1 override"),
            ("t2_override", "P2_CORE", "HC-T2 override"),
        ):
            cards = hc.get(key, [])
            if cards:
                blocks.append(_hc_override_block(
                    palette_tier, label, cards, tag=f"divcard_hc_{key}",
                ))

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
# L8: SSF 카테고리 (Lifeforce / Splinter / Scarab) — GGPK 기반 자동 추출
# ---------------------------------------------------------------------------
#
# 리그 업데이트 시 extract_data.exe 재실행 → BaseItemTypes.json 갱신 →
# 여기서 자동으로 신규 아이템 포함. 수동 하드코딩 금지.

_GGPK_CACHE: Optional[dict] = None
_TAGS_CACHE: Optional[list] = None  # Tags.json Id 인덱스 (TagsKeys 해석용)


@dataclass
class GGPKItems:
    """GGPK BaseItemTypes에서 카테고리별 추출 결과."""

    lifeforce: tuple[str, ...] = ()
    splinter_breach: tuple[str, ...] = ()
    splinter_legion: tuple[str, ...] = ()
    splinter_simulacrum: tuple[str, ...] = ()
    scarabs_all: tuple[str, ...] = ()
    scarabs_special: tuple[str, ...] = ()  # uber/uniques/influence 태그 (F0-fix-2)
    # Essences 티어별 — POE는 7 티어 (T0 부패 제외)
    essence_deafening: tuple[str, ...] = ()
    essence_shrieking: tuple[str, ...] = ()
    essence_screaming: tuple[str, ...] = ()
    essence_wailing: tuple[str, ...] = ()
    essence_weeping: tuple[str, ...] = ()
    essence_muttering: tuple[str, ...] = ()
    essence_whispering: tuple[str, ...] = ()
    # 부패 에센스 + Remnant — 별도 처리 (tier prefix 없음, 최고가)
    essence_corrupt: tuple[str, ...] = ()
    remnant_corruption: tuple[str, ...] = ()
    # Fossils / Resonators
    fossils_high: tuple[str, ...] = ()
    fossils_basic: tuple[str, ...] = ()
    resonators_prime: tuple[str, ...] = ()
    resonators_powerful: tuple[str, ...] = ()
    resonators_low: tuple[str, ...] = ()
    # Delirium / Oils
    delirium_orbs: tuple[str, ...] = ()
    oils_top: tuple[str, ...] = ()
    oils_high: tuple[str, ...] = ()
    oils_mid: tuple[str, ...] = ()
    oils_low: tuple[str, ...] = ()
    oils_premium: tuple[str, ...] = ()  # Reflective / Prismatic / Tainted (Wreckers 최상급)


def load_ggpk_items(filepath: Optional[Path] = None) -> GGPKItems:
    """data/game_data/BaseItemTypes.json에서 SSF 카테고리 추출 (태그 기반 분류).

    2026-04-17 F0-fix-2: `BaseItemTypes.TagsKeys` → `Tags.Id` 해결로 Name 휴리스틱 대체.
    번역된 클라이언트/리그 명명 변경에도 robust. 태그 없는 카테고리는 Name fallback.

    태그 매핑 (Tags.Id):
    - `breachstone_splinter` → 5 Breach 조각
    - `legion_splinter` → 5 Legion 조각
    - `scarab` → 전체 스카랩 (190)
    - `uber_scarab | uniques_scarab | influence_scarab` → 고가 스카랩 (11)
    - `essence` → 전체 에센스 (프리필터), Name 접두사로 티어 분류

    Name fallback (태그 없음):
    - Lifeforce: Id prefix `HarvestSeed` + Name 'Crystallised Lifeforce'
    - Simulacrum Splinter: Name 정확 매칭 (affliction_orb 태그는 Delirium과 공유)
    - Fossils/Resonators/Delirium Orbs/Oils: 기존 Name 규칙 유지 (F0-fix-2 범위 외)
    """
    global _GGPK_CACHE, _TAGS_CACHE
    path = filepath if filepath is not None else _DATA_DIR / "game_data" / "BaseItemTypes.json"
    if not path.exists():
        return GGPKItems()
    if _GGPK_CACHE is None:
        _GGPK_CACHE = json.loads(path.read_text(encoding="utf-8"))

    tags_path = _DATA_DIR / "game_data" / "Tags.json"
    if _TAGS_CACHE is None and tags_path.exists():
        _TAGS_CACHE = [t.get("Id", "") for t in json.loads(tags_path.read_text(encoding="utf-8"))]
    tags_index = _TAGS_CACHE or []

    bt = _GGPK_CACHE
    if not isinstance(bt, list):
        return GGPKItems()

    def _name(b: dict) -> str:
        return b.get("Name", "") if isinstance(b, dict) else ""

    def _tags(b: dict) -> set:
        if not isinstance(b, dict):
            return set()
        return {
            tags_index[i] for i in b.get("TagsKeys", [])
            if isinstance(i, int) and 0 <= i < len(tags_index)
        }

    # Lifeforce: 태그 없음 → Id prefix + Name 이중 검증
    lifeforce = tuple(sorted({
        _name(b) for b in bt
        if str(b.get("Id", "")).startswith("Metadata/Items/Currency/HarvestSeed")
        and "Crystallised Lifeforce" in _name(b)
        and not _name(b).startswith("[")
    }))

    splinter_breach = tuple(sorted({
        _name(b) for b in bt if "breachstone_splinter" in _tags(b)
    }))

    splinter_legion = tuple(sorted({
        _name(b) for b in bt if "legion_splinter" in _tags(b)
    }))

    # Simulacrum: affliction_orb 태그는 Delirium Orb와 공유 → Name 정확 매칭 유지
    splinter_simulacrum = ("Simulacrum Splinter",) if any(
        _name(b) == "Simulacrum Splinter" for b in bt
    ) else ()

    scarabs_all = tuple(sorted({
        _name(b) for b in bt if "scarab" in _tags(b) and not _name(b).startswith("[")
    }))

    # 고가 스카랩: GGPK 태그(uber/uniques/influence) UNION 위키 Name family(Horned/Titanic/Influencing)
    # POE Wiki는 4개 "Influencing Scarab of X"를 하나의 family로 묶음(disambiguation) —
    # GGPK는 1개만 influence_scarab 태그, 나머지 3개는 scarab_grants_extra_content.
    # 사용자 관점 분류 보존을 위해 union 채택 (F0-fix-2 triple-check, 2026-04-17).
    SPECIAL_SCARAB_TAGS = {"uber_scarab", "uniques_scarab", "influence_scarab"}
    SPECIAL_SCARAB_PREFIXES = ("Horned ", "Titanic ", "Influencing ")
    scarabs_special = tuple(sorted({
        _name(b) for b in bt
        if "scarab" in _tags(b) and (
            _tags(b) & SPECIAL_SCARAB_TAGS
            or _name(b).startswith(SPECIAL_SCARAB_PREFIXES)
        )
    }))

    # Essences 티어: essence 태그로 프리필터 + 접두사로 티어 분류
    def _essences_with_prefix(prefix: str) -> tuple[str, ...]:
        return tuple(sorted({
            _name(b) for b in bt
            if "essence" in _tags(b)
            and _name(b).startswith(prefix + " Essence of")
        }))
    essence_deafening = _essences_with_prefix("Deafening")
    essence_shrieking = _essences_with_prefix("Shrieking")
    essence_screaming = _essences_with_prefix("Screaming")
    essence_wailing = _essences_with_prefix("Wailing")
    essence_weeping = _essences_with_prefix("Weeping")
    essence_muttering = _essences_with_prefix("Muttering")
    essence_whispering = _essences_with_prefix("Whispering")
    # 부패 에센스: T0 (Hysteria/Insanity/Horror/Delirium/Desolation) + Remnant of Corruption
    _CORRUPT_ESSENCE_NAMES = {
        "Essence of Hysteria", "Essence of Insanity",
        "Essence of Horror", "Essence of Delirium",
        "Essence of Desolation",
    }
    essence_corrupt = tuple(sorted({
        _name(b) for b in bt
        if "essence" in _tags(b) and _name(b) in _CORRUPT_ESSENCE_NAMES
    }))
    remnant_corruption = tuple(sorted({
        _name(b) for b in bt if _name(b) == "Remnant of Corruption"
        and "Metadata/Items/Currency" in b.get("InheritsFrom", "")
    }))

    # Fossils
    all_fossils = {
        _name(b) for b in bt
        if "Fossil" in _name(b)
        and "Metadata/Items/Currency" in b.get("InheritsFrom", "")
        and not _name(b).startswith("[")
    }
    # HIGH_FOSSILS: Delve 3.5 이후 상위 12개 가치 fossil (Wiki "Fossil" tier 표 + Wreckers SSF).
    # 선정 기준: craft 수요 (Pristine=life, Gilded=quality, Bound=minion) 및 가격.
    # 출처: POE Wiki https://www.poewiki.net/wiki/Fossil (2026-04-19 확인, F7 감사).
    HIGH_FOSSILS = {
        "Sanctified Fossil", "Pristine Fossil", "Opulent Fossil", "Gilded Fossil",
        "Bound Fossil", "Encrusted Fossil", "Hollow Fossil", "Shuddering Fossil",
        "Fractured Fossil", "Glyphic Fossil", "Tangled Fossil", "Faceted Fossil",
    }
    fossils_high = tuple(sorted(all_fossils & HIGH_FOSSILS))
    fossils_basic = tuple(sorted(all_fossils - HIGH_FOSSILS))

    # Resonators
    all_resonators = {
        _name(b) for b in bt
        if "Resonator" in _name(b)
        and "Metadata/Items" in b.get("InheritsFrom", "")
        and not _name(b).startswith("[")
    }
    resonators_prime = tuple(sorted(n for n in all_resonators if n.startswith("Prime ")))
    resonators_powerful = tuple(sorted(n for n in all_resonators if n.startswith("Powerful ")))
    resonators_low = tuple(sorted(n for n in all_resonators
                                   if n.startswith(("Potent ", "Primitive "))))

    # Delirium Orbs
    delirium_orbs = tuple(sorted({
        _name(b) for b in bt if "Delirium Orb" in _name(b)
    }))

    # Oils
    all_oils = {
        _name(b) for b in bt
        if _name(b).endswith(" Oil") and not _name(b).startswith("[")
    }
    # Oil 5단계 티어 — Blight 3.8 enchant 가치 기준.
    # TOP: Golden/Silver/Opalescent (top anoint 가능, amulet enchant 상위)
    # HIGH: Black/Crimson/Violet (중상위 anoint + Delirium passive node)
    # MID/LOW: 저가 (양 축적용)
    # PREMIUM: Reflective/Prismatic/Tainted (Blighted map + Ravaged Blight, SSF 최상급)
    # 출처: Wreckers L1585-1674 13단계 + POE Wiki Oil 페이지 (2026-04-19 F7 감사 확인).
    OILS_TOP = {"Golden Oil", "Silver Oil", "Opalescent Oil"}
    OILS_HIGH = {"Black Oil", "Crimson Oil", "Violet Oil"}
    OILS_MID = {"Indigo Oil", "Teal Oil", "Azure Oil", "Verdant Oil"}
    OILS_LOW = {"Amber Oil", "Sepia Oil", "Clear Oil"}
    OILS_PREMIUM = {"Reflective Oil", "Prismatic Oil", "Tainted Oil"}
    oils_top = tuple(sorted(all_oils & OILS_TOP))
    oils_high = tuple(sorted(all_oils & OILS_HIGH))
    oils_mid = tuple(sorted(all_oils & OILS_MID))
    oils_low = tuple(sorted(all_oils & OILS_LOW))
    oils_premium = tuple(sorted(all_oils & OILS_PREMIUM))

    return GGPKItems(
        lifeforce=lifeforce,
        splinter_breach=splinter_breach,
        splinter_legion=splinter_legion,
        splinter_simulacrum=splinter_simulacrum,
        scarabs_all=scarabs_all,
        scarabs_special=scarabs_special,
        essence_deafening=essence_deafening,
        essence_shrieking=essence_shrieking,
        essence_screaming=essence_screaming,
        essence_wailing=essence_wailing,
        essence_weeping=essence_weeping,
        essence_muttering=essence_muttering,
        essence_whispering=essence_whispering,
        essence_corrupt=essence_corrupt,
        remnant_corruption=remnant_corruption,
        fossils_high=fossils_high,
        fossils_basic=fossils_basic,
        resonators_prime=resonators_prime,
        resonators_powerful=resonators_powerful,
        resonators_low=resonators_low,
        delirium_orbs=delirium_orbs,
        oils_top=oils_top,
        oils_high=oils_high,
        oils_mid=oils_mid,
        oils_low=oils_low,
        oils_premium=oils_premium,
    )


_ID_MOD_CACHE: Optional[dict] = None


def _load_id_mod_filtering() -> dict:
    """data/id_mod_filtering.json 로드 (NeverSink 추출 mod 데이터)."""
    global _ID_MOD_CACHE
    if _ID_MOD_CACHE is not None:
        return _ID_MOD_CACHE
    path = _DATA_DIR / "id_mod_filtering.json"
    if not path.exists():
        _ID_MOD_CACHE = {}
        return _ID_MOD_CACHE
    _ID_MOD_CACHE = json.loads(path.read_text(encoding="utf-8")).get("by_class", {})
    return _ID_MOD_CACHE


LOW_LIFE_SUFFIX_MODS = ("Hale", "Healthy", "Sanguine")


def layer_id_mod_filtering(mode: str = "ssf", strictness: int = 0) -> str:
    """L8 ID Mod Filtering — NeverSink [[0600]/[0700]/[0800]] 패턴 (Identified rare 가치 mod).

    각 클래스별 top mod 리스트로 Identified Rare 우선 Show.
    뒤이은 Hide: Identified rare without top mods + AL>=75 → 인벤 정리.

    SSF/HCSSF 핵심 — 인벤 ID 후 정리에 필수.
    Trade는 less aggressive (Hide 임계 더 높음).

    strictness >= 4 (UberPlus): Cobalt uberStrict convention — Show 조건에
    `HasExplicitMod 0 "Hale" "Healthy" "Sanguine"` 추가. 저급 생명력 접미사가
    섞인 rare는 top mod가 있어도 Show 탈락 → Hide로 흘러가 숨김. 혼합 mod
    rare 일부 missed 리스크 있음 (아키텍처 Phase 7 audit 참조).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    by_class = _load_id_mod_filtering()
    if not by_class:
        return ""

    blocks: list[str] = []

    # NeverSink 패턴: 모든 ID Mod 블록 동일 청록 (0 240 190) — 클래스별 차별 없음
    id_mod_style = LayerStyle(
        font=38,
        border="0 240 190",
        text="0 240 190",
        bg="0 75 30 220",
        effect="Blue",
        icon="1 Blue Diamond",
    )

    exclude_low_life = strictness >= 4
    low_life_quoted = " ".join(f'"{m}"' for m in LOW_LIFE_SUFFIX_MODS)

    # Per-class Show block (Identified + Class + top mod 보유)
    for cls, mods in sorted(by_class.items()):
        if not mods:
            continue
        quoted_mods = " ".join(f'"{m}"' for m in mods)
        conditions = [
            "Identified True",
            "Rarity Rare",
            f'Class == "{cls}"',
            "ItemLevel >= 68",
            f"HasExplicitMod {quoted_mods}",
        ]
        if exclude_low_life:
            conditions.append(f"HasExplicitMod 0 {low_life_quoted}")
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"ID Rare {cls} (top mod {len(mods)}종)",
            conditions=conditions,
            style=id_mod_style,
            continue_=True,
            category_tag=f"id_mod_{cls.lower().replace(' ','_')}",
        ))

    # Final Hide: Identified rare without top mods at AL>=75 (Trade는 80, HCSSF는 73 더 엄격)
    hide_al = {"trade": 80, "ssf": 75, "hcssf": 73}[mode]
    all_classes = ' '.join(f'"{c}"' for c in sorted(by_class.keys()))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"ID Rare 무가치 Hide (AL>={hide_al}, top mod 0)",
        conditions=[
            "Identified True",
            "Rarity Rare",
            f"Class == {all_classes}",
            f"AreaLevel >= {hide_al}",
            "Mirrored False", "Corrupted False",
            "LinkedSockets < 5",  # 5-Link 이상은 가치 (벤더)
        ],
        style=LayerStyle(disable_drop=True),
        continue_=True,
        action="Hide",
        category_tag="id_mod_hide_junk",
    ))

    return "".join(blocks)


def layer_leveling_supplies(mode: str = "ssf") -> str:
    """L8 Leveling Supplies — Wisdom/Portal/Scrap/Whetstone 등 고유 스타일.

    NeverSink 패턴 복사:
    - Scroll of Wisdom: bronze border (200/100/60) — 정체된 ID 핵심
    - Portal Scroll: blue border (60/100/200) — 도시 복귀
    - StackSize >= 2 더 큰 강조
    AL <= 67 (액트 구간) 만 활성. 엔드게임에선 L9 supply hide가 처리.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Wisdom Scroll — bronze
    for stack, font, tag in [(2, 45, "wisdom_stack2"), (1, 38, "wisdom_single")]:
        cond = ['Class "Stackable Currency"',
                'BaseType == "Scroll of Wisdom"',
                "AreaLevel <= 67"]
        if stack > 1:
            cond.append(f"StackSize >= {stack}")
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Wisdom Scroll{' x'+str(stack)+'+' if stack>1 else ''}",
            conditions=cond,
            style=LayerStyle(font=font, border="200 100 60", text="200 130 80",
                             bg="30 5 5 220"),
            continue_=True,
            category_tag=tag,
        ))

    # Portal Scroll — blue
    for stack, font, tag in [(2, 45, "portal_stack2"), (1, 38, "portal_single")]:
        cond = ['Class "Stackable Currency"',
                'BaseType == "Portal Scroll"',
                "AreaLevel <= 67"]
        if stack > 1:
            cond.append(f"StackSize >= {stack}")
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Portal Scroll{' x'+str(stack)+'+' if stack>1 else ''}",
            conditions=cond,
            style=LayerStyle(font=font, border="60 100 200", text="80 130 220",
                             bg="5 8 40 220"),
            continue_=True,
            category_tag=tag,
        ))

    # Scrap/Whetstone은 layer_currency P5_MINOR/P6_LOW가 전 AL 처리 (LEVELING_SUPPLY_BASES 제외).

    return "".join(blocks)


def layer_basic_orbs(mode: str = "ssf") -> str:
    """L8 기본 크래프팅 오브 — **Aurora 팔레트 카테고리별 Hue 차별화**.

    tier마다 다른 Aurora 카테고리 매핑으로 hue 자체가 다름:
    - T1 MAX: `links` Crimson (빨강 계열 중 최대 채도)
    - T2 High: `currency` Hot Coral (메인 핫 코랄)
    - T3 Mid: `gold` Lemonade (노랑 계열)
    - T4 Low: `gold` P3 (어둡지만 여전히 노랑 hue)
    - T5 Tan: `base` Turquoise P4 (청록 — 완전 다른 hue)
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # T1 MAX — Divine/Mirror/Awakener's (Crimson links 팔레트)
    # Cobalt convention: 강한 커뮤니티 T1 기호 (red star + sound 6). Awakener's Orb은
    # Sirus 드롭 + influence 결합용 고가 커런시, POE 커뮤니티 Mirror-tier 인식 강함.
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "기본오브 T1 최고가 (Divine/Mirror/Awakener's)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Divine Orb" "Mirror of Kalandra" "Mirror Shard"'
            ' "Sacred Orb" "Awakener\'s Orb"',
        ],
        style=style_from_palette("links", "P1_KEYSTONE",
                                 effect="Red", icon="0 Red Star",
                                 sound="6 300"),
        continue_=False,
        category_tag="basic_orb_t1_mirror_divine",
    ))

    # T2 Annulment — currency P1 Hot Coral + 흰색 + Sound (위험 강조)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Orb of Annulment (위험 고가)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Orb of Annulment"',
        ],
        style=style_from_palette("currency", "P1_KEYSTONE",
                                 effect="Red Temp", icon="0 Red Cross",
                                 sound="3 300"),
        continue_=False,
        category_tag="basic_orb_annulment",
    ))

    # T2 표준 — currency P1 Hot Coral (Exalted/Chaos/Scouring/Regret/Vaal/Gemcutter)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "기본오브 T2 (Exalted/Chaos/Scouring/Regret/Vaal/Gemcutter)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Exalted Orb" "Chaos Orb" "Orb of Scouring"'
            ' "Orb of Regret" "Vaal Orb" "Gemcutter\'s Prism"',
        ],
        style=style_from_palette("currency", "P1_KEYSTONE",
                                 effect="Red", icon="1 Red Cross",
                                 sound="2 300"),
        continue_=False,
        category_tag="basic_orb_t2_coral",
    ))

    # T3 Mid — gold P1 Lemonade (Fusing/Blessed/Glassblower/Unmaking/Binding/Regal)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "기본오브 T3 (Fusing/Blessed/Glassblower/Unmaking/Binding/Regal)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Orb of Fusing" "Blessed Orb" "Glassblower\'s Bauble"'
            ' "Orb of Unmaking" "Orb of Binding" "Regal Orb"',
        ],
        style=style_from_palette("gold", "P1_KEYSTONE",
                                 effect="Yellow", icon="1 Yellow Cross"),
        continue_=False,
        category_tag="basic_orb_t3_gold",
    ))

    # T4 Low — gold P3 (어두운 노랑, Chance/Jeweller)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "기본오브 T4 (Chance/Jeweller)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Orb of Chance" "Jeweller\'s Orb"',
        ],
        style=style_from_palette("gold", "P3_USEFUL",
                                 icon="2 Yellow Cross"),
        continue_=False,
        category_tag="basic_orb_t4_gold_dim",
    ))

    # T5 Turquoise — base P4 (Chromatic/Trans/Alter — 청록, 완전 다른 hue)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "기본오브 T5 크래프팅 기본 (Chromatic/Trans/Alter)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Chromatic Orb" "Orb of Transmutation" "Orb of Alteration"',
        ],
        style=style_from_palette("base", "P4_SUPPORT",
                                 icon="2 Cyan Cross"),
        continue_=False,
        category_tag="basic_orb_t5_base",
    ))

    # Augmentation — base P5 (더 어두운 청록, 최저)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Orb of Augmentation (보조)",
        conditions=[
            'Class "Stackable Currency"',
            'BaseType == "Orb of Augmentation"',
        ],
        style=style_from_palette("base", "P5_MINOR",
                                 icon="2 Cyan Cross"),
        continue_=False,
        category_tag="basic_orb_augment",
    ))

    return "".join(blocks)


def layer_hcssf_safety(mode: str = "ssf") -> str:
    """L8 HCSSF Safety — Hardcore SSF에서 생존 우선 강조 (HCSSF 모드만 활성).

    HC = 죽으면 캐릭 영구 손실. Life Flask / 방어 베이스 / Scouring/Annul 최우선.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    if mode != "hcssf":
        return ""  # SSF/Trade 모드에선 비활성

    blocks: list[str] = []

    # Life Flask 모든 magic+ 강조 (HC: 생명 회복 핵심)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "[HCSSF] Life Flask 전체 (Magic+)",
        conditions=[
            'Class "Life Flasks"',
            "Rarity Magic",
        ],
        style=LayerStyle(font=40, border="255 100 100", text="255 200 200",
                         effect="Red", icon="1 Red Cross"),
        continue_=True,
        category_tag="hcssf_life_flask",
    ))

    # 방어 옵션 — Granite/Quartz/Jade Flask (생존 유틸)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "[HCSSF] 방어 Utility Flask (Granite/Quartz/Jade)",
        conditions=[
            'Class "Utility Flasks"',
            'BaseType == "Granite Flask" "Quartz Flask" "Jade Flask" "Basalt Flask"'
            ' "Stibnite Flask" "Sapphire Flask" "Ruby Flask" "Topaz Flask"',
        ],
        style=LayerStyle(font=42, border="255 150 150", effect="Red",
                         icon="0 Red Star"),
        continue_=True,
        category_tag="hcssf_defense_flask",
    ))

    # Movement 유틸 (Quicksilver Flask) — 생존 도주
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "[HCSSF] Quicksilver Flask (이동 도주)",
        conditions=[
            'BaseType == "Quicksilver Flask"',
            "Rarity Magic",
        ],
        style=LayerStyle(font=40, border="200 200 255", effect="Blue",
                         icon="1 Blue Star"),
        continue_=True,
        category_tag="hcssf_quicksilver",
    ))

    return "".join(blocks)


def layer_special_modifiers(mode: str = "ssf") -> str:
    """L8 Special Modifiers — Fractured/Synthesised/Veiled/Quality 완벽 (NeverSink ID Mod 핵심).

    NeverSink [[0600]~[[1300]] 133 블록 중 SSF 가치 큰 핵심만 단순화:
    - Fractured Item True (영구 mod) → 큰 강조
    - Synthesised Item True (Synthesis 영향) → 강조
    - Identified + HasExplicitMod "Veil" → Veiled mod
    - Quality >= 26 (perfection 임계, 크래프팅 chance)
    상세 mod 리스트는 SSF에서 직접 ID로 확인 가능 → 거대 mod list 생략
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Fractured Item — Aurora base P1 Turquoise (영구성 = 견고)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Fractured Item (영구 mod)",
        conditions=[
            "FracturedItem True",
            "Mirrored False", "Corrupted False",
            "Rarity Normal Magic Rare",
        ],
        style=style_from_palette("base", "P1_KEYSTONE",
                                 effect="Cyan", icon="0 Cyan Diamond",
                                 sound="3 300"),
        continue_=True,
        category_tag="mod_fractured",
    ))

    # Synthesised Item — Aurora divcard P1 Electric Lavender (Synthesis 정체성)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Synthesised Item (Synthesis)",
        conditions=[
            "SynthesisedItem True",
            "Mirrored False", "Corrupted False",
            "Rarity Normal Magic Rare",
        ],
        style=style_from_palette("divcard", "P1_KEYSTONE",
                                 effect="Purple", icon="1 Purple Diamond",
                                 sound="3 300"),
        continue_=True,
        category_tag="mod_synthesised",
    ))

    # Veiled Mod — Aurora gold P1 Lemonade (Jun 보상 = 황금)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Veiled Mod (베일 모드)",
        conditions=[
            "Identified True",
            "Rarity Rare",
            'HasExplicitMod "Veil"',
            "Mirrored False",
        ],
        style=style_from_palette("gold", "P1_KEYSTONE",
                                 effect="Yellow", icon="2 Yellow Diamond",
                                 sound="3 300"),
        continue_=True,
        category_tag="mod_veiled",
    ))

    # Quality 26+ Perfection — 크래프팅 chance 임계
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Quality 26+ 완벽 (chance 가능)",
        conditions=[
            "Quality >= 26",
            "Mirrored False", "Corrupted False",
        ],
        style=LayerStyle(font=42, border="100 240 240", effect="Cyan",
                         icon="0 Cyan Diamond"),
        continue_=True,
        category_tag="mod_quality_perfect",
    ))

    # Memory Strands (Necropolis 메커니즘)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Memory Strands 보유 (Necropolis)",
        conditions=[
            "MemoryStrands >= 1",
            "Mirrored False", "Corrupted False",
            "Rarity Normal Magic Rare",
        ],
        style=LayerStyle(font=42, border="200 100 200", effect="Pink",
                         icon="1 Pink Diamond"),
        continue_=True,
        category_tag="mod_memory_strand",
    ))

    return "".join(blocks)


def layer_special_uniques(mode: str = "ssf") -> str:
    """L8 Special Uniques — Replica/Foulborn 변형 유니크 (NeverSink [[3100]] 패턴).

    Replica True / Foulborn True 조건으로 변형 유니크 강조.
    BaseType 리스트는 NeverSink에서 추출 가능하지만 단순 조건만으로도 충분 강조.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # NeverSink 표준: Replica/Foulborn 모두 반전 키스톤 패턴 (text/border=Tangerine, bg=흰)
    _REVERSED_KEYSTONE = LayerStyle(
        font=45, text="175 96 37", border="175 96 37",
        bg="255 255 255 255", effect="Red",
        icon="0 Red Star", sound="1 300",
    )
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Replica Unique 전체",
        conditions=["Rarity Unique", "Replica True"],
        style=_REVERSED_KEYSTONE,
        continue_=True,
        category_tag="unique_replica",
    ))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Foulborn Unique 전체",
        conditions=["Rarity Unique", "Foulborn True"],
        style=_REVERSED_KEYSTONE,
        continue_=True,
        category_tag="unique_foulborn",
    ))

    return "".join(blocks)


def layer_influenced_extra(mode: str = "ssf") -> str:
    """L8 Influenced 강화 — Shaper/Elder/Crusader/Hunter/Redeemer/Warlord 세분.

    L6 influenced는 ilvl>=86 + 노란 보더 단일 처리. 여기서 영향력별 색 분기.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Shaper — 파랑
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Shaper Influenced",
        conditions=["Rarity Rare", "HasInfluence Shaper"],
        style=LayerStyle(border="100 100 255", font=40, effect="Blue",
                         icon="0 Blue Triangle"),
        continue_=True,
        category_tag="infl_shaper",
    ))
    # Elder — 보라
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Elder Influenced",
        conditions=["Rarity Rare", "HasInfluence Elder"],
        style=LayerStyle(border="200 100 255", font=40, effect="Purple",
                         icon="0 Purple Triangle"),
        continue_=True,
        category_tag="infl_elder",
    ))
    # Crusader — 노랑
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Crusader Influenced",
        conditions=["Rarity Rare", "HasInfluence Crusader"],
        style=LayerStyle(border="255 200 80", font=40, effect="Yellow",
                         icon="0 Yellow Triangle"),
        continue_=True,
        category_tag="infl_crusader",
    ))
    # Hunter — 녹색
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Hunter Influenced",
        conditions=["Rarity Rare", "HasInfluence Hunter"],
        style=LayerStyle(border="100 255 100", font=40, effect="Green",
                         icon="0 Green Triangle"),
        continue_=True,
        category_tag="infl_hunter",
    ))
    # Redeemer — 청록
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Redeemer Influenced",
        conditions=["Rarity Rare", "HasInfluence Redeemer"],
        style=LayerStyle(border="100 240 240", font=40, effect="Cyan",
                         icon="0 Cyan Triangle"),
        continue_=True,
        category_tag="infl_redeemer",
    ))
    # Warlord — 빨강
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Warlord Influenced",
        conditions=["Rarity Rare", "HasInfluence Warlord"],
        style=LayerStyle(border="255 80 80", font=40, effect="Red",
                         icon="0 Red Triangle"),
        continue_=True,
        category_tag="infl_warlord",
    ))

    # Eldritch Exarch (Cobalt [[0400]]) — HasSearingExarchImplicit
    # Fractured/Synthesised는 `layer_special_modifiers`가 이미 처리 중 (중복 방지).
    # 여기서는 Eldritch만 추가 — Cobalt는 BaseType 리스트 제한이나 신규 리그 추가 번거로움 →
    # Pathcraft는 implicit 유무로 단순 매칭.
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Eldritch Exarch implicit (Searing)",
        conditions=[
            "Rarity Normal Magic Rare",
            "HasSearingExarchImplicit >= 1",
        ],
        style=LayerStyle(
            border="255 100 0", font=40, effect="Orange",
            icon="0 Orange Diamond",
        ),
        continue_=True,
        category_tag="eldritch_exarch",
    ))

    # Eldritch Eater of Worlds — HasEaterOfWorldsImplicit
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Eldritch Eater of Worlds implicit",
        conditions=[
            "Rarity Normal Magic Rare",
            "HasEaterOfWorldsImplicit >= 1",
        ],
        style=LayerStyle(
            border="100 200 255", font=40, effect="Blue",
            icon="0 Blue Diamond",
        ),
        continue_=True,
        category_tag="eldritch_eater",
    ))

    return "".join(blocks)


def layer_special_maps(mode: str = "ssf") -> str:
    """L8 Special Maps — NeverSink 패턴: Blighted/UberBlighted/Unique 맵.

    일반 Map은 layer_maps()에서 처리. 여기는 특수 맵만 강조.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # UberBlighted Map — 최고급 (Oil 전용 드롭)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Uber Blighted Map",
        conditions=['Class "Maps"', "UberBlightedMap True"],
        style=style_from_palette("divcard", "P1_KEYSTONE",
                                 effect="Purple", icon="0 Purple Star",
                                 sound="5 300"),
        continue_=False,
        category_tag="map_uber_blighted",
    ))

    # 일반 Blighted Map
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Blighted Map",
        conditions=['Class "Maps"', "BlightedMap True"],
        style=style_from_palette("divcard", "P2_CORE",
                                 effect="Purple", icon="0 Purple Hexagon"),
        continue_=False,
        category_tag="map_blighted",
    ))

    # Unique Map
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Unique Map",
        conditions=['Class "Maps"', "Rarity Unique"],
        style=style_from_palette("unique", "P1_KEYSTONE",
                                 effect="Red", icon="0 Red Star",
                                 sound="6 300"),
        continue_=False,
        category_tag="map_unique",
    ))

    return "".join(blocks)


def layer_jewels(mode: str = "ssf") -> str:
    """L8 Jewels — Abyss/Cluster/Generic 세분화 (NeverSink 패턴 + Aurora).

    Jewels는 항상 큰 가치 (특히 SSF) — 모든 jewel Show + Cluster/Abyss 강조.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Cluster Jewel — Large (가장 가치)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Cluster Jewel Large (ilvl>=75)",
        conditions=[
            'Class "Jewels"',
            'BaseType == "Large Cluster Jewel"',
            "ItemLevel >= 75",
        ],
        style=style_from_palette("jewel", "P1_KEYSTONE",
                                 effect="Pink", icon="0 Pink Star"),
        continue_=False,
        category_tag="jewel_cluster_large",
    ))

    # Cluster Jewel — Medium
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Cluster Jewel Medium (ilvl>=68)",
        conditions=[
            'Class "Jewels"',
            'BaseType == "Medium Cluster Jewel"',
            "ItemLevel >= 68",
        ],
        style=style_from_palette("jewel", "P2_CORE",
                                 effect="Pink", icon="1 Pink Star"),
        continue_=False,
        category_tag="jewel_cluster_medium",
    ))

    # Cluster Jewel — Small
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Cluster Jewel Small",
        conditions=[
            'Class "Jewels"',
            'BaseType == "Small Cluster Jewel"',
        ],
        style=style_from_palette("jewel", "P3_USEFUL",
                                 icon="1 Pink Star"),
        continue_=False,
        category_tag="jewel_cluster_small",
    ))

    # Abyss Jewel (특수 jewel — Eye 베이스)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Abyss Jewel (ilvl>=82)",
        conditions=[
            'Class "Abyss Jewels"',
            "ItemLevel >= 82",
        ],
        style=style_from_palette("jewel", "P1_KEYSTONE",
                                 effect="Pink", icon="0 Pink Hexagon"),
        continue_=False,
        category_tag="jewel_abyss_high",
    ))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Abyss Jewel (일반)",
        conditions=['Class "Abyss Jewels"'],
        style=style_from_palette("jewel", "P3_USEFUL",
                                 icon="2 Pink Hexagon"),
        continue_=False,
        category_tag="jewel_abyss_basic",
    ))

    # Generic Jewel (Cobalt/Crimson/Viridian/Prismatic/Timeless 등)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Generic Jewel (Cobalt/Crimson/Viridian 등)",
        conditions=['Class "Jewels"'],
        style=style_from_palette("jewel", "P3_USEFUL",
                                 icon="2 Pink Square"),
        continue_=True,  # Cluster 블록이 위에서 덮어쓸 수 있도록 (위 블록이 먼저 매칭)
        category_tag="jewel_generic",
    ))

    return "".join(blocks)


def layer_gold(mode: str = "ssf") -> str:
    """L8 Gold (Kingsmarch) — Wreckers 5단계 스택 패턴 + Aurora 'gold' 팔레트.

    임계: 5000(P1) / 2500(P2) / 1000(P3) / 100(P4) / 1(P5)
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []
    tiers = [
        (5000, "P1_KEYSTONE", "Yellow", "0 Yellow Raindrop", "gold_t1_5000"),
        (2500, "P2_CORE",     "Yellow", "1 Yellow Raindrop", "gold_t2_2500"),
        (1000, "P3_USEFUL",   None,     "1 Yellow Raindrop", "gold_t3_1000"),
        (100,  "P4_SUPPORT",  None,     "2 Yellow Raindrop", "gold_t4_100"),
        (1,    "P5_MINOR",    None,     "2 Yellow Raindrop", "gold_t5_1"),
    ]
    for stack, tier, effect, icon, tag in tiers:
        style = style_from_palette("gold", tier, icon=icon)
        if effect:
            style.effect = effect
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Gold {stack}+",
            conditions=['Class "Gold"', f"StackSize >= {stack}"],
            style=style,
            continue_=False,
            category_tag=tag,
        ))
    return "".join(blocks)


def layer_flasks_quality(mode: str = "ssf") -> str:
    """L8 Flasks Quality — Wreckers/NeverSink 패턴 (Q10/Q20/Q21).

    Class "Gem" "Flask" 동일하게 Quality 임계로 강조 (NeverSink는 Class==, Wreckers는 Class).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Q10+ — 약한 강조 (Gemcutter's Prism 후보)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "플라스크 Q10+",
        conditions=['Class "Flasks"', "Quality >= 10"],
        style=LayerStyle(font=37, border="200 100 200"),
        continue_=True,
        category_tag="flask_q10",
    ))
    # Q20+ — 폰트 확대
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "플라스크 Q20+",
        conditions=['Class "Flasks"', "Quality >= 20"],
        style=LayerStyle(font=40, border="255 0 200", effect="Cyan"),
        continue_=True,
        category_tag="flask_q20",
    ))
    # Q21+ — 최대
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "플라스크 Q21+ (완벽)",
        conditions=['Class "Flasks"', "Quality >= 21"],
        style=LayerStyle(font=45, bg="255 255 255 255", text="0 0 0",
                         effect="White", icon="0 White Cross", sound="12 200"),
        continue_=True,
        category_tag="flask_q21",
    ))
    # Utility Flask — Class 자체 강조 (다양한 효과)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Utility Flask 전체",
        conditions=['Class "Utility Flasks"', "Rarity Magic"],
        style=LayerStyle(font=36, border="100 200 200"),
        continue_=True,
        category_tag="utility_flask",
    ))
    return "".join(blocks)


# Heist handpicked 9 areas — 커뮤니티 검증 고수익 영역.
# 선정 기준: (1) Blueprint/Contract 수익성 상위 (Enchants/Divination/Trinkets 포함 확률),
# (2) Wreckers SSF 가이드 L937 영역. 출처: POE Wiki "Heist Contract" + Wreckers 필터 L937.
# GGPK 교차검증 (2026-04-19 F3b 감사): Blueprint: {area} / Contract: {area} 각 9종 → 18/18 존재.
_HEIST_HANDPICKED_AREAS: "list[str]" = [
    "Bunker", "Laboratory", "Mansion", "Prohibited Library",
    "Records Office", "Repository", "Smuggler's Den", "Tunnels", "Underbelly",
]


def layer_heist(mode: str = "ssf") -> str:
    """L8 Heist — Contract/Blueprint/Trinket Class 기반 (Wreckers 단순 패턴).

    Heist 아이템 전체 표시 (SSF 자급자족: Heist 보상 = 유니크/쿼리).
    Handpicked 9개 area는 고가 수익 영역 — 최상위 강조.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Blueprint handpicked (Cobalt L6643~6652 parity) — 9 고가 영역 먼저 매칭
    bp_quoted = " ".join(f'"Blueprint: {a}"' for a in _HEIST_HANDPICKED_AREAS)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Heist Blueprint handpicked ({len(_HEIST_HANDPICKED_AREAS)}개 고가 영역)",
        conditions=['Class == "Blueprints"', f"BaseType == {bp_quoted}"],
        style=LayerStyle(
            font=40, text="255 85 85", border="255 85 85",
            bg="40 0 30 255", effect="Yellow",
            icon="1 Yellow UpsideDownHouse", sound="5 300",
        ),
        continue_=False,
        category_tag="heist_blueprint_handpicked",
    ))

    # Contract handpicked (Cobalt L6614~6624 parity)
    ct_quoted = " ".join(f'"Contract: {a}"' for a in _HEIST_HANDPICKED_AREAS)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Heist Contract handpicked ({len(_HEIST_HANDPICKED_AREAS)}개 고가 영역)",
        conditions=['Class == "Contracts"', f"BaseType == {ct_quoted}"],
        style=LayerStyle(
            font=40, text="220 60 60", border="220 60 60",
            bg="20 20 0 255", effect="White",
            icon="2 White UpsideDownHouse", sound="4 300",
        ),
        continue_=False,
        category_tag="heist_contract_handpicked",
    ))

    # Blueprint (대규모 Heist 입장권 — 가장 가치)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Heist Blueprint (일반)",
        conditions=['Class "Blueprints"'],
        style=style_from_palette("base", "P1_KEYSTONE",
                                 effect="Cyan", icon="0 Cyan Diamond"),
        continue_=False,
        category_tag="heist_blueprint",
    ))
    # Contract (단일 Heist)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Heist Contract (일반)",
        conditions=['Class "Contracts"'],
        style=style_from_palette("base", "P3_USEFUL", icon="1 Cyan Diamond"),
        continue_=False,
        category_tag="heist_contract",
    ))
    # Heist Trinket (Rogue 강화)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Heist Trinket",
        conditions=['Class "Trinkets"'],
        style=style_from_palette("base", "P2_CORE",
                                 effect="Cyan", icon="0 Cyan Diamond"),
        continue_=False,
        category_tag="heist_trinket",
    ))

    # Rogue's Marker (도둑의 증표) — Heist 통화 (NeverSink 패턴: Salmon + Orange)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Rogue's Marker (도둑의 증표)",
        conditions=['Class "Stackable Currency"',
                    'BaseType == "Rogue\'s Marker"'],
        style=LayerStyle(font=40, text="255 178 135", border="255 178 135",
                         bg="60 30 20 240", effect="Orange",
                         icon="1 Orange Cross"),
        continue_=False,
        category_tag="heist_rogue_marker",
    ))

    # Wombgifts (화려한 결실 등) — **Breach** 특수 아이템 (5종)
    # Ancient/Growing/Lavish/Mysterious/Provisioning Wombgift
    # Breach 계열 Purple Aurora (Splinter와 일관성)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Wombgifts (Breach 특수, 화려한 결실 등)",
        conditions=['Class "Wombgifts"'],
        style=style_from_palette("fragment", "P1_KEYSTONE",
                                 effect="Purple", icon="0 Purple Star",
                                 sound="3 300"),
        continue_=False,
        category_tag="wombgifts",
    ))

    return "".join(blocks)


def layer_quest_items(mode: str = "ssf") -> str:
    """L8 Quest Items + Pantheon Souls — 놓치면 안 되는 퀘스트/lore 아이템.

    Maven's Writ, Watcher's Eye 등 핵심 퀘스트/엔드게임 아이템 + Sin/Tukohama
    Pantheon Souls (퀘스트 처음 1회 드롭).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    return make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Quest Items + Pantheon Souls",
        conditions=['Class == "Quest Items" "Pantheon Souls"'],
        style=LayerStyle(font=45, text="74 230 58", border="74 230 58",
                         bg="0 0 0 255", effect="Green",
                         icon="0 Green Star", sound="2 300"),
        continue_=False,
        category_tag="quest_items",
    )


# ---------------------------------------------------------------------------
# 스택 커런시 7티어 (Cobalt [[3905]]/[[3906]] — 6x/3x StackSize 기반)
# ---------------------------------------------------------------------------
#
# 원칙 6: Cobalt 7-tier 구조 이식 + Aurora currency 팔레트로 색 재해석.
# Cobalt 6단계 배경색 → Aurora P1~P6 텍스트 그라데이션.
# 첫 매칭 승리 (Continue=False) — 스택 아이템은 이 layer에서 최종 확정.

_STACK_TIER_DEFS: "list[tuple[str, str, str, str]]" = [
    # (tier_tag, palette_tier, icon, effect) — Cobalt 1~7 참조
    ("t1",  "P1_KEYSTONE", "0 Red Circle",     "Red"),
    ("t2",  "P2_CORE",     "0 Red Circle",     "Red"),
    ("t3",  "P3_USEFUL",   "1 Yellow Circle",  "Yellow"),
    ("t4",  "P4_SUPPORT",  "2 White Circle",   "White"),
    ("t5",  "P4_SUPPORT",  "2 White Circle",   "White"),
    ("t6",  "P5_MINOR",    "2 Grey Circle",    "Grey"),
    ("t7",  "P6_LOW",      "2 Grey Circle",    None),
]

# Cobalt [[3905]] 6x stack BaseType lists (extracted from cobaltStrict.txt L7290~7368)
_STACK_6X_BASES: "dict[str, list[str]]" = {
    "t1": ["Dextral Catalyst", "Sinistral Catalyst"],
    "t2": ["Ancient Orb", "Chaos Orb", "Fertile Catalyst", "Fracturing Shard",
           "Grand Eldritch Ember", "Orb of Annulment", "Prismatic Catalyst",
           "Stacked Deck"],
    "t3": ["Accelerating Catalyst", "Annulment Shard", "Burial Medallion",
           "Enkindling Orb", "Exalted Orb", "Exotic Coinage", "Gemcutter's Prism",
           "Grand Eldritch Ichor", "Greater Eldritch Ember", "Orb of Regret",
           "Orb of Scouring", "Scrap Metal", "Tempering Catalyst",
           "Unstable Catalyst", "Vaal Orb"],
    "t4": ["Abrasive Catalyst", "Blacksmith's Whetstone", "Blessed Orb",
           "Glassblower's Bauble", "Greater Eldritch Ichor", "Imbued Catalyst",
           "Instilling Orb", "Intrinsic Catalyst", "Noxious Catalyst",
           "Orb of Alchemy", "Orb of Alteration", "Orb of Chance",
           "Orb of Fusing", "Orb of Unmaking", "Regal Orb", "Turbulent Catalyst"],
    "t5": ["Armourer's Scrap", "Astragali", "Chaos Shard", "Chromatic Orb",
           "Exalted Shard", "Jeweller's Orb", "Lesser Eldritch Ember",
           "Lesser Eldritch Ichor"],
    "t6": ["Orb of Binding"],
    "t7": ["Alchemy Shard", "Regal Shard"],
}

# Cobalt [[3906]] 3x stack BaseType lists (L7375~7454) — 일부 tier 멤버십 다름
_STACK_3X_BASES: "dict[str, list[str]]" = {
    "t1": ["Dextral Catalyst"],
    "t2": ["Fertile Catalyst", "Fracturing Shard", "Grand Eldritch Ember",
           "Orb of Annulment", "Prismatic Catalyst", "Sinistral Catalyst"],
    "t3": ["Ancient Orb", "Burial Medallion", "Chaos Orb", "Enkindling Orb",
           "Exalted Orb", "Exotic Coinage", "Gemcutter's Prism",
           "Grand Eldritch Ichor", "Stacked Deck", "Unstable Catalyst"],
    "t4": ["Accelerating Catalyst", "Annulment Shard", "Blessed Orb",
           "Greater Eldritch Ember", "Greater Eldritch Ichor",
           "Intrinsic Catalyst", "Orb of Regret", "Orb of Scouring",
           "Orb of Unmaking", "Regal Orb", "Scrap Metal", "Tempering Catalyst",
           "Vaal Orb"],
    "t5": ["Abrasive Catalyst", "Astragali", "Blacksmith's Whetstone",
           "Chaos Shard", "Chromatic Orb", "Exalted Shard",
           "Glassblower's Bauble", "Imbued Catalyst", "Instilling Orb",
           "Jeweller's Orb", "Lesser Eldritch Ember", "Lesser Eldritch Ichor",
           "Noxious Catalyst", "Orb of Alchemy", "Orb of Alteration",
           "Orb of Chance", "Orb of Fusing", "Turbulent Catalyst"],
    "t6": ["Armourer's Scrap"],
    "t7": ["Orb of Binding"],
}


# ---------------------------------------------------------------------------
# Map Fragments 티어 (Cobalt [[3603]] Regular Fragment Tiering + [[3500]] 일부)
# ---------------------------------------------------------------------------
#
# Cobalt는 Map Fragments를 5단계 티어링 (T1~T5) + restex 안전망.
# 기존 `layer_maps`는 일반 맵만, `layer_scarabs`는 스카라브만 — 이 레이어는
# Invitation/Emblem/Crest/Fragment of X/Mortal X/Sacrifice 등 맵 디바이스 사용물 담당.

_FRAGMENT_TIERS: "dict[str, list[str]]" = {
    # T1: 최고가 (Unrelenting emblems, Echo, Syndicate Medallion 등)
    "t1": [
        "Echo of Loneliness", "Echo of Reverence", "Echo of Trauma",
        "Gift to the Goddess", "Incandescent Invitation", "Screaming Invitation",
        "Syndicate Medallion", "The Black Barya",
        "Unrelenting Timeless Eternal Emblem",
        "Unrelenting Timeless Karui Emblem",
        "Unrelenting Timeless Maraketh Emblem",
        "Unrelenting Timeless Templar Emblem",
        "Unrelenting Timeless Vaal Emblem",
    ],
    # T2: Fragment of X, Timeless Maraketh/Templar, Audience, 합성 관련
    "t2": [
        "An Audience With The King", "Awakening Fragment", "Blazing Fragment",
        "Cosmic Fragment", "Decaying Fragment", "Dedication to the Goddess",
        "Devouring Fragment", "Fragment of Knowledge", "Fragment of Shape",
        "Fragment of Terror", "Lonely Fragment", "Reality Fragment",
        "Reverent Fragment", "Sacred Blossom", "Synthesising Fragment",
        "Timeless Maraketh Emblem", "Timeless Templar Emblem",
        "Traumatic Fragment", "Tribute to the Goddess",
    ],
    # T4: Conqueror Crests, Mortal X, Simulacrum, Timeless(low), Maven's Writ
    "t4": [
        "Al-Hezmin's Crest", "Baran's Crest", "Blood-filled Vessel",
        "Drox's Crest", "Fragment of Constriction", "Fragment of Emptiness",
        "Fragment of Enslavement", "Fragment of Eradication",
        "Fragment of Purification", "Fragment of the Chimera",
        "Fragment of the Hydra", "Fragment of the Minotaur",
        "Fragment of the Phoenix", "Hivebrain Gland",
        "Mortal Grief", "Mortal Hope", "Mortal Ignorance", "Mortal Rage",
        "Offering to the Goddess", "Polaric Invitation", "Simulacrum",
        "The Maven's Writ",
        "Timeless Eternal Emblem", "Timeless Karui Emblem", "Timeless Vaal Emblem",
        "Veritania's Crest", "Writhing Invitation",
    ],
    # T5: Sacrifice/Divine Vessel (레벨링/초기 맵용)
    "t5": [
        "Divine Vessel", "Sacrifice at Dawn", "Sacrifice at Dusk",
        "Sacrifice at Midnight", "Sacrifice at Noon",
    ],
}


# ---------------------------------------------------------------------------
# 엔드게임 리그 컨텐츠 (Cobalt [[3500]] Misc Map Items + Expedition/Sanctum)
# ---------------------------------------------------------------------------
#
# Cobalt 여러 섹션에 흩어진 리그 엔트리 아이템 단일 레이어 집합.
# 전부 Continue=False 최종 Show — 리그 컨텐츠 진입권은 놓치면 안 되므로.

_RELIC_KEYS: "list[str]" = [
    "Ancient Reliquary Key", "Archive Reliquary Key", "Cosmic Reliquary Key",
    "Decaying Reliquary Key", "Forgotten Reliquary Key", "Lonely Reliquary Key",
    "Oubliette Reliquary Key", "Reverent Reliquary Key", "Shiny Reliquary Key",
    "Timeworn Reliquary Key", "Traumatic Reliquary Key", "Vaal Reliquary Key",
    "Visceral Reliquary Key", "Voidborn Reliquary Key",
]


def layer_endgame_content(mode: str = "ssf") -> str:
    """L8 Endgame Content — 리그 컨텐츠 엔트리 아이템 (Cobalt [[3500]]+).

    Expedition Logbook / Sanctum Research / Relic & Vault Keys /
    Chronicle of Atzoatl / Inscribed Ultimatum. 놓치면 안 되는 고가 리그 입장권.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # 1. Expedition Logbook (Cobalt L6592)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Expedition Logbook (리그 엔트리)",
        conditions=['BaseType == "Expedition Logbook"'],
        style=style_from_palette("unique", "P1_KEYSTONE",
                                 effect="Yellow",
                                 icon="0 Yellow UpsideDownHouse",
                                 sound="5 300"),
        continue_=False,
        category_tag="expedition_logbook",
    ))

    # 2. Sanctum Research — ilvl 83+ 최상 (Cobalt L6664)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Sanctum Research ilvl>=83 (최상)",
        conditions=['Class == "Sanctum Research"', "ItemLevel >= 83"],
        style=style_from_palette("unique", "P1_KEYSTONE",
                                 effect="Yellow",
                                 icon="0 Yellow UpsideDownHouse",
                                 sound="5 300"),
        continue_=False,
        category_tag="sanctum_ilvl83",
    ))

    # 3. Sanctum Research — any (Cobalt L6675)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Sanctum Research (일반)",
        conditions=['Class == "Sanctum Research"'],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Yellow",
                                 icon="1 Yellow UpsideDownHouse",
                                 sound="5 300"),
        continue_=False,
        category_tag="sanctum_any",
    ))

    # 4. Relic Keys (Cobalt L6690) — 14 bases, Mirror-tier 입장권
    relic_quoted = " ".join(f'"{k}"' for k in _RELIC_KEYS)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Relic Keys ({len(_RELIC_KEYS)}종, Uber 보스 입장권)",
        conditions=[f"BaseType == {relic_quoted}"],
        style=LayerStyle(
            font=45, text="255 0 0", border="255 0 0",
            bg="255 255 255 255",  # 흰 BG (Cobalt T1)
            sound="6 300", effect="Red",
            icon="0 Red Star",
        ),
        continue_=False,
        category_tag="relic_keys",
    ))

    # 5. Vault Keys class (Cobalt L6700) — 안전망
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Vault Keys class (미래 Key 안전망)",
        conditions=['Class == "Vault Keys"'],
        style=LayerStyle(
            font=45, text="255 0 0", border="255 0 0",
            bg="255 255 255 255",
            sound="6 300", effect="Red",
            icon="0 Red Star",
        ),
        continue_=False,
        category_tag="vault_keys",
    ))

    # 6. Chronicle of Atzoatl (Cobalt L6710) — Incursion 최종
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Chronicle of Atzoatl (Incursion 보스)",
        conditions=['BaseType == "Chronicle of Atzoatl"'],
        style=style_from_palette("currency", "P2_CORE",
                                 effect="Red",
                                 icon="0 Red Hexagon",
                                 sound="1 300"),
        continue_=False,
        category_tag="chronicle",
    ))

    # 7. Inscribed Ultimatum (Cobalt 8.19.x L6720) — Ultimatum 컨텐츠 (3.14 도입 영구 메커닉).
    # 출처: GGPK BaseItemTypes.json 확인 2026-04-19 (F3a 감사), Cobalt REGULAR 원본 라인 보존.
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Inscribed Ultimatum (Ultimatum 컨텐츠)",
        conditions=['BaseType == "Inscribed Ultimatum"'],
        style=style_from_palette("currency", "P2_CORE",
                                 effect="Red",
                                 icon="0 Red Hexagon",
                                 sound="1 300"),
        continue_=False,
        category_tag="ultimatum",
    ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# P0 미매칭 카테고리 (2026-04-15 audit 발견): Watchstone / Incubator /
# Forbidden Tome / Sanctum Research floors / Memory Lines / Metamorph DNA
# ---------------------------------------------------------------------------

_WATCHSTONE_HIGH = (  # Titanium/Platinum 지역 전용 (8 지역 × 2 = 16)
    "Titanium Glennach Cairns Watchstone", "Titanium Haewark Hamlet Watchstone",
    "Titanium Lex Ejoris Watchstone", "Titanium Lex Proxima Watchstone",
    "Titanium Lira Arthain Watchstone", "Titanium New Vastir Watchstone",
    "Titanium Tirn's End Watchstone", "Titanium Valdo's Rest Watchstone",
    "Platinum Glennach Cairns Watchstone", "Platinum Haewark Hamlet Watchstone",
    "Platinum Lex Ejoris Watchstone", "Platinum Lex Proxima Watchstone",
    "Platinum Lira Arthain Watchstone", "Platinum New Vastir Watchstone",
    "Platinum Tirn's End Watchstone", "Platinum Valdo's Rest Watchstone",
)
_WATCHSTONE_TOP = (  # Chromium — 8 지역
    "Chromium Glennach Cairns Watchstone", "Chromium Haewark Hamlet Watchstone",
    "Chromium Lex Ejoris Watchstone", "Chromium Lex Proxima Watchstone",
    "Chromium Lira Arthain Watchstone", "Chromium New Vastir Watchstone",
    "Chromium Tirn's End Watchstone", "Chromium Valdo's Rest Watchstone",
)
_WATCHSTONE_LOW = (  # legacy generic (Cobalt/Crimson/Ivory/Viridian/Golden)
    "Ivory Watchstone", "Cobalt Watchstone", "Crimson Watchstone",
    "Viridian Watchstone", "Golden Watchstone",
)

_INCUBATOR_ALL = (
    "Abyssal Incubator", "Blighted Incubator", "Cartographer's Incubator",
    "Celestial Armoursmith's Incubator", "Celestial Blacksmith's Incubator",
    "Celestial Jeweller's Incubator", "Challenging Incubator",
    "Diviner's Incubator", "Eldritch Incubator", "Enchanted Incubator",
    "Feral Incubator", "Fine Incubator", "Foreboding Incubator",
    "Fossilised Incubator", "Fragmented Incubator", "Gemcutter's Incubator",
    "Geomancer's Incubator", "Honoured Incubator", "Infused Incubator",
    "Kalguuran Incubator", "Maddening Incubator", "Miraged Incubator",
    "Mysterious Incubator", "Obscured Incubator", "Ornate Incubator",
    "Otherworldly Incubator", "Primal Incubator", "Sacred Incubator",
    "Singular Incubator", "Skittering Incubator", "Thaumaturge's Incubator",
    "Time-Lost Incubator", "Whispering Incubator",
)

_SANCTUM_FLOORS = (
    "Sanctum Archives Research", "Sanctum Cathedral Research",
    "Sanctum Necropolis Research", "Sanctum Vaults Research",
)

_MEMORY_LINES = ("Kirac's Memory", "Alva's Memory", "Niko's Memory", "Einhar's Memory")

_METAMORPH_ORGANS = (
    "Metamorph Brain", "Metamorph Eye", "Metamorph Heart",
    "Metamorph Liver", "Metamorph Lung",
)


def layer_atlas_and_memory(mode: str = "ssf") -> str:
    """P0 미매칭 카테고리 — Watchstone/Incubator/Forbidden Tome/Sanctum Floor/Memory/Metamorph.

    2026-04-15 filter_coverage_audit.py 발견. 이전 β 레이어는 이 카테고리 전혀 터치 안 함 →
    Normal 기본 스타일로 폴스루. 각 카테고리별 전용 Show 블록 추가.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # Forbidden Tome — Sanctum 최상위 진입 (Uber-tier, T0급)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Forbidden Tome (Sanctum Uber 진입)",
        conditions=['BaseType == "Forbidden Tome"'],
        style=LayerStyle(
            font=45, text="255 0 0", border="255 0 0",
            bg="255 255 255 255", sound="6 300", effect="Red",
            icon="0 Red Star",
        ),
        continue_=False,
        category_tag="forbidden_tome",
    ))

    # Watchstone T0 — Chromium (8 지역, 최상위)
    quoted = " ".join(f'"{n}"' for n in _WATCHSTONE_TOP)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Watchstone T0 Chromium ({len(_WATCHSTONE_TOP)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P1_KEYSTONE",
                                 effect="Purple",
                                 icon="0 Purple Star",
                                 sound="4 300"),
        continue_=False,
        category_tag="watchstone_chromium",
    ))

    # Watchstone T1 — Titanium/Platinum (16종, 지역 전용)
    quoted = " ".join(f'"{n}"' for n in _WATCHSTONE_HIGH)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Watchstone T1 Titanium/Platinum ({len(_WATCHSTONE_HIGH)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Purple",
                                 icon="1 Purple Star",
                                 sound="3 300"),
        continue_=False,
        category_tag="watchstone_high",
    ))

    # Watchstone T2 — 일반 (5종 legacy)
    quoted = " ".join(f'"{n}"' for n in _WATCHSTONE_LOW)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Watchstone T2 일반 ({len(_WATCHSTONE_LOW)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P3_USEFUL",
                                 effect="Purple",
                                 icon="2 Purple Star"),
        continue_=False,
        category_tag="watchstone_low",
    ))

    # Sanctum Floor Research (4종) — Forbidden Tome 없이도 일반 Sanctum 진입
    quoted = " ".join(f'"{n}"' for n in _SANCTUM_FLOORS)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Sanctum Floor Research ({len(_SANCTUM_FLOORS)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Yellow",
                                 icon="1 Yellow UpsideDownHouse",
                                 sound="3 300"),
        continue_=False,
        category_tag="sanctum_floor_research",
    ))

    # Memory Lines (4종) — league 재실행 티켓 (Kirac/Alva/Niko/Einhar)
    quoted = " ".join(f'"{n}"' for n in _MEMORY_LINES)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Memory Lines ({len(_MEMORY_LINES)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Green",
                                 icon="0 Green Hexagon",
                                 sound="2 300"),
        continue_=False,
        category_tag="memory_lines",
    ))

    # Incubator (33종) — XP 누적 시 아이템 드롭
    quoted = " ".join(f'"{n}"' for n in _INCUBATOR_ALL)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Incubator ({len(_INCUBATOR_ALL)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("currency", "P3_USEFUL",
                                 effect="Orange",
                                 icon="2 Orange Kite"),
        continue_=False,
        category_tag="incubator",
    ))

    # Metamorph DNA (5 장기) — 5종 모아 메타몰프 소환
    quoted = " ".join(f'"{n}"' for n in _METAMORPH_ORGANS)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Metamorph Organs ({len(_METAMORPH_ORGANS)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P3_USEFUL",
                                 effect="Cyan",
                                 icon="1 Cyan Raindrop"),
        continue_=False,
        category_tag="metamorph_organs",
    ))

    # --- P1 (2026-04-15 audit 후속) ---

    # Maven's Invitation T0 — The Feared (4-Boss 울트라 Uber, Mageblood 챈스)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Maven's Invitation T0 (The Feared, 4-Boss)",
        conditions=['BaseType == "Maven\'s Invitation: The Feared"'],
        style=LayerStyle(
            font=45, text="255 0 0", border="255 0 0",
            bg="255 255 255 255", sound="6 300", effect="Red",
            icon="0 Red Star",
        ),
        continue_=False,
        category_tag="maven_invitation_feared",
    ))

    # Maven's Invitation T1 — Elderslayers / Forgotten / Twisted / Formed / Hidden / Atlas / Remembered
    _MAVEN_T1 = (
        "Maven's Invitation: The Elderslayers",
        "Maven's Invitation: The Forgotten",
        "Maven's Invitation: The Twisted",
        "Maven's Invitation: The Formed",
        "Maven's Invitation: The Hidden",
        "Maven's Invitation: The Atlas",
        "Maven's Invitation: The Remembered",
    )
    quoted = " ".join(f'"{n}"' for n in _MAVEN_T1)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Maven's Invitation T1 boss ({len(_MAVEN_T1)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P1_KEYSTONE",
                                 effect="Yellow",
                                 icon="0 Yellow Star",
                                 sound="4 300"),
        continue_=False,
        category_tag="maven_invitation_boss",
    ))

    # Maven's Invitation T2 — 지역 전용 (8 지역, 3-Boss)
    _MAVEN_T2 = (
        "Maven's Invitation: Glennach Cairns",
        "Maven's Invitation: Haewark Hamlet",
        "Maven's Invitation: Lex Ejoris",
        "Maven's Invitation: Lex Proxima",
        "Maven's Invitation: Lira Arthain",
        "Maven's Invitation: New Vastir",
        "Maven's Invitation: Tirn's End",
        "Maven's Invitation: Valdo's Rest",
    )
    quoted = " ".join(f'"{n}"' for n in _MAVEN_T2)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Maven's Invitation T2 region ({len(_MAVEN_T2)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Yellow",
                                 icon="1 Yellow Star",
                                 sound="3 300"),
        continue_=False,
        category_tag="maven_invitation_region",
    ))

    # 고가 Stackable Currency — audit 발견 26종 (T1/T2 구분)
    _STACKABLE_T1 = (  # 최상위 Mirror-tier 또는 반복불가
        "Eternal Orb", "Imprint",
        "Veiled Exalted Orb", "Veiled Chaos Orb",
        "Lycia's Invocation of Eternal Youth",
    )
    quoted = " ".join(f'"{n}"' for n in _STACKABLE_T1)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Stackable Currency T1 legacy/Veiled ({len(_STACKABLE_T1)}종)",
        conditions=[f'Class "Stackable Currency"', f"BaseType == {quoted}"],
        style=LayerStyle(
            font=45, text="255 0 0", border="255 0 0",
            bg="255 255 255 255", sound="6 300", effect="Red",
            icon="0 Red Star",
        ),
        continue_=False,
        category_tag="stackable_t1_legacy",
    ))

    _STACKABLE_T2 = (  # T2 고가 (Maven Chisel/Awakened Sextant/Prime lens 등)
        "Maven's Chisel of Avarice", "Maven's Chisel of Divination",
        "Maven's Chisel of Procurement", "Maven's Chisel of Proliferation",
        "Maven's Chisel of Scarabs",
        "Awakened Sextant", "Prime Sextant",
        "Prime Regrading Lens",
        "Albino Rhoa Feather",
        "Tailoring Orb", "Tempering Orb",
        "Imprinted Bestiary Orb",
        "Veiled Scarab",
        "Harbinger's Shard", "Horizon Shard",
    )
    quoted = " ".join(f'"{n}"' for n in _STACKABLE_T2)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Stackable Currency T2 고가 ({len(_STACKABLE_T2)}종)",
        conditions=[f'Class "Stackable Currency"', f"BaseType == {quoted}"],
        style=style_from_palette("currency", "P1_KEYSTONE",
                                 effect="Red",
                                 icon="0 Red Cross",
                                 sound="3 300"),
        continue_=False,
        category_tag="stackable_t2_high",
    ))

    # Exceptional Artifacts/Ember/Ichor — Expedition 최고 티어.
    # 출처: GGPK BaseItemTypes.json 전수 확인 2026-04-19 — 6/6 존재 (F2 감사).
    # Expedition (3.16) 이후 변동 없음. Wiki: "Exceptional Currency" 카테고리.
    _EXCEPTIONAL = (
        "Exceptional Black Scythe Artifact", "Exceptional Broken Circle Artifact",
        "Exceptional Eldritch Ember", "Exceptional Eldritch Ichor",
        "Exceptional Order Artifact", "Exceptional Sun Artifact",
    )
    quoted = " ".join(f'"{n}"' for n in _EXCEPTIONAL)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Exceptional (Expedition T0, {len(_EXCEPTIONAL)}종)",
        conditions=[f'Class "Stackable Currency"', f"BaseType == {quoted}"],
        style=style_from_palette("currency", "P1_KEYSTONE",
                                 effect="Pink",
                                 icon="0 Pink Star",
                                 sound="3 300"),
        continue_=False,
        category_tag="exceptional_artifacts",
    ))

    # Unique Fragments — Harbinger shards (5 shards per unique) + 특수 (Primordial, Vaal Aspect).
    # 출처: GGPK BaseItemTypes.json 전수 확인 2026-04-19 — 8/8 존재 (F2 감사).
    # Harbinger (3.1) 이후 영구 메커닉. Wiki: "Harbinger" piece 페이지.
    _UNIQUE_FRAGMENTS = (
        "Archon Kite Shield Piece", "Blunt Arrow Quiver Piece",
        "Callous Mask Piece", "Cloth Belt Piece",
        "Imperial Staff Piece", "Legion Sword Piece",
        "Primordial Fragment", "Vaal Aspect",
    )
    quoted = " ".join(f'"{n}"' for n in _UNIQUE_FRAGMENTS)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Unique Fragments (Harbinger pieces, {len(_UNIQUE_FRAGMENTS)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Orange",
                                 icon="1 Orange Triangle",
                                 sound="2 250"),
        continue_=False,
        category_tag="harbinger_fragments",
    ))

    # Heist Objective — Heist 컨트랙트 타겟 아이템 (47종). 컨트랙트 실행 중 자동 드롭.
    # 출처: GGPK BaseItemTypes.json 전수 검증 2026-04-19 (F3b 감사) — 47/47 존재.
    # Heist 3.12 (2020-09) 도입, 이후 BaseType 리스트 변동 없음 (core 메커닉).
    _HEIST_OBJECTIVES = (
        "Abberathine Horns", "Admiral Proclar's Pipe", "Alchemical Chalice",
        "Ancient Seal", "Blood of Innocence", "Box of Tripyxis",
        "Bust of Emperor Caspiro", "Celestial Stone", "Ceremonial Goblet",
        "Crest of Ezomyr", "Crested Golden Idol", "Dekhara's Resolve",
        "Enigmatic Assembly A4", "Enigmatic Assembly B2",
        "Enigmatic Assembly C5", "Enigmatic Assembly D1",
        "Essence Burner", "Ez Myrae Tome", "Flask of Welakath",
        "Forbidden Lamp", "Golden Ceremonial Mask", "Golden Grotesque",
        "Golden Hetzapal Idol", "Golden Matatl Idol", "Golden Napuatzi Idol",
        "Golden Prayer Idol", "Golden Sacrificial Glyph", "Golden Slave Idol",
        "Golden Xoplotli Idol", "Hand of Arimor", "Heart Coil",
        "Impossible Crystal", "Incense of Keth", "Living Ice",
        "Mirror of Teklatipitzi", "Ogham Candelabra", "Orbala's Fifth Adventure",
        "Seal of Lunaris", "Seal of Solaris", "Staff of the First Sin Eater",
        "Sword of the Inverse Relic", "The Goddess of Water", "The Golden Ibis",
        "The Sea Pearl Heirloom", "Tusked Hominid Skull",
        "Urn of Farud", "Urn of the Original Ashes",
    )
    quoted = " ".join(f'"{n}"' for n in _HEIST_OBJECTIVES)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Heist Objective ({len(_HEIST_OBJECTIVES)}종, 컨트랙트 타겟)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("currency", "P3_USEFUL",
                                 effect="Yellow",
                                 icon="2 Yellow Triangle"),
        continue_=False,
        category_tag="heist_objective",
    ))

    # Wombgift — Chayula 리그 (Ancient/Growing/Lavish/Mysterious/Provisioning)
    _WOMBGIFT = (
        "Ancient Wombgift", "Growing Wombgift", "Lavish Wombgift",
        "Mysterious Wombgift", "Provisioning Wombgift",
    )
    quoted = " ".join(f'"{n}"' for n in _WOMBGIFT)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        f"Wombgift (Chayula 리그, {len(_WOMBGIFT)}종)",
        conditions=[f"BaseType == {quoted}"],
        style=style_from_palette("unique", "P2_CORE",
                                 effect="Purple",
                                 icon="1 Purple Pentagon",
                                 sound="2 250"),
        continue_=False,
        category_tag="wombgift",
    ))

    return "".join(blocks)


def layer_map_fragments(mode: str = "ssf") -> str:
    """L8 Map Fragments — Cobalt [[3603]] 5-tier + RestEx.

    Invitation/Emblem/Crest/Fragment of X/Mortal/Sacrifice/Divine Vessel 등
    Map Fragments + Misc Map Items 클래스. Aurora fragment 팔레트 P1~P5.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # 티어별 매핑 (Cobalt 배경색 → Aurora fragment 팔레트 + Hexagon 아이콘)
    _FRAG_TIER_STYLES: "list[tuple[str, str, str, str]]" = [
        ("t1", "P1_KEYSTONE", "0 Pink Hexagon", "Pink"),
        ("t2", "P2_CORE",     "0 Pink Hexagon", "Pink"),
        ("t4", "P4_SUPPORT",  "1 Pink Hexagon", None),
        ("t5", "P5_MINOR",    "2 Pink Hexagon", None),
    ]

    for tier_tag, palette_tier, icon, effect in _FRAG_TIER_STYLES:
        bases = _FRAGMENT_TIERS.get(tier_tag, [])
        if not bases:
            continue
        quoted = " ".join(f'"{b}"' for b in bases)
        style = style_from_palette("fragment", palette_tier, icon=icon)
        if effect:
            style.effect = effect
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"맵 프래그먼트 {tier_tag.upper()} ({len(bases)}종)",
            conditions=[
                'Class == "Map Fragments" "Misc Map Items"',
                f"BaseType == {quoted}",
            ],
            style=style,
            continue_=False,
            category_tag=f"fragment_{tier_tag}",
        ))

    # RestEx — 티어 외 프래그먼트 (신규 리그 등) 핑크 안전망
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "맵 프래그먼트 RestEx (미분류 안전망)",
        conditions=['Class == "Map Fragments" "Misc Map Items"'],
        style=LayerStyle(
            font=45, text="255 0 255", border="255 0 255",
            bg="100 0 100 255", effect="Pink",
            icon="0 Pink Circle", sound="3 300",
        ),
        continue_=False,
        category_tag="fragment_restex",
    ))

    return "".join(blocks)


def layer_stacked_currency(mode: str = "ssf") -> str:
    """L8 Stacked Currency — Cobalt [[3905]]/[[3906]] 7-tier 스택 티어링.

    StackSize >= 6 우선 블록 (인벤 효율 최대) + StackSize >= 3 보조 블록.
    6x 블록이 먼저 와서 더 구체적인 매치 우선. Continue=False로 최종 확정.
    Aurora currency 팔레트 P1~P6 적용 (Cobalt 6단계 배경색 대체).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    def _emit(stack: int, tier_tag: str, palette_tier: str,
              icon: str, effect: Optional[str], bases: list[str]):
        if not bases:
            return
        quoted = " ".join(f'"{b}"' for b in bases)
        style = style_from_palette("currency", palette_tier, icon=icon)
        if effect:
            style.effect = effect
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"스택 {stack}x {tier_tag.upper()} ({len(bases)}종)",
            conditions=[
                f"StackSize >= {stack}",
                'Class == "Stackable Currency"',
                f"BaseType == {quoted}",
            ],
            style=style,
            continue_=False,
            category_tag=f"stack_{stack}x_{tier_tag}",
        ))

    # 6x 블록 먼저 (StackSize 6 이상은 3보다 더 구체적 — 첫 매칭 승리)
    for tier_tag, palette_tier, icon, effect in _STACK_TIER_DEFS:
        _emit(6, tier_tag, palette_tier, icon, effect,
              _STACK_6X_BASES.get(tier_tag, []))
    # 3x 블록 (6x 매칭 실패 시 fallback)
    for tier_tag, palette_tier, icon, effect in _STACK_TIER_DEFS:
        _emit(3, tier_tag, palette_tier, icon, effect,
              _STACK_3X_BASES.get(tier_tag, []))

    return "".join(blocks)


def layer_lifeforce(mode: str = "ssf", items: Optional[GGPKItems] = None) -> str:
    """L8 Lifeforce — Harvest 결정화 생명력. NeverSink/Cobalt 5단계 임계.

    스택 임계: 4000(P1) / 500(P2) / 250(P3) / 45(P4) / 20(P5)
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")
    d = items if items is not None else load_ggpk_items()
    if not d.lifeforce:
        return ""
    quoted = " ".join(f'"{x}"' for x in d.lifeforce)

    blocks: list[str] = []
    # NeverSink 5단계: 4000/500/250/45/20
    # 팔레트 "gem" (Chartreuse 초록) — Harvest 정체성 일치
    tier_specs = [
        (4000, "P1_KEYSTONE", "Green",  "0 Green Hexagon", "lifeforce_t1_4000"),
        (500,  "P2_CORE",     "Green",  "0 Green Hexagon", "lifeforce_t2_500"),
        (250,  "P3_USEFUL",   "Green",  "1 Green Hexagon", "lifeforce_t3_250"),
        (45,   "P4_SUPPORT",  None,     "1 Green Hexagon", "lifeforce_t4_45"),
        (20,   "P5_MINOR",    None,     "2 Green Hexagon", "lifeforce_t5_20"),
    ]
    for stack, tier, effect, icon, tag in tier_specs:
        style = style_from_palette("gem", tier, icon=icon)
        if effect:
            style.effect = effect
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Lifeforce {stack}+ ({len(d.lifeforce)}종)",
            conditions=[f"BaseType == {quoted}", f"StackSize >= {stack}"],
            style=style,
            continue_=False,
            category_tag=tag,
        ))
    return "".join(blocks)


def layer_splinters(mode: str = "ssf", items: Optional[GGPKItems] = None) -> str:
    """L8 Splinters — NeverSink/Cobalt 패턴 (Breach/Legion 5단계, Simulacrum 단일).

    Breach/Legion 임계: 80(P1) / 60(P2) / 20(P3) / 5(P4) / 1(P5)
    Simulacrum: 150(P1) / 1(P5) — 단일 아이템이라 2단계
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")
    d = items if items is not None else load_ggpk_items()
    blocks: list[str] = []

    BREACH_LEGION_TIERS = [
        (80, "P1_KEYSTONE", "Purple", "0 Purple Hexagon"),
        (60, "P2_CORE",     "Purple", "0 Purple Hexagon"),
        (20, "P3_USEFUL",   None,     "1 Purple Hexagon"),
        (5,  "P4_SUPPORT",  None,     "2 Purple Hexagon"),
        (1,  "P5_MINOR",    None,     "2 Purple Hexagon"),
    ]
    SIM_TIERS = [
        (150, "P1_KEYSTONE", "Purple", "0 Purple Hexagon"),
        (1,   "P5_MINOR",    None,     "2 Purple Hexagon"),
    ]

    def _add(name_tag: str, names: tuple[str, ...], tier_specs: list,
             palette_cat: str):
        if not names:
            return
        quoted = " ".join(f'"{x}"' for x in names)
        for stack, tier, effect, icon in tier_specs:
            style = style_from_palette(palette_cat, tier, icon=icon)
            if effect:
                style.effect = effect
            blocks.append(make_layer_block(
                LAYER_CATEGORY_SHOW,
                f"{name_tag} {stack}+ ({len(names)}종)",
                conditions=[f"BaseType == {quoted}", f"StackSize >= {stack}"],
                style=style,
                continue_=False,
                category_tag=f"splinter_{name_tag.lower()}_s{stack}",
            ))

    _add("Breach", d.splinter_breach, BREACH_LEGION_TIERS, "fragment")
    _add("Legion", d.splinter_legion, BREACH_LEGION_TIERS, "fragment")
    _add("Simulacrum", d.splinter_simulacrum, SIM_TIERS, "fragment")
    return "".join(blocks)


_UNIQUE_TIERS_CACHE: Optional[dict] = None


def _load_unique_tiers() -> dict:
    """data/unique_tiers.json 로드 + Cobalt first-match 시맨틱 이식을 위한 디듀플리케이션.

    **중요**: 원본 Cobalt Strict는 first-match 엔진 ([4702] T1/T2 Show+no-Continue로 잠기면
    [4704]/[4707] 중복 트리거 안 됨). 우리 Continue=True 캐스케이드는 후순위 매치가
    덮어씀 → 상위 티어 base가 하위 티어 블록에 중복 존재하면 하위로 다운그레이드.

    해결: 우선순위 순회하며 상위 티어 확정 후 하위 티어에서 제거.
    우선순위: t1 > multi_high > t2 > t3 > t4 > t5
    """
    global _UNIQUE_TIERS_CACHE
    if _UNIQUE_TIERS_CACHE is not None:
        return _UNIQUE_TIERS_CACHE
    path = _DATA_DIR / "unique_tiers.json"
    if not path.exists():
        _UNIQUE_TIERS_CACHE = {}
        return _UNIQUE_TIERS_CACHE
    raw = json.loads(path.read_text(encoding="utf-8")).get("tiers", {})

    # 디듀플리케이션: 상위 티어 우선
    priority = ["t1", "multi_high", "t2", "t3", "t4", "t5"]
    seen: set[str] = set()
    dedup: dict[str, list[str]] = {}
    for key in priority:
        items = raw.get(key, [])
        dedup[key] = [b for b in items if b not in seen]
        seen.update(dedup[key])
    # 원본의 기타 키(있다면 — 예: 미래 확장)는 그대로 보존
    for key, val in raw.items():
        if key not in dedup:
            dedup[key] = val
    _UNIQUE_TIERS_CACHE = dedup
    return _UNIQUE_TIERS_CACHE


def layer_uniques(mode: str = "ssf") -> str:
    """L8 Uniques — NeverSink [[4700]] 구조 + Aurora Glow 스타일.

    keystone 예외(6-Link 유니크 전체, abyss socketed 등) + 티어별 BaseType 리스트.
    `data/unique_tiers.json`에서 티어 로드 (NeverSink 추출).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    tiers = _load_unique_tiers()
    blocks: list[str] = []

    # 0. Generic 유니크 fallback **먼저** — 후속 티어 블록이 덮어쓸 수 있음
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "유니크 일반 (T1~T3 외 fallback)",
        conditions=["Rarity Unique"],
        style=style_from_palette("unique", "P4_SUPPORT",
                                 icon="2 Orange Star"),
        continue_=True,
        category_tag="unique_generic",
    ))

    # NeverSink/Cobalt 표준 패턴 (6-source 검증):
    # - 표준 키스톤 (Tabula/Squire/Triadgrip): text=흰 / border=흰 / bg=Tangerine 175 96 37
    # - 반전 키스톤 (Abyss/Replica/Foulborn): text=Tangerine / border=Tangerine / bg=흰
    _STANDARD_KEYSTONE = LayerStyle(
        font=45, text="255 255 255", border="255 255 255",
        bg="175 96 37 255", effect="Red",
        icon="0 Red Star", sound="1 300",
    )

    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "유니크 6-Link 일반",
        conditions=["Rarity Unique", "LinkedSockets 6"],
        style=_STANDARD_KEYSTONE,
        continue_=True,
        category_tag="unique_6link",
    ))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "유니크 Squire 3x White (Elegant Round Shield)",
        conditions=["Rarity Unique",
                    "Sockets >= 3WWW",
                    'BaseType == "Elegant Round Shield"'],
        style=_STANDARD_KEYSTONE,
        continue_=True,
        category_tag="unique_squire",
    ))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "유니크 Tabula 6-Link (Simple Robe)",
        conditions=["Rarity Unique",
                    "LinkedSockets 6",
                    'BaseType == "Simple Robe"'],
        style=_STANDARD_KEYSTONE,
        continue_=True,
        category_tag="unique_tabula",
    ))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "유니크 Triad Grip 4x White (Mesh Gloves)",
        conditions=["Rarity Unique",
                    "Sockets >= 4WWWW",
                    'BaseType == "Mesh Gloves"'],
        style=_STANDARD_KEYSTONE,
        continue_=True,
        category_tag="unique_triadgrip",
    ))
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "유니크 Abyss Socket 4x (Bone Circlet)",
        conditions=["Rarity Unique",
                    "Sockets >= AAAA",
                    'BaseType == "Bone Circlet"'],
        # 반전 패턴
        style=LayerStyle(font=45, text="175 96 37", border="175 96 37",
                         bg="255 255 255 255", effect="Red",
                         icon="0 Red Star", sound="1 300"),
        continue_=True,
        category_tag="unique_abyss4",
    ))

    # 2. T1 유니크 베이스 (NeverSink 추출)
    if "t1" in tiers and tiers["t1"]:
        quoted = " ".join(f'"{b}"' for b in tiers["t1"])
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"유니크 T1 ({len(tiers['t1'])}종)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=style_from_palette("unique", "P1_KEYSTONE",
                                     effect="Red", icon="0 Red Star"),
            continue_=True,
            category_tag="unique_t1",
        ))

    # 3. T2 유니크
    if "t2" in tiers and tiers["t2"]:
        quoted = " ".join(f'"{b}"' for b in tiers["t2"])
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"유니크 T2 ({len(tiers['t2'])}종)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=style_from_palette("unique", "P2_CORE",
                                     effect="Red", icon="1 Red Star"),
            continue_=True,
            category_tag="unique_t2",
        ))

    # 4. T3 유니크
    if "t3" in tiers and tiers["t3"]:
        quoted = " ".join(f'"{b}"' for b in tiers["t3"])
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"유니크 T3 ({len(tiers['t3'])}종)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=style_from_palette("unique", "P3_USEFUL",
                                     icon="2 Orange Star"),
            continue_=True,
            category_tag="unique_t3",
        ))

    # 5. Multi-Unique high-tier base — Cobalt [4704] multispecialhigh (15종)
    # 여러 유니크가 공유하는 base + 그 중 최소 하나는 고가 → 중간 강조
    if "multi_high" in tiers and tiers["multi_high"]:
        quoted = " ".join(f'"{b}"' for b in tiers["multi_high"])
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"유니크 Multi-base 고티어 ({len(tiers['multi_high'])}종)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=style_from_palette("unique", "P2_CORE",
                                     icon="1 Red Star"),
            continue_=True,
            category_tag="unique_multi_high",
        ))

    # 6. T4 유니크 — Cobalt [4707] hideable2 (13종, 가치 낮지만 표시 유지)
    if "t4" in tiers and tiers["t4"]:
        quoted = " ".join(f'"{b}"' for b in tiers["t4"])
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"유니크 T4 ({len(tiers['t4'])}종, hideable2)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=style_from_palette("unique", "P4_SUPPORT",
                                     icon="2 Brown Star"),
            continue_=True,
            category_tag="unique_t4",
        ))

    # 7. T5 유니크 — Cobalt [4707] hideable (259종, 최하위 인식 티어)
    if "t5" in tiers and tiers["t5"]:
        quoted = " ".join(f'"{b}"' for b in tiers["t5"])
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"유니크 T5 ({len(tiers['t5'])}종, hideable)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=style_from_palette("unique", "P5_MINOR",
                                     icon="2 Brown Star"),
            continue_=True,
            category_tag="unique_t5",
        ))

    # RestEx (Cobalt [4708] 패턴)는 **이식 불가**: first-match 전제 (T1~T5 Show가
    # 먼저 확정 후 restex가 나머지 잡음). 우리 Continue=True 캐스케이드에서 restex를
    # 끝에 두면 T1~T5를 전부 Pink로 덮어쓰는 회귀. 원칙 6 적용하여 현재 unique_generic
    # fallback (P4_SUPPORT Orange Star)이 동일 역할 수행 — 미분류 유니크도 가시함.
    # 향후 Normal/Magic T1 재설계처럼 BaseType 제외 자동화 가능해지면 재검토.

    return "".join(blocks)


def layer_endgame_rare(mode: str = "ssf", game: str = "poe1") -> str:
    """L8 Endgame Rare — NeverSink [[1600]] 구조 + Aurora Glow 스타일.

    NeverSink 조건(ilvl 68+, 사이즈 분류, 링크, T1 ilvl, 부패)은 그대로 복사하되
    스타일은 Aurora 팔레트("base" 카테고리 Turquoise 그라데이션)로 치환.
    모든 블록 Continue=True → L6/L7이 상위 덮어씀.

    game="poe2": ItemClass 는 poe1_to_poe2 매핑 적용 (Shields → Shields+Bucklers,
                 Warstaves → Quarterstaves, Claws/Daggers/O1Axes/Swords drop).
                 매핑 결과가 빈 리스트인 T1 블록은 생성하지 않음.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    rare_exact = _rare_equip_exact_for(game)

    def _class_eq_or_none(poe1_classes: "tuple[str, ...]") -> Optional[str]:
        mapped = _map_poe1_classes(poe1_classes, game)
        if not mapped:
            return None
        return "Class == " + _join_classes_quoted(mapped)

    blocks: list[str] = []

    # 1. 대형 레어 (W>=2 H>=3) — Aurora "base" P2
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레어 대형 (W>=2, H>=3, ilvl>=68)",
        conditions=[
            "Width >= 2", "Height >= 3",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("base", "P2_CORE"),
        continue_=True,
        category_tag="rare_large",
    ))

    # 2. 중형 (W=1, H>=3) — Aurora "base" P3
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레어 중형 세로 (W=1, H>=3)",
        conditions=[
            "Width 1", "Height >= 3",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("base", "P3_USEFUL"),
        continue_=True,
        category_tag="rare_medium_tall",
    ))

    # 3. 중형 (W=2, H=2) — Aurora "base" P3
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레어 중형 정사각 (W=2, H=2)",
        conditions=[
            "Width 2", "Height 2",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("base", "P3_USEFUL"),
        continue_=True,
        category_tag="rare_medium_square",
    ))

    # 4. 소형 (W<=2, H=1) — Aurora "base" P4 (반지/벨트/목걸이)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레어 소형 (반지/벨트/목걸이)",
        conditions=[
            "Width <= 2", "Height 1",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("base", "P4_SUPPORT"),
        continue_=True,
        category_tag="rare_tiny",
    ))

    # 5. 4-Link+ — Aurora "links" 팔레트 (Crimson 계열 벤더 레시피 가치)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레어 4-Link+ (벤더 레시피)",
        conditions=[
            "LinkedSockets >= 4",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("links", "P3_USEFUL"),
        continue_=True,
        category_tag="rare_4link",
    ))

    # 6~9. T1 ilvl 별 Class — Aurora "base" P1 (최상위)
    # POE2 에서 매핑 결과가 빈 리스트인 블록은 skip.
    t1_melee_cond = _class_eq_or_none((
        "Claws", "Daggers", "One Hand Axes", "One Hand Maces",
        "One Hand Swords", "Thrusting One Hand Swords",
        "Two Hand Axes", "Two Hand Maces", "Two Hand Swords", "Warstaves",
    ))
    if t1_melee_cond is not None:
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            "레어 T1 ilvl>=83 근접 무기",
            conditions=[
                "ItemLevel >= 83", "Rarity Rare",
                t1_melee_cond,
            ],
            style=style_from_palette("base", "P1_KEYSTONE"),
            continue_=True,
            category_tag="rare_t1_melee",
        ))
    t1_caster_cond = _class_eq_or_none((
        "Rings", "Rune Daggers", "Sceptres", "Staves", "Wands",
    ))
    if t1_caster_cond is not None:
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            "레어 T1 ilvl>=84 반지/스태프",
            conditions=[
                "ItemLevel >= 84", "Rarity Rare",
                t1_caster_cond,
            ],
            style=style_from_palette("base", "P1_KEYSTONE"),
            continue_=True,
            category_tag="rare_t1_caster",
        ))
    t1_amulet_cond = _class_eq_or_none(("Amulets", "Gloves", "Helmets"))
    if t1_amulet_cond is not None:
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            "레어 T1 ilvl>=85 목걸이/장갑/헬멧",
            conditions=[
                "ItemLevel >= 85", "Rarity Rare",
                t1_amulet_cond,
            ],
            style=style_from_palette("base", "P1_KEYSTONE"),
            continue_=True,
            category_tag="rare_t1_amulet_gloves_helm",
        ))
    t1_armor_cond = _class_eq_or_none((
        "Belts", "Body Armours", "Boots", "Bows", "Quivers", "Shields",
    ))
    if t1_armor_cond is not None:
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            "레어 T1 ilvl>=86 방어구/벨트/보우/쉴드",
            conditions=[
                "ItemLevel >= 86", "Rarity Rare",
                t1_armor_cond,
            ],
            style=style_from_palette("base", "P1_KEYSTONE"),
            continue_=True,
            category_tag="rare_t1_armor",
        ))

    # 10. 부패 레어 (무효 임플리싯) — Aurora "currency" P4 (Faded Coral)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "부패 레어 (CorruptedMods 0)",
        conditions=[
            "Corrupted True", "CorruptedMods 0",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("currency", "P4_SUPPORT"),
        continue_=True,
        category_tag="rare_corrupted_bare",
    ))

    # 11. 부패 레어 + 임플리싯 — Aurora "currency" P1 (Hot Coral 최상)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "부패 레어 + 임플리싯",
        conditions=[
            "Corrupted True", "CorruptedMods >= 1",
            "ItemLevel >= 68", "Rarity Rare",
            rare_exact,
        ],
        style=style_from_palette("currency", "P1_KEYSTONE"),
        continue_=True,
        category_tag="rare_corrupted_implicit",
    ))

    return "".join(blocks)


def layer_ssf_currency_extras(mode: str = "ssf",
                              items: Optional[GGPKItems] = None) -> str:
    """L8 SSF 확장 커런시 — Essence/Oil/Fossil/Resonator/Delirium Orb.

    GGPK BaseItemTypes에서 **실제 존재하는 전체 아이템명**으로 BaseType == 정확 매칭.
    (Wreckers 접두사 substring 방식은 POE 파서 경고 유발 — 회피.)
    SSF 관점: 모든 티어 Show, 숨김 없음 (자급자족 크래프팅).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    d = items if items is not None else load_ggpk_items()
    blocks: list[str] = []

    def _row(label: str, names: tuple[str, ...], palette_tier: str, icon: str,
             category_tag: str, effect: Optional[str] = None):
        if not names:
            return
        quoted = " ".join(f'"{n}"' for n in names)
        style = style_from_palette("currency", palette_tier, icon=icon)
        if effect:
            style.effect = effect
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"{label} ({len(names)}종)",
            conditions=['Class "Currency"', f'BaseType == {quoted}'],
            style=style,
            continue_=False,
            category_tag=category_tag,
        ))

    # Essences 5 티어 — Pink/Magenta 명시 (currency 팔레트 Hot Coral과 구분)
    def _essence(label, names, font, border_a, text_a, bg_a, sound, icon, tag):
        if not names:
            return
        quoted = " ".join(f'"{n}"' for n in names)
        style = LayerStyle(
            font=font, text=text_a, border=border_a, bg=bg_a,
            sound=sound, effect="Pink", icon=icon,
        )
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"{label} ({len(names)}종)",
            conditions=['Class "Currency"', f'BaseType == {quoted}'],
            style=style,
            continue_=False,
            category_tag=tag,
        ))

    # 부패 T0 — 최상 (Hysteria/Insanity/Horror/Delirium/Desolation): 흰BG + 빨강 + Sound 6
    _essence("부패 에센스 T0 (5종)", d.essence_corrupt,
             45, "255 0 0", "255 255 255", "255 255 255 255",
             "6 300", "0 Red Star", "essence_corrupt")
    # Remnant of Corruption — 부패 변환 재료, Vaal Orb 격
    _essence("Remnant of Corruption", d.remnant_corruption,
             42, "255 80 80", "255 150 150", "80 0 0 230",
             "3 300", "0 Red Cross", "remnant_corruption")
    _essence("Essences Deafening (T1)", d.essence_deafening,
             45, "255 100 200", "255 140 220", "60 0 30 255",
             "6 300", "0 Pink Cross", "essence_t1")
    _essence("Essences Shrieking (T2)", d.essence_shrieking,
             42, "255 130 200", "255 160 220", "60 0 30 230",
             "3 300", "1 Pink Cross", "essence_t2")
    _essence("Essences Screaming (T3)", d.essence_screaming,
             38, "230 140 200", "240 170 220", "50 0 30 200",
             None, "1 Pink Cross", "essence_t3")
    _essence("Essences Wailing (T4)", d.essence_wailing,
             36, "200 130 180", "220 160 210", "40 0 25 180",
             None, "2 Pink Cross", "essence_t4")
    _essence("Essences Weeping (T5)", d.essence_weeping,
             35, "190 120 170", "210 150 200", "35 0 22 170",
             None, "2 Pink Cross", "essence_t5_weeping")
    _essence("Essences Muttering (T6)", d.essence_muttering,
             34, "180 110 160", "200 140 200", "30 0 20 160",
             None, "2 Pink Cross", "essence_t6_muttering")
    _essence("Essences Whispering (T7)", d.essence_whispering,
             33, "160 100 140", "180 130 180", "25 0 18 140",
             None, "2 Pink Cross", "essence_t7_whispering")

    # Fossils
    _row("Fossils 고가", d.fossils_high,
         "P1_KEYSTONE", "0 Pink Cross", "fossil_high", effect="Pink")
    _row("Fossils 일반", d.fossils_basic,
         "P3_USEFUL", "2 Pink Cross", "fossil_basic")

    # Resonators — Aurora 다른 카테고리로 tier 차별 (coral 단조 회피)
    def _reso_row(label, names, palette_cat, palette_tier, icon, tag, effect=None):
        if not names: return
        quoted = " ".join(f'"{n}"' for n in names)
        style = style_from_palette(palette_cat, palette_tier, icon=icon)
        if effect: style.effect = effect
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"{label} ({len(names)}종)",
            conditions=['Class "Currency"', f'BaseType == {quoted}'],
            style=style,
            continue_=False,
            category_tag=tag,
        ))
    # Prime → links Crimson (최상)
    _reso_row("Resonators Prime (T1)", d.resonators_prime,
              "links", "P1_KEYSTONE", "0 Red Cross", "resonator_prime", effect="Red")
    # Powerful → gold (메인)
    _reso_row("Resonators Powerful (T2)", d.resonators_powerful,
              "gold", "P2_CORE", "1 Yellow Cross", "resonator_powerful")
    # Potent/Primitive → base dim (저급)
    _reso_row("Resonators Potent/Primitive", d.resonators_low,
              "base", "P4_SUPPORT", "2 Cyan Cross", "resonator_low")

    # Delirium Orbs
    _row("Delirium Orbs", d.delirium_orbs,
         "P2_CORE", "1 Pink Cross", "delirium_orb", effect="Pink")

    # Blight Oils — Wreckers L1585~1674 13단계 계단식 이식.
    # 각 오일마다 고유 폰트(33~45)와 사운드 볼륨(120~300, 15씩 점증) → SSF 플레이어가
    # 소리/크기만으로 오일 등급 인식 가능. 색상은 오일 이름의 실제 hue 반영.
    # Phase 4a: 4-tier 그룹핑 → 13개 개별 블록 (Wreckers parity).
    _OIL_CASCADE: "list[tuple[str, int, int, str, str]]" = [
        # (name, font, sound_vol, text_rgb, icon)
        ("Clear Oil",      33, 120, "220 220 220", "2 Pink Cross"),
        ("Sepia Oil",      34, 135, "200 160 120", "2 Pink Cross"),
        ("Amber Oil",      35, 150, "255 180 60",  "2 Pink Cross"),
        ("Verdant Oil",    36, 165, "60 200 100",  "2 Pink Cross"),
        ("Teal Oil",       37, 180, "0 200 200",   "1 Cyan Cross"),
        ("Azure Oil",      38, 195, "60 120 255",  "1 Cyan Cross"),
        ("Indigo Oil",     39, 210, "120 60 220",  "1 Purple Cross"),
        ("Violet Oil",     40, 225, "200 60 255",  "1 Purple Cross"),
        ("Crimson Oil",    41, 240, "220 0 80",    "0 Pink Cross"),
        ("Black Oil",      42, 255, "150 70 180",  "0 Pink Cross"),
        ("Opalescent Oil", 43, 270, "230 230 230", "0 Pink Cross"),
        ("Silver Oil",     44, 285, "200 200 220", "0 Pink Cross"),
        ("Golden Oil",     45, 300, "240 200 60",  "0 Yellow Cross"),
    ]
    # Oil 이름 DB 존재 여부 체크 (모든 오일이 모든 리그에 있진 않음)
    _all_oil_names = set(d.oils_top) | set(d.oils_high) | set(d.oils_mid) | set(d.oils_low)
    for oil_name, font_sz, sound_vol, text_rgb, icon in _OIL_CASCADE:
        if oil_name not in _all_oil_names:
            continue
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Oil 계단식 {oil_name} (font {font_sz}, vol {sound_vol})",
            conditions=['Class "Currency"', f'BaseType == "{oil_name}"'],
            style=LayerStyle(
                font=font_sz,
                text=text_rgb,
                border=text_rgb,
                sound=f"12 {sound_vol}",
                icon=icon,
            ),
            continue_=False,
            category_tag=f"oil_{oil_name.split()[0].lower()}",
        ))

    # Reflective / Prismatic / Tainted Oil — 최상급 (font 45, vol 300, 흰BG)
    if d.oils_premium:
        quoted = " ".join(f'"{n}"' for n in d.oils_premium)
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Oil 최상급 Reflective/Prismatic/Tainted ({len(d.oils_premium)}종)",
            conditions=['Class "Currency"', f'BaseType == {quoted}'],
            style=LayerStyle(
                font=45,
                text="0 0 0",
                border="255 0 200",
                bg="255 255 255 255",
                sound="12 300",
                effect="Pink",
                icon="0 Pink Star",
            ),
            continue_=False,
            category_tag="oil_premium",
        ))

    return "".join(blocks)


def layer_gems_quality(mode: str = "ssf") -> str:
    """L8 Gems — 퀄리티/레벨/특수 변형 티어링.

    Wreckers SSF 패턴 구조 복사 (2026-04-13 레퍼런스):
      - Vaal 젬 (BaseType "Vaal") → 빨간 보더
      - AlternateQuality / TransfiguredGem → Cyan Circle + sound
      - Exceptional supports (Empower/Enhance/Enlighten) + GemLevel>=4 → 흰 배경 + Star
      - Quality 20+, 23+ → 폰트 확대 + 강조
      - Awakened 계열 → 항상 큰 Cyan Star
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    blocks: list[str] = []

    # 1. Vaal 젬 (corrupted) — 빨간 보더
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Vaal 젬 (부패)",
        conditions=['Class "Gem"', 'BaseType "Vaal"'],
        style=LayerStyle(border="200 0 0", effect="Red"),
        continue_=True,
        category_tag="gem_vaal",
    ))

    # 2. Alternate Quality (Divergent/Anomalous/Phantasmal) — Cyan Circle
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Alternate Quality 젬",
        conditions=['Class "Gem"', "AlternateQuality True"],
        style=LayerStyle(font=40, effect="Cyan", icon="0 Cyan Circle", sound="12 300"),
        continue_=True,
        category_tag="gem_altqual",
    ))

    # 3. Transfigured (POE 3.22+; 현재 GGPK에 없어도 조건은 유지 — 리그에 따라 활성)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Transfigured 젬",
        conditions=['Class "Gem"', "TransfiguredGem True"],
        style=LayerStyle(font=40, effect="Cyan", icon="0 Cyan Circle", sound="12 300"),
        continue_=True,
        category_tag="gem_transfigured",
    ))

    # 4. Awakened 계열 전체 — 항상 큰 Cyan Star
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Awakened 서포트 젬 (Sirus/Maven 드롭)",
        conditions=['Class "Gem"', 'BaseType "Awakened"'],
        style=LayerStyle(font=45, effect="Cyan", icon="0 Cyan Star", sound="6 300",
                         bg="0 40 60 240"),
        continue_=True,
        category_tag="gem_awakened",
    ))

    # 5. Exceptional supports (Empower/Enhance/Enlighten) + GemLevel>=4 — 흰 배경 + Star
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "Exceptional Support Lv4+ (Empower/Enhance/Enlighten)",
        conditions=[
            'Class "Gem"',
            'BaseType == "Empower Support" "Enhance Support" "Enlighten Support"',
            "GemLevel >= 4",
        ],
        style=LayerStyle(font=45, bg="255 255 255 255", text="0 0 0", effect="Cyan",
                         icon="0 Cyan Star", sound="12 300"),
        continue_=True,
        category_tag="gem_exceptional_lv4",
    ))

    # 6a. Quality 13%+ — 약한 강조 (NeverSink GCP 분류 임계)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "퀄리티 13%+ 젬",
        conditions=['Class "Gem"', "Quality >= 13"],
        style=LayerStyle(font=37, border="200 100 200"),
        continue_=True,
        category_tag="gem_q13",
    ))

    # 6b. Quality 20%+ — 폰트 확대 (GCP 레시피 / 퀄리티 가치 임계)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "퀄리티 20%+ 젬",
        conditions=['Class "Gem"', "Quality >= 20"],
        style=LayerStyle(font=40, border="255 0 200", effect="Cyan"),
        continue_=True,
        category_tag="gem_q20",
    ))

    # 7. Quality 23%+ — 최대 강조 (완벽 품질, 흰 배경 + sound)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "퀄리티 23%+ 젬 (완벽)",
        conditions=['Class "Gem"', "Quality >= 23"],
        style=LayerStyle(font=45, bg="255 255 255 255", text="0 0 0",
                         effect="White", icon="0 White Cross", sound="12 300"),
        continue_=True,
        category_tag="gem_q23",
    ))

    # 8a. GemLevel 18+ — 약한 강조 (NeverSink 임계)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레벨 18+ 젬",
        conditions=['Class "Gem"', "GemLevel >= 18"],
        style=LayerStyle(font=38, border="200 200 100"),
        continue_=True,
        category_tag="gem_lv18",
    ))

    # 8b. GemLevel 20+ — 큰 폰트 (고레벨 젬, 벤더 가치)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레벨 20+ 젬",
        conditions=['Class "Gem"', "GemLevel >= 20"],
        style=LayerStyle(font=42, border="255 255 100", effect="Yellow", icon="1 Yellow Star"),
        continue_=True,
        category_tag="gem_lv20",
    ))

    # 9. GemLevel 21+ — 최대 강조 (리미트 브레이크)
    blocks.append(make_layer_block(
        LAYER_CATEGORY_SHOW,
        "레벨 21+ 젬 (리미트)",
        conditions=['Class "Gem"', "GemLevel >= 21"],
        style=LayerStyle(font=45, bg="255 255 255 255", text="0 0 0",
                         effect="Yellow", icon="0 Yellow Star", sound="6 300"),
        continue_=True,
        category_tag="gem_lv21",
    ))

    return "".join(blocks)


def layer_scarabs(mode: str = "ssf", items: Optional[GGPKItems] = None) -> str:
    """L8 Scarabs — 특수(Horned/Titanic/Influencing) 우선, 일반은 표준 Show."""
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")
    d = items if items is not None else load_ggpk_items()
    if not d.scarabs_all:
        return ""
    blocks: list[str] = []

    if d.scarabs_special:
        quoted = " ".join(f'"{x}"' for x in d.scarabs_special)
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Scarabs 특수 ({len(d.scarabs_special)}종)",
            conditions=["Class \"Map Fragments\"", f"BaseType == {quoted}"],
            style=style_from_palette("fragment", "P1_KEYSTONE",
                                     effect="Yellow", icon="0 Yellow Hexagon"),
            continue_=False,
            category_tag="scarab_special",
        ))

    # 일반 스카랩 (특수 제외)
    regular = tuple(n for n in d.scarabs_all if n not in set(d.scarabs_special))
    if regular:
        quoted = " ".join(f'"{x}"' for x in regular)
        blocks.append(make_layer_block(
            LAYER_CATEGORY_SHOW,
            f"Scarabs 일반 ({len(regular)}종)",
            conditions=["Class \"Map Fragments\"", f"BaseType == {quoted}"],
            style=style_from_palette("fragment", "P3_USEFUL",
                                     icon="2 Yellow Hexagon"),
            continue_=False,
            category_tag="scarab_regular",
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


_WEAPON_MOD_TIERS_CACHE: Optional[dict] = None
_DEFENSE_MOD_TIERS_CACHE: Optional[dict] = None
_ACCESSORY_MOD_TIERS_CACHE: Optional[dict] = None

# L7 defense_proxy: slot key → POE filter Class 이름
_DEFENSE_SLOT_CLASS: dict[str, str] = {
    "body_armour": "Body Armours",
    "helmet": "Helmets",
    "boots": "Boots",
    "gloves": "Gloves",
    "shield": "Shields",
}

# L7 defense_proxy: strictness → HasExplicitMod counted 하한
# Phase B 무기 패턴 재사용 (0~1 관대, 2+ 엄격)
_STRICTNESS_DEFENSE_MOD_COUNT: dict[int, int] = {0: 2, 1: 2, 2: 3, 3: 3, 4: 4}


def _load_defense_mod_tiers() -> dict:
    """data/defense_mod_tiers.json — NeverSink 방어 mod-tier 룰 매핑.

    Missing → empty → caller skips defense_proxy blocks.
    """
    global _DEFENSE_MOD_TIERS_CACHE
    if _DEFENSE_MOD_TIERS_CACHE is not None:
        return _DEFENSE_MOD_TIERS_CACHE
    path = _DATA_DIR / "defense_mod_tiers.json"
    if not path.exists():
        logger.warning("defense_mod_tiers.json missing — L7 defense_proxy skipped")
        _DEFENSE_MOD_TIERS_CACHE = {}
        return _DEFENSE_MOD_TIERS_CACHE
    try:
        _DEFENSE_MOD_TIERS_CACHE = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("defense_mod_tiers.json 로드 실패: %s — L7 defense_proxy skipped", e)
        _DEFENSE_MOD_TIERS_CACHE = {}
    return _DEFENSE_MOD_TIERS_CACHE


def _active_defence_focuses(defence_types: frozenset[str]) -> list[str]:
    """defence axis 집합 → NeverSink focus 토큰 리스트 ('life', 'es').

    - "ar" 또는 "ev" 포함 → "life" (NeverSink life_based는 armour/evasion 둘 다 포괄)
    - "es" 포함 → "es"
    - 둘 다 있는 하이브리드(예: Occultist Aegis Aurora) → 양쪽
    """
    focuses: list[str] = []
    if defence_types & {"ar", "ev"}:
        focuses.append("life")
    if "es" in defence_types:
        focuses.append("es")
    return focuses


def _defense_proxy_blocks(
    defence_types: frozenset[str],
    strictness: int,
    label_suffix: str,
    al_conditions: list[str],
    category_tag_prefix: str,
) -> list[str]:
    """L7 defense_proxy — 빌드 방어 axis에 맞는 레어 장비 강조.

    defence_types 비면 빈 리스트. 각 (slot × focus) 조합마다 NeverSink 레퍼런스 패턴으로
    Show 블록 생성. first-match + continue_=False → 일반 rare 흐름 전에 가로챔.

    레퍼런스: _analysis/neversink_8.19.0b/1-REGULAR.filter line 1064-1300
    """
    focuses = _active_defence_focuses(defence_types)
    if not focuses:
        return []

    tiers = _load_defense_mod_tiers()
    slots = tiers.get("slots", {})
    if not slots:
        return []

    mod_count = _STRICTNESS_DEFENSE_MOD_COUNT.get(strictness, 3)
    blocks: list[str] = []

    for focus in focuses:
        for slot_key, cls_name in _DEFENSE_SLOT_CLASS.items():
            slot_data = slots.get(slot_key, {}).get(focus)
            if not slot_data:
                continue
            required = slot_data.get("required_any") or []
            # fallback: required_count_2 (일부 slot은 required_any 없이 count만)
            if not required:
                required = slot_data.get("required_count_2") or []
            counted_key = next(
                (k for k in slot_data if k.startswith("required_count_")),
                None,
            )
            counted = slot_data.get(counted_key, []) if counted_key else []
            exclude = slot_data.get("exclude", []) or []
            if not (required or counted):
                continue

            conditions: list[str] = [
                "Identified True",
                "Rarity Rare",
                f'Class == "{cls_name}"',
            ]
            if required:
                req_quoted = " ".join(f'"{m}"' for m in required)
                conditions.append(f"HasExplicitMod {req_quoted}")
            if counted:
                cnt_quoted = " ".join(f'"{m}"' for m in counted)
                conditions.append(f"HasExplicitMod >= {mod_count} {cnt_quoted}")
            if exclude:
                exc_quoted = " ".join(f'"{m}"' for m in exclude)
                conditions.append(f"HasExplicitMod = 0 {exc_quoted}")
            conditions.extend(al_conditions)

            comment = (
                f"빌드 방어 프록시{label_suffix} {slot_key}.{focus} "
                f"(mod count >= {mod_count}, required={len(required)}, "
                f"counted={len(counted)})"
            )
            blocks.append(make_layer_block(
                LAYER_BUILD_TARGET,
                comment,
                conditions=conditions,
                style=LayerStyle(
                    border=_BUILD_CYAN,
                    bg="0 0 0 220",
                    font=43,
                    effect="Cyan",
                    icon="0 Cyan Star",
                ),
                category_tag=f"{category_tag_prefix}_{slot_key}_{focus}",
            ))
    return blocks


# L7 accessory_proxy: slot key → POE filter Class 이름
_ACCESSORY_SLOT_CLASS: dict[str, str] = {
    "amulet": "Amulets",
    "ring": "Rings",
    "belt": "Belts",
}


def _load_accessory_mod_tiers() -> dict:
    """data/accessory_mod_tiers.json — NeverSink 악세서리 mod-tier 룰.

    Missing → empty → caller skips accessory_proxy blocks.
    """
    global _ACCESSORY_MOD_TIERS_CACHE
    if _ACCESSORY_MOD_TIERS_CACHE is not None:
        return _ACCESSORY_MOD_TIERS_CACHE
    path = _DATA_DIR / "accessory_mod_tiers.json"
    if not path.exists():
        logger.warning("accessory_mod_tiers.json missing — L7 accessory_proxy skipped")
        _ACCESSORY_MOD_TIERS_CACHE = {}
        return _ACCESSORY_MOD_TIERS_CACHE
    try:
        _ACCESSORY_MOD_TIERS_CACHE = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("accessory_mod_tiers.json 로드 실패: %s — L7 accessory_proxy skipped", e)
        _ACCESSORY_MOD_TIERS_CACHE = {}
    return _ACCESSORY_MOD_TIERS_CACHE


def _active_damage_axes(damage_types: frozenset[str]) -> list[str]:
    """빌드 damage_types + 공통 'common' 축 포함 리스트.

    - damage_types 비어 있어도 'common'은 항상 활성 (exalter amulet / general belt)
    - 순서: damage axis 먼저, common은 마지막 (필터 우선순위)
    """
    axes: list[str] = []
    # 결정적 순서 유지 (테스트 박제)
    for axis in ("attack", "caster", "dot", "minion"):
        if axis in damage_types:
            axes.append(axis)
    axes.append("common")
    return axes


def _accessory_proxy_blocks(
    damage_types: frozenset[str],
    strictness: int,
    label_suffix: str,
    al_conditions: list[str],
    category_tag_prefix: str,
) -> list[str]:
    """L7 accessory_proxy — amulet/ring/belt × damage axis + common.

    damage_types 비어 있어도 common 블록은 emit (exalter amulet, general belt).
    first-match + continue_=False → 일반 rare 흐름 전에 가로챔.

    레퍼런스: _analysis/neversink_8.19.0b/1-REGULAR.filter line 1238-1501
    """
    axes = _active_damage_axes(damage_types)
    if not axes:
        return []

    tiers = _load_accessory_mod_tiers()
    slots = tiers.get("slots", {})
    if not slots:
        return []

    mod_count = _STRICTNESS_DEFENSE_MOD_COUNT.get(strictness, 3)
    blocks: list[str] = []

    for axis in axes:
        for slot_key, cls_name in _ACCESSORY_SLOT_CLASS.items():
            slot_data = slots.get(slot_key, {}).get(axis)
            if not slot_data:
                continue
            required = slot_data.get("required_any") or []
            if not required:
                required = slot_data.get("required_count_2") or []
            counted_key = next(
                (k for k in slot_data if k.startswith("required_count_")),
                None,
            )
            counted = slot_data.get(counted_key, []) if counted_key else []
            exclude = slot_data.get("exclude", []) or []
            if not (required or counted):
                continue

            conditions: list[str] = [
                "Identified True",
                "Rarity Rare",
                f'Class == "{cls_name}"',
            ]
            if required:
                req_quoted = " ".join(f'"{m}"' for m in required)
                conditions.append(f"HasExplicitMod {req_quoted}")
            if counted:
                cnt_quoted = " ".join(f'"{m}"' for m in counted)
                conditions.append(f"HasExplicitMod >= {mod_count} {cnt_quoted}")
            if exclude:
                exc_quoted = " ".join(f'"{m}"' for m in exclude)
                conditions.append(f"HasExplicitMod = 0 {exc_quoted}")
            conditions.extend(al_conditions)

            comment = (
                f"빌드 악세서리 프록시{label_suffix} {slot_key}.{axis} "
                f"(mod count >= {mod_count}, required={len(required)}, "
                f"counted={len(counted)})"
            )
            blocks.append(make_layer_block(
                LAYER_BUILD_TARGET,
                comment,
                conditions=conditions,
                style=LayerStyle(
                    border=_BUILD_CYAN,
                    bg="0 0 0 220",
                    font=43,
                    effect="Cyan",
                    icon="0 Cyan Star",
                ),
                category_tag=f"{category_tag_prefix}_{slot_key}_{axis}",
            ))
    return blocks


def _load_weapon_mod_tiers() -> dict:
    """data/weapon_mod_tiers.json — NeverSink 812-844 룰 매핑.

    Missing file → empty dict → caller skips the weapon_phys_proxy block.
    Regenerate by re-running the analysis (data is hand-maintained, not auto).
    """
    global _WEAPON_MOD_TIERS_CACHE
    if _WEAPON_MOD_TIERS_CACHE is not None:
        return _WEAPON_MOD_TIERS_CACHE
    path = Path(__file__).resolve().parent.parent / "data" / "weapon_mod_tiers.json"
    if not path.exists():
        logger.warning("weapon_mod_tiers.json missing — L7 weapon_phys_proxy will be skipped")
        _WEAPON_MOD_TIERS_CACHE = {}
        return _WEAPON_MOD_TIERS_CACHE
    _WEAPON_MOD_TIERS_CACHE = json.loads(path.read_text(encoding="utf-8"))
    return _WEAPON_MOD_TIERS_CACHE


def _weapon_phys_proxy_block(
    weapon_classes: list[str],
    strictness: int,
    label_suffix: str,
    al_conditions: list[str],
    category_tag: str,
) -> Optional[str]:
    """L7 weapon_phys_proxy block — NeverSink weapon_phys/physpure mod-tier rule.

    Emits a rare-weapon Show rule gated by HasExplicitMod thresholds. Returns
    None when inputs insufficient so the caller's join drops the section.

    - strictness < mirrored_corrupted_exclude_at_strictness_below → physpure
      variant (Mirrored/Corrupted False, mod count ≥ 2)
    - otherwise → standard variant (mod count ≥ 3)

    al_conditions: per-stage AreaLevel filters from StageData.al_conditions().
    """
    if not weapon_classes:
        return None
    tiers = _load_weapon_mod_tiers()
    required = tiers.get("required_any_mod") or []
    counted = tiers.get("counted_good_mods") or []
    excluded = tiers.get("excluded_bad_mods") or []
    if not (required and counted and excluded):
        logger.warning(
            "weapon_mod_tiers.json incomplete (required=%d counted=%d excluded=%d) — "
            "skipping weapon_phys_proxy",
            len(required), len(counted), len(excluded),
        )
        return None

    mod_count = _STRICTNESS_WEAPON_MOD_COUNT.get(strictness, 3)
    physpure_threshold = tiers.get("mirrored_corrupted_exclude_at_strictness_below", 2)
    use_physpure = strictness < physpure_threshold
    drop_level_min = tiers.get("drop_level_min", 5)

    cls_quoted = " ".join(f'"{c}"' for c in weapon_classes)
    required_quoted = " ".join(f'"{m}"' for m in required)
    counted_quoted = " ".join(f'"{m}"' for m in counted)
    excluded_quoted = " ".join(f'"{m}"' for m in excluded)

    conditions: list[str] = []
    if use_physpure:
        # Match order to NeverSink 828-844 (Mirrored/Corrupted first for clarity).
        conditions.extend(["Mirrored False", "Corrupted False"])
    conditions.extend([
        "Identified True",
        f"DropLevel >= {drop_level_min}",
        "Rarity Rare",
        f"Class == {cls_quoted}",
        f"HasExplicitMod {required_quoted}",
        f"HasExplicitMod >= {mod_count} {counted_quoted}",
        f"HasExplicitMod = 0 {excluded_quoted}",
        *al_conditions,
    ])

    variant = "physpure" if use_physpure else "phys"
    comment = (
        f"빌드 무기 phys 프록시{label_suffix} ({len(weapon_classes)} class, "
        f"mod count >= {mod_count}, {variant})"
    )
    return make_layer_block(
        LAYER_BUILD_TARGET,
        comment,
        conditions=conditions,
        style=LayerStyle(
            border=_BUILD_CYAN,
            bg="0 0 0 220",
            font=43,
            effect="Cyan",
            icon="0 Cyan Star",
        ),
        category_tag=category_tag,
    )


def layer_build_target(
    build_data: "Optional[dict | list[dict]]" = None,
    coaching_data: Optional[dict] = None,
    stage: bool = False,
    al_split: int = 67,
    strictness: int = 3,
) -> str:
    """L7 Build Target — 빌드 유니크/디비카/chanceable/젬/베이스 하이라이트.

    - `stage=False` (기본): 모든 카테고리 union (AL 조건 없음).
    - `stage=True`: **uniques + chanceable만** Lv 기반 AL 분기 (al_split 기준).
    - `al_split`: 2-POB 전환 AL (기본 67 = Kitava 후). N>=3 POB는 Lv 중간값 사용.
    """
    if not build_data:
        return ""

    from build_extractor import merge_build_stages

    builds = build_data if isinstance(build_data, list) else [build_data]

    # 공통: union 카테고리(gem/support/divcard/base) 수집
    union_stages = merge_build_stages(builds, coaching_data, no_staging=True, al_split=al_split)
    if not union_stages:
        return ""
    union = union_stages[0]  # no_staging=True면 항상 단일 stage

    # stage 카테고리(unique/chanceable)
    if stage:
        staged = merge_build_stages(builds, coaching_data, no_staging=False, al_split=al_split)
    else:
        staged = [union]  # 전체 union 취급

    def _cyan_style(icon: str, font: int = 42) -> LayerStyle:
        return LayerStyle(border=_BUILD_CYAN, font=font, effect="Cyan", icon=icon)

    blocks: list[str] = []

    # ── uniques / chanceable (선택적 staging) ──
    for s in staged:
        tag_suffix = "" if s.label == "all" else f"_{s.label}"
        al_conds = s.al_conditions()
        hint = f" [{s.label}]" if s.label != "all" else ""

        if s.unique_bases:
            quoted = " ".join(f'"{b}"' for b in s.unique_bases)
            orig = ", ".join(s.unique_names[:3]) + ("..." if len(s.unique_names) > 3 else "")
            blocks.append(make_layer_block(
                LAYER_BUILD_TARGET,
                f"빌드 유니크{hint} ({len(s.unique_bases)}종 base, 원본: {orig})",
                conditions=["Rarity Unique", f"BaseType == {quoted}", *al_conds],
                style=_cyan_style("0 Cyan Star", font=45),
                category_tag=f"unique{tag_suffix}",
            ))
        if s.chanceable:
            names = " ".join(f'"{c["base"]}"' for c in s.chanceable)
            blocks.append(make_layer_block(
                LAYER_BUILD_TARGET,
                f"Chanceable 베이스{hint} ({len(s.chanceable)}종)",
                conditions=["Rarity Normal", f"BaseType == {names}", *al_conds],
                style=_cyan_style("0 Cyan Circle", font=40),
                category_tag=f"chanceable{tag_suffix}",
            ))

        # weapon_phys_proxy — Build 무기 클래스 레어 중 T1/T2 물리 mod만 강조.
        # 순서 고정: unique > chanceable > weapon_phys_proxy > defense_proxy > ...
        # (first-match semantics; Class+mod 조합이 일반 base whitelist보다 우선).
        proxy = _weapon_phys_proxy_block(
            s.weapon_classes,
            strictness=strictness,
            label_suffix=hint,
            al_conditions=al_conds,
            category_tag=f"weapon_phys_proxy{tag_suffix}",
        )
        if proxy is not None:
            blocks.append(proxy)

        # defense_proxy — 빌드 방어 axis(life/es)에 맞는 레어 장비 강조
        # (body/helmet/boots/gloves/shield × life/es). defence_types 비면 skip.
        blocks.extend(_defense_proxy_blocks(
            s.defence_types,
            strictness=strictness,
            label_suffix=hint,
            al_conditions=al_conds,
            category_tag_prefix=f"defense_proxy{tag_suffix}",
        ))

        # accessory_proxy — 빌드 damage axis(attack/caster/dot/minion)별 amu/ring/belt.
        # common 블록(exalter amulet, general belt)은 damage_types 비어도 항상 emit.
        blocks.extend(_accessory_proxy_blocks(
            s.damage_types,
            strictness=strictness,
            label_suffix=hint,
            al_conditions=al_conds,
            category_tag_prefix=f"accessory_proxy{tag_suffix}",
        ))

    # ── divcard / skill / support / base (항상 union) ──
    if union.target_cards:
        names = " ".join(f'"{c["card"]}"' for c in union.target_cards)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 타겟 디비카 ({len(union.target_cards)}종)",
            conditions=['Class "Divination Cards"', f"BaseType == {names}"],
            style=_cyan_style("0 Cyan Square", font=42),
            category_tag="divcard",
        ))
    if union.skills:
        names = " ".join(f'"{g}"' for g in union.skills)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 스킬 젬 ({len(union.skills)}종)",
            conditions=['Class == "Skill Gems"', f"BaseType == {names}"],
            style=_cyan_style("0 Cyan Hexagon", font=42),
            category_tag="skill_gem",
        ))
    if union.supports:
        names = " ".join(f'"{s}"' for s in union.supports)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 서포트 젬 ({len(union.supports)}종)",
            conditions=['Class == "Support Gems"', f"BaseType == {names}"],
            style=_cyan_style("1 Cyan Hexagon", font=38),
            category_tag="support_gem",
        ))
    if union.bases:
        names = " ".join(f'"{b}"' for b in union.bases)
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 장비 베이스 ({len(union.bases)}종)",
            conditions=["Rarity Rare", f"BaseType == {names}", "ItemLevel >= 75"],
            style=_cyan_style("1 Cyan Square", font=40),
            category_tag="base",
        ))

        # 액트 단계 빌드 무기/장비 감정 강조 — AL<68 (캠페인) + 모든 Rarity.
        # ilvl 제한 없음 — 레벨링 중 주워서 identify해볼 가치 있는 드롭 시각화.
        # Magenta 강조 (기존 Cyan과 구분 — "identify 후보" 시그널).
        _MAGENTA = "255 100 200"
        blocks.append(make_layer_block(
            LAYER_BUILD_TARGET,
            f"빌드 베이스 액트 감정 후보 ({len(union.bases)}종, AL<68 전체 Rarity)",
            conditions=[
                "Rarity Normal Magic Rare",
                f"BaseType == {names}",
                "AreaLevel < 68",
            ],
            style=LayerStyle(
                text=_MAGENTA, border=_MAGENTA,
                bg="60 20 40 240",
                font=42,
                effect="Pink",
                icon="0 Pink Diamond",
            ),
            category_tag="base_act_identify",
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


# ---------------------------------------------------------------------------
# Wreckers L172 + L237 T1 보더 재Show — build_data 무관 unconditional
# ---------------------------------------------------------------------------
#
# 원칙 6: Wreckers first parity. Wreckers는 Hide 뒤에서 T1 보더를 Show로 복원
# (L172 main equip + L237 Trinket/Heist/Flask/Tincture/Cluster).
# 우리 L10이 L9 Hide / L11 blanket 뒤에 위치하므로 동일 시맨틱.
# Continue=False → POE top-down 첫 매칭이 승리 → L11 blanket으로부터 T1 보호.

# T1 재Show 그룹. POE1 은 7 카테고리, POE2 는 2 카테고리 (Trinkets/Heist/Utility Flasks/
# Tinctures/Cluster Jewels 는 POE1 전용). 각 그룹의 Class 조건은 game 에 따라 매핑.
_T1_RESHOW_GROUPS_POE1: "list[tuple[str, list[str], int, str]]" = [
    # (tag_base, conditions_list, ilvl, comment_prefix)
    ("ring_glove_helm",
     ['Class == "Rings" "Gloves" "Helmets"'],
     85, "반지/장갑/헬멧 T1 보더"),
    ("main_equip",
     ['Class == "Amulets" "Belts" "Body Armours" "Boots" "Bows" "Claws" "Daggers" '
      '"One Hand Axes" "One Hand Maces" "One Hand Swords" "Quivers" "Rune Daggers" '
      '"Sceptres" "Shields" "Staves" "Thrusting One Hand Swords" "Two Hand Axes" '
      '"Two Hand Maces" "Two Hand Swords" "Wands" "Warstaves"'],
     86, "메인 장비 T1 보더"),
    ("trinket_heist",
     ['Class == "Trinkets" "Heist Gear" "Heist Tool" "Heist Cloak"'],
     83, "Trinket/Heist 장비 T1 보더"),
    ("flask_brooch",
     ['Class == "Life Flasks" "Mana Flasks" "Hybrid Flasks" "Heist Brooch"'],
     84, "Life/Mana/Hybrid Flask + Heist Brooch T1 보더"),
    ("utility_tincture",
     ['Class == "Utility Flasks" "Tinctures"'],
     85, "Utility Flask/Tincture T1 보더"),
    ("small_cluster",
     ['Class == "Jewels"', 'BaseType == "Small Cluster Jewel"'],
     75, "Small Cluster Jewel T1 보더"),
    ("mid_large_cluster",
     ['Class == "Jewels"',
      'BaseType == "Medium Cluster Jewel" "Large Cluster Jewel"'],
     84, "Medium/Large Cluster Jewel T1 보더"),
]


def _t1_reshow_groups_for(game: str) -> "list[tuple[str, list[str], int, str]]":
    """game 별 T1 재Show 그룹.

    - POE1: 7 카테고리 그대로.
    - POE2: ring_glove_helm / main_equip 만 POE2 ItemClass 로 변환하고
            Trinket/Heist/Flask/Tincture/Cluster Jewel 은 POE1 전용이라 skip.
    """
    if game == "poe1":
        return _T1_RESHOW_GROUPS_POE1
    if game != "poe2":
        raise ValueError(f"unsupported game: {game!r}")

    out: "list[tuple[str, list[str], int, str]]" = []
    rgh = _map_poe1_classes(_POE1_T1_RESHOW_RING_GLOVE_HELM, "poe2")
    if rgh:
        out.append((
            "ring_glove_helm",
            [f"Class == {_join_classes_quoted(rgh)}"],
            85, "반지/장갑/헬멧 T1 보더",
        ))
    main = _map_poe1_classes(_POE1_T1_RESHOW_MAIN_EQUIP, "poe2")
    if main:
        out.append((
            "main_equip",
            [f"Class == {_join_classes_quoted(main)}"],
            86, "메인 장비 T1 보더",
        ))
    return out

# Wreckers L172 표준 색 (rarity → border)
_T1_RESHOW_RARITY_BORDER: "list[tuple[str, str]]" = [
    ("Normal", "255 255 255"),
    ("Magic",  "0 75 255"),
    ("Rare",   "255 255 0"),
]


# Wreckers L936~977 Levelling Help + Sanavi 사운드 (5Link.mp3 / ProbPickUp.mp3)
# 빌드 무관 범용 — 캠페인 AL<=67 레벨링 중 링크/화이트 소켓 자원 자동 강조.


def _weapon_1h_cond_for(game: str) -> Optional[str]:
    """'Class "..." "..."' (== 없는 느슨한 match). 매핑 결과 비면 None."""
    cls = _map_poe1_classes(_POE1_WEAPON_1H, game)
    if not cls:
        return None
    return "Class " + _join_classes_quoted(cls)


def _weapon_2h_cond_for(game: str) -> Optional[str]:
    cls = _map_poe1_classes(_POE1_WEAPON_2H, game)
    if not cls:
        return None
    return "Class " + _join_classes_quoted(cls)


def _armor_4slot_classes_for(game: str) -> str:
    """'Class == "..." "..."' 용 클래스 문자열 (Class == prefix 없음). POE1/POE2 공통."""
    return _join_classes_quoted(_map_poe1_classes(_POE1_ARMOR_4SLOT, game))


def _leveling_help_blocks(game: str = "poe1") -> list[str]:
    """Wreckers L936 Levelling Help + Sanavi CustomAlertSound 이식.

    캠페인 AL<=67 전용. 링크/화이트 소켓 장비를 빌드 무관으로 강조 —
    4-링크 전환, Tabula 준비, 빌드 변경 유연성.
    전부 Continue=False (최종 Show, L11 blanket 방어).
    """
    blocks: list[str] = []
    weapon_1h_cond = _weapon_1h_cond_for(game)
    weapon_2h_cond = _weapon_2h_cond_for(game)
    armor_4slot_classes = _armor_4slot_classes_for(game)

    # 3-link 초반 (AL<=25) — Cyan Temp decoration
    blocks.append(make_layer_block(
        LAYER_RE_SHOW,
        "Levelling 3-link any (AL<=25)",
        conditions=["LinkedSockets >= 3", "AreaLevel <= 25"],
        style=LayerStyle(font=36, border="0 120 120",
                         effect="Grey Temp"),
        continue_=False,
        category_tag="lvl_3link_early",
    ))

    # 3-link 무기 (AL<=67) — 1h weapons only. POE2 에서 매핑 결과 비면 skip.
    if weapon_1h_cond is not None:
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            "Levelling 3-link 무기 1h (AL<=67)",
            conditions=[weapon_1h_cond, "LinkedSockets >= 3",
                        "AreaLevel <= 67"],
            style=LayerStyle(font=38, border="0 120 120",
                             effect="Grey Temp"),
            continue_=False,
            category_tag="lvl_3link_weapon",
        ))

    # 4-link 장비 (AL<=67) — any class, Blue border
    blocks.append(make_layer_block(
        LAYER_RE_SHOW,
        "Levelling 4-link 장비 (AL<=67)",
        conditions=["LinkedSockets >= 4", "AreaLevel <= 67"],
        style=LayerStyle(font=42, border="0 140 240",
                         bg="20 20 0 255", effect="Grey",
                         icon="2 Grey Diamond"),
        continue_=False,
        category_tag="lvl_4link",
    ))

    # 5-link 레벨링 (AL<=67) — Sanavi 5Link.mp3
    blocks.append(make_layer_block(
        LAYER_RE_SHOW,
        "Levelling 5-link (AL<=67, Sanavi 5Link.mp3)",
        conditions=["LinkedSockets >= 5", "AreaLevel <= 67"],
        style=LayerStyle(
            font=45, text="0 240 190", border="0 240 190",
            bg="20 20 0 255", effect="Yellow",
            icon="1 Yellow Diamond",
            custom_sound=("5Link.mp3", 300),
        ),
        continue_=False,
        category_tag="lvl_5link",
    ))

    # 3x White 무기 1h (AL<79) — 4-링크 준비용. POE2 에서 매핑 결과 비면 skip.
    if weapon_1h_cond is not None:
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            "Levelling 3x White 무기 1h (AL<79, 화이트 소켓 자원)",
            conditions=[weapon_1h_cond, "Sockets >= 3WWW",
                        "AreaLevel < 79"],
            style=LayerStyle(font=36, border="0 240 190",
                             effect="Blue Temp"),
            continue_=False,
            category_tag="lvl_3ww_weapon",
        ))

    # 4x White 방어구 (helm/glove/boot/body) — built-in sound 1
    blocks.append(make_layer_block(
        LAYER_RE_SHOW,
        f"Levelling 4x White 방어구 ({armor_4slot_classes.count(chr(34)) // 2}종 class)",
        conditions=[f"Class == {armor_4slot_classes}",
                    "Sockets >= 4WWWW"],
        style=LayerStyle(font=42, border="0 240 190",
                         bg="0 75 30 255", effect="Blue",
                         icon="1 Blue Square", sound="1 300"),
        continue_=False,
        category_tag="lvl_4ww_armor",
    ))

    # 6x White 2h 무기 — Sanavi ProbPickUp.mp3 (귀중). POE2 에서 매핑 결과 비면 skip.
    if weapon_2h_cond is not None:
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            "Levelling 6x White 2h 무기 (Sanavi ProbPickUp.mp3)",
            conditions=[weapon_2h_cond, "Sockets >= 6WWWWWW"],
            style=LayerStyle(
                font=45, text="0 240 190", border="0 240 190",
                bg="0 75 30 255", effect="Blue",
                icon="0 Blue Diamond",
                custom_sound=("ProbPickUp.mp3", 300),
            ),
            continue_=False,
            category_tag="lvl_6ww_2h",
        ))

    return blocks


def _unconditional_re_show_blocks(game: str = "poe1") -> list[str]:
    """Wreckers L172/L237 T1 보더 + L936 Levelling Help 재Show — build_data 무관.

    POE1: T1 보더 7 카테고리 × 3 Rarity = 21 블록 + Levelling Help 7 블록.
    POE2: T1 보더 2 카테고리 (ring_glove_helm/main_equip) × 3 Rarity = 6 블록 +
          Levelling Help 중 무기 관련은 매핑 결과에 따라 일부 skip.
    전부 Continue=False (최종 Show).
    """
    blocks: list[str] = []
    for tag_base, base_conds, ilvl, comment_prefix in _t1_reshow_groups_for(game):
        for rarity, border in _T1_RESHOW_RARITY_BORDER:
            blocks.append(make_layer_block(
                LAYER_RE_SHOW,
                f"{comment_prefix} ({rarity}, ilvl>={ilvl})",
                conditions=[
                    f"Rarity {rarity}",
                    *base_conds,
                    f"ItemLevel >= {ilvl}",
                ],
                style=LayerStyle(border=border, font=42),
                continue_=False,
                category_tag=f"{tag_base}_{rarity.lower()}",
            ))
    # Levelling help — T1 뒤에 위치 (T1이 ilvl>=75~86 endgame, lvl help는 AL<=67 campaign → 겹침 없음)
    blocks.extend(_leveling_help_blocks(game))
    return blocks


def layer_re_show(
    build_data: "Optional[dict | list[dict]]" = None,
    coaching_data: Optional[dict] = None,
    game: str = "poe1",
) -> str:
    """L10 Re-Show — Unconditional T1 보더 재Show + 빌드 타겟 재Show.

    Unconditional 블록 (build_data 무관, 항상 실행):
      Wreckers L172/L237 T1 보더 21개 (Ring/Glove/Helmet 85, 메인 86, Trinket/Heist 83,
      Flask/Brooch 84, Utility/Tincture 85, Cluster Small 75 / Large 84).

    빌드 타겟 블록 (build_data 있을 때만): chanceable/base/skill/support/unique_target/all_gems.
    다중 POB 입력은 union (RE_SHOW는 AL 분기 불필요).
    """
    blocks: list[str] = _unconditional_re_show_blocks(game)

    if not build_data:
        return "".join(blocks)

    from build_extractor import merge_build_stages

    builds = build_data if isinstance(build_data, list) else [build_data]
    # RE_SHOW는 항상 union (no_staging=True 강제)
    stages = merge_build_stages(builds, coaching_data, no_staging=True)
    if not stages:
        return ""
    # union이므로 1개 stage만 옴
    stage = stages[0]
    chanceable = stage.chanceable
    bases = stage.bases
    skills = stage.skills
    supports = stage.supports
    unique_bases = stage.unique_bases

    # `blocks`는 이미 unconditional T1 보더로 초기화됨 — 빌드 블록 append

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

    # 빌드 타겟 젬 재Show (Cyan Hexagon 최종) — L9 Rarity Normal blanket hide로부터 방어
    # Wreckers 관례 복사: 우선 빌드 젬 구체 매칭 Show, 이후 generic Class "Gem" Show로 fallback
    if skills:
        names = " ".join(f'"{g}"' for g in skills)
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"빌드 스킬 젬 재Show ({len(skills)}종)",
            conditions=['Class == "Skill Gems"', f"BaseType == {names}"],
            style=_reshow_style("0 Cyan Hexagon", font=40),
            continue_=False,
            category_tag="skill_gem",
        ))
    if supports:
        names = " ".join(f'"{s}"' for s in supports)
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"빌드 서포트 젬 재Show ({len(supports)}종)",
            conditions=['Class == "Support Gems"', f"BaseType == {names}"],
            style=_reshow_style("1 Cyan Hexagon", font=36),
            continue_=False,
            category_tag="support_gem",
        ))

    # 빌드 유니크 base 재Show (L8 unique 티어가 빌드 Cyan을 덮어쓰는 것 방어)
    if unique_bases:
        quoted = " ".join(f'"{b}"' for b in unique_bases)
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"빌드 유니크 base 재Show ({len(unique_bases)}종, L8 unique 방어)",
            conditions=["Rarity Unique", f"BaseType == {quoted}"],
            style=_reshow_style("0 Cyan Star", font=45),
            continue_=False,
            category_tag="unique_target",
        ))

    # 빌드 Rare 장비 베이스 재Show (L8 endgame_rare 덮어쓰기 방어)
    if bases:
        names = " ".join(f'"{b}"' for b in bases)
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"빌드 Rare base 재Show ({len(bases)}종, L8 endgame_rare 방어)",
            conditions=["Rarity Rare", f"BaseType == {names}", "ItemLevel >= 75"],
            style=_reshow_style("1 Cyan Square", font=40),
            continue_=False,
            category_tag="base_rare_target",
        ))

        # 액트 감정 후보 재Show — AL<68 + 모든 Rarity, L9 level_mid Hide 방어.
        # Magenta 강조 (L7 base_act_identify 대응 final Show).
        _MAGENTA = "255 100 200"
        blocks.append(make_layer_block(
            LAYER_RE_SHOW,
            f"빌드 베이스 액트 감정 재Show ({len(bases)}종, L9 level_mid 방어)",
            conditions=[
                "Rarity Normal Magic Rare",
                f"BaseType == {names}",
                "AreaLevel < 68",
            ],
            style=LayerStyle(
                text=_MAGENTA, border=_MAGENTA,
                bg="60 20 40 240",
                font=42,
                effect="Pink",
                icon="0 Pink Diamond",
            ),
            continue_=False,
            category_tag="base_act_identify",
        ))

    # weapon_phys_proxy 재Show — L7 weapon_phys_proxy는 Continue=True라서 L9
    # progressive_hide(Rarity Rare AL>=N)에 매칭돼 Hide됨. L10에서 복권해야
    # T1/T2 phys mod 무기가 실제로 보임. NeverSink도 동일 패턴 (weapon_phys는
    # [[0600]] + [[0900]] 두 층으로 Show 확정).
    weapon_classes = stage.weapon_classes
    if weapon_classes:
        tiers = _load_weapon_mod_tiers()
        required = tiers.get("required_any_mod") or []
        counted = tiers.get("counted_good_mods") or []
        excluded = tiers.get("excluded_bad_mods") or []
        if required and counted and excluded:
            # L10은 strictness 구분 없이 mod count >= 2 (가장 관대) — L9에서
            # 살아남아야 하는 아이템이므로 가능한 넓게 복권.
            drop_level_min = tiers.get("drop_level_min", 5)
            cls_quoted = " ".join(f'"{c}"' for c in weapon_classes)
            required_quoted = " ".join(f'"{m}"' for m in required)
            counted_quoted = " ".join(f'"{m}"' for m in counted)
            excluded_quoted = " ".join(f'"{m}"' for m in excluded)
            blocks.append(make_layer_block(
                LAYER_RE_SHOW,
                f"빌드 무기 phys 프록시 재Show ({len(weapon_classes)} class, L9 Hide 방어)",
                conditions=[
                    "Identified True",
                    f"DropLevel >= {drop_level_min}",
                    "Rarity Rare",
                    f"Class == {cls_quoted}",
                    f"HasExplicitMod {required_quoted}",
                    f"HasExplicitMod >= 2 {counted_quoted}",
                    f"HasExplicitMod = 0 {excluded_quoted}",
                ],
                style=LayerStyle(
                    text=_RESHOW_CYAN_TEXT,
                    border=_RESHOW_CYAN_TEXT,
                    bg=_RESHOW_CYAN_BG,
                    font=43,
                    effect="Cyan",
                    icon="0 Cyan Star",
                ),
                continue_=False,
                category_tag="weapon_phys_proxy",
            ))

    # Generic 모든 젬 재Show — Wreckers "Show Class Gem" pattern
    # L9의 Rarity Normal/Magic blanket hide를 뚫고 비빌드 젬도 Show로 확정
    blocks.append(make_layer_block(
        LAYER_RE_SHOW,
        "모든 젬 재Show (Rarity Normal/Magic blanket hide 방어)",
        conditions=['Class "Gem"'],
        style=LayerStyle(),  # 이전 레이어 스타일 유지 (L2 default 등)
        continue_=False,
        category_tag="all_gems",
    ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# L11: Endgame Rare Hide (Cobalt Strict [[2000]]/[[2200]]/[[2700]])
# ---------------------------------------------------------------------------
#
# RE_SHOW 이후 남은 레어/매직/노말 장비를 맵핑 구간(AL>=68)에서 단계적으로 숨김.
# - [[2000]] 부패·미러 unidentified no-implicit 레어
# - [[2200]] DropLevel 기반 레어 Hide (AL 73/78/80 + DropLevel<40/50/60)
# - [[2700]] 엔드게임 Normal/Magic/Rare 장비 blanket Hide
#
# 모든 블록 action=Hide, continue=False → 최종 결정. L12 REST_EX는 아직 미구현.

# [[2200]] droplevel 는 POE1/POE2 공히 Body Armours/Boots/Gloves/Helmets 4-slot.
# [[2700]] Normal/Magic blanket 은 Cobalt L4223 기반이되 Utility Flasks 제외.
#   이유: Wreckers L232 "Always Show Class Flask Tincture..." 철학. L8 layer_flasks_quality
#   (Utility Flask Magic Continue=True 데코) 덮어쓰기 회귀 방지.
# [[2000]] no-implicit 부패/미러 블록은 Amulets/Belts/Rings 제외 (Cobalt Strict L3483)
#   이유: [[2100]] Amulets/Rings/Belts 별도 Show가 해당 카테고리의 hide 책임.


def layer_endgame_rare_hide(mode: str = "ssf", game: str = "poe1") -> str:
    """L11 Endgame Rare Hide — Cobalt Strict [[2000]]/[[2200]]/[[2700]].

    모드 무관 동일 규칙. mode 인자는 다른 layer 시그니처와 통일을 위한 것.
    game="poe2": Class 목록은 poe1_to_poe2 매핑 (Shields+Bucklers, Warstaves→Quarterstaves,
                 Claws/Daggers/One Hand Axes 등 제거).
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")

    noimpl_classes = _endgame_rare_noimpl_for(game)
    droplevel_classes = _droplevel_hide_for(game)
    normalmagic_classes = _endgame_rare_equip_for(game)

    hide_style = LayerStyle(
        font=18,
        border="0 0 0 0",
        bg="20 20 0 0",
        disable_drop=True,
    )

    blocks: list[str] = []

    # [[2000]] Corrupted unidentified no-implicit rares
    blocks.append(make_layer_block(
        LAYER_ENDGAME_RARE,
        "[[2000]] 부패 unidentified 레어 (임플리싯 없음)",
        conditions=[
            "Corrupted True",
            "Identified False",
            "CorruptedMods 0",
            "ItemLevel >= 68",
            "Rarity Rare",
            f"Class == {noimpl_classes}",
        ],
        style=hide_style,
        action="Hide",
        continue_=False,
        category_tag="corrupted_noimpl",
    ))

    # [[2000]] Mirrored unidentified no-implicit rares
    blocks.append(make_layer_block(
        LAYER_ENDGAME_RARE,
        "[[2000]] 미러 unidentified 레어 (임플리싯 없음)",
        conditions=[
            "Mirrored True",
            "Identified False",
            "CorruptedMods 0",
            "ItemLevel >= 68",
            "Rarity Rare",
            f"Class == {noimpl_classes}",
        ],
        style=hide_style,
        action="Hide",
        continue_=False,
        category_tag="mirrored_noimpl",
    ))

    # [[2200]] Droplevel hiding — AL 73/78/80 threshold
    for al, drop_level in ((80, 60), (78, 50), (73, 40)):
        blocks.append(make_layer_block(
            LAYER_ENDGAME_RARE,
            f"[[2200]] AL>={al} DropLevel<{drop_level} 레어 Hide",
            conditions=[
                "ItemLevel >= 68",
                f"DropLevel < {drop_level}",
                "Rarity Rare",
                f"Class == {droplevel_classes}",
                f"AreaLevel >= {al}",
            ],
            style=hide_style,
            action="Hide",
            continue_=False,
            category_tag=f"droplevel_al{al}",
        ))

    # [[2700]] raresendgame blanket Hide는 **의도적으로 제외**.
    # 이유: Cobalt의 blanket Rare Hide는 first-match 전제 (상위 Show 블록이 non-Continue).
    # 우리 β는 Continue 캐스케이드 — L6 T1_BORDER / L8 layer_endgame_rare /
    # L7 BUILD_TARGET 모두 Continue=True 데코레이션이라 L11 blanket이 전부 덮어씀.
    # 결과: T1 크래프팅 베이스/Sized Rare/부패 임플리싯 등 valuable 레어 숨김.
    # Wreckers SSF 원본도 blanket Rare Hide 없음 (AL 기반 Normal/Magic hide만 존재).
    # droplevel + normalmagic_blanket + noimpl 3축만으로 맵핑 정크 다수 제거 가능.

    # [[2700]] Normal/Magic 장비 blanket Hide는 유지 — T1 크래프팅 Normal/Magic 베이스
    # (L6가 ilvl>=86 Rare에만 반응)와 조건 중첩 없음. AreaLevel>=68 전제로 안전.
    blocks.append(make_layer_block(
        LAYER_ENDGAME_RARE,
        "[[2700]] 엔드게임 Normal/Magic 장비 blanket Hide",
        conditions=[
            "Rarity Normal Magic",
            f"Class == {normalmagic_classes}",
            "AreaLevel >= 68",
        ],
        style=hide_style,
        action="Hide",
        continue_=False,
        category_tag="normalmagic_blanket",
    ))

    return "".join(blocks)


# ---------------------------------------------------------------------------
# β 오버레이 조립
# ---------------------------------------------------------------------------

_BETA_HEADER = """#===============================================================================================================
# PathcraftAI β Continue Chain Filter
# Arch: continue (Wreckers-style cascading layers)
# Layer order: 0 HARD_HIDE → 1 CATCH_ALL → 2 DEFAULT_RARITY → 3 SOCKET → 4 SPECIAL_BASE → 5 CORRUPT → 6 T1 → 7 BUILD → 8 CATEGORY → 9 PROG_HIDE → 10 RE_SHOW → 11 ENDGAME_RARE_HIDE
#===============================================================================================================

"""


def generate_beta_overlay(
    strictness: int = 3,
    build_data: "Optional[dict | list[dict]]" = None,
    coaching_data: Optional[dict] = None,
    stage: bool = False,
    mode: str = "ssf",
    al_split: int = 67,
    game: str = "poe1",
) -> str:
    """β 아키텍처 오버레이 생성. L0~L10 전 레이어.

    - build_data=dict → 단일 POB
    - build_data=list[dict] → 다중 POB (기본 union, stage=True면 uniques+chanceable AL 분기)
    - mode: trade|ssf|hcssf — L8 SSF 카테고리(Lifeforce/Splinter/Scarabs) 티어링 기준
    - al_split: 2-POB stage의 레벨링→엔드게임 전환 AL (기본 67 = Kitava 후)
    - game: "poe1"|"poe2" — ItemClass 매핑. POE2 는 data/item_class_map_poe2.json 사용.
    """
    if game not in ("poe1", "poe2"):
        raise ValueError(f"game must be poe1|poe2, got {game!r}")
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be in {VALID_MODES}, got {mode!r}")
    parts: list[str] = [_BETA_HEADER]
    parts.append(layer_hard_hide())
    parts.append(layer_catch_all())
    parts.append(layer_default_rarity())
    parts.append(layer_socket_border())
    parts.append(layer_special_base())
    parts.append(layer_corrupt_border())
    parts.append(layer_t1_border())
    parts.append(layer_build_target(
        build_data, coaching_data, stage=stage, al_split=al_split, strictness=strictness,
    ))
    parts.append(layer_currency(mode=mode))
    parts.append(layer_maps())
    parts.append(layer_divcards(mode=mode))
    # L8 SSF 카테고리 (GGPK 기반)
    parts.append(layer_lifeforce(mode=mode))
    parts.append(layer_splinters(mode=mode))
    parts.append(layer_scarabs(mode=mode))
    parts.append(layer_gems_quality(mode=mode))
    parts.append(layer_map_fragments(mode=mode))
    parts.append(layer_endgame_content(mode=mode))
    parts.append(layer_atlas_and_memory(mode=mode))
    parts.append(layer_stacked_currency(mode=mode))
    parts.append(layer_ssf_currency_extras(mode=mode))
    parts.append(layer_endgame_rare(mode=mode, game=game))
    parts.append(layer_uniques(mode=mode))
    parts.append(layer_gold(mode=mode))
    parts.append(layer_flasks_quality(mode=mode))
    parts.append(layer_heist(mode=mode))
    parts.append(layer_quest_items(mode=mode))
    parts.append(layer_special_maps(mode=mode))
    parts.append(layer_jewels(mode=mode))
    parts.append(layer_special_uniques(mode=mode))
    parts.append(layer_influenced_extra(mode=mode))
    parts.append(layer_special_modifiers(mode=mode))
    parts.append(layer_hcssf_safety(mode=mode))
    parts.append(layer_id_mod_filtering(mode=mode, strictness=strictness))
    parts.append(layer_leveling_supplies(mode=mode))
    parts.append(layer_basic_orbs(mode=mode))
    parts.append(layer_progressive_hide(strictness, mode=mode, game=game))
    parts.append(layer_re_show(build_data, coaching_data, game=game))
    parts.append(layer_endgame_rare_hide(mode=mode, game=game))
    return "".join(parts)
