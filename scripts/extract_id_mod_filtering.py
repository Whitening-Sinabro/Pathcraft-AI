"""F7-fix-2 — NeverSink 1-REGULAR.filter → data/id_mod_filtering.json.

NeverSink [[0600]/[[0700]]/[[0800]]] IDENTIFIED MOD FILTERING 섹션의 Show 블록을
파싱해 Class → mod 리스트로 집계. Identified Rare 블록을 강조하는 필터 출력에 사용.

소스 파일: `_analysis/neversink_8.19.0b/NeverSink's filter - 1-REGULAR.filter`
출력: `data/id_mod_filtering.json`

블록 구조 예 (line 1070):
    Show # %D5 $type->rareid $tier->helmet_life_based
        Class == "Helmets"
        HasExplicitMod "Fecund" "Athlete's" ...
        HasExplicitMod >=4 "Fecund" "Athlete's" ... (큰 pool)
        HasExplicitMod =0 "Hale" "Healthy" "Sanguine"

수집 규칙:
- `HasExplicitMod` 오퍼레이터 없거나 `>=N` → mod pool에 추가
- `HasExplicitMod =0` → exclude 대상 (집계 제외)
- Class 문자열 파싱해 각 class에 중복 제거 후 union

실행:
    python scripts/extract_id_mod_filtering.py
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

logger = logging.getLogger("extract_id_mod_filtering")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
NEVERSINK_DIR = ROOT / "_analysis" / "neversink_8.19.0b"
FILTER_NAME = "NeverSink's filter - 1-REGULAR.filter"
FILTER_PATH = NEVERSINK_DIR / FILTER_NAME
OUTPUT_PATH = ROOT / "data" / "id_mod_filtering.json"

_SECTION_RE = re.compile(r"\[\[0[6-8]00\]\]\s*IDENTIFIED MOD FILTERING")
_QUOTED_RE = re.compile(r'"([^"]+)"')


def _iter_show_blocks(content: str):
    """[[0600]]/[[0700]]/[[0800]] 섹션 내 Show 블록 이터레이트."""
    in_section = False
    current_block: list[str] | None = None
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# [[") and _SECTION_RE.search(line):
            in_section = True
            continue
        if line.startswith("# [[") and in_section:
            if not _SECTION_RE.search(line):
                # 다른 섹션 진입 → 종료
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
            # Class == "A" "B" 또는 Class "A" "B"
            return _QUOTED_RE.findall(stripped)
    return []


def _parse_mods(block: list[str]) -> tuple[set[str], set[str]]:
    """block → (include_mods, exclude_mods)."""
    include: set[str] = set()
    exclude: set[str] = set()
    for line in block:
        stripped = line.strip()
        if not stripped.startswith("HasExplicitMod"):
            continue
        mods = _QUOTED_RE.findall(stripped)
        body = stripped[len("HasExplicitMod"):].lstrip()
        if body.startswith("=0"):
            exclude.update(mods)
        else:
            include.update(mods)
    return include, exclude


def build_by_class() -> dict:
    content = FILTER_PATH.read_text(encoding="utf-8")
    # 필터 파일의 VERSION 헤더 추출
    version_m = re.search(r"^#\s*VERSION:\s*(.+)$", content, re.M)
    filter_version = version_m.group(1).strip() if version_m else "unknown"

    by_class: dict[str, set[str]] = {}
    total_blocks = 0
    for block in _iter_show_blocks(content):
        classes = _parse_classes(block)
        if not classes:
            continue
        include, _exclude = _parse_mods(block)
        if not include:
            continue
        total_blocks += 1
        for cls in classes:
            by_class.setdefault(cls, set()).update(include)

    sorted_classes = {cls: sorted(mods) for cls, mods in sorted(by_class.items())}
    total_unique_mods = len({m for mods in sorted_classes.values() for m in mods})

    return {
        "_meta": {
            "description": "NeverSink ID Mod Filtering [[0600]/[0700]/[0800]] 추출. Identified rare 가치 mod 리스트.",
            "source": f"NeverSink's filter - 1-REGULAR.filter v{filter_version}",
            "source_path": str(FILTER_PATH.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": hashlib.sha256(FILTER_PATH.read_bytes()).hexdigest(),
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "extractor": "scripts/extract_id_mod_filtering.py",
            "total_blocks": total_blocks,
            "total_unique_mods": total_unique_mods,
        },
        "by_class": sorted_classes,
    }


def main() -> int:
    if not FILTER_PATH.exists():
        logger.error("NeverSink 필터 없음: %s", FILTER_PATH)
        return 1

    payload = build_by_class()
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    meta = payload["_meta"]
    logger.info(
        "write %s: %d classes, %d blocks, %d unique mods (source=%s)",
        OUTPUT_PATH.relative_to(ROOT),
        len(payload["by_class"]),
        meta["total_blocks"],
        meta["total_unique_mods"],
        meta["source"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
