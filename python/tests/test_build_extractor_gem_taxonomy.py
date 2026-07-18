# -*- coding: utf-8 -*-
"""build_extractor integration with generated gem taxonomy."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_extractor import detect_build_type, extract_build_gems  # noqa: E402


def _build_with_links(links: str) -> dict:
    first = links.split(" - ")[0]
    return {
        "progression_stages": [{
            "gem_setups": {
                first: {"links": links}
            }
        }]
    }


def test_extract_build_gems_keeps_real_active_when_support_sibling_exists():
    build = _build_with_links("Barrage - Added Lightning Damage - Barrage Support")

    skills, supports = extract_build_gems(build)

    assert "Barrage" in skills
    assert "Barrage Support" not in skills
    assert "Added Lightning Damage Support" in supports
    assert "Barrage Support" in supports


def test_extract_build_gems_handles_transfigured_active_and_triggered_non_socketable():
    blight = _build_with_links("Blight of Contagion - Void Manipulation Support")
    skills, supports = extract_build_gems(blight)

    assert "Blight of Contagion" in skills
    assert "Void Manipulation Support" in supports
    assert detect_build_type(blight) == "dot"

    molten = _build_with_links("Molten Burst - Greater Multiple Projectiles Support")
    skills, supports = extract_build_gems(molten)

    assert "Molten Burst" not in skills
    assert "Greater Multiple Projectiles Support" in supports


def test_detect_build_type_uses_taxonomy_damage_flags():
    assert detect_build_type(_build_with_links("Static Strike - Faster Attacks Support")) == "attack"
    assert detect_build_type(_build_with_links("Raise Zombie - Minion Damage Support")) == "minion"
    assert detect_build_type(_build_with_links("Herald of Thunder - Lightning Penetration Support")) == "spell"
