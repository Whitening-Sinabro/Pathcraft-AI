"""Mobalytics 빌드 탭의 `.build` 파일을 사용자의 Playwright MCP(Chrome)로 받아 온다.

왜 MCP 를 따로 띄우나: Mobalytics 는 평범한 HTTP 요청에 403 을 준다(직접 확인).
그래서 브라우저가 필요하고, 이 워크스페이스에 이미 설정된 서버가
`npx @playwright/mcp --browser chrome` 이다. 세션의 MCP 연결이 끊겨도
같은 서버에 파이썬 MCP 클라이언트로 붙으면 같은 경로를 쓸 수 있다.
(연결 규칙: C:/Users/User/.agents/MCP_BROWSER_CONNECTION_RULES.md)

내려받기 버튼은 blob 을 만들어 앵커를 클릭한다. MCP 서버는 다운로드를
`--output-dir` 에 저장하므로 그 폴더를 결과로 본다.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import shutil
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

log = logging.getLogger("moba")

NODE = Path("C:/Program Files/nodejs/node.exe")
CLI_GLOB = "C:/Users/User/AppData/Local/npm-cache/_npx/*/node_modules/@playwright/mcp/cli.js"

# 탭을 하나씩 누를 필요가 없다 — 내려받기 한 번이면 zip 안에 모든 탭의 `.build` 가 들어온다.
# (실측: warbringer zip 에 Endgame·Starter·Leveling·구버전 2개까지 5개 전부 들어 있었다.)
TARGETS = {
    "warbringer": ("https://mobalytics.gg/poe-2/builds/corrupting-cry-warbringer-skadoosh", None),
    "leveling41": ("https://mobalytics.gg/poe-2/builds/skadoosh-warbringer-leveling-41", None),
    "gemling": ("https://mobalytics.gg/poe-2/profile/seongbin-poe2-hardcore-zaxjdu/builds/"
                "11f193d5-8baf-44ea-9938-579451232125", None),
}


def resolve_cli() -> Path:
    hits = sorted(Path("/").glob(CLI_GLOB.lstrip("C:/")))
    for base in ("C:/",):
        hits = sorted(Path(base).glob(CLI_GLOB[len(base):]))
        if hits:
            return hits[-1]
    raise SystemExit("@playwright/mcp cli.js 를 못 찾았다 — npx 캐시를 확인하라")


def text_of(result) -> str:
    out = []
    for c in getattr(result, "content", None) or []:
        t = getattr(c, "text", None)
        if t:
            out.append(t)
    return "\n".join(out)


def find_ref(snapshot: str, label: str, kind: str) -> str | None:
    """스냅샷 줄에서 `- <kind> "<label>" ... [ref=eNN]` 의 ref 를 뽑는다."""
    for line in snapshot.split("\n"):
        if kind in line and label in line:
            m = re.search(r"\[ref=([^\]]+)\]", line)
            if m:
                return m.group(1)
    return None


async def snapshot(session) -> str:
    r = await session.call_tool("browser_snapshot", {})
    body = text_of(r)
    m = re.search(r"\[Snapshot\]\(([^)]+)\)", body)
    if m:
        p = Path(m.group(1).strip())
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    return body


async def grab(session, out_dir: Path, key: str, url: str, tabs, results: list):
    log.info("=== %s : %s", key, url)
    await session.call_tool("browser_navigate", {"url": url})
    await session.call_tool("browser_wait_for", {"time": 3})
    snap = await snapshot(session)

    wanted = tabs or [None]
    for tab in wanted:
        if tab:
            ref = find_ref(snap, tab, 'tab "')
            if not ref:
                log.warning("  탭 못 찾음: %s", tab)
                results.append({"key": key, "tab": tab, "status": "탭 없음"})
                continue
            await session.call_tool("browser_click", {"element": f"{tab} 탭", "target": ref})
            await session.call_tool("browser_wait_for", {"time": 2})
            snap = await snapshot(session)
        before = {p.name for p in out_dir.glob("*") if p.is_file()}
        dref = find_ref(snap, "Download Build File", 'button "')
        if not dref:
            log.warning("  내려받기 버튼 없음 (%s)", tab)
            results.append({"key": key, "tab": tab, "status": "버튼 없음"})
            continue
        try:
            await session.call_tool("browser_click",
                                    {"element": "Download Build File", "target": dref})
        except Exception as exc:  # 다운로드가 연결을 끊는 경우가 있어 삼킨다
            log.warning("  클릭 예외(무시): %s", type(exc).__name__)
        await session.call_tool("browser_wait_for", {"time": 3})
        after = {p.name for p in out_dir.glob("*") if p.is_file()}
        new = sorted(after - before)
        log.info("  %-24s 새 파일 %s", tab or "(단일)", new or "없음")
        results.append({"key": key, "tab": tab, "files": new,
                        "status": "받음" if new else "파일 없음"})
        snap = await snapshot(session)


async def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s", stream=sys.stdout)
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=list(TARGETS))
    ap.add_argument("--out", default=".tmp/moba")
    args = ap.parse_args()

    out_dir = Path(args.out).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    cli = resolve_cli()
    log.info("서버: %s", cli)
    params = StdioServerParameters(
        command=str(NODE),
        args=[str(cli), "--browser", "chrome", "--output-dir", str(out_dir)],
        cwd=str(Path.cwd()),
    )
    results: list = []
    errlog = (out_dir / "server_stderr.log").open("w", encoding="utf-8")
    try:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                names = [t.name for t in (await session.list_tools()).tools]
                log.info("도구 %d개 연결", len(names))
                for key in args.only:
                    url, tabs = TARGETS[key]
                    try:
                        await grab(session, out_dir, key, url, tabs, results)
                    except Exception as exc:
                        log.error("%s 실패: %s: %s", key, type(exc).__name__, exc)
                        results.append({"key": key, "status": f"실패 {type(exc).__name__}"})
    finally:
        errlog.close()
    (out_dir / "result.json").write_text(json.dumps(results, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    log.info("결과: %s", out_dir / "result.json")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
