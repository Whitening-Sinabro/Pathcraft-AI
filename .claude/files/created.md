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
| src/components/CoachBlockedBanner.tsx | H6 L4 — 풀스크린 terminal block (drop 발견 시 결과 전체 차단 + 재분석 only) | 아니오 |
| src/components/CoachBlockedBanner.test.ts | H6 L4 — isCoachBlocked 5 케이스 단위 테스트 | 아니오 |
| python/tests/test_build_coach_retry.py | H6 L3 — Gate + Auto-retry 3 시나리오 (no-drop / recover / still-drop) | 아니오 |
| .claude/hooks/verify_on_stop.py | Stop hook — .py/.ts/.tsx 변경 시 응답 종료 전 자동 pytest/tsc/vitest (PATHCRAFT_SKIP_STOP_VERIFY 로 bypass) | 아니오 |
| .claude/settings.json | 프로젝트 공용 settings — Stop hook 등록 (team-wide) | 아니오 |
