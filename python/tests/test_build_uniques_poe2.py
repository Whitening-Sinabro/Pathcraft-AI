"""`scripts/build_uniques_poe2.py` 의 stash_type 라벨 매핑 헬퍼 단위 테스트.

UniqueStashTypes 는 GGPK 추가 추출이 필요한 신규 테이블. 테이블이 없는
환경(현재) 과 추가된 환경(다음 추출 이후) 모두에서 스크립트가 동작해야 함.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_uniques_poe2.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_uniques_poe2", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestBuildStashTypeLabels:
    def setup_method(self):
        self.mod = _load_module()

    def test_none_input_returns_empty(self):
        """UniqueStashTypes.json 추출 전 상태 — None 그대로 받아 빈 매핑."""
        assert self.mod.build_stash_type_labels(None) == {}

    def test_empty_list_returns_empty(self):
        assert self.mod.build_stash_type_labels([]) == {}

    def test_name_priority_with_id_fallback(self):
        rows = [
            {"Id": "Weapons", "Name": "Weapons"},              # Name 우선
            {"Id": "BodyArmours", "Name": "  "},                # Name 공백 → Id fallback
            {"Id": "", "Name": "Helmets"},                      # Name 만
            {"Id": "", "Name": ""},                             # 둘 다 공백 → 스킵
            {"Id": "Rings", "Name": "Rings"},
        ]
        labels = self.mod.build_stash_type_labels(rows)
        assert labels[0] == "Weapons"
        assert labels[1] == "BodyArmours"
        assert labels[2] == "Helmets"
        assert 3 not in labels, "빈 라벨 행은 매핑에 포함되지 않아야 함"
        assert labels[4] == "Rings"

    def test_label_strip_whitespace(self):
        rows = [{"Id": "X", "Name": "  Weapons  "}]
        labels = self.mod.build_stash_type_labels(rows)
        assert labels[0] == "Weapons"


class TestLoadOptional:
    def setup_method(self):
        self.mod = _load_module()

    def test_missing_file_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "POE2_ROOT", tmp_path)
        assert self.mod.load_optional("NoSuchTable.json") is None

    def test_existing_file_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "POE2_ROOT", tmp_path)
        payload = [{"Id": "A", "Name": "Alpha"}, {"Id": "B", "Name": "Beta"}]
        (tmp_path / "Sample.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8",
        )
        loaded = self.mod.load_optional("Sample.json")
        assert loaded == payload


class TestUniquesPoe2JsonIntegrity:
    """`data/uniques_poe2.json` (현재 생성물) 무결성 — stash_type 필드 유지."""

    def test_stash_type_is_int_for_all_uniques(self):
        payload = json.loads(
            (REPO_ROOT / "data" / "uniques_poe2.json").read_text(encoding="utf-8"),
        )
        for u in payload["uniques"]:
            assert isinstance(u.get("stash_type"), int), (
                f"stash_type 은 int 이어야 함 — got {type(u.get('stash_type'))}"
            )

    def test_stash_type_labels_consistent_with_meta(self):
        """_meta.stash_type_labels_count 가 있으면 모든 uniques 에 stash_type_label 이 존재해야 함.

        (label 값은 None 가능 — unknown_label 로 집계. 키 자체는 반드시 존재.)
        """
        payload = json.loads(
            (REPO_ROOT / "data" / "uniques_poe2.json").read_text(encoding="utf-8"),
        )
        meta = payload.get("_meta", {})
        if "stash_type_labels_count" in meta:
            for u in payload["uniques"]:
                assert "stash_type_label" in u, "라벨 매핑 활성 시 stash_type_label 키 필수"
        else:
            for u in payload["uniques"]:
                assert "stash_type_label" not in u, (
                    "라벨 매핑 비활성 시 stash_type_label 필드는 없어야 함 (graceful)"
                )
