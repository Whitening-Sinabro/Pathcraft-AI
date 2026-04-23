"""NeverSink POE2 필터에서 Class 이름을 재추출해 data/item_class_map_poe2.json 과 diff.

목적: POE2 패치 또는 NeverSink 릴리스 후 Class 목록 drift 감지.
   - 새 Class 추가 → item_class_map_poe2.json 갱신 필요 (경고)
   - Class 제거 → poe2_classes 리스트 업데이트 필요 (경고)

사용:
    python scripts/verify_item_class_map_poe2.py              # 온라인 fetch + diff
    python scripts/verify_item_class_map_poe2.py --local path # 로컬 필터 파일 diff

의존: urllib (stdlib). requests 불필요.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
MAP_PATH = ROOT / "data" / "item_class_map_poe2.json"

NEVERSINK_REPO = "NeverSinkDev/NeverSink-Filter-for-PoE2"
FILTER_FILES = [
    "NeverSink's filter 2 - 0-SOFT.filter",
    "NeverSink's filter 2 - 3-STRICT.filter",
]

_CLASS_LINE_RE = re.compile(r"\s*Class\s*(==|!=)?\s*(.*)")
_QUOTED_RE = re.compile(r'"([^"]+)"')

logger = logging.getLogger("verify_item_class_map_poe2")
logging.basicConfig(level=logging.INFO, format="%(message)s")


def _extract_classes(text: Iterable[str]) -> set[str]:
    out: set[str] = set()
    for line in text:
        m = _CLASS_LINE_RE.match(line)
        if not m:
            continue
        for val in _QUOTED_RE.findall(m.group(2)):
            out.add(val)
    return out


def _fetch_raw(file_name: str) -> str:
    from urllib.parse import quote
    encoded = quote(file_name, safe="")
    url = f"https://raw.githubusercontent.com/{NEVERSINK_REPO}/main/{encoded}"
    req = Request(url, headers={"User-Agent": "PathcraftAI-verify/1.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _load_map() -> dict:
    if not MAP_PATH.exists():
        raise FileNotFoundError(f"{MAP_PATH} 없음")
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def verify(remote: bool = True, local_paths: list[Path] | None = None) -> int:
    mapping = _load_map()
    known = set(mapping["poe2_classes"])

    observed: set[str] = set()
    if remote:
        for fn in FILTER_FILES:
            try:
                txt = _fetch_raw(fn)
            except URLError as e:
                logger.error(f"[fetch 실패] {fn}: {e}")
                return 2
            observed |= _extract_classes(txt.splitlines())
            logger.info(f"[+] fetched {fn}: +{len(_extract_classes(txt.splitlines()))} classes")
    if local_paths:
        for p in local_paths:
            if not p.exists():
                logger.error(f"[로컬 파일 없음] {p}")
                return 2
            observed |= _extract_classes(p.read_text(encoding="utf-8").splitlines())
            logger.info(f"[+] loaded {p}")

    added = observed - known
    removed = known - observed
    if not added and not removed:
        logger.info(f"[OK] Class 목록 일치 — {len(known)} classes")
        return 0
    if added:
        logger.warning(f"[DRIFT] NeverSink 에 있는데 map 에 없음 ({len(added)}): {sorted(added)}")
    if removed:
        logger.warning(f"[DRIFT] map 에 있는데 NeverSink 에 없음 ({len(removed)}): {sorted(removed)}")
    logger.warning("→ data/item_class_map_poe2.json 의 poe2_classes / categories_poe2 업데이트 필요")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", nargs="*", type=Path, default=None,
                    help="로컬 .filter 파일 경로 (여러 개). 지정 시 네트워크 fetch 스킵.")
    args = ap.parse_args()
    remote = args.local is None
    return verify(remote=remote, local_paths=args.local)


if __name__ == "__main__":
    sys.exit(main())
