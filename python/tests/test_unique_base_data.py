"""`unique_base_data.load_unique_base_mapping` 스모크 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unique_base_data import load_unique_base_mapping, reset_cache


def setup_function(_):
    reset_cache()


def test_load_returns_dict():
    mapping = load_unique_base_mapping()
    assert isinstance(mapping, dict)
    assert len(mapping) >= 20, f"expected 20+ entries, got {len(mapping)}"


def test_known_entries_match_prior_hardcoded():
    """기존 `UNIQUE_TO_BASE` 하드코딩과 정합 확인 — regression guard."""
    mapping = load_unique_base_mapping()

    assert mapping["Mageblood"] == "Heavy Belt"
    assert mapping["Headhunter"] == "Leather Belt"
    assert mapping["Tabula Rasa"] == "Simple Robe"
    assert mapping["Kaom's Heart"] == "Glorious Plate"
    assert mapping["Aegis Aurora"] == "Champion Kite Shield"


def test_entry_structure():
    """각 value는 비어있지 않은 base name 문자열이어야 함."""
    mapping = load_unique_base_mapping()
    for unique_name, base in mapping.items():
        assert isinstance(base, str), f"{unique_name}: base not str"
        assert base.strip(), f"{unique_name}: empty base"


def test_cache_reused():
    m1 = load_unique_base_mapping()
    m2 = load_unique_base_mapping()
    assert m1 is m2


def test_get_chanceable_bases_regression():
    """`get_chanceable_bases`가 로더 경로로 동일 결과 반환."""
    reset_cache()
    from build_extractor import get_chanceable_bases

    result = get_chanceable_bases(["Mageblood", "Tabula Rasa", "UnknownUnique"])
    bases = {r["base"]: r["unique"] for r in result}
    assert bases["Heavy Belt"] == "Mageblood"
    assert bases["Simple Robe"] == "Tabula Rasa"
    assert len(result) == 2  # UnknownUnique 폴백으로 제외


def test_extract_build_unique_bases_fallback():
    """POB base_type 누락 시 unique_base_mapping 폴백 — coaching 전용 경로."""
    reset_cache()
    from build_extractor import extract_build_unique_bases

    coaching = {"key_items": [{"name": "Mageblood"}, {"name": "Headhunter"}]}
    result = extract_build_unique_bases({}, coaching_data=coaching)
    assert "Heavy Belt" in result
    assert "Leather Belt" in result
