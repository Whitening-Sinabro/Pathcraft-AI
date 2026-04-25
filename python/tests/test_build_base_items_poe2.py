"""`scripts/build_base_items_poe2.py` AttributeRequirements 매핑 헬퍼 + 무결성.

AttributeRequirements 는 다음 GGPK 추출 사이클에 추가될 테이블. 부재 / 활성
두 상태 모두에서 build script 가 동작해야 함.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_base_items_poe2.py"
OUTPUT_PATH = REPO_ROOT / "data" / "base_items_poe2.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_base_items_poe2", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestBuildAttributeRequirements:
    def setup_method(self):
        self.mod = _load_module()

    def test_none_input_returns_empty(self):
        assert self.mod.build_attribute_requirements(None) == {}

    def test_empty_list_returns_empty(self):
        assert self.mod.build_attribute_requirements([]) == {}

    def test_zero_zero_zero_skipped(self):
        """ReqStr=0/Dex=0/Int=0 행은 매핑에서 제외 (요구치 없음과 동치)."""
        rows = [{"BaseItemType": 5, "ReqStr": 0, "ReqDex": 0, "ReqInt": 0}]
        assert self.mod.build_attribute_requirements(rows) == {}

    def test_valid_requirement_mapped(self):
        rows = [
            {"BaseItemType": 10, "ReqStr": 50, "ReqDex": 0, "ReqInt": 0},
            {"BaseItemType": 11, "ReqStr": 0, "ReqDex": 30, "ReqInt": 20},
        ]
        m = self.mod.build_attribute_requirements(rows)
        assert m[10] == {"req_str": 50, "req_dex": 0, "req_int": 0}
        assert m[11] == {"req_str": 0, "req_dex": 30, "req_int": 20}

    def test_invalid_basetype_skipped(self):
        """BaseItemType 이 int 가 아닌 행 스킵."""
        rows = [
            {"BaseItemType": "abc", "ReqStr": 10, "ReqDex": 0, "ReqInt": 0},
            {"BaseItemType": -1, "ReqStr": 10, "ReqDex": 0, "ReqInt": 0},
            {"BaseItemType": 7, "ReqStr": 5, "ReqDex": 0, "ReqInt": 0},
        ]
        m = self.mod.build_attribute_requirements(rows)
        assert list(m.keys()) == [7]

    def test_non_int_req_skipped(self):
        """ReqStr/Dex/Int 가 int 가 아닌 행 스킵 (스키마 깨짐 방어)."""
        rows = [{"BaseItemType": 1, "ReqStr": None, "ReqDex": 10, "ReqInt": 0}]
        assert self.mod.build_attribute_requirements(rows) == {}


class TestSimplifyWithAttrReq:
    def setup_method(self):
        self.mod = _load_module()

    def test_no_attr_req_no_fields(self):
        item = {"Id": "x", "Name": "y", "DropLevel": 1, "Width": 2, "Height": 3, "Tags": []}
        out = self.mod.simplify(item)
        assert "req_str" not in out
        assert "req_dex" not in out
        assert "req_int" not in out

    def test_attr_req_match_injects_fields(self):
        item = {"Id": "x", "Name": "y", "DropLevel": 1, "Width": 2, "Height": 3, "Tags": []}
        attr_req = {5: {"req_str": 30, "req_dex": 40, "req_int": 0}}
        out = self.mod.simplify(item, base_index=5, attr_req=attr_req)
        assert out["req_str"] == 30
        assert out["req_dex"] == 40
        assert out["req_int"] == 0

    def test_attr_req_miss_no_fields(self):
        item = {"Id": "x", "Name": "y", "DropLevel": 1, "Width": 2, "Height": 3, "Tags": []}
        attr_req = {5: {"req_str": 30, "req_dex": 40, "req_int": 0}}
        out = self.mod.simplify(item, base_index=99, attr_req=attr_req)
        assert "req_str" not in out


class TestLoadOptional:
    def setup_method(self):
        self.mod = _load_module()

    def test_missing_file_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "POE2_ROOT", tmp_path)
        assert self.mod.load_optional("NoSuchTable.json") is None

    def test_existing_file_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "POE2_ROOT", tmp_path)
        payload = [{"BaseItemType": 1, "ReqStr": 10, "ReqDex": 0, "ReqInt": 0}]
        (tmp_path / "Sample.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8",
        )
        loaded = self.mod.load_optional("Sample.json")
        assert loaded == payload


class TestBaseItemsPoe2JsonIntegrity:
    """`data/base_items_poe2.json` (현재 생성물) 무결성 — graceful 상태 / 활성 상태 양쪽."""

    def test_meta_consistent_with_req_fields(self):
        """_meta.attribute_requirements_count 가 있으면 weapons/armours 중 일부에 req_* 필드 존재해야 함."""
        payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        meta = payload.get("_meta", {})
        if "attribute_requirements_count" in meta:
            has_any_req = any(
                "req_str" in entry
                for cat in ("weapons", "armours")
                for entries in payload.get(cat, {}).values()
                for entry in entries
            )
            assert has_any_req, (
                "meta.attribute_requirements_count 활성 — entry 에 req_* 부착되어야 함"
            )
        else:
            no_req = all(
                "req_str" not in entry
                for cat in ("weapons", "armours", "other")
                for entries in payload.get(cat, {}).values()
                for entry in entries
            )
            assert no_req, (
                "meta.attribute_requirements_count 비활성 — entry 에 req_* 없어야 함 (graceful)"
            )

    def test_req_field_types_when_present(self):
        """req_str/dex/int 가 있으면 int 이어야 함."""
        payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        for cat in ("weapons", "armours", "other"):
            for entries in payload.get(cat, {}).values():
                for entry in entries:
                    for field in ("req_str", "req_dex", "req_int"):
                        if field in entry:
                            assert isinstance(entry[field], int), (
                                f"{cat}/{entry.get('id')}/{field} 는 int 이어야 함"
                            )
