# -*- coding: utf-8 -*-
"""build_coach OpenAI/GPT provider path tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _mk_build() -> dict:
    return {
        "meta": {"build_name": "OpenAI Test", "class_level": 90, "class": "Witch"},
        "stats": {"dps": 1, "life": 1, "energy_shield": 0},
        "progression_stages": [{
            "gem_setups": {"Fireball": {"links": "Fireball - Combustion Support"}},
            "gear_recommendation": {},
        }],
        "passives": {},
        "equipment": {},
    }


def _mk_result() -> str:
    return json.dumps({
        "build_summary": "test",
        "tier": "A",
        "strengths": [],
        "weaknesses": [],
        "leveling_guide": {"act1_4": "", "act5_10": "", "early_maps": "", "endgame": ""},
        "leveling_skills": {
            "damage_type": "fire",
            "recommended": {
                "name": "Fireball",
                "links_progression": [{"level_range": "1-10", "gems": ["Fireball"]}],
                "reason": "test",
                "transition_level": "",
            },
            "options": [],
            "skill_transitions": [],
        },
        "key_items": [],
        "aura_utility_progression": [],
        "build_rating": {
            "newbie_friendly": 0,
            "gearing_difficulty": 0,
            "play_difficulty": 0,
            "league_start_viable": 0,
            "hcssf_viability": 0,
        },
        "gear_progression": [],
        "map_mod_warnings": {"deadly": [], "dangerous": [], "caution": [], "regex_filter": ""},
        "variant_snapshots": [],
        "passive_priority": [],
        "danger_zones": [],
        "farming_strategy": "",
    })


def _make_mock_openai(text: str):
    usage = MagicMock()
    usage.input_tokens = 10
    usage.output_tokens = 20
    response = MagicMock()
    response.output_text = text
    response.usage = usage

    client = MagicMock()
    client.responses.create.return_value = response

    mock_openai = MagicMock()
    mock_openai.return_value = client
    return mock_openai, client


def test_default_model_uses_openai_responses_path():
    import build_coach

    mock_openai, client = _make_mock_openai(_mk_result())
    with patch.object(build_coach, "OpenAI", mock_openai):
        result = build_coach.coach_build(_mk_build())

    assert result["build_summary"] == "test"
    assert client.responses.create.call_count == 1
    call = client.responses.create.call_args.kwargs
    assert call["model"] == "gpt-5-nano"
    assert "POE1" in call["instructions"]
    assert "BuildInstance deterministic priority brief" in call["input"]
    assert "Fireball" in call["input"]
    assert "대표 빌드 코퍼스 대조 결과" in call["input"]


def test_gpt_nano_uses_openai_provider():
    import build_coach

    mock_openai, client = _make_mock_openai(_mk_result())
    with patch.object(build_coach, "OpenAI", mock_openai):
        build_coach.coach_build(_mk_build(), model="gpt-5-nano")

    assert client.responses.create.call_args.kwargs["model"] == "gpt-5-nano"


def test_codex_uses_openai_provider():
    import build_coach

    mock_openai, client = _make_mock_openai(_mk_result())
    with patch.object(build_coach, "OpenAI", mock_openai):
        build_coach.coach_build(_mk_build(), model="gpt-5.3-codex")

    assert client.responses.create.call_args.kwargs["model"] == "gpt-5.3-codex"


def test_build_instance_item_findings_are_applied_to_result():
    import build_coach

    build = _mk_build()
    build["progression_stages"][0]["gear_recommendation"] = {
        "Body Armour": {
            "rarity": "Rare",
            "name": "Rare Vaal Regalia",
            "base_type": "Vaal Regalia",
            "mods": ["+120 to maximum Life", "+45% to Fire Resistance"],
        },
        "Ring 1": {
            "rarity": "Unique",
            "name": "Storm Secret",
            "base_type": "Topaz Ring",
            "mods": ["Take 250 Lightning Damage when Herald of Thunder Hits an Enemy"],
        },
    }
    mock_openai, _client = _make_mock_openai(_mk_result())
    with patch.object(build_coach, "OpenAI", mock_openai):
        result = build_coach.coach_build(build, model="gpt-5-nano")

    findings = result["_build_instance_findings"]
    assert findings["gear_numeric_totals"]["maximum_life"] == 120
    assert findings["gear_numeric_totals"]["fire_resistance"] == 45
    assert findings["unique_jewellery_slots"] == ["Ring 1"]
    assert findings["readiness"]["defense"]["status"] == "blocked_until_verified"
    assert "BuildInstance 장비 수치 기준" in result["weaknesses"][0]
