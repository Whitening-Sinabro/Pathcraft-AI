import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_magefist_min_transition_pob import (  # noqa: E402
    make_budget_skill_set,
    make_lightning_arrow_group,
    serialize_config_value,
)


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = (
    ROOT
    / "config"
    / "build_setups"
    / "magefist_chaos_hot_pathfinder_3_29.spec.json"
)


def test_lightning_arrow_starter_is_only_a_cheap_two_link():
    group = make_lightning_arrow_group()

    assert [gem.get("nameSpec") for gem in group.findall("Gem")] == [
        "Lightning Arrow",
        "Overcharge",
    ]
    assert group.get("slot") == "Weapon 1"


def test_config_serialization_preserves_pantheon_case():
    assert serialize_config_value(
        {"name": "pantheonMajorGod", "type": "string", "value": "Lunaris"}
    ) == "Lunaris"
    assert serialize_config_value(
        {"name": "conditionUsingFlask", "type": "boolean", "value": True}
    ) == "true"


def test_budget_skill_set_removes_explosion_and_expensive_gem_levels():
    source = ET.fromstring(
        """
        <Skills>
          <SkillSet id="1">
            <Skill source="Explode"><Gem nameSpec="" /></Skill>
            <Skill slot="Weapon 2">
              <Gem nameSpec="Flame Dash" level="20" quality="20" />
              <Gem nameSpec="Convocation" level="20" quality="20" />
              <Gem nameSpec="Automation" level="20" quality="20" />
            </Skill>
            <Skill slot="Gloves"><Gem nameSpec="Despair" level="20" quality="20" /></Skill>
            <Skill slot="Boots">
              <Gem nameSpec="Phase Run" level="20" quality="20" />
              <Gem nameSpec="Withering Step" level="20" quality="20" />
            </Skill>
            <Skill slot="Helmet"><Gem nameSpec="Lightning Conduit" level="20" quality="20" /></Skill>
            <Skill slot="Weapon 1">
              <Gem nameSpec="Cast when Damage Taken" level="20" quality="20" />
            </Skill>
            <Skill slot="Body Armour">
              <Gem nameSpec="Herald of Thunder" level="20" quality="20" />
              <Gem nameSpec="Empower" level="4" quality="20" />
            </Skill>
          </SkillSet>
        </Skills>
        """
    )

    result = make_budget_skill_set(source)
    groups = result.findall("Skill")

    assert len(groups) == 7
    assert [gem.get("nameSpec") for gem in groups[0].findall("Gem")] == [
        "Lightning Arrow",
        "Overcharge",
    ]
    assert [gem.get("nameSpec") for gem in groups[1].findall("Gem")] == ["Flame Dash"]
    assert groups[1].get("slot") == "Weapon 1"
    assert "Phase Run" not in [gem.get("nameSpec") for gem in groups[3].findall("Gem")]
    empower = next(gem for gem in groups[6].findall("Gem") if gem.get("nameSpec") == "Empower")
    assert empower.get("level") == "3"
    assert all(gem.get("quality") == "0" for gem in result.findall(".//Gem"))


def test_canonical_minimum_setup_has_only_the_mechanical_transition_items():
    definition = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    setup = definition["minimum_transition"]
    item_text = "\n".join(
        line for item in setup["items"] for line in item["text"]
    )

    assert setup["level"] == 80
    assert setup["tree"]["official_pruned_node_count"] == 109
    assert setup["tree"]["ascendancy_points"] == 6
    assert "Sockets: G-W-W-W-W-W" in item_text
    assert all(name in item_text for name in setup["required_items"])
    assert all(name not in item_text for name in setup["excluded_expensive_items"])
