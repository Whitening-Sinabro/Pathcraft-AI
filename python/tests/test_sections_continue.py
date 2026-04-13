# -*- coding: utf-8 -*-
"""sections_continue β Continue 빌더 유닛 테스트."""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sections_continue import (
    LayerStyle, make_layer_block,
    LAYER_T1_BORDER, LAYER_CATCH_ALL, LAYER_DEFAULT_RARITY, LAYER_NAMES,
    load_t1_bases, T1Bases, style_from_palette, _pad_alpha,
    layer_catch_all, layer_default_rarity, generate_beta_overlay,
    layer_socket_border, layer_corrupt_border, layer_t1_border,
    layer_hard_hide, layer_progressive_hide,
    load_progressive_hide, ProgressiveHideData,
    layer_currency, layer_maps, layer_divcards,
    load_category_data, CategoryData,
    layer_build_target, layer_re_show,
)


# ---------------------------------------------------------------------------
# Mock build_data 픽스처
# ---------------------------------------------------------------------------

TABULA_BUILD = {
    "meta": {"build_name": "Tabula Test", "class": "Templar"},
    "items": [
        {"rarity": "unique", "name": "Tabula Rasa"},
        {"rarity": "unique", "name": "Mageblood"},
    ],
    "progression_stages": [
        {
            "gem_setups": {
                "Cyclone": ["Melee Physical Damage Support", "Fortify Support"],
            },
            "gear_recommendation": {
                "weapon": {"name": "Rare Sword", "rarity": "rare",
                           "base_type": "Jewelled Foil"},
            },
        }
    ],
}


# ---------------------------------------------------------------------------
# _pad_alpha
# ---------------------------------------------------------------------------

class TestPadAlpha:
    def test_rgb_gets_alpha_255(self):
        assert _pad_alpha("255 100 50") == "255 100 50 255"

    def test_rgba_unchanged(self):
        assert _pad_alpha("255 100 50 200") == "255 100 50 200"

    def test_single_space_normalization_not_done(self):
        """_pad_alpha는 스페이스 정규화를 하지 않음 (입력 그대로 패스 + alpha)."""
        result = _pad_alpha("0 0 0")
        assert result == "0 0 0 255"


# ---------------------------------------------------------------------------
# LayerStyle.emit_lines
# ---------------------------------------------------------------------------

class TestLayerStyle:
    def test_empty_style_emits_nothing(self):
        style = LayerStyle()
        assert style.emit_lines() == []

    def test_border_only(self):
        """Continue 캐스케이드 핵심: 지정한 필드만 출력, 나머지는 건드리지 않음."""
        style = LayerStyle(border="255 255 0")
        lines = style.emit_lines()
        assert len(lines) == 1
        assert lines[0] == "\tSetBorderColor 255 255 0 255"

    def test_icon_plus_effect(self):
        style = LayerStyle(effect="Yellow", icon="0 Yellow Star")
        lines = style.emit_lines()
        assert "\tPlayEffect Yellow" in lines
        assert "\tMinimapIcon 0 Yellow Star" in lines
        # font/text/border 안 나옴
        assert not any("SetFontSize" in l for l in lines)
        assert not any("SetTextColor" in l for l in lines)

    def test_disable_drop(self):
        style = LayerStyle(disable_drop=True)
        assert "\tDisableDropSound True" in style.emit_lines()

    def test_all_fields(self):
        style = LayerStyle(
            text="255 0 0", border="200 100 100", bg="0 0 0 240",
            font=45, sound="1 300", effect="Red", icon="0 Red Star",
        )
        lines = style.emit_lines()
        assert len(lines) == 7
        assert any("SetFontSize 45" in l for l in lines)
        assert any("PlayAlertSound 1 300" in l for l in lines)

    def test_rgba_passthrough(self):
        """이미 RGBA로 주면 중복 alpha 안 붙음."""
        style = LayerStyle(text="255 0 0 200")
        assert "\tSetTextColor 255 0 0 200" in style.emit_lines()


# ---------------------------------------------------------------------------
# make_layer_block
# ---------------------------------------------------------------------------

class TestMakeLayerBlock:
    def test_basic_show_continue(self):
        style = LayerStyle(border="255 255 0")
        block = make_layer_block(
            LAYER_T1_BORDER,
            "T1 테스트",
            ["Rarity Rare", 'BaseType == "Opal Ring"'],
            style,
        )
        assert block.startswith("Show # PathcraftAI [L6] T1 테스트")
        assert "\tContinue" in block
        assert "\tRarity Rare" in block

    def test_category_tag_appended(self):
        block = make_layer_block(
            LAYER_T1_BORDER,
            "T1 주얼리",
            ["Rarity Rare"],
            LayerStyle(border="255 255 0"),
            category_tag="jewelry",
        )
        assert "[L6|jewelry]" in block

    def test_hide_action(self):
        block = make_layer_block(
            LAYER_CATCH_ALL,
            "Normal AL>=14",
            ["Rarity Normal", "AreaLevel >= 14"],
            LayerStyle(),
            action="Hide",
        )
        assert block.startswith("Hide # PathcraftAI")

    def test_continue_off(self):
        block = make_layer_block(
            LAYER_T1_BORDER, "final", ["Rarity Rare"],
            LayerStyle(), continue_=False,
        )
        assert "\tContinue" not in block

    def test_invalid_action_raises(self):
        with pytest.raises(ValueError, match="action"):
            make_layer_block(
                LAYER_T1_BORDER, "x", [], LayerStyle(), action="Garbage",
            )

    def test_invalid_layer_raises(self):
        with pytest.raises(ValueError, match="layer"):
            make_layer_block(
                999, "x", [], LayerStyle(),
            )

    def test_conditions_indented(self):
        block = make_layer_block(
            LAYER_T1_BORDER, "x",
            ["Rarity Rare", 'BaseType == "Opal Ring"'],
            LayerStyle(),
        )
        lines = block.split("\n")
        assert lines[1] == "\tRarity Rare"
        assert lines[2] == '\tBaseType == "Opal Ring"'


# ---------------------------------------------------------------------------
# load_t1_bases
# ---------------------------------------------------------------------------

class TestLoadT1Bases:
    def test_loads_default(self):
        result = load_t1_bases()
        assert isinstance(result, T1Bases)
        assert isinstance(result.categories, dict)
        assert isinstance(result.has_influence_all, bool)

    def test_expected_categories_present(self):
        result = load_t1_bases()
        for expected in ("wands", "body_armour", "amulets", "rings", "belts"):
            assert expected in result.categories, f"missing: {expected}"
            assert len(result.categories[expected]) > 0

    def test_known_t1_bases(self):
        """프로젝트에서 의존하는 핵심 베이스 존재 확인."""
        cats = load_t1_bases().categories
        assert "Convoking Wand" in cats["wands"]
        assert "Opal Ring" in cats["rings"]
        assert "Stygian Vise" in cats["belts"]
        assert "Marble Amulet" in cats["amulets"]

    def test_has_influence_all_default(self):
        assert load_t1_bases().has_influence_all is True

    def test_ilvl_threshold_loaded(self):
        """_meta.ilvl_threshold 값이 JSON에서 그대로 로드되어야 함."""
        assert load_t1_bases().ilvl_threshold == 86

    def test_all_bases_flatten(self):
        """all_bases()는 중복 없는 평탄 리스트."""
        result = load_t1_bases()
        flat = result.all_bases()
        assert len(flat) == len(set(flat))  # 중복 없음
        assert "Opal Ring" in flat
        assert "Convoking Wand" in flat
        assert flat == sorted(flat)  # 정렬됨

    def test_t1bases_frozen(self):
        """T1Bases는 frozen dataclass — 변경 시도 시 FrozenInstanceError."""
        from dataclasses import FrozenInstanceError
        result = load_t1_bases()
        with pytest.raises(FrozenInstanceError):
            result.ilvl_threshold = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# style_from_palette
# ---------------------------------------------------------------------------

class TestStyleFromPalette:
    def test_produces_layerstyle(self):
        style = style_from_palette("currency", "P1_KEYSTONE")
        assert isinstance(style, LayerStyle)
        assert style.text is not None
        assert style.border is not None

    def test_overrides_apply(self):
        style = style_from_palette(
            "currency", "P1_KEYSTONE",
            border="255 255 0",
        )
        assert style.border == "255 255 0"


# ---------------------------------------------------------------------------
# L1 Catch-All + L2 Default Rarity
# ---------------------------------------------------------------------------

class TestLayerCatchAll:
    def test_produces_l1_block(self):
        block = layer_catch_all()
        assert "[L1|catchall]" in block
        assert block.startswith("Show # PathcraftAI")

    def test_orange_color(self):
        block = layer_catch_all()
        assert "SetTextColor 255 123 0 255" in block
        assert "SetBorderColor 255 123 0 255" in block

    def test_has_icon_and_continue(self):
        block = layer_catch_all()
        assert "MinimapIcon 2 Orange UpsideDownHouse" in block
        assert "\tContinue" in block

    def test_no_conditions_matches_all(self):
        """Catch-All은 조건 없이 모든 아이템 매칭."""
        lines = layer_catch_all().split("\n")
        cond_lines = [l for l in lines
                      if l.startswith("\t") and not any(
                          l.startswith(f"\t{kw}") for kw in
                          ("Set", "Play", "Minimap", "Continue",
                           "DisableDropSound"))]
        assert cond_lines == []


class TestLayerDefaultRarity:
    def test_four_blocks(self):
        """Normal/Magic/Rare/Unique 각각 L2 블록."""
        text = layer_default_rarity()
        assert text.count("[L2|normal]") == 1
        assert text.count("[L2|magic]") == 1
        assert text.count("[L2|rare]") == 1
        assert text.count("[L2|unique]") == 1

    def test_each_has_rarity_condition(self):
        text = layer_default_rarity()
        assert "Rarity Normal" in text
        assert "Rarity Magic" in text
        assert "Rarity Rare" in text
        assert "Rarity Unique" in text

    def test_all_continue(self):
        """모든 레어리티 블록은 Continue (다음 레이어로 흘러감)."""
        text = layer_default_rarity()
        assert text.count("\tContinue") == 4

    def test_no_bg_override(self):
        """L2는 색/폰트/보더만 지정, bg는 L1 오렌지 배경 유지."""
        text = layer_default_rarity()
        assert "SetBackgroundColor" not in text


class TestLayerSocketBorder:
    def test_two_blocks(self):
        text = layer_socket_border()
        assert "[L3|jeweller]" in text
        assert "[L3|chromatic]" in text

    def test_6socket_condition(self):
        text = layer_socket_border()
        assert "Sockets >= 6" in text

    def test_rgb_condition(self):
        text = layer_socket_border()
        assert "SocketGroup RGB" in text

    def test_pink_border(self):
        text = layer_socket_border()
        assert "SetBorderColor 255 0 200 255" in text
        # 두 블록 모두 핑크
        assert text.count("SetBorderColor 255 0 200 255") == 2

    def test_no_text_or_bg_override(self):
        """L3는 보더만 바꾼다 (text/bg/font 이전 레이어 유지)."""
        text = layer_socket_border()
        assert "SetTextColor" not in text
        assert "SetBackgroundColor" not in text
        assert "SetFontSize" not in text


class TestLayerCorruptBorder:
    def test_two_blocks(self):
        text = layer_corrupt_border()
        assert "[L5|corrupted]" in text
        assert "[L5|mirrored]" in text

    def test_corrupted_condition(self):
        text = layer_corrupt_border()
        assert "Corrupted True" in text

    def test_mirrored_condition(self):
        text = layer_corrupt_border()
        assert "Mirrored True" in text

    def test_red_border(self):
        text = layer_corrupt_border()
        # 부패/미러 둘 다 빨강
        assert text.count("SetBorderColor 200 0 0 255") == 2

    def test_both_have_play_effect(self):
        text = layer_corrupt_border()
        assert "PlayEffect Red Temp" in text   # 부패 (일시)
        assert "PlayEffect Red" in text        # 미러 (영구)


class TestLayerT1Border:
    def test_block_count_equals_categories_plus_influenced(self):
        """T1 블록 수 = 카테고리 수 + Influenced 블록 1개."""
        bases = load_t1_bases()
        text = layer_t1_border()
        expected = len(bases.categories) + (1 if bases.has_influence_all else 0)
        actual = text.count("[L6|")
        assert actual == expected

    def test_yellow_border_and_star(self):
        text = layer_t1_border()
        assert "SetBorderColor 255 255 0 255" in text
        assert "MinimapIcon 0 Yellow Star" in text
        assert "PlayEffect Yellow" in text

    def test_ilvl_threshold_in_all_blocks(self):
        """모든 T1 블록에 ItemLevel >= threshold 조건."""
        bases = load_t1_bases()
        text = layer_t1_border()
        expected_count = len(bases.categories) + (1 if bases.has_influence_all else 0)
        assert text.count(f"ItemLevel >= {bases.ilvl_threshold}") == expected_count

    def test_rarity_rare_filter(self):
        """T1 보더는 레어에만 적용."""
        text = layer_t1_border()
        assert "Rarity Rare" in text

    def test_influenced_block_separate(self):
        """Influenced는 BaseType 매칭 없이 HasInfluence 조건으로 독립."""
        bases = load_t1_bases()
        text = layer_t1_border()
        assert "[L6|influenced]" in text
        expected_cond = "HasInfluence " + " ".join(bases.influence_types)
        assert expected_cond in text

    def test_influence_types_loaded_from_json(self):
        """_meta.influence_types가 JSON에서 로드되어 T1Bases에 노출됨."""
        bases = load_t1_bases()
        assert bases.influence_types == (
            "Shaper", "Elder", "Crusader", "Hunter", "Redeemer", "Warlord",
        )

    def test_category_tags_present(self):
        """모든 T1Bases 카테고리가 블록 태그로 등장."""
        bases = load_t1_bases()
        text = layer_t1_border()
        for category in bases.categories:
            assert f"[L6|{category}]" in text, f"missing category tag: {category}"

    def test_no_text_bg_font_override(self):
        """L6는 보더/아이콘/이펙트만. text/bg/font는 이전 레이어 유지."""
        text = layer_t1_border()
        assert "SetTextColor" not in text
        assert "SetBackgroundColor" not in text
        assert "SetFontSize" not in text


class TestLoadProgressiveHide:
    def test_loads(self):
        data = load_progressive_hide()
        assert isinstance(data, ProgressiveHideData)

    def test_always_hide_items(self):
        d = load_progressive_hide()
        assert "Scroll Fragment" in d.always_hide
        assert "Alteration Shard" in d.always_hide

    def test_supply_stages_5(self):
        d = load_progressive_hide()
        assert len(d.supply_stages) == 5
        # Wreckers 분석문서 값
        assert d.supply_stages[0] == (64, 1)
        assert d.supply_stages[4] == (83, 5)

    def test_al_thresholds(self):
        d = load_progressive_hide()
        assert d.normal_all_al == 14
        assert d.magic_all_al == 24
        assert d.gem_hide_al == 45
        assert d.flask_hide_al == 73


class TestLayerHardHide:
    def test_always_hide_block(self):
        text = layer_hard_hide()
        assert "[L0|always]" in text
        assert text.startswith("Hide # PathcraftAI")

    def test_no_continue(self):
        """L0는 정지 (Continue 없음)."""
        text = layer_hard_hide()
        # 헤더 외 Continue 없음
        assert "\tContinue" not in text

    def test_disable_drop_sound(self):
        text = layer_hard_hide()
        assert "DisableDropSound True" in text


class TestLayerProgressiveHide:
    def test_strictness_0_empty(self):
        """엄격도 0은 빈 문자열 (L0 HARD_HIDE만 있고 프로그레시브 없음)."""
        assert layer_progressive_hide(0) == ""

    def test_normal_al14(self):
        text = layer_progressive_hide(1)
        assert "[L9|normal_all]" in text
        assert "Rarity Normal" in text
        assert "AreaLevel >= 14" in text

    def test_magic_al24_only_at_strictness_2_plus(self):
        assert "[L9|magic_all]" not in layer_progressive_hide(1)
        assert "[L9|magic_all]" in layer_progressive_hide(2)

    def test_supply_stages_progressive(self):
        """엄격도 1: stage 1개, 2: 2개, 3: 3개, 4: 5개."""
        assert layer_progressive_hide(1).count("[L9|supply]") == 1
        assert layer_progressive_hide(2).count("[L9|supply]") == 2
        assert layer_progressive_hide(3).count("[L9|supply]") == 3
        assert layer_progressive_hide(4).count("[L9|supply]") == 5

    def test_gem_al45_at_strictness_2(self):
        assert "[L9|gem]" not in layer_progressive_hide(1)
        text = layer_progressive_hide(2)
        assert "[L9|gem]" in text
        assert "AreaLevel >= 45" in text

    def test_flask_al73_at_strictness_3(self):
        assert "[L9|flask]" not in layer_progressive_hide(2)
        text = layer_progressive_hide(3)
        assert "[L9|flask]" in text
        assert "AreaLevel >= 73" in text

    def test_all_blocks_have_continue(self):
        """모든 Progressive Hide 블록은 Continue 포함 (재Show 허용)."""
        text = layer_progressive_hide(4)
        hide_blocks = text.count("Hide # PathcraftAI [L9|")
        continue_count = text.count("\tContinue")
        assert continue_count == hide_blocks

    def test_monotonic_block_count(self):
        """엄격도 높을수록 블록 수 단조 증가."""
        counts = [layer_progressive_hide(s).count("Hide # PathcraftAI [L9|")
                  for s in range(5)]
        assert counts[0] == 0
        assert counts[0] <= counts[1] <= counts[2] <= counts[3] <= counts[4]
        assert counts[4] > counts[1]  # 실제 증가 확인

    def test_leveling_bases_at_strictness_2(self):
        """strictness 2부터 레벨링 초반 베이스 포함."""
        assert layer_progressive_hide(1).count("[L9|level_early]") == 0
        d = load_progressive_hide()
        assert layer_progressive_hide(2).count("[L9|level_early]") == len(
            d.leveling_bases_early)

    def test_midgame_bases_at_strictness_3(self):
        assert layer_progressive_hide(2).count("[L9|level_mid]") == 0
        d = load_progressive_hide()
        assert layer_progressive_hide(3).count("[L9|level_mid]") == len(
            d.equipment_bases_midgame)

    def test_strictness_out_of_range_raises(self):
        """strictness 범위 밖 → ValueError (silent fallback 방지)."""
        with pytest.raises(ValueError, match="0~4"):
            layer_progressive_hide(-1)
        with pytest.raises(ValueError, match="0~4"):
            layer_progressive_hide(5)

    def test_small_flask_al3_present(self):
        """분석문서의 AL 3 Small Life/Mana Flask 커버."""
        text = layer_progressive_hide(2)
        assert "Small Life Flask" in text
        assert "Small Mana Flask" in text


class TestLoadCategoryData:
    def test_loads(self):
        d = load_category_data()
        assert isinstance(d, CategoryData)
        assert "t1_mirror_divine" in d.currency_tiers
        assert "t1_top" in d.divcard_tiers


class TestLayerCurrency:
    def test_six_tier_blocks(self):
        text = layer_currency()
        for tier in ("t1_mirror_divine", "t2_exalted", "t3_annulment",
                     "t4_chaos", "t5_alchemy", "t7_chance"):
            assert f"[L8|currency_{tier}]" in text, f"missing tier: {tier}"

    def test_no_continue(self):
        """L8는 최종 스타일 — Continue 없음."""
        text = layer_currency()
        assert "\tContinue" not in text

    def test_contains_known_currencies(self):
        """t1_mirror_divine은 Mirror + Divine 둘 다, t4_chaos는 Chaos 포함."""
        text = layer_currency()
        assert '"Mirror of Kalandra"' in text
        assert '"Divine Orb"' in text
        assert '"Chaos Orb"' in text
        assert '"Exalted Orb"' in text

    def test_class_conditions(self):
        """유효한 Class 토큰만 사용, 'Stackable Currency'는 실존 안 함."""
        text = layer_currency()
        assert 'Class "Currency"' in text
        assert '"Stackable Currency"' not in text  # 존재하지 않는 Class
        assert '"Map Fragments"' in text
        assert '"Scarabs"' in text


class TestLayerMaps:
    def test_four_tier_blocks(self):
        text = layer_maps()
        for tag in ("white", "yellow", "red", "t16plus"):
            assert f"[L8|map_{tag}]" in text

    def test_maptier_ranges(self):
        text = layer_maps()
        assert "MapTier <= 5" in text
        assert "MapTier >= 6" in text
        assert "MapTier <= 10" in text
        assert "MapTier >= 11" in text
        assert "MapTier <= 15" in text
        assert "MapTier >= 16" in text

    def test_t16_white_bg(self):
        """T16+는 흰색 배경."""
        text = layer_maps()
        # t16plus 블록만 배경이 흰색
        t16_block_start = text.find("[L8|map_t16plus]")
        t16_block = text[t16_block_start:t16_block_start + 500]
        assert "SetBackgroundColor 255 255 255" in t16_block

    def test_class_maps(self):
        text = layer_maps()
        assert 'Class "Maps"' in text

    def test_no_continue(self):
        text = layer_maps()
        assert "\tContinue" not in text


class TestLayerDivcards:
    def test_five_tier_blocks(self):
        text = layer_divcards()
        for tier in ("t1_top", "t2_high", "t3_good", "t4_medium", "t5_common"):
            assert f"[L8|divcard_{tier}]" in text

    def test_class_divination(self):
        text = layer_divcards()
        assert 'Class "Divination Cards"' in text

    def test_t1_has_purple_square_icon(self):
        """t1_top은 Purple Square (팔레트 P1) 아이콘."""
        text = layer_divcards()
        t1_start = text.find("[L8|divcard_t1_top]")
        t2_start = text.find("[L8|divcard_t2", t1_start)
        t1_block = text[t1_start:t2_start if t2_start > 0 else len(text)]
        assert "MinimapIcon 0 Purple Square" in t1_block

    def test_no_continue(self):
        text = layer_divcards()
        assert "\tContinue" not in text


class TestLayerBuildTarget:
    def test_no_build_data_returns_empty(self):
        assert layer_build_target(None) == ""
        assert layer_build_target({}) == ""

    def test_uniques_block(self):
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|unique]" in text
        assert '"Tabula Rasa"' in text
        assert '"Mageblood"' in text

    def test_target_divcards_block(self):
        """Tabula Rasa → Humility 카드, Mageblood → Apothecary 카드."""
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|divcard]" in text
        assert '"Humility"' in text
        assert '"The Apothecary"' in text

    def test_chanceable_block(self):
        """Tabula Rasa → Simple Robe chanceable."""
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|chanceable]" in text
        assert '"Simple Robe"' in text

    def test_skill_gems_block(self):
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|skill_gem]" in text
        assert '"Cyclone"' in text

    def test_support_gems_block(self):
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|support_gem]" in text
        assert '"Fortify Support"' in text

    def test_base_block(self):
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|base]" in text
        assert '"Jewelled Foil"' in text

    def test_all_continue(self):
        """L7 모든 블록은 Continue (스타일 누적용)."""
        text = layer_build_target(TABULA_BUILD)
        hide_show = text.count("Show # PathcraftAI [L7|")
        continue_count = text.count("\tContinue")
        assert continue_count == hide_show

    def test_cyan_signature(self):
        text = layer_build_target(TABULA_BUILD)
        # 모든 블록에 Cyan 시그니처
        assert text.count("PlayEffect Cyan") >= 5


class TestLayerReShow:
    def test_no_build_data_returns_empty(self):
        assert layer_re_show(None) == ""
        assert layer_re_show({}) == ""

    def test_chanceable_reshow(self):
        """Chanceable Normal 베이스를 L10에서 재Show (L9 Normal AL>=14 방어)."""
        text = layer_re_show(TABULA_BUILD)
        assert "[L10|chanceable]" in text
        assert "Rarity Normal" in text
        assert '"Simple Robe"' in text

    def test_no_continue(self):
        """L10은 최종 Show — Continue 없음."""
        text = layer_re_show(TABULA_BUILD)
        assert "\tContinue" not in text

    def test_base_magic_reshow(self):
        text = layer_re_show(TABULA_BUILD)
        assert "[L10|base_magic]" in text
        assert '"Jewelled Foil"' in text


class TestGenerateBetaOverlayWithBuild:
    def test_build_data_injects_l7_l10(self):
        """build_data 전달 시 L7/L10 블록 생성."""
        overlay = generate_beta_overlay(
            strictness=3,
            build_data=TABULA_BUILD,
        )
        assert "[L7|" in overlay
        assert "[L10|" in overlay

    def test_no_build_no_l7_l10(self):
        """build_data 없으면 L7/L10 비활성."""
        overlay = generate_beta_overlay(strictness=3)
        assert "[L7|" not in overlay
        assert "[L10|" not in overlay

    def test_l10_after_l9(self):
        """L10은 L9 뒤에 배치 (Hide 이후 재Show)."""
        overlay = generate_beta_overlay(
            strictness=3, build_data=TABULA_BUILD,
        )
        l9_pos = overlay.find("[L9|")
        l10_pos = overlay.find("[L10|")
        assert 0 < l9_pos < l10_pos


class TestGenerateBetaOverlay:
    def test_cascade_order(self):
        """L0 → L1 → L2 → L3 → L5 → L6 → L8 → L9 순서대로 배치됨."""
        overlay = generate_beta_overlay(strictness=3)
        positions = {
            "L0": overlay.find("[L0|always]"),
            "L1": overlay.find("[L1|catchall]"),
            "L2": overlay.find("[L2|normal]"),
            "L3": overlay.find("[L3|jeweller]"),
            "L5": overlay.find("[L5|corrupted]"),
            "L6": overlay.find("[L6|"),
            "L8": overlay.find("[L8|"),
            "L9": overlay.find("[L9|"),
        }
        assert all(p > 0 for p in positions.values())
        assert positions["L0"] < positions["L1"] < positions["L2"] < positions["L3"]
        assert positions["L3"] < positions["L5"] < positions["L6"]
        assert positions["L6"] < positions["L8"] < positions["L9"]

    def test_strictness_0_no_progressive(self):
        """엄격도 0: L0 있지만 L9 없음."""
        overlay = generate_beta_overlay(strictness=0)
        assert "[L0|always]" in overlay
        assert "[L9|" not in overlay

    def test_valid_filter_syntax(self):
        """POE 필터 기본 문법: Show/Hide로 시작하는 블록 존재, 인덴트는 탭."""
        overlay = generate_beta_overlay(strictness=3)
        lines = overlay.split("\n")
        block_starts = [l for l in lines if l.startswith("Show ") or l.startswith("Hide ")]
        # L0(1) + L1(1) + L2(4) + L3(2) + L5(2) + L6(20) + L9(다수) = 40+
        assert len(block_starts) >= 30
        for line in lines:
            if line and not line.startswith("#") and not line.startswith(("Show", "Hide")):
                if line.strip():
                    assert line.startswith("\t"), f"non-tab indent: {line!r}"

    def test_header_present(self):
        overlay = generate_beta_overlay()
        assert "PathcraftAI β Continue Chain Filter" in overlay
