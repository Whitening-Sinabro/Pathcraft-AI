# -*- coding: utf-8 -*-
"""pathcraft_palette Aurora Glow 단위 테스트."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathcraft_palette import (
    get_color, get_bg_color, get_border_color,
    get_currency_tiers, generate_tier_gradient, generate_theme_palette,
    CATEGORY_COLORS, CATEGORY_SHAPES, CATEGORY_BG_TINTS,
    CURRENCY_TIER_COLORS, TIER_COLORS_BY_CATEGORY, TIER_BG_ALPHA,
    VALID_MODES, DEFAULT_MODE, KEYSTONE_BG, FONT_SIZES,
    _parse_rgb_string, _brighten_color, _make_dark_tint,
)


class TestGetColor:
    """get_color: 카테고리 + 티어 조합으로 텍스트 색 반환."""

    def test_currency_tier_returns_tier_color(self):
        assert get_color("currency", "P1_KEYSTONE") == "255 64 120"
        assert get_color("currency", "P6_LOW") == "170 70 75"

    def test_unique_tier_returns_tier_color(self):
        assert get_color("unique", "P1_KEYSTONE") == "255 150 50"

    def test_without_tier_returns_base_color(self):
        assert get_color("currency") == CATEGORY_COLORS["currency"]

    def test_unknown_category_falls_back(self):
        assert get_color("nonexistent") == CATEGORY_COLORS["unique"]

    def test_unknown_tier_falls_back_to_base_color(self):
        assert get_color("currency", "INVALID_TIER") == CATEGORY_COLORS["currency"]


class TestAuroraGlowBackground:
    """Aurora Glow: Dark Tint 배경 시스템."""

    def test_all_categories_have_bg_tint(self):
        for cat in CATEGORY_COLORS:
            assert cat in CATEGORY_BG_TINTS, f"{cat} 배경 틴트 없음"

    def test_bg_tint_is_darker_than_seed(self):
        """배경 틴트의 RGB 합계는 시드 색보다 훨씬 작아야 함."""
        for cat, seed in CATEGORY_COLORS.items():
            seed_sum = sum(_parse_rgb_string(seed))
            tint_sum = sum(_parse_rgb_string(CATEGORY_BG_TINTS[cat]))
            assert tint_sum < seed_sum * 0.7, (
                f"{cat}: tint({tint_sum}) 이 seed({seed_sum})의 70% 이상"
            )

    def test_get_bg_color_includes_alpha(self):
        bg = get_bg_color("currency", "P1_KEYSTONE")
        parts = bg.split()
        assert len(parts) == 4, f"RGBA 4개 값 필요: {bg}"
        assert int(parts[3]) == TIER_BG_ALPHA["P1_KEYSTONE"]

    def test_higher_tier_has_higher_alpha(self):
        bg_p1 = get_bg_color("currency", "P1_KEYSTONE")
        bg_p6 = get_bg_color("currency", "P6_LOW")
        alpha_p1 = int(bg_p1.split()[3])
        alpha_p6 = int(bg_p6.split()[3])
        assert alpha_p1 > alpha_p6, "P1 alpha가 P6보다 높아야 함 (더 강한 glow)"

    def test_unknown_tier_uses_fallback_alpha(self):
        bg = get_bg_color("currency", "INVALID")
        parts = bg.split()
        assert int(parts[3]) == 170  # fallback alpha


class TestAuroraGlowBorder:
    """Aurora Glow: Edge Glow 보더 시스템."""

    def test_border_is_brighter_than_text(self):
        """보더 RGB 합계가 텍스트보다 커야 함 (Edge Glow)."""
        for cat in ("currency", "unique", "divcard", "gem", "base"):
            text = get_color(cat, "P2_CORE")
            border = get_border_color(cat, "P2_CORE")
            text_sum = sum(_parse_rgb_string(text))
            border_sum = sum(_parse_rgb_string(border))
            assert border_sum > text_sum, (
                f"{cat}: border({border_sum}) <= text({text_sum})"
            )

    def test_border_differs_from_text(self):
        """보더 ≠ 텍스트 (NeverSink 스타일 탈피)."""
        text = get_color("currency", "P1_KEYSTONE")
        border = get_border_color("currency", "P1_KEYSTONE")
        assert text != border


class TestBrightenAndDarken:
    """_brighten_color, _make_dark_tint 유틸리티."""

    def test_brighten_increases_lightness(self):
        original = "100 50 50"
        brighter = _brighten_color(original)
        assert sum(_parse_rgb_string(brighter)) > sum(_parse_rgb_string(original))

    def test_darken_creates_very_dark_color(self):
        dark = _make_dark_tint("255 64 120")
        r, g, b = _parse_rgb_string(dark)
        assert r + g + b < 300, f"dark tint가 너무 밝음: {dark}"

    def test_brighten_respects_cap(self):
        """이미 밝은 색을 brighten 해도 255를 넘지 않음."""
        very_bright = "250 250 250"
        result = _brighten_color(very_bright)
        r, g, b = _parse_rgb_string(result)
        assert r <= 255 and g <= 255 and b <= 255


class TestCategoryShapes:
    """PathcraftAI 독자 아이콘 shape."""

    def test_shapes_differ_from_neversink(self):
        """NeverSink 기본 매핑과 달라야 함."""
        neversink_shapes = {
            "currency": "Circle",
            "divcard":  "Triangle",
            "gem":      "Triangle",
            "base":     "Diamond",
        }
        for cat, ns_shape in neversink_shapes.items():
            assert CATEGORY_SHAPES[cat] != ns_shape, (
                f"{cat}: PathcraftAI shape이 NeverSink와 동일 ({ns_shape})"
            )

    def test_all_categories_have_shapes(self):
        for cat in CATEGORY_COLORS:
            assert cat in CATEGORY_SHAPES

    def test_unique_uses_star(self):
        assert CATEGORY_SHAPES["unique"] == "Star"


class TestGetCurrencyTiers:
    """모드별 Currency tier 매핑."""

    def test_returns_trade_tiers(self):
        tiers = get_currency_tiers("trade")
        assert "Mirror of Kalandra" in tiers["P1_KEYSTONE"]

    def test_returns_ssf_tiers_prioritizes_crafting(self):
        tiers = get_currency_tiers("ssf")
        assert "Orb of Alchemy" in tiers["P1_KEYSTONE"]
        assert "Chaos Orb" in tiers["P1_KEYSTONE"]
        assert "Orb of Fusing" in tiers["P1_KEYSTONE"]

    def test_returns_hcssf_tiers_prioritizes_safety(self):
        tiers = get_currency_tiers("hcssf")
        assert "Orb of Scouring" in tiers["P1_KEYSTONE"]
        assert "Orb of Annulment" in tiers["P1_KEYSTONE"]

    def test_trade_vs_ssf_differ_on_chaos_orb(self):
        trade = get_currency_tiers("trade")
        ssf = get_currency_tiers("ssf")
        assert "Chaos Orb" not in trade["P1_KEYSTONE"]
        assert "Chaos Orb" in ssf["P1_KEYSTONE"]

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError, match="알 수 없는 모드"):
            get_currency_tiers("pvp")

    def test_all_valid_modes_supported(self):
        for mode in VALID_MODES:
            tiers = get_currency_tiers(mode)
            assert "P1_KEYSTONE" in tiers
            assert len(tiers["P1_KEYSTONE"]) > 0


class TestGenerateTierGradient:
    """시드 RGB → 티어 그라데이션 생성."""

    def test_p1_equals_seed(self):
        gradient = generate_tier_gradient("255 64 120")
        assert gradient["P1_KEYSTONE"] == "255 64 120"

    def test_returns_all_p_tiers(self):
        gradient = generate_tier_gradient("128 0 255")
        expected_tiers = {"P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
                          "P4_SUPPORT", "P5_MINOR", "P6_LOW"}
        assert set(gradient.keys()) == expected_tiers

    def test_tuple_seed_also_works(self):
        gradient = generate_tier_gradient((128, 0, 255))
        assert gradient["P1_KEYSTONE"] == "128 0 255"

    def test_lower_tiers_are_darker(self):
        gradient = generate_tier_gradient("200 100 200")
        p1_sum = sum(int(x) for x in gradient["P1_KEYSTONE"].split())
        p6_sum = sum(int(x) for x in gradient["P6_LOW"].split())
        assert p6_sum < p1_sum

    def test_custom_n_tiers(self):
        gradient = generate_tier_gradient("100 100 100", n_tiers=3)
        assert len(gradient) == 3


class TestGenerateThemePalette:
    """여러 카테고리 시드 → 전체 팔레트."""

    def test_single_category(self):
        palette = generate_theme_palette({"currency": "128 0 255"})
        assert palette["currency"]["P1_KEYSTONE"] == "128 0 255"
        assert "P6_LOW" in palette["currency"]

    def test_multiple_categories(self):
        seeds = {
            "currency": "128 0 255",
            "unique":   "255 100 0",
            "gem":      "0 255 128",
        }
        palette = generate_theme_palette(seeds)
        assert len(palette) == 3
        assert palette["currency"]["P1_KEYSTONE"] == "128 0 255"
        assert palette["unique"]["P1_KEYSTONE"] == "255 100 0"
        assert palette["gem"]["P1_KEYSTONE"] == "0 255 128"


class TestPaletteIntegrity:
    """카테고리/팔레트 구조 불변 검증."""

    def test_all_categories_have_tier_colors(self):
        for cat in ("currency", "unique", "divcard", "gem", "base", "jewel", "fragment"):
            assert cat in TIER_COLORS_BY_CATEGORY

    def test_all_tier_dicts_have_six_tiers(self):
        expected = {"P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
                    "P4_SUPPORT", "P5_MINOR", "P6_LOW"}
        for cat, tiers in TIER_COLORS_BY_CATEGORY.items():
            assert set(tiers.keys()) == expected, f"{cat} 티어 불일치"

    def test_default_mode_is_ssf(self):
        assert DEFAULT_MODE == "ssf"

    def test_all_tier_bg_alphas_defined(self):
        expected = {"P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
                    "P4_SUPPORT", "P5_MINOR", "P6_LOW"}
        assert set(TIER_BG_ALPHA.keys()) == expected
