"""갑충석 계열 도출 회귀 가드.

핀을 믿지 않는다 — 매 실행 GGPK 에서 재도출해 핀과 대조한다.

이 파일이 지키는 핵심 주장 두 가지:
1. 'Scarab' 이름 196개 중 현행은 130개뿐이고, 나머지 66개의 정체가 밝혀져 있다
   (구 티어 64 + 갑충석 아닌 것 2). "미분류"로 남겨두면 필터가 없는 아이템을 취급한다.
2. 계열 → 아틀라스 메커니즘 조인은 **표시 이름으로는 불가능**하다. Anarchy=Rogue Exiles,
   Domination=Shrines 는 앵커 노드 id 의 내부 토큰으로만 붙는다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from derive_scarab_families import (  # noqa: E402
    EXPECTED,
    LEGACY_PREFIX,
    LEGACY_TIERS,
    OUT_PATH,
    SCARAB_INHERITS,
    atlas_mechanic_index,
    build_payload,
    join_to_mechanic,
    load_table,
    slugify,
)
from derived_data_inventory import ggpk_fingerprint  # noqa: E402

GAME_DATA = ROOT / "data" / "game_data"
REGENERATE = "python python/scripts/derive_scarab_families.py --write 로 재생성할 것"

pytestmark = pytest.mark.skipif(
    not (GAME_DATA / "Scarabs.json").exists(),
    reason="data/game_data/ 없음 (GGPK 추출본은 gitignore)",
)


@pytest.fixture(scope="module")
def pinned():
    return json.loads(OUT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def derived():
    return build_payload()


# --- 핀 대조 -------------------------------------------------------------------


def test_pin_matches_current_ggpk(pinned, derived):
    assert pinned["families"] == derived["families"], REGENERATE
    assert pinned["retired"] == derived["retired"], REGENERATE


def test_pin_fingerprint_matches_current_ggpk(pinned):
    assert pinned["ggpk_fingerprint"] == ggpk_fingerprint(), (
        f"GGPK 가 재추출됐다. {REGENERATE}"
    )


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_measured_counts_match_league_values(derived, key):
    measured = {
        "families": derived["family_count"],
        "active_variants": derived["active_variant_count"],
        "retired": derived["retired_count"],
    }[key]
    assert measured == EXPECTED[key], (
        f"{key} 이 {EXPECTED[key]} → {measured} 로 바뀌었다. "
        "리그 변경이면 패치노트 확인 후 EXPECTED 를 갱신할 것."
    )


# --- 196 = 130 + 66, 남는 것 없음 -----------------------------------------------


def test_every_scarab_named_item_is_accounted_for(derived):
    """분류도 폐기도 아닌 갑충석이 남으면 안 된다 — 그게 '미분류 66' 의 정체였다."""
    base_items = load_table("BaseItemTypes")
    named = {b["Name"] for b in base_items if "Scarab" in b.get("Name", "")}

    active = {v for f in derived["families"].values() for v in f["variants"]}
    legacy = {
        f"{tier} {family}"
        for family, tiers in derived["retired"]["legacy_tier_scarabs"]["families"].items()
        for tier in tiers
    }
    not_scarab = {x["name"] for x in derived["retired"]["not_scarab_items"]}

    unaccounted = named - active - legacy - not_scarab
    assert not unaccounted, f"어디에도 안 잡힌 갑충석: {sorted(unaccounted)}"
    assert len(named) == len(active) + len(legacy) + len(not_scarab)


def test_active_scarabs_carry_no_legacy_tier_prefix(derived):
    """현행 130종에 티어 접두사가 하나라도 있으면 '구 체계' 판정 근거가 무너진다."""
    tainted = [
        v for f in derived["families"].values() for v in f["variants"] if LEGACY_PREFIX.match(v)
    ]
    assert not tainted, f"현행 계열에 구 티어 접두사: {tainted}"


def test_legacy_tiers_form_a_complete_grid(derived):
    """4티어 × 16계열 = 64. 격자가 깨지면 '구 체계 일괄 폐기' 가정이 틀린 것이다."""
    legacy = derived["retired"]["legacy_tier_scarabs"]
    assert legacy["count"] == 64
    assert legacy["family_count"] == 16
    for family, tiers in legacy["families"].items():
        assert sorted(tiers) == sorted(LEGACY_TIERS), f"{family}: 티어가 빠졌다 {tiers}"


def test_non_scarab_items_are_excluded_by_inheritance_not_by_name(derived):
    """이름 규칙이 아니라 상속 루트로 갈라야 한다 — 이름만 보면 갑충석으로 오인한다."""
    base_items = load_table("BaseItemTypes")
    by_name = {b["Name"]: b for b in base_items if b.get("Name")}
    assert derived["retired"]["not_scarab_items"], "갑충석 아닌 항목 탐지가 죽었다"
    for entry in derived["retired"]["not_scarab_items"]:
        assert entry["inherits_from"] != SCARAB_INHERITS
        assert by_name[entry["name"]].get("InheritsFrom") == entry["inherits_from"]


# --- 아틀라스 메커니즘 조인 -----------------------------------------------------


@pytest.mark.parametrize("family,mechanic", [
    # 표시 이름으로는 절대 못 붙는 것들 — 내부 토큰 조인이 살아 있는지 보는 게 핵심이다.
    ("anarchy", "rogue_exiles"),
    ("domination", "shrines"),
    ("uniques", "unique_maps"),
    ("settlers", "settlers_of_kalguur"),
    # 단수/복수만 흔들리는 것들
    ("strongbox", "strongboxes"),
    ("mercenaries", "mercenaries"),
    # CamelCase 분리가 필요한 것
    ("divination_cards", "divination_cards"),
])
def test_family_joins_to_atlas_mechanic(derived, family, mechanic):
    assert derived["families"][family]["atlas_mechanic"] == mechanic


def test_joined_mechanics_all_exist_in_atlas_dataset(derived):
    """조인 결과가 실재하는 메커니즘이어야 한다 — 없는 키를 만들면 전략이 조용히 빈다."""
    mechanics = json.loads(
        (ROOT / "data" / "atlas_mechanics.json").read_text(encoding="utf-8")
    )["mechanics"]
    for key, info in derived["families"].items():
        if info["atlas_mechanic"]:
            assert info["atlas_mechanic"] in mechanics, f"{key}: 없는 메커니즘 {info['atlas_mechanic']}"


def test_unmapped_families_declare_a_reason(derived):
    """못 붙인 것을 조용히 null 로 두면 '아직 안 한 것' 과 '붙일 수 없는 것' 이 구분 안 된다."""
    unmapped = {k for k, v in derived["families"].items() if v["atlas_mechanic"] is None}
    assert unmapped == set(derived["unmapped_to_atlas_mechanic"])
    assert unmapped == {"influence", "misc", "uber"}
    for reason in derived["unmapped_to_atlas_mechanic"].values():
        assert reason and "미기재" not in reason


def test_join_does_not_guess_beyond_plural_forms():
    index = atlas_mechanic_index()
    assert join_to_mechanic("Bestiary", index) == "bestiary"
    assert join_to_mechanic("Misc", index) is None
    assert join_to_mechanic("완전히없는것", index) is None


def test_slugify_splits_camel_case():
    assert slugify("DivinationCards") == "divination_cards"
    assert slugify("Bestiary") == "bestiary"
    assert slugify("Strongbox") == "strongbox"


# --- provenance ----------------------------------------------------------------


def test_pin_declares_provenance(pinned):
    assert pinned["generated_by"] == "python/scripts/derive_scarab_families.py"
    assert "data/game_data/Scarabs.json" in pinned["source_tables"]
    assert pinned["ggpk_fingerprint"]
    assert "generated_at" not in pinned, "타임스탬프는 인벤토리 핀을 흔든다"
