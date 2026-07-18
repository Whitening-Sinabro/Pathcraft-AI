# -*- coding: utf-8 -*-
"""CLI runner: PoB/PoBB input -> parsed build_data -> recommendation result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pob_parser import decode_pob_code, get_pob_code_from_url, parse_pob_xml
from recommendation_engine import recommend_from_build_data


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_build_data_from_pob_url(pob_url: str) -> dict:
    pob_code = get_pob_code_from_url(pob_url)
    if not pob_code:
        raise ValueError(f"Could not fetch POB code from {pob_url}")

    if pob_code.startswith("__XML_DIRECT__"):
        xml_data = pob_code[14:]
    else:
        xml_data = decode_pob_code(pob_code)
        if not xml_data:
            raise ValueError(f"Could not decode POB data from {pob_url}")

    build_data = parse_pob_xml(xml_data, pob_url)
    if not build_data:
        raise ValueError(f"Could not parse POB XML from {pob_url}")
    return build_data


def load_build_payloads(build_json_paths: list[str], pob_urls: list[str]) -> list[dict]:
    payloads = []
    for path in build_json_paths:
        payloads.append(_load_json(Path(path)))
    for pob_url in pob_urls:
        payloads.append(load_build_data_from_pob_url(pob_url))
    return payloads


def build_recommendation_result(
    *,
    build_json_paths: list[str],
    pob_urls: list[str],
    user_state_path: str,
    coach_json_paths: list[str] | None = None,
) -> dict:
    build_payloads = load_build_payloads(build_json_paths, pob_urls)
    if not build_payloads:
        raise ValueError("At least one --build-json or --pob-url is required")

    coach_payloads = [_load_json(Path(path)) for path in (coach_json_paths or [])]
    while len(coach_payloads) < len(build_payloads):
        coach_payloads.append(None)

    user_state = _load_json(Path(user_state_path))
    return recommend_from_build_data(build_payloads, user_state, coach_payloads)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run POE1 recommendation pipeline from PoB links or parsed JSON.")
    parser.add_argument("--build-json", action="append", default=[], help="Parsed build_data JSON path. Repeatable.")
    parser.add_argument("--pob-url", action="append", default=[], help="PoB/PoBB URL or file:// XML path. Repeatable.")
    parser.add_argument("--coach-json", action="append", default=[], help="Coach JSON path aligned to input order.")
    parser.add_argument("--user-state", required=True, help="User state JSON path.")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = build_recommendation_result(
        build_json_paths=args.build_json,
        pob_urls=args.pob_url,
        user_state_path=args.user_state,
        coach_json_paths=args.coach_json,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
