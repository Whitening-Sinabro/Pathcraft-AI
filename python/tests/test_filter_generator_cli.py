# -*- coding: utf-8 -*-
"""filter_generator.py CLI 엔드투엔드 스모크.

argparse/sys.exit/파일 쓰기 전체 경로 회귀 커버리지.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent
FILTER_GEN = REPO / "filter_generator.py"


def run_cli(*args: str, check: bool = False):
    """filter_generator.py CLI 실행. stdout/stderr/returncode 반환.

    Windows 기본 콘솔 인코딩(cp949)과 로그의 UTF-8 충돌을 피하기 위해
    PYTHONIOENCODING=utf-8 강제.
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(FILTER_GEN), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO),
        env=env,
        check=check,
    )


class TestContinueArch:
    def test_stdout_emits_beta_filter(self):
        result = run_cli("--arch", "continue")
        assert result.returncode == 0
        assert "[L1|catchall]" in result.stdout
        assert "[L2|normal]" in result.stdout
        assert "[L2|rare]" in result.stdout

    def test_write_to_file(self, tmp_path: Path):
        out = tmp_path / "beta.filter"
        result = run_cli("--arch", "continue", "--out", str(out))
        assert result.returncode == 0
        text = out.read_text(encoding="utf-8")
        assert "[L1|catchall]" in text
        assert "[L2|unique]" in text
        # 모든 L2 블록 Continue 포함
        assert text.count("\tContinue") >= 5

    def test_json_flag_rejected(self):
        """β continue + --json = 에러 (β-5에서 구현 예정)."""
        result = run_cli("--arch", "continue", "--json")
        assert result.returncode == 2
        assert "json" in result.stderr.lower()

    def test_strictness_applied(self):
        """--strictness 값이 실제 필터 출력에 반영됨."""
        r0 = run_cli("--arch", "continue", "--strictness", "0")
        r3 = run_cli("--arch", "continue", "--strictness", "3")
        assert r0.returncode == 0 and r3.returncode == 0
        # 엄격도 3에 L9 progressive hide 블록 있고, 0에는 없음
        assert "[L9|" not in r0.stdout
        assert "[L9|" in r3.stdout

    def test_strictness_out_of_range(self):
        result = run_cli("--arch", "continue", "--strictness", "99")
        assert result.returncode == 2

    def test_build_json_stdin_injects_l7(self):
        """β continue + stdin build_json → L7 BUILD_TARGET 블록 생성."""
        build_json = '{"meta":{"build_name":"T"},"items":[{"rarity":"unique","name":"Tabula Rasa"}]}'
        result = subprocess.run(
            [sys.executable, str(FILTER_GEN), "-", "--arch", "continue"],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(REPO), input=build_json,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        assert result.returncode == 0
        assert "[L7|unique]" in result.stdout
        assert "[L10|chanceable]" in result.stdout


class TestAuroraArch:
    def test_missing_build_json_errors(self):
        """aurora는 build_json 필수."""
        result = run_cli("--arch", "aurora")
        assert result.returncode == 2
        assert "build_json" in result.stderr.lower() or "aurora" in result.stderr.lower()

    def test_default_arch_is_aurora(self):
        """--arch 생략 시 aurora가 기본값이므로 build_json 필수 에러."""
        result = run_cli()
        assert result.returncode == 2


class TestHelp:
    def test_help_mentions_arch(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "--arch" in result.stdout
        assert "aurora" in result.stdout
        assert "continue" in result.stdout
