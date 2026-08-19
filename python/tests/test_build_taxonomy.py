"""Build Taxonomy v2 — 어휘 무결성 + v1 이관 + 픽스처 수용 테스트.

스펙: ~/.claude/projects/D--Pathcraft-AI/2026-08-19-build-taxonomy-v2-spec.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_taxonomy import (
    V1_MECHANIC_TAGS,
    load_fixtures,
    load_taxonomy,
    migrate_v1_tag,
    validate_fixture,
)


# --------------------------------------------------------------------------
# 어휘 (taxonomy)
# --------------------------------------------------------------------------

def test_schema_is_v2():
    tax = load_taxonomy()
    assert tax["schema_version"] == "2.0"


def test_entities_are_the_four_locked_values():
    tax = load_taxonomy()
    assert tax["entities"] == ["player", "mercenary", "animate_guardian", "spectre"]


def test_delivery_has_the_ten_locked_values():
    tax = load_taxonomy()
    values = tax["identity_axes"]["delivery"]["values"]
    assert len(values) == 10
    # v1 이 표현하지 못했던 값들이 반드시 있어야 한다
    for missing_in_v1 in ("trap", "aura_self", "aura_link", "self_cast", "curse"):
        assert missing_in_v1 in values, f"{missing_in_v1} 누락 — v1 실패 사유가 그대로 남음"


def test_range_includes_proxy():
    tax = load_taxonomy()
    values = tax["identity_axes"]["range"]["values"]
    assert len(values) == 5
    assert "proxy" in values, "플레이어가 직접 교전하지 않는 빌드를 표현할 수 없음"


def test_damage_axis_is_primary_plus_secondary():
    tax = load_taxonomy()
    element = tax["identity_axes"]["damage"]["element"]
    assert element["selection"] == "primary_plus_secondary"
    assert set(element["values"]) == {"physical", "fire", "cold", "lightning", "chaos"}
    assert set(tax["identity_axes"]["damage"]["form"]["values"]) == {"hit", "dot", "ailment"}


def test_channelling_is_a_flag_not_a_delivery_value():
    tax = load_taxonomy()
    assert "is_channelled" in tax["flags"]
    assert "channel" not in tax["identity_axes"]["delivery"]["values"]


def test_constraint_carries_link_positioning_rules():
    """Flame Link: 'Link breaks if target leaves range or line of sight for 4 seconds'."""
    tax = load_taxonomy()
    constraints = tax["context_axes"]["constraint"]
    assert "tethered" in constraints
    assert "shared_death" in constraints


def test_scaling_is_open_vocabulary_but_declared():
    tax = load_taxonomy()
    scaling = tax["identity_axes"]["scaling"]
    assert scaling["open_vocabulary"] is True
    assert "link_effect" in scaling["values"]
    # §11.2 상한 신호
    assert len(scaling["values"]) <= 25


def test_v1_context_axes_are_preserved_verbatim():
    """v1 소비자를 깨지 않기 위해 기존 키는 그대로 남는다."""
    tax = load_taxonomy()
    assert len(tax["role_tags"]) == 10
    assert len(tax["content_tags"]) == 7
    assert len(tax["build_phases"]) == 8
    for key in ("evidence_types", "confidence_levels", "meta_popularity_basis", "patch_statuses"):
        assert key in tax, f"v1 키 {key} 유실"


# --------------------------------------------------------------------------
# v1 → v2 이관
# --------------------------------------------------------------------------

def test_v1_has_exactly_fourteen_mechanic_tags():
    assert len(V1_MECHANIC_TAGS) == 14


@pytest.mark.parametrize("tag", V1_MECHANIC_TAGS)
def test_every_v1_tag_has_a_destination(tag):
    assert migrate_v1_tag(tag) is not None, f"v1 태그 {tag} 이관처 없음 — 유실"


@pytest.mark.parametrize("tag", V1_MECHANIC_TAGS)
def test_every_migration_target_resolves_to_real_vocabulary(tag):
    tax = load_taxonomy()
    target = migrate_v1_tag(tag)
    if target == "dropped":
        return
    axis, _, value = target.partition(".")
    assert axis, f"{tag} → {target} 형식 오류"

    def _flatten(node):
        if isinstance(node, dict):
            if "values" in node:
                return list(node["values"])
            out = []
            for sub in node.values():
                out.extend(_flatten(sub))
            return out
        if isinstance(node, list):
            return list(node)
        return []

    pool = _flatten(tax["identity_axes"].get(axis) or tax["context_axes"].get(axis) or {})
    leaf = value.split(".")[-1]
    assert leaf in pool, f"{tag} → {target}: '{leaf}' 가 어휘에 없음"


def test_spell_is_the_only_dropped_tag():
    dropped = [t for t in V1_MECHANIC_TAGS if migrate_v1_tag(t) == "dropped"]
    assert dropped == ["spell"], "젬 태그로 파생되는 것은 spell 하나여야 한다"


# --------------------------------------------------------------------------
# 벡터화 정책
# --------------------------------------------------------------------------

def test_axis_values_are_never_embedded():
    tax = load_taxonomy()
    never = tax["vectorization_policy"]["never_embed"]
    assert "axis_values" in never
    assert "item_names" in never
    assert "numbers" in never


# --------------------------------------------------------------------------
# 픽스처 (수용 기준 §9)
# --------------------------------------------------------------------------

def _fixture_ids():
    return [b["build_id"] for b in load_fixtures()["builds"]]


def test_fixture_set_covers_the_eight_reference_builds():
    assert len(load_fixtures()["builds"]) == 8


@pytest.mark.parametrize("build_id", _fixture_ids())
def test_fixture_validates_against_taxonomy(build_id):
    tax = load_taxonomy()
    build = next(b for b in load_fixtures()["builds"] if b["build_id"] == build_id)
    errors = validate_fixture(build, tax)
    assert errors == [], f"{build_id}: " + " / ".join(errors)


@pytest.mark.parametrize("build_id", _fixture_ids())
def test_every_entity_has_a_primary_delivery(build_id):
    """수용 기준 §9.1 — delivery 빈 칸 금지."""
    build = next(b for b in load_fixtures()["builds"] if b["build_id"] == build_id)
    for entity, tags in build["entities"].items():
        primary = tags.get("delivery", {}).get("primary")
        assert primary, f"{build_id}/{entity}: delivery.primary 비어 있음"


def test_luminary_bot_is_multi_entity():
    """v1 이 표현하지 못했던 대표 사례 — 플레이어와 딜러가 분리된다."""
    build = next(b for b in load_fixtures()["builds"] if "luminary_bot" in b["build_id"])
    entities = build["entities"]
    assert set(entities) >= {"player", "mercenary"}
    assert entities["player"]["delivery"]["primary"] == "aura_link"
    assert entities["player"]["range"] == "proxy"
    assert "tethered" in entities["player"]["constraint"]
    assert entities["mercenary"]["delivery"]["primary"] == "trap"


def test_no_two_builds_collide_on_player_identity():
    """수용 기준 §9.2 — 다르게 플레이되는 빌드가 같은 튜플을 갖지 않는다."""
    seen: dict[tuple, str] = {}
    for build in load_fixtures()["builds"]:
        player = build["entities"]["player"]
        key = (
            player["delivery"]["primary"],
            player["range"],
            tuple(sorted(player.get("scaling", []))),
        )
        assert key not in seen, f"{build['build_id']} 가 {seen[key]} 와 충돌: {key}"
        seen[key] = build["build_id"]


def test_totem_and_minion_builds_share_proxy_but_differ():
    """§9.2 명시 사례 — Flamewood 토템과 SRS 는 proxy 를 공유하되 구분돼야 한다."""
    builds = {b["build_id"]: b["entities"]["player"] for b in load_fixtures()["builds"]}
    totem = next(v for k, v in builds.items() if "flamewood" in k)
    srs = next(v for k, v in builds.items() if "srs" in k)
    assert totem["range"] == srs["range"] == "proxy"
    assert totem["delivery"]["primary"] != srs["delivery"]["primary"]
    assert set(totem["scaling"]) != set(srs["scaling"])
