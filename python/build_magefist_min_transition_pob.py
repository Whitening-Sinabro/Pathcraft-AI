"""Build and install the level-80 Voltaxic minimum-transition PoB.

MAGEFIST did not publish the brief level-80 Voltaxic configuration shown in
the video.  This generator uses the published Part 1 PoB for the current gem
mechanics, an independently published non-cluster Voltaxic tree skeleton, and
the explicit budget gear templates in the canonical Pathcraft specification.
Every passive node and mastery is checked against the installed 3.29 tree data
before the generated XML is installed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from build_magefist_campaign_pob import (
    fetch_pob,
    parse_tree_lua,
    referenced_item_ids,
    validate_tree_specs,
    write_atomic,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = (
    ROOT
    / "config"
    / "build_setups"
    / "magefist_chaos_hot_pathfinder_3_29.spec.json"
)


def make_gem(**attributes: str) -> ET.Element:
    """Create a PoB gem element with stable shared defaults."""

    defaults = {
        "enableGlobal1": "true",
        "enableGlobal2": "true",
        "quality": "0",
        "enabled": "true",
        "count": "1",
    }
    defaults.update(attributes)
    return ET.Element("Gem", defaults)


def make_lightning_arrow_group() -> ET.Element:
    """Create the cheap two-link used to start HoT and refresh shock."""

    skill = ET.Element(
        "Skill",
        {
            "mainActiveSkillCalcs": "1",
            "mainActiveSkill": "1",
            "label": "Manual shock / Herald starter",
            "enabled": "true",
            "slot": "Weapon 1",
            "includeInFullDPS": "false",
        },
    )
    skill.append(
        make_gem(
            level="20",
            gemId="Metadata/Items/Gems/SkillGemLightningArrow",
            variantId="LightningArrow",
            skillId="LightningArrow",
            nameSpec="Lightning Arrow",
        )
    )
    skill.append(
        make_gem(
            level="20",
            gemId="Metadata/Items/Gems/SupportGemOvercharge",
            variantId="SupportOvercharge",
            skillId="SupportOvercharge",
            nameSpec="Overcharge",
        )
    )
    return skill


def make_budget_skill_set(source_skills: ET.Element) -> ET.Element:
    """Retain Part 1 mechanics while removing its explosion placeholder."""

    source_sets = source_skills.findall("SkillSet")
    try:
        source_set = next(
            skill_set
            for skill_set in source_sets
            if any(
                gem.get("nameSpec") == "Herald of Thunder"
                for gem in skill_set.findall(".//Gem")
            )
        )
    except StopIteration as error:
        raise ValueError("Part 1 source has no Herald of Thunder skill set") from error

    result = ET.Element(
        "SkillSet",
        {"id": "1", "title": "01 Lv80 Minimum Voltaxic Transition - Gems"},
    )
    result.append(make_lightning_arrow_group())

    level_overrides = {
        "Cast when Damage Taken": "1",
        "Crackling Lance of Branching": "4",
        "Immortal Call": "3",
        "Empower": "3",
        "Added Lightning Damage": "20",
    }
    for source_skill in source_set.findall("Skill"):
        if source_skill.get("source") == "Explode":
            continue
        skill = copy.deepcopy(source_skill)
        names = [gem.get("nameSpec") for gem in skill.findall("Gem")]
        if "Flame Dash" in names:
            for gem in list(skill.findall("Gem")):
                if gem.get("nameSpec") != "Flame Dash":
                    skill.remove(gem)
            skill.set("slot", "Weapon 1")
        elif "Withering Step" in names:
            for gem in list(skill.findall("Gem")):
                if gem.get("nameSpec") == "Phase Run":
                    skill.remove(gem)

        for gem in skill.findall("Gem"):
            gem.set("quality", "0")
            name = gem.get("nameSpec", "")
            if name in level_overrides:
                gem.set("level", level_overrides[name])
            elif (gem.get("level") or "0").isdigit() and int(gem.get("level", "0")) > 20:
                gem.set("level", "20")
        result.append(skill)

    groups = result.findall("Skill")
    if len(groups) != 7:
        raise ValueError(f"Expected seven minimum-transition skill groups, found {len(groups)}")
    main_group = groups[6]
    if not any(gem.get("nameSpec") == "Herald of Thunder" for gem in main_group.findall("Gem")):
        raise ValueError("Herald of Thunder must remain socket group 7")
    return result


def make_item(item_definition: dict[str, object]) -> ET.Element:
    """Convert a canonical item template to a PoB Item element."""

    item = ET.Element("Item", {"id": str(item_definition["id"])})
    lines = item_definition["text"]
    if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines):
        raise ValueError(f"Item {item_definition['id']} text must be a string list")
    item.text = "\n" + "\n".join(lines) + "\n"
    return item


def serialize_config_value(entry: dict[str, object]) -> str:
    """Serialize config values while preserving case-sensitive list entries."""

    value = str(entry["value"])
    return value.lower() if entry["type"] == "boolean" else value


def derive_official_budget_spec(
    source_spec: ET.Element,
    available_nodes: dict[int, set[int]],
    keep_socket_node: int,
    socket_item_id: str,
    target_tree_version: str,
) -> tuple[ET.Element, set[int]]:
    """Prune clusters and unused jewels from MAGEFIST's official Part 1 tree."""

    ordered_nodes = [
        int(node) for node in (source_spec.get("nodes") or "").split(",") if node
    ]
    source_socket_nodes = {
        int(socket.get("nodeId", "0"))
        for socket in source_spec.findall("./Sockets/Socket")
    }
    removed_nodes = {
        node for node in ordered_nodes if node not in available_nodes
    } | (source_socket_nodes - {keep_socket_node})
    budget_nodes = [node for node in ordered_nodes if node not in removed_nodes]
    if keep_socket_node not in budget_nodes:
        raise ValueError("Official Part 1 tree does not allocate the Lone Messenger socket")

    attributes = {
        "classId": source_spec.get("classId", "2"),
        "ascendClassId": source_spec.get("ascendClassId", "3"),
        "secondaryAscendClassId": source_spec.get("secondaryAscendClassId", "nil"),
        "nodes": ",".join(str(node) for node in budget_nodes),
        "masteryEffects": source_spec.get("masteryEffects", ""),
        "clusterHashFormatVersion": source_spec.get("clusterHashFormatVersion", "2"),
        "treeVersion": target_tree_version,
        "title": "01 Lv80 MAGEFIST Part 1 Pruned - Passive Tree",
    }
    spec = ET.Element("Spec", attributes)
    source_url = source_spec.findtext("URL")
    ET.SubElement(spec, "URL").text = source_url
    sockets = ET.SubElement(spec, "Sockets")
    ET.SubElement(
        sockets,
        "Socket",
        {"nodeId": str(keep_socket_node), "itemId": socket_item_id},
    )
    ET.SubElement(spec, "Overrides")
    return spec, removed_nodes


def build_minimum_document(
    definition: dict[str, object],
    source_xml: bytes,
    tree_path: Path,
) -> tuple[ET.ElementTree, list[dict[str, object]]]:
    """Build the single-stage minimum transition document."""

    root = ET.fromstring(source_xml)
    build = root.find("Build")
    tree = root.find("Tree")
    skills = root.find("Skills")
    items = root.find("Items")
    config = root.find("Config")
    notes = root.find("Notes")
    calcs = root.find("Calcs")
    if any(section is None for section in (build, tree, skills, items, config, notes)):
        raise ValueError("Part 1 source is missing a required PoB section")
    assert build is not None and tree is not None and skills is not None
    assert items is not None and config is not None and notes is not None

    setup = definition["minimum_transition"]  # type: ignore[index]
    tree_definition = setup["tree"]  # type: ignore[index]
    source_spec = tree.find("Spec")
    if source_spec is None:
        raise ValueError("Official Part 1 source has no passive tree")
    available_nodes = parse_tree_lua(tree_path)

    for child in list(build):
        build.remove(child)
    build.set("className", "Ranger")
    build.set("ascendClassName", "Pathfinder")
    build.set("level", str(setup["level"]))
    build.set("characterLevelAutoMode", "false")
    build.set("mainSocketGroup", "7")
    build.set("bandit", "Eramir")
    build.set("pantheonMajorGod", "Lunaris")
    build.set("pantheonMinorGod", "Ralakesh")

    for child in list(tree):
        tree.remove(child)
    calamitous_id = str(setup["calamitous_item_id"])
    spec, _removed_nodes = derive_official_budget_spec(
        source_spec,
        available_nodes,
        int(tree_definition["calamitous_socket_node"]),
        calamitous_id,
        str(tree_definition["target_tree_version"]),
    )
    tree.append(spec)
    tree.set("activeSpec", "1")

    tree_report = validate_tree_specs([spec], available_nodes)

    budget_skill_set = make_budget_skill_set(skills)
    for child in list(skills):
        skills.remove(child)
    skills.append(budget_skill_set)
    skills.set("activeSkillSet", "1")

    for child in list(items):
        items.remove(child)
    item_definitions = setup["items"]
    for item_definition in item_definitions:
        items.append(make_item(item_definition))
    item_set = ET.Element(
        "ItemSet",
        {
            "id": "1",
            "title": "01 Lv80 Minimum Voltaxic Transition - Items",
            "useSecondWeaponSet": "false",
        },
    )
    for item_definition in item_definitions:
        slot = item_definition.get("slot")
        if slot:
            ET.SubElement(
                item_set,
                "Slot",
                {"name": str(slot), "itemId": str(item_definition["id"])},
            )
    items.append(item_set)
    items.set("activeItemSet", "1")
    items.set("useSecondWeaponSet", "false")

    for child in list(config):
        config.remove(child)
    config_set = ET.Element(
        "ConfigSet",
        {"id": "1", "title": "01 Lv80 Minimum Voltaxic Transition - Configuration"},
    )
    for entry in setup["config"]:
        value = serialize_config_value(entry)
        attributes = {"name": entry["name"], entry["type"]: value}
        ET.SubElement(config_set, "Input", attributes)
    config.append(config_set)
    config.set("activeConfigSet", "1")

    notes.text = "\n".join(definition["minimum_transition_pob_notes"])
    if calcs is not None:
        for child in list(calcs):
            calcs.remove(child)
    return ET.ElementTree(root), tree_report


def validate_output(
    output_path: Path,
    definition: dict[str, object],
    available_nodes: dict[int, set[int]],
) -> dict[str, object]:
    """Fail closed if the installed minimum PoB loses a mechanical gate."""

    root = ET.parse(output_path).getroot()
    setup = definition["minimum_transition"]  # type: ignore[index]
    build = root.find("Build")
    spec = root.find("./Tree/Spec")
    skill_set = root.find("./Skills/SkillSet")
    item_set = root.find("./Items/ItemSet")
    if any(section is None for section in (build, spec, skill_set, item_set)):
        raise ValueError("Installed minimum PoB is missing a required section")
    assert build is not None and spec is not None and skill_set is not None and item_set is not None

    if build.get("level") != str(setup["level"]):
        raise ValueError("Installed minimum PoB has the wrong character level")
    if build.get("className") != "Ranger" or build.get("ascendClassName") != "Pathfinder":
        raise ValueError("Installed minimum PoB must be a Ranger Pathfinder")
    if build.findall("PlayerStat"):
        raise ValueError("Installed minimum PoB contains stale cached player stats")

    tree_report = validate_tree_specs([spec], available_nodes)
    actual_nodes = {int(node) for node in (spec.get("nodes") or "").split(",") if node}
    expected_count = int(setup["tree"]["official_pruned_node_count"])
    if len(actual_nodes) != expected_count:
        raise ValueError("Installed minimum PoB has the wrong official-pruned node count")
    if any(node not in available_nodes for node in actual_nodes):
        raise ValueError("Installed minimum PoB retained a dynamic cluster node")
    socket_nodes = {
        int(socket.get("nodeId", "0")) for socket in spec.findall("./Sockets/Socket")
    }
    if socket_nodes != {int(setup["tree"]["calamitous_socket_node"])}:
        raise ValueError("Installed minimum PoB retained a non-budget jewel socket")

    all_items = root.findall("./Items/Item")
    item_ids = {item.get("id") for item in all_items}
    references = referenced_item_ids(item_set, spec)
    orphaned = sorted(references - item_ids)
    if orphaned:
        raise ValueError(f"Installed minimum PoB has orphaned item references: {orphaned}")
    item_text = "\n".join(item.text or "" for item in all_items)
    for required in setup["required_items"]:
        if required not in item_text:
            raise ValueError(f"Installed minimum PoB is missing required item: {required}")
    for excluded in setup["excluded_expensive_items"]:
        if excluded in item_text:
            raise ValueError(f"Expensive item leaked into minimum PoB: {excluded}")
    dendrobate = next(item.text or "" for item in all_items if "Dendrobate" in (item.text or ""))
    if "Sockets: G-W-W-W-W-W" not in dendrobate or "Corrupted" in dendrobate:
        raise ValueError("Minimum Dendrobate must be the usable uncorrupted six-link template")

    groups = skill_set.findall("Skill")
    if len(groups) != 7 or build.get("mainSocketGroup") != "7":
        raise ValueError("Installed minimum PoB must have seven skill groups with group 7 active")
    main_names = [gem.get("nameSpec") for gem in groups[6].findall("Gem")]
    if main_names != setup["main_link"]:
        raise ValueError(f"Installed minimum PoB main link differs: {main_names}")
    if not any(
        [gem.get("nameSpec") for gem in group.findall("Gem")]
        == ["Lightning Arrow", "Overcharge"]
        for group in groups
    ):
        raise ValueError("Installed minimum PoB is missing Lightning Arrow + Overcharge")
    if any(group.get("slot") == "Weapon 2" for group in groups):
        raise ValueError("A bow build cannot place gems in its quiver slot")

    return {
        "level": int(build.get("level", "0")),
        "passive_nodes": len(actual_nodes),
        "masteries": tree_report[0]["masteries"],
        "skill_groups": len(groups),
        "items": len(all_items),
        "orphaned_item_references": len(orphaned),
        "cached_player_stats": len(build.findall("PlayerStat")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tree-data", type=Path)
    args = parser.parse_args()

    definition = json.loads(args.spec.read_text(encoding="utf-8"))
    source = definition["sources"]["pob_stages"][0]
    output_path = args.output or Path(definition["outputs"]["minimum_transition_pob"])
    pob_root = output_path.parents[2]
    tree_path = args.tree_data or pob_root / "TreeData" / "3_29" / "tree.lua"
    if not tree_path.is_file():
        raise FileNotFoundError(f"Installed PoB 3.29 tree data not found: {tree_path}")

    source_code, source_xml = fetch_pob(source["raw_url"])
    document, tree_report = build_minimum_document(definition, source_xml, tree_path)
    write_atomic(document, output_path)
    validation = validate_output(output_path, definition, parse_tree_lua(tree_path))

    result = {
        "output": str(output_path),
        "bytes": output_path.stat().st_size,
        "source": source["url"],
        "source_code_sha256": hashlib.sha256(source_code.encode("utf-8")).hexdigest().upper(),
        "source_xml_sha256": hashlib.sha256(source_xml).hexdigest().upper(),
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest().upper(),
        "tree_data": str(tree_path),
        "tree_validation": tree_report,
        **validation,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
