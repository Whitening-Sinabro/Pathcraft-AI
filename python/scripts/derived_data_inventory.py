# -*- coding: utf-8 -*-
"""파생 데이터 인벤토리 — 생성기 · provenance · 최신성을 한 파일로 조사한다.

왜 필요한가:
    GGPK 원본 테이블은 `_analysis/ggpk_truth_reference.json` 이 content hash 로 잠근다.
    그 위에 쌓인 `data/` 하위 파생 JSON 은 아무것도 감시하지 않는다. 그래서 리그 경계를
    조용히 넘어와 정본 행세를 한다(`atlastree-export/`, `farming_meta_all.json`, 그리고
    `db_catalog.json` 자신도 3.28 수치로 남아 있다).

이 스크립트가 하는 일 / 하지 않는 일:
    - 한다: git 이 추적하는 파생 파일마다 (생성기 · provenance · git 최신성 · GGPK 지문)을 조사.
    - 하지 않는다: GGPK 테이블 해시 **재계산**. 지문은 ggpk_truth_reference.json 에서
      **소비**한다. 원본 해시가 두 곳에서 계산되면 그 둘이 갈라지는 것이 다음 사고다.
    - 하지 않는다: 미추적(gitignore) 파일 조사. 핀이 워크스테이션에 종속되기 때문이다.
      대신 `untracked_present` 로 무엇이 밖에 있는지 선언한다.
    - 못 한다: 지금 이 레포의 파생 파일 중 `ggpk_fingerprint` 를 가진 것은 **0개**다.
      따라서 staleness 판정은 아직 아무 파일에도 적용되지 않는다 — 판정기는 있고 대상이 없다.

`python/ggpk_index.py` 와의 관계:
    ggpk_index 는 손으로 적은 DERIVED_DB_FILES 목록만 카탈로그에 담고 provenance 는 안 본다.
    여기서는 추적되는 파생 파일을 전부 훑으므로 그 목록에서 빠진 파일이 `in_db_catalog: false` 로 드러난다.

실행:
    python python/scripts/derived_data_inventory.py            # 조사 결과 요약만 출력
    python python/scripts/derived_data_inventory.py --write    # _analysis/derived_data_inventory.json 갱신
    (GGPK 지문이 바뀐 뒤에는 --accept-ggpk-change 를 함께 줘야 한다. 아래 main 주석 참고.)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("derived_data_inventory")

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
TRUTH_REFERENCE = ROOT / "_analysis" / "ggpk_truth_reference.json"
DB_CATALOG = DATA / "db_catalog.json"
OUT_PATH = ROOT / "_analysis" / "derived_data_inventory.json"

# 원본(추출물)과 대용량 수집 코퍼스는 파생 DB 가 아니다 — 조사 대상에서 뺀다.
# game_data*: GGPK 원본. builds/patch_notes: 수집물이라 생성기·지문 개념이 없다.
EXCLUDED_TOP_LEVEL = ("game_data", "game_data_poe2", "builds", "patch_notes")

# 파생물은 .json 만이 아니다 — build_ggpk_derived_item_mod_index.py 는 같은 GGPK 테이블에서
# .jsonl 과 .csv 도 함께 뽑는다. 확장자로 갈라놓으면 같은 데이터셋의 절반이 감시 밖으로 샌다.
DERIVED_SUFFIXES = (".json", ".jsonl", ".csv", ".db")
PARSEABLE_SUFFIXES = (".json",)

# 생성기 후보를 찾을 소스 트리. 테스트는 픽스처를 쓰지 생성기가 아니므로 뺀다.
SOURCE_TREES = (ROOT / "python", ROOT / "src-tauri" / "src", ROOT / "scripts")
SOURCE_SUFFIXES = (".py", ".rs", ".ts", ".mjs")
EXCLUDED_SOURCE_PARTS = ("__pycache__", "tests", "test")

# 쓰기 싱크. **파일명이 적힌 바로 그 줄**에서만 인정한다.
# 근처 몇 줄 안에 있으면 된다는 규칙(구 WRITE_WINDOW=15)은 소비자를 생성기로 둔갑시켰다:
# validate_mod_names.py 는 *_mod_tiers.json 3종을 읽기만 하는데, 10줄 아래의 REPORT_PATH 쓰기
# 때문에 그 3종의 생성기로 잡혔다.
WRITE_SINK = re.compile(
    r"write_text\(|write_bytes\(|json\.dump\(|to_string_pretty\(|writeFileSync\(|open\([^)]*['\"][wa]"
)

# 이 레포의 지배적 관습: 경로를 변수에 담고 쓰기는 수백 줄 아래에서 한다. 그래서 변수를 따라간다.
# 대문자 상수만 보면 지역 소문자 변수(tag_index_path = ...)를 통째로 놓친다.
PATH_ASSIGN = re.compile(r"^\s*([A-Za-z_]\w*)\s*(?::[^=]+)?=")

# provenance 키는 레포에 통일돼 있지 않다. 실제로 쓰이는 이름을 전부 받아준다.
GENERATOR_KEYS = ("generated_by", "generator", "script", "generated_from")
TIMESTAMP_KEYS = ("generated_at", "generated_date", "collected_at", "verified_at")
SOURCE_KEYS = ("source_table", "source_tables", "source_file", "source", "sources", "source_dataset")
FINGERPRINT_KEYS = ("ggpk_fingerprint",)

# provenance 문자열 안에서 생성기 경로처럼 보이는 토큰.
PATH_TOKEN = re.compile(r"[\w./\\-]+\.(?:py|rs|ts|mjs)")


def _rel(path: Path) -> str:
    """ROOT 기준 상대 경로 — 인벤토리의 모든 키가 이 형식이다."""
    return path.relative_to(ROOT).as_posix()


def _display(path: Path) -> str:
    """로그·예외 메시지용 경로. ROOT 밖(테스트의 tmp_path 등)이어도 터지지 않아야 한다."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def ggpk_fingerprint() -> str:
    """현재 GGPK 추출본의 단일 지문 — ggpk_truth_reference.json 의 테이블 해시를 집계한다.

    재계산하지 않는다. 원본 해시의 정본은 ggpk_truth_builder.py 하나뿐이어야 한다.
    """
    if not TRUTH_REFERENCE.exists():
        raise FileNotFoundError(
            f"{_display(TRUTH_REFERENCE)} 없음. "
            "python/scripts/ggpk_truth_builder.py 를 먼저 실행할 것."
        )
    reference = json.loads(TRUTH_REFERENCE.read_text(encoding="utf-8"))
    tables = reference.get("tables", {})
    if not tables:
        raise ValueError("ggpk_truth_reference.json 에 tables 블록이 비어 있다.")
    lines = [
        f"{name}:{info.get('content_hash', info.get('error', 'missing'))}"
        for name, info in sorted(tables.items())
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]


def externally_pinned_paths() -> set[str]:
    """ggpk_truth_reference.json 이 이미 따로 잠그고 있는 파일.

    `schema.min.json` 은 생성기도 provenance 도 없지만 방치된 게 아니라 schema_pin 이 잡고 있다.
    이 구분을 안 하면 인벤토리가 이미 관리되는 파일을 orphan 으로 신고한다.
    """
    if not TRUTH_REFERENCE.exists():
        return set()
    reference = json.loads(TRUTH_REFERENCE.read_text(encoding="utf-8"))
    pin_path = reference.get("schema_pin", {}).get("path")
    return {pin_path} if pin_path else set()


def _in_scope(path: Path) -> bool:
    return (
        path.suffix in DERIVED_SUFFIXES
        and path.relative_to(DATA).parts[0] not in EXCLUDED_TOP_LEVEL
    )


def git_tracked_data_paths() -> set[str]:
    try:
        raw = subprocess.check_output(
            ["git", "ls-files", "--", "data"],
            cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        raise RuntimeError(f"git ls-files 실패 — 추적 여부를 알 수 없다: {exc}") from exc
    return {line.strip() for line in raw.splitlines() if line.strip()}


def fingerprint_coverage() -> dict[str, Any]:
    """지문이 GGPK 의 어디까지를 덮는지 — 덮지 못하는 테이블을 숨기지 않는다.

    ggpk_truth_builder 의 KEY_FIELDS 는 추출된 테이블 전부가 아니다. 빠진 테이블은
    아무리 바뀌어도 지문이 그대로다. 이 사실이 payload 에 안 적혀 있으면
    "지문 일치 = 최신" 이라는 잘못된 결론이 만들어진다.
    """
    reference = json.loads(TRUTH_REFERENCE.read_text(encoding="utf-8"))
    hashed = set(reference.get("tables", {}))
    game_data = ROOT / "data" / "game_data"
    extracted = {p.stem for p in game_data.glob("*.json")} if game_data.is_dir() else set()
    return {
        "hashed_tables": len(hashed),
        "extracted_tables_present": len(extracted),
        "extracted_but_not_hashed": sorted(extracted - hashed),
        "note": (
            "extracted_but_not_hashed 의 테이블은 바뀌어도 ggpk_fingerprint 가 움직이지 않는다. "
            "해소하려면 ggpk_truth_builder.KEY_FIELDS 를 넓혀야 한다(앵커 재생성 동반)."
        ),
    }


def partition_derived_paths() -> tuple[list[Path], list[str]]:
    """레포의 파생 파일을 (인벤토리 대상 = git 추적본, 선언 대상 = 미추적) 으로 한 번에 가른다.

    미추적 파일(`data/atlastree-export/`, `data/ggpk_derived/`, `data/.claude/` 등 gitignore)을
    핀에 넣으면 이 워크스테이션에서만 통과하는 핀이 된다 — 클론에서는 통째로 사라져 테스트가
    red 가 되고, 그 red 를 `--write` 로 지우면 손실이 핀에 각인된다.
    그렇다고 조용히 버리지도 않는다. 밖에 무엇이 있는지는 `untracked_present` 로 남긴다.
    """
    tracked_index = git_tracked_data_paths()
    tracked: list[Path] = []
    untracked: list[str] = []
    for path in sorted(DATA.rglob("*")):
        if not path.is_file() or not _in_scope(path):
            continue
        rel = _rel(path)
        if rel in tracked_index:
            tracked.append(path)
        else:
            untracked.append(rel)
    return tracked, untracked


def _lookup(container: Any, keys: tuple[str, ...]) -> str | None:
    """dict 에서 keys 중 처음 발견되는 값을 짧은 문자열로 돌려준다."""
    if not isinstance(container, dict):
        return None
    for key in keys:
        value = container.get(key)
        if not value:
            continue
        if isinstance(value, (list, tuple)):
            value = ", ".join(str(v) for v in value[:3])
        return str(value)[:200]
    return None


def extract_provenance(value: Any) -> dict[str, Any]:
    """최상위와 `_meta`/`meta` 두 곳을 본다 — 레포에 두 관습이 공존한다."""
    blocks: list[Any] = [value]
    if isinstance(value, dict):
        for meta_key in ("_meta", "meta"):
            if isinstance(value.get(meta_key), dict):
                blocks.append(value[meta_key])

    found: dict[str, Any] = {
        "generator": None,
        "generated_at": None,
        "source": None,
        "ggpk_fingerprint": None,
    }
    for block in blocks:
        for field, keys in (
            ("generator", GENERATOR_KEYS),
            ("generated_at", TIMESTAMP_KEYS),
            ("source", SOURCE_KEYS),
            ("ggpk_fingerprint", FINGERPRINT_KEYS),
        ):
            if found[field] is None:
                found[field] = _lookup(block, keys)

    found["has_meta_block"] = isinstance(value, dict) and any(
        isinstance(value.get(k), dict) for k in ("_meta", "meta")
    )
    found["declared_dataset_kind"] = _lookup(value, ("dataset_kind",))
    return found


def _variable_scope(lines: list[str], index: int) -> list[str]:
    """대입 지점부터 그 변수가 살아 있는 범위까지.

    `path` 같은 흔한 이름은 큰 모듈에서 수십 번 재사용된다. 파일 전체를 뒤지면
    다른 함수의 쓰기가 이 함수의 읽기에 잘못 귀속된다(sections_continue.py 4500줄이 실례).
    모듈 최상단 상수(들여쓰기 0)만 파일 전체를 본다 — 그게 이 레포의 생성기 관습이다.
    """
    indent = len(lines[index]) - len(lines[index].lstrip())
    if indent == 0:
        return lines
    for j in range(index + 1, len(lines)):
        stripped = lines[j].strip()
        if not stripped:
            continue
        if len(lines[j]) - len(lines[j].lstrip()) <= indent and re.match(r"(def |class |@)", stripped):
            return lines[index:j]
    return lines[index:]


def _writes_through_variable(lines: list[str], var: str) -> bool:
    """변수에 담긴 경로가 실제로 **쓰기**에 쓰이는지.

    직접 호출(`p.write_text`)과 헬퍼 경유(`_write_json(p, ...)`) 둘 다 본다 — 이 레포의
    GGPK 파생 인덱스 빌더는 전부 헬퍼 경유라 직접 호출만 보면 하나도 안 잡힌다.
    `open(var, ...)` 은 모드까지 확인한다. 모드를 안 보면 읽기 오픈이 쓰기로 둔갑한다.
    """
    pattern = re.compile(
        rf"\b{var}\.write_text\(|\b{var}\.write_bytes\(|"
        rf"open\(\s*{var}\s*,\s*['\"][wa]|json\.dump\([^)]*,\s*{var}\b|"
        rf"\b\w*(?:write|dump|save|emit)\w*\(\s*{var}\s*[,)]",
        re.IGNORECASE,
    )
    return any(pattern.search(line) for line in lines)


def _is_writer(lines: list[str], name: str) -> bool:
    """소스가 `name` 파일을 쓰는가.

    인정 조건은 둘뿐이다 — (a) 파일명이 적힌 줄이 변수 대입이고 그 변수가 **살아 있는 범위
    안에서** 쓰기에 쓰인다, (b) 파일명이 적힌 **그 줄 자체**가 쓰기다.
    읽기만 하는 소비자를 배제하려면 이 정도로 좁혀야 한다.
    """
    for i, line in enumerate(lines):
        if name not in line:
            continue
        assigned = PATH_ASSIGN.match(line)
        if assigned and _writes_through_variable(_variable_scope(lines, i), assigned.group(1)):
            return True
        if WRITE_SINK.search(line):
            return True
    return False


def build_writer_index(derived_paths: list[Path]) -> dict[str, list[str]]:
    """파생 파일을 실제로 쓰는 소스를 찾는다.

    단정이 아니라 후보다 — 경로를 동적으로 조립하는 생성기는 이 방식으로 잡히지 않는다.
    """
    sources: list[tuple[str, list[str]]] = []
    for tree in SOURCE_TREES:
        if not tree.exists():
            continue
        for path in sorted(tree.rglob("*")):
            if path.suffix not in SOURCE_SUFFIXES:
                continue
            if any(part in EXCLUDED_SOURCE_PARTS for part in path.parts):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError as exc:
                logger.warning("소스 읽기 실패 %s: %s", _rel(path), exc)
                continue
            sources.append((_rel(path), lines))

    index: dict[str, list[str]] = {}
    for derived in derived_paths:
        name = derived.name
        index[_rel(derived)] = [src for src, lines in sources if _is_writer(lines, name)]
    return index


def git_last_commit_map() -> dict[str, dict[str, str]]:
    """data/ 전체 히스토리를 한 번에 읽어 파일별 최신 커밋을 뽑는다."""
    try:
        raw = subprocess.check_output(
            ["git", "log", "--name-only", "--date=short", "--format=%x01%H %ad", "--", "data"],
            cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        )
    except (subprocess.CalledProcessError, OSError) as exc:
        logger.warning("git log 실패 — 최신성 항목은 비워둔다: %s", exc)
        return {}

    out: dict[str, dict[str, str]] = {}
    commit = date = ""
    for line in raw.splitlines():
        if line.startswith("\x01"):
            commit, _, date = line[1:].partition(" ")
            continue
        path = line.strip()
        if path and path not in out:
            out[path] = {"commit": commit[:8], "date": date}
    return out


def declared_generator_path(generator: str | None) -> str | None:
    """자기 신고한 생성기가 실제로 레포에 있는지 — 있으면 정규화된 경로를 돌려준다.

    출력 경로를 CLI 인자로 받는 생성기(`ggpk_index.py --write-catalog`)는 파일명 grep 으로
    절대 안 잡힌다. 그런 경우 파일이 스스로 적어둔 `generated_by` 가 유일한 단서다.
    """
    if not generator:
        return None
    for token in PATH_TOKEN.findall(generator):
        candidate = ROOT / token.replace("\\", "/")
        if candidate.is_file():
            return candidate.resolve().relative_to(ROOT).as_posix()
    return None


def classify(entry: dict[str, Any], current_fingerprint: str) -> str:
    """조사 결과 → 한 단어 상태. 우선순위는 '고쳐야 하는 정도' 순."""
    if entry["parse_error"]:
        return "broken"
    provenance = entry["provenance"]
    pinned = provenance["ggpk_fingerprint"]
    if pinned:
        return "current" if pinned == current_fingerprint else "stale"
    if entry["externally_pinned"]:
        return "pinned_elsewhere"
    if entry["writer_candidates"] or entry["declared_generator"]:
        return "generated_no_fingerprint"
    if provenance["generator"] or provenance["source"] or provenance["generated_at"]:
        return "declared_no_generator"
    return "orphan"


def build_inventory() -> dict[str, Any]:
    current_fingerprint = ggpk_fingerprint()
    derived_paths, untracked = partition_derived_paths()
    writers = build_writer_index(derived_paths)
    commits = git_last_commit_map()
    pinned_elsewhere = externally_pinned_paths()

    catalogued: set[str] = set()
    if DB_CATALOG.exists():
        try:
            catalogued = set(json.loads(DB_CATALOG.read_text(encoding="utf-8")).get("derived", {}))
        except json.JSONDecodeError as exc:
            logger.warning("db_catalog.json 파싱 실패 — in_db_catalog 는 전부 false 가 된다: %s", exc)

    files: dict[str, Any] = {}
    for path in derived_paths:
        rel = _rel(path)
        raw = path.read_bytes()
        parse_error = None
        value: Any = None
        if path.suffix in PARSEABLE_SUFFIXES:
            try:
                value = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                parse_error = f"{type(exc).__name__}: {exc}"

        entry: dict[str, Any] = {
            "bytes": len(raw),
            "sha256_16": hashlib.sha256(raw).hexdigest()[:16],
            "parse_error": parse_error,
            "provenance": extract_provenance(value),
            "writer_candidates": writers.get(rel, []),
            "declared_generator": None,
            "externally_pinned": rel in pinned_elsewhere,
            "last_commit": commits.get(rel, {}),
            "in_db_catalog": path.relative_to(DATA).as_posix() in catalogued,
        }
        entry["declared_generator"] = declared_generator_path(entry["provenance"]["generator"])
        entry["status"] = classify(entry, current_fingerprint)
        files[rel] = entry

    by_status: dict[str, int] = {}
    for entry in files.values():
        by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1

    return {
        "schema_version": 1,
        "dataset_kind": "pathcraft_derived_data_inventory",
        "generated_by": "python/scripts/derived_data_inventory.py",
        "description": (
            "data/ 하위 파생 JSON 의 생성기·provenance·최신성 조사 결과. "
            "지문은 _analysis/ggpk_truth_reference.json 에서 소비하며 여기서 재계산하지 않는다."
        ),
        "ggpk_fingerprint": current_fingerprint,
        "fingerprint_source": "_analysis/ggpk_truth_reference.json",
        "fingerprint_coverage": fingerprint_coverage(),
        "excluded_top_level": list(EXCLUDED_TOP_LEVEL),
        "untracked_present": untracked,
        "untracked_note": (
            "레포에 실재하지만 git 미추적이라 인벤토리 밖. 핀이 클론에서 재현되려면 여기 있어야 한다. "
            "감시가 필요하면 gitignore 에서 빼거나 생성기 + ggpk_fingerprint 를 갖출 것."
        ),
        "totals": {
            "files": len(files),
            "fingerprinted": sum(
                1 for e in files.values() if e["provenance"]["ggpk_fingerprint"]
            ),
            "untracked_present": len(untracked),
            "by_status": dict(sorted(by_status.items())),
        },
        "status_meanings": {
            "current": "ggpk_fingerprint 이 현재 추출본과 일치",
            "stale": "ggpk_fingerprint 이 남아 있으나 현재 추출본과 불일치 — 재생성 대상",
            "generated_no_fingerprint": "생성기를 찾았으나 지문이 없어 최신성을 알 수 없음",
            "declared_no_generator": "provenance 는 있으나 생성기를 자동으로 찾지 못함 — '없다' 가 아니라 '못 찾았다'. 경로를 동적으로 조립하는 생성기는 탐지 밖일 수 있다",
            "pinned_elsewhere": "생성기는 없지만 ggpk_truth_reference.json 의 schema_pin 이 잠그고 있음",
            "orphan": "생성기도 provenance 도 없음 — 출처 불명",
            "broken": "JSON 파싱 실패",
        },
        "files": files,
    }


def pinned_fingerprint() -> str | None:
    if not OUT_PATH.exists():
        return None
    return json.loads(OUT_PATH.read_text(encoding="utf-8")).get("ggpk_fingerprint")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="파생 데이터 인벤토리 조사")
    parser.add_argument("--write", action="store_true", help=f"{_display(OUT_PATH)} 갱신")
    parser.add_argument(
        "--accept-ggpk-change", action="store_true",
        help="GGPK 지문이 바뀐 상태에서 핀을 갱신할 때 필요. 파생 파일 재생성을 마친 뒤에만 쓸 것.",
    )
    args = parser.parse_args(argv)

    inventory = build_inventory()

    # GGPK 가 바뀌었다는 것은 모든 파생물의 최신성이 불명이 됐다는 뜻이다. 그 상태에서 핀만
    # 갱신하면 테스트는 초록으로 돌아오지만 파생 파일은 한 개도 안 고쳐진 채로 남는다.
    # 그 조용한 재초록화가 애초에 이 스크립트가 막으려던 사고다.
    previous = pinned_fingerprint()
    if args.write and previous and previous != inventory["ggpk_fingerprint"] and not args.accept_ggpk_change:
        logger.error(
            "GGPK 지문이 바뀌었다 (%s → %s). 핀만 갱신하면 파생 파일 %d개의 낡음이 그대로 묻힌다.\n"
            "각 생성기를 다시 돌린 뒤 --accept-ggpk-change 를 함께 줄 것.",
            previous, inventory["ggpk_fingerprint"], inventory["totals"]["files"],
        )
        return 2

    if args.write:
        OUT_PATH.write_text(
            json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        logger.info("wrote %s", _display(OUT_PATH))

    logger.info("ggpk_fingerprint = %s", inventory["ggpk_fingerprint"])
    logger.info("파생 파일(git 추적) %d개 | 지문 보유 %d개 | 미추적 %d개",
                inventory["totals"]["files"], inventory["totals"]["fingerprinted"],
                inventory["totals"]["untracked_present"])
    for status, count in inventory["totals"]["by_status"].items():
        logger.info("  %-26s %4d", status, count)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    raise SystemExit(main())
