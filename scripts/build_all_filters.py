"""필터 스펙에서 `filters/` 전체를 재생성한다.

`filters/` 는 gitignore 산출물이고 정본은 `data/filter_build_targets/*.json` 이다.
스펙의 `_meta.outputs` 에 단계·출력 파일명·베이스가 이미 다 적혀 있는데
`build_poe2_build_overlay.py` 는 `--base` / `--out` 을 손으로 받는다. 그래서
베이스 경로를 틀리기 쉽다 — 실제로 `filters/` 와 `data/filter_sources/` 를
헷갈려 세 번 실패한 적이 있다. 이 스크립트가 그 연결을 대신한다.

    python scripts/build_all_filters.py                 # 전부
    python scripts/build_all_filters.py --spec poe2_infinite_ignite_arserina_0_5_5
    python scripts/build_all_filters.py --check         # 재생성 없이 상태만
    python scripts/build_all_filters.py --install       # 게임 폴더까지 설치

`--install` 은 덮어쓰기 전에 기존 파일을 `.bak-<날짜시각>` 으로 남긴다.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO / "data" / "filter_build_targets"
BASE_DIR = REPO / "data" / "filter_sources"
OUT_DIR = REPO / "filters"
BUILDER = REPO / "scripts" / "build_poe2_build_overlay.py"
GAME_DIR = Path.home() / "Documents" / "My Games" / "Path of Exile 2"


def specs(selector: str | None) -> list[Path]:
    """`_meta.outputs` 를 선언한 스펙만 고른다 — 그게 이 파이프라인의 대상이다."""
    out = []
    for path in sorted(SPEC_DIR.glob("*.json")):
        if selector and selector not in path.stem:
            continue
        try:
            meta = json.loads(path.read_text(encoding="utf-8")).get("_meta", {})
        except json.JSONDecodeError as e:
            print(f"  [건너뜀] {path.name} — JSON 파싱 실패: {e}")
            continue
        if meta.get("outputs"):
            out.append(path)
    return out


def plan(spec_path: Path) -> list[dict]:
    meta = json.loads(spec_path.read_text(encoding="utf-8"))["_meta"]
    rows = []
    for o in meta["outputs"]:
        rows.append({
            "stage": o["stage"],
            "base": BASE_DIR / o["base"],
            "out": OUT_DIR / o["file"],
        })
    return rows


def build(spec_path: Path, row: dict, verbose: bool) -> tuple[bool, str]:
    cmd = [sys.executable, str(BUILDER),
           "--spec", str(spec_path),
           "--base", str(row["base"]),
           "--out", str(row["out"]),
           "--stage", row["stage"]]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = [ln for ln in (r.stderr or "").splitlines() if "wrote" in ln or "ERROR" in ln]
    if verbose:
        print((r.stderr or "").rstrip())
    return r.returncode == 0, (tail[-1] if tail else (r.stderr or "").strip()[:200])


def install(out_path: Path, stamp: str) -> str:
    if not GAME_DIR.is_dir():
        return "게임 폴더 없음"
    dest = GAME_DIR / out_path.name
    note = ""
    if dest.exists():
        shutil.copy2(dest, GAME_DIR / f"{out_path.name}.bak-{stamp}")
        note = " (기존본 백업)"
    shutil.copy2(out_path, dest)
    return f"설치{note}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", help="스펙 파일명 일부 (생략하면 전부)")
    ap.add_argument("--check", action="store_true", help="재생성하지 않고 상태만 본다")
    ap.add_argument("--install", action="store_true", help="게임 폴더에도 복사")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    targets = specs(args.spec)
    if not targets:
        print("대상 스펙이 없다 (`_meta.outputs` 선언한 것만 처리한다)")
        return 1

    missing_base = [b for s in targets for b in (r["base"] for r in plan(s)) if not b.exists()]
    if missing_base and not args.check:
        print("NeverSink 베이스가 없다. 먼저 받아라:")
        print("  python scripts/fetch_neversink_poe2_bases.py")
        for b in sorted(set(missing_base)):
            print(f"  없음: {b}")
        return 1

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    failed = 0
    produced: set[Path] = set()
    for spec_path in targets:
        print(f"\n[{spec_path.stem}]")
        for row in plan(spec_path):
            produced.add(row["out"])
            if args.check:
                state = "있음" if row["out"].exists() else "없음"
                size = f"{row['out'].stat().st_size/1024:,.1f}KB" if row["out"].exists() else "-"
                print(f"  {row['stage']:<9} {row['out'].name:<52} {state} {size}")
                continue
            ok, msg = build(spec_path, row, args.verbose)
            mark = "OK  " if ok else "실패"
            extra = f" · {install(row['out'], stamp)}" if (ok and args.install) else ""
            print(f"  {mark} {row['stage']:<9} {row['out'].name}{extra}")
            if not ok:
                failed += 1
                print(f"       {msg}")

    if OUT_DIR.is_dir():
        orphans = sorted(p for p in OUT_DIR.glob("*.filter") if p not in produced)
        if orphans:
            print(f"\n스펙에서 안 나오는 파일 {len(orphans)}개 (POE1 등 다른 파이프라인일 수 있다):")
            for p in orphans:
                print(f"  {p.name}  {p.stat().st_size/1024:,.1f}KB")

    print(f"\n{'검사만 했다' if args.check else f'실패 {failed}건'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
