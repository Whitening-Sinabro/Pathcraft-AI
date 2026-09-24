# Pathcraft-AI 자료 기반 빌드 생성 제품 준비도 종합 판단

평가일: 2026-09-21, Asia/Bangkok. 평가 대상은 커밋 스냅샷이 아닌 **현재 실제 `D:/Pathcraft-AI` 전체 폴더**다. 최신 `build_planner/`, `deliverables/`, `.claude/`, `Docs/`의 미커밋·미추적 자료를 포함했다. 전체 폴더를 평가 범위로 삼았으나 모든 파일·영상·의존성을 전수 검사한 것은 아니다. 세 분야 작업자가 실제 호출 경로와 대표 개인 산출물을 추적했고, 책임자는 보고서·선정 원본·실행 로그·공식 정책을 대조했다. 다른 세션의 변경이 진행 중이므로 원자적 동결 스냅샷으로 해석하면 안 된다.

## 1. 요청에 대한 판단

**평가 목표는 모아 둔 자료를 활용해 사용자 조건에 맞는 빌드 구성과 성장 경로를 만들어 주는 제품이다.** PoB는 선택적 입력·출력·검증 수단이고, 기존 캐릭터 분석과 현재→목표 비교는 생성 후 수정·사용을 돕는 보조 기능이다. 검증된 기존 빌드·자료를 조합하거나 변형해 완성 구성을 만드는 것도 생성에 포함한다. 세상에 없던 메타 발명이나 모든 게임·클래스의 범용 최적화를 필수 조건으로 늘리지 않는다.

이 기준은 사용자의 최신 직접 교정을 HQ가 전달한 `msg_772967ca820d`, `msg_f913529f2b19`에 따른다. 이전 납품의 분석·비교 중심 프레이밍은 정정했다. 과거 [초기 PRD](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:16)는 분석·추천을, [architecture](D:/Pathcraft-AI/.claude/status/architecture.md:2)는 전체 로드맵 코치를 적고 [21행](D:/Pathcraft-AI/.claude/status/architecture.md:21)은 생성이 아닌 코치라고 적는다. 이 문서들을 근거로 현재 사용자의 목표를 축소하지 않으며, 과거 문서가 처음부터 일관된 생성 사양이었다고 주장하지도 않는다.

| 질문 | 판단 | 이유 |
|---|---|---|
| 지금 폴더에 있는 그대로 상용 판매 가능한가? | **판매 보류. 현재 상태의 유료 완제품 출시는 권고하지 않는다.** | **완성 구성 생성·통합검증 경로 미완결**, 고객 PC에서의 설치·완주 증거, 입력 오류와 저장 계약, 데이터 사용 권한, 키·개인정보 처리, 실제 과금·사용량·지원 운영이 미완결이다. 설치 파일이나 README 완료 표시는 이를 대신하지 못한다. |
| 자료 기반 개인용 빌드 생성 제품으로 발전시킬 수 있는가? | **재사용할 구현·자료 기반은 있다. 현재 완성된 생성 제품으로는 입증되지 않았다.** | 코칭 JSON과 자료 검색·추천·규칙 검증, 단계별 플래너·전환 근거가 있다. 그러나 사용자 조건을 반영한 스킬·지원젬·패시브·장비·자원·성장 단계의 일관된 구성을 만들고 검증하는 연결을 따로 확인해야 한다. 자세한 생성 경로와 자산의 연결 정도는 [생성 준비도 보고서](build_generation_readiness.md)를 따른다. |
| 지금 개인용 생성은 어디까지 가능한가? | **자료를 참고한 코칭·구성 초안과 기존 빌드 변환/추천을 활용하는 단계. 자동으로 검증된 완성 빌드를 받는 경험은 미완료다.** | POE2에는 PoB 없이 클래스·주력스킬·지원젬·메모로 코칭을 요청하는 경로가 이미 있다. 다만 구조화된 패치·예산·보유 자산·HC/SSF 입력과 통합 생성 검증은 별개다. 기존 문서·플래너의 수동 활용은 현재 가능한 보조 활용이며 최종 제품 목표를 대신하지 않는다. |

제품의 가치 후보는 **“내 조건과 모아 둔 근거 자료로 실행 가능한 빌드와 성장 경로를 만들어 주고, 그 구성의 이유와 바꿀 수 있는 범위를 설명하는 한국어 도우미”**다. 링크 검색·요약·복제만으로 생성 완료라고 하지 않으며, 이미 검증된 구성을 조건부로 조합·변형하는 방식은 유효하다. 전환 조건·출처·패치·HC/SSF·확보 가능성은 생성 결과의 제약과 검증 근거로 연결되어야 한다. [PoB 없는 입력](D:/Pathcraft-AI/src/components/VerbalBuildInput.tsx:4), [실제 코칭 호출](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378), [개인용 평가](personal_product.md).

## 2. 이미 있는 것과 아직 연결되지 않은 것

| 축 | 실제 자산·구현 | 미완결 또는 검증 한계 |
|---|---|---|
| 사용자 조건→빌드 생성 | 코치의 구조화 응답·자료 문맥, 기존 코퍼스 추천과 변환기 등 구성 요소 | 검색·추천·설명·변환과 새 사용자용 일관된 구성 생성을 분리해야 한다. 자료가 존재하는 것과 생성 경로에서 선택·변형·검증에 쓰이는 것은 다르다. [생성 연결 상세](build_generation_readiness.md) |
| POE1 앱 | React→Tauri→Python의 소스 해석·PoB 파싱·코칭·가이드 표시·localStorage 히스토리 | 실제 Tauri 창/IPC/AI/재시작 전체는 미검증. 파서는 저장된 PoB 수치를 읽으며 독립 전투 계산 엔진이 아니다. |
| POE2 개인 플래너 | 실제 `.build`, 현재 캐릭터·제작자 자료, 한국어 단계 안내, 정정·불확실성 기록 | 앱 구두 입력과 이 자산의 importer/현재·목표 비교가 연결돼 있지 않다. 문서의 ‘내’ 이름이 실제 사용자 장착 상태를 보증하지 않는다. |
| HC Journey | 스냅샷·변경·규칙·전환 노트·SQLite·HTML. 임시 DB에서 creator 8, snapshot 41, transition 33, note 114 재현 | 제작자 순차 자료와 사용자 목표를 구분해야 한다. 장비 첫 줄·패시브 개수 중심 비교는 같은 베이스의 옵션 변경·같은 점수의 노드 재배치를 놓칠 수 있다. |
| 아틀라스 | 단계 칩·순번·재생·목록 이동을 제시하는 로컬 HTML 및 트리/순서 JSON | 현재 앱에 통합된 기능과 다르다. 브라우저 인수 결과, 그래프 검증, 원천 교체 및 권리는 §5에서 별도로 판정한다. |
| 파밍·제작 안내 | 가이드 결과·연구 문서·전환 비용 사례가 존재 | 사용자 보유 재료/예산/모드에 맞춘 파밍·제작 계획까지 하나의 검증된 루프로 완결됐다는 증거는 없다. |

근거: [앱 입력 분기](D:/Pathcraft-AI/src/App.tsx:933), [코칭 호출](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:275), [등록 명령](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152), [Journey 축약](D:/Pathcraft-AI/python/hc_journey/build_db.py:73), [전환 근거·정정 사례](D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/교차검증_정정.md:48). 원본의 옛 WPF·유료 티어·‘자동 100%’ 문구는 완료 증거로 사용하지 않았다.

## 3. 실제 실행 검증과 결함

**생성 목표에서 가장 앞선 공백:** 구조화 지식 자체는 있다. 출처/patch 팩과 [knowledge_router.py:687](D:/Pathcraft-AI/python/knowledge_router.py:687)가 문맥을 고르고 [build_coach.py:1332](D:/Pathcraft-AI/python/build_coach.py:1332)가 POE1 코칭에 연결한다. 그러나 [추천 어댑터:164](D:/Pathcraft-AI/python/recommend_from_corpus.py:164)의 예산·자산 기본값, [기존 PoB 변환](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:484), [입력 stats 해석](D:/Pathcraft-AI/python/build_instance.py:445)은 각각 사용자 조건 기반 구성 생성·생성 결과 재계산과 다르다. 이름 정규화·경고·screening을 넘어 생성한 각 단계의 스킬/지원·패시브/포인트·장비/자원·확보/전환을 함께 검증하고 수정·저장까지 연결해야 한다. [연결/단절 표와 세부 근거](build_generation_readiness.md).

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
| **1. 최소 일관된 생성 범위 완성** | 사용자와 지원 게임·패치·빌드 계열·성장 구간을 정하고, 근거 있는 소수 구성을 조건에 맞게 조합·변형하는 생성기를 완결한다. 요청 조건→자료 선택→완성 구성→제약 검증→성장 경로→수정·재검증→저장·복원을 연결한다. 특정 게임·클래스는 이 평가가 임의 확정하지 않는다. | PoB 없이도 지원 범위 내 요청을 제출하고 스킬/지원젬·패시브·장비·자원·단계 전환이 서로 맞는 결과를 받음. 확인된 제약은 통과하고 충돌/미확인은 보류. 예산·보유품·모드 변경 시 관련 구성을 다시 만들고 검증. 각 구성의 출처·패치·변경 이유와 검증 범위를 추적하고 앱 재열기 후 유지. |
| **2. 소규모 비공개 생성 품질 검증** | 권리 확인된 자료로 독립 사용자의 대표 요청과 조건 변경 사례를 평가한다. 지원 밖 요청은 보류하며, 생성 결과의 실사용성·수정 가능성을 관찰한다. | 구성요소 이름의 유효성뿐 아니라 전체 조합의 자원·포인트·선행조건·확보 가능성·단계 전환 검증을 통과. 공격/생존 수치는 검증 방법·가정과 함께 제시하며 검증되지 않은 숫자는 미확인. 새 Windows 환경의 설치·저장·재열기 및 비용·정정 흐름까지 확인. |
| **3. 유료화 승인** | 상품/지원 범위, 권리 대장, BYOK 또는 사업자 부담 모델, 실제 결제·권한·원장·상한·환불을 준비한다. | 출시 자료의 이용 범위 근거, 비밀 없는 배포/안전 저장/전송·삭제 검증, 모든 재시도 비용 합산과 지출 차단, 결제→권한→해지/환불 시험, 패치·장애·지원 책임, 기존 대안 대비 추가 가치의 사용자 증거 확보. |

아틀라스는 **생성한 빌드의 성장·획득 계획을 돕는 보조 진행 플래너**다. 생성된 구성의 부족 재료와 목표 콘텐츠를 파밍·제작·아틀라스 계획으로 연결한다. 현재→목표 비교는 생성 결과의 개인별 수정과 전환을 돕되 생성기 자체의 대체 목표로 삼지 않는다. 입력 캐릭터 정보가 없는데 HC 최적 경로라고 단정하거나 제작자 장착품 전부를 필수품으로 바꾸면 안 된다. 자료 수를 더 늘리기보다 확인된 소수 자료가 실제 구성 생성과 검증까지 연결되도록 한다.

## 7. 필요한 결정과 납품 상태

이번 실사는 판단·문서 작업이며 구현을 시작하지 않았다. 다음 구현 착수 때 정할 사항은 **첫 생성 지원 범위(게임·패치·빌드 계열·성장 구간·허용 변형)**, **사용할 데이터 원천과 권한 범위**, **사용자 키 방식 또는 사업자 API 비용 부담 방식**이다. 생성 제품이라는 목표 자체는 이미 사용자가 명확히 했으므로 다시 물을 사안이 아니다. 유료화 전에 대상 시장·연령, 지원·환불 책임도 확정해야 한다.

최종 다섯 보고서는 `assessment_ko.md`, `technical.md`, `personal_product.md`, `commercialization.md`, `build_generation_readiness.md`다. 원본 평가 폴더의 실행별 납품 위치는 `D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/`다. 최초 납품은 overwrite=false로 복사·해시 대조했고, 아래 목표 교정판은 이전 판 보존 후 canonical을 갱신한다. 감독 provenance·사용자 요청 중단 이력·후임의 보완 수락과 정식 release 결과는 [supervision_log.md](supervision_log.md)에 기록한다. 중단된 실사 Task를 성공으로 소급 변경하지 않으며, 보고서 완성과 실제 제품 미완료를 구분한다.

사용자 목표 교정 후 [build_generation_readiness.md](build_generation_readiness.md)를 추가했다. 이전 납품판과 manifest는 `before_build_generation_correction/`에 보존하고, 이번 명시적 보완 요청에 따라 위 실행폴더의 canonical 다섯 보고서·감독 기록·수신 검토·manifest를 갱신했다. 기존 실험 결과와 상용화 조사 근거는 보존했으며 생성 연결에 필요한 좁은 정적 읽기만 추가했다.
