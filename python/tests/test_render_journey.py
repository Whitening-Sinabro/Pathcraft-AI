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


def test_render_single_build_and_live_freshness():
    build_db.build()
    page1 = rj.render([1])
    assert "임성빈" in page1 and "Skadoosh" not in page1
    now = datetime.now(timezone.utc)
    assert rj._fresh(now.isoformat(timespec="seconds"), now) is True
    assert rj._fresh((now - timedelta(hours=25)).isoformat(timespec="seconds"), now) is False
    assert rj._fresh(None, now) is False and rj._fresh("garbage", now) is False
