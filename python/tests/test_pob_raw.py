# -*- coding: utf-8 -*-
"""PoBRaw extraction tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pob_parser import parse_pob_xml  # noqa: E402
from pob_raw import extract_pob_raw  # noqa: E402


def _raw_fixture_xml() -> str:
    return """<PathOfBuilding>
  <Build level="92" className="Scion" ascendClassName="Reliquarian" targetVersion="3.29" bandit="Kill All" />
  <Skills activeSkillSet="1">
    <SkillSet id="1" title="Final">
      <Skill enabled="true" label="Autobomber" mainActiveSkill="1">
        <Gem nameSpec="Herald of Thunder" level="21" quality="20" skillId="HeraldOfThunder" enabled="true" />
        <Gem nameSpec="Lightning Penetration Support" level="20" quality="20" />
      </Skill>
    </SkillSet>
    <SkillSet id="2" title="Leveling">
      <Skill enabled="true" label="Campaign">
        <Gem nameSpec="Storm Brand" level="12" quality="0" />
      </Skill>
    </SkillSet>
  </Skills>
  <Items activeItemSet="1">
    <Item id="1"><![CDATA[Rarity: UNIQUE
Storm Secret
Topaz Ring
Unique ID: abc
Implicits: 1
+25% to Lightning Resistance
Herald of Thunder also creates a storm when you Shock an Enemy
Take 250 Lightning Damage when Herald of Thunder Hits an Enemy
]]></Item>
    <Item id="2"><![CDATA[Rarity: RARE
Glyph Shell
Vaal Regalia
Item Level: 86
+120 to maximum Life
+45% to Fire Resistance
]]></Item>
    <ItemSet id="1" title="Final Gear">
      <Slot name="Ring 1" itemId="1" />
      <Slot name="Body Armour" itemId="2" />
    </ItemSet>
  </Items>
  <Tree activeSpec="1">
    <Spec id="1" title="Final Tree" treeVersion="3_29">
      <URL>https://www.pathofexile.com/passive-skill-tree/AAAA</URL>
      <Sockets>
        <Socket nodeId="12345" itemId="7" />
      </Sockets>
    </Spec>
  </Tree>
  <Config>
    <Input name="enemyIsBoss" value="Guardian" />
    <Input name="usePowerCharges" value="true" />
  </Config>
  <PlayerStat stat="CombinedDPS" value="1200000" />
  <PlayerStat stat="Life" value="4300" />
</PathOfBuilding>"""


def test_extract_pob_raw_preserves_skills_items_tree_config_and_stats():
    raw = extract_pob_raw(_raw_fixture_xml(), "file:///fixture.xml")

    assert raw["build"]["attributes"]["className"] == "Scion"
    assert raw["summary"]["skill_set_count"] == 2
    assert raw["skills"]["skill_sets"][0]["skills"][0]["gems"][0]["name_spec"] == "Herald of Thunder"
    assert raw["skills"]["skill_sets"][0]["skills"][0]["gems"][0]["attributes"]["level"] == "21"
    assert raw["items"]["items"]["1"]["raw_text"].startswith("Rarity: UNIQUE")
    assert raw["items"]["items"]["1"]["parsed_text"]["name"] == "Storm Secret"
    assert raw["items"]["item_sets"][0]["slots"][1]["name"] == "Body Armour"
    assert raw["tree"]["specs"][0]["tree_version"] == "3_29"
    assert raw["tree"]["specs"][0]["sockets"][0]["node_id"] == "12345"
    assert raw["config"]["present"] is True
    assert raw["config"]["inputs"]["enemyIsBoss"] == "Guardian"
    assert raw["player_stats"]["values"]["CombinedDPS"] == 1200000.0


def test_parse_pob_xml_includes_pob_raw_layer():
    build_data = parse_pob_xml(_raw_fixture_xml(), "file:///fixture.xml")

    assert build_data["pob_raw"]["summary"]["item_count"] == 2
    assert build_data["pob_raw"]["config"]["inputs"]["usePowerCharges"] == "true"
    assert build_data["build_instance"]["source"]["raw_available"] is True
    ring = next(item for item in build_data["build_instance"]["item_state"]["slots"] if item["slot"] == "Ring 1")
    assert ring["mod_source"] == "pob_raw_item_text"
    assert ring["mod_summary"]["numeric_totals"]["lightning_resistance"] == 25
    assert ring["mod_state"][1]["likely_affix_generation"] == "unique_modifier"
