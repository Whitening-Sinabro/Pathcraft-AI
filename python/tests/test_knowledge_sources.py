"""지식 소스 레지스트리 무결성.

레지스트리가 코드 안 dict 리터럴이던 시절, 등록만 되고 실제로는 로드되지 않는
항목이 4건 섞여 있었다(경로 자리에 설명문이 들어 있었다). 아무도 몰랐던 이유는
검증이 없었기 때문이다. 이 파일이 그 검증이다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

REGISTRY_PATH = ROOT / "data" / "knowledge_sources.json"
DATA_ROOT = ROOT / "data"


@pytest.fixture(scope="module")
def registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sources(registry):
    return registry["sources"]


def _source_ids():
    return sorted(json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["sources"])


def test_registry_is_data_not_code():
    """라우터가 리터럴이 아니라 이 파일에서 읽어야 한다."""
    router = (ROOT / "python" / "knowledge_router.py").read_text(encoding="utf-8")
    assert "_load_source_registry" in router
    assert "knowledge_sources.json" in router


def test_router_loads_every_source(sources):
    from knowledge_router import SOURCE_REGISTRY

    assert set(SOURCE_REGISTRY) == set(sources)


@pytest.mark.parametrize("source_id", _source_ids())
def test_declared_files_actually_exist(sources, source_id):
    """`status: ok` 인 소스는 파일이 실재해야 한다."""
    entry = sources[source_id]
    if entry.get("status") != "ok":
        return

    missing: list[str] = []
    if entry.get("path"):
        if not (DATA_ROOT / entry["path"]).exists():
            missing.append(entry["path"])
    for relative in entry.get("paths") or []:
        if not (DATA_ROOT / relative).exists():
            missing.append(relative)
    for pattern in entry.get("globs") or []:
        if not list(DATA_ROOT.glob(pattern)):
            missing.append(f"{pattern} (매치 0)")

    assert not missing, f"{source_id}: 존재하지 않는 경로 {missing}"


@pytest.mark.parametrize("source_id", _source_ids())
def test_every_source_declares_a_target(sources, source_id):
    """경로 없이 등록된 소스는 status 로 사유를 밝혀야 한다."""
    entry = sources[source_id]
    has_target = bool(entry.get("path") or entry.get("paths") or entry.get("globs"))
    if has_target:
        return
    assert entry.get("status") != "ok", f"{source_id}: 대상이 없는데 status 가 ok"
    assert entry.get("note"), f"{source_id}: 대상이 없으면 note 로 사유를 남길 것"


@pytest.mark.parametrize("source_id", _source_ids())
def test_every_source_declares_retrieval_policy(sources, source_id):
    """벡터화 정책은 소스마다 명시돼야 한다 — 기본값으로 흘러가면 안 된다."""
    entry = sources[source_id]
    for field in ("kind", "evidence_layer", "retrieval_mode", "vectorization"):
        assert entry.get(field), f"{source_id}: {field} 누락"


def test_known_no_data_source_is_flagged(sources):
    """poe_ninja_economy 는 등록만 되고 실 데이터가 없다 — 조용히 통과시키지 않는다."""
    entry = sources["poe_ninja_economy"]
    assert entry["status"] == "declared_no_data"
    assert entry.get("note")


def test_creator_packs_are_registered(sources):
    """크리에이터 팩은 레지스트리에 있어야 라우터가 고른다."""
    creator_ids = [sid for sid, e in sources.items() if e.get("kind") == "community_build_knowledge"]
    assert len(creator_ids) >= 3
    for sid in creator_ids:
        assert sources[sid].get("path"), f"{sid}: 팩 경로 없음"


def test_dark_bargain_pack_gap_is_visible():
    """dark_bargain 팩은 파일은 있는데 레지스트리에 없다 — 알려진 갭이다.

    고쳐지면 이 테스트가 red 가 되고, 그때 이 단언을 지우면 된다.
    """
    sources = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["sources"]
    pack = DATA_ROOT / "guide_sources" / "poe1_dark_bargain_intuitive_link_luminary_3_29_v1.json"
    registered = any(
        str(entry.get("path", "")).endswith(pack.name) for entry in sources.values()
    )
    assert pack.exists(), "팩 파일이 사라졌다"
    assert not registered, "dark_bargain 팩이 등록됐다 — 이 가드를 지우고 갭 기록을 정리할 것"
