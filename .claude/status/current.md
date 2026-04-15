## 지금
- 패시브 트리 Canvas 뷰어 Phase 1 + 1b + PoB 호환 기능 대부분 구현 (미커밋)
- 테스트 31/31 passing
- Tauri 빌드 통과

## 패시브 트리 완료 기능
- ✅ Phase 1 (정적 트리) — orbit→cartesian, 2737 노드, BFS 경로
- ✅ Phase 1b (스프라이트) — 아이콘/프레임/그룹배경, Active/Inactive 분기
- ✅ Undo/Redo (Ctrl+Z/Y, 100 스냅샷)
- ✅ 포인트 카운터 (좌하단)
- ✅ Dealloc cascade (할당 해제 시 고아 노드 자동 제거)
- ✅ 검색 하이라이트 (Ctrl+F, 이름/stat 매칭)
- ✅ 사용법 가이드 패널 (우하단)

## 다음 우선순위
- [ ] **클래스 고정** — 7개 클래스 선택 UI, 시작 노드 자동 할당 + 변경 불가 (현재 아무 노드나 첫 할당 가능 = POE와 불일치)
- [ ] Phase 2: PoB 빌드 `progression_stages[].passive_tree_url` 디코드 → 자동 allocated
- [ ] Phase 3: 한국어 stat 툴팁 (merged_translations.json)

## Class Start 노드 매핑 (data.json)
- 0: Scion (id 58833, "Seven")
- 1: Marauder (id 47175)
- 2: Ranger (id 50459)
- 3: Witch (id 54447)
- 4: Duelist (id 50986)
- 5: Templar (id 61525)
- 6: Shadow (id 44683, "SIX")

## UX 결정 기록
- 우클릭 dealloc 분리 → **되돌림**. 왼클릭 토글 유지 (할당된 노드 클릭 = cascade dealloc)
- line sprite vs stroke arc 질감 차이 — 허용 (사용자 "어쩔 수 없음")
- 수동 URL import UI — **스킵**. 빌드 로드로 자동 처리할 것 (Phase 2)
- 검색 하이라이트 — 구현 완료

## 잔존 이슈
- 일부 엣지 굵기 불일치 (arc stroke vs 직선 sprite)
- 705 line PassiveTreeCanvas.tsx 분리 미수행 (audit 권고)

## 블로커
- 없음

## 참조
- [패시브 트리 플랜](passive_tree_plan.md)
- [Continue 아키텍처 (β)](continue_architecture.md)
- [아키텍처](architecture.md)
- [필터 분석](filter_analysis.md)
