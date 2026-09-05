# 생성된 파일 추적

| 파일 | 목적 | 삭제 가능 |
|------|------|-----------|
| src-tauri/src/oodle.rs | Oodle DLL 동적 로더 (OodleLZ_Decompress FFI) | 아니오 |
| src-tauri/src/bundle.rs | POE Bundle 파일 리더 (청크 압축 해제) | 아니오 |
| src-tauri/src/bundle_index.rs | Bundle Index 파서 (파일 매핑 + 경로 복원) | 아니오 |
| src-tauri/src/bin/test_bundle.rs | 번들 파이프라인 실제 테스트 바이너리 | 예 |
| src-tauri/src/bin/extract_data.rs | POE 게임 데이터 추출 CLI (자동탐지 + JSON 변환) | 아니오 |
| python/game_data_provider.py | 추출된 게임 데이터 로더 + 크로스레퍼런스 해결 | 아니오 |
| python/filter_generator.py | β Continue 필터 생성 CLI (standalone 필터) | 아니오 |
| python/pathcraft_palette.py | Aurora Glow 팔레트 — 색/상수/헬퍼 (498줄) | 아니오 |
| _archive/phase_f_legacy/sanavi_tier_parser.py | Sanavi 필터 파서 (2026-04-19 archive, F4 orphan) | 예 |
| python/filter_merge.py | POE 필터 오버레이 삽입/Sanavi 탐지 공유 유틸 | 아니오 |
| python/tests/test_pathcraft_palette.py | palette + sections 단위 테스트 (90 케이스) | 아니오 |
| _archive/phase_f_legacy/sanavi_tier_data.json | Sanavi tier 데이터 (2026-04-19 archive, F4 orphan) | 예 |
| data/hc_divcard_tiers.json | HC 경제 기반 디비카 티어 데이터 | 아니오 |
| _analysis/cobalt_filter_analysis.md | NeverSink Cobalt 상세 분석 문서 | 예 |
| _analysis/wreckers_ssf_analysis.md | Wreckers SSF 상세 분석 문서 | 예 |
| src/components/FilterPanel.tsx | 필터 생성 UI (엄격도 선택, 디비카/유니크 표시, 다운로드) | 아니오 |
| python/sections_continue.py | β Continue 체인 블록 빌더 (레이어 상수 + LayerStyle + make_layer_block + load_t1_bases + style_from_palette) | 아니오 |
| python/tests/test_sections_continue.py | Continue 빌더 유닛 테스트 (36 케이스, β-0+β-1 커버) | 아니오 |
| python/tests/test_filter_generator_cli.py | filter_generator.py CLI 엔드투엔드 스모크 (8 케이스) | 아니오 |
| data/t1_craft_bases.json | T1 크래프팅 가치 베이스 화이트리스트 (ilvl>=86 보더용, _meta.influence_types 포함) | 아니오 |
| data/progressive_hide.json | β 프로그레시브 엄격도 데이터 (Supply 5단계, AL 임계값, 레벨링/엔드게임 베이스) | 아니오 |
| python/build_extractor.py | POB 빌드 데이터 파싱 헬퍼 (유니크/젬/베이스/디비카/chanceable 추출) | 아니오 |
| .claude/status/continue_architecture.md | β 아키텍처 설계 문서 (레이어 순서, 빌더 API, 마이그레이션) | 아니오 |
| src/utils/syndicateEngine.ts | Syndicate 경로 추천 엔진 (current → target 액션 추천) | 아니오 |
| src/components/SyndicateTutorial.tsx | Syndicate 4 액션/분과/Rank/약어 튜토리얼 패널 | 아니오 |
| python/syndicate_vision.py | Claude Vision으로 POE Syndicate 스크린샷 → 멤버/Rank 추출 (Opus 4.6 + 캐싱) | 아니오 |
| python/tests/test_syndicate_vision.py | Vision 정규화/파싱 단위 테스트 (19 케이스, anthropic mock) | 아니오 |
| src/components/PassiveTreeView.tsx | 패시브 트리 탭 — POE 공식 iframe + fallback (현재 X-Frame 차단, 다음 세션 재설계) | 아니오 |
| _analysis/filter_coverage_audit.py | BaseItemTypes vs 필터 매칭 자동 감사 (P0/P1 누락 탐지) | 아니오 |
| src/utils/passiveTree.ts | 패시브 트리 좌표 변환 + 데이터 타입 (orbit→cartesian, 3.17 16-orbit 테이블) | 아니오 |
| src/utils/passiveTree.test.ts | 좌표 변환 유닛 테스트 (13 케이스, vitest) | 아니오 |
| .claude/status/passive_tree_plan.md | 패시브 트리 뷰어 Phase 1/2/3 플랜 (PASS 조건 + 파일 목록) | 아니오 |
| src/components/PassiveTreeCanvas.tsx | Canvas2D 패시브 트리 렌더 (Phase 1, 노드/연결/팬줌/호버) | 아니오 |
| src/vite-env.d.ts | Vite client types + ?url JSON import 선언 | 아니오 |
| src/utils/passiveTreeSprites.ts | 패시브 트리 sprite atlas 로더 (import.meta.glob + drawSprite) | 아니오 |
| src/utils/passiveTree.pathfind.test.ts | BFS 경로/인접 리스트 테스트 (7 케이스) | 아니오 |
| src/utils/passiveTreeUndo.ts | PoB식 undo/redo 스택 (100 깊이) | 아니오 |
| src/utils/passiveTreeUndo.test.ts | undo handler 단위 테스트 (6 케이스) | 아니오 |
| src/utils/passiveTree.dealloc.test.ts | dealloc cascade (고아 정리) 테스트 (5 케이스) | 아니오 |
| src/utils/passiveTreeUrl.ts | POE 공식 passive-tree URL 디코더 (base64url v6 포맷) | 아니오 |
| src/utils/passiveTreeUrl.test.ts | URL 디코더 단위 테스트 (9 케이스) | 아니오 |
| src/utils/passiveTreeConstants.ts | 상수 + classifyNode/NodeKind (Canvas 분리) | 아니오 |
| src/utils/passiveTreeRender.ts | 순수 Canvas draw 함수 (background/edges/nodes) | 아니오 |
| src/components/passive-tree/TreeControls.tsx | 드롭다운/검색/카운터/가이드 UI 분리 | 아니오 |
| src/components/passive-tree/ClassPortrait.tsx | P1 SVG 7 클래스 포트레이트 placeholder (번들, POE 독립) | 아니오 |
| python/extract_passive_tree_translations.py | 패시브 트리 stat → 한국어 사전 빌드 (poe_translations.json#mods) | 아니오 |
| data/skilltree-export/passive_tree_translations.json | 빌드 산출물, 트리 stat 한국어 템플릿 (2352/2559 매칭, 152KB) | 예 (재생성 가능) |
| src/utils/passiveTreeTranslate.ts | {N} 정규화 + 한국어 재주입 번역 유틸 | 아니오 |
| src/utils/passiveTreeTranslate.test.ts | 번역 유틸 단위 테스트 (13 케이스) | 아니오 |
| _analysis/passive_tree_translation_misses.md | 번역 미스 207건 패턴 분류 리포트 | 예 |
| _analysis/_gen_translation_misses.py | 미스 리포트 생성 일회성 스크립트 | 예 |
| .claude/status/build_aware_weapon_filter_plan.md | Build-aware 무기 필터 플랜 (Phase B+C, Step 1 완료) | 아니오 |
| data/weapon_mod_tiers.json | NeverSink 812-844 weapon_phys mod-tier 사전 | 아니오 |
| data/weapon_base_to_class.json | 무기 base_type → POE Class 매핑 (299 베이스, GGPK 자동) | 예 (재생성 가능) |
| data/gem_weapon_requirements.json | 젬 → weapon Class set (231 젬, POB 자동) | 예 (재생성 가능) |
| python/extract_weapon_bases.py | GGPK BaseItemTypes → weapon_base_to_class.json 생성 | 아니오 |
| python/extract_gem_weapon_reqs.py | POB src/Data/Skills/*.lua → gem_weapon_requirements.json 생성 | 아니오 |
| _analysis/neversink_weaponphys_rules.md | NeverSink 812-844 mod-tier 룰 분석 + 의미 주석 | 아니오 |
| _analysis/gem_weapon_restriction_audit.md | GGPK WeaponRestriction 전수 조사 (187 스킬, 부정확성 증거) | 예 (참조 자료) |
| _analysis/_gen_weapon_restriction_audit.py | 전수 감사 리포트 생성 일회성 스크립트 | 예 |
| src/contexts/ActiveGameContext.tsx | POE1/POE2 전역 상태 + localStorage (ActiveGameProvider, useActiveGame) | 아니오 |
| src-tauri/src/bin/probe_poe2.rs | POE2 GGPK feasibility probe (Oodle/Bundle/parse_paths 호환 검증) | 예 (일회성 검증) |
| src-tauri/src/bin/catalog_poe2_tables.rs | POE2 .datc64 전수 카탈로그 생성 (942 base tables) | 예 (재실행 가능) |
| src-tauri/src/bin/probe_poe2_schema.rs | POE2 schema 호환률 probe (13 테이블 row_size 검증, 11/13=85%) | 예 (검증용) |
| _analysis/poe2_tables.json | POE2 942 base 테이블 메타 (row_count/size/locale_variants) | 예 (재생성 가능) |
| python/tests/test_coach_validator_gems.py | 젬 hallucination 탐지 회귀 테스트 (9 케이스: POE2/가짜/stopword/괄호) | 아니오 |
| python/tests/test_pob_parser_retry.py | POB URL fetch 타임아웃/재시도 회귀 테스트 (4 케이스) | 아니오 |
| python/weapon_class_extractor.py | build_data → weapon Class set 유도 (착용 무기 + 젬 fallback) | 아니오 |
| python/tests/test_weapon_class_extractor.py | weapon class extractor 단위 테스트 (9 케이스) | 아니오 |
| .claude/status/mechanic_data_audit_plan.md | Phase F 메커닉 데이터 감사 플랜 (Divcard/Breach/Legion 등 F1~F7) | 아니오 |
| _analysis/mechanic_data_audit_divcard_unique.md | F1+F6 감사 리포트 (2026-04-17) | 예 (참조 자료) |
| data/divcard_mapping.json | 유니크→디비카 단일 진실원 (_meta 포함, 21 엔트리) | 아니오 |
| python/divcard_data.py | divcard_mapping.json 로더 (캐시 + 폴백) | 아니오 |
| python/tests/test_divcard_data.py | divcard 매핑 로더/회귀 테스트 (5 케이스) | 아니오 |
| data/unique_base_mapping.json | 유니크→chanceable base 단일 진실원 (_meta 포함, 22 엔트리) | 아니오 |
| python/unique_base_data.py | unique_base_mapping.json 로더 (캐시 + 폴백) | 아니오 |
| python/tests/test_unique_base_data.py | unique base 매핑 로더/회귀 테스트 (6 케이스) | 아니오 |
| scripts/refresh_unique_base_mapping.py | Wiki Cargo 기반 유니크→base 자동 생성 (642 엔트리) | 아니오 |
| scripts/validate_divcard_mapping.py | divcard_mapping.json Wiki 대조 검증 리포트 | 아니오 |
| scripts/refresh_hc_divcard_tiers.py | poe.ninja HC 경제 기반 디비카 T1/T2 override 자동 생성 | 아니오 |
| docs/league_refresh.md | 리그 교체 시 refresh 스크립트 실행 순서 + 체크리스트 | 아니오 |
| python/defense_type_extractor.py | 캐릭터 방어 축 분류 (Phase D, pob_parser 수치 기반 ratio hybrid) | 아니오 |
| python/tests/test_defense_type_extractor.py | defense_type_extractor 단위 테스트 (16 케이스) | 아니오 |
| data/defense_mod_tiers.json | NeverSink 1-REGULAR.filter 방어 mod-tier 추출 (5 slots × life/es) | 아니오 |
| scripts/extract_defense_mod_tiers.py | NeverSink → defense_mod_tiers.json 자동 재생성 | 아니오 |
| python/damage_type_extractor.py | 빌드 damage axis 분류 (Phase E, gem_setups → {attack/caster/dot/minion}) | 아니오 |
| python/tests/test_damage_type_extractor.py | damage_type_extractor 단위 테스트 (16 케이스) | 아니오 |
| python/extract_gem_damage_types.py | POB Lua skillTypes → gem_damage_types.json 자동 생성 | 아니오 |
| data/gem_damage_types.json | 741 gems × 4 axis flag (Phase E 빌드 damage 분류 소스) | 예 (재생성 가능) |
| data/accessory_mod_tiers.json | NeverSink 악세서리 mod-tier (amu/ring/belt × axis, 681 mods) | 아니오 |
| scripts/extract_accessory_mod_tiers.py | NeverSink → accessory_mod_tiers.json 자동 재생성 | 아니오 |
| python/tests/test_e2e_filter_pipeline.py | E2E 필터 파이프라인 (Juggernaut/Occultist/Guardian fixture + multi-stage + minimal) | 아니오 |
| _analysis/ggpk_extraction_completeness_audit.md | Phase F0 GGPK 추출 감사 (7/921=0.76%, Tier1/2 확장 권고) | 예 (참조 자료) |
| _analysis/ggpk_truth_reference.json | 19 테이블 rows+content_hash+schema pin+anchored_to 진실 레퍼런스 (리그 anchor) | 아니오 |
| python/scripts/ggpk_truth_builder.py | ggpk_truth_reference.json 빌더 — KEY_FIELDS 기반 sha256 계산 | 아니오 |
| python/tests/test_ggpk_truth_reference.py | 계층 1/3/5 검증 pytest (row/hash/schema/stale/구조) | 아니오 |
| _analysis/crosscheck/config.json | Layer 2 pathofexile-dat CLI 설정 (patch + tables) | 아니오 |
| _analysis/crosscheck/README.md | Layer 2 독립 추출기 + Layer 4 인게임 스크린샷 가이드 | 아니오 |
| python/scripts/ggpk_crosscheck.py | Layer 2 비교 CLI — 우리 vs pathofexile-dat 결과 diff | 아니오 |
| python/tests/test_ggpk_crosscheck.py | Layer 2 parametrized pytest (crosscheck 출력 있을 때만) | 아니오 |
| python/scripts/validate_mod_names.py | F0-fix-3 — tier JSON mod 이름 → GGPK Mods.Name 검증 (exact/substring/missing) | 아니오 |
| python/tests/test_validate_mod_names.py | F0-fix-3 pytest — defense/accessory/weapon tier 326/326 resolve 검증 | 아니오 |
| _analysis/mechanic_data_audit_f2.md | F2 감사 리포트 — Breach/Legion/Scarab/Incursion/Expedition PASS | 예 (참조) |
| _analysis/mechanic_data_audit_f3a.md | F3a 감사 리포트 — Ultimatum/Blight/Delve CONDITIONAL (farming_* orphan) | 예 (참조) |
| _analysis/mechanic_data_audit_f3b.md | F3b 감사 리포트 — Ritual/Heist/Beyond/Metamorph PASS | 예 (참조) |
| _analysis/mechanic_data_audit_f4.md | F4 감사 리포트 — Sanavi 티어 데이터 CONDITIONAL (ORPHAN) | 예 (참조) |
| _analysis/mechanic_data_audit_f5.md | F5 감사 리포트 — Syndicate PASS | 예 (참조) |
| _analysis/mechanic_data_audit_f7.md | F7 감사 리포트 — 크래프팅/Veiled/Influence mods CONDITIONAL | 예 (참조) |
| scripts/extract_id_mod_filtering.py | F7-fix-2 — NeverSink 1-REGULAR.filter → id_mod_filtering.json 재추출 CLI | 아니오 |
| src/utils/logger.ts | dev/prod 분기 로거 래퍼 (console.log 금지 룰 준수) | 아니오 |
| src/styles/global.css | 전역 다크 스타일 + CSS 변수 + 포커스 링 + 스크롤바 | 아니오 |
| .claude/status/design_phase_plan.md | 어플 전면 리디자인 Phase 0~5 플랜 + 토큰/타우리 검증 | 아니오 |
| src/hooks/useBuildAnalyzer.ts | POB 파싱 + coach 호출 + 캐시 + syndicate 추천 통합 훅 (Phase 2) | 아니오 |
| src/components/sections/BuildSummary.tsx | Phase 2 — Tier/요약/강점/약점 섹션 | 아니오 |
| src/components/sections/LevelingGuide.tsx | Phase 2 — 레벨링 가이드 (Act 1-4/5-10/초반맵/엔드게임) 체크리스트 | 아니오 |
| src/components/sections/LevelingSkills.tsx | Phase 2 — 추천 스킬 + 옵션 + 스킬 전환 | 아니오 |
| src/components/sections/AuraUtility.tsx | Phase 2 — 오라/유틸리티 진행 테이블 | 아니오 |
| src/components/sections/KeyItems.tsx | Phase 2 — 핵심 장비 SSF 획득 테이블 (gear_progression fallback) | 아니오 |
| src/components/sections/PassivePriority.tsx | Phase 2 — 패시브 트리 우선순위 리스트 | 아니오 |
| src/components/sections/DangerZones.tsx | Phase 2 — 위험 요소 리스트 | 아니오 |
| src/components/sections/FarmingStrategy.tsx | Phase 2 — 파밍 전략 (string/object union, atlas phase) | 아니오 |
| src/components/shell/TopBar.tsx | Phase 3 — 56px 상단바 (로고+빌드명+패치노트) | 아니오 |
| src/components/shell/Sidebar.tsx | Phase 3 — 240px 사이드바 (탭 네비+오버레이 토글 stub). 반응형 collapse | 아니오 |
| src/components/shell/icons.tsx | Phase 4b — 자체 SVG 아이콘 4개 (Build/Syndicate/Passive/Overlay, Lucide path 차용) | 아니오 |
| src/components/shell/Sidebar.test.ts | Phase 4c-A — isTabId type guard 테스트 11 케이스 | 아니오 |
| src/contexts/ChecklistContext.tsx | Phase 4c-B — checked/toggle/buildKey Context (localStorage 영속 내재화) | 아니오 |
| src/overlay/OverlayApp.tsx | Phase 5a — 오버레이 창 뼈대 (드래그 바 + 닫기, 반투명) | 아니오 |
| src/overlay/overlay.css | Phase 5a — 오버레이 전용 스타일 (반투명 bg, 프레임리스) | 아니오 |
| _analysis/syndicate_research_2026-04-20.md | Syndicate 8 에이전트 리서치 통합 리포트 (3.28 매트릭스 + 메타 + UX + 알고리즘 + OCR + HCSSF) | 아니오 |
| .claude/status/syndicate_phase_plan.md | Syndicate 전면 개편 Phase S1~S4 플랜 | 아니오 |
| src/utils/syndicate.integrity.test.ts | S1 — data 무결성 회귀 테스트 7건 (layouts ⊂ members, ss22 deprecated, aisling_fixed id 보존) | 아니오 |
| src/utils/syndicateEngine.test.ts | S2a — computeRecommendations/summarizeBoardDelta + S2c witness/demotion 19건 | 아니오 |
| src/components/syndicate/types.ts | S2b — Syndicate 공용 타입 + DIVISION_COLORS + actionColor | 아니오 |
| src/components/syndicate/useSyndicateBoard.ts | S2b — Syndicate 상태/핸들러 훅 (data 로드 + localStorage + vision + recs) | 아니오 |
| src/components/syndicate/PresetPicker.tsx | S2b — 프리셋 레이아웃 선택 + deprecated legacy 섹션 | 아니오 |
| src/components/syndicate/TargetPreview.tsx | S2b — 목표 분과 미리보기 | 아니오 |
| src/components/syndicate/CurrentBoard.tsx | S2b — 현재 인게임 상태 입력 + VisionControls 통합 | 아니오 |
| src/components/syndicate/VisionControls.tsx | S2b — 스크린샷 업로드/붙여넣기 + 목표/현재 전환 | 아니오 |
| src/components/syndicate/Recommendations.tsx | S2b — 다음 액션 추천 리스트 | 아니오 |
| src/components/syndicate/MemberDetail.tsx | S2b — 선택된 멤버 상세 | 아니오 |
| src/components/syndicate/icons.tsx | S2 감사 후속 — POE 미감 SVG 2개 (CrownIcon 5-peak, CheckSealIcon 육각seal). 이모지 👑/✓ 대체 | 아니오 |
| src-tauri/src/bin/scan_class_assets.rs | 패시브 트리 class portrait/어센던시/mastery asset GGPK 경로 스캐너 | 아니오 |
| .claude/status/passive_tree_assets_plan.md | 패시브 트리 asset run-time 추출 + SVG fallback Phase P1~P6 플랜 | 아니오 |
| .claude/status/poe2_integration_backlog.md | POE2 통합 backlog (feasibility 완료 / D0~D8 단계 / drift 2건 / 외부 의존) | 아니오 |
| _analysis/schema_upstream.min.json | upstream dat-schema 2026-04-08 snapshot (drift 비교용) | 예 (재다운로드 가능) |
| src/hooks/useBuildHistory.ts | 빌드 히스토리 Phase A — localStorage 영속 SavedBuild[] CRUD (최근 20개) | 아니오 |
| .claude/status/coach_quality_backlog.md | Phase H — 코치 LLM Hallucination 근본 해결 (Normalizer 파이프라인, H1~H5 단계, alias 맵 시드) | 아니오 |
| src/components/ValidationWarningsBanner.tsx | H1 — 코치 검증 경고 접이식 배너 (카테고리 그룹핑, App/Overlay 공용) | 아니오 |
| python/coach_normalizer.py | H2 — LLM 젬 이름 정규화 (alias/exact/fuzzy 3단 + 인플레이스 coach JSON 정규화) | 아니오 |
| data/gem_aliases.json | H2 — 젬 약칭/변형 → canonical 맵 (103개, 전부 valid_gems 검증 완료) | 아니오 |
| python/tests/test_coach_normalizer.py | H2 — normalizer 단위 테스트 34건 (exact/alias/fuzzy/인플레이스/trace/한국어) | 아니오 |
| python/gear_normalizer.py | H3 — 유니크/베이스/슬롯 정식화 (unique_base_mapping + BaseItemTypes + gear_aliases, 괄호 스트립, 설명문 감지) | 아니오 |
| data/gear_aliases.json | H3 — 유니크/베이스/슬롯 약칭 맵 (30 uniques + 14 bases + 슬롯 정식화) | 아니오 |
| python/tests/test_gear_normalizer.py | H3 — gear normalizer 27 테스트 (alias/exact/fuzzy/descriptive/인플레이스/trace) | 아니오 |
| python/tests/test_build_coach_prompt.py | H4 — SYSTEM_PROMPT H4 제약 스모크 6건 (정식명/추측금지/normalizer인지/canonical 슬롯) | 아니오 |
| scripts/refresh_valid_gems.py | H5 — BaseItemTypes → valid_gems 재생성 (리그 핀/SHA256/[UNUSED] 제거) | 아니오 |
| python/data_integrity.py | H5-1 — BaseItemTypes.json SHA256 drift 런타임 체크 공용 유틸 (경고 dedupe) | 아니오 |
| python/tests/test_data_integrity.py | H5-1 — drift check 5건 (match/mismatch/pin-less/dedupe/normalizer 통합) | 아니오 |
| scripts/compare_coach_trace.py | H4-1 — 코치 A/B 비교 도구 (trace/warnings/match_type breakdown 수동 수집 JSON 기반) | 아니오 |
| .claude/verify.json | Stop hook (~/.claude/hooks/verify_on_stop.py) 프로젝트 오버라이드 설정 파일 (skip_tests / test_cmd 등) | 아니오 |
| src/components/CoachBlockedBanner.tsx | H6 L4 — 풀스크린 terminal block (drop 발견 시 결과 전체 차단 + 재분석 only) | 아니오 |
| src/components/CoachBlockedBanner.test.ts | H6 L4 — isCoachBlocked 5 케이스 단위 테스트 | 아니오 |
| python/tests/test_build_coach_retry.py | H6 L3 — Gate + Auto-retry 3 시나리오 (no-drop / recover / still-drop) | 아니오 |
| data/valid_gems_poe2.json | POE2 유효 젬 화이트리스트 (1079 gems, Spear 21 WeaponReq=25) — L1/L2 anchor | 아니오 |
| data/schema/schema_poe2_override.json | POE2 drift 보정 정의 (SkillGems +32B List×2 / Mods +24B List+Row) — `SchemaStore::load_for_game(Poe2)` auto-merge (S2) | 아니오 |
| scripts/build_valid_gems_poe2.py | valid_gems_poe2 재생성 (BaseItemTypes + SkillGems + ActiveSkills 조인) | 아니오 |
| scripts/drift_reverse_poe2.py | drift 역추적 분석 도구 (datc64 끝 바이트 패턴 분석) | 예 (재사용 시만) |
| src/components/VerbalBuildInput.tsx | D6 UI — POB 없이 POE2 빌드 구두 입력 폼 (class/ascendancy/main/supports) | 아니오 |
| python/tests/test_coach_poe2_branch.py | D6 — POE2 분기 단위 테스트 12건 (normalizer/validator/cache isolation/L2 drop) | 아니오 |
| .claude/status/poe2_integration_diff.md | D6 세션 세부 기록 (§0 scope-bounded claim / §6~§8 diff / §10 빌드 방향) | 아니오 |
| .claude/status/poe2_d6_dod.md | POE2 D6 공식 DoD 체크리스트 + 해제 조건 3건 (CONDITIONAL DONE) | 아니오 |
| data/game_data_poe2/*.datc64 (19) | POE2 GGPK 추출 (ActiveSkills/BaseItemTypes/SkillGems/PassiveSkills/Ascendancy/Characters/Words 등) | 아니오 |
| data/game_data_poe2/*.json (19) | 위 datc64 의 JSON 변환 (Mods 14841 rows 포함, Tags/SpawnWeight 3 list 만 schema 오인지로 빈값) | 아니오 |
| data/base_items_poe2.json | D3 — 무기 283 (15 classes) + 방어구 562 (6 classes) + 기타 98 (Amulets/Belts/Charms/Flasks/Jewels/Quivers/Rings) | 아니오 |
| data/uniques_poe2.json | D3 — 유니크 393 visible + 10 hidden (403 total, UniqueStashLayout × Words JOIN) | 아니오 |
| scripts/build_base_items_poe2.py | D3 — base_items_poe2.json 재생성 (BaseItemTypes 분류 + DNT 필터) | 아니오 |
| scripts/build_uniques_poe2.py | D3 — uniques_poe2.json 재생성 (UniqueStashLayout × Words JOIN) | 아니오 |
| .claude/status/design-contract.md | Design enforcement contract 4필드 (2026-04-22 install) | 아니오 |
| .claude/status/design-exceptions.md | Design enforcement 예외 로그 (빈 상태) | 아니오 |
| design-tokens.css | Design tokens — `--color-bg/fg/accent` 3변수 | 아니오 |
| .stylelintrc.json | Stylelint gradient/blur 금지 룰 | 아니오 |
| .husky/pre-commit | pre-commit hook (stylelint + exception cap) | 아니오 |
| tailwind.config.js | Tailwind corePlugins 4개 false (backgroundImage/gradientColorStops/boxShadow/dropShadow) | 아니오 |
| data/item_class_map_poe2.json | D5 1단계 — POE2 40 ItemClass + POE1 24→POE2 매핑 (NeverSink POE2 0.9.1 ground truth) | 아니오 |
| scripts/verify_item_class_map_poe2.py | D5 1단계 — NeverSink POE2 필터 drift 검증 (online/--local) | 아니오 |
| python/tests/test_item_class_map_poe2.py | D5 1단계 — item_class_map_poe2.json 스키마/partition/매핑 테스트 11건 | 아니오 |
| python/tests/test_filter_poe2_class_mapping.py | D5 2단계 — POE2 필터 생성 Class 매핑 테스트 21건 (매핑 헬퍼/오버레이/레이어별 누수) | 아니오 |
| scripts/extract_id_mod_filtering_poe2.py | D7 Phase 2 — NeverSink POE2 0.9.1 [[0400]] Recombinator Mods 추출 (SOFT/STRICT 교차 검증) | 아니오 |
| data/id_mod_filtering_poe2.json | D7 Phase 2 — POE2 Recombinator Mods per-class top mod (11 classes, 소스 7 Show 블록 → 출력 11 블록, 19 mods) | 아니오 |
| python/tests/test_filter_poe2_d7.py | D7 Phase 1+2 — heist/special_uniques/flasks_quality/id_mod POE2 분기 테스트 22건 | 아니오 |
| python/tests/test_build_uniques_poe2.py | stash_type 라벨 매핑 헬퍼 단위 + uniques_poe2.json 무결성 테스트 8건 | 아니오 |
| python/tests/test_valid_gems_poe2_categories.py | POE2 valid_gems 카테고리 완전성 회귀 가드 — Awakened/Vaal sentinel + GemType=2 메타 젬 active 포함 검증 5건 | 아니오 |
| python/tests/test_build_base_items_poe2.py | AttributeRequirements 매핑 헬퍼 단위 + simplify(req_*) + base_items_poe2.json 무결성 13건 | 아니오 |
| .claude/status/passive_tree_gap_audit.md | 8-에이전트 갭 매핑 (PoB/공식/mobalytics/maxroll/community + 우리 audit). POE1+POE2 양립 원칙. Tier 0/1/2 + 단일 게임 한정 분리 | 아니오 |
| data/guide_sources/_template.poe1_external_guide_source.json | 빌드가이드 단일 템플릿 (빈 블랭크 + _field_notes). 다음 크리에이터 가이드가 복사해 채움 | 아니오 |
| data/guide_sources/poe1_cws_chieftain_emiracles_v1.json | CWS Chieftain 가이드 (poe1_external_guide_source 첫 인스턴스). phase_model + upgrade_nodes + Pohx RF PoB | 아니오 |
| python/cws_guide_loader.py | external-guide-source 검증기(CWS+zeeboub 공유) + CWS 카드 투영기 | 아니오 |
| python/tests/test_cws_guide_loader.py | 검증기 + 투영기 회귀 테스트 24건 (고아 PoB/prereq/patch-locked/콘텐츠 유실 가드) | 아니오 |
| data/builds/*.build.json (127) | POE1 3.22–3.29 실 PoB 빌드 코퍼스 (archetype/variant 커버, 커밋 953d918) | 아니오 |
| data/build_corpus_*.json / *_v1.json | 코퍼스 DB — taxonomy/support_matrix/promoted_instances/case_snapshots/manual_pob_sources/collection queues+backlog | 아니오 |
| data/poe1_creator_source_registry_v1.json / poe1_representative_build_profiles.latest.json / poe1_leveling_archetype_route_plan_v1.json | creator-first 수집 레지스트리 + 대표 프로필 + 레벨링 route 계획 | 아니오 |
| data/poe_ninja_build_variant_*_v1.json | poe.ninja variant evidence 큐/샘플링 계획 | 아니오 |
| data/build_transition_patterns_curated.json / atlas_farming_knowledge.json / poe1_gem_taxonomy.latest.json | 전환 패턴 + 아틀라스 파밍 지식 + 젬 taxonomy | 아니오 |
| python/recommend_from_corpus.py / recommend_from_pob.py / recommendation_engine.py | 코퍼스/PoB 기반 추천 엔진 (Plan A~D + selected_profile) | 아니오 |
| python/recommendation_contract_audit.py / recommendation_backend_guard.py | 추천 계약 감사 + 백엔드 가드 | 아니오 |
| python/build_corpus_pob_link_probe.py | PoB 링크 probe (패치 가드 fix — 3.26 PoB가 3.28 후보 승격 차단). 커밋 14e952e | 아니오 |
| python/gem_taxonomy.py / gem_taxonomy_adversarial_audit.py | 젬 taxonomy 빌더 + 적대 감사 | 아니오 |
| python/ggpk_index.py / scripts/build_ggpk_derived_item_mod_index.py | GGPK 파생 mod/item 인덱스 빌더 (산출물 data/ggpk_derived/는 gitignore, 재생성 가능) | 아니오 |
| python/knowledge_router.py / item_mod_semantics.py / passive_stat_semantics.py | 지식 라우팅 + item mod/passive stat 시맨틱 | 아니오 |
| python/passive_tree_url.py / passive_tree_graph.py / poe1_live_intake.py / pob_raw.py | 패시브 트리 URL/그래프 + 라이브 인테이크 + PoB raw | 아니오 |
| python/tests/ 신규 (65) | 위 모듈 회귀 테스트 (스냅샷 단언 candidate_id set pin fix 4건 포함). 커밋 14e952e | 아니오 |
| Docs/2026-07-*.md / POE1_*.md (17) | 코퍼스 스키마/variant model v2/leveling confirmation/recommendation filter/deep research 리포트 | 예 (참조 자료) |
| python/luminary_divcard_layer.py | Luminary 필터 점술 카드 전수 사다리 생성기 (GGPK+NeverSink 티어 → 12섹션) | 아니오 |
| python/apply_luminary_divcard_layer.py | 사다리를 단일 필터 마커 사이에 교체 삽입 + 세 사본 기록 (멱등) | 아니오 |
| python/tests/test_luminary_divcard_layer.py | 사다리 커버리지/비은닉/색상 일치/린트 테스트 12개 | 아니오 |
| data/filter_build_targets/poe1_luminary_bot_ssf_3_29.json | 필터 빌드 의존 강조 정본 (점술 카드 타깃/keep + 가이드 근거). 빌드 교체 = 파일 교체 | 아니오 |
| Docs/2026-08-19_LUMINARY_BOT_SSF_ATLAS_TREE_AND_BETRAYAL.md | Path of Chores 가이드 §5.1 첫 아틀라스 트리 검증 (poeplanner 4단계 실측) + 배신 보드 조작 절차 + 원문 오역 교정표 + 필터 반영 현황 | 예 |
| data/build_corpus_taxonomy.json (v2.0) | 빌드 택소노미 정본 — 주체 4 + 정체성 축 6 + 맥락 축 + v1 이관 맵 + 벡터화 정책 | 아니오 |
| data/build_taxonomy_fixtures.json | 택소노미 수용 픽스처 8빌드 (delivery 빈칸 금지 / 정체성 튜플 충돌 금지 회귀 가드) | 아니오 |
| python/build_taxonomy.py | 택소노미 로더 + v1 이관 + 픽스처 검증기 + CLI | 아니오 |
| python/tests/test_build_taxonomy.py | 어휘 무결성 / v1 이관 유실 / 벡터화 정책 / 픽스처 수용 테스트 60건 | 아니오 |
| python/scripts/derive_active_skill_types.py | GGPK ActiveSkillTypes int id 를 알려진 스킬 집합으로 역산 (--write 로 pin 갱신) | 아니오 |
| data/active_skill_types.json | 역산된 id 맵 pin + 출처 + 미해결 축(aoe/channelled/trigger) 명시 | 아니오 |
| python/tests/test_active_skill_types.py | pin↔현재 GGPK 재도출 일치 + attack/spell 배타 + 범주 순도 테스트 17건 | 아니오 |
| python/build_labeller.py | PoB → 택소노미 v2 자동 레이블러 (메인스킬 3단 캐스케이드 + delivery/range + 근거 기록) | 아니오 |
| python/tests/test_build_labeller.py | 실물 63빌드 채점 + 정확도 하한 90% + 축 규칙 단위 테스트 19건 | 아니오 |
| data/knowledge_sources.json | 지식 파이프라인 소스 레지스트리 정본 (소스 추가 = 이 파일 수정, 코드 무수정) | 아니오 |
| python/tests/test_knowledge_sources.py | 레지스트리 경로 실재 검증 + 검색정책 필수 + 알려진 갭 가시화 테스트 71건 | 아니오 |
| python/scripts/derived_data_inventory.py | data/ 파생 JSON 전수 인벤토리 — 생성기 후보/provenance/git 최신성/GGPK 지문 조사. 지문은 ggpk_truth_reference.json 에서 소비(재계산 안 함). --write 로 pin 갱신 | 아니오 |
| _analysis/derived_data_inventory.json | 위 조사 결과 pin. 파생 파일 추가·변경·stale 시 테스트가 대조해 red | 아니오 |
| python/tests/test_derived_data_inventory.py | pin↔현재 스캔 재대조 + staleness 게이트 + 지문 없는 파일 래칫 + 생성기 귀속 테스트 18건 | 아니오 |
| python/scripts/fix_guide_translation.py | 한국어 번역 가이드 docx 게임 용어 오역 교정. 영문 원본과 문단 1:1 대조로 근거 있을 때만 치환(손상=corrupt/damage 분기). run 내부만 고쳐 인라인 서식 보존 | 아니오 |
| python/tests/test_fix_guide_translation.py | 근거 없으면 미치환 / 모호어 문맥 분기 / Fractured=분열 vs Breach=균열 충돌 / run 보존 / 규칙 순서 테스트 20건 | 아니오 |
| python/scripts/derive_atlas_mechanics.py | PassiveSkills.AtlasGroup 에서 아틀라스 메커니즘 42개 도출 (--write 로 pin 갱신). 레포 최초로 ggpk_fingerprint 를 쓰는 생성기 | 아니오 |
| data/atlas_mechanics.json | 아틀라스 메커니즘 정본 42개 + provenance + ggpk_fingerprint. atlas_farming_knowledge.json(10개, boss_rush 는 가짜 이름) 대체 근거 | 아니오 |
| python/tests/test_atlas_mechanics.py | pin↔GGPK 재도출 일치 / 42개 / group 0 falsy 함정 / 이름 결정성 / boss_rush 부재 / 커버리지 격차 테스트 15건 | 아니오 |
| python/scripts/guide_retranslations.py | 가이드 docx 문단 재번역 표(501항목, 0~8장 본문 + 표 셀). 키=영문 원문이라 원본 개정 시 엉뚱한 자리에 안 붙고 미적용으로 보고됨. 한국어 용어는 레포 번역 데이터 확인분만 사용, 미확인은 영문 유지 | 아니오 |
| python/tests/test_guide_retranslations.py | 자리 오배치 방지 / 링크 run 불가침 / link_label 선언 강제(미선언·불일치·중복표기 거부) / 서식 경계 모호 시 포기 / XML 이스케이프 / 재번역↔용어치환 비침범 테스트 21건 | 아니오 |
| python/scripts/guide_terms.py | 가이드 docx 용어 치환 규칙표(192건). 엔진(fix_guide_translation)과 분리 — 규칙 추가가 엔진 파일을 건드리지 않게. 근거 정규식이 없으면 치환 금지가 이 표의 유일한 안전장치 | 아니오 |
| Docs/2026-08-27_SMOKIEZONE_HYDROSPHERE_BONESHATTER_3_29_SSF_GUIDE_DOC.html | Smokiezone Boneshatter 가이드의 Google Docs 원고(루미너리 가이드식 0~8장). Google Doc 1wS6VWfSAhukqzuT3Nvr6XixlTu5OMgklwCWLu2lxM4w 의 소스 — 수정 시 이 파일 고치고 재주입 | 아니오 |
| scripts/filter_cascade.py | 아이템 필터 Continue 캐스케이드 시뮬레이터(유효 스타일 합성 + 글자/배경 대비). 생성기 검증 게이트와 테스트가 사용 | 아니오 |
| Docs/2026-08-28_EXILEDCAT_SSF_STRENGTH_STACKER_JUGGERNAUT_3_29_GUIDE_DOC.html | Exiled Cat SSF Strength Stacker Juggernaut(3.29 Part 1) 가이드 Google Docs 원고(0~9장). 영상 자동자막 + pobb.in PoB 4개 근거, 행마다 근거 표기. Google Doc 1kOH5Q5v9iy1ECuUwru9hEJ-JnXxi8mlcTsS7WwHqV2c 의 소스 — 수정 시 이 파일 고치고 재주입 | 아니오 |
| data/filter_build_targets/poe1_exiledcat_ssf_strength_stacker_juggernaut_3_29.json | Exiled Cat SSF Strength Stacker 필터의 정본 스펙(라벨·타깃·근거). 빌더 `--spec` 입력 | 아니오 |
| python/tests/test_build_exiledcat_ssf_filter.py | Exiled Cat 스펙 해석·조합·검증·캐스케이드 가독성 + 라벨 상태 복원 테스트 | 아니오 |
| Docs/2026-08-28_EXILEDCAT_SSF_STRENGTH_STACKER_FILTER.md | Exiled Cat 필터 설명(규칙 표·검증 게이트·미해결) | 아니오 |
| Docs/2026-09-01_TANGJEONG_POE2_CURSEMASTER_SHIELDWALL_ANALYSIS.md | 탱정(탱커의정석) POE2 0.5 커스마스터 크로노맨서 + 방패벽 키타바 정밀분석 (자막 4편 + ninja PoB 14개 실파싱 근거) | 아니오 |
| Docs/2026-09-01_TANGJEONG_CURSEMASTER_CHRONOMANCER_0_5_5_GUIDE_DOC.html | 커스마스터 크로노맨서 0.5.5 가이드 원고(0~8장, 검증 17건 반영) — Google Doc 1eayunVXW2a9… 재주입용 정본 | 아니오 |
| C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/Cursemaster Final - Tangjeong [0.5].build | 커마 최종(닌자 25f87) 인게임 빌드 플래너 파일 (passives 134 + skills 15) | 예(게임 폴더, 재생성 가능) |
| C:/Users/User/Documents/My Games/Path of Exile 2/BuildPlanner/ACT 1~4 - [0.5.5] ED Contagion*.build (4파일) | 커마용 1~65 ED 레벨링 플래너 (deadrabbit/mobalytics 캡처, ACT3부터 절망·신성모독·어둠의 제웅) | 예(게임 폴더, 재획득 가능) |
| data/filter_build_targets/poe2_cursemaster_tangjeong_0_5_5.json | POE2 커마 오버레이 필터 정본 스펙 (스타일 3계층 + 룰 7, NeverSink 어휘 게이트 대상) | 아니오 |
| scripts/build_poe2_cursemaster_overlay.py | NeverSink POE2 위 Show-only 커마 강조 오버레이 생성기 (어휘/대비 게이트) | 아니오 |
| python/tests/test_build_poe2_cursemaster_overlay.py | 오버레이 스펙·생성 가드 (대비/코어 타깃/어휘 드랍/Show-only/빈 줄) | 아니오 |
| C:/Users/User/Documents/My Games/Path of Exile 2/PathcraftAI_Cursemaster_on_NeverSink-REGULAR.filter | 설치된 커마 필터 (생성물 — 재생성 가능) | 예 |
| data/filter_build_targets/poe2_infinite_ignite_arserina_0_5_5.json | 아르세리나 젬링 무한 점화 POE2 오버레이 필터 정본 스펙 (스타일 4계층 + 룰 14, NeverSink SOFT/REGULAR/STRICT 3단계 출력; filters/PathcraftAI_Ignite_*.filter 는 재생성 산출물) | 아니오 |
| scripts/check_guide_contract.py | 가이드 HTML 구조 계약 + 템플릿 준수 검사 (장 띠·이미지 마커·3열 표·필수 장·부록 번호·평문 타임스탬프). 장이 조용히 사라져 아웃라인에서 빠지는 사고 방지 | 아니오 |
| scripts/guide_evidence_check.py | 가이드 기계 검증 — 딥링크 산술·영상 길이 초과·중첩 앵커·기준 대비 사라진 본문. 6종 1.2초. `--adopt` 로 세션별 캐시를 data/_cache/ 로 통합 | 아니오 |
| scripts/poe2_filter_eval.py | POE2 필터 독립 평가기 (first-match-wins + Continue). 빌더를 import 하지 않아 라우드니스 검증의 오라클이 된다 | 아니오 |
| scripts/poe2_filter_sweep.py | 오버레이 vs 베이스 회귀 스윕 (REAL/폴백/무음 3분류). `--spec` 로 3단계 일괄, 15초 | 아니오 |
| scripts/build_poe2_build_overlay.py | 빌드별 Show-only 오버레이 생성기(일반화). 어휘·대비·값·라우드니스·단계 게이트 | 아니오 |
| scripts/fetch_neversink_poe2_bases.py | NeverSink POE2 베이스 필터를 `_meta.bases` 핀(URL+SHA-256)대로 복원·검증. 해시 불일치 시 exit 1 | 아니오 |
| data/filter_build_targets/poe2_fartfinder_skadoosh_0_5_5.json | Fartfinder 오버레이 필터 정본 스펙 (룰 15 · 3단계 출력 · 보라 팔레트) | 아니오 |
| python/tests/test_build_poe2_build_overlay.py | 오버레이 빌더 게이트 테스트 25건 (대비 반례·어휘 토큰·단계 분기·라우드니스 불변식·재현성) | 아니오 |
| .claude/status/poe2_guides.md | POE2 가이드/필터 파이프라인 도메인 파일 — 산출물 위치, 발행 닥 ID, 검사 도구, 밟은 지뢰 목록 | 아니오 |
| ~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md | 가이드 기준 템플릿 스펙(장 구성 고정·근거 계약·가독성 규칙). 문서마다 손으로 만들어 드리프트하던 것을 계약으로 고정 | 아니오 |
| D:/discord-admin/templates/build-cards-poe2/*.md | POE2 빌드 카드 5종 정본(하우스 템플릿 준수). POE1 퍼블리셔 sourceDirectory 와 분리 | 아니오 |
| scripts/build_poe2_planner_files.py | PoB XML -> 인게임 빌드 플래너 `.build` 생성기. 패시브 stringId / 젬 경로(GGPK 표) / 어센던시(할당 노드 역산) / weapon_set(`<WeaponSet1,2>`) / 장비(`<ItemSet>` -> inventory_slots) 5개 매핑. `--verify-against` 로 Mobalytics 정본과 대조 | 아니오 |
| python/tests/test_build_poe2_planner_files.py | 플래너 생성기 테스트 24건. 돌연변이 8종(전역 weapon_set·GGPK 무시·빈 support_skills·마크업 누출·임플리싯 혼입·노드 무단폐기·슬롯 무단폐기·물음표 제목) 전부 red 확인 | 아니오 |
| build_planner/Ignite *.build (5) | 아르세리나 젬링 무한 점화 인게임 빌드 플래너 파일 5단계. 게임 폴더에도 설치됨(`--install`). 재생성 가능하나 PoB 캐시 필요 | 예(재생성 가능) |
| Docs/2026-09-04_TANGJEONG_SHIELDWALL_KITAVA_HARDCORE_GUIDE_DOC.html | 탱정 방패벽 키타바 하드코어 보조 문서. 본 가이드에 운용법을 맡기고 HC 에서 달라지는 것만 다룬다. 판정 근거는 poe.ninja HC 래더 실측(458명/174명 표본). 구글 닥 `1wFlU2G0PWUb…` | 아니오 |
| Docs/2026-09-04_ARSERINA_GEMLING_INFINITE_IGNITE_HARDCORE_GUIDE_DOC.html | 젬링 무한 점화 하드코어 보조 문서. 래더 실측 결과가 기대와 반대(HC 1.57% < SC 1.92%)라 그 사실을 제0장에 먼저 적었다. 구글 닥 `1yvyIuL5EwEj…` | 아니오 |
| python/tests/test_check_guide_contract.py | 가이드 구조 계약 체커 게이트 테스트 13건. 평문 타임스탬프 오탐 경계(05:00 KST 면제)와 보조 문서 필수 장 분기를 고정. 돌연변이 2종으로 red 확인 | 아니오 |
| build_planner/Fartfinder *.build (8) | Skadoosh Fartfinder 인게임 플래너 8파일(레벨링 5 + Starter/Endgame/Uber 3). 제작자 정본 zip 과 패시브 수 전부 일치 확인. 디스코드 카드 001 에 zip 으로 첨부돼 있으나 원본이 gitignore 폴더에만 있어 이관 | 예(재생성 가능, PoB 캐시 필요) |
| build_planner/Kitava Endgame 2.0 - Tangjeong.build | 탱정 방패벽 키타바 2.0 인게임 플래너. PoB 28010 이 트리 세트를 하나(97레벨)만 갖고 있어 엔드게임 단일 파일이다. 베일 신체 부위 4칸(Combat/Guarding Arm · Sturdy/Sprinters Leg)은 플래너 슬롯 이름을 확인할 정본이 없어 뺐다 | 예(재생성 가능) |
| .claude/status/poe2_hardcore_sources.md | POE2 하드코어 1차 소스 명부(한/영/스/독/불/포/러/일 + 트위치). 하코 문서를 래더 집계가 아니라 크리에이터 원본으로 쓰기 위한 근거 목록. 확보한 자막 캐시 대응표 포함 | 아니오 |
| scripts/read_subs.py | `data/_cache/subs/*.json3` 자막 -> 타임스탬프 붙은 평문. 가이드 인용 스탬프(`영상 12:34`)의 원천이라 `tStartMs` 보존이 유일한 책임. 검색어 주면 앞뒤 2줄 문맥까지. Windows 는 `PYTHONIOENCODING=utf-8` 필수 | 아니오 |
| python/tests/test_read_subs.py | 자막 리더 테스트 11건. 스탬프 포맷(mm:ss/h:mm:ss 경계) · seg 분할 결합 · 문맥 윈도우 · 한국어 UTF-8 로드 · 없는 파일/무일치 종료코드 · broken pipe(Windows EINVAL) | 아니오 |
| scripts/ggpk_explore.py | GGPK 탐색기 — `ls` / `cat` / `verify`. 핵심은 verify: FILE 레코드의 저장 SHA256 이 전부 0 이면 그 파일은 **패치 미완료**다. POE2 추출 실패 원인을 두 번 오진(리더 결함 -> 포맷 변경)한 뒤 이걸로 끝냈다. 142GB 라 트리 전체 재귀 금지 — 경로를 한 단계씩 탄다 | 아니오 |
| python/tests/test_ggpk_explore.py | GGPK 탐색기 테스트 9건. 합성 GGPK(정상 파일 + 해시 0 파일)로 루트 역산·이름 UTF-16·해시 대조·미완료 판정·--deep 손상 검출·hexdump·덤프·없는 경로를 고정 | 아니오 |
| scripts/build_all_filters.py | 스펙의 `_meta.outputs` 를 읽어 `filters/` 를 전부 재생성. `--check` 상태만 · `--install` 게임 폴더 설치(기존본 .bak 백업) · 스펙에서 안 나오는 고아 파일도 보고. 베이스 경로를 손으로 넘기다 세 번 틀린 뒤 만들었다 | 아니오 |
| scripts/send_to_discord.py | 빌드 산출물(필터 `_meta.outputs` · 플래너 접두사 · 임의 파일)을 디스코드 채널로 전송. **레포가 공개라** 토큰·채널 ID 를 커밋하지 않고 환경변수/gitignore 된 `.env` 에서만 읽으며, 모든 예외·로그 출구를 `redact()` 로 덮는다. 첨부 10개/8MB 한계를 보내기 전에 쪼갠다 | 아니오 |
| python/tests/test_send_to_discord.py | 디스코드 전송 테스트 24건. 조용히 틀리는 3지점 고정 — 목록을 `_meta.outputs` 에서 유도(빌드와 갈리지 않게) · 토큰이 네트워크/HTTP 오류 본문으로 새지 않게 · 한계 초과를 보내기 전에 배치 분할 | 아니오 |
| .claude/status/poe2_ggpk.md | POE2 GGPK 추출 운용 메모. 추출 커맨드(자동 탐지 실패 → 경로 직접 지정) · 0.5 vs 0.5.5 데이터 격차(신규 영혼핵 17종 부재) · **추출 실패 시 진단 순서**(저장 SHA256 이 0 이면 패치 미완료, 리버싱 대상 아님) | 아니오 |
| build_planner/~Lvl * - [0.5.5] Oil Nade Flameblast Ge*.build (6) | ds lily 인게임 플래너 정본(Mobalytics 다운로드본). 하코 보조1 — 생존 축. **파일명·내부 name 을 바꾸지 않았다**: 정본 형식은 제작자 다운로드본뿐이고, 이름만 갈면 예전에 밟은 stale-name 함정을 재현한다 | 예(재다운 가능) |
| build_planner/ACT * - [0.5.5 Hardcore] 젬링 리그*.build (4) | 임성빈 인게임 플래너 정본. **하코 기준(base)** — 액트별 4탭. 엔드게임 무기가 차임벨 지팡이라 우리 SC 필터 S급 룰과 일치 | 예(재다운 가능) |
| build_planner/*Fubgun Flameblast Oil*.build (7) | fubgun 인게임 플래너 정본. 하코 보조2 — 7단계로 가장 촘촘. 지팡이가 Pyrophyte Staff 로 셋 중 유일 | 예(재다운 가능) |
| data/filter_build_targets/poe2_hc_gemling_seongbin_0_5_5.json | 하코 젬링 필터 정본 스펙(13룰·67베이스·3단계). 임성빈 기준 / ds lily·fubgun 보조. 베이스는 세 제작자 플래너 `inventory_slots` 에서 유도하고 GGPK 로 67/67 실재성 확인. 생성기: scratchpad/make_hc_spec.py | 아니오 |
| build_planner/HC Endgame +Stun Defence - Seongbin.build | 임성빈 엔드게임 트리 + ds lily 기절/상태이상 임계값 축 4노드(Unbreaking·Feel no Pain·Stun Threshold·General's Bindings). **+8포인트**, BFS 로 경로를 복원해 연결성 검증(159/159 한 덩어리). 장비·젬·어센던시는 임성빈 정본 그대로 | 예(재생성 가능) |
| .claude/status/poe2_hc_gemling.md | 하코 젬링 소스 배치(임성빈 기준/ds lily 52~93/fubgun 대조용) · 구간별 방어 비율 실측 · 4인 트리 겹침 · 병합본 재현법(BFS 비용 산출 + 연결성 검증) · `.build` passives 를 딕셔너리째 비교하면 안 되는 함정 | 아니오 |
| .claude/status/poe2_filter_design.md | POE2 필터 디자인 정본. 소음 기준선 실측(NeverSink 장비 블록 22~23%) · 레퍼런스 2축 문법(모양=종류/빔=가치) · Crimson 팔레트 7스타일 · **T0 자리 비우기 규칙** · 숨김 게이트 · GGG 공식 값 목록 출처 · 밟은 지뢰 4건 | 아니오 |
| data/filter_build_targets/poe2_hc_gemling_seongbin_0_5_5.json | 하코 젬링 필터 정본 스펙(19룰·73베이스·숨김 1). 생성기 scripts/make_hc_gemling_spec.py | 아니오 |
| scripts/make_hc_gemling_spec.py | 위 스펙 생성기. 베이스를 세 제작자 플래너 `inventory_slots` 에서 유도하고 GGPK 로 실재성 전수 확인 — 손으로 옮기면 오타 하나가 조용한 no-op 이 된다 | 아니오 |
| data/filter_sources/poe2filter_hc_mercenary_campaign.filter | poe2filter.com 레퍼런스 실물(하코·머시너리·캠페인 프리셋). 소음 기준선과 2축 문법의 근거. gitignore 라 커밋 안 됨 — 재취득은 브라우저로 사이트 열고 Copy to Clipboard 후킹 | 예(재취득 가능) |
