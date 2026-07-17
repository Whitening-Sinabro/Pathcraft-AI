# -*- coding: utf-8 -*-
"""Load and validate poe1_external_guide_source guides; project CWS to a card.

The validator is schema-shaped (works for any poe1_external_guide_source such as
the ZeeBoub brand guide), not CWS-specific. The projector is CWS-specific.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GUIDE_DIR = ROOT / "data" / "guide_sources"
CWS_GUIDE_FILE = "poe1_cws_chieftain_emiracles_v1.json"

_PATCH_LOCKED_KEY = re.compile(r"_3_2\d(_|$)")


class GuideSourceError(ValueError):
    """Raised when a poe1_external_guide_source guide fails validation."""


def _load_json(name: str) -> dict[str, Any]:
    return json.loads((GUIDE_DIR / name).read_text(encoding="utf-8-sig"))


def validate_external_guide_source(guide: dict[str, Any]) -> None:
    """Fail loud on the defects the redesign is meant to prevent.

    - patch-locked top-level keys (e.g. mirage_3_28_notes) — schema rot.
    - orphan pob_links (a PoB with no role) — the old 19-orphan defect.
    - dangling upgrade_node prereq / phase references — broken graph.
    """
    if guide.get("dataset_kind") != "poe1_external_guide_source":
        raise GuideSourceError(
            f"dataset_kind must be poe1_external_guide_source, got {guide.get('dataset_kind')!r}"
        )

    for key in guide:
        if _PATCH_LOCKED_KEY.search(key):
            raise GuideSourceError(f"patch-locked key name is banned: {key!r}")

    for pob in guide.get("pob_links", []):
        if not pob.get("role"):
            raise GuideSourceError(f"orphan pob_link (no role): {pob.get('url')!r}")

    phases = {phase["phase"] for phase in guide.get("phase_model", [])}
    node_ids = {node["node_id"] for node in guide.get("upgrade_nodes", [])}
    for node in guide.get("upgrade_nodes", []):
        if node.get("phase") and node["phase"] not in phases:
            raise GuideSourceError(
                f"upgrade_node {node['node_id']!r} references unknown phase {node['phase']!r}"
            )
        for req in node.get("prereq", []):
            if req not in node_ids:
                raise GuideSourceError(
                    f"upgrade_node {node['node_id']!r} has dangling prereq {req!r}"
                )
        for req in node.get("soft_recommend", []):
            if req not in node_ids:
                raise GuideSourceError(
                    f"upgrade_node {node['node_id']!r} has dangling soft_recommend {req!r}"
                )


_PHASE_STAGE_NAME = {
    "campaign_leveling": "레벨링 / Campaign",
    "cws_swap_gateway": "No Bloodnotch Swap",
    "bloodnotch_core": "Bloodnotch Initial Swap",
}


def _role_to_url(guide: dict[str, Any]) -> dict[str, str]:
    return {p["role"]: p["url"] for p in guide.get("pob_links", []) if p.get("role")}


def _source_cards(guide: dict[str, Any], ids: list[str]) -> list[dict[str, Any]]:
    by_id = {link["source_id"]: link for link in guide.get("links", []) if link.get("source_id")}
    cards = []
    for sid in ids:
        link = by_id.get(sid, {})
        cards.append({
            "source_id": sid,
            "label": link.get("label", sid),
            "url": link.get("url"),
            "family": link.get("family", "unknown"),
        })
    return cards


def _stage_from_phase(guide: dict[str, Any], phase: dict[str, Any], role_url: dict[str, str]) -> dict[str, Any]:
    roles = phase.get("pob_roles", [])
    pob_url = role_url.get(roles[0]) if roles else None
    return {
        "stage": _PHASE_STAGE_NAME[phase["phase"]],
        "goal": phase.get("goal", ""),
        "source_note": phase.get("exit") or phase.get("goal", ""),
        "pob_url": pob_url,
        "source_links": _source_cards(guide, phase.get("source_links", [])),
        "skill_setups": phase.get("skill_setups", []),
        "checks": phase.get("checks", []),
    }


def _stage_from_node(guide: dict[str, Any], node: dict[str, Any], role_url: dict[str, str]) -> dict[str, Any]:
    return {
        "stage": node["label"],
        "goal": node.get("gate", {}).get("note", ""),
        "source_note": node.get("gate", {}).get("note", ""),
        "pob_url": role_url.get(node.get("pob_role")) if node.get("pob_role") else None,
        "source_links": [],
        "skill_setups": [],
        "checks": [],
    }


def _knowledge_summaries(guide: dict[str, Any], tag: str) -> list[str]:
    return [c["summary"] for c in guide.get("knowledge_cards", []) if tag in c.get("tags", [])]


def _mirage_notes(guide: dict[str, Any]) -> list[str]:
    """Summaries of the mirage-league knowledge cards (card_id prefix ``mirage_``).

    Deliberately a card_id-prefix predicate, not a patch/tag/summary boolean mix:
    it is deterministic and immune to operator-precedence surprises.
    """
    return [
        c["summary"]
        for c in guide.get("knowledge_cards", [])
        if c.get("card_id", "").startswith("mirage_")
    ]


def load_cws_card(guide: dict[str, Any] | None = None) -> dict[str, Any]:
    """Project the CWS external guide into the research-dashboard watchlist card."""
    if guide is None:
        guide = _load_json(CWS_GUIDE_FILE)
    validate_external_guide_source(guide)

    role_url = _role_to_url(guide)
    phases = {p["phase"]: p for p in guide["phase_model"]}

    # Ordered practice_route: leveling -> gateway -> bloodnotch -> midgame nodes (by hint) -> aspirational split.
    route: list[dict[str, Any]] = [
        _stage_from_phase(guide, phases["campaign_leveling"], role_url),
        _stage_from_phase(guide, phases["cws_swap_gateway"], role_url),
        _stage_from_phase(guide, phases["bloodnotch_core"], role_url),
    ]
    midgame = sorted(
        (n for n in guide["upgrade_nodes"] if n["timing"] == "midgame_sequence"),
        key=lambda n: n["source_order_hint"],
    )
    route.extend(_stage_from_node(guide, n, role_url) for n in midgame)
    asp = phases["aspirational_endgame"]
    route.append({
        "stage": "Aspirational", "goal": asp.get("goal", ""), "source_note": asp.get("goal", ""),
        "pob_url": role_url.get("aspirational"), "source_links": _source_cards(guide, asp.get("source_links", [])),
        "skill_setups": [], "checks": [],
    })
    route.append({
        "stage": "Ultra Aspirational - Hybrid Mageblood/Imbue", "goal": asp.get("goal", ""),
        "source_note": asp.get("goal", ""), "pob_url": role_url.get("aspirational_hybrid"),
        "source_links": [], "skill_setups": asp.get("skill_setups", []), "checks": asp.get("checks", []),
    })

    anytime = [
        {"node_id": n["node_id"], "label": n["label"], "note": n.get("gate", {}).get("note", "")}
        for n in guide["upgrade_nodes"] if n["timing"] == "anytime"
    ]

    # Card-level sources = union of every source_id referenced by links, deduped in first-seen order.
    seen: dict[str, dict[str, Any]] = {}
    for link in guide.get("links", []):
        sid = link.get("source_id")
        if sid and sid not in seen:
            seen[sid] = {"source_id": sid, "label": link.get("label", sid),
                         "url": link.get("url"), "family": link.get("family", "unknown")}
    sources = list(seen.values())

    stage_pobs = [s["pob_url"] for s in route if s.get("pob_url")]
    alt_pobs = [p["url"] for p in guide["pob_links"] if p.get("role", "").endswith("_alt")]
    guardrails = guide.get("guardrails", [])
    red_flags = [g for g in guardrails if any(k in g for k in
                 ("Brine King", "Life Recoup", "Vaal Breach", "Hateful Accuser", "Maven", "beginner", "gateway"))]
    promotion_checks = [g for g in guardrails if g not in red_flags]

    return {
        "candidate_id": "3.29_cws_chieftain_emiracle_watch",
        "display_name": "Cast When Stunned Chieftain",
        "patch": "3.29",
        "main_skill": "Cast when Stunned",
        "class_name": "Marauder",
        "ascendancy": "Chieftain",
        "lane_id": "cws",
        "lane_label": "CWS",
        "player_label": "연습해도 됨",
        "default_recommendation": False,
        "reason": ("emiracles 3.28 Mirage CWS Chieftain 가이드 기반 저입력 고밀도 파밍 빌드입니다. "
                   "3.29에서는 일반 추천이 아니라 연습 후보로 둡니다."),
        "tags": ["3.29", "CWS", "Marauder", "Chieftain", "고밀도 파밍", "Simulacrum"],
        "sources": sources,
        "source_count": len(sources),
        "practice_route": route,
        "anytime_upgrades": anytime,
        "pob_urls": stage_pobs + alt_pobs,
        "alt_pob_urls": alt_pobs,
        "map_mods_to_avoid": guide.get("map_mods_to_avoid", []),
        "playstyle_summary": _knowledge_summaries(guide, "playstyle") + _knowledge_summaries(guide, "content_fit"),
        "mirage_notes": _mirage_notes(guide),
        "upgrade_notes": _knowledge_summaries(guide, "upgrade"),
        "red_flags": red_flags,
        "promotion_checks": promotion_checks,
        "next_actions": ["3.28 Mobalytics 단계별 PoB 전체 파싱", "3.29 패치 영향 재검증",
                         "Pohx RF 레벨링 루트 연결", "87+ No Bloodnotch 전환 조건 검증", "맵 모드 금지 목록 UI 반영"],
    }
