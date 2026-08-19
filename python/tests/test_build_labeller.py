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
    assert classify_range(skill, primary) == expected_range, f"{skill}: range"


def test_totem_and_minion_both_proxy_but_different_delivery():
    """택소노미 수용 기준 §9.2 를 레이블러 쪽에서도 지킨다."""
    totem_primary, _ = classify_delivery("Ancestral Protector")
    minion_primary, _ = classify_delivery("Summon Raging Spirit")
    assert totem_primary != minion_primary
    assert classify_range("Ancestral Protector", totem_primary) == "proxy"
    assert classify_range("Summon Raging Spirit", minion_primary) == "proxy"


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


def test_unresolved_declares_damage_and_weapon(labelled):
    """원소/무기는 PoB Lua skillTypes 가 있어야 한다 — 아직 안 붙였다고 명시."""
    for path, player in labelled:
        assert "damage" in player["unresolved"], path.name
        assert "weapon" in player["unresolved"], path.name


def test_detect_main_skill_reports_reason_when_empty():
    skill, source = detect_main_skill({})
    assert skill is None
    assert source == "no_skill_groups"
