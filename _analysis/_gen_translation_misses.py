"""One-shot: generate _analysis/passive_tree_translation_misses.md

Reads tree data + poe_translations.json, produces classified miss report.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

ROOT = Path(__file__).resolve().parent.parent
NUMERIC = re.compile(r"[+-]?\d+(?:\.\d+)?")


def normalize(s: str) -> str:
    counter = 0

    def sub(_m: re.Match[str]) -> str:
        nonlocal counter
        t = f"{{{counter}}}"
        counter += 1
        return t

    return NUMERIC.sub(sub, s)


def main() -> None:
    tree = json.loads((ROOT / "data/skilltree-export/data.json").read_text("utf-8"))
    tr = json.loads((ROOT / "data/poe_translations.json").read_text("utf-8"))
    mods = tr["mods"]

    seen: set[str] = set()
    misses: list[str] = []
    for n in tree["nodes"].values():
        if not isinstance(n, dict):
            continue
        for s in n.get("stats") or []:
            if s in seen:
                continue
            seen.add(s)
            if s in mods or normalize(s) in mods:
                continue
            misses.append(s)

    misses.sort()
    cats: dict[str, list[str]] = {"multiline": [], "trigger": [], "other": []}
    for m in misses:
        if "\n" in m:
            cats["multiline"].append(m)
        elif re.search(r"Trigger Level \d+", m):
            cats["trigger"].append(m)
        else:
            cats["other"].append(m)

    out: list[str] = []
    out.append("# Passive Tree 번역 미스 분석\n")
    out.append(f"총 고유 stat: 2559 | 매칭: 2352 | 미스: **{len(misses)}** ({len(misses) / 2559 * 100:.1f}%)\n")
    out.append("생성 스크립트: `_analysis/_gen_translation_misses.py` (일회성)\n")

    out.append("## 분류\n")
    out.append("| 패턴 | 건수 | 설명 |")
    out.append("|------|------|------|")
    out.append(
        f"| 멀티라인 (`\\n` 포함) | {len(cats['multiline'])} | "
        f"공식 데이터에 개행이 있음. mods 사전 개행 규칙과 불일치. 공백 치환해도 82 중 2건만 복구. |"
    )
    out.append(
        f"| Trigger Level 고정 | {len(cats['trigger'])} | "
        f'"Trigger Level 20 ..." 형태 — mods에 level 추상화 없음 |'
    )
    out.append(
        f"| 기타 | {len(cats['other'])} | "
        f"mods 사전 자체 누락 추정 (POE 업데이트로 추가된 신규 stat) |\n"
    )

    out.append("## 개선 옵션\n")
    out.append(
        "1. **mods 사전 업데이트** (근본 해결) — `poe_translations.json`을 최신 소스에서 "
        "재수집. 프로젝트 범위 외, 별도 작업 필요."
    )
    out.append(
        "2. **문장 유사도 매칭** — 현재 exact match만. 미스 하나당 `difflib` 또는 임베딩으로 "
        "최근접 mods 키 찾기. ROI 불확실 (false match 위험)."
    )
    out.append(
        "3. **수동 사전 오버레이** — `data/skilltree-export/passive_tree_overlay.json`에 "
        "미스된 stat만 직접 한국어 작성. 207건 번역 가능하나 유지보수 부담."
    )
    out.append("")
    out.append(
        "**현재 권고: 보류.** 91.9% 커버는 실용적 임계. 인게임 검증에서 구체적 pain이 "
        "나오면 그때 3번 오버레이 도입 재검토.\n"
    )

    out.append("## 샘플\n")
    for cat, items in cats.items():
        out.append(f"### {cat} ({len(items)})\n")
        for s in items[:20]:
            one_line = s.replace("\n", " / ")
            out.append(f"- `{one_line}`")
        if len(items) > 20:
            out.append(f"- ... (+{len(items) - 20} more)")
        out.append("")

    target = ROOT / "_analysis/passive_tree_translation_misses.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
