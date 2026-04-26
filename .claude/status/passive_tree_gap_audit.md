# 패시브 트리 시각/UX 갭 매핑 (2026-04-26 S12)

> 8 에이전트 병렬 분석 결과. POE1·POE2 양쪽 동시 대응 원칙. 단일 게임 한정 항목은 명시.
>
> 분석 대상: PoB-PoE1/PoE2 (Lua) · POE 공식 web · mobalytics POE1/POE2 · maxroll POE2 · poe.ninja · poe2planner.org · poeplanner.com · poe2db.tw · 우리 PathcraftAI 코드 audit.

---

## 0. 시장 핵심 인사이트

| 발견 | 함의 |
|---|---|
| 6개 community POE2 viewer 모두 GGG 원본 sprite + 직선 edge | 시각 품질로 차별화 가능 (zero competition) |
| 한국어/비영어권 viewer 전무 | 한국어 stat 번역 91.9% 가 차별점 |
| heatmap × planner 결합 부재 (poe.ninja=통계, planner=설계 X) | "내 트리 vs 메타 평균" 시장 빈자리 |
| mobalytics — Notable Priority/Resync/트리 변형 슬롯 (저작 도구화) | 빌드 가이드 작성자 워크플로우 |
| maxroll POE2 — Weapon Set 색상 (Set I/II/Global) | POE2 dual-spec 1급 |
| PoB-POE1 — Mastery 3-state sprite + effect picker | POE1 표준, viewer 들이 자주 누락 |

---

## 1. Tier 0 — 시급 (현재 시각/기능 결손)

| 갭 | POE1 영향 | POE2 영향 | 작업 위치 | 규모 |
|---|---|---|---|---|
| **거미줄 / 호 fallback 모호** — cutoff 1500 으로 정당 long-arc 일부 잘림 | 낮음 (1.7%) | **높음 (28%)** | `passiveTreeRender.ts:drawEdges` | 중 |
| **Class portrait** — POE2 8/8 부재 (POE1 7개 하드코딩) | OK | **0/8** | `PassiveTreeCanvas.tsx:438-474` `portraitRefs[7]` | 중 |
| **Ascendancy index→name 매핑 손실** | 손실 | 손실 | `passiveTreeUrl.ts:79-86` 디코드만 함 | 소 |
| **Mastery effect 선택 UI 부재** | **POE1 한정** (POE2 mastery 0개) | N/A | `passiveTreeUrl.ts` 디코드만, 적용 X | 중-대 |
| **Edge cutoff 게임별 미분리** | 1500 OK | 1500 부족 | `passiveTreeRender.ts:edgeMaxDist` | 소 (이미 일부 해결) |

---

## 2. Tier 1 — 표준 시각 요소 (POE 공식 / PoB 표준)

| 갭 | POE1 | POE2 | 작업 규모 |
|---|---|---|---|
| **Connector 3-state sprite** (Normal/Intermediate/Active + connectionArt 동적) | ✅ 적용 | ✅ 적용 | 대 |
| **Edge arc sprite** (atlas quad, 알고리듬 그리기 X) | ✅ 적용 | ✅ 적용 | 대 |
| **Frame 다단 상태** — allocated/unallocated + path-highlight + intermediate | ✅ 적용 | ✅ 적용 | 중 |
| **Group ring background sprite** (small/med/large + Alt + atlas 변형) | ✅ 적용 | ✅ 적용 (tree_0_4.json `groups[].background` 존재) | 중 |
| **Ascendancy 원형 배경 + cluster 외곽** | ✅ 7 | ✅ 21 (8 class) | 중 |
| **Mastery 4-state sprite + effect 페인팅** | ✅ 필수 | N/A (POE2 mastery 0) | 대 |
| **Cluster jewel sub-graph 렌더** | ✅ 필수 | N/A (POE2 cluster 없음) | 대 |
| **Timeless jewel radius sprite** (6종 × 2변종) | ✅ 필수 | N/A | 중-대 |
| **JewelSocket 색상 4종** (Red/Green/Blue/Prismatic/Abyss) | ✅ 적용 | tree_0_4.json `jewelSlots` | 소 |
| **Search pulsing glow** (zoom-out 가시) | ✅ 적용 | ✅ 적용 | 소 |
| **Highlight similar skills** / **shortest-path preview** | ✅ 적용 | ✅ 적용 | 중 |
| **Connector compare-mode 색** (added=green / removed=red) | ✅ 적용 | ✅ 적용 | 소 |
| **Replace/Conquered 노드 아이콘 교체** (Conqueror, Timeless) | ✅ 필수 | N/A | 중 |

---

## 3. Tier 2 — 차별화 기회 (시장 빈자리)

| 기회 | POE1 적용 | POE2 적용 | 영감 |
|---|---|---|---|
| **한국어 stat 번역 + UX** | ✅ 91.9% 보유 | ⏳ 신규 작업 (POE2 stat 번역 X) | 비영어권 공백 |
| **메타 채택률 heatmap × planner** | ✅ poe.ninja API | ✅ poe.ninja API (POE2 데이터 시작) | poe.ninja → planner 결합 |
| **트리 변형 슬롯** (main / set 1 / set 2) | ✅ 적용 | ✅ 적용 | mobalytics + PoB |
| **Notable Priority + Resync** (빌드 가이드 저작) | ✅ 적용 | ✅ 적용 | mobalytics |
| **Progression Steps** (레벨 구간별 트리) | ✅ 적용 | ✅ 적용 | maxroll |
| **Standalone shareable URL** (단독 트리 공유) | ✅ 적용 | ✅ 적용 | mobalytics 약점 |
| **Weapon Set 색상 분리** | N/A (POE1 weapon set 없음) | ✅ Set I 빨강 / II 초록 / Global | maxroll POE2 |

---

## 4. PathcraftAI 잘된 부분 (보존)

| 영역 | 위치 |
|---|---|
| Class Portrait DOM Overlay Sync (rAF, pointer-events:none, scale transform) | `PassiveTreeCanvas.tsx:438-474` |
| 한국어 stat 번역 (91.9% 커버, 숫자 정규화/재주입) | `passiveTreeTranslate.ts` |
| Dealloc cascade BFS (PoB PassiveSpec.lua 호환) | `passiveTree.ts:deallocWithCascade` |
| Undo/Redo 스택 (100단계, Ctrl+Z/Y/Shift+Z) | `passiveTreeUndo.ts` |
| PoE2 어댑터 — null group skip + outConn 메타 보존 + PoB 3분기 이식 | `passiveTree.ts:normalizePoe2Tree` + `passiveTreeRender.ts:drawEdges` |
| Game-aware 분기 (POE1/POE2 dataUrl, classStartIds, ascendancies, localStorage 분리) | `PassiveTreeCanvas.tsx` `gameTables` useMemo |

---

## 5. 권장 작업 순서 (양쪽 동시 적용 원칙)

**A. Tier 0 마무리** (양쪽 영향 / 단일 작업)
1. POE2 거미줄 시각 검증 + 호 fallback 정리 (POE2 한정 작업, 낮은 cost 잔여)
2. Class portrait 7→8 통일 + POE1/POE2 공통 코드 (양쪽 적용, 중)
3. Ascendancy index→name 매핑 (양쪽 적용, 소)
4. Mastery effect picker UI (POE1 한정, 중-대 — POE2 mastery 0개라 양쪽 의미 없음)

**B. Tier 1 — 표준 시각 인프라** (양쪽 동시)
1. Connector 3-state sprite + Edge arc sprite atlas (POB 표준, 양쪽)
2. Frame 다단 상태 (allocated/path/intermediate) (양쪽)
3. Group ring background sprite (양쪽 — POE2 데이터에도 background 존재)
4. Ascendancy 원형 배경 + cluster 외곽 (양쪽)

**C. Tier 2 — 차별화** (양쪽 동시 + 일부 게임 한정)
1. 한국어 stat 번역 POE2 확장 (POE2 한정 신규)
2. 트리 변형 슬롯 (양쪽)
3. 메타 heatmap × planner (양쪽 — poe.ninja API 의존)
4. Weapon Set 색상 (POE2 한정)

---

## 6. 단일 게임 한정 작업 — POE1/POE2 양립 원칙 예외

| 항목 | 게임 | 사유 |
|---|---|---|
| Mastery effect picker | POE1 | POE2 mastery 0개 (tree_0_4.json 실측) |
| Cluster jewel sub-graph | POE1 | POE2 cluster jewel 시스템 없음 |
| Timeless jewel radius | POE1 | POE2 timeless 시스템 없음 |
| Replace/Conquered 노드 | POE1 | POE2 Conqueror/Timeless 없음 |
| Weapon Set 색상 | POE2 | POE1 dual-spec 없음 |
| Edge cutoff 50000 (호 fallback) | POE2 | POE1 1500 충분 |

---

## 7. 도메인 파일 포인터

- 본 파일: `.claude/status/passive_tree_gap_audit.md`
- D4 계획: `.claude/status/passive_tree_poe2_plan.md`
- 패시브 asset 플랜: `.claude/status/passive_tree_assets_plan.md`
- 외부 raw 분석 결과: 8 에이전트 outputs (`/tmp/.../tasks/*.output`)
