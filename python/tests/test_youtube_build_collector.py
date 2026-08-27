# -*- coding: utf-8 -*-
"""YouTube description PoB-link extraction regression checks."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pob_link_collector import extract_pob_links as extract_reddit_pob_links  # noqa: E402
from youtube_build_collector import extract_pob_links as extract_youtube_pob_links  # noqa: E402


def test_extract_pob_links_includes_poedb_share_urls():
    description = """
    Part 1: https://poedb.tw/pob/GXoW7hsWd6
    Part 2: https://poedb.tw/us/pob/gcNfqrGAAe
    """

    assert extract_youtube_pob_links(description) == [
        "https://poedb.tw/pob/GXoW7hsWd6",
        "https://poedb.tw/us/pob/gcNfqrGAAe",
    ]


def test_reddit_collector_normalizes_poedb_share_urls():
    text = """
    https://poedb.tw/pob/GXoW7hsWd6
    https://poedb.tw/us/pob/gcNfqrGAAe
    """

    assert set(extract_reddit_pob_links(text)) == {
        "https://poedb.tw/pob/GXoW7hsWd6",
        "https://poedb.tw/pob/gcNfqrGAAe",
    }
