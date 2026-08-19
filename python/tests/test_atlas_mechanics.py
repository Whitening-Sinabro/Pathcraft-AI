"""아틀라스 메커니즘 도출 회귀 가드.

핀을 믿지 않는다 — 매 실행 GGPK 에서 재도출해 핀과 대조한다.
(`test_active_skill_types.py::test_pin_matches_current_ggpk` 와 같은 형태)

이 데이터셋은 레포에서 `ggpk_fingerprint` 를 갖는 첫 파생 파일이다. 그래서
`test_derived_data_inventory.py::test_stale_gate_vacuity_is_declared` 의 skip 이
여기서부터 풀린다.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from derive_atlas_mechanics import (  # noqa: E402
    EXPECTED_GROUP_COUNT,
    OUT_PATH,
    SENTINEL,
    build_payload,
    canonical_name,
    derive_mechanics,
    load_anchor_rows,
    slugify,
)
from derived_data_inventory import ggpk_fingerprint  # noqa: E402

PASSIVE_SKILLS = ROOT / "data" / "game_data" / "PassiveSkills.json"
REGENERATE = "python python/scripts/derive_atlas_mechanics.py --write 로 재생성할 것"

pytestmark = pytest.mark.skipif(
    not PASSIVE_SKILLS.exists(),
    reason="data/game_data/PassiveSkills.json 없음 (GGPK 추출본은 gitignore)",
)


@pytest.fixture(scope="module")
def pinned():
    return json.loads(OUT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def derived():
    return build_payload()


# --- 핀 대조 -------------------------------------------------------------------


def test_pin_matches_current_ggpk(pinned, derived):
    """리그 업데이트로 그룹이 늘거나 이름이 바뀌면 여기서 잡힌다."""
    assert pinned["mechanics"] == derived["mechanics"], REGENERATE


def test_pin_fingerprint_matches_current_ggpk(pinned):
    assert pinned["ggpk_fingerprint"] == ggpk_fingerprint(), (
        f"GGPK 가 재추출됐다. 이 파일을 다시 생성해야 한다. {REGENERATE}"
    )


def test_mechanic_count_matches_measured_league_value(derived):
    assert derived["mechanic_count"] == EXPECTED_GROUP_COUNT, (
        f"아틀라스 메커니즘이 {EXPECTED_GROUP_COUNT} → {derived['mechanic_count']} 로 바뀌었다. "
        "리그 변경이면 패치노트 확인 후 EXPECTED_GROUP_COUNT 를 갱신할 것."
    )


# --- 도출 규칙 ------------------------------------------------------------------


def test_group_zero_is_not_dropped_as_falsy(derived):
    """AtlasGroup 0 은 유효한 그룹(Abyss)이다. `if not group` 으로 거르면 통째로 사라진다."""
    groups = {m["atlas_group"] for m in derived["mechanics"].values()}
    assert 0 in groups
    assert derived["mechanics"]["abyss"]["atlas_group"] == 0


def test_sentinel_rows_are_excluded():
    rows = load_anchor_rows()
    assert rows, "앵커 행이 하나도 없다"
    assert all(r["AtlasGroup"] != SENTINEL for r in rows)


def test_canonical_name_is_deterministic():
    """이름이 갈리는 그룹(Map Boss / Map Bosses)에서 실행마다 다른 값이 나오면 핀이 흔들린다."""
    assert canonical_name(collections.Counter({"Map Bosses": 2, "Map Boss": 1})) == "Map Bosses"
    # 동률이면 사전순 — 임의 선택 금지
    assert canonical_name(collections.Counter({"B": 1, "A": 1})) == "A"


def test_name_variants_are_recorded_not_hidden(derived):
    """고른 이름만 남기고 나머지를 지우면, 다음 사람이 GGPK 를 다시 파야 한다."""
    variants = {k: v["name_variants"] for k, v in derived["mechanics"].items() if v["name_variants"]}
    assert variants.get("map_boss") == ["Map Boss", "Map Bosses"]


def test_slug_keys_are_unique_and_stable(derived):
    keys = list(derived["mechanics"])
    assert len(keys) == len(set(keys))
    assert all(k == slugify(k) for k in keys), "키가 슬러그 규칙을 벗어났다"
    assert slugify("The Searing Exarch") == "the_searing_exarch"
    assert slugify("Settlers of Kalguur") == "settlers_of_kalguur"


def test_every_name_comes_from_ggpk(derived):
    """이름을 하나라도 지어내면 안 된다."""
    ggpk_names = {r["Name"] for r in load_anchor_rows() if r.get("Name")}
    for info in derived["mechanics"].values():
        assert info["name"] in ggpk_names, f"{info['name']}: GGPK 에 없는 이름"


def test_anchor_counts_add_up(derived):
    total = sum(m["anchor_node_count"] for m in derived["mechanics"].values())
    assert total == derived["anchor_row_count"]


def test_derive_is_pure_for_same_input():
    rows = load_anchor_rows()
    assert derive_mechanics(rows) == derive_mechanics(rows)


# --- 기존 지식 파일과의 격차를 드러낸다 -----------------------------------------


KNOWN_TO_FARMING_KNOWLEDGE = {
    "essence", "harvest", "betrayal", "expedition", "legion",
    "breach", "delirium", "blight", "ritual", "boss_rush",
}


def test_boss_rush_is_not_a_ggpk_mechanic(derived):
    """`atlas_farming_knowledge.json` 의 boss_rush 는 GGPK 이름이 아니다.

    The Maven / The Shaper and Elder / Conquerors / The Searing Exarch /
    The Eater of Worlds 다섯을 한 덩어리로 뭉갠 것이라, 이걸 조인 키로 쓰면 전략이 안 붙는다.
    """
    assert "boss_rush" not in derived["mechanics"]
    for real in ("the_maven", "the_shaper_and_elder", "conquerors",
                 "the_searing_exarch", "the_eater_of_worlds"):
        assert real in derived["mechanics"], f"{real}: boss_rush 가 뭉갠 실제 그룹이 없다"


def test_farming_knowledge_coverage_gap_is_visible(derived):
    """10 vs 42 격차를 수치로 남긴다 — 눈에 안 보이면 아무도 안 메운다."""
    covered = KNOWN_TO_FARMING_KNOWLEDGE & set(derived["mechanics"])
    missing = set(derived["mechanics"]) - KNOWN_TO_FARMING_KNOWLEDGE
    assert len(covered) == 9, f"커버리지가 바뀌었다: {sorted(covered)}"
    assert len(missing) == 33, f"미커버 메커니즘 수가 바뀌었다: {len(missing)}"


# --- provenance ----------------------------------------------------------------


def test_pin_declares_provenance(pinned):
    assert pinned["generated_by"] == "python/scripts/derive_atlas_mechanics.py"
    assert pinned["source_table"] == "data/game_data/PassiveSkills.json"
    assert pinned["ggpk_fingerprint"]
    assert pinned["sentinel"] == SENTINEL


def test_pin_has_no_timestamp(pinned):
    """타임스탬프를 넣으면 데이터가 같아도 매 실행 해시가 바뀌어 인벤토리 핀이 흔들린다."""
    assert "generated_at" not in pinned
    assert "generated_date" not in pinned
