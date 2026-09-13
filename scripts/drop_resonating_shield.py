"""단계 플래너 02~06 에서 공명하는 방패를 뺀다.

왜: 이 플래너는 방송 관측을 옮긴 것이라 제작자의 시행착오까지 같이 들어왔다.
공개 스냅샷으로 확인한 사실은 이렇다 —
  - 그는 24·43·74·79레벨에 공명하는 방패를 들고 있었고 79→80 사이에 뺐다.
  - 그가 배포한 Mobalytics 가이드(레벨링 4탭 + Starter/Leveling/Endgame)에는
    이 스킬이 **한 번도** 없다. 즉 남에게 권하지 않는다.
따라서 따라 하는 사람 기준으로는 넣을 이유가 없다. 관측 사실은 주석으로 남긴다.

같은 이유로 걸러 낸 것 목록(실캐릭엔 있었으나 가이드엔 없음):
  공명하는 방패 · 불의 순수함 · 광기의 선구자 · 도약 강타 · 비취에 갇힘.
이번 스크립트는 그중 **공명하는 방패만** 처리한다. 나머지는 근거가 다르다
(광기의 선구자·도약 강타·비취에 갇힘은 89레벨 현재도 쓰고 있어 "버린 것"이 아니다).

무엇을 바꾸나: `skills` 에서 해당 액티브 1개(+그 보조)를 빼고, 본문에서 그 스킬을
가리키는 줄을 지우거나 고친다. 다른 스킬·패시브·슬롯은 건드리지 않는다.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys

log = logging.getLogger("drop-rs")

GAME_DIR = pathlib.Path(os.path.expandvars(
    r"%USERPROFILE%\Documents\My Games\Path of Exile 2\BuildPlanner"))
REPO_DIR = pathlib.Path("deliverables/skadoosh_early_survival_2026-09-08/BuildPlanner")
FILES = [
    "02 충격파 토템 - 1차 전직까지.build",
    "03 토템과 망치 - 2차 전직까지.build",
    "04 타락 함성 - 마나 사용.build",
    "05 전사 토템 - 혈마법 전환.build",
    "06 파콰테 - 두 함성 운영.build",
]
GEM_ID_PART = "ResonatingShield"

NOTE = ("공명하는 방패는 뺐다. 제작자는 79레벨까지 실제로 들고 있었지만(공개 스냅샷 24·43·74·79) "
        "79→80 사이에 버렸고, 그가 배포한 가이드에는 처음부터 한 번도 없다.")

# (옛 줄, 새 줄). 새 줄이 None 이면 삭제. 줄 단위 완전 일치.
LINE_FIXES: list[tuple[str, str | None]] = [
    ("공명하는 방패 → 격노 I", None),
    ("공명하는 방패 → 격노 I + 방어구 철거자 I", None),
    ("일반 무리: 몰강·공명하는 방패로 기절을 쌓고 준비 표시가 뜨면 뼈 박살. 화산 균열을 배운 뒤에는 "
     "진행 방향의 무리에도 균열을 깔며 이동한다. 방송에서도 일반 사냥에 사용한다.",
     "일반 무리: 몰강으로 기절을 쌓고 준비 표시가 뜨면 뼈 박살. 화산 균열을 배운 뒤에는 "
     "진행 방향의 무리에도 균열을 깔며 이동한다. 방송에서도 일반 사냥에 사용한다."),
    ("선대의 전사 토템 젬 13레벨(캐릭터 52·힘 92), 셉터 2개·철퇴·방패·정신력과 생명력 재생을 준비한다. "
     "방송은 54레벨에 전환했다. 충격파 토템·망치·화산 균열·지진·뼈 박살을 빼고 보강·공명하는 방패를 "
     "유지한다. 기존 토템의 포악함 II를 전사 토템으로 옮긴다. 마그마 장벽의 명상 II를 제거하고 "
     "순수함에 회복 보조를 준비한다. 혈마법 뒤 설치·함성이 생명력을 소모하므로 사용 후 회복이 "
     "따라오는지 확인한다.",
     "선대의 전사 토템 젬 13레벨(캐릭터 52·힘 92), 셉터 2개·철퇴·방패·정신력과 생명력 재생을 준비한다. "
     "방송은 54레벨에 전환했다. 충격파 토템·망치·화산 균열·지진·뼈 박살을 빼고 보강하는 함성을 "
     "유지한다. 기존 토템의 포악함 II를 전사 토템으로 옮긴다. 마그마 장벽의 명상 II를 제거하고 "
     "순수함에 회복 보조를 준비한다. 혈마법 뒤 설치·함성이 생명력을 소모하므로 사용 후 회복이 "
     "따라오는지 확인한다."),
    # 어제 붙인 주석 — 유지가 맞다고 적어 뒀으니 뒤집는다.
    ("공개 스냅샷: 이 단계의 공명하는 방패는 74레벨까지 실제로 들고 있던 것이다.", NOTE),
    ("           79→80 사이에 뺐다. 여기서는 유지가 맞다.", None),
]

TEXT_KEYS = ("description", "additional_text")


def carriers(node):
    if isinstance(node, dict):
        for key in TEXT_KEYS:
            if isinstance(node.get(key), str) and node[key]:
                yield node, key
        for value in node.values():
            yield from carriers(value)
    elif isinstance(node, list):
        for value in node:
            yield from carriers(value)


def fix_text(text: str, hits: list[str]) -> str:
    out = []
    for line in text.split("\n"):
        replaced = False
        for old, new in LINE_FIXES:
            if line.strip() == old:
                hits.append(old)
                if new is not None:
                    out.append(line.replace(old, new))
                replaced = True
                break
        if not replaced:
            out.append(line)
    return "\n".join(out)


def update(path: pathlib.Path, dry: bool) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    passives_before = json.dumps(data["passives"], ensure_ascii=False, sort_keys=True)
    ids_before = [s["id"] for s in data["skills"]]

    kept = [s for s in data["skills"] if GEM_ID_PART not in s["id"]]
    removed = len(data["skills"]) - len(kept)
    data["skills"] = kept

    hits: list[str] = []
    for holder, key in list(carriers(data)):
        if holder.get(key):
            holder[key] = fix_text(holder[key], hits)

    if json.dumps(data["passives"], ensure_ascii=False, sort_keys=True) != passives_before:
        raise SystemExit(f"{path.name}: 패시브가 바뀌었다")
    dropped = [i for i in ids_before if i not in {s["id"] for s in kept}]
    if any(GEM_ID_PART not in i for i in dropped):
        raise SystemExit(f"{path.name}: 의도 밖 스킬이 빠졌다 {dropped}")

    blob = json.dumps(data, ensure_ascii=False)
    stale = GEM_ID_PART in blob or "공명하는 방패" in blob.replace(NOTE, "")
    if not dry:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"removed": removed, "line_hits": len(hits), "stale": stale,
            "skills": len(data["skills"])}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    bad = False
    for d in (GAME_DIR, REPO_DIR):
        for fname in FILES:
            path = d / fname
            if not path.exists():
                raise SystemExit(f"없는 플래너: {path}")
            r = update(path, args.dry_run)
            log.info("%s / %s: 액티브 제거 %d · 줄 수정 %d · 최종 스킬 %d",
                     d.name, fname[:2], r["removed"], r["line_hits"], r["skills"])
            if r["stale"]:
                bad = True
                log.error("    '공명하는 방패' 흔적이 남았다")
    if bad:
        return 1
    log.info("완료%s", " (dry-run)" if args.dry_run else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
