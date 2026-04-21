"""pytest — scripts/refresh_valid_gems.py pollution 필터 단위 테스트.

실제 GGPK 데이터 없이 순수 함수 `_is_pollution` 과 suffix 유도 로직만 테스트.
"""
from __future__ import annotations

import sys
from pathlib import Path

# scripts/ 가 sys.path 에 없음 → 직접 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

from refresh_valid_gems import _is_pollution, derive_bare_support_forms


# === _is_pollution ===

def test_pollution_dots_rejected():
    assert _is_pollution("...", set()) is True


def test_pollution_camel_case_with_new_prefix_rejected():
    """NewPunishment 류 — 공백 없는 내부 ID."""
    assert _is_pollution("NewPunishment", {"NewPunishment", "Punishment"}) is True


def test_pollution_new_prefixed_duplicate_rejected():
    """'New Blade Vortex' 는 'Blade Vortex' 와 중복되는 dev iteration."""
    all_names = {"Blade Vortex", "New Blade Vortex"}
    assert _is_pollution("New Blade Vortex", all_names) is True


def test_pollution_new_prefixed_without_duplicate_kept():
    """dev iteration 이 아니라 진짜 'New X' 이름이면 (이론적 케이스) 유지.

    현재 GGPK 에 이런 엔트리는 없지만, 필터가 과잉 작동하지 않도록 보증.
    """
    all_names = {"New Feature Gem"}
    assert _is_pollution("New Feature Gem", all_names) is False


def test_pollution_legitimate_single_word_kept():
    """Cleave, Arc, Frenzy 같은 합법적 단어 젬은 pollution 아님."""
    assert _is_pollution("Cleave", {"Cleave"}) is False
    assert _is_pollution("Arc", {"Arc"}) is False
    assert _is_pollution("Punishment", {"Punishment"}) is False


def test_pollution_awakened_name_kept():
    assert _is_pollution("Awakened Added Fire Damage Support", {"Awakened Added Fire Damage Support"}) is False


def test_pollution_vaal_name_kept():
    assert _is_pollution("Vaal Cleave", {"Vaal Cleave", "Cleave"}) is False


# === derive_bare_support_forms (regression) ===

def test_bare_support_strips_suffix():
    out = derive_bare_support_forms({"Added Fire Damage Support"})
    assert out == {"Added Fire Damage"}


def test_bare_support_skips_non_support():
    """'Support' 안 붙은 젬은 그대로 둠 (이미 bare form)."""
    out = derive_bare_support_forms({"Cleave", "Arc"})
    assert out == set()


def test_bare_support_skips_collision_with_existing():
    """'Added Fire Damage Support' 의 bare 'Added Fire Damage' 가 이미 있으면 추가 안 함."""
    out = derive_bare_support_forms({"Added Fire Damage Support", "Added Fire Damage"})
    assert out == set()


def test_bare_support_handles_awakened_form():
    out = derive_bare_support_forms({"Awakened Added Fire Damage Support"})
    assert out == {"Awakened Added Fire Damage"}
