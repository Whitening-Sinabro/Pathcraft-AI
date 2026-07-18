# -*- coding: utf-8 -*-
"""
게임 데이터 프로바이더 — 추출된 .datc64 JSON을 로드하고 크로스레퍼런스 해결

사용법:
    from game_data_provider import GameData
    gd = GameData()
    info = gd.get_gem_info("Fireball")
    rewards = gd.get_quest_gems("Witch")
    context = gd.build_context_for_coach(build_data)
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("game_data")

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
GAME_DATA_DIR_POE1 = DATA_ROOT / "game_data"
GAME_DATA_DIR_POE2 = DATA_ROOT / "game_data_poe2"

# Legacy alias — 기존 소비자 호환. coach_build 등 game 미지정 경로는 POE1 기본.
GAME_DATA_DIR = GAME_DATA_DIR_POE1


def _resolve_data_dir(game: str) -> Path:
    if game == "poe2":
        return GAME_DATA_DIR_POE2
    return GAME_DATA_DIR_POE1


CLASS_NAMES = {
    0: "Marauder", 1: "Witch", 2: "Ranger",
    3: "Duelist", 4: "Templar", 5: "Shadow", 6: "Scion",
}
CLASS_IDS = {v: k for k, v in CLASS_NAMES.items()}


class GameData:
    """추출된 게임 데이터를 로드하고 이름 기반 조회를 제공.

    game="poe1" (기본): data/game_data/ (POE1 BaseItemTypes/SkillGems/QuestRewards/Maps)
    game="poe2": data/game_data_poe2/ (POE2 동일 테이블, Huntress/Druid 포함)

    data_dir 을 명시적으로 전달하면 game 파라미터 무시하고 그 경로 사용.
    """

    def __init__(self, data_dir: Optional[Path] = None, game: str = "poe1"):
        self.game = game
        self.data_dir = data_dir or _resolve_data_dir(game)
        self._items: list = []
        self._gems: list = []
        self._quest_rewards: list = []
        self._maps: list = []
        self._gem_by_name: dict = {}
        self._item_name_idx: dict = {}
        self._ggpk_index = None
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return
        self._loaded = True

        self._items = self._load_json("BaseItemTypes.json")
        self._gems = self._load_json("SkillGems.json")
        self._quest_rewards = self._load_json("QuestRewards.json")
        self._maps = self._load_json("Maps.json")

        try:
            from ggpk_index import GGPKIndex
            self._ggpk_index = GGPKIndex(
                game=self.game,
                data_root=DATA_ROOT,
                game_data_dir=self.data_dir,
            )
        except ImportError:
            self._ggpk_index = None

        # 아이템 이름 → 인덱스 매핑
        for i, item in enumerate(self._items):
            name = item.get("Name", "")
            if name:
                self._item_name_idx[name] = i

        # 젬 이름 → 젬 데이터 매핑 (BaseItemTypes에서 이름 해석)
        # POE1 SkillGems: BaseItemTypesKey
        # POE2 SkillGems: BaseItemType (이름 단축)
        self._gem_item_indices: set[int] = set()
        for gem in self._gems:
            idx = gem.get("BaseItemTypesKey", gem.get("BaseItemType", -1))
            if 0 <= idx < len(self._items):
                item = self._items[idx]
                name = item.get("Name", "")
                gem["_name"] = name
                gem["_drop_level"] = item.get("DropLevel", 0)
                gem["_id"] = item.get("Id", "")
                self._gem_item_indices.add(idx)
                if name:
                    self._gem_by_name[name.lower()] = gem

        logger.info(
            "GameData 로드: items=%d, gems=%d, quest_rewards=%d, maps=%d",
            len(self._items), len(self._gems), len(self._quest_rewards), len(self._maps),
        )

    def _load_json(self, filename: str) -> list:
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning("게임 데이터 없음: %s", filepath)
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_gem_info(self, gem_name: str) -> Optional[dict]:
        """젬 이름으로 정보 조회. 대소문자 무시."""
        self._ensure_loaded()
        gem = self._gem_by_name.get(gem_name.lower())
        if not gem:
            return None
        return {
            "name": gem["_name"],
            "required_level": gem["_drop_level"],
            "is_support": gem.get("IsSupport", False),
            "is_vaal": gem.get("IsVaalVariant", False),
            "str_pct": gem.get("StrengthRequirementPercent", 0),
            "dex_pct": gem.get("DexterityRequirementPercent", 0),
            "int_pct": gem.get("IntelligenceRequirementPercent", 0),
        }

    def get_quest_gems(self, class_name: str) -> list[dict]:
        """클래스별 퀘스트 젬 보상 목록. 레벨 순으로 정렬."""
        self._ensure_loaded()
        class_id = CLASS_IDS.get(class_name)
        if class_id is None:
            return []

        rewards = []
        for qr in self._quest_rewards:
            chars = qr.get("Characters", [])
            if class_id not in chars:
                continue
            reward_idx = qr.get("Reward", -1)
            if reward_idx < 0 or reward_idx >= len(self._items):
                continue
            # 젬만 필터 (장비 보상 제외)
            if reward_idx not in self._gem_item_indices:
                continue
            item = self._items[reward_idx]
            name = item.get("Name", "")
            if not name:
                continue
            rewards.append({
                "gem": name,
                "level": qr.get("RewardLevel", 0),
            })

        # 같은 젬의 최소 레벨만 유지 (가장 빨리 사용 가능한 시점)
        earliest: dict[str, dict] = {}
        for r in rewards:
            key = r["gem"]
            if key not in earliest or r["level"] < earliest[key]["level"]:
                earliest[key] = r
        result = sorted(earliest.values(), key=lambda r: (r["level"], r["gem"]))
        return result

    def get_item_drop_level(self, item_name: str) -> Optional[int]:
        """아이템 이름으로 드랍 레벨 조회."""
        self._ensure_loaded()
        idx = self._item_name_idx.get(item_name)
        if idx is None:
            return None
        return self._items[idx].get("DropLevel")

    def build_context_for_coach(self, build_data: dict) -> str:
        """빌드 데이터를 분석하여 코치용 게임 데이터 컨텍스트 생성."""
        self._ensure_loaded()
        if not self._gems:
            return ""

        parts = []

        # 1. 빌드에 사용된 젬 정보
        gem_names = self._extract_gem_names(build_data)
        if gem_names:
            gem_infos = []
            for name in gem_names:
                info = self.get_gem_info(name)
                if info:
                    attr = []
                    if info["str_pct"]:
                        attr.append(f"STR{info['str_pct']}%")
                    if info["dex_pct"]:
                        attr.append(f"DEX{info['dex_pct']}%")
                    if info["int_pct"]:
                        attr.append(f"INT{info['int_pct']}%")
                    gem_infos.append({
                        "name": info["name"],
                        "required_level": info["required_level"],
                        "type": "Support" if info["is_support"] else "Skill",
                        "attributes": " ".join(attr),
                    })
            if gem_infos:
                parts.append(
                    "빌드 젬 실제 게임 데이터 (이 레벨 요구사항을 반드시 참고):\n"
                    + json.dumps(gem_infos, ensure_ascii=False, indent=2)
                )

        # 2. 빌드 젬의 퀘스트 가용 여부
        char_class = build_data.get("meta", {}).get("class", "")
        if char_class and gem_names:
            quest_gems = self.get_quest_gems(char_class)
            quest_lookup = {g["gem"]: g["level"] for g in quest_gems}

            availability = []
            for name in gem_names:
                info = self.get_gem_info(name)
                if not info:
                    continue
                quest_lv = quest_lookup.get(info["name"])
                availability.append({
                    "gem": info["name"],
                    "quest_available": quest_lv is not None,
                    "quest_level": quest_lv,
                    "gem_level_req": info["required_level"],
                })

            if availability:
                parts.append(
                    f"\n{char_class} 빌드 젬 퀘스트 가용 여부 (quest_available=false면 트레이드/다른 캐릭터 필요):\n"
                    + json.dumps(availability, ensure_ascii=False, indent=2)
                )

        # 3. 맵 티어 요약 (상위 티어 맵 목록)
        if self._maps:
            parts.append(self._build_map_summary())

        integrated_context = self._build_integrated_db_context(build_data)
        if integrated_context:
            parts.append(integrated_context)

        if not parts:
            return ""

        return "\n\n".join(parts)

    def _extract_gem_names(self, build_data: dict) -> list[str]:
        """빌드 데이터에서 사용된 젬 이름 추출."""
        names = set()

        def add_link_text(value: str) -> None:
            for part in value.replace(" - ", "|").split("|"):
                part = part.strip()
                if part:
                    names.add(part)

        stages = build_data.get("progression_stages", [])
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            gem_setups = stage.get("gem_setups", {})
            for setup_name, links in gem_setups.items():
                # setup_name이 젬 이름일 수 있음
                if isinstance(setup_name, str):
                    names.add(setup_name)
                # links가 리스트면 서포트 젬 목록
                if isinstance(links, list):
                    for link in links:
                        if isinstance(link, str):
                            names.add(link)
                        elif isinstance(link, dict):
                            name = link.get("name", link.get("gem", ""))
                            if name:
                                names.add(name)
                elif isinstance(links, dict):
                    for key in ("name", "gem", "links"):
                        value = links.get(key)
                        if isinstance(value, str):
                            add_link_text(value)
                elif isinstance(links, str):
                    add_link_text(links)
            for alt in (stage.get("alternate_gem_sets", {}) or {}).values():
                if not isinstance(alt, dict):
                    continue
                for setup_name, links in alt.items():
                    if isinstance(setup_name, str):
                        names.add(setup_name)
                    if isinstance(links, dict):
                        value = links.get("links")
                        if isinstance(value, str):
                            add_link_text(value)
                    elif isinstance(links, str):
                        add_link_text(links)
        return sorted(names)

    def _build_map_summary(self) -> str:
        """맵 티어별 요약 (코치 컨텍스트용)."""
        # Maps.json 필드 분석 — 간략한 티어 분포만
        return f"맵 데이터: {len(self._maps)}개 맵 로드됨 (상세 조회 가능)"

    def _build_integrated_db_context(self, build_data: dict) -> str:
        """GGPK 원천 + 기존 파생 DB 통합 조회 결과를 코치에 제공."""
        if self._ggpk_index is None:
            return ""
        context = self._ggpk_index.build_targeted_context(build_data)
        build_instance_summary = self._build_instance_summary(build_data)
        if not context.get("matched_gems") and not context.get("matched_items") and not build_instance_summary:
            return ""
        build_instance_brief = self._build_instance_coach_brief(build_instance_summary)

        # 프롬프트 오염 방지: 없는 항목은 앞쪽 일부만 보여준다. setup label이 섞일 수 있다.
        compact = {
            "game": context.get("game"),
            "build_instance_coach_brief": build_instance_brief,
            "catalog": context.get("catalog"),
            "build_instance_summary": build_instance_summary,
            "matched_gems": context.get("matched_gems", []),
            "matched_items": context.get("matched_items", []),
            "missing_gems_sample": context.get("missing_gems", [])[:8],
            "missing_items_sample": context.get("missing_items", [])[:8],
            "rule": (
                "이 블록은 GGPK 원천 테이블과 기존 파생 DB를 합친 사실 조회 결과다. "
                "여기에 없는 이름은 추측하지 말고 POB 원문 또는 레어 일반론으로 처리한다."
            ),
        }
        return (
            "통합 GGPK/기존 DB 조회 결과 (raw game_data + derived data; 확인된 사실만 사용):\n"
            + json.dumps(compact, ensure_ascii=False, indent=2)
        )

    @staticmethod
    def _build_instance_summary(build_data: dict) -> dict:
        """Compact BuildInstance view for prompts.

        The full BuildInstance can contain many item/mod joins. The prompt only
        needs the state axes that constrain coaching.
        """
        instance = build_data.get("build_instance")
        if not isinstance(instance, dict):
            try:
                from build_instance import build_instance_from_pob_data
                instance = build_instance_from_pob_data(build_data, include_ggpk_context=False)
            except Exception:
                return {}

        gem_state = instance.get("gem_state") or {}
        calc_state = instance.get("calc_state") or {}
        item_state = instance.get("item_state") or {}
        lenses = instance.get("lenses") or {}
        tree_state = instance.get("tree_state") or {}
        config_state = instance.get("config_state") or {}
        readiness = instance.get("readiness") or {}
        slot_mod_summaries = []
        for item in (item_state.get("slots") or [])[:12]:
            if not isinstance(item, dict):
                continue
            slot_mod_summaries.append({
                "slot": item.get("slot"),
                "name": item.get("name"),
                "rarity": item.get("rarity"),
                "base_type": item.get("base_type"),
                "mod_source": item.get("mod_source"),
                "mod_summary": item.get("mod_summary") or {},
                "affix_pressure": item.get("affix_pressure") or {},
                "ggpk_join_status": (item.get("ggpk_mod_context") or {}).get("join_status"),
            })
        return {
            "identity": instance.get("identity") or {},
            "main_skill_group": gem_state.get("main_skill_group"),
            "gem_counts": gem_state.get("counts") or {},
            "raw_available": (instance.get("source") or {}).get("raw_available"),
            "calc_state": {
                "dps": calc_state.get("dps"),
                "life": calc_state.get("life"),
                "energy_shield": calc_state.get("energy_shield"),
                "ehp": calc_state.get("ehp"),
                "resistances": calc_state.get("resistances"),
                "flags": calc_state.get("flags"),
            },
            "gear_pressure": (item_state.get("gear_pressure") or {}),
            "item_mod_summary": item_state.get("mod_summary") or {},
            "slot_mod_summaries": slot_mod_summaries,
            "readiness": readiness,
            "t16_readiness_inputs": (lenses.get("t16_readiness_inputs") or {}),
            "tree_parse_status": tree_state.get("parse_status"),
            "config_raw_present": config_state.get("raw_config_present"),
            "config_raw_input_keys": sorted((config_state.get("raw_inputs") or {}).keys())[:12],
        }

    @staticmethod
    def _build_instance_coach_brief(summary: dict) -> dict:
        """Small high-signal BuildInstance extract for the LLM to cite first."""
        if not isinstance(summary, dict):
            return {}
        gear_pressure = summary.get("gear_pressure") or {}
        item_mod_summary = summary.get("item_mod_summary") or {}
        totals = (
            gear_pressure.get("gear_numeric_totals")
            or (item_mod_summary.get("numeric_totals") if isinstance(item_mod_summary, dict) else {})
            or {}
        )
        suffix_pressure_slots = []
        for slot in summary.get("slot_mod_summaries") or []:
            if not isinstance(slot, dict):
                continue
            pressure = slot.get("affix_pressure") or {}
            categories = pressure.get("suffix_pressure_categories") or []
            if categories or pressure.get("likely_suffix_mods"):
                suffix_pressure_slots.append({
                    "slot": slot.get("slot"),
                    "name": slot.get("name"),
                    "rarity": slot.get("rarity"),
                    "likely_suffix_mods": pressure.get("likely_suffix_mods", 0),
                    "suffix_pressure_categories": categories,
                    "ggpk_join_status": slot.get("ggpk_join_status"),
                })
        return {
            "target_version": (summary.get("identity") or {}).get("target_version"),
            "main_skill": (summary.get("main_skill_group") or {}).get("active_gem"),
            "gear_numeric_totals": totals,
            "unique_jewellery_slots": gear_pressure.get("unique_jewellery_slots", []),
            "rare_likely_prefix_mods": gear_pressure.get("rare_likely_prefix_mods", 0),
            "rare_likely_suffix_mods": gear_pressure.get("rare_likely_suffix_mods", 0),
            "readiness_overall": (summary.get("readiness") or {}).get("overall", {}),
            "readiness_defense": {
                "status": ((summary.get("readiness") or {}).get("defense") or {}).get("status"),
                "reasons": (((summary.get("readiness") or {}).get("defense") or {}).get("reasons") or [])[:5],
                "next_actions": (((summary.get("readiness") or {}).get("defense") or {}).get("next_actions") or [])[:4],
            },
            "readiness_bossing": {
                "status": ((summary.get("readiness") or {}).get("bossing") or {}).get("status"),
                "reasons": (((summary.get("readiness") or {}).get("bossing") or {}).get("reasons") or [])[:5],
                "next_actions": (((summary.get("readiness") or {}).get("bossing") or {}).get("next_actions") or [])[:4],
            },
            "suffix_pressure_slots": suffix_pressure_slots[:8],
            "must_use_rule": (
                "When discussing weaknesses, gear upgrades, and resistance/suppression fixes, cite these deterministic "
                "BuildInstance numbers before generic advice. Unique jewellery is locked and does not provide rare suffix room."
            ),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    gd = GameData()

    # 젬 조회 테스트
    for gem in ["Fireball", "Essence Drain", "Cyclone", "Multistrike Support"]:
        info = gd.get_gem_info(gem)
        if info:
            logger.info("%s: Lv%d %s %s", info["name"], info["required_level"],
                        "Support" if info["is_support"] else "Skill",
                        f"STR{info['str_pct']}% DEX{info['dex_pct']}% INT{info['int_pct']}%")
        else:
            logger.info("%s: NOT FOUND", gem)

    # 퀘스트 보상 테스트
    for cls in ["Witch", "Marauder", "Ranger"]:
        rewards = gd.get_quest_gems(cls)
        logger.info("\n%s quest gems (%d):", cls, len(rewards))
        for r in rewards[:10]:
            logger.info("  Lv%d %s", r["level"], r["gem"])
