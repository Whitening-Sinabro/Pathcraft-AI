# -*- coding: utf-8 -*-
"""Regression checks for external build source URL resolver."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_source_resolver import resolve_from_html, resolve_source  # noqa: E402


def test_resolve_direct_pobb_source():
    result = resolve_source("https://pobb.in/AbCdEf")

    assert result["source_type"] == "pobb"
    assert result["pob_url"] == "https://pobb.in/AbCdEf"
    assert result["passive_tree_url"] is None


def test_resolve_direct_passive_tree_source():
    url = "https://www.pathofexile.com/passive-skill-tree/AAAA_BBBB"
    result = resolve_source(url)

    assert result["source_type"] == "passive_tree"
    assert result["pob_url"] is None
    assert result["passive_tree_url"] == url


def test_extracts_pobb_and_passive_urls_from_generic_html():
    html = """
    <html>
      <head>
        <title>Example Build</title>
        <link rel="canonical" href="https://example.com/build" />
      </head>
      <body>
        <a href="https://pobb.in/TestBuild42">PoB</a>
        <script>
          const tree = "https://www.pathofexile.com/passive-skill-tree/ABC_DEF";
        </script>
      </body>
    </html>
    """
    result = resolve_from_html("https://example.com/build", html)

    assert result["canonical_url"] == "https://example.com/build"
    assert result["pob_url"] == "https://pobb.in/TestBuild42"
    assert result["passive_tree_url"] == "https://www.pathofexile.com/passive-skill-tree/ABC_DEF"


def test_generic_html_fetch_falls_back_after_proxy_error():
    success = MagicMock()
    success.raise_for_status = MagicMock()
    success.text = '<html><body><a href="https://pobb.in/TestBuild42">PoB</a></body></html>'
    session = MagicMock()
    session.get.return_value = success

    with patch("build_source_resolver.requests.get", side_effect=requests.exceptions.ProxyError("proxy")) as mock_get:
        with patch("build_source_resolver.requests.Session", return_value=session) as mock_session:
            result = resolve_source("https://example.com/build")

    assert result["pob_url"] == "https://pobb.in/TestBuild42"
    assert mock_get.call_count == 1
    assert mock_session.call_count == 1
    session.get.assert_called_once()
    assert session.trust_env is False


def test_maxroll_generic_tool_links_do_not_count_as_build_specific_resolution():
    html = """
    <html>
      <head><title>Maxroll Build</title></head>
      <body>
        <a href="/poe/planner">PoEPlanner</a>
        <a href="/poe/pob">PoB Import / Export</a>
      </body>
    </html>
    """
    result = resolve_from_html("https://maxroll.gg/poe/build-guides/example", html)

    assert result["source_type"] == "maxroll"
    assert result["pob_url"] is None
    assert result["passive_tree_url"] is None
    assert any("did not expose" in warning for warning in result["warnings"])


def test_maxroll_specific_tool_url_is_retained_as_metadata():
    html = """
    <html>
      <body>
        <a href="/poe/planner/abc123">Planner</a>
      </body>
    </html>
    """
    result = resolve_from_html("https://maxroll.gg/poe/build-guides/example", html)

    assert result["maxroll_tool_url"] == "https://maxroll.gg/poe/planner/abc123"


def test_maxroll_pob_page_resolves_to_profile_endpoint():
    result = resolve_source("https://maxroll.gg/poe/pob/lz4pi0lj")

    assert result["source_type"] == "maxroll_pob_page"
    assert result["pob_url"] == "https://planners.maxroll.gg/profiles/load/poe/lz4pi0lj"
    assert result["maxroll_tool_url"] == "https://maxroll.gg/poe/pob/lz4pi0lj"
    assert any("resolved to its planner profile endpoint" in warning for warning in result["warnings"])


def test_maxroll_planner_page_resolves_to_profile_endpoint():
    result = resolve_source("https://maxroll.gg/poe/planner/lz4pi0lj")

    assert result["source_type"] == "maxroll_planner_page"
    assert result["pob_url"] == "https://planners.maxroll.gg/profiles/load/poe/lz4pi0lj"
    assert result["maxroll_tool_url"] == "https://maxroll.gg/poe/planner/lz4pi0lj"


def test_direct_maxroll_profile_api_is_treated_as_pob_source():
    result = resolve_source("https://planners.maxroll.gg/profiles/load/poe/lz4pi0lj")

    assert result["source_type"] == "maxroll_profile_api"
    assert result["pob_url"] == "https://planners.maxroll.gg/profiles/load/poe/lz4pi0lj"
    assert result["warnings"] == []


def test_poe_ninja_pob_page_resolves_to_raw_export_endpoint():
    result = resolve_source("https://poe.ninja/poe1/pob/8c8b9")

    assert result["source_type"] == "poe_ninja_pob_page"
    assert result["pob_url"] == "https://poe.ninja/poe1/pob/raw/8c8b9"
    assert any("resolved to its raw Path of Building export endpoint" in warning for warning in result["warnings"])


def test_direct_poe_ninja_raw_endpoint_is_treated_as_pob_source():
    result = resolve_source("https://poe.ninja/poe1/pob/raw/8c8b9")

    assert result["source_type"] == "poe_ninja_pob_raw"
    assert result["pob_url"] == "https://poe.ninja/poe1/pob/raw/8c8b9"


def test_poedb_build_page_resolves_to_raw_export_endpoint():
    result = resolve_source("https://poedb.tw/us/pob/gcNfqrGAAe")

    assert result["source_type"] == "poedb_pob_page"
    assert result["pob_url"] == "https://poedb.tw/pob/gcNfqrGAAe/raw"
    assert any("raw Path of Building" in warning for warning in result["warnings"])


def test_direct_poedb_raw_endpoint_is_treated_as_pob_source():
    result = resolve_source("https://poedb.tw/pob/GXoW7hsWd6/raw")

    assert result["source_type"] == "poedb_pob_raw"
    assert result["pob_url"] == "https://poedb.tw/pob/GXoW7hsWd6/raw"


def test_extracts_poedb_build_url_from_generic_html_as_raw_export():
    html = '<a href="https://poedb.tw/pob/GXoW7hsWd6">PoB</a>'

    result = resolve_from_html("https://example.com/build", html)

    assert result["pob_url"] == "https://poedb.tw/pob/GXoW7hsWd6/raw"
