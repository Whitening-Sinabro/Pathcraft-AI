"""`data/divcard_mapping.json` 검증 — Wiki 대조로 stale 엔트리 감지.

사용:
    python scripts/validate_divcard_mapping.py

검증 항목:
1. 각 divcard (예: "The Apothecary") 이름이 Wiki `items` 테이블 (class_id="DivinationCard")에 존재하는가
2. 각 target unique (예: "Mageblood") 이름이 Wiki `items` 테이블 (rarity="Unique")에 존재하는가
3. Wiki divcard `description`에서 추출한 reward unique와 매핑이 일치하는가

제약:
- `stack_size` 필드는 Wiki Cargo 스키마에서 MW exception 발생 → stack 검증은 수동
- description HTML에서 `[[UniqueName|...]]` 패턴 regex 추출 (wikitext 의존, 불완전)

출력: 검증 리포트만. 자동 수정 안 함 (수동 검토 유도).
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("validate_divcard")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
MAPPING_PATH = ROOT / "data" / "divcard_mapping.json"
WIKI_API = "https://www.poewiki.net/w/api.php"
HEADERS = {"User-Agent": "PathcraftAI/1.0 validate_divcard"}

WIKILINK_PATTERN = re.compile(r"\[\[(?!File:)([^|\]]+)\|")


def cargo(fields: str, where: str, limit: int = 50) -> list[dict]:
    params = {
        "action": "cargoquery", "tables": "items", "fields": fields,
        "where": where, "format": "json", "limit": str(limit),
    }
    r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Wiki API error: {data['error']}")
    return [item["title"] for item in data.get("cargoquery", [])]


def quote_names(names: list[str]) -> str:
    # SQL IN() — 홑따옴표 포함 이름 이스케이프
    parts = [f'"{n.replace(chr(34), chr(34)+chr(34))}"' for n in names]
    return ",".join(parts)


def extract_reward_uniques(description: str) -> list[str]:
    if not description:
        return []
    return [m for m in WIKILINK_PATTERN.findall(description)]


def main() -> int:
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))["unique_to_cards"]
    target_uniques = sorted(mapping.keys())
    card_names = sorted({e["card"] for entries in mapping.values() for e in entries})

    logger.info("loaded mapping: %d uniques -> %d cards", len(target_uniques), len(card_names))

    # 1. 유니크 존재 확인
    logger.info("verifying %d target uniques on wiki...", len(target_uniques))
    rows = cargo(
        fields="items.name",
        where=f'items.rarity="Unique" AND items.name IN ({quote_names(target_uniques)})',
        limit=500,
    )
    wiki_uniques = {r["name"] for r in rows}
    missing_uniques = sorted(set(target_uniques) - wiki_uniques)

    # 2. 디비카 존재 + description 확인
    logger.info("verifying %d divcards on wiki...", len(card_names))
    rows = cargo(
        fields="items.name,items.description",
        where=f'items.class_id="DivinationCard" AND items.name IN ({quote_names(card_names)})',
        limit=500,
    )
    wiki_cards = {r["name"]: r.get("description", "") or "" for r in rows}
    missing_cards = sorted(set(card_names) - set(wiki_cards))

    # 3. 매핑 vs Wiki description reward 교차 검증
    mismatches: list[tuple[str, str, list[str]]] = []
    for unique, entries in mapping.items():
        for entry in entries:
            card = entry["card"]
            desc = wiki_cards.get(card, "")
            rewards = extract_reward_uniques(desc)
            # 실제 reward이면 unique 이름이 rewards 리스트에 등장해야 함
            if rewards and unique not in rewards:
                mismatches.append((unique, card, rewards))

    # 리포트
    print("=" * 70)
    print(f"divcard_mapping.json 검증 리포트 ({MAPPING_PATH})")
    print("=" * 70)
    print(f"엔트리: {len(target_uniques)} uniques -> {len(card_names)} cards")
    print()
    print(f"[1] Wiki에 없는 target unique: {len(missing_uniques)}")
    for n in missing_uniques:
        print(f"  - {n}")
    print()
    print(f"[2] Wiki에 없는 divcard: {len(missing_cards)}")
    for n in missing_cards:
        print(f"  - {n}")
    print()
    print(f"[3] Reward 불일치 (매핑 unique가 wiki description에 없음): {len(mismatches)}")
    for unique, card, rewards in mismatches:
        print(f"  - {unique} <- {card}: wiki rewards = {rewards[:5]}")
    print()

    total_issues = len(missing_uniques) + len(missing_cards) + len(mismatches)
    if total_issues == 0:
        print("✅ 모든 매핑 Wiki와 정합")
        return 0
    print(f"⚠️ 총 {total_issues}건 검토 필요 — 수동 수정 후 재실행 권장")
    return 1


if __name__ == "__main__":
    sys.exit(main())
