"""Compare a build overlay against its NeverSink base, drop by drop.

The overlay is prepended, so first-match-wins means every block it emits *replaces*
what NeverSink would have said. This sweeps fully specified item states through
both filters with `poe2_filter_eval` and reports where the overlay made things
worse — quieter, or hidden.

Why this is a repo script and not a throwaway: the scratchpad version scraped its
base-name list from the *whole output file*, which includes NeverSink's own 1,364
BaseType tokens, so it swept 22x more states than the build actually names and
took 4-5 minutes per stage. An agent told to prove "0 regressions across three
stages" then spent most of an hour on it. The overlay's own rules are the correct
scope, and that runs in seconds.

Three kinds of difference are reported separately, because lumping them together
hides the one that matters:

  REAL          the base showed it louder, and the block that did so was specific
                (named the BaseType or a Class). This is a regression.
  catch-all     the base only matched it via its "unknown item" fallback. Our
                overlay recognising the item is an improvement, not a downgrade.
  silent-base   the base block had no sound and ours does. We are louder where it
                counts and slightly smaller in font; not a regression.

Usage:
    python scripts/poe2_filter_sweep.py <base.filter> <overlay.filter> [--verbose]
    python scripts/poe2_filter_sweep.py --spec data/filter_build_targets/<spec>.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# 이 스크립트는 게이트다. 윈도 콘솔 기본 코덱(cp949)이 보고문의 기호를
# 못 찍는다고 도중에 죽으면, 통과도 실패도 아닌 상태로 끝나 결함을 놓친다.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[1]
NEVERSINK_HEADER = "NeverSink's Indepth Loot Filter"

RARITIES = ("Normal", "Magic", "Rare", "Unique")
AREA_LEVELS = (10, 35, 60, 70, 80)
SOCKETS = (0, 2)
# NeverSink 의 chancing/over-quality 티어는 Quality >= 24 에서 켜진다. 20 까지만
# 훑으면 그 구간 회귀가 그리드에 아예 안 잡힌다 — 실제로 점화 필터에서 이 차원
# 에서만 드러난 회귀가 있었다(고퀄 노멀 호신부·장갑).
QUALITIES = (0, 20, 28)

def _class_map() -> dict[str, str]:
    """GGPK 클래스 -> 필터 클래스 매핑은 **빌더가 정본**이다. 사본을 두지 않는다.

    한때 이 파일이 자기 사본을 들고 있었고, 빌더에 `CasterStaves` 를 추가했을 때 여기만
    낡았다. 그 결과 시뮬레이터가 Chiming/Ashen/Spriggan Staff 의 클래스를 `None` 으로 보고
    `Class == "Staves"` 조건을 못 맞춰, **우리 지팡이 룰이 없는 것처럼** 보고했다.
    게임은 멀쩡히 잡는데 검사기만 눈이 먼 것이라 더 나쁘다 — 통과도 실패도 아닌 거짓 결함이다.
    """
    spec = importlib.util.spec_from_file_location(
        "overlay_builder", REPO / "scripts" / "build_poe2_build_overlay.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["overlay_builder"] = mod
    spec.loader.exec_module(mod)
    return dict(mod.GAME_CLASS_TO_FILTER_CLASS)


GAME_CLASS_TO_FILTER_CLASS = _class_map()


def load_eval():
    spec = importlib.util.spec_from_file_location("ev", REPO / "scripts" / "poe2_filter_eval.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ev"] = mod
    spec.loader.exec_module(mod)
    return mod


def overlay_only(path: Path) -> str:
    """Just our blocks -- the base's own BaseType tokens are not our scope."""
    text = path.read_text(encoding="utf-8")
    cut = text.find(NEVERSINK_HEADER)
    return text[:cut] if cut > 0 else text


def class_index(ev, base_blocks) -> dict[str, str]:
    index: dict[str, str] = {}
    for b in base_blocks:
        classes = [v for k, _o, v in b.conditions if k == "Class"]
        bases = [v for k, _o, v in b.conditions if k == "BaseType"]
        if len(classes) == 1 and len(classes[0]) == 1 and bases:
            for name in bases[0]:
                index.setdefault(name, classes[0][0])
    items = REPO / "data" / "base_items_poe2.json"
    if items.exists():
        data = json.loads(items.read_text(encoding="utf-8"))
        for group in ("weapons", "armours", "other"):
            for game_class, entries in data.get(group, {}).items():
                filter_class = GAME_CLASS_TO_FILTER_CLASS.get(game_class)
                if filter_class and isinstance(entries, list):
                    for e in entries:
                        if isinstance(e, dict) and e.get("name"):
                            index.setdefault(e["name"], filter_class)
    return index


def sweep(base_path: Path, overlay_path: Path, verbose: bool) -> int:
    ev = load_eval()
    base_blocks = ev.load(base_path)
    over_blocks = ev.load(overlay_path)
    ours = ev.parse(overlay_only(overlay_path))

    classes = class_index(ev, base_blocks)
    names = sorted({n for b in ours for k, _o, v in b.conditions if k == "BaseType" for n in v})
    # BaseType 없이 Class 만 거는 블록(우리 숨김 룰이 그렇다)의 대상은 이 목록에 안 들어와서
    # **한 번도 안 훑였다**. 그래서 그 블록이 무엇을 숨기든 스윕은 0 을 보고했다.
    # 클래스만 거는 블록의 대상 베이스를 파생 DB 에서 채워 넣는다.
    class_only = {c for b in ours
                  if not any(k == "BaseType" for k, _o, _v in b.conditions)
                  for k, _o, v in b.conditions if k == "Class" for c in v}
    hidden_classes = {c for b in ours if b.action == "Hide"
                      for k, _o, v in b.conditions if k == "Class" for c in v}
    if class_only:
        names = sorted(set(names) | {n for n, c in classes.items() if c in class_only})
    if not names:
        print(f"  {overlay_path.name}: 오버레이가 지정한 BaseType 이 없다 — 스윕할 것이 없음")
        return 1
    by_line = {b.line: b for b in base_blocks}

    counts = {"louder": 0, "same": 0, "real": 0, "catchall": 0, "silent": 0,
              "hidden": 0, "declared_hidden": 0, "unhidden": 0, "total": 0}
    our_lines = {b.line for b in ours}
    regressions: list[str] = []

    for name in names:
        for rarity in RARITIES:
            for area in AREA_LEVELS:
                for sockets in SOCKETS:
                    for quality in QUALITIES:
                        item = ev.Item(
                            base_type=name, item_class=classes.get(name, ""),
                            rarity=rarity, sockets=sockets, area_level=area,
                            item_level=area, quality=quality,
                        )
                        b = ev.evaluate(base_blocks, item)
                        o = ev.evaluate(over_blocks, item)
                        counts["total"] += 1
                        if b.visible and not o.visible:
                            # 스펙이 **선언한** 숨김(못 쓰는 무기·보조장비)과 사고를 가른다.
                            # 둘을 합쳐 세면 "HIDDEN 0" 이 의도된 숨김을 지우거나,
                            # 반대로 의도된 숨김이 실수를 덮는다.
                            declared = (o.block_line in our_lines
                                        and classes.get(name, "") in hidden_classes)
                            if declared:
                                counts["declared_hidden"] += 1
                            else:
                                counts["hidden"] += 1
                                regressions.append(f"HIDDEN {name} {rarity} alvl{area}")
                            continue
                        if not b.visible:
                            counts["unhidden"] += o.visible
                            continue
                        if (o.font, o.volume) > (b.font, b.volume):
                            counts["louder"] += 1
                        elif (o.font, o.volume) == (b.font, b.volume):
                            counts["same"] += 1
                        else:
                            blk = by_line.get(b.block_line)
                            named = blk and any(k in ("BaseType", "Class") for k, _o, _v in blk.conditions)
                            if not named:
                                counts["catchall"] += 1
                            elif b.volume == 0 and o.volume > 0:
                                counts["silent"] += 1
                            else:
                                counts["real"] += 1
                                regressions.append(
                                    f"{name} {rarity} alvl{area} sock{sockets} q{quality}: "
                                    f"base f{b.font}/v{b.volume}(L{b.block_line}) -> "
                                    f"overlay f{o.font}/v{o.volume}(L{o.block_line})"
                                )

    print(f"\n  {overlay_path.name}")
    print(f"    베이스 {len(names)}종 · 상태 {counts['total']:,}")
    print(f"    louder {counts['louder']} · same {counts['same']} · "
          f"un-hidden {counts['unhidden']}")
    print(f"    REAL 회귀 {counts['real']} · HIDDEN {counts['hidden']} "
          f"| 폴백 대체 {counts['catchall']} · 무음에 소리 추가 {counts['silent']} "
          f"· 선언된 숨김 {counts['declared_hidden']}")
    if verbose:
        seen = set()
        for r in regressions:
            head = r.split(":")[0]
            if head in seen:
                continue
            seen.add(head)
            print(f"      ✗ {r}")
    return counts["real"] + counts["hidden"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", nargs="?")
    ap.add_argument("overlay", nargs="?")
    ap.add_argument("--spec", help="_meta.outputs 를 읽어 3단계를 한 번에 검사")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    pairs: list[tuple[Path, Path]] = []
    if args.spec:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        for out in spec["_meta"]["outputs"]:
            pairs.append((REPO / "data" / "filter_sources" / out["base"],
                          REPO / "filters" / out["file"]))
    elif args.base and args.overlay:
        pairs.append((Path(args.base), Path(args.overlay)))
    else:
        ap.error("base 와 overlay 를 주거나 --spec 을 주십시오")

    bad = 0
    for base, overlay in pairs:
        if not base.exists() or not overlay.exists():
            print(f"  건너뜀: {overlay.name} (파일 없음)")
            continue
        bad += sweep(base, overlay, args.verbose)
    print(f"\n  회귀 총 {bad}건")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
