"""`scripts/build_poe2_build_overlay.py` 안전 게이트 + 단계(stage) 분기.

이 빌더가 만드는 것은 사용자가 게임에 직접 설치하는 로그 필터라, 조용히 틀리면
"안 뜨는 아이템"으로만 드러난다. 그래서 게이트 4개를 테스트로 못박는다.

  1. 어휘 게이트  — 베이스 필터에 없는 Class/BaseType 은 절대 방출하지 않는다
  2. 대비 게이트  — 글자/배경 휘도 차가 기준 미만이면 빌드 자체를 실패시킨다
  3. Show-only   — 오버레이는 무엇도 숨기지 않는다
  4. 단계 게이트  — --stage 로 해당 단계 룰만 방출한다

그리고 실제 산출물(filters/PathcraftAI_Fartfinder_*.filter) 3종이 위 성질을
지키는지 파일 자체로 재확인한다 — 생성기와 같은 코드를 두 번 믿지 않기 위함.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_poe2_build_overlay.py"
SPEC_PATH = REPO_ROOT / "data" / "filter_build_targets" / "poe2_fartfinder_skadoosh_0_5_5.json"
FILTERS_DIR = REPO_ROOT / "filters"
NEVERSINK_HEADER = "NeverSink's Indepth Loot Filter"

STAGE_FILES = {
    "campaign": "PathcraftAI_Fartfinder_1-Campaign_on_NeverSink-SOFT.filter",
    "maps": "PathcraftAI_Fartfinder_2-EarlyMaps_on_NeverSink-REGULAR.filter",
    "endgame": "PathcraftAI_Fartfinder_3-Endgame_on_NeverSink-STRICT.filter",
}


def _load_module():
    spec = importlib.util.spec_from_file_location("build_poe2_build_overlay", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _overlay_text(filter_path: Path) -> str:
    """오버레이 구간만 잘라낸다 — NeverSink 본문이 섞이면 집계가 전부 오염된다."""
    text = filter_path.read_text(encoding="utf-8")
    cut = text.index(NEVERSINK_HEADER)
    return text[:cut]


@pytest.fixture(scope="module")
def mod():
    return _load_module()


@pytest.fixture(scope="module")
def spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


class TestContrastGate:
    def test_all_spec_styles_clear_the_threshold(self, mod, spec):
        for name, style in spec["styles"].items():
            mod.check_contrast(name, style)  # raises SystemExit on failure

    def test_low_contrast_style_is_rejected(self, mod):
        # 보라 배경 위 보라 글자 — 인게임에서 글자가 배경에 먹힌다
        bad = {"text": [80, 0, 140], "background": [74, 0, 140]}
        with pytest.raises(SystemExit):
            mod.check_contrast("bad", bad)

    def test_luminance_is_monotonic(self, mod):
        assert mod.luminance([0, 0, 0]) < mod.luminance([128, 128, 128]) < mod.luminance([255, 255, 255])


class TestVocabularyGate:
    def test_unknown_token_is_rejected(self, mod):
        base = 'BaseType "Iron Greaves" "Spiked Club"'
        assert mod.vocab_ok("Iron Greaves", base)
        assert not mod.vocab_ok("Brigand Mace", base)

    def test_every_spec_name_survives_against_its_real_base(self, spec):
        """스펙에 적힌 이름이 실제 NeverSink 어휘에 전부 있는지 — 오타 1글자면 조용히 빠진다."""
        for output in spec["_meta"]["outputs"]:
            base = (REPO_ROOT / "data" / "filter_sources" / output["base"]).read_text(encoding="utf-8")
            for rule in spec["rules"]:
                stages = rule.get("stages")
                if stages and output["stage"] not in stages:
                    continue
                for cls in rule.get("class", []) or []:
                    assert f'"{cls}"' in base, f"{output['stage']}: class {cls!r} 없음"
                for base_type in rule["base_types"]:
                    assert base_type in base, f"{output['stage']}: BaseType {base_type!r} 없음"


class TestStageGate:
    def test_stage_rule_counts(self, spec):
        """단계별로 몇 개가 나가야 하는지를 스펙에서 직접 센다."""
        expected = {"campaign": 0, "maps": 0, "endgame": 0}
        for rule in spec["rules"]:
            for stage in rule.get("stages", list(expected)):
                expected[stage] += 1
        for stage, path in STAGE_FILES.items():
            overlay = _overlay_text(FILTERS_DIR / path)
            emitted = overlay.count("\nShow\n")
            assert emitted == expected[stage], f"{stage}: {emitted} != {expected[stage]}"

    def test_levelling_rules_never_reach_the_map_files(self, spec):
        levelling_bases = [
            b for r in spec["rules"] if r.get("stages") == ["campaign"] for b in r["base_types"]
        ]
        assert levelling_bases, "campaign 전용 룰이 사라졌다 — 테스트가 무력화된 상태"
        for stage in ("maps", "endgame"):
            overlay = _overlay_text(FILTERS_DIR / STAGE_FILES[stage])
            for base_type in levelling_bases:
                assert base_type not in overlay, f"{stage} 에 레벨링 베이스 {base_type!r} 누출"

    def test_core_rules_reach_every_stage(self):
        """시신걸음은 11레벨부터 우버까지 계속 필요하다 — 한 단계라도 빠지면 빌드가 끊긴다."""
        for stage, path in STAGE_FILES.items():
            assert "Iron Greaves" in _overlay_text(FILTERS_DIR / path), f"{stage} 에 시신걸음 없음"


class TestShowOnly:
    def test_no_hide_block_in_any_overlay(self):
        for stage, path in STAGE_FILES.items():
            overlay = _overlay_text(FILTERS_DIR / path)
            assert "\nHide\n" not in overlay, f"{stage} 오버레이가 무언가를 숨긴다"

    def test_overlay_precedes_the_base(self):
        """first-match-wins — 오버레이가 뒤로 가면 NeverSink 규칙에 전부 먹힌다."""
        for stage, path in STAGE_FILES.items():
            text = (FILTERS_DIR / path).read_text(encoding="utf-8")
            assert text.index("# [overlay]") < text.index(NEVERSINK_HEADER), stage


class TestEmittedFilesMatchTheirDeclaredBase:
    def test_each_file_carries_the_base_its_spec_declares(self, spec):
        for output in spec["_meta"]["outputs"]:
            text = (FILTERS_DIR / output["file"]).read_text(encoding="utf-8")
            assert f"# stage: {output['stage']} | base: {output['base']}" in text

    def test_regeneration_is_reproducible(self, spec, tmp_path):
        """스펙만 있으면 같은 바이트가 다시 나와야 한다 — 손으로 고친 필터를 잡는다."""
        for output in spec["_meta"]["outputs"]:
            out = tmp_path / output["file"]
            subprocess.run(
                [
                    sys.executable, str(SCRIPT_PATH),
                    "--base", str(REPO_ROOT / "data" / "filter_sources" / output["base"]),
                    "--spec", str(SPEC_PATH),
                    "--stage", output["stage"],
                    "--out", str(out),
                ],
                check=True,
                capture_output=True,
            )
            assert out.read_bytes() == (FILTERS_DIR / output["file"]).read_bytes(), output["file"]
