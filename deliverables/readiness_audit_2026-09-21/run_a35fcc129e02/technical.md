# Pathcraft-AI 현재 구현·실행 실사

**실제 원본 `D:/Pathcraft-AI`를 직접 읽고 실행했다. 기준 확인 시각: 2026-09-21 17:03:53 +07:00 (Asia/Bangkok).** 새 checkout의 제품 코드는 평가하지 않았다. 원본 HEAD는 `dd7a09a0b2237307b3ae44ad2ca6ee8be091a586`이나, 평가 범위에는 미커밋·미추적 파일이 포함된다. 실사 중에도 다른 세션이 원본 문서·산출물을 추가했으므로 이 결과는 원자적 스냅샷이 아니다.

최종 보고서는 이 `technical.md` 하나다. `.audit-readiness/`는 이 작업트리 안에 만든 임시 테스트 실행기·로그·빌드 출력·검증용 DB 공간이며 제품 기능이나 추가 납품물이 아니다. 원본 및 하위 작업트리 제품 코드는 수정하지 않았고, 설치·키 사용·유료 API·게임 쓰기·게시·프로세스 종료는 하지 않았다.

**후속 편집 이력:** 2026-09-21, Task `task_cda112ace434` / Dispatch `ctx_a34d1f00696c`에서 기존 증거만 읽어 이 보고서를 보완했다. 위 시각과 실행 결과는 기존 실사 Task `task_9076d3c085bf` / Dispatch `ctx_30a92ca0cdb6`의 기록이며 새 실행 시각이 아니다. 기존 Dispatch는 사용자 stop으로 종료됐다. 이번 편집에서는 새 실사·테스트·빌드·브라우저 실행·추출·네트워크 조사 없이 `technical.md`만 수정했다. Atlas R1/R3의 추가 범위와 증거 한계는 §7 및 부록에 명시한다.

## 판단

**동작하는 React/Tauri/Python 구현과 별도 연구·플래너 파이프라인이 있다. 그러나 사용자 조건과 수집자료로 완성 빌드 구성·성장 경로를 만들고 검증·수정·저장하는 제품 경로는 미완료다.** PoB는 선택적 입출력·검증 보조이며, 기존 구성의 조건부 조합·변형도 생성에 포함한다. README의 완료/Mock 표시 대신 실제 명령 등록·호출·데이터 연결을 판단 근거로 삼는다. 기존 실행 결과는 보존하되 생성 품질의 PASS로 사용하지 않는다.

후임 책임자의 생성 목표 보완은 [build_generation_readiness.md](build_generation_readiness.md)에 별도로 기록했다. 실제 자료 연결은 `knowledge_sources → knowledge_router → build_coach`로 존재하지만 [build_coach.py:1332](D:/Pathcraft-AI/python/build_coach.py:1332)의 router 호출은 POE1 한정이고, 주로 LLM 문맥을 제공한다. [추천 어댑터:164](D:/Pathcraft-AI/python/recommend_from_corpus.py:164)는 예산 기본값 3 divine·빈 보유품을 사용하며 [204행](D:/Pathcraft-AI/python/recommend_from_corpus.py:204)은 기존 profile 후보를 추천한다. [플래너:484](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:484)는 기존 PoB 입력을 요구하는 변환 경로다. 이것들을 사용자 제약으로 완성 구성을 합성하는 동일 기능으로 세지 않는다.

검증에는 젬 정규화·1회 교정·경고와 입력 스탯 screening이 있지만, [build_instance.py:445](D:/Pathcraft-AI/python/build_instance.py:445)는 입력의 DPS/HP 등을 읽으므로 생성·변경된 구성의 성능 재계산이 아니다. [build_coach.py:1851](D:/Pathcraft-AI/python/build_coach.py:1851)의 정규화·[1966행](D:/Pathcraft-AI/python/build_coach.py:1966)의 경고를 스킬/지원·패시브/포인트·장비/능력치·자원·확보·단계 전환의 통합 검증으로 확대하지 않는다. 이 추가 보완은 정적 읽기이며 테스트·API·빌드 실행은 하지 않았다.

- 확인된 실행: TypeScript 타입 검사, 원본 소스를 이용한 Vite production 빌드, 프런트엔드 115개 테스트, Python 핵심 176개 및 여정 DB/렌더 13개 테스트. 합계 **304 passed / 0 failed / 1 skipped**이며 서로 다른 범위의 합계다. 전체 Python 137개 테스트 파일 중 20개를 실행했다.
- 실제 재현한 결함: 잘못된 PoB XML 입력에 Python CLI가 JSON `null`과 exit 0을 반환한다. 일반 `.build` 검증기는 트리 전용 파일의 빠진 `skills` 키를 처리하지 못한다.
- 코드로 확인한 완결성 결함: POE2 구두 입력의 저장 키 문제, 게임 구분 없는 빌드 히스토리, 시스템 Python 및 원본 디렉터리에 의존하는 실행 구조, 앱과 최신 `.build`/여정/아틀라스 산출물의 연결 부재.
- **미검증:** Tauri 창 실행, 실제 IPC, 유료 AI 응답, 실제 URL 서비스, 앱 저장·재시작·복원 E2E, 설치 패키지와 깨끗한 PC, 게임 내 플래너/필터 로드. 이번 통과 수로 이 항목을 대신하지 않는다.

## 1. 실제 진입점과 연결 흐름

| 단계 | 현재 실제 구현과 근거 | 이번에 확인한 범위 |
|---|---|---|
| 웹 진입 | [D:/Pathcraft-AI/index.html:19](D:/Pathcraft-AI/index.html:19) → [src/main.tsx:13](D:/Pathcraft-AI/src/main.tsx:13). React root에 ActiveGameProvider를 두고 `?mode=overlay`로 메인/오버레이를 분기한다. | 타입 검사·번들 생성. React 앱 화면 렌더/상호작용 미실행. 별도 Atlas HTML의 R1 기록은 §7 참조. |
| 데스크톱 진입 | [src-tauri/src/main.rs:4](D:/Pathcraft-AI/src-tauri/src/main.rs:4) → [lib.rs:1148](D:/Pathcraft-AI/src-tauri/src/lib.rs:1148). 13개 Tauri command가 실제 등록되어 있다. | 소스·설정 정적 확인. Rust/Tauri 빌드 및 실행 미실행. |
| 입력 | 기본 탭은 research이며 후보 선택 시 PoB 링크를 채운다([App.tsx:748](D:/Pathcraft-AI/src/App.tsx:748), [App.tsx:754](D:/Pathcraft-AI/src/App.tsx:754)). POE1은 링크·보조 PoB·SC/SSF/HCSSF 입력, POE2는 구두 폼으로 갈라진다([App.tsx:933](D:/Pathcraft-AI/src/App.tsx:933)). | 실제 UI 코드 확인. POE2 UI에서 `.build` 파일을 가져오는 경로는 확인되지 않았다. |
| URL 해석·파싱 | [useBuildAnalyzer.ts:225](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:225)의 `resolve_build_source` → `parse_pob`. Rust는 [lib.rs:90](D:/Pathcraft-AI/src-tauri/src/lib.rs:90), [lib.rs:113](D:/Pathcraft-AI/src-tauri/src/lib.rs:113)에서 Python subprocess의 stdout JSON을 반환한다. | resolver/파서 테스트와 로컬 XML CLI 진입 실행. 외부 URL 성공 및 Rust IPC는 미검증. |
| 분석·추천 | `pob_parser`는 XML PlayerStat, 활성/보조 스킬·트리, 장비를 읽고 BuildInstance를 붙인다([pob_parser.py:444](D:/Pathcraft-AI/python/pob_parser.py:444)). [useBuildAnalyzer.ts:128](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:128) → [lib.rs:132](D:/Pathcraft-AI/src-tauri/src/lib.rs:132)의 대표 코퍼스 추천은 POE1 전용이다. | 샘플은 Ranger/Deadeye, DPS 4,000,000으로 파싱되고 23개 후보에서 Plan A `3_25_lightning_arrow_ranger`를 출력했다. 이는 현 시즌 추천 품질 증명이 아니라 기존 샘플과 현재 코드의 실행 증거다. |
| AI 계획·가이드 | [useBuildAnalyzer.ts:275](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:275)는 리그 모드·보조 빌드를 묶어 캐시 또는 `coach_build`를 사용한다. UI 모델은 [useBuildAnalyzer.ts:42](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:42)의 `gpt-5-nano`. Rust가 stdin으로 JSON을 전달하고 stdout/stderr를 함께 수집한다([lib.rs:185](D:/Pathcraft-AI/src-tauri/src/lib.rs:185)). | OpenAI/Anthropic은 기존 테스트의 mock으로만 실행. 실제 LLM 정확성·지연·비용·오류는 미검증. |
| 결과 표시·검증 | [App.tsx:1396](D:/Pathcraft-AI/src/App.tsx:1396)에서 정규화 중 삭제된 젬이 있으면 차단하고, 아니면 요약/레벨링/장비/패시브/위험/파밍/필터를 표시한다. 판정은 [CoachBlockedBanner.tsx:9](D:/Pathcraft-AI/src/components/CoachBlockedBanner.tsx:9)의 trace 검사다. | 정규화·재시도·블록 판정과 일부 SSR 테스트 통과. 모든 가이드의 품질 또는 실제 화면 전체를 검증한 것은 아니다. |
| 저장·재열기 | [useBuildAnalyzer.ts:151](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:151)의 자동 저장 → [useBuildHistory.ts:22](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:22)의 localStorage v2, 최대 20개. [useBuildAnalyzer.ts:49](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:49)의 최신 복원 및 [useBuildAnalyzer.ts:176](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:176)의 선택 복원이 있다. TopBar에서 선택 가능([App.tsx:877](D:/Pathcraft-AI/src/App.tsx:877)). | 코드 경로 존재 확인. 브라우저/Tauri 영속 스토리지를 실제 생성·재열기하지 않았다. |

파서의 DPS 등은 **PoB XML에 저장된 수치**다. 현재 캐릭터의 전투를 시뮬레이션해 재계산하는 엔진으로 해석하면 안 된다([pob_parser.py:20](D:/Pathcraft-AI/python/pob_parser.py:20), [pob_parser.py:450](D:/Pathcraft-AI/python/pob_parser.py:450)). `build_readiness.py`의 방어/맵/보스 판정은 별도 결정 규칙이며 실제 맵 시간·사망 빈도 같은 미입력 정보를 테스트에서도 구분한다([test_build_instance.py:61](D:/Pathcraft-AI/python/tests/test_build_instance.py:61)).

## 2. 중요한 결함과 반례

### A. 구두 입력을 저장·재열기할 수 있다는 보장이 없다 — 코드로 확인

[useBuildAnalyzer.ts:158](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:158)는 현재 렌더의 `pobLink`가 비면 저장을 즉시 종료한다. 반면 POE2 구두 입력은 [같은 파일:368](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:368)에서 `setPobLink("")`를 호출하고 [413행](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:413)에서 기존 closure의 `saveToHistory`를 부른다.

가능한 반례는 두 가지다. (1) 새 프로필에서 POE2 구두 입력으로 코칭을 성공시켜도 호출 시 링크가 비어 있으므로 히스토리가 저장되지 않는다. (2) 기존 POE1 링크 A를 가진 상태에서 POE2로 바꾸어 구두 입력하면, 진행 중 함수가 가진 이전 링크 A로 저장되어 A의 히스토리를 덮어쓸 수 있다. 히스토리 id는 링크만 hash한 값이다([useBuildHistory.ts:83](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:83)). **UI 재현은 하지 않았고 React closure와 저장 조건에 근거한 결함 판정이다.** 최소 수정 조건은 링크와 독립된 빌드 id/source kind를 두고, 구두 입력·빈 링크·기존 링크의 저장/재열기 회귀 시나리오를 통과시키는 것이다.

### B. 히스토리가 게임 문맥을 보존하지 않는다 — 코드로 확인

[SavedBuild:5](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:5)에 `game` 필드가 없고 저장 키도 양 게임 공통이다. 게임은 별도 localStorage에서 복원된다([ActiveGameContext.tsx:8](D:/Pathcraft-AI/src/contexts/ActiveGameContext.tsx:8)). 게임 버튼은 `setGame(g)`만 호출한다([TopBar.tsx:119](D:/Pathcraft-AI/src/components/shell/TopBar.tsx:119)); 히스토리 선택도 게임을 바꾸지 않는다([useBuildAnalyzer.ts:176](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:176)).

반례: POE1 빌드를 저장한 뒤 POE2를 선택하고 재시작하거나 기존 히스토리를 선택하면, 현재 game은 POE2인데 저장된 빌드/가이드는 POE1일 수 있다. 필터 호출은 현재 game을 전달한다([FilterPanel.tsx:40](D:/Pathcraft-AI/src/components/FilterPanel.tsx:40)). 게임별 캐시 키는 이미 있으나([useBuildAnalyzer.ts:283](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:283)) 히스토리 문제를 해결하지 않는다. 최소 조건은 저장 레코드의 game/version 포함, 게임 전환 시 진행 중 요청과 표시 상태 정리, 게임이 다른 히스토리의 복원 정책이다.

### C. XML 실패를 subprocess 성공으로 보고한다 — 이번 실행으로 재현

임시 `malformed.xml` 내용 `<PathOfBuilding>`을 `pob_parser.py --game poe1 file:///…/malformed.xml`에 전달했다. stderr에는 `ElementTree.ParseError: no element found: line 1, column 16`, stdout에는 `null`, **exit code는 0**이었다. [pob_parser.py:453](D:/Pathcraft-AI/python/pob_parser.py:453)가 예외를 `None`으로 바꾸고 [487행](D:/Pathcraft-AI/python/pob_parser.py:487)이 결과 검증 없이 출력 후 0으로 종료한다. [lib.rs:99](D:/Pathcraft-AI/src-tauri/src/lib.rs:99)는 exit 성공만 보고 `Ok`를 반환하며 [useBuildAnalyzer.ts:243](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:243)는 런타임 스키마 검증 없이 타입 단언한다.

최소 조건: 파서 실패의 비정상 exit 및 명시적 오류 스키마, Rust/프런트의 null·부분 JSON 검증, 이 입력으로 AI 호출·히스토리 저장을 시도하지 않는 통합 회귀 검증. `--selftest`는 문자열만 출력하므로 실제 파싱 증거로 사용하지 않았다([pob_parser.py:474](D:/Pathcraft-AI/python/pob_parser.py:474)).

### D. 개발 PC 밖의 배포·재현 경로가 미완성 — 구성으로 확인

[lib.rs:52](D:/Pathcraft-AI/src-tauri/src/lib.rs:52)는 `Command::new("python")`을 사용한다. [project_root:58](D:/Pathcraft-AI/src-tauri/src/lib.rs:58)는 환경변수 또는 exe/CWD 조상에서 `python/`을 찾는다. [tauri.conf.json:49](D:/Pathcraft-AI/src-tauri/tauri.conf.json:49)의 bundle은 아이콘/targets 중심이며 Python 실행 파일·스크립트·data를 포함하는 resources/externalBin 설정은 없다. 따라서 소스 폴더와 전역 Python을 가진 이 PC에서의 가능성과 독립 설치 앱의 가능성을 분리해야 한다.

활성 루트와 `python/` 양쪽에 requirements.txt/pyproject.toml이 없다. README의 설치 절차는 [README.md:117](D:/Pathcraft-AI/README.md:117)의 옛 Python 경로 및 requirements 설치를 가리켜 현재 신규 환경 재현 계약으로 충분하지 않다. 최소 조건은 Python 버전/의존성 잠금, 스크립트·데이터 패키징, 사용자 쓰기 디렉터리 계약, 빈 머신/격리 프로필 설치→분석→재열기 검증이다.

### E. 저장 신뢰성의 추가 공백 — 코드로 확인

히스토리는 AI 코칭 성공 후에 저장된다([useBuildAnalyzer.ts:292](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:292), [323행](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:323)). 유효 PoB 파싱 뒤 API 오류가 나면 입력/분석만 보존하는 저장 경로가 없다. `skipCoach` 분기는 내부 helper에 있으나 공개 UI 동작으로 확인되지 않았으므로 “파싱만 버튼”이 있다고 주장하지 않는다. 구버전 저장소는 migration 대신 삭제되고([useBuildHistory.ts:35](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:35)), quota 오류는 로그만 남긴다([58행](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:58)). 체크리스트는 빌드 이름 기반 키여서 같은 이름의 서로 다른 빌드가 공유할 수 있다([App.tsx:770](D:/Pathcraft-AI/src/App.tsx:770), [ChecklistContext.tsx:47](D:/Pathcraft-AI/src/contexts/ChecklistContext.tsx:47)).

## 3. build_planner·deliverables·최신 문서의 실제 위치

**플래너/여정 파이프라인은 실체가 있고 일부 실행 재현도 되지만, 현재 Tauri 앱 기능과 동일하지 않다.** `src/`와 `src-tauri/src/`에서 `build_planner`, `hc_journey`, `deliverables`, `hc_atlas_order` 참조를 찾지 못했다. Tauri 등록 목록([lib.rs:1152](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152))에도 해당 import/export나 여정 DB 조회 command가 없다.

- [scripts/build_poe2_planner_files.py:483](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:483)는 PoB XML → `.build` 변환 CLI, [scripts/import_poe2_planner_files.py:120](D:/Pathcraft-AI/scripts/import_poe2_planner_files.py:120)는 외부 `.build` 정규화/검증/저장 CLI다. `--install`은 실제 게임 폴더에 복사한다([build_poe2_planner_files.py:542](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:542), [import_poe2_planner_files.py:132](D:/Pathcraft-AI/scripts/import_poe2_planner_files.py:132)); 이번에는 설치 기능을 호출하지 않았다.
- 현재 원본 `build_planner/**/*.build` **78개**, `deliverables/**/*.build` **138개**, 합계 216개를 JSON으로 읽고 기존 validator를 **메모리에서만** 실행했다. deliverables 138개는 validator 문제 0, build_planner는 77개 검사 완료와 1개 `KeyError`다. 두 묶음 모두 메모리상 경로 교정 0개였다.
- 예외 파일은 [~Lvl 51 - [0.5.5] Oil Nade Flameblast Ge.build:1](<D:/Pathcraft-AI/build_planner/~Lvl 51 - [0.5.5] Oil Nade Flameblast Ge.build:1>): 키가 `author/link/ascendancy/name/passives`만 있고 `skills/inventory_slots`가 없다. [validator:91](D:/Pathcraft-AI/scripts/import_poe2_planner_files.py:91)는 `data["skills"]`를 직접 접근한다. [HC Journey README:37](D:/Pathcraft-AI/python/hc_journey/README.md:37)에도 ds lily Lvl51은 트리 탭으로 제외된다고 적혀 있다. **파일 손상이나 게임 로드 실패로 단정하지 않는다.** 트리 전용 변형과 완전 빌드의 스키마 계약이 다르다는 증거다.
- 기존 validator가 허용한 미등록 젬 경로는 build_planner 묶음에서 8종, deliverables에서 3종이었다. [import_poe2_planner_files.py:107](D:/Pathcraft-AI/scripts/import_poe2_planner_files.py:107)는 DB가 0.4.0d여서 없는 젬도 경고만 내고 통과한다. 따라서 validator 통과가 0.5.5의 모든 젬·게임 호환성 확인을 뜻하지 않는다. 앱 패시브 뷰도 [PassiveTreeCanvas.tsx:34](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:34)의 `tree_0_4.json`을 읽고, 플래너 생성기는 [build_poe2_planner_files.py:67](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:67)의 `tree_0_5.json`을 사용한다.
- 여정 DB는 [python/hc_journey/build_db.py:224](D:/Pathcraft-AI/python/hc_journey/build_db.py:224)의 creator 설정/픽스처 → 스냅샷 diff/규칙/노트 → [render_journey.py:145](D:/Pathcraft-AI/python/hc_journey/render_journey.py:145)의 HTML 렌더 구조다. 임시 DB로 기존 테스트를 재현하여 **creator 8 / build 8 / snapshot 41 / transition 33 / curation_rule 27 / transition_note 114**를 확인했다. 이는 결과 HTML 및 결정 규칙의 재현 증거이며 Tauri 앱 연동 증거는 아니다.
- 실사 중 추가된 [Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:1](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:1)와 실제 [hc_atlas_order.html:2979](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:2979)을 읽었다. 단계 선택·순번·재생 JS가 존재한다([3044행](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3044)). 다만 배포된 스크립트는 여전히 `ninja/atlas_tree.json`, `atlas_src/…` 상대 경로를 읽고 쓴다([classify.py:3](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/classify.py:3), [full_order.py:132](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_order.py:132)). 제공된 `data/` 레이아웃에서 그대로 재생성되는 상태라고 볼 수 없다. 초기 본문 작성 뒤 기존 기술 작업자가 별도 HTML 두 개를 브라우저에서 실행한 기록이 추가됐다. UTF-8 응답 보정 조건과 확인 범위는 §7 R1을 따른다.
- [Docs/2026-09-10_SEONGBIN_SESSION5_LOG.md:118](D:/Pathcraft-AI/Docs/2026-09-10_SEONGBIN_SESSION5_LOG.md:118)의 검증/생성 기록과 [planner_game_load.txt:1](D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/planner_game_load.txt:1)의 “새 parser load 로그 없음”은 과거 기록으로 취급했다. 게임 내 최신 로드 증거로 승격하지 않았다.

`.claude/status/current.md`는 9월 18일 실캐릭·필터·플래너 작업을 가리킨다([current.md:1](D:/Pathcraft-AI/.claude/status/current.md:1)). 그 문서의 “전체 테스트 실패 12 + 에러 16”([current.md:6](D:/Pathcraft-AI/.claude/status/current.md:6))은 **이번 실행으로 재현한 수치가 아니다**. `.claude/status/architecture.md`는 Claude 우선/HCSSF 기본([architecture.md:3](D:/Pathcraft-AI/.claude/status/architecture.md:3))이라고 하나 실제 UI는 nano/SC 기본이며, [CLAUDE.md:12](D:/Pathcraft-AI/CLAUDE.md:12)의 “Tauri 리빌드 예정”, POE1 전용 설명도 현재 코드와 어긋난다. 상태 문서·화면 문구의 완료/미완 표시를 실제 구현보다 우선하지 않았다.

## 4. 실행 안전성 점검과 실제 결과

기본 앱 실사의 제품 입력은 `D:/Pathcraft-AI`에서 읽었다. 추가 R3는 기존 게임 GGPK를 읽은 별도 범위이며 §7에 구분했다. 출력·임시 DB·pytest basetemp는 `C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness`(이하 **T**) 아래다. 전체 복사·git reset/clean/stash/checkout·설치·필터 생성·게임 복사는 하지 않았다. 기존 R1의 Playwright MCP 연결 기록은 §7에 한정하며, 현재 연결 가능 여부나 로그인 프로필 검증을 뜻하지 않는다.

### 사전 발견한 부작용

1. [package.json:8](D:/Pathcraft-AI/package.json:8)의 build에는 `prebuild → npm run translations`가 붙는다. [extract_passive_tree_translations.py:175](D:/Pathcraft-AI/python/extract_passive_tree_translations.py:175)는 원본 번역 JSON을 쓴다. 일반 `npm/pnpm build`를 그대로 실행하지 않았다.
2. [build_coach.py:16](D:/Pathcraft-AI/python/build_coach.py:16)은 import 때 루트의 키 파일을 override 로드하며 실제 provider client를 만들 수 있다. CLI는 [2021행](D:/Pathcraft-AI/python/build_coach.py:2021)에서 `_debug/coach_last_*.json`도 쓴다. 테스트는 dotenv 로딩을 비활성화하고 provider mock을 유지했으며 실제 코치 CLI를 호출하지 않았다.
3. [build_db.py:394](D:/Pathcraft-AI/python/hc_journey/build_db.py:394)는 기존 DB를 삭제하고 재생성한다. 여정 테스트 전에 **메모리상의 `build_db.DB_PATH`만 T/journey-audit.db로 변경**했다. 제품 파일/테스트 assertion을 수정하지 않았다.
4. [build_poe2_planner_files.py:65](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:65)는 트리 캐시가 없으면 사용자 temp에서 복사하여 원본 캐시를 만든다. 원본 `data/_cache/tree_0_5.json`이 이미 있는 것을 확인했고 fallback 쓰기를 실행하지 않았다.
5. `cargo test/check --target-dir T/...`만으로는 모든 쓰기가 격리되지 않는다. [src-tauri/build.rs:2](D:/Pathcraft-AI/src-tauri/build.rs:2) → 설치된 tauri-build 2.5.6의 [acl.rs:422](C:/Users/User/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/tauri-build-2.5.6/src/acl.rs:422) → tauri-utils의 [schema.rs:323](C:/Users/User/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/tauri-utils-2.8.3/src/acl/schema.rs:323)가 CWD의 `gen/schemas`를 생성/갱신할 수 있다. **원본 변경 금지 조건 때문에 Cargo/Tauri 빌드·테스트는 실행하지 않았다.** 별도 전체 복사나 소스 수정으로 우회하지 않았다.

### 환경

Windows / PowerShell / cwd `D:/Pathcraft-AI`. Node **v24.11.1**, Python **3.13.14**, pytest **9.0.2**, Vite **8.0.4**, Vitest **4.1.4**, cargo **1.93.0**, rustc **1.93.0**. 설치된 Python 패키지는 requests 2.32.5, beautifulsoup4 4.14.3, python-dotenv 1.2.1, openai 2.15.0, anthropic 0.76.0. 버전 조회는 기존 설치 상태를 읽었으며 설치/업데이트하지 않았다.

### 결과 표

| 실행 | cwd / 주요 환경·격리 | 통과·실패·skip / exit | 증거와 제한 |
|---|---|---|---|
| `node D:/Pathcraft-AI/node_modules/typescript/bin/tsc --project D:/Pathcraft-AI/tsconfig.json --noEmit --pretty false` | D:/Pathcraft-AI, 기존 tsconfig | 테스트 수 N/A, 진단 0 / **0** | emit 없이 타입 검사 성공. |
| Vitest programmatic `startVitest('test',['src'],…)` | D:/Pathcraft-AI, configLoader runner, envFile false, cache false, cacheDir T | **115/0/0**, 13 files / **0** | 16:56:30 시작, 3.33s. 모든 기존 src 테스트. hook 저장/재시작 E2E는 포함되지 않는다. |
| Vite programmatic `build(…)` | 원본 vite.config.ts, configLoader runner, envFile false, outDir T/dist, emptyOutDir false | N/A / **0** | 165 modules, 1.94s. main JS 439.92 kB, gzip 137.19 kB. 기존 번역 JSON을 사용했으며 prebuild 재생성 및 Tauri 패키징은 제외. |
| Python 최초 차단 harness | -B, 플러그인 autoload off, cacheprovider off, audit hook | **0 tests**, 내부 오류 / **3** | pytest 기본 로그 sink를 guard가 원본 외 쓰기로 판정해 차단. 제품 실패가 아니다. 로그 파일을 T로 명시한 뒤 재시도했다. |
| `python -B T/run_python_audit.py core` | D:/Pathcraft-AI, 아래 격리 적용 | **176/0/1**, 18 files / **0** | 30.74s. 네트워크 시도 2건은 연결 전에 차단됨. |
| `python -B T/run_python_audit.py journey` | 위 격리 + DB_PATH를 T로 변경 | **13/0/0**, 2 files / **0** | 3.97s. 원본 creator 픽스처·규칙 사용, 출력만 임시 경로. 차단 사건 0. |
| `python -B T/run_python_audit.py cli` | 원본 CLI를 runpy로 실행, 동일 argv, 임시 출력 | test framework 수 N/A / harness **0** | 정상 parser 0/dict, corpus 0/dict, malformed parser **0/null**. 부정 입력의 exit 계약 결함을 발견한 관찰이며 “3건 모두 기능 성공”이 아니다. subprocess/IPC는 검증하지 않는다. |
| `.build` 읽기 전용 inventory/validator | D:/Pathcraft-AI, `python -B -`, 디스크 저장 없음 | 216 JSON 읽기, 215 validator 완료, 1 예외 / 조사 명령 **0** | 예외를 수집해서 보고한 명령이므로 exit 0이 전체 데이터 통과를 뜻하지 않는다. 게임 미실행. |
| Cargo/Tauri/설치/게임/UI E2E | 실행하지 않음 | pass/fail/skip **집계 제외**, exit N/A | 위 쓰기 경로, 실제 API/개인 저장소 경계를 지키기 위해 미실행. |

Python 격리: `PYTHONDONTWRITEBYTECODE=1` 및 `-B`, `PYTHONIOENCODING=utf-8`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, TEMP/TMP=T, `-p no:cacheprovider`, `--basetemp T/pytest-<group>`, `--log-file T/pytest-<group>.log`, `-q -s --tb=short`. 프로세스 환경에서 API_KEY/TOKEN/SECRET/PASSWORD 이름의 값을 제거하고 출력하지 않았다. dotenv loader는 no-op으로 바꾸며 Python audit hook이 credential 파일 읽기, network connect/DNS, subprocess, T 밖 파일 mutation/SQLite를 거부한다. 이는 실제 OS 샌드박스를 검증했다는 뜻은 아니며, 읽은 기존 테스트의 부작용을 제한하기 위한 프로세스 내 안전장치다.

차단 2건의 정확한 내용은 (1) [test_pob_parser.py:113](D:/Pathcraft-AI/python/tests/test_pob_parser.py:113)의 존재하지 않는 pobb.in URL 오류 경로, (2) [test_build_coach_openai.py:110](D:/Pathcraft-AI/python/tests/test_build_coach_openai.py:110)의 Storm Secret Wiki 조회다. 네트워크 예외/폴백으로 통과했으므로 실서비스 접속 검증으로 세지 않는다. 정상 LLM 응답은 테스트 mock이고 실제 API 키는 쓰지 않았다.

skip 1건은 [test_build_poe2_planner_files.py:303](D:/Pathcraft-AI/python/tests/test_build_poe2_planner_files.py:303)의 `TestAgainstKnownGoodFile.test_fartfinder_mappings_reproduce`. PoB 캐시 2개는 있지만 `Documents/My Games/Path of Exile 2/BuildPlanner/Fartfinder 2 Endgame - Skadoosh.build`가 없어 309행에서 skip했다. 개인 게임 파일을 만들거나 복사해서 통과시키지 않았다. core 로그의 XML traceback은 기존 malformed-input 테스트의 기대 오류이고 실패 수는 0이다.

전체 Python 회귀는 실행하지 않았다. 그 안에는 네트워크/CLI/필터/실파일·DB 쓰기 테스트가 섞여 있어 전부 안전하다고 추정하지 않았다. 남은 **117개 파일**, Rust 테스트, 기존 C# 빈 테스트([UnitTest1.cs:6](D:/Pathcraft-AI/tests/PathcraftAI.Tests/UnitTest1.cs:6))도 이번 통과 합계에 넣지 않았다. coverage 비율은 측정하지 않았다.

## 5. 재현 명령과 범위 차이

프런트엔드 명령은 패키지 관리자/lifecycle 실행을 거치지 않는다. 기존 config와 실제 소스를 쓰되 dotenv 읽기·config 번들 임시 파일·캐시·출력 위치를 제한했다. 따라서 **일반 `pnpm build` 자체가 재현되었다고 표현하면 안 된다.** 아래 코드는 D:/Pathcraft-AI를 cwd로 실행한 JavaScript이며, PowerShell here-string을 `node --input-type=module`에 전달했다.

```js
// 테스트
import { startVitest } from 'file:///D:/Pathcraft-AI/node_modules/vitest/dist/node.js';
const tmp = 'C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness';
const ctx = await startVitest('test', ['src'], {
  root: 'D:/Pathcraft-AI', config: 'D:/Pathcraft-AI/vite.config.ts',
  configLoader: 'runner', watch: false, cache: false, reporters: ['default']
}, { envFile: false, cacheDir: tmp + '/vitest-cache' });
await ctx.close();
```

```js
// 빌드: 원본 번역 JSON 재생성 없이 사용
import { build } from 'file:///D:/Pathcraft-AI/node_modules/vite/dist/node/index.js';
const tmp = 'C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness';
await build({ root: 'D:/Pathcraft-AI', configFile: 'D:/Pathcraft-AI/vite.config.ts',
  configLoader: 'runner', envFile: false, cacheDir: tmp + '/vite-cache',
  build: { outDir: tmp + '/dist', emptyOutDir: false } });
```

Python core의 실제 test 파일 목록은 모두 `D:/Pathcraft-AI/python/tests/test_<이름>.py`이다: `pob_parser`, `pob_parser_retry`, `pob_raw`, `build_source_resolver`, `build_instance`, `build_readiness`, `recommend_from_pob`, `recommend_from_corpus`, `build_coach`, `build_coach_openai`, `build_coach_prompt`, `build_coach_extras`, `build_coach_retry`, `coach_normalizer`, `coach_validator_gems`, `coach_poe2_branch`, `build_poe2_planner_files`, `import_poe2_planner_files`. journey는 `hc_journey_db`, `render_journey`이다.

CLI 조사에서 실제 원본 `__main__`에 전달한 argv:

```text
D:/Pathcraft-AI/python/pob_parser.py --game poe1 file:///D:/Pathcraft-AI/data/samples/recommendation_runner_sample.xml
D:/Pathcraft-AI/python/recommend_from_corpus.py --build-json T/parsed-pob.json --mode sc
D:/Pathcraft-AI/python/pob_parser.py --game poe1 file:///T/malformed.xml
```

여기서 T는 앞서 정의한 실제 절대 임시 디렉터리다. 마지막 입력은 `<PathOfBuilding>`이며 기존 오류 위치는 line 1, column 16이다. 아래 부록에 기존 안전 harness 전체와 명령·로그 출처를 보존한다. 재현 조건 설명은 재실행 지시가 아니다. 테스트 재실행에는 기존 설치 의존성, 원본 데이터/캐시, 출력 경로 쓰기 권한이 필요하며, 설치 없는 새 PC 재현을 증명한 것은 아니다.

## 6. 최소 완결 조건과 남은 결정

1. **자료 기반 생성 계약:** 지원할 게임·패치·빌드 계열과 허용 변형을 정하고 요청 조건→출처 있는 구성 선택·조합/변형→완성 빌드와 성장 단계로 연결한다. 정본 구성에는 스킬/지원젬·패시브·장비/대체품·자원·전환 조건과 source/revision을 보존한다. 링크 추천이나 설명만 생성하는 경로로 완료 판정하지 않는다. 특정 게임/클래스를 이번 평가에서 임의 확정하지 않는다.
2. **전체 조합 검증·오류 계약:** 생성한 각 단계에 이름·지원 호환·패시브 연결/포인트·능력치·자원·확보/예산·패치·전환 선행조건을 함께 적용한다. 검증된 성능 가정과 미검증 항목을 분리한다. XML/JSON 경계 실패뿐 아니라 구성 충돌·미확인이 성공 빌드로 저장되지 않도록 차단/보류 상태를 둔다.
3. **수정·저장·보조 연결:** PoB 없는 독립 build ID/revision과 입력/출처/판정을 저장하고, 사용자 수정으로 영향받는 검증을 무효화·갱신한 뒤 재열기를 확인한다. 현재/목표 비교·여정·아틀라스·파밍·제작·PoB/플래너 출력은 생성 결과의 사용을 돕는 보조 경로로 연결한다. 외부 HTML이나 304개 기존 테스트가 있다는 사실만으로 이 통합이 완료되지는 않는다.
4. **실행·배포 재현성:** Python 의존성/런타임과 데이터 자산을 포함하고 출력 경로를 사용자 데이터 디렉터리로 분리한다. prebuild와 Tauri schema 생성도 원본 변경 없는 검증 경로를 제공해야 한다. 승인된 복제/격리 환경이 준비된 뒤 Rust/Tauri 빌드, 설치, 재시작 검증이 필요하다.
5. **버전·근거 명시:** 앱 0.4 트리, 플래너 0.5 캐시, 낡은 젬 allowlist, 최신 산출물 간 버전 차이를 계약으로 드러내고 미등록 젬을 검증 완료로 표시하지 않는다. 실제 AI 품질과 게임 로드는 별도의 승인된 검증이 필요하다.

이번 읽기 전용 실사 자체에 추가 사용자 결정은 필요하지 않다. 정식 settlement/release는 검토 책임자가 이 증거를 읽고 판단한다. 후속 구현의 첫 완결 시나리오와, 실제 API/설치/게임 검증의 허용 환경·비용 범위는 아직 결정·검증되지 않았다.

### 원본 식별 보조값

17:02 +07:00에 읽은 SHA-256: `src/hooks/useBuildAnalyzer.ts` = `C9C8571E9C565D9E2C0F5E52E6CF0C02C8752CE71E74561CBDD000680B82C2E6`, `src/hooks/useBuildHistory.ts` = `24352F5381DF04C85275A2E7B218F577000F9C5F63EC2134BF07EA64FC3EA935`, `src-tauri/src/lib.rs` = `7AD07A2DC00EE37A2EF1E924604F74A753CE3C18A1B0CCC51BB04AD0A8AE133E`, `python/pob_parser.py` = `8CE187553DA8C294181B0F5668898977B6BFDC3768B1D7A38EA9374EA8E8AC14`, `python/build_coach.py` = `958C12D5BB4F7DBCC1AE7B4F0ABBEDD09391BF9325842A5725BFCF6C1549E5BD`.

최초 원본 status에 있던 변경은 `.claude/status/poe2_hc_gemling.md`, `AGENTS.md`, `CLAUDE.md`, `scripts/poe2_filter_eval.py`, `scripts/probe_trade_listings.py`였다. 17:03 확인 때에는 `.claude/files/created.md`와 새로운 아틀라스 자료도 추가돼 있었다. 이는 다른 세션의 진행 결과로 보존했으며 되돌리지 않았다. 원본 전체의 해시를 비교하지 않았으므로 원본 전체가 불변이라고 주장하지 않는다.

## 7. Atlas 추가 범위 — 기존 R1/R3 증거의 수신 정리

기준은 [레퍼런스 요청](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:1)과 [송수신 계약](D:/contracts/atlas-viewer-to-pathcraft-app.md:1)이다. 송신 S1–S4 PASS와 수신 R1/R2/R3는 별개이며, 다음은 중지 전 증거를 정리한 결과다. **R3는 partial이고 이 기능의 상용화 판단은 보류한다.** 파일 추출 성공으로 데이터 대체 완결이나 상용 이용 권리를 증명하지 않는다.

### R1: 별도 HTML 브라우저 실행 기록 — charset 조건부

추적 출처는 [책임자 인계문:81](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-audit-20260921/deliverables/readiness_audit_2026-09-21/manager_handoff_medium.md:81)의 기존 기술 작업자 status `msg_f45bc6ca4a29` 요약이다. 해당 기록은 `pages/hc_atlas_order.html` 및 `pages/seongbin_atlas.html` 두 HTML의 칩·행 클릭·재생/멈춤·처음부터 재생·초록→파랑 전환·reduced-motion을 실제 Playwright MCP 브라우저에서 확인했다고 보고한다. Orca embedded browser의 `runtime_unavailable` 후 양쪽 클라이언트 MCP 설정 확인 규칙을 읽고 실제 Playwright MCP 연결로 진행한 이력이다.

**실행 조건:** `localhost:7928`의 raw HTTP 응답에서는 UTF-8 charset/meta 누락으로 EUC-KR 해석이 발생했다. 원본 HTML을 수정하지 않고 route에서 응답 charset을 UTF-8로 지정한 상태의 동작 확인이다. 따라서 원본 raw HTTP 제공 상태의 한글 표시가 정상이라고 판정하지 않으며, 응답 보정 없는 직접 열기·다른 서버·설치 앱에 대한 PASS로 확대하지 않는다. 남아 있는 [serve_atlas.py](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/serve_atlas.py:1)는 임시 HTTP 서버 소스일 뿐, 7928 응답이나 브라우저 검증 결과를 독립적으로 증명하는 로그가 아니다.

이번 편집에서 기존 transcript 회수를 시도한 정확한 명령은 부록에 기록했다. `--source transcript`는 `transcript_required / session_not_reported`로 실패했고, `--source auto`는 종료된 terminal fallback에서 0행을 반환했다(`sourceExact=false`, `contentComplete=false`). 따라서 **R1 실행 이력은 기존 책임자가 남긴 위 문서와 메시지 ID를 출처로 보존하되, 세부 브라우저 명령·raw 결과·화면별 assertion·console 오류 수는 이번 편집에서 직접 대조하지 못해 미확인**이다. 새 브라우저 실행으로 보충하지 않았다. 앱 저장/재열기 E2E, Tauri IPC, 실제 캐릭터 포인트 할당 검증은 여전히 미실행이다.

임시 서버 정리 상태도 구분한다. 책임자의 후속 메시지 `msg_37b986bdb66a`(2026-09-21 10:34:47 UTC)는 `Get-NetTCPConnection -LocalPort 7928 -State Listen`에서 listener 결과가 없었다고 보고했다. 이는 책임자의 해당 시점 관찰이며 이 작업자의 재조회가 아니다. 보존된 `serve_atlas.py`는 `127.0.0.1`의 **port 0(동적 포트)**으로 시작하며 포트/PID를 출력하고 종료 endpoint를 제공한다. 해당 서버의 실제 할당 포트·PID·정상 종료 출력은 transcript 미회수로 **미확인**이다. 7928 listener 부재만으로 동적 포트 서버도 종료됐다고 단정하지 않는다. 이번 편집에서 서버 실행·종료·프로세스 조작을 하지 않았다.

### R3: 4파일 제한 추출 및 prefix 대조 — semantic 대체 미완료

[ggpk-read.log](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/ggpk-read.log:1)와 [read_atlas_ggpk.py](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/read_atlas_ggpk.py:1)가 직접 출처다. 인계문은 당시 GGPK를 약 152GB로 기록한다. 실행기는 원본 `scripts/ggpk_explore.py`의 `GGPK` 경로를 읽기 전용으로 열며, 로그에는 `Bundles2/_.index.bin` 115,073,230 bytes와 사용 bundle의 저장 SHA-256 대조 성공이 남아 있다. 이는 **152GB 전체 GGPK 해시 검증이 아니다**. Oodle DLL을 이용해 index/bundle을 풀고 아래 4파일만 T/ggpk-selected에 썼다. index 집계는 bundles 63,123 / files·paths 4,262,817 / directories 95,796이다.

| GGPK 내부 경로 | T/ggpk-selected의 파일명 | bytes | 로그에 기록된 SHA-256 |
|---|---|---:|---|
| `metadata/atlasskillgraphs/atlasskillgraph.psg` | `metadata__atlasskillgraphs__atlasskillgraph.psg` | 19,336 | `c705685dfd3028cddbd535ca718931a8ece1eed369d16b79f867c37e9986e9d4` |
| `metadata/atlasskillgraphs/endgamemaplayoutgraph.psg` | `metadata__atlasskillgraphs__endgamemaplayoutgraph.psg` | 29,028 | `f511ae9708d8278e1886c8af86e22020241449394ff82f8c53e5ac46989f4c7f` |
| `data/balance/passiveskills.datc64` | `data__balance__passiveskills.datc64` | 5,497,515 | `49af4f7dfab787b57efa22e06e2673c268cbd90c4f40140aa085cb8fbb602bc2` |
| `data/balance/korean/passiveskills.datc64` | `data__balance__korean__passiveskills.datc64` | 5,415,801 | `f3996270a036ffc1965b5203fff1eb6f75c3908075d8c424b5cd1d240562329f` |

위 값은 기존 로그에서 옮겼으며 이번에 다시 추출하거나 해시를 계산한 값이 아니다. 실행기에는 `C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/DotNET/AutomationTool/oo2core_9_win64.dll` 의존성이 있다. 기술적 호출 성공을 해당 DLL이나 추출 자산의 재배포 허가로 해석하지 않는다.

[atlas-tables.log](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/atlas-tables.log:1)의 최초 해석은 실제 row 크기 **487 bytes**와 기존 schema의 **392 bytes** 불일치로 `assert stride==actual`에서 실패했다. 뒤의 [atlas-tables-prefix.log](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/atlas-tables-prefix.log:1)와 현재 [inspect_atlas_tables.py](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/inspect_atlas_tables.py:1)는 전체 schema 검증을 통과시킨 결과가 아니라 `Id / PassiveSkillGraphId / Name` prefix만 제한적으로 읽은 후속 조사다. 두 로그의 실패와 부분 결과를 모두 보존한다.

- EN/KO 각 9,731 rows 중 레퍼런스 노드 ID 537개에 대응하는 행 537개, missing 0, EN/KO Id parity 537이 기록됐다. 레퍼런스 `atlas_tree.json`의 노드 ID로 대상을 선별했으므로 독립 그래프 재구성 검증이 아니다.
- EN 이름은 530/537 일치했다. 불일치 7개는 레퍼런스의 Atlas/Breach/Expedition/Delirium/Ritual/Abyss/Incursion 루트명에 대해 GGPK Name이 빈 문자열인 경우다. KO 표본에는 성소 확률·총애받는 사도·적응형 생태·욕심 나는 제안이 있다. 전체 한국어 품질 및 선택형 옵션의 `selectionName` 출처 대체는 미검증이다.
- PSG semantic parse, 전체 노드·그룹·좌표·연결의 직접 재구성 및 레퍼런스와의 동등성, schema 후반 `SkillType/AtlasSubTree` 의미, 선택형 옵션·지역 조건 대체는 완료되지 않았다. binary 추출과 일부 이름 대조를 완전한 그래프/현지화/상용 데이터 교체 PASS로 승격하지 않는다.

### 앱에 가져갈 진행 계약과 남은 경계

**메인 아틀라스 진행과 콘텐츠별 내부 배분 순서를 분리한다.** 의식·균열·탐험 등은 메인 초록 단계에서 실제 조우할 수 있는 독립 콘텐츠이며, 메인을 끝낸 뒤 의식→인커전→심연 등의 순서로 반드시 진행해야 한다는 의미가 아니다. 각 콘텐츠에는 독립 `pointPool`(가용·사용 포인트), `unlock`(해금 조건/상태/근거), `encounter`(실제 조우·접근 가능 상태), `selectedScope`(메인 또는 현재 선택 콘텐츠 범위)를 둔다. 범위 내부 순서는 해당 포인트와 해금 조건 안에서만 안내하고, 콘텐츠 간 의무 선후 관계나 공유 포인트 지갑을 만들지 않는다. 화면 재생 진도와 실제 할당 상태도 분리한다.

이것은 후속 앱 데이터/UI 계약이며 이번에 구현한 기능이 아니다. 초록은 단계 표시이고 안전 보증이 아니다. R2 집계와 별개로 S5 위험 분류는 partial이며 서브트리/58 이후 순서 적대검증, 311 대 336 포인트 차이, 지역 레벨 70/75 적용 조건, 0.5.5 포인트 획득 출처가 미해결이다. 콘텐츠 간 의무 순서가 없다는 사용자 요구를 불명확한 총순번 530으로 덮어쓰지 않는다. R1 실행 이력과 R3 제한 추출은 **304 passed / 0 failed / 1 skipped에 추가 합산하지 않는다**. 원본 제품의 상용 판매 및 Atlas 출처 교체 완결 판정은 계속 보류한다.

## 부록: 기존 명령·로그 출처와 임시 Python 검증 실행기

T는 `C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness`의 약칭이며 원본 평가 대상은 `D:/Pathcraft-AI` 전체다. 아래는 기존 실행의 재현 조건과 증거 위치를 정리한 것으로, 이번 편집에서 명령을 다시 실행하지 않았다.

| 대상 | 기존 명령/실행기 출처 | 기존 결과 출처와 한계 |
|---|---|---|
| TypeScript / Vitest / Vite | §4의 tsc 명령, §5의 JavaScript programmatic 호출 | 기존 technical.md 및 인계문의 결과 기록, 빌드 출력 T/dist. 독립 stdout 로그 파일이나 exact transcript는 이번에 회수하지 못했다. 기존 115 tests 및 build exit 0을 새로 검증한 것으로 표현하지 않는다. |
| Python core | `python -B T/run_python_audit.py core` | [python-core.log](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/python-core.log:1): 176 passed / 1 skipped, 차단 2건. pytest 세부 로그 T/pytest-core.log. |
| Python journey | `python -B T/run_python_audit.py journey` | [python-journey.log](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/python-journey.log:1): 13 passed, 차단 0건. pytest 로그 T/pytest-journey.log, DB T/journey-audit.db. |
| Python CLI | `python -B T/run_python_audit.py cli`; 정확한 argv는 아래 harness의 cli 분기 | [python-cli.log](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/python-cli.log:1), T/parsed-pob.json, T/corpus-result.json, T/malformed-result.json. 정상 dict 둘과 malformed NoneType/exit 0을 구분한다. |
| 최초 Python guard 실패 / .build inventory | §4와 기존 technical.md의 실행 기록 | 최초 harness exit 3과 216개 inventory의 전체 one-off 명령·별도 원시 로그는 이번에 회수하지 못했다. 0 tests 실패와 215 validator 완료/1 예외의 기존 기록을 보존하며 전수 게임 호환성으로 확대하지 않는다. |
| R1 브라우저 | 인계문:81 및 `msg_f45bc6ca4a29` | §7의 charset 보정 조건부 기록. 정확한 브라우저 명령/원시 결과는 미회수. |
| R3 제한 추출 | T/read_atlas_ggpk.py 전체 소스 | T/ggpk-read.log와 T/ggpk-selected의 4개 파일. 당시 shell 호출·redirect 구문은 미회수이므로 추정 명령을 실제 실행 명령으로 쓰지 않는다. |
| R3 테이블 부분 대조 | T/inspect_atlas_tables.py 현재 소스 | T/atlas-tables.log는 이전 assert 실패, T/atlas-tables-prefix.log는 prefix-only 후속 결과. 현재 실행기와 최초 실패 버전을 동일시하지 않는다. |

기존 Dispatch 기록 회수를 위해 이번 편집에서 실행한 읽기 전용 명령과 결과:

```text
orca orchestration worker-read --dispatch ctx_30a92ca0cdb6 --source transcript --limit 3 --json
# exit 1: transcript_required, session_not_reported
orca orchestration worker-read --dispatch ctx_30a92ca0cdb6 --source auto --limit 200 --json
# exit 0: source terminal, terminal exited, returnedLineCount 0,
# sourceExact false, contentComplete false, fallbackReason session_not_reported
```

다음은 T/run_python_audit.py의 기존 파일 전체를 그대로 수록한 것이다. 외부 shell의 `-B`/UTF-8 환경과 cwd 조건은 §4를 함께 적용해야 한다. 새 실행기나 테스트를 생성하지 않았으며 이 코드 블록은 문서 보존용이다.

```python
import os
import sys
from pathlib import Path

root = Path('D:/Pathcraft-AI')
tmp = Path(__file__).resolve().parent
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['TEMP'] = os.environ['TMP'] = str(tmp)
for key in list(os.environ):
    if any(x in key.upper() for x in ('API_KEY', 'TOKEN', 'SECRET', 'PASSWORD')):
        os.environ.pop(key, None)

denied = {}
def in_tmp(p):
    return isinstance(p, (str, bytes, os.PathLike)) and Path(os.fsdecode(p)).resolve().is_relative_to(tmp)

def deny(kind):
    denied[kind] = denied.get(kind, 0) + 1
    raise PermissionError('AUDIT_DENIED_' + kind)

def guard(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'subprocess.Popen', 'os.system'):
        deny('NETWORK_OR_SUBPROCESS')
    if event == 'open':
        p, mode, flags = args
        if isinstance(p, (str, bytes, os.PathLike)) and Path(os.fsdecode(p)).name == '.env':
            deny('CREDENTIAL_FILE')
        writing = (isinstance(mode, str) and any(x in mode for x in 'wax+')) or ((flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not (isinstance(p, int) or in_tmp(p)):
            deny('WRITE_OUTSIDE_TMP')
    if event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime') and not in_tmp(args[0]):
        deny('MUTATION_OUTSIDE_TMP')
    if event in ('os.rename', 'os.link', 'os.symlink') and not all(in_tmp(p) for p in args[:2]):
        deny('MUTATION_OUTSIDE_TMP')
    if event == 'sqlite3.connect' and args[0] != ':memory:' and not in_tmp(args[0]):
        deny('SQLITE_OUTSIDE_TMP')

sys.addaudithook(guard)
import dotenv
dotenv.load_dotenv = lambda *a, **kw: False
import pytest

group = sys.argv[1] if len(sys.argv) > 1 else 'core'
if group == 'cli':
    import json
    import runpy
    sys.path.insert(0, str(root / 'python'))
    def cli(script, args, name):
        sys.argv = [str(root / 'python' / script)] + args
        output = tmp / name
        original_stdout = sys.stdout
        try:
            with output.open('w', encoding='utf-8') as stream:
                sys.stdout = stream
                try:
                    runpy.run_path(sys.argv[0], run_name='__main__')
                    code = 0
                except SystemExit as e:
                    code = e.code
        finally:
            sys.stdout = original_stdout
        payload = json.loads(output.read_text(encoding='utf-8'))
        print('CLI_RESULT', script, 'exit', code, 'type', type(payload).__name__)
        return payload
    parsed = cli('pob_parser.py', ['--game', 'poe1', (root/'data/samples/recommendation_runner_sample.xml').as_uri()], 'parsed-pob.json')
    print('PARSED', parsed['meta']['class'], parsed['meta']['ascendancy'], parsed['stats']['dps'])
    corpus = cli('recommend_from_corpus.py', ['--build-json', str(tmp/'parsed-pob.json'), '--mode', 'sc'], 'corpus-result.json')
    print('CORPUS', corpus['candidate_pool_size'], corpus['recommendation'].get('selected_plan'), corpus['recommendation'].get('selected_build_id'))
    malformed = tmp / 'malformed.xml'
    malformed.write_text('<PathOfBuilding>', encoding='utf-8')
    cli('pob_parser.py', ['--game', 'poe1', malformed.as_uri()], 'malformed-result.json')
    print('AUDIT_DENIED_COUNTS', denied)
    raise SystemExit(0)
if group == 'journey':
    sys.path.insert(0, str(root / 'python/hc_journey'))
    import build_db
    build_db.DB_PATH = tmp / 'journey-audit.db'
    names = ['hc_journey_db', 'render_journey']
else:
    names = ['pob_parser', 'pob_parser_retry', 'pob_raw', 'build_source_resolver', 'build_instance', 'build_readiness', 'recommend_from_pob', 'recommend_from_corpus', 'build_coach', 'build_coach_openai', 'build_coach_prompt', 'build_coach_extras', 'build_coach_retry', 'coach_normalizer', 'coach_validator_gems', 'coach_poe2_branch', 'build_poe2_planner_files', 'import_poe2_planner_files']
args = ['-q', '-s', '-p', 'no:cacheprovider', '--basetemp', str(tmp / ('pytest-' + group)), '--log-file', str(tmp / ('pytest-' + group + '.log')), '--tb=short'] + [str(root / 'python/tests' / ('test_' + n + '.py')) for n in names]
print('AUDIT_TEST_FILES', len(names), 'PYTEST_VERSION', pytest.__version__, flush=True)
exit_code = pytest.main(args)
print('AUDIT_DENIED_COUNTS', denied, flush=True)
raise SystemExit(exit_code)
```
