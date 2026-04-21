# -*- coding: utf-8 -*-
"""Phase H3 — gear_normalizer 단위 테스트.

커버리지:
- normalize_item: alias_unique / alias_base / exact / fuzzy / descriptive / unmatched
- normalize_slot: canonical / alias / 한국어 / unmatched
- normalize_gear: gear_progression / key_items 인플레이스 + trace
- 괄호 주석 스트립 ("(6L)" 등)
- 자연어 설명 문구 경고 생략
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gear_normalizer import (  # noqa: E402
    normalize_item,
    normalize_slot,
    normalize_gear,
)


# ---------- normalize_item ----------


def test_item_exact_unique():
    canon, mt = normalize_item("Tabula Rasa")
    assert canon == "Tabula Rasa"
    assert mt == "exact_unique"


def test_item_exact_unique_case_insensitive():
    canon, mt = normalize_item("tabula rasa")
    assert canon == "Tabula Rasa"
    assert mt == "exact_unique"


def test_item_strip_annotation():
    # 괄호 주석은 매칭 전에 제거
    canon, mt = normalize_item("Tabula Rasa (6L)")
    assert canon == "Tabula Rasa"
    assert mt == "exact_unique"


def test_item_alias_unique():
    canon, mt = normalize_item("HH")
    assert canon == "Headhunter"
    assert mt == "alias_unique"


def test_item_alias_tabula():
    canon, mt = normalize_item("tabula")
    assert canon == "Tabula Rasa"
    assert mt == "alias_unique"


def test_item_alias_kaoms_heart_apostrophe_variants():
    canon, mt = normalize_item("kaoms heart")
    assert canon == "Kaom's Heart"
    assert mt == "alias_unique"


def test_item_alias_base():
    canon, mt = normalize_item("two toned boots")
    assert canon == "Two-Toned Boots"
    assert mt == "alias_base"


def test_item_exact_base():
    # alias 맵에 없는 베이스만 exact_base 로 분류 (alias 우선 정책)
    canon, mt = normalize_item("Full Plate")
    assert canon == "Full Plate"
    assert mt == "exact_base"


def test_item_fuzzy_unique_typo():
    # "Maegblood" (오타) → "Mageblood"
    canon, mt = normalize_item("Maegblood")
    assert canon == "Mageblood"
    assert mt == "fuzzy_unique"


def test_item_descriptive_rare():
    canon, mt = normalize_item("Rare Gloves with life and resists")
    assert canon is None
    assert mt == "descriptive"


def test_item_descriptive_korean():
    canon, mt = normalize_item("레어 헬멧 생명력+저항")
    assert canon is None
    assert mt == "descriptive"


def test_item_descriptive_any_slot():
    canon, mt = normalize_item("Any Ring")
    assert canon is None
    assert mt == "descriptive"


def test_item_unmatched_gibberish():
    # 설명 키워드 없고 매칭 실패 — unmatched
    canon, mt = normalize_item("Zorgblax Crown")
    assert canon is None
    assert mt == "unmatched"


def test_item_empty_and_none():
    assert normalize_item("")[0] is None
    assert normalize_item(None)[0] is None  # type: ignore[arg-type]


# ---------- normalize_slot ----------


def test_slot_canonical():
    canon, mt = normalize_slot("Body Armour")
    assert canon == "Body Armour"
    assert mt == "exact"


def test_slot_alias_chest():
    canon, mt = normalize_slot("chest")
    assert canon == "Body Armour"
    assert mt == "alias"


def test_slot_alias_main_hand():
    canon, mt = normalize_slot("main hand")
    assert canon == "Weapon"
    assert mt == "alias"


def test_slot_korean_skipped():
    # 한국어 = 설명 간주, 경고/교정 없음
    canon, mt = normalize_slot("장갑")
    assert canon is None
    assert mt == "descriptive"


def test_slot_unmatched():
    canon, mt = normalize_slot("Headgear Slot Extra")
    assert canon is None
    assert mt == "unmatched"


# ---------- normalize_gear (인플레이스) ----------


def test_gear_progression_item_and_slot_normalized():
    result = {
        "gear_progression": [
            {
                "slot": "chest",
                "phases": [
                    {"phase": "lv 1-40", "item": "tabula", "key_stats": [], "acquisition": "", "priority": ""},
                    {"phase": "lv 70+", "item": "kaoms heart", "key_stats": [], "acquisition": "", "priority": ""},
                ],
            },
        ],
    }
    warnings, trace = normalize_gear(result)
    assert result["gear_progression"][0]["slot"] == "Body Armour"
    assert result["gear_progression"][0]["phases"][0]["item"] == "Tabula Rasa"
    assert result["gear_progression"][0]["phases"][1]["item"] == "Kaom's Heart"
    assert len(trace) == 3
    assert warnings == []


def test_key_items_normalized_with_alternatives():
    result = {
        "key_items": [
            {
                "name": "HH",
                "slot": "belt",
                "alternatives": ["mageblood", "Rare Belt with life"],
                "importance": "",
                "acquisition": "",
                "ssf_difficulty": "",
            },
        ],
    }
    warnings, trace = normalize_gear(result)
    assert result["key_items"][0]["name"] == "Headhunter"
    assert result["key_items"][0]["slot"] == "Belt"
    assert result["key_items"][0]["alternatives"][0] == "Mageblood"
    # Rare Belt with life → 설명, 원본 유지
    assert result["key_items"][0]["alternatives"][1] == "Rare Belt with life"
    assert warnings == []


def test_gear_unmatched_reports_path():
    result = {
        "gear_progression": [
            {"slot": "Body Armour", "phases": [
                {"phase": "lv 1", "item": "Zorgblax Crown", "key_stats": [], "acquisition": "", "priority": ""},
            ]},
        ],
    }
    warnings, trace = normalize_gear(result)
    assert len(warnings) == 1
    assert "gear_progression[0].phases[0].item" in warnings[0]
    assert trace == []


def test_gear_descriptive_silent():
    result = {
        "gear_progression": [
            {"slot": "Gloves", "phases": [
                {"phase": "early", "item": "Rare Gloves with life", "key_stats": [], "acquisition": "", "priority": ""},
            ]},
        ],
    }
    warnings, trace = normalize_gear(result)
    assert warnings == []
    assert trace == []
    # 원본 유지
    assert result["gear_progression"][0]["phases"][0]["item"] == "Rare Gloves with life"


def test_gear_skips_unchanged():
    result = {
        "gear_progression": [
            {"slot": "Body Armour", "phases": [
                {"phase": "end", "item": "Kaom's Heart", "key_stats": [], "acquisition": "", "priority": ""},
            ]},
        ],
    }
    warnings, trace = normalize_gear(result)
    assert warnings == []
    assert trace == []  # 모두 canonical


def test_gear_missing_sections():
    result = {"build_summary": "x"}
    warnings, trace = normalize_gear(result)
    assert warnings == []
    assert trace == []


def test_gear_non_dict():
    warnings, trace = normalize_gear([])  # type: ignore[arg-type]
    assert warnings == []
    assert trace == []


def test_descriptive_keyword_no_unique_collision():
    # H3-2 회귀: descriptive 키워드가 실제 유니크 이름과 겹치지 않는지 보장
    # (현재 642 유니크 중 0 충돌. 변경 시 이 테스트 실패 → 재평가 트리거)
    import re, json
    from pathlib import Path
    u = json.loads(
        (Path(__file__).resolve().parent.parent.parent / "data" / "unique_base_mapping.json")
        .read_text(encoding="utf-8")
    )["unique_to_base"]
    DESC = {"rare", "magic", "any", "with", "or", "generic", "suitable",
            "appropriate", "placeholder", "tbd", "ilvl"}
    collisions = []
    for name in u:
        if any(ord(c) > 127 for c in name):
            continue
        words = re.findall(r"[A-Za-z]+", name.lower())
        if any(w in DESC for w in words):
            collisions.append(name)
    assert collisions == [], (
        f"descriptive 키워드가 유니크 이름과 충돌: {collisions}. "
        f"gear_normalizer.DESCRIPTIVE_ASCII_KEYWORDS 재검토 필요"
    )


def test_gear_trace_entries_have_required_fields():
    result = {
        "gear_progression": [
            {"slot": "head", "phases": [
                {"phase": "lv 1", "item": "goldrim", "key_stats": [], "acquisition": "", "priority": ""},
            ]},
        ],
    }
    _, trace = normalize_gear(result)
    # slot (alias) + item (alias)
    assert len(trace) == 2
    for entry in trace:
        assert "field" in entry
        assert "from" in entry
        assert "to" in entry
        assert "match_type" in entry
