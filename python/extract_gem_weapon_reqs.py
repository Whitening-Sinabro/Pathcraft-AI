"""
Build data/gem_weapon_requirements.json from POB Community source data.

Why POB and not GGPK? GGPK's ActiveSkills.WeaponRestriction_ItemClassesKeys is
INCOMPLETE for many skills (e.g. Sunder is missing Axes). POB's skill files at
src/Data/Skills/*.lua carry a fully-populated `weaponTypes` block that matches
the live game. See `_analysis/gem_weapon_restriction_audit.md` for the GGPK
discrepancies that motivated this rewrite.

Source:
  https://github.com/PathOfBuildingCommunity/PathOfBuilding (MIT license).
  Game data is © GGG; POB ships a cleaned form. We only extract the weapon
  restriction table — no PathOfBuilding code.

Fetched files (src/Data/Skills/):
  act_str.lua, act_dex.lua, act_int.lua   — active skill gems by colour
  other.lua, glove.lua                     — hybrid / enchantment skills
  sup_str.lua, sup_dex.lua, sup_int.lua   — support gems (rarely carry restrictions)

Output: data/gem_weapon_requirements.json
  {
    "source": "PathOfBuildingCommunity src/Data/Skills/*.lua",
    "gem_weapon_classes": { "<gem name>": ["<filter class>", ...], ... }
  }

Only physical-weapon classes (NeverSink list, see weapon_mod_tiers.json) are
kept; gems that only allow sceptre/staff/rune-dagger/fishing-rod are omitted.

Usage:
  python python/extract_gem_weapon_reqs.py              # live fetch
  python python/extract_gem_weapon_reqs.py --cache-only # no network, use .cache/
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# --- POB source URLs -------------------------------------------------------

_POB_BASE = (
    "https://raw.githubusercontent.com/PathOfBuildingCommunity/"
    "PathOfBuilding/master/src/Data/Skills/"
)

_POB_FILES = (
    "act_str.lua",
    "act_dex.lua",
    "act_int.lua",
    "other.lua",
    "glove.lua",
    "sup_str.lua",
    "sup_dex.lua",
    "sup_int.lua",
)

# --- POB weaponTypes label → POE filter `Class ==` name --------------------
# "None" means Unarmed, skipped. Keys mirror what POB files use verbatim.
_POB_TO_FILTER: dict[str, str] = {
    "Claw": "Claws",
    "Dagger": "Daggers",
    "Rune Dagger": "Rune Daggers",
    "One Handed Axe": "One Hand Axes",
    "One Handed Mace": "One Hand Maces",
    "One Handed Sword": "One Hand Swords",
    "Thrusting One Handed Sword": "Thrusting One Hand Swords",
    "Wand": "Wands",
    "Bow": "Bows",
    "Staff": "Staves",
    "Warstaff": "Warstaves",
    "Sceptre": "Sceptres",
    "Fishing Rod": "Fishing Rods",
    "Two Handed Axe": "Two Hand Axes",
    "Two Handed Mace": "Two Hand Maces",
    "Two Handed Sword": "Two Hand Swords",
}

# Physical weapon list (data/weapon_mod_tiers.json#weapon_classes, NeverSink ground truth).
_PHYSICAL_CLASSES: frozenset[str] = frozenset([
    "Bows", "Claws", "Daggers",
    "One Hand Axes", "One Hand Maces", "One Hand Swords", "Thrusting One Hand Swords",
    "Two Hand Axes", "Two Hand Maces", "Two Hand Swords",
    "Wands", "Warstaves",
])

# --- Lua parsing ------------------------------------------------------------
# POB source files are generated from a canonical template. Each skill entry
# looks like:
#   skills["Sunder"] = {
#       name = "Sunder",
#       ...
#       weaponTypes = {
#           ["One Handed Axe"] = true,
#           ...
#       },
#       ...
#   }
# We extract per-skill blocks by anchoring on the `skills["Name"] = {` line,
# then cut the block ending with a line that is exactly `}` at column 0
# (skills entries are always top-level assignments in these files).

_SKILL_START_RE = re.compile(r'^skills\["([^"]+)"\]\s*=\s*\{', re.MULTILINE)
_TOP_LEVEL_CLOSE_RE = re.compile(r"^\}", re.MULTILINE)
# Inside a block: weaponTypes = { ... } — flat, no nesting.
_WEAPON_BLOCK_RE = re.compile(r"weaponTypes\s*=\s*\{([^}]*)\}", re.DOTALL)
_WEAPON_ENTRY_RE = re.compile(r'\["([^"]+)"\]\s*=\s*true')
# POB uses space-stripped keys (skills["HeavyStrike"]) but keeps the
# game-facing name in `name = "Heavy Strike"` — that's what POB parses from a
# build export, so that's what our dict key must be.
_NAME_FIELD_RE = re.compile(r'^\s*name\s*=\s*"([^"]+)"', re.MULTILINE)


def iter_skill_blocks(text: str):
    """Yield (display_name, block_text) for every `skills["..."]` entry.

    display_name comes from the block's `name = "..."` field (POB's game-facing
    label, including transfigured suffixes like "of Earthbreaking"); if absent,
    we fall back to the raw key for diagnostics.
    """
    starts = list(_SKILL_START_RE.finditer(text))
    for i, m in enumerate(starts):
        block_start = m.end()
        # Next skills["..."] start or end of file
        next_start = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        # Find the first top-level `}` before the next entry.
        window = text[block_start:next_start]
        close = _TOP_LEVEL_CLOSE_RE.search(window)
        block = window[: close.start()] if close else window
        name_match = _NAME_FIELD_RE.search(block)
        display = name_match.group(1) if name_match else m.group(1)
        yield display, block


def extract_weapon_types(block: str) -> list[str]:
    """Return POB weaponType labels (verbatim) for one skill block, or []."""
    wb = _WEAPON_BLOCK_RE.search(block)
    if not wb:
        return []
    return _WEAPON_ENTRY_RE.findall(wb.group(1))


def map_to_filter_classes(pob_types: list[str]) -> tuple[set[str], set[str]]:
    """Split labels into (resolved filter classes, unknown labels).

    `None` entries (unarmed) are silently dropped. Everything else must be in
    _POB_TO_FILTER or we surface it so the map can be extended.
    """
    resolved: set[str] = set()
    unknown: set[str] = set()
    for label in pob_types:
        if label == "None":
            continue
        cls = _POB_TO_FILTER.get(label)
        if cls is None:
            unknown.add(label)
        else:
            resolved.add(cls)
    return resolved, unknown


# --- Fetching ---------------------------------------------------------------


def fetch(url: str, cache_dir: Path, cache_only: bool) -> str:
    """Return POB file content, writing through to cache on live fetch."""
    name = url.rsplit("/", 1)[-1]
    cached = cache_dir / name
    if cache_only:
        if not cached.exists():
            raise FileNotFoundError(f"cache miss and --cache-only: {cached}")
        return cached.read_text(encoding="utf-8")
    try:
        r = requests.get(
            url, timeout=30, headers={"User-Agent": "PathcraftAI/1.0"}
        )
        r.raise_for_status()
    except requests.RequestException as e:
        if cached.exists():
            logger.warning("fetch failed (%s), using cached %s", e, cached)
            return cached.read_text(encoding="utf-8")
        raise
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_text(r.text, encoding="utf-8")
    return r.text


# --- Main -------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--cache-only",
        action="store_true",
        help="Do not touch the network; require cached copies.",
    )
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    cache_dir = root / "data" / "pob_skills_cache"
    dst = root / "data" / "gem_weapon_requirements.json"

    all_classes: dict[str, set[str]] = {}
    unknown_labels: set[str] = set()
    processed_skills = 0

    for fname in _POB_FILES:
        try:
            text = fetch(_POB_BASE + fname, cache_dir, args.cache_only)
        except (requests.RequestException, FileNotFoundError) as e:
            logger.error("skip %s: %s", fname, e)
            continue

        file_skill_count = 0
        for name, block in iter_skill_blocks(text):
            processed_skills += 1
            file_skill_count += 1
            pob_types = extract_weapon_types(block)
            if not pob_types:
                continue  # spell / aura / buff — no weapon gate
            resolved, unk = map_to_filter_classes(pob_types)
            unknown_labels |= unk
            # Filter to physical list — omit sceptre/staff/rune-dagger-only skills
            phys = resolved & _PHYSICAL_CLASSES
            if not phys:
                continue
            prev = all_classes.get(name)
            if prev is not None:
                # Same gem appears in multiple files (rare but possible for
                # alt-quality / transfigured base sharing) — union keeps truth.
                all_classes[name] = prev | phys
            else:
                all_classes[name] = set(phys)
        logger.info("%s: %d skills parsed", fname, file_skill_count)

    if unknown_labels:
        logger.warning(
            "unknown POB weapon labels (update _POB_TO_FILTER): %s",
            sorted(unknown_labels),
        )

    if not all_classes:
        logger.error("no gems extracted — check POB file format or network")
        return 1

    sorted_out = {k: sorted(v) for k, v in sorted(all_classes.items())}

    payload = {
        "source": (
            "PathOfBuildingCommunity src/Data/Skills/*.lua (MIT). "
            "Game data © GGG."
        ),
        "generator": "python/extract_gem_weapon_reqs.py",
        "pob_files_used": list(_POB_FILES),
        "cache_dir": str(cache_dir.relative_to(root)),
        "physical_weapon_classes": sorted(_PHYSICAL_CLASSES),
        "gem_weapon_classes": sorted_out,
    }

    dst.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "wrote %s: %d gems (processed %d total)",
        dst, len(sorted_out), processed_skills,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
