# Syndicate 리서치 통합 리포트 — 2026-04-20

> 8 병렬 에이전트(general-purpose) 병렬 리서치 결과 통합. 기준점 v2 적용.
> 원문: 각 에이전트 출력(Syndicate 현재 코드 분석 / 메타 / 기존 도구 / 보상 매트릭스 / UX / 알고리즘 / OCR / HCSSF 프리셋).
> 리그 앵커: **3.28 Mirage (2026-03-06 ~ 2026-07-13 예정)**.

---

## 1. 치명적 발견

| # | 문제 | 영향 | 소스 에이전트 |
|---|------|------|:--:|
| 1 | `syndicate_members.json` 보상 70%+ 부정확 | 사용자 오도 | Agent 4 |
| 2 | **It That Fled = Breach 테마** (JSON엔 Bestiary로 오기재) | 치명 오인 | Agent 4 (fdaytalk/aoeah 교차 확인) |
| 3 | 리그 = 3.28, 문서/MEMORY는 3.26 표기 | 3.26 Mastermind 분리 / 3.28 보상 리워크 미반영 | Agent 2, 4 |
| 4 | SS22 프리셋 deprecated (3.26 이후 구식) | 구식 레이아웃 추천 | Agent 2, 8 |
| 5 | SyndicateBoard.tsx 620줄 + syndicateEngine 단위 테스트 0건 | 300룰 초과 + 회귀 테스트 부재 | Agent 1, 6 |
| 6 | 알고리즘 = 1-step greedy, 액션 부작용/비용/목격자 제약 무시 | 추천 오도 가능 | Agent 6 |
| 7 | OCR 실측 정확도 0건 (mock 19건만) | 프롬프트 회귀 추적 불가 | Agent 7 |
| 8 | 현 meta = **2x2/2x5** (2명 파밍 + 5명 인텔리). `meta_2x2_5` 프리셋 없음 | 메타 공백 | Agent 2, 8 |

---

## 2. 3.28 Mirage 17 멤버 × 4 분과 보상 매트릭스 (T2 교차 확인)

출처: fdaytalk.com + aoeah.com + poe-vault.com (3 T2 소스 교차 확인).

| 멤버 | Transportation | Fortification | Research | Intervention (Scarab) |
|------|---|---|---|---|
| Aisling | Double Veiled Items | Craft: Veiled Exalted Orb | Craft: Veiled Chaos | Torment |
| Cameria | Abyss Scarabs | Jewel chest | Jewel crafting | Delirium |
| Elreon | Fragments | Corrupted gear chest | Tainted currency | Beyond |
| Gravicius | Divination card stacks | Div card chest | Swap div cards | Divination |
| Guff | Random currency | Rare equipment chest | Reflecting Mist jewel | Blight |
| Haku | Unique strongbox | Domination Scarabs | Influenced crafting | Ambush |
| Hillock | Influenced gear chest | Influence crafting | Eldritch implicit crafting | Influencing |
| **It That Fled** | **Foulborn uniques** | **Breach ring crafting** | **Tainted socket currency** | **Breach** |
| Janus | Gold piles (Kalguur) | Kalguuran Scarabs | Unique purchase trade | Expedition |
| Jorgin | Sulphite Scarabs | Delve gear chest | Talisman crafting | Bestiary |
| Korell | Anarchy Scarabs | Essence gear chest | Essence crafting | Essence |
| Leo | Incursion Scarabs | Corrupted unique chest | Unique corruption crafting | Ultimatum |
| Riker | Unique items | Unique chest | Ancient Orb crafting | Titanic |
| Rin | Originator maps | Unique map chest | Scarab chest | Cartography |
| Tora | Quality gems | Gem chest | Gem crafting currency | Ritual |
| Vagan | Incubators | Incubator completion | Fracturing Orb crafting | Legion |
| Vorici | Currency stacks | Socket/link crafting | Chance/Scour crafting | Harvest |

+ Catarina = Mastermind. Leader 7명 승격 + 4 Safehouse 클리어 시 Mastermind Medallion 드롭 (3.26 이후).

Leader-specific drops (공통): Veiled Chaos Orb / Syndicate Medallion / Allflames / Paradoxica(Intervention Leader).

---

## 3. 현 코드 구조 요약 (Agent 1)

- **SyndicateBoard.tsx 620줄**: 6 관심사 혼재
  - PresetPicker (313-352)
  - TargetPreview (354-390)
  - CurrentBoard (392-543)
  - VisionControls (215-284)
  - Recommendations (545-572)
  - MemberDetail (574-619)
- **syndicateEngine.ts 187줄**: computeRecommendations (1-step greedy, priority 상수 100/95/90/75/60/55/40)
- **syndicate_vision.py**: Claude Opus 4-6, ephemeral cache, 17 멤버 ko alias 하드코딩
- **통합**: React ↔ Tauri command(`analyze_syndicate_image`, `syndicate_recommend`) ↔ Python 완전 연결
- **테스트**: engine 단위 0건 / vision 19건 모두 mock (실 이미지 0건)

**내부 모순 발견**: `layouts.json` `ss22` 프리셋이 Gravicius를 Intervention에 배치 — 튜토리얼은 "Transportation Gravicius + Intervention Cameria"로 설명. 데이터 불일치.

---

## 4. 메타 변화 (Agent 2)

### 3.26 (Secrets of the Atlas) 큰 변경
- Mastermind가 Safehouse에서 분리 — Medallion 필요 (≈1/10~1/15 Leader 처치당)
- "SS22 2-Safehouse Standard" 구식화

### 3.28 (Mirage) 변경
- Veiled Exalted Orb 드롭률 대폭 상향 (Divine → Chaos급)
- Aisling Fortification = Veiled Exalt craft (더 선호). Research = Veiled Chaos.
- It That Fled 복귀 (3.26에서 임시 제거)
- Atlas Passive "Pillage and Plunder" 리워크 (drop → Fractured Veiled Modifier)
- Betrayal Scarab of Intelligence → of the Allflame 이름 변경

### 현 meta = 2x2/2x5
- 2명 집중 파밍 분과 × 2 (예: Transportation: Gravicius + It That Fled / Research: Guff + Janus)
- 5명 인텔리 충전 분과 × 2 (Fortification / Intervention)

---

## 5. UX 권고 (Agent 5)

- Drag-and-drop은 성인 대상 점·클릭 대비 느림(+0.5~1s/op). a11y 부담 큼 → **보류**
- Cmd+K 멤버 할당 팔레트 권장 (Linear/Raycast 패턴, 20+ 옵션에 적합)
- Before/After 분과 diff 그리드 (목표 / 현재 나란히 + 색 코딩)
- 추천 hover → 보드 슬롯 펄스 연동
- ARIA live + 키보드 네비게이션 (현 `aria-live` 없음)

POE 인게임 보드 은유: string 연결 라인, Intelligence 진척 bar (토글식 차용 가능)

---

## 6. 알고리즘 개선 (Agent 6)

현 computeRecommendations:
- O(n) 그리디 1-step
- priority 상수 하드코딩 (100/95/90/75/60/55/40)
- 목격자 제약 없음, Interrogate rank 0 연쇄(이탈) 미모델링
- Betray 부작용(동반 승격) 미시뮬

권고:
- **[P0] 액션 비용 벡터 + 도달성 게이트** — `ActionCost { encounterTurns, sideEffect, preconditions }`. priority를 `benefit - cost` 계산으로
- **[P1] Beam search (k=3, d=5)** 오버레이 — "3-step 플랜" 표시. 현 그리디는 "지금 1개"로 유지
- MCTS는 과잉 (Bargain 확률 결과 모델링이 필요한 경우에만)

상태공간 상한: 10^7 이내, pruning 후 전수 탐색 가능.

---

## 7. OCR 파이프라인 (Agent 7)

- E2E 연결 완료 (Python ↔ Tauri ↔ React)
- 골든 스크린샷 회귀 세트 0건 — 프롬프트 변경 시 침묵 실패 가능
- 이미지 SHA-256 캐싱 없음 — 재업로드 시 매번 API 비용
- Opus 4-6 → 4-7 마이그레이션 대상 (토크나이저 +35% 필요)

권고:
- **[P0] 골든 스크린샷 5~10장** + `@pytest.mark.integration`
- **[P0] 이미지 SHA-256 캐싱** (`cache_dir/<sha256>.json`)
- **[P1] Opus 4-7 migration** (골든 세트 통과 후)

---

## 8. HCSSF 프리셋 3종 설계 (Agent 8)

### A. `hcssf_safe_start` — 캠페인~T1 맵
```
Intervention: hillock, tora
Fortification: haku, elreon, korell
Research: vorici, jorgin
Transportation: guff, riker, it_that_fled
```
목적: Flask quality + quality currency + life/resist jewelry

### B. `ssf_crafting_core` — 중반 (Aisling + Vorici)
```
Research: aisling, vorici, jorgin, rin
Fortification: elreon, haku, korell
Intervention: tora, hillock
Transportation: guff, riker
```
목적: Veiled craft + white socket + gem level 21

### C. `ssf_currency_sustain` — 후반 HC-safe
```
Intervention: cameria, tora, hillock
Transportation: gravicius, guff, riker
Research: aisling, vorici
Fortification: elreon, haku, korell
```
목적: Currency Scarab + Gravicius payout + Mirror Shard. Janus/Vagan 제외 (HC 위험).

---

## 9. 기존 도구 경쟁력 (Agent 3)

| 도구 | OCR/IR | drag-drop | preset | recommend | 유지보수 (2026) |
|------|:--:|:--:|:--:|:--:|:--:|
| Awakened PoE Trade | — | — | 정적 치트시트 | — | Active (03) |
| Exile-UI | Template Matching | — | Yes | Yes (색) | Active (04) |
| BetrayalPlanner | — | ✅ | — | — | Dead |
| Exilence CE | — | — | — | — | Active (N/A for syndicate) |

Negative Space (PathcraftAI 없고 경쟁사 있음):
- Drag-drop 보드 (BetrayalPlanner)
- 보상 우선순위 색 코딩 (Exile-UI)
- 오버레이 핫키 호출 (APT/Exile-UI)

주의: 인게임 overlay/template matching은 GGG ToS 회색지대. Exile-UI는 "read values 안 함" 조항으로 회피. PathcraftAI OCR은 **사용자가 스크린샷 수동 업로드** 모델 → ToS 안전.

---

## 10. 소스 (Tier + URL + 리그 + 확인 포인트)

핵심 소스만 발췌. 전체는 각 에이전트 원문 참조.

- **T0** [PoE Patch Notes 3.28.0](https://www.pathofexile.com/forum/view-thread/3913392) — 멤버 보상 변경 원문 (3.28 Mirage)
- **T1** [PoE Wiki: Mirage league](https://www.poewiki.net/wiki/Mirage_league)
- **T1** [PoE Wiki: Version 3.26.0](https://www.poewiki.net/wiki/Version_3.26.0) — Mastermind 분리
- **T1** [PoE Wiki: Version 3.28.0](https://www.poewiki.net/wiki/Version_3.28.0) — Atlas Passive 변경
- **T1** [PoE Wiki: Immortal Syndicate](https://www.poewiki.net/wiki/Immortal_Syndicate) — canonical 구조
- **T1** [PoE Wiki: Veiled Exalted Orb](https://www.poewiki.net/wiki/Veiled_Exalted_Orb) — 드롭률 변경
- **T1** [Maxroll Betrayal Farming Guide](https://maxroll.gg/poe/currency/betrayal-farming-guide) — 5-5-2-2 setup
- **T1** [Maxroll 3.28 Mirage Patch Notes](https://maxroll.gg/poe/news/3-28-mirage-patch-notes) — Betrayal 섹션
- **T2** [PoE Vault Immortal Syndicate Guide](https://www.poe-vault.com/guides/immortal-syndicate-guide) — 17×4 매트릭스
- **T2** [fdaytalk 3.28 Betrayal Cheat Sheet](https://www.fdaytalk.com/poe-3-28-betrayal-cheat-sheet-best-syndicate-rewards-guide/) — 교차 검증 소스
- **T2** [aoeah 3.28 Betrayal Cheat Sheet](https://www.aoeah.com/news/4442--poe-328-betrayal-cheat-sheet-rewards--farming-strategy) — 2x2/2x5 meta
- **T2** [Inven 신디케이트 가이드](https://www.inven.co.kr/webzine/news/?news=224006) — 한국 커뮤니티 (한영 용어 매핑)
- **T0** [NN/g Drag-and-Drop](https://www.nngroup.com/articles/drag-drop/) — UX 연구
- **T0** [NN/g Fitts's Law](https://www.nngroup.com/articles/fitts-law/) — UX 이론
- **T1** [W3C WAI-ARIA Drag-Drop Best Practices](https://www.w3.org/wiki/PF/ARIA/BestPractices/DragDrop) — a11y
- **T0** [Anthropic Prompt Caching](https://platform.claude.com/docs/en/about-claude/pricing) — OCR 비용 모델

---

## 11. 검증 미완료

- poe.ninja Mirage 경제 스냅샷 fetch 실패 (Aisling T4 divine 환산가, Veiled Exalted Orb 실거래가)
- poewiki 일부 페이지 403 — T2 가이드 교차 의존
- Steelmage/Mathil 영상 transcript 미확인 (YouTube 차단)
- 한국 커뮤니티 독립 메타 여부 불명 — 영어권 "2x2/2x5" 번역 수준

---

**다음 단계**: `.claude/status/syndicate_phase_plan.md` 참조.
