#!/usr/bin/env python3
"""Build and validate the Smokiezone Hydrosphere Boneshatter HCSSF filter.

The validated Luminary progressive filter is treated as an immutable composition
source.  This generator replaces only Pathcraft-owned theme/build layers, keeps
the Wrecker SSF visibility policy byte-for-byte at the block level, and applies
one shared Violet Velvet token system from the canonical build specification.
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import re
import shutil
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_FILTER = REPO_ROOT / "filters" / "Luminary_Bot_SSF_3.29_Progressive.filter"
SPEC_PATH = (
    REPO_ROOT
    / "data"
    / "filter_build_targets"
    / "poe1_smokiezone_hydrosphere_boneshatter_hcssf_3_29.json"
)
ECONOMY_PATH = (
    REPO_ROOT / "data" / "filter_sources" / "neversink_poe1_8_20_1d_903189_economy.json"
)
OUTPUT_FILTER = (
    REPO_ROOT
    / "filters"
    / "Smokiezone_Hydrosphere_Boneshatter_HCSSF_3.29_Progressive.filter"
)
GAME_FILTER_DIR = Path(r"C:\Users\User\Documents\My Games\Path of Exile")

EXPECTED_BASE_SHA256 = (
    "C8332945290D367DF633884B2C66A8DCF894D6C369BC451DFB7872321839F188"
)
SOURCE_HASHES = {
    Path(
        r"C:\Users\User\Desktop\SSF.txt"
    ): "94CC3493AD7374B8AD8C54A88D3C43527E4DA557CA1D5723719064E3A98971E9",
    Path(
        r"C:\Users\User\Desktop\death oath.txt"
    ): "E637B4BB917E670CA332B350CA094DDB0AF467364B75B0922240507C81A1F8CF",
    Path(
        r"C:\Users\User\Desktop\allie.txt"
    ): "BEE3CC4352B3403DA752796FD764E45EEB25E9F1F76C491091CA6A59FD90B497",
}

NEVERSINK_COMMIT = "903189340cdafa1f4ed73c9968380826312a51f0"
NEVERSINK_VERSION = "8.20.1d"
NEVERSINK_URL = (
    "https://raw.githubusercontent.com/NeverSinkDev/NeverSink-Filter/"
    + NEVERSINK_COMMIT
    + "/NeverSink%27s%20filter%20-%201-REGULAR.filter"
)

OLD_BUILD_MARKER = (
    "# PATHCRAFT: PATH OF CHORES 3.29 LUMINARY BOT - BUILD-SPECIFIC SSF TARGETS"
)
OLD_BUILD_END = "# END PATH OF CHORES LUMINARY BUILD-SPECIFIC TARGETS"
OLD_CARD_BEGIN = "# LUMINARY DIVINATION CARD LADDER - BEGIN"
OLD_CARD_END = "# LUMINARY DIVINATION CARD LADDER - END"
NEW_CARD_BEGIN = "# SMOKIEZONE HCSSF DIVINATION CARD LADDER - BEGIN"
NEW_CARD_END = "# SMOKIEZONE HCSSF DIVINATION CARD LADDER - END"
SEPARATOR = "#" + "=" * 111

BLOCK_START_RE = re.compile(r"^(Show|Hide)(?:\s+#.*)?\s*$")
QUOTED_RE = re.compile(r'"([^"]+)"')

# Familiar Path of Exile rarity/category cues are semantic tokens, not theme
# accents. Violet is reserved for value, build relevance and urgency.
RARITY_TEXT = {
    "Normal": (200, 200, 200),
    "Magic": (136, 136, 255),
    "Rare": (255, 255, 119),
    "Unique": (175, 96, 37),
}
GEM_TEXT = (27, 217, 217)
GEM_BORDER = (25, 139, 139)
GEM_BACKGROUND = (5, 31, 34)
EQUIPMENT_CLASSES = (
    "Abyss Jewels",
    "Amulets",
    "Belts",
    "Body Armours",
    "Boots",
    "Bows",
    "Claws",
    "Daggers",
    "Gloves",
    "Helmets",
    "Hybrid Flasks",
    "Jewels",
    "Life Flasks",
    "Mana Flasks",
    "One Hand Axes",
    "One Hand Maces",
    "One Hand Swords",
    "Quivers",
    "Rings",
    "Rune Daggers",
    "Sceptres",
    "Shields",
    "Staves",
    "Thrusting One Hand Swords",
    "Tinctures",
    "Two Hand Axes",
    "Two Hand Maces",
    "Two Hand Swords",
    "Utility Flasks",
    "Wands",
    "Warstaves",
)


class FilterBuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class FilterBlock:
    action: str
    header: str
    lines: tuple[str, ...]
    start_line: int

    @property
    def directives(self) -> tuple[str, ...]:
        return tuple(
            line.strip()
            for line in self.lines[1:]
            if line.strip() and not line.lstrip().startswith("#")
        )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FilterBuildError(f"Could not read JSON {path}: {exc}") from exc


def quoted(values: Iterable[str]) -> str:
    return " ".join(f'"{value}"' for value in values)


def rgba(rgb: Sequence[int], alpha: int = 255) -> str:
    return f"{rgb[0]} {rgb[1]} {rgb[2]} {alpha}"


def mix(
    source: Sequence[int], target: Sequence[int], target_weight: float
) -> tuple[int, int, int]:
    return tuple(
        round(source[i] * (1.0 - target_weight) + target[i] * target_weight)
        for i in range(3)
    )


def hue_shift(rgb: Sequence[int], degrees: float) -> tuple[int, int, int]:
    r, g, b = (channel / 255.0 for channel in rgb)
    h, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    h = (h + degrees / 360.0) % 1.0
    shifted = colorsys.hls_to_rgb(h, lightness, saturation)
    return tuple(round(channel * 255) for channel in shifted)


def derive_palette(main_hex: str) -> dict[str, tuple[int, int, int]]:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", main_hex):
        raise FilterBuildError(f"Invalid main colour: {main_hex}")
    main = tuple(int(main_hex[i : i + 2], 16) for i in (1, 3, 5))
    black = (0, 0, 0)
    white = (255, 255, 255)
    return {
        "P-950": mix(main, black, 0.82),
        "P-900": mix(main, black, 0.70),
        "P-700": mix(main, black, 0.45),
        "P-500": main,
        # Approved Allie-inspired Velvet middle step. It is deliberately one
        # named token instead of a new per-category colour.
        "P-orchid": (200, 101, 242),
        "P-300": mix(main, white, 0.30),
        "P-100": mix(main, white, 0.72),
        "A-warm": hue_shift(main, 25.0),
        "N-950": (12, 12, 16),
        "N-700": (82, 82, 94),
        "N-300": (190, 190, 200),
        "N-50": (248, 248, 250),
        "I-ink": (19, 10, 29),
        "R-text": (172, 160, 188),
        "R-border": (100, 90, 112),
        "R-bg": (18, 16, 22),
        "U-optional-bg": (25, 13, 29),
    }


def parse_blocks(lines: Sequence[str]) -> list[FilterBlock]:
    starts: list[int] = []
    for index, line in enumerate(lines):
        if BLOCK_START_RE.match(line):
            starts.append(index)
    blocks: list[FilterBlock] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        match = BLOCK_START_RE.match(lines[start])
        assert match is not None
        blocks.append(
            FilterBlock(
                action=match.group(1),
                header=lines[start],
                lines=tuple(lines[start:end]),
                start_line=start + 1,
            )
        )
    return blocks


def iter_compact_blocks(lines: Sequence[str]) -> Iterator[tuple[str, list[str]]]:
    """Yield filter blocks ending at a blank line; used for tier extraction."""
    header: str | None = None
    body: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if BLOCK_START_RE.match(raw):
            if header is not None:
                yield header, body
            header = stripped
            body = []
            continue
        if header is None:
            continue
        if not stripped:
            yield header, body
            header = None
            body = []
            continue
        if not stripped.startswith("#"):
            body.append(stripped)
    if header is not None:
        yield header, body


def parse_basetypes(body: Sequence[str]) -> list[str]:
    names: list[str] = []
    for line in body:
        if line.startswith("BaseType"):
            names.extend(QUOTED_RE.findall(line))
    return names


def refresh_economy_snapshot() -> dict:
    request = urllib.request.Request(
        NEVERSINK_URL,
        headers={"User-Agent": "Pathcraft-AI filter snapshot builder"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
    except OSError as exc:
        raise FilterBuildError(
            f"Could not fetch official NeverSink source: {exc}"
        ) from exc

    text = raw.decode("utf-8-sig")
    version_match = re.search(r"^# VERSION:\s+([^\r\n]+)", text, re.MULTILINE)
    version = version_match.group(1).strip() if version_match else ""
    if version != NEVERSINK_VERSION:
        raise FilterBuildError(
            f"Expected NeverSink {NEVERSINK_VERSION} at pinned commit, found {version!r}"
        )

    unique_tiers: dict[str, list[str]] = {}
    currency_tiers: dict[str, list[str]] = {}
    divination_tiers: dict[str, list[str]] = {}
    for header, body in iter_compact_blocks(text.splitlines()):
        unique_match = re.search(r"\$type->uniques\s+\$tier->(t1|t2)\b", header)
        currency_match = re.search(
            r"\$type->currency\s+\$tier->(t1exalted|t2divine)\b", header
        )
        divination_match = re.search(
            r"\$type->divination\s+\$tier->(t1|t2|t3|t4c|t4|t5c|t5)\b",
            header,
        )
        if unique_match:
            unique_tiers[unique_match.group(1)] = parse_basetypes(body)
        if currency_match:
            currency_tiers[currency_match.group(1)] = parse_basetypes(body)
        if divination_match:
            divination_tiers[divination_match.group(1)] = parse_basetypes(body)

    required = {
        "unique": ({"t1", "t2"}, set(unique_tiers)),
        "currency": ({"t1exalted", "t2divine"}, set(currency_tiers)),
        "divination": (
            {"t1", "t2", "t3", "t4c", "t4", "t5c", "t5"},
            set(divination_tiers),
        ),
    }
    for label, (expected, actual) in required.items():
        if expected != actual:
            raise FilterBuildError(
                f"NeverSink {label} tiers incomplete: expected {sorted(expected)}, got {sorted(actual)}"
            )
    if any(
        not values
        for table in (unique_tiers, currency_tiers, divination_tiers)
        for values in table.values()
    ):
        raise FilterBuildError("NeverSink snapshot contains an empty required tier")

    payload = {
        "schema_version": "1.0",
        "dataset_kind": "poe1_neversink_economy_snapshot",
        "source": {
            "repository": "https://github.com/NeverSinkDev/NeverSink-Filter",
            "raw_url": NEVERSINK_URL,
            "commit": NEVERSINK_COMMIT,
            "version": version,
            "filter_type": "1-REGULAR",
            "style": "DEFAULT",
            "raw_sha256": sha256_bytes(raw),
            "refreshed_at_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        },
        "unique_tiers": unique_tiers,
        "currency_tiers": currency_tiers,
        "divination_tiers": divination_tiers,
    }
    ECONOMY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ECONOMY_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload


def validate_source_hashes() -> None:
    if not BASE_FILTER.exists():
        raise FilterBuildError(f"Composition source missing: {BASE_FILTER}")
    actual_base = sha256_file(BASE_FILTER)
    if actual_base != EXPECTED_BASE_SHA256:
        raise FilterBuildError(
            f"Composition source changed: expected {EXPECTED_BASE_SHA256}, got {actual_base}"
        )
    for path, expected in SOURCE_HASHES.items():
        if not path.exists():
            raise FilterBuildError(f"Original filter source missing: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise FilterBuildError(
                f"Original filter source changed: {path} expected {expected}, got {actual}"
            )


def render_block(
    title: str,
    conditions: Sequence[str],
    styles: Sequence[str],
    comments: Sequence[str] = (),
    action: str = "Show",
) -> list[str]:
    lines: list[str] = []
    lines.extend(f"# {comment}" for comment in comments)
    lines.append(f"{action} # {title}")
    lines.extend(f"    {condition}" for condition in conditions)
    lines.extend(f"    {style}" for style in styles)
    lines.append("")
    return lines


def velvet_value_style(
    palette: dict[str, tuple[int, int, int]],
    tier: str,
    *,
    shape: str,
    effect_color: str,
    sound: str | None = None,
    builtin_sound: str | None = None,
    show_icon: bool | None = None,
) -> list[str]:
    """Render the four-level Allie-inspired value ladder."""
    if sound and builtin_sound:
        raise FilterBuildError(
            "A style cannot combine custom and built-in alert sounds"
        )
    if tier == "T0":
        styles = [
            "SetFontSize 45",
            f"SetTextColor {rgba(palette['P-500'])}",
            f"SetBorderColor {rgba(palette['P-500'])}",
            f"SetBackgroundColor {rgba(palette['N-50'])}",
        ]
        icon_size = 0
        effect = f"PlayEffect {effect_color}"
    elif tier == "T1":
        styles = [
            "SetFontSize 45",
            f"SetTextColor {rgba(palette['N-50'])}",
            f"SetBorderColor {rgba(palette['P-100'])}",
            f"SetBackgroundColor {rgba(palette['P-500'])}",
        ]
        icon_size = 0
        effect = f"PlayEffect {effect_color}"
    elif tier == "BUILD":
        styles = [
            "SetFontSize 42",
            f"SetTextColor {rgba(palette['I-ink'])}",
            f"SetBorderColor {rgba(palette['P-500'])}",
            f"SetBackgroundColor {rgba(palette['P-orchid'], 245)}",
        ]
        icon_size = 1
        effect = f"PlayEffect {effect_color} Temp"
    elif tier == "ROUTINE":
        styles = [
            "SetFontSize 38",
            f"SetTextColor {rgba(palette['R-text'])}",
            f"SetBorderColor {rgba(palette['R-border'])}",
            f"SetBackgroundColor {rgba(palette['R-bg'], 245)}",
        ]
        icon_size = 2
        effect = ""
    elif tier == "QUIET":
        styles = [
            "SetFontSize 34",
            f"SetTextColor {rgba(palette['N-300'])}",
            f"SetBorderColor {rgba(palette['N-700'])}",
            f"SetBackgroundColor {rgba(palette['N-950'], 225)}",
        ]
        icon_size = 2
        effect = ""
    else:
        raise FilterBuildError(f"Unknown Violet Velvet value tier: {tier}")
    if sound:
        volume = {
            "T0": 300,
            "T1": 270,
            "BUILD": 230,
            "ROUTINE": 130,
            "QUIET": 90,
        }[tier]
        styles.append(f'CustomAlertSound "{sound}" {volume}')
    elif builtin_sound:
        styles.append(f"PlayAlertSound {builtin_sound}")
    else:
        styles.append("PlayAlertSound None")
    styles.append(effect if effect else "PlayEffect None")
    if show_icon is None:
        show_icon = tier in {"T0", "T1", "BUILD"}
    if show_icon:
        styles.append(f"MinimapIcon {icon_size} {effect_color} {shape}")
    else:
        styles.append("MinimapIcon -1")
    return styles


def build_relevance_style(
    palette: dict[str, tuple[int, int, int]],
    priority: str,
    *,
    shape: str,
    effect_color: str,
    sound: str | None = None,
) -> list[str]:
    """Highlight a build target without replacing its rarity text colour."""
    settings = {
        "required": (43, 245, f"PlayEffect {effect_color}", 1, "3 220"),
        "important": (41, 240, f"PlayEffect {effect_color} Temp", 1, "3 180"),
        "crafting": (37, 232, "PlayEffect None", 2, None),
    }
    if priority not in settings:
        raise FilterBuildError(f"Unknown build relevance priority: {priority}")
    font, alpha, effect, icon_size, default_builtin = settings[priority]
    styles = [
        f"SetFontSize {font}",
        f"SetBorderColor {rgba(palette['P-500'])}",
        f"SetBackgroundColor {rgba(palette['P-900'], alpha)}",
    ]
    if sound:
        styles.append(
            f'CustomAlertSound "{sound}" {300 if priority == "required" else 220}'
        )
    elif default_builtin:
        styles.append(f"PlayAlertSound {default_builtin}")
    else:
        styles.append("PlayAlertSound None")
    styles.extend(
        [
            effect,
            f"MinimapIcon {icon_size} {effect_color} {shape}",
        ]
    )
    return styles


def native_rare_safety_style() -> list[str]:
    """Quiet terminal style for broad HCSSF rare-equipment safety rules."""
    return [
        "SetFontSize 36",
        f"SetTextColor {rgba(RARITY_TEXT['Rare'])}",
        "SetBorderColor 140 120 41 255",
        "SetBackgroundColor 29 26 7 242",
        "PlayAlertSound None",
        "PlayEffect None",
        "MinimapIcon -1",
    ]


def native_gem_style(
    priority: str,
    *,
    effect_color: str,
    sound: str | None = None,
    builtin_sound: str | None = None,
) -> list[str]:
    if sound and builtin_sound:
        raise FilterBuildError(
            "A gem style cannot combine custom and built-in alert sounds"
        )
    settings = {
        "required": (45, f"PlayEffect {effect_color}", 0),
        "important": (42, f"PlayEffect {effect_color} Temp", 1),
        "routine": (38, "PlayEffect None", 2),
        "quiet": (34, "PlayEffect None", -1),
    }
    if priority not in settings:
        raise FilterBuildError(f"Unknown gem priority: {priority}")
    font, effect, icon_size = settings[priority]
    styles = [
        f"SetFontSize {font}",
        f"SetTextColor {rgba(GEM_TEXT)}",
        f"SetBorderColor {rgba(GEM_BORDER)}",
        f"SetBackgroundColor {rgba(GEM_BACKGROUND, 245)}",
    ]
    if sound:
        styles.append(
            f'CustomAlertSound "{sound}" {260 if priority == "required" else 220}'
        )
    elif builtin_sound:
        styles.append(f"PlayAlertSound {builtin_sound}")
    else:
        styles.append("PlayAlertSound None")
    styles.append(effect)
    styles.append(
        f"MinimapIcon {icon_size} {effect_color} Triangle"
        if icon_size >= 0
        else "MinimapIcon -1"
    )
    return styles


def render_audit_baseline(palette: dict[str, tuple[int, int, int]]) -> list[str]:
    classes = f"Class == {quoted(EQUIPMENT_CLASSES)}"
    lines = [
        SEPARATOR,
        "# PATHCRAFT FULL AUDIT BASELINE - VIOLET HCSSF EQUIPMENT COVERAGE",
        "# These Continue rules only provide a rarity baseline; later specific rules may override them.",
        SEPARATOR,
    ]
    lines += render_block(
        "PATHCRAFT HCSSF - NORMAL EQUIPMENT FALLBACK",
        [classes, "Rarity Normal"],
        [
            "SetFontSize 34",
            f"SetTextColor {rgba(RARITY_TEXT['Normal'])}",
            "SetBorderColor 90 88 96 255",
            "SetBackgroundColor 17 17 20 240",
            "Continue",
        ],
    )
    lines += render_block(
        "PATHCRAFT HCSSF - MAGIC EQUIPMENT FALLBACK",
        [classes, "Rarity Magic"],
        [
            "SetFontSize 35",
            f"SetTextColor {rgba(RARITY_TEXT['Magic'])}",
            "SetBorderColor 80 85 142 255",
            "SetBackgroundColor 14 14 34 240",
            "Continue",
        ],
    )
    lines += render_block(
        "PATHCRAFT HCSSF - RARE EQUIPMENT FALLBACK",
        [classes, "Rarity Rare"],
        [
            "SetFontSize 36",
            f"SetTextColor {rgba(RARITY_TEXT['Rare'])}",
            "SetBorderColor 140 120 41 255",
            "SetBackgroundColor 29 26 7 242",
            "Continue",
        ],
    )
    return lines


def render_native_category_policy() -> list[str]:
    return [
        SEPARATOR,
        "# PATHCRAFT VIOLET VELVET - NATIVE CATEGORY CUES PRESERVED",
        "# No global purple wash: ordinary uniques stay brown, gems cyan, maps native,",
        "# six-links red and quest items green. Violet is reserved for value/relevance.",
        SEPARATOR,
        "",
    ]


def render_rarity_guard() -> list[str]:
    """Apply final semantic text colours after imported Continue decorators."""
    classes = f"Class == {quoted(EQUIPMENT_CLASSES)}"
    lines = [
        SEPARATOR,
        "# SMOKIEZONE VIOLET VELVET - NATIVE TEXT COLOUR GUARD",
        "# Text communicates rarity/category; later terminal rules communicate value and urgency.",
        SEPARATOR,
        "",
    ]
    for rarity in ("Normal", "Magic", "Rare"):
        lines += render_block(
            f"SMOKIEZONE - {rarity.upper()} EQUIPMENT TEXT GUARD",
            [classes, f"Rarity {rarity}"],
            [
                f"SetTextColor {rgba(RARITY_TEXT[rarity])}",
                "Continue",
            ],
        )
    lines += render_block(
        "SMOKIEZONE - ORDINARY UNIQUE TEXT GUARD",
        ["Rarity Unique"],
        [
            f"SetTextColor {rgba(RARITY_TEXT['Unique'])}",
            "Continue",
        ],
    )
    lines += render_block(
        "SMOKIEZONE - NATIVE GEM TEXT GUARD",
        ['Class == "Skill Gems" "Support Gems"'],
        [
            f"SetTextColor {rgba(GEM_TEXT)}",
            "Continue",
        ],
    )
    return lines


def extract_essence_buckets() -> dict[str, list[str]]:
    """Partition every current POE1 essence currency into one visual value tier."""
    base_items = read_json(REPO_ROOT / "data" / "game_data" / "BaseItemTypes.json")
    essence_names = {
        row["Name"]
        for row in base_items
        if row.get("Name")
        and str(row.get("Id", "")).startswith(
            "Metadata/Items/Currency/CurrencyEssence"
        )
    }
    essence_names.add("Remnant of Corruption")

    buckets: dict[str, list[str]] = {
        "high": [],
        "important": [],
        "routine": [],
        "quiet": [],
    }
    for name in sorted(essence_names):
        if name == "Remnant of Corruption" or name.startswith(
            ("Deafening Essence of ", "Essence of ")
        ):
            buckets["high"].append(name)
        elif name.startswith("Shrieking Essence of "):
            buckets["important"].append(name)
        elif name.startswith(("Screaming Essence of ", "Wailing Essence of ")):
            buckets["routine"].append(name)
        elif name.startswith(
            (
                "Weeping Essence of ",
                "Muttering Essence of ",
                "Whispering Essence of ",
            )
        ):
            buckets["quiet"].append(name)
        else:
            raise FilterBuildError(f"Unclassified 3.29 essence BaseType: {name}")

    assigned = [name for names in buckets.values() for name in names]
    if len(assigned) != len(set(assigned)) or set(assigned) != essence_names:
        raise FilterBuildError("Essence visual ladder does not partition the universe")
    if any(not names for names in buckets.values()):
        raise FilterBuildError("Essence visual ladder contains an empty tier")
    return buckets


def render_essence_visual_ladder(
    palette: dict[str, tuple[int, int, int]],
) -> list[str]:
    """Override imported essence colours without changing visibility or sounds."""
    buckets = extract_essence_buckets()
    styles = {
        "high": [
            f"SetTextColor {rgba(palette['N-50'])}",
            f"SetBorderColor {rgba(palette['P-100'])}",
            f"SetBackgroundColor {rgba(palette['P-500'], 250)}",
            "Continue",
        ],
        "important": [
            f"SetTextColor {rgba(palette['P-100'])}",
            f"SetBorderColor {rgba(palette['P-300'])}",
            f"SetBackgroundColor {rgba(palette['P-700'], 245)}",
            "Continue",
        ],
        "routine": [
            f"SetTextColor {rgba(palette['P-300'])}",
            f"SetBorderColor {rgba(palette['P-500'])}",
            f"SetBackgroundColor {rgba(palette['P-900'], 240)}",
            "Continue",
        ],
        "quiet": [
            f"SetTextColor {rgba(palette['N-300'])}",
            f"SetBorderColor {rgba(palette['P-700'])}",
            f"SetBackgroundColor {rgba(palette['P-950'], 225)}",
            "Continue",
        ],
    }
    titles = {
        "high": "SMOKIEZONE - ESSENCES HIGH VIOLET",
        "important": "SMOKIEZONE - ESSENCES IMPORTANT VIOLET",
        "routine": "SMOKIEZONE - ESSENCES ROUTINE VIOLET",
        "quiet": "SMOKIEZONE - ESSENCES QUIET VIOLET",
    }
    lines = [
        SEPARATOR,
        "# SMOKIEZONE VIOLET VELVET - ESSENCE VALUE LADDER",
        "# Colour-only Continue rules replace legacy red/white essence colours.",
        "# Visibility, font size, sounds, beams and icons remain owned by their layers.",
        SEPARATOR,
        "",
    ]
    for key in ("high", "important", "routine", "quiet"):
        lines += render_block(
            titles[key],
            [
                'Class == "Stackable Currency"',
                f"BaseType == {quoted(buckets[key])}",
            ],
            styles[key],
        )
    return lines


def extract_card_sources(
    base_lines: Sequence[str],
) -> tuple[list[str], list[str], dict[str, list[str]]]:
    without_generated: list[str] = []
    skipping = False
    for line in base_lines:
        if line == OLD_CARD_BEGIN:
            skipping = True
            continue
        if line == OLD_CARD_END:
            skipping = False
            continue
        if not skipping:
            without_generated.append(line)

    filter_cards: set[str] = set()
    for header, body in iter_compact_blocks(without_generated):
        if header.startswith("Show # LUMINARY -"):
            continue
        if not any(
            line.startswith("Class") and "Divination Card" in line for line in body
        ):
            continue
        filter_cards.update(parse_basetypes(body))

    ggpk = read_json(REPO_ROOT / "data" / "game_data" / "BaseItemTypes.json")
    ggpk_cards = {
        row["Name"]
        for row in ggpk
        if str(row.get("Id", "")).startswith("Metadata/Items/DivinationCards/")
        and row.get("ItemClassesKey") == 42
        and row.get("Name")
    }
    universe = sorted(ggpk_cards | filter_cards)

    league_marker = next(
        (i for i, line in enumerate(base_lines) if "### LEAGUE / NEW ITEMS" in line),
        None,
    )
    if league_marker is None:
        raise FilterBuildError(
            "League/new item marker is missing from composition source"
        )
    league_cards: list[str] = []
    for header, body in iter_compact_blocks(base_lines[league_marker:]):
        if any(line.startswith("Class") and "Divination Card" in line for line in body):
            league_cards = parse_basetypes(body)
            break
    if not league_cards:
        raise FilterBuildError("Could not extract the 3.29 league divination-card list")

    markers = {
        "ssf_wanted": "You've Got to be Kidding",
        "ssf_notable": '"Absolutely!" Div Cards',
        "ssf_dontcare": "Don't Care if I Miss Them",
    }
    preferences: dict[str, list[str]] = {}
    for key, marker in markers.items():
        for header, body in iter_compact_blocks(base_lines):
            if marker in header:
                preferences[key] = parse_basetypes(body)
                break
        if key not in preferences:
            raise FilterBuildError(f"Missing Wrecker card preference list: {marker}")
    return universe, league_cards, preferences


def assign_card_buckets(
    universe: Sequence[str],
    economy: dict,
    league_cards: Sequence[str],
    preferences: dict[str, list[str]],
    spec: dict,
) -> dict[str, list[str]]:
    build_cards = spec.get("divination_cards", {})
    build_target = [entry["card"] for entry in build_cards.get("build_target", [])]
    build_keep = [entry["card"] for entry in build_cards.get("keep", [])]
    div = economy["divination_tiers"]
    order = [
        ("build_target", build_target),
        ("build_keep", build_keep),
        ("league_new", league_cards),
        ("t0", div["t1"]),
        ("t1", div["t2"]),
        ("ssf_wanted", preferences["ssf_wanted"]),
        ("t2", div["t3"]),
        ("ssf_notable", preferences["ssf_notable"]),
        ("t3", div["t4c"]),
        ("t4", div["t4"]),
        ("bulk", div["t5c"]),
        ("low", div["t5"]),
    ]
    known = set(universe)
    taken: set[str] = set()
    buckets: dict[str, list[str]] = {}
    for key, candidates in order:
        picked = sorted(
            {card for card in candidates if card in known and card not in taken}
        )
        buckets[key] = picked
        taken.update(picked)
    buckets["untiered"] = sorted(known - taken)
    if sum(len(values) for values in buckets.values()) != len(universe):
        raise FilterBuildError(
            "Divination card ladder does not partition the card universe"
        )
    return buckets


def render_card_ladder(
    buckets: dict[str, list[str]],
    palette: dict[str, tuple[int, int, int]],
    effect_color: str,
    total_cards: int,
) -> list[str]:
    styles = {
        "build_target": velvet_value_style(
            palette,
            "T1",
            shape="Square",
            effect_color=effect_color,
            sound="DivinationCard.mp3",
        ),
        "build_keep": velvet_value_style(
            palette,
            "BUILD",
            shape="Square",
            effect_color=effect_color,
            sound="DivinationCard.mp3",
        ),
        "league_new": velvet_value_style(
            palette,
            "BUILD",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="12 300",
        ),
        "t0": velvet_value_style(
            palette,
            "T0",
            shape="Square",
            effect_color=effect_color,
            sound="HolyMotherfuckingShit.mp3",
        ),
        "t1": velvet_value_style(
            palette,
            "T1",
            shape="Square",
            effect_color=effect_color,
            sound="Thatsworthsomething.mp3",
        ),
        "ssf_wanted": velvet_value_style(
            palette,
            "T1",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="1 300",
        ),
        "t2": velvet_value_style(
            palette,
            "BUILD",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="2 280",
        ),
        "ssf_notable": velvet_value_style(
            palette,
            "ROUTINE",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="12 240",
            show_icon=True,
        ),
        "t3": velvet_value_style(
            palette,
            "ROUTINE",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="2 200",
            show_icon=True,
        ),
        "stack": velvet_value_style(
            palette,
            "ROUTINE",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="2 180",
            show_icon=True,
        ),
        "t4": velvet_value_style(
            palette,
            "ROUTINE",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="12 160",
            show_icon=False,
        ),
        "bulk": velvet_value_style(
            palette,
            "QUIET",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="12 120",
            show_icon=False,
        ),
        "low": velvet_value_style(
            palette,
            "QUIET",
            shape="Square",
            effect_color=effect_color,
            builtin_sound="12 100",
            show_icon=False,
        ),
    }
    titles = {
        "build_target": "SMOKIEZONE - BUILD TARGET DIVINATION CARDS",
        "build_keep": "SMOKIEZONE - GUIDE KEEP DIVINATION CARDS",
        "league_new": "SMOKIEZONE - LEAGUE NEW DIVINATION CARDS",
        "t0": "SMOKIEZONE - DIVINATION CARDS T0",
        "t1": "SMOKIEZONE - DIVINATION CARDS T1",
        "ssf_wanted": "SMOKIEZONE - DIVINATION CARDS HCSSF WANTED",
        "t2": "SMOKIEZONE - DIVINATION CARDS T2",
        "ssf_notable": "SMOKIEZONE - DIVINATION CARDS HCSSF NOTABLE",
        "t3": "SMOKIEZONE - DIVINATION CARDS T3",
        "stack": "SMOKIEZONE - DIVINATION CARDS STACK 3+",
        "t4": "SMOKIEZONE - DIVINATION CARDS T4",
        "bulk": "SMOKIEZONE - DIVINATION CARDS BULK",
        "low": "SMOKIEZONE - DIVINATION CARDS LOW",
    }
    lines = [
        NEW_CARD_BEGIN,
        f"# {total_cards} known cards resolve to exactly one terminal Show rule.",
        "# Build targets are empty because the guide names no divination-card farm.",
        "# The unconditional magenta catch-all protects future or unclassified cards.",
        SEPARATOR,
        "",
    ]
    for key in (
        "build_target",
        "build_keep",
        "league_new",
        "t0",
        "t1",
        "ssf_wanted",
        "t2",
        "ssf_notable",
        "t3",
    ):
        cards = buckets[key]
        if not cards:
            continue
        lines += render_block(
            titles[key],
            ['Class == "Divination Cards"', f"BaseType == {quoted(cards)}"],
            styles[key],
        )

    quiet_cards = sorted(buckets["t4"] + buckets["bulk"] + buckets["low"])
    lines += render_block(
        titles["stack"],
        [
            "StackSize >= 3",
            'Class == "Divination Cards"',
            f"BaseType == {quoted(quiet_cards)}",
        ],
        styles["stack"],
    )
    for key in ("t4", "bulk", "low"):
        if buckets[key]:
            lines += render_block(
                titles[key],
                ['Class == "Divination Cards"', f"BaseType == {quoted(buckets[key])}"],
                styles[key],
            )
    lines += render_block(
        "SMOKIEZONE - DIVINATION CARDS UNTIERED CATCH-ALL",
        ['Class == "Divination Cards"'],
        [
            "SetFontSize 45",
            "SetTextColor 255 0 255 255",
            "SetBorderColor 255 0 255 255",
            "SetBackgroundColor 100 0 100 255",
            "PlayAlertSound 3 300",
            "PlayEffect Pink",
            "MinimapIcon 0 Pink UpsideDownHouse",
        ],
    )
    lines.extend([NEW_CARD_END, ""])
    return lines


def render_link_rules(
    palette: dict[str, tuple[int, int, int]], effect_color: str, progression: dict
) -> list[str]:
    campaign_max = progression["campaign_max_area_level"]
    lines: list[str] = []
    rarity_text = {
        rarity: rgba(RARITY_TEXT[rarity]) for rarity in ("Normal", "Magic", "Rare")
    }
    for rarity, text in rarity_text.items():
        lines += render_block(
            f"SMOKIEZONE - FIVE LINK {rarity.upper()}",
            [f"Rarity {rarity}", "LinkedSockets = 5"],
            [
                "SetFontSize 45",
                f"SetTextColor {text}",
                f"SetBorderColor {rgba(palette['P-100'])}",
                f"SetBackgroundColor {rgba(palette['P-700'])}",
                'CustomAlertSound "5Link.mp3" 260',
                f"PlayEffect {effect_color}",
                f"MinimapIcon 1 {effect_color} Diamond",
            ],
        )
    for rarity, text in rarity_text.items():
        lines += render_block(
            f"SMOKIEZONE - FOUR LINK {rarity.upper()} CAMPAIGN",
            [f"AreaLevel <= {campaign_max}", f"Rarity {rarity}", "LinkedSockets >= 4"],
            [
                "SetFontSize 40",
                f"SetTextColor {text}",
                f"SetBorderColor {rgba(palette['P-300'])}",
                f"SetBackgroundColor {rgba(palette['P-900'])}",
                "PlayAlertSound 3 150",
                f"PlayEffect {effect_color} Temp",
                f"MinimapIcon 2 {effect_color} Diamond",
            ],
        )
    for rarity, text in rarity_text.items():
        lines += render_block(
            f"SMOKIEZONE - THREE LINK {rarity.upper()} EARLY CAMPAIGN",
            ["AreaLevel <= 25", f"Rarity {rarity}", "LinkedSockets >= 3"],
            [
                "SetFontSize 36",
                f"SetTextColor {text}",
                f"SetBorderColor {rgba(palette['P-700'])}",
                f"SetBackgroundColor {rgba(palette['P-950'])}",
                "PlayAlertSound None",
                "PlayEffect Grey Temp",
                "MinimapIcon 2 Grey Diamond",
            ],
        )
    return lines


def render_crafting_bases(
    spec: dict, palette: dict[str, tuple[int, int, int]], effect_color: str
) -> list[str]:
    lines: list[str] = []
    for group in spec["crafting_base_groups"]:
        conditions: list[str] = []
        if group.get("minimum_item_level") is not None:
            conditions.append(f"ItemLevel >= {group['minimum_item_level']}")
        if group.get("maximum_area_level") is not None:
            conditions.append(f"AreaLevel <= {group['maximum_area_level']}")
        if group.get("mirrored") is False:
            conditions.append("Mirrored False")
        if group.get("corrupted") is False:
            conditions.append("Corrupted False")
        conditions.append(f"Rarity {' '.join(group['rarities'])}")
        conditions.append(f"BaseType == {quoted(group['base_types'])}")
        comments = [f"Source: {group['source_section']}"]
        if group.get("rationale"):
            comments.append(group["rationale"])
        if group.get("always_show"):
            comments.append(
                "Approved crafting base: terminal Show at every AreaLevel whenever all listed conditions match."
            )
        lines += render_block(
            f"SMOKIEZONE - {group['id'].upper()}",
            conditions,
            build_relevance_style(
                palette,
                group["priority"],
                shape="Diamond",
                effect_color=effect_color,
            ),
            comments,
        )
    return lines


def render_resource_groups(
    spec: dict, palette: dict[str, tuple[int, int, int]], effect_color: str
) -> list[str]:
    lines: list[str] = []
    for group in spec["resource_groups"]:
        conditions: list[str] = []
        if group.get("classes"):
            conditions.append(f"Class == {quoted(group['classes'])}")
        if group.get("base_types"):
            operator = (
                "BaseType ==" if group.get("match_mode") == "exact" else "BaseType"
            )
            conditions.append(f"{operator} {quoted(group['base_types'])}")
        shape = group.get("minimap_shape", "Cross")
        if group["id"] == "build.resources.core":
            style = velvet_value_style(
                palette,
                "BUILD",
                shape=shape,
                effect_color=effect_color,
                sound="ProbPickUp.mp3",
            )
        elif group["priority"] == "important":
            style = velvet_value_style(
                palette,
                "BUILD",
                shape=shape,
                effect_color=effect_color,
                builtin_sound="2 210",
            )
        else:
            style = velvet_value_style(
                palette,
                "BUILD",
                shape=shape,
                effect_color=effect_color,
                builtin_sound="2 170",
            )
        lines += render_block(
            f"SMOKIEZONE - {group['id'].upper()}",
            conditions,
            style,
            [f"Source: {group['source_section']}"],
        )
    return lines


def render_gem_rules(
    spec: dict, palette: dict[str, tuple[int, int, int]], effect_color: str
) -> list[str]:
    lines: list[str] = []
    for gem in spec["gem_targets"]:
        priority = "required" if gem["priority"] == "required" else "important"
        styles = native_gem_style(
            priority,
            effect_color=effect_color,
            sound="Shiny.mp3",
        )
        conditions = [f"Class == {quoted(gem['classes'])}"]
        if gem.get("transfigured_gem_names"):
            conditions.append(
                f"TransfiguredGem {quoted(gem['transfigured_gem_names'])}"
            )
        else:
            conditions.append(f"BaseType == {quoted(gem['base_types'])}")
        lines += render_block(
            f"SMOKIEZONE - TARGET GEM {gem['id'].upper()}",
            conditions,
            styles,
            [f"Source: {gem['source_section']}"],
        )
    premium_style = native_gem_style(
        "important",
        effect_color=effect_color,
        sound="Shiny.mp3",
    )
    lines += render_block(
        "SMOKIEZONE - PREMIUM TRANSFIGURED GEMS",
        ['Class "Gem"', "TransfiguredGem True"],
        premium_style,
    )
    lines += render_block(
        "SMOKIEZONE - PREMIUM NAMED GEMS",
        [
            'Class "Gem"',
            'BaseType "Awakened" "Vaal" "Empower Support" "Enhance Support" "Enlighten Support" "Portal" "Item Quantity Support"',
        ],
        premium_style,
    )
    lines += render_block(
        "SMOKIEZONE - QUALITY GEMS",
        ['Class "Gem"', "Quality >= 10"],
        native_gem_style(
            "routine",
            effect_color=effect_color,
            builtin_sound="12 90",
        ),
    )
    lines += render_block(
        "SMOKIEZONE - CAMPAIGN GEMS",
        ['Class "Gem"', "AreaLevel < 45"],
        native_gem_style("quiet", effect_color=effect_color),
    )
    return lines


def render_flask_rules(
    spec: dict, palette: dict[str, tuple[int, int, int]], effect_color: str
) -> list[str]:
    bases = sorted(
        {base for group in spec["flask_targets"] for base in group["base_types"]}
    )
    early_maps = spec["progression"]["early_maps_max_area_level"]
    endgame = spec["progression"]["endgame_min_area_level"]
    lines = render_block(
        "HCSSF - QUALITY CORE FLASK BASES",
        ["Rarity Normal Magic", "Quality >= 10", f"BaseType == {quoted(bases)}"],
        build_relevance_style(
            palette,
            "important",
            shape="Raindrop",
            effect_color=effect_color,
        ),
    )
    lines += render_block(
        "HCSSF - CORE FLASK BASES THROUGH RED MAPS",
        [
            f"AreaLevel <= {early_maps}",
            "Rarity Normal Magic",
            f"BaseType == {quoted(bases)}",
        ],
        build_relevance_style(
            palette,
            "crafting",
            shape="Raindrop",
            effect_color=effect_color,
        ),
        [
            "Life, speed and elemental mitigation flask bases stay prominent while gearing."
        ],
    )
    lines += render_block(
        "HCSSF - CORE FLASK BASES IN ENDGAME",
        [
            f"AreaLevel >= {endgame}",
            "Rarity Normal Magic",
            f"BaseType == {quoted(bases)}",
        ],
        [
            "SetFontSize 34",
            f"SetBorderColor {rgba(palette['P-700'])}",
            f"SetBackgroundColor {rgba(palette['R-bg'], 225)}",
            "PlayAlertSound None",
            "PlayEffect None",
            "MinimapIcon -1",
        ],
        [
            "HCSSF never assumes the flask setup is finished; endgame drops are shown quietly."
        ],
    )
    return lines


def render_hcssf_safety(
    palette: dict[str, tuple[int, int, int]], effect_color: str, progression: dict
) -> list[str]:
    early_maps = progression["early_maps_max_area_level"]
    relevant_armour_jewellery = (
        'Class == "Amulets" "Belts" "Body Armours" "Boots" "Gloves" "Helmets" "Rings"'
    )
    lines = render_block(
        "HCSSF - RARE ARMOUR AND JEWELLERY THROUGH RED MAPS",
        [
            f"AreaLevel <= {early_maps}",
            "Rarity Rare",
            relevant_armour_jewellery,
        ],
        native_rare_safety_style(),
        ["Life, resistances and armour upgrades stay visible longer for HCSSF."],
    )
    lines += render_block(
        "HCSSF - RARE TWO HAND AXES THROUGH RED MAPS",
        [
            f"AreaLevel <= {early_maps}",
            "Rarity Rare",
            'Class == "Two Hand Axes"',
        ],
        native_rare_safety_style(),
        [
            "Unidentified rare axes remain inspectable until the endgame craft is established."
        ],
    )
    return lines


def render_utility_currency(
    palette: dict[str, tuple[int, int, int]], effect_color: str, progression: dict
) -> list[str]:
    campaign_max = progression["campaign_max_area_level"]
    basic = [
        "Armourer's Scrap",
        "Blacksmith's Whetstone",
        "Glassblower's Bauble",
        "Gemcutter's Prism",
        "Orb of Transmutation",
        "Orb of Augmentation",
        "Orb of Alteration",
        "Chromatic Orb",
        "Jeweller's Orb",
        "Orb of Fusing",
        "Orb of Chance",
        "Orb of Alchemy",
        "Orb of Binding",
        "Orb of Scouring",
        "Orb of Regret",
        "Vaal Orb",
        "Blessed Orb",
        "Regal Orb",
        "Cartographer's Chisel",
    ]
    useful = [
        "Glassblower's Bauble",
        "Gemcutter's Prism",
        "Orb of Alteration",
        "Chromatic Orb",
        "Jeweller's Orb",
        "Orb of Fusing",
        "Orb of Alchemy",
        "Orb of Binding",
        "Orb of Scouring",
        "Orb of Regret",
        "Vaal Orb",
        "Blessed Orb",
        "Regal Orb",
        "Cartographer's Chisel",
    ]
    low = [
        "Armourer's Scrap",
        "Blacksmith's Whetstone",
        "Orb of Transmutation",
        "Orb of Augmentation",
        "Orb of Chance",
    ]
    lines = render_block(
        "HCSSF - WISDOM SCROLLS CAMPAIGN",
        ['BaseType == "Scroll of Wisdom"', f"AreaLevel <= {campaign_max}"],
        [
            "SetFontSize 42",
            "SetTextColor 255 255 255 255",
            "SetBorderColor 190 190 190 255",
            "SetBackgroundColor 35 35 35 245",
            'CustomAlertSound "Wisdom.mp3" 90',
            "PlayEffect None",
            "MinimapIcon -1",
        ],
    )
    lines += render_block(
        "HCSSF - WISDOM SCROLLS MAP STACK",
        ['BaseType == "Scroll of Wisdom"', "AreaLevel >= 68", "StackSize >= 5"],
        velvet_value_style(
            palette,
            "ROUTINE",
            shape="Cross",
            effect_color=effect_color,
            sound="Wisdom.mp3",
            show_icon=False,
        ),
    )
    lines += render_block(
        "HCSSF - WISDOM SCROLLS MAP SINGLE",
        ['BaseType == "Scroll of Wisdom"', "AreaLevel >= 68"],
        velvet_value_style(
            palette, "QUIET", shape="Cross", effect_color=effect_color, show_icon=False
        ),
    )
    lines += render_block(
        "HCSSF - PORTAL SCROLLS CAMPAIGN",
        ['BaseType == "Portal Scroll"', f"AreaLevel <= {campaign_max}"],
        [
            "SetFontSize 42",
            "SetTextColor 170 220 255 255",
            "SetBorderColor 90 180 255 255",
            "SetBackgroundColor 10 45 85 245",
            'CustomAlertSound "Portal.mp3" 90',
            "PlayEffect None",
            "MinimapIcon -1",
        ],
    )
    lines += render_block(
        "HCSSF - PORTAL SCROLLS MAP STACK",
        ['BaseType == "Portal Scroll"', "AreaLevel >= 68", "StackSize >= 5"],
        [
            "SetFontSize 40",
            "SetTextColor 190 220 245 255",
            "SetBorderColor 80 140 195 255",
            "SetBackgroundColor 10 30 55 235",
            'CustomAlertSound "Portal.mp3" 70',
            "PlayEffect None",
            "MinimapIcon -1",
        ],
    )
    lines += render_block(
        "HCSSF - PORTAL SCROLLS MAP SINGLE",
        ['BaseType == "Portal Scroll"', "AreaLevel >= 68"],
        [
            "SetFontSize 34",
            "SetTextColor 155 180 205 255",
            "SetBorderColor 60 95 125 255",
            "SetBackgroundColor 10 20 32 220",
            "PlayAlertSound None",
            "PlayEffect None",
            "MinimapIcon -1",
        ],
    )
    lines += render_block(
        "HCSSF - BASIC CRAFTING CURRENCY CAMPAIGN",
        [f"BaseType == {quoted(basic)}", f"AreaLevel <= {campaign_max}"],
        velvet_value_style(
            palette,
            "ROUTINE",
            shape="Cross",
            effect_color=effect_color,
            builtin_sound="2 130",
            show_icon=False,
        ),
    )
    lines += render_block(
        "HCSSF - BASIC CRAFTING CURRENCY MAP STACK",
        [f"BaseType == {quoted(basic)}", "AreaLevel >= 68", "StackSize >= 5"],
        velvet_value_style(
            palette,
            "ROUTINE",
            shape="Cross",
            effect_color=effect_color,
            builtin_sound="2 140",
            show_icon=False,
        ),
    )
    lines += render_block(
        "HCSSF - USEFUL CRAFTING CURRENCY MAP SINGLE",
        [f"BaseType == {quoted(useful)}", "AreaLevel >= 68"],
        velvet_value_style(
            palette,
            "ROUTINE",
            shape="Cross",
            effect_color=effect_color,
            show_icon=False,
        ),
    )
    lines += render_block(
        "HCSSF - LOW CRAFTING CURRENCY MAP SINGLE",
        [f"BaseType == {quoted(low)}", "AreaLevel >= 68"],
        velvet_value_style(
            palette, "QUIET", shape="Cross", effect_color=effect_color, show_icon=False
        ),
    )
    return lines


def render_build_layer(
    spec: dict, economy: dict, base_lines: Sequence[str]
) -> list[str]:
    palette = derive_palette(spec["theme"]["main_color"])
    effect_color = spec["theme"]["poe_effect_color"]
    progression = spec["progression"]
    required_bases = sorted(
        {
            base
            for target in spec["unique_targets"]
            if target["priority"] == "required"
            for base in target["resolved_base_types"]
        }
    )
    optional_bases = sorted(
        {
            base
            for target in spec["unique_targets"]
            if target["priority"] == "optional"
            for base in target["resolved_base_types"]
        }
    )

    lines = [
        SEPARATOR,
        "# PATHCRAFT: SMOKIEZONE HYDROSPHERE BONESHATTER 3.29 HCSSF TARGETS",
        "# Output: one automatic progressive filter; theme: violet #7C3AED.",
        "# Visibility authority remains the preserved Wrecker SSF source; this layer adds HCSSF safety Shows.",
        "# Exact targets come from the canonical JSON spec, not from every item equipped in a PoB snapshot.",
        "# Endgame crafting tiers use ItemLevel; AreaLevel only controls broad campaign/map progression.",
        SEPARATOR,
        "",
    ]
    lines += render_rarity_guard()
    lines += render_essence_visual_ladder(palette)
    lines += render_block(
        "SMOKIEZONE - SIX LINK SAFETY",
        ["LinkedSockets >= 6"],
        [
            "SetFontSize 45",
            "SetTextColor 255 255 255 255",
            "SetBorderColor 255 255 255 255",
            "SetBackgroundColor 200 0 0 255",
            'CustomAlertSound "6Link.mp3" 300',
            "PlayEffect Red",
            "MinimapIcon 0 Red Diamond",
        ],
    )
    lines += render_block(
        "SMOKIEZONE - DEAD MAN'S SULPHUR",
        ['BaseType == "Dead Man\'s Sulphur"'],
        [
            "SetFontSize 45",
            "SetTextColor 215 255 145 255",
            "SetBorderColor 145 255 20 255",
            "SetBackgroundColor 8 38 8 255",
            'CustomAlertSound "Shiny.mp3" 210',
            "PlayEffect Green",
            "MinimapIcon 0 Green Star",
        ],
    )
    lines += render_block(
        "SMOKIEZONE - QUEST ITEMS DARK GREEN",
        ['Class "Quest" "Atlas Upgrade Item"'],
        [
            "SetFontSize 45",
            "SetTextColor 210 255 215 255",
            "SetBorderColor 55 165 80 255",
            "SetBackgroundColor 0 42 20 250",
            'CustomAlertSound "Quest Item.mp3" 240',
            "PlayEffect Green Temp",
            "MinimapIcon 0 Green Circle",
        ],
    )
    lines += render_block(
        "SMOKIEZONE - ALLFLAME CHARTS",
        ['Class == "Chart"'],
        [
            "SetFontSize 45",
            "SetTextColor 255 255 255 255",
            "SetBorderColor 80 220 210 255",
            "SetBackgroundColor 0 45 55 255",
            "PlayAlertSound None",
            "PlayEffect Blue",
        ],
    )
    lines += render_block(
        "SMOKIEZONE - CORE REQUIRED UNIQUE BASES",
        ["Rarity Unique", f"BaseType == {quoted(required_bases)}"],
        [
            "SetFontSize 45",
            f"SetTextColor {rgba(palette['N-50'])}",
            f"SetBorderColor {rgba(palette['P-orchid'])}",
            f"SetBackgroundColor {rgba(palette['P-900'], 248)}",
            'CustomAlertSound "MyPrecious.mp3" 300',
            f"PlayEffect {effect_color}",
            f"MinimapIcon 0 {effect_color} Star",
        ],
        [
            "Soul Tether/Replica Soul Tether share Cloth Belt; The Burden of Truth uses Crystal Belt.",
            "Unidentified unique-base matching can also show other uniques on the same bases.",
        ],
    )

    unique_tiers = economy["unique_tiers"]
    currency_tiers = economy["currency_tiers"]
    lines += render_block(
        "SMOKIEZONE - GLOBAL T0 UNIQUE BASES",
        ["Rarity Unique", f"BaseType == {quoted(unique_tiers['t1'])}"],
        velvet_value_style(
            palette,
            "T0",
            shape="Star",
            effect_color=effect_color,
            sound="HolyMotherfuckingShit.mp3",
        ),
    )
    lines += render_block(
        "SMOKIEZONE - GLOBAL T0 CURRENCY",
        [
            'Class == "Stackable Currency"',
            f"BaseType == {quoted(currency_tiers['t1exalted'])}",
        ],
        velvet_value_style(
            palette,
            "T0",
            shape="Cross",
            effect_color=effect_color,
            sound="HolyMotherfuckingShit.mp3",
        ),
    )
    lines += render_block(
        "SMOKIEZONE - GLOBAL HIGH VALUE UNIQUE BASES",
        ["Rarity Unique", f"BaseType == {quoted(unique_tiers['t2'])}"],
        velvet_value_style(
            palette,
            "T1",
            shape="Star",
            effect_color=effect_color,
            sound="Thatsworthsomething.mp3",
        ),
    )
    lines += render_block(
        "SMOKIEZONE - GLOBAL HIGH VALUE CURRENCY",
        [
            'Class == "Stackable Currency"',
            f"BaseType == {quoted(currency_tiers['t2divine'])}",
        ],
        velvet_value_style(
            palette,
            "T1",
            shape="Cross",
            effect_color=effect_color,
            sound="Thatsworthsomething.mp3",
        ),
    )

    lines += render_link_rules(palette, effect_color, progression)
    lines += render_block(
        "SMOKIEZONE - OPTIONAL UNIQUE BASES",
        ["Rarity Unique", f"BaseType == {quoted(optional_bases)}"],
        [
            "SetFontSize 38",
            f"SetTextColor {rgba(RARITY_TEXT['Unique'])}",
            f"SetBorderColor {rgba(palette['P-500'])}",
            f"SetBackgroundColor {rgba(palette['U-optional-bg'], 245)}",
            "PlayAlertSound None",
            "PlayEffect None",
            f"MinimapIcon 2 {effect_color} Star",
        ],
        [
            "Stormblood is a late crit variant, not a league-start requirement.",
            "Unidentified Sapphire Flask matching can also show another unique on that base.",
        ],
    )
    for target in spec["identified_targets"]:
        lines += render_block(
            "HCSSF - IDENTIFIED INFAMY HELMETS",
            [
                "Identified True",
                f"Class == {quoted(target['classes'])}",
                f"HasExplicitMod {quoted(target['has_explicit_mod'])}",
            ],
            build_relevance_style(
                palette,
                "important",
                shape="Diamond",
                effect_color=effect_color,
                sound="Shiny.mp3",
            ),
            [
                "The filter can only see the shared suffix 'of Infamy'.",
                "Inspect each alerted helmet for the exact per-exerting-Warcry critical strike modifier.",
            ],
        )
    lines += render_crafting_bases(spec, palette, effect_color)
    lines += render_hcssf_safety(palette, effect_color, progression)
    lines += render_resource_groups(spec, palette, effect_color)
    lines += render_gem_rules(spec, palette, effect_color)
    lines += render_flask_rules(spec, palette, effect_color)
    lines += render_utility_currency(palette, effect_color, progression)

    universe, league_cards, preferences = extract_card_sources(base_lines)
    buckets = assign_card_buckets(universe, economy, league_cards, preferences, spec)
    lines += render_card_ladder(buckets, palette, effect_color, len(universe))
    lines.extend(
        [
            SEPARATOR,
            "# END SMOKIEZONE HYDROSPHERE BONESHATTER HCSSF TARGETS",
            SEPARATOR,
            "",
        ]
    )
    return lines


def previous_separator(lines: Sequence[str], marker_index: int) -> int:
    if marker_index > 0 and lines[marker_index - 1].startswith("#==="):
        return marker_index - 1
    return marker_index


def replace_theme_layers(
    lines: list[str], palette: dict[str, tuple[int, int, int]], effect_color: str
) -> list[str]:
    audit_marker = next(
        i for i, line in enumerate(lines) if "PATHCRAFT FULL AUDIT BASELINE" in line
    )
    audit_start = previous_separator(lines, audit_marker)
    audit_end = next(
        i
        for i, line in enumerate(lines[audit_marker + 1 :], audit_marker + 1)
        if line.startswith("Show # Pathcraft Death Oath visual rule 741")
    )
    lines = lines[:audit_start] + render_audit_baseline(palette) + lines[audit_end:]

    category_marker = next(
        i
        for i, line in enumerate(lines)
        if "PATHCRAFT FULL AUDIT - CRIMSON CATEGORY NORMALIZATION" in line
    )
    category_start = previous_separator(lines, category_marker)
    allie_marker = next(
        i
        for i, line in enumerate(lines)
        if "ALLIE HIGH-PRIORITY VELVET ACCENT LAYER" in line
    )
    allie_start = previous_separator(lines, allie_marker)
    lines = (
        lines[:category_start] + render_native_category_policy() + lines[allie_start:]
    )
    return lines


def compose_filter(spec: dict, economy: dict) -> tuple[str, dict]:
    base_text = BASE_FILTER.read_text(encoding="utf-8")
    base_lines = base_text.splitlines()
    if base_lines.count(OLD_BUILD_MARKER) != 1 or base_lines.count(OLD_BUILD_END) != 1:
        raise FilterBuildError(
            "Could not locate the one preserved Luminary build layer"
        )

    palette = derive_palette(spec["theme"]["main_color"])
    effect_color = spec["theme"]["poe_effect_color"]
    themed = replace_theme_layers(list(base_lines), palette, effect_color)

    start_marker = themed.index(OLD_BUILD_MARKER)
    start = previous_separator(themed, start_marker)
    end_marker = themed.index(OLD_BUILD_END)
    end = end_marker + 1
    if end < len(themed) and themed[end].startswith("#==="):
        end += 1
    build_layer = render_build_layer(spec, economy, base_lines)
    composed = themed[:start] + build_layer + themed[end:]

    header_end = composed.index("")
    header = [
        SEPARATOR,
        "# PATHCRAFT SMOKIEZONE HYDROSPHERE BONESHATTER 3.29 HCSSF - VIOLET PROGRESSIVE FILTER",
        "# Visibility/progression source: C:\\Users\\User\\Desktop\\SSF.txt",
        "# Broad visual source: C:\\Users\\User\\Desktop\\death oath.txt",
        "# High-value accent source: C:\\Users\\User\\Desktop\\allie.txt",
        f"# Global economy source: NeverSink {economy['source']['version']} @ {economy['source']['commit']}",
        "# Canonical build targets: data/filter_build_targets/poe1_smokiezone_hydrosphere_boneshatter_hcssf_3_29.json",
        "# Architecture: visual Continue layers -> terminal HCSSF/build overrides -> preserved SSF visibility rules",
        SEPARATOR,
        "",
    ]
    composed = header + composed[header_end + 1 :]
    output = "\n".join(composed).rstrip() + "\n"

    universe, league_cards, preferences = extract_card_sources(base_lines)
    buckets = assign_card_buckets(universe, economy, league_cards, preferences, spec)
    metadata = {
        "palette": {key: list(value) for key, value in palette.items()},
        "card_universe": len(universe),
        "card_bucket_counts": {key: len(value) for key, value in buckets.items()},
    }
    return output, metadata


def validate_target_names(spec: dict) -> None:
    base_items = read_json(REPO_ROOT / "data" / "game_data" / "BaseItemTypes.json")
    base_names = {row.get("Name") for row in base_items if row.get("Name")}
    active_skills = read_json(REPO_ROOT / "data" / "game_data" / "ActiveSkills.json")
    active_skill_names = {
        row.get("DisplayedName") for row in active_skills if row.get("DisplayedName")
    }
    errors: list[str] = []
    exact_base_names: set[str] = set()
    exact_gem_base_names: set[str] = set()
    contains_names: set[str] = set()
    for target in spec["unique_targets"]:
        exact_base_names.update(target["resolved_base_types"])
    for group in spec["crafting_base_groups"]:
        exact_base_names.update(group["base_types"])
    for group in spec["resource_groups"]:
        if group.get("match_mode") == "exact":
            exact_base_names.update(group.get("base_types", []))
        elif group.get("match_mode") == "contains":
            contains_names.update(group.get("base_types", []))
    for group in spec["flask_targets"]:
        exact_base_names.update(group["base_types"])
    for gem in spec["gem_targets"]:
        base_types = gem.get("base_types", [])
        transfigured_gem_names = gem.get("transfigured_gem_names", [])
        display_names = gem.get("display_names", [])
        if bool(base_types) == bool(transfigured_gem_names):
            errors.append(
                "Gem target must define exactly one of base_types or "
                f"transfigured_gem_names: {gem['id']}"
            )
            continue
        if base_types:
            exact_gem_base_names.update(base_types)
            if display_names:
                errors.append(
                    f"Ordinary gem target unexpectedly defines display_names: {gem['id']}"
                )
            continue

        if not display_names:
            errors.append(
                f"Transfigured gem target lacks display_names: {gem['id']}"
            )
            continue
        for display_name in display_names:
            matches = [
                row
                for row in active_skills
                if row.get("DisplayedName") == display_name
                and isinstance(row.get("TransfigureBase"), int)
                and 0 <= row["TransfigureBase"] < len(active_skills)
            ]
            if not matches:
                errors.append(
                    "Transfigured gem display name is absent from 3.29 game data: "
                    f"{display_name}"
                )
                continue
            resolved_bases = {
                active_skills[row["TransfigureBase"]].get("DisplayedName")
                for row in matches
            }
            if not resolved_bases.intersection(transfigured_gem_names):
                errors.append(
                    f"Transfigured gem base mismatch for {display_name}: "
                    f"expected one of {sorted(transfigured_gem_names)}, "
                    f"resolved {sorted(name for name in resolved_bases if name)}"
                )
        for name in transfigured_gem_names:
            if name not in base_names or name not in active_skill_names:
                errors.append(
                    f"TransfiguredGem name is absent from 3.29 game data: {name}"
                )

    for name in sorted(exact_base_names):
        if name not in base_names:
            errors.append(f"Exact BaseType is absent from 3.29 game data: {name}")
    for name in sorted(exact_gem_base_names):
        if name not in base_names:
            errors.append(f"Exact gem BaseType is absent from 3.29 game data: {name}")
    for fragment in sorted(contains_names):
        if not any(fragment in name for name in base_names):
            errors.append(
                f"Partial BaseType matches nothing in 3.29 game data: {fragment}"
            )

    crafting_groups = {group["id"]: group for group in spec["crafting_base_groups"]}
    researched_thresholds = {
        "build.weapon.endgame_vaal_axe": spec["progression"][
            "endgame_weapon_item_level"
        ],
        "build.armour.optimal_breach_bases": spec["progression"][
            "optimal_armour_item_level"
        ],
        "build.jewellery.endgame_crafting": spec["progression"][
            "endgame_jewellery_item_level"
        ],
    }
    for group_id, expected_item_level in researched_thresholds.items():
        group = crafting_groups.get(group_id)
        if group is None:
            errors.append(f"Researched crafting group is missing: {group_id}")
            continue
        if group.get("minimum_item_level") != expected_item_level:
            errors.append(
                f"Researched ItemLevel threshold drifted for {group_id}: "
                f"expected {expected_item_level}, got {group.get('minimum_item_level')}"
            )
    for group in spec["crafting_base_groups"]:
        if not group.get("always_show"):
            continue
        if group.get("maximum_area_level") is not None:
            errors.append(
                f"Always-show crafting group has an AreaLevel ceiling: {group['id']}"
            )
        if not group.get("rationale"):
            errors.append(
                f"Always-show crafting group lacks a research rationale: {group['id']}"
            )
    if errors:
        raise FilterBuildError("\n".join(errors))


def normalized_hide_blocks(text: str) -> list[tuple[str, ...]]:
    result: list[tuple[str, ...]] = []
    for block in parse_blocks(text.splitlines()):
        if block.action != "Hide":
            continue
        result.append(tuple([block.header.strip(), *block.directives]))
    return result


def validate_filter(output: str, spec: dict, source_text: str) -> dict:
    lines = output.splitlines()
    blocks = parse_blocks(lines)
    errors: list[str] = []

    def require_block_style(
        marker: str,
        required: Sequence[str],
        forbidden_prefixes: Sequence[str] = (),
    ) -> None:
        matches = [block for block in blocks if marker in block.header]
        if len(matches) != 1:
            errors.append(
                f"Expected exactly one style block for {marker}: found {len(matches)}"
            )
            return
        directives = matches[0].directives
        for directive in required:
            if directive not in directives:
                errors.append(f"Required style missing in {marker}: {directive}")
        for prefix in forbidden_prefixes:
            if any(directive.startswith(prefix) for directive in directives):
                errors.append(f"Forbidden style in {marker}: {prefix}")

    if OLD_BUILD_MARKER in output or OLD_BUILD_END in output:
        errors.append("Old Luminary build layer marker survived composition")
    if "CRIMSON CATEGORY NORMALIZATION" in output:
        errors.append("Old Crimson category-normalization marker survived recolouring")
    if (
        "VIOLET CATEGORY NORMALIZATION" in output
        or "PATHCRAFT HCSSF - GENERIC" in output
    ):
        errors.append("Global violet category wash survived the native-cue refactor")
    for marker in (
        "SMOKIEZONE - SIX LINK SAFETY",
        "SMOKIEZONE - CORE REQUIRED UNIQUE BASES",
        "SMOKIEZONE - BUILD.WEAPON.ENDGAME_VAAL_AXE",
        "SMOKIEZONE - BUILD.ARMOUR.OPTIMAL_BREACH_BASES",
        "SMOKIEZONE - BUILD.JEWELLERY.ENDGAME_CRAFTING",
        "HCSSF - IDENTIFIED INFAMY HELMETS",
        "SMOKIEZONE - TARGET GEM BUILD.GEM.COMPLEX_TRAUMA",
        "SMOKIEZONE - BUILD.RESOURCES.CORE",
        "SMOKIEZONE - ESSENCES HIGH VIOLET",
        "SMOKIEZONE - ESSENCES IMPORTANT VIOLET",
        "SMOKIEZONE - ESSENCES ROUTINE VIOLET",
        "SMOKIEZONE - ESSENCES QUIET VIOLET",
        "SMOKIEZONE - DIVINATION CARDS UNTIERED CATCH-ALL",
    ):
        if marker not in output:
            errors.append(f"Required marker missing: {marker}")

    semantic_guards = {
        "NORMAL EQUIPMENT TEXT GUARD": "SetTextColor 200 200 200 255",
        "MAGIC EQUIPMENT TEXT GUARD": "SetTextColor 136 136 255 255",
        "RARE EQUIPMENT TEXT GUARD": "SetTextColor 255 255 119 255",
        "ORDINARY UNIQUE TEXT GUARD": "SetTextColor 175 96 37 255",
        "NATIVE GEM TEXT GUARD": "SetTextColor 27 217 217 255",
    }
    for marker, colour in semantic_guards.items():
        require_block_style(marker, [colour, "Continue"])

    essence_styles = {
        "SMOKIEZONE - ESSENCES HIGH VIOLET": [
            "SetTextColor 248 248 250 255",
            "SetBorderColor 218 200 250 255",
            "SetBackgroundColor 124 58 237 250",
            "Continue",
        ],
        "SMOKIEZONE - ESSENCES IMPORTANT VIOLET": [
            "SetTextColor 218 200 250 255",
            "SetBorderColor 163 117 242 255",
            "SetBackgroundColor 68 32 130 245",
            "Continue",
        ],
        "SMOKIEZONE - ESSENCES ROUTINE VIOLET": [
            "SetTextColor 163 117 242 255",
            "SetBorderColor 124 58 237 255",
            "SetBackgroundColor 37 17 71 240",
            "Continue",
        ],
        "SMOKIEZONE - ESSENCES QUIET VIOLET": [
            "SetTextColor 190 190 200 255",
            "SetBorderColor 68 32 130 255",
            "SetBackgroundColor 22 10 43 225",
            "Continue",
        ],
    }
    for marker, required in essence_styles.items():
        require_block_style(
            marker,
            required,
            forbidden_prefixes=(
                "SetFontSize",
                "PlayAlertSound",
                "CustomAlertSound",
                "PlayEffect",
                "MinimapIcon",
            ),
        )

    require_block_style(
        "SMOKIEZONE - CORE REQUIRED UNIQUE BASES",
        [
            "SetTextColor 248 248 250 255",
            "SetBorderColor 200 101 242 255",
            "SetBackgroundColor 37 17 71 248",
            'CustomAlertSound "MyPrecious.mp3" 300',
            "PlayEffect Purple",
            "MinimapIcon 0 Purple Star",
        ],
    )
    require_block_style(
        "SMOKIEZONE - OPTIONAL UNIQUE BASES",
        [
            "SetTextColor 175 96 37 255",
            "SetBorderColor 124 58 237 255",
            "SetBackgroundColor 25 13 29 245",
            "PlayAlertSound None",
            "PlayEffect None",
        ],
    )
    require_block_style(
        "SMOKIEZONE - GLOBAL T0 CURRENCY",
        [
            "SetTextColor 124 58 237 255",
            "SetBackgroundColor 248 248 250 255",
            "PlayEffect Purple",
        ],
    )
    require_block_style(
        "SMOKIEZONE - GLOBAL HIGH VALUE CURRENCY",
        [
            "SetTextColor 248 248 250 255",
            "SetBorderColor 218 200 250 255",
            "SetBackgroundColor 124 58 237 255",
            "PlayEffect Purple",
        ],
    )
    require_block_style(
        "SMOKIEZONE - BUILD.RESOURCES.CORE",
        [
            "SetTextColor 19 10 29 255",
            "SetBorderColor 124 58 237 255",
            "SetBackgroundColor 200 101 242 245",
            "PlayEffect Purple Temp",
        ],
    )
    require_block_style(
        "SMOKIEZONE - TARGET GEM BUILD.GEM.COMPLEX_TRAUMA",
        [
            "SetTextColor 27 217 217 255",
            "SetBackgroundColor 5 31 34 245",
            "PlayEffect Purple",
        ],
    )

    for retired_marker in (
        "HCSSF - RARE ARMOUR AND JEWELLERY IN ENDGAME",
        "HCSSF - RARE TWO HAND AXES IN ENDGAME",
    ):
        if retired_marker in output:
            errors.append(
                f"Retired broad AreaLevel 83+ equipment catch-all survived: {retired_marker}"
            )

    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.count('"') % 2:
            errors.append(f"Unbalanced quotes at line {line_number}: {stripped}")
        color_match = re.match(
            r"^Set(?:Text|Border|Background)Color\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)(?:\s+(-?\d+))?$",
            stripped,
        )
        if color_match and any(
            not 0 <= int(value) <= 255 for value in color_match.groups() if value
        ):
            errors.append(
                f"Colour channel out of range at line {line_number}: {stripped}"
            )
        font_match = re.match(r"^SetFontSize\s+(\d+)$", stripped)
        if font_match and not 18 <= int(font_match.group(1)) <= 45:
            errors.append(f"Font size out of range at line {line_number}: {stripped}")

    source_tokens = {
        line.strip().split()[0]
        for line in source_text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    output_tokens = {
        line.strip().split()[0]
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    }
    unknown_tokens = sorted(output_tokens - source_tokens)
    if unknown_tokens:
        errors.append(f"Directives absent from loaded source filter: {unknown_tokens}")

    custom_sounds: set[str] = set()
    for block in blocks:
        custom = [
            line for line in block.directives if line.startswith("CustomAlertSound ")
        ]
        builtin = [
            line
            for line in block.directives
            if line.startswith("PlayAlertSound ") and line != "PlayAlertSound None"
        ]
        if custom and builtin:
            errors.append(
                f"Built-in/custom sound collision at line {block.start_line}: {block.header}"
            )
        for directive in custom:
            match = re.match(r'^CustomAlertSound\s+"([^"]+)"', directive)
            if not match:
                errors.append(
                    f"Malformed custom sound at line {block.start_line}: {directive}"
                )
            else:
                custom_sounds.add(match.group(1))
        if block.action == "Hide":
            for directive in block.directives:
                if directive.startswith("CustomAlertSound "):
                    errors.append(
                        f"Hide block leaks custom sound at line {block.start_line}"
                    )
                if (
                    directive.startswith("PlayAlertSound ")
                    and directive != "PlayAlertSound None"
                ):
                    errors.append(
                        f"Hide block leaks alert sound at line {block.start_line}"
                    )
                if (
                    directive.startswith("PlayEffect ")
                    and directive != "PlayEffect None"
                ):
                    errors.append(f"Hide block leaks beam at line {block.start_line}")
                if (
                    directive.startswith("MinimapIcon ")
                    and directive != "MinimapIcon -1"
                ):
                    errors.append(
                        f"Hide block leaks minimap icon at line {block.start_line}"
                    )

    missing_sounds = sorted(
        sound for sound in custom_sounds if not (GAME_FILTER_DIR / sound).exists()
    )
    if missing_sounds:
        errors.append(
            f"Custom sound files missing from game directory: {missing_sounds}"
        )

    source_hides = normalized_hide_blocks(source_text)
    output_hides = normalized_hide_blocks(output)
    if source_hides != output_hides:
        errors.append(
            f"Preserved visibility policy changed: source Hide blocks={len(source_hides)}, output={len(output_hides)}"
        )

    first_hide = next(
        (block.start_line for block in blocks if block.action == "Hide"), None
    )
    if first_hide is None:
        errors.append("No Hide block remains in the progressive SSF visibility layer")
    else:
        for marker in (
            "SMOKIEZONE - SIX LINK SAFETY",
            "SMOKIEZONE - CORE REQUIRED UNIQUE BASES",
            "SMOKIEZONE - TARGET GEM BUILD.GEM.COMPLEX_TRAUMA",
        ):
            marker_line = next(
                (i for i, line in enumerate(lines, 1) if marker in line), None
            )
            if marker_line is None or marker_line >= first_hide:
                errors.append(
                    f"Required terminal rule is not before the first Hide: {marker}"
                )

        for group in spec["crafting_base_groups"]:
            if not group.get("always_show"):
                continue
            marker = f"SMOKIEZONE - {group['id'].upper()}"
            matching = [block for block in blocks if marker in block.header]
            if len(matching) != 1:
                errors.append(
                    f"Always-show crafting group must render exactly once: {marker} ({len(matching)})"
                )
                continue
            block = matching[0]
            if block.action != "Show" or block.start_line >= first_hide:
                errors.append(
                    f"Always-show crafting group is not a pre-Hide Show: {marker}"
                )
            if "Continue" in block.directives:
                errors.append(f"Always-show crafting group is not terminal: {marker}")
            if any(line.startswith("SetTextColor") for line in block.directives):
                errors.append(f"Crafting base overwrites rarity text colour: {marker}")
            if "SetBorderColor 124 58 237 255" not in block.directives:
                errors.append(
                    f"Crafting base lacks the shared violet relevance border: {marker}"
                )
            if not any(
                line.startswith("SetBackgroundColor 37 17 71 ")
                for line in block.directives
            ):
                errors.append(
                    f"Crafting base lacks the shared aubergine background: {marker}"
                )
            if group.get("maximum_area_level") is not None:
                errors.append(
                    f"Always-show crafting group has an AreaLevel ceiling: {marker}"
                )
            if group.get("rationale") and group["rationale"] not in output:
                errors.append(
                    f"Always-show crafting rationale comment is missing: {marker}"
                )

    for block in blocks:
        if (
            any(
                marker in block.header
                for marker in (
                    "SIX LINK SAFETY",
                    "CORE REQUIRED UNIQUE BASES",
                    "TARGET GEM BUILD.GEM.COMPLEX_TRAUMA",
                )
            )
            and "Continue" in block.directives
        ):
            errors.append(f"Required safety rule is not terminal: {block.header}")

    if "MinimapIcon 0 Pink UpsideDownHouse" not in output:
        errors.append("Unclassified divination-card safety icon is missing")
    if errors:
        raise FilterBuildError("Filter validation failed:\n- " + "\n- ".join(errors))

    stats = {
        "lines": len(lines),
        "show": sum(block.action == "Show" for block in blocks),
        "hide": sum(block.action == "Hide" for block in blocks),
        "continue": sum(line.strip() == "Continue" for line in lines),
        "custom_sound_calls": sum(
            line.strip().startswith("CustomAlertSound ") for line in lines
        ),
        "custom_sound_files": sorted(custom_sounds),
        "minimap_icons": sum(line.strip().startswith("MinimapIcon ") for line in lines),
        "play_effects": sum(line.strip().startswith("PlayEffect ") for line in lines),
        "source_hide_blocks_preserved": len(source_hides),
    }
    return stats


def install_filter(output_path: Path) -> dict:
    GAME_FILTER_DIR.mkdir(parents=True, exist_ok=True)
    destination = GAME_FILTER_DIR / output_path.name
    backup: Path | None = None
    if destination.exists() and sha256_file(destination) != sha256_file(output_path):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(
            f"{destination.stem}.pre-{stamp}{destination.suffix}"
        )
        shutil.copy2(destination, backup)
    shutil.copy2(output_path, destination)
    source_hash = sha256_file(output_path)
    installed_hash = sha256_file(destination)
    if source_hash != installed_hash:
        raise FilterBuildError("Installed filter hash does not match workspace output")
    return {
        "installed_path": str(destination),
        "installed_sha256": installed_hash,
        "backup_path": str(backup) if backup else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-economy",
        action="store_true",
        help="Refresh the pinned official NeverSink 8.20.1d economy snapshot.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install the validated output into the Path of Exile filter directory.",
    )
    args = parser.parse_args()

    validate_source_hashes()
    spec = read_json(SPEC_PATH)
    validate_target_names(spec)
    economy = (
        refresh_economy_snapshot() if args.refresh_economy else read_json(ECONOMY_PATH)
    )
    if economy.get("source", {}).get("commit") != NEVERSINK_COMMIT:
        raise FilterBuildError(
            "Economy snapshot is not pinned to the approved NeverSink commit"
        )

    output, metadata = compose_filter(spec, economy)
    source_text = BASE_FILTER.read_text(encoding="utf-8")
    stats = validate_filter(output, spec, source_text)
    OUTPUT_FILTER.write_text(output, encoding="utf-8", newline="\n")
    output_hash = sha256_file(OUTPUT_FILTER)

    result = {
        "output": str(OUTPUT_FILTER),
        "sha256": output_hash,
        "source_sha256": sha256_file(BASE_FILTER),
        "economy": economy["source"],
        "stats": stats,
        **metadata,
    }
    if args.install:
        result["installation"] = install_filter(OUTPUT_FILTER)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FilterBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
