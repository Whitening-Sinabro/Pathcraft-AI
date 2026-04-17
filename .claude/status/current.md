## 지금
- **Build-aware 무기 필터 Phase B+C — Step 1~4 완료, Step 6b 인게임 검증 대기** (2026-04-16~17)
  - Step 1: 데이터 사전 3종 (POB ground truth, 231 gems)
  - Step 2: weapon_class_extractor (9 tests)
  - Step 3: build_extractor 통합 (StageData.weapon_classes)
  - Step 4: L7 weapon_phys_proxy + L10 re_show 복권 (6 tests)
  - Step 5+6a: 자동검증 PASS (tsc/vitest/pytest 425+53, E2E smoke)
  - **핵심 결정: GGPK ActiveSkills 신뢰 불가 → POB ground truth**
  - 플랜: [build_aware_weapon_filter_plan.md](build_aware_weapon_filter_plan.md)
- (완료) Phase 3 한국어 stat 툴팁 — 인게임 호버 지연 측정 대기 (별건)

## 패시브 트리 완료 기능
- ✅ Phase 1 (정적 트리) — orbit→cartesian, 2737 노드, BFS 경로
- ✅ Phase 1b (스프라이트) — 아이콘/프레임/그룹배경, Active/Inactive 분기
- ✅ Undo/Redo (Ctrl+Z/Y, 100 스냅샷)
- ✅ 포인트 카운터 (좌하단)
- ✅ Dealloc cascade (할당 해제 시 고아 노드 자동 제거)
- ✅ 검색 하이라이트 (Ctrl+F, 이름/stat 매칭)
- ✅ 사용법 가이드 패널 (우하단)
- ✅ 클래스 7개 + 어센던시 20개 드롭다운 (localStorage 영속)
- ✅ Phase 2: PoB URL 자동 디코드 → allocated 자동 표시 (`passiveTreeUrl.ts`)
- ✅ Phase 3: 한국어 stat 툴팁 (poe_translations.json#mods 사용, 91.9% 커버)
- ✅ 파일 분리: Canvas 591 line + Render 307 + Controls 155 + Constants 85

## 다음 (우선순위순)
1. [ ] **Phase F1+F6 감사** — Divcard (`hc_divcard_tiers.json _meta:{}` + `UNIQUE_TO_DIVCARD` 하드코딩) + Unique base (`UNIQUE_TO_BASE` 26개 하드코딩). 병합 6~8h
2. [ ] **Phase D: 방어 타입 필터** — 착용 장비에서 Arm/Ev/ES 유도 + defense mod-tier 프록시. 4~6h
3. [ ] **Phase E: 악세서리 필터** — Ring/Amulet/Belt suffix mod-tier 프록시. 4~6h
4. [ ] **Phase F2~F7 나머지 감사** — Breach/Legion/Scarab/Incursion/Essence/기타 12~18h
5. [ ] **E2E 필터 통합 테스트** — POB 링크 → filter file 전 과정 1건 이상. 2~3h
6. [ ] **pob_parser stats API 실측** — `pob_parser.py:190` TODO 주석 확인 + fallback. 1~2h
7. [ ] Step 6b: 인게임 스모크 (무기 필터 — Tyrannical vs Heavy, DropLevel 5 리튜닝)
8. [ ] 패시브 트리 Phase 3 인게임 호버 지연 검증
9. [ ] (이후) 아틀라스 트리 뷰어 / 빌드 패시브 추천 — 현재 인프라 준비도 60~90%

## Class Start 노드 매핑 (data.json)
- 0: Scion (id 58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## 잔존 이슈 (허용됨)
- 일부 엣지 굵기 불일치 (arc stroke vs 직선 sprite 질감 차이)
- PassiveTreeCanvas.tsx 591 line (300 룰 초과, 기능 복잡도로 허용)

## UX 결정 기록
- 우클릭 dealloc 분리 시도 → 되돌림. 왼클릭 토글 유지
- 수동 URL import UI 스킵 — Phase 2 자동 디코드로 대체
- 드롭다운 형식 (버튼 대신) — 공간 절약
- AI 이모지 제거 (패시브 트리 영역)

## 블로커
- 없음

## 참조
- [Build-aware 무기 필터 플랜 (Phase B+C)](build_aware_weapon_filter_plan.md)
- [메커닉 데이터 감사 플랜 (Phase F)](mechanic_data_audit_plan.md)
- [패시브 트리 플랜](passive_tree_plan.md)
- [Continue 아키텍처 (β)](continue_architecture.md)
- [아키텍처](architecture.md)
- [필터 분석](filter_analysis.md)
- _analysis/neversink_weaponphys_rules.md — NeverSink 812-844 mod-tier 룰 분석
- _analysis/gem_weapon_restriction_audit.md — GGPK 부정확성 전수 증거 (187 스킬)
