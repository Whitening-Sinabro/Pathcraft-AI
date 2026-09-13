"""84레벨(09-08 갱신) 공개 스냅샷과 86레벨(09-11 갱신) 스냅샷을 대조한다.

방송 발언의 대명사 대신 공개 캐릭터 원자료로 "무엇이 실제로 바뀌었나"를 정한다.
"""
import json
import logging
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = ROOT / "deliverables/skadoosh_new_broadcast_2026-09-09/creator_latest.json"
NEW = HERE / "creator_latest.json"

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
log = logging.getLogger("diff")


def gem_name(entry):
    return entry.get("name") or (entry.get("itemData") or {}).get("name") or "?"


def gem_level(entry):
    for tab in (entry.get("gemTabs") or []):
        for page in (tab.get("pages") or []):
            for prop in (page.get("properties") or []):
                if prop.get("name") == "Level":
                    values = prop.get("values") or []
                    if values and values[0]:
                        return values[0][0]
    return "?"


def socket_group(skill):
    data = skill.get("itemData") or {}
    main = gem_name(skill)
    supports = []
    for socketed in data.get("socketedItems") or []:
        label = None
        for tab in (socketed.get("gemTabs") or []):
            if tab.get("name") not in ("Support", None, ""):
                label = tab["name"]
                break
        supports.append(label or "?")
    return main, supports


def summarise(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    groups = {}
    for skill in payload.get("skills") or []:
        main, supports = socket_group(skill)
        groups[main] = supports
    items = {}
    for item in payload.get("items") or []:
        slot = item.get("slot") or item.get("inventoryId") or "?"
        items[slot] = item.get("name") or item.get("typeLine") or item.get("baseType") or "?"
    return payload, groups, items


def main():
    old_payload, old_groups, old_items = summarise(OLD)
    new_payload, new_groups, new_items = summarise(NEW)

    log.info("=== 레벨 %s -> %s ===", old_payload.get("level"), new_payload.get("level"))
    log.info("갱신 시각 %s -> %s", old_payload.get("updatedUtc"), new_payload.get("updatedUtc"))

    log.info("")
    log.info("=== 스킬 그룹 (신규 스냅샷) ===")
    for main, supports in new_groups.items():
        mark = " [NEW]" if main not in old_groups else (" [CHANGED]" if old_groups[main] != supports else "")
        log.info("%-32s <- %s%s", main, ", ".join(supports) or "(없음)", mark)

    removed = [m for m in old_groups if m not in new_groups]
    if removed:
        log.info("")
        log.info("=== 사라진 스킬 그룹 ===")
        for main in removed:
            log.info("%-32s <- %s", main, ", ".join(old_groups[main]))

    log.info("")
    log.info("=== 장비 변화 ===")
    for slot in sorted(set(old_items) | set(new_items)):
        before, after = old_items.get(slot), new_items.get(slot)
        if before != after:
            log.info("%-22s %s -> %s", slot, before, after)


if __name__ == "__main__":
    main()
