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

## 사용자 목표 교정 후 생성 준비도 보완 — 앞선 납품의 개정

10:44 UTC HQ `msg_772967ca820d`가 사용자의 직접 교정 “PoB는 부가적이고 자료를 모은 목적은 빌드를 만들어 주는 것”을 전달했다. 앞선 분석·현재/목표 비교 중심의 최종 수락은 보류됐다. `msg_f913529f2b19`에 따라 기존 검증 자료의 조건부 조합·변형도 생성으로 인정하며, 세상에 없던 메타 발명으로 요구를 확대하지 않는다. 후임은 제품 목표를 되묻지 않고 그 기준으로 좁은 정적 읽기와 보고서 개정을 수행했다. 이 절 이후의 개정판이 앞선 납품판에 우선한다.

### 실제 배치와 수락

- Task `task_06590f8efd27` / Dispatch `ctx_0deaebf4f7e3`, terminal `term_2577eb11-18c3-4da3-ae28-b6083a005105`, 동일 기술 worktree. 추가 작업자 1명, 재귀 위임 없음.
- start receipt `c8ba85d6-475f-4445-85da-83a0e0585034`: requested/effective 모두 `codex / gpt-6-astra / medium`; ready, turnStart observed; prompt `ae14f348-f18e-4d0b-84f1-fd656949abc9`, input_accepted/turn_started. 책임자도 medium 유지.
- worker 소유 파일은 `readiness-technical-20260921/build_generation_readiness.md` 하나. 기존 네 보고서와 canonical 납품판은 책임자가 수정했다.
- 완료 `msg_861c6235b0bf`(10:52:42 UTC), outcome succeeded. 보고서 전문과 knowledge_router/coach 입력·정규화·경고, 추천 예산·자산 기본값, planner의 PoB 변환, build_instance stats 경로를 책임자가 읽어 대조한 뒤 수락했다.
- release receipt `bf80211b-55f5-4e43-8dc7-7eafb14ffb41`: released, closed_agent_terminal, transcript captured. 성공 Task를 별도 task-update로 변경하지 않았다.
- 중간 발견 요청이 완료와 교차해 `dispatch_inactive`로 거절됐다. 이를 전달 성공으로 취급하거나 같은 worker를 재시작하지 않았고 도착한 정식 worker_done을 처리했다.

### 개정 내용과 증거 범위

자료는 단순 보관뿐 아니라 source/patch 팩·지식 router·정규화/추천으로 일부 연결돼 있다. 그러나 해당 router의 coach 연결은 POE1 한정이고, 추천·코칭 문맥·기존 PoB 변환과 조건부 완성 구성 생성은 다르다. 입력 stats screening은 생성·수정 결과의 성능 재계산이 아니다. 이름/ID 검사·경고·1회 교정을 자원·포인트·지원호환·확보·전환의 통합검증으로 확대하지 않았다. PoB 없는 입력의 독립 저장과 구성 수정 후 재검증/리비전도 미완료로 남겼다.

종합 보고서의 목표·가치·최소 마일스톤·필요 결정, 개인용 보고서의 최소완결 6단계·G1·최종판단, 기술 보고서의 핵심 판정·§6, 상용화 보고서의 생성 품질 P0·비공개 검증 과제를 본문에서 고쳤다. 상용화 권리/시장/가격 조사는 재수행하지 않고 책임자 개정만 추가했다. Atlas는 생성 빌드의 보조 진행 플래너로 위치를 고쳤으며 R1/R2/R3와 콘텐츠 간 의무순서 금지 계약은 유지했다.

기존 304 선택검증·Atlas 증거의 사실과 한계는 그대로다. 새 테스트·빌드·API·브라우저·GGPK·대량 추출/집계를 하지 않았고 제품코드/전역설정은 수정하지 않았다. 자료 정규화 비율·생성품질·DPS·완성률·기간·매출을 추정하지 않았다. 특정 게임·클래스는 완료된 사용자 결정으로 취급하지 않고 후속 생성 지원 범위 제안으로 남겼다.

### 개정 납품 및 HQ 보고

앞선 source/canonical 보고서와 manifest는 각 `before_build_generation_correction/`에 overwrite=false로 보존했다. HQ의 명시적 canonical/manifest 갱신 요청에 따라 기존 납품파일의 이전 해시를 확인한 뒤 개정판으로 갱신한다. `build_generation_readiness.md`는 worker 원본을 보존하고 책임자 취합 사본에 짧은 자료→지식→구성→검증→앱/저장 연결표를 보완했다. 최종 source+canonical SHA-256과 인용 경로는 갱신 manifest로 대조한다. 이전 상용화 hash는 역사적 수락본의 값이고, 이번 목표 보완판은 새 hash를 갖는다.

착수 교정 회신 `msg_2198b3dc27e3`는 reply였고 HQ가 Run inbox 직접 status를 요구했다. 이후 `msg_73cf87d942d5`(배치), `msg_37e59b251b1c`(진행), `msg_2ded4a6cd17b`(수락·단절)로 `run_debe30e1db10`에 직접 status를 보냈다. 5분 보고가 늦어져 본부의 재촉을 받은 사실은 숨기지 않는다. 최종 제품 평가의 사용자 종합보고 책임은 최신 HQ 지시에 따라 HQ가 맡으며, 후임은 개정 산출물·검증·정리 완료를 HQ에 전달한다.

최종 HQ 검수 `msg_a58f3e378773`, `msg_591a3b6d46df`를 수락해 판매보류 첫 이유를 완성 구성 생성·통합검증 미완결로, 납품을 생성보고서 포함 5개로 정정했다. 최종 reclaimable 조회 receipt `7896c548-1350-46b4-92b7-93702c0f6edf`는 workers=[], total0, retained1/released5다. retained는 이미 자원이 없는 최초 개인용 이력이며 새 작업자를 의미하지 않는다. 이전 canonical 6문서의 manifest hash와 백업 byte 동일성을 확인한 뒤 개정 7문서를 복사한다. 최종 복사 동일성·로컬 링크 결과는 동봉 manifest의 verification에 기록한다.
