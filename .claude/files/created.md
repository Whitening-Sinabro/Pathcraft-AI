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
| python/sanavi_tier_parser.py | Sanavi 필터에서 카테고리×티어 BaseType 리스트 추출 | 아니오 |
| python/filter_merge.py | POE 필터 오버레이 삽입/Sanavi 탐지 공유 유틸 | 아니오 |
| python/tests/test_pathcraft_palette.py | palette + sections 단위 테스트 (90 케이스) | 아니오 |
| data/sanavi_tier_data.json | Sanavi 실제 tier 데이터 (32 카테고리) 캐시 | 아니오 |
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
| python/weapon_class_extractor.py | build_data → weapon Class set 유도 (착용 무기 + 젬 fallback) | 아니오 |
| python/tests/test_weapon_class_extractor.py | weapon class extractor 단위 테스트 (9 케이스) | 아니오 |
| .claude/status/mechanic_data_audit_plan.md | Phase F 메커닉 데이터 감사 플랜 (Divcard/Breach/Legion 등 F1~F7) | 아니오 |
