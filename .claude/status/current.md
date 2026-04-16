## 지금
- **Build-aware 무기 필터 Phase B+C, Step 1 완료** (2026-04-16)
  - 플랜: [build_aware_weapon_filter_plan.md](build_aware_weapon_filter_plan.md)
  - 산출: `data/weapon_mod_tiers.json`(NeverSink 룰) + `weapon_base_to_class.json`(299) + `gem_weapon_requirements.json`(231 젬)
  - **핵심 결정: GGPK ActiveSkills.WeaponRestriction 신뢰 불가** (Sunder Axe 누락 등) → POB `src/Data/Skills/*.lua` ground truth 전환. [메모리 참조](../../../../../Users/User/.claude/projects/D--Pathcraft-AI/memory/project_weapon_filter_ground_truth.md)
  - 재감사: Phase A ⚠️ CONDITIONAL (BLOCK 해제). 🟡 잔여 4건 (C3 단위 테스트, I4-b nameSpec 실측 Step 2, I4-d L7 physpure 스펙 Step 4, I4-e 세션 연속성 → 이 파일 + memory 갱신으로 처리)
- (완료) Phase 3 한국어 stat 툴팁 — 자동검증 PASS, 인게임 호버 지연 측정 대기 (별건)

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

## 다음
- [x] Step 2: `python/weapon_class_extractor.py` — 9 테스트 통과 (커밋 221269d)
- [x] Step 3: build_extractor 통합 — StageData.weapon_classes 필드, 419 테스트 통과
- [ ] Step 4: sections_continue L7 weapon_phys_proxy — physpure 블록 strictness 0~1 분기 스펙 박제 (I4-d)
- [ ] Step 5/6: 빌드/타입 + 자동 스모크 + 인게임 검증
- [ ] **Phase F: 메커닉 데이터 감사** (사용자 제기 2026-04-16)
  - 플랜: [mechanic_data_audit_plan.md](mechanic_data_audit_plan.md)
  - 메모리: `memory/project_mechanic_data_audit_required.md`
  - F1(Divcard) 🔴 HIGH / F2~F7 🟡~🟢
  - Phase B+C Step 4 완료 후 착수
- [ ] (별건) 패시브 트리 Phase 3 인게임 호버 지연 검증

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
