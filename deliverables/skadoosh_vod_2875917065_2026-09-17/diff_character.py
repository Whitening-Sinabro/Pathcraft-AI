"""90레벨(09-15 적재분) 스냅샷과 91레벨(09-17 05:33 KST 갱신, 이 방송 종료 직후) 스냅샷을 대조한다.

방송 발언의 대명사 대신 공개 캐릭터 원자료로 "무엇이 실제로 바뀌었나"를 정한다.
ninja 응답 구조: skills[].allGems[] = {name, level, quality, itemData.socketedItems[]},
보조의 이름은 socketedItems[].typeLine 에 있다(allGems[].name 은 주 스킬만 채워진다).
"""
import json
import logging
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = ROOT / "deliverables/skadoosh_vod_2874116335_2026-09-15/creator_latest.json"
NEW = HERE / "creator_latest.json"

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
log = logging.getLogger("diff")


def supports(gem):
    out = []
    for socketed in (gem.get("itemData") or {}).get("socketedItems") or []:
        if not socketed.get("support"):
            continue
        out.append(socketed.get("typeLine") or socketed.get("baseType") or "?")
    return out


def summarise(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    groups = {}
    for skill in payload.get("skills") or []:
        for gem in skill.get("allGems") or []:
            name = gem.get("name") or "?"
            groups[name] = {
                "supports": supports(gem),
                "level": gem.get("level"),
                "quality": gem.get("quality"),
            }
    items = {}
    for item in payload.get("items") or []:
        data = item.get("itemData") or {}
        slot = item.get("itemSlot") or "?"
        name = (data.get("name") or "").strip() or data.get("typeLine") or data.get("baseType") or "?"
        items[slot] = name
    return payload, groups, items


def main():
    old_payload, old_groups, old_items = summarise(OLD)
    new_payload, new_groups, new_items = summarise(NEW)

    log.info("=== 레벨 %s -> %s ===", old_payload.get("level"), new_payload.get("level"))
    log.info("갱신 %s -> %s", old_payload.get("updatedUtc"), new_payload.get("updatedUtc"))
    log.info("패시브 %s -> %s", old_payload.get("passiveCounts"), new_payload.get("passiveCounts"))

    log.info("")
    log.info("=== 젬 그룹 변화 ===")
    quiet = True
    for name in sorted(set(old_groups) | set(new_groups)):
        before, after = old_groups.get(name), new_groups.get(name)
        if before == after:
            continue
        quiet = False
        if before is None:
            log.info("[신규] %-26s Lv%s/Q%s <- %s", name, after["level"], after["quality"],
                     ", ".join(after["supports"]) or "(없음)")
        elif after is None:
            log.info("[삭제] %-26s <- %s", name, ", ".join(before["supports"]) or "(없음)")
        else:
            if before["supports"] != after["supports"]:
                gone = [s for s in before["supports"] if s not in after["supports"]]
                new_s = [s for s in after["supports"] if s not in before["supports"]]
                log.info("[보조] %-26s +%s  -%s", name, ", ".join(new_s) or "-", ", ".join(gone) or "-")
            if (before["level"], before["quality"]) != (after["level"], after["quality"]):
                log.info("[레벨] %-26s Lv%s/Q%s -> Lv%s/Q%s", name, before["level"], before["quality"],
                         after["level"], after["quality"])
    if quiet:
        log.info("(변화 없음)")

    log.info("")
    log.info("=== 장비 변화 ===")
    quiet = True
    for slot in sorted(set(old_items) | set(new_items)):
        before, after = old_items.get(slot), new_items.get(slot)
        if before != after:
            quiet = False
            log.info("%-22s %s -> %s", slot, before, after)
    if quiet:
        log.info("(변화 없음)")


if __name__ == "__main__":
    main()
