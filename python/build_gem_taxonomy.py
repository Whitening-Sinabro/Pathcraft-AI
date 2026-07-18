# -*- coding: utf-8 -*-
"""Build a POE1 gem taxonomy from GGPK extracts and derived skill databases.

This file is intentionally data-generating glue. It does not try to infer a
single "correct build recommendation"; it records which source proves each
classification so downstream code can tell socketable gems, support gems,
transfigured active names, and granted/triggered ActiveSkills apart.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data"
GAME_DATA_DIR = DATA_ROOT / "game_data"
SENTINEL = -72340172838076674


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _norm(value: str) -> str:
    return value.strip().casefold()


def _is_real_active_skill(row: dict[str, Any]) -> bool:
    name = str(row.get("DisplayedName") or "").strip()
    skill_id = str(row.get("Id") or "").strip()
    if not name or not skill_id:
        return False
    lowered = f"{name} {skill_id}".casefold()
    return "[dnt]" not in lowered and "unused" not in lowered


def _best_active_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    real_rows = [row for row in rows if _is_real_active_skill(row)]
    if real_rows:
        rows = real_rows

    def score(row: dict[str, Any]) -> tuple[int, str]:
        skill_id = str(row.get("Id") or "")
        value = 0
        if not skill_id.endswith("_old"):
            value += 2
        if row.get("TransfigureBase", SENTINEL) != SENTINEL:
            value += 1
        if row.get("IsManuallyCasted"):
            value += 1
        return (-value, skill_id)

    return sorted(rows, key=score)


def _collect_skill_gems(items: list[dict[str, Any]], skill_gems: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in skill_gems:
        if not isinstance(row, dict):
            continue
        idx = row.get("BaseItemTypesKey")
        if not isinstance(idx, int) or idx < 0 or idx >= len(items):
            continue
        item = items[idx]
        name = str(item.get("Name") or "").strip()
        if not name or name.startswith("[UNUSED]"):
            continue
        result[_norm(name)] = {
            "name": name,
            "metadata_id": item.get("Id", ""),
            "drop_level": item.get("DropLevel", 0),
            "is_support": bool(row.get("IsSupport", False)),
            "is_vaal": bool(row.get("IsVaalVariant", False)),
            "str_pct": row.get("StrengthRequirementPercent", 0),
            "dex_pct": row.get("DexterityRequirementPercent", 0),
            "int_pct": row.get("IntelligenceRequirementPercent", 0),
            "gem_effect_refs": row.get("GemEffects", []),
            "item_experience_type": row.get("ItemExperienceType"),
        }
    return result


def _collect_active_skills(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, dict) or not _is_real_active_skill(row):
            continue
        name = str(row.get("DisplayedName") or "").strip()
        result.setdefault(_norm(name), []).append(row)
    return {key: _best_active_rows(value) for key, value in result.items()}


def _support_alias_target(name: str, skill_gems_by_name: dict[str, dict[str, Any]]) -> str | None:
    if name.endswith(" Support"):
        return None
    target = f"{name} Support"
    row = skill_gems_by_name.get(_norm(target))
    if row and row.get("is_support"):
        return target
    return None


def _socketability(
    name: str,
    *,
    valid_gem: bool,
    skill_gem: dict[str, Any] | None,
    active_rows: list[dict[str, Any]],
    alias_of: str | None,
) -> tuple[str, bool]:
    if skill_gem:
        if skill_gem.get("is_support"):
            return "socketable_support_gem_item", True
        return "socketable_active_gem_item", True
    if alias_of and active_rows:
        return "active_skill_only_and_support_alias_not_socketable_gem", False
    if alias_of:
        return "support_alias_not_socketable_name", False
    if valid_gem and active_rows:
        return "socketable_transfigured_or_active_name", True
    if active_rows:
        return "active_skill_only_not_socketable_gem", False
    if valid_gem:
        return "valid_name_without_local_skill_row", True
    return "unknown", False


def _gem_kind(
    *,
    socketability: str,
    skill_gem: dict[str, Any] | None,
    active_rows: list[dict[str, Any]],
    alias_of: str | None,
) -> str:
    if alias_of and active_rows:
        return "active_skill_only_and_support_alias"
    if alias_of:
        return "support_alias"
    if skill_gem and skill_gem.get("is_support"):
        return "support_gem"
    if skill_gem:
        return "active_gem"
    if socketability == "socketable_transfigured_or_active_name":
        return "active_transfigured_or_valid_active"
    if active_rows:
        return "active_skill_only"
    return "unknown_valid_name"


def _damage_flags_for(
    canonical: str,
    active_rows: list[dict[str, Any]],
    damage_types: dict[str, dict[str, Any]],
) -> tuple[dict[str, bool], str]:
    direct = damage_types.get(canonical)
    if isinstance(direct, dict):
        return {
            "attack": bool(direct.get("attack")),
            "caster": bool(direct.get("caster")),
            "dot": bool(direct.get("dot")),
            "minion": bool(direct.get("minion")),
        }, "gem_damage_types"

    triggered = damage_types.get(f"Triggered {canonical}")
    if isinstance(triggered, dict):
        return {
            "attack": bool(triggered.get("attack")),
            "caster": bool(triggered.get("caster")),
            "dot": bool(triggered.get("dot")),
            "minion": bool(triggered.get("minion")),
        }, f"gem_damage_types:Triggered {canonical}"

    if any(row.get("MinionActiveSkillTypes") for row in active_rows):
        return {
            "attack": False,
            "caster": False,
            "dot": False,
            "minion": True,
        }, "active_skills:minion_active_skill_types"

    return {
        "attack": False,
        "caster": False,
        "dot": False,
        "minion": False,
    }, "default_false"


def _offense_class(damage_flags: dict[str, Any] | None, kind: str) -> str:
    if kind in {"support_gem", "support_alias"}:
        return "support_not_active"
    flags = damage_flags or {}
    axes = [key for key in ("attack", "caster", "dot", "minion") if flags.get(key)]
    if axes:
        return "offensive_active"
    return "utility_or_unknown_active"


def _compact_active(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("Id"),
        "displayed_name": row.get("DisplayedName"),
        "description": row.get("Description"),
        "active_skill_type_ids": row.get("ActiveSkillTypes", []),
        "minion_active_skill_type_ids": row.get("MinionActiveSkillTypes", []),
        "weapon_restriction_item_class_ids": row.get("WeaponRestriction_ItemClassesKeys", []),
        "is_manually_casted": row.get("IsManuallyCasted"),
        "transfigure_base": row.get("TransfigureBase"),
    }


def build_taxonomy() -> dict[str, Any]:
    items = _load_json(GAME_DATA_DIR / "BaseItemTypes.json", [])
    skill_gems = _load_json(GAME_DATA_DIR / "SkillGems.json", [])
    active_skills = _load_json(GAME_DATA_DIR / "ActiveSkills.json", [])

    valid_data = _load_json(DATA_ROOT / "valid_gems.json", {})
    valid_names = {
        str(name).strip()
        for name in valid_data.get("gems", [])
        if isinstance(name, str) and name.strip()
    }
    valid_by_norm = {_norm(name): name for name in valid_names}

    damage_types = _load_json(DATA_ROOT / "gem_damage_types.json", {}).get("gems", {})
    weapon_reqs = _load_json(DATA_ROOT / "gem_weapon_requirements.json", {}).get("gem_weapon_classes", {})
    gem_levels = _load_json(DATA_ROOT / "gem_levels.json", {}).get("gems", {})

    skill_gems_by_name = _collect_skill_gems(items, skill_gems)
    active_by_name = _collect_active_skills(active_skills)

    all_keys = set(skill_gems_by_name) | set(active_by_name) | set(valid_by_norm)
    entries: dict[str, dict[str, Any]] = {}

    for key in sorted(all_keys):
        canonical = (
            skill_gems_by_name.get(key, {}).get("name")
            or valid_by_norm.get(key)
            or active_by_name.get(key, [{}])[0].get("DisplayedName")
        )
        if not canonical:
            continue

        skill_gem = skill_gems_by_name.get(key)
        active_rows = active_by_name.get(key, [])
        valid_gem = key in valid_by_norm
        alias_of = None if skill_gem else _support_alias_target(canonical, skill_gems_by_name)
        socketability, socketable = _socketability(
            canonical,
            valid_gem=valid_gem,
            skill_gem=skill_gem,
            active_rows=active_rows,
            alias_of=alias_of,
        )
        kind = _gem_kind(
            socketability=socketability,
            skill_gem=skill_gem,
            active_rows=active_rows,
            alias_of=alias_of,
        )
        flags, flags_source = _damage_flags_for(canonical, active_rows, damage_types)

        level_info = gem_levels.get(canonical, {})
        required_level = (
            level_info.get("required_level")
            if isinstance(level_info, dict) else None
        )
        if required_level is None and skill_gem:
            required_level = skill_gem.get("drop_level")

        source_membership = {
            "skill_gems": skill_gem is not None,
            "active_skills": bool(active_rows),
            "valid_gems": valid_gem,
            "gem_damage_types": flags_source.startswith("gem_damage_types"),
            "gem_weapon_requirements": canonical in weapon_reqs,
            "gem_levels": canonical in gem_levels,
        }

        entries[canonical] = {
            "name": canonical,
            "gem_kind": kind,
            "socketability": socketability,
            "socketable": socketable,
            "support_alias_of": alias_of,
            "source_membership": source_membership,
            "required_level": required_level,
            "damage_flags": flags,
            "damage_flags_source": flags_source,
            "offense_class": _offense_class(flags, kind),
            "weapon_requirements": weapon_reqs.get(canonical, []),
            "skill_gem": skill_gem,
            "active_skills": [_compact_active(row) for row in active_rows],
        }

    counts: dict[str, int] = {}
    socketability_counts: dict[str, int] = {}
    offense_counts: dict[str, int] = {}
    for entry in entries.values():
        counts[entry["gem_kind"]] = counts.get(entry["gem_kind"], 0) + 1
        socketability_counts[entry["socketability"]] = socketability_counts.get(entry["socketability"], 0) + 1
        offense_counts[entry["offense_class"]] = offense_counts.get(entry["offense_class"], 0) + 1

    return {
        "dataset_kind": "poe1_gem_taxonomy",
        "schema_version": "1.0.0",
        "generated_from": {
            "raw": [
                "data/game_data/BaseItemTypes.json",
                "data/game_data/SkillGems.json",
                "data/game_data/ActiveSkills.json"
            ],
            "derived": [
                "data/valid_gems.json",
                "data/gem_damage_types.json",
                "data/gem_weapon_requirements.json",
                "data/gem_levels.json"
            ],
        },
        "classification_policy": {
            "active_gem": "Name exists as a SkillGems row with IsSupport=false.",
            "support_gem": "Name exists as a SkillGems row with IsSupport=true.",
            "support_alias": "Bare name exists in valid_gems and '<name> Support' is a real support gem.",
            "active_transfigured_or_valid_active": "Name exists in valid_gems and ActiveSkills but not SkillGems; common for transfigured display names in local extracts.",
            "active_skill_only": "Name exists in ActiveSkills but not as a socketable valid gem; common for triggered/granted skills like Molten Burst.",
            "active_skill_only_and_support_alias": "Bare support alias also has an ActiveSkill row, such as Summon Phantasm; do not treat the bare name as a socketable active gem.",
            "offensive_active": "Active entry has PoB damage flags on at least one of attack/caster/dot/minion.",
        },
        "summary": {
            "entry_count": len(entries),
            "gem_kind_counts": counts,
            "socketability_counts": socketability_counts,
            "offense_class_counts": offense_counts,
        },
        "entries": entries,
    }


def write_taxonomy(path: Path) -> dict[str, Any]:
    taxonomy = build_taxonomy()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return taxonomy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build POE1 gem taxonomy DB.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DATA_ROOT / "poe1_gem_taxonomy.latest.json",
    )
    args = parser.parse_args(argv)
    taxonomy = write_taxonomy(args.output)
    print(json.dumps(taxonomy["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
