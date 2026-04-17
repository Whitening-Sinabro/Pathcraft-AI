"""NeverSink 1-REGULAR.filter → data/accessory_mod_tiers.json (Phase E4).

사용:
    python scripts/extract_accessory_mod_tiers.py

동작 (Phase D extract_defense_mod_tiers 패턴 복제):
1. NeverSink 1-REGULAR.filter 로드
2. `$tier->(amu|ring|belt)_(token)` 블록 식별 — 11 block
3. 각 블록에서 HasExplicitMod 라인 파싱
4. JSON 출력 — slot → axis → mod 리스트

axis 매핑:
- amu_1coreattack / amu_2coreattack + ring_attack → attack
- amu_1corecaster / amu_2corecaster + ring_caster → caster
- amu_1coredot / amu_2coredot → dot
- ring_minion → minion
- amu_exalter + belt_general → common (damage type 무관 공용)
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

logger = logging.getLogger("extract_accessory_mod_tiers")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)

ROOT = Path(__file__).resolve().parent.parent
FILTER_PATH = ROOT / "_analysis" / "neversink_8.19.0b" / "NeverSink's filter - 1-REGULAR.filter"
OUTPUT = ROOT / "data" / "accessory_mod_tiers.json"

# tier 토큰 → (slot, axis)
_TIER_MAP: dict[str, tuple[str, str]] = {
    "amu_exalter":      ("amulet", "common"),
    "amu_1coreattack":  ("amulet", "attack"),
    "amu_2coreattack":  ("amulet", "attack"),
    "amu_1corecaster":  ("amulet", "caster"),
    "amu_2corecaster":  ("amulet", "caster"),
    "amu_1coredot":     ("amulet", "dot"),
    "amu_2coredot":     ("amulet", "dot"),
    "ring_attack":      ("ring", "attack"),
    "ring_caster":      ("ring", "caster"),
    "ring_minion":      ("ring", "minion"),
    "belt_general":     ("belt", "common"),
}

_MOD_QUOTED_RE = re.compile(r'"([^"]+)"')


def _parse_mod_line(line: str) -> tuple[str, list[str]]:
    """HasExplicitMod 라인 → (kind, mod_names). Phase D 동일 로직."""
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
    """NeverSink filter → tier_token → {mod_kind: [mods]}."""
    blocks: dict[str, dict] = {}
    tier_re = re.compile(r"\$tier->(\w+)")
    block_re = re.compile(
        r"^(Show|Hide)[^\n]*\n((?:\t[^\n]*\n?|[ ]{4}[^\n]*\n?)+)",
        re.MULTILINE,
    )
    for match in block_re.finditer(content):
        header_start = match.start()
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


def _consolidate(raw_blocks: dict[str, dict]) -> dict[str, dict[str, dict[str, list[str]]]]:
    """tier 토큰 블록 → slot.axis 통합 (mod 리스트 union, 정렬)."""
    out: dict[str, dict[str, dict[str, list[str]]]] = {}
    for token, parsed in raw_blocks.items():
        slot, axis = _TIER_MAP[token]
        slot_dict = out.setdefault(slot, {})
        axis_dict = slot_dict.setdefault(axis, {})
        for kind, mods in parsed.items():
            merged = set(axis_dict.get(kind, [])) | set(mods)
            axis_dict[kind] = sorted(merged)
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
            "script": "scripts/extract_accessory_mod_tiers.py",
            "consolidation": (
                "amu_{1,2}core{attack,caster,dot} → amulet.{attack,caster,dot}; "
                "ring_{attack,caster,minion} → ring.{axis}; "
                "amu_exalter + belt_general → {amulet,belt}.common (damage 무관 공용 블록)"
            ),
            "slot_count": len(consolidated),
            "spot_check_status": (
                "skipped — NeverSink 8.19.0b curation trusted (Phase D 동일 정책). "
                "mod names are GGG game data, auto-synced from NeverSink 4h updates."
            ),
        },
        "slots": consolidated,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    total_mods = sum(
        len(m) for slot in consolidated.values()
        for axis in slot.values() for m in axis.values()
    )
    logger.info("Wrote %s — %d slots, %d total mod entries",
                OUTPUT.relative_to(ROOT), len(consolidated), total_mods)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
