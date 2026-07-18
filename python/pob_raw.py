# -*- coding: utf-8 -*-
"""Loss-preserving PoB XML extraction.

`pob_parser.py` produces a coach-friendly build_data shape. This module keeps a
separate raw-ish layer so later lenses can revisit original PoB structure
without relying on already-filtered summaries.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Optional


def _attrs(element: Optional[ET.Element]) -> dict[str, str]:
    return dict(element.attrib) if element is not None else {}


def _text(element: Optional[ET.Element]) -> str:
    return (element.text or "").strip() if element is not None else ""


def _float_or_text(value: str) -> float | str:
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _extract_skill_sets(skills_element: Optional[ET.Element]) -> dict[str, Any]:
    if skills_element is None:
        return {
            "active_skill_set_id": "",
            "skill_sets": [],
            "legacy_skills": [],
        }

    skill_sets = []
    for skill_set in skills_element.findall("./SkillSet"):
        skills = []
        for skill in skill_set.findall("./Skill"):
            gems = []
            for gem in skill.findall("./Gem"):
                gems.append({
                    "attributes": _attrs(gem),
                    "name_spec": gem.get("nameSpec", ""),
                    "skill_id": gem.get("skillId", ""),
                    "enabled": gem.get("enabled", ""),
                    "level": gem.get("level", ""),
                    "quality": gem.get("quality", ""),
                })
            skills.append({
                "attributes": _attrs(skill),
                "label": skill.get("label", ""),
                "enabled": skill.get("enabled", ""),
                "main_active_skill": skill.get("mainActiveSkill", ""),
                "gems": gems,
            })
        skill_sets.append({
            "attributes": _attrs(skill_set),
            "id": skill_set.get("id", ""),
            "title": skill_set.get("title", ""),
            "skills": skills,
        })

    legacy_skills = []
    if not skill_sets:
        for skill in skills_element.findall("./Skill"):
            gems = [
                {
                    "attributes": _attrs(gem),
                    "name_spec": gem.get("nameSpec", ""),
                    "skill_id": gem.get("skillId", ""),
                    "enabled": gem.get("enabled", ""),
                    "level": gem.get("level", ""),
                    "quality": gem.get("quality", ""),
                }
                for gem in skill.findall("./Gem")
            ]
            legacy_skills.append({
                "attributes": _attrs(skill),
                "label": skill.get("label", ""),
                "enabled": skill.get("enabled", ""),
                "main_active_skill": skill.get("mainActiveSkill", ""),
                "gems": gems,
            })

    return {
        "attributes": _attrs(skills_element),
        "active_skill_set_id": skills_element.get("activeSkillSet", ""),
        "skill_sets": skill_sets,
        "legacy_skills": legacy_skills,
    }


def _parse_item_text(raw_text: str) -> dict[str, Any]:
    lines = [line.strip() for line in raw_text.splitlines()]
    non_empty = [line for line in lines if line]
    rarity = ""
    name = ""
    base_type = ""
    if non_empty:
        first = non_empty[0]
        if first.casefold().startswith("rarity:"):
            rarity = first.split(":", 1)[1].strip().title()
    if len(non_empty) > 1:
        name = non_empty[1]
    if len(non_empty) > 2:
        base_type = non_empty[2]
    return {
        "rarity": rarity,
        "name": name,
        "base_type": base_type,
        "lines": lines,
        "non_empty_lines": non_empty,
    }


def _extract_items(items_element: Optional[ET.Element]) -> dict[str, Any]:
    if items_element is None:
        return {
            "active_item_set_id": "",
            "items": {},
            "item_sets": [],
        }

    items: dict[str, dict[str, Any]] = {}
    for item in items_element.findall(".//Item"):
        item_id = item.get("id", "")
        if not item_id:
            continue
        raw_text = _text(item)
        items[item_id] = {
            "id": item_id,
            "attributes": _attrs(item),
            "raw_text": raw_text,
            "parsed_text": _parse_item_text(raw_text),
        }

    item_sets = []
    for item_set in items_element.findall(".//ItemSet"):
        slots = []
        for slot in item_set.findall("./Slot"):
            slots.append({
                "attributes": _attrs(slot),
                "name": slot.get("name", ""),
                "item_id": slot.get("itemId", ""),
            })
        item_sets.append({
            "attributes": _attrs(item_set),
            "id": item_set.get("id", ""),
            "title": item_set.get("title", ""),
            "slots": slots,
        })

    return {
        "attributes": _attrs(items_element),
        "active_item_set_id": items_element.get("activeItemSet", ""),
        "items": items,
        "item_sets": item_sets,
    }


def _extract_tree(tree_element: Optional[ET.Element]) -> dict[str, Any]:
    if tree_element is None:
        return {
            "active_spec_id": "",
            "specs": [],
        }

    specs = []
    for spec in tree_element.findall("./Spec"):
        url = spec.find("./URL")
        sockets = []
        for socket in spec.findall(".//Socket"):
            sockets.append({
                "attributes": _attrs(socket),
                "node_id": socket.get("nodeId", ""),
                "item_id": socket.get("itemId", ""),
            })
        specs.append({
            "attributes": _attrs(spec),
            "id": spec.get("id", ""),
            "title": spec.get("title", ""),
            "tree_version": spec.get("treeVersion", ""),
            "url": _text(url),
            "sockets": sockets,
        })

    return {
        "attributes": _attrs(tree_element),
        "active_spec_id": tree_element.get("activeSpec", ""),
        "specs": specs,
    }


def _extract_config(root: ET.Element) -> dict[str, Any]:
    config = root.find("Config")
    if config is None:
        return {
            "inputs": {},
            "sections": [],
            "present": False,
        }

    inputs: dict[str, Any] = {}
    sections = []
    for child in list(config):
        entry = {
            "tag": child.tag,
            "attributes": _attrs(child),
            "text": _text(child),
        }
        sections.append(entry)
        key = child.get("name") or child.get("id") or child.get("stat") or child.tag
        value = child.get("value")
        if value is None:
            value = _text(child)
        if key:
            inputs[str(key)] = value

    return {
        "attributes": _attrs(config),
        "inputs": inputs,
        "sections": sections,
        "present": True,
    }


def _extract_player_stats(root: ET.Element) -> dict[str, Any]:
    rows = []
    values: dict[str, Any] = {}
    for stat in root.findall(".//PlayerStat"):
        name = stat.get("stat", "")
        value = stat.get("value", "")
        row = {
            "attributes": _attrs(stat),
            "stat": name,
            "value": value,
        }
        rows.append(row)
        if name:
            values[name] = _float_or_text(value)
    return {
        "rows": rows,
        "values": values,
    }


def extract_pob_raw(xml_string: str, pob_url: str = "") -> dict[str, Any]:
    root = ET.fromstring(xml_string)
    build = root.find("Build")
    notes = root.find("Notes")
    skills = root.find("Skills")
    items = root.find("Items")
    tree = root.find("Tree")

    raw = {
        "schema_version": 1,
        "source": {
            "pob_url": pob_url,
            "root_tag": root.tag,
        },
        "build": {
            "attributes": _attrs(build),
        },
        "notes": _text(notes),
        "skills": _extract_skill_sets(skills),
        "items": _extract_items(items),
        "tree": _extract_tree(tree),
        "config": _extract_config(root),
        "player_stats": _extract_player_stats(root),
    }
    raw["summary"] = {
        "skill_set_count": len(raw["skills"].get("skill_sets", [])),
        "legacy_skill_count": len(raw["skills"].get("legacy_skills", [])),
        "item_count": len(raw["items"].get("items", {})),
        "item_set_count": len(raw["items"].get("item_sets", [])),
        "tree_spec_count": len(raw["tree"].get("specs", [])),
        "config_present": bool(raw["config"].get("present")),
        "player_stat_count": len(raw["player_stats"].get("rows", [])),
    }
    return raw


__all__ = ["extract_pob_raw"]
