# -*- coding: utf-8 -*-
"""
PoE Wiki Cargo API 연동 — 유니크 아이템 획득 정보 조회
"""

import json
import sys
import logging
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("wiki_data")
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

WIKI_API = "https://www.poewiki.net/w/api.php"
HEADERS = {"User-Agent": "PathcraftAI/1.0"}


def cargo_query(fields: str, where: str, tables: str = "items", limit: int = 10) -> list:
    params = {
        "action": "cargoquery",
        "tables": tables,
        "fields": fields,
        "where": where,
        "format": "json",
        "limit": str(limit),
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        data = r.json()
        return [item["title"] for item in data.get("cargoquery", [])]
    except Exception as e:
        logger.error(f"Wiki API 실패: {e}")
        return []


LEAGUE_PREFIXES = ["Foulborn", "Sanctified", "Foreboding", "Transfigured"]


def normalize_item_name(name: str) -> tuple[str, str | None]:
    for prefix in LEAGUE_PREFIXES:
        if name.startswith(prefix + " "):
            base_name = name[len(prefix) + 1:]
            return base_name, prefix
    return name, None


def get_item_acquisition(item_name: str) -> dict:
    results = cargo_query(
        fields="items.name, items.drop_enabled, items.is_drop_restricted, items.drop_text, items.drop_areas_html",
        where=f'items.name="{item_name}"',
    )
    if not results:
        return {"name": item_name, "error": "Wiki에서 찾을 수 없음"}

    item = results[0]
    return {
        "name": item.get("name", item_name),
        "drop_enabled": item.get("drop enabled") == "1",
        "is_drop_restricted": item.get("is drop restricted") == "1",
        "drop_text": item.get("drop text") or None,
        "drop_areas": item.get("drop areas html") or None,
    }


KNOWN_DIV_CARDS = {
    "Death's Oath": [{"card": "The Oath", "stack": 6}],
    "Shavronne's Wrappings": [{"card": "The Offering", "stack": 8}],
    "Headhunter": [{"card": "The Doctor", "stack": 8}, {"card": "The Fiend", "stack": 11}],
    "Mageblood": [{"card": "The Apothecary", "stack": 13}],
    "Aegis Aurora": [{"card": "The Gladiator", "stack": 5}],
}


def get_divination_cards_for_item(item_name: str) -> list:
    cards = []
    known = KNOWN_DIV_CARDS.get(item_name, [])
    for entry in known:
        card_info = cargo_query(
            fields="items.name, items.drop_areas_html",
            where=f'items.name="{entry["card"]}"',
        )
        drop_areas = "불명"
        if card_info:
            drop_areas = card_info[0].get("drop areas html") or "불명"
        cards.append({
            "card_name": entry["card"],
            "stack_size": entry["stack"],
            "drop_areas": drop_areas,
        })

    generic_cards = [
        {"card_name": "The Body", "stack_size": 4, "drop_areas": "일반 드롭 (모든 갑옷)"},
        {"card_name": "Jack in the Box", "stack_size": 4, "drop_areas": "일반 드롭 (모든 아이템)"},
    ]
    if not known:
        cards.extend(generic_cards)

    return cards


def get_unique_item_full_info(item_name: str) -> dict:
    base_name, league_prefix = normalize_item_name(item_name)

    acquisition = get_item_acquisition(base_name)
    div_cards = get_divination_cards_for_item(base_name)

    chanceable = not acquisition.get("is_drop_restricted", True) and acquisition.get("drop_enabled", False)

    result = {
        "name": item_name,
        "base_name": base_name,
        "drop_anywhere": acquisition.get("drop_enabled", False) and not acquisition.get("is_drop_restricted", False),
        "is_drop_restricted": acquisition.get("is_drop_restricted", False),
        "drop_text": acquisition.get("drop_text"),
        "chanceable": chanceable,
        "divination_cards": div_cards,
    }

    if league_prefix:
        result["league_variant"] = league_prefix
        result["note"] = f"{league_prefix} 변형 — 리그 메카닉 전용 모디파이어 포함. 기본 아이템({base_name})과 동일한 드롭 소스"

    return result


def get_build_items_info(item_names: list) -> list:
    results = []
    for name in item_names:
        logger.info(f"  Wiki 조회: {name}")
        info = get_unique_item_full_info(name)
        results.append(info)
    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="PoE Wiki 아이템 획득 정보")
    ap.add_argument("items", nargs="+", help="유니크 아이템 이름들")
    args = ap.parse_args()

    results = get_build_items_info(args.items)
    print(json.dumps(results, ensure_ascii=False, indent=2))
