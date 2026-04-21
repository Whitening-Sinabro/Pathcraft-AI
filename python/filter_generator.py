# -*- coding: utf-8 -*-
"""PathcraftAI β Continue 필터 생성 CLI.

Wreckers식 Continue 체인 레이어(L0~L10)로 standalone 필터를 출력한다.
빌드 데이터(POB JSON)가 있으면 L7 BUILD_TARGET / L10 RE_SHOW를 동적 주입.
다중 POB 입력 시 Lv 차이 기반 자동 staging (레벨링/엔드게임 AL 분기).

사용법:
    python filter_generator.py --strictness 3 --out my.filter
    python filter_generator.py build.json --out my.filter
    python filter_generator.py - --strictness 3 < build.json
    python filter_generator.py sunder.json boneshatter.json --out build1.filter
    python filter_generator.py a.json b.json --no-staging --out merged.filter
"""

import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Optional

from sections_continue import generate_beta_overlay

logger = logging.getLogger("filter_gen")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="PathcraftAI β Continue Filter Generator")
    ap.add_argument("build_json", nargs="*", default=None,
                    help="POB 빌드 JSON 파일 경로(들) 또는 '-' (stdin, 단일만). 생략 가능.")
    ap.add_argument("--coaching", help="AI 코치 결과 JSON 파일 (L7/L10 강화용)")
    ap.add_argument("--out", help="출력 필터 경로 (생략 시 stdout)")
    ap.add_argument("--strictness", type=int, default=3,
                    help="엄격도 (0=Soft, 1=Regular, 2=Semi-Strict, 3=Strict, 4=Very Strict)")
    ap.add_argument("--stage", action="store_true",
                    help="다중 POB 입력 시 uniques+chanceable만 Lv 기반 AL 분기 (기본: 전체 union)")
    ap.add_argument("--mode", choices=("trade", "ssf", "hcssf"), default="ssf",
                    help="필터 모드 (기본: ssf)")
    ap.add_argument("--al-split", type=int, default=67,
                    help="2-POB stage 모드의 레벨링→엔드게임 전환 AL (기본: 67, 범위: 14~85)")
    ap.add_argument("--json", action="store_true",
                    help="Tauri용 JSON 출력 (overlay + stats + divcards + chanceable)")
    # POE2 D0 — Rust 가 --game poe1|poe2 전달. POE2 필터 문법/ItemClass 매핑은 D5 구현 예정.
    ap.add_argument("--game", choices=["poe1", "poe2"], default="poe1",
                    help="대상 게임 (POE2 필터 분기는 D5 에서 구현 예정)")
    args = ap.parse_args()

    if args.strictness < 0 or args.strictness > 4:
        logger.error("--strictness는 0~4 범위 (실제: %d)", args.strictness)
        sys.exit(2)

    if args.game == "poe2":
        logger.warning("--game poe2 는 D0 플래그 수용 단계 — POE1 필터 포맷으로 생성 (D5 미완)")

    build_inputs = args.build_json or []
    coaching_data: Optional[dict] = None
    if args.coaching:
        with open(args.coaching, "r", encoding="utf-8") as f:
            coaching_data = json.load(f)

    # 입력 로드
    build_data: "Optional[dict | list[dict]]" = None
    if len(build_inputs) == 1 and build_inputs[0] == "-":
        build_data = json.load(sys.stdin)
    elif len(build_inputs) == 1:
        with open(build_inputs[0], "r", encoding="utf-8") as f:
            build_data = json.load(f)
    elif len(build_inputs) > 1:
        if "-" in build_inputs:
            logger.error("다중 POB 입력 시 stdin('-') 혼용 불가")
            sys.exit(2)
        build_data = []
        for p in build_inputs:
            with open(p, "r", encoding="utf-8") as f:
                build_data.append(json.load(f))
        logger.info("다중 POB %d개 로드 (stage=%s)",
                    len(build_data), args.stage)

    overlay = generate_beta_overlay(
        strictness=args.strictness,
        build_data=build_data,
        coaching_data=coaching_data,
        stage=args.stage,
        mode=args.mode,
        al_split=args.al_split,
    )

    if args.json:
        # Tauri용 JSON 출력 — overlay + 빌드 통계
        from build_extractor import merge_build_stages
        builds = build_data if isinstance(build_data, list) else (
            [build_data] if build_data else [])
        stages = merge_build_stages(builds, coaching_data, no_staging=True) if builds else []
        stage = stages[0] if stages else None
        result = {
            "overlay": overlay,
            "stats": {
                "unique_count": len(stage.unique_bases) if stage else 0,
                "divcard_count": len(stage.target_cards) if stage else 0,
                "chanceable_count": len(stage.chanceable) if stage else 0,
            },
            "target_divcards": [
                {"card": c["card"], "stack": c.get("stack", 0),
                 "target_unique": c.get("unique", "")}
                for c in (stage.target_cards if stage else [])
            ],
            "chanceable_bases": [
                {"base": c["base"], "unique": c.get("unique", "")}
                for c in (stage.chanceable if stage else [])
            ],
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False))
        sys.exit(0)

    if args.out:
        Path(args.out).write_text(overlay, encoding="utf-8")
        logger.info("β Continue 필터 출력: %s", args.out)
    else:
        sys.stdout.write(overlay)
        if not overlay.endswith("\n"):
            sys.stdout.write("\n")
