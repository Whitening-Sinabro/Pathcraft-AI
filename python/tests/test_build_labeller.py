"""자동 레이블러 회귀 가드.

`data/builds/*.build.json` 실물 63건을 채점 코퍼스로 쓴다. 파일명에 정답 스킬이
들어 있어서(`3.22_detonate_dead_elementalist.<hash>.build.json`) 객관적 채점이 된다.

정확도 하한을 박아두는 이유: 휴리스틱을 건드렸을 때 조용히 나빠지는 것을 막기 위해서다.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from build_labeller import (  # noqa: E402
    _PROXY_DELIVERY,
    classify_damage,
    classify_defense,
    classify_delivery,
    classify_range,
    detect_main_skill,
    label_build,
)

CORPUS = sorted((ROOT / "data" / "builds").glob("*.build.json"))
# 파일명 약어 → 실제 젬 이름
ALIASES = {"srs": "summonragingspirit", "minionarmy": "raisespectre"}


def _norm(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def _expected_token(path: Path) -> str:
    token = _norm(path.name.split(".")[1])
    for short, full in ALIASES.items():
        token = token.replace(short, full)
    return token


def _core(gem_name: str) -> str:
    return _norm(re.sub(r"^(Vaal|Awakened)\s+", "", gem_name).split(" of ")[0])


@pytest.fixture(scope="module")
def labelled():
    out = []
    for path in CORPUS:
        data = json.loads(path.read_text(encoding="utf-8"))
        out.append((path, label_build(data)["entities"]["player"]))
    return out


def test_corpus_is_present():
    assert len(CORPUS) >= 60, "채점 코퍼스가 사라졌다"


def test_main_skill_accuracy_floor(labelled):
    hits = 0
    misses = []
    for path, player in labelled:
        skill = player["main_skill"] or ""
        core = _core(skill)
        if core and core in _expected_token(path):
            hits += 1
        else:
            misses.append(f"{path.name.split('.')[1]} -> {skill or '(없음)'}")
    accuracy = hits / len(labelled)
    assert accuracy >= 0.90, f"메인 스킬 정확도 {accuracy:.0%} < 90%. 불일치: {misses}"


def test_main_socket_group_is_the_dominant_evidence(labelled):
    """PoB 가 직접 표시한 그룹이 근거의 대부분이어야 한다 — 휴리스틱 의존도 감시."""
    sources = [player["main_skill_source"] for _, player in labelled]
    assert sources.count("main_socket_group") / len(sources) >= 0.90


def test_delivery_resolved_for_almost_every_build(labelled):
    resolved = [p for _, p in labelled if p["delivery"]["primary"]]
    assert len(resolved) / len(labelled) >= 0.95


def test_scaling_is_always_declared_unresolved(labelled):
    """이 소스로는 성장 축을 알 수 없다. 조용히 비우면 코퍼스가 오염된다."""
    for path, player in labelled:
        assert "scaling" in player["unresolved"], path.name


def test_proxy_range_implies_proxy_delivery(labelled):
    for path, player in labelled:
        if player["range"] != "proxy":
            continue
        assert player["delivery"]["primary"] in _PROXY_DELIVERY, path.name


def test_every_label_records_its_evidence(labelled):
    for path, player in labelled:
        assert player["main_skill_source"], path.name


# --------------------------------------------------------------------------
# 축 판정 단위 테스트 (코퍼스와 무관하게 규칙 자체를 고정)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("skill,expected_delivery,expected_range", [
    ("Cyclone", "attack", "melee"),
    ("Split Arrow", "attack", "projectile"),
    ("Fireball", "self_cast", "projectile"),
    ("Summon Raging Spirit", "minion", "proxy"),
    ("Ancestral Protector", "totem", "proxy"),
    ("Bear Trap", "trap", "proxy"),
    ("Stormblast Mine", "mine", "proxy"),
    ("Flame Link", "aura_link", "proxy"),
    ("Enfeeble", "curse", None),
    ("Determination", "aura_self", None),
])
def test_axis_rules_on_known_skills(skill, expected_delivery, expected_range):
    primary, _ = classify_delivery(skill)
    assert primary == expected_delivery, f"{skill}: delivery"
    assert classify_range(skill, primary)[0] == expected_range, f"{skill}: range"


def test_totem_and_minion_both_proxy_but_different_delivery():
    """택소노미 수용 기준 §9.2 를 레이블러 쪽에서도 지킨다."""
    totem_primary, _ = classify_delivery("Ancestral Protector")
    minion_primary, _ = classify_delivery("Summon Raging Spirit")
    assert totem_primary != minion_primary
    assert classify_range("Ancestral Protector", totem_primary)[0] == "proxy"
    assert classify_range("Summon Raging Spirit", minion_primary)[0] == "proxy"


# --------------------------------------------------------------------------
# defense 축
# --------------------------------------------------------------------------

def test_defense_pool_resolved_for_almost_every_build(labelled):
    resolved = [p for _, p in labelled if p["defense"]["pool"]]
    assert len(resolved) / len(labelled) >= 0.95


def test_defense_pool_values_are_in_vocabulary(labelled):
    allowed = {"life", "es", "hybrid", "ci", None}
    for path, player in labelled:
        assert player["defense"]["pool"] in allowed, path.name


def test_defense_layers_are_in_vocabulary(labelled):
    allowed = {"armour", "evasion", "block", "suppress", "recoup", "maxres"}
    for path, player in labelled:
        assert set(player["defense"]["layer"]) <= allowed, path.name


def test_ci_is_detected_by_life_equal_to_one():
    """CI 는 최대 생명력을 1 로 만든다 — 임계값이 아니라 게임 규칙이다."""
    assert classify_defense({"stats": {"life": 1, "energy_shield": 9000}})["pool"] == "ci"
    assert classify_defense({"stats": {"life": 5000, "energy_shield": 0}})["pool"] == "life"
    assert classify_defense({"stats": {"life": 4000, "energy_shield": 4000}})["pool"] == "hybrid"


def test_block_layer_requires_nonzero_block():
    assert "block" not in classify_defense({"stats": {"life": 5000, "block": 0}})["layer"]
    assert "block" in classify_defense({"stats": {"life": 5000, "block": 40}})["layer"]


def test_defense_survives_missing_stats():
    result = classify_defense({})
    assert result["pool"] is None
    assert result["layer"] == []


def test_weapon_is_always_declared_unresolved(labelled):
    """무기 축은 아직 안 붙였다 — 조용히 빈 값이 채워지는 것을 막는다."""
    for path, player in labelled:
        assert "weapon" in player["unresolved"], path.name


def test_damage_unresolved_flag_matches_element(labelled):
    """원소를 못 잡았으면 반드시 unresolved 에 남아야 한다."""
    for path, player in labelled:
        has_element = bool(player["damage"]["element"]["primary"])
        assert has_element != ("damage" in player["unresolved"]), path.name


def test_detect_main_skill_reports_reason_when_empty():
    skill, source = detect_main_skill({})
    assert skill is None
    assert source == "no_skill_groups"


# --------------------------------------------------------------------------
# damage 축 + aoe 후보
# --------------------------------------------------------------------------

@pytest.mark.parametrize("skill,element", [
    ("Fireball", "fire"),
    ("Ice Nova", "cold"),
    ("Arc", "lightning"),
    ("Essence Drain", "chaos"),
])
def test_element_from_skill_types(skill, element):
    assert classify_damage(skill)["element"]["primary"] == element


def test_physical_attack_element_stays_unresolved():
    """공격의 물리 피해는 스킬이 아니라 무기에서 온다 — GGPK 에 통합 Physical 타입이 없다."""
    result = classify_damage("Heavy Strike")
    assert result["resolved"] is False
    assert result["element"]["primary"] is None


def test_dot_skill_gets_dot_form():
    assert "dot" in classify_damage("Essence Drain")["form"]


def test_area_skill_narrows_range_to_two_candidates():
    """GGPK 는 자기중심/원격 aoe 를 가르지 않는다. 확정하지 말고 후보만 좁힌다."""
    value, candidates = classify_range("Firestorm", "self_cast")
    assert value is None
    assert candidates == ["aoe_self", "aoe_remote"]


def test_confirmed_range_has_no_candidates():
    for skill, delivery in (("Cyclone", "attack"), ("Split Arrow", "attack")):
        value, candidates = classify_range(skill, delivery)
        assert value is not None and candidates == []


def test_damage_resolution_rate(labelled):
    resolved = [p for _, p in labelled if p["damage"]["element"]["primary"]]
    assert len(resolved) / len(labelled) >= 0.55


def test_range_is_confirmed_or_narrowed_for_most_builds(labelled):
    known = [p for _, p in labelled if p["range"] or p["range_candidates"]]
    assert len(known) / len(labelled) >= 0.80
