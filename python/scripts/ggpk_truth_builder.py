"""GGPK 진실 레퍼런스 빌더 — content hash 계산 + ggpk_truth_reference.json 생성.

계층 1 (content fingerprinting) + 계층 3 (schema pin) 구현.

실행:
    python python/scripts/ggpk_truth_builder.py > _analysis/ggpk_truth_reference.json

설계:
- 각 테이블마다 안정적 식별 필드 조합(KEY_FIELDS)만 추려 정렬 후 sha256.
- 큰 테이블(Mods 39291)도 핵심 필드만 써서 해시 — 내부 무의미 필드(Unknown*) 배제.
- 해시는 field name 순서가 아닌 값 순서 기반 → field reordering에 불변.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GAME_DATA = ROOT / "data" / "game_data"
SCHEMA_FILE = ROOT / "data" / "schema" / "schema.min.json"


# 각 테이블의 content hash를 만들 때 사용할 키 필드.
# 원칙: 리그 전환 시 안정적(Unknown* 제외), 의미 변화를 포착할 수 있는 최소 조합.
KEY_FIELDS: dict[str, tuple[str, ...]] = {
    "ActiveSkills":      ("Id", "DisplayedName"),
    "ArmourTypes":       ("BaseItemTypesKey", "ArmourMin", "ArmourMax", "EvasionMin", "EvasionMax", "EnergyShieldMin", "EnergyShieldMax"),
    "Ascendancy":        ("Id", "ClassNo", "Character"),
    "BaseItemTypes":     ("Id", "Name", "InheritsFrom"),
    "Characters":        ("Attr", "ACTFile"),
    "Essences":          ("BaseItemTypesKey", "Level", "DropLevel", "IsScreamingEssence"),
    "Flasks":            ("BaseItemTypesKey", "Name", "Type"),
    "GemTags":           ("Id", "Tag"),
    "Maps":              ("BaseItemTypesKey", "Tier"),
    "ModFamily":         ("Id",),
    "Mods":              ("Id", "Name", "Level", "Domain", "GenerationType"),
    "ModType":           ("Name",),
    "PassiveSkills":     ("Id", "IsNotable", "IsKeystone", "IsJewelSocket"),
    "QuestRewards":      ("Characters", "Reward", "RewardLevel"),
    "Scarabs":           ("Type", "Items"),
    "ScarabTypes":       ("Id", "Tag", "Count"),
    "SkillGems":         ("BaseItemTypesKey", "IsSupport", "IsVaalVariant"),
    "Tags":              ("Id",),
    "UniqueStashLayout": ("WordsKey", "UniqueStashTypesKey"),
}


def normalize_value(v: Any) -> Any:
    """해시 결정성을 위한 정규화. list는 tuple로, dict는 sorted items."""
    if isinstance(v, list):
        return tuple(normalize_value(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, normalize_value(val)) for k, val in v.items()))
    return v


def table_hash(rows: list[dict], fields: tuple[str, ...]) -> str:
    """지정 필드만 추려 정렬 후 sha256.

    None 또는 누락 필드는 `None`으로 통일 — 필드 부재도 식별 요소로 반영.
    """
    tuples = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = tuple(normalize_value(row.get(f)) for f in fields)
        tuples.append(key)
    tuples.sort(key=lambda t: json.dumps(t, default=str, ensure_ascii=False, sort_keys=True))
    payload = json.dumps(tuples, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def schema_pin() -> dict:
    """schema.min.json git commit + sha256."""
    try:
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", str(SCHEMA_FILE.relative_to(ROOT))],
            cwd=ROOT, text=True,
        ).strip()
    except subprocess.CalledProcessError:
        commit = ""
    content_sha = hashlib.sha256(SCHEMA_FILE.read_bytes()).hexdigest()
    return {
        "path": "data/schema/schema.min.json",
        "git_commit": commit,
        "sha256": content_sha,
        "size_bytes": SCHEMA_FILE.stat().st_size,
    }


def build_tables_block() -> dict:
    out = {}
    for table, fields in KEY_FIELDS.items():
        path = GAME_DATA / f"{table}.json"
        if not path.exists():
            out[table] = {"error": "missing", "expected_path": str(path.relative_to(ROOT))}
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        out[table] = {
            "rows": len(rows),
            "key_fields": list(fields),
            "content_hash": table_hash(rows, fields),
        }
    return out


def build_reference() -> dict:
    return {
        "$schema_version": 1,
        "patch_note_sources": {
            "canonical_forum": "https://www.pathofexile.com/forum/view-forum/patch-notes",
            "wiki_version_history": "https://www.poewiki.net/wiki/Version_history",
        },
        "anchored_to": {
            "league": "3.28 Mirage",
            "verified_at": "2026-04-17",
            "patch_notes_url": "https://www.poewiki.net/wiki/Version_3.28.0",
            "expected_changes": [
                "Scion 신규 ascendancy Reliquarian 추가 (Ascendancy 20 → Characters 7 유지)",
                "신규 스킬 젬 Holy Hammers (ActiveSkills/SkillGems 증가)",
                "Atlas Keystone 재편 (Shadow Shaping/Bold Undertakings/Singular Focus 제거, The Paths Not Taken/Synthesised Stability 추가)",
            ],
        },
        "schema_pin": schema_pin(),
        "extractor_pin": {
            "binary": "src-tauri/src/bin/extract_data.rs",
            "targets_count": 19,
        },
        "tables": build_tables_block(),
        "notes": {
            "hash_semantics": "각 테이블 key_fields 값의 정렬 튜플 리스트 → sha256. 리그 전환 시 hash 변경이 기대되면 anchored_to.expected_changes에 기록.",
            "verification_layers": [
                "Layer 1 (자동, pytest): rows + content_hash 일치",
                "Layer 3 (반자동): schema_pin.git_commit 및 sha256 불일치 시 재검증 요구",
                "Layer 5 (수동): 새 리그 패치노트 읽고 expected_changes 갱신 후 재해시",
            ],
            "out_of_scope_layers": [
                "Layer 2 (독립 추출기 SnosMe/poe-dat-viewer cross-check): 후속 작업",
                "Layer 4 (인게임 골든 스크린샷): 후속 작업",
            ],
        },
    }


if __name__ == "__main__":
    ref = build_reference()
    out_path = ROOT / "_analysis" / "ggpk_truth_reference.json"
    out_path.write_text(
        json.dumps(ref, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[ok] wrote {out_path.relative_to(ROOT)} -- {len(ref['tables'])} tables")
