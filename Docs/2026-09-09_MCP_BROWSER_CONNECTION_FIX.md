# Claude·Codex MCP 연결 확인 누락 재발 방지

사용자는 다른 클라이언트에 설정이 있다는 이유로 매번 도구를 못 찾았다고 보고하는 문제를 지적했고, 공통으로 기록하라고 요청했다.

## 실제 적용

- 정본: `C:/Users/User/.agents/MCP_BROWSER_CONNECTION_RULES.md`.
- Codex 글로벌 `C:/Users/User/.codex/AGENTS.md`와 Claude 글로벌 `C:/Users/User/.claude/CLAUDE.md`에 같은 필수 확인 지침·정본 경로를 추가했다.
- 프로젝트 `AGENTS.md`와 `CLAUDE.md`에도 같은 확인 경로를 기록했다.
- Codex `config.toml`의 `mcp_servers.playwright`를 Claude 글로벌 등록과 동일한 command/args로 추가했다. 기존 항목은 변경하지 않았다. 변경 전 파일은 각 원본 옆에 타임스탬프 백업했다.
- TOML 파싱과 변경 전후 비교로 추가한 서버 외 기존 설정이 동일함을 확인했다. 양쪽 Playwright command/args 일치와 양쪽 글로벌 지침 존재를 확인했다.

## 실제 연결 근거와 한계

현재 세션의 도구 목록에 없더라도, 이미 등록된 로컬 서버에 실제 MCP `ClientSession`으로 연결할 수 있었다. 사용한 서버는 캐시된 `@playwright/mcp` 0.0.80, Chrome 채널이다.

- `browser_tabs` 호출 성공, 기존 blank 탭을 보존하고 조사 탭을 생성했다.
- 첫날 영상 `zKJQyBm4VnI`의 24분 링크를 열었고, `browser_evaluate` 응답에서 재생 시간 1535.284초, readyState 4, 1280×720, paused false를 확인했다.
- 페이지에 로그인 링크가 보였고 아바타가 없어 **사용자 계정 로그인 상태는 확인되지 않았다**. 등록/연결 성공과 인증 성공을 구분한다.
- 원본 화면 지정 시각 캡처와 판독도 성공했다. 4레벨 원소 병기 새기기 확인 창, 6레벨 섬광 등록·빈 보조 슬롯·무정 패시브, 8레벨 보조 목록과 허리띠 비교 등을 원본 화면대장에 저장했다. 설정 추가가 현재 Codex 대화의 기본 도구 목록에 즉시 반영됐다고 주장하지 않는다.

실제 MCP 응답: `deliverables/seongbin_from_day1_2026-09-09/mcp_session/response_001.json`~`response_003.json`. 접속 구현: `playwright_mcp_bridge.py`.

다음 에이전트는 Codex·Claude 양쪽 글로벌/프로젝트 설정, 실제 MCP 호출, 브라우저 profile/root, 로그인, 목표 콘텐츠 재생을 순서대로 확인한다. “다른 쪽에 등록돼 있어 못 봤다”라는 설명만 하고 사용자에게 연결 작업을 되돌리지 않는다.
