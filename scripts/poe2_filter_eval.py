"""A first-match-wins evaluator for PoE2 loot filters.

Why this exists. The overlay builder decides how loud a block must be by reading
the base filter itself, and the test that checked "no block is quieter than
vanilla" called that same function -- so disabling the loudness gate entirely
still produced a green suite. A gate audited by its own logic proves nothing.

This module is the independent oracle. It knows nothing about the builder: it
parses a finished .filter the way the game does and answers "what happens when
this item drops". Point it at the base filter and at the overlay-prepended file,
compare the two answers, and a regression is a fact rather than an assertion
about intermediate state.

Deliberate under-approximation: a block using a condition this module does not
model is treated as *not matching*. That makes the base filter look quieter than
it really is, so a comparison test built on it can miss a regression but can
never invent one. `unmodelled_conditions()` reports what was skipped, so the
blind spot stays measurable instead of silent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

QUOTED = re.compile(r'"([^"]+)"')

NUMERIC_CONDITIONS = {
    "Sockets", "AreaLevel", "ItemLevel", "Quality", "StackSize", "DropLevel",
    "WaystoneTier", "BaseArmour", "BaseEnergyShield", "BaseEvasion", "BaseWard",
    "UnidentifiedItemTier", "MapTier", "GemLevel", "Width", "Height",
}
BOOLEAN_CONDITIONS = {
    "Corrupted", "Mirrored", "Identified", "SynthesisedItem", "FracturedItem",
    "AnyEnchantment", "AlternateQuality", "Replica", "Scourged", "HasImplicitMod",
}
NAME_CONDITIONS = {"BaseType", "Class", "Rarity", "HasExplicitMod", "HasEnchantment"}
RARITY_ORDER = {"Normal": 0, "Magic": 1, "Rare": 2, "Unique": 3}

ACTION_PREFIXES = ("Set", "Play", "Minimap", "Custom", "Disable", "Enable")


@dataclass
class Item:
    """One fully specified drop. Defaults describe a plain white item."""

    base_type: str
    item_class: str = ""
    rarity: str = "Normal"
    sockets: int = 0
    area_level: int = 65
    item_level: int = 65
    quality: int = 0
    corrupted: bool = False
    mirrored: bool = False
    stack_size: int = 1


@dataclass
class Outcome:
    visible: bool = True
    font: int = 32
    volume: int = 0
    sound_id: int | None = None
    icon_size: int | None = None
    block_line: int = 0
    matched: bool = False

    def louder_than(self, other: "Outcome") -> bool:
        return (self.font, self.volume) > (other.font, other.volume)


@dataclass
class Block:
    action: str = "Show"
    line: int = 0
    conditions: list[tuple[str, str, list[str]]] = field(default_factory=list)
    font: int | None = None
    volume: int | None = None
    sound_id: int | None = None
    icon_size: int | None = None
    cont: bool = False
    unmodelled: set[str] = field(default_factory=set)


def _split_condition(line: str) -> tuple[str, str, list[str]]:
    keyword, _, rest = line.partition(" ")
    rest = rest.strip()
    operator = ""
    match = re.match(r"^(==|<=|>=|!=|<|>|=)\s*", rest)
    if match:
        operator = match.group(1)
        rest = rest[match.end():]
    values = QUOTED.findall(rest) or rest.split()
    return keyword, operator, values


def parse(text: str) -> list[Block]:
    blocks: list[Block] = []
    current: Block | None = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            if current is not None:
                blocks.append(current)
                current = None
            continue
        if line.startswith(("Show", "Hide")):
            if current is not None:
                blocks.append(current)
            current = Block(action=line.split("#")[0].strip() or "Show", line=lineno)
            continue
        if current is None or line.startswith("#"):
            continue
        line = line.split("#")[0].strip()
        if not line:
            continue
        keyword = line.split()[0]
        if keyword == "Continue":
            current.cont = True
            continue
        if keyword.startswith(ACTION_PREFIXES):
            parts = line.split()
            try:
                if keyword == "SetFontSize":
                    current.font = int(parts[1])
                elif keyword == "PlayAlertSound":
                    current.sound_id = int(parts[1])
                    current.volume = int(parts[2]) if len(parts) > 2 else 100
                elif keyword == "MinimapIcon":
                    current.icon_size = int(parts[1])
            except (IndexError, ValueError):
                pass
            continue
        if keyword not in NUMERIC_CONDITIONS | BOOLEAN_CONDITIONS | NAME_CONDITIONS:
            current.unmodelled.add(keyword)
        current.conditions.append(_split_condition(line))
    if current is not None:
        blocks.append(current)
    return blocks


def _compare(actual: int, operator: str, expected: int) -> bool:
    return {
        ">=": actual >= expected, ">": actual > expected,
        "<=": actual <= expected, "<": actual < expected,
        "!=": actual != expected,
    }.get(operator, actual == expected)


def _matches_condition(item: Item, keyword: str, operator: str, values: list[str]) -> bool:
    if keyword == "BaseType":
        if operator == "==":
            return item.base_type in values
        return any(v in item.base_type for v in values)
    if keyword == "Class":
        if operator == "==":
            return item.item_class in values
        return any(v in item.item_class for v in values)
    if keyword == "Rarity":
        if operator in {"<", "<=", ">", ">="} and len(values) == 1 and values[0] in RARITY_ORDER:
            return _compare(RARITY_ORDER[item.rarity], operator, RARITY_ORDER[values[0]])
        return item.rarity in values
    if keyword in BOOLEAN_CONDITIONS:
        wanted = values and values[0].lower() == "true"
        actual = {"Corrupted": item.corrupted, "Mirrored": item.mirrored}.get(keyword)
        if actual is None:
            return not wanted  # unmodelled flags are false on a plain drop
        return actual == wanted
    if keyword in NUMERIC_CONDITIONS:
        actual = {
            "Sockets": item.sockets, "AreaLevel": item.area_level,
            "ItemLevel": item.item_level, "Quality": item.quality,
            "StackSize": item.stack_size,
        }.get(keyword)
        if actual is None:
            return False  # a dimension we do not model -> cannot prove a match
        try:
            return _compare(actual, operator, int(values[0]))
        except (IndexError, ValueError):
            return False
    return False


def matches(block: Block, item: Item) -> bool:
    if block.unmodelled:
        return False
    return all(_matches_condition(item, *c) for c in block.conditions)


def evaluate(blocks: list[Block], item: Item) -> Outcome:
    """Walk the filter the way the client does: first match wins, Continue falls through."""
    outcome = Outcome()
    for block in blocks:
        if not matches(block, item):
            continue
        outcome.matched = True
        outcome.visible = block.action == "Show"
        outcome.block_line = block.line
        if block.font is not None:
            outcome.font = block.font
        if block.volume is not None:
            outcome.volume = block.volume
            outcome.sound_id = block.sound_id
        if block.icon_size is not None:
            outcome.icon_size = block.icon_size
        if not block.cont:
            return outcome
    return outcome


def unmodelled_conditions(blocks: list[Block]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for block in blocks:
        for keyword in block.unmodelled:
            counts[keyword] = counts.get(keyword, 0) + 1
    return counts


def load(path: str | Path) -> list[Block]:
    return parse(Path(path).read_text(encoding="utf-8"))
