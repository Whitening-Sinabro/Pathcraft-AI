"""파생 데이터 인벤토리 회귀 가드.

핀(`_analysis/derived_data_inventory.json`)을 믿지 않는다. 매 실행마다 현재 레포를 다시 훑어
핀과 대조한다 — 파생 파일이 늘거나 provenance 가 바뀌었는데 인벤토리를 갱신 안 하면 여기서 잡힌다.

staleness 게이트(계획서 §3.2)도 여기 있지만 **지금은 공허하다** — 지문을 가진 파생 파일이
0개라서 검사 대상이 없다. 그 공허함 자체를 `test_stale_gate_vacuity_is_declared` 가 감시한다.
지문이 붙기 시작하면 그 skip 이 사라지고 게이트가 실제로 작동한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from derived_data_inventory import (  # noqa: E402
    OUT_PATH,
    TRUTH_REFERENCE,
    build_inventory,
    classify,
    declared_generator_path,
    extract_provenance,
    ggpk_fingerprint,
)

REGENERATE = "python python/scripts/derived_data_inventory.py --write 로 재생성할 것"


@pytest.fixture(scope="module")
def scanned():
    """현재 레포를 다시 훑은 결과."""
    return build_inventory()


@pytest.fixture(scope="module")
def pinned():
    return json.loads(OUT_PATH.read_text(encoding="utf-8"))


# --- 핀 대조 (핀을 믿지 않는다) ------------------------------------------------


def test_pinned_file_set_matches_current_scan(scanned, pinned):
    added = sorted(set(scanned["files"]) - set(pinned["files"]))
    removed = sorted(set(pinned["files"]) - set(scanned["files"]))
    assert not added and not removed, f"인벤토리 누락. 추가={added} 삭제={removed}. {REGENERATE}"


def test_pinned_status_matches_current_scan(scanned, pinned):
    drifted = {
        path: (pinned["files"][path]["status"], entry["status"])
        for path, entry in scanned["files"].items()
        if path in pinned["files"] and pinned["files"][path]["status"] != entry["status"]
    }
    assert not drifted, f"상태가 바뀐 파일(핀→현재): {drifted}. {REGENERATE}"


def test_pinned_content_hash_matches_current_scan(scanned, pinned):
    """파일 내용이 바뀌었는데 인벤토리를 안 돌린 경우."""
    drifted = sorted(
        path for path, entry in scanned["files"].items()
        if path in pinned["files"] and pinned["files"][path]["sha256_16"] != entry["sha256_16"]
    )
    assert not drifted, f"내용이 바뀐 파일: {drifted}. {REGENERATE}"


def test_pinned_fingerprint_matches_current_ggpk(pinned):
    """GGPK 를 재추출하면 여기서 먼저 터진다.

    이 red 의 처방은 `--write` 가 **아니다**. 지문이 바뀌었다는 것은 파생 파일 전부의
    최신성이 불명이 됐다는 뜻이고, 핀만 갈아끼우면 그 사실이 그대로 묻힌다.
    """
    assert pinned["ggpk_fingerprint"] == ggpk_fingerprint(), (
        "핀의 GGPK 지문이 현재 추출본과 불일치. 각 파생 파일의 생성기를 다시 돌린 뒤 "
        "python python/scripts/derived_data_inventory.py --write --accept-ggpk-change "
        "로 재생성할 것 (--write 단독은 거부된다)."
    )


# --- staleness 게이트 ----------------------------------------------------------


def test_stale_gate_vacuity_is_declared(scanned):
    """지금 이 게이트가 **아무것도 지키지 않는다**는 사실을 숨기지 않는다.

    지문을 가진 파생 파일이 0개인 동안 `test_no_derived_file_is_stale` 는 빈 집합을 검사한다.
    이 테스트는 그 사실을 payload 에 드러나게 강제하고, 지문 보유 파일이 생기는 순간
    (게이트가 실제로 작동하기 시작하는 순간) 여기서 알린다.
    """
    fingerprinted = scanned["totals"]["fingerprinted"]
    assert fingerprinted == sum(
        1 for e in scanned["files"].values() if e["provenance"]["ggpk_fingerprint"]
    )
    if fingerprinted == 0:
        pytest.skip(
            "지문을 가진 파생 파일이 0개 — staleness 게이트는 아직 대상이 없다(판정기만 존재). "
            "첫 생성기가 ggpk_fingerprint 를 쓰기 시작하면 이 skip 이 사라진다."
        )


def test_fingerprinted_count_does_not_decrease(scanned, pinned):
    """지문을 붙인 파일이 다시 떨어져 나가면 안 된다 — 진행의 래칫."""
    assert scanned["totals"]["fingerprinted"] >= pinned["totals"]["fingerprinted"], (
        "지문 보유 파일이 줄었다 — 생성기에서 ggpk_fingerprint 가 빠졌는지 확인할 것"
    )


def test_no_derived_file_is_stale(scanned):
    """`ggpk_fingerprint` 을 적어둔 파일이 현재 추출본과 어긋나면 조용히 두지 않는다.

    주의: 지문 보유 파일이 0개인 동안 이 검사는 공허하다. 위 두 테스트가 그 상태를 감시한다.
    """
    stale = sorted(p for p, e in scanned["files"].items() if e["status"] == "stale")
    assert not stale, (
        "GGPK 지문이 어긋난 파생 파일: " + ", ".join(stale)
        + " — 각 생성기를 다시 돌려 재생성할 것"
    )


def test_unfingerprinted_count_does_not_grow(scanned, pinned):
    """래칫 — 지문 없는 파생 파일이 지금보다 늘어나면 실패한다.

    지금은 대부분이 지문이 없다(그게 §1 의 병이다). 줄이는 건 후속 작업이고,
    이 테스트가 막는 것은 **새로 늘어나는 것**이다.
    """
    unfingerprinted = {"orphan", "declared_no_generator", "generated_no_fingerprint"}
    baseline = sum(pinned["totals"]["by_status"].get(s, 0) for s in unfingerprinted)
    current = sum(1 for e in scanned["files"].values() if e["status"] in unfingerprinted)
    assert current <= baseline, (
        f"지문 없는 파생 파일이 {baseline} → {current} 로 늘었다. "
        "새 파생 JSON 은 생성기 + ggpk_fingerprint 를 갖춰야 한다."
    )


def test_broken_json_is_declared_not_silently_skipped(scanned, pinned):
    """파싱 실패는 인벤토리에 남는다 — 조용히 빠지면 '없는 파일'로 오해된다."""
    pinned_broken = {p for p, e in pinned["files"].items() if e["status"] == "broken"}
    current_broken = {p for p, e in scanned["files"].items() if e["status"] == "broken"}
    assert current_broken == pinned_broken, (
        f"파싱 실패 목록 변화(핀={sorted(pinned_broken)} 현재={sorted(current_broken)}). {REGENERATE}"
    )
    for path in current_broken:
        assert scanned["files"][path]["parse_error"], f"{path}: broken 인데 사유가 비어 있음"


# --- 지문은 소비하지 재계산하지 않는다 -----------------------------------------


def test_fingerprint_is_derived_from_truth_reference_only(monkeypatch, tmp_path):
    """원본 해시의 정본은 ggpk_truth_builder 하나다. 레퍼런스를 바꾸면 지문이 따라 바뀌어야 한다."""
    import derived_data_inventory as module

    real = json.loads(TRUTH_REFERENCE.read_text(encoding="utf-8"))
    baseline = ggpk_fingerprint()

    mutated = json.loads(json.dumps(real))
    first_table = sorted(mutated["tables"])[0]
    mutated["tables"][first_table]["content_hash"] = "0" * 64
    fake = tmp_path / "ggpk_truth_reference.json"
    fake.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(module, "TRUTH_REFERENCE", fake)
    assert module.ggpk_fingerprint() != baseline, (
        "레퍼런스 테이블 해시를 바꿨는데 지문이 그대로다 — 지문이 다른 경로에서 계산되고 있다"
    )


def test_fingerprint_fails_loudly_when_reference_missing(monkeypatch, tmp_path):
    import derived_data_inventory as module

    monkeypatch.setattr(module, "TRUTH_REFERENCE", tmp_path / "absent.json")
    with pytest.raises(FileNotFoundError):
        module.ggpk_fingerprint()


# --- 생성기 귀속 ---------------------------------------------------------------


@pytest.mark.parametrize("derived,generator", [
    # grep 으로 잡히는 경우: 출력 경로가 모듈 상수에 문자열로 박혀 있다.
    ("data/active_skill_types.json", "python/scripts/derive_active_skill_types.py"),
])
def test_writer_is_attributed_by_source_scan(scanned, derived, generator):
    entry = scanned["files"][derived]
    assert generator in entry["writer_candidates"], (
        f"{derived}: 생성기 {generator} 를 못 찾았다 — 탐지 규칙이 이 관습을 놓치고 있다"
    )


def test_writer_is_attributed_by_self_declaration(scanned):
    """출력 경로를 CLI 인자로 받는 생성기는 grep 으로 안 잡힌다. 자기 신고가 유일한 단서다."""
    entry = scanned["files"]["data/db_catalog.json"]
    assert entry["declared_generator"] == "python/ggpk_index.py"
    assert entry["status"] == "generated_no_fingerprint"


def test_declared_generator_must_actually_exist():
    assert declared_generator_path("python/ggpk_index.py") == "python/ggpk_index.py"
    assert declared_generator_path("python/does_not_exist.py") is None
    assert declared_generator_path("사람이 손으로 정리함") is None
    assert declared_generator_path(None) is None


def test_reader_is_not_mistaken_for_writer(scanned):
    """오탐 회귀 가드 — validate_mod_names.py 는 *_mod_tiers.json 3종을 **읽기만** 한다.

    창(window) 방식이었을 때 10줄 아래의 무관한 REPORT_PATH 쓰기 때문에 이 세 파일의
    생성기로 잡혔다. `weapon_mod_tiers.json` 은 그 오탐 하나 때문에 '생성기 있음' 이 됐었다.
    """
    for target in ("data/weapon_mod_tiers.json", "data/defense_mod_tiers.json",
                   "data/accessory_mod_tiers.json"):
        writers = scanned["files"][target]["writer_candidates"]
        assert "python/scripts/validate_mod_names.py" not in writers, (
            f"{target}: 읽기 전용 소비자가 생성기로 잡혔다"
        )


def test_generic_variable_reuse_does_not_leak_attribution(scanned):
    """`path` 처럼 흔한 이름은 큰 모듈에서 재사용된다 — 다른 함수의 쓰기가 새면 안 된다."""
    writers = scanned["files"]["data/weapon_mod_tiers.json"]["writer_candidates"]
    assert "python/sections_continue.py" not in writers, (
        "sections_continue.py 는 이 파일을 읽기만 한다 — 변수 추적 범위가 함수 밖으로 샌다"
    )


def test_real_generators_are_found(scanned):
    """누락 회귀 가드 — 실제로 존재하는 생성기는 잡혀야 한다."""
    for target, generator in (
        ("data/defense_mod_tiers.json", "scripts/extract_defense_mod_tiers.py"),
        ("data/accessory_mod_tiers.json", "scripts/extract_accessory_mod_tiers.py"),
        ("data/valid_gems.json", "scripts/refresh_valid_gems.py"),
    ):
        assert generator in scanned["files"][target]["writer_candidates"], (
            f"{target}: 실재하는 생성기 {generator} 를 놓쳤다"
        )


# --- provenance 추출 -----------------------------------------------------------


def test_provenance_reads_both_repo_conventions():
    """최상위 관습과 `_meta` 관습이 레포에 공존한다. 한쪽만 보면 절반을 놓친다."""
    top_level = extract_provenance({"generated_by": "python/x.py", "generated_at": "2026-08-19"})
    assert top_level["generator"] == "python/x.py"
    assert top_level["generated_at"] == "2026-08-19"
    assert top_level["has_meta_block"] is False

    nested = extract_provenance({"_meta": {"script": "python/y.py", "collected_at": "2026-08-01"}})
    assert nested["generator"] == "python/y.py"
    assert nested["generated_at"] == "2026-08-01"
    assert nested["has_meta_block"] is True

    assert extract_provenance([1, 2, 3])["generator"] is None


def test_classify_prefers_fingerprint_over_every_other_signal():
    base = {
        "parse_error": None,
        "writer_candidates": ["python/x.py"],
        "declared_generator": "python/x.py",
        "externally_pinned": False,
        "provenance": {"generator": "python/x.py", "source": None, "generated_at": None,
                       "ggpk_fingerprint": "aaaaaaaaaaaaaaaa"},
    }
    assert classify(base, "aaaaaaaaaaaaaaaa") == "current"
    assert classify(base, "bbbbbbbbbbbbbbbb") == "stale"

    orphan = dict(base, writer_candidates=[], declared_generator=None,
                  provenance={"generator": None, "source": None, "generated_at": None,
                              "ggpk_fingerprint": None})
    assert classify(orphan, "aaaaaaaaaaaaaaaa") == "orphan"
    assert classify(dict(orphan, parse_error="boom"), "x") == "broken"


# --- 커버리지: db_catalog 가 못 보던 영역 ---------------------------------------


def test_inventory_covers_files_db_catalog_misses(scanned):
    """ggpk_index 의 손으로 적은 목록이 무엇을 놓치고 있는지 드러나야 한다."""
    missed = [p for p, e in scanned["files"].items() if not e["in_db_catalog"]]
    assert missed, "db_catalog 가 전부 담고 있다면 이 인벤토리는 필요 없다 — 전제를 다시 볼 것"
    assert len(scanned["files"]) > len(missed), "in_db_catalog 판정이 전부 false 다 — 경로 정규화 의심"


def test_every_emitted_status_is_documented(scanned):
    documented = set(scanned["status_meanings"])
    emitted = {e["status"] for e in scanned["files"].values()}
    assert emitted <= documented, f"설명 없는 상태: {sorted(emitted - documented)}"


def test_raw_ggpk_tables_are_out_of_scope(scanned):
    """원본은 ggpk_truth_reference 담당이다. 여기서 또 다루면 정본이 둘이 된다."""
    assert not [p for p in scanned["files"] if p.startswith("data/game_data")]
    for excluded in scanned["excluded_top_level"]:
        assert not [p for p in scanned["files"] if p.startswith(f"data/{excluded}/")]


# --- 핀의 재현성 ---------------------------------------------------------------


def test_every_pinned_path_is_git_tracked(pinned):
    """핀은 클론에서도 재현돼야 한다.

    gitignore 된 로컬 산출물(`data/atlastree-export/`, `data/ggpk_derived/`, `data/.claude/`)을
    핀에 넣으면 이 워크스테이션에서만 통과한다. 클론에서는 통째로 사라져 red 가 되고,
    그 red 를 --write 로 지우면 손실이 핀에 각인된다.
    """
    import subprocess

    tracked = set(subprocess.check_output(
        ["git", "ls-files", "--", "data"], cwd=ROOT, text=True, encoding="utf-8",
    ).splitlines())
    untracked = sorted(p for p in pinned["files"] if p not in tracked)
    assert not untracked, f"핀에 미추적 파일이 들어 있다: {untracked}"


def test_untracked_derived_files_are_declared_not_hidden(scanned):
    """범위 밖으로 뺀 것을 조용히 버리지 않는다 — 무엇이 감시 밖인지 payload 가 말해야 한다."""
    assert scanned["untracked_present"], (
        "미추적 파생 파일이 0건으로 보고됐다 — 탐지가 죽었는지 확인할 것"
    )
    assert scanned["totals"]["untracked_present"] == len(scanned["untracked_present"])
    assert not set(scanned["untracked_present"]) & set(scanned["files"]), (
        "같은 파일이 인벤토리와 미추적 목록 양쪽에 있다"
    )


def test_non_json_derived_siblings_are_in_scope():
    """같은 생성기가 뽑는 .jsonl/.csv 를 확장자로 갈라내면 데이터셋의 절반이 감시 밖이 된다."""
    from derived_data_inventory import DERIVED_SUFFIXES

    for suffix in (".json", ".jsonl", ".csv"):
        assert suffix in DERIVED_SUFFIXES


# --- 지문 커버리지의 한계를 선언한다 -------------------------------------------


def test_fingerprint_coverage_gap_is_declared(scanned):
    """지문이 못 덮는 테이블을 숨기면 '지문 일치 = 최신' 이라는 잘못된 결론이 만들어진다."""
    coverage = scanned["fingerprint_coverage"]
    assert coverage["hashed_tables"] > 0
    if coverage["extracted_tables_present"] > coverage["hashed_tables"]:
        assert coverage["extracted_but_not_hashed"], (
            "해시 안 된 테이블이 있는데 목록이 비었다 — 갭이 숨겨졌다"
        )


# --- GGPK 가 바뀌면 핀만 갱신해서 초록으로 돌아갈 수 없다 -----------------------


def test_write_refuses_to_repin_a_changed_ggpk(monkeypatch, tmp_path, capsys):
    """이 스크립트가 막으려는 사고 그 자체 — 지문만 갈아끼우고 파생물은 그대로 두는 것."""
    import derived_data_inventory as module

    monkeypatch.setattr(module, "pinned_fingerprint", lambda: "deadbeefdeadbeef")
    monkeypatch.setattr(module, "OUT_PATH", tmp_path / "inventory.json")

    assert module.main(["--write"]) == 2, "지문이 바뀌었는데 --write 가 그냥 통과했다"
    assert not (tmp_path / "inventory.json").exists(), "거부했는데 핀을 썼다"

    assert module.main(["--write", "--accept-ggpk-change"]) == 0
    assert (tmp_path / "inventory.json").exists(), "명시 승인 후에도 핀을 안 썼다"
