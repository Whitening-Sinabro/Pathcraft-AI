# -*- coding: utf-8 -*-
"""poe.ninja build/profile API policy regression tests."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

import poe_ninja_build_scraper  # noqa: E402
import poe_ninja_fetcher  # noqa: E402


def test_fetch_build_overview_does_not_call_internal_poe_ninja_api():
    with patch("poe_ninja_fetcher.requests.get") as mock_get:
        result = poe_ninja_fetcher.fetch_build_overview("Mirage")

    assert result is None
    assert poe_ninja_fetcher.POE_NINJA_BUILD_API_POLICY == "disabled_internal_unsupported"
    mock_get.assert_not_called()


def test_legacy_build_scraper_does_not_call_internal_poe_ninja_api():
    with patch("poe_ninja_build_scraper.requests.get") as mock_get:
        result = poe_ninja_build_scraper.fetch_poe_ninja_builds(
            league="Mirage",
            skill="Lightning Arrow",
            class_name="Deadeye",
            limit=5,
        )

    assert result == []
    assert poe_ninja_build_scraper.POE_NINJA_BUILD_API_POLICY == "disabled_internal_unsupported"
    mock_get.assert_not_called()

