"""Generate a Show-only Cursemaster highlight overlay on top of NeverSink's POE2 filter.

Usage:
    python scripts/build_poe2_build_overlay.py \
        --base <NeverSink .filter> \
        --spec data/filter_build_targets/<build>.json \
        --out <output .filter> [--stage campaign|maps|endgame] [--install-dir <dir>]

Stages:
  A spec rule may declare "stages" — which progression stages it belongs to.
  Under --stage, a rule that declares stages and does not list the requested one
  is left out, so the campaign file is not polluted by endgame-only crafting
  materials and the endgame file is not polluted by levelling bases. A rule with
  no "stages" key counts as all-stages. Without --stage every rule is emitted.

Safety model (silent-failure guards):
  * Vocabulary gate: every Class/BaseType token must appear verbatim in the base
    filter text; unknown names are dropped with a warning (never emitted blind).
  * Show-only: the overlay cannot hide anything; unmatched items fall through to
    NeverSink's own rules (first-match-wins).
  * Contrast gate: text vs background relative-luminance difference must clear a
    fixed threshold, so no label can render unreadable.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("build-overlay")

REPO_ROOT = Path(__file__).resolve().parents[1]

CONTRAST_MIN = 0.35  # relative luminance gap; POE1 cascade-gate lesson, lightweight port


def repo_relative(path: Path) -> str:
    """Render a path for the regenerate hint.

    The hint has to be identical no matter which directory the build was run
    from, otherwise two byte-identical filters compare unequal and the
    reproducibility check becomes noise. Paths outside the repo keep their
    absolute form, which is the honest answer for an external base filter.
    """
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def luminance(rgb: list[int]) -> float:
    r, g, b = (c / 255.0 for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def check_contrast(style_name: str, style: dict) -> None:
    gap = abs(luminance(style["text"]) - luminance(style["background"]))
    if gap < CONTRAST_MIN:
        raise SystemExit(
            f"contrast gate FAIL: style '{style_name}' text/background gap {gap:.2f} < {CONTRAST_MIN}"
        )


def vocab_ok(token: str, base_text: str) -> bool:
    return token in base_text


def build_block(rule: dict, style: dict) -> str:
    lines = [f"# [overlay] {rule['name']} — {rule.get('note', '')}".rstrip(), "Show"]
    if rule.get("rarity"):
        lines.append(f'\tRarity == "{rule["rarity"]}"')
    if rule.get("class"):
        classes = rule["class"] if isinstance(rule["class"], list) else [rule["class"]]
        quoted_cls = " ".join(f'"{c}"' for c in classes)
        lines.append(f"\tClass == {quoted_cls}")
    quoted = " ".join(f'"{b}"' for b in rule["base_types"])
    op = "== " if rule.get("exact") else ""
    lines.append(f"\tBaseType {op}{quoted}")
    if rule.get("area_level_max"):
        lines.append(f"	AreaLevel <= {int(rule['area_level_max'])}")
    t, bo, bg = style["text"], style["border"], style["background"]
    lines.append(f"\tSetTextColor {t[0]} {t[1]} {t[2]} 255")
    lines.append(f"\tSetBorderColor {bo[0]} {bo[1]} {bo[2]} 255")
    lines.append(f"\tSetBackgroundColor {bg[0]} {bg[1]} {bg[2]} 255")
    lines.append(f"\tSetFontSize {style['font']}")
    snd = style["sound"]
    lines.append(f"\tPlayAlertSound {snd[0]} {snd[1]}")
    lines.append(f"\tPlayEffect {style['beam']}")
    icon = style["icon"]
    lines.append(f"\tMinimapIcon {icon[0]} {icon[1]} {icon[2]}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--stage",
        default=None,
        choices=["campaign", "maps", "endgame"],
        help="emit only the rules that apply to this progression stage",
    )
    ap.add_argument("--install-dir", default=None)
    args = ap.parse_args()

    base_path, spec_path = Path(args.base), Path(args.spec)
    if not base_path.exists():
        raise SystemExit(f"base filter not found: {base_path}")
    base_text = base_path.read_text(encoding="utf-8")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    for name, style in spec["styles"].items():
        check_contrast(name, style)

    blocks: list[str] = []
    dropped: list[str] = []
    skipped_stage = 0
    for rule in spec["rules"]:
        stages = rule.get("stages")
        if args.stage and stages and args.stage not in stages:
            skipped_stage += 1
            continue
        classes = rule.get("class")
        if classes:
            classes = classes if isinstance(classes, list) else [classes]
            bad = [c for c in classes if not vocab_ok(f'"{c}"', base_text)]
            if bad:
                dropped.append(f"{rule['name']}: class {bad}")
                continue
        kept = [b for b in rule["base_types"] if vocab_ok(b, base_text)]
        missing = [b for b in rule["base_types"] if b not in kept]
        for m in missing:
            dropped.append(f"{rule['name']}: {m}")
        if not kept:
            log.warning("rule '%s' lost every BaseType — skipped", rule["name"])
            continue
        rule = {**rule, "base_types": kept}
        blocks.append(build_block(rule, spec["styles"][rule["style"]]))

    if dropped:
        log.warning("vocabulary gate dropped %d name(s):", len(dropped))
        for d in dropped:
            log.warning("  - %s", d)

    meta = spec.get("_meta", {})
    stage_label = args.stage or "all stages"
    header = "\n".join(
        [
            "#" + "=" * 79,
            f"# PathcraftAI build overlay: {meta.get('build', spec_path.stem)}",
            f"# stage: {stage_label} | base: {base_path.name}",
            f"# spec: {spec_path.name}",
            "# Show-only. Nothing is hidden; unmatched items fall through to NeverSink.",
            f"# regenerate: python scripts/build_poe2_build_overlay.py"
            f" --spec {repo_relative(spec_path)} --base {repo_relative(base_path)} --out <out>"
            + (f" --stage {args.stage}" if args.stage else ""),
            "#" + "=" * 79,
            "",
        ]
    )
    out_text = header + "\n\n".join(blocks) + "\n\n" + base_text
    out_path = Path(args.out)
    out_path.write_text(out_text, encoding="utf-8", newline="\n")
    log.info(
        "wrote %s (%d overlay blocks, %d bytes, %d rule(s) skipped by stage)",
        out_path,
        len(blocks),
        out_path.stat().st_size,
        skipped_stage,
    )

    if args.install_dir:
        dest = Path(args.install_dir) / out_path.name
        shutil.copy(out_path, dest)
        log.info("installed -> %s", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
