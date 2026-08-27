import base64
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zlib

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_magefist_campaign_pob import (  # noqa: E402
    add_transition_gem_preparation,
    decode_pob_code,
    parse_mastery_pairs,
    parse_tree_lua,
    validate_tree_specs,
)


def test_add_transition_gem_preparation_adds_six_swap_gems():
    skill_set = ET.fromstring('<SkillSet title="Act 6" />')
    preparation = {
        "slot": "Weapon 1 Swap",
        "label": "HoT prep",
        "gems": [
            {
                "name": f"Gem {index}",
                "gem_id": f"Metadata/Gem{index}",
                "skill_id": f"Skill{index}",
                "variant_id": f"Variant{index}",
                "target_level": 20,
            }
            for index in range(6)
        ],
    }

    add_transition_gem_preparation(skill_set, preparation)

    skill = skill_set.find("Skill")
    assert skill is not None
    assert skill.get("slot") == "Weapon 1 Swap"
    assert skill.get("label") == "HoT prep"
    assert [gem.get("nameSpec") for gem in skill.findall("Gem")] == [
        f"Gem {index}" for index in range(6)
    ]


def test_decode_pob_code_round_trips_xml():
    xml = b"<PathOfBuilding><Build className='Ranger'/></PathOfBuilding>"
    code = base64.urlsafe_b64encode(zlib.compress(xml)).decode().rstrip("=")

    assert decode_pob_code(code) == xml


def test_parse_mastery_pairs_handles_empty_and_multiple_values():
    assert parse_mastery_pairs(None) == []
    assert parse_mastery_pairs("") == []
    assert parse_mastery_pairs("{41016,29214},{44316,34242}") == [
        (41016, 29214),
        (44316, 34242),
    ]


def test_tree_validation_checks_nodes_and_mastery_effects(tmp_path):
    tree_path = tmp_path / "tree.lua"
    tree_path.write_text(
        """return {
    ["nodes"]= {
        [100]= {
            ["skill"]= 100,
            ["masteryEffects"]= {
                {
                    ["effect"]= 200,
                },
            },
        },
        [101]= {
            ["skill"]= 101,
        },
    },
    ["jewelSlots"]= {
    },
}
""",
        encoding="utf-8",
    )
    available = parse_tree_lua(tree_path)
    spec = ET.fromstring(
        '<Spec title="Act 1" nodes="100,101" masteryEffects="{100,200}" />'
    )

    assert validate_tree_specs([spec], available) == [
        {"title": "Act 1", "nodes": 2, "masteries": 1}
    ]

    invalid = ET.fromstring(
        '<Spec title="Bad Act" nodes="100,999" masteryEffects="{100,201}" />'
    )
    with pytest.raises(ValueError, match=r"missing nodes=\[999\]"):
        validate_tree_specs([invalid], available)
