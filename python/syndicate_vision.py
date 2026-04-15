# -*- coding: utf-8 -*-
"""PathcraftAI Syndicate Vision — Claude Vision으로 POE Syndicate 스크린샷 분석.

stdin: base64-encoded image bytes (PNG/JPEG/WebP)
stdout: JSON {"divisions": {division: [{member_id, name_en, name_ko, rank}]}, "diagnostics": {...}}
stderr: 진행 로그 (logger.info/warning)

사용법:
    cat image.b64 | python syndicate_vision.py

환경변수: ANTHROPIC_API_KEY 필수.

캐싱: 시스템 프롬프트 + 멤버 명단 (~2K 토큰)에 cache_control. 동일 세션 반복 분석 시 90% 절감.
모델: claude-opus-4-6 (Skill 가이드 — 사용자가 별도 지정 없으면 Opus 사용).
"""

import base64
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("syndicate_vision")

VALID_DIVISIONS = ("Transportation", "Fortification", "Research", "Intervention")
VALID_RANKS = ("Member", "Leader")
MODEL = "claude-opus-4-6"


def _load_member_catalog() -> list[dict[str, Any]]:
    """syndicate_members.json에서 정규화 카탈로그 로드. id, name(en), 한국어 alias 매핑."""
    path = Path(__file__).resolve().parent.parent / "data" / "syndicate_members.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    members = raw.get("members", [])
    catalog: list[dict[str, Any]] = []
    for m in members:
        if m.get("default_division") is None:
            continue  # Catarina (Mastermind) 제외
        catalog.append({
            "id": m["id"],
            "name_en": m["name"],
            "default_division": m["default_division"],
            "tags": m.get("tags", []),
        })
    return catalog


def _build_system_prompt(catalog: list[dict[str, Any]]) -> str:
    """캐싱 가능한 안정적 시스템 프롬프트 — 멤버 카탈로그 임베드."""
    member_lines = []
    # 한국어 ↔ English 매핑은 명시 (POE 한국어 클라이언트 대응)
    ko_alias = {
        "aisling": "에이슬링 라프리",
        "cameria": "캐머리아",
        "elreon": "엘리언",
        "gravicius": "그라비키우스",
        "guff": "구프",
        "haku": "하쿠",
        "hillock": "힐록",
        "it_that_fled": "도망친 그것",
        "janus": "제이너스 페란두스",
        "jorgin": "조르긴",
        "korell": "코렐 고야",
        "leo": "리오 레드메인",
        "riker": "라이커 말로니",
        "rin": "린 유슈",
        "tora": "토라",
        "vagan": "바간",
        "vorici": "보리치",
    }
    for m in catalog:
        ko = ko_alias.get(m["id"], "")
        member_lines.append(
            f'  - id="{m["id"]}", en="{m["name_en"]}", ko="{ko}", default_division="{m["default_division"]}"'
        )

    return f"""You analyze Path of Exile Betrayal Syndicate panel screenshots and extract \
structured member placement data.

The Syndicate has exactly 4 divisions: Transportation, Fortification, Research, Intervention.
Each division can hold 0-4 members. The first member shown in each division is the LEADER (rank=Leader); \
others are MEMBER (rank=Member). The Korean POE client labels:
- Transportation = "수송", Fortification = "방어/요새", Research = "연구", Intervention = "개입"

Members (use exact id as the canonical identifier):
{chr(10).join(member_lines)}

The screenshot may be in English or Korean. Use the en/ko names above to map to the canonical id. \
Catarina (Mastermind) is NOT placed in divisions — ignore her.

Output STRICT JSON only, no prose, no markdown fences. Schema:
{{
  "divisions": {{
    "Transportation": [{{"member_id": "<id>", "rank": "Leader"|"Member"}}],
    "Fortification":  [...],
    "Research":       [...],
    "Intervention":   [...]
  }},
  "confidence": "high"|"medium"|"low",
  "notes": "<brief observation if any uncertainty>"
}}

Empty divisions: use empty array []. If the image is unclear or not a Syndicate panel, \
return all empty arrays with confidence="low" and a note explaining."""


def _detect_media_type(image_bytes: bytes) -> str:
    """PNG/JPEG/WebP magic bytes 감지. Claude Vision 지원 포맷."""
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    if image_bytes.startswith(b"GIF8"):
        return "image/gif"
    raise ValueError("Unsupported image format (PNG/JPEG/WebP/GIF only)")


def _normalize_response(parsed: dict[str, Any], catalog: list[dict[str, Any]]) -> dict[str, Any]:
    """Claude 응답 검증 + 정규화. unknown member_id 폐기, division/rank 화이트리스트."""
    valid_ids = {m["id"] for m in catalog}
    name_to_id = {m["name_en"]: m["id"] for m in catalog}

    out: dict[str, Any] = {"divisions": {d: [] for d in VALID_DIVISIONS}}
    diagnostics: dict[str, Any] = {"unknown_members": [], "invalid_ranks": []}

    raw_divs = parsed.get("divisions", {}) or {}
    for div in VALID_DIVISIONS:
        members = raw_divs.get(div, []) or []
        if not isinstance(members, list):
            continue
        for slot in members:
            if not isinstance(slot, dict):
                continue
            mid = slot.get("member_id", "")
            # Claude이 가끔 영문 이름을 그대로 반환 — name 폴백
            if mid not in valid_ids and mid in name_to_id:
                mid = name_to_id[mid]
            if mid not in valid_ids:
                diagnostics["unknown_members"].append({"div": div, "raw": slot.get("member_id", "")})
                continue
            rank = slot.get("rank", "Member")
            if rank not in VALID_RANKS:
                diagnostics["invalid_ranks"].append({"div": div, "id": mid, "raw": rank})
                rank = "Member"
            out["divisions"][div].append({"member_id": mid, "rank": rank})

    out["confidence"] = parsed.get("confidence", "medium")
    out["notes"] = parsed.get("notes", "")
    out["diagnostics"] = diagnostics
    return out


def analyze_image(image_bytes: bytes) -> dict[str, Any]:
    """이미지 → Claude Vision → 정규화 JSON. 에러 시 raise."""
    try:
        import anthropic
    except ImportError as e:
        raise ImportError("anthropic 패키지 필요: pip install anthropic") from e

    # 프로젝트 .env에서 자동 로드 (build_coach.py 패턴)
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass  # 환경변수만 있어도 동작
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수 미설정 (.env 또는 환경변수 필요)")

    media_type = _detect_media_type(image_bytes)
    image_b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    catalog = _load_member_catalog()
    system_prompt = _build_system_prompt(catalog)

    logger.info(f"Sending {len(image_bytes)} bytes ({media_type}) to {MODEL}")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Analyze this POE Syndicate panel screenshot. Return ONLY the JSON described in the system prompt.",
                    },
                ],
            }
        ],
    )

    usage = response.usage
    logger.info(
        f"Tokens: input={usage.input_tokens}, output={usage.output_tokens}, "
        f"cache_create={getattr(usage,'cache_creation_input_tokens',0)}, "
        f"cache_read={getattr(usage,'cache_read_input_tokens',0)}"
    )

    # 응답에서 텍스트 추출
    text_blocks = [b for b in response.content if b.type == "text"]
    if not text_blocks:
        raise RuntimeError(f"No text in response. stop_reason={response.stop_reason}")
    raw_text = text_blocks[0].text.strip()

    # 모델이 가끔 ```json fence를 둘러서 반환 — 제거
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```", 2)[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip().rstrip("`").strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude 응답 JSON 파싱 실패: {e}\nraw: {raw_text[:500]}") from e

    return _normalize_response(parsed, catalog)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    sys.stdout.reconfigure(encoding="utf-8")

    raw = sys.stdin.buffer.read().strip()
    if not raw:
        print(json.dumps({"error": "stdin empty (expect base64 image)"}, ensure_ascii=False))
        return 2

    try:
        image_bytes = base64.b64decode(raw, validate=True)
    except (ValueError, base64.binascii.Error) as e:
        print(json.dumps({"error": f"base64 decode 실패: {e}"}, ensure_ascii=False))
        return 2

    try:
        result = analyze_image(image_bytes)
    except (ValueError, RuntimeError, ImportError) as e:
        logger.exception("analyze_image 실패")
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
