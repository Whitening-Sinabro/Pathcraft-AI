# NeverSink Cobalt Regular 필터 상세 분석

> 소스: `cobaltregular.txt` (v8.19.0a.2026.65.16, COBALT 스타일, REGULAR 엄격도)
> 10,676줄, captainlacer9 사용 필터

---

## 1. 전체 통계

| 항목 | 수량 |
|------|------|
| **총 라인** | 10,676 |
| **활성 Show 블록** | ~430 |
| **활성 Hide 블록** | ~19 |
| **주석 처리(비활성) 블록** | ~60 |
| **Continue 데코레이터 블록** | ~30 |

---

## 2. 섹션 구조 (목차)

| 섹션 | 이름 | 블록 수 (대략) |
|------|------|---------------|
| [[0100]] | Global Overriding (6링크) | 2 |
| [[0200]] | Gold (StackSize 기반) | 5 |
| [[0300]] | Influenced Items | 18 |
| [[0400]] | Eldritch Items | 2 |
| [[0500]] | Exotic Bases | 12 |
| [[0600]] | ID Mod Filtering — Combinations | 35 |
| [[0700]] | ID Mod Filtering — Dual Mods | 6 |
| [[0800]] | ID Mod Filtering — Single Mods | 8 |
| [[0900]] | High Priority Equipment (Perfection, Memory Strand) | 18 |
| [[1000]] | ID Mod — Corrupted Items | 3 |
| [[1100]] | Exotic Mods (Veiled, Incursion, Delve, Warband 등) | 20 |
| [[1200]] | Exotic Item Classes (Imbued, Voidstone, Relics 등) | 8 |
| [[1300]] | Exotic Variations (Synth, Fractured, Enchanted, Crucible) | 16 |
| [[1400]] | Recipes and 5links | 6 |
| [[1500]] | High Level Crafting Bases | 0 (전부 주석) |
| [[1600-1700]] | Endgame Rare Decorators (Continue) | 11 |
| [[1800]] | Endgame Rare — Veiled | 5 |
| [[1900]] | Endgame Rare — Breach/Talisman | 8 |
| [[2000]] | Endgame Rare — Conditional Hide | 2 |
| [[2100]] | Endgame Rare — Amulets/Rings/Belts | 6 |
| [[2300]] | Endgame Crafting Matrix | 14 |
| [[2400]] | Chancing Bases | 2 |
| [[2500]] | Endgame Flasks & Tinctures | 14 |
| [[2600]] | Misc Rules (RGB, Remaining Rares) | 4 |
| [[2700]] | Hide Layer 1 — Rare & Magic Gear | 2 (Hide) |
| [[2800]] | Jewels (Abyss, Generic, Cluster) | ~30 |
| [[2900]] | Heist (Cloak, Brooch, Gear, Tool) | 16 |
| [[3000]] | Gem Tierlists | ~30 |
| [[3100]] | Replica and Foulborn Uniques | 10 |
| [[3200-3300]] | Maps (Special + Normal Progression) | ~35 |
| [[3400]] | Pseudo-Map-Items (Logbook, Blueprint 등) | 10 |
| [[3500]] | Fragments & Scarabs | 13 |
| [[3600]] | Currency — Lifeforce | 7 |
| [[3700]] | Currency — Leveling Exceptions | 15 |
| [[3800]] | Currency — Stacked (3x/6x/Supply) | 27 |
| [[3900]] | Currency — Regular Tiering | 11 |
| [[4000]] | Currency — Special (Vials, Delirium, Fossil, Oil, Rune, Corpse, Essence, Omen, Tattoo) | ~40 |
| [[4100]] | Splinters (Breach, Legion, Simulacrum) | 16 |
| [[4200]] | Divination Cards | 10 |
| [[4300-4400]] | Remaining Currency + Questlike | 3 |
| [[4500]] | Idols | 13 |
| [[4600]] | Uniques | 30+ |
| [[4700-4800]] | Misc Map Items + Questlike #2 | 7 |
| [[4900]] | Hide Outdated Leveling Flasks | 4 (Hide) |
| [[5000]] | Leveling — Utility Flasks & Tinctures | 6 |
| [[5100]] | Leveling — Life/Mana/Hybrid Flasks | 30 |
| [[5200]] | Leveling — Rares | 40 |
| [[5300]] | Leveling — Magic/Normal Items | 30 |
| [5306-5307] | Final Hide + Safety Net | 2 |

---

## 3. Cobalt 6단계 배경색 티어 시스템

NeverSink의 핵심 설계. **배경색**이 가치 등급을 결정한다.

| 티어 | 배경색 RGB | 색 이름 | 텍스트 | 사운드 | 이펙트 | 아이콘 크기 |
|------|-----------|---------|--------|--------|--------|------------|
| **T1** | `255 255 255` | 흰색 | 빨강 `255 0 0` 또는 유니크갈 `175 96 37` | **6** 300 | Red | **0** (최대) |
| **T2** | `185 0 120` | 딥핑크/마젠타 | 흰색 `255 255 255` | **1** 300 | Red | **0** |
| **T3** | `130 30 190` | 보라 | 흰색 | **2** 300 | Yellow | **1** |
| **T4** | `50 70 190` | 코발트 블루 | 흰색 | **2** 300 | White | **2** |
| **T5** | `80 120 160` | 회청색 | 흰색 | **2** 300 | Grey | **2** |
| **RestEx** | `100 0 100` | 진보라 | 핑크 `255 0 255` | **3** 300 | Pink | **0** |

**RestEx**: 모든 카테고리 끝에 존재하는 "안전망" 블록. 티어리스트에 없는 신규 아이템을 핑크색으로 최대 강조해서 놓치지 않게 함.

---

## 4. 사운드 체계

| AlertSound ID | 의미 | 사용 맥락 |
|---------------|------|-----------|
| **6** | 최고가 알림 | T1 (Mirror, Divine, Faceted Fossil, Golden Oil 등) |
| **5** | 맵 전용 | Blighted 맵, Enchanted 맵, Logbook, Blueprint, Sanctum |
| **4** | 일반 맵 | 맵 T1~T10 |
| **3** | 크래프팅/특수 | Exotic 모드, Veiled, Enchanted, 하이스트, 퀘스트, RestEx |
| **2** | 범용 중급 | T3~T5 화폐, 젬, 스카라브, 주얼, 클러스터 |
| **1** | 고가 | T2 (Exalted급, 고가 프래그먼트), 6링크 |

---

## 5. MinimapIcon shape 매핑

| 아이콘 모양 | 카테고리 |
|------------|----------|
| **Star** | 유니크, T1 최고가 전반 |
| **Circle** | 커런시, Omen, Tattoo, Lifeforce, Vial, Delirium Orb |
| **Triangle** | 디비니 카드, 젬 |
| **Hexagon** | 프래그먼트, 스카라브, 6소켓, Chronicle/Ultimatum |
| **Diamond** | 인플루언스, 크래프팅, Exotic, Fractured, Synthesised |
| **Pentagon** | 퀘스트류, Imbued, Voidstone, Trinket |
| **Kite** | 스플린터 (Breach, Legion, Simulacrum) |
| **Moon** | 아이돌 |
| **Raindrop** | 하이스트 장비, 플라스크 |
| **Square** | 맵 |
| **UpsideDownHouse** | 로그북, 블루프린트 |
| **Cross** | 골드 |

---

## 6. 폰트 크기 체계

| 크기 | 의미 |
|------|------|
| **45** | 최고 우선순위 (T1, T2, 6링크, Exotic T1, 맵 T14+, RestEx) |
| **40** | 표준 (대부분 Show 블록) |
| **35** | 저가치 (Remaining Rares, Chancing, 후반 레벨링 보조) |
| **18** | 숨김 (Hide 블록 — 사실상 비가시) |

---

## 7. StackSize 시스템 상세

### 7-1. 골드

| 임계값 | 폰트 | 텍스트 | 보더 | 배경 | 사운드 | 이펙트 | 아이콘 |
|--------|------|--------|------|------|--------|--------|--------|
| >= 3001 | 40 | 금색 `235 200 110` | 금색 | `20 20 0 255` | 2 300 | Orange | 1 Yellow Cross |
| >= 500 | 40 | 흰색 | 흰색 | `20 20 0 255` | — | Orange Temp | 1 White Cross |
| >= 150 | 40 | 흰색 | 흰색 | `20 20 0 255` | — | — | 2 Grey Cross |
| >= 50 (AL<=68) | 40 | 흰색 | 흰색 | `20 20 0 255` | — | — | 2 Grey Cross |
| 나머지 | 35 | 회색 `180 180 180` | 검정 | `20 20 0 180` | — | — | 2 Grey Cross |

### 7-2. 보급품 커런시 (3/5/10 체계)

**Orb of Transmutation:**
| >= 10 | 파랑 BG `50 70 190` + Sound 2 + White + 2 White Circle |
| >= 5 | 회청 BG `80 120 160` (무음, 아이콘 없음) |
| >= 3 | 회청 BG `80 120 160` (무음, 아이콘 없음) |

**Orb of Augmentation:**
| >= 10 | 회청 BG `80 120 160` + Sound 2 + Grey + 2 Grey Circle |
| >= 5 | 회청 BG (무음) |
| >= 3 | 회청 BG (무음) |

**Portal Scroll:**
| >= 10 | 보더 `60 100 200`, BG `5 8 40` |
| >= 5 | 보더 `60 100 200`, BG `5 8 40` |
| >= 3 | 보더 `30 50 100`, BG `20 20 0` |

**Scroll of Wisdom:**
| >= 10 | 보더 `200 100 60`, BG `30 5 5` |
| >= 5 | 보더 `200 100 60`, BG `30 5 5` |
| >= 3 | 보더 `100 50 30`, BG `20 20 0` |

### 7-3. 일반 커런시 6x 스택

| 티어 | 스택 | 커런시 예시 | 배경 | 사운드 | 이펙트 |
|------|------|-----------|------|--------|--------|
| t1 | >= 6 | Fracturing Shard | 흰 BG | 6 | Red |
| t2 | >= 6 | Ancient Orb, Chaos Orb, Exalted Orb 등 20종 | 딥핑크 | 1 | Red |
| t3 | >= 6 | Abrasive Catalyst, Vaal Orb 등 19종 | 보라 | 2 | Yellow |
| t4 | >= 6 | Blacksmith's Whetstone, Orb of Chance | 코발트 | 2 | White |
| t5 | >= 6 | Armourer's Scrap, Jeweller's Orb 등 4종 | 코발트 | 2 | White |
| t6 | >= 6 | Chromatic Orb, Orb of Alteration | 회청 | 2 | Grey |
| t7 | >= 6 | Alchemy/Alteration/Regal Shard | 회청 | — | — |

### 7-4. 일반 커런시 3x 스택

t1~t7 동일 구조, `StackSize >= 3`으로 조건만 변경. 색상 체계 동일.

### 7-5. Lifeforce (4000/500/250/45/20)

6단계: 흰BG → 딥핑크 → 보라 → 코발트 → 코발트 → 회청. 5단계로 매우 세분화.

### 7-6. Splinter (Breach/Legion)

**고가 스플린터** (Maraketh 등): 80/25/10/5/2 임계값
**저가 스플린터**: 66/25/10/5/2 임계값
**Simulacrum**: 150/60/20/3 임계값 + 낱개 별도

---

## 8. 카테고리별 고유 색상 팔레트

### 커런시 (일반)
- 텍스트/보더: 거의 다 **흰색** `255 255 255`
- 배경색으로 티어 구분 (6단계 체계 그대로)

### 유니크
| 등급 | 텍스트 | 보더 | 배경 |
|------|--------|------|------|
| T1 | 유니크갈 `175 96 37` | 유니크갈 | 흰 `255 255 255` |
| T2 | 흰 | 흰 | 유니크갈 `175 96 37` |
| Multi/중간 | 검정 `0 0 0` | 검정 또는 민트 | 유니크갈 |
| T3/Boss | 유니크갈 | 유니크갈 | 어두운적 `53 13 13` |
| Hideable | 유니크갈 | 유니크갈 | 올리브 `20 20 0` |
| RestEx | 핑크 `255 0 255` | 핑크 | 진보라 `100 0 100` |

### 젬
| 등급 | 텍스트 | 보더 | 배경 |
|------|--------|------|------|
| Exceptional/고가 | 시안 `20 240 240` | 빨강 `240 0 0` | 다크레드 `70 0 20` |
| T1 (Empower 등) | 진파 `0 0 125` | 진파 | 흰 `255 255 255` |
| 중급 (Q20/L21) | 시안 `20 240 240` | 시안 | 다크퍼플 `6 0 60` |
| 일반 (L20/Q13) | 틸시안 `30 190 190` | 틸시안 | 없음 |
| Vaal 젬 | — | 검정 | 다크레드 `55 0 0` |

### 디비니 카드
| 등급 | 텍스트 | 보더 | 배경 |
|------|--------|------|------|
| T1 | 순수파랑 `0 0 255` | 순수파랑 | 흰 |
| T2 | 흰 | 흰 | 딥핑크 `185 0 120` |
| T3 | 흰 | 흰 | 보라 `130 30 190` |
| T4/T4c | 흰 | 흰 | 코발트 `50 70 190` |
| T5c | 청록 `39 141 192` | 청록 | 올리브 `20 20 0` |
| New | 검정 | 검정 | 민트 `40 255 217` |

### 맵
| 등급 | 텍스트 | 배경 | 사운드 |
|------|--------|------|--------|
| T14~16 | 검정 | 연회색 `235 235 235` | 5 |
| T11~13 | 검정 | 회색 `200 200 200` | 5 |
| T6~10 | 흰 | 올리브 `20 20 0` | 4 |
| T1~5 | 흰 | 올리브 `20 20 0` | 4 |
| Blight/Special | 보라 `145 30 220` | 연보라 `235 220 245` | 5 |

### 클러스터 주얼
| 등급 | 텍스트 | 보더 | 배경 |
|------|--------|------|------|
| T1 (Eco) | 보라 `150 0 255` | 오렌지 `240 100 0` | **흰** |
| T2 (Eco) | 흰 | 흰 | **오렌지** `240 100 0` |
| 일반 상위 | 보라 | 오렌지 | 다크퍼플 `34 0 67` |
| 일반 하위 | 보라 | 보라 | 다크퍼플 |

### 하이스트 장비
- 텍스트: 금색 `245 190 0` (고레벨만)
- 보더: 빨강 `255 85 85` (alpha 255 또는 200)
- 배경: 올리브 `20 20 0` 또는 진회색 `35 35 35`
- 아이콘: **Raindrop** 모양

### 주얼 (Abyss/Generic)
| 등급 | 텍스트 | 보더 | 배경 |
|------|--------|------|------|
| 레어 | 골드 `220 220 0` | 오렌지/골드 | 다크옐로 `120 120 0` |
| 매직/노말 | 파랑 `0 75 250` | 파랑/오렌지 | 다크네이비 `0 20 40` |

### 플라스크/팅크처
- 보더: 초록 `50 200 125`
- 배경: 다크틸 `25 100 75`
- 이펙트: Grey / Grey Temp

---

## 9. 특수 패턴

### Continue 데코레이터
- **레어 크기별 보더**: 큰 아이템 → 검정/회색 보더, 작은 아이템 → 밝은 초록/흰 보더
- **고 ilvl 텍스트**: ilvl 83~86 레어 → 금색 텍스트 `245 190 0` 오버라이드
- **타락 상태**: CorruptedMods 0 → 어두운빨강 보더 `120 0 0`, CorruptedMods >= 1 → 밝은빨강 `250 0 0`
- **맵 업그레이드 감지**: AreaLevel 미달 → 빨강 보더 `220 50 0`

### 레벨링 체계
- Life 플라스크: 12단계 (보더 `120 0 0`)
- Mana 플라스크: 12단계 (보더 `0 0 120`)
- Hybrid: 6단계 (보더 `100 0 100`)
- 무기 진행: 15단계 (DropLevel 슬라이딩 윈도우)
- 빌드별 레어 색분: 캐스터=남색, 궁수=초록, 근접2H=붉은갈, 근접1H=노랑, 미니언=보라

### Hale/Healthy/Sanguine 필터
- 대부분 ID 모드 블록에서 `HasExplicitMod =0 "Hale" "Healthy" "Sanguine"` 제외 조건
- 저급 생명력 접미사가 있으면 다른 좋은 모드가 있어도 가치 없음 판정

---

## 10. PathcraftAI Aurora Glow와의 핵심 차이

| 요소 | NeverSink Cobalt | PathcraftAI Aurora Glow |
|------|-----------------|------------------------|
| **가치 구분 방식** | 배경색 (6단계) | 텍스트 색 (카테고리별 그라데이션) |
| **텍스트 색** | 거의 다 흰색 | 카테고리별 고유 색 (Coral, Tangerine, Lavender 등) |
| **보더** | 텍스트와 동일 (또는 상황별 변경) | Edge Glow (텍스트보다 밝은 톤) |
| **배경** | 6단계 고정 (흰→핑크→보라→파랑→회청→올리브) | Dark Tint (카테고리별 어두운 틴트 + 티어별 alpha) |
| **아이콘 color** | 티어별 (Red→Yellow→White→Grey) | 전부 Cyan (시그니처) |
| **아이콘 shape** | 카테고리별 고정 매핑 | PathcraftAI 독자 매핑 |
| **사운드** | 6종 AlertSound (1~6) | Sanavi 관례 유지 (1~3, 6) |
| **폰트 범위** | 18~45 (4단계) | 34~45 (6단계) |
| **안전망** | RestEx (핑크색 최대 강조) | 없음 (TODO) |
| **레벨링 체계** | 30+ 플라스크 진행 + 무기 15단계 | 없음 (TODO) |
| **ID 모드 필터링** | HasExplicitMod 복합 조건 35+ 블록 | 없음 (빌드 기반만) |
| **커런시 스택** | 3x/6x + 보급품 3/5/10 + Lifeforce 5단계 + Splinter 5단계 | 3x/6x + 보급품 3/5/10 (신규 구현) |
| **Decorator/Continue** | 크기별 보더 + ilvl 텍스트 + 타락 표시 | 없음 |

---

## 11. PathcraftAI가 참고할 만한 Cobalt 설계

1. **RestEx 안전망**: 모든 카테고리 끝에 미분류 아이템 캐치올 블록. 필터 업데이트 누락 시 즉시 시각적 경고.
2. **AreaLevel 기반 레벨링 분기**: AreaLevel <= 67에서 보급품 커런시 별도 처리 (SSF에서 특히 유용).
3. **Continue 데코레이터**: 아이템 크기/ilvl/타락 상태를 레이어링으로 시각 표시.
4. **Hale/Healthy/Sanguine 제외**: ID 모드 필터링 시 저급 모드 강제 배제.
5. **신규 카드 전용 스타일**: 디비카 `tnew`에 민트색 배경 (`40 255 217`) — 즉시 구별 가능.
6. **Lifeforce/Splinter 세분화**: 4000/500/250/45/20 등 5단계 StackSize 분기.
7. **6소켓 + 5링크 분리 처리**: Height 3/4 구분까지 해서 인벤 효율 고려.
