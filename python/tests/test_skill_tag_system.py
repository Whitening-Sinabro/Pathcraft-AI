# -*- coding: utf-8 -*-
"""skill_tag_system 회귀 테스트.

목표:
- curated transition pattern 이 raw 노이즈보다 높은 우선순위를 가진다.
- 실제 로더가 curated overlay 파일을 병합한다.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skill_tag_system import SkillTagSystem, ActGuideSearcher  # noqa: E402


def _make_system(patterns: list[dict]) -> SkillTagSystem:
    system = SkillTagSystem.__new__(SkillTagSystem)
    system.SKILL_DATABASE = {}
    system.gem_levels = {}
    system.quest_rewards = {}
    system.vendor_recipes = []
    system.transition_patterns = patterns
    system.translations = {}
    system.reverse_translations = {}
    return system


def test_curated_pattern_weight_beats_raw_noise():
    system = _make_system([
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Galvanic Arrow",
            "source": "raw",
            "weight": 1,
        },
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "curated",
            "weight": 6,
        },
    ])

    recs = system.get_leveling_skill_for_build("Lightning Arrow", include_korean=False)

    assert recs[0]["skill"] == "Rain of Arrows"
    assert recs[0]["count"] == 6
    assert recs[0]["sources"] == ["curated"]


def test_class_hint_reorders_recommendations_toward_matching_class():
    system = _make_system([
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Galvanic Arrow",
            "source": "raw",
            "weight": 3,
            "class": "Templar",
        },
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "curated",
            "weight": 3,
            "class": "Ranger",
        },
    ])
    system.SKILL_DATABASE = {
        "rain_of_arrows": type("Skill", (), {"name": "Rain of Arrows"})(),
        "galvanic_arrow": type("Skill", (), {"name": "Galvanic Arrow"})(),
        "lightning_arrow": type("Skill", (), {"name": "Lightning Arrow"})(),
    }

    recs = system.get_leveling_skill_for_build(
        "Lightning Arrow",
        include_korean=False,
        class_name="Ranger",
    )

    assert recs[0]["skill"] == "Rain of Arrows"
    assert recs[0]["class"] == "Ranger"


def test_transition_info_uses_pattern_transition_point():
    system = _make_system([
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "curated",
            "weight": 5,
            "transition_point": "act_complete",
        },
    ])

    info = system.get_transition_info("Rain of Arrows", "Lightning Arrow")

    assert info["transition_point"] == "act_complete"
    assert info["recommended_level"] == 60


def test_ascendancy_hint_filters_conflicting_specific_patterns():
    system = _make_system([
        {
            "final_skill": "Penance Brand of Dissipation",
            "leveling_skill": "Storm Brand",
            "source": "curated",
            "weight": 5,
            "ascendancy": "Inquisitor",
        },
        {
            "final_skill": "Penance Brand of Dissipation",
            "leveling_skill": "Rolling Magma",
            "source": "curated",
            "weight": 4,
            "ascendancy": "Hierophant",
        },
    ])
    system.SKILL_DATABASE = {
        "storm_brand": type("Skill", (), {"name": "Storm Brand"})(),
        "rolling_magma": type("Skill", (), {"name": "Rolling Magma"})(),
        "penance_brand_of_dissipation": type("Skill", (), {"name": "Penance Brand of Dissipation"})(),
    }

    recs = system.get_leveling_skill_for_build(
        "Penance Brand of Dissipation",
        include_korean=False,
        ascendancy="Inquisitor",
    )

    assert recs[0]["skill"] == "Storm Brand"
    assert recs[0]["ascendancy"] == "Inquisitor"
    assert all(rec["skill"] != "Rolling Magma" for rec in recs)


def test_skill_names_are_canonicalized_from_noisy_patterns():
    system = _make_system([
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "rain of arrows",
            "source": "raw",
            "weight": 1,
        },
    ])
    system.SKILL_DATABASE = {
        "rain_of_arrows": type("Skill", (), {"name": "Rain of Arrows"})(),
        "lightning_arrow": type("Skill", (), {"name": "Lightning Arrow"})(),
    }

    recs = system.get_leveling_skill_for_build("Lightning Arrow", include_korean=False)

    assert recs[0]["skill"] == "Rain of Arrows"


def test_conflicting_raw_ascendancies_are_dropped():
    system = _make_system([
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "raw",
            "weight": 1,
            "ascendancy": "Deadeye",
        },
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "raw",
            "weight": 1,
            "ascendancy": "Inquisitor",
        },
    ])
    system.SKILL_DATABASE = {
        "rain_of_arrows": type("Skill", (), {"name": "Rain of Arrows"})(),
        "lightning_arrow": type("Skill", (), {"name": "Lightning Arrow"})(),
    }

    recs = system.get_leveling_skill_for_build("Lightning Arrow", include_korean=False)

    assert recs[0]["ascendancy"] is None


def test_curated_metadata_overrides_raw_ascendancy_noise():
    system = _make_system([
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "raw",
            "weight": 1,
            "ascendancy": "Inquisitor",
            "transition_point": "maps_entry",
        },
        {
            "final_skill": "Lightning Arrow",
            "leveling_skill": "Rain of Arrows",
            "source": "curated",
            "weight": 5,
            "ascendancy": None,
            "transition_point": "act_complete",
        },
    ])
    system.SKILL_DATABASE = {
        "rain_of_arrows": type("Skill", (), {"name": "Rain of Arrows"})(),
        "lightning_arrow": type("Skill", (), {"name": "Lightning Arrow"})(),
    }

    recs = system.get_leveling_skill_for_build("Lightning Arrow", include_korean=False)

    assert recs[0]["ascendancy"] is None
    assert recs[0]["transition_point"] == "act_complete"


def test_real_loader_merges_curated_overlay():
    system = SkillTagSystem()

    assert any(
        pattern.get("source") == "curated"
        and pattern.get("final_skill") == "Penance Brand of Dissipation"
        for pattern in system.transition_patterns
    )


def test_generate_leveling_summary_passes_class_context_to_recommendations():
    searcher = ActGuideSearcher.__new__(ActGuideSearcher)
    searcher.skill_system = _make_system([])
    searcher.skill_system.find_skill_by_name = lambda _: type("Skill", (), {"tags": [], "required_level": 28})()
    searcher.skill_system.get_leveling_skill_for_build = lambda *args, **kwargs: [
        {
            "skill": "Rain of Arrows",
            "transition_point": "maps_entry",
            "skill_kr": "비의 화살",
            "sources": ["curated"],
        }
    ]
    searcher.skill_system.get_transition_info = lambda *args, **kwargs: {
        "transition_point": "maps_entry",
        "recommended_level": 68,
        "tips": [],
    }
    searcher.skill_system.get_gem_quest_info = lambda *args, **kwargs: None
    searcher.skill_system.get_similar_skills = lambda *args, **kwargs: []
    searcher.skill_system.get_archetype_for_skill = lambda *args, **kwargs: "attack_ranged"
    searcher.skill_system.get_leveling_recipes = lambda: []
    searcher.skill_system.quest_rewards = []
    searcher.skill_system.vendor_recipes = []
    searcher.ARCHETYPE_TRANSLATIONS = {}

    captured = {}

    def _capture(skill_name, include_korean=True, class_name="", ascendancy=""):
        captured["class_name"] = class_name
        captured["ascendancy"] = ascendancy
        return [{
            "skill": "Rain of Arrows",
            "transition_point": "maps_entry",
            "skill_kr": "비의 화살",
            "sources": ["curated"],
        }]

    searcher.skill_system.get_leveling_skill_for_build = _capture

    summary = searcher.generate_leveling_guide_summary("Lightning Arrow", "Ranger", "Deadeye")

    assert summary["transition_info"]["leveling_skill"] == "Rain of Arrows"
    assert captured == {"class_name": "Ranger", "ascendancy": "Deadeye"}
