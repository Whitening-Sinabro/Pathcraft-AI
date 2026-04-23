"""data/item_class_map_poe2.json 스키마·무결성 검증.

구조 계약 고정. NeverSink drift 는 scripts/verify_item_class_map_poe2.py 가 별도로 체크.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MAP_PATH = REPO_ROOT / "data" / "item_class_map_poe2.json"


def _load():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def test_file_exists():
    assert MAP_PATH.exists(), "scripts/verify_item_class_map_poe2.py --local 로 재생성"


def test_required_top_level_keys():
    d = _load()
    for k in ("_meta", "poe2_classes", "categories_poe2", "poe1_to_poe2",
              "poe2_new_classes", "notes"):
        assert k in d, f"필수 키 누락: {k}"


def test_poe2_classes_nonempty_unique_sorted():
    d = _load()
    classes = d["poe2_classes"]
    assert isinstance(classes, list) and classes
    assert len(classes) == len(set(classes)), "중복 class 이름"
    assert classes == sorted(classes), "poe2_classes 는 정렬 상태 유지 — diff 편의"


def test_categories_partition_poe2_classes_exactly():
    """categories_poe2 의 union 이 poe2_classes 와 정확히 일치 (누락 0, 중복 0)."""
    d = _load()
    classes = set(d["poe2_classes"])
    cats = d["categories_poe2"]
    union: set[str] = set()
    for cat, members in cats.items():
        assert isinstance(members, list) and members, f"빈 카테고리: {cat}"
        for m in members:
            assert m in classes, f"categories_poe2[{cat}]={m} 가 poe2_classes 에 없음"
            assert m not in union, f"중복 분류: {m} (여러 카테고리에 존재)"
            union.add(m)
    missing = classes - union
    assert not missing, f"카테고리 미분류: {missing}"


def test_poe1_to_poe2_targets_valid():
    """poe1_to_poe2 의 모든 값은 poe2_classes 부분집합 (빈 리스트 허용)."""
    d = _load()
    classes = set(d["poe2_classes"])
    for poe1, poe2_list in d["poe1_to_poe2"].items():
        assert isinstance(poe2_list, list), f"{poe1} 값이 list 아님"
        for c in poe2_list:
            assert c in classes, f"poe1_to_poe2[{poe1}]={c} 가 poe2_classes 에 없음"


def test_poe1_to_poe2_covers_sections_continue_poe1_classes():
    """sections_continue.py 에서 하드코딩된 POE1 ItemClass 가 전부 매핑 키로 존재."""
    d = _load()
    # sections_continue.py _EQUIP_CLASSES + _RARE_EQUIP_CLASSES_EXACT 합집합 (POE1 rare/equip)
    required_poe1 = {
        "Amulets", "Belts", "Body Armours", "Boots", "Bows", "Claws", "Daggers",
        "Gloves", "Helmets", "One Hand Axes", "One Hand Maces", "One Hand Swords",
        "Quivers", "Rings", "Rune Daggers", "Sceptres", "Shields", "Staves",
        "Thrusting One Hand Swords", "Two Hand Axes", "Two Hand Maces",
        "Two Hand Swords", "Wands", "Warstaves",
    }
    missing = required_poe1 - set(d["poe1_to_poe2"].keys())
    assert not missing, f"sections_continue.py POE1 Class 가 매핑 키로 누락: {missing}"


def test_poe2_new_classes_subset_and_not_poe1_class_name():
    """poe2_new_classes = POE2 에서 신설된 Class 이름. POE1 Class 키 이름과 겹치면 안 됨.

    주의: poe1_to_poe2 의 *값* (e.g., POE1 Shields → [Shields, Bucklers]) 에는 등장해도 OK.
    '값' 은 POE1 semantic 이 POE2 어느 Class(들)에 대응하는지 매핑일 뿐이고, Bucklers 는
    여전히 POE2 에서 처음 도입된 Class 이름.
    """
    d = _load()
    classes = set(d["poe2_classes"])
    poe1_keys = set(d["poe1_to_poe2"].keys())
    for c in d["poe2_new_classes"]:
        assert c in classes, f"poe2_new_classes[{c}] 가 poe2_classes 에 없음"
        assert c not in poe1_keys, (
            f"{c} 는 POE1 에도 존재하는 Class 키 — 'new' 가 아님. poe2_new_classes 에서 제거"
        )


def test_shields_maps_to_both_shields_and_bucklers():
    """POE1 Shields → POE2 [Shields, Bucklers] 분할 규칙."""
    d = _load()
    assert set(d["poe1_to_poe2"]["Shields"]) == {"Shields", "Bucklers"}, (
        "POE2 는 Shields (Str/Int) + Bucklers (Dex) 두 클래스로 분리 — 둘 다 매핑해야"
    )


def test_warstaves_maps_to_quarterstaves():
    d = _load()
    assert d["poe1_to_poe2"]["Warstaves"] == ["Quarterstaves"], (
        "POE1 Warstaves 포지션은 POE2 Quarterstaves"
    )


def test_poe1_unreleased_classes_map_to_empty():
    """POE2 0.4 미릴리스 무기류는 빈 리스트로 명시."""
    d = _load()
    for removed in ("Claws", "Daggers", "One Hand Axes", "One Hand Swords",
                    "Two Hand Axes", "Two Hand Swords", "Rune Daggers",
                    "Thrusting One Hand Swords"):
        assert d["poe1_to_poe2"][removed] == [], (
            f"POE2 0.4 미릴리스인 {removed} 는 빈 리스트여야 (현재: {d['poe1_to_poe2'][removed]})"
        )


def test_meta_has_provenance():
    d = _load()
    m = d["_meta"]
    for k in ("source_primary", "source_files", "source_version", "source_fetched_utc",
              "verify_script"):
        assert k in m and m[k], f"_meta.{k} 누락 또는 공백"
