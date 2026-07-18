# -*- coding: utf-8 -*-
"""Runtime lookup helpers for the generated POE1 gem taxonomy DB."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
TAXONOMY_PATH = DATA_ROOT / "poe1_gem_taxonomy.latest.json"

ACTIVE_KINDS = {
    "active_gem",
    "active_transfigured_or_valid_active",
    "active_skill_only",
    "active_skill_only_and_support_alias",
}
SOCKETABLE_ACTIVE_KINDS = {
    "active_gem",
    "active_transfigured_or_valid_active",
}
SUPPORT_KINDS = {
    "support_gem",
    "support_alias",
}


def _norm(value: str) -> str:
    return value.strip().casefold()


@lru_cache(maxsize=1)
def load_gem_taxonomy() -> dict[str, Any]:
    if not TAXONOMY_PATH.exists():
        return {}
    with TAXONOMY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _entry_index() -> dict[str, dict[str, Any]]:
    taxonomy = load_gem_taxonomy()
    entries = taxonomy.get("entries", {}) if isinstance(taxonomy, dict) else {}
    if not isinstance(entries, dict):
        return {}
    return {
        _norm(name): entry
        for name, entry in entries.items()
        if isinstance(name, str) and isinstance(entry, dict)
    }


def get_gem_entry(name: str) -> dict[str, Any] | None:
    if not isinstance(name, str) or not name.strip():
        return None
    return _entry_index().get(_norm(name))


def resolve_gem_name(
    name: str,
    *,
    allow_support_alias: bool = True,
    require_socketable: bool = True,
) -> str | None:
    """Resolve a raw PoB gem label into the canonical socketable gem name.

    Bare support aliases such as "Added Lightning Damage" resolve to
    "Added Lightning Damage Support", but real active gems such as "Barrage"
    remain active even when a sibling "Barrage Support" exists.
    """
    entry = get_gem_entry(name)
    if not entry:
        return None

    gem_kind = entry.get("gem_kind")
    if gem_kind == "support_alias":
        return entry.get("support_alias_of") if allow_support_alias else None
    if gem_kind == "active_skill_only_and_support_alias":
        return entry.get("support_alias_of") if allow_support_alias else None

    if require_socketable and not entry.get("socketable"):
        return None

    canonical = entry.get("name")
    return canonical if isinstance(canonical, str) and canonical else None


def is_support_gem(name: str) -> bool:
    entry = get_gem_entry(name)
    return bool(entry and entry.get("gem_kind") == "support_gem")


def is_active_gem(name: str, *, socketable_only: bool = False) -> bool:
    entry = get_gem_entry(name)
    if not entry:
        return False
    allowed = SOCKETABLE_ACTIVE_KINDS if socketable_only else ACTIVE_KINDS
    return entry.get("gem_kind") in allowed


def is_offensive_active(name: str, *, socketable_only: bool = False) -> bool:
    entry = get_gem_entry(name)
    if not entry:
        return False
    if socketable_only and not entry.get("socketable"):
        return False
    return entry.get("gem_kind") in ACTIVE_KINDS and entry.get("offense_class") == "offensive_active"


def damage_flags_for(name: str) -> dict[str, bool]:
    entry = get_gem_entry(name) or {}
    flags = entry.get("damage_flags", {})
    if not isinstance(flags, dict):
        flags = {}
    return {
        "attack": bool(flags.get("attack")),
        "caster": bool(flags.get("caster")),
        "dot": bool(flags.get("dot")),
        "minion": bool(flags.get("minion")),
    }


def weapon_requirements_for(name: str) -> list[str]:
    entry = get_gem_entry(name) or {}
    values = entry.get("weapon_requirements", [])
    return [value for value in values if isinstance(value, str)]
