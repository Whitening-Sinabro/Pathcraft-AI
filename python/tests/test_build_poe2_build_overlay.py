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
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_poe2_build_overlay.py"
SPEC_PATH = REPO_ROOT / "data" / "filter_build_targets" / "poe2_fartfinder_skadoosh_0_5_5.json"
FILTERS_DIR = REPO_ROOT / "filters"
NEVERSINK_HEADER = "NeverSink's Indepth Loot Filter"

SOURCES_DIR = REPO_ROOT / "data" / "filter_sources"

STAGE_FILES = {
    "campaign": "PathcraftAI_Fartfinder_1-Campaign_on_NeverSink-SOFT.filter",
    "maps": "PathcraftAI_Fartfinder_2-EarlyMaps_on_NeverSink-REGULAR.filter",
    "endgame": "PathcraftAI_Fartfinder_3-Endgame_on_NeverSink-STRICT.filter",
}

# .gitignore excludes *.filter, so a fresh clone has neither the NeverSink bases
# nor the generated overlays. Those tests skip with an actionable message instead
# of failing -- but the pin check below still runs, so the pins themselves can
# never rot unnoticed.
FETCH_HINT = "run: python scripts/fetch_neversink_poe2_bases.py"
BUILD_HINT = "regenerate: see the header of any filters/PathcraftAI_Fartfinder_*.filter"

needs_bases = pytest.mark.skipif(
    not all((SOURCES_DIR / n).exists() for n in
            ("neversink_poe2_soft.filter", "neversink_poe2_regular.filter", "neversink_poe2_strict.filter")),
    reason=f"NeverSink base filters absent -- {FETCH_HINT}",
)
needs_outputs = pytest.mark.skipif(
    not all((FILTERS_DIR / f).exists() for f in STAGE_FILES.values()),
    reason=f"generated overlays absent -- {BUILD_HINT}",
)


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


class TestBasePins:
    """_meta.bases is the only committed record of what the overlays were built
    against. If it drifts from the files on disk, every other gate in this file
    is checking the wrong vocabulary."""

    def test_pin_block_covers_every_declared_output(self, spec):
        pinned = {b["file"] for b in spec["_meta"]["bases"]}
        for output in spec["_meta"]["outputs"]:
            assert output["base"] in pinned, f"{output['base']} 가 _meta.bases 에 없다"

    def test_pins_are_well_formed(self, spec):
        for b in spec["_meta"]["bases"]:
            assert len(b["sha256"]) == 64 and int(b["sha256"], 16) >= 0
            assert b["bytes"] > 100_000, b["file"]
            assert b["url"].startswith("https://raw.githubusercontent.com/NeverSinkDev/")

    @needs_bases
    def test_on_disk_bases_match_their_pins(self, spec):
        import hashlib

        for b in spec["_meta"]["bases"]:
            path = SOURCES_DIR / b["file"]
            if not path.exists():
                continue
            data = path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == b["sha256"], (
                f"{b['file']} 가 핀과 다르다 — NeverSink 새 릴리스라면 어휘 게이트부터 재검사"
            )
            assert len(data) == b["bytes"]


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


class TestValueGate:
    def test_nonsense_beam_colour_is_rejected(self, mod):
        allowed = {"font": {36, 45}, "sound_id": {1, 3}, "volume": {100, 300},
                   "beam": {"Purple", "Red"}, "icon_size": {0, 1, 2},
                   "icon_color": {"Purple"}, "icon_shape": {"Star"}}
        good = {"font": 36, "sound": [1, 200], "beam": "Purple", "icon": [0, "Purple", "Star"]}
        mod.check_style_values("ok", good, allowed)
        for broken in (
            {**good, "beam": "Chartreuse"},
            {**good, "icon": [0, "Chartreuse", "Star"]},
            {**good, "icon": [0, "Purple", "Banana"]},
            {**good, "font": 999},
            {**good, "sound": [1, 9999]},
        ):
            with pytest.raises(SystemExit):
                mod.check_style_values("broken", broken, allowed)


class TestVocabularyGate:
    def test_vocabulary_is_a_token_set_not_a_substring_test(self, mod):
        """`"Club" in base_text` 는 'Spiked Club' 때문에 통과한다 — 게임에는 없는 이름인데도.

        적대검증이 실제로 이 구멍으로 깨진 필터를 초록으로 통과시켰다.
        """
        base = 'Show\n\tBaseType == "Iron Greaves" "Spiked Club"\n\tClass == "Boots"\n'
        vocab = mod.base_vocabulary(base)
        assert "Spiked Club" in vocab and "Boots" in vocab
        assert "Club" not in vocab, "부분 문자열이 어휘로 통과하면 안 된다"
        assert "Greaves" not in vocab

    def test_comments_do_not_contribute_vocabulary(self, mod):
        base = '# Brigand Mace is mentioned only in a comment\nShow\n\tBaseType == "Slim Mace"\n'
        assert mod.base_vocabulary(base) == {"Slim Mace"}

    def test_game_data_supplements_the_base_filter(self, mod):
        """NeverSink 가 안 부르는 실존 베이스(도둑 철퇴)를 게임 데이터가 살려준다."""
        names = mod.game_base_names()
        assert "Brigand Mace" in names
        assert "Spined Bracers" in names

    @needs_bases
    def test_every_spec_name_survives_against_its_real_base(self, mod, spec):
        """스펙 이름이 전부 실제 어휘에 있는지 — 오타 1글자면 조용히 빠진다.

        어휘 = 베이스 필터의 인용 토큰 ∪ GGPK 파생 베이스명. 후자가 없으면
        NeverSink 가 안 부르는 실존 베이스(도둑 철퇴)를 스펙에 쓸 수 없다.
        """
        game = mod.game_base_names()
        for output in spec["_meta"]["outputs"]:
            base = (SOURCES_DIR / output["base"]).read_text(encoding="utf-8")
            vocab = mod.base_vocabulary(base) | game
            for rule in spec["rules"]:
                stages = rule.get("stages")
                if stages and output["stage"] not in stages:
                    continue
                for cls in rule.get("class", []) or []:
                    assert cls in vocab, f"{output['stage']}: class {cls!r} 없음"
                for base_type in rule["base_types"]:
                    assert base_type in vocab, f"{output['stage']}: BaseType {base_type!r} 없음"


@needs_outputs
class TestStageGate:
    def test_stage_rule_counts(self, spec):
        """단계별로 어떤 룰이 나가야 하는지를 스펙에서 직접 센다.

        블록 수로 세면 안 된다 — 라우드니스 게이트가 한 룰을 볼륨별로 쪼개므로
        블록 수는 스펙에서 예측되지 않는다. 룰 이름 집합이 계약이다.
        """
        expected: dict[str, set[str]] = {"campaign": set(), "maps": set(), "endgame": set()}
        for rule in spec["rules"]:
            for stage in rule.get("stages", list(expected)):
                expected[stage].add(rule["name"])
        for stage, path in STAGE_FILES.items():
            emitted = set(re.findall(r"^# \[overlay\] (.+)$", _overlay_text(FILTERS_DIR / path), re.M))
            assert emitted == expected[stage], (
                f"{stage}: 빠짐={sorted(expected[stage] - emitted)} 남음={sorted(emitted - expected[stage])}"
            )

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


@needs_outputs
class TestNoAlertDowngrade:
    """첫 매치 승리 = 오버레이가 NeverSink 경보를 대체한다.

    NeverSink 가 소리치던 것을 우리가 속삭이면 필터를 나쁘게 만든 것이다.
    적대검증이 Astrid's Creativity(최상위 45/300) 가 가장 조용한 스타일로
    내려앉은 것을 포함해 40건을 찾아냈다.
    """

    @needs_bases
    def test_no_emitted_block_is_quieter_than_the_base(self, mod, spec):
        for output in spec["_meta"]["outputs"]:
            base_text = (SOURCES_DIR / output["base"]).read_text(encoding="utf-8")
            base_blocks = mod.parse_base_blocks(base_text)
            overlay = _overlay_text(FILTERS_DIR / output["file"])
            for block in overlay.split("\nShow\n")[1:]:
                body = block.split("\n\n")[0]
                names = re.findall(r'"([^"]+)"', re.search(r"\tBaseType [^\n]+", body).group())
                rarity_line = re.search(r"\tRarity ([^\n]+)", body)
                scope = set(rarity_line.group(1).split()) if rarity_line else set(mod.ALL_RARITIES)
                font = int(re.search(r"\tSetFontSize (\d+)", body).group(1))
                volume = int(re.search(r"\tPlayAlertSound \d+ (\d+)", body).group(1))
                for name in names:
                    req_font, req_vol, _, _ = mod.required_loudness(name, scope, set(), base_blocks)
                    assert font >= req_font, f"{output['stage']} {name}: font {font} < base {req_font}"
                    assert volume >= req_vol, f"{output['stage']} {name}: volume {volume} < base {req_vol}"


@needs_outputs
class TestExactMatching:
    """`BaseType "Exalted Orb"` 는 'Perfect Exalted Orb'(S급)까지 삼킨다."""

    def test_every_overlay_basetype_line_is_exact(self):
        for stage, path in STAGE_FILES.items():
            for line in _overlay_text(FILTERS_DIR / path).splitlines():
                if line.startswith("\tBaseType"):
                    assert line.startswith("\tBaseType == "), f"{stage}: 부분 일치 — {line.strip()}"

    def test_no_overlay_token_is_a_prefix_of_a_longer_real_base(self, mod, spec):
        """정확 일치라도 스펙에 'Ruby' 같은 짧은 이름이 있으면 의도를 의심해야 한다."""
        names = mod.game_base_names()
        for rule in spec["rules"]:
            if rule.get("substring"):
                continue
            for token in rule["base_types"]:
                longer = [n for n in names if n != token and token in n]
                if longer and token not in names:
                    raise AssertionError(f"{token!r} 은 실존 베이스가 아니면서 {longer[:3]} 의 부분 문자열")


@needs_outputs
class TestBuildCriticalItems:
    """가이드가 못박은 3대 핵심 유니크가 전 단계에 살아 있어야 한다."""

    CORE = {"Iron Greaves": "시신걸음", "Spiked Club": "참호목", "Spined Bracers": "뱀 이빨"}

    def test_all_three_core_uniques_present_at_every_stage(self):
        for stage, path in STAGE_FILES.items():
            overlay = _overlay_text(FILTERS_DIR / path)
            for base, korean in self.CORE.items():
                assert f'"{base}"' in overlay, f"{stage} 에 {korean}({base}) 없음"

    def test_core_unique_rules_are_rarity_scoped(self, spec):
        """유니크 룰이 등급을 안 걸면 같은 베이스의 레어까지 먹어 티어 경보를 덮는다."""
        for rule in spec["rules"]:
            if rule["base_types"] and rule["base_types"][0] in self.CORE:
                assert rule.get("rarity") == ["Unique"], rule["name"]


@needs_outputs
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


@needs_outputs
class TestEmittedFilesMatchTheirDeclaredBase:
    def test_each_file_carries_the_base_its_spec_declares(self, spec):
        for output in spec["_meta"]["outputs"]:
            text = (FILTERS_DIR / output["file"]).read_text(encoding="utf-8")
            assert f"# stage: {output['stage']} | base: {output['base']}" in text

    @needs_bases
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
