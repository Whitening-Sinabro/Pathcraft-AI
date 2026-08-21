"""Build the Luminary divination-card ladder for the single progressive filter.

Every divination card that exists in the GGPK must land in exactly one section.
Tier evidence comes from the NeverSink reference filter; the build-target and
build-keep cards come from the Path of Chores Luminary Bot SSF 3.29 guide.
The emitted blocks are terminal Show rules, so card presentation is decided
here and not by the later SSF/NeverSink visual layers.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_ITEM_TYPES = REPO_ROOT / "data" / "game_data" / "BaseItemTypes.json"
NEVERSINK_REFERENCE = REPO_ROOT / "filtersample.txt"
LUMINARY_FILTER = REPO_ROOT / "filters" / "Luminary_Bot_SSF_3.29_Progressive.filter"
BUILD_TARGETS_FILE = (
    REPO_ROOT / "data" / "filter_build_targets" / "poe1_luminary_bot_ssf_3_29.json"
)

DIVCARD_METADATA_PREFIX = "Metadata/Items/DivinationCards/"
# Stacked Deck lives under the divination metadata path but is stackable currency.
DIVCARD_ITEM_CLASS = 42

# 점술 카드 전용 시각 계열 = 청록(시안)
# ----------------------------------------------------------------------------
# 화폐·유니크 사다리는 붉은 계열을 쓴다. 카드가 같은 붉은 계열을 쓰면 바닥에 뜬
# 라벨만 보고는 구분이 안 된다 — 실제로 T0/T1 카드는 GLOBAL T0 / HIGH VALUE
# 화폐·유니크와 글씨·테두리·배경·글자 크기·알림음이 **전부** 같았다. 미니맵 도형
# (Square)으로 갈라 놓았지만 그건 바닥 라벨에 안 보이므로 구분 수단이 못 된다.
#
# 그래서 카드 라벨 배경을 청록 계열로 전용한다. 근거는 배경색 하나뿐이다:
#   아래 12개 배경값은 각각 파일 전체에서 정확히 1회, 카드 블록에서만 쓰인다.
#   (T3 와 STACK 3+ 가 같은 값을 공유하는 건 의도. 둘 다 카드다.)
# 밝을수록 상위 티어. 배경 알파는 교체 전 값을 그대로 유지해 투명도는 안 건드린다.
#
# 전용이 아닌 것 — 착각하면 안 되는 자리:
#   * PlayEffect / MinimapIcon 색은 11개 열거값뿐이고 **전부 이미 사용 중**이다.
#     Cyan 도 예외가 아니다: 변신/각성 젬이 PlayEffect Cyan + MinimapIcon Cyan
#     Circle|Star 을 이미 쓴다(필터 11060~11090). 빛기둥은 도형이 없으므로 카드와
#     젬의 기둥은 인게임에서 같아 보인다. 이 필터 안에서 카테고리를 유일하게
#     가릴 수 있는 자리는 라벨 배경색뿐이라는 뜻이고, 그래서 이 겹침은 감수한 값이다.
#     (젬도 카드도 '주워서 확인' 부류라 오인 비용이 낮다. 화폐 오인과 달리 건너뛰지 않는다.)
#   * MinimapIcon Square 도 전용이 아니다 — 지도/균열/영향력 장비 등 16블록이 같이 쓴다.
#   * 필터 자체 범례(8951행)는 Cyan 을 젬/시체, Grey 를 점술 카드에 배정해 두었다.
#     Grey 는 T0 경보로 쓸 수 없을 만큼 어두워서 따르지 않았다. 의도적 이탈이다.
#   * 알림음은 이번 교체 범위 밖이라 T0/T1 은 아직 화폐와 같은 소리를 쓴다.
GENERATED_BLOCK_PREFIX = "Show # LUMINARY - "

BEGIN_MARKER = "# LUMINARY DIVINATION CARD LADDER - BEGIN"
END_MARKER = "# LUMINARY DIVINATION CARD LADDER - END"

def load_build_targets(path: Path = BUILD_TARGETS_FILE) -> Dict[str, List[str]]:
    """Read the build-dependent card emphasis.

    The build never decides whether a card is shown - every card is in the ladder
    either way. It only decides which cards get promoted to the top sections, so
    swapping builds means pointing at a different file of this shape.
    """
    if not path.exists():
        raise DivcardLayerError("Build target file missing: %s" % path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    cards = payload.get("divination_cards")
    if not isinstance(cards, dict):
        raise DivcardLayerError("%s has no divination_cards object" % path)
    result: Dict[str, List[str]] = {}
    for key in ("build_target", "keep"):
        entries = cards.get(key, [])
        names = [entry["card"] for entry in entries if entry.get("card")]
        if key == "build_target" and not names:
            raise DivcardLayerError("%s lists no build_target cards" % path)
        result[key] = names
    return result


class DivcardLayerError(RuntimeError):
    """Raised when the ladder cannot be built from verified inputs."""


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    comment: str
    style: Sequence[str]
    cards: Sequence[str] = field(default_factory=tuple)
    extra_conditions: Sequence[str] = field(default_factory=tuple)


def load_ggpk_cards(path: Path = BASE_ITEM_TYPES) -> List[str]:
    """Return every divination card base name known to the extracted GGPK data."""
    if not path.exists():
        raise DivcardLayerError("GGPK base item data missing: %s" % path)
    rows = json.loads(path.read_text(encoding="utf-8"))
    names = {
        row["Name"]
        for row in rows
        if str(row.get("Id", "")).startswith(DIVCARD_METADATA_PREFIX)
        and row.get("ItemClassesKey") == DIVCARD_ITEM_CLASS
        and row.get("Name")
    }
    if not names:
        raise DivcardLayerError("No divination cards found in %s" % path)
    return sorted(names)


def load_filter_card_names(path: Path = LUMINARY_FILTER) -> List[str]:
    """Collect card names named by the filter's own divination blocks.

    The extracted GGPK dump in this repo predates 3.29, so cards added by the
    live patch only exist in the NeverSink/SSF source layers. Those layers are
    the fallback evidence for the card universe; the generated ladder blocks
    themselves are skipped so regeneration stays non-circular.
    """
    if not path.exists():
        raise DivcardLayerError("Filter missing: %s" % path)
    names: Set[str] = set()
    for header, body in _iter_blocks(path.read_text(encoding="utf-8").splitlines()):
        if header.startswith(GENERATED_BLOCK_PREFIX):
            continue
        if not any(l.startswith("Class") and "Divination Card" in l for l in body):
            continue
        for line in body:
            if line.startswith("BaseType"):
                names.update(_quoted(line))
    return sorted(names)


def _iter_blocks(lines: Sequence[str]):
    """Yield (header, body) per filter block.

    A block runs from its Show/Hide line to the next blank line, so condition
    order inside a block is irrelevant and every BaseType line is seen. Comment
    lines between directives are skipped rather than ending the block.
    """
    header: Optional[str] = None
    body: List[str] = []
    for raw in lines:
        line = raw.strip()
        if re.match(r"^(?:Show|Hide)\b", line) and not raw.startswith((" ", "\t")):
            if header is not None:
                yield header, body
            header = line
            body = []
            continue
        if header is None:
            continue
        if not line:
            yield header, body
            header, body = None, []
            continue
        if line.startswith("#"):
            continue
        body.append(line)
    if header is not None:
        yield header, body


def _quoted(line: str) -> List[str]:
    return re.findall(r'"([^"]+)"', line)


def parse_neversink_tiers(path: Path = NEVERSINK_REFERENCE) -> Dict[str, List[str]]:
    """Extract the divination card tier lists from the NeverSink reference filter."""
    if not path.exists():
        raise DivcardLayerError("NeverSink reference filter missing: %s" % path)
    tiers: Dict[str, List[str]] = {}
    current_tier: Optional[str] = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        tier_match = re.match(r"^(?:Show|Hide)\s+#.*\$type->divination\s+\$tier->(\S+)", line)
        if tier_match:
            current_tier = tier_match.group(1)
            continue
        if line.startswith("#") or line.startswith("Show") or line.startswith("Hide"):
            current_tier = None
            continue
        if current_tier and line.startswith("BaseType"):
            tiers.setdefault(current_tier, []).extend(_quoted(line))
            current_tier = None
    if not tiers:
        raise DivcardLayerError("No divination tiers parsed from %s" % path)
    return tiers


def parse_ssf_league_cards(path: Path = LUMINARY_FILTER) -> List[str]:
    """Read the 3.29 league/new divination card list kept in the SSF suffix."""
    if not path.exists():
        raise DivcardLayerError("Filter missing: %s" % path)
    lines = path.read_text(encoding="utf-8").splitlines()
    league_start = next(
        (i for i, line in enumerate(lines) if "### LEAGUE / NEW ITEMS" in line), None
    )
    if league_start is None:
        raise DivcardLayerError("SSF league/new section marker not found")
    for line in lines[league_start:]:
        stripped = line.strip()
        if stripped.startswith("BaseType"):
            return _quoted(stripped)
    raise DivcardLayerError("SSF league/new divination card list not found")


SSF_PREFERENCE_TITLES = {
    "ssf_wanted": "You've Got to be Kidding",
    "ssf_notable": '"Absolutely!" Div Cards',
    "ssf_dontcare": "Don't Care if I Miss Them",
}

def parse_ssf_preference_lists(path: Path = LUMINARY_FILTER) -> Dict[str, List[str]]:
    """Read the Wrecker SSF pickup-preference card lists kept in the filter."""
    lines = path.read_text(encoding="utf-8").splitlines()
    found: Dict[str, List[str]] = {}
    for key, marker in SSF_PREFERENCE_TITLES.items():
        header = next(
            (i for i, l in enumerate(lines) if l.startswith("Show #") and marker in l), None
        )
        if header is None:
            raise DivcardLayerError("SSF preference list not found: %s" % marker)
        for line in lines[header : header + 6]:
            if line.strip().startswith("BaseType"):
                found[key] = _quoted(line)
                break
        else:
            raise DivcardLayerError("SSF preference list has no BaseType: %s" % marker)
    return found


def assign_sections(
    universe: Sequence[str],
    tiers: Dict[str, Sequence[str]],
    league_cards: Sequence[str],
    ssf_lists: Optional[Dict[str, Sequence[str]]] = None,
    build_targets: Optional[Dict[str, Sequence[str]]] = None,
) -> Dict[str, List[str]]:
    """Assign every known card to exactly one bucket, highest precedence first.

    Two sources disagree on purpose. The NeverSink tierlist knows league economy;
    the Wrecker SSF source knows what this player actually stops for. A card takes
    the louder of the two, so an SSF pickup target never falls to a quiet tier.
    """
    ssf = dict(ssf_lists or {})
    build_targets = dict(build_targets or load_build_targets())
    # SSF picks up everything, so the source's "skip" list only lowers emphasis,
    # never visibility or sound. Those cards simply fall through to their economy tier.
    _ = ssf.pop("ssf_dontcare", None)
    order = (
        ("build_target", build_targets["build_target"]),
        ("build_keep", build_targets["keep"]),
        ("league_new", league_cards),
        ("t0", tiers.get("t1", ())),
        ("t1", tiers.get("t2", ())),
        ("ssf_wanted", ssf.get("ssf_wanted", ())),
        ("t2", tiers.get("t3", ())),
        ("ssf_notable", ssf.get("ssf_notable", ())),
        ("t3", tiers.get("t4c", ())),
        ("t4", tiers.get("t4", ())),
        ("bulk", tiers.get("t5c", ())),
        ("low", tiers.get("t5", ())),
    )
    known: Set[str] = set(universe)
    taken: Set[str] = set()
    buckets: Dict[str, List[str]] = {}
    for key, candidates in order:
        picked: List[str] = []
        for card in candidates:
            if card not in known:
                logger.warning("Skipping unknown divination card %r in bucket %s", card, key)
                continue
            if card in taken:
                continue
            taken.add(card)
            picked.append(card)
        buckets[key] = sorted(picked)
    buckets["untiered"] = sorted(known - taken)
    return buckets


def _basetype_line(cards: Iterable[str]) -> str:
    return "    BaseType == " + " ".join('"%s"' % card for card in cards)


def build_sections(buckets: Dict[str, List[str]]) -> List[Section]:
    """Describe the ladder from loudest build target down to the new-card catch-all."""
    return [
        Section(
            "build_target",
            "LUMINARY - BUILD TARGET DIVINATION CARDS",
            "# Guide-named target cards. Loudest rung of the cyan card family.\n"
            "# Light and Truth -> Nycta's Lantern, The King's Heart -> Kaom's Heart,\n"
            "# The Spark and the Flame -> Berek's Respite, Pride Before the Fall -> corrupted Kaom's Heart.",
            (
                "    SetFontSize 45",
                "    SetTextColor 0 0 0 255",
                "    SetBorderColor 255 255 255 255",
                "    SetBackgroundColor 60 255 245 255",
                '    CustomAlertSound "DivinationCard.mp3" 300',
                "    PlayEffect Cyan",
                "    MinimapIcon 0 Cyan Square",
            ),
            buckets["build_target"],
        ),
        Section(
            "build_keep",
            "LUMINARY - GUIDE KEEP DIVINATION CARDS",
            "# Guide section 8.6: Betrayal Hillock pays this out as Fertile Catalyst, so it must stay visible.",
            (
                "    SetFontSize 42",
                "    SetTextColor 0 0 0 255",
                "    SetBorderColor 255 255 255 255",
                "    SetBackgroundColor 130 240 255 250",
                '    CustomAlertSound "DivinationCard.mp3" 260',
                "    PlayEffect Cyan",
                "    MinimapIcon 1 Cyan Square",
            ),
            buckets["build_keep"],
        ),
        Section(
            "league_new",
            "LUMINARY - LEAGUE NEW DIVINATION CARDS",
            "# 3.29 cards from the SSF league/new list. Their value is unsettled, so they stay near the top.",
            (
                "    SetFontSize 42",
                "    SetTextColor 0 0 0 255",
                "    SetBorderColor 255 255 255 255",
                "    SetBackgroundColor 175 235 255 245",
                "    PlayAlertSound 12 300",
                "    PlayEffect Cyan",
                "    MinimapIcon 1 Cyan Square",
            ),
            buckets["league_new"],
        ),
        Section(
            "t0",
            "LUMINARY - DIVINATION CARDS T0",
            "# Economy tiers below follow the NeverSink reference tierlist (t1..t5) in filtersample.txt.",
            (
                "    SetFontSize 45",
                "    SetTextColor 0 0 0 255",
                "    SetBorderColor 255 255 255 255",
                "    SetBackgroundColor 0 200 255 255",
                '    CustomAlertSound "HolyMotherfuckingShit.mp3" 300',
                "    PlayEffect Cyan",
                "    MinimapIcon 0 Cyan Square",
            ),
            buckets["t0"],
        ),
        Section(
            "t1",
            "LUMINARY - DIVINATION CARDS T1",
            "",
            (
                "    SetFontSize 45",
                "    SetTextColor 0 0 0 255",
                "    SetBorderColor 200 245 255 255",
                "    SetBackgroundColor 0 160 195 255",
                '    CustomAlertSound "Thatsworthsomething.mp3" 270',
                "    PlayEffect Cyan",
                "    MinimapIcon 0 Cyan Square",
            ),
            buckets["t1"],
        ),
        Section(
            "ssf_wanted",
            "LUMINARY - DIVINATION CARDS SSF WANTED",
            "# SSF pickup targets the economy tierlist ranks lower. The player's own list wins here.",
            (
                "    SetFontSize 45",
                "    SetTextColor 255 255 255 255",
                "    SetBorderColor 120 225 245 255",
                "    SetBackgroundColor 0 132 165 250",
                "    PlayAlertSound 1 300",
                "    PlayEffect Cyan",
                "    MinimapIcon 0 Cyan Square",
            ),
            buckets["ssf_wanted"],
        ),
        Section(
            "t2",
            "LUMINARY - DIVINATION CARDS T2",
            "",
            (
                "    SetFontSize 42",
                "    SetTextColor 235 250 255 255",
                "    SetBorderColor 85 195 220 255",
                "    SetBackgroundColor 0 106 134 250",
                "    PlayAlertSound 2 280",
                "    PlayEffect Cyan",
                "    MinimapIcon 1 Cyan Square",
            ),
            buckets["t2"],
        ),
        Section(
            "ssf_notable",
            "LUMINARY - DIVINATION CARDS SSF NOTABLE",
            "# Second SSF pickup list. Kept audible even where the economy tierlist is lukewarm.",
            (
                "    SetFontSize 40",
                "    SetTextColor 220 242 250 255",
                "    SetBorderColor 62 168 195 255",
                "    SetBackgroundColor 8 86 108 245",
                "    PlayAlertSound 12 280",
                "    MinimapIcon 1 Cyan Square",
            ),
            buckets["ssf_notable"],
        ),
        Section(
            "t3",
            "LUMINARY - DIVINATION CARDS T3",
            "",
            (
                "    SetFontSize 40",
                "    SetTextColor 205 232 242 255",
                "    SetBorderColor 46 142 168 255",
                "    SetBackgroundColor 7 68 88 245",
                "    PlayAlertSound 2 220",
                "    MinimapIcon 2 Cyan Square",
            ),
            buckets["t3"],
        ),
        Section(
            "stack",
            "LUMINARY - DIVINATION CARDS STACK 3+",
            "# A full stack of an otherwise quiet card is still worth stopping for."
            " Scoped to the quiet tiers on purpose: an unclassified card must keep"
            " falling through to the catch-all alarm even when it drops as a stack.",
            (
                "    SetFontSize 40",
                "    SetTextColor 205 232 242 255",
                "    SetBorderColor 46 142 168 255",
                "    SetBackgroundColor 7 68 88 245",
                "    PlayAlertSound 2 200",
                "    MinimapIcon 1 Cyan Square",
            ),
            sorted(buckets["t4"] + buckets["bulk"] + buckets["low"]),
            ("    StackSize >= 3",),
        ),
        Section(
            "t4",
            "LUMINARY - DIVINATION CARDS T4",
            "",
            (
                "    SetFontSize 38",
                "    SetTextColor 180 210 224 255",
                "    SetBorderColor 34 112 138 255",
                "    SetBackgroundColor 6 52 68 240",
                "    PlayAlertSoundPositional 12 200",
                "    MinimapIcon 2 Cyan Square",
            ),
            buckets["t4"],
        ),
        Section(
            "bulk",
            "LUMINARY - DIVINATION CARDS BULK",
            "# Vendor and stack fodder: visible and silent.",
            (
                "    SetFontSize 34",
                "    SetTextColor 150 182 196 255",
                "    SetBorderColor 26 86 106 255",
                "    SetBackgroundColor 5 38 50 235",
                "    PlayAlertSoundPositional 12 200",
                "    MinimapIcon 2 Cyan Square",
            ),
            buckets["bulk"],
        ),
        Section(
            "low",
            "LUMINARY - DIVINATION CARDS LOW",
            "# NeverSink hides this tier. SSF shows every card, so it is only shrunk."
            " The quiet positional cue from the SSF source is kept so nothing drops unheard.",
            (
                "    SetFontSize 32",
                "    SetTextColor 130 160 175 255",
                "    SetBorderColor 20 68 86 255",
                "    SetBackgroundColor 4 28 38 230",
                "    PlayAlertSoundPositional 12 200",
                "    MinimapIcon 2 Cyan Square",
            ),
            buckets["low"],
        ),
        Section(
            "untiered",
            "LUMINARY - DIVINATION CARDS UNTIERED CATCH-ALL",
            "# Legacy cards plus anything a future patch adds. Magenta means not classified yet.",
            (
                "    SetFontSize 45",
                "    SetTextColor 255 0 255 255",
                "    SetBorderColor 255 0 255 255",
                "    SetBackgroundColor 100 0 100 255",
                "    PlayAlertSound 3 300",
                "    PlayEffect Pink",
                "    MinimapIcon 0 Pink UpsideDownHouse",
            ),
        ),
    ]


def render_section(section: Section) -> List[str]:
    lines: List[str] = []
    if section.comment:
        lines.extend(section.comment.splitlines())
    lines.append("Show # %s" % section.title)
    lines.extend(section.extra_conditions)
    lines.append('    Class == "Divination Cards"')
    if section.cards:
        lines.append(_basetype_line(section.cards))
    lines.extend(section.style)
    lines.append("")
    return lines


def render_ladder(sections: Sequence[Section], total_cards: int) -> List[str]:
    header = [
        BEGIN_MARKER,
        "#===============================================================================================================",
        "# Every divination card resolves to exactly one terminal rule below. Coverage is",
        "# guaranteed by the unconditional catch-all, not by the card list being complete.",
        "# Named cards at generation time: %d (GGPK dump is 3.28-anchored plus source-only names)." % total_cards,
        "# Generator: python/luminary_divcard_layer.py",
        "# Order: build targets -> guide keep -> league new -> economy tiers -> stack rule -> catch-all.",
        "# Build-dependent sections come from data/filter_build_targets/; swapping builds only re-ranks.",
        "# These rules are terminal, so cards no longer reach the later NeverSink/SSF card layers;",
        "# those layers stay in the file untouched as the tier evidence this ladder is generated from.",
        "#===============================================================================================================",
        "",
    ]
    body: List[str] = []
    for section in sections:
        if section.key not in {"stack", "untiered"} and not section.cards:
            logger.warning("Section %s has no cards and is skipped", section.key)
            continue
        body.extend(render_section(section))
    return header + body + [END_MARKER]


def build_card_universe() -> List[str]:
    """GGPK cards plus every card the trusted source layers already reference."""
    ggpk = set(load_ggpk_cards())
    from_filter = set(load_filter_card_names())
    for tier_cards in parse_neversink_tiers().values():
        from_filter.update(tier_cards)
    only_in_sources = sorted(from_filter - ggpk)
    if only_in_sources:
        logger.warning(
            "%d cards exist only in the filter sources, not in the GGPK dump: %s",
            len(only_in_sources),
            ", ".join(only_in_sources),
        )
    return sorted(ggpk | from_filter)


def build_ladder_lines() -> List[str]:
    universe = build_card_universe()
    buckets = assign_sections(
        universe,
        parse_neversink_tiers(),
        parse_ssf_league_cards(),
        parse_ssf_preference_lists(),
        load_build_targets(),
    )
    covered = sum(len(cards) for cards in buckets.values())
    if covered != len(universe):
        raise DivcardLayerError(
            "Coverage mismatch: %d assigned vs %d known cards" % (covered, len(universe))
        )
    return render_ladder(build_sections(buckets), len(universe))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    lines = build_ladder_lines()
    logger.info("Rendered divination ladder: %d lines", len(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
