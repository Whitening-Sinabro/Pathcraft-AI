"""The Exiled Cat SSF Strength Stacker filter is composed from its spec, not from Smokiezone constants."""
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import build_smokiezone_hcssf_filter as filter_builder  # noqa: E402
import filter_cascade  # noqa: E402


SPEC_PATH = (
    ROOT
    / "data"
    / "filter_build_targets"
    / "poe1_exiledcat_ssf_strength_stacker_juggernaut_3_29.json"
)
SMOKIEZONE_SPEC_PATH = (
    ROOT
    / "data"
    / "filter_build_targets"
    / "poe1_smokiezone_hydrosphere_boneshatter_hcssf_3_29.json"
)
ECONOMY_PATH = (
    ROOT / "data" / "filter_sources" / "neversink_poe1_8_20_1d_903189_economy.json"
)


def load_spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def restore_default_labels():
    """The builder keeps its label vocabulary as module state; never leak it across test files."""
    yield
    filter_builder.configure_labels(
        json.loads(SMOKIEZONE_SPEC_PATH.read_text(encoding="utf-8"))
    )


def compose():
    spec = load_spec()
    economy = json.loads(ECONOMY_PATH.read_text(encoding="utf-8"))
    output, _ = filter_builder.compose_filter(spec, economy)
    return spec, output


def test_spec_targets_resolve_against_game_data():
    filter_builder.validate_target_names(load_spec())


def test_composed_filter_uses_the_exiled_cat_vocabulary_only():
    spec, output = compose()

    assert "Show # EXILEDCAT - CORE REQUIRED UNIQUE BASES" in output
    assert "Show # EXILEDCAT - TARGET GEM BUILD.GEM.SMITE_OF_DIVINE_JUDGEMENT" in output
    assert "# EXILEDCAT SCSSF DIVINATION CARD LADDER - BEGIN" in output
    assert "EXILEDCAT - DIVINATION CARDS SCSSF WANTED" in output
    assert "SMOKIEZONE" not in output
    assert "HCSSF" not in output
    assert "SCSSF - RARE ARMOUR AND JEWELLERY THROUGH RED MAPS" in output
    assert "RARE TWO HAND AXES THROUGH RED MAPS" not in output
    assert f"# PATHCRAFT {spec['labels']['filter_title']}" in output
    assert f"# Canonical build targets: data/filter_build_targets/{spec['build_id']}.json" in output


def test_required_unique_bases_are_the_seven_creator_uniques():
    spec, output = compose()
    block = next(
        block
        for block in filter_builder.parse_blocks(output.splitlines())
        if "EXILEDCAT - CORE REQUIRED UNIQUE BASES" in block.header
    )
    base_line = next(line for line in block.directives if line.startswith("BaseType =="))
    assert base_line == (
        'BaseType == "Amber Amulet" "Crusader Plate" "Heavy Belt" "Hubris Circlet" '
        '"Ritual Sceptre" "Soldier Boots" "Vaal Rapier"'
    )
    required = [t for t in spec["unique_targets"] if t["priority"] == "required"]
    assert {base for t in required for base in t["resolved_base_types"]} == {
        "Amber Amulet",
        "Crusader Plate",
        "Heavy Belt",
        "Hubris Circlet",
        "Ritual Sceptre",
        "Soldier Boots",
        "Vaal Rapier",
    }


def test_full_validation_passes_for_the_exiled_cat_spec():
    spec, output = compose()
    source_text = filter_builder.BASE_FILTER.read_text(encoding="utf-8")
    stats = filter_builder.validate_filter(output, spec, source_text)
    assert stats["hide"] == stats["source_hide_blocks_preserved"]


def test_creator_targets_are_readable_after_cascade():
    _, output = compose()
    blocks = filter_cascade.parse_cascade(output.splitlines())
    probes = [
        filter_cascade.SimulatedItem("Ritual Sceptre", "Sceptres", "Unique", 28, 28),
        filter_cascade.SimulatedItem("Soldier Boots", "Boots", "Unique", 49, 49),
        filter_cascade.SimulatedItem("Hubris Circlet", "Helmets", "Unique", 80, 80),
        filter_cascade.SimulatedItem("Crusader Plate", "Body Armours", "Unique", 85, 85),
        filter_cascade.SimulatedItem("Timeless Jewel", "Jewels", "Unique", 85, 85),
        filter_cascade.SimulatedItem("Amethyst Ring", "Rings", "Rare", 85, 85),
        filter_cascade.SimulatedItem("Walnut Spirit Shield", "Shields", "Normal", 84, 84),
        filter_cascade.SimulatedItem("Leviathan Gauntlets", "Gloves", "Magic", 84, 84),
        filter_cascade.SimulatedItem("Astral Plate", "Body Armours", "Rare", 70, 70),
    ]
    for item in probes:
        result = filter_cascade.simulate(blocks, item)
        assert result.action == "Show", item
        text = result.colour("SetTextColor")
        background = result.colour("SetBackgroundColor")
        assert text is not None and background is not None, item
        assert filter_cascade.contrast_ratio(text, background) >= 2.0, (
            item,
            text,
            background,
            result.chain[-4:],
        )


def test_configure_labels_restores_the_smokiezone_defaults():
    smokiezone = json.loads(SMOKIEZONE_SPEC_PATH.read_text(encoding="utf-8"))
    filter_builder.configure_labels(load_spec())
    assert filter_builder.CREATOR_LABEL == "EXILEDCAT"
    assert filter_builder.ORDINARY_UNIQUE_DEFAULT == "EXILEDCAT - ORDINARY UNIQUE DEFAULT"
    filter_builder.configure_labels(smokiezone)
    assert filter_builder.CREATOR_LABEL == "SMOKIEZONE"
    assert filter_builder.GENERATED_HEADER_MARKERS == ("SMOKIEZONE", "HCSSF", "PATHCRAFT HCSSF")
    assert filter_builder.output_path(smokiezone).name == (
        "Smokiezone_Hydrosphere_Boneshatter_HCSSF_3.29_Progressive.filter"
    )
