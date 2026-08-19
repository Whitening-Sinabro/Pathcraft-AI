"""ActiveSkillTypes id 역산 회귀 가드.

GGPK 는 스킬 성질을 이름 없는 int 로만 준다. id 는 리그마다 밀릴 수 있으므로
pin 파일을 믿지 말고 **현재 GGPK 로 재도출한 값과 일치하는지** 매번 확인한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from derive_active_skill_types import (  # noqa: E402
    OUT_PATH,
    SEED_CASES,
    UNRESOLVED,
    _members,
    derive,
    load_skill_types,
)


@pytest.fixture(scope="module")
def table():
    return load_skill_types()


@pytest.fixture(scope="module")
def pinned():
    return json.loads(OUT_PATH.read_text(encoding="utf-8"))


def test_derivation_has_no_unsolved_seed_case(table):
    _, problems = derive(table)
    assert problems == [], "시드 도출 실패: " + " / ".join(problems)


def test_every_seed_case_resolves(table):
    resolved, _ = derive(table)
    assert set(resolved) == set(SEED_CASES), "일부 범주가 도출되지 않음"


def test_pin_matches_current_ggpk(table, pinned):
    """리그 업데이트로 id 가 밀리면 여기서 잡힌다."""
    resolved, _ = derive(table)
    pinned_ids = {k: v["id"] for k, v in pinned["types"].items()}
    assert pinned_ids == resolved, (
        "pin 이 현재 GGPK 와 불일치. "
        "python/scripts/derive_active_skill_types.py --write 로 재생성할 것"
    )


def test_attack_and_spell_are_mutually_exclusive(table, pinned):
    """PoE 불변식 — 이 배타성이 spell id 를 고른 근거다."""
    attack = set(_members(table, pinned["types"]["attack"]["id"]))
    spell = set(_members(table, pinned["types"]["spell"]["id"]))
    assert attack & spell == set()


def test_link_id_is_exactly_the_six_link_skills(table, pinned):
    members = set(_members(table, pinned["types"]["link"]["id"]))
    assert members == {
        "Flame Link", "Soul Link", "Protective Link",
        "Vampiric Link", "Destructive Link", "Intuitive Link",
    }


@pytest.mark.parametrize("category,must_contain,must_not_contain", [
    ("totem", "Ancestral Protector", "Fireball"),
    ("trap", "Bear Trap", "Stormblast Mine"),
    ("mine", "Stormblast Mine", "Bear Trap"),
    ("curse", "Enfeeble", "Grace"),
    ("aura", "Determination", "Enfeeble"),
    ("minion", "Raise Zombie", "Cyclone"),
    ("melee", "Cyclone", "Split Arrow"),
    ("projectile", "Split Arrow", "Ground Slam"),
])
def test_category_membership_is_pure(table, pinned, category, must_contain, must_not_contain):
    members = set(_members(table, pinned["types"][category]["id"]))
    assert must_contain in members, f"{category}: {must_contain} 누락"
    assert must_not_contain not in members, f"{category}: {must_not_contain} 오염"


def test_curse_and_aura_do_not_overlap(table, pinned):
    curse = set(_members(table, pinned["types"]["curse"]["id"]))
    aura = set(_members(table, pinned["types"]["aura"]["id"]))
    assert curse & aura == set()


def test_trap_and_mine_do_not_overlap(table, pinned):
    trap = set(_members(table, pinned["types"]["trap"]["id"]))
    mine = set(_members(table, pinned["types"]["mine"]["id"]))
    assert trap & mine == set()


def test_unresolved_axes_are_declared_not_guessed(pinned):
    """이 소스로 못 얻는 것을 명시한다 — 조용히 빠지면 레이블러가 틀린 값을 채운다."""
    assert set(pinned["unresolved"]) == set(UNRESOLVED)
    for axis in ("aoe", "channelled", "trigger"):
        assert axis in pinned["unresolved"]
        assert pinned["unresolved"][axis], f"{axis}: 미해결 사유가 비어 있음"


def test_pin_records_provenance(pinned):
    assert pinned["source_table"] == "data/game_data/ActiveSkills.json"
    assert pinned["skills_with_display_name"] > 1000
    for info in pinned["types"].values():
        assert info["member_count"] > 0
        assert info["sample"]
