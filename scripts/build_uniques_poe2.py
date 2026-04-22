"""
POE2 uniques_poe2.json 생성 — UniqueStashLayout × Words 조인.

입력:
  - data/game_data_poe2/UniqueStashLayout.json : 403 rows (이름은 WordsKey 로만 참조)
  - data/game_data_poe2/Words.json             : Text / Text2 로 유니크 이름 제공

출력:
  - data/uniques_poe2.json : 유니크 아이템 이름/메타 화이트리스트

조인 키: UniqueStashLayout.WordsKey (index) → Words[i].Text (localized name)

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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    layout = load("UniqueStashLayout.json")
    words = load("Words.json")

    logger.info("UniqueStashLayout: %d rows", len(layout))
    logger.info("Words: %d rows", len(words))

    uniques: list[dict] = []
    skipped_hidden = 0
    skipped_badref = 0

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

        uniques.append({
            "name": name,
            "name_alt": (w.get("Text2") or "").strip() or None,
            "visual_id": row.get("ItemVisualIdentityKey", 0),
            "is_alt_art": bool(row.get("IsAlternateArt", False)),
            "stash_type": row.get("UniqueStashTypesKey", 0),
        })

    # 이름 알파벳 정렬
    uniques.sort(key=lambda x: x["name"])

    out = {
        "_meta": {
            "source": "GGPK UniqueStashLayout + Words JOIN",
            "game": "poe2",
            "generator": "scripts/build_uniques_poe2.py",
            "total": len(uniques),
            "skipped_hidden": skipped_hidden,
            "skipped_badref": skipped_badref,
        },
        "uniques": uniques,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "uniques_poe2.json 생성 — 유니크 %d / 숨김 %d / badref %d",
        len(uniques), skipped_hidden, skipped_badref,
    )
    logger.info("sample 10: %s", [u["name"] for u in uniques[:10]])


if __name__ == "__main__":
    main()
