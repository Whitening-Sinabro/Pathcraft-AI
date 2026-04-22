"""
POE2 valid_gems.json 생성 — GGPK 추출 JSON 3개 조인.

입력:
  - data/game_data_poe2/BaseItemTypes.json : 젬 이름 (Id, Name)
  - data/game_data_poe2/SkillGems.json : 젬 메타 (MinLevelReq, GemType, GemColour)
  - data/game_data_poe2/ActiveSkills.json : 스킬 속성 (Id, DisplayedName, WeaponRequirements)

출력:
  - data/valid_gems_poe2.json : 화이트리스트 + 무기 제한 매핑

카테고리:
  - active: ItemClass=18 + InheritsFrom=ActiveSkillGem
  - support: Id 에 "Support" 포함
  - spirit: Id 에 "Spirit" 또는 "Persistent"
  - lineage: TBD (0.4 신규 endgame support — 별도 분류 필요, 현재는 support 에 섞임)

[DNT-UNUSED] 는 자동 제외.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

POE2_ROOT = Path(__file__).resolve().parents[1] / "data" / "game_data_poe2"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "valid_gems_poe2.json"


def load(name: str) -> list[dict]:
    with (POE2_ROOT / name).open(encoding="utf-8") as f:
        return json.load(f)


def extract_metadata_id(raw_id: str) -> str:
    """Metadata/Items/Gem/SkillGemTwister → SkillGemTwister"""
    return raw_id.rsplit("/", 1)[-1]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    base_items = load("BaseItemTypes.json")
    skill_gems = load("SkillGems.json")
    active_skills = load("ActiveSkills.json")

    # ActiveSkills: Id 기반 dict (weapon requirements 조인용)
    # Id 예: "twister", "whirling_slash"
    active_by_id: dict[str, dict] = {}
    for sk in active_skills:
        sid = (sk.get("Id") or "").lower()
        if sid:
            active_by_id[sid] = sk

    # BaseItemTypes 중 gem 카테고리만
    active_gems: list[dict] = []
    support_gems: list[dict] = []
    spirit_gems: list[dict] = []
    excluded_dnt = 0

    for it in base_items:
        raw_id = it.get("Id") or ""
        name = it.get("Name") or ""
        if "/Gem" not in raw_id:
            continue
        if "[DNT" in name:
            excluded_dnt += 1
            continue

        meta_id = extract_metadata_id(raw_id)  # SkillGemTwister 등
        # ActiveSkills 매칭 — meta_id 에서 "SkillGem" 제거 후 snake_case
        # e.g. SkillGemTwister → twister / SkillGemWhirlingSlash → whirling_slash
        if meta_id.startswith("SkillGem"):
            short = meta_id[len("SkillGem"):]
        elif meta_id.startswith("SupportGem"):
            short = meta_id[len("SupportGem"):]
        else:
            short = meta_id

        # CamelCase → snake_case
        snake: list[str] = []
        for i, ch in enumerate(short):
            if ch.isupper() and i > 0 and short[i - 1].islower():
                snake.append("_")
            snake.append(ch.lower())
        skill_id = "".join(snake)

        entry = {
            "name": name,
            "metadata_id": raw_id,
            "skill_id": skill_id,
        }

        active_match = active_by_id.get(skill_id)
        if active_match:
            entry["weapon_requirements"] = active_match.get("WeaponRequirements")
            entry["displayed_name"] = active_match.get("DisplayedName")

        if "Support" in raw_id:
            support_gems.append(entry)
        elif "Spirit" in raw_id or "Persistent" in raw_id:
            spirit_gems.append(entry)
        else:
            active_gems.append(entry)

    result = {
        "meta": {
            "source": "GGPK 2026-04-22 poe2 0.4.0d",
            "base_items_gem_count": len(active_gems) + len(support_gems) + len(spirit_gems),
            "skill_gems_row_count": len(skill_gems),
            "active_skills_row_count": len(active_skills),
            "excluded_dnt_unused": excluded_dnt,
        },
        "active": sorted(active_gems, key=lambda g: g["name"]),
        "support": sorted(support_gems, key=lambda g: g["name"]),
        "spirit": sorted(spirit_gems, key=lambda g: g["name"]),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(
        "valid_gems_poe2.json 생성: active=%d, support=%d, spirit=%d, dnt_excluded=%d",
        len(active_gems),
        len(support_gems),
        len(spirit_gems),
        excluded_dnt,
    )

    # Spear 스킬 검증 샘플
    spear_skills = [g for g in active_gems if g.get("weapon_requirements") == 25]
    logger.info("Spear 스킬 (WeaponRequirements=25): %d 개", len(spear_skills))
    for g in spear_skills[:15]:
        logger.info("  - %s (%s)", g["name"], g["skill_id"])


if __name__ == "__main__":
    main()
