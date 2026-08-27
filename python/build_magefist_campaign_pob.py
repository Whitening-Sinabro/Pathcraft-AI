"""Build and install the staged campaign companion for MAGEFIST Chaos HoT.

The MAGEFIST videos do not publish a campaign PoB.  This generator preserves the
act-by-act Ranger/Pathfinder data from the independently authored MrRonit PConc
starter, removes its unrelated endgame tab, and refuses to migrate the retained
trees to 3.29 unless every node and mastery effect exists in the installed 3.29
Path of Building tree data.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zlib


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = (
    ROOT
    / "config"
    / "build_setups"
    / "magefist_chaos_hot_pathfinder_3_29.spec.json"
)


def decode_pob_code(code: str) -> bytes:
    """Decode a Path of Building share code into XML bytes."""

    compact = code.strip()
    padded = compact + "=" * (-len(compact) % 4)
    return zlib.decompress(base64.urlsafe_b64decode(padded))


def fetch_pob(raw_url: str) -> tuple[str, bytes]:
    """Fetch a public raw PoB code and return both code and decoded XML."""

    request = urllib.request.Request(
        raw_url,
        headers={"User-Agent": "Pathcraft-AI/1.0 (campaign PoB generator)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        code = response.read().decode("utf-8").strip()
    if not code:
        raise ValueError(f"Empty PoB response from {raw_url}")
    try:
        xml_bytes = decode_pob_code(code)
        decoded_root = ET.fromstring(xml_bytes)
    except (ValueError, zlib.error, ET.ParseError) as error:
        raise ValueError(f"Invalid PoB response from {raw_url}") from error
    if decoded_root.tag != "PathOfBuilding":
        raise ValueError(f"Unexpected PoB XML root from {raw_url}: {decoded_root.tag}")
    return code, xml_bytes


def parse_mastery_pairs(value: str | None) -> list[tuple[int, int]]:
    """Parse PoB's ``{node,effect},{node,effect}`` mastery representation."""

    if not value:
        return []
    return [(int(node), int(effect)) for node, effect in re.findall(r"\{(\d+),(\d+)\}", value)]


def parse_tree_lua(tree_path: Path) -> dict[int, set[int]]:
    """Return passive node IDs mapped to the mastery effects in each node block."""

    text = tree_path.read_text(encoding="utf-8")
    start_marker = '    ["nodes"]= {'
    end_marker = '    ["jewelSlots"]= {'
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise ValueError(f"Could not locate top-level passive nodes in {tree_path}")

    section = text[start:end]
    matches = list(re.finditer(r"(?m)^        \[(\d+)\]= \{\s*$", section))
    if not matches:
        raise ValueError(f"No passive node blocks found in {tree_path}")

    result: dict[int, set[int]] = {}
    for index, match in enumerate(matches):
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        block = section[match.start():block_end]
        node_id = int(match.group(1))
        result[node_id] = {
            int(effect)
            for effect in re.findall(r'\["effect"\]= (\d+)', block)
        }
    return result


def validate_tree_specs(
    specs: list[ET.Element],
    available_nodes: dict[int, set[int]],
) -> list[dict[str, object]]:
    """Validate all allocated nodes and selected mastery effects."""

    reports: list[dict[str, object]] = []
    for spec in specs:
        title = spec.get("title", "untitled")
        node_ids = {
            int(value)
            for value in (spec.get("nodes") or "").split(",")
            if value
        }
        missing_nodes = sorted(node_ids - available_nodes.keys())
        invalid_masteries: list[dict[str, int | str]] = []
        mastery_pairs = parse_mastery_pairs(spec.get("masteryEffects"))
        for node_id, effect_id in mastery_pairs:
            if node_id not in node_ids:
                invalid_masteries.append(
                    {"node": node_id, "effect": effect_id, "reason": "mastery node not allocated"}
                )
            elif effect_id not in available_nodes.get(node_id, set()):
                invalid_masteries.append(
                    {"node": node_id, "effect": effect_id, "reason": "effect missing in 3.29"}
                )
        if missing_nodes or invalid_masteries:
            raise ValueError(
                f"3.29 tree validation failed for {title}: "
                f"missing nodes={missing_nodes}, invalid masteries={invalid_masteries}"
            )
        reports.append(
            {
                "title": title,
                "nodes": len(node_ids),
                "masteries": len(mastery_pairs),
            }
        )
    return reports


def children_by_title(container: ET.Element, tag: str) -> dict[str, ET.Element]:
    """Index direct child elements by their required title attribute."""

    result: dict[str, ET.Element] = {}
    for child in container.findall(tag):
        title = child.get("title")
        if not title:
            raise ValueError(f"Untitled {tag} in campaign source")
        if title in result:
            raise ValueError(f"Duplicate {tag} title in campaign source: {title}")
        result[title] = child
    return result


def referenced_item_ids(*elements: ET.Element) -> set[str]:
    """Collect all non-zero itemId references below the supplied elements."""

    result: set[str] = set()
    for element in elements:
        for descendant in element.iter():
            item_id = descendant.get("itemId")
            if item_id and item_id != "0":
                result.add(item_id)
    return result


def add_transition_gem_preparation(
    skill_set: ET.Element,
    preparation: dict[str, object],
) -> None:
    """Add the six off-hand gems that must be levelled before the level-80 swap."""

    skill = ET.SubElement(
        skill_set,
        "Skill",
        {
            "enabled": "true",
            "mainActiveSkillCalcs": "1",
            "mainActiveSkill": "1",
            "slot": str(preparation["slot"]),
            "label": str(preparation["label"]),
            "includeInFullDPS": "false",
        },
    )
    for gem in preparation["gems"]:  # type: ignore[index]
        ET.SubElement(
            skill,
            "Gem",
            {
                "count": "1",
                "enableGlobal1": "true",
                "enableGlobal2": "true",
                "skillId": str(gem["skill_id"]),
                "variantId": str(gem["variant_id"]),
                "gemId": str(gem["gem_id"]),
                "quality": "0",
                "level": str(gem["target_level"]),
                "nameSpec": str(gem["name"]),
                "enabled": "true",
            },
        )


def build_campaign_document(
    definition: dict[str, object],
    source_xml: bytes,
    tree_path: Path,
) -> tuple[ET.ElementTree, list[dict[str, object]]]:
    """Create the six-stage campaign-only document from the canonical spec."""

    root = ET.fromstring(source_xml)
    build = root.find("Build")
    tree = root.find("Tree")
    skills = root.find("Skills")
    items = root.find("Items")
    config = root.find("Config")
    if any(section is None for section in (build, tree, skills, items, config)):
        raise ValueError("Campaign source is missing a required PoB section")
    assert build is not None and tree is not None and skills is not None
    assert items is not None and config is not None
    if build.get("className") != "Ranger" or build.get("ascendClassName") != "Pathfinder":
        raise ValueError("Campaign source must be a Ranger Pathfinder")

    campaign = definition["sources"]["campaign_pob"]  # type: ignore[index]
    stage_defs = campaign["stages"]  # type: ignore[index]
    if len(stage_defs) != 6:
        raise ValueError("Canonical campaign setup must contain exactly six stages")

    source_specs = children_by_title(tree, "Spec")
    source_skill_sets = children_by_title(skills, "SkillSet")
    source_item_sets = children_by_title(items, "ItemSet")
    source_config_sets = children_by_title(config, "ConfigSet")

    kept_specs: list[ET.Element] = []
    kept_skill_sets: list[ET.Element] = []
    kept_item_sets: list[ET.Element] = []
    kept_config_sets: list[ET.Element] = []
    gem_preparation = definition["campaign_transition_gem_preparation"]
    for stage_index, stage in enumerate(stage_defs, start=1):
        source_title = stage["source_title"]
        target_title = stage["title"]
        try:
            spec = copy.deepcopy(source_specs[source_title])
            skill_set = copy.deepcopy(source_skill_sets[source_title])
            item_set = copy.deepcopy(source_item_sets[source_title])
            config_set = copy.deepcopy(source_config_sets[stage["config_source_title"]])
        except KeyError as error:
            raise ValueError(f"Missing campaign source stage: {error.args[0]}") from error

        if not any(
            gem.get("nameSpec") == stage["main_skill"]
            for gem in skill_set.findall(".//Gem")
        ):
            raise ValueError(
                f"Expected main skill {stage['main_skill']} is absent from {source_title}"
            )

        spec.set("title", f"{target_title} - Passive Tree")
        skill_set.set("id", str(stage_index))
        skill_set.set("title", f"{target_title} - Gems")
        item_set.set("id", str(stage_index))
        item_set.set("title", f"{target_title} - Items")
        config_set.set("id", str(stage_index))
        config_set.set("title", f"{target_title} - Configuration")
        if stage_index >= int(gem_preparation["start_stage"]):  # type: ignore[arg-type]
            add_transition_gem_preparation(skill_set, gem_preparation)
        kept_specs.append(spec)
        kept_skill_sets.append(skill_set)
        kept_item_sets.append(item_set)
        kept_config_sets.append(config_set)

    available_nodes = parse_tree_lua(tree_path)
    tree_report = validate_tree_specs(kept_specs, available_nodes)
    target_tree_version = campaign["conversion_target_tree_version"]
    for spec in kept_specs:
        spec.set("treeVersion", target_tree_version)

    item_ids = referenced_item_ids(*kept_item_sets, *kept_specs)
    source_items = {item.get("id"): item for item in items.findall("Item")}
    missing_items = sorted(item_ids - source_items.keys())
    if missing_items:
        raise ValueError(f"Campaign source has orphaned item references: {missing_items}")
    kept_items = [
        copy.deepcopy(item)
        for item in items.findall("Item")
        if item.get("id") in item_ids
    ]

    for child in list(tree):
        if child.tag == "Spec":
            tree.remove(child)
    for spec in kept_specs:
        tree.append(spec)
    tree.set("activeSpec", "1")

    for child in list(skills):
        if child.tag == "SkillSet":
            skills.remove(child)
    for skill_set in kept_skill_sets:
        skills.append(skill_set)
    skills.set("activeSkillSet", "1")

    for child in list(items):
        if child.tag in {"Item", "ItemSet"}:
            items.remove(child)
    for item in kept_items:
        items.append(item)
    for item_set in kept_item_sets:
        items.append(item_set)
    items.set("activeItemSet", "1")

    for child in list(config):
        if child.tag == "ConfigSet":
            config.remove(child)
    for config_set in kept_config_sets:
        config.append(config_set)
    config.set("activeConfigSet", "1")

    build.set("level", str(stage_defs[0]["level"]))
    build.set("mainSocketGroup", "1")
    build.set("className", "Ranger")
    build.set("ascendClassName", "Pathfinder")

    notes = root.find("Notes")
    if notes is None:
        notes = ET.SubElement(root, "Notes")
    original_notes = notes.text or ""
    canonical_notes = "\r\n".join(definition["campaign_pob_notes"])
    if original_notes.strip():
        canonical_notes += (
            "\r\n\r\n^xFFAAAAAA--- Original MrRonit source notes ---^7\r\n"
            + original_notes.strip()
        )
    notes.text = canonical_notes

    return ET.ElementTree(root), tree_report


def validate_output(
    output_path: Path,
    stage_defs: list[dict[str, object]],
    target_tree_version: str,
) -> dict[str, object]:
    """Re-open the installed XML and validate its cross-section references."""

    root = ET.parse(output_path).getroot()
    specs = root.findall("./Tree/Spec")
    skill_sets = root.findall("./Skills/SkillSet")
    item_sets = root.findall("./Items/ItemSet")
    config_sets = root.findall("./Config/ConfigSet")
    counts = [len(specs), len(skill_sets), len(item_sets), len(config_sets)]
    if counts != [6, 6, 6, 6]:
        raise ValueError(f"Unexpected output stage counts: {counts}")
    if any(spec.get("treeVersion") != target_tree_version for spec in specs):
        raise ValueError("Not every retained passive stage uses the validated 3.29 tree")
    all_titles = "\n".join(
        element.get("title", "")
        for element in [*specs, *skill_sets, *item_sets, *config_sets]
    )
    if "Endgame" in all_titles:
        raise ValueError("Unrelated PConc Endgame stage leaked into the campaign file")

    item_ids = {item.get("id") for item in root.findall("./Items/Item")}
    refs = referenced_item_ids(*item_sets, *specs)
    orphaned = sorted(refs - item_ids)
    if orphaned:
        raise ValueError(f"Installed campaign PoB has orphaned item references: {orphaned}")

    for stage, skill_set in zip(stage_defs, skill_sets, strict=True):
        if not any(
            gem.get("nameSpec") == stage["main_skill"]
            for gem in skill_set.findall(".//Gem")
        ):
            raise ValueError(f"Installed stage is missing {stage['main_skill']}")

    return {
        "passive_stages": counts[0],
        "skill_stages": counts[1],
        "item_stages": counts[2],
        "config_stages": counts[3],
        "orphaned_item_references": len(orphaned),
    }


def write_atomic(document: ET.ElementTree, output_path: Path) -> None:
    """Write UTF-8 XML next to the destination and atomically replace it."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(document, space="  ")
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.stem}.", suffix=".tmp", dir=output_path.parent
    )
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        document.write(temporary_path, encoding="utf-8", xml_declaration=True)
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tree-data", type=Path)
    args = parser.parse_args()

    definition = json.loads(args.spec.read_text(encoding="utf-8"))
    campaign = definition["sources"]["campaign_pob"]
    output_path = args.output or Path(definition["outputs"]["campaign_pob"])
    pob_root = output_path.parents[2]
    tree_path = args.tree_data or (
        pob_root
        / "TreeData"
        / campaign["conversion_target_tree_version"]
        / "tree.lua"
    )
    if not tree_path.is_file():
        raise FileNotFoundError(f"Installed PoB 3.29 tree data not found: {tree_path}")

    source_code, source_xml = fetch_pob(campaign["raw_url"])
    document, tree_report = build_campaign_document(definition, source_xml, tree_path)
    write_atomic(document, output_path)
    validation = validate_output(
        output_path,
        campaign["stages"],
        campaign["conversion_target_tree_version"],
    )

    result = {
        "output": str(output_path),
        "bytes": output_path.stat().st_size,
        "source": campaign["url"],
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
