"""워브링어 단계 플래너 05·06·07 의 순수함 표기를 상황 의존으로 되돌린다.

왜: 순수함은 PoB 정의에서 `fromItem = true` 다. 성소 셉터가 주는 오라이고,
불·얼음·번개는 같은 스킬의 원소 차이일 뿐이다(각각 그 저항만 올린다).
따라서 "불의 순수함" 이나 "번개의 순수함" 을 목표로 적으면 특정 셉터를
들고 있던 한 시점의 스냅샷을 규칙으로 굳히는 것이 된다.

제작자 88레벨 공개 스냅샷은 양 세트 모두 번개였고, 그때 초과 저항이
번개 37 · 냉기 27 · 화염 13 이었다. 그건 그의 장비 사정이지 빌드 규칙이 아니다.

무엇을 안 건드리나: 트리·젬 구조 전부(텍스트 외의 모든 필드를 지문으로 비교한다).
본문은 문서 전체를 순회해서 고친다 — `.build` 는 자유 텍스트를 최상위 description,
장비 슬롯, 젬, 젬 안의 support_skills 네 깊이에 흩어 둔다.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys

log = logging.getLogger("purity")

GAME_DIR = pathlib.Path(os.path.expandvars(
    r"%USERPROFILE%\Documents\My Games\Path of Exile 2\BuildPlanner"))
REPO_DIR = pathlib.Path("deliverables/skadoosh_early_survival_2026-09-08/BuildPlanner")
FILES = [
    "05 전사 토템 - 혈마법 전환.build",
    "06 파콰테 - 두 함성 운영.build",
    "07 지도 성장 - 후기 목표.build",
]

OPTION_LINE = ("2. 순수함 오라를 부여하는 성소 셉터. 불·얼음·번개 중 무엇이 붙는지는 "
               "셉터가 정하므로 지금 모자란 저항으로 고른다.")

# 줄 단위 완전 일치로 먼저 바꾼다.
LINE_FIXES: list[tuple[str, str]] = [
    ("2. 불의 순수함을 부여하는 성소 셉터", OPTION_LINE),
    ("2. 번개의 순수함을 부여하는 성소 셉터", OPTION_LINE),
    ("순수함은 불이 아니라 번개다.",
     "순수함의 원소는 셉터가 정한다. 88레벨 스냅샷은 양 세트 모두 번개였고 "
     "그때 초과 저항이 번개 37·냉기 27·화염 13이었다."),
]

# 그다음 남은 원소 이름만 떼어 낸다. 치환문이 원문을 포함하지 않아 재실행에 안전하다.
TOKEN_FIXES = [("불의 순수함", "순수함"), ("번개의 순수함", "순수함"), ("얼음의 순수함", "순수함")]


def fix(text: str, counts: dict[str, int]) -> str:
    out = []
    for line in text.split("\n"):
        for old, new in LINE_FIXES:
            if line.strip() == old:
                line = line.replace(old, new)
                counts[old] = counts.get(old, 0) + 1
                break
        out.append(line)
    joined = "\n".join(out)
    for old, new in TOKEN_FIXES:
        if old in joined:
            counts[old] = counts.get(old, 0) + joined.count(old)
            joined = joined.replace(old, new)
    return joined


TEXT_KEYS = ("description", "additional_text")


def carriers(node):
    """`.build` 는 자유 텍스트를 여러 깊이에 흩어 둔다 — 최상위 description,
    장비 슬롯, 젬, 그리고 젬 안의 support_skills. 경로를 열거하면 반드시 하나를
    빠뜨린다(실제로 두 번 빠뜨렸다). 그래서 통째로 순회한다."""
    if isinstance(node, dict):
        for key in TEXT_KEYS:
            if isinstance(node.get(key), str) and node[key]:
                yield node, key
        for value in node.values():
            yield from carriers(value)
    elif isinstance(node, list):
        for value in node:
            yield from carriers(value)


def skeleton(data) -> str:
    """문구만 고쳤는지 보는 지문 — 텍스트를 뺀 나머지 구조 전부."""
    def strip(node):
        if isinstance(node, dict):
            return {k: strip(v) for k, v in sorted(node.items()) if k not in TEXT_KEYS}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node
    return json.dumps(strip(data), ensure_ascii=False, sort_keys=True)


def update(path: pathlib.Path, dry: bool) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    frozen = skeleton(data)
    counts: dict[str, int] = {}
    for holder, key in list(carriers(data)):
        if holder.get(key):
            holder[key] = fix(holder[key], counts)
    if skeleton(data) != frozen:
        raise SystemExit(f"{path.name}: 트리나 젬이 바뀌었다 — 문구만 고쳐야 한다")
    if not dry:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    blob = json.dumps(data, ensure_ascii=False)
    stale = [old for old, _ in TOKEN_FIXES if old in blob]
    return {"counts": counts, "stale": stale}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
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
            total = sum(r["counts"].values())
            log.info("%s / %s: %d곳", d.name, fname[:2], total)
            for k, n in sorted(r["counts"].items()):
                log.info("    %s (%d)", k[:50], n)
            if r["stale"]:
                bad = True
                log.error("    원소 표기가 남았다: %s", r["stale"])
    if bad:
        return 1
    log.info("완료%s", " (dry-run)" if args.dry_run else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
