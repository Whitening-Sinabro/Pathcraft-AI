# 새 빌드·성장 경로 생성 준비도 — 좁은 정적 평가

작성일: 2026-09-21. 평가 제품: **D:/Pathcraft-AI 전체를 원본으로 유지**. 이 문서의 소유 출력만 현재 기술 worktree에 작성했다. Task `task_06590f8efd27`, Dispatch `ctx_0deaebf4f7e3`.

**판정:** 수집자료를 구조화하고 기존 빌드를 추천·진단하며 단계별 코칭을 만드는 자산과 실제 앱 경로는 있다. 그러나 사용자 조건을 받아 스킬·지원젬·패시브·장비·자원·진행 조건이 함께 성립하는 새 구성을 만들고, 수정 후 재검증·저장하는 제품 경로의 완결은 확인되지 않았다. 이는 신규 메타 발명 능력 평가가 아니다. 검증된 기존 빌드/자료를 조합·변형해 사용자 조건에 맞는 완성 구성을 만드는 것도 목표에 포함한다. 링크 선택이나 설명문 생성만으로 그 목표를 충족했다고 판정하지 않는다.

**사례 실증 보완:** 임성빈 화염파 젬링과 스카두쉬 토템·함성 워브링어에서 수집→교차확인→정정→성장/전환 조건→개인용 가이드·플래너 반영은 이미 수행됐다. 이를 단순 자료나 변환만으로 축소하지 않는다. 위 미완결 판정은 이 성과의 전체 범위 일반화·사용자 조건별 앱 자동화에 관한 것이며 사례 검증 자체의 부재를 뜻하지 않는다. [사례별 성과·원본 대응·미확인·확장 과제](case_validation_evidence.md).

사람·에이전트가 자료 대조·정정·조건/순서 결정과 가이드/.build 제작을 수행한 과정도 실제 생성·검증 실증으로 인정한다. 앱 함수 하나로 자동 연결되지 않았다고 이 성과를 미구현으로 되돌리지 않으며, 독립 완전자동 계산엔진을 생성 인정의 필수 조건으로 추가하지 않는다.

## 평가 범위와 증거 읽는 법

책임자 취합 보완: 아래 연결표는 작업자의 상세 근거와 책임자의 주요 원본 대조를 요약한다. 후속 실행 검증은 수행하지 않았다.

| 연결 단계 | 실제 연결 | 끊긴 부분·완료로 확대할 수 없는 점 |
|---|---|---|
| 수집자료→구조화 지식 | [knowledge_sources.json](D:/Pathcraft-AI/data/knowledge_sources.json:1)의 층·경로·상태, 출처/patch가 있는 개별 팩, [지식 팩 검증](D:/Pathcraft-AI/python/sanavixx_cyclone_knowledge.py:57) | 전체 자료 정규화율·최신 패치 적합성은 미집계/미검증. source_refs 정합성이 게임 기계적 정확성 증명은 아님 |
| 지식→코칭 문맥 | [router](D:/Pathcraft-AI/python/knowledge_router.py:687)에서 선택·검색, [coach](D:/Pathcraft-AI/python/build_coach.py:1332)의 POE1 호출 | POE2 동일 router 연결 없음. 검색 hit와 vector 후보 표지는 제약 해결·생성 근거 강제 계약이 아님 |
| 조건→구성 | [기존 후보 추천](D:/Pathcraft-AI/python/recommend_from_corpus.py:204), [구두 입력→coach](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378), [기존 PoB→planner](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:484) | 사용자 실제 예산·보유품 대신 기본값인 경로가 있고, 조건부 조합/변형의 정본 완성 구성 계약은 미완료 |
| 구성→검증 | [젬/gear 정규화](D:/Pathcraft-AI/python/build_coach.py:1851), [경고 반환](D:/Pathcraft-AI/python/build_coach.py:1966), [입력 스탯 해석](D:/Pathcraft-AI/python/build_instance.py:445) | 생성·수정된 전체 조합의 성능 재계산·자원/포인트/확보/전환 통합검증과 같지 않음 |
| 결과→앱 사용·수정·저장 | [단계 UI](D:/Pathcraft-AI/src/App.tsx:1426), [history](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:22) | PoB 없는 이력 저장 공백, 독립 build/revision·구성 수정 후 의존 검증 갱신·내보내기 통합 미완료 |

- **사실**: 아래 파일의 정적 코드·데이터·문서에서 직접 확인한 내용. 실행 성공을 뜻하지 않는다.
- **추론**: 관찰한 호출경로와 계약에서 도출한 제품 영향. 다른 미조사 모듈 전체의 부재를 단정하지 않는다.
- **미확인**: 실행·통합 또는 최신성 근거가 없어 확정하지 않은 내용. **제안**은 아직 구현되지 않은 다음 범위다.
- 적용 AGENTS와 `orchestration`의 Orca live guide를 읽고 실제 Dispatch CLI를 사용했다. 하위위임 없이 필요한 파일만 읽었다. 원본 제품코드·기존 책임자 보고서·모델 설정은 변경하지 않았다.
- 테스트/빌드/브라우저/API/네트워크/GGPK 접근·추출·대량집계·상용화 재조사를 하지 않았다. 일반 파일 내용과 표적 경로 검색만 사용했다. `build_analyzer.py` 등 경로 부재는 검색 관찰로 명시하고 실행 오류라고 꾸미지 않는다.
- 기존 [technical.md:13](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-audit-20260921/deliverables/readiness_audit_2026-09-21/technical.md:13)의 **304 passed / 0 failed / 1 skipped**는 선택된 기존 테스트 범위다. [동 보고서:204](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-audit-20260921/deliverables/readiness_audit_2026-09-21/technical.md:204)의 Atlas 추가 결과도 생성품질·완성 구성·HC 안전성 합격으로 확대하지 않는다. 이 문서는 해당 보고서를 수정하지 않는다.

## 0. 현재 목표와 과거 요구사항의 구분

**사실:** 원 PRD [Docs/PathcraftAI_PRD_v1_0.md:16](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:16)는 설명·추천·분석을 핵심 목표로 두고, [같은 파일:6](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:6)은 POE1/2, [같은 파일:10](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:10)은 초보~중급·HC 사용자를 명시한다. [PRD.md:14](D:/Pathcraft-AI/PRD.md:14)는 검색 및 분석 도구라고 정의한다. 반면 [Docs/PRD.md:85](D:/Pathcraft-AI/Docs/PRD.md:85)는 자연어 빌드 추천, 플레이스타일·예산 설명과 레벨링 1–70·예산별 업그레이드·단계별 필수 아이템을 요구한다. [.claude/status/architecture.md:2](D:/Pathcraft-AI/.claude/status/architecture.md:2)는 레벨 1~엔드게임 로드맵과 HCSSF를 적지만, [같은 파일:21](D:/Pathcraft-AI/.claude/status/architecture.md:21)은 “생성이 아닌 코치”라고 적는다.

**해석 기준:** 과거 자료는 방향이 일치하지 않는다. 현재 직접 사용자 교정인 “수집자료를 이용한 실행 가능한 새 빌드와 성장 경로 생성, PoB는 선택적 입출력/검증 보조”를 평가 기준으로 삼는다. 과거 PRD가 처음부터 완성 구성 생성기를 요구했다고 소급 해석하지 않는다.

| 입력 축 | 기존 자료 및 실제 코드의 사실 | 현재 목표를 위한 구분 |
|---|---|---|
| 게임 | 원 PRD는 POE1/2. 실제 앱은 [App.tsx:933](D:/Pathcraft-AI/src/App.tsx:933)에서 POE2 구두 폼 / POE1 PoB 입력 분기 | 두 게임 범위 근거는 있으나 동일한 생성 입력 계약은 아님 |
| 클래스·전직·주력스킬 | [VerbalBuildInput.tsx:4](D:/Pathcraft-AI/src/components/VerbalBuildInput.tsx:4)에 클래스·전직·레벨·주력·지원·보조스킬·노트가 있음. [같은 파일:77](D:/Pathcraft-AI/src/components/VerbalBuildInput.tsx:77)은 클래스와 주력스킬을 제출 조건으로 사용 | 현 POE2 코칭 폼의 입력 사실. 모든 생성에서 필수여야 한다는 확정 PRD 근거와는 다름 |
| 플레이스타일 | Docs/PRD의 추천 출력에 존재. [recommend_from_corpus.py:169](D:/Pathcraft-AI/python/recommend_from_corpus.py:169)는 기존 젬으로 입력 스타일을 추론 | 독립 사용자 선호 입력·최대 버튼수 등은 제안 범위. 추론된 스타일을 명시 선택으로 취급하지 말 것 |
| 예산 | 원 PRD의 예산별 아이템 추천 및 Docs/PRD의 단계 예산 근거가 있음. [recommend_from_corpus.py:164](D:/Pathcraft-AI/python/recommend_from_corpus.py:164)의 liquid_divines 기본값은 3.0 | 현재 coach 경로가 실제 사용자 예산을 받는다고 볼 수 없음. 정확한 통화/예산 입력 계약은 미확정 |
| 보유자산 | 원 PRD [Docs/PathcraftAI_PRD_v1_0.md:192](D:/Pathcraft-AI/Docs/PathcraftAI_PRD_v1_0.md:192) 이후 스태시 분석은 별도 기능. 현재 추천 어댑터 [recommend_from_corpus.py:180](D:/Pathcraft-AI/python/recommend_from_corpus.py:180)는 owned_uniques=[]·chaos=0 및 제작 가능 여부 기본값 사용 | 실제 보유자산을 새 구성 제약으로 소비하는 UI 연결은 미확인. 자동 스태시 연동을 생성 MVP 필수로 단정하지 않음 |
| SSF·HC | architecture의 HCSSF 방향, [useBuildAnalyzer.ts:34](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:34)의 sc/ssf/hcssf 선택, [같은 파일:276](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:276)의 mode 전달 | 순수 HC 거래 모드는 이 선택형에 없음. POE2 verbal payload [같은 파일:378](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:378)는 해당 mode context를 넣지 않음. 모든 경로에서 조건 반영 완료로 보지 않음 |

## 1. 수집자료: 보관·검색과 구조화 생성지식

**사실 — 단순 문서 더미 이상인 자산:** [knowledge_sources.json:1](D:/Pathcraft-AI/data/knowledge_sources.json:1)에 schema_version, evidence_layer, retrieval_mode, vectorization, 경로·상태가 있고, GGPK 젬/아이템/패시브, 패치 delta, 파생 taxonomy를 서로 다른 층으로 등록한다. 이 레지스트리의 status=ok는 메타데이터 선언이며, 이번에 모든 원본 파일·현재 패치 동등성을 검증한 것은 아니다.

[knowledge_router.py:687](D:/Pathcraft-AI/python/knowledge_router.py:687)는 의도·엔티티로 소스를 고르고 item mod·Brand·CWS·Luminary·Cyclone 문맥과 제한된 패치 항목을 만든다. [같은 파일:770](D:/Pathcraft-AI/python/knowledge_router.py:770)의 출력은 selected_sources/exact_sources/vector_candidates, 문맥 및 evidence_rule이다. **vector_candidates 등록 자체는 전체 소스 벡터 검색이 수행됐다는 증거가 아니다.** [cws_knowledge.py:2](D:/Pathcraft-AI/python/cws_knowledge.py:2)는 구조화 JSON 정본 + 폐기 가능한 SQLite FTS5 색인 + 선택 embedder의 검색 설계를 명시한다. 검색 회수와 구성 제약 해결은 다른 기능이다.

**사실 — 출처와 버전 관리의 구체 사례:** [poe1_brand_guide_zeeboub_v2.json:1](D:/Pathcraft-AI/data/guide_sources/poe1_brand_guide_zeeboub_v2.json:1)은 수동 Markdown import 날짜·원본 경로·SHA256·저자·출처 링크·patch_mentions(3.25~3.27)를 담는다. [sanavixx_cyclone_knowledge.py:57](D:/Pathcraft-AI/python/sanavixx_cyclone_knowledge.py:57)는 3.29 patch lock, semantic knowledge_version, source/claim ID 유일성 및 dangling source_refs/claim_refs를 검증한다. 이는 특정 팩의 근거 무결성 구현이다. 모든 수집자료가 같은 계약으로 정규화됐다는 증거는 아니다.

**사실 — 성장 지식과 불확실성 구분:** [poe1_leveling_archetype_route_plan_v1.json:1](D:/Pathcraft-AI/data/poe1_leveling_archetype_route_plan_v1.json:1)은 최신 단계 PoB 우선순위, inferred/near_confirmed/confirmed, 최종 스냅샷만으로 레벨링 확정 금지 정책을 둔다. [같은 파일:34](D:/Pathcraft-AI/data/poe1_leveling_archetype_route_plan_v1.json:34) 이후는 자료 자체가 3.27/3.28 및 더 오래된 fallback을 설명한다. 데이터 안의 coverage_summary 수치는 기존 선언이며 이번 재집계가 아니다.

**실제 생성/코칭 연결:** [build_coach.py:1321](D:/Pathcraft-AI/python/build_coach.py:1321)에서 GameData를, [같은 파일:1332](D:/Pathcraft-AI/python/build_coach.py:1332)에서는 **POE1에 한해** knowledge context pack을 만든다. [game_data_provider.py:303](D:/Pathcraft-AI/python/game_data_provider.py:303)의 matched gems/items·BuildInstance 요약은 코치 프롬프트로 들어간다. [build_coach.py:1502](D:/Pathcraft-AI/python/build_coach.py:1502)는 router 결과를 주입한다. 이 연결은 출처 기반 설명을 돕지만, 결과의 모든 선택에 출처 ID·패치·의존조건을 강제하는 완성 구성 스키마와 같지 않다.

**추론:** 정확 조회 데이터와 조건·출처가 붙은 가이드 팩은 제한된 생성기의 좋은 재료다. 현재 확인한 주 경로는 이들을 주로 프롬프트 문맥/추천 근거로 소비한다. 패치가 섞인 단계 자료를 그대로 “현재 패치에서 실행 가능”으로 승격할 근거는 없다. **미확인:** 모든 수집자료의 포괄적 정규화 비율, 라이브 인덱스 최신 상태, 사용자 조건별 실제 recall/구성 정확도.

## 2. 생성 모듈·실제 호출경로와 산출물의 차이

| 경로 | 직접 확인된 동작 | 생성 목표와의 관계 |
|---|---|---|
| 이름상 guide generator | [build_guide_generator.py:13](D:/Pathcraft-AI/python/build_guide_generator.py:13)는 keyword/provider/tier를 받아 Markdown 반환. [같은 파일:53](D:/Pathcraft-AI/python/build_guide_generator.py:53)에서 build_analyzer의 Reddit·아이템·패치 로더로 프롬프트 구성, [같은 파일:180](D:/Pathcraft-AI/python/build_guide_generator.py:180)부터 Markdown 파일 저장 | 설명문 생성 경로. 스킬·패시브·아이템 전체의 제약 해결·검증 호출을 이 함수에서 확인하지 못함 |
| 현 React → Rust → Python | [useBuildAnalyzer.ts:241](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:241)의 parse_pob → [같은 파일:276](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:276) 추가 빌드+mode → [같은 파일:309](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:309) invoke coach_build → [lib.rs:185](D:/Pathcraft-AI/src-tauri/src/lib.rs:185), [같은 파일:205](D:/Pathcraft-AI/src-tauri/src/lib.rs:205)의 build_coach.py subprocess | 실제 코칭 호출경로 존재. 생성기 파일명만으로 앱 호출을 가정하지 않음 |
| PoB 없는 앱 경로 | [useBuildAnalyzer.ts:349](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:349)에서 POE2 폼을 최소 BuildData로 바꾸어 [같은 파일:402](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:402) coach_build 호출 | PoB 비필수 경로는 실제 존재. 빈 상태에서 완성 패시브·장비·자원을 함께 합성/확정하는 계약은 아님 |
| 템플릿·기존 후보 추천 | [build_coach.py:498](D:/Pathcraft-AI/python/build_coach.py:498)는 젬 문자열로 archetype 선택 후 guide_templates 읽기. [recommend_from_corpus.py:204](D:/Pathcraft-AI/python/recommend_from_corpus.py:204)는 기존 profiles를 guard/filter하고 recommend_profiles 결과에 metadata 부착 | 기존 후보 선택을 완성된 맞춤 구성 생성과 구분. [build_coach.py:1027](D:/Pathcraft-AI/python/build_coach.py:1027)는 추천을 설명 grounding으로 사용한다고 명시 |
| POE2 planner 출력 | [build_poe2_planner_files.py:484](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:484)의 필수 --pob → specs/skillsets/itemsets 파싱 → [같은 파일:372](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:372)의 inventory/passives/skills 포함 .build 구성 | 완성 구성 파일 형식은 있으나 이 경로는 기존 PoB 변환. [같은 파일:513](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:513)은 stage 인덱스로 세트를 대응시키고 부족하면 마지막 세트 사용. 사용자 제약을 풀어 새 stage를 합성하는 알고리즘은 아님 |

**부정 증거의 범위:** `src`, `src-tauri/src`, `python`에 `build_guide_generator|generate_build_guide_with_llm`을 표적 검색했을 때 generator 자체 외 호출을 찾지 못했다. `rg --files D:/Pathcraft-AI -g build_analyzer.py`도 결과가 없었다. 따라서 generator의 import dependency가 이 원본 파일 집합에 보이지 않는다는 **정적 의존성 공백**이며, 외부 PYTHONPATH 가능성까지 배제하거나 실행 실패를 재현한 것은 아니다. [build_guide_generator.py:203](D:/Pathcraft-AI/python/build_guide_generator.py:203), [같은 파일:259](D:/Pathcraft-AI/python/build_guide_generator.py:259)의 패키지/API 실패 시 mock fallback도 산출물 존재를 실생성 성공으로 오인할 수 있는 구조다.

**판정:** 현재 확인한 기능은 “추천+근거 기반 LLM 코칭+기존 구성 변환”이다. 조건부 조합/변형으로 완성 구성을 만드는 기능도 목표에 부합하지만, 그 기능이 이 호출경로에서 보장된다고 판단할 증거는 부족하다.

## 3. 실제 검증과 완성 구성 검증의 간격

| 검증 축 | 구현 사실 | 한계·미확인 |
|---|---|---|
| 이름·출력 형식 | [build_coach.py:1851](D:/Pathcraft-AI/python/build_coach.py:1851)에서 젬 canonical 정규화, POE1 gear 정규화. [같은 파일:1873](D:/Pathcraft-AI/python/build_coach.py:1873)에서 dropped 젬 1회 교정 재호출. [coach_validator.py:148](D:/Pathcraft-AI/python/coach_validator.py:148)는 POE1 필수필드·rating·tier·젬 이름 검사 | 존재하는 젬끼리도 supportability·무기·trigger·링크·중복 제한 등이 맞는지는 별도. 이름 교정/삭제 후 다른 구성 요소가 여전히 작동하는지 재계산하는 흐름은 확인 못함. POE2 gear normalizer는 명시 skip |
| 잘못된 출력 차단 | [build_coach.py:1966](D:/Pathcraft-AI/python/build_coach.py:1966)에서 경고 메타를 결과에 담음. [App.tsx:1397](D:/Pathcraft-AI/src/App.tsx:1397)는 dropped trace 차단 배너와 일반 warning 배너를 분리 | 모든 검증 실패를 성공 구성에서 배제하는 단일 완성 판정이 아님. validator는 warnings 반환이며 젬 이름 검사 [coach_validator.py:246](D:/Pathcraft-AI/python/coach_validator.py:246)는 비ASCII 설명 토큰을 건너뜀 |
| 스탯·자원 | [build_instance.py:445](D:/Pathcraft-AI/python/build_instance.py:445)는 입력 stats의 DPS/HP/ES/eHP/저항을 읽고 elemental_res_capped 등을 도출. suppression/recovery 등은 None | 입력 스냅샷 해석이지 생성/수정된 스킬·장비 전체를 재계산하는 엔진이 아님. 능력치 요구량, 마나/점유/정신력, 지속 비용과 회복 균형의 stage별 결합 검증은 이 경로에서 확인 못함 |
| 패시브·포인트·선행조건 | [build_instance.py:355](D:/Pathcraft-AI/python/build_instance.py:355)의 tree state와 [build_poe2_planner_files.py:374](D:/Pathcraft-AI/scripts/build_poe2_planner_files.py:374)의 unknown node/ascendancy 차단, [import_poe2_planner_files.py:84](D:/Pathcraft-AI/scripts/import_poe2_planner_files.py:84)의 ID 존재 검사 | ID 존재는 루트 연결·stage 레벨별 포인트 예산·퀘스트 획득·전직 순서·무기세트 조건의 동시 충족이 아님. 변환 결과에 대한 이 전체 검증은 해당 함수에 없음 |
| 공격·생존·콘텐츠 적합 | [build_readiness.py:93](D:/Pathcraft-AI/python/build_readiness.py:93)의 방어 screening, [같은 파일:210](D:/Pathcraft-AI/python/build_readiness.py:210)의 DPS/eHP/저항 기반 map phase screening | mapping 상태는 코드상 unknown_runtime_inputs이고 flask uptime·사망·clear time 등을 요구. [build_instance.py:524](D:/Pathcraft-AI/python/build_instance.py:524)도 inputs_only_not_final_verdict. 생성품질이나 HC 안전 보증으로 읽지 않음 |
| 확보·패치 | [build_coach.py:1351](D:/Pathcraft-AI/python/build_coach.py:1351)의 기존 stage 유니크 Wiki 조회, router의 패치 delta/특정 guide pack; [coach_validator.py:178](D:/Pathcraft-AI/python/coach_validator.py:178)의 POE1 클래스별 퀘스트 젬 근사 레벨 대조 | POE2 퀘스트 검증 skip. 실제 보유·총구매비·드롭 확률·제작 가능성·SSF 자력 확보의 통합 확정이 아님. [import_poe2_planner_files.py:107](D:/Pathcraft-AI/scripts/import_poe2_planner_files.py:107)는 0.4.0d 표에 없는 0.5.5 젬을 warning 후 허용하므로 PASS 의미 제한 |
| 진행순서·전환 | [build_coach.py:1367](D:/Pathcraft-AI/python/build_coach.py:1367) 추가 PoB, [같은 파일:1412](D:/Pathcraft-AI/python/build_coach.py:1412) alternate skillset, 구조화 leveling route와 LLM stage 출력이 존재 | 단계 설명과 필수 선행조건을 풀어 얻는 실행 순서는 다름. 필수 장비 미획득 시 전환 금지·대체 루트·환불 포인트·자원 부족 전파를 모든 stage에 강제하는 통합 경로 미확인 |

**중요한 긍정 근거와 한계:** 특정 지식 팩에는 출처를 보존하는 규칙 진단이 있고, [sanavixx_cyclone_knowledge.py:147](D:/Pathcraft-AI/python/sanavixx_cyclone_knowledge.py:147)는 source_refs를 포함한 진단을 반환한다. 다만 router의 해당 연결은 [knowledge_router.py:722](D:/Pathcraft-AI/python/knowledge_router.py:722)에서 검색 hits를 담는 것이므로, 독립 diagnose 구현을 모든 coach 결과에 실행되는 자동 veto라고 확대하지 않는다. [build_instance.py:572](D:/Pathcraft-AI/python/build_instance.py:572)는 mastery text/config 정규화/일부 stat·acquisition 층의 known_missing_layers도 직접 공개한다.

## 4. 생성 결과 수정·단계 사용·저장 연결

**사실:** [App.tsx:1426](D:/Pathcraft-AI/src/App.tsx:1426)부터 leveling guide/skills, aura utility, gear timeline, passive priority, 위험·파밍 조언을 렌더한다. [GearTimeline.tsx:20](D:/Pathcraft-AI/src/components/GearTimeline.tsx:20) 및 [ChecklistContext.tsx:23](D:/Pathcraft-AI/src/contexts/ChecklistContext.tsx:23)의 체크 상태는 localStorage에 영속된다. 단계별 사용을 돕는 실제 UI 자산이다. 체크를 했다고 스킬·장비·트리 구성이나 검증 상태가 함께 전이되는 코드로 보아서는 안 된다.

**사실:** PoB 경로는 [useBuildAnalyzer.ts:323](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:323)에서 raw input/coach JSON을 이력에 저장하고, [같은 파일:176](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:176)에서 재선택 복원한다. [useBuildHistory.ts:22](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:22)는 v2 localStorage 최대 20개, [같은 파일:83](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:83)는 PoB 링크 해시로 갱신한다. 문서 리비전과 검증 provenance를 가진 독립 빌드 ID 계약은 아니다.

**구체적인 PoB 없는 저장 공백:** verbal 경로는 [useBuildAnalyzer.ts:368](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:368)에서 pobLink를 비우고 [같은 파일:413](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:413)에서 saveToHistory를 부르지만, [같은 파일:158](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:158)은 빈 pobLink이면 즉시 return한다. **추론:** 깨끗한 빈 링크 상태의 구두 입력 결과는 이 이력 함수로 저장되지 않는다. 기존 링크가 있던 render closure 상황에서는 이전 링크로 저장될 위험도 코드 구조상 있어, 정확한 런타임 양상은 미확인이다. 따라서 “PoB 없는 입력→생성→저장→재열기 완료” 판정은 불가하다.

**미확인/범위 제한:** 표적 확인한 App/hook/단계 component에서는 완성 구성의 젬·장비·패시브를 직접 편집한 뒤 의존 stage를 재검증하고 리비전 저장하는 end-to-end 경로를 찾지 못했다. 입력 수정 후 코칭 재호출, 체크박스, variant 보기와 구별한다. `.build` 내보내기는 별도 스크립트에 있지만 현 Rust/프런트 검색에서 생성 결과를 그 변환기로 보내는 연결을 확인하지 못했다. 기존 외부 여정/Atlas 산출물 존재를 앱 통합 완료의 대용 증거로 사용하지 않는다.

## 5. 현재 개인용 범위, 판매에서 빠진 핵심, 가장 작은 일관된 생성 범위

### 현재 개인용으로 확인 가능한 범위

**정적 근거에 따른 범위 판단:** 알려진 기존 빌드·단계 PoB나 POE2 구두 스킬 입력을 놓고 자료 검색, 추천 후보 비교, 단계별 코칭 초안, 체크리스트, 기존 PoB의 planner 형식 변환을 활용할 수 있는 코드 기반은 있다. 숙련 사용자가 출처·패치·구성·획득을 직접 대조하는 보조 작업에는 의미가 있다. 이번에 API나 앱을 실행하지 않았으므로 현재 환경에서의 실제 성공·품질·저장 재현성을 확정하지 않는다.

**현재 미충족 판정:** 사용자 예산·보유자산·취향·모드만 주면 곧바로 따라 할 완성 빌드와 성장 경로를 자동 보장한다는 범위는 근거가 부족하다. “개인용 생성 가능”을 주장하려면 최소한 제한된 한 빌드군에서 조건 변경으로 실구성이 달라지고, 모든 단계가 검증되며, 실패 조건을 보류하고 수정·재열기가 이어지는 증거가 필요하다.

### 판매 전 핵심 제품 공백 — 상용화 시장 조사 아님

1. **입력 계약:** 실제 사용자 제약과 3 divine·빈 자산 같은 기본값을 분리하고, 누락을 묻거나 미확인 상태로 유지해야 한다. 두 게임에서 PoB 선택성·모드 전달이 일관돼야 한다.
2. **정본 구성:** 설명 JSON과 별도로 game/patch/source/revision을 포함한 완성 구성·단계·전환 조건이 필요하다. 기존 후보 추천 후 어떤 슬롯·노드·젬을 왜 바꿨는지 추적돼야 한다.
3. **통합 검증:** 이름 존재, 패시브 합법성, 자원·스탯, 획득·예산, 전환·공격·생존 조건을 같은 결과와 stage에 적용하고, 실패/미확인을 판매 가능한 성공 결과와 분리해야 한다.
4. **수정과 보존:** PoB 없는 독립 저장·재열기, 구성 수정 후 영향받은 검증 무효화/재실행, 단계 체크와 실제 캐릭터 상태 분리가 필요하다.
5. **제품 증거:** 위 한정 범위의 실제 end-to-end 결과와 잘못된 조건 거절 증거가 필요하다. 기존 304 테스트·Atlas 뷰어 결과는 이를 대신하지 않는다.

### 제안: 검증된 한 빌드군의 조건부 구성 생성부터

이것은 현재 완성됐다는 선언도, 게임 범위를 영구 축소하자는 결정도 아니다. **원본 제품 목표를 유지하면서 생성 단위만 한정하는 구현 제안**이다.

- 한 게임·명시 패치·한 클래스/주력스킬 계열·한 모드를 고른다. 단계별 스킬/장비/트리 및 출처가 있는 기존 자료를 기준으로 삼는다. 특정 팩이 최신 게임과 동일하다는 재검증 없이 여기서 합격 빌드를 지명하지 않는다.
- 초기 입력은 목표 스킬/클래스, 현재 단계, 예산 또는 SSF, 필수 보유/미보유 아이템, 버튼 부담 등 최소 선호를 받는다. 이 필드들의 정확한 필수 여부는 **제품 계약 제안**이며 과거 PRD 확정사항으로 쓰지 않는다. 보유자산은 수동 선택으로 시작할 수 있고 PoB는 선택적 import다.
- 검증된 한 계열 내부의 대체 젬·장비·패시브 조합만 허용한다. 사용자 조건에 따라 실제 구성이 달라지되 검증 범위 밖이면 보류한다. 단순 원본 링크 반환이나 이름만 바꾼 복제는 완료가 아니다. 새 메타 발명이나 전 게임 조합 탐색은 요구하지 않는다.
- 캠페인/전환/초기 목표 콘텐츠처럼 소수의 의미 있는 단계를 만들고, 각 단계에 canonical ID의 주력·지원·보조스킬, 패시브와 포인트 예산, 장비/대체품, 능력치·자원·방어 조건, 확보 방법, 다음 단계 gate를 함께 기록한다. 필수품 미획득이면 현재 단계 유지/대체 루트를 낸다.
- 기존 정확 조회·출처 팩·readiness screening을 재사용하되, 생성된 구성 자체에 규칙 검증을 추가한다. 성능은 통제된 조건의 재계산/검증 근거를 붙이고 미검증 수치를 LLM이 채우지 못하게 한다. PoB는 선택 검증/출력 보조로 사용할 수 있으며 없는 입력도 정본 구성을 가져야 한다.
- 사용자가 한 장비/젬을 바꾸면 영향을 받은 자원·스탯·진행 조건을 다시 판단한다. 독립 build ID/revision으로 저장·재열기하고, UI 체크리스트는 이 구성 stage를 참조한다. LLM은 허용된 선택의 설명과 출처 연결을 담당한다.

**이 최소 범위의 완료 증거 제안:** 동일한 기준 빌드에 예산/보유품 조건이 다른 입력 둘을 주어 서로 다른 실행 가능한 완성 구성과 전환 계획을 얻고, 불가능한 조건 하나에서는 명시 보류를 받는다. 지원 불가 젬·연결 끊긴 트리·포인트 초과·자원 부족·필수품 미확보·패치 불일치를 성공으로 저장하지 않는지 확인한다. 결과 수정→검증 갱신→저장→재열기에서 구성과 출처/판정이 보존되어야 한다. 이는 향후 승인된 구현·검증 범위이며 이번에 테스트를 추가하거나 실행하지 않았다.

## 전달 및 남은 일

전달물은 이 파일 하나다. 5개 평가축의 코드·자료 근거와 사실/추론/미확인/제안을 기재했고, 기존 보고서는 읽기 참고만 했다. 남은 것은 원본 제품에서 위 최소 생성 범위를 구현·실행 검증하는 일이며 이번 문서 작업에 포함하지 않았다. 책임자가 먼저 게임/패치/한 빌드군/모드 및 필수 입력 계약을 결정할 수 있도록 제안 범위를 남겼다. 현재 생성품질·판매 준비 완료·HC 안전 합격 선언은 하지 않는다.
