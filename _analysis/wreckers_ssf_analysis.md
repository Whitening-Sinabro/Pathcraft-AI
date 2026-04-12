# Wreckers SSF Filter 상세 분석

> 소스: `Wreckers SSF Filter.txt` (2,460줄, 174 Show, 87 Hide)
> SSF 전용, Continue 체인 아키텍처

---

## 1. 전체 통계

| 항목 | 수량 |
|------|------|
| 총 라인 | 2,460 |
| Show 블록 | 174 |
| Hide 블록 | 87 |
| Continue 사용 | 315 (거의 전부) |
| 주석 비활성 블록 | ~31 (빌드 전용 템플릿) |

---

## 2. NeverSink과의 핵심 차이

| 관점 | NeverSink Cobalt | Wreckers SSF |
|------|-----------------|--------------|
| 구조 | Top-down, 첫 매칭 정지 | **Continue 체인** — 스타일 레이어링 |
| 크기 | 10,676줄, 759 Show | 2,460줄, 174 Show |
| 엄격도 | 5단계 파일 분리 | Progressive — AreaLevel 기반 자동 |
| 색상 | 복잡한 테마 (배경 6단계) | 12색 고정 (배경 항상 검정 or 흰색) |
| 사운드 | 6종 | 4종 (1=Epic, 9=Quest, 12=기타, 16=Map) + 커런시 전용 |
| SSF 최적화 | Trade 경제 파생 | SSF 전용 설계 |
| 안전망 | RestEx (섹션 끝) | **Orange Catch-All** (맨 위, 모든 아이템) |

---

## 3. Continue 체인 아키텍처

Wreckers의 가장 독특한 설계. CSS 캐스케이드와 유사.

**레이어링 순서:**
1. **Catch-All**: 모든 아이템에 Orange 텍스트 → 미분류 아이템 안전망
2. **Chromatic/Jeweller**: RGB 소켓 → Pink 보더, 6소켓 → Pink 보더
3. **Default Display**: 레어리티별 기본 색상 (Normal=White, Magic=Blue, Rare=Yellow)
4. **Special BaseTypes**: 특수 베이스 → 다시 Orange로 복원
5. **Corrupted/Mirrored**: Red 보더 추가
6. **T1 Borders**: 높은 ilvl → 레어리티색 보더 (크래프팅 가능 표시)
7. **Hide + Continue**: Normal(AL>=14), Magic(AL>=24) 숨기기
8. **Re-Show**: 특수 클래스(Jewel/Flask/Tincture 등) 다시 Show

**핵심 트릭: Hide + Continue**
- Normal/Magic을 숨기되 Continue를 사용
- 이후 블록에서 특정 조건(링크/소켓/특수모드)으로 다시 Show 가능
- NeverSink은 이를 위해 Hide 위에 모든 예외를 나열해야 함

---

## 4. 색상 체계

| 색상 | RGB | 용도 |
|------|-----|------|
| Black | 0 0 0 | 배경 (기본) |
| White | 255 255 255 | 배경 (에픽), Normal 텍스트 |
| Blue | 0 75 255 | Magic 텍스트 |
| Yellow | 255 255 0 | Rare 텍스트 |
| Brown | 150 75 0 | Unique 텍스트 |
| Cyan | 0 255 255 | 젬, 시체 |
| Pink | 255 0 200 | 커런시, 레시피 보더 |
| Purple | 200 0 255 | 프래그먼트 |
| Red | 200 0 0 | 부패/타락/미러 보더 |
| Orange | 255 123 0 | Catch-All, 신규 아이템 |
| Grey | 123 123 123 | 디비니 카드 |
| Gold | 225 175 25 | 골드, 블라이트 맵 |
| Green | 0 75 0 (bg) / 0 123 0 (text) | 퀘스트 |

**보더 의미:**
- Pink = 벤더 레시피 가치 (Chromatic/Jeweller)
- Red = 부패/타락/미러
- 레어리티색 = T1 모드 크래프팅 가능 (ilvl 85/86+)
- Orange = 새 리그 아이템

---

## 5. 사운드 체계

| Sound ID | 용도 |
|----------|------|
| **1** | Epic (6링크, 최고급 디비카) |
| **9** | 퀘스트 |
| **12** | 기타 전부 (볼륨으로 가치 구분: 75~300) |
| **16** | 맵 (볼륨 150~300, 티어별 점진) |
| **Sh[Name]** | 커런시 전용 사운드 (ShAlchemy, ShChaos, ShExalted, ShDivine, ShMirror 등) |
| **None** | 저가/무음 아이템 |

---

## 6. 미니맵 아이콘 매핑

| 모양 | 카테고리 |
|------|----------|
| UpsideDownHouse | Catch-All |
| Cross | 커런시 |
| Square | 디비카, 장비 |
| Star | 에픽, 유니크 |
| Circle | 젬, 맵 |
| Moon | 프래그먼트 |
| Raindrop | 플라스크 |
| Kite | 쥬얼 |
| Triangle | 퀘스트 |

---

## 7. 커런시 티어링 (SSF 관점)

**4종 사운드 없는 기본 커런시 ("Silent Singles"):**
- Wisdom/Portal Scroll, Armourer's/Whetstone, Transmutation, Augmentation → 폰트 25, 무음
- Chance, Shards → 폰트 30, 무음
- Alteration, Chromatic, Jeweller's → 폰트 35, 무음

**오일 계단식 (폰트/볼륨 점진 증가):**
Clear(33) → Sepia(34) → Amber(35) → Verdant(36) → Teal(37) → Azure(38) → Indigo(39) → Violet(40) → Crimson(41) → Black(42) → Opalescent(43) → Silver(44) → Golden/Reflective/Prismatic/Tainted(45)

**전용 사운드 커런시:**
Alchemy(ShAlchemy), Chaos(ShChaos), Regal(ShRegal), Vaal(ShVaal), Fusing(ShFusing), Blessed(ShBlessed), Exalted(ShExalted), Divine(ShDivine), Mirror(ShMirror)

**최고급 (흰배경 + 핑크):**
Awakener's Orb, Eternal Orb, Fracturing Orb, Sacred Oil, Harbinger's Orb, Exalted/Divine/Mirror 등

---

## 8. Hide Progression (레벨링 숨김)

**프로그레시브 숨김 — AreaLevel 기반:**
- AL 3: Small Life/Mana Flask
- AL 5~13: 초반 장비 (Crude Bow, Rusted Sword, Plate Vest 등) 단계적 숨김
- AL 14: **모든 Normal 숨김** (가장 큰 전환점)
- AL 24: **모든 Magic 숨김**
- AL 28~83: 중후반 장비 베이스 단계적 숨김 (개별 BaseType 정확 매칭)
- AL 83: T16+ 맵 수준 — 저가 커런시까지 숨기기 시작
- AL 84: 고급 방어구 베이스 숨김

**특수 숨김:**
- Scroll Fragment, Alteration/Transmutation Shard → 모든 레벨 즉시 숨김
- Currency 6종 (Wisdom, Portal, Armourer's, Whetstone, Trans, Aug) → StackSize 프로그레시브:

| AreaLevel | 맵 티어 | StackSize 임계값 |
|-----------|---------|-----------------|
| >= 64 | Act 10 | <= 1 숨김 |
| >= 68 | 화이트 맵 | <= 2 숨김 |
| >= 73 | 옐로우 맵 | <= 3 숨김 |
| >= 78 | 레드 맵 | <= 4 숨김 |
| >= 83 | T16+ | <= 5 숨김 |

**젬 프로그레션:** AL >= 45에서 젬 드롭 숨김 (릴리 도착 전까지)
**플라스크 프로그레션:** AL >= 73에서 노말 플라스크 + 특정 엔드게임 플라스크 숨김
**장비 프로그레션:** AL 39~78까지 30+개 블록으로 개별 BaseType 순차 숨김. AL 73에서 최상위 베이스(Vaal Regalia, Hubris Circlet 등)까지 숨김.
**리그 소모품:** Heist 도구 + Expedition 아이템도 AL 75/80/83 3단계 숨김

---

## 9. 디비니 카드 3단계

| 등급 | 폰트 | 배경 | 사운드 | 아이콘 |
|------|------|------|--------|--------|
| "Don't Care" (36장) | 25 | 검정 | None | 없음 |
| 기본 (나머지) | 30 | 검정 | 12 vol200 | 1 Grey Square |
| "Absolutely!" (~160장) | 40 | 검정 | 12 vol300 | 0 Grey Square |
| "You've Got to be Kidding ME!!!" (~52장) | 45 | **흰색** | **1** vol300 | 0 Grey **Star** |

---

## 10. 맵 시스템

**색상 4단계 (티어 범위):**
- T1~5: 흰텍스트, 검정배경 (White Map)
- T6~10: 노란텍스트, 검정배경, 노란이펙트 (Yellow Map)
- T11~15: 빨간텍스트, 검정배경, 빨간이펙트 (Red Map)
- T16+: 빨간텍스트, **흰배경**, 흰이펙트 (최고 티어)

**폰트/볼륨 개별 매핑 (T1~T17):**
T1(30/150) → T2(31/160) → ... → T15(44/290) → T16(45/300) → T17+(46/300)

**특수 맵:**
- Influenced/Zana Memory: 흰별 아이콘
- Blighted: 금색 텍스트
- Uber Blighted: 금색 배경 + 흰별

---

## 11. PathcraftAI HCSSF에 참고할 핵심 설계

1. **Continue 체인 레이어링** — 한 아이템이 여러 블록에 매칭되어 스타일 누적. 코드 중복 최소화.
2. **프로그레시브 엄격도** — AreaLevel 기반 자동 전환. 별도 파일 불필요.
3. **모든 비장비 표시** — SSF 철학: 커런시/젬/플라스크/프래그먼트는 절대 숨기지 않음.
4. **T1 보더 인디케이터** — ilvl 85/86+에서 보더색으로 "T1 크래프팅 가능" 시각 표시.
5. **커런시 전용 사운드** — Alchemy/Chaos/Exalted/Divine/Mirror에 고유 사운드. 소리만으로 식별.
6. **오일 계단식** — 14종 오일에 각각 폰트/볼륨 1단계씩 차등. 가치 순서가 한눈에.
7. **신규 리그 섹션** — 오렌지 테마로 통일. 추가/제거 용이.
8. **레시피 AreaLevel 제한** — 고레벨에서 크로매틱/주얼러 레시피 아이템 크기 제한 (인벤 효율).
9. **디비카 3등급** — "Don't Care" / 일반 / "Absolutely!" / "Kidding ME!!!" 명확한 4단계.
10. **Orange Catch-All 안전망** — 맨 위에서 모든 아이템에 오렌지 적용. 필터가 모르는 아이템 = 오렌지.
