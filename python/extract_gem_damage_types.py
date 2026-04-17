"""POB pob_skills_cache/*.lua → data/gem_damage_types.json (Phase E2).

Why POB and not GGPK? SkillType enum 매핑은 POB 커뮤니티 소스가 ground truth.
Phase B `extract_gem_weapon_reqs.py` 와 동일 캐시(data/pob_skills_cache/) 재활용.

Source: src/Data/Skills/*.lua (MIT). Game data © GGG. POB SkillType enum을
직접 플래그로 매핑한다 (Attack/Spell/DamageOverTime/CreatesMinion).

Output: data/gem_damage_types.json
  {
    "_meta": {...},
    "gems": {
      "<gem name>": {
        "attack": bool,    # SkillType.Attack
        "caster": bool,    # SkillType.Spell AND NOT SkillType.DamageOverTime (pure spell)
        "dot": bool,       # SkillType.DamageOverTime OR DegenOnlySpellDamage OR CausesBurning
        "minion": bool,    # SkillType.CreatesMinion
      }, ...
    }
  }

Note: caster와 dot은 서로 배타적이지 않음 (예: Righteous Fire는 spell + dot 모두 true).
damage_type_extractor에서 set union 처리.

Usage:
  python python/extract_gem_damage_types.py              # live fetch + cache write-through
  python python/extract_gem_damage_types.py --cache-only # 네트워크 없이 기존 캐시만
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

_POB_BASE = (
    "https://raw.githubusercontent.com/PathOfBuildingCommunity/"
    "PathOfBuilding/master/src/Data/Skills/"
)

_POB_FILES = (
    "act_str.lua",
    "act_dex.lua",
    "act_int.lua",
    "other.lua",
    "glove.lua",
    "sup_str.lua",
    "sup_dex.lua",
    "sup_int.lua",
)

# SkillType enum → damage axis
# Phase E1 실측 결과 (grep -hoE "SkillType\.\w+" *.lua | sort -u) 기반 확정.
_ATTACK_TYPES = frozenset(["Attack"])
_CASTER_TYPES = frozenset(["Spell"])
_DOT_TYPES = frozenset([
    "DamageOverTime",
    "DegenOnlySpellDamage",
    "CausesBurning",
])
_MINION_TYPES = frozenset(["CreatesMinion"])

# Lua block parsing (Phase B와 동일 패턴)
_SKILL_START_RE = re.compile(r'^skills\["([^"]+)"\]\s*=\s*\{', re.MULTILINE)
_TOP_LEVEL_CLOSE_RE = re.compile(r"^\}", re.MULTILINE)
_NAME_FIELD_RE = re.compile(r'^\s*name\s*=\s*"([^"]+)"', re.MULTILINE)
# skillTypes = { [SkillType.Spell] = true, [SkillType.Damage] = true, ... }
_SKILL_TYPES_BLOCK_RE = re.compile(
    r"skillTypes\s*=\s*\{([^}]*)\}", re.DOTALL
)
_SKILL_TYPE_ENTRY_RE = re.compile(r"SkillType\.(\w+)")


def iter_skill_blocks(text: str):
    """Yield (display_name, block_text) per skills entry. Phase B와 동일."""
    starts = list(_SKILL_START_RE.finditer(text))
    for i, m in enumerate(starts):
        block_start = m.end()
        next_start = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        window = text[block_start:next_start]
        close = _TOP_LEVEL_CLOSE_RE.search(window)
        block = window[: close.start()] if close else window
        name_match = _NAME_FIELD_RE.search(block)
        display = name_match.group(1) if name_match else m.group(1)
        yield display, block


def extract_skill_types(block: str) -> set[str]:
    """블록에서 SkillType.* 식별자 집합 추출 (set of enum name strings)."""
    wb = _SKILL_TYPES_BLOCK_RE.search(block)
    if not wb:
        return set()
    return set(_SKILL_TYPE_ENTRY_RE.findall(wb.group(1)))


def classify_damage_axes(skill_types: set[str]) -> dict[str, bool]:
    """SkillType set → {attack, caster, dot, minion} bool flags.

    Rules:
    - attack: has SkillType.Attack
    - caster: has SkillType.Spell
    - dot: has any of {DamageOverTime, DegenOnlySpellDamage, CausesBurning}
    - minion: has SkillType.CreatesMinion

    Note: caster와 dot 공존 가능 (RF 등). 소비처(damage_type_extractor)에서
    축별 set union으로 처리.
    """
    return {
        "attack": bool(skill_types & _ATTACK_TYPES),
        "caster": bool(skill_types & _CASTER_TYPES),
        "dot": bool(skill_types & _DOT_TYPES),
        "minion": bool(skill_types & _MINION_TYPES),
    }


def fetch(url: str, cache_dir: Path, cache_only: bool) -> str:
    name = url.rsplit("/", 1)[-1]
    cached = cache_dir / name
    if cache_only:
        if not cached.exists():
            raise FileNotFoundError(f"cache miss and --cache-only: {cached}")
        return cached.read_text(encoding="utf-8")
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "PathcraftAI/1.0"})
        r.raise_for_status()
    except requests.RequestException as e:
        if cached.exists():
            logger.warning("fetch failed (%s), using cached %s", e, cached)
            return cached.read_text(encoding="utf-8")
        raise
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_text(r.text, encoding="utf-8")
    return r.text


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-only", action="store_true")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parent.parent
    cache_dir = root / "data" / "pob_skills_cache"
    dst = root / "data" / "gem_damage_types.json"

    all_gems: dict[str, dict[str, bool]] = {}
    processed = 0
    with_any_axis = 0

    for fname in _POB_FILES:
        try:
            text = fetch(_POB_BASE + fname, cache_dir, args.cache_only)
        except (requests.RequestException, FileNotFoundError) as e:
            logger.error("skip %s: %s", fname, e)
            continue

        file_count = 0
        for name, block in iter_skill_blocks(text):
            processed += 1
            file_count += 1
            types = extract_skill_types(block)
            if not types:
                continue
            axes = classify_damage_axes(types)
            if not any(axes.values()):
                continue  # aura/buff only — no damage axis
            with_any_axis += 1
            # 같은 gem 중복 등장 시 axis OR 누적
            prev = all_gems.get(name)
            if prev is not None:
                for k in axes:
                    axes[k] = axes[k] or prev.get(k, False)
            all_gems[name] = axes
        logger.info("%s: %d skills parsed", fname, file_count)

    if not all_gems:
        logger.error("no gems extracted — check POB file format or network")
        return 1

    sorted_gems = {k: all_gems[k] for k in sorted(all_gems)}

    payload = {
        "_meta": {
            "source": "PathOfBuildingCommunity src/Data/Skills/*.lua (MIT). Game data © GGG.",
            "generator": "python/extract_gem_damage_types.py",
            "pob_files_used": list(_POB_FILES),
            "cache_dir": str(cache_dir.relative_to(root)).replace("\\", "/"),
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "skill_type_mapping": {
                "attack": sorted(_ATTACK_TYPES),
                "caster": sorted(_CASTER_TYPES),
                "dot": sorted(_DOT_TYPES),
                "minion": sorted(_MINION_TYPES),
            },
            "gem_count": len(sorted_gems),
            "processed_skills": processed,
            "notes": (
                "caster와 dot은 공존 가능 (예: Righteous Fire). "
                "damage_type_extractor에서 메인 스킬의 true flag 축을 union."
            ),
        },
        "gems": sorted_gems,
    }

    dst.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "wrote %s: %d gems with damage axis (processed %d total)",
        dst, len(sorted_gems), processed,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
