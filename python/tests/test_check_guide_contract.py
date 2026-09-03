"""가이드 구조 계약 체커의 판정 로직 테스트.

이 체커는 게이트다. 오탐이 섞이면 진짜 결함 경고까지 같이 무시하게 되고,
누락 판정이 틀리면 장이 빠진 문서가 그대로 구글 닥으로 나간다. 그래서
"무엇을 결함으로 볼 것인가"의 경계만 골라 고정한다.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_guide_contract.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("check_guide_contract", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["check_guide_contract"] = m
    spec.loader.exec_module(m)
    return m


def band(title: str) -> str:
    return f'<table><tr><td style="background:#7c3aed;padding:4px"><b>{title}</b></td></tr></table>'


ROW3 = "<table><tr><th>항목</th><th>내용</th><th>근거</th></tr>" \
       "<tr><td>가</td><td>나</td><td>다</td></tr></table>"


class TestBareTimestamp:
    """평문 타임스탬프 = 독자가 영상을 손으로 뒤져야 하는 근거."""

    def test_plain_video_timestamp_is_flagged(self, mod):
        assert mod.stats("<p>2.0 가이드 3:22 참고</p>")["bare_ts"] == 1

    def test_league_start_clock_time_is_not_a_citation(self, mod):
        # 리그 개막 시각이지 영상 인용점이 아니다. 오탐으로 잡으면 안 된다.
        assert mod.stats("<p>9월 5일 05:00 KST에 시작한다</p>")["bare_ts"] == 0

    @pytest.mark.parametrize("zone", ["KST", "UTC", "GMT", "AM", "PM"])
    def test_other_clock_suffixes_are_also_exempt(self, mod, zone):
        assert mod.stats(f"<p>10:30 {zone}</p>")["bare_ts"] == 0

    def test_timestamp_inside_a_deeplink_is_not_counted(self, mod):
        text = '<p><a href="https://youtu.be/abc?t=202">2.0 가이드 3:22</a></p>'
        got = mod.stats(text)
        assert got["bare_ts"] == 0
        assert got["deeplinks"] == 1


class TestRequiredBands:
    """본 가이드는 제0~8장을 다 갖춰야 하고, 보조 문서는 그렇지 않다."""

    def test_full_guide_missing_chapters_fails(self, mod, tmp_path):
        p = tmp_path / "X_GUIDE_DOC.html"
        p.write_text(band("제0장 — 결론") + ROW3 + band("출처") + ROW3, encoding="utf-8")
        assert any("템플릿 필수 장 누락" in x for x in mod.check(p, None))

    def test_supplement_needs_only_a_sources_chapter(self, mod, tmp_path):
        p = tmp_path / "X_HARDCORE_GUIDE_DOC.html"
        p.write_text(band("제0장 — 결론") + ROW3 + band("출처") + ROW3, encoding="utf-8")
        assert mod.check(p, None) == []

    def test_supplement_without_sources_fails(self, mod, tmp_path):
        p = tmp_path / "X_HARDCORE_GUIDE_DOC.html"
        p.write_text(band("제0장 — 결론") + ROW3, encoding="utf-8")
        assert any("출처" in x for x in mod.check(p, None))


class TestStructuralLoss:
    """생성기가 문서를 어떻게 자르는지에 걸린 것들."""

    def test_duplicate_image_markers_are_rejected(self, mod, tmp_path):
        p = tmp_path / "X_HARDCORE_GUIDE_DOC.html"
        p.write_text(band("제0장") + ROW3 + band("출처") + ROW3
                     + "<p>@@IMG:a@@</p><p>@@IMG:a@@</p>", encoding="utf-8")
        assert any("이미지 마커 중복" in x for x in mod.check(p, None))

    def test_tables_without_a_three_column_row_are_rejected(self, mod, tmp_path):
        p = tmp_path / "X_HARDCORE_GUIDE_DOC.html"
        p.write_text(band("제0장") + "<table><tr><td>가</td><td>나</td></tr></table>"
                     + band("출처") + ROW3.replace("<td>다</td>", ""), encoding="utf-8")
        assert any("3열 근거 행이 0" in x for x in mod.check(p, None))
