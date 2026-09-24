# 2026-09-21 카페 브라우저 연결 재검증

## 큐 중지

사용자 steering msg_19652b8574fc 후 UIA helper session36673의 exit1을 확인했고 `cafe_queue_stop.request`를 만들었다. `cafe_ui.py`는 매 도구 호출 전 이 파일을 확인해 추가 동작 없이 종료한다. 이후 카페 자동 이동·입력·스크롤을 재개하지 않았다. Chrome/agent 프로세스 종료 없이 협조적으로 중지했다. HQ 최초 중지 보고 msg_09e3e2657014, 후속 msg_2b10f6d279e9.

## 서로 다른 두 Chrome

- 실제 사용자 Chrome: PID30624, window1442544. 초기 URL은 cafe31644155/article165. 읽기 전용 UI에 내정보 및 카페탈퇴하기가 있어 로그인 상태를 확인했다. 프로세스 인자에 remote-debugging-port/pipe가 없으며 해당 PID의 TCP Listen도 없었다.
- 기존 Playwright MCP: 실제 `browser_tabs` 응답과 Chrome PID12016의 `mcp-chrome-6f08191` user-data-dir/remote-debugging-pipe를 확인했다. 별도 프로필이다. 메뉴6 페이지에 로그인/가입하기가 표시돼 로그아웃 상태를 확인했다.
- Codex/Claude 전역의 관련 서버 필드는 모두 `npx -y @playwright/mcp@latest --browser chrome`. Claude 추가 전역 및 양쪽 프로젝트 설정에서 별도 cafe용 CDP/extension 연결을 찾지 못했다. 설정은 변경하지 않았다.

기존 MCP 새 연구 탭에서 메뉴6와 글224를 실제 열었다. iframe 본문 및 댓글9개가 읽혔다. 9/21의29d39 링크·아홉꼬리·함성 무기세트 정정을 직접 확인했다. 이것은 **공개 페이지의 실제 읽기 성공**이며 사용자 로그인 Chrome에 연결한 성공이 아니다. 이후 부족한 공개 글은 같은 MCP DOM으로 읽고 `cafe_playwright/batch_01.json` 이후에 저장했다.

## 실제 사용자 Chrome 확장 연결

설치 확장 manifest에서 Playwright Extension0.4.0을 발견했다. 프로필/쿠키/세션 데이터베이스를 읽지 않았다. 로컬 MCP 패키지의 지원 옵션 `--extension`으로 실제 Python MCP ClientSession을 초기화했다. 서버 식별은 Playwright `1.64.0-alpha-1789764292000`, MCP protocol2025-11-25. 기존 Chrome에 연결 선택 화면이 나타났다.

첫 `browser_tabs` 호출은 helper의45초 제한에서 TimeoutError가 났다. 사용자 허용은 msg_5a5bb827fd5b 및 직접 지시로 전달받았다. 새 세션·승인탭·토큰복사 없이 **같은 ClientSession**에서 두 번째 `browser_tabs`를 요청했지만 역시45초 TimeoutError였다. 이는 Python helper의 timeout이며 Playwright가 별도 오류문구를 반환한 것은 아니다.

13:35–13:38 UTC 읽기 점검에서 해당 relay Node PID40312는 localhost14131 Listen을 유지했으나 Established 연결은 없었다. 패키지 원 구현의 relay는 확장 WebSocket 연결 및 초기화를 기다리고, 토큰 없는 승인 대기에는 자체 deadline을 두지 않는다. extension0.4.0 원 구현은 승인 후 relay WebSocket을 여는 구조다. 따라서 helper의 요청 취소 영향은 가능성이 있으나 **확정 원인으로 단정하지 않는다**. 사용자가 승인하지 않았거나 잘못 눌렀다고 판단하지 않는다.

공개 경로에서 빈 본문이 나온9글은160/158/149/135/131/129/121/120/112다. 글131의 outer URL 재확인 시 사이트가 NAVER 로그인 창을 열었다. 나머지8글은 빈 article shell/selector timeout이며 같은 권한 원인이라고 아직 단정하지 않는다. 현재 관련102글 중93본문·댓글 완료,9미완료. 사용자 Chrome의 Playwright 본문·댓글 읽기는 아직 입증되지 않았다.

CU 자동수집은 계속 중지. 사용자 탭 닫기·브라우저 재시작·설정 변경·쿠키 반출 없이 같은 확장 ClientSession을 유지했다. 로컬 연결 요청/응답 운영 폴더는 사용자가 열 플래너의 배포 파일에 포함하지 않는다.

## 허용된 1회 복구 · 13:50 UTC 이후

msg_81deacf00ca5에 따라 기존 helper session64770의 stop.request → exit0 및 정확 relay Node40312 종료를 확인했다. 45초 강제취소를 제거하고 요청 제한30분으로 같은 MCP --extension 복구1회(session33616)를 시작했다. 새 ClientSession 초기화는 성공했으나 14:00 UTC browser_tabs 응답은 아직 없다. 정확 relay Node28764, localhost10697 Listen만 확인했고 Established 연결은 없다. 초기화는 실제 사용자 Chrome 연결이나 카페 읽기 성공이 아니다. 사용자 승인 자동클릭·토큰 추출·Chrome 재시작·프로필 변경·CU 탐색·경쟁 재연결을 하지 않았다. 카페9글은 계속 미완료다.

### 복구 최종 결과 · 14:20 UTC

같은 browser_tabs 요청은 1800초 뒤 McpError: Timed out while waiting for response to ClientRequest로 종료되었다. 사용자 Chrome의 탭·카페 읽기 연결은 입증되지 않았다. 추가 복구를 만들지 않고 stop.request로 helper session33616을 협조 종료했으며 exit0을 확인했다. Chrome/Orca/agent 프로세스를 종료하지 않았다. 허용된 복구1회는 실패로 기록하고9개미완료를유지한다.
