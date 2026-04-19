## 지금
- **F2-fix + 주석 보강 8건 완료** (2026-04-19) — 모든 하드코딩 리스트 출처 주석 + syndicate_layouts/t1_craft_bases _meta 완비. F2-fix-2는 기존 test_p1_base_routed 커버 확인. 535 pytest PASS. 커밋 대기.

## 다음 (우선순위순)
1. [ ] **F1-fix-2 HCSSF 파이프라인** (별도 세션, 4~6h, 제품 기능)
2. [ ] **인게임 검증** (사용자 영역, Claude 대기)
   - Phase B+C Step 6b: 무기 필터 Tyrannical vs Heavy, DropLevel 5 리튜닝
   - Phase D 방어 필터 스모크
   - Phase E 악세서리 필터 스모크
   - 패시브 트리 Phase 3 한국어 stat 툴팁 호버 지연

## 완료된 기능 (참조용, git log 대체 요약)
- **β Continue 필터 L0~L10**: weapon_phys_proxy(B+C), defense_proxy(D), accessory_proxy(E) 모두 L7 통합. L7 7-way 순서 박제됨
- **패시브 트리 Phase 1~3**: Canvas 뷰어 / PoB URL 자동 디코드 / 한국어 stat 툴팁 (91.9%)
- **F1+F6**: 디비카/유니크 단일 진실원 + HCSSF Mirage 파이프라인

## 도메인 파일 포인터
- [메커닉 데이터 감사 플랜 (Phase F)](mechanic_data_audit_plan.md)
- [Build-aware 무기 필터 플랜 (Phase B+C)](build_aware_weapon_filter_plan.md)
- [패시브 트리 플랜](passive_tree_plan.md)
- [Continue 아키텍처 (β)](continue_architecture.md)
- [필터 분석](filter_analysis.md)
- _analysis/ggpk_extraction_completeness_audit.md — F0 감사 (0.76% 커버리지)
- _analysis/ggpk_truth_reference.json — 19 테이블 진실 anchor (3.28 Mirage, content hash + schema pin)
- _analysis/crosscheck/README.md — Layer 2 독립 추출기 + Layer 4 스크린샷 가이드
- _analysis/mechanic_data_audit_divcard_unique.md — F1+F6 리포트
- _analysis/mechanic_data_audit_f2.md — F2 리포트 (Breach/Legion/Scarab/Incursion/Expedition)
- _analysis/mechanic_data_audit_f3a.md — F3a 리포트 (Ultimatum/Blight/Delve)
- _analysis/mechanic_data_audit_f3b.md — F3b 리포트 (Ritual/Heist/Beyond/Metamorph)
- _analysis/mechanic_data_audit_f4.md — F4 리포트 (Sanavi 티어, ORPHAN)
- _analysis/mechanic_data_audit_f5.md — F5 리포트 (Syndicate)
- _analysis/mechanic_data_audit_f7.md — F7 리포트 (크래프팅/Veiled/Influence mods)
- _analysis/neversink_weaponphys_rules.md — NeverSink 812-844 무기 mod-tier
- _analysis/gem_weapon_restriction_audit.md — GGPK 부정확성 증거 (187 스킬)

## Class Start 노드 매핑 (data.json, 수동 — Characters.json 추출 후 자동화 예정)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## 잔존 이슈 (허용됨)
- PassiveTreeCanvas.tsx 591 line (300 룰 초과, 기능 복잡도로 허용)
- 일부 엣지 굵기 불일치 (arc stroke vs 직선 sprite)

## 블로커
- 없음

## UX 결정 기록 (패시브 트리)
- 우클릭 dealloc 분리 시도 → 되돌림 (왼클릭 토글 유지)
- 수동 URL import UI 스킵 (Phase 2 자동 디코드로 대체)
- 드롭다운 형식 (공간 절약)
- AI 이모지 제거
