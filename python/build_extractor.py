# -*- coding: utf-8 -*-
"""POB 빌드 데이터 파싱 헬퍼.

filter_generator.py(aurora) 및 sections_continue.py(β)에서 공용.
"""

from typing import Optional


# 유니크 → 디비니 카드 매핑 (빌드 타겟용)
UNIQUE_TO_DIVCARD: dict[str, list[dict]] = {
    "Death's Oath": [{"card": "The Oath", "stack": 6}],
    "Shavronne's Wrappings": [{"card": "The Offering", "stack": 8}],
    "Headhunter": [{"card": "The Doctor", "stack": 8}, {"card": "The Fiend", "stack": 11}],
    "Mageblood": [{"card": "The Apothecary", "stack": 13}],
    "Aegis Aurora": [{"card": "The Gladiator", "stack": 5}],
    "Kaom's Heart": [{"card": "The King's Heart", "stack": 8}],
    "The Squire": [{"card": "The Shieldbearer", "stack": 13}],
    "Ashes of the Stars": [{"card": "The Enlightened", "stack": 6}],
    "Nimis": [{"card": "The Rabbit's Foot", "stack": 9}],
    "Badge of the Brotherhood": [{"card": "Brotherhood in Exile", "stack": 5}],
    "Inpulsa's Broken Heart": [{"card": "The Spark and the Flame", "stack": 7}],
    "Cospri's Malice": [{"card": "The Wolven King's Bite", "stack": 8}],
    "Hyrri's Ire": [{"card": "The Wind", "stack": 10}],
    "Tabula Rasa": [{"card": "Humility", "stack": 9}],
    "Skin of the Loyal": [{"card": "The Sacrifice", "stack": 9}],
    "Replica Farruls Fur": [{"card": "The Cheater", "stack": 5}],
    "The Brass Dome": [{"card": "The Mountain", "stack": 8}],
    "Cloak of Defiance": [{"card": "The Easy Stroll", "stack": 5}],
    "Queen of the Forest": [{"card": "The Wolf", "stack": 5}],
    "Doryani's Prototype": [{"card": "Doryani's Epiphany", "stack": 5}],
    "Forbidden Shako": [{"card": "The Dragon's Heart", "stack": 10}],
}

# 유니크 → chanceable 베이스 매핑 (자주 쓰이는 것만)
UNIQUE_TO_BASE: dict[str, str] = {
    "Tabula Rasa": "Simple Robe",
    "Goldrim": "Leather Cap",
    "Wanderlust": "Wool Shoes",
    "Lifesprig": "Driftwood Wand",
    "Praxis": "Paua Ring",
    "Le Heup of All": "Iron Ring",
    "Berek's Grip": "Two-Stone Ring",
    "Berek's Pass": "Two-Stone Ring",
    "Berek's Respite": "Two-Stone Ring",
    "Aegis Aurora": "Champion Kite Shield",
    "Death's Oath": "Astral Plate",
    "Shavronne's Wrappings": "Occultist's Vestment",
    "Inpulsa's Broken Heart": "Sadist Garb",
    "Cospri's Malice": "Jewelled Foil",
    "Hyrri's Ire": "Zodiac Leather",
    "The Brass Dome": "Gladiator Plate",
    "Queen of the Forest": "Destiny Leather",
    "Cloak of Defiance": "Lacquered Garb",
    "Doryani's Prototype": "Saint's Hauberk",
    "Mageblood": "Heavy Belt",
    "Headhunter": "Leather Belt",
    "Kaom's Heart": "Glorious Plate",
}


def extract_build_uniques(
    build_data: dict,
    coaching_data: Optional[dict] = None,
) -> list[str]:
    """빌드에서 사용하는 유니크 아이템 이름 추출.

    소스 우선순위:
    1. coaching_data의 key_items (AI 코치가 식별한 핵심 장비)
    2. build_data의 progression_stages에서 gear 정보
    3. build_data.items 필드 (POB 직접 파싱)
    """
    uniques: set[str] = set()

    if coaching_data:
        for item in coaching_data.get("key_items", []):
            name = item.get("name", "")
            if name:
                uniques.add(name)

    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if isinstance(slot_data, dict):
                    name = slot_data.get("name", slot_data.get("item", ""))
                    rarity = slot_data.get("rarity", "")
                    if name and rarity.lower() == "unique":
                        uniques.add(name)

    for item in build_data.get("items", []):
        if isinstance(item, dict):
            if item.get("rarity", "").lower() == "unique":
                name = item.get("name", "")
                if name:
                    uniques.add(name)

    return sorted(uniques)


def get_target_divcards(unique_names: list[str]) -> list[dict]:
    """유니크 아이템 목록에서 타겟 디비니 카드 추출."""
    cards: list[dict] = []
    seen: set[str] = set()
    for uname in unique_names:
        for entry in UNIQUE_TO_DIVCARD.get(uname, []):
            card_name = entry["card"]
            if card_name not in seen:
                seen.add(card_name)
                cards.append({
                    "card": card_name,
                    "stack": entry["stack"],
                    "target_unique": uname,
                })
    return cards


def get_chanceable_bases(unique_names: list[str]) -> list[dict]:
    """유니크 아이템 목록에서 chanceable 베이스 추출."""
    bases: list[dict] = []
    seen: set[str] = set()
    for uname in unique_names:
        base = UNIQUE_TO_BASE.get(uname)
        if base and base not in seen:
            seen.add(base)
            bases.append({"base": base, "unique": uname})
    return bases


def extract_build_gems(build_data: dict) -> tuple[list[str], list[str]]:
    """빌드에서 사용하는 스킬젬/서포트젬 이름 추출. (skills, supports)"""
    skills: set[str] = set()
    supports: set[str] = set()

    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gem_setups = stage.get("gem_setups", {})
        for setup_name, links in gem_setups.items():
            skills.add(setup_name)
            if isinstance(links, list):
                for link in links:
                    if isinstance(link, str):
                        supports.add(link)
                    elif isinstance(link, dict):
                        name = link.get("name", link.get("gem", ""))
                        if name:
                            if "Support" in name:
                                supports.add(name)
                            else:
                                skills.add(name)

    return sorted(skills), sorted(supports)


def extract_build_bases(build_data: dict) -> list[str]:
    """빌드 장비에서 베이스 타입 추출."""
    bases: set[str] = set()
    stages = build_data.get("progression_stages", [])
    for stage in stages:
        gear = stage.get("gear_recommendation", stage.get("gear", {}))
        if isinstance(gear, dict):
            for slot_data in gear.values():
                if isinstance(slot_data, dict):
                    base = slot_data.get("base_type", slot_data.get("base", ""))
                    if base:
                        bases.add(base)
    return sorted(bases)


def detect_build_type(build_data: dict) -> str:
    """빌드 타입 감지 (spell/attack/minion/dot)."""
    gems = " ".join(extract_build_gems(build_data)[0]).lower()
    if any(k in gems for k in ["raise zombie", "raise spectre", "summon", "animate"]):
        return "minion"
    if any(k in gems for k in ["blight", "contagion", "essence drain", "toxic rain", "caustic"]):
        return "dot"
    if any(k in gems for k in ["cyclone", "lacerate", "lightning arrow", "tornado shot"]):
        return "attack"
    return "spell"


def get_crafting_bases(build_type: str) -> list[str]:
    """빌드 타입별 크래프팅 베이스 목록."""
    common = [
        "Vaal Regalia", "Astral Plate", "Zodiac Leather", "Titanium Spirit Shield",
        "Fingerless Silk Gloves", "Sorcerer Boots", "Two-Toned Boots", "Bone Helmet",
        "Crystal Belt", "Stygian Vise", "Marble Amulet", "Opal Ring", "Vermillion Ring",
    ]
    type_specific = {
        "spell": ["Profane Wand", "Opal Sceptre", "Void Sceptre", "Samite Helmet"],
        "attack": ["Siege Axe", "Jewelled Foil", "Ambusher", "Imperial Claw",
                   "Thicket Bow", "Spine Bow"],
        "dot": ["Profane Wand", "Opal Sceptre", "Short Bow"],
        "minion": ["Convoking Wand", "Bone Helmet", "Fossilised Spirit Shield"],
    }
    return common + type_specific.get(build_type, [])
