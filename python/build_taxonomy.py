# -*- coding: utf-8 -*-
"""Build Taxonomy v2 로더 + 픽스처 검증기.

어휘 정본은 ``data/build_corpus_taxonomy.json`` (schema_version 2.0), 수용 픽스처는
``data/build_taxonomy_fixtures.json``. 스펙은
``~/.claude/projects/D--Pathcraft-AI/2026-08-19-build-taxonomy-v2-spec.md``.

v1 은 mechanic_tags 14개를 한 바구니에 담아 전달 방식 / 사거리 / 피해 / 제약을 섞었다.
v2 는 축을 직교로 분리하고 주체(player / mercenary / animate_guardian / spectre)에 매단다.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("build_taxonomy")

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = ROOT / "data" / "build_corpus_taxonomy.json"
FIXTURES_PATH = ROOT / "data" / "build_taxonomy_fixtures.json"

# v1 mechanic_tags 원본 14개. 이관 누락을 잡기 위해 코드에 고정한다.
V1_MECHANIC_TAGS = (
    "requires_respec",
    "requires_unique_to_function",
    "attribute_stacker",
    "crit_scaler",
    "totem",
    "mine",
    "dot",
    "trigger",
    "minion",
    "melee",
    "projectile",
    "spell",
    "attack",
    "hybrid_defense",
)

_taxonomy_cache: dict[str, Any] | None = None
_fixtures_cache: dict[str, Any] | None = None


def reset_cache() -> None:
    global _taxonomy_cache, _fixtures_cache
    _taxonomy_cache = None
    _fixtures_cache = None


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.error("taxonomy 파일 없음: %s", path)
        raise
    except json.JSONDecodeError as exc:
        logger.error("taxonomy JSON 파싱 실패 %s: %s", path, exc)
        raise


def load_taxonomy() -> dict[str, Any]:
    global _taxonomy_cache
    if _taxonomy_cache is None:
        _taxonomy_cache = _load(TAXONOMY_PATH)
    return _taxonomy_cache


def load_fixtures() -> dict[str, Any]:
    global _fixtures_cache
    if _fixtures_cache is None:
        _fixtures_cache = _load(FIXTURES_PATH)
    return _fixtures_cache


def migrate_v1_tag(tag: str) -> str | None:
    """v1 mechanic_tag 하나의 v2 이관처. 미등록이면 None (= 유실 신호)."""
    return load_taxonomy().get("v1_migration", {}).get(tag)


# --------------------------------------------------------------------------
# 픽스처 검증
# --------------------------------------------------------------------------

def _axis_values(taxonomy: dict[str, Any], *path: str) -> list[str]:
    node: Any = taxonomy
    for key in path:
        node = (node or {}).get(key, {})
    if isinstance(node, dict):
        return list(node.get("values", []))
    if isinstance(node, list):
        return list(node)
    return []


def _check_single(errors: list[str], where: str, value: Any, allowed: list[str], required: bool) -> None:
    if value is None:
        if required:
            errors.append(f"{where}: 필수인데 비어 있음")
        return
    if value not in allowed:
        errors.append(f"{where}: '{value}' 는 어휘에 없음")


def _check_many(errors: list[str], where: str, values: Any, allowed: list[str]) -> None:
    if values is None:
        return
    if not isinstance(values, list):
        errors.append(f"{where}: 리스트여야 함")
        return
    for value in values:
        if value not in allowed:
            errors.append(f"{where}: '{value}' 는 어휘에 없음")


def validate_entity(entity: str, tags: dict[str, Any], taxonomy: dict[str, Any]) -> list[str]:
    """주체 하나의 태그 묶음을 어휘에 대조. 오류 문자열 리스트를 돌려준다."""
    errors: list[str] = []

    if entity not in taxonomy.get("entities", []):
        errors.append(f"주체 '{entity}' 는 어휘에 없음")

    delivery = tags.get("delivery") or {}
    delivery_values = _axis_values(taxonomy, "identity_axes", "delivery")
    _check_single(errors, f"{entity}.delivery.primary", delivery.get("primary"), delivery_values, required=True)
    _check_many(errors, f"{entity}.delivery.secondary", delivery.get("secondary"), delivery_values)

    _check_single(errors, f"{entity}.range", tags.get("range"),
                  _axis_values(taxonomy, "identity_axes", "range"), required=True)

    damage = tags.get("damage") or {}
    element = damage.get("element") or {}
    element_values = _axis_values(taxonomy, "identity_axes", "damage", "element")
    _check_single(errors, f"{entity}.damage.element.primary", element.get("primary"), element_values, required=False)
    _check_many(errors, f"{entity}.damage.element.secondary", element.get("secondary"), element_values)
    _check_many(errors, f"{entity}.damage.form", damage.get("form"),
                _axis_values(taxonomy, "identity_axes", "damage", "form"))

    defense = tags.get("defense") or {}
    _check_single(errors, f"{entity}.defense.pool", defense.get("pool"),
                  _axis_values(taxonomy, "identity_axes", "defense", "pool"), required=False)
    _check_many(errors, f"{entity}.defense.layer", defense.get("layer"),
                _axis_values(taxonomy, "identity_axes", "defense", "layer"))

    weapon = tags.get("weapon") or {}
    _check_single(errors, f"{entity}.weapon.type", weapon.get("type"),
                  _axis_values(taxonomy, "identity_axes", "weapon", "type"), required=False)
    _check_single(errors, f"{entity}.weapon.style", weapon.get("style"),
                  _axis_values(taxonomy, "identity_axes", "weapon", "style"), required=False)

    _check_many(errors, f"{entity}.scaling", tags.get("scaling"),
                _axis_values(taxonomy, "identity_axes", "scaling"))
    _check_many(errors, f"{entity}.flags", tags.get("flags"), list(taxonomy.get("flags", [])))
    _check_many(errors, f"{entity}.constraint", tags.get("constraint"),
                list(taxonomy.get("context_axes", {}).get("constraint", [])))

    return errors


def validate_fixture(build: dict[str, Any], taxonomy: dict[str, Any] | None = None) -> list[str]:
    """픽스처 빌드 하나를 검증. 오류가 없으면 빈 리스트."""
    taxonomy = taxonomy or load_taxonomy()

    if not build.get("build_id"):
        return ["build_id 없음"]

    entities = build.get("entities") or {}
    if not entities:
        return [f"{build['build_id']}: entities 비어 있음"]
    if "player" not in entities:
        return [f"{build['build_id']}: player 주체 필수"]

    errors: list[str] = []
    for entity, tags in entities.items():
        errors.extend(validate_entity(entity, tags or {}, taxonomy))
    return errors


def validate_all_fixtures() -> dict[str, list[str]]:
    """전체 픽스처 검증 결과 — build_id → 오류 리스트."""
    taxonomy = load_taxonomy()
    return {b["build_id"]: validate_fixture(b, taxonomy) for b in load_fixtures().get("builds", [])}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    failures = {k: v for k, v in validate_all_fixtures().items() if v}
    if not failures:
        logger.info("픽스처 %d건 전부 통과", len(load_fixtures().get("builds", [])))
    else:
        for build_id, errors in failures.items():
            logger.error("%s: %s", build_id, " / ".join(errors))
        raise SystemExit(1)
