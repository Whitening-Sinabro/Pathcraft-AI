"""Guards for the POE2 Cursemaster overlay generator (spec + block hygiene)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "data/filter_build_targets/poe2_cursemaster_tangjeong_0_5_5.json"
SCRIPT = ROOT / "scripts/build_poe2_cursemaster_overlay.py"


@pytest.fixture(scope="module")
def spec():
    return json.loads(SPEC.read_text(encoding="utf-8"))


def test_spec_styles_have_contrast(spec):
    def lum(rgb):
        r, g, b = (c / 255.0 for c in rgb[:3])
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    for name, style in spec["styles"].items():
        assert abs(lum(style["text"]) - lum(style["background"])) >= 0.35, name


def test_spec_rules_reference_known_styles(spec):
    for rule in spec["rules"]:
        assert rule["style"] in spec["styles"], rule["name"]
        assert rule["base_types"], rule["name"]


def test_core_targets_present(spec):
    all_bases = {b for r in spec["rules"] for b in r["base_types"]}
    # 빌드 코어 3종은 스펙에서 절대 빠지면 안 된다 (가이드 정본 근거)
    for must in ["Doedre's Undoing", "Atziri's Allure", "Betrayal of Aldur", "Withered Wand"]:
        assert must in all_bases, must


def _run_build(tmp_path: Path, base_text: str):
    base = tmp_path / "base.filter"
    base.write_text(base_text, encoding="utf-8")
    out = tmp_path / "out.filter"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--base", str(base), "--spec", str(SPEC), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return out.read_text(encoding="utf-8"), proc.stderr


def test_vocab_gate_drops_unknown_names(tmp_path, spec):
    # 베이스에 코어 이름 몇 개만 존재 → 나머지는 드랍되고, 드랍 경고가 남아야 한다
    base_text = 'Show\n\tBaseType "Doedre\'s Undoing" "Withered Wand" "Skill Gems"\n'
    out, stderr = _run_build(tmp_path, base_text)
    assert "Doedre's Undoing" in out
    assert "Betrayal of Aldur" not in out.split("# NeverSink")[0]
    assert "vocabulary gate dropped" in stderr


def test_overlay_is_show_only_and_blocks_end_with_blank_line(tmp_path, spec):
    names = " ".join(f'"{b}"' for r in spec["rules"] for b in r["base_types"])
    base_text = f'Show\n\tClass == "Skill Gems"\n\tBaseType {names}\n'
    out, _ = _run_build(tmp_path, base_text)
    overlay = out.split(base_text)[0]
    assert "Hide" not in overlay
    # 모든 오버레이 블록은 빈 줄로 종료되어야 한다 (POE 필터 블록 규칙)
    blocks = [b for b in overlay.split("\n\n") if b.strip().startswith(("#", "Show"))]
    assert len([b for b in blocks if "Show" in b]) == len(spec["rules"])
