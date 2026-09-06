"""Generate a Show-only build-highlight overlay on top of NeverSink's POE2 filter.

Usage:
    python scripts/build_poe2_build_overlay.py \
        --base <NeverSink .filter> \
        --spec data/filter_build_targets/<build>.json \
        --out <output .filter> [--stage campaign|maps|endgame] [--install-dir <dir>]

Stages:
  A spec rule may declare "stages" -- which progression stages it belongs to.
  Under --stage, a rule that declares stages and does not list the requested one
  is left out, so the campaign file is not polluted by endgame-only crafting
  materials and the endgame file is not polluted by levelling bases. A rule with
  no "stages" key counts as all-stages. Without --stage every rule is emitted.

Safety model. Every failure mode of a loot filter is silent -- the only symptom
is an item that never appears on screen -- so each one gets a gate that fails the
build rather than a warning nobody reads:

  * Vocabulary gate: a BaseType/Class must appear as a *quoted token* in the base
    filter or as a real base name in data/base_items_poe2.json. A raw substring
    test is not enough: "Club" is a substring of "Spiked Club" and would sail
    through while matching nothing in game.
  * Exact-match default: BaseType is emitted with `==`. Substring matching is
    opt-in per rule, because `BaseType "Exalted Orb"` silently swallows
    "Perfect Exalted Orb", and `"Sapphire"` swallows "Sapphire Ring",
    "Sapphire Charm" and "Time-Lost Sapphire".
  * Loudness gate: the overlay is prepended, so first-match-wins means every
    block we emit *replaces* whatever NeverSink would have said. If NeverSink
    shouted and we whisper, we have made the filter worse. Each emitted block is
    raised to at least the base's font size, alert volume and minimap icon size
    for the items it captures -- splitting a rule into several blocks when its
    items need different volumes, so one apex item does not drag its siblings up.
  * Contrast gate: text vs background relative-luminance difference must clear a
    fixed threshold, so no label can render unreadable.
  * Value gate: font sizes, sound ids, volumes, beam colours, minimap shapes and
    colours must all be values the base filter itself uses. The game silently
    ignores a directive it cannot parse.
  * Show-only: the overlay cannot hide anything; unmatched items fall through to
    NeverSink's own rules.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("build-overlay")

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_ITEMS = REPO_ROOT / "data" / "base_items_poe2.json"

CONTRAST_MIN = 0.35  # relative luminance gap; POE1 cascade-gate lesson, lightweight port
ALL_RARITIES = ("Normal", "Magic", "Rare", "Unique")

QUOTED = re.compile(r'"([^"]+)"')

# Conditions a rule of ours can also express. A base block using only these
# matches whenever our block matches, so it is a fair loudness comparison. A
# block with any other condition (Quality, Sockets, ItemLevel, AreaLevel,
# Corrupted, StackSize, ...) is a narrower special case: it may or may not fire
# on the same item, so raising our whole rule to its volume is wrong.
COMPARABLE_CONDITIONS = frozenset({"BaseType", "Class", "Rarity"})

# `Corrupted False` and friends only *remove* items from a block. The block still
# fires on most of what our rule matches, so being quieter than it is a real
# regression -- while being louder on the excluded remainder (a corrupted drop)
# costs nothing. NeverSink L401 (2-socket one-hand mace, font 42 / volume 300)
# reaches the guide's own craft base only through this path.
NARROWING_FLAGS = frozenset({"Corrupted", "Mirrored", "Identified", "Replica", "Scourged"})


def repo_relative(path: Path) -> str:
    """Render a path for the regenerate hint.

    The hint has to be identical no matter which directory the build was run
    from, otherwise two byte-identical filters compare unequal and the
    reproducibility check becomes noise. Paths outside the repo keep their
    absolute form, which is the honest answer for an external base filter.
    """
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


# --------------------------------------------------------------------------- #
# base filter parsing
# --------------------------------------------------------------------------- #


class BaseBlock:
    """One Show block of the base filter, reduced to what the gates need."""

    __slots__ = (
        "base_types", "classes", "rarities", "font", "volume",
        "icon_size", "line", "extra", "sockets_min", "item_level_min", "quality_min",
    )

    def __init__(self) -> None:
        self.base_types: set[str] = set()
        self.classes: set[str] = set()
        self.rarities: set[str] = set(ALL_RARITIES)
        self.font: int = 32
        self.volume: int = 0
        self.icon_size: int | None = None
        self.line: int = 0
        self.extra: set[str] = set()  # conditions we cannot express -> narrower than us
        self.sockets_min: int = 0  # from `Sockets >= n`
        self.item_level_min: int = 0  # from `ItemLevel >= n`
        self.quality_min: int = 0  # from `Quality >= n` -- NeverSink's chancing tier


def parse_base_blocks(text: str) -> list[BaseBlock]:
    """Split the base filter into Show blocks.

    A block runs from its `Show`/`Hide` header to the next blank line -- cutting
    on indentation fails on this file, a lesson already paid for in the POE1
    cascade work.
    """
    blocks: list[BaseBlock] = []
    current: BaseBlock | None = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            if current is not None:
                blocks.append(current)
                current = None
            continue
        if line.startswith("Show"):
            current = BaseBlock()
            current.line = lineno
            continue
        if line.startswith("Hide"):
            current = None  # a Hide block emits no alert, so it cannot be "louder"
            continue
        if current is None or line.startswith("#"):
            continue
        keyword = line.split()[0]
        if keyword.startswith("Set") or keyword.startswith("Play") or keyword in {
            "MinimapIcon", "CustomAlertSound", "DisableDropSound", "EnableDropSound", "Continue",
        }:
            pass  # an action, not a condition
        elif keyword == "Sockets" and re.match(r"^Sockets\s*>=\s*\d+$", line):
            current.sockets_min = int(line.split(">=")[1])
        elif keyword == "ItemLevel" and re.match(r"^ItemLevel\s*>=\s*\d+$", line):
            current.item_level_min = int(line.split(">=")[1])
        elif keyword == "Quality" and re.match(r"^Quality\s*>=\s*\d+$", line):
            current.quality_min = int(line.split(">=")[1])
        elif keyword in NARROWING_FLAGS and line.split()[-1] == "False":
            pass  # excludes items from the block; the rest of our scope still lands in it
        elif keyword not in COMPARABLE_CONDITIONS:
            current.extra.add(keyword)

        if line.startswith("BaseType"):
            current.base_types |= set(QUOTED.findall(line))
        elif line.startswith("Class"):
            current.classes |= set(QUOTED.findall(line))
        elif line.startswith("Rarity"):
            named = {r for r in ALL_RARITIES if re.search(rf"\b{r}\b", line)}
            if named and not re.search(r"[<>]", line):
                current.rarities = named
        elif line.startswith("SetFontSize"):
            current.font = int(line.split()[1])
        elif line.startswith("PlayAlertSound"):
            parts = line.split()
            current.volume = int(parts[2]) if len(parts) > 2 else 100
        elif line.startswith("MinimapIcon"):
            current.icon_size = int(line.split()[1])
    if current is not None:
        blocks.append(current)
    return blocks


def base_vocabulary(text: str) -> set[str]:
    """Every quoted token the base filter uses on a BaseType/Class line."""
    vocab: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(("BaseType", "Class")):
            vocab |= set(QUOTED.findall(line))
    return vocab


def game_base_names() -> set[str]:
    """Real base names from the repo's GGPK-derived base item table.

    NeverSink does not name every base in the game -- `Brigand Mace` is a real
    PoE2 base its filter never mentions -- so gating on the base filter alone
    would reject an item a build guide explicitly asks for.
    """
    if not BASE_ITEMS.exists():
        log.warning("%s missing -- vocabulary gate falls back to the base filter alone", BASE_ITEMS.name)
        return set()
    data = json.loads(BASE_ITEMS.read_text(encoding="utf-8"))
    names: set[str] = set()
    for group in ("weapons", "armours", "other"):
        for entries in data.get(group, {}).values():
            if isinstance(entries, list):
                names |= {e["name"] for e in entries if isinstance(e, dict) and e.get("name")}
    return names


GAME_CLASS_TO_FILTER_CLASS = {
    "OneHandMaces": "One Hand Maces", "TwoHandMaces": "Two Hand Maces",
    "OneHandAxes": "One Hand Axes", "TwoHandAxes": "Two Hand Axes",
    "OneHandSwords": "One Hand Swords", "TwoHandSwords": "Two Hand Swords",
    "Bows": "Bows", "Crossbows": "Crossbows", "Claws": "Claws", "Daggers": "Daggers",
    "Spears": "Spears", "Flail": "Flails", "Quivers": "Quivers",
    "Staves": "Quarterstaves",  # GGPK 'Weapons/TwoHandWeapons/Staves' 는 전부 쿼터스태프다.
    # 캐스터용 지팡이는 `Metadata/Items/Staves/` 라 Weapons 트리 밖에 산다. 한때
    # base_items_poe2.json 에 아예 없어서 NeverSink 가 안 쓰는 이름(Spriggan·Dark Staff)이
    # 어휘 게이트에 걸려 조용히 떨어졌다. 생성기가 이제 CasterStaves 로 담는다.
    "CasterStaves": "Staves",
    "BodyArmours": "Body Armours", "Boots": "Boots", "Gloves": "Gloves",
    "Helmets": "Helmets", "Shields": "Shields", "Focus": "Foci",
    "Amulets": "Amulets", "Belts": "Belts", "Rings": "Rings",
    "Jewels": "Jewels", "Charms": "Charms",
    # 필터는 `Life Flasks` / `Mana Flasks` 를 따로 쓴다. 한때 둘을 `Flasks` 한 덩어리로
    # 매핑해서 시뮬레이터가 플라스크 클래스를 틀리게 잡고 엉뚱한 블록을 평가했다.
    "LifeFlasks": "Life Flasks", "ManaFlasks": "Mana Flasks",
}


def class_index(text: str) -> dict[str, str]:
    """base name -> filter Class, from the base filter first, then game data.

    Needed because NeverSink's loudest gear rules are Class-only: they never name
    a BaseType, so without this a rule about `Brigand Mace` cannot tell that
    `Class == "One Hand Maces"` covers it.
    """
    index: dict[str, str] = {}
    blocks_classes: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(("Show", "Hide")):
            blocks_classes = None
        elif line.startswith("Class"):
            found = QUOTED.findall(line)
            blocks_classes = found[0] if len(found) == 1 else None
        elif line.startswith("BaseType") and blocks_classes:
            for name in QUOTED.findall(line):
                index.setdefault(name, blocks_classes)
    if BASE_ITEMS.exists():
        data = json.loads(BASE_ITEMS.read_text(encoding="utf-8"))
        for group in ("weapons", "armours", "other"):
            for game_class, entries in data.get(group, {}).items():
                filter_class = GAME_CLASS_TO_FILTER_CLASS.get(game_class)
                if not filter_class or not isinstance(entries, list):
                    continue
                for entry in entries:
                    if isinstance(entry, dict) and entry.get("name"):
                        index.setdefault(entry["name"], filter_class)
    return index


def base_value_vocabulary(text: str) -> dict[str, set]:
    """Directive values the base filter itself uses -- our allowed range."""
    found: dict[str, set] = {
        "font": set(), "sound_id": set(), "volume": set(), "beam": set(),
        "icon_size": set(), "icon_color": set(), "icon_shape": set(),
    }
    for raw in text.splitlines():
        line = raw.strip()
        parts = line.split()
        try:
            if line.startswith("SetFontSize"):
                found["font"].add(int(parts[1]))
            elif line.startswith("PlayAlertSound"):
                found["sound_id"].add(int(parts[1]))
                if len(parts) > 2:
                    found["volume"].add(int(parts[2]))
            elif line.startswith("PlayEffect"):
                found["beam"].add(parts[1])
                # `PlayEffect <색> Temp` 는 드롭 순간에만 빔이 뜬다. 베이스가 52번
                # 쓰는 형태인데 색만 기록하면 우리가 쓰려 할 때 값 게이트가 막는다.
                if len(parts) > 2 and parts[2] == "Temp":
                    found["beam"].add(f"{parts[1]} Temp")
            elif line.startswith("MinimapIcon"):
                found["icon_size"].add(int(parts[1]))
                found["icon_color"].add(parts[2])
                found["icon_shape"].add(parts[3])
        except (IndexError, ValueError):
            continue  # a directive shape we do not model; the base is not ours to police
    return found


# --------------------------------------------------------------------------- #
# gates
# --------------------------------------------------------------------------- #


def luminance(rgb: list[int]) -> float:
    r, g, b = (c / 255.0 for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def check_contrast(style_name: str, style: dict) -> None:
    gap = abs(luminance(style["text"]) - luminance(style["background"]))
    if gap < CONTRAST_MIN:
        raise SystemExit(
            f"contrast gate FAIL: style '{style_name}' text/background gap {gap:.2f} < {CONTRAST_MIN}"
        )


# GGG 공식 아이템 필터 문서(pathofexile.com/item-filter/about, 2026-09-04 확인)의
# 열거값. 베이스 필터가 안 쓰는 값이라도 게임은 받는다 — 베이스는 합법성의 대리
# 지표일 뿐 권위가 아니다. 여기 없는 값은 여전히 게이트에서 죽는다.
_BEAM_COLOURS = {"Red", "Green", "Blue", "Brown", "White", "Yellow",
                 "Cyan", "Grey", "Orange", "Pink", "Purple"}
OFFICIAL_VALUES: dict[str, set] = {
    # PlayEffect: 색 단독, 또는 "색 Temp"(드롭 순간에만 빔)
    "beam": _BEAM_COLOURS | {f"{c} Temp" for c in _BEAM_COLOURS},
    "icon_color": _BEAM_COLOURS,
    "icon_shape": {"Circle", "Diamond", "Hexagon", "Square", "Star", "Triangle",
                   "Cross", "Moon", "Raindrop", "Kite", "Pentagon", "UpsideDownHouse"},
    "icon_size": {0, 1, 2, -1},
    "sound_id": set(range(1, 17)),  # 문서상 1-16
}


def check_style_values(style_name: str, style: dict, allowed: dict[str, set]) -> None:
    """Reject values the game would ignore.

    Two different kinds of field, so two different checks: font size and volume
    are continuous, and the base filter happening to use only 100 and 300 says
    nothing about what is legal, so those get a range. Beam colour, minimap
    shape and the rest are enumerations the client either knows or does not.

    For the enumerations the base filter is a *proxy* for legality, not the
    authority. GGG publishes the real lists, so a value the official docs allow
    passes even when NeverSink never happens to use it -- `Raindrop` is a legal
    minimap shape that NeverSink's POE2 filter does not use, and flasks/charms
    want it. Anything outside both sets still fails.
    """
    ranges = {"font": (1, 45), "volume": (0, 300)}
    for key, value in [
        ("font", style["font"]),
        ("sound_id", style["sound"][0] if style.get("sound") else DEFAULT_SOUND_ID),
        ("volume", style_volume(style)),
        ("beam", style.get("beam")),
        ("icon_size", style_icon_size(style)),
        ("icon_color", style["icon"][1] if style.get("icon") else None),
        ("icon_shape", style["icon"][2] if style.get("icon") else None),
    ]:
        if value is None:
            continue  # 스타일이 그 지시어를 끈 것 — 아예 안 나가므로 검사 대상이 아니다
        if key in ranges:
            low, high = ranges[key]
            if not (low <= value <= high):
                raise SystemExit(
                    f"value gate FAIL: style '{style_name}' {key}={value} outside {low}..{high}"
                )
        elif allowed[key] and value not in allowed[key] | OFFICIAL_VALUES.get(key, set()):
            raise SystemExit(
                f"value gate FAIL: style '{style_name}' {key}={value!r} is not a value the base "
                f"filter or the official docs allow "
                f"(allowed: {sorted(allowed[key] | OFFICIAL_VALUES.get(key, set()))})"
            )


def constrains_us(block: BaseBlock, base_type: str, scope: dict) -> bool:
    """True when every drop our rule matches also matches this base block.

    That is the only sound basis for "NeverSink was louder here". Membership in
    the block's BaseType list is not required -- its loudest gear rules are
    Class-only -- but a condition we do not also impose disqualifies it, because
    then the block may simply not fire on the drop we are colouring.
    """
    names_it = base_type in block.base_types
    if block.base_types and not names_it:
        return False
    if block.classes and not names_it:
        # The block reaches us by class alone, so our class must be inside its set.
        # When the block names the BaseType outright, its Class line is satisfied by
        # construction -- NeverSink would not list a base under a class it cannot be.
        if not scope["classes"] or not scope["classes"] <= block.classes:
            return False
    if not scope["rarities"] <= block.rarities:
        return False
    if block.sockets_min and scope["sockets_min"] < block.sockets_min:
        return False
    if block.item_level_min and scope["item_level_min"] < block.item_level_min:
        return False
    if block.quality_min and scope["quality_min"] < block.quality_min:
        return False
    if block.extra:
        return False
    if not block.base_types and not block.classes:
        return False  # a catch-all block; treating it as our floor is meaningless
    return True


def required_loudness(
    base_type: str, scope: dict, blocks: list[BaseBlock]
) -> tuple[int, int, int | None, list[BaseBlock]]:
    """What the base filter already guarantees for this item: (font, volume, icon).

    The fourth value lists blocks that might fire but are not implied by our
    scope, so the caller can report what the overlay answers ahead of.
    """
    font = volume = 0
    icon: int | None = None
    shadowed: list[BaseBlock] = []
    for block in blocks:
        names_it = base_type in block.base_types
        covers_class = bool(block.classes) and bool(scope["classes"] & block.classes)
        if not names_it and not covers_class:
            continue
        if constrains_us(block, base_type, scope):
            font = max(font, block.font)
            volume = max(volume, block.volume)
            if block.icon_size is not None:
                icon = block.icon_size if icon is None else min(icon, block.icon_size)
        elif block.volume or block.font >= 40:
            shadowed.append(block)
    return font, volume, icon, shadowed


def narrower_louder_blocks(
    base_type: str, scope: dict, blocks: list[BaseBlock], style: dict
) -> list[tuple[frozenset, int, int, int, int | None]]:
    """Blocks that beat our style on a subset of our scope we can still express.

    Returns (rarities, sockets_min, font, volume, icon) for each -- the recipe for
    a variant block. Only Rarity and `Sockets >= n` qualify: they are the two
    narrowings the filter language lets us restate.
    """
    out = []
    for block in blocks:
        if block.extra:
            continue
        if block.base_types and base_type not in block.base_types:
            continue
        if block.classes and base_type not in block.base_types:
            if not (scope["classes"] and scope["classes"] <= block.classes):
                continue
        if not block.base_types and not block.classes:
            continue  # catch-all fallback ("unknown item"); recognising it is not a downgrade
        rarities = scope["rarities"] & block.rarities
        if not rarities:
            continue
        sockets = max(scope["sockets_min"], block.sockets_min)
        item_level = max(scope["item_level_min"], block.item_level_min)
        quality = max(scope["quality_min"], block.quality_min)
        if (block.font, block.volume) <= (style["font"], style_volume(style)):
            continue
        if (
            rarities == scope["rarities"]
            and sockets == scope["sockets_min"]
            and item_level == scope["item_level_min"]
            and quality == scope["quality_min"]
        ):
            continue  # not narrower -- required_loudness already handles it
        out.append(
            (frozenset(rarities), sockets, item_level, quality,
             block.font, block.volume, block.icon_size)
        )
    return out


# --------------------------------------------------------------------------- #
# emission
# --------------------------------------------------------------------------- #


DEFAULT_SOUND_ID = 3  # 스타일이 소리를 끈 상태에서 베이스가 소리를 요구할 때만 쓰인다


def style_volume(style: dict) -> int:
    """스타일이 스스로 요구하는 음량 바닥. 소리를 끈 스타일은 0."""
    return style["sound"][1] if style.get("sound") else 0


def style_icon_size(style: dict) -> int:
    """아이콘을 끈 스타일은 '가장 작은 아이콘'(2)으로 취급해 베이스 요구만 반영한다."""
    return style["icon"][0] if style.get("icon") else 2


def render_block(
    rule: dict, style: dict, base_types: list[str], font: int, volume: int, icon_size: int
) -> str:
    # Rule names contain em dashes, so name and note must be separate comment
    # lines -- one line cannot be split back apart reliably.
    lines = [f"# [overlay] {rule['name']}"]
    if rule.get("note"):
        lines.append(f"#   {rule['note']}")
    lines.append("Show")
    rarities = rule.get("rarity")
    if rarities:
        rarities = rarities if isinstance(rarities, list) else [rarities]
        lines.append("\tRarity " + " ".join(rarities))  # the base never quotes rarity values
    if rule.get("class"):
        classes = rule["class"] if isinstance(rule["class"], list) else [rule["class"]]
        lines.append("\tClass == " + " ".join(f'"{c}"' for c in classes))
    op = "" if rule.get("substring") else "== "
    lines.append("\tBaseType " + op + " ".join(f'"{b}"' for b in base_types))
    if rule.get("sockets_min"):
        lines.append(f"\tSockets >= {int(rule['sockets_min'])}")
    if rule.get("item_level_min"):
        lines.append(f"\tItemLevel >= {int(rule['item_level_min'])}")
    if rule.get("quality_min"):
        lines.append(f"\tQuality >= {int(rule['quality_min'])}")
    if rule.get("area_level_max"):
        lines.append(f"\tAreaLevel <= {int(rule['area_level_max'])}")
    t, bo, bg = style["text"], style["border"], style["background"]
    lines.append(f"\tSetTextColor {t[0]} {t[1]} {t[2]} 255")
    lines.append(f"\tSetBorderColor {bo[0]} {bo[1]} {bo[2]} 255")
    lines.append(f"\tSetBackgroundColor {bg[0]} {bg[1]} {bg[2]} 255")
    lines.append(f"\tSetFontSize {font}")
    # 소리·빔·아이콘은 선택형이다. NeverSink 는 장비 블록의 22~23% 에만 이것들을
    # 붙이는데 우리가 100% 에 붙이면 흔한 드롭까지 전부 경보가 된다(캠페인 455개
    # 상황 중 289개가 베이스는 무음인데 우리만 소리를 냈다). 스타일에서 null 로
    # 끄면, **베이스가 이미 요구하는 경우에만** 다시 켜진다 — 회귀는 그대로 막는다.
    if style.get("sound") is not None or volume > 0:
        sound_id = style["sound"][0] if style.get("sound") else DEFAULT_SOUND_ID
        lines.append(f"\tPlayAlertSound {sound_id} {volume}")
    if style.get("beam"):
        lines.append(f"\tPlayEffect {style['beam']}")
    if style.get("icon"):
        lines.append(f"\tMinimapIcon {icon_size} {style['icon'][1]} {style['icon'][2]}")
    return "\n".join(lines)


def build_rule_blocks(
    rule: dict, style: dict, base_blocks: list[BaseBlock], classes_of: dict[str, str]
) -> tuple[list[str], list[str], list[str]]:
    """Emit one block per loudness class so no item ends up quieter than vanilla."""
    rarities = set(rule.get("rarity") or ALL_RARITIES)
    declared = rule.get("class") or []
    declared = set(declared if isinstance(declared, list) else [declared])
    groups: dict[tuple[int, int, int], list[str]] = {}
    variants: dict[tuple, list[str]] = {}
    raises: list[str] = []
    shadows: list[str] = []
    for base_type in rule["base_types"]:
        # A rule need not declare a Class; resolve the item's own class so
        # Class-only base blocks are still comparable.
        resolved = declared or {classes_of[base_type]} if base_type in classes_of else declared
        scope = {
            "rarities": rarities,
            "classes": resolved,
            "sockets_min": int(rule.get("sockets_min") or 0),
            "item_level_min": int(rule.get("item_level_min") or 0),
            "quality_min": int(rule.get("quality_min") or 0),
        }
        req_font, req_volume, req_icon, shadowed = required_loudness(
            base_type, scope, base_blocks
        )
        for block in shadowed:
            shadows.append(
                f"{base_type}: base L{block.line} (font {block.font}, volume {block.volume}, "
                f"extra conditions {sorted(block.extra)}) is shadowed by this overlay"
            )
        font = max(style["font"], req_font)
        volume = max(style_volume(style), req_volume)
        icon = style_icon_size(style) if req_icon is None else min(style_icon_size(style), req_icon)
        if (font, volume, icon) != (style["font"], style_volume(style), style_icon_size(style)):
            raises.append(
                f"{base_type}: font {style['font']}->{font}, volume {style_volume(style)}->{volume}, "
                f"icon {style_icon_size(style)}->{icon}"
            )
        groups.setdefault((font, volume, icon), []).append(base_type)

        # Distinct names: reusing `rarities`/`sockets` here would rebind the rule
        # scope and every later base type would inherit the last variant's scope.
        for v_rarities, v_sockets, v_ilvl, v_qual, v_font, v_volume, v_icon in (
            narrower_louder_blocks(base_type, scope, base_blocks, style)
        ):
            # 변이의 바닥은 스타일이 아니라 **일반 블록이 확보한 값**이다.
            # 변이는 일반 블록보다 앞에 깔리므로, 일반 블록이 NeverSink 때문에
            # 올려둔 폰트·음량보다 조용하면 그 상향분이 통째로 사라진다.
            # 실제로 그랬다: 진주광 목걸이는 NeverSink 가 Exotic Base 로 음량 300 을
            # 주는데(soft L207), 등급을 {Magic,Normal} 로 좁힌 변이가 스타일 바닥
            # 200 만 쥐고 앞을 막아 회귀 72건이 났다.
            v_font = max(font, v_font)
            v_volume = max(volume, v_volume)
            v_icon = icon if v_icon is None else min(icon, v_icon)
            key = (tuple(sorted(v_rarities)), v_sockets, v_ilvl, v_qual, v_font, v_volume, v_icon)
            variants.setdefault(key, []).append(base_type)

    blocks = []
    # Variants carry extra conditions, so they must precede the general block --
    # first-match-wins would otherwise never reach them.
    #
    # 변이끼리도 순서가 있다. **넓은 것이 좁은 것을 먹는다.** 예전에는 폰트·음량
    # (=시끄러운 순)으로 정렬해서, `Rarity Magic Normal`(폰트 42) 변이가
    # `Rarity Normal + ItemLevel>=82`(폰트 40 · 음량 300) 변이를 통째로 가렸다.
    # 좁은 쪽이 영영 안 걸려 NeverSink 의 시끄러운 경보가 조용해졌다.
    # 어떤 변이 A 가 B 를 가리려면 A 는 모든 축에서 B 보다 넓어야 하므로,
    # (등급 수 오름차순, 나머지 조건 내림차순) = 좁은 것부터가 정확한 순서다.
    for (rarities, sockets, ilvl, qual, v_font, v_volume, v_icon), names in sorted(
        variants.items(),
        key=lambda kv: (len(kv[0][0]), -kv[0][1], -kv[0][2], -kv[0][3], kv[0]),
    ):
        variant_rule = {
            **rule,
            "name": f"{rule['name']} [조건부 상향]",
            "note": (
                f"NeverSink 가 이 구간(등급 {' '.join(rarities)}"
                + (f" · 소켓 {sockets}+" if sockets else "")
                + (f" · 아이템 레벨 {ilvl}+" if ilvl else "")
                + (f" · 퀄리티 {qual}+" if qual else "")
                + f")에 폰트 {v_font} / 음량 {v_volume} 를 준다. 오버레이가 앞서므로 "
                "같은 크기로 맞춘 변이 블록을 먼저 깐다 — 안 그러면 빌드 색을 얻는 대신 "
                "경보가 작아진다"
            ),
            "rarity": list(rarities),
            "sockets_min": sockets or None,
            "item_level_min": ilvl or None,
            "quality_min": qual or None,
        }
        blocks.append(render_block(variant_rule, style, sorted(set(names)), v_font, v_volume, v_icon))

    blocks += [
        render_block(rule, style, sorted(names), font, volume, icon)
        for (font, volume, icon), names in sorted(groups.items())
    ]
    return blocks, raises, shadows


def render_hide_block(rule: dict, spec: dict, vocabulary: set[str]) -> str:
    """Emit one Hide block, with a gate that makes hiding our own gear impossible.

    Hiding is the one thing a build overlay can do that loses information, and the
    symptom of getting it wrong is an item that simply never appears. So the gate
    is mechanical rather than a review note: the rule's Class list is intersected
    with every Class and BaseType the spec's Show rules name, and any overlap kills
    the build. That is not paranoia -- NeverSink's own `hideweaponsbytype` block
    lists "Crossbows" and "Staves", which is exactly what this build wields, so
    enabling it verbatim would have hidden the build's weapons.

    Structure follows NeverSink's disabled `conditionalhiders` (soft L687-L864)
    including its three guards, which exist so a hider never eats something worth
    keeping: `Sockets 0` (no rune slots), `Quality 0` (not a quality base) and
    `UnidentifiedItemTier <= 3` (not a good rare).
    """
    classes = rule.get("class") or []
    classes = classes if isinstance(classes, list) else [classes]
    if not classes:
        raise SystemExit(f"hide gate FAIL: '{rule['name']}' must name at least one Class")

    unknown = [c for c in classes if c not in vocabulary]
    if unknown:
        raise SystemExit(f"hide gate FAIL: '{rule['name']}' names unknown class {unknown}")

    shown_classes: set[str] = set()
    shown_bases: set[str] = set()
    for other in spec["rules"]:
        if other.get("kind") == "hide":
            continue
        oc = other.get("class") or []
        shown_classes |= set(oc if isinstance(oc, list) else [oc])
        shown_bases |= set(other.get("base_types") or [])
    clash = sorted(set(classes) & shown_classes)
    if clash:
        raise SystemExit(
            f"hide gate FAIL: '{rule['name']}' would hide class(es) the build shows: {clash}"
        )
    if rule.get("base_types"):
        bclash = sorted(set(rule["base_types"]) & shown_bases)
        if bclash:
            raise SystemExit(
                f"hide gate FAIL: '{rule['name']}' would hide base(s) the build shows: {bclash}"
            )

    lines = [f"# [overlay:hide] {rule['name']}"]
    if rule.get("note"):
        lines.append(f"#   {rule['note']}")
    lines.append("Hide")
    lines.append("	Rarity " + " ".join(rule.get("rarity") or ["Normal", "Magic"]))
    lines.append("	Class == " + " ".join(f'"{c}"' for c in classes))
    if rule.get("base_types"):
        lines.append("	BaseType == " + " ".join(f'"{b}"' for b in rule["base_types"]))
    # NeverSink 의 세 안전장치를 그대로 쓴다 -- 룬 슬롯이 뚫렸거나 퀄리티가 붙었거나
    # 상위 티어 미감정이면 숨기지 않는다.
    lines.append("	Sockets 0")
    lines.append("	Quality 0")
    lines.append(f"	UnidentifiedItemTier <= {int(rule.get('unid_tier_max', 3))}")
    if rule.get("area_level_min"):
        lines.append(f"	AreaLevel >= {int(rule['area_level_min'])}")
    if rule.get("area_level_max"):
        lines.append(f"	AreaLevel <= {int(rule['area_level_max'])}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--stage",
        default=None,
        choices=["campaign", "maps", "endgame"],
        help="emit only the rules that apply to this progression stage",
    )
    ap.add_argument(
        "--allow-drops",
        action="store_true",
        help="downgrade vocabulary-gate misses from an error to a warning",
    )
    ap.add_argument("-v", "--verbose", action="store_true", help="list every shadowed base block")
    ap.add_argument("--install-dir", default=None)
    args = ap.parse_args()

    base_path, spec_path = Path(args.base), Path(args.spec)
    if not base_path.exists():
        raise SystemExit(f"base filter not found: {base_path}")
    base_text = base_path.read_text(encoding="utf-8")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    base_blocks = parse_base_blocks(base_text)
    classes_of = class_index(base_text)
    allowed_values = base_value_vocabulary(base_text)
    vocabulary = base_vocabulary(base_text) | game_base_names()

    for name, style in spec["styles"].items():
        check_contrast(name, style)
        check_style_values(name, style, allowed_values)

    blocks: list[str] = []
    hide_blocks: list[str] = []
    dropped: list[str] = []
    raised: list[str] = []
    shadowed: list[str] = []
    skipped_stage = 0
    for rule in spec["rules"]:
        stages = rule.get("stages")
        if args.stage and stages and args.stage not in stages:
            skipped_stage += 1
            continue

        if rule.get("kind") == "hide":
            hide_blocks.append(render_hide_block(rule, spec, vocabulary))
            continue

        classes = rule.get("class")
        if classes:
            classes = classes if isinstance(classes, list) else [classes]
            bad = [c for c in classes if c not in vocabulary]
            if bad:
                dropped.append(f"{rule['name']}: class {bad}")
                continue

        kept = [b for b in rule["base_types"] if b in vocabulary]
        dropped += [f"{rule['name']}: {b}" for b in rule["base_types"] if b not in kept]
        if not kept:
            dropped.append(f"{rule['name']}: rule lost every BaseType")
            continue

        rule_blocks, rule_raises, rule_shadows = build_rule_blocks(
            {**rule, "base_types": kept}, spec["styles"][rule["style"]], base_blocks, classes_of
        )
        blocks += rule_blocks
        raised += [f"{rule['name']} / {r}" for r in rule_raises]
        shadowed += [f"{rule['name']} / {s}" for s in rule_shadows]

    if raised:
        log.info("loudness gate raised %d item(s) to match the base filter:", len(raised))
        for item in raised:
            log.info("  + %s", item)

    if shadowed:
        # Inherent to a prepended overlay: an item that is BOTH a build target and
        # hits one of NeverSink's narrow special cases (high quality, socket count,
        # corrupted) now answers in build colours instead. It is never hidden, so
        # this is a note, not a defect -- one line unless --verbose asks for the list.
        by_block: dict[str, int] = {}
        for item in shadowed:
            by_block[item.split(": base ", 1)[-1]] = by_block.get(item.split(": base ", 1)[-1], 0) + 1
        ranked = sorted(by_block.items(), key=lambda kv: -kv[1])
        log.warning(
            "%d item/condition pair(s) shadow %d conditional base block(s) "
            "(narrower cases: sockets, quality, corrupted). Loudest: %s. Use --verbose for the list.",
            len(shadowed), len(by_block), ranked[0][0] if ranked else "-",
        )
        if args.verbose:
            for key, count in ranked:
                log.warning("  ~ %d item(s) -> %s", count, key)

    if dropped:
        for name in dropped:
            log.error("vocabulary gate: %s", name)
        if not args.allow_drops:
            raise SystemExit(
                f"vocabulary gate FAIL: {len(dropped)} name(s) unknown to both the base filter and "
                f"{BASE_ITEMS.name}. Fix the spelling, or pass --allow-drops if intended."
            )

    if not blocks:
        raise SystemExit("nothing to emit: every rule was dropped or filtered out by --stage")

    meta = spec.get("_meta", {})
    stage_label = args.stage or "all stages"
    header = "\n".join(
        [
            "#" + "=" * 79,
            f"# PathcraftAI build overlay: {meta.get('build', spec_path.stem)}",
            f"# stage: {stage_label} | base: {base_path.name}",
            f"# spec: {spec_path.name}",
            # 배너는 세지 말고 **계산해서** 쓴다. 한때 여기에 "Nothing is hidden" 이 박혀
            # 있었는데 숨김 룰이 들어온 뒤에도 그대로라, 배포된 세 필터가 전부 자기를
            # 잘못 설명했다(각 파일에 Hide 블록 1개). 적대검증이 이걸로 주장을 깼다.
            (f"# {len(hide_blocks)} hide rule(s) declared by the spec; everything else falls"
             " through to NeverSink." if hide_blocks
             else "# Show-only. Nothing is hidden; unmatched items fall through to NeverSink."),
            "# regenerate: python scripts/build_poe2_build_overlay.py"
            f" --spec {repo_relative(spec_path)} --base {repo_relative(base_path)} --out <out>"
            + (f" --stage {args.stage}" if args.stage else ""),
            "#" + "=" * 79,
            "",
        ]
    )
    # Hide 는 Show 뒤, 베이스 앞. 우리 Show 가 먼저 이기고, 그 다음 우리 Hide 가
    # 베이스보다 먼저 걸린다 -- 순서가 뒤집히면 빌드 아이템을 우리 손으로 지운다.
    out_text = header + "\n\n".join(blocks + hide_blocks) + "\n\n" + base_text
    out_path = Path(args.out)
    out_path.write_text(out_text, encoding="utf-8", newline="\n")
    log.info(
        "wrote %s (%d overlay blocks, %d bytes, %d rule(s) skipped by stage)",
        out_path,
        len(blocks),
        out_path.stat().st_size,
        skipped_stage,
    )

    if args.install_dir:
        dest = Path(args.install_dir) / out_path.name
        shutil.copy(out_path, dest)
        log.info("installed -> %s", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
