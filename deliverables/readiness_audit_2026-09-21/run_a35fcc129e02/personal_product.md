# Pathcraft-AI 개인용 제품·데이터 실사

최종 취합 주석(후임 책임자, 2026-09-21): 기존 개인용 작업자의 본문·집계 증거를 보존한 사본이다. 최초 Task는 성공 수락됐고 Atlas 후속 Task는 사용자 요청으로 중단됐다. 후임이 보존 결과를 검토하여 아래 계약을 보완했다. 본문의 “구현 담당 결과 대기”는 해당 작업자의 관측 범위이며, 최종 R1/R3 판정은 [기술 보고서](technical.md)와 [Atlas 수신 검토서](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_RECEIVER_REVIEW.md)를 따른다. 추가 테스트·집계·브라우저 실행은 하지 않았다.

평가 기준 시각: 2026-09-21 17:05, Asia/Bangkok(+07:00), 원본 읽기는 16:53부터 수행했다. 평가 원본은 **현재 실제 `D:/Pathcraft-AI` 전체 폴더**다. 이 보고서가 놓인 Orca 하위 worktree는 보고서 공간으로만 사용했다. 원본 `AGENTS.md`, `CLAUDE.md`, 초기·개정 PRD, 현재 React/Tauri/Python 호출 경로, `build_planner/`, `deliverables/`, `python/hc_journey/`, `data/hc_journey/`, 최신 `Docs/`, `.claude/status/`를 실제 읽었다. 원본 Git 상태에서 미커밋·미추적 파일을 확인하고 대표 사례에 포함했다. 전체 폴더를 평가 범위로 삼되 파일 전수를 정독한 것은 아니며, 실행 경로와 최신 개인 산출물의 대표 사례를 추적했다.

이 실사는 **정적 읽기 검토**다. 테스트·빌드·앱·게임·프로젝트 스크립트를 실행하지 않았고, 설치·필터 변경·외부 게시도 하지 않았다. JSON 일부는 PowerShell로 읽어 구조를 확인했고, 후속 Atlas 검토에서는 표준 라이브러리만 사용하는 독립 Python 인라인 명령으로 JSON을 읽어 메모리에서 계수·집합·연결성을 계산했다(실제 명령은 추가 장에 수록). 아래 “구현됨”은 실제 소스와 진입 경로가 존재한다는 뜻이며, 이번 평가에서 실행 성공을 재현했다는 뜻이 아니다. 문서에 적힌 패치·게임 수치·검증 이력은 저장된 자료의 주장으로 인용한다. 현재 게임의 최신 사실이나 라이브 서비스 동작을 독립 확인한 것으로 취급하지 않았다.

## 판정

최종 목표는 **수집 자료로 사용자 조건에 맞는 빌드와 성장 경로를 생성**하는 것이다. 검증된 구성의 조합·변형도 포함하며 PoB·분석·현재/목표 비교는 선택적 보조다. 아래 수동 사용 절차는 현 상태의 활용 근거이지 최종 제품 정의가 아니다. 코드와 자료의 생성 연결은 [생성 준비도](build_generation_readiness.md)를 함께 읽는다.

**개인용 생성에 재사용할 자료·코칭·검증·플래너 자산은 있다. 그러나 `요청 조건 → 자료 선택·조합/변형 → 일관된 빌드 구성과 성장 경로 → 검증 → 개인별 수정·저장`을 완결하는 제품은 아직 입증되지 않았다.** 최근 POE2 자료의 실체와 앱 생성 경로의 연결은 구분해야 한다. POE1 분석·추천과 POE2 구두 코칭도 구성 요소이지만 링크 추천·설명·파일 변환만으로 검증된 완성 빌드를 만든다고 볼 수 없다. [POE1 선택](D:/Pathcraft-AI/src/App.tsx:754), [PoB 없는 코칭](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378), [생성 연결 상세](build_generation_readiness.md).

완성률·개발 기간·매출은 추정하지 않는다. 개인용 최소 완결판의 중심은 **모은 자료를 구성·제약·근거로 연결하고 사용자 조건에 맞게 만든 결과를 조합 단위로 검증하는 것**이다. 자료의 존재·수량과 생성 지식으로서의 정규화·버전·출처·실제 호출 연결을 구분한다.

후속 Atlas 확인으로 이 판단을 보강한다. **단계·순번·재생 UX를 담은 독립 HTML 레퍼런스와 정합적인 그래프/순서 데이터까지 존재한다.** R2의 537노드·255그룹, 비루트 530노드의 목록 완전성, 초반 58노드 연결과 11목표 포함은 이번 수신 측 읽기 계산으로 확인했다. 그러나 현재 앱의 개인 캐릭터→아틀라스 계획 연결, R1 브라우저 동작, R3 직접 추출, 패치별 포인트 획득·지역 조건·위험 분류·상용 권리는 이 결과만으로 통과하지 않는다. 상세 근거·명령·앱 계약 제안은 아래 Atlas 추가 장에 있다.

## 원래 의도와 현재 결과

과거 PRD·상태 문서에는 분석·코치·로드맵 정의가 섞여 있다. 아래는 역사적 기록이며, 현재 사용자가 교정한 빌드 생성 목표를 제한하는 규칙이 아니다. 새로운 메타 발명만을 생성으로 인정하는 과도한 기준도 적용하지 않는다.

초기 PRD는 빌드의 What뿐 아니라 Why를 설명하고, PoB의 스킬·장비·방어·트리를 분석하며, SSF와 HC를 별도 맥락으로 다루는 도우미를 요구한다. POE2는 초기에는 후순위였다. 이후 PRD는 빌드 검색·최신 패치·레벨링·약점 개선을 강조했고, 현재 아키텍처 문서는 “레벨 1~엔드게임 로드맵”과 HCSSF를 제품 방향으로 적었다. 이는 단순한 문서 모음이나 최종 장비 복제보다 넓은 요구다. [초기 목표](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:16), [초기 분석 범위](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:53), [모드·게임 범위](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:252), [개정 사용자 과제](D:/Pathcraft-AI/PRD.md:43), [현재 방향 문서](D:/Pathcraft-AI/.claude/status/architecture.md:1).

문서 간 결정은 동기화되어 있지 않다. `CLAUDE.md`는 POE1 전용·POE2 데이터 금지를 적지만 실제 원본에는 POE2 연구와 실행 코드가 있다. 아키텍처 문서의 오버레이 포기와 현재 Sidebar 오버레이 버튼도 다르다. 따라서 문구 하나를 최종 제품 사양이나 기능 부재의 증거로 삼으면 안 된다. 이번에는 양 게임의 실제 파일을 요청 범위대로 평가했다. 유료 티어·WPF·완료 체크 표시는 완료 판정에서 제외했다. [기존 규칙](D:/Pathcraft-AI/CLAUDE.md:25), [과거 결정](D:/Pathcraft-AI/.claude/status/architecture.md:18), [현재 Sidebar](D:/Pathcraft-AI/src/components/shell/Sidebar.tsx:53), [완료 표기가 있는 PRD](D:/Pathcraft-AI/PRD.md:75), [WPF 체크가 남은 개정 PRD](D:/Pathcraft-AI/Docs/PRD.md:9).

## 기능별 상태

| 사용자가 얻는 것 | 판정 | 실제 연결과 제한 |
|---|---|---|
| POE1 리서치 후보·출처를 보고 PoB 분석으로 이동 | 구현됨, 실행 미확인 | `ResearchDashboard → load_poe1_research_dashboard → data/poe1_*.json`, 선택 시 PoB 링크와 보조 링크를 채우고 분석 탭으로 이동한다. 자료 상태에 따라 보류/연습 후보도 구분한다. [로더](D:/Pathcraft-AI/src/components/ResearchDashboard.tsx:1264), [데이터](D:/Pathcraft-AI/src-tauri/src/lib.rs:882), [선택](D:/Pathcraft-AI/src/App.tsx:754), [라벨](D:/Pathcraft-AI/src/components/ResearchDashboard.tsx:620) |
| POE1 PoB → AI 가이드·단계·장비·주의사항 | 구현됨, 정확성·실행 미확인 | resolver→parser→coach 호출이 있고 레벨링·장비·패시브·위험 UI에 결과를 전달한다. 입력은 자동 현재 캐릭터 인식이 아니라 사용자가 고른 PoB다. [분석](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:224), [coach](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:275), [표시](D:/Pathcraft-AI/src/App.tsx:1411) |
| AI 오류 노출·정규화 | 구현됨, 적용 범위 제한 | 젬 정규화, 재시도, 검증 경고, 차단 배너가 있다. 과거 품질 backlog의 “경고 UI 없음”을 현재 결함으로 그대로 재인용하면 틀린다. POE2 장비 정규화는 명시적으로 건너뛴다. [현재 후처리](D:/Pathcraft-AI/python/build_coach.py:1851), [재시도](D:/Pathcraft-AI/python/build_coach.py:1873), [UI](D:/Pathcraft-AI/src/App.tsx:1396) |
| POE2 앱 분석 | 부분 구현 | 직업·레벨·스킬·자유 메모 폼에서 coach로 간다. 최근 `.build` 파일이나 HC Journey를 여는 입력 경로가 아니다. [폼](D:/Pathcraft-AI/src/components/VerbalBuildInput.tsx:4), [앱 분기](D:/Pathcraft-AI/src/App.tsx:933), [입력 조립](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378) |
| 패시브 트리 탐색·배정 | 구현됨, 데이터 버전 제한 | POE1/POE2 별 트리와 배정 상태를 다룬다. POE2 UI는 `tree_0_4.json`을 가져오며 한국어 번역은 POE1에만 로드한다. 최신 POE2 개인 플래너와 같은 트리라는 보장은 없다. [데이터 경로](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:33), [게임별 상태](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:131), [번역](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:255) |
| POE2 단계별 한국어 가이드·게임용 `.build` | 문서·스크립트·실제 산출물 있음 | 단순 계획서가 아니다. 예를 들어 현재 원본의 임성빈 엔드게임 파일은 작성자·링크·장비·트리·스킬을 가진 JSON이다. 다만 그것은 제작자 스냅샷이지 자동으로 사용자 현재 상태가 되지는 않는다. [실제 파일](<D:/Pathcraft-AI/build_planner/HC 5 실캐릭 엔드게임 - 임성빈.build:1>), [육성 설명](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/planner/임성빈_빌드플래너_업데이트.md:6>) |
| 공개 캐릭터 변화 추적·플래너 갱신 | 스크립트 구현, 앱 통합 미확인 | `track_poe2_character.py`가 공개 응답을 받아 기록하고 생성기→정규화·검사기→플래너 경로로 연결한다. 계정·캐릭터·리그·출력 위치 등 CLI 인자가 필요하다. [조회](D:/Pathcraft-AI/scripts/track_poe2_character.py:74), [호출](D:/Pathcraft-AI/scripts/track_poe2_character.py:196), [인자](D:/Pathcraft-AI/scripts/track_poe2_character.py:270) |
| 여러 제작자의 성장 여정·차이·근거·거래 링크 | 별도 Python/SQLite/HTML 구현 | `.build` fixture→스냅샷→diff→손노트·규칙→HTML까지 코드가 있다. 앱 명령 표에는 해당 로더가 없고 모듈 README도 UI/API를 다음 단계로 적는다. [적재](D:/Pathcraft-AI/python/hc_journey/build_db.py:445), [HTML](D:/Pathcraft-AI/python/hc_journey/render_journey.py:143), [앱 명령](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152), [남은 일](D:/Pathcraft-AI/python/hc_journey/README.md:130) |
| 내 현재 캐릭터와 선택한 목표의 전환 가능성 비교 | 핵심 흐름 미완성 | 보조 PoB는 coach 문맥으로 들어가지만 `current`/`target` 역할 구분과 재료·장비 보유 여부를 사용자에게 확인하는 흐름은 해당 경로에 없다. Journey는 제작자 순차 스냅샷 비교다. [추가 PoB](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:275), [순차 비교](D:/Pathcraft-AI/python/hc_journey/build_db.py:473) |
| 저장·재열기 | POE1 경로 구현, POE2 결함 정황 | 공통 localStorage 히스토리가 있으나 `game` 필드가 없고, 저장 함수는 PoB 링크가 비면 반환한다. 구두 입력은 링크를 비운 뒤 같은 저장 함수를 부르므로 새 POE2 구두 분석의 지속 저장을 보장하지 못한다. [히스토리 스키마](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:5), [저장 조건](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:150), [구두 입력·저장](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:361) |

## 지금 가능한 개인용 사용 절차와 한계

현재 개인 자료는 **Pathcraft 앱을 거치지 않고 문서와 게임 Build Planner를 함께 보는 방식**으로 활용할 수 있다. 아래는 저장된 산출물의 사용 경로를 정리한 것이며, 이번 실사에서 복사·설치·게임 로드를 실행한 것은 아니다.

1. **먼저 목적을 고른다.** 임성빈 육성·52레벨 전환을 따라가려면 첫날/전환 문서를, 제작자 후기 상태를 참고하려면 엔드게임 스냅샷을 본다. 최신 상태 문서는 9월 18일 Lv97 갱신을 기록하고, Journey 입력은 여전히 `05_live_lv93.build`까지 적재한다. 두 경로의 “현재”가 같지 않다. [육성/후기 구분](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/planner/임성빈_빌드플래너_업데이트.md:3>), [최신 상태 기록](D:/Pathcraft-AI/.claude/status/current.md:1), [Journey 입력](D:/Pathcraft-AI/python/hc_journey/build_db.py:231).
2. **파일명을 현재 캐릭터 판정으로 해석하지 않는다.** `build_planner/내 Lv52 화염파 전환.build`는 실제 파일명·표시명은 개인화되어 있어도 `author`가 “임성빈 정본”이고 장비 목표가 들어 있다. “내”라는 이름만으로 사용자의 실착용·방어 수치가 확정되지 않는다. 후기 참고 파일은 `build_planner/HC 5 실캐릭 엔드게임 - 임성빈.build`이며 작성자·링크가 제작자 기준이다. [Lv52 파일](<D:/Pathcraft-AI/build_planner/내 Lv52 화염파 전환.build:2>), [표시명](<D:/Pathcraft-AI/build_planner/내 Lv52 화염파 전환.build:97>), [후기 파일](<D:/Pathcraft-AI/build_planner/HC 5 실캐릭 엔드게임 - 임성빈.build:2>).
3. **검토한 `.build`만 게임 플래너 경로에 둔 뒤 게임 목록에서 해당 표시명을 선택한다.** 저장된 가이드의 경로는 `C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner`이고 생성기도 같은 사용자 Documents 경로를 사용한다. 기존 선택 경로를 바꿔 오류가 난 이력이 있으므로 기존 파일 전체를 치우거나 일괄 덮어쓰는 방식은 이 절차에 포함하지 않는다. 실제 사용 시 파일명·표시명·현재 선택을 함께 확인해야 한다. [경로와 선택 오류 이력](<D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/ready/시작안내.md:47>), [생성기의 경로](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:49), [저장된 수동 사용 안내](<D:/Pathcraft-AI/deliverables/arserina_flameblast_sc_2026-09-07/먼저읽기.md:158>).
4. **화면의 목표와 실제 장착·젬·무기 세트 설정을 별도로 대조한다.** 문서도 플래너의 목표와 캐릭터 설정을 구분한다. 요구 능력치, 소켓/보조 확보, 자원, 재분배 비용이 충족되기 전에는 다음 단계로 넘어갈 근거가 없다. 해당 조건은 현재 앱이 자동 판정해 주는 것으로 확인되지 않았다. [목표·수동 설정](<D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/플래너_설치안내.md:19>), [설정 경계](<D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/플래너_설치안내.md:34>), [요구치·비활성 장비 사례](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/planner/임성빈_빌드플래너_업데이트.md:53>).
5. **새 상태를 원하면 별도 수집·생성 절차가 필요하다.** 추적기는 자동 UI 서비스가 아니고 기본 설치 동작과 캐릭터별 사이드카 주의사항이 있는 운영 스크립트다. 생성·재적재를 수행하지 않아도 기존 문서·HTML·플래너를 참고할 수 있지만, 그 자료가 갱신됐다고 자동 가정할 수 없다. 이번 실사에서는 이 스크립트를 실행하지 않았다. [추적기 옵션](D:/Pathcraft-AI/scripts/track_poe2_character.py:270), [사이드카 경고](D:/Pathcraft-AI/scripts/track_poe2_character.py:283), [주석 갱신 중단 기록](D:/Pathcraft-AI/.claude/status/current.md:4).

따라서 가능한 개인용 범위는 **선정된 빌드의 읽는 가이드, 단계별 게임 플래너, 공개 제작자 스냅샷의 수동 대조, 별도 여정 HTML 열람**이다. 현재 자료에서 자동으로 보장되지 않는 것은 사용자 장비 적합성, HC 생존, SSF 획득 가능성, 최신 패치 적합성, 캐릭터 변화의 앱 반영, 사용자 진행 상태의 안정적 재열기다.

## 연구 자산의 가치와 핵심 단절

### 단순 문서보다 가치 있는 부분

연구는 “최종 장비를 나열”하는 수준을 넘는다. 임성빈 자료는 계획·Lv61 스냅샷·방송에서 실제 실행한 연결을 분리하고 `level_interval`을 젬 등급으로 읽지 말라고 명시한다. 전환 비용, 실제 지능 요구, 장비 비활성, 무기 세트 수정도 프레임 좌표로 남긴다. 잘못 읽은 내용의 정정과 남은 불확실성까지 있어, 향후 **조건부 단계 안내와 근거 표시를 위한 재사용 가능한 사례**다. [계획/실제 구분](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/플래너_대조.md:3>), [전환 비용 정정](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/교차검증_정정.md:48>), [무기 세트 정정](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/교차검증_정정.md:64>).

Skadoosh 최신 Docs는 방송의 시행착오까지 목표에 섞였던 문제를 인정하고 제작자 배포 가이드로 기준선을 바꿨다. 또한 07단계의 트리와 젬이 서로 다른 관측 시점임을 적는다. 이는 출처와 시점을 제품 모델에서 분리해야 한다는 실제 사례다. [기준선 변경·시점 혼합 경고](D:/Pathcraft-AI/Docs/2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md:25).

HC Journey는 손노트와 재사용 규칙을 별도 테이블에 담고, 자동 초안과 승인 상태를 분리한다. HTML은 거래 검색 결과의 시각을 설명하고 오래된 매물 수를 숨긴다. 연구 도구로서 이런 구조는 유지할 가치가 있다. [근거·규칙 스키마](D:/Pathcraft-AI/python/hc_journey/schema.sql:83), [초안 승인 기록](D:/Pathcraft-AI/python/hc_journey/rule_autodraft.py:41), [승인 전 자동 반영 금지](D:/Pathcraft-AI/python/hc_journey/rule_autodraft.py:429), [시각 표시](D:/Pathcraft-AI/python/hc_journey/render_journey.py:151).

### 앱과 이어지지 않은 호출 경로

- **앱 POE1:** `App.selectResearchBuild → useBuildAnalyzer.analyzeBuildCore → resolve_build_source / parse_pob → pob_parser.py → coach_build / build_coach.py → 가이드·장비·패시브 UI`. 입력 PoB의 Notes도 파싱한다. [선택](D:/Pathcraft-AI/src/App.tsx:754), [Rust→Python](D:/Pathcraft-AI/src-tauri/src/lib.rs:113), [Notes](D:/Pathcraft-AI/python/pob_parser.py:155), [결과 표시](D:/Pathcraft-AI/src/App.tsx:1426).
- **앱 POE2:** `VerbalBuildInput → 최소 JSON → coach_build`. 메타·스킬·메모만 조립하며 장비·방어·예산·패치·HC/SSF가 구조화된 입력에 없다. 외부 `.build` 생성기를 호출하는 경로가 아니다. [실제 입력 조립](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378).
- **최근 POE2 개인 자료:** `track_poe2_character → 공개 캐릭터 응답/PoB → build_poe2_planner_files → import_poe2_planner_files → build_planner/`. 이 중간 결과가 앱 입력으로 자동 이어지지 않는다. [스크립트 연결](D:/Pathcraft-AI/scripts/track_poe2_character.py:196), [앱 명령 전부](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152).
- **HC Journey:** `data/hc_journey/creators/*.build → build_db.load_build/diff_snapshots → SQLite → render_journey → 별도 HTML`. 고정 제작자 설정을 수정하고 재생성하는 운영 흐름이며, 사용자 프로필 관리 화면과는 다르다. [원본 로더](D:/Pathcraft-AI/python/hc_journey/build_db.py:73), [제작자 설정](D:/Pathcraft-AI/python/hc_journey/build_db.py:224), [렌더](D:/Pathcraft-AI/python/hc_journey/render_journey.py:215).

## 잘못된 추론이 생기는 구체 지점

| 지점 | 정적 근거와 구체 사례 | 제품에 필요한 처리 |
|---|---|---|
| “WHAT/WHEN 100% 자동”을 완전한 비교로 해석 | README의 문구와 달리 `load_build`는 장비 텍스트 첫 줄과 패시브 배열 길이만 비교에 남긴다. 같은 베이스의 생명력·저항 옵션만 바뀌거나 동일 점수로 패시브 위치/무기 세트가 바뀌면 그 차이는 이 diff에서 표현되지 않는다. inventory도 슬롯 ID 사전이므로 같은 슬롯 ID의 여러 항목은 덮일 수 있다. 이는 코드로부터의 추론이며 이번 실행 재현은 없다. [문구](D:/Pathcraft-AI/python/hc_journey/README.md:8), [축약](D:/Pathcraft-AI/python/hc_journey/build_db.py:73), [비교](D:/Pathcraft-AI/python/hc_journey/build_db.py:103) | 옵션·노드 ID·무기 세트·젬 등급/소켓·장비 위치를 보존하고, 미지원 비교 항목을 화면에 표시한다. |
| 제작자 계획→실캐릭 순서를 실제 성장 시간축으로 오해 | 임성빈 DB는 ACT3-4 → 엔드게임 계획 → Lv93 실캐릭을 순차 전환으로 만든다. “목표에서 실제로 이동했다”는 사건 증거가 아니라 계획과 관측의 차이다. 스냅샷 스키마에는 `captured_utc`가 있어도 현 INSERT는 그 값을 채우지 않는다. [밴드](D:/Pathcraft-AI/python/hc_journey/build_db.py:231), [적재](D:/Pathcraft-AI/python/hc_journey/build_db.py:462), [시각 필드](D:/Pathcraft-AI/python/hc_journey/schema.sql:33) | planned/observed/user-current 역할과 관측일을 나누고, 서로 다른 역할을 비교했음을 명시한다. |
| POE2 최신 자료를 앱의 최신 게임 데이터로 간주 | 자료는 0.5.5를 대상으로 적지만 UI 트리는 0.4이고 젬 DB 메타는 0.4.0d다. 생성기는 그 낡은 표에 없는 `VirtuousBarrier` 등을 PoB 경로 그대로 보존하도록 이미 보완했다. 이 보완이 앱 전체 패치 호환성을 증명하지는 않는다. [자료 표기](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/planner/임성빈_빌드플래너_업데이트.md:6>), [UI 트리](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:34), [젬 메타](D:/Pathcraft-AI/data/valid_gems_poe2.json:3), [생성기 예외](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:139) | source_patch/data_patch/target_patch를 따로 표시하고 불일치나 알 수 없음은 검증 전 확정 안내에서 제외한다. |
| POE1/POE2 토글만으로 자료가 분리됐다고 간주 | POE2를 선택해도 리서치 컴포넌트는 `load_poe1_research_dashboard`를 부른다. 히스토리 스키마에 game이 없고 복원 함수도 game을 복원하지 않는다. 별도 경고 배너는 있지만 자료의 귀속을 강제하지 않는다. [탭 렌더](D:/Pathcraft-AI/src/App.tsx:917), [로더](D:/Pathcraft-AI/src/components/ResearchDashboard.tsx:1270), [저장](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:5), [복원](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:175) | 게임별 자료·히스토리·캐시·선택 상태를 일관되게 분리한다. |
| HC와 SSF를 같은 축으로 처리 | UI 모드는 `sc/ssf/hcssf`로 HC Trade가 없다. POE2 구두 입력은 모드 자체를 넘기지 않으며 coach 문맥 기본값은 sc다. 자유 메모의 “하코”가 구조화된 조건 검증을 대신할 수 없다. [모드](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:33), [구두 입력](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378), [기본값](D:/Pathcraft-AI/python/build_coach.py:1371) | hardcore와 trade/ssf를 독립 필드로 두고 unknown을 허용한다. |
| “HC 근거 없음”을 SC 확정 또는 HC 거래시장으로 변환 | ds lily/Fubgun 항목은 “HC 근거 없음”으로 `hardcore=0`인데 `league`는 `hc-forbidden-rites`다. 렌더는 0을 SC라고 표시하고, 거래 링크는 league 문자열을 따른다. 이는 저장된 설정 내부의 모순이지 해당 제작자의 실제 모드를 새로 판정한 결과가 아니다. [설정](D:/Pathcraft-AI/python/hc_journey/build_db.py:278), [표시](D:/Pathcraft-AI/python/hc_journey/render_journey.py:64), [검색 리그](D:/Pathcraft-AI/python/hc_journey/trade_links.py:393) | 미확인과 SC를 구분하고 근거 없는 리그의 거래 링크는 생성 보류한다. |
| SSF 가이드 제목을 현재 HC 실캐릭의 SSF 증명으로 사용 | Blazeworks 항목은 제목이 SSF여도 관측 캐릭터 리그 때문에 ssf=0으로 둔다. 이 분리는 좋은 판단이다. 그러나 SSF 규칙이 없는 동안 조용히 노트가 0건이고, 거래 링크 생성 루프에는 ssf 건너뛰기가 없다. 현재 등록 사례의 ssf=0을 넘어 SSF 지원 완료라고 확대할 수 없다. [분리한 설정](D:/Pathcraft-AI/python/hc_journey/build_db.py:336), [SSF 노트 부재](D:/Pathcraft-AI/python/hc_journey/README.md:21), [거래 생성 루프](D:/Pathcraft-AI/python/hc_journey/trade_links.py:393) | SSF에서 구매 링크 대신 획득 경로·대체안·불가능/미확인 조건을 제공한다. |
| 한국어 설명이면 게임명 검색도 해결됐다고 간주 | 한국어 가이드와 영문/메타 ID 자산은 있지만 POE2 폼은 영문 직업 목록·자유 텍스트 입력이고 트리 번역은 POE1 전용이다. HC Journey의 `_short`는 메타 ID 앞부분 제거이지 한영 이름 해소가 아니다. [입력](D:/Pathcraft-AI/src/components/VerbalBuildInput.tsx:20), [트리 번역](D:/Pathcraft-AI/src/components/PassiveTreeCanvas.tsx:255), [ID 축약](D:/Pathcraft-AI/python/hc_journey/build_db.py:68) | 정본 ID와 한국어/영문 명칭을 함께 유지하고, 해소 실패한 이름은 사용자가 검색·확인하도록 한다. |
| 일반화된 기본값을 사용자 현재 상태로 간주 | POE1 추천 문맥은 빌드명에서 레벨을 찾고 없으면 90, 기본 예산 3 divine, 사망 허용 medium을 넣는다. 실제 보유 예산·레벨·HC 위험 허용을 입력받은 판정과 다르다. [현재 상태 조립](D:/Pathcraft-AI/python/recommend_from_corpus.py:152) | 자동 추정값과 확인된 사용자 값을 구분하고, 결정을 바꾸는 값은 사용자 입력이나 신뢰 가능한 가져오기로 확정한다. |

앱 가이드 캐시는 입력과 게임·모델 해시로 분리하지만 데이터/패치 갱신 식별자를 키에 직접 포함하지 않는다. 따라서 게임 데이터가 바뀌었을 때 이전 가이드의 재검증·무효화 기준도 최소 완결 범위에 필요하다. [현재 캐시 키](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:282).

## “검증됨”의 경계

기존 보고서에는 실제 게임 로그에서 플래너 7개 로드와 02 트리 표시를 확인했다는 기록이 있다. 동시에 실전 전투 성능은 직접 검증하지 않았다고 적는다. 더 최근 설치 안내는 05/06 트리 교체 후 게임 내부 재불러오기가 미확인이라고 한다. 따라서 **과거 일부 버전의 파일 로드 성공 → 현재 전체 산출물의 로드 성공 → 전투에서 안전함**으로 이어지는 추론은 금지해야 한다. 이번 실사는 이 기록을 읽었을 뿐 재실행하지 않았다. [과거 검사와 한계](<D:/Pathcraft-AI/deliverables/skadoosh_hc_2026-09-07/ready/검증결과.md:15>), [후속 버전 경계](<D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/플래너_설치안내.md:4>).

같은 원칙은 영상에도 적용된다. 임성빈 플래너 문서는 정지 화면 판독 기반이고 직접 청취 0초였다고 밝힌다. 링크 문법·시각 범위 검사가 실제 영상 재생이나 연속 전투 검증을 대신하지 않는다. 최신 아틀라스 기록도 미확정 노드와 별도 적대검증을 하지 않은 확장분을 남긴다. [판독 범위](<D:/Pathcraft-AI/deliverables/seongbin_from_day1_2026-09-09/planner/임성빈_빌드플래너_업데이트.md:10>), [링크/게임 검사 한계](D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/validation.json:28), [최신 아틀라스 한계](D:/Pathcraft-AI/.claude/status/poe2_hc_gemling.md:671).

## 최소 완결 제품 범위 권고

**최소 범위는 한 게임·패치와 근거 있는 소수 빌드 계열 안에서 사용자 조건을 반영한 완성 구성과 연속 성장 단계를 만드는 것으로 제안한다.** 특정 게임·클래스·스킬은 이 실사에서 확정하지 않는다. POE2 개인 자료의 풍부함이나 POE1 앱 연결은 후보를 고를 근거이며 특정 제작자 빌드 복제만으로 제품 목표를 대신하지 않는다. [개인 자료 맥락](D:/Pathcraft-AI/.claude/status/current.md:1), [POE1 연결](D:/Pathcraft-AI/src/App.tsx:754), [생성 범위 제안](build_generation_readiness.md).

선택한 범위에서 다음 여섯 가지가 하나의 화면 흐름으로 이어져야 한다. 지원 밖 모든 빌드의 범용 최적화·자동 대량 수집·OAuth는 필수 선행 조건이 아니다. 검증된 소수 자료로 시작하더라도 사용자 조건에 따른 실질적인 구성 생성·변형과 검증은 포함해야 한다.

1. **요청 입력:** 게임·패치, 클래스/주력스킬의 고정·선호 여부, 플레이스타일, 예산·보유 자산, HC와 Trade/SSF, 목표 성장 구간을 구분한다. 현재 캐릭터/PoB는 선택 입력이다. 미입력을 0·SC·기본 예산으로 확정하지 않고 생성에 필요한 최소 입력과 선택 입력을 표시한다.
2. **자료 기반 구성:** 호환되는 자료를 선택해 스킬·지원젬·패시브·장비 요구/대체안·자원 운영을 단계별 빌드로 조합·변형한다. 각 구성의 출처·버전과 유지/변경 이유를 남기며 제작자 장착품 전부를 필수품으로 바꾸지 않는다. 필수·권장·예시·미확인을 구분한다.
3. **전체 조합 검증과 성장 경로:** 단계마다 레벨/능력치·지원 호환·소켓·패시브 연결/포인트·자원·장비·확보 가능성을 검증하고 단계 간 선행조건과 전환 비용을 확인한다. 공격/생존 성능은 검증 방법과 가정이 없는 숫자로 채우지 않는다. 핵심 충돌/미확인이면 확정 생성을 보류하고 대안·필요 입력을 제시한다.
4. **근거:** 각 핵심 조건은 원본 파일/영상 좌표와 관측 시점, 계획/실측/추정 상태로 연결한다. 패치 불일치·단일 정지 화면·로드 검사·전투 검증의 차이를 같은 화면에서 읽을 수 있어야 한다. 정정된 주장에는 이전 판정이 남지 않아야 한다.
5. **수정·저장·재열기:** 예산·보유품·스킬·선호 변경 시 영향받은 구성을 다시 생성·검증한다. 요청·생성 빌드 revision·근거·단계·미확인을 저장하고 재시작 후 복원한다. 현재/목표 비교는 수정·성장의 보조이며 원본이나 이전 결과를 조용히 덮어쓰지 않는다.
6. **외부 플래너 사용:** 필요하면 기존 `.build`를 내보내거나 위치를 안내하되, 파일 생성/검사·게임 로드·실전 확인 상태를 따로 적는다. 자동 설치 없이도 핵심 비교와 가이드 흐름은 완결되어야 한다.

이 설계는 기존 문서의 `patch/character/availability/confidence guard`와 AI를 설명자로 제한한 방향을 실제 사용자 경로까지 적용하는 것이다. [판정 경계](D:/Pathcraft-AI/Docs/2026-07-10_DETERMINISTIC_AI_BOUNDARY.md:12), [AI 역할](D:/Pathcraft-AI/Docs/2026-07-10_DETERMINISTIC_AI_BOUNDARY.md:40).

## 개인용 → 소규모 검증의 통과 조건

아래는 후속 구현·검증 담당자가 수행할 **관측 가능한 합격 기준**이다. 이번 읽기 전용 작업에서 통과했다고 선언하지 않는다.

| 게이트 | 합격을 보여 줄 증거 | 현재 평가 |
|---|---|---|
| G1 생성 흐름 완결 | PoB 없이 지원 범위의 조건을 제출해 자료 기반 빌드 구성과 성장 경로를 생성하고, 조건 변경에 따라 구성·검증 결과가 바뀌며, 저장/재열기 후 같은 revision이 복구되는 연속 기록 | 미확인. 코칭 초안·추천·변환과 완성 구성 생성의 연결 보완 필요 |
| G2 비교의 중요한 차이 보존 | 같은 베이스의 옵션만 변경, 동일 점수 트리 재배치, 무기 세트만 변경, 보조 등급·소켓 변경 사례에서 차이를 놓치지 않음. 못 비교하는 스탯은 명확히 표시 | 현 Journey 축약 방식은 충분하지 않음 |
| G3 게임·패치·모드 격리 | POE1/POE2 전환·히스토리 복원 후 자료가 섞이지 않음. 데이터 패치와 목표 패치 불일치 시 확정 안내 보류. HC Trade, SC SSF, HCSSF, 모드 미확인 사례의 화면/다음 행동이 각각 구분됨 | 입력·히스토리·자료 버전 계약 보완 필요 |
| G4 단계 안전·획득 가능성 | 요구 능력치·핵심 젬/장비·자원이 부족한 실제 사례는 전환 보류 또는 검증된 대체 단계로 남음. SSF 사례는 구매를 해결책으로 내놓지 않음. 필수품 판단을 착용 목록과 구분함 | 문서에 좋은 사례가 있으나 앱 판정 연결 미완성 |
| G5 한국어/영어·근거 추적 | 동일 아이템/스킬의 한영 입력이 같은 정본 ID에 연결됨. 없는 이름은 미확인으로 처리. 사용자 핵심 의사결정마다 출처·패치·관측시각·확신 수준을 열 수 있음 | 부분 자산 존재, 일관된 사용자 흐름 미완성 |
| G6 자료 갱신과 재현성 | 원본 체크아웃 밖의 새 사용자 환경에서 필요한 자료를 안내대로 가져오거나 제공받아 같은 결과를 재현. 문서/`.build`/Journey의 개정 ID를 비교 가능. 갱신 후 예전 캐시와 미적재 스냅샷을 감지 | 원본 의존 경로·수동 재생성·최신본 분산이 남음 |
| G7 소규모 관찰 사용 | 해당 빌드/모드의 소수 사용자가 G1 흐름을 독립 수행. “무엇을 바꾸고 왜 멈추는지” 이해 여부와 오판 사례를 기록. 발견된 중대한 패치·HC·SSF·단계 오판은 원인/수정/재확인 후 종료 | 아직 이 실사로 확인할 자료 없음 |

G1–G6 이전에는 연구자/개발자 동반 개인 도구로 설명하는 것이 적절하다. 그 뒤에 소규모 검증을 진행하되 파일 파싱 성공이나 테스트 개수를 실제 사용 완료·HC 안전의 대체 지표로 삼지 않는다. 설치 배포성을 확인할 때는 현재 Rust가 시스템 `python`과 프로젝트 `python/` 디렉터리를 찾는 구조도 재현 대상이다. [런타임 경로](D:/Pathcraft-AI/src-tauri/src/lib.rs:51).

## 전달·검토·미완료

전달물은 이 한국어 보고서 `personal_product.md` 하나다. 원본 제품 코드·자료·필터는 변경하지 않았다. 실제 호출 경로와 대표 원본 파일을 교차 읽었으며, 최신 상태 문서와 구현이 다른 곳은 문서의 완료 선언 대신 코드와 개정 이력을 근거로 판정했다. 초기 보고서의 원본 인용 116개는 파일 존재와 지정 줄번호 범위를 읽기 전용으로 확인했다. 후속 Atlas 내용과 그 별도 검토 경계는 다음 장에 추가했다.

남은 핵심은 **조건 입력→근거 자료의 조합·변형→빌드와 성장 경로 생성→전체 조합 검증→수정·저장**의 연속 증거다. 첫 게임·패치·계열·허용 변형·성장 구간은 사용자와 정할 후속 범위이며 이 평가가 임의 확정하지 않는다. PoB/게임 플래너 내보내기나 현재 캐릭터 비교는 생성 결과 사용의 보조다. 기존 선택 테스트와 일부 파일 로드 이력을 생성 품질 PASS로 계산하지 않는다.

## Atlas 추가 장 — 외부 레퍼런스 수신 검토와 개인용 앱 계약

추가 검토: 2026-09-21, Asia/Bangkok(+07:00), 원본 읽기 17:09부터. 후속 Task task_d8b58bc9e030 / Dispatch ctx_c2a10749908a에 따라 기존 본문을 보존하고 추가했다. 지정된 [전달 문서](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:1)와 [송수신 계약](D:/contracts/atlas-viewer-to-pathcraft-app.md:1)을 **전체 읽었다**. 두 문서의 브라우저 실행·직접 추출·Docs 작성 요청 중 이번 소유권 밖의 작업은 수행하지 않았다. R1과 R3는 구현 담당, 권리 검토는 상용 담당, 정식 receiver review와 settlement는 책임자 몫이다.

### A. 기존 제품 판정에 더해지는 것

아틀라스는 **생성된 빌드의 성장·파밍·제작을 돕는 보조 진행 플래너**다. 전달 문서의 PoB/캐릭터 입력은 해당 기능의 입력 예시이며 제품 전체를 PoB 분석 도구로 제한하지 않는다. 이번 자료에는 독립 HTML과 그래프·순서 산출물이 있다. [Atlas 목적](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:9), [레퍼런스 목록](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:17).

다만 **외부 레퍼런스이며 현재 Tauri 앱 통합 기능으로 확인되지 않았다.** 현 앱에는 파밍 UI의 아틀라스 초·중·후반 설명과 패시브 초점 텍스트가 있고, 독립 HTML에는 단계·노드·순번·커서와 재생 JS가 있다. 이번에 읽은 src, 앱 진입, 등록 명령에서는 이 전달물의 atlas_tree/full_order/stage_lists를 가져오는 경로를 찾지 못했다. PassiveTree 코드의 “atlas” 변수 대부분은 스프라이트 이미지 아틀라스이므로 아틀라스 패시브 계획 기능의 증거가 아니다. [현 앱 텍스트 영역](D:/Pathcraft-AI/src/components/sections/FarmingStrategy.tsx:196), [등록 명령](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152), [스프라이트 아틀라스의 의미](D:/Pathcraft-AI/src/utils/passiveTreeSprites.ts:1), [독립 뷰어 상태](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:2976).

개인용으로는 저장된 순서를 검토하는 레퍼런스가 추가된 것이고, 개인 캐릭터에 맞는 아틀라스 추천이 완성된 것은 아니다. PoB의 빌드 상태만으로 현재 아틀라스 할당·획득 포인트·선택형 옵션·지역 진행을 알 수 있다고 가정해서는 안 된다. 전달 자료도 범용 HC 경로와 특정 제작자의 화면 복원본을 구분한다. [범용/제작자 페이지 구분](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:17), [현재 구두 입력 필드](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378).

### B. 송신 보고와 수신 측 확인을 분리한 상태표

| 항목 | 송신 측 기록 | 이번 개인용 작업자의 수신 측 확인 |
|---|---|---|
| S1 노드 수와 게임 화면 카운터 일치 | PASS 보고 | 저장 JSON의 비루트 수는 같은 숫자로 집계했다. 방송 화면·게임 카운터와의 대조는 수행하지 않았다 |
| S2 초반 경로 루트 연결·11목표 | PASS 보고 | 저장 그래프를 무방향 인접 그래프로 읽어 59개(루트 포함) 도달, 비루트 58개, 목표 이름 11개 각각 1개 ID 포함을 확인했다. 게임의 실제 할당 적법성은 미검증 |
| S3 총 530·중복 없음 | PASS 보고 | stage_lists의 노드 ID 530개·유일 ID 530개, 비루트 집합과 완전 일치, full_order와 트리별 순서 일치를 확인했다 |
| S4 JS 오류·재생·멈춤·자동 넘김 | Chrome PASS 보고 | 코드의 이벤트/상태 전이는 읽었다. 브라우저를 열지 않았고 S4를 수신 측 PASS로 승격하지 않는다 |
| S5 위험도 정확성 | 부분: 본 트리 5건 수정, 서브트리·58 이후 미검증 | **부분 상태 그대로** 유지한다. 후반 순서의 그래프 연결 확인은 위험 분류·순서 품질 적대검증의 대체가 아니다 |
| R1 로컬 브라우저 동작 | 수신 측 요구 | 이 작업에서 미수행, 구현 담당 결과 대기 |
| R2 537노드·255그룹 | 수신 측 요구 | **이번 직접 JSON 계수로 PASS** |
| R3 GGPK 아틀라스 PSG 직접 추출 가능성 | 상용 판단 전 요구 | 이 작업에서 미수행, 구현 담당 결과 대기. 기술 가능성 확인과 상용 권리 판단은 별개 |

근거: [S1–S5 계약](D:/contracts/atlas-viewer-to-pathcraft-app.md:15), [R1–R3 계약](D:/contracts/atlas-viewer-to-pathcraft-app.md:25), [노드 원본 — JSON /nodes, /groups](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/atlas_tree.json:1), [순서 원본](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/full_order.json:1), [단계 원본](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/stage_lists.json:1). minified JSON은 실제 한 줄이므로 줄번호 1과 JSON 필드명을 함께 인용한다.

### C. 직접 읽은 집계 결과와 의미

**노드/그룹.** atlas_tree.json의 최상위는 groups와 nodes다. nodes 537개 중 isRootOfAtlasTree인 루트는 7개이며, 나머지 530개가 단계 목록에 들어 있다. 그룹 255개다. out의 대상 ID 누락, 노드의 group 참조 누락, screen_xy의 노드 좌표 항목 누락은 각 0건이었다. 좌표 항목이 있다는 것과 실제 게임 배치/렌더 좌표가 맞는 것은 다른 검사다. [트리](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/atlas_tree.json:1), [좌표](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/screen_xy.json:1).

| 트리 | 루트 ID | 비루트 수 | 초록 목록 | 빨강 목록 |
|---|---:|---:|---:|---:|
| 본/Main | 25703 | 336 | 58 | 37 |
| 의식/Ritual | 18887 | 36 | 22 | 14 |
| 인커전/Incursion | 14255 | 36 | 29 | 7 |
| 심연/Abyss | 63227 | 35 | 22 | 13 |
| 균열/Breach | 5477 | 32 | 17 | 15 |
| 환영/Delirium | 30679 | 31 | 24 | 7 |
| 탐험/Expedition | 25844 | 24 | 19 | 5 |

본 트리의 나머지는 파랑 147개(59–205), 노랑 60개(206–265), 주황 34개(266–299)다. **전체 색 단계별 목록 수는 초록 191 / 파랑 147 / 노랑 60 / 주황 34 / 빨강 98, 합계 530**이다. 초록 칩의 “1~58”은 본 트리 순번이며 초록 목록 전체의 개수가 아니다. 서브트리마다 독립 순번과 루트가 있으므로 이를 “캐릭터가 확보한 포인트 총 530”이나 “본 트리 58포인트로 초록 191개 전부 가능”으로 표시하면 틀린다. [목록 원본](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/stage_lists.json:1), [단계 배정 방식](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_svg.py:20), [뷰어가 순번을 구분하는 문구](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3010).

**530개의 범위.** full_order.json에는 초반 노드 58개가 배열로 들어 있는 것이 아니라 main_start라는 정수 58이 있다. 배열 부분은 main_rest 278개 + 서브트리 194개 = 472개다. stage_lists에서 본 트리 순번 1–58을 복원해 합쳐야 530개가 된다. 그 복원본은 hc_route_result.nodes에서 루트 25703을 뺀 집합과 일치했다. 본 트리 나머지 및 6개 서브트리는 full_order와 stage_lists의 트리별 순번 정렬 결과가 배열 순서까지 같았다. 트리별 i는 각각 1부터 개수까지 빠짐없이 이어졌다. [main_start와 배열](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/full_order.json:1), [초반 저장 노드](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/hc_route_result.json:15), [생성기의 초반 결합](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_svg.py:14).

**초반 58 연결·11목표.** hc_route_result.nodes는 중복 없는 59개 ID이며 루트 하나를 포함한다. 루트로부터 해당 집합 안의 59개가 모두 도달 가능했다. stage_lists의 본 트리 1–58 순서에서 매 노드는 루트 또는 이미 앞서 추가한 노드 중 하나와 인접했다(끊긴 prefix 0건). 목표는 다음과 같이 각각 정확히 1개 ID로 포함됐다. [목표 원본](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/hc_route_result.json:2), [노드 정의](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/atlas_tree.json:1).

| 저장된 목표 이름 | 확인한 ID |
|---|---:|
| Specialised Seeker | 25802 |
| Essence Dowsing | 38492 |
| Archaeological Interest | 50652 |
| Valuable Paths | 38181 |
| The Chosen Path | 4434 |
| Eons of Contamination | 7839 |
| Reverse Transcription | 28843 |
| Industrial Improvements | 8122 |
| Divined Blessing | 7116 |
| Hidden Scars | 18956 |
| Eons of Domination | 42764 |

**연결된 순서와 바로 옆 순서는 다르다.** 같은 prefix 검사를 본 트리 336개와 각 서브트리 전체에 적용해도 끊김은 각 0건이었다. 그러나 직전 노드와 바로 인접하지 않은 이동은 본 139회, 의식 15, 인커전 12, 심연 13, 균열 13, 환영 13, 탐험 12회다. 이는 이미 찍은 다른 가지로 이동하는 경우를 포함하며 연결 실패와 같지 않다. 저장 생성기는 같은 위험 등급에서 직전 노드 인접→화면 거리→ID 순으로 고르고, 특정 조건에서는 gate 탐색 결과를 우선한다. 이번 계산은 그 우선순위의 최적성이나 모든 거리 선택을 독립 검증하지 않았다. [무방향 그래프 정규화](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_order.py:44), [우선순위·예외](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_order.py:54).

**단계 색은 안전 인증이 아니다.** 저장된 분류를 단순 계수하면 본 트리 초록 58개는 안전 35·주의 15·위험 3·선택형 5, 빨강 37개는 위험 35·주의 2다. 이는 분류 라벨 분포를 읽은 결과이며 라벨의 게임상 정확성을 확인한 것이 아니다. 서브트리도 최초 주의/위험 이후의 모든 노드를 빨강으로 묶으므로 빨강 목록에는 안전 라벨 노드가 있을 수 있다. 단계 ID와 위험 등급을 같은 필드로 합치면 사용자 의도가 손상된다. [저장 라벨](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/stage_lists.json:1), [서브트리 단계 묶기](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_svg.py:25).

### D. 실제 사용한 집계 명령

아래 PowerShell 명령을 실제 실행했다. 리포지토리 모듈을 import하거나 제품 생성기·검사기·테스트를 호출하지 않는다. 파일은 읽기만 하고 계산은 메모리에서 수행한다. out 연결을 양방향으로 정규화한 것은 전달된 생성기의 graph 방식에 맞춘 **파일 그래프 검사 가정**이며, 게임의 숨은 할당 규칙을 증명하는 가정은 아니다.

~~~powershell
@'
import json, hashlib
from pathlib import Path
from collections import Counter
base = Path("D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data")
names = ["atlas_tree.json", "full_order.json", "stage_lists.json", "hc_route_result.json", "screen_xy.json"]
raw = {n: (base/n).read_bytes() for n in names}
tree, full, stages, route, xy = [json.loads(raw[n]) for n in names]
N = tree["nodes"]
roots = {n.get("subTree", "Main"): k for k,n in N.items() if n.get("isRootOfAtlasTree")}
allocated = set(N)-set(roots.values())
adj = {k:set() for k in N}
missing_edges = []
for k,n in N.items():
    for v in n.get("out", []):
        if v not in adj: missing_edges.append([k,v])
        else: adj[k].add(v); adj[v].add(k)
rows = [r for a in stages.values() for r in a]
ids = [r["k"] for r in rows]
bytree = {t:sorted([r for r in rows if N[r["k"]].get("subTree","Main")==t],key=lambda r:r["i"]) for t in roots}
seq = {t:[r["k"] for r in a] for t,a in bytree.items()}
def prefix_breaks(order, root):
    have, bad = {root}, []
    for i,k in enumerate(order,1):
        if not adj[k]&have: bad.append([i,k])
        have.add(k)
    return bad
route_ids = set(route["nodes"])
seen, pending = {roots["Main"]}, [roots["Main"]]
while pending:
    for v in (adj[pending.pop()] & route_ids)-seen:
        seen.add(v); pending.append(v)
out = {
 "sha256": {n:hashlib.sha256(raw[n]).hexdigest() for n in names},
 "R2": {"nodes":len(N),"groups":len(tree["groups"]),"roots":roots},
 "non_root_counts":dict(Counter(N[k].get("subTree","Main") for k in allocated)),
 "missing_edge_ids":missing_edges,
 "missing_groups":[k for k,n in N.items() if str(n.get("group")) not in tree["groups"]],
 "missing_xy":sorted(set(N)-set(xy)),
 "stage_counts":{c:dict(Counter(N[r["k"]].get("subTree","Main") for r in a)) for c,a in stages.items()},
 "stage_total":len(ids),"stage_unique":len(set(ids)),
 "duplicate_ids":[k for k,c in Counter(ids).items() if c>1],
 "coverage_missing":sorted(allocated-set(ids)),"coverage_extra":sorted(set(ids)-allocated),
 "full_main_start":full["main_start"],
 "full_array_counts":{k:len(v) for k,v in full.items() if isinstance(v,list)},
 "full_main_rest_equal":full["main_rest"]==seq["Main"][full["main_start"]:],
 "full_sub_equal":{t:full[t]==seq[t] for t in roots if t!="Main"},
 "ordinals_contiguous":{t:[r["i"] for r in a]==list(range(1,len(a)+1)) for t,a in bytree.items()},
 "route":{"raw_count":len(route["nodes"]),"unique":len(route_ids),"allocations":len(route_ids-set(roots.values())),
          "reachable":len(seen),"unreachable":sorted(route_ids-seen),
          "first58_equal":route_ids-set(roots.values())==set(seq["Main"][:58]),
          "target_matches":{name:[k for k in route_ids if N[k].get("name")==name] for name in route["targets"]},
          "first58_prefix_breaks":prefix_breaks(seq["Main"][:58],roots["Main"]),"saved_score":route["score"]},
 "prefix_breaks_all":{t:prefix_breaks(s,roots[t]) for t,s in seq.items()},
 "consecutive_nonadjacent":{t:sum(b not in adj[a] for a,b in zip([roots[t]]+s,s)) for t,s in seq.items()}
}
print(json.dumps(out,ensure_ascii=True,indent=2))
'@ | python -X utf8 -
~~~

결과는 위 C절과 같다. 주요 원시 출력은 R2={nodes:537,groups:255}, stage_total=530, stage_unique=530, duplicate_ids=[], coverage_missing=[], coverage_extra=[], full_main_rest_equal=true, full_sub_equal의 6개 값 모두 true, ordinals_contiguous의 7개 값 모두 true, route={raw_count:59,unique:59,allocations:58,reachable:59,unreachable:[],first58_equal:true,first58_prefix_breaks:[]}, prefix_breaks_all의 7개 배열 모두 []였다. 저장 score는 [3,15,58]이었다. 이를 최단/최소 위험 증명으로 확대하지 않는다. [저장 score](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/hc_route_result.json:364), [수학적 최소 미증명 고지](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:48).

라벨 분포는 다음의 별도 읽기 명령으로 집계했다.

~~~powershell
@'
import json
from pathlib import Path
from collections import Counter
b=Path('D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data')
t=json.loads((b/'atlas_tree.json').read_bytes())['nodes']
s=json.loads((b/'stage_lists.json').read_bytes())
print(json.dumps({'main_green_labels':dict(Counter(r['c'] for r in s['g'] if not t[r['k']].get('subTree'))),'main_red_labels':dict(Counter(r['c'] for r in s['r'] if not t[r['k']].get('subTree')))},ensure_ascii=True))
'@ | python -X utf8 -
~~~

집계한 정확한 파일 버전을 식별하는 SHA-256은 다음과 같다. 파일은 이 작업에서 수정하지 않았다.

| 파일 | SHA-256 |
|---|---|
| atlas_tree.json | cb460643cbb4c29d9efd9533ca6893a49498cc4a1870858f6eb58181686efe48 |
| full_order.json | 5955908059ea8765f66be872a960f90b0193f65b8b3b4cc395ae93ef7d25f086 |
| stage_lists.json | caaee0d38c8ca03efa061e95a912d034b8f6c5b82b83fef8b7cce89dfca1b6db |
| hc_route_result.json | a20b982e1cd7b348c95770e106728c72964771d6de891bd52f18b1726af4e3e3 |
| screen_xy.json | fc5da72350fc21ad0c1a097edbdb870f216a21b78b44616c0608670c39d44dd0 |

### E. 남겨야 할 미확인 사항

1. **S5 부분 상태:** 본 트리 분류 5건을 고쳤다는 것은 송신 보고다. 서브트리 위험 분류와 58 이후 순서의 적대검증은 미실시다. 이번 prefix 연결성 계산은 정합성만 보완하며 S5를 PASS로 바꾸지 않는다. “안전”은 현재 분류 정책의 라벨로 표시하고 해당 패치·빌드의 생존 보장으로 쓰지 않는다. [계약 S5](D:/contracts/atlas-viewer-to-pathcraft-app.md:23), [정규식 변경 위험](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:46).
2. **311 vs 336:** 이번 336은 본 트리 비루트 노드 수로 확인했다. 0.5.0~0.5.4 자료의 총 포인트 311과 0.5.5 화면 336/336의 불일치는 여전히 미확인이다. 노드 수를 세어도 캐릭터가 얻을 수 있는 총 포인트나 “결국 전부 찍는다”는 명제는 증명되지 않는다. 레퍼런스 서두의 그 표현은 앱에서 확정 규칙으로 수용하지 말아야 한다. [불일치 고지](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:50), [전부 찍는다는 템플릿 표현](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/hcguide/template.html:86), [템플릿 자체의 미확인 주석](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/hcguide/template.html:99).
3. **지역 70/75 조건:** 전달 문서는 노드별 해당 지역 조건이 데이터에 없다고 명시한다. 원본 노드의 필드 집합은 color/edgeOrbits/group/icon/isKeystone/isNotable/isRootOfAtlasTree/name/orbit/orbitIndex/out/skill/stats/subTree였고, 별도의 적용 지역 레벨 필드는 없었다. 어떤 stat가 조건을 암시하는지까지 해석한 것은 아니다. 앱은 미확인을 조건 없음으로 바꾸거나 캐릭터 레벨로 대체하면 안 된다. [조건 누락](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:50), [노드 원본](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/atlas_tree.json:1).
4. **포인트 획득 출처:** 지역 맵 1·정점 보스 6·대탐험 보스라는 서브트리 포인트 출처는 0.5 기준 2차 자료에 의존하며 0.5.5 공식 1차 확인이 안 되어 있다고 계약에 적혀 있다. 이번 작업에서 최신 공식 사실을 새로 확인하지 않았고, 그 수치를 현재 획득 규칙으로 채택하지 않는다. [포인트 출처 경계](D:/contracts/atlas-viewer-to-pathcraft-app.md:37).
5. **출처·권리:** 레이아웃은 poe.ninja 번들, 제작자 트리/선택형 이름은 Mobalytics 페이지 상태 등에서 가져왔다는 송신 기록이다. R3에서 GGPK 추출에 성공하더라도 그것은 기술 가능성의 증거이며 게임사·서비스·제작자 권리가 확정됐다는 증거가 아니다. 상용 허용 여부는 상용 담당의 검토가 별도로 필요하다. 계약의 “상용 사용 불가 가정”은 현재 전달물의 보류 조건으로 취급하며 이 보고서가 법률 결론을 새로 내린 것은 아니다. [출처 표](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:54), [계약 상태](D:/contracts/atlas-viewer-to-pathcraft-app.md:5), [R3](D:/contracts/atlas-viewer-to-pathcraft-app.md:31).
6. **수집 경계:** poe.ninja 해시 번들 자동수집을 제품 갱신 경로로 채택하지 않는다. Mobalytics의 Cloudflare 확인을 우회하지 않는다. 이번에는 네트워크 수집·브라우저·GGPK 직접 추출을 수행하지 않았다. [명시된 금지](D:/contracts/atlas-viewer-to-pathcraft-app.md:35).
7. **재생 UX의 수신 확인:** 원본 HTML에 단계 선택·done/dim/wait 클래스·커서·재생/멈춤·행 클릭·reduced-motion CSS가 있는 것은 읽었다. 실제 눈에 보이는 흰색/링·모션·행 이동, JS 오류, 포커스 동작은 R1에서 확인해야 한다. 행 클릭 핸들러는 step 변경 후 paint를 부르므로 “그 노드로 이동”을 자동 카메라 이동까지 의미한다고 이 실사에서 확대하지 않는다. [상태 반영](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:2981), [재생/멈춤](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3030), [행 클릭](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3052), [reduced motion](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:57).

### F. 앱으로 가져갈 데이터 계약 제안

아래는 구현된 API가 아니라 **제안 계약**이다. 지도 뷰어와 개인 추천 판단을 나누면 먼저 확인된 트리+순서를 보여 주면서, 아직 확인하지 못한 게임 조건을 보류 상태로 유지할 수 있다. 전달물에 이미 분리된 tree/xy/order/stages를 수용하고, 자료 버전·사용자 현재 상태·근거를 보강한다. [전달 데이터 구조](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:19), [앱의 현재 파밍 입력/표시](D:/Pathcraft-AI/src/components/sections/FarmingStrategy.tsx:196).

| 계약 객체 | 필수 필드와 역할 | 거부/미확인 규칙 |
|---|---|---|
| AtlasTreeSnapshot | schemaVersion, treeRevision, game, sourcePatch, capturedAt, sourceRefs, contentHash; trees별 rootId; nodes의 canonicalId/treeId/nameEn/nameKo/status/stats/group/orbit; edges; geometry 또는 좌표와 그 revision | ID·group·edge 누락, 순서의 tree hash 불일치는 렌더 전 오류. 이름 번역 부재는 영문+미번역 표시. 537/255는 이번 fixture의 값이지 모든 패치의 고정 규칙이 아님 |
| AtlasPlayerState | characterSnapshotRef, targetPatch, hardcore=true/false/unknown, acquisitionMode=trade/ssf/unknown; allocatedIdsByTree, choiceSelections, pointPools별 availablePoints/observedAt/evidence, contentStates별 encountered/unlocked와 근거; currentAreaLevel 및 atlas 진행의 known/unknown | PoB가 제공하지 않는 값은 입력/별도 가져오기로 확인. 루트/전체 노드 수를 보유 포인트로 계산하지 않음. 콘텐츠를 만남·해금·포인트 보유는 서로 다른 상태 |
| AtlasGoalContext | linkedBuildPlanId, linkedNextStepId, farmingGoal(resource/currency/material), chosenContent, riskPreference, requiredEvidence | SSF 제작 재료 목표와 거래 통화 목표를 구분. 빌드 DPS 하나로 콘텐츠 안전성을 확정하지 않음 |
| AtlasAllocationPlan | planId, treeContentHash, policyVersion, sourcePatch/targetPatch; perTree orderedSteps; step마다 nodeId, treeOrdinal, stageId, riskLabel, riskEvidence, choiceOptionId, prerequisites, appliesWhen, reasonRefs | 노드·단계 중복, 끊긴 prefix, 해소되지 않은 패치 매핑을 차단. 위험/지역 조건 미확인은 검증 필요로 유지. 미확인 옵션은 자동 선택 금지 |
| AtlasEvidence | evidenceId, kind(official/source_snapshot/creator_plan/video_readout/inference), 원본 경로·URL·영상 시각, 관측일·patch, senderClaim, receiverCheck, riskReviewStatus, rightsReviewStatus | 송신 PASS와 수신 PASS를 별도 저장. 그래프 검사/위험 검증/게임 확인/권리 검토를 한 verified 플래그로 합치지 않음 |
| AtlasViewState | planId/treeRevision, selectedScope(main 또는 사용자가 선택한 contentId), selectedStageId, playbackMode(stage/allWithinScope/stopped), stageStepIndex, cursorNodeId, focusedTreeId, reducedMotion, viewport(지원 시) | 재생 진도는 실제 게임 배정 상태와 분리. 범위 전환 시 멈춤. 저장한 tree hash가 바뀌면 단계 복구 전에 재검증하며 자동 재생을 재개하지 않음 |

핵심 함수의 입출력은 다음 정도로 고정할 수 있다.

~~~typescript
// 제안 계약의 축약 예시 — 현재 구현 파일이 아님
type AtlasViewInput = {
  tree: AtlasTreeSnapshot;
  plan: AtlasAllocationPlan;
  player: AtlasPlayerState;
  view: AtlasViewState;
};

type AtlasViewOutput = {
  selectedScope: { kind: "main" | "content"; treeId: string; contentId?: string };
  selectedStageId: string;
  stageRows: Array<{
    nodeId: string;
    treeId: string;
    stageOrdinal: number;  // 해당 칩의 목록·재생 인덱스
    treeOrdinal: number;   // 본 1..336, 각 서브트리는 각각 1부터
    nameEn: string;
    nameKo: string | null;
    risk: "safe" | "caution" | "danger" | "choice" | "unknown";
    eligibility: "met" | "blocked" | "unknown";
    evidenceIds: string[];
  }>;
  nodes: Array<{
    nodeId: string;
    display: "root" | "previous-white" | "current-revealed"
           | "current-waiting" | "future-dim";
    simulatedAllocated: boolean;
    observedAllocated: boolean | null;
  }>;
  cursorNodeId: string | null;
  revealedOrdinalByTree: Record<string, number>;
  pointBudgetsByTree: Record<string, {
    pointPoolId: string;
    available: number | null;
    requiredForSelection: number;
    status: "known" | "unknown";
  }>;
  unresolvedConditions: Array<{
    nodeId: string;
    field: "patch" | "areaLevel" | "points" | "choice" | "risk" | "unlock" | "encounter";
    evidenceIds: string[];
  }>;
};
// deriveAtlasView(input) -> output: I/O 없는 결정적 변환
// reduceAtlasView(state, event) -> state:
// selectScope / selectStage / playStage / playAllWithinScope / stop / seekRow / next / previous
~~~

treeOrdinal과 stageOrdinal을 분리해야 초록 단계의 59번째 행(서브트리 시작)을 “본 트리 59번째 포인트”로 오해하지 않는다. 계산된 다음 노드는 현재 prefix 또는 확인된 실제 할당 집합의 연결 경계에 있어야 하며, 같은 등급에서는 직전 노드 인접→가까운 노드를 우선한다. 가지 이동이 필요한 경우에도 이미 연결된 경계에서 선택하고, 선택 이유/경로를 보존한다. 저장된 순서의 재생과 새 순서 최적화는 별도 기능이다. 이번 수신 검토는 전자를 위한 데이터 정합성을 확인했으며 후자의 개인화 최적성을 입증하지 않았다.

### G. 채택된 UX를 보존하는 상태 전이·수용 조건

사용자가 거절한 흑백/모양만의 분류나 5색 동시 강조로 되돌리지 않는다. 현재 단계 칩만 강조하고, 이전 단계는 흰색, 다음 단계는 흐리게 표시한다. 숫자는 드러난 노드의 순번이며 커서 링은 현재 안내 노드 하나를 가리킨다. 재생·처음부터 전부·멈춤·행 클릭 이동과 reduced motion을 유지한다. [채택한 UX 전체](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:29).

| 이벤트/상태 | 제안 동작 | 관측 가능한 합격 조건 |
|---|---|---|
| 단계 칩 선택 | 재생을 멈추고 해당 단계의 첫 행으로 이동. 이전 단계의 계획상 배정은 흰색, 해당 단계만 강조, 이후는 흐림 | 어느 단계가 켜졌는지 하나로 식별되며, 앞 단계의 연결 출발점이 보임 |
| 단계 재생 | 현재 단계의 순서를 한 노드씩 표시하고 마지막에서 멈춤 | 숫자·행 선택·커서가 같은 nodeId를 가리킴 |
| 선택 범위 처음부터 | main 또는 사용자가 선택한 콘텐츠 내부에서 초록 첫 행부터 해당 단계 순서를 재생 | 의식→균열 등 콘텐츠 간 자동 전환·의무 선후를 만들지 않음. 5색 전체를 한꺼번에 활성화하지 않으며 선택 범위를 계속 표시 |
| 멈춤 | 타이머/스케줄을 해제하고 현재 cursor와 step을 보존 | 추가 시간 경과 후 순번이 진행하지 않음 |
| 행 클릭 이동 | 선택 행의 단계/순번/커서를 동기화하고 재생을 멈춤 | 노드 ID가 정확히 맞고 화면 밖이면 확인 가능한 초점 이동을 제공. 자동 pan을 구현하면 reduced motion에서는 즉시 이동 |
| 연결·거리 | 선택한 트리 루트/기존 할당에서 연결된 경계만 순서에 추가. 같은 우선순위는 직전 인접과 가까운 노드를 먼저 검토 | 그래프 prefix 연결 확인과 시각적 이동 검토를 별개로 수행. 다른 콘텐츠는 사용자의 명시적 범위 선택으로 전환 |
| reduced motion | 튀는 효과·부드러운 카메라 애니메이션을 끄되 순번·커서·단계 선택·정지 기능은 유지 | OS 설정을 켜도 핵심 정보/조작이 사라지지 않음 |
| 저장·재열기 | 계획 revision·단계·cursor·현재/목표 구분을 저장. 재열기는 stopped 상태 | 이전 계획을 실제 게임에 배정했다고 간주하지 않고 같은 위치로 복원 |
| 비용·조건 미확인 | 그림 재생은 “레퍼런스 미리보기”로 허용하되 개인 캐릭터의 다음 할당 가능 판정은 보류 | 311/336, 지역 70/75, 미확인 포인트 출처가 UI에서 0/조건 없음으로 바뀌지 않음 |

이 표는 후속 앱의 수용 조건이다. 현재 HTML에서 전부 동작한다고 주장하는 표가 아니다. 특히 HTML의 행 클릭은 현재 코드상 재생 타이머를 멈추는 호출이 없으므로, 앱 계약에서 “행 클릭 후 그 위치를 유지”하려면 명시적인 상태 전이를 두고 R1/앱 검증에서 확인해야 한다. [현 행 클릭 핸들러](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3052), [현 stop 구현](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3030).

### H. 개인용 흐름에 연결하는 최소 범위와 다음 게이트

**사용자 보정이 우선하는 계약:** 메인 진행과 각 콘텐츠 내부 배분 순서는 별개다. 메인 초록 단계 도중 실제 만나는 콘텐츠는 사용자마다 다르다. 의식 1→2→3은 의식을 선택하고 해당 해금·포인트 조건이 충족됐을 때의 내부 순서일 뿐, 메인 진행 후 의식부터 해야 하거나 의식 다음에 균열을 해야 한다는 뜻이 아니다. `treeId → pointPoolId`, `contentId → encountered/unlocked`, `selectedScope`, `orderedStepsByTree`를 분리한다. pointPool 간 잔여 포인트를 합치지 않고, unknown을 0 또는 해금 완료로 바꾸지 않는다. treeOrdinal/stageOrdinal 구분만으로 이 오해가 해결되지는 않는다.

예시 수용 조건: 메인 초록 20번째에서 의식을 만나지 않은 사용자는 메인 진행을 계속할 수 있다. 균열을 먼저 만나 선택했다면 균열 내부 순서만 열리고 의식 선행을 요구하지 않는다. 의식을 선택해도 포인트/해금이 미확인이면 시뮬레이션 미리보기와 실제 다음 배분 가능 판정을 분리한다. 이는 이번 보고서의 계약 보완이며 게임 획득 규칙이나 UI 구현 완료를 주장하는 예시는 아니다.

생성한 빌드의 각 성장 단계에서 필요한 재료·장비·자원을 파밍·제작 목표로 연결하고, 사용자가 선택한 콘텐츠와 실제 아틀라스 상태·가용 포인트를 확인해 내부 배분 순서를 보여 준다. 현재 캐릭터/PoB는 있으면 참고하며 필수 시작점으로 강제하지 않는다. 범용 HC 순서를 캐릭터 이름 옆에 붙이는 것으로 개인화가 완성되지는 않는다. 생성 결과와 진행 플래너는 동일한 game/patch/build revision 및 조건·근거를 참조해야 한다. [현재 파밍 영역](D:/Pathcraft-AI/src/components/sections/FarmingStrategy.tsx:196).

첫 수신 게이트는 이 작업에서 직접 확인한 **R2 + 파일 집합/순서/연결 정합성**이다. 이후 필요한 증거는 (1) 구현 담당 R1 UX 확인, (2) R3 직접 추출로 얻은 동일 의미의 트리/연결/명칭 데이터와 출처 구분, (3) 상용 담당 권리 검토, (4) 패치별 포인트 획득·지역 조건의 공식 근거, (5) 서브트리 위험/58 이후 순서의 적대검증, (6) 실제 사용자 입력→다음 파밍·아틀라스·제작 단계→저장·재열기의 연속 기록이다. 순서를 끝까지 재생했다는 사실은 실제 게임에 그 포인트를 확보/할당했다는 증거가 아니다.

**수정된 최종 판단:** 개인용 아틀라스 레퍼런스와 구조 근거는 생성 빌드의 보조 진행 플래너에 재사용할 수 있다. 앱 통합·개인 조건·게임 유효성·상용 적격성은 미완료이며, 이 축을 완성해도 빌드 구성 생성기 자체가 완성되는 것은 아니다. 생성 제품의 중심과 각 보조 기능의 판정을 분리한다.
