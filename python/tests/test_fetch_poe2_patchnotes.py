"""`scripts/fetch_poe2_patchnotes.py` — 포럼 인덱스 파싱 + 첫 게시물 추출.

두 함정을 고정한다 (둘 다 2026-09-05 실제로 밟았다):
1. 뉴스형 콘텐츠 업데이트 스레드는 `td[colspan=2]` 가 본문이고 `forumPostListTable`
   첫 행은 **댓글**이다. 첫 행만 보면 0.5.0 패치노트가 "massive patch" 한 줄이 된다.
2. 인덱스 페이지마다 낮은 id 의 고정 공지가 끼어 있어 "낮은 id 존재 = 끝" 으로 끊으면
   1페이지에서 멈춘다.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "fetch_poe2_patchnotes.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fetch_poe2_patchnotes", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load_module()

NEWS_LAYOUT = """
<html><body>
<table><tr><td colspan="2"><div class="content"><h1>Content Update 0.5.0</h1>
<p>Table of Contents</p><ul><li>Skill Changes</li></ul>
<p>Corrupting Cry I, Corrupting Cry II: No longer causes the supported skill to inflict Corrupted Blood.</p>
</div></td></tr></table>
<table class="forumPostListTable">
<tr class="staff"><td class="content-container"><div class="contentStart"></div><div class="content">massive patch</div></td></tr>
<tr><td class="content-container"><div class="content">Huge GGG W</div></td></tr>
</table>
</body></html>
"""

HOTFIX_LAYOUT = """
<html><body>
<table class="forumPostListTable">
<tr class="staff"><td class="content-container"><div class="contentStart"></div>
<div class="content"><h3>0.5.5 Hotfix</h3><br><ul><li>Fixed a client crash.</li></ul><br>This patch has been deployed without restarting the servers.</div></td></tr>
<tr><td class="content-container"><div class="content">Buffer underflow in every hideout it seems.</div></td></tr>
</table>
</body></html>
"""

INDEX_PAGE = """
<html><body><table>
<tr><td><div class="title"><a href="/forum/view-thread/1000">Sticky: Read this first</a></div></td><td>Jan 1, 2025</td></tr>
<tr><td><div class="title"><a href="/forum/view-thread/4001365">0.5.5 Hotfix 5</a></div></td><td><span class="post_date">Sep 5, 2026, 11:57:16 AM</span></td></tr>
<tr><td><div class="title"><a href="/forum/view-thread/4000864">0.5.5 Patch Notes</a></div></td><td>Sep 3, 2026</td></tr>
<tr><td><a href="/forum/view-thread/4000864/page/2">2</a></td><td></td></tr>
</table></body></html>
"""


def test_news_layout_prefers_colspan_body_over_first_comment():
    text = mod.first_post_text(NEWS_LAYOUT)
    assert "Corrupting Cry I, Corrupting Cry II" in text
    assert "massive patch" not in text


def test_hotfix_layout_uses_first_post_only():
    text = mod.first_post_text(HOTFIX_LAYOUT)
    assert "Fixed a client crash." in text
    assert "Buffer underflow" not in text
    assert "0.5.5 Hotfix" in text.splitlines()[0]


def test_missing_container_raises():
    try:
        mod.first_post_text("<html><body><p>nothing</p></body></html>")
    except RuntimeError as exc:
        assert "container" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_parse_index_dedupes_and_keeps_sticky_rows_visible():
    rows = mod.parse_index(INDEX_PAGE)
    ids = [r["id"] for r in rows]
    assert ids == [1000, 4001365, 4000864], ids
    by_id = {r["id"]: r for r in rows}
    assert by_id[4001365]["title"] == "0.5.5 Hotfix 5"
    assert by_id[4001365]["date"] == "Sep 5, 2026"
    # 고정 공지(낮은 id)가 같은 페이지에 있다 — 호출 측은 이걸로 페이지 순회를 끊으면 안 된다
    assert min(ids) < 3883495 and max(ids) > 3883495


def test_slugify_is_filename_safe():
    slug = mod.slugify("Content Update 0.5.0 — Path of Exile 2: Return of the Ancients")
    assert slug.startswith("Content_Update_0.5.0")
    assert "/" not in slug and ":" not in slug and len(slug) <= 60
