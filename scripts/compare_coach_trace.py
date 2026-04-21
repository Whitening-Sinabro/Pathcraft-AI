"""코치 출력 A/B 비교 (Phase H4 / H-후속).

두 coach_result JSON (구/신 프롬프트 각각 수동 수집) 의 _normalization_trace /
_validation_warnings 를 diff 해 품질 회귀 여부 정량 측정.

사용:
    python scripts/compare_coach_trace.py <before.json> <after.json>

출력:
  - trace 건수 before → after (감소가 품질 개선 신호)
  - warnings 건수 before → after
  - match_type 별 breakdown (alias/exact/fuzzy)
  - 양측에만 있는 필드 경로 샘플

제약:
  - 동일 빌드/동일 모델로 생성한 JSON 기준. 이 스크립트는 단순 비교일 뿐
    통계적 유의성 검증은 충분한 샘플 수집 후 사용자가 별도로 수행.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

logger = logging.getLogger("compare_coach_trace")
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def _load(path: Path) -> dict:
    if not path.exists():
        logger.error("파일 없음: %s", path)
        sys.exit(2)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error("로드 실패 %s: %s", path, e)
        sys.exit(2)


def _summary(label: str, data: dict) -> dict:
    trace = data.get("_normalization_trace", []) or []
    warnings = data.get("_validation_warnings", []) or []
    match_types = Counter(t.get("match_type", "?") for t in trace if isinstance(t, dict))
    fields = {t.get("field") for t in trace if isinstance(t, dict)}
    return {
        "label": label,
        "trace_count": len(trace),
        "warnings_count": len(warnings),
        "match_types": dict(match_types),
        "fields": fields,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="코치 출력 A/B 비교")
    ap.add_argument("before", type=Path, help="이전 (구 프롬프트) coach_result JSON")
    ap.add_argument("after", type=Path, help="이후 (신 프롬프트) coach_result JSON")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    before = _summary("before", _load(args.before))
    after = _summary("after", _load(args.after))

    logger.info("=" * 50)
    logger.info("정규화 trace — 낮을수록 좋음 (프롬프트가 정식명 잘 지킴)")
    logger.info("  before: %d건 / after: %d건 (Δ %+d)",
                before["trace_count"], after["trace_count"],
                after["trace_count"] - before["trace_count"])
    logger.info("")
    logger.info("검증 warnings — 낮을수록 좋음")
    logger.info("  before: %d건 / after: %d건 (Δ %+d)",
                before["warnings_count"], after["warnings_count"],
                after["warnings_count"] - before["warnings_count"])
    logger.info("")
    logger.info("match_type breakdown:")
    all_types = set(before["match_types"]) | set(after["match_types"])
    for mt in sorted(all_types):
        b = before["match_types"].get(mt, 0)
        a = after["match_types"].get(mt, 0)
        logger.info("  %-20s  %d → %d (Δ %+d)", mt, b, a, a - b)

    only_before = before["fields"] - after["fields"]
    only_after = after["fields"] - before["fields"]
    if only_before:
        logger.info("")
        logger.info("before 만 교정된 필드 (after 에서 프롬프트가 미리 잘 씀): %d", len(only_before))
        for f in sorted(only_before)[:5]:
            logger.info("  - %s", f)
    if only_after:
        logger.info("")
        logger.info("after 만 교정된 필드 (신 프롬프트에서 새로 생긴 오류): %d", len(only_after))
        for f in sorted(only_after)[:5]:
            logger.info("  - %s", f)


if __name__ == "__main__":
    main()
