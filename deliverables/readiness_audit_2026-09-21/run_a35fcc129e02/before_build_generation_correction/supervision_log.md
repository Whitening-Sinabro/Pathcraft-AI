# 실사 감독 기록

- 원본 평가 대상: 현재 `D:/Pathcraft-AI` 전체. 새 checkout은 배치·보고서 공간이다.
- 내부 Run: `run_a35fcc129e02`; 최초 책임자: `term_8236f49f-d5a0-4315-96d6-d55d5e00dced`. 10:31 UTC 이후 후임은 `term_563ecf5f-053e-4df4-a387-b4af588997a2`이며 아래 인수 기록이 우선한다.
- 배치 확인: Orca 1.4.206의 `worktree current/list`, `task-list`, 각 `dispatch-show`, `worker-show`로 master → 책임자 → 분야별 3개 하위트리를 확인했다. 세 작업 모두 depth 1, 재귀 위임 금지.
- `worker-start --worktree new-child --agent codex --setup skip` 사용. 모델·effort 지정 없음. 저장소 기본 설치 훅 `pnpm install`은 설치 금지 범위 때문에 생략했다.
- 제품 코드 수정·설치·배포·게임 쓰기 금지. 테스트·빌드는 부작용 검토 후 구현 담당만 수행한다.

| 분야 | Task | Dispatch | 보고서 소유 경로 |
|---|---|---|---|
| 구현·실행 | task_9076d3c085bf | ctx_30a92ca0cdb6 | C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/technical.md |
| 개인용 제품·데이터 | task_1d7873da8938 | ctx_181fcc75a1fe | C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-personal-20260921/personal_product.md |
| 상용화 | task_1f68bd784579 | ctx_058c95b1d793 | C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-commercial-20260921/commercialization.md |

## 추가 보고 계약

2026-09-21 09:58 UTC, 본부의 `msg_c162cfd94b4a` 및 `msg_7203ff57065e`를 수신했다. 본부는 사용자 추가 지시로 종료 대신 외부 읽기 전용 감독 Run `run_debe30e1db10`에서 보고를 받는다고 전달했다. 내부 Run/Task/Dispatch 소유권은 변경하지 않는다. 본부 현재 핸들은 `term_f5f99c65-4767-4cfc-8175-e0849a3c5e3e`이며, 사용자가 재사용 금지한 이전 책임자 터미널과 다르다.

- `orca orchestration send --to run:run_debe30e1db10 --type status`로 5분 간격 보고.
- 분야 완료·장애·결정 필요·최종 완료는 즉시 보고.
- 시각, 작업별 마지막 검증, 새 사실·근거, 잠정 판단/불확실성, 차단 여부, 다음 행동을 포함한다.
- `check --wait`는 최대 45초로 나누며 `worker_done,escalation,question,status`를 포함한다.
- 최종 네 보고서 경로, 검증 명령·결과·미검증 범위를 본부에도 전달한다. 책임자 세션의 최종 사용자 보고 의무는 유지한다.

## 체크포인트

- 09:59 UTC: 수신 확인 `msg_53749fdd123c`, 첫 정기보고 `msg_88b8d824ad6e` 발송. 세 분야 live/working. 완료 보고 미수신. 구현 담당은 원본 JSON을 쓰는 prebuild를 발견하여 안전한 분리 검증을 준비 중. 개인용 담당은 POE1 앱 흐름과 POE2 별도 플래너/HTML의 통합 단절을 추적 중. 상용화 담당은 결제 Mock·개발 PC 경로 및 공식 자료를 조사 중.
- 10:04 UTC 체크포인트 보고 발송: 프런트엔드 115, Python 핵심 176 및 여정 13 통과라는 구현 담당의 중간 결과를 전달했다. 아직 최종 수락 전 수치임을 표시했고 원명령 빌드·Rust·설치/E2E 미검증을 구분했다. 216개 `.build` 중 하나의 검증기 예외, 개인용 비교 깊이, 오래된 미서명 설치파일과 인증 코드 문제를 추가 전달했다. 세 작업자는 live이며 차단·결정 요청 없음.
- 10:06–10:09 UTC: 본부 `msg_a4909ff29a1f`의 사용자 추가 Atlas 검토 지시 수신. reference/contract 두 문서 전체를 읽었다. 구현 담당에 R1 브라우저 및 R3 기술, 상용화 담당에 R3 권리 검토를 추가했다. 개인용 최초 보고서는 10:07:26에 `msg_7f644ebf4fea`로 성공 종료됐다. 책임자가 보고서 전체와 원본 저장/게임 구분/여정 diff 근거를 확인하여 최초 범위는 수락했다. 후속 메시지가 `dispatch_inactive`로 거절된 것을 확인하고 동일 터미널 `term_cdce07aa-842a-484a-a5ab-5b47e298024e`에 정식 후속 Task `task_d8b58bc9e030` / Dispatch `ctx_c2a10749908a`를 시작했다. 기존 worktree/terminal 재사용, 새 인원·하위트리 없음. 후속 범위는 R2 수량·연결성 및 앱 데이터 계약을 기존 personal_product.md에 추가하는 것이다.
- 10:14 UTC 체크포인트: 본부 `msg_8181c19da316`에 R2 중간 정합성, R1 브라우저 연결 대안 확인, R3 제한 조사 진행 및 책임자의 원본/로그/공식 정책 대조를 보고했다.
- 10:16 UTC: 사용자가 이 책임자 세션에서 직접 의식 등 콘텐츠의 의무 선후 오해를 지적했다. 세 활성 Dispatch에 메인 진행과 콘텐츠별 내부 순서를 분리하는 UX·데이터 계약 기준을 전달했고 본부 `msg_dee8d796c30a`로 즉시 공유했다. 분석·보고서 범위이며 제품 UI 변경은 하지 않는다.
- 10:21 UTC 이후: 사용자가 본부 xhigh와 하위 작업자별 모델·effort 선택을 구분하라는 기존 원칙을 재강조했다. 책임자는 초기 인계문의 기본값 지시를 적용해 옵션을 생략했고, 전역 Codex 설정 `model_reasoning_effort = "xhigh"`가 그대로 적용된 배치 문제를 인정했다. 현재 진행분은 임의 재시작·중복 실행 없이 회수하며 향후 추가 배치에는 사용자 최신 역할별 선택 원칙을 적용한다. 전역 설정을 수정하지 않았다.

## Atlas 추가 산출물

네 최종 보고서에 R1/R2/R3를 반영하고, `D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_RECEIVER_REVIEW.md`를 새로 작성한다. 동명 파일이 있으면 실행별 이름을 사용해 덮어쓰지 않는다. 송신 S1–S4 PASS는 재검증과 구분하며, S5 부분·311/336·지역 레벨 조건·포인트 원천 미확인을 유지한다. 기술 추출 가능성과 상용 권리 확인을 분리한다.

완료 수락은 보고서와 근거 검토 뒤에만 한다. 사용자가 지정한 공식 settlement/release 흐름을 사용하며 다른 프로세스나 작업트리를 종료·삭제하지 않는다.

## 사용자 중단 지시와 medium 후임 인수

사용자가 하위 작업자뿐 아니라 중간 책임자도 역할별 모델/effort로 교체하라고 지시했다. 기술 `ctx_30a92ca0cdb6`와 개인용 Atlas 후속 `ctx_c2a10749908a`는 공식 worker-stop으로 종료됐다. 후임의 worker-show에서 둘 모두 worker state stopped, dispatch failed/lastFailure stopped, liveness exited/source worker_stop을 확인했다. 이 중단 이력을 성공으로 소급 변경하지 않는다. 최초 개인용 `ctx_181fcc75a1fe`는 succeeded/completed로 유지되며 터미널 정리 소유권은 후속 Dispatch로 이미 이전됐다. 상용화 `ctx_058c95b1d793`는 succeeded/completed/released이고 재배치하지 않았다.

후임은 인계문 전체, 적용 AGENTS, orchestration/orca-cli SKILL 및 선택 CLI `orca`의 live guide와 takeover/messaging/placement/coordinator/recovery reference를 읽었다. 제품 코드·모델 전역 설정을 수정하지 않았고 새 checkout·전체 실사·재테스트·추출을 수행하지 않았다.

### 인수·실행 증거의 수준

| 사실 | 증거 | 직접 관측/전달 구분 |
|---|---|---|
| 기존 Run 인수 | `orca orchestration run-use --id run_a35fcc129e02 --json`; receipt `612b9d51-cad9-4677-a310-e6651d6115e2`, mutation `ddb83015-9da2-475a-b6fc-aacbb00823b3`; coordinator=후임, consumer_generation=2, updated_at=2026-09-21T10:31:13Z | 후임 직접 성공 receipt 확인 |
| 후임 model/effort | HQ `msg_1deb6fefa134`: 본부가 10:31 UTC exact terminal read에서 `gpt-6-astra medium` 실제 표시 확인 | 본부의 독립 TUI 관측을 받은 사실. 후임 terminal show에는 model/effort 필드가 없어 그 출력으로 증명했다고 주장하지 않음 |
| 후임 launch/시작 | HQ가 이전 책임자 `msg_7ac814a04863`을 전달: `codex --model gpt-6-astra -c model_reasoning_effort=medium`, send request `81206117-d562-4daa-9adc-ad8b2c99eb74`, accepted true, input_accepted/turn_started | 원 create/send JSON을 후임이 직접 열람한 것은 아님. 기존 책임자의 실행 보고와 HQ 관측을 연결 |
| HQ 인수 재확인 | HQ run-show receipt `393d56fc-fba0-4914-84be-46b714f0627e`, 동일 handle/generation | HQ 전달 증거 |
| 이전 책임자 종료 | HQ exact terminal close receipt `a8f54e0c-191c-4dac-ba74-bf4901f5e641`, 이전 handle만 ptyKilled true | HQ가 목록 재확인 후 수행했다고 `msg_1deb6fefa134`로 보고. 후임은 종료하거나 재위임하지 않음 |

인수 직후 HQ에 `msg_074b9a192a39` status를 보냈다. 기존 수락 메시지 `msg_667da477bacb`는 새 generation의 delivery `delivery_1f96bb303370`로 받아 처리 후 ack했다. HQ 후임 수락 `msg_307eee3bc22e`와 증거 `msg_1deb6fefa134`도 처리 후 ack했다. 활성 Dispatch가 없는 책임자가 worker_done을 가장하지 않고 HQ에는 status만 사용한다.

### 최소 후속 배치와 편집 소유권

기존 넓은 실사 spec를 그대로 재시도하지 않도록, 동일 기술 worktree에 **보고서 편집만** 담당하는 새 Task `task_cda112ace434` / Dispatch `ctx_a34d1f00696c`를 만들었다. 이는 이전 중단 Task의 재실사 성공 처리가 아니며 보존 증거를 최종 문서로 만드는 후속 소유권이다. 재귀 위임·실행 검사·추출·브라우저 실행·제품 변경을 금지했다.

- worker terminal: `term_025c5ea6-a649-4916-a02f-3fb2576d57e1`.
- start receipt `a66e42bd-47b1-45cb-a5e3-de800ff18517`: launch requested/effective 모두 `codex / gpt-6-astra / medium`, state ready, turnStart observed.
- prompt/mutation request `f89cbf9c-2636-4347-9166-25ec585aa6d6`, stages `input_accepted`, `turn_started`; 새 worktree/설치 없음.
- 기술 작업자는 자기 `technical.md`만 편집. 후임은 종합 보고서·수신 검토서·감독 기록·취합 개인용 사본만 편집한다. 상용화 수락본은 그대로 유지한다.
- 개인용 작업자 원본 SHA-256 `75EBBD5508A99E4CE90607BBB2CAC21287DF63AAA363C2DA8B39EB2F76BD8EFA`를 보존하고 overwrite=false로 취합했다. 취합 사본의 계약에서 selectedScope/pointPool/encounter/unlock 및 선택 범위 내부 재생을 명시적으로 보완했으므로 최종 사본 해시는 원본과 달라진다.
- HQ `msg_bfea8520461d`로 명시적 medium receipt와 소유권을 보고했다. HQ `msg_1deb6fefa134`는 이 최소 배치를 확인하고 추가 조사 없이 산출물에 집중하도록 답했다.

### 보존 증거 대조와 범위

후임은 개인용 R2 명령·집계·해시, 상용화 수락 보고서, 기술 `.audit-readiness/ggpk-read.log`, `atlas-tables.log`, `atlas-tables-prefix.log`를 읽었다. prefix 로그의 EN/KO 537 ID 대응·영문 530명 일치·7루트 빈 이름은 반영하되 actual stride487/schema392, PSG 의미·좌표·링크·선택형·조건 미완료를 유지했다. R1 인코딩 보정 조건과 R2 구조 PASS는 제품 통합/게임 유효성/권리 PASS로 확대하지 않는다.

HQ `msg_20176b7e743d`의 임시 서버 정리 요청에 따라 10:34 UTC `Get-NetTCPConnection -LocalPort 7928 -State Listen`을 확인했고 listener 결과가 없었다. `serve_atlas.py`는 dynamic port=0이므로 이 확인만으로 다른 포트의 서버 종료를 단정하지 않는다. 보존 transcript의 종료 기록 확인을 기술 편집 작업자에게 요청했으며 프로세스를 이름으로 찾거나 종료하지 않았다.

## 최종 수락과 정리

10:38 UTC 후속 기술 `msg_1aea9b380743` worker_done succeeded를 받았다. 후임은 보고서의 실행 범위·명령·안전 harness·R1/R3와 보존 Python/GGPK 로그를 대조해 보고서 편집 완료를 수락했다. 기술 원본 보고서를 overwrite=false로 취합했다. R1 원시 transcript는 `session_not_reported`, terminal fallback 0행으로 회수되지 않았다는 한계를 종합·Docs에 명시했다. 프런트엔드 115 테스트/빌드 결과도 기존 실행 보고를 승계한 것이며 후임이 재실행한 결과가 아니다. HQ `msg_66978b977c41`의 동일 경계 요구를 처리하고 ack했다.

| Task / Dispatch | 최종 outcome와 납품 책임 | 정리 receipt |
|---|---|---|
| task_9076d3c085bf / ctx_30a92ca0cdb6 | 사용자 중단 failed/stopped 유지. 보존 기술 결과의 문서 보완은 새 Task가 담당 | `a71651aa-a512-4173-a978-2b9a909496ef`: released, processAction none, archive unavailable |
| task_1d7873da8938 / ctx_181fcc75a1fe | 최초 개인용 succeeded/completed 수락 유지. 터미널은 아래 후속 Task가 소유 | 초기 행의 retained/missing_status는 별도 살아 있는 worker가 아님. resource absent, nextAction none이며 후속 exact resource가 해제됨 |
| task_d8b58bc9e030 / ctx_c2a10749908a | 사용자 중단 failed/stopped 유지. R2 보존 결과·개인용 취합 사본의 UX 보완은 후임 책임자가 수락 | `9365be2b-d092-49b7-9fcb-3a5e8c27174b`: released, processAction none, archive unavailable |
| task_1f68bd784579 / ctx_058c95b1d793 | 상용화 succeeded/completed 수락 유지, 원본과 취합본 SHA 동일 | 기존 released 재확인; 재시작·재실사·수정 없음 |
| task_cda112ace434 / ctx_a34d1f00696c | 보고서 편집 succeeded/completed; worker_done msg_1aea9b380743 수락 | `e4812b3d-c91e-42f7-be65-28d140e86418`: released, closed_agent_terminal, transcript captured |

중단된 두 작업은 사용자 요청에 의한 중단 결과를 수락한 뒤 worker-show/list의 literal nextAction에 따라 worker-release로 자원 소유권을 정리했다. 이미 닫힌 프로세스를 다시 종료하지 않았다. 정리 조회 `orca orchestration worker-list --run run_a35fcc129e02 --terminal-state reclaimable --json` receipt `5f035b51-7791-4c92-8c6f-1bebbf13bb82`는 workers=[], total0을 반환했다. 원시 기록 미회수는 남겨 두며 자료 완성을 주장하기 위해 실행을 반복하지 않는다.

동적 포트 검증 서버는 실제 포트/PID·종료 기록을 복구하지 못했다. 7928 listener 부재 외의 종료는 미확인이며, 소유권 불명확 프로세스에는 조치하지 않았다. 이는 제품 검증 미완료와 별개의 환경 정리 한계다.

최종 납품은 네 보고서와 Atlas 수신 검토서다. 네 보고서의 원본 평가 폴더 내 사본은 `D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/`에 덮어쓰기 없이 복사하고 `delivery_manifest.json`의 SHA-256으로 취합본과 대조한다. 감독 기록과 수신 검토서 사본도 근거로 동봉한다. 제품 완성/상용 승인 및 새PC·IPC·실제 저장/재열기·R3 의미 대체 등 후속 구현 게이트는 완료로 처리하지 않는다.
