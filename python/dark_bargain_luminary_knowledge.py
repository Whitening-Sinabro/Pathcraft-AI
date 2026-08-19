# -*- coding: utf-8 -*-
"""3.29 SSF Dark Bargain Intuitive Link Luminary knowledge layer."""

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
DEFAULT_PACK = ROOT / "data" / "guide_sources" / "poe1_dark_bargain_intuitive_link_luminary_3_29_v1.json"

QUERY_ALIASES = {
    "다크 바겐": ("dark bargain", "dark pact"),
    "다크팩트": ("dark bargain", "dark pact"),
    "루미너리": ("luminary", "scion"),
    "직관의 연결": ("intuitive link",),
    "인튜이티브 링크": ("intuitive link",),
    "해골": ("summon skeletons", "skeleton life"),
    "원버튼": ("one button", "automatic skeleton delivery"),
    "아틀라스": ("atlas curriculum", "mechanic progression"),
    "자급자족": ("ssf", "acquisition"),
}


class DarkBargainLuminaryError(CWSKnowledgeError):
    """Raised when the Dark Bargain Luminary pack is inconsistent."""


def load_pack(path: Path | str = DEFAULT_PACK) -> dict[str, Any]:
    pack = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    validate_pack(pack)
    return pack


def validate_pack(pack: dict[str, Any]) -> None:
    if pack.get("dataset_kind") != "pathcraft_creator_build_knowledge_pack":
        raise DarkBargainLuminaryError("unexpected dataset_kind")
    if pack.get("build_id") != "poe1_3_29_dark_bargain_intuitive_link_luminary_ssf":
        raise DarkBargainLuminaryError("unexpected build_id")
    if pack.get("patch") != "3.29":
        raise DarkBargainLuminaryError("pack must be patch-locked to 3.29")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(pack.get("knowledge_version", ""))):
        raise DarkBargainLuminaryError("knowledge_version must use semantic versioning")

    sources = pack.get("sources", [])
    claims = pack.get("claims", [])
    source_ids = [row.get("source_id") for row in sources]
    claim_ids = [row.get("claim_id") for row in claims]
    if None in source_ids or len(source_ids) != len(set(source_ids)):
        raise DarkBargainLuminaryError("source_id values must be present and unique")
    if None in claim_ids or len(claim_ids) != len(set(claim_ids)):
        raise DarkBargainLuminaryError("claim_id values must be present and unique")
    source_set, claim_set = set(source_ids), set(claim_ids)

    for claim in claims:
        if not claim.get("text_ko") or not claim.get("source_refs"):
            raise DarkBargainLuminaryError(f"claim lacks text/source_refs: {claim.get('claim_id')}")
        for ref in claim["source_refs"]:
            if ref.get("source_id") not in source_set:
                raise DarkBargainLuminaryError(f"dangling source ref: {ref}")
    for rule in pack.get("diagnostic_rules", []):
        dangling = set(rule.get("claim_refs", [])) - claim_set
        if dangling:
            raise DarkBargainLuminaryError(f"rule {rule.get('rule_id')} has dangling claims: {sorted(dangling)}")
    for chain in pack.get("revision_chain", []):
        if chain.get("source_id") not in source_set:
            raise DarkBargainLuminaryError(f"revision has dangling source: {chain}")

    for key in ("pob_variants", "atlas_curriculum"):
        rows = pack.get(key, [])
        orders = [row.get("order") for row in rows]
        if not rows or None in orders or len(orders) != len(set(orders)):
            raise DarkBargainLuminaryError(f"{key} must have unique explicit order values")
        if sorted(orders) != list(range(len(orders))):
            raise DarkBargainLuminaryError(f"{key} order values must be contiguous from zero")


def normalize_query(query: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(query or ""))
    normalized = re.sub(r"\s+", " ", normalized.strip().casefold())
    expanded = [normalized]
    compact = normalized.replace(" ", "")
    for needle, aliases in QUERY_ALIASES.items():
        if needle in normalized or needle.replace(" ", "") in compact:
            expanded.extend(aliases)
    return " ".join(dict.fromkeys(part for part in expanded if part))


def _pack_documents(pack: dict[str, Any]) -> list[dict[str, Any]]:
    docs = _documents(pack)
    for phase in pack.get("atlas_curriculum", []):
        docs.append({
            "doc_id": f"atlas:{phase['phase_id']}",
            "record_type": "atlas_curriculum",
            "title": phase["phase_id"],
            "text": json.dumps(phase, ensure_ascii=False),
            "metadata": {
                "patch": pack["patch"],
                "order": phase["order"],
                "map_band": phase.get("map_band"),
                "focus": phase.get("focus", []),
            },
            "source_refs": [{"source_id": "pathcraft_adaptation", "locator": phase["phase_id"]}],
        })
    return docs


class DarkBargainLuminaryKnowledgeBase(CWSKnowledgeBase):
    def __init__(self, pack_path: Path | str = DEFAULT_PACK):
        self.pack_path = Path(pack_path)
        self.pack = load_pack(self.pack_path)
        self.docs = _pack_documents(self.pack)

    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        return super().search(normalize_query(query), **kwargs)

    def diagnose(self, state: dict[str, Any], limit: int = 8) -> dict[str, Any]:
        claims = {row["claim_id"]: row for row in self.pack.get("claims", [])}
        matches = []
        for rule in self.pack.get("diagnostic_rules", []):
            if all(_condition_matches(state, condition) for condition in rule.get("when", [])):
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
            "player_pob_url", "atlas_phase", "is_ci", "energy_shield",
            "link_trigger_reliable", "linked_allies_survive", "content",
        )
        return {
            "build_id": self.pack["build_id"],
            "patch": self.pack["patch"],
            "status": self.pack["status"],
            "diagnoses": matches[:limit],
            "missing_observations": [key for key in required if key not in state],
            "disclaimer": "실험형 SSF 진단이다. 공개 이론 PoB를 성능 증명으로 취급하지 말고 실제 링크 대상, 해골 공급, PoB와 실패 장면으로 검증해야 한다.",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query the 3.29 SSF Dark Bargain Luminary pack.")
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
    diagnose.add_argument("--state", required=True)
    args = parser.parse_args(argv)

    kb = DarkBargainLuminaryKnowledgeBase(args.pack)
    if args.command == "index":
        result = kb.build_index(args.db, None if args.no_vectors else hashing_embedder)
    elif args.command == "search":
        result = kb.search(args.query, db_path=args.db, embedder=hashing_embedder if args.db else None, limit=args.limit)
    else:
        raw_arg = args.state.strip()
        state_path = None if raw_arg.startswith("{") else Path(raw_arg)
        raw = state_path.read_text(encoding="utf-8") if state_path and state_path.exists() else raw_arg
        result = kb.diagnose(json.loads(raw))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
