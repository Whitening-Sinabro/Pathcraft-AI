# -*- coding: utf-8 -*-
"""Build derived item/mod indexes from GGPK-exported tables.

The raw GGPK tables are intentionally normalized and terse. This script creates
joinable project-level views that answer:

- which effective tags an item base has,
- which prefix/suffix mods can spawn on that base at an item level,
- which stat keys and ranges each mod carries.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from ggpk_index import DATA_ROOT, GGPKIndex, _is_valid_ref  # noqa: E402


DEFAULT_OUTPUT_DIR = DATA_ROOT / "ggpk_derived"
AFFIX_GENERATION_TYPES = (1, 2)


def _generation_type_name(value: Any) -> str:
    return {1: "prefix", 2: "suffix"}.get(value, str(value))


def _tag_ids(index: GGPKIndex, keys: Iterable[int]) -> list[str]:
    return sorted(index._tag_id(key) for key in keys)


def _explicit_tag_keys(row: dict[str, Any]) -> set[int]:
    return {
        value
        for value in row.get("TagsKeys", []) or []
        if isinstance(value, int) and value >= 0
    }


def _stat_keys(row: dict[str, Any]) -> list[int]:
    keys: list[int] = []
    for idx in range(1, 7):
        value = row.get(f"StatsKey{idx}")
        if _is_valid_ref(value):
            keys.append(int(value))
    return keys


def _spawn_weight_rows(index: GGPKIndex, row: dict[str, Any]) -> list[dict[str, Any]]:
    tags = row.get("SpawnWeight_TagsKeys") or []
    values = row.get("SpawnWeight_Values") or []
    result: list[dict[str, Any]] = []
    for tag, value in zip(tags, values):
        if not isinstance(tag, int) or not isinstance(value, int):
            continue
        result.append({
            "tag_key": tag,
            "tag_id": index._tag_id(tag),
            "weight": value,
        })
    return result


def _mod_record_for_stat_index(index: GGPKIndex, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("Id"),
        "name": row.get("Name"),
        "domain": row.get("Domain"),
        "generation_type_key": row.get("GenerationType"),
        "generation_type": _generation_type_name(row.get("GenerationType")),
        "level": row.get("Level"),
        "max_level": row.get("MaxLevel"),
        "mod_type_key": row.get("ModTypeKey"),
        "families": row.get("Families") or [],
        "implicit_tag_keys": row.get("ImplicitTagsKeys") or [],
        "implicit_tags": _tag_ids(
            index,
            (
                key
                for key in row.get("ImplicitTagsKeys", []) or []
                if isinstance(key, int) and key >= 0
            ),
        ),
        "spawn_weights": _spawn_weight_rows(index, row),
        "stats": index._mod_stat_ranges(row),
        "stat_keys": _stat_keys(row),
        "is_essence_only": bool(row.get("IsEssenceOnlyModifier")),
    }


def _mod_record_for_item(row: dict[str, Any], spawn_weight: int) -> dict[str, Any]:
    return {
        "mod_id": row.get("Id"),
        "name": row.get("Name"),
        "level": row.get("Level"),
        "max_level": row.get("MaxLevel"),
        "generation_type": _generation_type_name(row.get("GenerationType")),
        "spawn_weight": spawn_weight,
        "mod_type_key": row.get("ModTypeKey"),
        "families": row.get("Families") or [],
        "stat_keys": _stat_keys(row),
        "is_essence_only": bool(row.get("IsEssenceOnlyModifier")),
    }


def _item_record(index: GGPKIndex, row: dict[str, Any], row_index: int) -> dict[str, Any]:
    explicit_keys = _explicit_tag_keys(row)
    effective_keys = index._effective_item_tag_keys(row)
    inferred_keys = effective_keys - explicit_keys
    return {
        "base_row_index": row_index,
        "metadata_id": row.get("Id"),
        "name": row.get("Name"),
        "drop_level": row.get("DropLevel"),
        "item_class_key": row.get("ItemClassesKey"),
        "mod_domain": row.get("ModDomain"),
        "inherits_from": row.get("InheritsFrom"),
        "explicit_tag_keys": sorted(explicit_keys),
        "explicit_tags": _tag_ids(index, explicit_keys),
        "inferred_tag_keys": sorted(inferred_keys),
        "inferred_tags": _tag_ids(index, inferred_keys),
        "effective_tag_keys": sorted(effective_keys),
        "effective_tags": _tag_ids(index, effective_keys),
    }


def _matching_item_rows(
    index: GGPKIndex,
    item_names: Optional[Iterable[str]],
) -> list[tuple[int, dict[str, Any]]]:
    wanted = {name.casefold() for name in item_names or []}
    rows: list[tuple[int, dict[str, Any]]] = []
    for row_index, row in enumerate(index.load_table("BaseItemTypes")):
        if not isinstance(row, dict):
            continue
        name = row.get("Name")
        if not isinstance(name, str) or not name.strip():
            continue
        if row.get("ModDomain") != 1:
            continue
        if wanted and name.casefold() not in wanted:
            continue
        rows.append((row_index, row))
    return rows


def _candidate_mod_rows(index: GGPKIndex) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in index.load_table("Mods"):
        if not isinstance(row, dict):
            continue
        if row.get("GenerationType") not in AFFIX_GENERATION_TYPES:
            continue
        rows.append(row)
    return rows


def _item_affix_record(
    index: GGPKIndex,
    row: dict[str, Any],
    row_index: int,
    candidate_mods: list[dict[str, Any]],
    item_level: int,
) -> dict[str, Any]:
    item = _item_record(index, row, row_index)
    item_tags = set(item["effective_tag_keys"])
    item_domain = item["mod_domain"]
    groups: dict[str, list[dict[str, Any]]] = {"prefix": [], "suffix": []}

    for mod in candidate_mods:
        if item_domain is not None and mod.get("Domain") != item_domain:
            continue
        level = mod.get("Level")
        if isinstance(level, int) and level > item_level:
            continue
        weight = index._spawn_weight_for_tags(mod, item_tags)
        if weight <= 0:
            continue
        generation_type = _generation_type_name(mod.get("GenerationType"))
        groups.setdefault(generation_type, []).append(_mod_record_for_item(mod, weight))

    for values in groups.values():
        values.sort(key=lambda mod: (str(mod.get("name") or ""), int(mod.get("level") or 0), str(mod.get("mod_id") or "")))

    return {
        "base": item,
        "item_level": item_level,
        "counts": {key: len(values) for key, values in groups.items()},
        "affixes": groups,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")
            count += 1
    return count


def _write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "base_row_index",
        "metadata_id",
        "name",
        "drop_level",
        "item_class_key",
        "mod_domain",
        "explicit_tags",
        "inferred_tags",
        "effective_tags",
        "prefix_count",
        "suffix_count",
        "prefix_preview",
        "suffix_preview",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            base = row["base"]
            prefixes = row["affixes"].get("prefix", [])
            suffixes = row["affixes"].get("suffix", [])
            writer.writerow({
                "base_row_index": base["base_row_index"],
                "metadata_id": base["metadata_id"],
                "name": base["name"],
                "drop_level": base["drop_level"],
                "item_class_key": base["item_class_key"],
                "mod_domain": base["mod_domain"],
                "explicit_tags": "|".join(base["explicit_tags"]),
                "inferred_tags": "|".join(base["inferred_tags"]),
                "effective_tags": "|".join(base["effective_tags"]),
                "prefix_count": len(prefixes),
                "suffix_count": len(suffixes),
                "prefix_preview": "|".join(str(mod.get("name") or "") for mod in prefixes[:20]),
                "suffix_preview": "|".join(str(mod.get("name") or "") for mod in suffixes[:20]),
            })


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(DATA_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def build_exports(
    *,
    game: str = "poe1",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    item_level: int = 100,
    item_names: Optional[Iterable[str]] = None,
    full_mod_index: bool = True,
) -> dict[str, Any]:
    index = GGPKIndex(game=game)
    selected_items = _matching_item_rows(index, item_names)
    candidate_mods = _candidate_mod_rows(index)

    item_tag_rows = [_item_record(index, row, row_index) for row_index, row in selected_items]
    affix_rows = [
        _item_affix_record(index, row, row_index, candidate_mods, item_level)
        for row_index, row in selected_items
    ]
    linked_mod_ids = {
        mod["mod_id"]
        for row in affix_rows
        for mods in row["affixes"].values()
        for mod in mods
        if mod.get("mod_id")
    }
    mod_rows = {
        str(row.get("Id")): _mod_record_for_stat_index(index, row)
        for row in index.load_table("Mods")
        if (
            isinstance(row, dict)
            and row.get("Id")
            and (full_mod_index or row.get("Id") in linked_mod_ids)
        )
    }

    prefix_total = sum(row["counts"].get("prefix", 0) for row in affix_rows)
    suffix_total = sum(row["counts"].get("suffix", 0) for row in affix_rows)

    tag_index_path = output_dir / f"{game}_item_tag_index.json"
    affix_index_path = output_dir / f"{game}_item_base_affix_index.jsonl"
    summary_path = output_dir / f"{game}_item_base_affix_summary.csv"
    mod_index_path = output_dir / f"{game}_mod_stat_index.json"
    manifest_path = output_dir / f"{game}_item_mod_derivation_manifest.json"

    _write_json(tag_index_path, {
        "schema_version": 1,
        "game": game,
        "source_tables": ["BaseItemTypes", "Tags"],
        "join_keys": ["base_row_index", "metadata_id", "effective_tag_keys"],
        "rows": item_tag_rows,
    })
    affix_count = _write_jsonl(affix_index_path, affix_rows)
    _write_summary_csv(summary_path, affix_rows)
    _write_json(mod_index_path, {
        "schema_version": 1,
        "game": game,
        "source_tables": ["Mods", "Tags"],
        "stat_resolution_status": "raw_stats_table_missing; stats are numeric StatsKey values with min/max ranges",
        "join_keys": ["mod_id", "stat_keys", "implicit_tag_keys", "spawn_weights.tag_key"],
        "mods": mod_rows,
    })

    manifest = {
        "schema_version": 1,
        "game": game,
        "generated_by": "python/scripts/build_ggpk_derived_item_mod_index.py",
        "item_level": item_level,
        "scope": "all_mod_domain_1_bases" if not item_names else "selected_bases",
        "mod_index_scope": "all_mods" if full_mod_index else "linked_affix_mods_only",
        "source_tables": {
            "BaseItemTypes": len(index.load_table("BaseItemTypes")),
            "Mods": len(index.load_table("Mods")),
            "Tags": len(index.load_table("Tags")),
            "Stats": "missing_in_current_extract",
        },
        "outputs": {
            "item_tag_index": _display_path(tag_index_path),
            "item_base_affix_index": _display_path(affix_index_path),
            "item_base_affix_summary": _display_path(summary_path),
            "mod_stat_index": _display_path(mod_index_path),
            "manifest": _display_path(manifest_path),
        },
        "join_model": {
            "item_to_affixes": "base.metadata_id/base_row_index -> item_base_affix_index.base",
            "affix_to_mod_stats": "affixes[].mod_id -> mod_stat_index.mods[mod_id]",
            "item_to_spawn_tags": "base.effective_tag_keys -> mod_stat_index.mods[mod_id].spawn_weights[].tag_key",
        },
        "counts": {
            "item_tag_rows": len(item_tag_rows),
            "item_base_affix_rows": affix_count,
            "mods": len(mod_rows),
            "candidate_affix_mod_rows": len(candidate_mods),
            "prefix_links": prefix_total,
            "suffix_links": suffix_total,
        },
        "limitations": [
            "The current GGPK export does not include Stats.json, so stat text is not resolved here.",
            "Crafting bench, influence-only acquisition rules, corruption outcomes, and mod group blocking are later lenses, not encoded as final gearing advice in this export.",
            "Affix availability is base-tag/domain/item-level candidate resolution; build desirability must be scored by separate build shell lenses.",
        ],
    }
    _write_json(manifest_path, manifest)
    return manifest


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build Pathcraft derived item/mod DBs from GGPK extracts.")
    parser.add_argument("--game", choices=("poe1", "poe2"), default="poe1")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--item-level", type=int, default=100)
    parser.add_argument("--item", action="append", dest="items", help="Limit export to a base item name; repeatable.")
    parser.add_argument(
        "--linked-mod-index-only",
        action="store_true",
        help="Write only mods linked by selected item affixes. Intended for tests/smoke exports.",
    )
    args = parser.parse_args(argv)

    manifest = build_exports(
        game=args.game,
        output_dir=args.output_dir,
        item_level=args.item_level,
        item_names=args.items,
        full_mod_index=not args.linked_mod_index_only,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
