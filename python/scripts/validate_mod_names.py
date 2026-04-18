"""F0-fix-3 — 필터 mod-tier JSON의 mod 이름이 GGPK Mods.Name과 일치하는지 검증.

대상:
- data/defense_mod_tiers.json (NeverSink 방어 5 slots × {life, es})
- data/accessory_mod_tiers.json (NeverSink 악세 3 slots × axes)
- data/weapon_mod_tiers.json (NeverSink 무기 mod 리스트)

검증:
- `HasExplicitMod "X"`는 Mods.Name 정확 매칭. 타이포/누락/trailing space 감지.
- 매칭된 mod의 Domain/Level 샘플 표기 — 필터가 의도한 티어와 실제 일치 여부 스팟체크 근거.

실행:
    python python/scripts/validate_mod_names.py
    # → _analysis/mod_name_validation_report.json + 콘솔 요약
    # exit 0: 모두 매칭 / exit 1: 누락 발견

사전 조건:
    data/game_data/Mods.json (cargo run --bin extract_data -- --json)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MODS_PATH = DATA_DIR / "game_data" / "Mods.json"
REPORT_PATH = ROOT / "_analysis" / "mod_name_validation_report.json"


def collect_defense_mods(d: dict) -> set[str]:
    """defense_mod_tiers: slots[slot][axis][bucket] = list[str]."""
    names: set[str] = set()
    for slot, axes in d.get("slots", {}).items():
        for axis, buckets in axes.items():
            if not isinstance(buckets, dict):
                continue
            for bucket, values in buckets.items():
                if isinstance(values, list):
                    for v in values:
                        if isinstance(v, str):
                            names.add(v)
    return names


def collect_accessory_mods(d: dict) -> set[str]:
    """accessory_mod_tiers: 동일 구조."""
    return collect_defense_mods(d)


def collect_weapon_mods(d: dict) -> set[str]:
    """weapon_mod_tiers: top-level required_any_mod / counted_good_mods / excluded_bad_mods."""
    names: set[str] = set()
    for k in ("required_any_mod", "counted_good_mods", "excluded_bad_mods"):
        for v in d.get(k, []):
            if isinstance(v, str):
                names.add(v)
    return names


def build_mods_index(mods: list[dict]) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = defaultdict(list)
    for m in mods:
        n = m.get("Name", "")
        if n:
            idx[n].append(m)
    return idx


def classify(name: str, mods_idx: dict[str, list[dict]]) -> dict:
    """각 이름을 exact / substring / missing으로 분류.

    POE 필터 `HasExplicitMod "X"`는 기본적으로 substring 매칭 (== 오퍼레이터 없을 때).
    예: "Veil"은 "Veiled", "Veiling Tempest", "Catarina's Veiled" 전부 매치.
    trailing space("Elevated ")는 prefix 의도 — "Elevated Shaper's" 등.
    """
    entry: dict = {"name": name}
    # 1) exact match
    if name in mods_idx:
        rows = mods_idx[name]
        entry["status"] = "exact"
        entry["match_count"] = len(rows)
        entry["domains"] = sorted({m.get("Domain") for m in rows})
        return entry

    # 2) substring match — 어떤 Mods.Name이 'name' 포함
    substring_hits = [k for k in mods_idx.keys() if name in k]
    if substring_hits:
        # 총 행 수도 합산
        total_rows = sum(len(mods_idx[k]) for k in substring_hits)
        entry["status"] = "substring"
        entry["substring_match_count"] = total_rows
        entry["substring_sample"] = substring_hits[:5]
        if name != name.strip():
            entry["note"] = "trailing/leading whitespace → prefix 의도"
        return entry

    # 3) missing — 근접 힌트
    entry["status"] = "missing"
    stripped = name.strip()
    if stripped != name:
        candidates = [k for k in mods_idx.keys() if stripped in k][:5]
    else:
        # fuzzy: 첫 2 단어 매칭
        head = stripped.split()[0] if stripped.split() else stripped
        candidates = [k for k in mods_idx.keys() if head in k][:5]
    if candidates:
        entry["fuzzy_candidates"] = candidates
    return entry


def validate_file(label: str, path: Path, collector, mods_idx) -> dict:
    if not path.exists():
        return {"label": label, "status": "missing_file", "path": str(path.relative_to(ROOT))}
    doc = json.loads(path.read_text(encoding="utf-8"))
    names = collector(doc)
    entries = [classify(n, mods_idx) for n in sorted(names)]
    exact = sum(1 for e in entries if e["status"] == "exact")
    substring = sum(1 for e in entries if e["status"] == "substring")
    missing = sum(1 for e in entries if e["status"] == "missing")
    return {
        "label": label,
        "path": str(path.relative_to(ROOT)),
        "total_names": len(names),
        "exact": exact,
        "substring": substring,
        "missing": missing,
        "entries": entries,
    }


def main() -> int:
    if not MODS_PATH.exists():
        print(f"[error] {MODS_PATH.relative_to(ROOT)} 없음. cargo run --bin extract_data -- --json 먼저.")
        return 2

    mods = json.loads(MODS_PATH.read_text(encoding="utf-8"))
    mods_idx = build_mods_index(mods)
    print(f"[info] Mods.json {len(mods)} rows, {len(mods_idx)} distinct Names")

    targets = [
        ("defense",   DATA_DIR / "defense_mod_tiers.json",   collect_defense_mods),
        ("accessory", DATA_DIR / "accessory_mod_tiers.json", collect_accessory_mods),
        ("weapon",    DATA_DIR / "weapon_mod_tiers.json",    collect_weapon_mods),
    ]
    reports = [validate_file(lbl, p, coll, mods_idx) for lbl, p, coll in targets]
    overall = {
        "mods_total": len(mods),
        "distinct_names": len(mods_idx),
        "files": reports,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(overall, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\n{'label':<10} {'total':>6} {'exact':>6} {'subst':>6} {'miss':>5}")
    print("-" * 45)
    total_miss = 0
    for r in reports:
        print(f"{r['label']:<10} {r.get('total_names', '?'):>6} {r.get('exact', '?'):>6} {r.get('substring', '?'):>6} {r.get('missing', '?'):>5}")
        total_miss += r.get("missing", 0)

    # 상세: missing + substring(정보 제공)
    print("\n=== substring (prefix/wildcard 의도) ===")
    for r in reports:
        subs = [e for e in r.get("entries", []) if e["status"] == "substring"]
        if not subs:
            continue
        print(f"\n[{r['label']}]")
        for e in subs:
            note = f" ({e.get('note', '')})" if e.get("note") else ""
            print(f"  {e['name']!r:20s} → {e['substring_match_count']:4d} rows via {e['substring_sample']}{note}")

    print("\n=== missing (조사 대상) ===")
    any_missing = False
    for r in reports:
        miss = [e for e in r.get("entries", []) if e["status"] == "missing"]
        if not miss:
            continue
        any_missing = True
        print(f"\n[{r['label']}]")
        for e in miss:
            hints = f" fuzzy={e['fuzzy_candidates']}" if "fuzzy_candidates" in e else ""
            print(f"  {e['name']!r:40s}{hints}")
    if not any_missing:
        print("  (없음)")

    print(f"\nreport: {REPORT_PATH.relative_to(ROOT)}")
    return 0 if total_miss == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
