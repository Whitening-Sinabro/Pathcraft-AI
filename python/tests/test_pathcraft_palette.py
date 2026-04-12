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
from pathcraft_sections import (
    make_show_block, make_gold_block, make_restex_block, make_hide_block,
    make_currency_stack_block,
    generate_currency_stack_section, generate_leveling_currency_section,
    generate_lifeforce_section, generate_splinter_section,
    generate_links_sockets_section,
    _promote_tier, _find_currency_tier,
    CURRENCY_STACK_THRESHOLDS, SUPPLY_STACK_THRESHOLDS, SUPPLY_CURRENCIES,
    LIFEFORCE_BASES, SPLINTER_HIGH, SPLINTER_LOW,
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


class TestMakeShowBlock:
    """make_show_block: Aurora Glow Show 블록 생성."""

    def test_keystone_uses_royal_crimson_bg(self):
        out = make_show_block(
            "test keystone",
            ["Rarity Unique"],
            category="unique",
            tier="P1_KEYSTONE",
            keystone=True,
        )
        assert f"SetBackgroundColor {KEYSTONE_BG} 240" in out

    def test_keystone_border_is_bright(self):
        """Keystone 보더는 Royal Crimson보다 훨씬 밝아야 함."""
        out = make_show_block(
            "test keystone",
            ["Rarity Unique"],
            category="unique",
            tier="P1_KEYSTONE",
            keystone=True,
        )
        assert "SetBorderColor" in out
        for line in out.split("\n"):
            if "SetBorderColor" in line:
                parts = line.strip().split()
                r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
                ks_r, ks_g, ks_b = _parse_rgb_string(KEYSTONE_BG)
                assert r + g + b > ks_r + ks_g + ks_b, "Keystone border가 bg보다 밝아야 함"

    def test_non_keystone_uses_dark_tint_bg(self):
        out = make_show_block(
            "test normal",
            ["Rarity Unique"],
            category="unique",
            tier="P2_CORE",
        )
        # 투명(0 0 0 0)이 아닌 Dark Tint 배경
        assert "SetBackgroundColor 0 0 0 0" not in out
        assert "SetBackgroundColor" in out
        # alpha 값 존재 확인
        for line in out.split("\n"):
            if "SetBackgroundColor" in line:
                parts = line.strip().split()
                assert len(parts) == 5, f"RGBA 4개 값 필요: {line}"
                alpha = int(parts[4])
                assert alpha == TIER_BG_ALPHA["P2_CORE"]

    def test_border_differs_from_text_in_block(self):
        """생성된 블록에서 보더 색 ≠ 텍스트 색."""
        out = make_show_block(
            "test",
            ["Rarity Unique"],
            category="currency",
            tier="P1_KEYSTONE",
        )
        text_color = border_color = None
        for line in out.split("\n"):
            if "SetTextColor" in line:
                text_color = " ".join(line.strip().split()[1:])
            if "SetBorderColor" in line:
                border_color = " ".join(line.strip().split()[1:])
        assert text_color is not None
        assert border_color is not None
        assert text_color != border_color, "Aurora Glow: 보더 ≠ 텍스트"

    def test_build_target_adds_cyan_signature(self):
        out = make_show_block(
            "test",
            ["Rarity Unique"],
            category="unique",
            tier="P2_CORE",
            is_build_target=True,
        )
        assert "PlayEffect Cyan" in out
        assert "MinimapIcon" in out
        assert "Cyan" in out

    def test_gold_category_forces_no_cyan_vfx(self):
        out = make_show_block(
            "gold test",
            ['BaseType == "Gold"'],
            category="gold",
            tier="P1_KEYSTONE",
            is_build_target=True,
        )
        assert "PlayEffect Cyan" not in out
        assert "MinimapIcon" not in out

    def test_invalid_tier_falls_back_without_error(self):
        out = make_show_block(
            "bad tier",
            ["Rarity Unique"],
            category="unique",
            tier="INVALID_XXX",
        )
        assert f"SetFontSize {FONT_SIZES['P2_CORE']}" in out

    def test_font_size_p1_is_max(self):
        out = make_show_block("x", ["Rarity Unique"], "unique", "P1_KEYSTONE")
        assert "SetFontSize 45" in out

    def test_font_size_p6_is_small(self):
        out = make_show_block("x", ["Rarity Unique"], "unique", "P6_LOW")
        assert "SetFontSize 34" in out


class TestMakeGoldBlock:
    """make_gold_block: Gold StackSize 기반 블록 — Aurora Glow."""

    def test_no_border(self):
        """Gold는 보더 없음."""
        out = make_gold_block(5000, 45)
        assert "SetBorderColor" not in out

    def test_contains_stack_condition(self):
        out = make_gold_block(1000, 42)
        assert "StackSize >= 1000" in out

    def test_dark_tint_bg_not_transparent(self):
        """Aurora Glow: 투명 배경이 아닌 Dark Tint."""
        out = make_gold_block(100, 34)
        assert "SetBackgroundColor 0 0 0 0" not in out
        assert "SetBackgroundColor" in out

    def test_uses_lemonade_color(self):
        out = make_gold_block(500, 38)
        assert CATEGORY_COLORS["gold"] in out

    def test_no_cyan_signature(self):
        out = make_gold_block(5000, 45)
        assert "PlayEffect" not in out

    def test_uses_raindrop_icon(self):
        out = make_gold_block(5000, 45)
        assert "Raindrop" in out


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


class TestPromoteTier:
    """_promote_tier: 티어 승격 로직."""

    def test_promote_p5_by_2(self):
        assert _promote_tier("P5_MINOR", 2) == "P3_USEFUL"

    def test_promote_p6_by_3(self):
        assert _promote_tier("P6_LOW", 3) == "P3_USEFUL"

    def test_promote_caps_at_p1(self):
        assert _promote_tier("P2_CORE", 5) == "P1_KEYSTONE"

    def test_promote_zero_no_change(self):
        assert _promote_tier("P4_SUPPORT", 0) == "P4_SUPPORT"

    def test_invalid_tier_returns_as_is(self):
        assert _promote_tier("INVALID", 2) == "INVALID"


class TestFindCurrencyTier:
    """_find_currency_tier: 커런시 이름 → 기본 티어 조회."""

    def test_wisdom_scroll_is_p6_in_ssf(self):
        assert _find_currency_tier("Scroll of Wisdom", "ssf") == "P6_LOW"

    def test_chaos_orb_is_p1_in_ssf(self):
        assert _find_currency_tier("Chaos Orb", "ssf") == "P1_KEYSTONE"

    def test_chaos_orb_is_p3_in_trade(self):
        assert _find_currency_tier("Chaos Orb", "trade") == "P3_USEFUL"

    def test_unknown_currency_falls_back_to_p6(self):
        assert _find_currency_tier("Nonexistent Orb", "ssf") == "P6_LOW"


class TestCurrencyStackBlock:
    """make_currency_stack_block: 스택 기반 커런시 Show 블록."""

    def test_contains_stacksize_condition(self):
        out = make_currency_stack_block(
            ["Chaos Orb"], "P3_USEFUL", min_stack=6, promotion=2,
        )
        assert "StackSize >= 6" in out

    def test_uses_promoted_tier_color(self):
        """P3 + 2승격 → P1 색을 사용해야 함."""
        out = make_currency_stack_block(
            ["Chaos Orb"], "P3_USEFUL", min_stack=6, promotion=2,
        )
        p1_color = get_color("currency", "P1_KEYSTONE")
        assert f"SetTextColor {p1_color} 255" in out

    def test_no_cyan_vfx(self):
        """스택 커런시는 빌드 타겟이 아님 — Cyan VFX 없음."""
        out = make_currency_stack_block(
            ["Exalted Orb"], "P2_CORE", min_stack=3, promotion=1,
        )
        assert "PlayEffect Cyan" not in out

    def test_multiple_currencies_in_one_block(self):
        out = make_currency_stack_block(
            ["Chaos Orb", "Vaal Orb"], "P3_USEFUL", min_stack=3, promotion=1,
        )
        assert '"Chaos Orb"' in out
        assert '"Vaal Orb"' in out


class TestGenerateCurrencyStackSection:
    """generate_currency_stack_section: 전체 스택 섹션 생성."""

    def test_section_header_contains_mode(self):
        section = generate_currency_stack_section("ssf")
        assert "SSF" in section

    def test_supply_currencies_present(self):
        section = generate_currency_stack_section("ssf")
        for name in SUPPLY_CURRENCIES:
            assert name in section, f"{name} 스택 룰 없음"

    def test_stack_thresholds_present(self):
        section = generate_currency_stack_section("ssf")
        assert "StackSize >= 10" in section
        assert "StackSize >= 6" in section
        assert "StackSize >= 5" in section
        assert "StackSize >= 3" in section

    def test_all_modes_generate_without_error(self):
        for mode in VALID_MODES:
            section = generate_currency_stack_section(mode)
            assert len(section) > 100

    def test_high_stack_before_low_stack(self):
        """높은 스택 임계값이 낮은 것보다 먼저 나와야 함 (top-down)."""
        section = generate_currency_stack_section("ssf")
        pos_10 = section.index("StackSize >= 10")
        pos_5 = section.index("StackSize >= 5")
        pos_3 = section.index("StackSize >= 3")
        assert pos_10 < pos_5 < pos_3


class TestRestExBlock:
    """make_restex_block: 미분류 아이템 안전망."""

    def test_uses_pink_colors(self):
        out = make_restex_block("test", ['Class "Currency"'])
        assert "255 0 255" in out
        assert "100 0 100" in out

    def test_has_sound_and_effect(self):
        out = make_restex_block("test", ['Class "Maps"'])
        assert "PlayAlertSound 3 300" in out
        assert "PlayEffect Pink" in out
        assert "MinimapIcon 0 Pink Circle" in out

    def test_font_45(self):
        out = make_restex_block("test", [])
        assert "SetFontSize 45" in out


class TestHideBlock:
    """make_hide_block: Hide 블록."""

    def test_uses_hide_keyword(self):
        out = make_hide_block("test", ['Class "Gems"'])
        assert out.startswith("Hide #")

    def test_disables_drop_sound(self):
        out = make_hide_block("test", [])
        assert "DisableDropSound True" in out

    def test_font_18(self):
        out = make_hide_block("test", [])
        assert "SetFontSize 18" in out


class TestLevelingCurrencySection:
    """generate_leveling_currency_section: 레벨링 커런시."""

    def test_contains_arealevel_condition(self):
        section = generate_leveling_currency_section()
        assert "AreaLevel <= 67" in section

    def test_contains_binding_and_chance(self):
        section = generate_leveling_currency_section()
        assert "Orb of Binding" in section
        assert "Orb of Chance" in section

    def test_contains_scrolls(self):
        section = generate_leveling_currency_section()
        assert "Portal Scroll" in section
        assert "Scroll of Wisdom" in section


class TestLifeforceSection:
    """generate_lifeforce_section: Lifeforce 스택."""

    def test_contains_all_lifeforce_types(self):
        section = generate_lifeforce_section()
        for name in LIFEFORCE_BASES:
            assert name in section

    def test_stack_thresholds_present(self):
        section = generate_lifeforce_section()
        assert "StackSize >= 4000" in section
        assert "StackSize >= 500" in section
        assert "StackSize >= 250" in section
        assert "StackSize >= 45" in section
        assert "StackSize >= 20" in section

    def test_has_fallback(self):
        section = generate_lifeforce_section()
        assert "fallback" in section


class TestSplinterSection:
    """generate_splinter_section: 스플린터 스택."""

    def test_contains_breach_splinters(self):
        section = generate_splinter_section()
        for name in SPLINTER_HIGH:
            assert name in section

    def test_contains_legion_splinters(self):
        section = generate_splinter_section()
        for name in SPLINTER_LOW:
            assert name in section

    def test_contains_simulacrum(self):
        section = generate_splinter_section()
        assert "Simulacrum Splinter" in section
        assert "StackSize >= 150" in section

    def test_has_single_fallbacks(self):
        section = generate_splinter_section()
        assert section.count("single") == 3  # Breach, Legion, Simulacrum


class TestLinksSocketsSection:
    """generate_links_sockets_section: 6링크/5링크/6소켓."""

    def test_contains_6link_blocks(self):
        section = generate_links_sockets_section()
        assert "LinkedSockets 6" in section
        assert "6-Link High Base" in section
        assert "6-Link any" in section

    def test_contains_5link_blocks(self):
        section = generate_links_sockets_section()
        assert "LinkedSockets >= 5" in section
        assert "5-Link Leveling" in section
        assert "5-Link Endgame" in section

    def test_contains_6socket_blocks(self):
        section = generate_links_sockets_section()
        assert "6-Socket Height 4" in section
        assert "6-Socket Height 3" in section

    def test_contains_white_socket(self):
        section = generate_links_sockets_section()
        assert "6WWWWWW" in section

    def test_6link_high_uses_keystone(self):
        section = generate_links_sockets_section()
        assert KEYSTONE_BG in section

    def test_leveling_has_arealevel(self):
        section = generate_links_sockets_section()
        assert "AreaLevel <= 67" in section
        assert "AreaLevel >= 68" in section
