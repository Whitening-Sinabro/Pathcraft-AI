"""Continue-cascade simulator for Path of Exile item filters.

A filter block with ``Continue`` keeps matching later blocks, so the style an
item finally renders with is the merge of every matching block up to the first
terminal one. Text/background collisions therefore cannot be detected block by
block; they only appear in the merged result. This module models enough of the
condition language to reproduce that merge for equipment archetypes and to
measure the resulting text/background contrast.

Unknown conditions are treated as *not matching*, so the simulator under-reports
matches rather than inventing them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Sequence

BLOCK_START_RE = re.compile(r"^(Show|Hide)(?:\s+#.*)?\s*$")
RARITY_ORDER = ("Normal", "Magic", "Rare", "Unique")
STYLE_PREFIXES = ("Set", "Play", "Minimap", "Custom", "Continue", "Disable")
BOOLEAN_CONDITIONS = frozenset(
    {
        "Corrupted",
        "Mirrored",
        "Identified",
        "AnyEnchantment",
        "FracturedItem",
        "SynthesisedItem",
        "Replica",
        "Scourged",
        "Transfigured",
        "HasEaterOfWorldsImplicit",
        "HasSearingExarchImplicit",
        "HasCruciblePassiveTree",
        "ShapedMap",
        "ElderMap",
        "BlightedMap",
        "UberBlightedMap",
        "AlternateQuality",
        "ZanaMemory",
        "Foulborn",
        "Vestigial",
    }
)
NUMERIC_CONDITIONS = {
    "AreaLevel": "area_level",
    "ItemLevel": "item_level",
    "DropLevel": "drop_level",
    "StackSize": "stack_size",
    "LinkedSockets": "linked_sockets",
    "Sockets": "sockets",
    "Height": "height",
    "Width": "width",
    "Quality": "quality",
}
# Metadata id path segment -> loot-filter Class name (equipment only).
ID_SEGMENT_TO_CLASS = {
    "OneHandAxes": "One Hand Axes",
    "OneHandMaces": "One Hand Maces",
    "OneHandSwords": "One Hand Swords",
    "OneHandThrustingSwords": "Thrusting One Hand Swords",
    "Claws": "Claws",
    "Daggers": "Daggers",
    "RuneDaggers": "Rune Daggers",
    "Wands": "Wands",
    "Sceptres": "Sceptres",
    "Bows": "Bows",
    "Staves": "Staves",
    "Warstaves": "Warstaves",
    "TwoHandAxes": "Two Hand Axes",
    "TwoHandMaces": "Two Hand Maces",
    "TwoHandSwords": "Two Hand Swords",
    "BodyArmours": "Body Armours",
    "Boots": "Boots",
    "Gloves": "Gloves",
    "Helmets": "Helmets",
    "Shields": "Shields",
    "Quivers": "Quivers",
    "Rings": "Rings",
    "Amulets": "Amulets",
    "Belts": "Belts",
}


@dataclass(frozen=True)
class SimulatedItem:
    base_type: str
    item_class: str
    rarity: str
    area_level: int
    item_level: int
    drop_level: int = 1
    stack_size: int = 1
    linked_sockets: int = 0
    sockets: int = 1
    height: int = 3
    width: int = 2
    quality: int = 0


@dataclass(frozen=True)
class ParsedCondition:
    """One condition line pre-parsed once so simulation stays cheap."""

    keyword: str
    values: tuple[str, ...]
    exact: bool
    operator: str
    number: int | None
    rarity_bound: tuple[str, int] | None
    boolean: bool | None

    @classmethod
    def parse(cls, condition: str) -> "ParsedCondition":
        keyword, _, rest = condition.partition(" ")
        rest = rest.strip()
        quoted = re.findall(r'"([^"]+)"', rest)
        values = tuple(quoted or rest.replace("==", "").split())
        exact = "==" in rest
        operator, number, rarity_bound, boolean = "==", None, None, None
        if keyword in NUMERIC_CONDITIONS:
            numeric = re.match(r"(>=|<=|<|>|==|=|!)?\s*(\d+)", rest)
            if numeric:
                operator, number = numeric.group(1) or "==", int(numeric.group(2))
        elif keyword == "Rarity":
            ordered = re.match(r"(>=|<=|<|>)\s*(\w+)", rest)
            if ordered and ordered.group(2) in RARITY_ORDER:
                rarity_bound = (ordered.group(1), RARITY_ORDER.index(ordered.group(2)))
        elif keyword in BOOLEAN_CONDITIONS:
            boolean = rest.lower() == "true"
        return cls(keyword, values, exact, operator, number, rarity_bound, boolean)


@dataclass
class CascadeBlock:
    action: str
    header: str
    line: int
    conditions: list[ParsedCondition] = field(default_factory=list)
    styles: dict[str, str] = field(default_factory=dict)
    continues: bool = False


@dataclass(frozen=True)
class CascadeResult:
    action: str
    styles: dict[str, str]
    chain: tuple[int, ...]

    def colour(self, key: str) -> tuple[int, int, int, int] | None:
        value = self.styles.get(key)
        if value is None:
            return None
        parts = value.split()[1:]
        if len(parts) < 3:
            return None
        rgba = [int(part) for part in parts[:4]]
        if len(rgba) == 3:
            rgba.append(255)
        return tuple(rgba)  # type: ignore[return-value]


def parse_cascade(lines: Sequence[str]) -> list[CascadeBlock]:
    blocks: list[CascadeBlock] = []
    current: CascadeBlock | None = None
    for index, raw in enumerate(lines, 1):
        stripped = raw.strip()
        match = BLOCK_START_RE.match(raw)
        if match:
            current = CascadeBlock(action=match.group(1), header=stripped, line=index)
            blocks.append(current)
            continue
        if current is None or not stripped or stripped.startswith("#"):
            continue
        if stripped == "Continue":
            current.continues = True
        elif stripped.startswith(STYLE_PREFIXES):
            current.styles[stripped.split()[0]] = stripped
        else:
            current.conditions.append(ParsedCondition.parse(stripped))
    return blocks


def _compare(value: int, operator: str, target: int) -> bool:
    operator = "==" if operator in ("", "=") else operator
    return {
        "==": value == target,
        ">=": value >= target,
        "<=": value <= target,
        ">": value > target,
        "<": value < target,
        "!": value != target,
    }[operator]


def _condition_matches(condition: ParsedCondition, item: SimulatedItem) -> bool:
    keyword = condition.keyword
    if keyword == "BaseType":
        if condition.exact:
            return item.base_type in condition.values
        return any(value in item.base_type for value in condition.values)
    if keyword == "Class":
        if condition.exact:
            return item.item_class in condition.values
        return any(value in item.item_class for value in condition.values)
    if keyword == "Rarity":
        if condition.rarity_bound is not None:
            operator, bound = condition.rarity_bound
            return _compare(RARITY_ORDER.index(item.rarity), operator, bound)
        return item.rarity in condition.values
    if keyword in NUMERIC_CONDITIONS:
        if condition.number is None:
            return False
        actual = getattr(item, NUMERIC_CONDITIONS[keyword])
        return _compare(actual, condition.operator, condition.number)
    if keyword in BOOLEAN_CONDITIONS:
        # Simulated archetypes carry none of these flags.
        return condition.boolean is False
    return False


def simulate(blocks: Iterable[CascadeBlock], item: SimulatedItem) -> CascadeResult:
    styles: dict[str, str] = {}
    chain: list[int] = []
    for block in blocks:
        if not all(_condition_matches(condition, item) for condition in block.conditions):
            continue
        chain.append(block.line)
        styles.update(block.styles)
        if not block.continues:
            return CascadeResult(block.action, styles, tuple(chain))
    return CascadeResult("Show", styles, tuple(chain))


def relative_luminance(rgb: Sequence[int]) -> float:
    def channel(value: int) -> float:
        scaled = value / 255
        return scaled / 12.92 if scaled <= 0.03928 else ((scaled + 0.055) / 1.055) ** 2.4

    red, green, blue = rgb[:3]
    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def contrast_ratio(first: Sequence[int], second: Sequence[int]) -> float:
    lum_a, lum_b = relative_luminance(first), relative_luminance(second)
    high, low = max(lum_a, lum_b), min(lum_a, lum_b)
    return (high + 0.05) / (low + 0.05)


def class_from_metadata_id(metadata_id: str) -> str | None:
    """Map a BaseItemTypes metadata id to its loot-filter Class name."""
    leaf = metadata_id.rsplit("/", 1)[-1]
    if "/Flasks/" in metadata_id:
        for prefix, item_class in (
            ("FlaskLife", "Life Flasks"),
            ("FlaskMana", "Mana Flasks"),
            ("FlaskHybrid", "Hybrid Flasks"),
            ("FlaskUtility", "Utility Flasks"),
        ):
            if leaf.startswith(prefix):
                return item_class
        return None
    if "/Jewels/" in metadata_id:
        return "Abyss Jewels" if leaf.startswith("JewelAbyss") else "Jewels"
    for segment in reversed(metadata_id.split("/")[:-1]):
        if segment in ID_SEGMENT_TO_CLASS:
            return ID_SEGMENT_TO_CLASS[segment]
    return None


@dataclass(frozen=True)
class Collision:
    item: SimulatedItem
    contrast: float
    text: tuple[int, int, int, int]
    background: tuple[int, int, int, int]
    chain: tuple[int, ...]


def find_collisions(
    blocks: Sequence[CascadeBlock],
    items: Iterable[SimulatedItem],
    *,
    minimum_contrast: float,
    minimum_background_alpha: int = 60,
) -> list[Collision]:
    """Return visible archetypes whose merged text/background contrast is too low."""
    collisions: list[Collision] = []
    for item in items:
        result = simulate(blocks, item)
        if result.action == "Hide":
            continue
        text = result.colour("SetTextColor")
        background = result.colour("SetBackgroundColor")
        if text is None or background is None or background[3] < minimum_background_alpha:
            continue
        ratio = contrast_ratio(text, background)
        if ratio < minimum_contrast:
            collisions.append(Collision(item, ratio, text, background, result.chain))
    collisions.sort(key=lambda collision: collision.contrast)
    return collisions
