"""
POE2 uniques_poe2.json 생성 — UniqueStashLayout × Words (+ 선택: UniqueStashTypes) 조인.

입력:
  - data/game_data_poe2/UniqueStashLayout.json : 403 rows (이름은 WordsKey 로만 참조)
  - data/game_data_poe2/Words.json             : Text / Text2 로 유니크 이름 제공
  - data/game_data_poe2/UniqueStashTypes.json  : (선택) 34 rows — stash_type id → Name
                                                  존재 시 `stash_type_label` 필드 추가

출력:
  - data/uniques_poe2.json : 유니크 아이템 이름/메타 화이트리스트

조인 키:
  - UniqueStashLayout.WordsKey (index) → Words[i].Text (localized name)
  - UniqueStashLayout.UniqueStashTypesKey → UniqueStashTypes[j].Name (예: "Weapons", "Body Armours")

제외:
  - ShowIfEmptyStandard == False AND ShowIfEmptyChallengeLeague == False (비활성)
  - WordsKey 가 Words 범위 초과 (garbage index)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

POE2_ROOT = Path(__file__).resolve().parents[1] / "data" / "game_data_poe2"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "uniques_poe2.json"


def load(name: str) -> list[dict]:
    with (POE2_ROOT / name).open(encoding="utf-8") as f:
        return json.load(f)


def load_optional(name: str) -> list[dict] | None:
    """테이블이 아직 GGPK 추출되지 않았으면 None 반환 (graceful degradation)."""
    path = POE2_ROOT / name
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_stash_type_labels(stash_types: list[dict] | None) -> dict[int, str]:
    """UniqueStashTypes 행 인덱스 → Name 문자열 매핑.

    Name 이 비어있으면 Id 를 fallback, 그것도 비면 생략. Label 없는 인덱스는
    후속 stash_type 조회 시 None 으로 떨어지도록 dict 에 포함하지 않는다.
    """
    if not stash_types:
        return {}
    labels: dict[int, str] = {}
    for idx, row in enumerate(stash_types):
        label = (row.get("Name") or "").strip() or (row.get("Id") or "").strip()
        if label:
            labels[idx] = label
    return labels


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    layout = load("UniqueStashLayout.json")
    words = load("Words.json")
    stash_types = load_optional("UniqueStashTypes.json")
    stash_labels = build_stash_type_labels(stash_types)

    logger.info("UniqueStashLayout: %d rows", len(layout))
    logger.info("Words: %d rows", len(words))
    if stash_types is not None:
        logger.info("UniqueStashTypes: %d rows (labels: %d)", len(stash_types), len(stash_labels))
    else:
        logger.info("UniqueStashTypes.json 없음 — stash_type_label 생략 (다음 GGPK 추출 후 자동 반영)")

    uniques: list[dict] = []
    skipped_hidden = 0
    skipped_badref = 0
    skipped_unknown_label = 0

    for row in layout:
        if not (row.get("ShowIfEmptyStandard") or row.get("ShowIfEmptyChallengeLeague")):
            skipped_hidden += 1
            continue

        wk = row.get("WordsKey", -1)
        if not isinstance(wk, int) or wk < 0 or wk >= len(words):
            skipped_badref += 1
            continue

        w = words[wk]
        name = (w.get("Text") or "").strip()
        if not name:
            skipped_badref += 1
            continue

        stash_type = row.get("UniqueStashTypesKey", 0)
        entry = {
            "name": name,
            "name_alt": (w.get("Text2") or "").strip() or None,
            "visual_id": row.get("ItemVisualIdentityKey", 0),
            "is_alt_art": bool(row.get("IsAlternateArt", False)),
            "stash_type": stash_type,
        }
        if stash_labels:
            label = stash_labels.get(stash_type)
            if label is None:
                skipped_unknown_label += 1
            entry["stash_type_label"] = label
        uniques.append(entry)

    uniques.sort(key=lambda x: x["name"])

    meta = {
        "source": "GGPK UniqueStashLayout + Words JOIN",
        "game": "poe2",
        "generator": "scripts/build_uniques_poe2.py",
        "total": len(uniques),
        "skipped_hidden": skipped_hidden,
        "skipped_badref": skipped_badref,
    }
    if stash_labels:
        meta["source"] = "GGPK UniqueStashLayout + Words + UniqueStashTypes JOIN"
        meta["stash_type_labels_count"] = len(stash_labels)
        meta["skipped_unknown_label"] = skipped_unknown_label

    out = {"_meta": meta, "uniques": uniques}

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if stash_labels:
        logger.info(
            "uniques_poe2.json 생성 — 유니크 %d / 숨김 %d / badref %d / unknown_label %d",
            len(uniques), skipped_hidden, skipped_badref, skipped_unknown_label,
        )
    else:
        logger.info(
            "uniques_poe2.json 생성 — 유니크 %d / 숨김 %d / badref %d",
            len(uniques), skipped_hidden, skipped_badref,
        )
    logger.info("sample 10: %s", [u["name"] for u in uniques[:10]])


if __name__ == "__main__":
    main()
