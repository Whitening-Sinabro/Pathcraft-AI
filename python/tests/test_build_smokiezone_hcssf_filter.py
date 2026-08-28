import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_smokiezone_hcssf_filter as filter_builder  # noqa: E402
import filter_cascade  # noqa: E402


SPEC_PATH = (
    ROOT
    / "data"
    / "filter_build_targets"
    / "poe1_smokiezone_hydrosphere_boneshatter_hcssf_3_29.json"
)
ECONOMY_PATH = (
    ROOT / "data" / "filter_sources" / "neversink_poe1_8_20_1d_903189_economy.json"
)
BASE_FILTER = ROOT / "filters" / "Luminary_Bot_SSF_3.29_Progressive.filter"


def load_spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def crafting_group(spec, group_id):
    return next(
        group for group in spec["crafting_base_groups"] if group["id"] == group_id
    )


def one_block(blocks, marker):
    matches = [block for block in blocks if marker in block.header]
    assert len(matches) == 1
    return matches[0]


def test_researched_endgame_base_tiers_match_the_creator_sources():
    spec = load_spec()

    vaal_axe = crafting_group(spec, "build.weapon.endgame_vaal_axe")
    assert vaal_axe["base_types"] == ["Vaal Axe"]
    assert vaal_axe["minimum_item_level"] == 83
    assert vaal_axe["always_show"] is True

    armour = crafting_group(spec, "build.armour.optimal_breach_bases")
    assert armour["base_types"] == [
        "Royal Plate",
        "Giantslayer Helmet",
        "Leviathan Gauntlets",
        "Leviathan Greaves",
    ]
    assert armour["minimum_item_level"] == 84
    assert armour["always_show"] is True

    jewellery = crafting_group(spec, "build.jewellery.endgame_crafting")
    assert jewellery["base_types"] == ["Amethyst Ring", "Turquoise Amulet"]
    assert jewellery["minimum_item_level"] == 83
    assert jewellery["always_show"] is True


def test_optimal_armour_bases_are_the_drop_level_84_strength_tier():
    base_items = json.loads(
        (ROOT / "data" / "game_data" / "BaseItemTypes.json").read_text(encoding="utf-8")
    )
    armour_types = json.loads(
        (ROOT / "data" / "game_data" / "ArmourTypes.json").read_text(encoding="utf-8")
    )
    expected_max_armour = {
        "Royal Plate": 1360,
        "Giantslayer Helmet": 669,
        "Leviathan Gauntlets": 413,
        "Leviathan Greaves": 413,
    }
    observed = {}
    for armour in armour_types:
        base = base_items[armour["BaseItemTypesKey"]]
        if base.get("Name") in expected_max_armour:
            observed[base["Name"]] = {
                "drop_level": base["DropLevel"],
                "armour_max": armour["ArmourMax"],
                "evasion_max": armour["EvasionMax"],
                "energy_shield_max": armour["EnergyShieldMax"],
            }

    assert set(observed) == set(expected_max_armour)
    for name, armour_max in expected_max_armour.items():
        assert observed[name] == {
            "drop_level": 84,
            "armour_max": armour_max,
            "evasion_max": 0,
            "energy_shield_max": 0,
        }


def test_approved_crafting_bases_render_as_terminal_pre_visibility_shows():
    spec = load_spec()
    palette = filter_builder.derive_palette(spec["theme"]["main_color"])
    lines = filter_builder.render_crafting_bases(spec, palette, "Purple")
    blocks = filter_builder.parse_blocks(lines)

    for group in spec["crafting_base_groups"]:
        if not group.get("always_show"):
            continue
        marker = f"SMOKIEZONE - {group['id'].upper()}"
        matches = [block for block in blocks if marker in block.header]
        assert len(matches) == 1
        block = matches[0]
        assert block.action == "Show"
        assert "Continue" not in block.directives
        assert not any(line.startswith("AreaLevel <=") for line in block.directives)
        assert not any(line.startswith("SetTextColor") for line in block.directives)
        assert "SetBorderColor 124 58 237 255" in block.directives
        assert any(
            line.startswith("SetBackgroundColor 37 17 71 ") for line in block.directives
        )


def test_area_level_83_does_not_force_every_rare_equipment_drop_to_show():
    spec = load_spec()
    palette = filter_builder.derive_palette(spec["theme"]["main_color"])
    text = "\n".join(
        filter_builder.render_hcssf_safety(palette, "Purple", spec["progression"])
    )

    assert "RARE ARMOUR AND JEWELLERY THROUGH RED MAPS" in text
    assert "RARE TWO HAND AXES THROUGH RED MAPS" in text
    assert "RARE ARMOUR AND JEWELLERY IN ENDGAME" not in text
    assert "RARE TWO HAND AXES IN ENDGAME" not in text
    assert "SetTextColor 255 255 119 255" in text
    assert "PlayEffect None" in text


def test_text_guard_only_recolours_gems():
    """Text-only rarity guards after the decorators made unique labels unreadable."""
    blocks = filter_builder.parse_blocks(filter_builder.render_rarity_guard())

    assert [block.header for block in blocks] == [
        "Show # SMOKIEZONE - NATIVE GEM TEXT GUARD"
    ]
    gem_guard = blocks[0]
    assert "SetTextColor 27 217 217 255" in gem_guard.directives
    assert "Continue" in gem_guard.directives
    assert not any("SetBackgroundColor" in line for line in gem_guard.directives)


def test_sentinel_decorators_are_neutralised_not_guarded():
    source_lines = BASE_FILTER.read_text(encoding="utf-8").splitlines()
    source_blocks = filter_builder.parse_blocks(source_lines)
    sentinel_headers = [
        block.header
        for block in source_blocks
        if tuple(block.directives) == filter_builder.SENTINEL_STYLE
    ]
    assert sentinel_headers, "the Death Oath source should carry the magenta reset"

    lines = filter_builder.neutralise_sentinel_decorators(list(source_lines))
    blocks = filter_builder.parse_blocks(lines)

    assert not any(tuple(block.directives) == filter_builder.SENTINEL_STYLE for block in blocks)
    default = one_block(blocks, filter_builder.ORDINARY_UNIQUE_DEFAULT)
    assert default.directives == (
        "Rarity Unique",
        "SetTextColor 175 96 37 255",
        "SetBorderColor 175 96 37 255",
        "SetBackgroundColor 20 20 0 255",
        "Continue",
    )
    unique_tier_blocks = [
        block
        for block in blocks
        if block.header.startswith("Show # Pathcraft Death Oath visual rule")
        and "Rarity Unique" in block.directives
        and any(line.startswith("BaseType") for line in block.directives)
    ]
    assert default.start_line < unique_tier_blocks[0].start_line


def test_unique_crude_bow_label_is_readable_after_cascade():
    """Regression: black-on-brown unique tier + brown text guard rendered text == background."""
    spec = load_spec()
    economy = json.loads(ECONOMY_PATH.read_text(encoding="utf-8"))
    output, _ = filter_builder.compose_filter(spec, economy)
    blocks = filter_cascade.parse_cascade(output.splitlines())

    probes = [
        filter_cascade.SimulatedItem("Crude Bow", "Bows", "Unique", 5, 5, sockets=2),
        filter_cascade.SimulatedItem("Onyx Amulet", "Amulets", "Unique", 45, 45),
        filter_cascade.SimulatedItem("Royal Plate", "Body Armours", "Unique", 85, 85),
        filter_cascade.SimulatedItem(
            "Gold Amulet", "Amulets", "Magic", 3, 3, linked_sockets=0, sockets=6
        ),
        filter_cascade.SimulatedItem("Iron Flask", "Utility Flasks", "Rare", 85, 85),
    ]
    for item in probes:
        result = filter_cascade.simulate(blocks, item)
        assert result.action == "Show", item
        text = result.colour("SetTextColor")
        background = result.colour("SetBackgroundColor")
        assert text is not None and background is not None, item
        assert text[:3] != background[:3], (item, result.chain[-4:])
        assert filter_cascade.contrast_ratio(text, background) >= 2.0, (
            item,
            text,
            background,
            result.chain[-4:],
        )


def test_essence_visual_ladder_partitions_all_current_currency_bases():
    buckets = filter_builder.extract_essence_buckets()
    flattened = [name for names in buckets.values() for name in names]

    assert len(flattened) == 106
    assert len(flattened) == len(set(flattened))
    assert "Essence of Insanity" in buckets["high"]
    assert "Essence of Desolation" in buckets["high"]
    assert "Deafening Essence of Woe" in buckets["high"]
    assert "Shrieking Essence of Woe" in buckets["important"]
    assert "Screaming Essence of Woe" in buckets["routine"]
    assert "Wailing Essence of Woe" in buckets["routine"]
    assert "Whispering Essence of Woe" in buckets["quiet"]


def test_essence_ladder_replaces_only_colours_and_precedes_build_overrides():
    spec = load_spec()
    palette = filter_builder.derive_palette(spec["theme"]["main_color"])
    essence_lines = filter_builder.render_essence_visual_ladder(palette)
    blocks = filter_builder.parse_blocks(essence_lines)

    expected = {
        "ESSENCES HIGH VIOLET": {
            "SetTextColor 248 248 250 255",
            "SetBorderColor 218 200 250 255",
            "SetBackgroundColor 124 58 237 250",
        },
        "ESSENCES IMPORTANT VIOLET": {
            "SetTextColor 218 200 250 255",
            "SetBorderColor 163 117 242 255",
            "SetBackgroundColor 68 32 130 245",
        },
        "ESSENCES ROUTINE VIOLET": {
            "SetTextColor 163 117 242 255",
            "SetBorderColor 124 58 237 255",
            "SetBackgroundColor 37 17 71 240",
        },
        "ESSENCES QUIET VIOLET": {
            "SetTextColor 190 190 200 255",
            "SetBorderColor 68 32 130 255",
            "SetBackgroundColor 22 10 43 225",
        },
    }
    for marker, colours in expected.items():
        block = one_block(blocks, marker)
        assert colours <= set(block.directives)
        assert "Continue" in block.directives
        assert not any(
            directive.startswith(
                ("SetFontSize", "PlayAlertSound", "CustomAlertSound", "PlayEffect", "MinimapIcon")
            )
            for directive in block.directives
        )

    economy = json.loads(ECONOMY_PATH.read_text(encoding="utf-8"))
    output, _ = filter_builder.compose_filter(spec, economy)
    assert output.index("Pathcraft Death Oath visual rule 445") < output.index(
        "SMOKIEZONE - ESSENCES QUIET VIOLET"
    )
    assert output.index("SMOKIEZONE - ESSENCES QUIET VIOLET") < output.index(
        "SMOKIEZONE - HCSSF.RESOURCES.CRAFTING"
    )


def test_violet_velvet_unique_and_value_priorities_are_distinct():
    spec = load_spec()
    economy = json.loads(ECONOMY_PATH.read_text(encoding="utf-8"))
    base_lines = BASE_FILTER.read_text(encoding="utf-8").splitlines()
    blocks = filter_builder.parse_blocks(
        filter_builder.render_build_layer(spec, economy, base_lines)
    )

    required = one_block(blocks, "CORE REQUIRED UNIQUE BASES")
    assert "SetTextColor 248 248 250 255" in required.directives
    assert "SetBorderColor 200 101 242 255" in required.directives
    assert "SetBackgroundColor 37 17 71 248" in required.directives
    assert 'CustomAlertSound "MyPrecious.mp3" 300' in required.directives
    assert "PlayEffect Purple" in required.directives
    assert "MinimapIcon 0 Purple Star" in required.directives

    optional = one_block(blocks, "OPTIONAL UNIQUE BASES")
    assert "SetTextColor 175 96 37 255" in optional.directives
    assert "SetBorderColor 124 58 237 255" in optional.directives
    assert "SetBackgroundColor 25 13 29 245" in optional.directives
    assert "PlayAlertSound None" in optional.directives
    assert "PlayEffect None" in optional.directives

    t0 = one_block(blocks, "GLOBAL T0 CURRENCY")
    assert "SetTextColor 124 58 237 255" in t0.directives
    assert "SetBackgroundColor 248 248 250 255" in t0.directives
    assert "PlayEffect Purple" in t0.directives

    t1 = one_block(blocks, "GLOBAL HIGH VALUE CURRENCY")
    assert "SetTextColor 248 248 250 255" in t1.directives
    assert "SetBorderColor 218 200 250 255" in t1.directives
    assert "SetBackgroundColor 124 58 237 255" in t1.directives
    assert "PlayEffect Purple" in t1.directives


def test_resources_currency_and_target_gems_use_the_approved_shared_tokens():
    spec = load_spec()
    palette = filter_builder.derive_palette(spec["theme"]["main_color"])

    resource_blocks = filter_builder.parse_blocks(
        filter_builder.render_resource_groups(spec, palette, "Purple")
    )
    core = one_block(resource_blocks, "BUILD.RESOURCES.CORE")
    essence = one_block(resource_blocks, "HCSSF.RESOURCES.CRAFTING")
    for block in (core, essence):
        assert "SetTextColor 19 10 29 255" in block.directives
        assert "SetBorderColor 124 58 237 255" in block.directives
        assert "SetBackgroundColor 200 101 242 245" in block.directives
        assert "PlayEffect Purple Temp" in block.directives

    currency_blocks = filter_builder.parse_blocks(
        filter_builder.render_utility_currency(palette, "Purple", spec["progression"])
    )
    routine = one_block(currency_blocks, "USEFUL CRAFTING CURRENCY MAP SINGLE")
    assert "SetTextColor 172 160 188 255" in routine.directives
    assert "SetBackgroundColor 18 16 22 245" in routine.directives
    assert "PlayEffect None" in routine.directives
    assert "MinimapIcon -1" in routine.directives

    gem_blocks = filter_builder.parse_blocks(
        filter_builder.render_gem_rules(spec, palette, "Purple")
    )
    target = one_block(gem_blocks, "TARGET GEM BUILD.GEM.COMPLEX_TRAUMA")
    assert 'Class == "Skill Gems"' in target.directives
    assert 'TransfiguredGem "Boneshatter"' in target.directives
    assert not any(
        directive.startswith("BaseType") for directive in target.directives
    )
    assert not any(
        "Boneshatter of Complex Trauma" in directive
        for directive in target.directives
    )
    assert "SetTextColor 27 217 217 255" in target.directives
    assert "SetBackgroundColor 5 31 34 245" in target.directives
    assert "PlayEffect Purple" in target.directives
