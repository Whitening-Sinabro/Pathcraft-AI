"""HC Journey — 여정 뷰 렌더 검증."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hc_journey"))
import build_db  # noqa: E402
import render_journey as rj  # noqa: E402


def test_render_all_builds_has_journey_notes_and_trade_links():
    build_db.build()
    page = rj.render()
    for name in ("임성빈", "Skadoosh", "ds lily", "Fubgun"):
        assert name in page
    assert "규칙 · why" in page and "손 · cost" in page          # 두 층이 구분돼 보인다
    assert "T1 그대로 · 국제" in page and "T3 같은 부위 · 한국" in page
    assert "/trade2/search/poe2/HC%20Forbidden%20Rites?q=" in page
    assert "linear-gradient" not in page and "#" not in rj.CSS.replace("&#", "")  # 문서 스타일: 그라데이션·hex 없음
    assert "요구 ≤ 93" in page
    # 슬롯 규칙(무기 유형 함정)은 첫 전환에만 전문, 이후 전환에선 접힌 한 줄 — 같은 빌드 안에서 전문은 한 번
    one = rj.render([1])
    full = "석궁→지팡이 전환 때 급습 제거). 요구 레벨·힘·민첩과 함께"   # 따옴표는 HTML 이스케이프되므로 따옴표 없는 구간으로 센다
    assert one.count(full) == 1 and "앞서 본 규칙" in one


def test_render_split_writes_per_build_files_and_index(tmp_path):
    build_db.build()
    files = rj.render_split(tmp_path)
    names = sorted(p.name for p in files)
    assert names == sorted(["journey.html"] + [f"journey_{i}.html" for i in range(1, len(build_db.CREATORS) + 1)])
    index = (tmp_path / "journey.html").read_text(encoding="utf-8")
    assert "journey_1.html" in index and "임성빈" in index and "?q=" not in index   # 목차엔 무거운 링크가 없다
    one = (tmp_path / "journey_1.html").read_text(encoding="utf-8")
    assert "임성빈" in one and "Skadoosh" not in one and "T1 그대로 · 국제" in one


def test_render_single_build_and_live_freshness():
    build_db.build()
    page1 = rj.render([1])
    assert "임성빈" in page1 and "Skadoosh" not in page1
    now = datetime.now(timezone.utc)
    assert rj._fresh(now.isoformat(timespec="seconds"), now) is True
    assert rj._fresh((now - timedelta(hours=25)).isoformat(timespec="seconds"), now) is False
    assert rj._fresh(None, now) is False and rj._fresh("garbage", now) is False
