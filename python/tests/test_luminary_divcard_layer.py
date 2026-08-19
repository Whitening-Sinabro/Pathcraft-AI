"""Coverage and lint tests for the Luminary divination-card ladder."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from luminary_divcard_layer import (  # noqa: E402
    BEGIN_MARKER,
    BUILD_TARGETS_FILE,
    END_MARKER,
    LUMINARY_FILTER,
    build_card_universe,
    load_build_targets,
)

REQUIRED_UNIQUE_STYLE = (
    "SetTextColor 255 255 255 255",
    "SetBorderColor 255 255 255 255",
    "SetBackgroundColor 190 0 0 255",
)

# Cards that neither the economy tierlist nor the SSF pickup lists classify.
# Pinned so a silent list change fails loudly.
EXPECTED_UNTIERED = {
    "Birth of the Three",
    "Luck of the Vaal",
    "Soul Quenched",
    "The Devastator",
    "The Puzzle",
    "The Sustenance",
    "Treasures of the Vaal",
}


class Block:
    def __init__(self, action: str, title: str, line_number: int) -> None:
        self.action = action
        self.title = title
        self.line_number = line_number
        self.body: List[str] = []

    @property
    def is_continue(self) -> bool:
        return any(line.strip() == "Continue" for line in self.body)

    @property
    def matches_divination(self) -> bool:
        return any(
            line.strip().startswith("Class") and "Divination Card" in line for line in self.body
        )

    @property
    def base_types(self) -> List[str]:
        for line in self.body:
            if line.strip().startswith("BaseType"):
                return re.findall(r'"([^"]+)"', line)
        return []

    @property
    def has_stack_condition(self) -> bool:
        return any(line.strip().startswith("StackSize") for line in self.body)

    def directive(self, name: str) -> Optional[str]:
        for line in self.body:
            stripped = line.strip()
            if stripped.startswith(name):
                return stripped
        return None


@pytest.fixture(scope="module")
def filter_lines() -> List[str]:
    return LUMINARY_FILTER.read_text(encoding="utf-8").splitlines()


@pytest.fixture(scope="module")
def blocks(filter_lines: List[str]) -> List[Block]:
    parsed: List[Block] = []
    current: Optional[Block] = None
    for number, raw in enumerate(filter_lines, start=1):
        header = re.match(r"^(Show|Hide)\s*(?:#\s*(.*))?$", raw.rstrip())
        if header:
            current = Block(header.group(1), (header.group(2) or "").strip(), number)
            parsed.append(current)
            continue
        if current is None:
            continue
        # SSF source blocks are flush-left, so a block ends at a blank line, not at
        # the first unindented line. Comments between directives are skipped.
        stripped = raw.strip()
        if not stripped:
            current = None
            continue
        if stripped.startswith("#"):
            continue
        current.body.append(raw)
    return parsed


@pytest.fixture(scope="module")
def ladder_blocks(blocks: List[Block]) -> List[Block]:
    return [b for b in blocks if b.title.startswith("LUMINARY - ") and b.matches_divination]


def first_matching_block(blocks: List[Block], card: str, stack: int) -> Tuple[Block, ...]:
    """Return the blocks a dropped card walks through until a terminal rule wins."""
    walked: List[Block] = []
    for block in blocks:
        if not block.matches_divination:
            continue
        base_types = block.base_types
        if base_types and card not in base_types:
            continue
        if block.has_stack_condition and stack < 3:
            continue
        walked.append(block)
        if not block.is_continue:
            break
    return tuple(walked)


def test_ladder_markers_present(filter_lines: List[str]) -> None:
    assert filter_lines.count(BEGIN_MARKER) == 1
    assert filter_lines.count(END_MARKER) == 1
    assert filter_lines.index(BEGIN_MARKER) < filter_lines.index(END_MARKER)


def test_ladder_is_inside_the_luminary_override_region(filter_lines: List[str]) -> None:
    start = next(
        i for i, l in enumerate(filter_lines) if l.startswith("# PATHCRAFT: PATH OF CHORES")
    )
    end = next(
        i for i, l in enumerate(filter_lines) if l.startswith("# END PATH OF CHORES LUMINARY")
    )
    assert start < filter_lines.index(BEGIN_MARKER) < filter_lines.index(END_MARKER) < end


def test_every_known_card_lands_in_a_ladder_section(blocks: List[Block]) -> None:
    for card in build_card_universe():
        walked = first_matching_block(blocks, card, stack=1)
        assert walked, "no block matches %s" % card
        terminal = walked[-1]
        assert not terminal.is_continue, "%s never reaches a terminal rule" % card
        assert terminal.title.startswith("LUMINARY - "), "%s ends at %r" % (card, terminal.title)


def test_no_card_is_hidden(blocks: List[Block]) -> None:
    for card in build_card_universe():
        for stack in (1, 3):
            terminal = first_matching_block(blocks, card, stack)[-1]
            assert terminal.action == "Show", "%s is hidden by %r" % (card, terminal.title)


def test_ladder_sections_are_disjoint(ladder_blocks: List[Block]) -> None:
    """Each card has one home tier. The stack rule deliberately re-lists quiet cards."""
    seen: Dict[str, str] = {}
    for block in ladder_blocks:
        if block.has_stack_condition:
            continue
        for card in block.base_types:
            assert card not in seen, "%s appears in %r and %r" % (card, seen[card], block.title)
            seen[card] = block.title


def test_stack_rule_cannot_shadow_the_catch_all(ladder_blocks: List[Block]) -> None:
    """A 3-stack of an unclassified card must still hit the magenta catch-all."""
    stack = next(b for b in ladder_blocks if b.has_stack_condition)
    quiet = set()
    for suffix in ("CARDS T4", "CARDS BULK", "CARDS LOW"):
        quiet |= set(next(b for b in ladder_blocks if b.title.endswith(suffix)).base_types)
    assert set(stack.base_types) == quiet
    catch_all = next(b for b in ladder_blocks if b.title.endswith("UNTIERED CATCH-ALL"))
    assert not catch_all.base_types
    assert not set(stack.base_types) & set(EXPECTED_UNTIERED)


def test_untiered_catch_all_membership() -> None:
    from luminary_divcard_layer import (
        assign_sections,
        parse_neversink_tiers,
        parse_ssf_league_cards,
        parse_ssf_preference_lists,
    )

    buckets = assign_sections(
        build_card_universe(),
        parse_neversink_tiers(),
        parse_ssf_league_cards(),
        parse_ssf_preference_lists(),
        load_build_targets(),
    )
    assert set(buckets["untiered"]) == EXPECTED_UNTIERED


def test_guide_cards_are_in_their_own_sections(ladder_blocks: List[Block]) -> None:
    build_targets = load_build_targets()
    target = next(b for b in ladder_blocks if b.title.endswith("BUILD TARGET DIVINATION CARDS"))
    keep = next(b for b in ladder_blocks if b.title.endswith("GUIDE KEEP DIVINATION CARDS"))
    assert set(target.base_types) == set(build_targets["build_target"])
    assert set(keep.base_types) == set(build_targets["keep"])


def test_build_target_file_names_only_real_cards() -> None:
    universe = set(build_card_universe())
    for key, cards in load_build_targets().items():
        for card in cards:
            assert card in universe, "%s in %s is not a known card (%s)" % (
                card,
                key,
                BUILD_TARGETS_FILE.name,
            )


def test_build_emphasis_never_removes_a_card(blocks: List[Block]) -> None:
    """Switching builds may re-rank cards; it must never drop one from the ladder."""
    promoted = {c for cards in load_build_targets().values() for c in cards}
    for card in build_card_universe():
        terminal = first_matching_block(blocks, card, stack=1)[-1]
        assert terminal.action == "Show"
        if card not in promoted:
            assert terminal.title.startswith("LUMINARY - "), card


def test_build_targets_reuse_the_required_unique_colours(
    ladder_blocks: List[Block], blocks: List[Block]
) -> None:
    target = next(b for b in ladder_blocks if b.title.endswith("BUILD TARGET DIVINATION CARDS"))
    required_unique = next(b for b in blocks if b.title == "LUMINARY - CORE REQUIRED UNIQUE BASES")
    for directive in REQUIRED_UNIQUE_STYLE:
        name = directive.split(" ", 1)[0]
        assert target.directive(name) == directive
        assert required_unique.directive(name) == directive


def test_ladder_blocks_are_terminal(ladder_blocks: List[Block]) -> None:
    for block in ladder_blocks:
        assert not block.is_continue, "%r must stay terminal" % block.title


def test_no_block_mixes_builtin_and_custom_alerts(ladder_blocks: List[Block]) -> None:
    for block in ladder_blocks:
        assert not (
            block.directive("PlayAlertSound") and block.directive("CustomAlertSound")
        ), "%r mixes alert types" % block.title


def test_custom_alert_sounds_exist(ladder_blocks: List[Block]) -> None:
    sound_dir = LUMINARY_FILTER.parent
    game_dir = Path(r"C:\Users\User\Documents\My Games\Path of Exile")
    for block in ladder_blocks:
        directive = block.directive("CustomAlertSound")
        if not directive:
            continue
        name = re.findall(r'"([^"]+)"', directive)[0]
        assert (game_dir / name).exists() or (sound_dir / name).exists(), "missing sound %s" % name


def test_ladder_directive_ranges(ladder_blocks: List[Block]) -> None:
    for block in ladder_blocks:
        for raw in block.body:
            line = raw.strip()
            font = re.match(r"^SetFontSize (\d+)$", line)
            if font:
                assert 18 <= int(font.group(1)) <= 45, line
            colour = re.match(r"^Set(?:Text|Border|Background)Color((?: \d+){3,4})$", line)
            if colour:
                assert all(0 <= int(v) <= 255 for v in colour.group(1).split()), line
            assert line.count('"') % 2 == 0, line
