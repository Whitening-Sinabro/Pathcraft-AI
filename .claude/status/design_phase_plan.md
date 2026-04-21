# 어플 전면 리디자인 — Phase 0~5

> 2026-04-20 착수. 범위=c(전면), 레퍼런스=b+e(참고앱+POE UI), 창=하이브리드(1440×900+오버레이), 테마=다크 단일.

---

## 의사결정 요약

| 축 | 결정 |
|---|---|
| 범위 | 전면 리디자인 (c) |
| 레퍼런스 | Linear 레이아웃 + PoB Community 정보 밀도 + POE 아이템 툴팁 프레임 + Awakened POE Trade 오버레이 |
| 기본 창 | 1440×900, min 1100×700 |
| 오버레이 | 2개 창 전략 (transparent 런타임 토글 불가, Tauri 2.x `set_transparent` API 부재 확인) |
| 테마 | 다크 단일 (bg.base #0E0E10) |
| 대비 검증 | WCAG AA 이상 확정 (text.muted/rarity.unique/accent.primary 보정 완료) |
| POE Rarity | 실제 4등급(normal/magic/rare/unique)만. `rarity.mythic` 제거, `tier.s~d` 분리 |

---

## Phase 1 — 기반 정비 (2026-04-20 완료)

**PASS 조건**:
- pnpm test 53/53 ✅
- pnpm build 경고 0 ✅
- src/ 내 console 호출 0건 (logger 제외) ✅
- raw hex baseline: 측정 시점 다름 — 정정값은 Phase 4 항목 참조

**수정**:
- `src/theme.ts` 다크 토큰 전면 교체 (bg/border/text/accent/rarity/tier/status/anim/z/breakpoints + legacy flat aliases)
- `index.html` Pretendard Variable + JetBrains Mono CDN 로드
- `src/main.tsx` global.css import
- `src/App.tsx:161` console.info → logger.info
- `src/components/PassiveTreeCanvas.tsx:210` console.warn → logger.warn
- `src-tauri/tauri.conf.json` 1440×900 + min 1100×700 + theme Dark + CSP jsdelivr 허용
- `src/components/PobInputSection.tsx`, `src/App.tsx` 3개 call site nested 토큰 전환

**생성**:
- `src/utils/logger.ts` — dev/prod 분기 (prod에서 info/warn no-op)
- `src/styles/global.css` — CSS 변수 + 다크 body + 포커스 링 + 스크롤바

---

## Phase 2 — App.tsx 섹션 분리 (2026-04-20 완료)

**PASS 결과**:
- App.tsx 604 → 252줄 (목표 <200 미달, 300 룰 통과)
- 섹션 8개 생성, 각 18~103줄 (모두 <150 ✅)
- `useBuildAnalyzer` 훅 추출 (139줄)
- pnpm test 53/53, build 경고 0

**생성**:
- `src/components/sections/{BuildSummary,LevelingGuide,LevelingSkills,AuraUtility,KeyItems,PassivePriority,DangerZones,FarmingStrategy}.tsx`
- `src/hooks/useBuildAnalyzer.ts`

**잔존**: LevelingGuide fallback 회귀(수정 완료), tierColor 2-source(Phase 4), prop drilling(Phase 4)

---

## Phase 3 — 레이아웃 재구성 (2026-04-20 완료)

**PASS 결과**:
- App.tsx 252 → 224줄
- TopBar 28줄, Sidebar 58줄
- CSS bundle 1.44 → 4.15 kB (Shell + 반응형 + 광폭 예외)
- 반응형: <1100 사이드바 56px 아이콘 모드, <900 사이드바 숨김

**생성**:
- `src/components/shell/TopBar.tsx`, `src/components/shell/Sidebar.tsx`

**적용 패치**:
- 메인 자식 max-width 1100 + auto margin (가독성)
- `.app-main__full` 클래스 (광폭 예외 — PassiveTreeView 적용)
- Sidebar 라벨 ellipsis

**잔존**: SVG 아이콘 도입(Phase 4b), 키보드 네비, 오버레이 stub UX(Phase 5)

---

## Phase 4 — 컴포넌트 스타일링 (분할 검토)

**Baseline (2026-04-20 측정)**: 실 컴포넌트 raw hex 223건 (theme.ts 58 + global.css 13 제외 src/ 합계).

### Phase 4a — 토큰 치환 + dark 카드 (2026-04-20 완료)

**PASS 결과**:
- raw hex 실 컴포넌트 223 → **44** (-80%, 목표 <50 ✅)
- pnpm test 53/53, build 경고 0, CSS 4.19→6.88 kB
- legacy flat alias 22개 전부 제거
- tierColor 2-source → BuildSummary가 `colors.tier` 직접 참조
- Syndicate DIVISION_COLORS 다크 팔레트 적용

**생성 클래스 (global.css)**:
- 카드: `ui-card`, `ui-card--accent`, `ui-card--soft`, `ui-card--inset`
- 타이틀: `ui-section-title`, `ui-section-title__hint`
- 텍스트: `ui-text-muted`, `ui-text-secondary`, `ui-text-success/warning/danger/info`
- 버튼: `ui-button`, `ui-button--primary`, `ui-button--secondary`
- 알림: `ui-alert`, `ui-alert--danger`, `ui-alert--warning`
- 표: `ui-table`
- 배지: `ui-badge`, `ui-badge--accent/success/info`

**잔존 44건** (Phase 4 후속 또는 별도 트랙):
- 패시브 트리 38건 (TreeControls/PassiveTreeCanvas/Constants/Render — 캔버스 자체 그래픽)
- SyndicateBoard 5 (DIVISION_COLORS 4 dark hex 정의 + #fff 1)
- BuildSummary 1 (tier 원형 배지 텍스트 #fff)

### Phase 4b — SVG 아이콘 (2026-04-20 완료)

**결과**:
- 자체 SVG 인라인 채택 (Lucide React가 React 19 peer 미지원으로 `--force` 룰 위반 회피)
- 4개 아이콘: BuildIcon(hammer), SyndicateIcon(network), PassiveIcon(git-branch), OverlayIcon(picture-in-picture-2)
- Lucide path 차용 (ISC 라이선스)
- Sidebar B/S/P 영문 → SVG 교체

**생성**: `src/components/shell/icons.tsx` (~67줄)

### Phase 4c-A — 아키텍처 정리 4건 (2026-04-20 완료)

**결과**:
- drift 가드: theme.ts colors가 `var(--*)` 참조 반환 — global.css :root 단일 진실원
- TabId sync: `isTabId()` type guard + `TAB_IDS` const array
- DIVISION_COLORS 통합: SyndicateBoard가 `colors.syndicate` import (이전 2-source 해소)
- useBuildAnalyzer cleanup: `runIdRef` race-condition 가드 (unmount + 재호출)

**수치**:
- theme.ts hex 36 → 1 (text.onAccent 순수 흰색만)
- global.css 22 → 35 (tier/syndicate/rarity 신규 추가)
- 실 컴포넌트 hex 44 → 40

### Phase 4c-B — Context 도입 (2026-04-20 완료)

**결과**:
- `src/contexts/ChecklistContext.tsx` 생성 (57줄) — checked/toggle/buildKey/ck(helper)
- App.tsx Build 탭 Provider 래핑, 로컬 checked/toggleCheck 제거
- LevelingGuide/LevelingSkills/GearTimeline 3컴포넌트가 `useChecklist()` 직접 사용 (props 4개 → 0개)
- localStorage 영속 Context 내부로 이전 (단일 책임)
- App.tsx 224 → 189줄 (최초 <200 달성)
- 56/56 vitest (isTabId 테스트 3 추가)

---

## Phase 5 — 오버레이 모드

### Phase 5a — 인프라 (2026-04-20 완료)

**결과**:
- `tauri.conf.json` 2-창 선언 (main + overlay, overlay 초기 hidden)
- `capabilities/default.json` overlay 창 + show/hide/close/drag 권한
- `src/main.tsx` URL param 분기 (?mode=overlay)
- `src/overlay/OverlayApp.tsx` 드래그 바 + 닫기 버튼 + placeholder (58줄)
- `src/overlay/overlay.css` 반투명/프레임리스/둥근 모서리
- `Sidebar.toggleOverlay()` 실 구현 — `WebviewWindow.getByLabel` show/hide + setFocus
- Windows 실측 PASS — transparent + always_on_top 정상, 드래그/복귀 작동

### Phase 5b — 콘텐츠 (다음)

**범위**:
- 현재 Act/Lv 표시 (buildData → coaching.leveling_guide 매핑)
- 레벨링 체크리스트 (ChecklistContext 공유)
- 다음 스킬 전환 알림 (coaching.leveling_skills.skill_transitions)
- 맵 경고 요약 (coaching.map_mod_warnings.deadly)
- 컨텐츠는 localStorage에서 coaching 로드 (오버레이는 독립 창 — Provider 공유 불가. localStorage cache 활용)

**검증**: 실행 → 오버레이 콘텐츠 표시 확인

### Phase 5c — 폴리시 (Phase 5b 후)

- 창 위치/크기 localStorage 영속 (이벤트: `tauri://resize`, `tauri://move`)
- 단축키 `Cmd/Ctrl+Shift+O` 전역 토글 (Tauri GlobalShortcut 플러그인 검토)
- 오버레이 내에서 메인 분석 상태 동기 (Tauri 이벤트 emit/listen)

---

## 스펙 결정 (놓친 항목 7종, Phase 3~4 적용)

1. 포커스 링: `outline: 2px solid accent.hover + 2px offset`, `:focus-visible`만
2. 빈 상태: POB 미입력 시 중앙 64px 아이콘 + 안내 + Cmd/Ctrl+V 힌트
3. 로딩: 카드 스켈레톤 + 상단 4px progress bar (accent.primary indeterminate)
4. 에러: danger×10% bg + 1px danger border + 16px 아이콘
5. 애니메이션: anim.fast(120) / default(200) / slow(320), easing cubic-bezier(0.2, 0, 0, 1)
6. 반응형: 1100 접힘 / 900 숨김, minSize로 강제
7. 단축키: Cmd/Ctrl+1/2/3 탭, Cmd/Ctrl+K POB 포커스, Cmd/Ctrl+Shift+O 오버레이, Esc 모달

---

## 참고

- Tauri Window API: https://docs.rs/tauri/2.10.2/tauri/window/struct.Window.html
- transparent 런타임 토글 부재: tauri#8308
- 오버레이 창 치수(400×640): 추정값. Phase 5 프로토타입 실측 후 확정
