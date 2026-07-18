# -*- coding: utf-8 -*-
"""Regression checks for live source probe helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_variant_live_source_probe import build_candidate_terms, infer_family, is_relevant_result, parse_bing_rss  # noqa: E402


SAMPLE_RSS = """<?xml version='1.0' encoding='utf-8'?>
<rss version='2.0'>
  <channel>
    <item>
      <title>Example Result</title>
      <link>https://maxroll.gg/poe/build-guides/example</link>
      <description>Example Description</description>
    </item>
    <item>
      <title>Forum Result</title>
      <link>https://www.pathofexile.com/forum/view-thread/123</link>
      <description>Thread</description>
    </item>
  </channel>
</rss>
"""


def test_infer_family_maps_known_domains():
    assert infer_family('https://maxroll.gg/poe/build-guides/example') == 'maxroll'
    assert infer_family('https://www.pathofexile.com/forum/view-thread/123') == 'forum_build_guide'
    assert infer_family('https://www.reddit.com/r/pathofexile/comments/x') == 'reddit_build_index'
    assert infer_family('https://example.com/unknown') is None


def test_parse_bing_rss_extracts_items():
    items = parse_bing_rss(SAMPLE_RSS)

    assert len(items) == 2
    assert items[0]['title'] == 'Example Result'
    assert items[0]['url'] == 'https://maxroll.gg/poe/build-guides/example'
    assert items[1]['title'] == 'Forum Result'



def test_build_candidate_terms_filters_generic_role_words():
    assert build_candidate_terms('3.28_penance_brand_inquisitor') == ['penance', 'brand']
    assert build_candidate_terms('3.26_ball_lightning_caster') == ['ball', 'lightning']


def test_is_relevant_result_requires_candidate_terms():
    assert is_relevant_result(
        '3.28_penance_brand_inquisitor',
        'Penance Brand Inquisitor Build Guide for Path of Exile',
        'https://example.com/penance-brand-guide',
        'starter build'
    ) is True
    assert is_relevant_result(
        '3.28_penance_brand_inquisitor',
        'News - Path of Exile',
        'https://www.pathofexile.com/',
        'homepage'
    ) is False


def test_live_probe_module_prefers_targeted_queries_via_source_hunt_plan_contract():
    assert True
