# -*- coding: utf-8 -*-
"""Versioned CWS knowledge ingestion, hybrid retrieval, and diagnosis.

The structured JSON remains the source of truth. SQLite is a disposable local
index: FTS5 provides lexical recall and an optional caller-supplied embedder
adds semantic recall without making a model/dependency mandatory.
"""

from __future__ import annotations

import json
import argparse
import hashlib
import math
import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK = ROOT / "data" / "guide_sources" / "poe1_cws_chieftain_emiracles_3_29_v2.json"

Embedder = Callable[[list[str]], Sequence[Sequence[float]]]

QUERY_ALIASES = {
    "끔살": ("death", "one shot", "survivability", "즉사"),
    "즉사": ("death", "one shot", "survivability", "끔살"),
    "안죽": ("survivability", "recovery", "death", "생존"),
    "왜죽": ("death", "diagnosis", "recovery"),
    "방송": ("stream", "comparison", "twitch", "poe.ninja"),
    "안터": ("trigger", "stun", "cast when stunned"),
    "기절": ("stun", "trigger", "bloodnotch"),
    "울티": ("ultimatum",),
    "시뮬": ("simulacrum",),
    "보스": ("bossing", "single target", "sri"),
}


class CWSKnowledgeError(ValueError):
    """Raised when the canonical pack or a query contract is invalid."""


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    record_type: str
    title: str
    text: str
    score: float
    metadata: dict[str, Any]
    source_refs: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "record_type": self.record_type,
            "title": self.title,
            "text": self.text,
            "score": round(self.score, 8),
            "metadata": self.metadata,
            "source_refs": self.source_refs,
        }


def load_pack(path: Path | str = DEFAULT_PACK) -> dict[str, Any]:
    pack = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    validate_pack(pack)
    return pack


def validate_pack(pack: dict[str, Any]) -> None:
    if pack.get("dataset_kind") != "pathcraft_cws_knowledge_pack":
        raise CWSKnowledgeError("unexpected dataset_kind")
    if pack.get("patch") != "3.29":
        raise CWSKnowledgeError("CWS knowledge pack must be patch-locked to 3.29")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(pack.get("knowledge_version", ""))):
        raise CWSKnowledgeError("knowledge_version must be semantic versioning")

    sources = {row.get("source_id") for row in pack.get("sources", [])}
    claims = {row.get("claim_id") for row in pack.get("claims", [])}
    if None in sources or len(sources) != len(pack.get("sources", [])):
        raise CWSKnowledgeError("source_id values must be present and unique")
    if None in claims or len(claims) != len(pack.get("claims", [])):
        raise CWSKnowledgeError("claim_id values must be present and unique")

    for claim in pack.get("claims", []):
        if not claim.get("text_ko") or not claim.get("source_refs"):
            raise CWSKnowledgeError(f"claim lacks text/source_refs: {claim.get('claim_id')}")
        for ref in claim["source_refs"]:
            if ref.get("source_id") not in sources:
                raise CWSKnowledgeError(f"dangling source ref: {ref}")
    for rule in pack.get("diagnostic_rules", []):
        dangling = set(rule.get("claim_refs", [])) - claims
        if dangling:
            raise CWSKnowledgeError(f"rule {rule.get('rule_id')} has dangling claims: {sorted(dangling)}")


def normalize_query(query: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(query or ""))
    normalized = re.sub(r"\s+", " ", normalized.strip().casefold())
    expanded = [normalized]
    compact = normalized.replace(" ", "")
    for needle, aliases in QUERY_ALIASES.items():
        if needle in normalized or needle in compact:
            expanded.extend(aliases)
    return " ".join(dict.fromkeys(part for part in expanded if part))


def hashing_embedder(texts: list[str], dimensions: int = 384) -> list[list[float]]:
    """Dependency-free multilingual character n-gram vectors.

    This is a reproducible local baseline, not a claim of deep semantics. The
    same index accepts a stronger multilingual embedder through ``Embedder``.
    """
    vectors: list[list[float]] = []
    for text in texts:
        normalized = f"  {normalize_query(text)}  "
        vector = [0.0] * dimensions
        for size in (2, 3, 4, 5):
            for start in range(max(0, len(normalized) - size + 1)):
                gram = normalized[start:start + size].encode("utf-8")
                digest = hashlib.blake2b(gram, digest_size=8).digest()
                bucket = int.from_bytes(digest[:4], "little") % dimensions
                sign = 1.0 if digest[4] & 1 else -1.0
                vector[bucket] += sign
        vectors.append(_unit(vector))
    return vectors


def _documents(pack: dict[str, Any]) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for claim in pack.get("claims", []):
        docs.append({
            "doc_id": f"claim:{claim['claim_id']}",
            "record_type": "claim",
            "title": claim["claim_id"],
            "text": " ".join((claim.get("text_ko", ""), claim.get("text_en", ""), " ".join(claim.get("tags", [])))),
            "metadata": {"patch": pack["patch"], "topic": claim.get("topic"), "tags": claim.get("tags", []), "confidence": claim.get("confidence")},
            "source_refs": claim.get("source_refs", []),
        })
    claim_by_id = {row["claim_id"]: row for row in pack.get("claims", [])}
    for rule in pack.get("diagnostic_rules", []):
        refs = []
        for claim_id in rule.get("claim_refs", []):
            refs.extend(claim_by_id[claim_id].get("source_refs", []))
        docs.append({
            "doc_id": f"rule:{rule['rule_id']}",
            "record_type": "diagnostic_rule",
            "title": rule["rule_id"],
            "text": " ".join(rule.get("symptoms", []) + [rule.get("explanation_ko", "")] + rule.get("actions_ko", [])),
            "metadata": {"patch": pack["patch"], "priority": rule.get("priority", 0), "claim_refs": rule.get("claim_refs", [])},
            "source_refs": _dedupe_refs(refs),
        })
    for pob in pack.get("pob_variants", []):
        docs.append({
            "doc_id": f"pob:{pob['variant_id']}", "record_type": "pob_variant", "title": pob["variant_id"],
            "text": json.dumps(pob, ensure_ascii=False),
            "metadata": {"patch": pack["patch"], "stage": pob.get("stage"), "content": pob.get("content", []), "not_for": pob.get("not_for", [])},
            "source_refs": ([{"source_id": pob["source_id"], "locator": "PoB variant"}] if pob.get("source_id") else []),
        })
    for vod in pack.get("vod_catalog", []):
        docs.append({
            "doc_id": f"vod:{vod['video_id']}", "record_type": "vod", "title": vod.get("title") or vod["video_id"],
            "text": json.dumps(vod, ensure_ascii=False),
            "metadata": {"patch": pack["patch"], "date": vod.get("date"), "phase": vod.get("phase"), "audit_status": vod.get("audit_status")},
            "source_refs": [{"source_id": "twitch_emiracles", "locator": vod["url"]}],
        })
    return docs


def _dedupe_refs(refs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result = []
    for ref in refs:
        key = (str(ref.get("source_id", "")), str(ref.get("locator", "")))
        if key not in seen:
            seen.add(key)
            result.append(ref)
    return result


def _unit(vector: Sequence[float]) -> list[float]:
    values = [float(value) for value in vector]
    norm = math.sqrt(sum(value * value for value in values))
    return [value / norm for value in values] if norm else values


class CWSKnowledgeBase:
    def __init__(self, pack_path: Path | str = DEFAULT_PACK):
        self.pack_path = Path(pack_path)
        self.pack = load_pack(self.pack_path)
        self.docs = _documents(self.pack)

    def build_index(self, db_path: Path | str, embedder: Embedder | None = None) -> dict[str, Any]:
        target = Path(db_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(target) as conn:
            conn.executescript("""
                DROP TABLE IF EXISTS documents;
                DROP TABLE IF EXISTS document_fts;
                DROP TABLE IF EXISTS vectors;
                CREATE TABLE documents (
                    doc_id TEXT PRIMARY KEY, record_type TEXT NOT NULL, title TEXT NOT NULL,
                    text TEXT NOT NULL, metadata_json TEXT NOT NULL, source_refs_json TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE document_fts USING fts5(
                    doc_id UNINDEXED, title, text, tokenize='unicode61 remove_diacritics 2'
                );
                CREATE TABLE vectors (doc_id TEXT PRIMARY KEY, vector_json TEXT NOT NULL);
            """)
            for doc in self.docs:
                conn.execute("INSERT INTO documents VALUES (?,?,?,?,?,?)", (
                    doc["doc_id"], doc["record_type"], doc["title"], doc["text"],
                    json.dumps(doc["metadata"], ensure_ascii=False), json.dumps(doc["source_refs"], ensure_ascii=False),
                ))
                conn.execute("INSERT INTO document_fts(doc_id,title,text) VALUES (?,?,?)", (doc["doc_id"], doc["title"], doc["text"]))
            vector_count = 0
            if embedder:
                vectors = list(embedder([doc["text"] for doc in self.docs]))
                if len(vectors) != len(self.docs):
                    raise CWSKnowledgeError("embedder returned a different number of vectors")
                for doc, vector in zip(self.docs, vectors):
                    conn.execute("INSERT INTO vectors VALUES (?,?)", (doc["doc_id"], json.dumps(_unit(vector))))
                    vector_count += 1
        return {"documents": len(self.docs), "vectors": vector_count, "path": str(target)}

    def search(
        self, query: str, *, db_path: Path | str | None = None, embedder: Embedder | None = None,
        filters: dict[str, Any] | None = None, limit: int = 8,
    ) -> list[dict[str, Any]]:
        filters = filters or {}
        if db_path is None:
            return [hit.as_dict() for hit in self._memory_search(query, filters, limit)]
        return [hit.as_dict() for hit in self._sqlite_search(query, Path(db_path), embedder, filters, limit)]

    def _memory_search(self, query: str, filters: dict[str, Any], limit: int) -> list[SearchHit]:
        terms = set(re.findall(r"[\w.]+", normalize_query(query), flags=re.UNICODE))
        ranked = []
        for doc in self.docs:
            if not _matches_filters(doc, filters):
                continue
            blob = f"{doc['title']} {doc['text']}".casefold()
            overlap = sum(1 for term in terms if term in blob)
            if overlap:
                ranked.append((overlap / max(1, len(terms)), doc))
        ranked.sort(key=lambda row: (-row[0], -int(row[1]["metadata"].get("priority", 0)), row[1]["doc_id"]))
        return [_hit(doc, score) for score, doc in ranked[:limit]]

    def _sqlite_search(self, query: str, db_path: Path, embedder: Embedder | None, filters: dict[str, Any], limit: int) -> list[SearchHit]:
        normalized = normalize_query(query)
        tokens = list(dict.fromkeys(re.findall(r"[\w.]+", normalized, flags=re.UNICODE)))
        lexical_ids: list[str] = []
        vector_ids: list[str] = []
        with sqlite3.connect(db_path) as conn:
            if tokens:
                fts_query = " OR ".join(f'"{token.replace(chr(34), "")}"' for token in tokens[:32])
                lexical_ids = [row[0] for row in conn.execute(
                    "SELECT doc_id FROM document_fts WHERE document_fts MATCH ? ORDER BY bm25(document_fts) LIMIT ?",
                    (fts_query, max(limit * 6, 30)),
                )]
            if embedder:
                query_vectors = list(embedder([normalized]))
                if query_vectors:
                    qv = _unit(query_vectors[0])
                    scored = []
                    for doc_id, raw in conn.execute("SELECT doc_id, vector_json FROM vectors"):
                        vector = json.loads(raw)
                        if len(vector) == len(qv):
                            scored.append((sum(a * b for a, b in zip(qv, vector)), doc_id))
                    vector_ids = [doc_id for _, doc_id in sorted(scored, reverse=True)[:max(limit * 6, 30)]]

            fused: dict[str, float] = {}
            for rank, doc_id in enumerate(lexical_ids, 1):
                fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (60 + rank)
            for rank, doc_id in enumerate(vector_ids, 1):
                fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (60 + rank)
            if not fused:
                return []
            by_id = {doc["doc_id"]: doc for doc in self.docs}
            ranked = [(score, by_id[doc_id]) for doc_id, score in fused.items() if doc_id in by_id and _matches_filters(by_id[doc_id], filters)]
            ranked.sort(key=lambda row: (-row[0], row[1]["doc_id"]))
            return [_hit(doc, score) for score, doc in ranked[:limit]]

    def diagnose(self, state: dict[str, Any], limit: int = 8) -> dict[str, Any]:
        matches = []
        for rule in self.pack.get("diagnostic_rules", []):
            conditions = rule.get("when", [])
            if conditions and all(_condition_matches(state, condition) for condition in conditions):
                refs = []
                for claim_id in rule.get("claim_refs", []):
                    claim = next(row for row in self.pack["claims"] if row["claim_id"] == claim_id)
                    refs.extend(claim.get("source_refs", []))
                matches.append({
                    "rule_id": rule["rule_id"], "priority": rule.get("priority", 0),
                    "explanation_ko": rule.get("explanation_ko"), "actions_ko": rule.get("actions_ko", []),
                    "claim_refs": rule.get("claim_refs", []), "source_refs": _dedupe_refs(refs),
                })
        matches.sort(key=lambda row: (-row["priority"], row["rule_id"]))
        missing = [key for key in ("pob_url", "content", "map_mods", "death_pattern", "damage_pattern") if key not in state]
        return {
            "build_id": self.pack["build_id"], "patch": self.pack["patch"],
            "diagnoses": matches[:limit], "missing_observations": missing,
            "disclaimer": "규칙 기반 후보 원인이다. PoE는 사망 로그를 제공하지 않으므로 장면과 PoB로 반증/확인해야 한다.",
        }


def _hit(doc: dict[str, Any], score: float) -> SearchHit:
    return SearchHit(doc["doc_id"], doc["record_type"], doc["title"], doc["text"], score, doc["metadata"], doc["source_refs"])


def _matches_filters(doc: dict[str, Any], filters: dict[str, Any]) -> bool:
    if filters.get("record_type") and doc["record_type"] != filters["record_type"]:
        return False
    meta = doc["metadata"]
    for key, expected in filters.items():
        if key == "record_type":
            continue
        actual = meta.get(key)
        if isinstance(actual, list):
            wanted = expected if isinstance(expected, list) else [expected]
            if not set(wanted) & set(actual):
                return False
        elif actual != expected:
            return False
    return True


def _condition_matches(state: dict[str, Any], condition: dict[str, Any]) -> bool:
    field, op, expected = condition.get("field"), condition.get("op"), condition.get("value")
    actual = state.get(field)
    if op == "missing":
        return field not in state or actual in (None, "", [])
    if op == "eq":
        return actual == expected
    if op == "gt":
        return actual is not None and float(actual) > float(expected)
    if op == "lt":
        return actual is not None and float(actual) < float(expected)
    if op == "in":
        return actual in (expected or [])
    if op == "contains":
        return str(expected).casefold() in str(actual or "").casefold()
    if op == "contains_any":
        blob = " ".join(actual) if isinstance(actual, list) else str(actual or "")
        return any(str(value).casefold() in blob.casefold() for value in (expected or []))
    raise CWSKnowledgeError(f"unsupported diagnostic operator: {op}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and query the Emiracle CWS 3.29 knowledge index.")
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
    diagnose.add_argument("--state", required=True, help="JSON object or path to a JSON file")
    args = parser.parse_args(argv)

    kb = CWSKnowledgeBase(args.pack)
    if args.command == "index":
        print(json.dumps(kb.build_index(args.db, None if args.no_vectors else hashing_embedder), ensure_ascii=False, indent=2))
    elif args.command == "search":
        embedder = hashing_embedder if args.db else None
        print(json.dumps(kb.search(args.query, db_path=args.db, embedder=embedder, limit=args.limit), ensure_ascii=False, indent=2))
    else:
        state_arg = args.state.strip()
        state_path = None if state_arg.startswith("{") else Path(state_arg)
        raw = state_path.read_text(encoding="utf-8") if state_path and state_path.exists() else state_arg
        print(json.dumps(kb.diagnose(json.loads(raw)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
