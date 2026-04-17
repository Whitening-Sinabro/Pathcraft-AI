"""`divcard_data.load_divcard_mapping` 스모크 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from divcard_data import load_divcard_mapping, reset_cache


def setup_function(_):
    reset_cache()


def test_load_returns_dict():
    mapping = load_divcard_mapping()
    assert isinstance(mapping, dict)
    # 2026-04-17 validate_divcard_mapping.py 검증 후 5건 stale 제거 → 16 엔트리
    assert len(mapping) >= 15, f"expected 15+ entries, got {len(mapping)}"


def test_known_entries_match_prior_hardcoded():
    """기존 `UNIQUE_TO_DIVCARD` 하드코딩과 정합 확인 — regression guard."""
    mapping = load_divcard_mapping()

    assert mapping["Mageblood"] == [{"card": "The Apothecary", "stack": 13}]
    assert mapping["Headhunter"] == [
        {"card": "The Doctor", "stack": 8},
        {"card": "The Fiend", "stack": 11},
    ]
    assert mapping["Death's Oath"] == [{"card": "The Oath", "stack": 6}]
    assert mapping["Forbidden Shako"] == [{"card": "The Dragon's Heart", "stack": 10}]


def test_entry_structure():
    """각 value는 [{"card": str, "stack": int}, ...] 형태여야 함."""
    mapping = load_divcard_mapping()
    for unique_name, entries in mapping.items():
        assert isinstance(entries, list), f"{unique_name}: value not list"
        for entry in entries:
            assert "card" in entry, f"{unique_name}: missing 'card'"
            assert "stack" in entry, f"{unique_name}: missing 'stack'"
            assert isinstance(entry["card"], str)
            assert isinstance(entry["stack"], int)
            assert entry["stack"] > 0


def test_cache_reused():
    m1 = load_divcard_mapping()
    m2 = load_divcard_mapping()
    assert m1 is m2


def test_build_extractor_get_target_divcards_regression():
    """`get_target_divcards`가 로더 경로로 동일 결과 반환."""
    reset_cache()
    from build_extractor import get_target_divcards

    result = get_target_divcards(["Mageblood", "Headhunter"])
    cards = {c["card"]: c["stack"] for c in result}
    assert cards["The Apothecary"] == 13
    assert cards["The Doctor"] == 8
    assert cards["The Fiend"] == 11
