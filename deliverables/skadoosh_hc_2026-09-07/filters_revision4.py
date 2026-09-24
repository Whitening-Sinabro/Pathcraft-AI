"""Add conservative progressive cleanup to frozen v3 filters; verify before install."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import poe2_filter_eval as ev

GAME = Path("C:/Users/User/Documents/My Games/Path of Exile 2")
OUT = HERE / "revision4/Filters"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def quote(values):
    return " ".join(f'"{v}"' for v in values)


def render(policy):
    guards = policy["guards"]
    blocks = []

    def block(title, conditions, rarities=None):
        lines = [f"# [cleanup:v4] {title}", "Hide",
                 "\tRarity " + " ".join(rarities or guards["rarities"]),
                 f'\tQuality {guards["quality"]}',
                 f'\tSockets {guards["sockets"]}',
                 f'\tUnidentifiedItemTier {guards["unidentified_item_tier"]}',
                 f'\tAlwaysShow {str(guards["always_show"])}']
        lines += ["\t" + c for c in conditions]
        # Existing NeverSink utility_minimize tokens, no new palette.
        lines += ["\tSetFontSize 18", "\tSetBorderColor 0 0 0 0",
                  "\tSetBackgroundColor 20 20 0 0", "\tDisableDropSound True"]
        blocks.append("\n".join(lines))

    for step in policy["equipment_thresholds"]:
        area, drop = step["area_min"], step["drop_below"]
        title = f"Obsolete equipment: area >= {area}, base unlock < {drop}"
        bounds = [f"AreaLevel >= {area}", f"DropLevel < {drop}"]
        classes = policy["equipment_classes"]
        boot_min = policy["magic_boots_keep_through_area"] + 1
        if area < boot_min:
            block(title, ["Class == " + quote(classes)] + bounds, ["Normal"])
            block(title, ["Class == " + quote([c for c in classes if c != "Boots"])] + bounds, ["Magic"])
            block(title + " (movement-speed boot grace)",
                  ['Class == "Boots"', f"AreaLevel >= {boot_min}", f"DropLevel < {drop}"], ["Magic"])
        else:
            block(title, ["Class == " + quote(classes)] + bounds)
    for step in policy["flask_thresholds"]:
        block(f'Obsolete flasks: area >= {step["area_min"]}',
              ['Class == "Life Flasks" "Mana Flasks"',
               "BaseType == " + quote(step["bases"]), f'AreaLevel >= {step["area_min"]}'])
    header = ("# Pathcraft Skadoosh HC | v4 progressive obsolete-base cleanup\n"
              "# Canonical policy: filter_cleanup_v4.json; regenerate: filters_revision4.py\n"
              "# AreaLevel, not character level or the dropped item's ItemLevel.\n"
              "# Rares/uniques, sockets, quality, tiered/AlwaysShow items pass to v3.\n\n")
    return header + "\n\n".join(blocks) + "\n\n"


def validate(before, after, prefix):
    old, new, cleanup = ev.parse(before), ev.parse(after), ev.parse(prefix)
    assert not ev.unmodelled_conditions(cleanup)
    # Explicit acceptance examples, independent of policy-to-filter rendering.
    cases = [
        ("starter retained at 21", ev.Item("Rusted Cuirass", "Body Armours", area_level=21, drop_level=1), False),
        ("starter expires at 22", ev.Item("Rusted Cuirass", "Body Armours", area_level=22, item_level=80, drop_level=1), True),
        ("current base retained", ev.Item("Plated Mace", "One Hand Maces", area_level=22, drop_level=22), False),
        ("iron retained at 29", ev.Item("Iron Cuirass", "Body Armours", area_level=29, drop_level=11), False),
        ("iron expires at 30", ev.Item("Iron Cuirass", "Body Armours", area_level=30, drop_level=11), True),
        ("plain boots expire", ev.Item("Rough Greaves", "Boots", area_level=22, drop_level=1), True),
        ("magic boots grace", ev.Item("Rough Greaves", "Boots", "Magic", area_level=32, drop_level=1), False),
        ("magic boots expire", ev.Item("Rough Greaves", "Boots", "Magic", area_level=33, drop_level=1), True),
        ("old life flask expires", ev.Item("Lesser Life Flask", "Life Flasks", area_level=15, drop_level=1), True),
        ("current life flask retained", ev.Item("Greater Life Flask", "Life Flasks", area_level=22, drop_level=10), False),
        ("late campaign flask retained", ev.Item("Transcendent Life Flask", "Life Flasks", area_level=70, drop_level=50), False),
        ("spirit base retained", ev.Item("Shrine Sceptre", "Sceptres", area_level=70, drop_level=1), False),
        ("spirit amulet retained", ev.Item("Solar Amulet", "Amulets", area_level=70, drop_level=1), False),
        ("currency retained", ev.Item("Exalted Orb", "Stackable Currency", area_level=70), False),
    ]
    base = ev.Item("Rusted Cuirass", "Body Armours", area_level=45, drop_level=1)
    for label, change in [
        ("rare", {"rarity": "Rare"}), ("unique", {"rarity": "Unique"}),
        ("socket", {"sockets": 1}), ("quality", {"quality": 1}),
        ("special", {"always_show": True}), ("tiered", {"unidentified_item_tier": 1}),
    ]:
        cases.append((label + " preserved", replace(base, **change), False))
    for label, item, hidden in cases:
        matched = [b for b in cleanup if ev.matches(b, item)]
        assert bool(matched) == hidden, (label, matched)
        result = ev.evaluate(new, item)
        if hidden:
            assert result.matched and not result.visible, label
        else:
            prior = asdict(ev.evaluate(old, item)); current = asdict(result)
            prior.pop("block_line"); current.pop("block_line")
            assert current == prior, (label, current, prior)
    # Exhaustive threshold edges; ItemLevel deliberately fixed high to catch
    # accidental substitution of ItemLevel for the base's DropLevel.
    thresholds = [(22, 8), (30, 16), (40, 24), (48, 32), (56, 40), (60, 44)]
    count = 0
    for area in [14, 15, 21, 22, 29, 30, 32, 33, 39, 40, 47, 48, 55, 56, 59, 60, 65, 80]:
        limit = max([d for a, d in thresholds if area >= a] or [0])
        for drop in [1, 7, 8, 15, 16, 23, 24, 31, 32, 39, 40, 43, 44, 65]:
            for rarity in ["Normal", "Magic", "Rare", "Unique"]:
                for cls in ["Body Armours", "Boots", "One Hand Maces", "Sceptres", "Rings"]:
                    item = ev.Item("Boundary fixture", cls, rarity, area_level=area,
                                   item_level=85, drop_level=drop)
                    expected = (cls in ["Body Armours", "Boots", "One Hand Maces"]
                                and rarity in ["Normal", "Magic"] and drop < limit
                                and not (cls == "Boots" and rarity == "Magic" and area <= 32))
                    assert any(ev.matches(b, item) for b in cleanup) == expected, item
                    count += 1
    return {"acceptance_cases": len(cases), "threshold_cases": count,
            "new_hide_blocks": len(cleanup), "unmodelled_cleanup_conditions": {},
            "unmodelled_existing_conditions": ev.unmodelled_conditions(old),
            "validation_scope": "Local condition evaluation and byte preservation; not a live client load"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--install", action="store_true")
    args = ap.parse_args()
    policy = json.loads((HERE / "filter_cleanup_v4.json").read_text(encoding="utf-8"))
    hashes = {r["file"]: r["sha256"] for r in json.loads((HERE / "validation_filters_v3.json").read_text(encoding="utf-8"))}
    prefix = render(policy)
    outputs, report = {}, []
    for stage in policy["stages"]:
        name = f"Pathcraft-Skadoosh-HC-{stage}.filter"
        raw = (HERE / policy["source_revision"] / name).read_bytes()
        assert digest(raw) == hashes[name], f"Frozen v3 changed: {name}"
        before = raw.decode("utf-8")
        data = prefix.encode("utf-8") + raw
        assert data[len(prefix.encode("utf-8")):] == raw
        result = validate(before, data.decode("utf-8"), prefix)
        result.update(file=name, sha256=digest(data), frozen_v3_sha256=hashes[name], frozen_v3_tail_exact=True)
        outputs[name] = data; report.append(result)
    # All outputs verified before replacing any installed file.
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    (HERE / "validation_filters_v4.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.install:
        destinations = [HERE / "ready/Filters", GAME]
        for dest in destinations:
            for name, data in outputs.items():
                p = dest / name
                assert p.is_file(), f"Expected existing filter missing: {p}"
                assert digest(p.read_bytes()) in {hashes[name], digest(data)}, f"Unexpected local edits: {p}"
        installed = []
        for dest in destinations:
            for name, data in outputs.items():
                p = dest / name; old = p.read_bytes()
                backup = HERE / "installed_before_revision4" / ("game" if dest == GAME else "ready") / name
                if old != data:
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    if backup.exists():
                        assert backup.read_bytes() == old
                    else:
                        shutil.copy2(p, backup)
                    p.write_bytes(data)
                assert digest(p.read_bytes()) == digest(data)
                installed.append({"path": str(p), "sha256": digest(data), "backup": str(backup)})
        (HERE / "installation_filters_v4.json").write_text(json.dumps({"files": installed, "game_reload_verified": False}, ensure_ascii=False, indent=2), encoding="utf-8")
        with zipfile.ZipFile(HERE / "Skadoosh-HC-필터-v4.zip", "w", zipfile.ZIP_DEFLATED) as package:
            for name, data in outputs.items(): package.writestr("Filters/" + name, data)
            package.write(HERE / "filter_cleanup_v4.json", "filter_cleanup_v4.json")
    print(json.dumps({"passed": True, "stages": len(outputs), "acceptance_cases": sum(r["acceptance_cases"] for r in report),
                      "threshold_cases": sum(r["threshold_cases"] for r in report), "installed": args.install}, ensure_ascii=False))


if __name__ == "__main__":
    main()
