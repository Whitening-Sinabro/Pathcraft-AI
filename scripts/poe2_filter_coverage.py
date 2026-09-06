"""제작자가 실제로 끼는 장비가 **그 장비를 끼는 구간에서** 우리 오버레이에 잡히는지 검사한다.

`poe2_filter_sweep.py` 는 "베이스 필터보다 조용해졌나"(회귀)를 본다. 그건 이 질문에 답하지 않는다.
룰이 아예 안 걸려도 회귀는 0 이다 — 조용해진 게 아니라 없는 것이라서.
실제로 두 번 당했다:
  1. 좁은 룰을 넓은 룰 뒤에 둬서 블록이 가려졌다(assert_no_shadowing 으로 막음).
  2. 드롭 16 장비를 액트1 밴드(지역 레벨 상한 20)에 넣어서 2막(지역 22)에서 꺼졌다.
     사용자가 인게임에서 잡아냈다. 스윕은 두 번 다 0 을 보고했다.

그래서 이 검사는 반대편에서 본다: **제작자 정본이 말하는 (베이스, 구간)** 조합마다
우리 블록이 이기는지 확인한다. 구간은 `inventory_slots[].level_interval` 이고,
그가 쓰는 표기는 전부 `[드롭 레벨, 100]` 이다 — 상한을 두지 않는다.

출처 우선순위(사용자 지시 2026-09-06): poe.ninja 실캐릭 > 라이브 방송 > 모발리틱스 가이드.
`--source` 로 어느 정본을 검사할지 고른다.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import poe2_filter_sweep as sweep  # noqa: E402

log = logging.getLogger("coverage")

REPO = pathlib.Path("D:/Pathcraft-AI")
GAME = pathlib.Path(os.path.expandvars(r"%USERPROFILE%\Documents\My Games\Path of Exile 2"))
# 그가 실제로 밟는 지역 레벨. WorldAreas 에서 뽑은 액트 경계다.
PROBE_LEVELS = (1, 5, 10, 12, 15, 16, 20, 22, 26, 28, 31, 33, 36, 40, 45, 48, 52, 54, 58, 62,
                # 65+ 는 마감 구간이다. 여기가 없으면 드롭 80 짜리(Cryptic Crown ·
                # Adherent Cuffs)가 **한 번도 평가되지 않고** 그냥 통과한다 —
                # 적대검증이 이 구멍으로 "35종 다 잡힌다"는 주장을 깼다.
                65, 70, 75, 80, 82)


# 모발리틱스 정본의 단계 순서. 파일 이름으로 정렬하면 ACT 1 / ACT 2 / ACT 34 / Interludes 가
# 우연히 맞지만 우연에 기대지 않는다.
STAGE_ORDER = ("ACT 1", "ACT 2", "ACT 34", "Interludes")


def creator_gear(src_dir: pathlib.Path) -> list[tuple[str, int, int, str]]:
    """(베이스, 시작 레벨, 끝 레벨, 출처) — **슬롯별 교체 시점까지**가 그 베이스의 수명이다.

    `level_interval` 을 그대로 쓰면 안 된다. 그의 표기는 전부 `[드롭 레벨, 100]` 이라
    1막 석궁(Tense, 드롭 4)이 62레벨에도 유효한 것으로 읽힌다. 실제로는 2막 파일에서
    광택 나는 석궁(16)으로 갈아탄다 — **단계가 파일에 들어 있고 구간에는 없다.**
    그래서 같은 슬롯의 다음 단계 시작 레벨을 이 베이스의 끝으로 삼는다.
    """
    stages: list[tuple[str, dict]] = []
    for key in STAGE_ORDER:
        for p in sorted(src_dir.glob(f"{key}*.build")):
            stages.append((p.name, json.loads(p.read_text(encoding="utf-8"))))
    if not stages:
        sys.exit(f"{src_dir}: 단계 파일을 못 찾았다 (기대 접두: {STAGE_ORDER})")
    # 이 파일 맨 위가 "poe.ninja 실캐릭이 1순위"라고 써놓고 정작 모발리틱스 단계 파일만
    # 읽고 있었다. 실캐릭에만 있는 6종(Ashen Staff · Hallowed Crown · Kalguuran Cuffs ·
    # Pelt Leggings · Solar Amulet · Grand Mana Flask)이 검사에서 통째로 빠졌다 —
    # **검사기가 검사 대상과 같은 가정(모발리틱스가 정본)을 공유**하고 있었던 것이다.
    live = sorted(src_dir.glob("LIVE*.build"))
    if not live:
        sys.exit(f"{src_dir}: 실캐릭 스냅샷(LIVE*.build)이 없다 — 1순위 출처가 빠진 채로 "
                 "통과시키지 않는다. scripts/track_poe2_character.py 로 받아라.")

    per_slot: dict[str, list[tuple[int, str, str]]] = {}
    for fname, data in stages:
        for slot in data.get("inventory_slots", []):
            name = (slot.get("additional_text") or "").split("\n")[0].strip()
            if not name:
                continue
            iv = slot.get("level_interval") or [1, 100]
            per_slot.setdefault(slot.get("inventory_id") or "?", []).append(
                (int(iv[0]), name, fname))

    out: list[tuple[str, int, int, str]] = []
    for entries in per_slot.values():
        for i, (start, name, fname) in enumerate(entries):
            nxt = next((s for s, n, _f in entries[i + 1:] if n != name and s > start), None)
            out.append((name, start, (nxt - 1) if nxt else 10 ** 6, fname))

    # 실캐릭 스냅샷으로 모발리틱스 창을 **교정한다**(사용자가 정한 출처 우선순위:
    # poe.ninja 실캐릭 > 라이브 방송 > 모발리틱스). 모발리틱스 후기 파일은 몸통·장화 슬롯이
    # 비어 있어서 Shaman Mantle 같은 게 `[28, ∞]` 로 읽혔는데, 실캐릭은 그 자리에
    # 다른 것을 끼고 있다. 그러면 그 시점에 교체된 것이므로 창을 거기서 끊는다.
    # 실캐릭 목록은 `.build` 가 아니라 ninja 사이드카에서 읽는다. 유니크 슬롯은
    # `unique_name` 만 담고 **베이스 타입을 안 담아서**(주얼은 아예 빠진다) 첫 줄만 읽으면
    # 4종이 새어 나간다 — 검사기가 그걸 그대로 읽으면 **검사 대상과 같은 사각을 공유해서**
    # 새로 넣은 룰을 검증하지 못한다.
    side = src_dir / "LIVE_ninja_items.json"
    if not side.exists():
        sys.exit(f"{side} 가 없다 — 1순위 출처 없이 통과시키지 않는다")
    payload = json.loads(side.read_text(encoding="utf-8"))
    live_level = int((payload.get("_meta") or {}).get("level") or 0)
    if not live_level:
        sys.exit(f"{side}: _meta.level 이 없다 — 실캐릭 시점을 모르면 창을 못 끊는다")
    live_names_all = [n for n in payload.get("bases") or [] if n]
    # 슬롯 귀속은 `.build` 쪽에만 있으므로 그대로 쓰되, 이름 대조는 사이드카로 한다.
    live_slot: dict[str, str] = {}
    for p in live:
        for slot in json.loads(p.read_text(encoding="utf-8")).get("inventory_slots", []):
            name = (slot.get("additional_text") or "").split("\n")[0].strip()
            if name:
                live_slot[slot.get("inventory_id") or "?"] = name

    # 슬롯 대조로는 부족하다 — 유니크 슬롯의 첫 줄이 비어 있어(베이스 타입 자리가 없다)
    # `live_slot` 에 BodyArmour1 이 안 들어온다. 그러면 Shaman Mantle 이 교체된 줄 모른다.
    # 실캐릭 스냅샷은 **장비 전체 목록**이므로, 거기 없으면 그 시점엔 안 쓰는 것이다.
    live_names = set(live_names_all)
    corrected: list[tuple[str, int, int, str]] = []
    for name, start, end, fname in out:
        # 실캐릭 시점 **이후에 시작**하는 장비는 실캐릭이 말해 줄 게 없다.
        # 이 조건이 없으면 드롭 80 짜리(Cryptic Crown)를 61 로 잘라 창이 통째로 사라진다.
        if start <= live_level and end > live_level and name not in live_names:
            end = live_level
        corrected.append((name, start, end, fname))

    known = {n for n, *_ in corrected}
    for name in live_names_all:
        if name not in known:
            known.add(name)
            corrected.append((name, 1, 10 ** 6, f"LIVE Lv{live_level}"))
    return corrected


def probe_levels(start: int, end: int) -> list[int]:
    """고정 격자 + **그 창 자신의 경계**. 격자만 쓰면 짧은 창이 통째로 안 밟힌다 —
    Iron Ring [1,7] · Stone Charm [8,11] 처럼 8종이 평가 0회로 조용히 통과했다."""
    hi = min(end, 10 ** 5)
    pts = {a for a in PROBE_LEVELS if start <= a <= hi}
    # `start + 1` 도 반드시 찍는다. 게이트(ilvl/소켓)가 시작 직후 한두 레벨만 막는 경우가
    # 격자에 안 걸린다 — 광택 나는 석궁이 ilvl 18 게이트 때문에 16~17 에서만 빠졌는데
    # 격자에 17 이 없어 내 검사기는 16 하나만 보고했다(외부 검증이 17 도 짚었다).
    pts.update({start, start + 1, hi if hi < 10 ** 5 else max(PROBE_LEVELS),
                (start + min(hi, 90)) // 2})
    return sorted(a for a in pts if start <= a <= hi)


def check(filters: list[tuple[str, pathlib.Path]], base_path: pathlib.Path,
          gear: list[tuple[str, int, int, str]]) -> list[str]:
    """**세 단계 필터를 함께** 본다.

    한때 캠페인 필터 하나만 놓고 지역 80 까지 검사했다. 캠페인 필터는 액트 구간에서만
    쓰는데 마감 레벨로 캐물으니 Cryptic Crown(드롭 80) 같은 게 '안 잡힌다'로 나왔다 —
    실제로는 그 레벨에서 쓰는 endgame 필터가 잡는다. 질문은 "이 베이스가 쓸모 있는 순간에
    **내가 그때 켜 둘 필터**가 띄우나" 이므로, 셋 중 하나라도 잡으면 통과다.
    """
    ev = sweep.load_eval()
    loaded = [(label, ev.load(p), {b.line for b in ev.parse(sweep.overlay_only(p))})
              for label, p in filters]
    classes = sweep.class_index(ev, ev.load(base_path))
    misses: list[str] = []
    seen: set[tuple[str, int]] = set()
    # 실제로 평가한 횟수를 센다. 한때 보고문이 `len(gear) * len(PROBE_LEVELS) * 3` 이라는
    # **곱셈 상한**을 찍었는데 중복제거·창 밖 스킵·플라스크 2등급이 반영 안 돼 4.1배 부풀었고,
    # 그 사이 평가 0회인 베이스 2종이 "잡힌다"에 묻어 통과했다.
    check.evaluated = 0
    check.never_probed = set()
    check.probed = set()
    for name, start, end, src in gear:
        before = check.evaluated
        for alvl in probe_levels(start, end):
            if (name, alvl) in seen:
                continue
            seen.add((name, alvl))
            # 플라스크·호신부는 POE2 에서 Rare 가 안 된다. 넣으면 검사기가 헛것을 세운다.
            # 클래스 이름을 하드코딩하면 낡는다 — 파생 DB 를 `Flasks` 에서
            # `Life Flasks`/`Mana Flasks` 로 쪼갠 순간 이 예외가 조용히 풀려 헛것 30건이 났다.
            # 그래서 이름이 아니라 **접미로** 판정한다.
            cls = classes.get(name, "")
            no_rare = cls == "Charms" or cls.endswith("Flasks")
            rarities = ("Normal", "Magic") if no_rare else ("Normal", "Magic", "Rare")
            for rarity in rarities:
                item = ev.Item(base_type=name, item_class=cls, rarity=rarity,
                               sockets=0, area_level=alvl, item_level=alvl, quality=0)
                check.evaluated += 1
                hit = None
                for label, blocks, ours in loaded:
                    r = ev.evaluate(blocks, item)
                    if r.block_line in ours:
                        hit = label
                        break
                if hit is None:
                    r = ev.evaluate(loaded[0][1], item)
                    misses.append(f"{name} · {rarity} · 지역 {alvl} → 세 단계 어디도 안 잡음 "
                                  f"(캠페인 L{r.block_line}, 폰트 {r.font}) [{src[:14]}]")
        if check.evaluated == before and name not in check.probed:
            check.never_probed.add(name)
        elif check.evaluated > before:
            check.probed.add(name)
            check.never_probed.discard(name)
    return misses


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=".tmp/seongbin",
                    help="정본 .build 폴더 (기본: 임성빈)")
    ap.add_argument("--spec", default=str(REPO / "data/filter_build_targets/poe2_hc_gemling_seongbin_0_5_5.json"),
                    help="_meta.outputs 를 읽어 세 단계를 한꺼번에 본다")
    ap.add_argument("--base", default=str(REPO / "data/filter_sources/neversink_poe2_soft.filter"))
    ap.add_argument("--quiet-limit", type=int, default=40)
    args = ap.parse_args()

    outputs = json.loads(pathlib.Path(args.spec).read_text(encoding="utf-8"))["_meta"]["outputs"]
    filters = [(o["stage"], REPO / "filters" / o["file"]) for o in outputs]
    missing = [str(p) for _s, p in filters if not p.exists()]
    if missing:
        sys.exit(f"빌드된 필터가 없다: {missing} — 먼저 build_poe2_build_overlay.py 를 돌려라")

    gear = creator_gear(pathlib.Path(args.source))
    misses = check(filters, pathlib.Path(args.base), gear)
    names = {g[0] for g in gear}
    miss_names = {m.split(" · ")[0] for m in misses}
    log.info("정본 장비 %d종 · **실제 평가 %d회**", len(names), check.evaluated)
    if check.never_probed:
        log.info("⚠ 한 번도 평가 못 한 베이스 %d종: %s — PROBE_LEVELS 가 이 구간을 안 밟는다",
                 len(check.never_probed), sorted(check.never_probed))
    log.info("우리 오버레이가 못 잡는 조합 %d개 · 베이스 %d종", len(misses), len(miss_names))
    for m in misses[:args.quiet_limit]:
        log.info("   x %s", m)
    if len(misses) > args.quiet_limit:
        log.info("   … 그 외 %d개", len(misses) - args.quiet_limit)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
