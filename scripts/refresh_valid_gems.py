"""valid_gems.json 재생성 (GGPK BaseItemTypes → valid_gems Phase H5).

사용:
    python scripts/refresh_valid_gems.py [--dry-run] [--league "Mirage 3.28"]

동작:
1. data/game_data/BaseItemTypes.json 로드 (Rust extract_data.exe 출력)
2. Id prefix 'Metadata/Items/Gems/' 필터 → active/support 젬 후보
3. `[UNUSED]` 접두어 엔트리 제외
4. Support 젬의 suffix 제거 형태 추가 (LLM 단축 표기 커버)
5. `data/valid_gems.json` 기록 + _meta (league/collected_at/sha256)

출력 스키마:
{
  "_meta": {
    "description": "...",
    "source": "data/game_data/BaseItemTypes.json",
    "league": "Mirage 3.28",
    "collected_at": "2026-04-21",
    "source_sha256": "...",
    "sources": {"ggpk_gems": N, "bare_support_names": M},
    "total": N + M
  },
  "gems": [...sorted unique names...]
}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from datetime import date
from pathlib import Path

logger = logging.getLogger("refresh_valid_gems")
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_ggpk_gem_names(base_item_types_path: Path) -> set[str]:
    try:
        rows = json.loads(base_item_types_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error("BaseItemTypes.json 로드 실패: %s", e)
        sys.exit(2)

    names: set[str] = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        id_ = r.get("Id", "")
        if not isinstance(id_, str) or not id_.startswith("Metadata/Items/Gems/"):
            continue
        name = r.get("Name", "")
        if not isinstance(name, str):
            continue
        name = name.strip()
        if not name:
            continue
        if name.startswith("[UNUSED]"):
            continue  # 제거된/비활성 젬
        names.add(name)
    return names


def collect_transfigured_gems(active_skills_path: Path) -> set[str]:
    """ActiveSkills.json 에서 transfigured gem (3.22+ alternate variant) 추출.

    BaseItemTypes 에는 base gem 만 있고 transfigured variant (_alt_x/_alt_y Id, " of X"
    DisplayedName) 는 ActiveSkills 에 따로 기록됨. 이 단계 없으면 "Boneshatter of
    Complex Trauma" 같은 정상 젬이 allowlist 밖으로 떨어짐.

    필터:
    - TransfigureBase 가 sentinel(-72340172838076674) 또는 None 이면 base gem → 제외
      (base gem 은 BaseItemTypes 경로에서 이미 수집됨)
    - DisplayedName 에 " of " 포함 (transfigured naming convention, 몬스터 변종 배제)
    - [DNT] 접두어 제외 (미출시 placeholder)
    """
    TB_SENTINEL = -72340172838076674
    try:
        rows = json.loads(active_skills_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("ActiveSkills.json 로드 실패: %s — transfigured 건너뜀", e)
        return set()

    names: set[str] = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        name = r.get("DisplayedName", "")
        tb = r.get("TransfigureBase")
        if not isinstance(name, str) or not name.strip():
            continue
        name = name.strip()
        if name.startswith("[DNT]"):
            continue
        if " of " not in name:
            continue
        if tb is None or tb == TB_SENTINEL:
            continue
        names.add(name)
    return names


def derive_bare_support_forms(gem_names: set[str]) -> set[str]:
    """'... Support' → '...' (suffix 제거). LLM 단축 표기 커버용."""
    bare: set[str] = set()
    for n in gem_names:
        if n.endswith(" Support"):
            stripped = n[: -len(" Support")].strip()
            if stripped and stripped not in gem_names:
                bare.add(stripped)
    return bare


def build_output(league: str, base_path: Path, active_skills_path: Path) -> dict:
    ggpk_gems = collect_ggpk_gem_names(base_path)
    transfigured = collect_transfigured_gems(active_skills_path)
    bare_support = derive_bare_support_forms(ggpk_gems)
    all_names = sorted(ggpk_gems | transfigured | bare_support)
    return {
        "_meta": {
            "description": "POE1 유효 젬·서포트·Transfigured 이름 화이트리스트 (GGPK 전용).",
            "sources_files": [
                "data/game_data/BaseItemTypes.json",
                "data/game_data/ActiveSkills.json",
            ],
            "source_filter": (
                "BaseItems: Id startswith 'Metadata/Items/Gems/' AND NOT Name startswith '[UNUSED]'. "
                "ActiveSkills: TransfigureBase != sentinel AND ' of ' in DisplayedName AND NOT [DNT]."
            ),
            "league": league,
            "collected_at": date.today().isoformat(),
            "source_sha256": _sha256(base_path),
            "active_skills_sha256": _sha256(active_skills_path),
            "sources": {
                "ggpk_gems": len(ggpk_gems),
                "transfigured_gems": len(transfigured),
                "bare_support_names": len(bare_support),
            },
            "total": len(all_names),
            "note": (
                "bare_support_names 는 'Added Fire Damage Support' → 'Added Fire Damage' 단축 형태. "
                "transfigured_gems 는 3.22+ 도입된 alt variant ('Boneshatter of Complex Trauma')."
            ),
            "refresh_script": "scripts/refresh_valid_gems.py",
        },
        "gems": all_names,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="valid_gems.json 재생성")
    ap.add_argument("--dry-run", action="store_true", help="기록 없이 diff만 출력")
    ap.add_argument("--league", default="Mirage 3.28", help="리그 태그 (_meta.league)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    root = _repo_root()
    base_path = root / "data" / "game_data" / "BaseItemTypes.json"
    active_skills_path = root / "data" / "game_data" / "ActiveSkills.json"
    out_path = root / "data" / "valid_gems.json"

    if not base_path.exists():
        logger.error("BaseItemTypes.json 없음: %s — 먼저 extract_data.exe 실행 필요", base_path)
        sys.exit(2)
    if not active_skills_path.exists():
        logger.error("ActiveSkills.json 없음: %s — 먼저 extract_data.exe 실행 필요", active_skills_path)
        sys.exit(2)

    new_out = build_output(args.league, base_path, active_skills_path)
    new_gems = set(new_out["gems"])

    if out_path.exists():
        try:
            cur = json.loads(out_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cur = {}
        cur_gems = set(cur.get("gems", []))
        added = new_gems - cur_gems
        removed = cur_gems - new_gems
        logger.info("diff: +%d / -%d (현재 %d → 신규 %d)",
                    len(added), len(removed), len(cur_gems), len(new_gems))
        if added:
            logger.info("  추가(샘플): %s", sorted(added)[:10])
        if removed:
            logger.info("  제거(샘플): %s", sorted(removed)[:10])
    else:
        logger.info("신규 생성: %d 엔트리", len(new_gems))

    if args.dry_run:
        logger.info("dry-run — 기록 생략")
        return

    out_path.write_text(
        json.dumps(new_out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("기록 완료: %s", out_path)


if __name__ == "__main__":
    main()
