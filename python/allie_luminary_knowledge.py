# -*- coding: utf-8 -*-
"""Versioned Allie Bob & Friends Luminary knowledge and diagnosis layer.

The structured JSON is canonical.  This module deliberately reuses the proven
local FTS5/vector implementation from ``cws_knowledge`` while keeping Allie's
player, mercenary, Animate Guardian, and spectre states as separate entities.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

from cws_knowledge import (
    CWSKnowledgeBase,
    CWSKnowledgeError,
    _condition_matches,
    _dedupe_refs,
    _documents,
    hashing_embedder,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK = ROOT / "data" / "guide_sources" / "poe1_luminary_allie_bob_friends_3_29_v1.json"

QUERY_ALIASES = {
    "앨리": ("allie", "bob friends"),
    "알리": ("allie", "bob friends"),
    "루미너리": ("luminary", "mercenary", "aurabot"),
    "용병": ("mercenary", "manyshot", "kineticist"),
    "밥": ("bob", "animate guardian", "hallowed monarch"),
    "오라봇": ("aurabot", "flame link", "aura"),
    "딜이 안": ("weak mercenary", "supports", "flame link"),
    "약해": ("weak mercenary", "supports", "diagnosis"),
    "죽": ("death", "survivability", "hardcore"),
    "소울이터": ("soul eater", "soulthirst", "ceinture"),
    "스톰블라스트": ("stormblast mine", "smite", "correction"),
    "망령": ("spectre", "empower", "arena master"),
}


class LuminaryKnowledgeError(CWSKnowledgeError):
    """Raised when the Allie Luminary pack is internally inconsistent."""


def load_pack(path: Path | str = DEFAULT_PACK) -> dict[str, Any]:
    pack = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    validate_pack(pack)
    return pack


def validate_pack(pack: dict[str, Any]) -> None:
    if pack.get("dataset_kind") != "pathcraft_creator_build_knowledge_pack":
        raise LuminaryKnowledgeError("unexpected dataset_kind")
    if pack.get("build_id") != "poe1_3_29_allie_bob_friends_luminary":
        raise LuminaryKnowledgeError("unexpected build_id")
    if pack.get("patch") != "3.29":
        raise LuminaryKnowledgeError("Luminary pack must be patch-locked to 3.29")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(pack.get("knowledge_version", ""))):
        raise LuminaryKnowledgeError("knowledge_version must use semantic versioning")

    source_rows = pack.get("sources", [])
    claim_rows = pack.get("claims", [])
    source_ids = [row.get("source_id") for row in source_rows]
    claim_ids = [row.get("claim_id") for row in claim_rows]
    if None in source_ids or len(source_ids) != len(set(source_ids)):
        raise LuminaryKnowledgeError("source_id values must be present and unique")
    if None in claim_ids or len(claim_ids) != len(set(claim_ids)):
        raise LuminaryKnowledgeError("claim_id values must be present and unique")

    source_set = set(source_ids)
    claim_set = set(claim_ids)
    for claim in claim_rows:
        if not claim.get("text_ko") or not claim.get("source_refs"):
            raise LuminaryKnowledgeError(f"claim lacks text/source_refs: {claim.get('claim_id')}")
        for ref in claim["source_refs"]:
            if ref.get("source_id") not in source_set:
                raise LuminaryKnowledgeError(f"dangling source ref: {ref}")
    for rule in pack.get("diagnostic_rules", []):
        dangling = set(rule.get("claim_refs", [])) - claim_set
        if dangling:
            raise LuminaryKnowledgeError(f"rule {rule.get('rule_id')} has dangling claims: {sorted(dangling)}")
    for media in pack.get("media_catalog", []):
        if media.get("source_id") not in source_set:
            raise LuminaryKnowledgeError(f"media has dangling source: {media.get('video_id')}")
    orders = [row.get("order") for row in pack.get("pob_variants", []) if row.get("order") is not None]
    if len(orders) != len(set(orders)):
        raise LuminaryKnowledgeError("ordered PoB variants must have unique order values")


def normalize_query(query: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(query or ""))
    normalized = re.sub(r"\s+", " ", normalized.strip().casefold())
    expanded = [normalized]
    compact = normalized.replace(" ", "")
    for needle, aliases in QUERY_ALIASES.items():
        if needle in normalized or needle.replace(" ", "") in compact:
            expanded.extend(aliases)
    return " ".join(dict.fromkeys(part for part in expanded if part))


def _luminary_documents(pack: dict[str, Any]) -> list[dict[str, Any]]:
    # cws_knowledge's document builder is build-agnostic for claims, rules, and
    # variants.  Allie media uses its own source ids, so it is appended here.
    base_pack = dict(pack)
    base_pack.pop("vod_catalog", None)
    docs = _documents(base_pack)
    for media in pack.get("media_catalog", []):
        docs.append({
            "doc_id": f"media:{media['video_id']}",
            "record_type": "media",
            "title": media.get("title") or media["video_id"],
            "text": json.dumps(media, ensure_ascii=False),
            "metadata": {
                "patch": pack["patch"],
                "date": media.get("date"),
                "phase": media.get("phase"),
                "platform": media.get("platform", "youtube"),
            },
            "source_refs": [{"source_id": media.get("source_id", "youtube_launch_guide"), "locator": media["url"]}],
        })
    return docs


class LuminaryKnowledgeBase(CWSKnowledgeBase):
    def __init__(self, pack_path: Path | str = DEFAULT_PACK):
        self.pack_path = Path(pack_path)
        self.pack = load_pack(self.pack_path)
        self.docs = _luminary_documents(self.pack)

    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        return super().search(normalize_query(query), **kwargs)

    def diagnose(self, state: dict[str, Any], limit: int = 8) -> dict[str, Any]:
        matches = []
        claims = {row["claim_id"]: row for row in self.pack.get("claims", [])}
        for rule in self.pack.get("diagnostic_rules", []):
            conditions = rule.get("when", [])
            if conditions and all(_condition_matches(state, condition) for condition in conditions):
                refs = []
                for claim_id in rule.get("claim_refs", []):
                    refs.extend(claims[claim_id].get("source_refs", []))
                matches.append({
                    "rule_id": rule["rule_id"],
                    "priority": rule.get("priority", 0),
                    "explanation_ko": rule.get("explanation_ko"),
                    "actions_ko": rule.get("actions_ko", []),
                    "claim_refs": rule.get("claim_refs", []),
                    "source_refs": _dedupe_refs(refs),
                })
        matches.sort(key=lambda row: (-row["priority"], row["rule_id"]))
        required = (
            "variant", "player_pob_url", "merc_snapshot", "merc_class",
            "merc_skills", "merc_gear", "bob_state", "flame_link_active",
            "content", "map_mods",
        )
        return {
            "build_id": self.pack["build_id"],
            "patch": self.pack["patch"],
            "diagnoses": matches[:limit],
            "missing_observations": [key for key in required if key not in state],
            "disclaimer": "본체·용병·Bob·망령을 분리한 규칙 기반 후보 진단이다. 실제 장면과 각 엔티티 상태로 확인해야 한다.",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and query Allie's 3.29 Luminary knowledge index.")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("index")
    build.add_argument("--db", type=Path, required=True)
    build.add_argument("--no-vectors", action="store_true")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--db", type=Path)
    search.add_argument("--limit", type=int, default=8)
    diagnose = sub.add_parser("diagnose")
    diagnose.add_argument("--state", required=True, help="JSON object or path to JSON")
    args = parser.parse_args(argv)

    kb = LuminaryKnowledgeBase(args.pack)
    if args.command == "index":
        result = kb.build_index(args.db, None if args.no_vectors else hashing_embedder)
    elif args.command == "search":
        result = kb.search(args.query, db_path=args.db, embedder=hashing_embedder if args.db else None, limit=args.limit)
    else:
        state_arg = args.state.strip()
        state_path = None if state_arg.startswith("{") else Path(state_arg)
        raw = state_path.read_text(encoding="utf-8") if state_path and state_path.exists() else state_arg
        result = kb.diagnose(json.loads(raw))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
