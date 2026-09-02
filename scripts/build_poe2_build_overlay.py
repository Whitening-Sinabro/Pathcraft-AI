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

    __slots__ = ("base_types", "classes", "rarities", "font", "volume", "icon_size", "line", "extra")

    def __init__(self) -> None:
        self.base_types: set[str] = set()
        self.classes: set[str] = set()
        self.rarities: set[str] = set(ALL_RARITIES)
        self.font: int = 32
        self.volume: int = 0
        self.icon_size: int | None = None
        self.line: int = 0
        self.extra: set[str] = set()  # conditions we cannot express -> narrower than us


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


def check_style_values(style_name: str, style: dict, allowed: dict[str, set]) -> None:
    """Reject values the game would ignore.

    Two different kinds of field, so two different checks: font size and volume
    are continuous, and the base filter happening to use only 100 and 300 says
    nothing about what is legal, so those get a range. Beam colour, minimap
    shape and the rest are enumerations the client either knows or does not, so
    those must be values the base filter actually uses.
    """
    ranges = {"font": (1, 45), "volume": (0, 300)}
    for key, value in [
        ("font", style["font"]),
        ("sound_id", style["sound"][0]),
        ("volume", style["sound"][1]),
        ("beam", style["beam"]),
        ("icon_size", style["icon"][0]),
        ("icon_color", style["icon"][1]),
        ("icon_shape", style["icon"][2]),
    ]:
        if key in ranges:
            low, high = ranges[key]
            if not (low <= value <= high):
                raise SystemExit(
                    f"value gate FAIL: style '{style_name}' {key}={value} outside {low}..{high}"
                )
        elif allowed[key] and value not in allowed[key]:
            raise SystemExit(
                f"value gate FAIL: style '{style_name}' {key}={value!r} is not a value the base "
                f"filter uses (allowed: {sorted(allowed[key])})"
            )


def required_loudness(
    base_type: str, rarities: set[str], classes: set[str], blocks: list[BaseBlock]
) -> tuple[int, int, int | None, list[BaseBlock]]:
    """What the base filter already says about this item: (font, volume, icon size).

    Only blocks that name the BaseType, overlap our rarity scope and use no
    condition we cannot express count -- a T1-unique block does not constrain a
    rule that excludes uniques, and a "chance this if it has 3 sockets" block
    does not constrain a rule about the plain base.

    The fourth return value is the list of narrower blocks we shadow anyway, so
    the caller can report them rather than silently swallowing them.
    """
    font = volume = 0
    icon: int | None = None
    shadowed: list[BaseBlock] = []
    for block in blocks:
        if base_type not in block.base_types or not (rarities & block.rarities):
            continue
        if block.classes and classes and not (block.classes & classes):
            continue
        if block.extra:
            if block.volume or block.font >= 40:
                shadowed.append(block)
            continue
        font = max(font, block.font)
        volume = max(volume, block.volume)
        if block.icon_size is not None:
            icon = block.icon_size if icon is None else min(icon, block.icon_size)
    return font, volume, icon, shadowed


# --------------------------------------------------------------------------- #
# emission
# --------------------------------------------------------------------------- #


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
    if rule.get("area_level_max"):
        lines.append(f"\tAreaLevel <= {int(rule['area_level_max'])}")
    t, bo, bg = style["text"], style["border"], style["background"]
    lines.append(f"\tSetTextColor {t[0]} {t[1]} {t[2]} 255")
    lines.append(f"\tSetBorderColor {bo[0]} {bo[1]} {bo[2]} 255")
    lines.append(f"\tSetBackgroundColor {bg[0]} {bg[1]} {bg[2]} 255")
    lines.append(f"\tSetFontSize {font}")
    lines.append(f"\tPlayAlertSound {style['sound'][0]} {volume}")
    lines.append(f"\tPlayEffect {style['beam']}")
    lines.append(f"\tMinimapIcon {icon_size} {style['icon'][1]} {style['icon'][2]}")
    return "\n".join(lines)


def build_rule_blocks(
    rule: dict, style: dict, base_blocks: list[BaseBlock]
) -> tuple[list[str], list[str], list[str]]:
    """Emit one block per loudness class so no item ends up quieter than vanilla."""
    rarities = set(rule.get("rarity") or ALL_RARITIES)
    declared = rule.get("class") or []
    classes = set(declared if isinstance(declared, list) else [declared])
    groups: dict[tuple[int, int, int], list[str]] = {}
    raises: list[str] = []
    shadows: list[str] = []
    for base_type in rule["base_types"]:
        req_font, req_volume, req_icon, shadowed = required_loudness(
            base_type, rarities, classes, base_blocks
        )
        for block in shadowed:
            shadows.append(
                f"{base_type}: base L{block.line} (font {block.font}, volume {block.volume}, "
                f"extra conditions {sorted(block.extra)}) is shadowed by this overlay"
            )
        font = max(style["font"], req_font)
        volume = max(style["sound"][1], req_volume)
        icon = style["icon"][0] if req_icon is None else min(style["icon"][0], req_icon)
        if (font, volume, icon) != (style["font"], style["sound"][1], style["icon"][0]):
            raises.append(
                f"{base_type}: font {style['font']}->{font}, volume {style['sound'][1]}->{volume}, "
                f"icon {style['icon'][0]}->{icon}"
            )
        groups.setdefault((font, volume, icon), []).append(base_type)
    blocks = [
        render_block(rule, style, sorted(names), font, volume, icon)
        for (font, volume, icon), names in sorted(groups.items())
    ]
    return blocks, raises, shadows


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
    allowed_values = base_value_vocabulary(base_text)
    vocabulary = base_vocabulary(base_text) | game_base_names()

    for name, style in spec["styles"].items():
        check_contrast(name, style)
        check_style_values(name, style, allowed_values)

    blocks: list[str] = []
    dropped: list[str] = []
    raised: list[str] = []
    shadowed: list[str] = []
    skipped_stage = 0
    for rule in spec["rules"]:
        stages = rule.get("stages")
        if args.stage and stages and args.stage not in stages:
            skipped_stage += 1
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
            {**rule, "base_types": kept}, spec["styles"][rule["style"]], base_blocks
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
            "# Show-only. Nothing is hidden; unmatched items fall through to NeverSink.",
            "# regenerate: python scripts/build_poe2_build_overlay.py"
            f" --spec {repo_relative(spec_path)} --base {repo_relative(base_path)} --out <out>"
            + (f" --stage {args.stage}" if args.stage else ""),
            "#" + "=" * 79,
            "",
        ]
    )
    out_text = header + "\n\n".join(blocks) + "\n\n" + base_text
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
