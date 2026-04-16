"""One-shot: audit every player-usable skill gem's WeaponRestriction in GGPK.

Writes _analysis/gem_weapon_restriction_audit.md with a full table of skills,
their DisplayedName, Id, raw restriction keys, and resolved Class names.

Purpose: let the user eyeball the data against the actual POE1 game so we
don't ship gem_weapon_requirements.json with bad assumptions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

ROOT = Path(__file__).resolve().parent.parent

INHERIT_MAP = {
    "AbstractClaw": "Claws",
    "AbstractDagger": "Daggers",
    "AbstractRuneDagger": "Rune Daggers",
    "AbstractOneHandAxe": "One Hand Axes",
    "AbstractOneHandMace": "One Hand Maces",
    "AbstractSceptre": "Sceptres",
    "AbstractOneHandSword": "One Hand Swords",
    "AbstractOneHandSwordThrusting": "Thrusting One Hand Swords",
    "AbstractWand": "Wands",
    "AbstractBow": "Bows",
    "AbstractFishingRod": "Fishing Rods",
    "AbstractStaff": "Staves",
    "AbstractWarstaff": "Warstaves",
    "AbstractTwoHandAxe": "Two Hand Axes",
    "AbstractTwoHandMace": "Two Hand Maces",
    "AbstractTwoHandSword": "Two Hand Swords",
}

PHYS_CLASSES = frozenset([
    "Bows", "Claws", "Daggers",
    "One Hand Axes", "One Hand Maces", "One Hand Swords", "Thrusting One Hand Swords",
    "Two Hand Axes", "Two Hand Maces", "Two Hand Swords",
    "Wands", "Warstaves",
])

# Variant suffixes we skip for the "player-facing" view
SKIP_ID_SUFFIXES = ("_old", "_alt_x", "_alt_y", "_monster", "_totem", "_vaal", "_royale")
SKIP_ID_SUBSTRS = ("_trap_", "_mine_", "_ghost_", "_npc_", "_cloned_", "_triggered_")


def classify(inherits: str) -> str | None:
    return INHERIT_MAP.get(inherits.rsplit("/", 1)[-1])


def build_key_to_class(base_items: list[dict]) -> dict[int, str]:
    out: dict[int, str] = {}
    for it in base_items:
        if not isinstance(it, dict):
            continue
        cls = classify(it.get("InheritsFrom") or "")
        if cls is None:
            continue
        k = it.get("ItemClassesKey")
        if isinstance(k, int):
            out[k] = cls
    return out


def load() -> tuple[list[dict], list[dict]]:
    ask = json.loads((ROOT / "data/game_data/ActiveSkills.json").read_text("utf-8"))
    bt = json.loads((ROOT / "data/game_data/BaseItemTypes.json").read_text("utf-8"))
    return ask, bt


def is_player_variant(sk: dict) -> bool:
    sid = sk.get("Id") or ""
    if not sid:
        return False
    if any(sid.endswith(suf) for suf in SKIP_ID_SUFFIXES):
        return False
    if any(sub in sid for sub in SKIP_ID_SUBSTRS):
        return False
    name = sk.get("DisplayedName") or ""
    if not name.strip():
        return False
    return True


def main() -> None:
    ask, bt = load()
    k2c = build_key_to_class(bt)

    rows: list[tuple[str, str, list[int], list[str], list[str]]] = []
    spell_count = 0
    skipped_variants = 0
    for sk in ask:
        if not isinstance(sk, dict):
            continue
        if not is_player_variant(sk):
            skipped_variants += 1
            continue
        raw = [x for x in (sk.get("WeaponRestriction_ItemClassesKeys") or []) if x != 0]
        if not raw:
            spell_count += 1
            continue
        resolved = [k2c.get(k, f"?{k}") for k in raw]
        phys = sorted(set(resolved) & PHYS_CLASSES)
        all_classes = sorted(set(resolved))
        rows.append((
            sk.get("DisplayedName") or "",
            sk.get("Id") or "",
            raw,
            all_classes,
            phys,
        ))

    rows.sort(key=lambda r: r[0].lower())

    out: list[str] = []
    out.append("# GGPK 전체 스킬젬 WeaponRestriction 감사\n")
    out.append("출처: `data/game_data/ActiveSkills.json` + `data/game_data/BaseItemTypes.json` (GGPK 추출본)\n")
    out.append(
        "필터 기준: player-facing 변형만 (변형/몬스터/토템/공격봇/트리거 id 제외)\n"
    )
    out.append(f"- WeaponRestriction 있는 스킬: **{len(rows)}개**")
    out.append(f"- WeaponRestriction 없는 스킬 (스펠/오라/버프): {spell_count}개")
    out.append(f"- 스킵된 변형/내부 엔트리: {skipped_variants}개\n")

    out.append("## 열 설명\n")
    out.append("- **Name**: DisplayedName (게임 내 이름)")
    out.append("- **Id**: ActiveSkills.Id (내부 ID)")
    out.append("- **All Classes**: WeaponRestriction → 모든 Class (Sceptre/Staff/Rune Dagger/Fishing Rod 포함)")
    out.append("- **Phys-only**: NeverSink 물리 12 Class 필터 적용 후 (PathcraftAI에서 실제 쓰는 값)")
    out.append("- **Raw keys**: 원본 ItemClassesKey 숫자\n")

    out.append("## ItemClassesKey 매핑 (참고)\n")
    out.append("```")
    for k in sorted(k2c.keys()):
        out.append(f"  {k:3d}: {k2c[k]}")
    out.append("```\n")

    out.append("## 전체 표\n")
    out.append("| Name | Id | All Classes | Phys-only | Raw |")
    out.append("|------|-----|-------------|-----------|-----|")
    for name, sid, raw, all_c, phys in rows:
        all_s = ", ".join(all_c) if all_c else "—"
        phys_s = ", ".join(phys) if phys else "∅"
        raw_s = str(raw)
        out.append(f"| {name} | `{sid}` | {all_s} | {phys_s} | {raw_s} |")

    target = ROOT / "_analysis/gem_weapon_restriction_audit.md"
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {target} ({target.stat().st_size} bytes, {len(rows)} rows)")


if __name__ == "__main__":
    main()
