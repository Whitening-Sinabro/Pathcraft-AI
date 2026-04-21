#!/usr/bin/env python3
"""Stop hook — 프로젝트 Pathcraft-AI.

Claude가 응답 종료하기 직전 자동으로 pytest/tsc/vitest 를 돌려서 "완료/검증됨"
자가 주장이 실제 evidence 와 일치하는지 강제. 과장 단정 + 조용한 실패 방지.

동작:
1. `git status --short` 로 modified/untracked 파일 감지
2. 확장자별로 필요한 도구만 실행:
   - .py 변경 → `python -m pytest python/tests -q --tb=no`
   - .ts/.tsx 변경 → `npx tsc --noEmit`
   - .test.ts/.test.tsx 변경 → `npx vitest run --reporter=dot`
3. 1건이라도 실패 → hook 이 JSON {"continue": false, ...} 반환 →
   Claude 가 stop 못 하고 수정 요구 받음
4. 전부 성공 → 조용히 exit 0 (응답 종료 허용)

테스트 outputs 는 additionalContext 로 Claude 에게 제공. stopReason 은 사용자에게.

Skip 조건:
- 환경변수 `PATHCRAFT_SKIP_STOP_VERIFY=1` 설정되면 즉시 pass
- 파일 변경 없으면 즉시 pass
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Windows 기본 cp949 → 한국어 출력 UnicodeEncodeError 방지
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except AttributeError:
    pass

SKIP_ENV = "PATHCRAFT_SKIP_STOP_VERIFY"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _run(cmd: list[str], use_shell: bool = False) -> tuple[int, str]:
    """Run a command, return (returncode, combined output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            shell=use_shell,
            timeout=120,
        )
        return result.returncode, (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"[timeout 120s] {' '.join(cmd)}"
    except FileNotFoundError:
        return 127, f"[command not found] {' '.join(cmd)}"


def _changed_files() -> list[str]:
    rc, out = _run(["git", "status", "--short"])
    if rc != 0:
        return []
    files: list[str] = []
    for line in out.splitlines():
        # format: "XY filename" — X/Y is status code, columns 0-2, then space, then path
        if len(line) > 3:
            files.append(line[3:].strip())
    return files


def main() -> None:
    sys.stdin.read()  # drain stdin to avoid hook hang

    if os.environ.get(SKIP_ENV):
        return

    changed = _changed_files()
    if not changed:
        return

    has_py = any(f.endswith(".py") for f in changed)
    has_ts = any(f.endswith((".ts", ".tsx")) for f in changed)
    has_vitest = any(f.endswith((".test.ts", ".test.tsx")) for f in changed)

    if not (has_py or has_ts or has_vitest):
        return

    fails: list[str] = []
    sections: list[str] = []

    if has_py:
        rc, out = _run(["python", "-m", "pytest", "python/tests", "-q", "--tb=no"])
        if rc != 0:
            fails.append("pytest")
            sections.append("[pytest]\n" + out.strip()[-1200:])

    if has_ts:
        rc, out = _run(["npx", "tsc", "--noEmit"], use_shell=True)
        if rc != 0:
            fails.append("tsc")
            sections.append("[tsc]\n" + out.strip()[:1200])

    if has_vitest:
        rc, out = _run(["npx", "vitest", "run", "--reporter=dot"], use_shell=True)
        if rc != 0:
            fails.append("vitest")
            sections.append("[vitest]\n" + out.strip()[-1200:])

    if not fails:
        return  # all green — allow stop

    payload = {
        "continue": False,
        "stopReason": f"Stop hook 검증 실패: {', '.join(fails)} — evidence 를 확인하고 수정하라",
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                "Stop hook (D:/Pathcraft-AI/.claude/hooks/verify_on_stop.py) 이 "
                "현재 작업 트리에서 수정된 파일 기준으로 자동 검증을 실행했고 실패를 발견함. "
                "'완료/검증됨' 주장 전에 아래 실제 출력을 확인하고 수정 필요.\n\n"
                + "\n\n".join(sections)
            ),
        },
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # 훅 자체의 버그로 Claude 를 못 멈추게 하면 UX 손상 — skip 대신 warning 으로 처리
        sys.stderr.write(f"[verify_on_stop.py] hook 내부 오류: {exc}\n")
        sys.exit(0)
