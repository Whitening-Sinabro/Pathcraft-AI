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


# TEMPORARY stub — replaced by the CWS card projector in Task 3.
def load_cws_card(guide=None):
    return {}
