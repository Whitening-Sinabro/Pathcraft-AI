## 지금
- **다음 세션 주제: 어플 디자인** (UI/UX). 백엔드/데이터/필터 파이프라인은 전부 종료됨
- **Phase F 감사 전체 완결** (2026-04-19) — 8 감사 + 15 fix + legacy cleanup + truth reference 5계층. 535 pytest PASS

## 다음 (우선순위순)
1. [ ] **어플 디자인** (다음 세션 집중) — 범위 확정 필요:
   - Tauri UI 전반 개선? (`src/App.tsx`, `src/components/`)
   - 특정 화면/컴포넌트 리디자인?
   - 디자인 시스템/토큰 정비?
   - 사용자 의도 확인 필요
2. [ ] **인게임 검증** (사용자 영역, 플레이 피드백 대기)
   - Phase B+C Step 6b: 무기 필터 Tyrannical vs Heavy, DropLevel 5 리튜닝
   - Phase D 방어 필터 스모크
   - Phase E 악세서리 필터 스모크
   - 패시브 트리 Phase 3 한국어 stat 툴팁 호버 지연

## 완료된 기능 (참조용, git log 대체 요약)
- **β Continue 필터 L0~L10**: weapon_phys_proxy(B+C) / defense_proxy(D) / accessory_proxy(E) L7 통합. layer_build_target 완전 연결
- **패시브 트리 Phase 1~3**: Canvas 뷰어 / PoB URL 자동 디코드 / 한국어 stat 툴팁 (91.9%)
- **F1+F6**: 디비카/유니크 단일 진실원 + HCSSF Mirage 파이프라인 (7 pytest)
- **F0**: GGPK 추출 19 테이블 + Truth reference 5계층 (content hash / schema pin / 독립 추출기 / 스크린샷 가이드 / stale warning)
- **F2/F3a/F3b/F4/F5/F7 감사 + fix 완료**: legacy 6 파일 archive, 전 하드코딩 출처 주석

## 도메인 파일 포인터 (다음 세션에서 필요 시 참조)
- **어플 디자인 진입점**: `src/App.tsx` (~700 lines, 메인 레이아웃), `src/components/` (FilterPanel, PassiveTreeCanvas, SyndicateTutorial, PobInputSection)
- [Continue 아키텍처](continue_architecture.md) — 필터 레이어 설계
- [패시브 트리 플랜](passive_tree_plan.md) — UI 컴포넌트 결정 기록
- [메커닉 데이터 감사 (Phase F)](mechanic_data_audit_plan.md) — 전 Phase 감사 종료 상태
- _analysis/ggpk_truth_reference.json — 19 테이블 진실 anchor (3.28 Mirage)
- _analysis/crosscheck/README.md — 리그 전환 시 GGPK 재검증 가이드
- _analysis/mechanic_data_audit_{f2,f3a,f3b,f4,f5,f7,divcard_unique}.md — Phase F 감사 리포트 7건
- docs/league_refresh.md — 리그 교체 시 refresh 실행 순서 (9 섹션)

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
