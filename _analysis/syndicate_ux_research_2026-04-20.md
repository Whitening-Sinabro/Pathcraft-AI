# Syndicate UX 2차 리서치 + 사용자 피드백 (2026-04-20)

> S3 구현 후 사용자 피드백 기반 방향 재정립. 1차 리서치: `syndicate_research_2026-04-20.md` (8 에이전트).

---

## 사용자 피드백 요지

1. **Cmd+K 팔레트는 "고인물 전용"** — 초보자/중급자는 멤버 이름/분과/rank 모두 모름
2. **타겟 재설정** = 초보자 + 3-4년차 이하
3. **핵심 문제**: "누굴 잡아야 하는지 / 지금 멤버가 이득인지 / 어떻게 배치해야 할지 **아무것도 모름**"
4. 스트리머도 대충하거나 몇몇만 암기하고 그 자리에 넣음
5. **사용자 가설**: "다른 메커닉과 Syndicate는 초반에만 하거나 SSF에서 많이 함"
6. **요구**: 유추 금지, Reddit/실 데이터 기반으로 리서치

---

## 핵심 교훈

> **"알고 있다"를 전제로 한 UI는 타겟 오인**
> 현 구현(Cmd+K 팔레트, diff 색 코딩, hover 펄스) 전부 멤버/분과/rank 지식을 가정.
> 타겟(초보~중급 SSF)은 그 지식 자체가 없음.

---

## 2차 리서치 시도 결과

### 5 병렬 에이전트 — 혼합 결과

| # | 주제 | 상태 | tool_uses |
|---|------|:--:|:--:|
| 1 | Reddit 초보 Syndicate 혼란 | 완료 | **49** ✅ 실 리서치 |
| 2 | 메커닉 × Syndicate 연계 | 완료 | **0** — training data 추정 |
| 3 | SSF vs Trade 행동 차이 | 완료 | **0** — 명시적으로 작업 거부 |
| 4 | 리그 진입 시점 | 완료 | **0** — training data 추정 |
| 5 | 스트리머 실 플레이 패턴 | 완료 | **0** — training data 추정 |

**원인 추정**: 에이전트 풀이 이번 배치에서 WebFetch/WebSearch 로드 실패. 1/5만 정상.

---

## 🔑 Agent 1 핵심 발견 (실 데이터 — 49 tool_uses)

> 15+ 실 포스트 + 한국 커뮤니티 포함. 2018~2025 타임라인.

### 사용자 가설 재검증

**"초반만 / SSF만"** 가설 — 부분 증거:
- "스킵함" 그룹 존재 (5건 인용): pinksagee "level 80 이후 안 함", semma_car19 "Catarina 키워도 1샷", petrovskyz "오프스크린 4K 원샷"
- **단**: 스킵 이유 = **복잡성이 아닌 난이도/원샷**. 사용자 가설의 인과(복잡하니까 안 함)와 다름

### 3대 혼란 지점 (최빈)

1. **Thumbs up / 색 기호 해석** — 치트시트 보면서도 모름 (flores91091)
2. **Interrogate vs Execute 언제?** — 4건 포스트
3. **Execute 회색 이유** — **암묵 규칙** "2+ 멤버 + 마지막 대화 대상 아님". UI에 안 알려줌 (OP + TemjinGold 답변)

### 핵심 insight

- **"게임이 깊은 게 아니라 문서화 안 됨"** (ImmortalCX) — 복잡성보다 **"안 알려줌"**이 진짜 문제
- **베테랑도 못 잡음** (esostaks 250+ 시간): "I'm still can't grasp Syndicate mechanics"
- **치트시트 이미 존재하지만 해결 안 됨** — flores91091은 치트시트 **보면서** 질문
- **되돌리기 불가** (TravisL 2025-06): "실수 2-3번이면 50맵 필요"
- **"Aisling/Vorici만 중요"** 실질 (6_din_49): "do your best to make them lvl 3... bargain=수량↑". 17명 평등 UI는 **과도**

### 한국 커뮤니티 특이점

- **Inven/루리웹/fmkorea 가이드가 영어권보다 더 친절** — 보상표 + 추천 배치 구체
- **Inven**: "Guff는 도박으로... 고인물 급만 좋은 아이템, 초보는 어버버"
- 한국 유저는 가이드 접근성 ↑, 그래도 RNG 멤버(Guff)는 포기

### 실 pain 빈도표

| 주제 | 포스트 수 | 원인 |
|------|:--:|------|
| interrogate vs execute | 4 | 암묵 룰 |
| Execute 회색 조건 | 2 | UI 미설명 |
| 치트시트 해석 | 2 | 기호 의미 |
| 되돌리기 불가 | 2 | 3.26 이후 |
| 난이도/원샷 | 5 | 별도 도메인 |
| 베테랑도 포기 | 1+ | 학습 ROI |

---

## Agent 1 권고 Actionable (실 데이터 근거)

| ID | 기능 | 근거 인용 |
|----|------|-----------|
| **A** | Action Gating 툴팁 — "Execute 회색?" → "2+ 멤버 + 마지막 아님" | TemjinGold #6 (포럼 답변으로만 존재) |
| **B** | Rank × Division × Reward 3축 매트릭스 시각화 | 치트시트 해석 실패 flores91091 |
| **C** | "한 번에 하지 마" pre-commit 경고 (부작용) | TravisL "50 맵" |
| **D** | 한국어 UI 우선 | Inven 가이드 품질 |
| **E** | "스킵 OK" 빌드별 안내 | pinksagee/petrovskyz 스킵 그룹 |
| **F** | 초보 모드 — 핵심 3명(Aisling/Vorici/ITF)만 강조 vs 17명 평등 | 6_din_49 실질 |

### Red Team (Agent 1 자기 반박)

1. **치트시트 이미 있음** — 정적 lookup이면 경쟁력 X. **차별화 = OCR + 상호작용 + 현 리그 반영 + Rank 플랜 자동화**
2. **복잡성 불만 ≠ 도구 수요** — 스킵 그룹이 다수일 수 있음. TAM 작을 리스크. **검증법**: β 출시 시 "스킵 권장" 모드 선택률 측정
3. **17명 평등 UI는 과도** — 초보 "Aisling/Vorici만 3 명 모드"가 효과적일 수 있음

### 주요 인용 URL

- [PoE Forum: Questions about syndicates cheat sheet (flores91091)](https://www.pathofexile.com/forum/view-thread/3076254)
- [PoE Forum: Betrayal execution mechanic question (TemjinGold)](https://www.pathofexile.com/forum/view-thread/3347982)
- [PoE Forum: No way to wipe the syndicate board (TravisL 2025-06)](https://www.pathofexile.com/forum/view-thread/3799281)
- [PoE Forum: Still can't grasp (esostaks)](https://www.pathofexile.com/forum/view-thread/3003611)
- [PoE Forum: New Player's Thoughts on Betrayal (ImmortalCX "undocumented")](https://www.pathofexile.com/forum/view-thread/2275160/page/2)
- [Inven 신디케이트 가이드](https://www.inven.co.kr/webzine/news/?news=224006)
- [Reddit: Idiot proof Syndicate guide (2021)](https://www.reddit.com/r/pathofexile/comments/qx3fjx/)

### 메인 스레드 직접 WebSearch/WebFetch

사용자 가설 검증 목적. 아래는 **실 검색 결과**.

#### 1. "Syndicate 초반만 / SSF만" 가설 vs 커뮤니티 서술

**검증 결과**: 사용자 가설과 상충하는 서술 다수.

- [aoeah 3.28 Cheat Sheet](https://www.aoeah.com/news/4442--poe-328-betrayal-cheat-sheet-rewards--farming-strategy): "Focusing on high-value members like Gravicius, Aisling, Vorici, and It That Fled can make Betrayal **one of the most profitable farming methods** in Path of Exile 3.28."
- [sportskeeda 3.28 cheat sheet](https://www.sportskeeda.com/mmo/path-exile-betrayal-cheat-sheet-3-28): 3.28 Syndicate "valuable and worth farming"
- YouTube (검색만, 영상 미시청): `"STOP Struggling! This Betrayal Strategy Is FREE Money (PoE 3.28 Mirage)"` — 3.28 주력 farming 주장
- YouTube: `"PoE 3.28 - Don't Skip The Mirage Mechanic in Campaign!"`

**Maxroll Betrayal Farming Guide** (T1) [직접 fetch]:
- 가이드는 **엔드게임 최적화** 초점 (Rank 3 멤버 + Mastermind + Scarab self-sustain)
- "early vs endgame" 구분 명시 **없음**
- SSF vs Trade 분기 명시 **없음**
- "skip" 권고 **없음**

**해석 (추정)**:
- 사용자 가설("초반만 / SSF만")은 **부분적으로만 옳음** — 일부 플레이어 행동일 수는 있으나, 가이드 생태계는 엔드게임 파밍을 전제로 설계됨
- 실제 데이터(Reddit 비율, 플레이타임 통계)는 **미확보** — WebSearch에서 Reddit 직접 스레드 매칭 실패 ("No links found")
- **결론 미확정**. 추가 Reddit 직접 탐색 필요

#### 2. Reddit 직접 탐색 실패

- WebSearch 쿼리 `"syndicate worth" OR "betrayal worth" beginner SSF` → 0 결과
- Reddit 검색은 Google 인덱스 의존 → 특정 스레드 접근성 낮음
- **Future 작업**: reddit.com 직접 URL + 알려진 스레드 제목 검색 필요

---

## 에이전트 2 hypothesis (미검증, 훈련 데이터 기반)

> **불확실 라벨 강제** — 실 검증 없음

### 메커닉 × Syndicate 의존도 표 (추정)

| 메커닉 | Syndicate 필수? | 연계 멤버 | 근거 |
|---|---|---|---|
| Scarab farming | 보조 (Strong) | Intervention 전체 | 추정 |
| Breach (It That Fled 3.28) | 무관~보조 | Research | 추정 |
| Delve | 약한 보조 | Jorgin (Sulphite Scarab) | 추정 |
| Essence | 보조 | Aisling T4 판매 | 추정 |
| Harvest | 무관 | — | 사실 (독립 메커닉) |
| Legion | 무관~보조 | Intervention Legion Scarab | 추정 |
| Expedition | 무관 | — | 사실 |
| Ultimatum/Ritual | 무관 | — | 사실 |
| Mastermind farm | **필수 (본체)** | 전체 | 사실 |

**검증 필요**: 3.28 Mirage 특화 값 (Foulborn Unique 기여도, Breach Scarab 시세, Pure Talent 시세)

---

## 에이전트 4 hypothesis (미검증, 훈련 데이터 기반)

### 리그 타임라인 진입점 분포 (추정)

| 시점 | 진입 % (추정) | 주된 목적 |
|------|:--:|------|
| Act 2~5 | 0% | N/A (조우 전) |
| Act 6~8 Campaign | 100% (passive) | 자연 루팅만 |
| Act 9 Safehouse 해금 | 40~50% | 호기심 1~2 run |
| Act 10 ~ White Maps | 20~30% | Scarab/Currency |
| Yellow Maps (Day 2~4) | 40~60% | Veiled unveil 시작 |
| Red Maps (Day 5~14) | 70~85% | Aisling T4, Jun mission |
| Post-Atlas (Week 2+) | 80%+ | Aisling rank 3, Mastermind |

**일반론**: "Syndicate는 엔드게임 기능" 다수 의견. "리그 첫날부터"는 Jun 전문 farmer 니치.

**검증 필요**: 이 %는 훈련 데이터 ballpark — poe.ninja/Reddit 실 데이터 미수행.

### Aisling rank 3 달성 (추정)

- SSF: Jun mission 40~80회, Day 3~7
- Trade: TFT "Aisling service" 구매 → Day 3+ 즉시 (5~15 Divine)
- 리그 초반 Aisling T4 service 10~40 Divine → Week 2 안정화 5~15 Divine
- **미검증**: poe.ninja 직접 확인 필요

---

## 설계 방향 (재정립, 현 리서치 한계 감안)

### 확정된 것 (사용자 피드백 확정)

1. **Cmd+K 팔레트는 초보자 부적합** — hidden/advanced 토글로 격하
2. **타겟 audience = 초보~3-4년차 SSF/casual**
3. **Decision helper** 필요 — "지금 뭐 해야 하지?"에 답하는 UI

### 설계 아이디어 (검증 필요)

| 아이디어 | 근거 | 검증 포인트 |
|----------|------|-------------|
| Encounter Advisor (인카운터 4명 입력 → 잡아/넘겨) | 초보자 결정 지원 | 실제 초보자가 이걸 원하나? Reddit에서 "Who should I capture" 질문 빈도? |
| Slot Value 상시 표시 (보상 1줄) | 학습 도움 | "보상이 뭔지 모른다"가 실제 주된 혼란인가? |
| Goal-driven 프리셋 선택 (뭘 원해? → 자동 추천) | 선택 부담 감소 | HCSSF 3 프리셋이 이미 부분 해결. UI 명시 강화? |
| 트레이드 유저 스킵 안내 배너 | 잘못된 투자 방지 | 실제 트레이드 유저 스킵 비율 검증 필요 |

### 미해결 질문 (다음 세션 또는 사용자 응답)

1. Syndicate는 리그 어느 시점에 가장 많이 플레이되는가 — 실 데이터?
2. SSF vs Trade 비율 + 행동 차이 — 실측?
3. 초보자의 실 혼란 지점 — Reddit 직접 조사 필요 (현재 WebSearch 인덱스 문제)
4. 스트리머 실 행동 — VOD 샘플링 필요 (transcript 접근 제약)

---

## 다음 액션 후보

### A. 현 상태로 설계 진행 (검증 유보)
장점: 빠름 / 단점: 검증되지 않은 가설로 코드 작성, 잘못된 방향 리스크

### B. 직접 Reddit 스레드 URL 수동 수집 후 WebFetch
- 알려진 큰 포스트 (월간 ~100k+ subscribers subreddit)
- `reddit.com/r/pathofexile/search?q=syndicate+skip`
- reddit API 직접 쿼리 (anon)

### C. 사용자에게 실 경험 인터뷰
- "본인이 Syndicate 막혔던 순간 묘사"
- "친구/커뮤니티에서 들은 초보 질문"
- → 1인 관찰 < 10명 스레드 but 직접 소스

### D. 일단 보류, 다른 플레이 UX 테스트
- Cmd+K 팔레트만 advanced 뒤로 숨기고
- HCSSF 프리셋 카드 **설명 강화** (Slot Value 미니 버전)
- 나머지는 실 사용 후 재판단

**추정 권장**: D → 작은 개선만 적용하고 실제 시각 검증 반복. 큰 아키텍처 변경은 실 데이터 수집 후.

---

## 기록 목적

- S3 구현(팔레트/diff/hover) 후 **방향 재검토 필요**
- 1차 리서치 8 에이전트 + 2차 5 에이전트 = 13 시도 중 1차 8 성공, 2차 5 중 0 성공 (툴 미로드)
- 실 데이터는 메인 스레드에서 직접 수집해야 함 (web tools 사용 가능)
- 사용자 가설 중 일부 (초반만/SSF만) 는 커뮤니티 가이드와 **상충** — 추가 검증 필요
- Decision helper UI 방향은 유효하나 구체 설계는 실 초보자 데이터 수집 후
