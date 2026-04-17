"""NeverSink 1-REGULAR.filter → data/defense_mod_tiers.json (Phase D2).

사용:
    python scripts/extract_defense_mod_tiers.py

동작:
1. NeverSink 1-REGULAR.filter 로드 (_analysis/neversink_8.19.0b/)
2. `$tier->(slot)_(focus)` 블록 식별 — body/helmet/boots/gloves/shield × life/es
3. 각 블록에서 HasExplicitMod 라인 파싱 (required/required_4plus/exclude)
4. JSON 출력 — slot → focus → mod 리스트

NeverSink 블록 구조 (예: helmet_life_based, line 1064-1079):
    Class == "Helmets"
    HasExplicitMod "A" "B" "C"              → required_any (T1 key mods)
    HasExplicitMod >=4 "A" "B" ... "Z"      → required_count4 (any 4 mods from full pool)
    HasExplicitMod =0 "weak1" "weak2"       → exclude (weak mod 0개)

설계 결정:
- `life` 통합: life_based / defense / lifedefense → life (NeverSink granular 단계 병합)
- `es`는 es_based만
- Shield: esfocus → es, lifefocus → life (defensefocus/casterfocus 제외 — attack 오리엔트)
"""
from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger("extract_defense_mod_tiers")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
FILTER_PATH = ROOT / "_analysis" / "neversink_8.19.0b" / "NeverSink's filter - 1-REGULAR.filter"
OUTPUT = ROOT / "data" / "defense_mod_tiers.json"

# tier 토큰 → (slot, focus) 매핑.
# NeverSink 세분 단계를 통합: body_life/defense/lifedefense → body.life, body_es → body.es
_TIER_MAP: dict[str, tuple[str, str]] = {
    "body_life": ("body_armour", "life"),
    "body_defense": ("body_armour", "life"),
    "body_lifedefense": ("body_armour", "life"),
    "body_es": ("body_armour", "es"),
    "helmet_life_based": ("helmet", "life"),
    "helmet_es_based": ("helmet", "es"),
    "boots_life_based": ("boots", "life"),
    "boots_es_based": ("boots", "es"),
    "gloves_life_based": ("gloves", "life"),
    "gloves_es_based": ("gloves", "es"),
    "shield_lifefocus": ("shield", "life"),
    "shield_esfocus": ("shield", "es"),
}


_MOD_QUOTED_RE = re.compile(r'"([^"]+)"')


def _parse_mod_line(line: str) -> tuple[str, list[str]]:
    """HasExplicitMod 라인 → (kind, mod_names).

    kind: "required_any" (operator 없음) | "required_count_N" (>=N) | "exclude" (=0)
    """
    # HasExplicitMod >=4 "A" "B" ...
    # HasExplicitMod "A" "B" ...
    # HasExplicitMod =0 "A" "B" ...
    stripped = line.strip()
    if not stripped.startswith("HasExplicitMod"):
        raise ValueError(f"not HasExplicitMod: {line!r}")
    mods = _MOD_QUOTED_RE.findall(stripped)
    body = stripped[len("HasExplicitMod"):].strip()
    if body.startswith(">="):
        n = body.split()[0][2:]
        return (f"required_count_{n}", mods)
    if body.startswith("="):
        n = body.split()[0][1:]
        if n == "0":
            return ("exclude", mods)
        return (f"required_eq_{n}", mods)
    return ("required_any", mods)


def _parse_blocks(content: str) -> dict[str, dict]:
    """Show 블록들을 tier 토큰 → {mod_kind: [mods]} 딕셔너리로 파싱."""
    blocks: dict[str, dict] = {}
    # $type->... $tier->(token)
    tier_re = re.compile(r"\$tier->(\w+)")
    # Show 블록 = "Show" 부터 빈 줄 또는 다음 "Show"/"Hide"까지
    block_re = re.compile(
        r"^(Show|Hide)[^\n]*\n((?:\t[^\n]*\n?|[ ]{4}[^\n]*\n?)+)",
        re.MULTILINE,
    )
    for match in block_re.finditer(content):
        header_start = match.start()
        # 블록 헤더 라인에서 tier 토큰 검색
        header_line = content[header_start:content.find("\n", header_start)]
        tier_match = tier_re.search(header_line)
        if tier_match is None:
            continue
        tier_token = tier_match.group(1)
        if tier_token not in _TIER_MAP:
            continue
        body = match.group(2)
        parsed: dict[str, list[str]] = {}
        for raw_line in body.splitlines():
            stripped = raw_line.strip()
            if not stripped.startswith("HasExplicitMod"):
                continue
            try:
                kind, mods = _parse_mod_line(raw_line)
            except ValueError:
                continue
            parsed.setdefault(kind, []).extend(mods)
        if parsed:
            blocks[tier_token] = parsed
    return blocks


def _consolidate(raw_blocks: dict[str, dict]) -> dict[str, dict]:
    """raw tier 토큰 블록 → slot.focus 통합 (body_life + body_defense + body_lifedefense → body.life)."""
    out: dict[str, dict[str, dict[str, list[str]]]] = {}
    for token, parsed in raw_blocks.items():
        slot, focus = _TIER_MAP[token]
        slot_dict = out.setdefault(slot, {})
        focus_dict = slot_dict.setdefault(focus, {})
        for kind, mods in parsed.items():
            merged = set(focus_dict.get(kind, [])) | set(mods)
            focus_dict[kind] = sorted(merged)
    return out


def main() -> int:
    if not FILTER_PATH.exists():
        logger.error("NeverSink filter not found: %s", FILTER_PATH)
        return 1
    content = FILTER_PATH.read_text(encoding="utf-8")
    raw = _parse_blocks(content)
    logger.info("Parsed %d tier blocks: %s", len(raw), sorted(raw.keys()))
    consolidated = _consolidate(raw)
    payload = {
        "_meta": {
            "source": str(FILTER_PATH.relative_to(ROOT)).replace("\\", "/"),
            "neversink_version": "8.19.0b",
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "script": "scripts/extract_defense_mod_tiers.py",
            "consolidation": (
                "body_life/defense/lifedefense → body_armour.life; "
                "shield defensefocus/casterfocus 제외 (attack-oriented); "
                "mod kinds: required_any (T1 key), required_count_N (any N from pool), exclude (weak)"
            ),
            "slot_count": len(consolidated),
            "spot_check_status": (
                "skipped — NeverSink 8.19.0b curation trusted as source of truth. "
                "mod names are GGG game data (not NeverSink authored) and auto-synced "
                "from 4h economy updates. Wiki cross-check deferred unless false-positive "
                "reports surface in-game."
            ),
        },
        "slots": consolidated,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    total_mods = sum(
        len(m) for slot in consolidated.values()
        for focus in slot.values() for m in focus.values()
    )
    logger.info("Wrote %s — %d slots, %d total mod entries",
                OUTPUT.relative_to(ROOT), len(consolidated), total_mods)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
