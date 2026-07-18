# -*- coding: utf-8 -*-
"""CLI runner: build_data/PoB input -> normalized POE1 build profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from recommend_from_pob import load_build_data_from_pob_url
from recommendation_engine import infer_build_profile


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def build_profile_result(
    *,
    build_json_path: str | None,
    pob_url: str | None,
    coach_json_path: str | None = None,
    patch: str | None = None,
    representative_status: str = "near_confirmed",
) -> dict:
    if bool(build_json_path) == bool(pob_url):
        raise ValueError("Provide exactly one of --build-json or --pob-url")

    if build_json_path:
        build_data = _load_json(Path(build_json_path))
    else:
        build_data = load_build_data_from_pob_url(str(pob_url))

    coach_data = _load_json(Path(coach_json_path)) if coach_json_path else None
    return infer_build_profile(
        build_data,
        coach_data,
        representative_status=representative_status,
        patch=patch,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a normalized POE1 build profile from PoB or parsed build_data.")
    parser.add_argument("--build-json", help="Parsed build_data JSON path.")
    parser.add_argument("--pob-url", help="PoB/PoBB URL or file:// XML path.")
    parser.add_argument("--coach-json", help="Optional coach JSON path.")
    parser.add_argument("--patch", help="Override patch string in the emitted profile.")
    parser.add_argument(
        "--representative-status",
        default="near_confirmed",
        choices=["confirmed", "near_confirmed", "hold"],
        help="Representative build confidence status for the emitted profile.",
    )
    parser.add_argument("--output", help="Optional output JSON file path.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = build_profile_result(
        build_json_path=args.build_json,
        pob_url=args.pob_url,
        coach_json_path=args.coach_json,
        patch=args.patch,
        representative_status=args.representative_status,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    print(payload)
