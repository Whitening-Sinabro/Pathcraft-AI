"""POE2 D7 Phase 2 — NeverSink POE2 0.9.1 필터 → data/id_mod_filtering_poe2.json.

NeverSink POE2 [[0400]] IDENTIFIED MODS: RECOMBINATOR MODS 섹션의 Show 블록을
파싱해 Class → mod 리스트로 집계. POE2 Recombinator (Identified rare + top mod)
강조 필터 출력에 사용.

POE1 대비 차이점:
- 섹션 앵커: [[0400]] (POE1 = [[0600]/[0700]/[0800]])
- HasExplicitMod 오퍼레이터: `>=1` 고정 (POE1 은 count 생략 또는 `>=N`)
- Rarity 조건: `Normal Magic Rare` (POE1 = Rare only)
- ItemLevel 조건 없음 (POE1 = ItemLevel >= 68)
- Mirrored False / Corrupted False 명시 (POE1 블록 기본 없음)

SOFT / STRICT 교차 검증: 두 파일의 by_class 가 동일할 것을 단정 (2026-04-24 실측).

실행:
    python scripts/extract_id_mod_filtering_poe2.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("extract_id_mod_filtering_poe2")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
NEVERSINK_DIR = ROOT / "_analysis" / "neversink_poe2_0.9.1"
SOFT_PATH = NEVERSINK_DIR / "NeverSink's filter 2 - 0-SOFT.filter"
STRICT_PATH = NEVERSINK_DIR / "NeverSink's filter 2 - 3-STRICT.filter"
OUTPUT_PATH = ROOT / "data" / "id_mod_filtering_poe2.json"

_SECTION_RE = re.compile(r"\[\[0400\]\]\s*IDENTIFIED MODS:\s*RECOMBINATOR MODS", re.I)
_QUOTED_RE = re.compile(r'"([^"]+)"')


def _iter_show_blocks(content: str):
    """[[0400]] 섹션 내 Show 블록 이터레이트 (다음 섹션 진입 시 종료)."""
    in_section = False
    current_block: list[str] | None = None
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# [["):
            if _SECTION_RE.search(line):
                in_section = True
                continue
            if in_section:
                if current_block:
                    yield current_block
                    current_block = None
                in_section = False
                continue
        if not in_section:
            continue
        if line.startswith("Show"):
            if current_block:
                yield current_block
            current_block = [line]
            continue
        if current_block is not None:
            if line.strip() == "" or line.startswith("#"):
                if current_block:
                    yield current_block
                    current_block = None
                continue
            current_block.append(line)
    if current_block:
        yield current_block


def _parse_classes(block: list[str]) -> list[str]:
    for line in block:
        stripped = line.strip()
        if stripped.startswith("Class "):
            return _QUOTED_RE.findall(stripped)
    return []


def _parse_mods(block: list[str]) -> set[str]:
    """block 의 HasExplicitMod 라인에서 mod 문자열 수집."""
    mods: set[str] = set()
    for line in block:
        stripped = line.strip()
        if not stripped.startswith("HasExplicitMod"):
            continue
        body = stripped[len("HasExplicitMod"):].lstrip()
        # POE2 관례: `>=1` 또는 생략. `=0` (exclude) 는 [[0400]] 블록에 없음.
        if body.startswith("=0"):
            continue
        mods.update(_QUOTED_RE.findall(stripped))
    return mods


def _build_by_class(path: Path) -> tuple[dict[str, list[str]], int]:
    content = path.read_text(encoding="utf-8")
    by_class: dict[str, set[str]] = {}
    total_blocks = 0
    for block in _iter_show_blocks(content):
        classes = _parse_classes(block)
        if not classes:
            continue
        mods = _parse_mods(block)
        if not mods:
            continue
        total_blocks += 1
        for cls in classes:
            by_class.setdefault(cls, set()).update(mods)
    sorted_classes = {cls: sorted(mods) for cls, mods in sorted(by_class.items())}
    return sorted_classes, total_blocks


def _assert_cross_consistent(soft: dict[str, list[str]], strict: dict[str, list[str]]) -> None:
    """SOFT vs STRICT by_class 동일성 검증. 불일치 시 상세 diff 로그 + 에러."""
    if soft == strict:
        return
    only_soft = set(soft) - set(strict)
    only_strict = set(strict) - set(soft)
    diffs: list[str] = []
    if only_soft:
        diffs.append(f"SOFT only classes: {sorted(only_soft)}")
    if only_strict:
        diffs.append(f"STRICT only classes: {sorted(only_strict)}")
    for cls in sorted(set(soft) & set(strict)):
        if soft[cls] != strict[cls]:
            diffs.append(
                f"{cls}: SOFT={soft[cls]!r} STRICT={strict[cls]!r}"
            )
    raise RuntimeError(
        "NeverSink POE2 SOFT/STRICT [[0400]] 불일치 — 스크립트 재검토 필요:\n  "
        + "\n  ".join(diffs)
    )


def build_payload() -> dict:
    soft_by_class, soft_blocks = _build_by_class(SOFT_PATH)
    strict_by_class, strict_blocks = _build_by_class(STRICT_PATH)
    _assert_cross_consistent(soft_by_class, strict_by_class)

    total_unique_mods = len({m for mods in soft_by_class.values() for m in mods})

    return {
        "_meta": {
            "description": (
                "NeverSink POE2 0.9.1 IDENTIFIED MODS: RECOMBINATOR MODS [[0400]] 추출. "
                "Identified rare/normal/magic + top mod 리스트 (POE2 Recombinator 강조용)."
            ),
            "source_soft": str(SOFT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "source_strict": str(STRICT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "source_soft_sha256": hashlib.sha256(SOFT_PATH.read_bytes()).hexdigest(),
            "source_strict_sha256": hashlib.sha256(STRICT_PATH.read_bytes()).hexdigest(),
            "cross_verified": True,
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "extractor": "scripts/extract_id_mod_filtering_poe2.py",
            "total_blocks": soft_blocks,
            "total_unique_mods": total_unique_mods,
            "notes": (
                "SOFT/STRICT 동일 (2026-04-24 실측). "
                "Rarity Normal Magic Rare + HasExplicitMod >=1 + Mirrored/Corrupted False 패턴."
            ),
        },
        "by_class": soft_by_class,
    }


def main() -> int:
    for p in (SOFT_PATH, STRICT_PATH):
        if not p.exists():
            logger.error("NeverSink POE2 필터 없음: %s", p)
            return 1

    payload = build_payload()
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    meta = payload["_meta"]
    logger.info(
        "write %s: %d classes, %d blocks, %d unique mods",
        OUTPUT_PATH.relative_to(ROOT),
        len(payload["by_class"]),
        meta["total_blocks"],
        meta["total_unique_mods"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
