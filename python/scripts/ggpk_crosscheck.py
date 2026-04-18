"""Layer 2 — 독립 추출기 cross-check.

우리 Rust `extract_data` 결과 vs SnosMe `pathofexile-dat` (npm) 결과 비교.
두 독립 구현이 동일 결과 → 추출 파이프라인 신뢰 확보.

사전 조건:
    npm install -g pathofexile-dat     (v15.1.0 이상, MIT, SnosMe)
    # 최신 patch 버전은 poe-tool-dev/latest-patch-version/main/latest.txt

실행:
    cd _analysis/crosscheck
    node "$(npm root -g)/pathofexile-dat/dist/cli/run.js"
    # → _analysis/crosscheck/tables/English/*.json 생성

    python python/scripts/ggpk_crosscheck.py
    # → _analysis/crosscheck/report.json + 콘솔 출력

config.json은 리포에 커밋되지만 tables/와 .cache/는 gitignore.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OURS_DIR = ROOT / "data" / "game_data"
THEIRS_DIR = ROOT / "_analysis" / "crosscheck" / "tables" / "English"
REPORT_PATH = ROOT / "_analysis" / "crosscheck" / "report.json"


# 비교 방식: 테이블별로 rows와 안정 식별 필드(Id/Name/Attr 등) 집합 일치 확인.
# None이면 rows만 비교.
COMPARE_FIELDS: dict[str, tuple[str, ...] | None] = {
    "Characters":   ("Attr",),
    "Ascendancy":   ("Id",),
    "Tags":         ("Id",),
    "Scarabs":      None,         # Type 필드 비교는 row index 의존 -- rows만
    "ScarabTypes":  ("Id",),
    "Flasks":       None,         # Name 없이 구조만 비교
    "GemTags":      ("Id",),
}


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_table(table: str, fields: tuple[str, ...] | None) -> dict:
    ours_path = OURS_DIR / f"{table}.json"
    theirs_path = THEIRS_DIR / f"{table}.json"
    result = {
        "table": table,
        "ours_path": str(ours_path.relative_to(ROOT)),
        "theirs_path": str(theirs_path.relative_to(ROOT)),
    }
    if not ours_path.exists():
        return {**result, "status": "error", "reason": "ours missing"}
    if not theirs_path.exists():
        return {**result, "status": "error", "reason": "theirs missing"}

    ours = load(ours_path)
    theirs = load(theirs_path)
    result["rows_ours"] = len(ours)
    result["rows_theirs"] = len(theirs)

    if len(ours) != len(theirs):
        return {**result, "status": "mismatch", "reason": f"row count diff ({len(ours)} vs {len(theirs)})"}

    if fields is None:
        return {**result, "status": "ok_rows_only", "reason": "rows match, no field comparison"}

    missing_fields = []
    for f in fields:
        if ours and f not in ours[0]:
            missing_fields.append(f"ours missing field {f!r}")
        if theirs and f not in theirs[0]:
            missing_fields.append(f"theirs missing field {f!r}")
    if missing_fields:
        return {**result, "status": "schema_diff", "reason": "; ".join(missing_fields)}

    a_set = {tuple(row.get(f) for f in fields) for row in ours}
    b_set = {tuple(row.get(f) for f in fields) for row in theirs}
    only_ours = a_set - b_set
    only_theirs = b_set - a_set
    if not only_ours and not only_theirs:
        return {**result, "status": "ok", "compared_fields": list(fields)}
    return {
        **result,
        "status": "content_diff",
        "compared_fields": list(fields),
        "only_ours": [list(t) for t in sorted(only_ours)[:10]],
        "only_theirs": [list(t) for t in sorted(only_theirs)[:10]],
    }


def main() -> int:
    if not THEIRS_DIR.exists():
        print(f"[skip] {THEIRS_DIR.relative_to(ROOT)} 없음 -- pathofexile-dat 먼저 실행")
        return 2

    rows = []
    for table, fields in COMPARE_FIELDS.items():
        rows.append(compare_table(table, fields))

    summary = {
        "total": len(rows),
        "ok": sum(1 for r in rows if r["status"] == "ok"),
        "ok_rows_only": sum(1 for r in rows if r["status"] == "ok_rows_only"),
        "mismatch": sum(1 for r in rows if r["status"] in ("mismatch", "content_diff", "schema_diff")),
        "error": sum(1 for r in rows if r["status"] == "error"),
    }
    REPORT_PATH.write_text(
        json.dumps({"summary": summary, "tables": rows}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{'table':<14} {'ours':>6} {'theirs':>7} {'status':<14} {'reason'}")
    print("-" * 70)
    for r in rows:
        reason = r.get("reason", "") if r["status"] != "ok" else ""
        print(f"{r['table']:<14} {r.get('rows_ours', '?'):>6} {r.get('rows_theirs', '?'):>7} {r['status']:<14} {reason}")
    print(f"\nsummary: {summary}")
    print(f"report: {REPORT_PATH.relative_to(ROOT)}")

    return 0 if summary["mismatch"] == 0 and summary["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
