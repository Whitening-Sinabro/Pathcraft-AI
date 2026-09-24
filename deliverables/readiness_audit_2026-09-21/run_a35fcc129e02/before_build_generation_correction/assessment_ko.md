# Pathcraft-AI 개인용·상용화 준비도 종합 판단

평가일: 2026-09-21, Asia/Bangkok. 평가 대상은 커밋 스냅샷이 아닌 **현재 실제 `D:/Pathcraft-AI` 전체 폴더**다. 최신 `build_planner/`, `deliverables/`, `.claude/`, `Docs/`의 미커밋·미추적 자료를 포함했다. 전체 폴더를 평가 범위로 삼았으나 모든 파일·영상·의존성을 전수 검사한 것은 아니다. 세 분야 작업자가 실제 호출 경로와 대표 개인 산출물을 추적했고, 책임자는 보고서·선정 원본·실행 로그·공식 정책을 대조했다. 다른 세션의 변경이 진행 중이므로 원자적 동결 스냅샷으로 해석하면 안 된다.

## 1. 요청에 대한 판단

| 질문 | 판단 | 이유 |
|---|---|---|
| 지금 폴더에 있는 그대로 상용 판매 가능한가? | **판매 보류. 현재 상태의 유료 완제품 출시는 권고하지 않는다.** | 고객 PC에서의 설치·완주 증거, 입력 오류와 저장 계약, 데이터 사용 권한, 키·개인정보 처리, 실제 과금·사용량·지원 운영이 미완결이다. 설치 파일이나 README 완료 표시는 이를 대신하지 못한다. |
| 처음 목표한 개인용 빌드 플래너·가이드로 발전시킬 수 있는가? | **가능성이 충분하며 목표를 유지하는 것이 타당하다.** | 실행되는 파서·코치·검증 코드, 단계별 `.build`, 전환 조건과 출처가 있는 한국어 가이드, HC Journey 및 아틀라스 레퍼런스가 있다. 새 제품으로 갈아엎기보다 이 자산을 한 사용자 흐름으로 연결할 근거가 있다. 다만 개발 성공·HC 안전·유료 수요를 이미 증명한 것은 아니다. |
| 지금 개인적으로 무엇을 쓸 수 있는가? | **선정 빌드의 문서·게임 플래너·별도 HTML을 수동으로 대조하는 보조 환경.** | POE1 앱은 리서치→PoB→가이드 호출이 더 연결돼 있고, 최신 POE2 자료는 별도 생성·추적·여정 경로의 비중이 크다. 일반 사용자가 앱 하나에서 입력→현재/목표 비교→다음 행동→저장·재열기를 끝내는 제품은 아직 입증되지 않았다. |

현재 가장 강한 가치 후보는 **“내 상태에서 다음 단계로 언제, 왜, 어떤 조건을 갖추고 넘어갈지 근거와 함께 알려주는 한국어 도우미”**다. 단순 AI 답변이나 파일 개수보다 전환 조건·출처·패치·HC/SSF를 사용자 상태에 맞게 보존하는 것이 핵심이다. 초기 PRD의 Why·레벨링·SSF/HC 목표와도 맞는다. [초기 PRD](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:16), [현재/목표 흐름의 상세 평가](personal_product.md).

## 2. 이미 있는 것과 아직 연결되지 않은 것

| 축 | 실제 자산·구현 | 미완결 또는 검증 한계 |
|---|---|---|
| POE1 앱 | React→Tauri→Python의 소스 해석·PoB 파싱·코칭·가이드 표시·localStorage 히스토리 | 실제 Tauri 창/IPC/AI/재시작 전체는 미검증. 파서는 저장된 PoB 수치를 읽으며 독립 전투 계산 엔진이 아니다. |
| POE2 개인 플래너 | 실제 `.build`, 현재 캐릭터·제작자 자료, 한국어 단계 안내, 정정·불확실성 기록 | 앱 구두 입력과 이 자산의 importer/현재·목표 비교가 연결돼 있지 않다. 문서의 ‘내’ 이름이 실제 사용자 장착 상태를 보증하지 않는다. |
| HC Journey | 스냅샷·변경·규칙·전환 노트·SQLite·HTML. 임시 DB에서 creator 8, snapshot 41, transition 33, note 114 재현 | 제작자 순차 자료와 사용자 목표를 구분해야 한다. 장비 첫 줄·패시브 개수 중심 비교는 같은 베이스의 옵션 변경·같은 점수의 노드 재배치를 놓칠 수 있다. |
| 아틀라스 | 단계 칩·순번·재생·목록 이동을 제시하는 로컬 HTML 및 트리/순서 JSON | 현재 앱에 통합된 기능과 다르다. 브라우저 인수 결과, 그래프 검증, 원천 교체 및 권리는 §5에서 별도로 판정한다. |
| 파밍·제작 안내 | 가이드 결과·연구 문서·전환 비용 사례가 존재 | 사용자 보유 재료/예산/모드에 맞춘 파밍·제작 계획까지 하나의 검증된 루프로 완결됐다는 증거는 없다. |

근거: [앱 입력 분기](D:/Pathcraft-AI/src/App.tsx:933), [코칭 호출](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:275), [등록 명령](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152), [Journey 축약](D:/Pathcraft-AI/python/hc_journey/build_db.py:73), [전환 근거·정정 사례](D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/교차검증_정정.md:48). 원본의 옛 WPF·유료 티어·‘자동 100%’ 문구는 완료 증거로 사용하지 않았다.

## 3. 실제 실행 검증과 결함

테스트·빌드는 부작용을 검토한 구현 담당 한 명만 수행했다. 책임자는 테스트를 중복 실행하지 않고 실제 로그와 원본을 대조했다.

| 검증 | 결과 | 범위 |
|---|---|---|
| TypeScript `tsc --project D:/Pathcraft-AI/tsconfig.json --noEmit --pretty false` | exit 0, 진단 0 | 설치된 원본 의존성으로 검사 |
| Vitest `startVitest('test',['src'],…)` | **13개 파일, 115 passed / 0 failed** | 기존 src 테스트; 저장·재시작 E2E 아님 |
| Vite `build(…)` | exit 0, 165 modules | 원본 config/소스, 키 로드 차단, 임시 외부 출력; 일반 prebuild·Tauri 패키징 제외 |
| Python 핵심 18개 파일 | **176 passed / 0 failed / 1 skipped** | 키·네트워크·subprocess 차단, 원본 밖 임시 출력 |
| Python Journey 2개 파일 | **13 passed / 0 failed** | DB_PATH만 메모리에서 임시 DB로 바꿈; assertion/제품 코드 수정 없음 |
| `.build` 216개 메모리 검사 | JSON 216개 읽음, validator 215개 완료, 1개 예외 | 예외는 트리 전용 파일의 `skills` 부재. 파일 손상/게임 실패로 단정하지 않음 |
| 실제 원본 Python CLI 진입 | 정상 샘플 parser·corpus 실행; 깨진 XML에 **null + exit 0** 재현 | runpy 기반, Rust IPC 또는 실제 외부 URL 검증 아님 |

자동 테스트 합계는 **304 passed / 0 failed / 1 skipped**다. 선택한 범위의 결과이며 전체 저장소·앱 완주 합격률이 아니다. Python 137개 테스트 파일 중 20개를 실행했고 나머지는 미검증이다. skip은 게임 폴더의 기준 파일 부재 때문이다. 잘못된 pobb.in 조회와 Wiki 조회 2건은 연결 전에 차단되어 fallback 처리됐다. 최초 안전 실행기의 로그 출력 경로 오류(exit 3, 테스트 0개)는 격리 경로 설정 후 해소됐으며 제품 테스트 실패와 구분했다. 상세 명령·환경·실행기는 [technical.md](technical.md)에 있다.

일반 build는 사전 번역 생성이 원본 JSON을 쓰므로 그대로 실행하지 않았다. Cargo/Tauri는 target-dir 외의 원본 `gen/schemas` 쓰기 경로가 있어 실행하지 않았다. 따라서 **Rust/Tauri 빌드·설치·실제 IPC·AI 응답·전체 UI 저장/재열기·게임 로드/전투는 미검증**이다. [build 설정](D:/Pathcraft-AI/package.json:8), [번역 쓰기](D:/Pathcraft-AI/python/extract_passive_tree_translations.py:175), [Rust build 진입](D:/Pathcraft-AI/src-tauri/build.rs:2).

중요한 제품 결함은 다음과 같다.

1. **저장·게임 맥락:** 히스토리 저장은 PoB 링크가 비면 반환한다. 새 POE2 구두 입력은 링크가 없고, 이전 링크가 있는 경우 closure 때문에 잘못된 키에 저장될 수 있다. SavedBuild에 game도 없어 양 게임 전환/복원 시 혼합 가능성이 있다. 이는 정적 코드 판정이며 UI에서 재현한 것으로 주장하지 않는다. [저장 조건](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:158), [구두 입력](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:368), [저장 스키마](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:5).
2. **오류 경계:** 잘못된 XML을 성공 exit로 돌려보내며, 이후 Rust와 프런트가 성공으로 취급할 여지가 있다. AI 호출·저장 이전에 명시적 오류로 중단돼야 한다. [파서 예외](D:/Pathcraft-AI/python/pob_parser.py:453), [CLI 종료](D:/Pathcraft-AI/python/pob_parser.py:487), [Rust 판정](D:/Pathcraft-AI/src-tauri/src/lib.rs:99).
3. **패치·모드·한영 일관성:** POE2 앱 트리는 0.4, 플래너는 0.5 캐시, 젬 목록은 0.4.0d이며 최신 자료와 버전 계약이 다르다. HC/Trade/SSF·미확인을 분리하고 미해결 한영 이름은 사용자 검색으로 풀어야 한다. [UI 트리](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:34), [젬 메타](D:/Pathcraft-AI/data/valid_gems_poe2.json:3), [구두 입력 구조](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378).
4. **배포·운영:** PATH의 Python과 프로젝트 폴더 탐색에 의존하고 현행 Python/data 번들·잠금 의존성 계약이 부족하다. 7월 미서명 설치물 두 개의 존재는 현재 원본의 새 PC 실행 증거가 아니다. [실행 경로](D:/Pathcraft-AI/src-tauri/src/lib.rs:51), [번들 설정](D:/Pathcraft-AI/src-tauri/tauri.conf.json:49).

## 4. 상용 판매를 막는 별도 조건

현재 README의 유료 티어·Fine-tuned 모델·OAuth 승인·무제한·환불·우선지원은 운영 사실로 입증되지 않았다. 크레딧 함수는 Mock이며 차감한 잔액을 영속 저장하지 않는다. 기존 OAuth 코드에는 고정 state/검증 누락, 민감 응답 로그, 평문 토큰 저장 경로가 있다. 이 OAuth가 현 Tauri UI에 연결됐다고 단정하지 않지만, 판매 기능으로 내세우려면 제외 또는 보완·검증이 필요하다. [Mock 잔액](D:/Pathcraft-AI/python/build_guide_generator.py:349), [차감](D:/Pathcraft-AI/python/build_guide_generator.py:373), [OAuth state](D:/Pathcraft-AI/python/poe_oauth.py:138), [로그](D:/Pathcraft-AI/python/poe_oauth.py:192), [저장](D:/Pathcraft-AI/python/poe_oauth.py:436).

**데이터 접근과 재판매 권한은 기술 동작과 별개다.** 현재 캐릭터 추적기는 poe.ninja의 내부 character endpoint를 쓴다. 공식 API 문서는 builds/profiles/character 등의 비경제 endpoint를 제3자용으로 제공하지 않는다고 명시한다. 이 경로는 별도 허가 또는 허용된 입력 경로로 대체해야 한다. [현재 추적기](D:/Pathcraft-AI/scripts/track_poe2_character.py:74), [공식 poe.ninja API 정책](https://poe.ninja/docs/api), 확인 2026-09-21.

GGG는 상업적 IP 사용과 게임 파일 상호작용에 대한 제한을 공지한다. Mobalytics도 허용되지 않은 상업적 이용 제한이 있어 플랫폼 조건과 제작자 권리를 나눠 확인해야 한다. **개별 허가 미확인을 허용 또는 위법 확정으로 바꾸지 않는다.** 직접 GGPK에서 얻을 수 있다는 사실만으로 판매 권리를 확보한 것은 아니다. [GGG 개발자 정책](https://www.pathofexile.com/developer/docs), [공식 Data Exports](https://www.pathofexile.com/developer/docs/data), [Mobalytics 약관](https://mobalytics.gg/terms/), 확인 2026-09-21. 방송·자막·위키·필터·PoB·스키마별 상세 공식 URL, 가격·보존 조건과 한계는 [commercialization.md](commercialization.md)에 있다.

## 5. 아틀라스 인수 검증

송신 S1–S4 PASS와 수신 검증을 분리해 아래처럼 수락한다. 이번 후임은 보존된 보고서·실행 로그를 검토했으며 재테스트·추출을 하지 않았다.

| 수신 항목 | 최종 판단 | 확인 범위와 한계 |
|---|---|---|
| R1 브라우저 | **기존 실행 보고 수락, 인코딩 조건부** | 기존 기술 작업자의 실제 Playwright MCP 조작 보고를 인계문·메시지 ID로 보존했다. 종료 세션의 원시 출력은 회수되지 않아 후임이 세부 assertion을 직접 대조하지 못했다. localhost 원시 HTTP에서는 UTF-8 charset/meta 누락으로 EUC-KR 해석이 발생했고, 원본 수정 없이 응답 charset을 UTF-8로 지정한 기능 검사와 구분한다. 현재 배포 방식 전체·Tauri 통합 합격은 아니다. |
| R2 구조 | **PASS** | 기존 개인용 작업자의 노드 537/그룹 255, 루트 7 제외 530/중복 0, 메인 336+콘텐츠 194, 초반 58 루트 연결·11목표 포함 및 트리별 prefix 연결 검사. 실제 획득 가능 포인트·위험 정확성을 증명하지 않는다. |
| R3 원천 교체 | **부분, 상용화 보류** | 기존 GGPK에서 PSG 2개와 EN/KO PassiveSkills 2개 선택 추출. 보존 prefix 로그는 EN/KO 각 537 ID 대응, 영문명 530/537 일치(7루트 빈 이름)를 보인다. 실제 행 487바이트와 스키마 392바이트가 달라 선두 ID/GraphId/Name 이외 의미 해석은 미확인. PSG 좌표·링크·옵션·조건을 포함한 완전한 대체와 상용 권한은 미완료. |

S5 위험분류 부분 상태, 서브트리/58 이후 순서 적대검증, 311 대 336 포인트, 지역 레벨 70/75 조건, 0.5.5 포인트 출처는 미해결로 유지한다. 초록 191개는 메인 58+콘텐츠 133의 표시 집합이며, 메인 초록에도 위험 라벨 3개가 있으므로 안전 인증이 아니다. [수신 검토서](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_RECEIVER_REVIEW.md), [R3 보존 로그](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/atlas-tables-prefix.log:1).

**사용자의 최신 UX 보정:** 초록 단계 진행 중 어떤 콘텐츠를 만날지는 다르므로, 의식→다른 콘텐츠처럼 모두에게 의무인 순서로 보이면 안 된다. 메인 트리 진행과 의식·균열·탐험 등 **독립 콘텐츠의 내부 배정 순서**를 분리한다. 각 콘텐츠는 해금·보유 포인트·사용자 선택을 확인한 뒤 자기 내부 순서를 보여 주며, 전역 번호나 ‘전체 재생’으로 의식 우선 플레이를 암시하지 않는다. 이는 이번 보고서의 설계 기준이며 제품 UI는 수정하지 않았다.

## 6. 개인용 완성 → 소규모 검증 → 유료화

| 순서 | 수행할 일 | 다음 단계 통과 조건 |
|---|---|---|
| **1. 개인용 한 흐름 완성** | 한 게임·한 빌드·한 전환 구간을 고정하고 현재/목표 입력, 실제 차이, 조건부 다음 행동, 출처, 저장·복원을 연결한다. 최근 개인 사용을 기준으로 하면 POE2 현재 젬링 자료를 첫 후보로 권고한다. POE1 우선이라면 기존 앱 연결을 활용한다. | 개발자 터미널 도움 없이 실제 사용자 자료로 입력→비교→행동/보류→종료→재열기를 연속 수행. 게임/패치/HC·Trade·SSF가 섞이지 않고 옵션·노드 차이를 보존. 없는 이름·조건·스탯은 미확인 표시. API 실패·깨진 입력에도 상태를 잃지 않음. |
| **2. 소규모 비공개 검증** | 권리 확인된 자료/자기 export만 담은 배포 후보, 키 없는 설치물, 지원 가능한 한정 범위를 준비한다. 독립 사용자가 같은 과제를 수행하는지 관찰한다. | 개발 도구 없는 새 Windows 환경에서 설치·사용·저장·재열기·삭제/복구 재현. 사용자 스스로 다음 행동과 멈출 이유를 설명. 중대한 패치·HC·SSF 오판을 해결하고 재확인. 개인정보·비용·신고/정정 흐름 확인. |
| **3. 유료화 승인** | 상품/지원 범위, 권리 대장, BYOK 또는 사업자 부담 모델, 실제 결제·권한·원장·상한·환불을 준비한다. | 출시 자료의 이용 범위 근거, 비밀 없는 배포/안전 저장/전송·삭제 검증, 모든 재시도 비용 합산과 지출 차단, 결제→권한→해지/환불 시험, 패치·장애·지원 책임, 기존 대안 대비 추가 가치의 사용자 증거 확보. |

아틀라스는 이 흐름 안에서 **현재 배정/목표 순서와 근거를 보여 주는 축**으로 연결한다. 입력 캐릭터 정보가 없는데 보편적인 HC 최적 경로라고 단정하거나, 제작자 장착품 전부를 사용자 필수품으로 바꾸면 안 된다. 파밍·제작도 같은 현재 상태·획득 가능성·조건 모델을 공유해야 한다. 새 크롤러·자료 확장·범용 AI·전 게임 지원을 먼저 늘리기보다 선정 흐름의 완결을 우선한다.

## 7. 필요한 결정과 납품 상태

이번 실사는 판단·문서 작업이며 구현을 시작하지 않았다. 다음 구현 착수 때 정할 사항은 **첫 게임/대표 빌드**, **사용할 데이터 원천과 권한 범위**, **사용자 키 방식 또는 사업자 API 비용 부담 방식**이다. 유료화 전에 대상 시장·연령, 지원·환불 책임도 확정해야 한다. 지금 반복 승인 요청을 할 필요는 없으며 위 결정 없이 판매 준비 완료라고 선언해서도 안 된다.

최종 네 보고서는 `assessment_ko.md`, `technical.md`, `personal_product.md`, `commercialization.md`다. 원본 평가 폴더의 실행별 납품 위치는 `D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/`다. 복사 시 기존 동명 파일을 덮어쓰지 않고 SHA-256으로 대조한다. 감독 provenance·사용자 요청 중단 이력·후임의 보완 수락과 정식 release 결과는 [supervision_log.md](supervision_log.md)에 기록한다. 중단된 실사 Task를 성공으로 소급 변경하지 않으며, 보존 결과를 이어 최종 보고서를 완성한 것과 실제 제품 미완료를 구분한다.
