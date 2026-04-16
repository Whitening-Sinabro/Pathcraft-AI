## 지금
- Phase 3: 한국어 stat 툴팁 연동 — 자동검증 PASS, 인게임 호버 지연 측정 대기
- DoD 상태 (`passive_tree_plan.md:79-82` 기준):
  - 80%+ 한국어 매칭 → 91.9% (2352/2559) ✅
  - 호버 50ms 이내 툴팁 → **미측정 ⚠️** (dev 서버에서 Profiler 확인 필요)
  - 미매칭 영문 fallback → ✅ (translateStat null 경로)
- 데이터 소스: 플랜 1순위 `merged_translations.json`(`#` placeholder, 재배치 불가)
  → 2순위 `poe_translations.json#mods`(`{0}` placeholder, 재배치 가능) 로 폴백. 플랜 허용 범위
- 번역 미스 207건(8.1%) 분석: 82 멀티라인 + 123 기타 + 2 트리거. 보류 권고 (인게임 pain 후 재판단)
  - 리포트: [_analysis/passive_tree_translation_misses.md](../../_analysis/passive_tree_translation_misses.md)
- 재생성: `npm run translations` (또는 `npm run build`의 prebuild 훅 자동)
- 테스트 53/53 passing (기존 40 + 신규 13)

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
- [ ] 인게임 검증: 호버 지연 50ms 체크 (React Profiler) + 한국어 표시 샘플링
- [ ] (선택) 노드 이름(name) 한국어 번역 — 현재 영문 고정
- [ ] (선택) UX 개선: Intuitive Leap 미구현, 기타 피드백 반영

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
- [패시브 트리 플랜](passive_tree_plan.md)
- [Continue 아키텍처 (β)](continue_architecture.md)
- [아키텍처](architecture.md)
- [필터 분석](filter_analysis.md)
