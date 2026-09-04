"""빌드 산출물(필터 · 인게임 플래너 파일)을 디스코드 채널로 보낸다.

여행 중이거나 다른 PC 에서 리그를 시작할 때 필터와 플래너 파일을 옮길 방법이
필요하다. 매번 손으로 첨부하면 세 단계 중 하나를 빠뜨리거나 구버전을 올리게
되므로, 보낼 목록을 **스펙에서 직접 유도한다** — 필터는 `_meta.outputs`,
플래너는 파일명 접두사. `scripts/build_all_filters.py` 와 같은 근거를 쓰기
때문에 빌드한 것과 보낸 것이 갈릴 수 없다.

비밀값은 레포에 없다. **이 레포는 공개(public)** 라서 봇 토큰은 물론이고
채널 ID 도 커밋하지 않는다 — 채널 ID 자체는 비밀이 아니지만 개인 서버의
존재를 드러낸다. 둘 다 환경변수 또는 gitignore 된 `.env` 에서만 읽고,
어떤 로그·예외 메시지에도 토큰이 실리지 않게 `redact()` 를 거친다.

    python scripts/send_to_discord.py --spec poe2_infinite_ignite --planner Ignite
    python scripts/send_to_discord.py --spec poe2_infinite_ignite --dry-run
    python scripts/send_to_discord.py --file Docs/guide.html --message-file msg.txt

값을 찾는 순서: 명령행 인자 -> 환경변수 -> `--env-file` 의 dotenv.
`--env-file` 기본값은 레포와 나란히 있는 `discord-admin/.env` 다(봇이 사는 곳).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Callable, Iterator, Sequence

import requests

REPO = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO / "data" / "filter_build_targets"
FILTER_DIR = REPO / "filters"
PLANNER_DIR = REPO / "build_planner"
DEFAULT_ENV_FILE = REPO.parent / "discord-admin" / ".env"

DISCORD_API = "https://discord.com/api/v10"
TOKEN_KEY = "DISCORD_BOT_TOKEN"
CHANNEL_KEY = "DISCORD_CHANNEL_ID"

# 디스코드 한 메시지 한계. 넘기면 400 이 오는데 본문이 불친절해서 먼저 자른다.
MAX_ATTACHMENTS = 10
MAX_CONTENT_CHARS = 2000
MAX_MESSAGE_BYTES = 8 * 1024 * 1024

log = logging.getLogger("send_to_discord")


# --------------------------------------------------------------------------- #
# 비밀값


def read_dotenv(path: Path) -> dict[str, str]:
    """dotenv 를 최소한으로 판다. 값에 `=` 가 들어 있어도 첫 `=` 에서만 자른다."""
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip("\"'")
    return out


def resolve(key: str, cli_value: str | None, env_file: Path) -> str:
    """명령행 -> 환경변수 -> dotenv 순서로 찾는다. 없으면 어디에 넣으라고 알려준다."""
    if cli_value:
        return cli_value
    if os.environ.get(key):
        return os.environ[key]
    value = read_dotenv(env_file).get(key)
    if value:
        return value
    raise SystemExit(
        f"{key} 를 못 찾았다. 환경변수로 넣거나 {env_file} 에 `{key}=...` 한 줄을 두어라. "
        "이 레포는 공개라 값을 커밋하지 않는다."
    )


def redact(text: str, token: str) -> str:
    """토큰이 예외 본문이나 로그에 섞여 나가는 경로를 막는 마지막 관문."""
    return text.replace(token, "***") if token else text


# --------------------------------------------------------------------------- #
# 보낼 목록


def spec_outputs(selector: str) -> list[Path]:
    """`_meta.outputs` 에서 필터 산출물 경로를 얻는다 — build_all_filters.py 와 같은 근거."""
    matches = [p for p in sorted(SPEC_DIR.glob("*.json")) if selector in p.stem]
    if not matches:
        raise SystemExit(f"스펙을 못 찾았다: {selector!r} (본 곳: {SPEC_DIR})")
    if len(matches) > 1:
        names = ", ".join(p.stem for p in matches)
        raise SystemExit(f"스펙이 여러 개 걸린다: {names}. 더 구체적으로 적어라.")

    meta = json.loads(matches[0].read_text(encoding="utf-8")).get("_meta", {})
    outputs = meta.get("outputs")
    if not outputs:
        raise SystemExit(f"{matches[0].name} 에 `_meta.outputs` 가 없다 — 보낼 파일을 알 수 없다.")
    return [FILTER_DIR / o["file"] for o in outputs]


def planner_files(prefix: str) -> list[Path]:
    found = sorted(PLANNER_DIR.glob(f"{prefix}*.build"))
    if not found:
        raise SystemExit(f"플래너 파일이 없다: {PLANNER_DIR}/{prefix}*.build")
    return found


def check_payload(paths: Sequence[Path]) -> None:
    """보내기 전에 존재와 크기를 확인한다. 빌드를 안 돌린 채 보내는 사고를 막는다."""
    missing = [p for p in paths if not p.is_file()]
    if missing:
        listing = "\n".join(f"  없음: {p}" for p in missing)
        raise SystemExit(
            f"보낼 파일이 없다:\n{listing}\n"
            "먼저 빌드해라: python scripts/build_all_filters.py"
        )
    oversized = [p for p in paths if p.stat().st_size > MAX_MESSAGE_BYTES]
    if oversized:
        listing = "\n".join(f"  {p.name}  {p.stat().st_size / 1048576:.1f}MB" for p in oversized)
        raise SystemExit(f"한 파일이 {MAX_MESSAGE_BYTES // 1048576}MB 를 넘는다:\n{listing}")


def batches(paths: Sequence[Path]) -> Iterator[list[Path]]:
    """첨부 개수와 총 바이트 두 한계를 동시에 지키며 메시지 단위로 쪼갠다."""
    batch: list[Path] = []
    size = 0
    for path in paths:
        this = path.stat().st_size
        if batch and (len(batch) >= MAX_ATTACHMENTS or size + this > MAX_MESSAGE_BYTES):
            yield batch
            batch, size = [], 0
        batch.append(path)
        size += this
    if batch:
        yield batch


def default_message(paths: Sequence[Path]) -> str:
    lines = ["**PathcraftAI 산출물**", ""]
    lines += [f"- `{p.name}`  {p.stat().st_size / 1024:,.1f}KB" for p in paths]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 전송


def post_message(channel_id: str, token: str, content: str, paths: Sequence[Path]) -> dict:
    """네트워크에 닿는 유일한 함수. 테스트는 이것만 갈아끼운다."""
    parts: list[tuple[str, tuple]] = [
        ("payload_json", (None, json.dumps({"content": content}), "application/json"))
    ]
    for i, path in enumerate(paths):
        parts.append((f"files[{i}]", (path.name, path.read_bytes(), "application/octet-stream")))

    try:
        response = requests.post(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            headers={"Authorization": f"Bot {token}"},
            files=parts,
            timeout=120,
        )
    except requests.RequestException as e:
        raise SystemExit(f"디스코드에 못 닿았다: {redact(str(e), token)}") from e

    if not response.ok:
        raise SystemExit(
            f"전송 실패 {response.status_code}: {redact(response.text, token)[:500]}"
        )
    return response.json()


def deliver(
    channel_id: str,
    token: str,
    content: str,
    paths: Sequence[Path],
    poster: Callable[..., dict] = post_message,
) -> int:
    sent = 0
    for index, batch in enumerate(batches(paths)):
        # 본문은 첫 메시지에만. 뒤따르는 메시지에 같은 설명이 반복되면 읽기 나쁘다.
        body = content if index == 0 else ""
        result = poster(channel_id, token, body, batch)
        attachments = result.get("attachments", [])
        sent += len(attachments)
        log.info("메시지 %s · 첨부 %d개", result.get("id", "?"), len(attachments))
        for a in attachments:
            log.info("  %s  %.1fKB", a.get("filename"), a.get("size", 0) / 1024)
    return sent


# --------------------------------------------------------------------------- #


def collect(args) -> list[Path]:
    paths: list[Path] = []
    if args.spec:
        paths += spec_outputs(args.spec)
    if args.planner:
        paths += planner_files(args.planner)
    paths += [Path(f) if Path(f).is_absolute() else REPO / f for f in args.file]
    return paths


def build_content(args, paths: Sequence[Path]) -> str:
    if args.message_file:
        content = Path(args.message_file).read_text(encoding="utf-8").rstrip()
    elif args.message:
        content = args.message
    else:
        content = default_message(paths)
    if len(content) > MAX_CONTENT_CHARS:
        raise SystemExit(f"본문이 {len(content)}자다 — 디스코드 한계 {MAX_CONTENT_CHARS}자.")
    return content


def main(argv: Sequence[str] | None = None, poster: Callable[..., dict] = post_message) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", help="필터 스펙 파일명 일부 — `_meta.outputs` 의 필터를 보낸다")
    ap.add_argument("--planner", help="플래너 파일 접두사 (예: Ignite)")
    ap.add_argument("--file", action="append", default=[], help="임의 파일 (반복 가능)")
    ap.add_argument("--message", help="본문")
    ap.add_argument("--message-file", help="본문을 담은 파일")
    ap.add_argument("--channel", help=f"채널 ID (없으면 {CHANNEL_KEY})")
    ap.add_argument("--token", help=f"봇 토큰 (없으면 {TOKEN_KEY}) — 셸 히스토리에 남으니 권장하지 않는다")
    ap.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    ap.add_argument("--dry-run", action="store_true", help="보내지 않고 목록만 확인한다")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)

    if not (args.spec or args.planner or args.file):
        raise SystemExit("보낼 게 없다. --spec / --planner / --file 중 하나는 있어야 한다.")

    paths = collect(args)
    check_payload(paths)
    content = build_content(args, paths)

    total = sum(p.stat().st_size for p in paths)
    log.info("보낼 파일 %d개 · %.1fKB · 메시지 %d개", paths.__len__(), total / 1024, len(list(batches(paths))))
    for path in paths:
        log.info("  %-58s %8.1fKB", path.name, path.stat().st_size / 1024)

    if args.dry_run:
        log.info("\n--dry-run 이라 보내지 않았다. 본문 %d자:\n%s", len(content), content)
        return 0

    channel_id = resolve(CHANNEL_KEY, args.channel, args.env_file)
    token = resolve(TOKEN_KEY, args.token, args.env_file)
    sent = deliver(channel_id, token, content, paths, poster=poster)
    log.info("전송 완료 · 첨부 %d개", sent)
    return 0 if sent == len(paths) else 1


if __name__ == "__main__":
    raise SystemExit(main())
