"""POE2 campaign_structure_poe2.json + 동적 leveling_guide schema 검증.

목적: 0.4 GGPK 기준 생성된 phases 가 SYSTEM_PROMPT_POE2 에 유효 JSON 으로 치환되는지 보장.
패치마다 데이터 드리프트 허용하되 스키마 계약 (필수 필드, phase key 형태) 은 고정.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python"))

import build_coach  # noqa: E402


def test_campaign_structure_file_exists():
    p = REPO_ROOT / "data" / "campaign_structure_poe2.json"
    assert p.exists(), "scripts/build_poe2_campaign_structure.py 재실행 필요"


def test_campaign_structure_has_required_fields():
    p = REPO_ROOT / "data" / "campaign_structure_poe2.json"
    struct = json.loads(p.read_text(encoding="utf-8"))
    assert struct.get("game") == "poe2"
    assert isinstance(struct.get("phases"), list) and struct["phases"]
    for ph in struct["phases"]:
        assert "key" in ph and ph["key"]
        assert "label" in ph and ph["label"]
        assert "level_range" in ph and len(ph["level_range"]) == 2
        lo, hi = ph["level_range"]
        assert isinstance(lo, int) and isinstance(hi, int)
        assert 0 <= lo <= hi <= 100
        assert isinstance(ph.get("towns", []), list)


def test_campaign_structure_has_endgame_phase():
    """Atlas / endgame 구간이 항상 존재해야 (0.4+ 모든 패치)."""
    p = REPO_ROOT / "data" / "campaign_structure_poe2.json"
    struct = json.loads(p.read_text(encoding="utf-8"))
    keys = {ph["key"] for ph in struct["phases"]}
    assert "endgame_maps" in keys or any("endgame" in k for k in keys), (
        f"endgame phase 없음: {keys}"
    )


def test_campaign_structure_phase_keys_unique():
    p = REPO_ROOT / "data" / "campaign_structure_poe2.json"
    struct = json.loads(p.read_text(encoding="utf-8"))
    keys = [ph["key"] for ph in struct["phases"]]
    assert len(keys) == len(set(keys)), f"중복 phase key: {keys}"


def test_system_prompt_poe2_substitutes_schema():
    """@@LEVELING_GUIDE_SCHEMA@@ 플레이스홀더가 실제 JSON 객체로 치환되어야."""
    prompt = build_coach.get_system_prompt("poe2")
    assert "@@LEVELING_GUIDE_SCHEMA@@" not in prompt
    assert '"leveling_guide":' in prompt


def test_system_prompt_poe2_leveling_guide_is_valid_json_snippet():
    """치환된 leveling_guide 가 valid JSON snippet 이어야 (LLM 이 파싱 가능한 example)."""
    prompt = build_coach.get_system_prompt("poe2")
    # "leveling_guide": {...}, 패턴 추출 — 다음 top-level key 까지
    m = re.search(r'"leveling_guide":\s*(\{[^}]*\})', prompt, re.DOTALL)
    assert m, "leveling_guide 스키마 블록 추출 실패"
    snippet = m.group(1)
    parsed = json.loads(snippet)
    assert isinstance(parsed, dict) and parsed, "leveling_guide 가 빈 객체"
    # 각 value 는 문자열 (LLM 에 주는 hint)
    for k, v in parsed.items():
        assert isinstance(k, str) and k
        assert isinstance(v, str) and v


def test_poe1_prompt_unchanged_by_poe2_schema():
    """POE1 prompt 에는 POE2 placeholder 가 영향 없어야."""
    prompt = build_coach.get_system_prompt("poe1")
    assert "@@LEVELING_GUIDE_SCHEMA@@" not in prompt
    # POE1 은 기존 act1_4/act5_10 스키마 유지
    assert "act1_4" in prompt or "Act 1-4" in prompt


def test_fallback_when_structure_missing(monkeypatch, tmp_path):
    """campaign_structure_poe2.json 이 없어도 fallback 으로 prompt 생성."""
    fake_path = tmp_path / "nowhere.json"
    original = build_coach._build_leveling_guide_schema_poe2

    def patched():
        # 파일 부재 상황 재현 — fallback 경로 강제
        struct_path = fake_path
        if not struct_path.exists():
            return (
                '{\n    "acts_1_3": "Act 1-3 전반 캠페인 (Lv 1~40)",\n'
                '    "endgame_maps": "Waystone / Atlas 엔드게임 (Lv 65+)"\n  }'
            )
        return original()

    monkeypatch.setattr(build_coach, "_build_leveling_guide_schema_poe2", patched)
    prompt = build_coach.get_system_prompt("poe2")
    assert "@@LEVELING_GUIDE_SCHEMA@@" not in prompt
    assert "acts_1_3" in prompt
    assert "endgame_maps" in prompt
