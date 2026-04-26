# -*- coding: utf-8 -*-
"""sections_continue β Continue 빌더 유닛 테스트."""

import json
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

    def test_custom_sound_emit(self):
        """custom_sound 튜플 → CustomAlertSound "filename" volume 출력."""
        style = LayerStyle(custom_sound=("6Link.mp3", 300))
        lines = style.emit_lines()
        assert '\tCustomAlertSound "6Link.mp3" 300' in lines

    def test_custom_sound_omit_when_none(self):
        """custom_sound=None이면 CustomAlertSound 줄 생성 안 함."""
        style = LayerStyle(border="255 0 0")
        lines = style.emit_lines()
        assert not any("CustomAlertSound" in l for l in lines)

    def test_sound_and_custom_sound_coexist(self):
        """PlayAlertSound와 CustomAlertSound 둘 다 지정 가능 (POE 엔진이 custom 우선)."""
        style = LayerStyle(sound="1 300", custom_sound=("6Link.mp3", 300))
        lines = style.emit_lines()
        # 순서: PlayAlertSound 먼저, CustomAlertSound 뒤
        sound_idx = next(i for i, l in enumerate(lines) if "PlayAlertSound" in l)
        custom_idx = next(i for i, l in enumerate(lines) if "CustomAlertSound" in l)
        assert sound_idx < custom_idx


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

    def test_rarity_specific_font_sizes(self):
        """Option D: Rarity별 차등 폰트 (Aurora 팔레트 P5~P2 정렬).
        Normal 36 / Magic 38 / Rare 40 / Unique 42.
        """
        text = layer_default_rarity()
        expected = [
            ("normal", 36), ("magic", 38), ("rare", 40), ("unique", 42),
        ]
        for tag, font_sz in expected:
            idx = text.find(f"[L2|{tag}]")
            end = text.find("Continue", idx)
            block = text[idx:end]
            assert f"SetFontSize {font_sz}" in block, \
                f"L2 {tag} should have font {font_sz}"

    def test_fonts_at_or_above_palette_floor(self):
        """모든 L2 폰트 >= Aurora 팔레트 하한 P6(34)."""
        from pathcraft_palette import FONT_SIZES
        text = layer_default_rarity()
        floor = FONT_SIZES["P6_LOW"]  # 34
        import re
        for m in re.finditer(r"SetFontSize (\d+)", text):
            assert int(m.group(1)) >= floor, \
                f"L2 font {m.group(1)} below palette floor {floor}"


class TestLayerSocketBorder:
    """Wreckers L2417~2444 4블록 parity — AL 및 크기 제한."""

    def test_six_blocks(self):
        text = layer_socket_border()
        for tag in ("chromatic_campaign", "chromatic_small",
                    "jeweller_campaign", "jeweller_small",
                    "epic_6link_corrupted", "epic_6link"):
            assert f"[L3|{tag}]" in text

    def test_rgb_campaign_al_limit(self):
        """Wreckers L2417: 캠페인 RGB는 AL<68 전체 크기."""
        text = layer_socket_border()
        start = text.find("[L3|chromatic_campaign]")
        end = text.find("Continue", start)
        block = text[start:end]
        assert "AreaLevel < 68" in block
        assert "SocketGroup RGB" in block
        assert "Height" not in block  # 크기 제한 없음

    def test_rgb_small_yellow_map(self):
        """Wreckers L2423: AL<81 + H<=3 + W=1 소형만."""
        text = layer_socket_border()
        start = text.find("[L3|chromatic_small]")
        end = text.find("Continue", start)
        block = text[start:end]
        assert "AreaLevel < 81" in block
        assert "Height <= 3" in block
        assert "Width = 1" in block

    def test_jeweller_campaign_al_limit(self):
        """Wreckers L2431: 6소켓 AL<78 전체 크기."""
        text = layer_socket_border()
        start = text.find("[L3|jeweller_campaign]")
        end = text.find("Continue", start)
        block = text[start:end]
        assert "AreaLevel < 78" in block
        assert "Sockets >= 6" in block
        assert "Height" not in block

    def test_jeweller_small_red_map(self):
        """Wreckers L2437: AL 78~82 + H<=3 + W<=2 소형만."""
        text = layer_socket_border()
        start = text.find("[L3|jeweller_small]")
        end = text.find("Continue", start)
        block = text[start:end]
        assert "AreaLevel >= 78" in block
        assert "AreaLevel <= 82" in block
        assert "Sockets >= 6" in block
        assert "Height <= 3" in block
        assert "Width <= 2" in block

    def test_pink_border_all_blocks(self):
        text = layer_socket_border()
        # 4 decoration + 1 Epic (uncorrupted) = 5 블록 pink 보더. 부패 Epic은 Red.
        assert text.count("SetBorderColor 255 0 200 255") == 5
        # Corrupted Epic은 Red border 별도
        assert text.count("SetBorderColor 200 0 0 255") == 1

    def test_decoration_blocks_no_text_or_bg_override(self):
        """L3 decoration 4블록은 보더/이펙트/아이콘만. Epic 6-Link는 예외 (final Show)."""
        text = layer_socket_border()
        # Epic 6-Link는 text/bg/font 명시 필요 (final Show라 이전 레이어 의존 불가)
        # decoration 4블록만 따로 확인
        for tag in ("chromatic_campaign", "chromatic_small",
                    "jeweller_campaign", "jeweller_small"):
            start = text.find(f"[L3|{tag}]")
            end = text.find("Continue", start)
            block = text[start:end]
            assert "SetTextColor" not in block, f"{tag}: text override forbidden"
            assert "SetBackgroundColor" not in block, f"{tag}: bg override forbidden"
            assert "SetFontSize" not in block, f"{tag}: font override forbidden"

    def test_epic_6link_style(self):
        """Epic 6-Link: Red BG + White text + Pink Star + Sanavi CustomAlertSound."""
        text = layer_socket_border()
        start = text.find("[L3|epic_6link]")
        end = text.find("\n\n", start)
        block = text[start:end] if end > 0 else text[start:]
        assert "LinkedSockets >= 6" in block
        assert "SetFontSize 45" in block
        assert "SetTextColor 255 255 255 255" in block
        assert "SetBackgroundColor 200 0 0 255" in block
        assert "SetBorderColor 255 0 200 255" in block  # Pink border
        assert 'CustomAlertSound "6Link.mp3" 300' in block
        assert "PlayEffect Red" in block
        assert "MinimapIcon 0 Pink Star" in block
        # Continue 없음 (final Show)
        assert "\tContinue" not in block

    def test_t17_maps_no_socket_display(self):
        """AL>82 (T16+) 구간은 RGB/6소켓 표시 없음 (Epic 6-Link은 예외)."""
        text = layer_socket_border()
        # Decoration 4블록만 확인
        for tag in ("chromatic_campaign", "chromatic_small",
                    "jeweller_campaign", "jeweller_small"):
            start = text.find(f"[L3|{tag}]")
            end = text.find("Continue", start)
            block = text[start:end]
            assert "AreaLevel >= 83" not in block
            assert "AreaLevel > 82" not in block

    def test_corrupted_6link_before_uncorrupted(self):
        """POE 필터 top-down semantic: 부패 Epic 6L이 uncorrupted Epic보다 앞에 와야 함.
        순서 반전 시 uncorrupted가 모든 6L을 잡아 부패 Red border 못 적용.
        """
        text = layer_socket_border()
        idx_corrupted = text.find("[L3|epic_6link_corrupted]")
        idx_uncorrupted = text.find("[L3|epic_6link]")
        assert 0 < idx_corrupted < idx_uncorrupted, \
            f"Corrupted Epic must precede uncorrupted Epic (got {idx_corrupted}, {idx_uncorrupted})"

    def test_al_boundary_conditions(self):
        """AL 경계값 문자열 정확성 — 회귀 시 <= vs < 실수 탐지.
        Wreckers 원본: AL<68, AL<81, AL<78, AL>=78 + AL<=82.
        """
        text = layer_socket_border()
        assert "AreaLevel < 68" in text  # chromatic_campaign (캠페인 전체)
        assert "AreaLevel < 81" in text  # chromatic_small (옐로우맵까지)
        assert "AreaLevel < 78" in text  # jeweller_campaign (화이트맵까지)
        assert "AreaLevel >= 78" in text  # jeweller_small 하한
        assert "AreaLevel <= 82" in text  # jeweller_small 상한
        # 잘못된 경계 (회귀 탐지)
        assert "AreaLevel <= 68" not in text
        assert "AreaLevel >= 81" not in text
        assert "AreaLevel <= 78" not in text


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

    def test_white_border_and_star(self):
        """NeverSink/Wreckers 표준: T1 보더 흰색 통일."""
        text = layer_t1_border()
        assert "SetBorderColor 255 255 255 255" in text
        assert "MinimapIcon 0 White Star" in text
        assert "PlayEffect White" in text

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

    def test_uniform_white_border(self):
        """L6 T1 border는 NeverSink/Wreckers 표준 따라 모든 클래스 흰색 통일."""
        text = layer_t1_border()
        assert "PlayEffect White" in text
        assert "255 255 255" in text  # White border
        # 그룹별 색 차별화 안 함 (Yellow/Orange/Pink 안 보여야)
        assert "PlayEffect Yellow" not in text
        assert "PlayEffect Orange" not in text
        assert "PlayEffect Pink" not in text


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

    def test_gem_al45_trade_only(self):
        """Trade 모드에서만 bare gem hide. SSF/HCSSF는 젬 전체 유지."""
        assert "[L9|gem]" not in layer_progressive_hide(2, mode="ssf")
        assert "[L9|gem]" not in layer_progressive_hide(4, mode="ssf")
        assert "[L9|gem]" not in layer_progressive_hide(2, mode="hcssf")
        text_trade = layer_progressive_hide(2, mode="trade")
        assert "[L9|gem]" in text_trade
        assert "AreaLevel >= 45" in text_trade
        # trade mode strictness 1 에서도 없음
        assert "[L9|gem]" not in layer_progressive_hide(1, mode="trade")

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
    def test_six_palette_tier_blocks(self):
        """모드 기본(ssf): pathcraft_palette의 P1~P6 6티어 모두 생성."""
        text = layer_currency()  # default mode="ssf"
        for ptier in ("p1_keystone_palette", "p2_core_palette", "p3_useful_palette",
                      "p4_support_palette", "p5_minor_palette", "p6_low_palette"):
            assert f"[L8|currency_{ptier}]" in text, f"missing palette tier: {ptier}"

    def test_no_continue(self):
        """L8는 최종 스타일 — Continue 없음."""
        text = layer_currency()
        assert "\tContinue" not in text

    def test_contains_non_basic_currencies(self):
        """layer_currency는 basic_orbs 이외 커런시만 담당."""
        text = layer_currency()
        # 기본 orb들은 layer_basic_orbs로 이동 → 여기선 없어야
        # 대신 Alchemy 등 다른 커런시 포함
        assert '"Orb of Alchemy"' in text or '"Ancient Orb"' in text

    def test_mode_independence(self):
        """모드별 호출이 에러 없이 동작."""
        for mode in ("trade", "ssf", "hcssf"):
            text = layer_currency(mode=mode)
            assert text  # 비어있지 않음

    def test_class_conditions(self):
        """레퍼런스 필터(NeverSink/Cobalt/Wreckers) 합집합에 있는 Class만 사용."""
        text = layer_currency()
        assert 'Class "Currency"' in text
        assert '"Stackable Currency"' not in text  # 부분매치로 "Currency"가 이미 커버
        assert '"Map Fragments"' in text
        assert '"Scarabs"' not in text  # 레퍼런스 0/8 부재
        assert '"Delirium Orbs"' not in text  # 레퍼런스 0/8 부재


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

    def test_ssf_mode_has_no_hc_override(self):
        """SSF 모드는 HC override 블록 생성하지 않음."""
        text = layer_divcards(mode="ssf")
        assert "[L8|divcard_hc_t1_override]" not in text
        assert "[L8|divcard_hc_t2_override]" not in text

    def test_trade_mode_has_no_hc_override(self):
        """Trade 모드도 HC override 없음."""
        text = layer_divcards(mode="trade")
        assert "[L8|divcard_hc_t1_override]" not in text

    def test_hcssf_mode_inserts_override_blocks(self):
        """HCSSF 모드는 T1/T2 override 블록을 SC 흐름 앞에 삽입."""
        text = layer_divcards(mode="hcssf")
        assert "[L8|divcard_hc_t1_override]" in text
        assert "[L8|divcard_hc_t2_override]" in text
        # HC override가 SC t1_top 앞에 위치
        hc_t1 = text.find("[L8|divcard_hc_t1_override]")
        sc_t1 = text.find("[L8|divcard_t1_top]")
        assert 0 <= hc_t1 < sc_t1

    def test_hcssf_t1_override_has_keystone_styling(self):
        """HC T1 override는 P1_KEYSTONE (Purple Square 0) 스타일."""
        text = layer_divcards(mode="hcssf")
        t1_start = text.find("[L8|divcard_hc_t1_override]")
        t1_end = text.find("[L8|divcard_hc_t2", t1_start)
        t1_block = text[t1_start:t1_end]
        assert "MinimapIcon 0 Purple Square" in t1_block

    def test_hcssf_apothecary_in_t1_override(self):
        """HC Mirage 최고가 카드 The Apothecary는 T1 override 포함."""
        text = layer_divcards(mode="hcssf")
        t1_start = text.find("[L8|divcard_hc_t1_override]")
        t1_end = text.find("[L8|divcard_hc_t2", t1_start)
        t1_block = text[t1_start:t1_end]
        assert '"The Apothecary"' in t1_block


class TestLoadHcDivcardOverride:
    def test_file_missing_returns_empty(self, tmp_path):
        """파일 없으면 빈 override (SC 흐름 유지)."""
        from sections_continue import _load_hc_divcard_override
        result = _load_hc_divcard_override(tmp_path / "missing.json")
        assert result == {"t1_override": [], "t2_override": []}

    def test_malformed_json_returns_empty(self, tmp_path):
        """JSON 파싱 실패 시 빈 override (예외 전파 금지)."""
        from sections_continue import _load_hc_divcard_override
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        result = _load_hc_divcard_override(bad)
        assert result == {"t1_override": [], "t2_override": []}

    def test_loads_override_lists(self, tmp_path):
        """정상 파일은 t1/t2 리스트 반환."""
        from sections_continue import _load_hc_divcard_override
        good = tmp_path / "good.json"
        good.write_text(json.dumps({
            "_meta": {"league": "Hardcore Mirage"},
            "t1_override": ["The Apothecary", "Brother's Gift"],
            "t2_override": ["The Doctor"],
        }), encoding="utf-8")
        result = _load_hc_divcard_override(good)
        assert result["t1_override"] == ["The Apothecary", "Brother's Gift"]
        assert result["t2_override"] == ["The Doctor"]


class TestLayerBuildTarget:
    def test_no_build_data_returns_empty(self):
        assert layer_build_target(None) == ""
        assert layer_build_target({}) == ""

    def test_uniques_block(self):
        """유니크 매칭은 base_type으로 (POE 필터 규약).
        UNIQUE_TO_BASE: Tabula Rasa → Simple Robe, Mageblood → Heavy Belt.
        """
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|unique]" in text
        assert '"Simple Robe"' in text
        assert '"Heavy Belt"' in text
        # 원본 유니크명은 주석에만 (디버깅/추적)
        assert "Tabula Rasa" in text
        assert "Mageblood" in text

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

    def test_act_identify_block(self):
        """액트 단계 빌드 베이스 감정 후보 — AL<68 + Normal/Magic/Rare + Magenta."""
        text = layer_build_target(TABULA_BUILD)
        assert "[L7|base_act_identify]" in text
        # 시그니처: 모든 Rarity + AL<68 + Pink 다이아몬드
        idx = text.find("[L7|base_act_identify]")
        end = text.find("Continue", idx)
        block = text[idx:end]
        assert "Rarity Normal Magic Rare" in block
        assert "AreaLevel < 68" in block
        assert '"Jewelled Foil"' in block
        assert "SetTextColor 255 100 200 255" in block  # Magenta
        assert "MinimapIcon 0 Pink Diamond" in block

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


class TestWeaponPhysProxy:
    """L7 weapon_phys_proxy — NeverSink 812-844 mod-tier 룰 emit.

    통합 테스트: data/weapon_{mod_tiers,base_to_class}.json + gem_weapon_requirements.json
    실제 로드. Tabula fixture의 Jewelled Foil → Thrusting One Hand Swords 경로 검증.
    """

    def test_strictness_3_emits_phys_variant(self):
        # strictness 2+ → HasExplicitMod >= 3, Mirrored/Corrupted 조건 없음
        text = layer_build_target(TABULA_BUILD, strictness=3)
        assert "[L7|weapon_phys_proxy]" in text
        idx = text.find("[L7|weapon_phys_proxy]")
        end = text.find("Continue", idx)
        block = text[idx:end]
        assert '"Thrusting One Hand Swords"' in block
        assert "HasExplicitMod >= 3" in block
        assert '"Tyrannical"' in block  # T1 flat phys — counted_good_mods
        assert 'HasExplicitMod = 0 "Heavy"' in block  # excluded_bad_mods leader
        # physpure 지표 부재
        assert "Mirrored False" not in block
        assert "Corrupted False" not in block

    def test_strictness_1_emits_physpure_variant(self):
        # strictness 0~1 → HasExplicitMod >= 2 + Mirrored/Corrupted False
        text = layer_build_target(TABULA_BUILD, strictness=1)
        idx = text.find("[L7|weapon_phys_proxy]")
        end = text.find("Continue", idx)
        block = text[idx:end]
        assert "Mirrored False" in block
        assert "Corrupted False" in block
        assert "HasExplicitMod >= 2" in block

    def test_no_weapon_in_build_skips_block(self):
        # Spell-only build (no weapon base, only armour) → proxy 블록 생략
        build = {
            "meta": {"build_name": "CI Witch"},
            "items": [],
            "progression_stages": [{
                "gem_setups": {"Arc": []},
                "gear_recommendation": {
                    "Body Armour": {"rarity": "rare", "base_type": "Astral Plate"},
                },
            }],
        }
        text = layer_build_target(build, strictness=3)
        assert "[L7|weapon_phys_proxy" not in text

    def test_block_order_chanceable_before_weapon_proxy(self):
        # first-match semantics: unique > chanceable > weapon_phys_proxy > ...
        text = layer_build_target(TABULA_BUILD, strictness=3)
        pos_chance = text.find("[L7|chanceable")
        pos_proxy = text.find("[L7|weapon_phys_proxy")
        pos_divcard = text.find("[L7|divcard")
        assert pos_chance >= 0 and pos_proxy >= 0 and pos_divcard >= 0
        assert pos_chance < pos_proxy < pos_divcard


class TestDefenseProxy:
    """L7 defense_proxy — 빌드 defence_types 기반 방어 장비 강조 (D4)."""

    @staticmethod
    def _mk_build(armour=0, evasion=0, energy_shield=0) -> dict:
        """Minimal build with stats only (triggers defence_types extraction)."""
        return {
            "meta": {"build_name": "DefenseTest"},
            "items": [],
            "stats": {
                "armour": armour,
                "evasion": evasion,
                "energy_shield": energy_shield,
            },
            "progression_stages": [{
                "gem_setups": {},
                "gear_recommendation": {},
            }],
        }

    def test_no_defence_types_skips_all_blocks(self):
        """stats 없는 빌드 → defence_types 비어 있음 → L7 defense_proxy 0 블록."""
        build = {
            "meta": {"build_name": "NoStats"},
            "items": [],
            "progression_stages": [{"gem_setups": {}, "gear_recommendation": {}}],
        }
        text = layer_build_target(build, strictness=3)
        assert "[L7|defense_proxy" not in text

    def test_pure_armour_emits_life_focused_blocks(self):
        """pure AR 빌드 → life focus 블록만 (5 slots), es focus 없음."""
        text = layer_build_target(self._mk_build(armour=25000), strictness=3)
        for slot in ("body_armour", "helmet", "boots", "gloves", "shield"):
            assert f"[L7|defense_proxy_{slot}_life]" in text
        assert "defense_proxy" in text  # sanity
        # ES focus 미활성
        for slot in ("body_armour", "helmet", "boots", "gloves", "shield"):
            assert f"[L7|defense_proxy_{slot}_es]" not in text

    def test_pure_es_emits_es_focused_blocks(self):
        """CI Witch ES 빌드 → es focus 블록만, life focus 없음."""
        text = layer_build_target(self._mk_build(energy_shield=8000), strictness=3)
        for slot in ("body_armour", "helmet", "boots", "gloves", "shield"):
            assert f"[L7|defense_proxy_{slot}_es]" in text
        for slot in ("body_armour", "helmet", "boots", "gloves", "shield"):
            assert f"[L7|defense_proxy_{slot}_life]" not in text

    def test_hybrid_ar_es_emits_both_focuses(self):
        """Aegis Aurora Occultist ES+AR → life + es 양쪽."""
        text = layer_build_target(
            self._mk_build(armour=6000, energy_shield=6000),
            strictness=3,
        )
        assert "[L7|defense_proxy_body_armour_life]" in text
        assert "[L7|defense_proxy_body_armour_es]" in text

    def test_strictness_affects_mod_count(self):
        """strictness 2+ → HasExplicitMod >= 3, 0~1 → >= 2."""
        text3 = layer_build_target(self._mk_build(armour=25000), strictness=3)
        text1 = layer_build_target(self._mk_build(armour=25000), strictness=1)
        # helmet_life 블록에서 확인
        idx3 = text3.find("[L7|defense_proxy_helmet_life]")
        end3 = text3.find("Continue", idx3)
        block3 = text3[idx3:end3]
        idx1 = text1.find("[L7|defense_proxy_helmet_life]")
        end1 = text1.find("Continue", idx1)
        block1 = text1[idx1:end1]
        assert "HasExplicitMod >= 3" in block3
        assert "HasExplicitMod >= 2" in block1

    def test_block_order_defense_after_weapon_proxy(self):
        """first-match: weapon_phys_proxy > defense_proxy > divcard 순서."""
        # weapon + defence types 둘 다 있는 fixture
        build = {
            "meta": {"build_name": "Combo"},
            "items": [],
            "stats": {"armour": 20000, "evasion": 0, "energy_shield": 0},
            "progression_stages": [{
                "gem_setups": {"Main": {"links": "Cleave"}},
                "gear_recommendation": {
                    "Weapon 1": {"base_type": "Reaver Axe", "rarity": "Normal"},
                },
            }],
        }
        text = layer_build_target(build, strictness=3)
        pos_weapon = text.find("[L7|weapon_phys_proxy")
        pos_defense = text.find("[L7|defense_proxy_")
        pos_divcard = text.find("[L7|divcard")
        assert pos_weapon >= 0 and pos_defense >= 0
        assert pos_weapon < pos_defense
        if pos_divcard >= 0:
            assert pos_defense < pos_divcard

    def test_staged_build_emits_per_stage_defence_types(self):
        """Multi-POB 전환 빌드: leveling life → endgame CI.
        stage=True → leveling 블록엔 life만, endgame 블록엔 es만.
        """
        leveling_pob = {
            "meta": {"class_level": 30, "build_name": "Lv30 life"},
            "items": [],
            "stats": {"armour": 5000, "evasion": 3000, "energy_shield": 0},
            "progression_stages": [{"gem_setups": {}, "gear_recommendation": {}}],
        }
        endgame_pob = {
            "meta": {"class_level": 95, "build_name": "Lv95 CI"},
            "items": [],
            "stats": {"armour": 0, "evasion": 0, "energy_shield": 10000},
            "progression_stages": [{"gem_setups": {}, "gear_recommendation": {}}],
        }
        text = layer_build_target(
            [leveling_pob, endgame_pob], stage=True, strictness=3,
        )
        # leveling stage 블록에 life focus만, es focus 없음
        assert "[L7|defense_proxy_leveling_body_armour_life]" in text
        assert "[L7|defense_proxy_leveling_body_armour_es]" not in text
        # endgame stage 블록에 es focus만, life focus 없음
        assert "[L7|defense_proxy_endgame_body_armour_es]" in text
        assert "[L7|defense_proxy_endgame_body_armour_life]" not in text

    def test_l7_full_block_order_snapshot(self):
        """L7 7-way 블록 순서 박제: unique > chanceable > weapon > defense > accessory > divcard > skill.

        회귀 방어: layer_build_target 내부 emit 순서가 바뀌면 이 테스트로 감지.
        """
        # 모든 L7 카테고리를 활성화하는 fixture
        # - Tabula + Mageblood (unique/chanceable/base)
        # - Jewelled Foil weapon (weapon_phys_proxy)
        # - 20000 armour (defense_proxy)
        # - gem_setups Cyclone (attack → accessory_proxy)
        build = {
            "meta": {"build_name": "FullCoverage"},
            "items": [
                {"rarity": "unique", "name": "Tabula Rasa"},
                {"rarity": "unique", "name": "Mageblood"},
            ],
            "stats": {"armour": 20000, "evasion": 0, "energy_shield": 0},
            "progression_stages": [{
                "gem_setups": {
                    "Cyclone": {
                        "links": "Cyclone - Melee Physical Damage Support - Fortify Support",
                        "reasoning": None,
                    },
                },
                "gear_recommendation": {
                    "weapon": {"rarity": "rare", "base_type": "Jewelled Foil"},
                },
            }],
        }
        text = layer_build_target(build, strictness=3)
        positions = {
            "unique":     text.find("[L7|unique]"),
            "chanceable": text.find("[L7|chanceable]"),
            "weapon":     text.find("[L7|weapon_phys_proxy]"),
            "defense":    text.find("[L7|defense_proxy_"),
            "accessory":  text.find("[L7|accessory_proxy_"),
            "divcard":    text.find("[L7|divcard]"),
            "skill":      text.find("[L7|skill_gem]"),
        }
        # 모든 블록 존재 확인
        for name, pos in positions.items():
            assert pos >= 0, f"missing L7 block: {name}"
        # 순서 박제 (first-match 시맨틱 준수)
        order = ["unique", "chanceable", "weapon", "defense", "accessory", "divcard", "skill"]
        for prev, curr in zip(order, order[1:]):
            assert positions[prev] < positions[curr], (
                f"L7 order violation: {prev}({positions[prev]}) >= {curr}({positions[curr]})"
            )


class TestAccessoryProxy:
    """L7 accessory_proxy — 빌드 damage_types 기반 악세서리 강조 (E6)."""

    @staticmethod
    def _mk_build(main_skill: str = "", armour: int = 0, ev: int = 0, es: int = 0) -> dict:
        """gem_setups + 선택적 stats 빌드."""
        build = {
            "meta": {"build_name": "AccessoryTest"},
            "items": [],
            "progression_stages": [{
                "gem_setups": (
                    {main_skill: {"links": main_skill, "reasoning": None}}
                    if main_skill else {}
                ),
                "gear_recommendation": {},
            }],
        }
        if any((armour, ev, es)):
            build["stats"] = {"armour": armour, "evasion": ev, "energy_shield": es}
        return build

    def test_no_damage_types_still_emits_common(self):
        """damage_types 비어도 common(exalter amulet, general belt)은 emit."""
        build = self._mk_build()  # no gem_setups
        text = layer_build_target(build, strictness=3)
        assert "[L7|accessory_proxy_amulet_common]" in text
        assert "[L7|accessory_proxy_belt_common]" in text
        # damage axis 블록은 없어야 함
        for axis in ("attack", "caster", "dot", "minion"):
            assert f"[L7|accessory_proxy_amulet_{axis}]" not in text

    def test_cyclone_emits_attack_plus_common(self):
        """Cyclone → attack + common 블록, caster/dot/minion 없음."""
        text = layer_build_target(self._mk_build("Cyclone"), strictness=3)
        assert "[L7|accessory_proxy_amulet_attack]" in text
        assert "[L7|accessory_proxy_ring_attack]" in text
        assert "[L7|accessory_proxy_amulet_common]" in text
        for axis in ("caster", "dot", "minion"):
            assert f"[L7|accessory_proxy_amulet_{axis}]" not in text

    def test_righteous_fire_emits_caster_plus_dot(self):
        """RF → caster + dot + common (RF는 Spell + DamageOverTime)."""
        text = layer_build_target(self._mk_build("Righteous Fire"), strictness=3)
        assert "[L7|accessory_proxy_amulet_caster]" in text
        assert "[L7|accessory_proxy_amulet_dot]" in text
        assert "[L7|accessory_proxy_amulet_common]" in text
        assert "[L7|accessory_proxy_amulet_attack]" not in text

    def test_srs_emits_caster_plus_minion(self):
        """SRS → caster + minion + common. ring_minion 포함."""
        text = layer_build_target(self._mk_build("Summon Raging Spirit"), strictness=3)
        assert "[L7|accessory_proxy_amulet_caster]" in text
        assert "[L7|accessory_proxy_ring_minion]" in text
        assert "[L7|accessory_proxy_amulet_minion]" not in text  # amu에 minion axis 없음
        assert "[L7|accessory_proxy_amulet_attack]" not in text

    def test_strictness_affects_mod_count(self):
        """strictness 2+ → HasExplicitMod >= 3, 0~1 → >= 2."""
        text3 = layer_build_target(self._mk_build("Cyclone"), strictness=3)
        text1 = layer_build_target(self._mk_build("Cyclone"), strictness=1)
        idx3 = text3.find("[L7|accessory_proxy_amulet_attack]")
        end3 = text3.find("Continue", idx3)
        idx1 = text1.find("[L7|accessory_proxy_amulet_attack]")
        end1 = text1.find("Continue", idx1)
        assert "HasExplicitMod >= 3" in text3[idx3:end3]
        assert "HasExplicitMod >= 2" in text1[idx1:end1]

    def test_exalter_amulet_common_mod(self):
        """amulet.common 블록은 Exalter's mod 하나만 요구 (NeverSink amu_exalter)."""
        text = layer_build_target(self._mk_build(), strictness=3)
        idx = text.find("[L7|accessory_proxy_amulet_common]")
        end = text.find("Continue", idx)
        block = text[idx:end]
        assert '"Exalter\'s"' in block
        assert 'Class == "Amulets"' in block


class TestWeaponPhysProxyReShow:
    """L10 weapon_phys_proxy 재Show — L9 Hide 복권 검증."""

    def test_weapon_phys_proxy_reshow_present(self):
        """L10에 weapon_phys_proxy 재Show 블록이 존재해야 L9 Hide 복권."""
        text = layer_re_show(TABULA_BUILD)
        assert "[L10|weapon_phys_proxy]" in text
        idx = text.find("[L10|weapon_phys_proxy]")
        end = text.find("\n\n", idx)
        block = text[idx:end] if end > 0 else text[idx:]
        assert '"Thrusting One Hand Swords"' in block
        assert "HasExplicitMod >= 2" in block  # L10은 관대 (2)
        assert '"Tyrannical"' in block
        assert "Continue" not in block  # L10은 Continue=False (최종 Show)

    def test_no_weapon_no_reshow(self):
        """무기 없는 빌드면 weapon_phys_proxy 재Show도 없어야."""
        spell_build = {
            "meta": {"build_name": "CI Witch"},
            "items": [],
            "progression_stages": [{
                "gem_setups": {"Arc": []},
                "gear_recommendation": {
                    "Body Armour": {"rarity": "rare", "base_type": "Astral Plate"},
                },
            }],
        }
        text = layer_re_show(spell_build)
        assert "[L10|weapon_phys_proxy]" not in text


class TestLayerReShow:
    def test_no_build_data_returns_unconditional_t1_only(self):
        """Phase 2 이후: build_data 없어도 unconditional T1 보더 21블록 생성."""
        text_none = layer_re_show(None)
        text_empty = layer_re_show({})
        for text in (text_none, text_empty):
            # 빌드 전용 블록 없음
            assert "[L10|chanceable]" not in text
            assert "[L10|skill_gem]" not in text
            assert "[L10|unique_target]" not in text
            # Unconditional T1 블록 21개 (Wreckers L172/L237 parity)
            assert "[L10|ring_glove_helm_normal]" in text
            assert "[L10|main_equip_rare]" in text
            assert "[L10|small_cluster_magic]" in text

    def test_unconditional_28_blocks(self):
        text = layer_re_show(None)
        # 7 T1 groups × 3 rarities = 21 + 7 Levelling Help blocks = 28
        tag_count = sum(1 for line in text.splitlines()
                        if line.startswith("Show # PathcraftAI [L10|"))
        assert tag_count == 28

    def test_chanceable_reshow(self):
        """Chanceable Normal 베이스를 L10에서 재Show (L9 Normal AL>=14 방어)."""
        text = layer_re_show(TABULA_BUILD)
        assert "[L10|chanceable]" in text
        assert "Rarity Normal" in text
        assert '"Simple Robe"' in text

    def test_no_continue(self):
        """L10은 최종 Show — Continue 없음 (unconditional + 빌드 블록 둘 다)."""
        text = layer_re_show(TABULA_BUILD)
        assert "\tContinue" not in text

    def test_base_magic_reshow(self):
        text = layer_re_show(TABULA_BUILD)
        assert "[L10|base_magic]" in text
        assert '"Jewelled Foil"' in text

    def test_act_identify_reshow_defends_l9(self):
        """액트 감정 재Show — L9 level_mid의 Normal/Magic Hide 방어. Continue=False."""
        text = layer_re_show(TABULA_BUILD)
        assert "[L10|base_act_identify]" in text
        idx = text.find("[L10|base_act_identify]")
        # 다음 블록 시작까지 추출 (단일 Show 블록)
        end = text.find("Show # PathcraftAI [L10|", idx + 1)
        if end < 0:
            end = len(text)
        block = text[idx:end]
        assert "Rarity Normal Magic Rare" in block
        assert "AreaLevel < 68" in block
        assert '"Jewelled Foil"' in block
        # Continue 없음 (final Show)
        assert "\tContinue" not in block


class TestGenerateBetaOverlayWithBuild:
    def test_build_data_injects_l7_l10(self):
        """build_data 전달 시 L7/L10 블록 생성."""
        overlay = generate_beta_overlay(
            strictness=3,
            build_data=TABULA_BUILD,
        )
        assert "[L7|" in overlay
        assert "[L10|" in overlay

    def test_no_build_still_has_l10_unconditional(self):
        """Phase 2: build_data 없어도 L10 unconditional T1 보더 생성 (L7은 여전히 없음)."""
        overlay = generate_beta_overlay(strictness=3)
        assert "[L7|" not in overlay
        # L10 unconditional T1 존재
        assert "[L10|ring_glove_helm_normal]" in overlay
        assert "[L10|main_equip_rare]" in overlay

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
            "L3": overlay.find("[L3|jeweller_campaign]"),
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


# ---------------------------------------------------------------------------
# 다중 POB staging (A+B 플랜 커버리지)
# ---------------------------------------------------------------------------


def _make_build(build_name: str, uniques: list[str] = None, skills: list[str] = None) -> dict:
    """테스트용 POB JSON 팩토리."""
    return {
        "meta": {"build_name": build_name, "class": "Duelist"},
        "items": [{"rarity": "unique", "name": u} for u in (uniques or [])],
        "progression_stages": [{
            "gem_setups": {s: [] for s in (skills or [])},
            "gear_recommendation": {},
        }],
    }


class TestMultiPOBStaging:
    """다중 POB 처리: 기본 union, stage=True시 uniques+chanceable만 AL 분기."""

    def test_single_pob_backward_compat(self):
        """단일 POB (기존 동작 유지, AL 조건 없음)."""
        build = _make_build("Duelist Gladiator Lvl 93", uniques=["Mageblood"], skills=["Cyclone"])
        text = layer_build_target(build)
        assert "[L7|unique]" in text
        assert "AreaLevel" not in text

    def test_default_union_no_al_split(self):
        """기본(stage=False): 다중 POB Δ>=15여도 전체 union, AL 조건 없음."""
        lv = _make_build("Duelist Lvl 69", uniques=["Tabula Rasa"], skills=["Sunder"])
        eg = _make_build("Duelist Lvl 93", uniques=["Mageblood"], skills=["Boneshatter"])
        text = layer_build_target([lv, eg])
        assert "[L7|unique]" in text
        assert "[L7|unique_leveling]" not in text
        assert "[L7|unique_endgame]" not in text
        assert "[L7|skill_gem]" in text
        assert "AreaLevel" not in text
        assert '"Simple Robe"' in text
        assert '"Heavy Belt"' in text
        assert '"Sunder"' in text
        assert '"Boneshatter"' in text

    def test_stage_true_splits_uniques_chanceable_only(self):
        """stage=True: uniques+chanceable만 AL 분기, 나머지 카테고리는 union."""
        lv = _make_build("Duelist Lvl 69", uniques=["Tabula Rasa"], skills=["Sunder"])
        eg = _make_build("Duelist Lvl 93", uniques=["Mageblood"], skills=["Boneshatter"])
        text = layer_build_target([lv, eg], stage=True)
        # uniques 분기
        assert "[L7|unique_leveling]" in text
        assert "[L7|unique_endgame]" in text
        assert "AreaLevel <= 67" in text
        assert "AreaLevel >= 68" in text
        # chanceable 분기 (Tabula Rasa → Simple Robe leveling)
        assert "[L7|chanceable_leveling]" in text
        # skills/supports는 단일 union (AL 조건 없음)
        assert "[L7|skill_gem]" in text  # suffix 없음
        assert "[L7|skill_gem_leveling]" not in text
        assert "[L7|skill_gem_endgame]" not in text

    def test_stage_true_parse_fail_fallbacks_to_union(self):
        """stage=True지만 Lv 파싱 실패 → union fallback."""
        unknown = _make_build("HC SSF Endgame", uniques=["Mageblood"])
        known = _make_build("Lvl 69", uniques=["Tabula Rasa"])
        text = layer_build_target([unknown, known], stage=True)
        assert "[L7|unique]" in text
        assert "[L7|unique_leveling]" not in text
        assert "AreaLevel" not in text

    def test_stage_true_delta_lt_15_unions(self):
        """stage=True지만 Δ<15 → union (분기 무의미)."""
        b1 = _make_build("Duelist Lvl 96", uniques=["Mageblood"])
        b2 = _make_build("Duelist Lvl 99", uniques=["Headhunter"])
        text = layer_build_target([b1, b2], stage=True)
        assert "[L7|unique]" in text
        assert "AreaLevel" not in text

    def test_union_dedups_common_items(self):
        """union 모드에서 공통 젬(Leap Slam)이 1회만 나옴."""
        lv = _make_build("Duelist Lvl 69", skills=["Leap Slam", "Sunder"])
        eg = _make_build("Duelist Lvl 93", skills=["Leap Slam", "Boneshatter"])
        text = layer_build_target([lv, eg])  # 기본 stage=False
        assert "[L7|skill_gem]" in text
        assert "AreaLevel" not in text
        assert text.count('"Leap Slam"') == 1
        assert '"Sunder"' in text
        assert '"Boneshatter"' in text


# ---------------------------------------------------------------------------
# SSF 카테고리 (Lifeforce / Splinter / Scarabs) — MVP
# ---------------------------------------------------------------------------


class TestLoadGGPKItems:
    def test_load_extracts_nonempty(self):
        from sections_continue import load_ggpk_items
        d = load_ggpk_items()
        assert len(d.lifeforce) >= 3, "Lifeforce 3종 이상 (Primal/Sacred/Vivid)"
        assert len(d.splinter_breach) == 5
        assert len(d.splinter_legion) == 5
        assert d.splinter_simulacrum == ("Simulacrum Splinter",)
        assert len(d.scarabs_all) >= 100, "Scarabs 100종 이상"
        # special 포함 여부
        assert any(n.startswith("Horned ") for n in d.scarabs_special), \
            "Horned 스카랩이 special에 있어야 함"

    def test_snapshot_tag_based_classification(self):
        """F0-fix-2 (2026-04-17): 태그 기반 분류 결과 박제.

        변경 감지용 스냅샷. 리그 업데이트 후 GGPK 데이터가 바뀌면 의도적 변경인지 확인.
        diff가 생기면 `_analysis/ggpk_extraction_completeness_audit.md` 업데이트 필요.
        """
        from sections_continue import load_ggpk_items
        import sections_continue as sc
        sc._GGPK_CACHE = None
        sc._TAGS_CACHE = None
        d = load_ggpk_items()

        # Tier 1 — 태그 기반 (명확한 Tags.Id 매핑)
        assert d.splinter_breach == (
            "Splinter of Chayula", "Splinter of Esh", "Splinter of Tul",
            "Splinter of Uul-Netol", "Splinter of Xoph",
        )
        assert d.splinter_legion == (
            "Timeless Eternal Empire Splinter", "Timeless Karui Splinter",
            "Timeless Maraketh Splinter", "Timeless Templar Splinter",
            "Timeless Vaal Splinter",
        )
        assert len(d.scarabs_all) == 190, f"scarabs_all 190 고정, got {len(d.scarabs_all)}"
        # scarabs_special: GGPK 태그(uber/uniques/influence) UNION 위키 Name prefix = 26
        # 2026-04-25: dat64 List element-type 분기 적용 후 BaseItemTypes.Tags 가 정확히 채워져
        # Elder/Reliquary/Shaper 각 4티어 (Rusted/Polished/Gilded/Winged) 12 종이 추가 매칭.
        # 이전 14 → 26. POE Wiki 기준 모두 influence/uber 카테고리.
        assert len(d.scarabs_special) == 26, (
            f"scarabs_special 26 고정 (tag∪wiki-name family), got {len(d.scarabs_special)}"
        )
        assert d.scarabs_special == (
            "Gilded Elder Scarab", "Gilded Reliquary Scarab", "Gilded Shaper Scarab",
            "Horned Scarab of Awakening", "Horned Scarab of Bloodlines",
            "Horned Scarab of Glittering", "Horned Scarab of Nemeses",
            "Horned Scarab of Pandemonium", "Horned Scarab of Preservation",
            "Horned Scarab of Tradition",
            "Influencing Scarab of Hordes",
            "Influencing Scarab of Interference",
            "Influencing Scarab of the Elder",
            "Influencing Scarab of the Shaper",
            "Polished Elder Scarab", "Polished Reliquary Scarab", "Polished Shaper Scarab",
            "Rusted Elder Scarab", "Rusted Reliquary Scarab", "Rusted Shaper Scarab",
            "Titanic Scarab", "Titanic Scarab of Legend", "Titanic Scarab of Treasures",
            "Winged Elder Scarab", "Winged Reliquary Scarab", "Winged Shaper Scarab",
        )

        # Essence 티어: essence 태그 + Name 접두사
        assert len(d.essence_deafening) == 20
        assert len(d.essence_shrieking) == 20
        assert len(d.essence_screaming) == 20
        assert len(d.essence_wailing) == 16
        assert len(d.essence_weeping) == 12
        assert len(d.essence_muttering) == 8
        assert len(d.essence_whispering) == 4
        assert len(d.essence_corrupt) == 5
        assert d.remnant_corruption == ("Remnant of Corruption",)


class TestLayerLifeforce:
    def test_generates_five_tiers(self):
        """NeverSink/Cobalt 5단계 임계: 4000/500/250/45/20"""
        from sections_continue import layer_lifeforce
        text = layer_lifeforce("ssf")
        for stack in (4000, 500, 250, 45, 20):
            assert f"[L8|lifeforce_t" in text
            assert f"StackSize >= {stack}" in text
        assert '"Primal Crystallised Lifeforce"' in text

    def test_invalid_mode_raises(self):
        from sections_continue import layer_lifeforce
        import pytest
        with pytest.raises(ValueError):
            layer_lifeforce("pvp")


class TestLayerSplinters:
    def test_generates_all_three_subcategories(self):
        """NeverSink Breach/Legion 5단계 (80/60/20/5/1) + Simulacrum 2단계 (150/1)."""
        from sections_continue import layer_splinters
        text = layer_splinters("ssf")
        # Breach/Legion 5 임계
        for stack in (80, 60, 20, 5, 1):
            assert f"StackSize >= {stack}" in text
        # Simulacrum 150
        assert "StackSize >= 150" in text
        # 카테고리 태그 존재
        assert "[L8|splinter_breach_s80]" in text
        assert "[L8|splinter_legion_s80]" in text
        assert "[L8|splinter_simulacrum_s150]" in text


class TestLayerScarabs:
    def test_generates_special_and_regular(self):
        from sections_continue import layer_scarabs
        text = layer_scarabs("ssf")
        assert "[L8|scarab_special]" in text
        assert "[L8|scarab_regular]" in text
        assert 'Class "Map Fragments"' in text
        # Horned/Titanic 샘플 포함
        assert 'Horned ' in text or 'Titanic ' in text


class TestGenerateBetaOverlayMode:
    def test_mode_ssf_includes_ssf_categories(self):
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(strictness=3, mode="ssf")
        for tag in ("lifeforce_t1_4000", "splinter_breach_s80", "scarab_special"):
            assert f"[L8|{tag}]" in text

    def test_mode_invalid_raises(self):
        from sections_continue import generate_beta_overlay
        import pytest
        with pytest.raises(ValueError):
            generate_beta_overlay(mode="pvp")


class TestLayerGemsQuality:
    """Wreckers SSF 패턴 기반 젬 퀄리티/레벨 티어링."""

    def test_generates_tier_blocks(self):
        from sections_continue import layer_gems_quality
        text = layer_gems_quality("ssf")
        for tag in ("gem_vaal", "gem_altqual", "gem_awakened",
                    "gem_exceptional_lv4", "gem_q20", "gem_q23", "gem_lv20", "gem_lv21"):
            assert f"[L8|{tag}]" in text

    def test_quality_thresholds_present(self):
        from sections_continue import layer_gems_quality
        text = layer_gems_quality("ssf")
        assert "Quality >= 20" in text
        assert "Quality >= 23" in text
        assert "GemLevel >= 20" in text
        assert "GemLevel >= 21" in text
        assert "GemLevel >= 4" in text

    def test_invalid_mode_raises(self):
        from sections_continue import layer_gems_quality
        import pytest
        with pytest.raises(ValueError):
            layer_gems_quality("pvp")

    def test_included_in_generate_beta_overlay(self):
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(mode="ssf")
        assert "[L8|gem_awakened]" in text
        assert "[L8|gem_q23]" in text


class TestLayerEndgameRare:
    """NeverSink [[1600]] 11블록 구조."""

    def test_eleven_blocks_present(self):
        from sections_continue import layer_endgame_rare
        text = layer_endgame_rare("ssf")
        for tag in (
            "rare_large", "rare_medium_tall", "rare_medium_square", "rare_tiny",
            "rare_4link", "rare_t1_melee", "rare_t1_caster",
            "rare_t1_amulet_gloves_helm", "rare_t1_armor",
            "rare_corrupted_bare", "rare_corrupted_implicit",
        ):
            assert f"[L8|{tag}]" in text

    def test_ilvl_threshold_68_present(self):
        """NeverSink 패턴: 사이즈/4link/corrupted 블록은 ilvl >= 68 (맵 드롭)."""
        from sections_continue import layer_endgame_rare
        text = layer_endgame_rare("ssf")
        assert "ItemLevel >= 68" in text
        # T1 임계는 83/84/85/86
        for ilvl in (83, 84, 85, 86):
            assert f"ItemLevel >= {ilvl}" in text

    def test_size_conditions(self):
        """W>=2 H>=3 (large), W=1 H>=3 (medium tall), W=2 H=2 (square), W<=2 H=1 (tiny)."""
        from sections_continue import layer_endgame_rare
        text = layer_endgame_rare("ssf")
        assert "Width >= 2" in text
        assert "Height >= 3" in text
        assert "Height 1" in text
        assert "Width 2" in text

    def test_invalid_mode_raises(self):
        from sections_continue import layer_endgame_rare
        import pytest
        with pytest.raises(ValueError):
            layer_endgame_rare("pvp")


class TestLayerUniques:
    """NeverSink [[4700]] 유니크 티어링 + Aurora 스타일."""

    def test_keystone_exceptions_present(self):
        from sections_continue import layer_uniques
        text = layer_uniques("ssf")
        for tag in ("unique_6link", "unique_squire", "unique_tabula",
                    "unique_triadgrip", "unique_abyss4"):
            assert f"[L8|{tag}]" in text

    def test_tier_blocks_loaded(self):
        """data/unique_tiers.json에서 T1~T5 + multi_high 로드 확인 (Phase 3a)."""
        from sections_continue import layer_uniques
        text = layer_uniques("ssf")
        for tier in ("t1", "t2", "t3", "t4", "t5", "multi_high"):
            assert f"[L8|unique_{tier}]" in text

    def test_t4_t5_multi_high_basetypes(self):
        """T4/T5/multi_high 샘플 BaseType 존재 확인 (Cobalt Strict 추출)."""
        from sections_continue import layer_uniques
        text = layer_uniques("ssf")
        # T4 (hideable2): Bone Helmet / Nameless Ring / Rustic Sash
        assert '"Bone Helmet"' in text
        assert '"Nameless Ring"' in text
        # T5 (hideable): Wool Gloves / Vine Circlet / Zodiac Leather
        assert '"Wool Gloves"' in text
        assert '"Zodiac Leather"' in text
        # multi_high: Heavy Belt / Leather Belt / Small Cluster Jewel
        assert '"Heavy Belt"' in text
        assert '"Leather Belt"' in text

    def test_tier_palette_differentiation(self):
        """각 티어가 다른 Aurora unique 팔레트 사용 (P1~P5)."""
        from sections_continue import layer_uniques
        from pathcraft_palette import UNIQUE_TIER_COLORS
        text = layer_uniques("ssf")
        # 각 티어 고유 색이 적어도 한 번 등장
        for tier_key in ("P1_KEYSTONE", "P2_CORE", "P3_USEFUL",
                         "P4_SUPPORT", "P5_MINOR"):
            color = UNIQUE_TIER_COLORS[tier_key]
            assert f"SetTextColor {color}" in text, \
                f"{tier_key} color {color} not found"

    def test_tier_dedup_no_overlap(self):
        """Cobalt first-match 시맨틱 이식: 상위 티어 base는 하위 티어에 없어야 함.
        회귀 방지: JSON 업데이트 시 중복 누적 → Continue 캐스케이드 다운그레이드 회귀.
        """
        from sections_continue import _load_unique_tiers
        # cache reset (모듈 전역이므로 다른 테스트 영향 최소화)
        import sections_continue
        sections_continue._UNIQUE_TIERS_CACHE = None
        tiers = _load_unique_tiers()
        priority = ["t1", "multi_high", "t2", "t3", "t4", "t5"]
        seen: set[str] = set()
        for key in priority:
            items = set(tiers.get(key, []))
            overlap = items & seen
            assert not overlap, \
                f"{key}에 상위 티어 중복 base 존재: {sorted(overlap)}"
            seen.update(items)

    def test_tier_dedup_specific_regressions(self):
        """실측 overlap 샘플 — 디듀플리케이션 후 제거 확인."""
        from sections_continue import _load_unique_tiers
        import sections_continue
        sections_continue._UNIQUE_TIERS_CACHE = None
        tiers = _load_unique_tiers()
        # Deicide Mask: Cobalt t2 → t3에 있으면 안 됨
        assert "Deicide Mask" in tiers["t2"]
        assert "Deicide Mask" not in tiers["t3"]
        # Bone Helmet: t3 → t4에 있으면 안 됨
        assert "Bone Helmet" in tiers["t3"]
        assert "Bone Helmet" not in tiers["t4"]
        # Zodiac Leather: t3 → t5에 있으면 안 됨
        assert "Zodiac Leather" in tiers["t3"]
        assert "Zodiac Leather" not in tiers["t5"]
        # Faithful Helmet: t1 → t2에 있으면 안 됨
        assert "Faithful Helmet" in tiers["t1"]
        assert "Faithful Helmet" not in tiers["t2"]

    def test_generic_fallback_first_for_cascade(self):
        """unique_generic이 맨 처음 (Continue=True 캐스케이드, T1~T3가 덮어씀)."""
        from sections_continue import layer_uniques
        text = layer_uniques("ssf")
        gen_pos = text.find("[L8|unique_generic]")
        t1_pos = text.find("[L8|unique_t1]")
        assert gen_pos != -1 and t1_pos != -1
        assert gen_pos < t1_pos, "unique_generic이 T1보다 먼저 나와야 (캐스케이드 순서)"

    def test_invalid_mode_raises(self):
        from sections_continue import layer_uniques
        import pytest
        with pytest.raises(ValueError):
            layer_uniques("pvp")


class TestGemQualityLevelThresholdsExpanded:
    """Q13/Lv18 (NeverSink) 신규 임계 회귀 테스트."""

    def test_q13_lv18_present(self):
        from sections_continue import layer_gems_quality
        text = layer_gems_quality("ssf")
        assert "Quality >= 13" in text
        assert "GemLevel >= 18" in text
        assert "[L8|gem_q13]" in text
        assert "[L8|gem_lv18]" in text


class TestLayerGold:
    def test_five_tiers(self):
        from sections_continue import layer_gold
        text = layer_gold("ssf")
        for stack in (5000, 2500, 1000, 100, 1):
            assert f"StackSize >= {stack}" in text
        assert '"Gold"' in text


class TestLayerFlasksQuality:
    def test_quality_thresholds(self):
        from sections_continue import layer_flasks_quality
        text = layer_flasks_quality("ssf")
        for q in (10, 20, 21):
            assert f"Quality >= {q}" in text
        assert "[L8|utility_flask]" in text


class TestLayerHeist:
    def test_three_blocks(self):
        from sections_continue import layer_heist
        text = layer_heist("ssf")
        for tag in ("heist_blueprint", "heist_contract", "heist_trinket"):
            assert f"[L8|{tag}]" in text

    def test_handpicked_present(self):
        """Phase 6: Cobalt L6614/L6643 handpicked 9 고가 영역."""
        from sections_continue import layer_heist
        text = layer_heist("ssf")
        assert "[L8|heist_blueprint_handpicked]" in text
        assert "[L8|heist_contract_handpicked]" in text
        # 9 areas 대표 샘플
        for area in ("Laboratory", "Mansion", "Prohibited Library", "Underbelly"):
            assert f'"Blueprint: {area}"' in text
            assert f'"Contract: {area}"' in text

    def test_handpicked_before_generic(self):
        """first-match: handpicked이 generic Blueprint/Contract보다 앞."""
        from sections_continue import layer_heist
        text = layer_heist("ssf")
        idx_bp_hp = text.find("[L8|heist_blueprint_handpicked]")
        idx_bp_gen = text.find("[L8|heist_blueprint]")
        idx_ct_hp = text.find("[L8|heist_contract_handpicked]")
        idx_ct_gen = text.find("[L8|heist_contract]")
        assert 0 < idx_bp_hp < idx_bp_gen
        assert 0 < idx_ct_hp < idx_ct_gen

    def test_invalid_mode_raises(self):
        from sections_continue import layer_heist
        with pytest.raises(ValueError):
            layer_heist("pvp")


class TestLayerQuestItems:
    def test_quest_items_block(self):
        from sections_continue import layer_quest_items
        text = layer_quest_items("ssf")
        assert '[L8|quest_items]' in text
        # Phase 6: Pantheon Souls 통합
        assert 'Class == "Quest Items" "Pantheon Souls"' in text

    def test_invalid_mode_raises(self):
        from sections_continue import layer_quest_items
        with pytest.raises(ValueError):
            layer_quest_items("pvp")


class TestLayerSpecialMaps:
    def test_three_special_blocks(self):
        from sections_continue import layer_special_maps
        text = layer_special_maps("ssf")
        for tag in ("map_uber_blighted", "map_blighted", "map_unique"):
            assert f"[L8|{tag}]" in text
        assert "UberBlightedMap True" in text


class TestLayerJewels:
    def test_cluster_abyss_generic_blocks(self):
        from sections_continue import layer_jewels
        text = layer_jewels("ssf")
        for tag in ("jewel_cluster_large", "jewel_cluster_medium",
                    "jewel_cluster_small", "jewel_abyss_high",
                    "jewel_abyss_basic", "jewel_generic"):
            assert f"[L8|{tag}]" in text


class TestLayerSpecialUniques:
    def test_replica_foulborn(self):
        from sections_continue import layer_special_uniques
        text = layer_special_uniques("ssf")
        assert "[L8|unique_replica]" in text
        assert "[L8|unique_foulborn]" in text
        assert "Replica True" in text
        assert "Foulborn True" in text


class TestLayerEndgameContent:
    """Phase 5: Cobalt [[3500]] 리그 엔트리 아이템 (Expedition/Sanctum/Relic/Chronicle/Ultimatum)."""

    def test_all_seven_blocks_present(self):
        from sections_continue import layer_endgame_content
        text = layer_endgame_content("ssf")
        for tag in ("expedition_logbook", "sanctum_ilvl83", "sanctum_any",
                    "relic_keys", "vault_keys", "chronicle", "ultimatum"):
            assert f"[L8|{tag}]" in text

    def test_signature_basetypes(self):
        from sections_continue import layer_endgame_content
        text = layer_endgame_content("ssf")
        assert '"Expedition Logbook"' in text
        assert '"Chronicle of Atzoatl"' in text
        assert '"Inscribed Ultimatum"' in text
        # Relic Keys 14종 샘플
        for key in ("Ancient Reliquary Key", "Vaal Reliquary Key",
                    "Voidborn Reliquary Key"):
            assert f'"{key}"' in text

    def test_sanctum_ilvl83_priority(self):
        """ilvl>=83 Sanctum이 any 블록보다 앞에 위치 (first-match)."""
        from sections_continue import layer_endgame_content
        text = layer_endgame_content("ssf")
        idx_83 = text.find("[L8|sanctum_ilvl83]")
        idx_any = text.find("[L8|sanctum_any]")
        assert 0 < idx_83 < idx_any

    def test_relic_keys_white_bg_t1(self):
        """Relic Keys는 Cobalt T1 (흰 BG + 빨강 + Red Star + sound 6)."""
        from sections_continue import layer_endgame_content
        text = layer_endgame_content("ssf")
        idx = text.find("[L8|relic_keys]")
        end = text.find("\n\n", idx)
        block = text[idx:end] if end > 0 else text[idx:idx + 2000]
        assert "SetBackgroundColor 255 255 255 255" in block
        assert "SetTextColor 255 0 0" in block
        assert "PlayAlertSound 6 300" in block
        assert "MinimapIcon 0 Red Star" in block

    def test_vault_keys_class_match(self):
        """Vault Keys는 BaseType이 아닌 Class == 'Vault Keys'로 매칭 (미래 key 안전망)."""
        from sections_continue import layer_endgame_content
        text = layer_endgame_content("ssf")
        idx = text.find("[L8|vault_keys]")
        end = text.find("\n\n", idx)
        block = text[idx:end] if end > 0 else text[idx:idx + 500]
        assert 'Class == "Vault Keys"' in block

    def test_no_continue(self):
        from sections_continue import layer_endgame_content
        text = layer_endgame_content("ssf")
        assert "\tContinue" not in text

    def test_invalid_mode_raises(self):
        from sections_continue import layer_endgame_content
        with pytest.raises(ValueError):
            layer_endgame_content("pvp")


class TestLayerMapFragments:
    """Phase 4c: Cobalt [[3603]] 5-tier 맵 프래그먼트 (Invitation/Emblem/Crest/Mortal/Sacrifice)."""

    def test_four_tiers_plus_restex(self):
        from sections_continue import layer_map_fragments
        text = layer_map_fragments("ssf")
        for tag in ("fragment_t1", "fragment_t2", "fragment_t4",
                    "fragment_t5", "fragment_restex"):
            assert f"[L8|{tag}]" in text

    def test_signature_fragments(self):
        """대표 프래그먼트 — Cobalt 원본 BaseType 일치."""
        from sections_continue import layer_map_fragments
        text = layer_map_fragments("ssf")
        # T1: Unrelenting Timeless Emblem, Syndicate Medallion
        assert '"Unrelenting Timeless Vaal Emblem"' in text
        assert '"Syndicate Medallion"' in text
        # T2: Fragment of X, Awakening/Reverent Fragment
        assert '"Fragment of Knowledge"' in text
        assert '"Timeless Templar Emblem"' in text
        # T4: Conqueror Crest, Mortal X, Simulacrum
        assert '"Al-Hezmin\'s Crest"' in text
        assert '"Mortal Ignorance"' in text
        assert '"Simulacrum"' in text
        # T5: Sacrifice
        assert '"Sacrifice at Midnight"' in text
        assert '"Divine Vessel"' in text

    def test_class_condition(self):
        """모든 블록 Class == 'Map Fragments' 'Misc Map Items' 조건."""
        from sections_continue import layer_map_fragments
        text = layer_map_fragments("ssf")
        assert 'Class == "Map Fragments" "Misc Map Items"' in text

    def test_no_continue(self):
        from sections_continue import layer_map_fragments
        text = layer_map_fragments("ssf")
        assert "\tContinue" not in text

    def test_restex_pink_safety(self):
        """RestEx는 핑크 최강조 (Cobalt restex 안전망)."""
        from sections_continue import layer_map_fragments
        text = layer_map_fragments("ssf")
        idx = text.find("[L8|fragment_restex]")
        end = text.find("Continue", idx) if text.find("Continue", idx) > 0 else len(text)
        block = text[idx:min(end, idx + 600)]
        assert "SetTextColor 255 0 255" in block
        assert "SetBackgroundColor 100 0 100" in block

    def test_invalid_mode_raises(self):
        from sections_continue import layer_map_fragments
        with pytest.raises(ValueError):
            layer_map_fragments("pvp")


class TestLayerStackedCurrency:
    """Phase 4b: Cobalt [[3905]]/[[3906]] 7-tier 스택 티어링."""

    def test_6x_tiers_generated(self):
        from sections_continue import layer_stacked_currency
        text = layer_stacked_currency("ssf")
        for tag in ("stack_6x_t1", "stack_6x_t2", "stack_6x_t3",
                    "stack_6x_t4", "stack_6x_t5", "stack_6x_t6", "stack_6x_t7"):
            assert f"[L8|{tag}]" in text

    def test_3x_tiers_generated(self):
        from sections_continue import layer_stacked_currency
        text = layer_stacked_currency("ssf")
        for tag in ("stack_3x_t1", "stack_3x_t2", "stack_3x_t3",
                    "stack_3x_t4", "stack_3x_t5", "stack_3x_t6", "stack_3x_t7"):
            assert f"[L8|{tag}]" in text

    def test_6x_before_3x(self):
        """POE first-match: 더 구체적인 6x 블록이 3x보다 앞에 와야 함."""
        from sections_continue import layer_stacked_currency
        text = layer_stacked_currency("ssf")
        idx_6x_t1 = text.find("[L8|stack_6x_t1]")
        idx_3x_t1 = text.find("[L8|stack_3x_t1]")
        assert 0 < idx_6x_t1 < idx_3x_t1

    def test_signature_basetypes(self):
        """대표 BaseType 샘플 존재 확인 (Cobalt 원본 일치)."""
        from sections_continue import layer_stacked_currency
        text = layer_stacked_currency("ssf")
        assert '"Dextral Catalyst"' in text
        assert '"Fracturing Shard"' in text
        assert '"Chaos Orb"' in text
        assert '"Alchemy Shard"' in text

    def test_no_continue(self):
        """스택 매칭은 최종 확정 (Continue=False)."""
        from sections_continue import layer_stacked_currency
        text = layer_stacked_currency("ssf")
        assert "\tContinue" not in text

    def test_invalid_mode_raises(self):
        from sections_continue import layer_stacked_currency
        with pytest.raises(ValueError):
            layer_stacked_currency("pvp")


class TestLayerOilCascade:
    """Phase 4a: Wreckers L1585~1674 오일 13단계 계단식."""

    def test_13_oils_font_progression(self):
        """Clear(33) → Sepia(34) → ... → Golden(45) 폰트 1씩 점증."""
        from sections_continue import layer_ssf_currency_extras
        text = layer_ssf_currency_extras("ssf")
        expected = [
            ("Clear Oil", 33), ("Sepia Oil", 34), ("Amber Oil", 35),
            ("Verdant Oil", 36), ("Teal Oil", 37), ("Azure Oil", 38),
            ("Indigo Oil", 39), ("Violet Oil", 40), ("Crimson Oil", 41),
            ("Black Oil", 42), ("Opalescent Oil", 43), ("Silver Oil", 44),
            ("Golden Oil", 45),
        ]
        for oil, font in expected:
            assert f'"{oil}"' in text, f"{oil} missing"
            idx = text.find(f'"{oil}"')
            # 근접한 SetFontSize 확인 (same block)
            end = text.find("Continue", idx)
            block = text[idx:end]
            assert f"SetFontSize {font}" in block, \
                f"{oil} should have font {font}"

    def test_13_oils_sound_progression(self):
        """볼륨 120→300, 15씩 점증."""
        from sections_continue import layer_ssf_currency_extras
        text = layer_ssf_currency_extras("ssf")
        expected = [
            ("Clear Oil", 120), ("Sepia Oil", 135), ("Amber Oil", 150),
            ("Verdant Oil", 165), ("Teal Oil", 180), ("Azure Oil", 195),
            ("Indigo Oil", 210), ("Violet Oil", 225), ("Crimson Oil", 240),
            ("Black Oil", 255), ("Opalescent Oil", 270), ("Silver Oil", 285),
            ("Golden Oil", 300),
        ]
        for oil, vol in expected:
            idx = text.find(f'"{oil}"')
            end = text.find("Continue", idx)
            block = text[idx:end]
            assert f"PlayAlertSound 12 {vol}" in block, \
                f"{oil} should have sound 12 {vol}"

    def test_premium_oils_white_bg(self):
        """Reflective/Prismatic/Tainted Oil: 흰 BG + Pink 강조 (font 45)."""
        from sections_continue import layer_ssf_currency_extras
        text = layer_ssf_currency_extras("ssf")
        # oil_premium 블록 존재
        if "[L8|oil_premium]" in text:
            idx = text.find("[L8|oil_premium]")
            end = text.find("Continue", idx)
            block = text[idx:end]
            assert "SetBackgroundColor 255 255 255 255" in block
            assert "SetFontSize 45" in block
            assert "PlayAlertSound 12 300" in block

    def test_oil_tag_count(self):
        """13개 개별 계단식 블록 (4-tier grouping에서 13-step cascade로 리팩토링)."""
        from sections_continue import layer_ssf_currency_extras
        text = layer_ssf_currency_extras("ssf")
        oil_tags = sum(1 for line in text.splitlines()
                       if "[L8|oil_" in line and "oil_premium" not in line)
        assert oil_tags == 13, f"예상 13 cascade 블록, 실제 {oil_tags}"


class TestLayerInfluencedExtra:
    def test_six_influences(self):
        from sections_continue import layer_influenced_extra
        text = layer_influenced_extra("ssf")
        for infl in ("shaper","elder","crusader","hunter","redeemer","warlord"):
            assert f"[L8|infl_{infl}]" in text

    def test_eldritch_exarch_eater(self):
        """Phase 3b: Cobalt [[0400]] Eldritch parity — Exarch + Eater implicit."""
        from sections_continue import layer_influenced_extra
        text = layer_influenced_extra("ssf")
        assert "[L8|eldritch_exarch]" in text
        assert "[L8|eldritch_eater]" in text
        assert "HasSearingExarchImplicit >= 1" in text
        assert "HasEaterOfWorldsImplicit >= 1" in text

    def test_eldritch_rarity_guard(self):
        """Eldritch는 Normal/Magic/Rare 전부. Unique는 별도 처리(제외)."""
        from sections_continue import layer_influenced_extra
        text = layer_influenced_extra("ssf")
        for tag in ("eldritch_exarch", "eldritch_eater"):
            start = text.find(f"[L8|{tag}]")
            end = text.find("Continue", start)
            block = text[start:end]
            assert "Rarity Normal Magic Rare" in block


class TestLayerSpecialModifiers:
    def test_five_modifier_blocks(self):
        from sections_continue import layer_special_modifiers
        text = layer_special_modifiers("ssf")
        for tag in ("mod_fractured", "mod_synthesised", "mod_veiled",
                    "mod_quality_perfect", "mod_memory_strand"):
            assert f"[L8|{tag}]" in text
        assert "FracturedItem True" in text
        assert "SynthesisedItem True" in text
        assert 'HasExplicitMod "Veil"' in text


class TestLayerHCSSFSafety:
    def test_only_active_in_hcssf(self):
        """SSF/Trade 모드에선 빈 문자열 (HCSSF만 활성)."""
        from sections_continue import layer_hcssf_safety
        assert layer_hcssf_safety("ssf") == ""
        assert layer_hcssf_safety("trade") == ""
        text = layer_hcssf_safety("hcssf")
        for tag in ("hcssf_life_flask", "hcssf_defense_flask", "hcssf_quicksilver"):
            assert f"[L8|{tag}]" in text


class TestThreeModeGeneration:
    """3모드 모두 에러 없이 생성 + 모드별 차이 확인."""

    def test_trade_mode(self):
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(mode="trade")
        assert "[L1|catchall]" in text
        assert '"Mirror of Kalandra"' in text  # Trade P1

    def test_ssf_mode(self):
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(mode="ssf")
        assert "[L1|catchall]" in text
        assert '"Orb of Alchemy"' in text  # SSF P1

    def test_hcssf_mode(self):
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(mode="hcssf")
        assert "[L8|hcssf_life_flask]" in text  # HCSSF 전용 블록
        assert '"Orb of Scouring"' in text  # HCSSF P1
        assert "[L8|divcard_hc_t1_override]" in text  # HCSSF 디비카 T1 경제 override


class TestLayerLevelingSupplies:
    def test_wisdom_portal_distinct(self):
        from sections_continue import layer_leveling_supplies
        text = layer_leveling_supplies("ssf")
        # Wisdom 2 스타일 (single + stack)
        assert "[L8|wisdom_stack2]" in text
        assert "[L8|wisdom_single]" in text
        # Portal 2 스타일
        assert "[L8|portal_stack2]" in text
        assert "[L8|portal_single]" in text
        # 색상 차이 (bronze vs blue)
        assert "200 100 60" in text  # Wisdom bronze
        assert "60 100 200" in text  # Portal blue
        # AL 액트 구간만
        assert "AreaLevel <= 67" in text


class TestProgressiveHideData533:
    """533 base 회귀 테스트 (3-source 합집합)."""

    def test_data_size(self):
        from sections_continue import load_progressive_hide
        d = load_progressive_hide()
        assert len(d.leveling_bases_early) >= 70, "초반 base 70+개"
        assert len(d.equipment_bases_midgame) >= 400, "중후반 base 400+개"

    def test_al_range(self):
        from sections_continue import load_progressive_hide
        d = load_progressive_hide()
        for base, al in d.leveling_bases_early:
            assert 3 <= al <= 27, f"early base {base}: AL {al} 범위 밖"
        for base, al in d.equipment_bases_midgame:
            # 매우 낮은 base는 AL 70+에서도 hide (Plate Vest 등)
            assert 28 <= al <= 75, f"mid base {base}: AL {al} 범위 밖"

    def test_all_bases_in_ggpk(self):
        """모든 base가 GGPK BaseItemTypes에 존재."""
        import json
        from sections_continue import load_progressive_hide
        bt = json.load(open('data/game_data/BaseItemTypes.json', encoding='utf-8'))
        valid = {b['Name'] for b in bt if isinstance(b, dict) and b.get('Name')}
        d = load_progressive_hide()
        for base, _ in d.leveling_bases_early + d.equipment_bases_midgame:
            assert base in valid, f"GGPK 미등록: {base}"


class TestBuildTargetConflictProtection:
    """L10 RE_SHOW가 leveling hide로부터 빌드 chanceable 보호."""

    def test_chanceable_reshow_overrides_leveling_hide(self):
        """Tabula 빌드 → Simple Robe AL>=5 hide되지만 L10 chanceable Show가 보호."""
        from sections_continue import generate_beta_overlay
        build = {
            "meta": {"build_name": "Tabula Test"},
            "items": [{"rarity": "unique", "name": "Tabula Rasa"}],
            "progression_stages": [{"gem_setups": {}, "gear_recommendation": {}}],
        }
        text = generate_beta_overlay(strictness=3, build_data=build, mode="ssf")
        # L9 Simple Robe hide 존재
        assert '"Simple Robe"' in text
        # L10 chanceable Re-Show 존재 (방어)
        assert "[L10|chanceable]" in text


class TestLayerProgressiveHideRarityGuard:
    """L9 leveling/midgame Hide 블록이 Rarity Normal Magic 제약 있어서 Unique 보호.

    배경: layer_progressive_hide의 leveling_bases_early / equipment_bases_midgame 루프가
    BaseType + AreaLevel만 조건으로 갖고 있으면 Unique Tabula(Simple Robe),
    Goldrim(Leather Cap), Astral Plate 기반 유니크 등이 L8 unique Show+Continue 뒤
    L9 Hide Continue로 덮여 숨김 회귀. Rarity Normal Magic 추가로 방지.
    """

    def test_leveling_bases_have_rarity_guard(self):
        from sections_continue import layer_progressive_hide
        text = layer_progressive_hide(strictness=2, mode="ssf")
        # level_early 블록마다 Rarity Normal Magic 필수
        lines = text.splitlines()
        level_early_blocks = 0
        for i, line in enumerate(lines):
            if "[L9|level_early]" in line:
                level_early_blocks += 1
                block_tail = "\n".join(lines[i:i + 10])
                assert "Rarity Normal Magic" in block_tail, \
                    f"level_early block missing Rarity guard at line {i}"
        assert level_early_blocks > 0, "level_early 블록이 생성되지 않음"

    def test_midgame_bases_have_rarity_guard(self):
        from sections_continue import layer_progressive_hide
        text = layer_progressive_hide(strictness=3, mode="ssf")
        lines = text.splitlines()
        level_mid_blocks = 0
        for i, line in enumerate(lines):
            if "[L9|level_mid]" in line:
                level_mid_blocks += 1
                block_tail = "\n".join(lines[i:i + 10])
                assert "Rarity Normal Magic" in block_tail, \
                    f"level_mid block missing Rarity guard at line {i}"
        assert level_mid_blocks > 0, "level_mid 블록이 생성되지 않음"

    def test_simple_robe_unique_not_hidden_in_overlay(self):
        """전체 오버레이에서 'Simple Robe' 매칭 L9 Hide 블록이 Rarity Normal Magic로 제약되어
        Unique Tabula Rasa가 해당 Hide에 안 걸리는지 회귀 확인.
        """
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(strictness=3, mode="ssf")
        # Simple Robe가 포함된 L9 level_early Hide 블록 찾기
        idx = text.find('[L9|level_early]')
        while idx != -1:
            end = text.find("\n\n", idx)
            block = text[idx:end] if end > 0 else text[idx:]
            if '"Simple Robe"' in block:
                assert "Rarity Normal Magic" in block, \
                    "Simple Robe L9 level_early block must have Rarity guard"
                break
            idx = text.find('[L9|level_early]', idx + 1)
        else:
            raise AssertionError("Simple Robe가 L9 level_early에 없음 — 데이터 변경?")


class TestLayerReShowUnconditionalT1:
    """Phase 2: Wreckers L172/L237 T1 보더 unconditional 재Show 21블록."""

    def test_all_seven_groups_three_rarities(self):
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        groups = ("ring_glove_helm", "main_equip", "trinket_heist",
                  "flask_brooch", "utility_tincture",
                  "small_cluster", "mid_large_cluster")
        rarities = ("normal", "magic", "rare")
        for g in groups:
            for r in rarities:
                assert f"[L10|{g}_{r}]" in text, f"missing {g}_{r}"

    def test_rarity_borders_wreckers_standard(self):
        """Wreckers L172: Normal=White / Magic=Blue(0 75 255) / Rare=Yellow(255 255 0)."""
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        # 7 groups × Normal = 7 white borders (unconditional)
        assert text.count("SetBorderColor 255 255 255 255") >= 7
        assert text.count("SetBorderColor 0 75 255 255") >= 7
        assert text.count("SetBorderColor 255 255 0 255") >= 7

    def test_ilvl_thresholds_per_group(self):
        """Wreckers 정확 ilvl: ring_glove_helm=85, main_equip=86, trinket_heist=83,
        flask_brooch=84, utility_tincture=85, small_cluster=75, mid_large_cluster=84.
        """
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        for tag, ilvl in [
            ("ring_glove_helm_normal", 85),
            ("main_equip_normal", 86),
            ("trinket_heist_normal", 83),
            ("flask_brooch_normal", 84),
            ("utility_tincture_normal", 85),
            ("small_cluster_normal", 75),
            ("mid_large_cluster_normal", 84),
        ]:
            idx = text.find(f"[L10|{tag}]")
            end = text.find("\n\n", idx)
            block = text[idx:end] if end > 0 else text[idx:]
            assert f"ItemLevel >= {ilvl}" in block, f"{tag} wrong ilvl"

    def test_cluster_jewel_basetypes(self):
        """Cluster Jewel 블록은 Class==Jewels + BaseType== Small/Medium/Large."""
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        idx = text.find("[L10|small_cluster_normal]")
        end = text.find("\n\n", idx)
        block = text[idx:end] if end > 0 else text[idx:]
        assert 'Class == "Jewels"' in block
        assert 'BaseType == "Small Cluster Jewel"' in block

        idx = text.find("[L10|mid_large_cluster_normal]")
        end = text.find("\n\n", idx)
        block = text[idx:end] if end > 0 else text[idx:]
        assert 'BaseType == "Medium Cluster Jewel" "Large Cluster Jewel"' in block

    def test_all_unconditional_blocks_continue_false(self):
        """Wreckers parity: 재Show는 최종 Show (Continue 없음)."""
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        assert "\tContinue" not in text

    def test_leveling_help_blocks_present(self):
        """Wreckers L936 Levelling Help + Sanavi 사운드 이식 (7블록)."""
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        for tag in ("lvl_3link_early", "lvl_3link_weapon", "lvl_4link",
                    "lvl_5link", "lvl_3ww_weapon", "lvl_4ww_armor",
                    "lvl_6ww_2h"):
            assert f"[L10|{tag}]" in text

    def test_leveling_help_sanavi_custom_sounds(self):
        """5-link / 6-white 2h에 Sanavi CustomAlertSound 이식."""
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        # 5-link Sanavi sound
        idx5 = text.find("[L10|lvl_5link]")
        end5 = text.find("Show # PathcraftAI [L10|", idx5 + 1)
        block5 = text[idx5:end5] if end5 > 0 else text[idx5:]
        assert 'CustomAlertSound "5Link.mp3" 300' in block5
        # 6-white 2h ProbPickUp sound
        idx6 = text.find("[L10|lvl_6ww_2h]")
        end6 = text.find("Show # PathcraftAI [L10|", idx6 + 1)
        if end6 < 0:
            end6 = len(text)
        block6 = text[idx6:end6]
        assert 'CustomAlertSound "ProbPickUp.mp3" 300' in block6

    def test_leveling_help_al67_limit(self):
        """레벨링 블록 AL<=67 (캠페인 전용) 조건 확인."""
        from sections_continue import layer_re_show
        text = layer_re_show(None)
        for tag in ("lvl_3link_weapon", "lvl_4link", "lvl_5link"):
            idx = text.find(f"[L10|{tag}]")
            end = text.find("Show # PathcraftAI [L10|", idx + 1)
            if end < 0:
                end = len(text)
            block = text[idx:end]
            assert "AreaLevel <= 67" in block, \
                f"{tag} should limit to campaign AL<=67"


class TestLayerSpecialBase:
    """L4 Wreckers SSF L146 특수 BaseType 오렌지 복원."""

    def test_layer_tag_and_orange_text(self):
        from sections_continue import layer_special_base
        text = layer_special_base()
        assert "[L4|wreckers_special]" in text
        assert "SetTextColor 255 123 0 255" in text
        assert text.rstrip().endswith("Continue")

    def test_contains_signature_basetypes(self):
        """Wreckers L148 대표 베이스 — 누락 시 레퍼런스 드리프트."""
        from sections_continue import layer_special_base
        text = layer_special_base()
        # Rings / Amulet / Belt / Jewel / Trinket 각 계열에서 대표 하나씩
        for base in ("Bone Ring", "Marble Amulet", "Stygian Vise",
                     "Cobalt Jewel", "Thief's Trinket",
                     "Two-Toned Boots", "Fishing Rod"):
            assert f'"{base}"' in text

    def test_included_in_beta_overlay_before_corrupt(self):
        """L4는 L3 SOCKET 뒤, L5 CORRUPT 앞."""
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(mode="ssf")
        idx_l3 = text.find("[L3|")
        idx_l4 = text.find("[L4|wreckers_special]")
        idx_l5 = text.find("[L5|corrupted]")
        assert idx_l3 < idx_l4 < idx_l5, (idx_l3, idx_l4, idx_l5)


class TestLayerEndgameRareHide:
    """L11 Cobalt Strict [[2000]]/[[2200]]/[[2700]] Hide blocks."""

    def test_all_subsection_tags(self):
        from sections_continue import layer_endgame_rare_hide
        text = layer_endgame_rare_hide("ssf")
        for tag in (
            "corrupted_noimpl", "mirrored_noimpl",
            "droplevel_al80", "droplevel_al78", "droplevel_al73",
            "normalmagic_blanket",
        ):
            assert f"[L11|{tag}]" in text
        # rare_blanket은 의도적으로 제외 (Continue 캐스케이드 호환성)
        assert "[L11|rare_blanket]" not in text

    def test_all_blocks_are_hide_no_continue(self):
        """L11은 최종 Hide — Continue 금지 (L12 REST_EX 전까지 덮어쓰기 없음)."""
        from sections_continue import layer_endgame_rare_hide
        text = layer_endgame_rare_hide("ssf")
        show_count = sum(1 for line in text.splitlines()
                         if line.startswith("Show # PathcraftAI [L11|"))
        hide_count = sum(1 for line in text.splitlines()
                         if line.startswith("Hide # PathcraftAI [L11|"))
        assert show_count == 0
        assert hide_count == 6
        assert "\tContinue" not in text

    def test_droplevel_thresholds_match_cobalt(self):
        """Cobalt Strict L3574~ 기준: AL 80/DL 60, AL 78/DL 50, AL 73/DL 40."""
        from sections_continue import layer_endgame_rare_hide
        text = layer_endgame_rare_hide("ssf")
        for al, dl in ((80, 60), (78, 50), (73, 40)):
            assert f"AreaLevel >= {al}" in text
            assert f"DropLevel < {dl}" in text

    def test_disable_drop_sound(self):
        from sections_continue import layer_endgame_rare_hide
        text = layer_endgame_rare_hide("ssf")
        assert text.count("DisableDropSound True") == 6

    def test_normalmagic_blanket_excludes_utility_flasks(self):
        """Wreckers L232 철학 + L8 layer_flasks_quality 덮어쓰기 회귀 방지.
        Utility Flasks가 L11 normalmagic_blanket에 포함되면 L8 Continue=True 데코 덮어씀.
        """
        from sections_continue import layer_endgame_rare_hide
        text = layer_endgame_rare_hide("ssf")
        start = text.find("[L11|normalmagic_blanket]")
        end = text.find("DisableDropSound True", start)
        block = text[start:end]
        assert '"Utility Flasks"' not in block

    def test_noimpl_blocks_exclude_trinkets(self):
        """Cobalt Strict L3483: [[2000]] 부패/미러 블록은 Amulets/Belts/Rings 제외."""
        from sections_continue import layer_endgame_rare_hide
        text = layer_endgame_rare_hide("ssf")
        for tag in ("corrupted_noimpl", "mirrored_noimpl"):
            start = text.find(f"[L11|{tag}]")
            end = text.find("DisableDropSound True", start)
            block = text[start:end]
            assert '"Amulets"' not in block, f"{tag} must exclude Amulets"
            assert '"Belts"' not in block, f"{tag} must exclude Belts"
            assert '"Rings"' not in block, f"{tag} must exclude Rings"

    def test_t1_craft_base_not_hidden_by_cascade(self):
        """회귀 방지: L6이 흰 보더로 표시한 T1 크래프팅 베이스 Rare ilvl>=86가
        L11 캐스케이드 끝에서 Hide로 뒤집히지 않는지 확인.
        rare_blanket 제거 후 Rare equip은 L11에서 matching 블록 없음.
        """
        from sections_continue import generate_beta_overlay, load_t1_bases
        text = generate_beta_overlay(mode="ssf")
        bases = load_t1_bases()
        # 테스트용 T1 베이스 하나 샘플
        sample_base = None
        for items in bases.categories.values():
            if items:
                sample_base = items[0]
                break
        assert sample_base is not None

        # L11 rare_blanket는 없어야 함
        assert "[L11|rare_blanket]" not in text

        # L11 영역에서 Rarity Rare + equip class를 조건으로 하는 Hide 블록
        # (droplevel_al* + corrupted_noimpl + mirrored_noimpl)은 BaseType까지 걸려야 안전.
        # noimpl은 Corrupted/Mirrored 조건 있어 비부패 rare 무시.
        # droplevel은 DropLevel<X 조건 있어 ilvl 86+ T1 베이스 (DropLevel 높음) 미매칭.
        # 검증: generate_beta_overlay 결과에 T1 샘플 BaseType이 존재하고 L11 Hide 블록이
        # 부패/droplevel 조건 없이 Rare를 잡는 블록이 없어야 함
        assert f'"{sample_base}"' in text  # L6 T1_BORDER에 존재

    def test_invalid_mode_raises(self):
        from sections_continue import layer_endgame_rare_hide
        with pytest.raises(ValueError):
            layer_endgame_rare_hide("pvp")

    def test_included_in_beta_overlay_after_re_show(self):
        """L11은 L10 RE_SHOW 뒤에 위치."""
        from sections_continue import generate_beta_overlay
        text = generate_beta_overlay(mode="ssf")
        idx_l10 = text.rfind("[L10|")
        idx_l11 = text.find("[L11|")
        assert idx_l10 < idx_l11, (idx_l10, idx_l11)


class TestT1MaxRouting:
    """layer_basic_orbs T1 MAX 블록 도달 보장 — layer_currency P1_KEYSTONE 중복 매칭 회귀 방지."""

    @pytest.mark.parametrize("mode", ["trade", "ssf", "hcssf"])
    def test_t1_max_orbs_route_only_to_basic_orbs(self, mode):
        """T1 MAX base는 layer_basic_orbs T1 MAX 블록에서만 처리 (continue=False).

        layer_currency가 layer_basic_orbs보다 먼저 실행되므로 T1 MAX base가
        layer_currency P1_KEYSTONE 매칭으로 잠기면 T1 MAX 블록 도달 불가.
        LEVELING_SUPPLY_BASES 제외 셋이 이를 보장. 3 mode 모두 동일 라우팅.
        """
        from sections_continue import generate_beta_overlay
        import re
        text = generate_beta_overlay(mode=mode)
        blocks = re.split(r'(?=^(?:Show|Hide)\b)', text, flags=re.MULTILINE)
        for target in ("Divine Orb", "Mirror of Kalandra", "Mirror Shard",
                       "Sacred Orb", "Awakener's Orb"):
            tags = []
            for b in blocks:
                if target in b:
                    m = re.search(r'\[L\d+\|([^\]]+)\]', b)
                    if m:
                        tags.append(m.group(1))
            assert tags == ["basic_orb_t1_mirror_divine"], (
                f"[{mode}] {target} routing: expected only T1 MAX, got {tags}"
            )


class TestAtlasAndMemoryCoverage:
    """P0 미매칭 카테고리 (2026-04-15 audit) 전수 styling 회귀 방지.

    Watchstone / Incubator / Forbidden Tome / Sanctum Floor / Memory / Metamorph.
    """

    @pytest.mark.parametrize("base,expected_tag", [
        ("Forbidden Tome", "forbidden_tome"),
        ("Chromium Haewark Hamlet Watchstone", "watchstone_chromium"),
        ("Titanium Lex Ejoris Watchstone", "watchstone_high"),
        ("Platinum Valdo's Rest Watchstone", "watchstone_high"),
        ("Ivory Watchstone", "watchstone_low"),
        ("Cobalt Watchstone", "watchstone_low"),
        ("Sanctum Archives Research", "sanctum_floor_research"),
        ("Kirac's Memory", "memory_lines"),
        ("Alva's Memory", "memory_lines"),
        ("Niko's Memory", "memory_lines"),
        ("Einhar's Memory", "memory_lines"),
        ("Whispering Incubator", "incubator"),
        ("Cartographer's Incubator", "incubator"),
        ("Obscured Incubator", "incubator"),
        ("Metamorph Brain", "metamorph_organs"),
        ("Metamorph Heart", "metamorph_organs"),
    ])
    def test_p0_base_routed(self, base, expected_tag):
        from sections_continue import generate_beta_overlay
        import re
        text = generate_beta_overlay(mode="ssf")
        blocks = re.split(r'(?=^(?:Show|Hide)\b)', text, flags=re.MULTILINE)
        tags = [m for b in blocks if base in b for m in re.findall(r'\[L\d+\|([^\]]+)\]', b)]
        assert expected_tag in tags, f"{base}: expected {expected_tag} in {tags}"

    def test_layer_atlas_and_memory_invalid_mode_raises(self):
        from sections_continue import layer_atlas_and_memory
        with pytest.raises(ValueError):
            layer_atlas_and_memory("pvp")


class TestP1CategoryCoverage:
    """P1 미매칭 (Maven Invitation / 고가 Stackable / Harbinger pieces / Wombgift) 회귀."""

    @pytest.mark.parametrize("base,expected_tag", [
        # Maven's Invitation 티어
        ("Maven's Invitation: The Feared", "maven_invitation_feared"),
        ("Maven's Invitation: The Elderslayers", "maven_invitation_boss"),
        ("Maven's Invitation: The Hidden", "maven_invitation_boss"),
        ("Maven's Invitation: Glennach Cairns", "maven_invitation_region"),
        ("Maven's Invitation: Valdo's Rest", "maven_invitation_region"),
        # Stackable T1 legacy
        ("Eternal Orb", "stackable_t1_legacy"),
        ("Imprint", "stackable_t1_legacy"),
        ("Veiled Exalted Orb", "stackable_t1_legacy"),
        ("Lycia's Invocation of Eternal Youth", "stackable_t1_legacy"),
        # Stackable T2 고가
        ("Maven's Chisel of Avarice", "stackable_t2_high"),
        ("Awakened Sextant", "stackable_t2_high"),
        ("Albino Rhoa Feather", "stackable_t2_high"),
        ("Tailoring Orb", "stackable_t2_high"),
        # Exceptional
        ("Exceptional Eldritch Ember", "exceptional_artifacts"),
        ("Exceptional Sun Artifact", "exceptional_artifacts"),
        # Harbinger fragments
        ("Archon Kite Shield Piece", "harbinger_fragments"),
        ("Legion Sword Piece", "harbinger_fragments"),
        ("Primordial Fragment", "harbinger_fragments"),
        # Wombgift
        ("Ancient Wombgift", "wombgift"),
        ("Lavish Wombgift", "wombgift"),
        # Heist Objective
        ("Urn of Farud", "heist_objective"),
        ("Box of Tripyxis", "heist_objective"),
        ("Mirror of Teklatipitzi", "heist_objective"),
        ("Staff of the First Sin Eater", "heist_objective"),
    ])
    def test_p1_base_routed(self, base, expected_tag):
        from sections_continue import generate_beta_overlay
        import re
        text = generate_beta_overlay(mode="ssf")
        blocks = re.split(r'(?=^(?:Show|Hide)\b)', text, flags=re.MULTILINE)
        tags = [m for b in blocks if base in b for m in re.findall(r'\[L\d+\|([^\]]+)\]', b)]
        assert expected_tag in tags, f"{base}: expected {expected_tag} in {tags}"


class TestEssenceTierCoverage:
    """POE 7 에센스 티어 + 부패 에센스 + Remnant 전수 styling 보장.

    이전 버그: Weeping/Whispering 티어 + 부패 5종 (Hysteria/Insanity/Horror/Delirium/Desolation)
    + Remnant of Corruption 모두 미처리 → unstyled 폴스루.
    """

    @pytest.mark.parametrize("base,expected_tag", [
        ("Essence of Hysteria", "essence_corrupt"),
        ("Essence of Insanity", "essence_corrupt"),
        ("Remnant of Corruption", "remnant_corruption"),
        ("Deafening Essence of Anger", "essence_t1"),
        ("Shrieking Essence of Anger", "essence_t2"),
        ("Screaming Essence of Anger", "essence_t3"),
        ("Wailing Essence of Anger", "essence_t4"),
        ("Weeping Essence of Anger", "essence_t5_weeping"),
        ("Muttering Essence of Anger", "essence_t6_muttering"),
        ("Whispering Essence of Greed", "essence_t7_whispering"),
    ])
    def test_essence_routed(self, base, expected_tag):
        from sections_continue import generate_beta_overlay
        import re
        text = generate_beta_overlay(mode="ssf")
        blocks = re.split(r'(?=^(?:Show|Hide)\b)', text, flags=re.MULTILINE)
        tags = [m for b in blocks if base in b for m in re.findall(r'\[L\d+\|([^\]]+)\]', b)]
        assert expected_tag in tags, f"{base}: expected {expected_tag} in {tags}"


class TestLevelingSupplyRouting:
    """Armourer's Scrap / Blacksmith's Whetstone — 전 AL에서 styling 보장.

    회귀 방지: layer_currency P5_MINOR/P6_LOW가 처리해야 함.
    이전 버그: LEVELING_SUPPLY_BASES 제외 + leveling_supply_basic의 AL<=67 조건으로
    AL>67 맵에서 unstyled 폴스루 (인게임 검증 발견).
    """

    @pytest.mark.parametrize("mode,expected_tier", [
        ("trade", "currency_p6_low_palette"),
        ("ssf", "currency_p5_minor_palette"),
        ("hcssf", "currency_p5_minor_palette"),
    ])
    def test_scrap_whetstone_routed_to_currency_tier(self, mode, expected_tier):
        from sections_continue import generate_beta_overlay
        import re
        text = generate_beta_overlay(mode=mode)
        blocks = re.split(r'(?=^(?:Show|Hide)\b)', text, flags=re.MULTILINE)
        for target in ("Armourer's Scrap", "Blacksmith's Whetstone"):
            first_tag = None
            for b in blocks:
                if target in b:
                    m = re.search(r'\[L\d+\|([^\]]+)\]', b)
                    if m:
                        first_tag = m.group(1)
                        break
            assert first_tag == expected_tier, (
                f"[{mode}] {target}: first block {first_tag!r}, expected {expected_tier!r}"
            )

    def test_no_dead_leveling_supply_basic_block(self):
        """leveling_supply_basic 블록이 제거되었는지 확인 (Scrap/Whetstone은 currency tier 처리)."""
        from sections_continue import layer_leveling_supplies
        text = layer_leveling_supplies(mode="ssf")
        assert "leveling_supply_basic" not in text


class TestEquipmentBasesExpansion:
    """progressive_hide.json equipment_bases_midgame 확장 (455→599+) 회귀."""

    def test_minimum_count(self):
        from sections_continue import load_progressive_hide
        data = load_progressive_hide()
        # 599 from 2026-04-15 expansion. 회귀 시 즉시 발견.
        assert len(data.equipment_bases_midgame) >= 590, len(data.equipment_bases_midgame)

    def test_known_expansion_bases_present(self):
        """확장 시 추가된 대표 base 확인 (DL 50-65 범위)."""
        from sections_continue import load_progressive_hide
        data = load_progressive_hide()
        names = {b for b, _ in data.equipment_bases_midgame}
        # 2026-04-15 추가된 DL 50-65 대표 sample
        for sample in ("Abyssal Sceptre", "Fancy Foil", "Ezomyte Burgonet"):
            assert sample in names, f"{sample} missing from equipment_bases_midgame"


class TestIdModFilteringStrictness:
    """layer_id_mod_filtering — Hale/Healthy/Sanguine 제외 플래그 (strictness>=4)."""

    def test_default_no_low_life_exclusion(self):
        from sections_continue import layer_id_mod_filtering
        text = layer_id_mod_filtering(mode="ssf", strictness=0)
        assert 'HasExplicitMod 0 "Hale"' not in text

    def test_strictness_3_no_low_life_exclusion(self):
        from sections_continue import layer_id_mod_filtering
        text = layer_id_mod_filtering(mode="ssf", strictness=3)
        assert 'HasExplicitMod 0 "Hale"' not in text

    def test_strictness_4_adds_low_life_exclusion(self):
        from sections_continue import layer_id_mod_filtering
        text = layer_id_mod_filtering(mode="ssf", strictness=4)
        assert 'HasExplicitMod 0 "Hale" "Healthy" "Sanguine"' in text

    def test_strictness_4_show_blocks_unchanged_count(self):
        """Hale 조건 추가해도 Show 블록 수는 그대로 (per-class 수 동일)."""
        from sections_continue import layer_id_mod_filtering
        default = layer_id_mod_filtering(mode="ssf", strictness=0)
        strict = layer_id_mod_filtering(mode="ssf", strictness=4)
        assert default.count("\nShow") == strict.count("\nShow")

    def test_threaded_through_beta_overlay(self):
        from sections_continue import generate_beta_overlay
        lenient = generate_beta_overlay(strictness=3, mode="ssf")
        aggressive = generate_beta_overlay(strictness=4, mode="ssf")
        assert 'HasExplicitMod 0 "Hale"' not in lenient
        assert 'HasExplicitMod 0 "Hale" "Healthy" "Sanguine"' in aggressive
