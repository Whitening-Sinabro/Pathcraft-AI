# Syndicate 전면 개편 — Phase S1~S4

> 2026-04-20 착수. 사용자 선택: **C (완전 개편)**. 기반 리서치: `_analysis/syndicate_research_2026-04-20.md` (8 에이전트 통합 리포트).
> 리그 앵커: 3.28 Mirage.

---

## 범위

Agent 3 스코프 크리프 경고: PathcraftAI 원래 POB/젬 중심. Syndicate는 외연 확장. 사용자 "손봐야할듯" 직접 요청으로 범위 확정.

---

## S1 — 데이터 정확성 (BLOCK급, 선결) — 2026-04-20 완료

**PASS 결과**:
- `syndicate_members.json` 17 멤버 × 4 분과 × 3 T2 소스 교차 확인 일치 ✅
- It That Fled Breach 테마 정정 ✅
- `syndicate_layouts.json` `_meta.poe_league: 3.28 Mirage` ✅
- SS22 `deprecated: true` 태그 ✅
- `meta_2x2_5` 프리셋 신설 ✅
- pnpm test 63/63 (기존 56 + integrity 7), build 경고 0 ✅

**실 변경 파일**:
- 수정: `data/syndicate_members.json` (전면 rewrite — 17 × 4 분과 + Scarab 매핑 + _meta 정정)
- 수정: `data/syndicate_layouts.json` (_meta 정정 + 9 프리셋 — 기존 5 유지 + 4 신규)
- 생성: `src/utils/syndicate.integrity.test.ts` — data 무결성 7 테스트

**범위 변경 (S1 감사 후 확정)**:
- 원래 S1 범위 = `meta_2x2_5` 1개 + ss22 deprecate
- 실제 S1 커버리지: 추가로 HCSSF 3종(`hcssf_safe_start`/`ssf_crafting_core`/`ssf_currency_sustain`) + Aisling 변형 1종(`aisling_fortification_vexalted`) 주입
- 이유: Agent 8이 프리셋 완성 설계 제시. 데이터만 삽입이라 S3 UX 작업과 분리 가능. 사용자 "C 전면 개편" 승인 범위 내.

**S1 감사 후 즉시 조치 반영**:
- `aisling_research_fixed` → `aisling_fixed` id 원복 (localStorage 호환성)
- 데이터 무결성 vitest 7 케이스 추가
- 프리셋 5→9 수치 명시

---

## S2 — 코드 구조 + 알고리즘 (2026-04-20 완료)

**PASS 결과**:
- `SyndicateBoard.tsx` 620 → **89줄** (-86%) ✅
- 서브컴포넌트 6개 생성, 훅 1개 추출 (hook 264줄, components 49~161) ✅
- `syndicateEngine.test.ts` 19 케이스 (S2a baseline 14 + S2c 5) ✅
- 액션 비용 벡터 `ACTION_COSTS` + 목격자 제약 `hasExecuteWitness` + demotion 케이스 ✅
- pnpm test 82/82, build 경고 0 ✅

**실 분리 (components/syndicate/)**:
- `types.ts` 56 — 공용 타입 + DIVISION_COLORS + actionColor
- `useSyndicateBoard.ts` 264 — 상태/핸들러 훅 (data 로드/localStorage/vision/recs)
- `PresetPicker.tsx` 101 — deprecated legacy 섹션 분리
- `TargetPreview.tsx` 49
- `CurrentBoard.tsx` 161 + `VisionControls.tsx` 116 (분리)
- `Recommendations.tsx` 58
- `MemberDetail.tsx` 56

**엔진 개선 (S2c)**:
- `ActionCost { encounterTurns, sideEffects }` 인터페이스 + `ACTION_COSTS` 상수
- 모든 Recommendation에 `cost` 필드 부착
- Execute 목격자 preconditions — witness 없으면 Interrogate(priority 45) 폴백
- **신규**: target Member + current Leader demotion 케이스 (Interrogate priority 50)

**기존 priority 값 보존** — 회귀 없음.

---

## S3 — HCSSF 프리셋 + UX 개선

**PASS 조건**:
- HCSSF 3 프리셋 (`hcssf_safe_start` / `ssf_crafting_core` / `ssf_currency_sustain`) 추가
- Before/After diff 그리드 적용
- 추천 hover ↔ 보드 펄스 연동
- Cmd+K 멤버 할당 팔레트
- UI 시각 검증

**파일**:
- 수정: `data/syndicate_layouts.json` (3 프리셋 추가)
- 수정/신설: 섹션 컴포넌트 (S2 분리 결과물)
- 신설: `sections/syndicate/AssignPalette.tsx` (Cmd+K)

---

## S4 — OCR 품질 + 추가 기능

**PASS 조건**:
- 골든 스크린샷 5~10장 + integration 테스트
- 이미지 SHA-256 캐싱 (동일 업로드 재분석 skip)
- Scarab 매핑 테이블 (17 멤버)
- Leader/Mastermind 드롭 테이블 분리
- Mastermind 진행 추적 UI (Leader 7명 카운터)

**파일**:
- 신설: `python/tests/fixtures/syndicate/*.png` (5~10장)
- 수정: `python/syndicate_vision.py` (SHA-256 캐시)
- 수정: `data/syndicate_members.json` (Scarab + Leader drops 분리 필드)
- 수정: 섹션 컴포넌트 (Mastermind 카운터)

---

## 차후 / 선택 (각 Phase 외)

- Beam search 3-step 플랜 오버레이 (Agent 6 P1 권고, 과공학 리스크 있음)
- Opus 4-7 migration (Agent 7, 골든 세트 후)
- ARIA live + 키보드 네비 확장 (Agent 5)
- HCSSF 필터 토글 UI (Agent 8)

---

## 진행 원칙

1. S1 → S4 순차 (S1이 모든 다른 phase의 기반)
2. 각 Phase 완료 후 감사 (`/audit-all`) + 사용자 검토
3. 각 파일 수정 전 Read 필수 (CLAUDE.md Read → Edit)
4. POB/젬 영역과 격리 유지 (원래 프로젝트 스코프 보호)

---

## 기록 / 참조

- 리서치 원본: `_analysis/syndicate_research_2026-04-20.md`
- 현재 리그: 3.28 Mirage (MEMORY `project_current_league.md` 정정 필요 — 감시됨)
- 8 에이전트 출력: `.../tasks/a1cd778c935f578d5.output` 외 7건 (세션 종료 시 삭제)
