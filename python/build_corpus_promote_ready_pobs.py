# -*- coding: utf-8 -*-
"""Promote verified direct PoB links into parsed BuildInstance artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from pob_parser import decode_pob_code, get_pob_code_from_url, parse_pob_xml


ROOT = Path(__file__).resolve().parent.parent
PROBE_PATH = ROOT / "data" / "build_corpus_pob_link_probe.latest.json"
OUT_PATH = ROOT / "data" / "build_corpus_promoted_instances.latest.json"
BUILDS_DIR = ROOT / "data" / "builds"

GENERIC_SKILL_TERMS = {
    "and",
    "the",
    "with",
    "support",
    "awakened",
    "greater",
    "lesser",
    "multiple",
    "projectiles",
    "specialist",
    "shell",
    "mapper",
    "bossing",
    "budget",
    "final",
    "mixed",
}


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return slug[:80] or "pob"


def pob_url_slug(url: str) -> str:
    if "pobb.in/" in url:
        return safe_slug(url.rsplit("/", 1)[-1])
    if "pastebin.com/raw/" in url:
        return safe_slug(url.rsplit("/", 1)[-1])
    if "poe.ninja/pob/" in url:
        return safe_slug(url.rsplit("/", 1)[-1])
    return safe_slug(url)


def skill_terms(skill_name: str) -> list[str]:
    terms = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9]+", skill_name.lower()):
        if len(token) < 4 or token in GENERIC_SKILL_TERMS:
            continue
        if token not in terms:
            terms.append(token)
    return terms


def _walk_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        rows: list[str] = []
        for key, nested in value.items():
            rows.append(str(key))
            rows.extend(_walk_values(nested))
        return rows
    if isinstance(value, list):
        rows = []
        for nested in value:
            rows.extend(_walk_values(nested))
        return rows
    return []


def build_skill_text(build_data: dict[str, Any]) -> str:
    stages = build_data.get("progression_stages") or []
    if not stages:
        return ""
    stage = stages[0]
    parts = []
    parts.extend(_walk_values(stage.get("gem_setups") or {}))
    parts.extend(_walk_values(stage.get("alternate_gem_sets") or {}))
    parts.append(str(build_data.get("build_notes") or ""))
    return " ".join(parts).lower()


def summarize_parsed_build(build_data: dict[str, Any]) -> dict[str, Any]:
    meta = build_data.get("meta") or {}
    stats = build_data.get("stats") or {}
    raw = build_data.get("pob_raw") or {}
    stage = (build_data.get("progression_stages") or [{}])[0]
    alternate_sets = stage.get("alternate_gem_sets") or {}
    active_setups = stage.get("gem_setups") or {}
    build_instance = build_data.get("build_instance") or {}
    readiness = build_instance.get("readiness") or {}
    return {
        "identity": {
            "build_name": meta.get("build_name"),
            "class": meta.get("class"),
            "ascendancy": meta.get("ascendancy"),
            "version": meta.get("version"),
            "pob_link": meta.get("pob_link"),
        },
        "stats": {
            "dps": stats.get("dps"),
            "life": stats.get("life"),
            "energy_shield": stats.get("energy_shield"),
            "ehp": stats.get("ehp"),
            "resistances": stats.get("resistances"),
        },
        "pob_raw_summary": raw.get("summary") or {},
        "active_gem_groups": list(active_setups.keys()),
        "alternate_gem_sets": list(alternate_sets.keys()),
        "readiness": readiness,
    }


def validate_candidate_against_build(candidate: dict[str, Any], build_data: dict[str, Any]) -> dict[str, Any]:
    meta = build_data.get("meta") or {}
    expected_class = str(candidate.get("class_name") or "").casefold()
    expected_asc = str(candidate.get("ascendancy") or "").casefold()
    actual_class = str(meta.get("class") or "").casefold()
    actual_asc = str(meta.get("ascendancy") or "").casefold()
    skill_text = build_skill_text(build_data)
    terms = skill_terms(str(candidate.get("main_skill") or ""))
    matched_terms = [term for term in terms if term in skill_text]
    skill_match = bool(terms) and len(matched_terms) >= max(1, min(2, len(terms)))

    class_match = expected_class == actual_class
    ascendancy_match = expected_asc == actual_asc
    accepted = class_match and ascendancy_match and skill_match
    blockers = []
    if not class_match:
        blockers.append("class_mismatch")
    if not ascendancy_match:
        blockers.append("ascendancy_mismatch")
    if not skill_match:
        blockers.append("main_skill_not_found_in_pob")

    return {
        "accepted": accepted,
        "class_match": class_match,
        "ascendancy_match": ascendancy_match,
        "skill_match": skill_match,
        "matched_skill_terms": matched_terms,
        "blockers": blockers,
        "actual_identity": {
            "class": meta.get("class"),
            "ascendancy": meta.get("ascendancy"),
            "build_name": meta.get("build_name"),
        },
    }


def parse_pob_url(url: str) -> dict[str, Any] | None:
    code = get_pob_code_from_url(url)
    if not code:
        return None
    xml = decode_pob_code(code)
    if not xml:
        return None
    return parse_pob_xml(xml, url)


def promote_ready_pobs(*, write_artifacts: bool = True, candidate_limit: int | None = None) -> dict[str, Any]:
    probe = _load_json(PROBE_PATH)
    work_orders = [
        order
        for order in probe.get("work_orders", [])
        if order.get("direct_pob_candidates")
    ]
    if candidate_limit is not None:
        work_orders = work_orders[:candidate_limit]

    parsed_cache: dict[str, dict[str, Any] | None] = {}
    promoted = []
    rejected = []
    parse_errors = []

    if write_artifacts:
        BUILDS_DIR.mkdir(parents=True, exist_ok=True)

    for order in work_orders:
        for link in order.get("direct_pob_candidates", [])[:3]:
            url = link["url"]
            artifact_base = f"{order['candidate_id']}.{pob_url_slug(url)}"
            build_path = BUILDS_DIR / f"{artifact_base}.build.json"
            instance_path = BUILDS_DIR / f"{artifact_base}.build_instance.json"
            if url not in parsed_cache:
                if build_path.exists():
                    parsed_cache[url] = _load_json(build_path)
                else:
                    try:
                        parsed_cache[url] = parse_pob_url(url)
                    except Exception as exc:
                        parsed_cache[url] = None
                        parse_errors.append(
                            {
                                "candidate_id": order["candidate_id"],
                                "url": url,
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )
            build_data = parsed_cache[url]
            if not build_data:
                parse_errors.append(
                    {
                        "candidate_id": order["candidate_id"],
                        "url": url,
                        "error": "parse_returned_none",
                    }
                )
                continue

            validation = validate_candidate_against_build(order, build_data)
            summary = summarize_parsed_build(build_data)
            if not validation["accepted"]:
                rejected.append(
                    {
                        "candidate_id": order["candidate_id"],
                        "display_name": order["display_name"],
                        "url": url,
                        "validation": validation,
                        "parsed_summary": summary,
                    }
                )
                continue

            if write_artifacts:
                build_path.write_text(json.dumps(build_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                instance_path.write_text(
                    json.dumps(build_data.get("build_instance") or {}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

            promoted.append(
                {
                    "candidate_id": order["candidate_id"],
                    "display_name": order["display_name"],
                    "url": url,
                    "validation": validation,
                    "parsed_summary": summary,
                    "artifact_paths": {
                        "build_data": str(build_path.relative_to(ROOT)).replace("\\", "/"),
                        "build_instance": str(instance_path.relative_to(ROOT)).replace("\\", "/"),
                    },
                }
            )

    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_build_corpus_promoted_instances",
        "updated_at": "2026-07-17",
        "summary": {
            "work_order_count": len(work_orders),
            "unique_pob_url_count": len(parsed_cache),
            "promoted_count": len(promoted),
            "rejected_count": len(rejected),
            "parse_error_count": len(parse_errors),
        },
        "promoted": promoted,
        "rejected": rejected,
        "parse_errors": parse_errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help=f"Write {OUT_PATH.relative_to(ROOT)}")
    parser.add_argument("--no-artifacts", action="store_true", help="Do not write parsed build artifacts.")
    parser.add_argument("--candidate-limit", type=int, default=None)
    args = parser.parse_args()

    result = promote_ready_pobs(
        write_artifacts=not args.no_artifacts,
        candidate_limit=args.candidate_limit,
    )
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.write:
        OUT_PATH.write_text(text + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
