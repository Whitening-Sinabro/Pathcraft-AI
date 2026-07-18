# -*- coding: utf-8 -*-
"""Unified lookup layer for GGPK extracts and existing derived data files.

This module keeps the raw GGPK-exported tables (`data/game_data*`) separate
from derived project databases (`valid_gems*.json`, `unique_tiers.json`, etc.)
on disk, but exposes them through one compact query surface. The coach should
ask this layer for targeted facts instead of dumping full JSON tables into a
prompt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Optional

from passive_stat_semantics import passive_node_stat_semantics

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
RAW_GAME_DIRS = {
    "poe1": "game_data",
    "poe2": "game_data_poe2",
}

SENTINEL = -72340172838076674

CORE_TABLES = (
    "BaseItemTypes",
    "SkillGems",
    "ActiveSkills",
    "Mods",
    "PassiveSkills",
    "Maps",
    "QuestRewards",
    "Tags",
)

DERIVED_DB_FILES = (
    "valid_gems.json",
    "valid_gems_poe2.json",
    "poe1_gem_taxonomy.latest.json",
    "gem_taxonomy_adversarial_audit.latest.json",
    "gem_aliases.json",
    "gear_aliases.json",
    "unique_tiers.json",
    "unique_base_mapping.json",
    "uniques_poe2.json",
    "base_items_poe2.json",
    "t1_craft_bases.json",
    "vendor_recipes.json",
    "weapon_base_to_class.json",
    "weapon_mod_tiers.json",
    "defense_mod_tiers.json",
    "accessory_mod_tiers.json",
    "id_mod_filtering.json",
    "id_mod_filtering_poe2.json",
    "item_class_map_poe2.json",
    "divcard_mapping.json",
    "hc_divcard_tiers.json",
    "neversink_filter_rules.json",
    "progressive_hide.json",
    "atlas_farming_knowledge.json",
    "new_player_friction_knowledge.json",
    "poe1_season_research_3_29_reliquarian.json",
    "poe1_season_research_3_29_allflame_live.json",
    "poe1_3_29_global_review.json",
    "poe1_3_29_live_validation_queue.json",
    "poe1_3_29_information_intake_plan.json",
    "poe1_3_29_information_intake_status.latest.json",
    "poe1_3_29_corpus_reuse_review_v1.json",
    "poe1_3_29_luminary_merc_link_intake_v1.json",
    "build_corpus_manual_pob_sources_v1.json",
    "build_corpus_expanded_collection_queue_v1.json",
    "build_corpus_pob_link_probe.latest.json",
    "build_corpus_promoted_instances.latest.json",
    "build_corpus_promoted_case_snapshots.latest.json",
    "poe1_representative_build_profiles.latest.json",
    "poe1_representative_source_slot_queue.latest.json",
    "poe1_creator_source_registry_v1.json",
    "poe1_global_creator_source_targets_v1.json",
    "poe1_global_creator_priority_matrix_v1.json",
    "poe_ninja_build_variant_sampling_plan_v1.json",
    "poe_ninja_build_variant_evidence_queue_v1.json",
    "poe1_leveling_archetype_route_plan_v1.json",
    "poe1_reliquarian_build_shells_3_29.json",
    "guide_sources/poe1_brand_guide_zeeboub_v2.json",
    "ggpk_derived/poe1_item_mod_derivation_manifest.json",
    "builds/scion_reliquarian_hot_autobomber_3_29.build.json",
    "builds/scion_reliquarian_hot_autobomber_3_29.coach.json",
    "builds/scion_reliquarian_hot_autobomber_3_29.profile.json",
    "farming_meta/farming_meta_all.json",
    "patch_notes/patch_index.json",
    "patch_notes/patch_3_29_0.json",
    "patch_notes/summary_3_29_0.json",
    "patch_notes/poe1_3_27_3_29_patch_history_context.json",
    "patch_notes/poe1_3_29_0_patch_delta_index.json",
    "patch_notes/poe1_3_29_0_early_patch_adjustment_policy.json",
)


def _norm(value: str) -> str:
    return value.strip().casefold()


def _is_valid_ref(value: Any) -> bool:
    return isinstance(value, int) and value >= 0 and value != SENTINEL


def _first_ref(row: dict[str, Any], names: Iterable[str]) -> Optional[int]:
    for name in names:
        value = row.get(name)
        if _is_valid_ref(value):
            return value
    return None


def _load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _json_count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, str):
        return len(value)
    if isinstance(value, dict):
        for key in (
            "records",
            "profiles",
            "creators",
            "reviews",
            "link_skill_hypotheses",
            "validation_tracks",
            "collection_lanes",
            "immediate_collection_queue",
            "routes",
            "slots",
            "league_sampling_plan",
            "archetype_sampling_targets",
        ):
            nested = value.get(key)
            if isinstance(nested, list):
                return len(nested)
        for container, key in (
            ("totals", "candidate_count"),
            ("coverage_summary", "target_count"),
            ("coverage_summary", "creator_count"),
            ("coverage_summary", "route_count"),
            ("coverage_summary", "candidate_count"),
            ("summary", "profile_count"),
            ("queue_status", "archetype_target_count"),
        ):
            nested = value.get(container)
            if isinstance(nested, dict) and isinstance(nested.get(key), int):
                return nested[key]
        return len(value)
    return 0


def _sha256_prefix(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _pick(row: dict[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    return {field: row.get(field) for field in fields if field in row}


def _gem_candidate_score(info: dict[str, Any]) -> int:
    """Prefer live/default gems over event-only duplicate names."""
    metadata_id = str(info.get("metadata_id", ""))
    score = 0
    lowered = metadata_id.casefold()
    if "royale" in lowered:
        score -= 100
    if "dnt" in lowered or "unused" in lowered:
        score -= 100
    if metadata_id:
        score += 1
    if info.get("required_level", 0):
        score += 1
    return score


class GGPKIndex:
    """Lazy index over one game data directory plus project derived databases."""

    def __init__(
        self,
        game: str = "poe1",
        data_root: Optional[Path] = None,
        game_data_dir: Optional[Path] = None,
    ):
        self.game = "poe2" if game == "poe2" else "poe1"
        self.data_root = data_root or DATA_ROOT
        self.game_data_dir = game_data_dir or self.data_root / RAW_GAME_DIRS[self.game]

        self._tables: dict[str, list[dict[str, Any]]] = {}
        self._derived: dict[str, Any] = {}
        self._items_by_name: Optional[dict[str, dict[str, Any]]] = None
        self._items_by_id: Optional[dict[str, dict[str, Any]]] = None
        self._gems_by_name: Optional[dict[str, dict[str, Any]]] = None
        self._mods_by_key: Optional[dict[str, list[dict[str, Any]]]] = None
        self._tag_key_by_id: Optional[dict[str, int]] = None
        self._tag_id_by_key: Optional[dict[int, str]] = None
        self._passives_by_key: Optional[dict[str, list[dict[str, Any]]]] = None
        self._passives_by_graph_id: Optional[dict[int, dict[str, Any]]] = None
        self._skilltree_nodes_by_id: Optional[dict[str, dict[str, Any]]] = None
        self._maps_by_name: Optional[dict[str, dict[str, Any]]] = None
        self._valid_gems: Optional[set[str]] = None
        self._unique_tiers: Optional[dict[str, str]] = None
        self._unique_bases: Optional[dict[str, str]] = None
        self._poe2_uniques: Optional[dict[str, dict[str, Any]]] = None

    def load_table(self, table: str) -> list[dict[str, Any]]:
        if table not in self._tables:
            data = _load_json_file(self.game_data_dir / f"{table}.json", [])
            self._tables[table] = data if isinstance(data, list) else []
        return self._tables[table]

    def load_derived(self, rel_path: str) -> Any:
        if rel_path not in self._derived:
            self._derived[rel_path] = _load_json_file(self.data_root / rel_path, {})
        return self._derived[rel_path]

    def build_catalog(self, include_hash: bool = False) -> dict[str, Any]:
        games: dict[str, Any] = {}
        for game, dirname in RAW_GAME_DIRS.items():
            raw_dir = self.data_root / dirname
            tables: dict[str, Any] = {}
            for path in sorted(raw_dir.glob("*.json")):
                value = _load_json_file(path, [])
                entry = {
                    "path": str(path.relative_to(self.data_root)).replace("\\", "/"),
                    "rows": _json_count(value),
                    "bytes": path.stat().st_size,
                }
                if include_hash:
                    entry["sha256_16"] = _sha256_prefix(path)
                tables[path.stem] = entry
            games[game] = {
                "raw_dir": dirname,
                "table_count": len(tables),
                "tables": tables,
            }

        derived: dict[str, Any] = {}
        for rel in DERIVED_DB_FILES:
            path = self.data_root / rel
            if not path.exists():
                continue
            value = _load_json_file(path, {})
            entry = {
                "path": rel.replace("\\", "/"),
                "kind": self._classify_derived(rel),
                "rows": _json_count(value),
                "bytes": path.stat().st_size,
            }
            if include_hash:
                entry["sha256_16"] = _sha256_prefix(path)
            derived[rel.replace("\\", "/")] = entry

        return {
            "schema_version": 1,
            "generated_by": "python/ggpk_index.py",
            "games": games,
            "derived": derived,
        }

    @staticmethod
    def _classify_derived(rel_path: str) -> str:
        if "gem" in rel_path:
            return "gems"
        if "unique" in rel_path:
            return "uniques"
        if "mod" in rel_path or "base" in rel_path:
            return "items_and_mods"
        if "atlas" in rel_path or "farming" in rel_path:
            return "atlas_farming"
        if (
            "build_corpus" in rel_path
            or "creator_source" in rel_path
            or "creator_priority_matrix" in rel_path
            or "source_targets" in rel_path
            or "poe_ninja_build_variant" in rel_path
            or "leveling_archetype_route" in rel_path
            or "representative_build_profiles" in rel_path
            or "representative_source_slot_queue" in rel_path
        ):
            return "operations"
        if "builds/" in rel_path or "build_profile" in rel_path:
            return "builds"
        if (
            "season_research" in rel_path
            or "reliquarian" in rel_path
            or "global_review" in rel_path
            or "live_validation_queue" in rel_path
            or "luminary_merc_link_intake" in rel_path
        ):
            return "season_research"
        if "patch" in rel_path:
            return "patch_notes"
        if "information_intake" in rel_path:
            return "operations"
        if "translation" in rel_path:
            return "translations"
        return "support"

    def catalog_summary(self) -> dict[str, Any]:
        raw = {}
        for table in CORE_TABLES:
            path = self.game_data_dir / f"{table}.json"
            if path.exists():
                raw[table] = len(self.load_table(table))

        derived = {}
        for rel in DERIVED_DB_FILES:
            path = self.data_root / rel
            if path.exists():
                value = self.load_derived(rel)
                derived[rel.replace("\\", "/")] = _json_count(value)

        return {
            "game": self.game,
            "raw_tables": raw,
            "derived_dbs": derived,
        }

    def _ensure_item_indexes(self) -> None:
        if self._items_by_name is not None:
            return
        by_name: dict[str, dict[str, Any]] = {}
        by_id: dict[str, dict[str, Any]] = {}
        for idx, row in enumerate(self.load_table("BaseItemTypes")):
            if not isinstance(row, dict):
                continue
            enriched = dict(row)
            enriched["_row_index"] = idx
            name = row.get("Name")
            item_id = row.get("Id")
            if isinstance(name, str) and name.strip():
                by_name[_norm(name)] = enriched
            if isinstance(item_id, str) and item_id.strip():
                by_id[item_id] = enriched
        self._items_by_name = by_name
        self._items_by_id = by_id

    def get_item(self, name: str) -> Optional[dict[str, Any]]:
        self._ensure_item_indexes()
        assert self._items_by_name is not None
        row = self._items_by_name.get(_norm(name))
        unique_base = self.get_unique_base(name)
        unique_tier = self.get_unique_tier(name)
        if not row and unique_base:
            row = self._items_by_name.get(_norm(unique_base))
        if not row:
            poe2_unique = self.get_poe2_unique(name)
            if poe2_unique:
                return poe2_unique
            return None
        base_name = row.get("Name", "")
        return {
            "name": name if unique_base else base_name,
            "base_type": base_name if unique_base else None,
            "metadata_id": row.get("Id", ""),
            "drop_level": row.get("DropLevel", 0),
            "inherits_from": row.get("InheritsFrom", ""),
            "item_class": row.get("ItemClassesKey", row.get("ItemClass")),
            "tags": row.get("TagsKeys", row.get("Tags", [])),
            "tag_keys": row.get("TagsKeys", row.get("Tags", [])),
            "mod_domain": row.get("ModDomain"),
            "source": f"{self.game}:BaseItemTypes",
            "unique_tier": unique_tier,
            "unique_base": unique_base,
        }

    def _ensure_gem_index(self) -> None:
        if self._gems_by_name is not None:
            return
        self._ensure_item_indexes()
        items = self.load_table("BaseItemTypes")
        by_name: dict[str, dict[str, Any]] = {}
        for row in self.load_table("SkillGems"):
            if not isinstance(row, dict):
                continue
            idx = _first_ref(row, ("BaseItemTypesKey", "BaseItemType"))
            if idx is None or idx >= len(items):
                continue
            item = items[idx]
            if not isinstance(item, dict):
                continue
            name = item.get("Name")
            if not isinstance(name, str) or not name.strip():
                continue
            info = {
                "name": name,
                "metadata_id": item.get("Id", ""),
                "required_level": item.get("DropLevel", row.get("MinLevelReq", 0)),
                "min_level_req": row.get("MinLevelReq"),
                "is_support": bool(row.get("IsSupport", False)) if self.game == "poe1" else row.get("GemType") == 1,
                "is_vaal": bool(row.get("IsVaalVariant", False)),
                "str_pct": row.get("StrengthRequirementPercent", 0),
                "dex_pct": row.get("DexterityRequirementPercent", 0),
                "int_pct": row.get("IntelligenceRequirementPercent", 0),
                "gem_type": row.get("GemType"),
                "tier": row.get("Tier"),
                "source": f"{self.game}:SkillGems+BaseItemTypes",
            }
            key = _norm(name)
            current = by_name.get(key)
            if current is None or _gem_candidate_score(info) > _gem_candidate_score(current):
                by_name[key] = info
        self._gems_by_name = by_name

    def get_gem(self, name: str) -> Optional[dict[str, Any]]:
        self._ensure_gem_index()
        assert self._gems_by_name is not None
        gem = self._gems_by_name.get(_norm(name))
        if not gem:
            return None
        result = dict(gem)
        valid = self.valid_gems()
        result["valid_gem"] = _norm(result["name"]) in valid
        return result

    def valid_gems(self) -> set[str]:
        if self._valid_gems is not None:
            return self._valid_gems
        names: set[str] = set()
        if self.game == "poe2":
            data = self.load_derived("valid_gems_poe2.json")
            if isinstance(data, dict):
                for bucket in ("active", "support", "spirit"):
                    for entry in data.get(bucket, []) or []:
                        if isinstance(entry, dict) and entry.get("name"):
                            names.add(_norm(entry["name"]))
                        elif isinstance(entry, str):
                            names.add(_norm(entry))
        else:
            data = self.load_derived("valid_gems.json")
            if isinstance(data, dict):
                for name in data.get("gems", []) or []:
                    if isinstance(name, str):
                        names.add(_norm(name))
        self._valid_gems = names
        return names

    def _ensure_mod_index(self) -> None:
        if self._mods_by_key is not None:
            return
        by_key: dict[str, list[dict[str, Any]]] = {}
        for row in self.load_table("Mods"):
            if not isinstance(row, dict):
                continue
            for field in ("Id", "Name"):
                value = row.get(field)
                if isinstance(value, str) and value.strip():
                    by_key.setdefault(_norm(value), []).append(row)
        self._mods_by_key = by_key

    def find_mods(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        self._ensure_mod_index()
        assert self._mods_by_key is not None
        exact = self._mods_by_key.get(_norm(query), [])
        rows = exact[:limit]
        if not rows:
            needle = _norm(query)
            for key, candidates in self._mods_by_key.items():
                if needle in key:
                    rows.extend(candidates)
                    if len(rows) >= limit:
                        break
        return [
            {
                **_pick(
                    row,
                    (
                        "Id",
                        "Name",
                        "Level",
                        "MaxLevel",
                        "Domain",
                        "GenerationType",
                        "ModTypeKey",
                        "ModType",
                    ),
                ),
                "source": f"{self.game}:Mods",
            }
            for row in rows[:limit]
        ]

    def _ensure_tag_index(self) -> None:
        if self._tag_key_by_id is not None and self._tag_id_by_key is not None:
            return
        by_id: dict[str, int] = {}
        by_key: dict[int, str] = {}
        for idx, row in enumerate(self.load_table("Tags")):
            tag_id = row.get("Id")
            if isinstance(tag_id, str) and tag_id:
                by_id[tag_id] = idx
                by_key[idx] = tag_id
        self._tag_key_by_id = by_id
        self._tag_id_by_key = by_key

    def _tag_key(self, tag_id: str) -> Optional[int]:
        self._ensure_tag_index()
        assert self._tag_key_by_id is not None
        return self._tag_key_by_id.get(tag_id)

    def _tag_id(self, tag_key: int) -> str:
        self._ensure_tag_index()
        assert self._tag_id_by_key is not None
        return self._tag_id_by_key.get(tag_key, str(tag_key))

    def _add_known_tag(self, tags: set[int], tag_id: str) -> None:
        key = self._tag_key(tag_id)
        if key is not None:
            tags.add(key)

    def _effective_item_tag_keys(self, item: dict[str, Any]) -> set[int]:
        """Return explicit + inferred item tags used for mod spawn weights.

        BaseItemTypes often omits class tags on concrete weapon bases. For
        example, Pneumatic Dagger may only carry experimental-base tags while
        its `InheritsFrom` path still proves it is a dagger. The mod spawn
        weight table expects tags such as `weapon` and `dagger`, so we infer
        conservative class tags from the inheritance path.
        """
        tags = {
            value
            for value in (item.get("TagsKeys") or item.get("tag_keys") or item.get("tags") or [])
            if isinstance(value, int) and value >= 0
        }
        path = str(item.get("InheritsFrom") or item.get("inherits_from") or item.get("Id") or item.get("metadata_id") or "").casefold()

        inferred: list[str] = []
        if "/bodyarmours/" in path:
            inferred += ["equipment", "armour", "body_armour"]
        if "/helmets/" in path:
            inferred += ["equipment", "armour", "helmet"]
        if "/boots/" in path:
            inferred += ["equipment", "armour", "boots"]
        if "/gloves/" in path:
            inferred += ["equipment", "armour", "gloves"]
        if "/shields/" in path:
            inferred += ["equipment", "armour", "shield"]

        if "/weapons/" in path:
            inferred += ["equipment", "weapon"]
        if "/daggers/" in path:
            inferred.append("dagger")
        if "/claws/" in path:
            inferred.append("claw")
        if "/bows/" in path:
            inferred.append("bow")
        if "/wands/" in path:
            inferred.append("wand")
        if "/onehandaxes/" in path or "/twohandaxes/" in path:
            inferred.append("axe")
        if "/onehandmaces/" in path or "/twohandmaces/" in path:
            inferred.append("mace")
        if "/onehandswords/" in path or "/twohandswords/" in path:
            inferred.append("sword")
        if "/staves/" in path or "/warstaves/" in path:
            inferred.append("staff")

        item_class = item.get("ItemClassesKey", item.get("item_class"))
        if item.get("Name", item.get("name")) and item_class in (7,):
            inferred += ["equipment", "weapon", "dagger"]

        for tag_id in inferred:
            self._add_known_tag(tags, tag_id)
        return tags

    @staticmethod
    def _generation_type_name(value: Any) -> str:
        return {1: "prefix", 2: "suffix"}.get(value, str(value))

    @staticmethod
    def _spawn_weight_for_tags(mod: dict[str, Any], item_tags: set[int]) -> int:
        tags = mod.get("SpawnWeight_TagsKeys") or []
        values = mod.get("SpawnWeight_Values") or []
        fallback = 0
        for tag, value in zip(tags, values):
            if not isinstance(tag, int) or not isinstance(value, int):
                continue
            if tag == 0:
                fallback = value
                continue
            if tag in item_tags:
                return value
        return fallback

    @staticmethod
    def _mod_stat_ranges(row: dict[str, Any]) -> list[dict[str, int]]:
        ranges = []
        for idx in range(1, 7):
            key = row.get(f"StatsKey{idx}")
            if not _is_valid_ref(key):
                continue
            ranges.append({
                "stats_key": key,
                "min": int(row.get(f"Stat{idx}Min") or 0),
                "max": int(row.get(f"Stat{idx}Max") or 0),
            })
        return ranges

    def get_item_mod_candidates(
        self,
        item_name: str,
        *,
        item_level: int = 100,
        generation_types: tuple[int, ...] = (1, 2),
        limit_per_group: int = 120,
    ) -> Optional[dict[str, Any]]:
        """Resolve prefix/suffix mods that can spawn on a concrete base item.

        This is a derived view over BaseItemTypes + Mods, not a handcrafted
        build recommendation. It answers "can this affix spawn on this base?"
        before later layers decide whether that affix matters for a shell.
        """
        item = self.get_item(item_name)
        if item is None:
            return None

        item_tags = self._effective_item_tag_keys(item)
        item_domain = item.get("mod_domain", item.get("ModDomain"))
        groups: dict[str, list[dict[str, Any]]] = {
            self._generation_type_name(gen): [] for gen in generation_types
        }

        for row in self.load_table("Mods"):
            if not isinstance(row, dict):
                continue
            gen = row.get("GenerationType")
            if gen not in generation_types:
                continue
            if item_domain is not None and row.get("Domain") != item_domain:
                continue
            level = row.get("Level")
            if isinstance(level, int) and level > item_level:
                continue
            weight = self._spawn_weight_for_tags(row, item_tags)
            if weight <= 0:
                continue

            bucket = self._generation_type_name(gen)
            groups.setdefault(bucket, []).append({
                "id": row.get("Id"),
                "name": row.get("Name"),
                "level": row.get("Level"),
                "max_level": row.get("MaxLevel"),
                "generation_type": bucket,
                "spawn_weight": weight,
                "mod_type_key": row.get("ModTypeKey"),
                "families": row.get("Families") or [],
                "is_essence_only": bool(row.get("IsEssenceOnlyModifier")),
                "stats": self._mod_stat_ranges(row),
            })

        for values in groups.values():
            values.sort(key=lambda row: (str(row.get("name") or ""), int(row.get("level") or 0), str(row.get("id") or "")))

        return {
            "source": f"{self.game}:BaseItemTypes+Mods",
            "item": {
                "name": item.get("name"),
                "base_type": item.get("base_type"),
                "metadata_id": item.get("metadata_id"),
                "drop_level": item.get("drop_level"),
                "mod_domain": item_domain,
                "explicit_tag_keys": item.get("tag_keys", []),
                "effective_tags": sorted(self._tag_id(tag) for tag in item_tags),
            },
            "item_level": item_level,
            "generation_types": [self._generation_type_name(gen) for gen in generation_types],
            "counts": {key: len(values) for key, values in groups.items()},
            "mods": {
                key: values[:limit_per_group]
                for key, values in groups.items()
            },
            "truncated": {
                key: len(values) > limit_per_group
                for key, values in groups.items()
            },
        }

    def _ensure_passive_index(self) -> None:
        if self._passives_by_key is not None and self._passives_by_graph_id is not None:
            return
        by_key: dict[str, list[dict[str, Any]]] = {}
        by_graph_id: dict[int, dict[str, Any]] = {}
        for row in self.load_table("PassiveSkills"):
            if not isinstance(row, dict):
                continue
            for field in ("Id", "Name"):
                value = row.get(field)
                if isinstance(value, str) and value.strip():
                    by_key.setdefault(_norm(value), []).append(row)
            graph_id = row.get("PassiveSkillGraphId")
            if isinstance(graph_id, int):
                by_graph_id[graph_id] = row
        self._passives_by_key = by_key
        self._passives_by_graph_id = by_graph_id

    @staticmethod
    def _passive_stat_values(row: dict[str, Any]) -> list[dict[str, int]]:
        values: list[dict[str, int]] = []
        for idx, stat_key in enumerate(row.get("Stats") or [], start=1):
            if not _is_valid_ref(stat_key):
                continue
            values.append({
                "stats_key": int(stat_key),
                "value": int(row.get(f"Stat{idx}Value") or 0),
            })
        return values

    def _ensure_skilltree_nodes(self) -> None:
        if self._skilltree_nodes_by_id is not None:
            return
        data = _load_json_file(self.data_root / "skilltree-export" / "data.json", {})
        nodes = data.get("nodes", {}) if isinstance(data, dict) else {}
        self._skilltree_nodes_by_id = {
            str(node_id): node
            for node_id, node in nodes.items()
            if isinstance(node, dict)
        }

    def _skilltree_node_for_graph_id(self, graph_id: int | str) -> Optional[dict[str, Any]]:
        self._ensure_skilltree_nodes()
        assert self._skilltree_nodes_by_id is not None
        try:
            node_int = int(graph_id)
        except (TypeError, ValueError):
            return None
        keys = [str(node_int)]
        if node_int < 0:
            keys.append(str(node_int + 65536))
        if node_int > 32767:
            keys.append(str(node_int - 65536))
        for key in keys:
            node = self._skilltree_nodes_by_id.get(key)
            if node is not None:
                return node
        return None

    def get_passive_by_graph_id(self, node_id: str | int) -> Optional[dict[str, Any]]:
        """Lookup a passive by official tree node id / PassiveSkillGraphId.

        Official passive tree URLs encode node ids as unsigned u16. The GGPK
        table may store the same 16-bit value as a signed int, so values above
        32767 are retried as `node_id - 65536`.
        """
        self._ensure_passive_index()
        assert self._passives_by_graph_id is not None
        try:
            raw_id = int(node_id)
        except (TypeError, ValueError):
            return None

        candidates = [raw_id]
        if raw_id > 32767:
            candidates.append(raw_id - 65536)
        row = None
        for graph_id in candidates:
            row = self._passives_by_graph_id.get(graph_id)
            if row is not None:
                break
        if row is None:
            tree_node = self._skilltree_node_for_graph_id(raw_id)
            if tree_node is None:
                return None
            semantic = passive_node_stat_semantics(
                graph_id=raw_id,
                stat_values=[],
                tree_node=tree_node,
            )
            return {
                "node_id": str(node_id),
                "graph_id": raw_id,
                "id": None,
                "name": tree_node.get("name"),
                "is_notable": bool(tree_node.get("isNotable")),
                "is_keystone": bool(tree_node.get("isKeystone")),
                "is_jewel_socket": bool(tree_node.get("isJewelSocket")),
                "is_ascendancy_starting_node": False,
                "is_multiple_choice": False,
                "is_multiple_choice_option": False,
                "ascendancy_key": None,
                "mastery_group": None,
                "stats": [],
                **semantic,
                "source": f"{self.game}:skilltree-export",
            }

        tree_node = self._skilltree_node_for_graph_id(row.get("PassiveSkillGraphId"))
        stat_values = self._passive_stat_values(row)
        semantic = passive_node_stat_semantics(
            graph_id=row.get("PassiveSkillGraphId"),
            stat_values=stat_values,
            tree_node=tree_node,
        )
        return {
            "node_id": str(node_id),
            "graph_id": row.get("PassiveSkillGraphId"),
            "id": row.get("Id"),
            "name": row.get("Name"),
            "is_notable": bool(row.get("IsNotable")),
            "is_keystone": bool(row.get("IsKeystone")),
            "is_jewel_socket": bool(row.get("IsJewelSocket")),
            "is_ascendancy_starting_node": bool(row.get("IsAscendancyStartingNode")),
            "is_multiple_choice": bool(row.get("IsMultipleChoice")),
            "is_multiple_choice_option": bool(row.get("IsMultipleChoiceOption")),
            "ascendancy_key": row.get("AscendancyKey"),
            "mastery_group": row.get("MasteryGroup"),
            "stats": stat_values,
            **semantic,
            "source": f"{self.game}:PassiveSkills",
        }

    def get_passives_by_graph_ids(self, node_ids: Iterable[str | int]) -> dict[str, Any]:
        resolved: list[dict[str, Any]] = []
        missing: list[str] = []
        for node_id in node_ids:
            info = self.get_passive_by_graph_id(node_id)
            if info:
                resolved.append(info)
            else:
                missing.append(str(node_id))
        return {
            "resolved": resolved,
            "missing": missing,
            "counts": {
                "total": len(resolved) + len(missing),
                "resolved": len(resolved),
                "missing": len(missing),
                "notables": sum(1 for row in resolved if row.get("is_notable")),
                "keystones": sum(1 for row in resolved if row.get("is_keystone")),
                "jewel_sockets": sum(1 for row in resolved if row.get("is_jewel_socket")),
            },
        }

    def find_passives(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        self._ensure_passive_index()
        assert self._passives_by_key is not None
        rows = self._passives_by_key.get(_norm(query), [])[:limit]
        return [
            {
                **_pick(
                    row,
                    (
                        "Id",
                        "Name",
                        "IsNotable",
                        "IsKeystone",
                        "IsJewelSocket",
                        "IsAscendancyStartingNode",
                        "AscendancyKey",
                        "Ascendancy",
                    ),
                ),
                "source": f"{self.game}:PassiveSkills",
            }
            for row in rows
        ]

    def _ensure_map_index(self) -> None:
        if self._maps_by_name is not None:
            return
        items = self.load_table("BaseItemTypes")
        by_name: dict[str, dict[str, Any]] = {}
        for row in self.load_table("Maps"):
            if not isinstance(row, dict):
                continue
            idx = _first_ref(row, ("BaseItemTypesKey", "BaseItemType"))
            if idx is None or idx >= len(items):
                continue
            item = items[idx]
            if not isinstance(item, dict):
                continue
            name = item.get("Name")
            if isinstance(name, str) and name.strip():
                by_name[_norm(name)] = {
                    "name": name,
                    "tier": row.get("Tier"),
                    "metadata_id": item.get("Id", ""),
                    "source": f"{self.game}:Maps+BaseItemTypes",
                }
        self._maps_by_name = by_name

    def get_map(self, name: str) -> Optional[dict[str, Any]]:
        self._ensure_map_index()
        assert self._maps_by_name is not None
        row = self._maps_by_name.get(_norm(name))
        return dict(row) if row else None

    def get_unique_tier(self, unique_name: str) -> Optional[str]:
        if self._unique_tiers is None:
            tiers: dict[str, str] = {}
            data = self.load_derived("unique_tiers.json")
            tier_root = data.get("tiers", {}) if isinstance(data, dict) else {}
            if isinstance(tier_root, dict):
                for tier, names in tier_root.items():
                    if isinstance(names, list):
                        for name in names:
                            if isinstance(name, str):
                                tiers[_norm(name)] = tier
            self._unique_tiers = tiers
        return self._unique_tiers.get(_norm(unique_name))

    def get_unique_base(self, unique_name: str) -> Optional[str]:
        if self._unique_bases is None:
            bases: dict[str, str] = {}
            data = self.load_derived("unique_base_mapping.json")
            mapping = data.get("unique_to_base", {}) if isinstance(data, dict) else {}
            if isinstance(mapping, dict):
                for name, base in mapping.items():
                    if isinstance(name, str) and isinstance(base, str):
                        bases[_norm(name)] = base
            self._unique_bases = bases
        return self._unique_bases.get(_norm(unique_name))

    def get_poe2_unique(self, unique_name: str) -> Optional[dict[str, Any]]:
        if self.game != "poe2":
            return None
        if self._poe2_uniques is None:
            uniques: dict[str, dict[str, Any]] = {}
            data = self.load_derived("uniques_poe2.json")
            rows = data.get("uniques", []) if isinstance(data, dict) else []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                name = row.get("name")
                if isinstance(name, str) and name.strip():
                    uniques[_norm(name)] = row
            self._poe2_uniques = uniques
        row = self._poe2_uniques.get(_norm(unique_name))
        if not row:
            return None
        return {
            "name": row.get("name"),
            "base_type": row.get("stash_type_label"),
            "metadata_id": row.get("visual_id"),
            "drop_level": None,
            "inherits_from": "",
            "item_class": row.get("stash_type_label"),
            "tags": [],
            "source": "poe2:uniques_poe2",
            "unique_tier": None,
            "unique_base": row.get("stash_type_label"),
        }

    def build_targeted_context(self, build_data: dict, max_items: int = 12, max_gems: int = 24) -> dict[str, Any]:
        gem_names = self.extract_gem_names(build_data)[:max_gems]
        item_names = self.extract_item_names(build_data)[:max_items]

        gems = [info for name in gem_names if (info := self.get_gem(name))]
        items = [info for name in item_names if (info := self.get_item(name))]

        missing_gems = [name for name in gem_names if not self.get_gem(name)]
        missing_items = [name for name in item_names if not self.get_item(name)]

        return {
            "game": self.game,
            "catalog": self.catalog_summary(),
            "matched_gems": gems,
            "missing_gems": missing_gems,
            "matched_items": items,
            "missing_items": missing_items,
        }

    @staticmethod
    def extract_gem_names(build_data: dict) -> list[str]:
        names: set[str] = set()
        stages = build_data.get("progression_stages", [])
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            for setup_name, links in (stage.get("gem_setups", {}) or {}).items():
                if isinstance(setup_name, str):
                    names.add(setup_name)
                if isinstance(links, list):
                    for link in links:
                        if isinstance(link, str):
                            names.add(link)
                        elif isinstance(link, dict):
                            value = link.get("name", link.get("gem", ""))
                            if value:
                                names.add(value)
                elif isinstance(links, dict):
                    for key in ("name", "gem", "links"):
                        value = links.get(key)
                        if isinstance(value, str):
                            for part in value.replace(" - ", "|").split("|"):
                                part = part.strip()
                                if part:
                                    names.add(part)
            for alt in (stage.get("alternate_gem_sets", {}) or {}).values():
                if isinstance(alt, dict):
                    for setup_name, value in alt.items():
                        if isinstance(setup_name, str):
                            names.add(setup_name)
                        if isinstance(value, dict) and isinstance(value.get("links"), str):
                            for part in value["links"].replace(" - ", "|").split("|"):
                                part = part.strip()
                                if part:
                                    names.add(part)
        return sorted(names)

    @staticmethod
    def extract_item_names(build_data: dict) -> list[str]:
        names: set[str] = set()
        for item in build_data.get("items", []) or []:
            if isinstance(item, dict):
                for key in ("name", "base_type", "base"):
                    value = item.get(key)
                    if isinstance(value, str) and value.strip():
                        names.add(value.strip())
        for stage in build_data.get("progression_stages", []) or []:
            if not isinstance(stage, dict):
                continue
            gear = stage.get("gear_recommendation", {}) or {}
            if isinstance(gear, dict):
                for item in gear.values():
                    if isinstance(item, dict):
                        for key in ("name", "base_type", "base", "item"):
                            value = item.get(key)
                            if isinstance(value, str) and value.strip() and not value.lower().startswith("rare "):
                                names.add(value.strip())
        return sorted(names)


def write_catalog(path: Path, include_hash: bool = False) -> dict[str, Any]:
    catalog = GGPKIndex().build_catalog(include_hash=include_hash)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return catalog


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect GGPK extracts and derived Pathcraft DBs.")
    parser.add_argument("--game", choices=("poe1", "poe2"), default="poe1")
    parser.add_argument("--write-catalog", type=Path, help="Write deterministic DB catalog JSON.")
    parser.add_argument("--hash", action="store_true", help="Include sha256 prefixes in catalog output.")
    parser.add_argument("--item", help="Lookup an item/base name.")
    parser.add_argument("--item-mods", help="Lookup prefix/suffix mods that can spawn on an item/base name.")
    parser.add_argument("--item-level", type=int, default=100, help="Item level for --item-mods filtering.")
    parser.add_argument("--gem", help="Lookup a gem name.")
    parser.add_argument("--mod", help="Lookup a mod Id/name.")
    args = parser.parse_args(argv)

    index = GGPKIndex(game=args.game)
    if args.write_catalog:
        write_catalog(args.write_catalog, include_hash=args.hash)
        return 0

    payload: dict[str, Any] = {"catalog": index.catalog_summary()}
    if args.item:
        payload["item"] = index.get_item(args.item)
    if args.item_mods:
        payload["item_mods"] = index.get_item_mod_candidates(args.item_mods, item_level=args.item_level)
    if args.gem:
        payload["gem"] = index.get_gem(args.gem)
    if args.mod:
        payload["mods"] = index.find_mods(args.mod)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
