# PoE 3.29 (Curse of the Allflame) — SSF 루미너리 봇 "첫 번째 아틀라스 트리" 리서치 & 한국어 재작성

- 작성일: 2026-08-19
- 대상 원문: **Path of Chores**, `[SSF] LUMINARY BOT BUILD GUIDE — LIFE & LIGHT RADIUS STACKING` §5.1 "First Atlas tree: Low tier uniques"
  - 원문 구글 문서(1차 출처): <https://docs.google.com/document/d/1ssZKi-RZm29n53LDat-T5xxuRsJk6uPc>
  - 원문 영상: <https://www.youtube.com/watch?v=VQQPGBpYLmQ> ((SSF) My week 1 Atlas strategy - Luminary support [POE 3.29])
  - 사용자가 제공한 `.docx` = 위 구글 문서의 영문 원본. **본 문서의 모든 재작성은 이 영문 원문을 기준으로 검증**했다.
- 검증 방식: poeplanner 4개 링크 실제 열람(Atlas Tree Version 3.29.0) + 공식 3.29.0 패치노트 + PoEDB(KR/US) + PoE Wiki / Maxroll 교차.
- 표기 규칙: **사실** = 1차 출처 확인 / **추정** = 근거는 있으나 미확정 / **불확실** = 확인 실패.

---

## 0. 한 줄 요약

이 트리는 "돈 버는 트리"가 아니라 **저티어 유니크를 손에 쥐는 트리**다. 아틀라스 키스톤 **Unwavering Vision(변함없는 시각)** 으로 갑충석·조각을 통째로 포기하는 대신 **아틀라스 패시브 20포인트**를 먼저 당겨오고, 그 포인트를 **용병(Trarthus) → 배신(Jun) → 균열(Breach) + 점술 카드** 순서로 몰아넣어, 리그 초반에 빌드가 요구하는 유니크 12종을 SSF에서 직접 떨어뜨린다.

---

## 1. 이 트리의 목적 요약

| 목적 | 실제 수단 | 왜 이 빌드에 필요한가 |
|---|---|---|
| 아틀라스 포인트 조기 확보 | **Unwavering Vision** 키스톤 | "패시브 스킬 포인트 20포인트 제공". 대가는 *성스러운 시험관(Divine Vessel) 외 조각으로 지도 속성 부여 불가* + *지도에서 갑충석 발견 불가*. 리그 1주차엔 어차피 갑충석이 없으니 순수 이득. ([PoEDB KR](https://poedb.tw/kr/Unwavering_Vision)) |
| 수량 대신 **희귀도** | **Meticulous Appraiser** 키스톤 | "지도 아이템 수량 증가 모드가 대신 희귀도에 300% 값으로 적용". 유니크 사냥이 목표라 수량보다 희귀도가 낫다. (3.22 Ancestor 도입, [PoE Wiki](https://www.poewiki.net/wiki/Passive_Skill:Atlas~keystone~quantity~converted~to~rarity)) |
| 메인 딜러(용병) 확보 | 용병 조우 확률 + **House Azadi** + Infamous | Blade Ambusher와 Combatant가 **둘 다 Azadi 가문**이라, Azadi 확률 노드 하나로 두 용병을 동시에 타깃 파밍한다(원문 §2). |
| 크래프팅 해금 + 유니크 | 배신(Jun) 100% | Rin→요새(유니크 지도 = 메타모드 해금), Janus→연구(Cadiro 유니크 상점), Riker→연구(고대 오브), Vagan→운송(**트라투스 갑충석 상자**), Leo→요새(이중 타락 유니크). |
| 유니크·레어 대량 생산 | 균열 → **생명의 결실(Wombgift)** + Genesis Tree | 고대 결실=유니크, 베푸는 결실=레어 장비, 수수께끼 결실=벌레집 두뇌 분비선. |
| 닉타의 등불 확정 루트 | 점술 카드 **빛과 진실** | 유일하게 "확정적으로" 주무기를 주는 경로. |

> **원문에 안 적힌 함정:** Unwavering Vision을 찍은 상태에서 poeplanner 요약창의 *"갑충석이 트라투스/배신/균열 갑충석일 확률 X% 증가"* 라인은 **전부 죽은 스탯**이다. 그 수치는 용병·배신·균열 노트어블에 딸려 오는 부속 옵션일 뿐, 이 트리에서 갑충석은 애초에 드롭되지 않는다. 원문 §5.1의 *"Vagan to Transportation … Might have to wait until you unlock 2nd Atlas tree though. Since this one has Unwavering Vision."* 이 정확히 그 이야기다.

---

## 2. poeplanner 4단계 — 무엇을 찍고 언제 넘어가는가

원문의 진행 순서(영문 그대로):

```
https://poeplanner.com/a/6ZbQ  for Unwavering Vision  ->
https://poeplanner.com/a/6Zb4  for 100% Merc chance   ->
https://poeplanner.com/a/65Ct  for 100% Jun chance    ->
https://poeplanner.com/a/65kJ  for Breach and Div cards wheel
```

아래 수치는 **2026-08-19 기준 poeplanner Atlas Tree Version 3.29.0에서 직접 열어 읽은 합계**다.

### 2-1. 1단계 `6ZbQ` — 36/158 (소형 30 / 노트어블 4 / **키스톤 2**)

| 확보 | 값 |
|---|---|
| 키스톤 | **Meticulous Appraiser**, **Unwavering Vision** |
| 용병 | 지도에 용병 출현 확률 **+60%** |
| 배신 | 지도에 Jun 출현 확률 **+40%** |
| 균열 | 균열 포함 확률 +13% (경유용 소형) |
| 지도 | 지도 발견량 +16%, T1–15 지도 25% 확률로 1티어 상승, 희귀도 +4%, 희귀 몬스터 +10% |

- **핵심**: 36포인트로 키스톤 2개를 먼저 찍는다. Unwavering Vision이 **+20포인트**를 즉시 돌려주므로, 실질 투자는 16포인트에 가깝다.
- **넘어가는 시점**: 20포인트가 들어오는 즉시. 별도 파밍 조건 없음. 여기는 *경유 지점*이지 *운영 트리*가 아니다.

### 2-2. 2단계 `6Zb4` — 52/158 (+16포인트) · 용병 휠 완성

| 새로 열리는 것 | 값 |
|---|---|
| 용병 출현 | +60% → **+90%** |
| 용병 배낭 | **지도에서 발견한 용병은 항상 배낭이 가득 참** |
| 용병 처치 | 가져가지 않은 아이템 **2개 추가 드롭**, **10% 확률로 전 장비 드롭** |
| 용병 장비 | 착용 아이템이 **유니크일 확률 45% 증가** |
| 용병 스킬 | 스킬에 **추가 보조 젬이 붙을 확률 40%** |
| 배신 | Jun +40% → **+64%** |
| 지도 | 지도 발견량 +20% |

- **핵심**: 여기서부터 "용병 장비 강탈"이 실제로 성립한다. *배낭 항상 가득 + 안 가져간 아이템 2개 추가 드롭 + 유니크 확률 45% 증가* 가 세트로 묶여야 저티어 유니크가 쌓인다.
- **넘어가는 시점**: 흰 T1/T2 맵을 돌려 **쓸 만한 Blade Ambusher(또는 Combatant) 1명을 확보**하면 곧바로 3단계로. 이 트리를 오래 굴릴 이유는 없다.
- ⚠ 원문 라벨 "100% Merc chance" ↔ 플래너 합계 **+90%** 불일치 → §6-1 참조.

### 2-3. 3단계 `65Ct` — 77/158 (+25포인트) · 배신 휠 + 용병 가문

| 새로 열리는 것 | 값 |
|---|---|
| 배신 | **"당신의 지도에 Jun이 등장한다"** (확률 표기 소멸 = 확정 등장) |
| 배신 | 단원이 **지도자와 동반할 확률 100% more**, 지도자 **베일 아이템 1개 추가**, 단원 30% 확률 베일 아이템 추가 |
| 배신 | 단원 **처형 시 해당 부서 정보력을 계급 × 2**만큼 획득, 처형 시 **100% 확률로 계급 1 추가 상승** |
| 배신 | 아이템 **물물교환(Bargain) 제안 확률 200% more**, 교환 시 **드롭 아이템 200% more** |
| 배신 | 단원이 지원군을 동반할 확률 15% 증가 |
| 용병 | **Infamous(악명 높은) 용병일 확률 20% 증가**, **House Azadi 출신일 확률 100% 증가** |
| 용병 | 출현 확률 +90% → **+100%** |
| 지도 | 명시 모드 효과 +6% |

- **핵심**: 이 단계의 진짜 값어치는 Jun 100%가 아니라 **"처형 시 계급 +1 확정 + 정보력 2배"** 다. 신디케이트 보드를 원하는 배치(§3-2)로 굳히는 속도가 배 이상 빨라진다.
- **넘어가는 시점**: 보드에서 Rin / Janus / Riker / Vagan / Leo 배치가 자리 잡고 안가(Safehouse)가 한 바퀴 돌기 시작하면 4단계로.

### 2-4. 4단계 `65kJ` — 108/158 (+31포인트) · 균열 + 점술 카드 휠 (= §5.1 최종형)

| 새로 열리는 것 | 값 |
|---|---|
| 균열 | 균열 포함 확률 +13% → **+87%** |
| 균열 | **Breach Hive가 Fortress로 이어질 확률 40% 증가** |
| 균열 | **균열 보스 25% 확률로 복제**, 균열 보스 **50% 확률로 생명의 결실 추가 드롭** |
| 균열 | 팩 사이즈 +10%, 균열 진행 **20% 빠르게**, 마법 몬스터 +11% |
| 결실 | **생명의 결실 발견량 +35%**, **Grasping Coffer가 결실을 담을 확률 50% 증가**, **결실이 고대(Ancient)일 확률 50% 증가**, Hiveblood 수량 +25% |
| 점술 | **지도에서 점술 카드 발견량 +12%** (Altered Prophecy 소형 노드) |
| 지도 | T1–15 티어 상승 확률 25% → **50%**, 희귀 몬스터 +20%, 명시 모드 효과 +12% |

- **핵심**: `Grasping Coffer`(안정 균열 안쪽 사각에 숨은 상자) + `고대 결실 확률 50%`가 이 트리 전체의 유니크 생산 라인이다.
- **다음 단계**: §5.1은 여기서 끝. 원문은 이후 `5.2 두 번째 트리`(<https://poeplanner.com/a/65eL> — King's Heart 점술 카드 → 카옴의 심장, Trauma/Ritual), `5.3 하베스트 대체안`(<https://poeplanner.com/a/65kf>), `5.4 세 번째 트리`(우버 조각 → 거룩한 국왕)로 넘어간다.

> **Altered Prophecy 클러스터는 3.29 신규.** 공식 패치노트: *"Added a new Altered Prophecy cluster to the Atlas Passive Tree. The Notable grants your Tier 14+ Maps 4% chance to drop a Scrying Orb on completion, while the small Passives grant your Maps increased chance to drop Divination Cards."* ([3.29.0 패치노트](https://www.pathofexile.com/forum/view-thread/3985332)) 이 트리는 **소형 노드(점술 카드 확률)만** 가져가고, Scrying Orb용 노트어블은 두 번째 트리에서 찍었다가 오브가 나오면 다시 빼는 식으로 쓴다(원문 §5.2).

---

## 3. 메커니즘별 실제 운영법

### 3-1. 용병 (Mercenaries of Trarthus)

**공식 기준 사실** ([3.29.0 패치노트](https://www.pathofexile.com/forum/view-thread/3985332))

- 3막부터 지역에서 용병이 결투를 걸어온다. 골드를 걸고 **이기면 그가 지닌 아이템 1개를 전리품으로 가져가고**, 용병은 일정 지역 수만큼 아군으로 따라온다. 지면 건 골드를 잃고 용병은 사라진다.
- 캠페인 확정 등장: **The Sceptre of God(3막), The Grand Arena(4막), The Ridge(6막), The Hidden Underbelly(8막)**. 단 *이 지역의 용병은 배낭(Rucksack) 아이템이 없다.*
- **3.29.1 추가**: **10막 Control Blocks에 용병이 항상 등장**하고, 캐릭터 레벨이 지역보다 높아도 스폰이 끊기지 않는다 → 트라투스 갑충석·아틀라스 포인트가 없는 시점에 **시작 용병을 낚는 최적 장소**. ([Maxroll 3.29.1](https://maxroll.gg/poe/news/3-29-1-patch-notes)) 원문이 "GGG가 10막 Control Blocks 용병 패치를 넣어서 더 좋아졌다"고 한 것이 이것.
- **Warrant(영장)**: 맵에서 마음에 드는 게 없으면 영장을 요구할 수 있다. 같은 스킬 세트 + **새 장비 세트**로 미래 맵에 그 용병을 다시 소환. **용병당 1회만** 발급.
- **Luminary(Scion 신규 승천)** 는 **용병을 영구 고용**할 수 있는 유일한 승천. 최대 3명(활성 1 + 은신처 대기 2), 그리고 **영구 고용 용병은 장비를 직접 갈아끼울 수 있다**.
- **Infamous 용병** = 트라투스 4대 가문(**Keita / Cyaxan / Bardiya / Azadi**) 소속. **유니크 1개를 반드시 착용**하며, `Infamous` 전용 모드가 붙은 아이템의 유일한 출처.
- 트라투스 갑충석 4종: 기본 / **of Infamy**(용병이 Infamous가 되고 야생 용병 2명 동반) / **of Renown**(용병의 **모든 장비가 유니크**) / of Surprising Alliances.

**원문이 실제로 시키는 것**

1. **House Azadi 100% 증가**를 찍는 이유 — Blade Ambusher와 Combatant가 **같은 Azadi 가문**이라 노드 하나로 둘 다 타깃 파밍된다.
2. 맵을 돌며 (a) 더 좋은 Blade Ambusher/Combatant를 찾고, (b) **쓸 만한 레어·유니크를 강탈**한다.
3. **Infamous Combatant** → *"근접 무기 공격이 만드는 투사체마다 투사체 속도가 50% more ~ 50% less 사이에서 무작위"* 모드가 붙은 **장갑**을 노림 (Spectral Helix of Trarthus 트랩 조합용).
4. **Infamous Eruptor** → *"전투의 함성이 적을 5초간 재로 뒤덮음"* **투구**를 노림.
5. 이렇게 모은 Infamous 장비는 나중에 **재조합(Recombinator)** 재료로 쓴다.
   → 사용자 원문의 **"장비 강탈 / 재결합"** 은 ① **강탈**(결투 전리품 1개) → ② **재조합(recomb)** 2단계다. **Warrant(재소환)와는 다른 개념**.
6. **Infamy + Renown 갑충석 한 쌍**이 생기면 흰 T1/T2 맵에서 유니크 낚시.
   단, 이 트리는 Unwavering Vision 때문에 갑충석이 안 나오므로 **두 번째 트리 이후**로 미뤄야 한다(원문이 직접 명시).

**용병 선택(원문 §2 요약)**
- **Blade Ambusher** — 맵핑 D- / 보스 S+. 트랩 기반. 초반 생존력·기어링이 압도적으로 쉬움 → **먼저 확보 권장**.
- **Combatant** — 맵핑 B+ / 보스 B+. Frost Blades(클리어 특화) 또는 Wild Strike + Static Strike(단일 대상이 더 나음).
- 둘 다 무기에 **"적중을 회피할 수 없음(Hit Cannot Be Evaded)"** 을 벤치 크래프트할 수 있어, 초반 명중률 문제를 통째로 해결한다.

### 3-2. 배신 (Immortal Syndicate) — 원문 우선순위 그대로

| # | 배치 | 노리는 것 | 검증 |
|---|---|---|---|
| 1 | **Rin Yuushu → 요새(Fortification)** | **유니크 지도 상자.** 유니크 지도를 클리어해야 메타모드 크래프팅이 열린다 | 3.28 기준 Rin 요새 = Unique map chest (repo `data/syndicate_members.json`) |
| 2 | **Janus Perandus → 연구(Research)** | **Cadiro의 유니크 상점.** 광범위한 유니크를 골드로 구매. "Cadiro 이상 현상(Anomaly)만큼 강력하진 않지만 초반 유니크 수급으로는 훌륭" | Janus 연구 = Unique purchase trade (Kalguur 상인) |
| 3 | **Riker Maloney → 연구 / 요새 / 운송 중 택1** | 셋 다 유니크 관련. **연구가 최강 — 고대 오브(Ancient Orb) 30개 슬램** | Riker 연구 = Craft: Ancient Orb, 요새 = Unique chest, 운송 = Unique items drop |
| 4 | **Vagan → 운송(Transportation)** | **트라투스 갑충석 상자** | **공식 3.29.0 패치노트**: *"Vagan's Transportation Safehouse Reward is now a chest containing Trarthan Scarabs."* (3.28까진 인큐베이터 — 3.29 변경점) |
| 5 | **Leo Redmane → 요새** | **이중 타락(double-corrupted) 유니크.** 원하는 유니크가 아니어도 **장갑(피격 시 저주)** 과 **투구(광휘 반경 임플리싯)** 는 반드시 확인 | Leo 요새 = Trapped chest: Corrupted Unique |
| 6 | **Gravicius → 운송** | **점술 카드 한 스택.** 원문 저자는 3.29에서 King's Heart 카드를 풀스택으로 받았다 | Gravicius 운송 = Full stack of Divination Cards |
| 7 | **It That Fled → 운송 또는 개입(Intervention)** | 운송 = **Foulborn 유니크** / 개입 = Eye of Terror 카드(너프됨) + **균열 갑충석** | It That Fled 운송 = Foulborn Unique, 개입 = Breach Scarabs |
| 8 | **Hillock → 아무 부서나** | 점술 카드 **「화룡점정(The Finishing Touch)」 → 풍요의 기폭제(Fertile Catalyst)** | 카드 확정: [PoEDB](https://poedb.tw/us/The_Finishing_Touch) — 보상 "1x Fertile Catalyst", 2장 세트, 드롭 레벨 61. **KR 공식명이 실제로 「화룡점정」** |

> **3.29 중요 변경**: 공식 패치노트에 *"Ultimatum is now the exclusive source of Catalysts"* — 기폭제는 얼티메이텀 전용이 되었고 원정 상자·Tujen 상점·의식 보상에서 제거되었다. 따라서 **점술 카드 경로(화룡점정)와 킹스마치 매퍼가 사실상 남은 우회로**다. 원문 §6.2의 *"Source of other Catalysts are from either (1) Hillock in Betrayal or (2) Kingsmarch mappers"* 가 이 맥락이다.

### 3-2-B. 배신 보드 세팅 실전 절차 — "Rin을 요새로"를 실제로 하는 법

원문은 **결과(어느 멤버를 어느 분과에)** 만 적어놨고 **과정**은 생략했다. 아래가 그 과정이다.

**보드 기본**
- 4개 분과(운송 / 요새 / 연구 / 개입), 총 **14 슬롯**. 중위 17명이므로 항상 3명은 미배치(무계급) 상태다.
- 계급: **무계급(0) → 1 → 2 → 3**. **계급이 있어야만 분과 슬롯을 차지**한다.
- 각 분과의 **리더(최고 계급자)가 안가(Safehouse) 보상을 지배**한다. 나머지 단원은 보조 보상.
- 정보력(Intelligence)이 가득 차면 그 분과의 안가가 열리고, 배정된 멤버 전원이 그리로 이동한다.

**조우 후 4가지 선택지 — 정확한 효과**

| 선택지 | 등장 조건 | 효과 |
|---|---|---|
| **심문 (Interrogate)** | 항상 가능 | 대상 **계급 −1**, 3회 조우 동안 투옥, 해당 분과 **정보력을 3회에 걸쳐 획득**(계급 높을수록 많음). 계급 1이면 **0이 되어 분과에서 이탈** |
| **처형 (Execute)** | **다른 멤버가 목격 중일 때만**(2명 이상 등장) | 대상 **계급 +1**. **무계급(0) 멤버를 처형하면 "가장 최근 조우한 분과"에 배정**된다 |
| **거래 (Bargain)** | 멤버가 혼자이거나 마지막 1명일 때 | 랜덤: 보상 드롭 / 즉시 정보력 / 계급 상승 / **분과 교체** / 신디케이트 탈퇴 / 라이벌 관계 해제 |
| **배신 (Betray)** | 동맹(Trusted) 관계인 두 멤버 사이 | 적대 관계로 전환. 드물게 멤버 제거 |

> 불사 신디케이트는 말 그대로 *불사*라서, **처형이 곧 승진**이다. 멤버를 보드에서 빼는 수단은 처형이 아니라 **심문(계급 0으로 떨구기)** 또는 **거래(탈퇴)** 다.

**3-스텝 레시피 — 특정 멤버를 특정 분과에 꽂기**

1. **비운다** — 목표 멤버가 엉뚱한 분과에 있으면 **심문을 반복**해 계급을 0으로 떨어뜨린다 → 분과에서 이탈, 무계급 풀로 간다.
2. **넣는다** — **목표 분과의 조우**에서 그 무계급 멤버가 등장할 때 **처형**한다 → 계급 1 + **그 분과에 배정**.
   - 기준이 "**가장 최근 조우한 분과**"이므로, **요새 조우에서 처형해야 요새로 간다.** 조우 종류를 확인하고 실행할 것.
   - 처형은 목격자가 필요하므로 **2명 이상 등장하는 조우**를 노린다.
3. **키운다** — 같은 분과 조우에서 그 멤버를 계속 **처형** → 계급 3까지. 리더가 되면 안가 보상이 그 멤버 것으로 고정된다.

**3단계 트리(`65Ct`)가 이 절차를 얼마나 줄여주나 — 이게 그 트리의 진짜 값어치다**

| 노드 | 절차상 효과 |
|---|---|
| *처형 시 100% 확률로 계급 1 추가 상승* | 처형 1회 = **계급 +2**. 무계급 → 계급 3까지 **처형 2회**면 끝 |
| *처형 시 해당 부서 정보력을 계급 × 2 만큼 획득* | 계급을 올리는 행동이 곧 안가를 채우는 행동이 된다 |
| *지도자와 동반할 확률 100% more* | 리더가 자주 등장 → 계급 관리 쉬움 + **목격자 조건이 저절로 충족** |
| *거래 제안 200% more / 거래 시 아이템 200% more* | 혼자 나온 멤버를 거래로 굴려도 손해가 아니다 |
| *지도에 Jun 확정 등장* | 조우 횟수 자체가 최대 |

**이 빌드용 배치 순서 — 원문 우선순위를 보드 작업으로 번역하면**

한 분과의 보상은 **리더 1명이 지배**하므로, 8명을 동시에 다 세팅할 수는 없다. **리더 슬롯을 순차 교체하며 안가를 한 번씩 터는 방식**이 정석이다.

| 순번 | 작업 | 목적 |
|---|---|---|
| 1 | **요새 리더 = Rin** (계급 3) | 유니크 지도 → 메타모드 크래프팅 해금 |
| 2 | **연구 리더 = Janus** (계급 3) | Cadiro 유니크 상점 — 초반 유니크 수급 |
| 3 | Janus 안가를 턴 뒤 **연구 리더를 Riker로 교체** | 고대 오브 30개 슬램 |
| 4 | **요새 리더를 Leo로 교체** | 이중 타락 유니크 (장갑=피격 시 저주 / 투구=광휘 반경 임플리싯 반드시 확인) |
| 5 | **운송 리더 = Gravicius** | 점술 카드 한 스택 (King's Heart 노림) |
| 6 | **운송 리더를 It That Fled로 교체** | Foulborn 유니크 (Foulborn 솔라리스 흉갑 / 히네코라의 통찰력) |
| 7 | **운송 리더를 Vagan으로 교체** | 트라투스 갑충석 상자 — **단, Unwavering Vision을 뺀 뒤**(= 두 번째 트리 이후) |
| 8 | **Hillock은 아무 분과에나 계급만 올려둠** | 「화룡점정」 카드 → 풍요의 기폭제 |

**주의**
- **라이벌(적대) 관계**인 멤버끼리는 같은 분과에 잘 붙지 않는다. 붙이고 싶은 둘은 **거래의 "라이벌 관계 해제"** 결과를 노리거나 동맹을 유도한다.
- 심문의 정보력은 **3회 조우에 걸쳐** 들어온다. **안가 개방 직전에는 처형(즉시 정보력)** 이 낫다.
- repo 참고: `data/syndicate_layouts.json` 의 `meta_2x2_5`(2명 분과 ×2 + 5명 분과 ×2)는 **범용 커런시 메타**다. 이 빌드는 "리더 순차 교체형"이라 그 프리셋을 그대로 쓰면 맞지 않는다.

### 3-3. 균열 (Breach) — Genesis Tree / 생명의 결실

**용어 정리 (KR 공식명 = PoEDB KR 확인)**

| 영문 | 한국어 공식명 | 정체 |
|---|---|---|
| Ancient Wombgift | **고대 생명의 결실** | Genesis Tree의 **유니크 자궁(womb)** 에 넣어 유니크로 성장 (드롭 레벨 21) |
| Provisioning Wombgift | **베푸는 생명의 결실** | **장비(레어) 자궁** 용 |
| Mysterious Wombgift | **수수께끼의 생명의 결실** | **기타 자궁** 용 — 겹쳐진 덱, 고레벨 젬, 특정 점술 카드, 가디언/정복자/합성 지도, 갑충석, **벌레집 두뇌 분비선** (드롭 레벨 68) |
| Lavish Wombgift | **화려한 생명의 결실** | **화폐 자궁** 용 (드롭 레벨 13) |
| Hivebrain Gland | **벌레집 두뇌 분비선** | 균열 **쌍둥이 보스** 소환 |
| Synaptic Ring | **시냅스 반지** | 균열 반지의 한 종류(Esh 계열 모드) |
| Trarthan Scarab | **트라투스 갑충석** | |

**원문이 실제로 시키는 것**

- **모든 균열 패시브를 열기 전까지는 "Hive 전용" 또는 "Unstable Breach 전용"으로 특화하지 말 것.**
- **불안정 균열(Unstable Breach)** 을 돌려 보스 **Vruun**을 잡는다 → **레어 균열 반지 확정 드롭**.
- **고대 결실**을 몰아서 유니크 뽑기.
- **베푸는 결실**을 몰아서 레어 장비 뽑기(§8.2 투구 크래프팅 재료).
- **수수께끼 결실**에 **"드물게 발견되는 아이템(INFREQUENTLY found items)"** 옵션을 걸어 **벌레집 두뇌 분비선**을 노림 → 쌍둥이 보스.
- **화려한 결실은 벤더 5개 → 1개**로 교환해 다른 종류로 돌린다. (결실 5개 → 랜덤 결실 1개 벤더 레시피, 3.27.0c 도입. **추정: 3.29 유지** — 2차 출처만 확인)
- (선택) **레어 균열 반지 60개 → 「탐욕스러운 사슬옷(Grasping Mail)」 벤더 레시피.** 원문 §6.15는 **"시냅스 반지 60개"** 로 채워야 Esh 모드가 100% 보장된다고 못 박는다. 다른 균열 반지를 섞으면 최종 결과물의 모드 풀이 오염된다. (목표 모드 *"치명타 확률이 초과 번개 저항만큼 증가"* 는 60개를 다 넣어도 적중률 10% 수준 — 원문도 "Ben이 아니면 권하지 않는다"고 적었다.)

**3.29 균열 너프(공식)** — 원문이 "(nerfed) Breach tree"라 부르는 근거:
- Genesis Tree **장비 패시브 최대 16포인트**(이전 20), 노트어블 **300%**(이전 500%), 소형 "추가 장비 출산 확률" **25%**(이전 50%).
- 동시 개방 가능한 불안정 균열 **최대 2개**(이전 3), 몬스터 팩 15% 감소.
- **"고대 생명의 결실은 다른 결실에 비해 상대적으로 더 희귀해졌다."**

### 3-4. 점술 카드 — 「빛과 진실(Light and Truth)」

- **보상: 랜덤 유니크 수정 셉터(Crystal Sceptre), 2장 세트.** **닉타의 등불(Nycta's Lantern)** 이 후보에 포함된다. ([PoE Wiki](https://pathofexile.fandom.com/wiki/Light_and_Truth), [PoEDB KR](https://poedb.tw/kr/Light_and_Truth))
- 드롭처: Upper Sceptre of God(3막), **Palace 지도**, Residence, Villa.
- 원문 권장 파밍처: **Palace(자연 티어 9)** 또는 **Ivory Temple(자연 티어 13 — 레이아웃이 훨씬 낫다)**.
- **필터 조치**: 원문 *"add card into a higher tier in your filter"* → **「빛과 진실」 카드를 필터 상위 티어로 승격**.
  ✅ **이미 반영되어 있다** — §4-B 참조.
- 트리 근거: 4단계의 **"지도에서 점술 카드 발견량 +12%"**(Altered Prophecy 소형 노드).

---

## 4. 타깃 유니크 표 (원문 §5.1 목록, 순서 보존)

착용자: **[나]** = 루미너리 본체 / **[AG]** = Animate Guardian(소환 수호자) / **[용병]** = Blade Ambusher 등

| # | 영문명 | 한국어 공식명 | 기반 아이템 | 착용 | 용도 | 획득 경로 | 필터 상향 |
|---|---|---|---|---|---|---|---|
| 1 | **Nycta's Lantern** | 닉타의 등불 | 수정 셉터 | [나] | 주무기(광휘 반경·화염). **요구 레벨 41** | ① **레벨 41 골드 셉터 도박** ② **「빛과 진실」 카드**(Palace T9 / Ivory Temple T13) ③ Crystal Sceptre 기회의 오브 | **필수** — 카드 상향 + `Crystal Sceptre (ilvl 1+)` 찬스 베이스 노출 |
| 2 | **Lori's Lantern** | 로리의 등불 | 분광 반지 | [나] | 반지(광휘 반경). 2개까지 착용 | 균열/용병 드롭, **`Prismatic Ring (ilvl 1+)` 기회의 오브** | 찬스 베이스 노출 |
| 3 | **Voideye** (원문 표기 "Void Eye") | 공허의 눈 | 무보석 반지 | [나] | **소켓 젬 +5 레벨** → 화염 연결(Flame Link) +5 | 저티어 유니크 드롭 | 권장 |
| 4 | **Kaom's Binding** | 카옴의 속박 | 육중한 허리띠 | [나] | 생명력 허리띠 | 저티어 유니크 드롭 | 권장 |
| 5 | **Ceinture of Benevolence** | 관대함의 띠 | 헝겊 허리띠 | [나] | 카옴의 속박 대안(§6.17 바알 오브 타락 대상) | 저티어 유니크 드롭 | **권장** — 원문: "Cloth Belt 유니크 비주얼을 필터에서 잘 보이게" |
| 6 | **Solaris Lorica** / **Foulborn 판본** | 솔라리스 흉갑 | 구리 판금 갑옷 | [나] | 초·중반 갑옷. **Foulborn 판본 = 광휘 반경 25% + 원소 피해 25%를 카오스로 받음** | 드롭 / **`Copper Plate (ilvl 1+)` 기회의 오브** / Foulborn은 It That Fled → 운송 | 찬스 베이스 노출 |
| 7 | **Ignomon** | *(공식 KR명 미확인)* | 금 목걸이 | [나] | 광휘 반경 + **적 실명** → 초반 용병 명중률 부족 보완 | 저티어 유니크 드롭 | 권장 |
| 8 | **Hinekora's Sight (Foulborn)** | 히네코라의 통찰력 | 오닉스 목걸이 | [나] | **Foulborn 판본에서 광휘 반경 최대 50%** | Foulborn = It That Fled → 운송 | 권장 |
| 9 | **Dying Breath** | 죽어가는 숨결 | 철제 지팡이 | **[AG]** | 오라/저주 효과를 아군에 증폭 | 저티어 유니크 드롭 | 권장 |
| 10 | **Leer Cast** | 음흉한 시선 | 축제용 가면 | **[AG]** | 주변 아군 피해 증가 | 저티어 유니크 드롭 | 권장 |
| 11 | **Belly of the Beast** | 짐승의 소굴 | 전신 아룡 비늘 갑옷 | **[AG]** (초반엔 [나]도 가능) | AG 생존력 | 저티어 유니크 드롭 | 권장 |
| 12 | **Wake of Destruction** | **파괴의 경야** | 망사 장화 | **[AG]** | 바닥 번개 피해 | 저티어 유니크 드롭 | 권장 |
| 13 | **Southbound** | 남행 | 병사 장갑 | **[AG]** | 냉기/빙결 유틸 | 저티어 유니크 드롭 | 권장 |
| 14 | **Vulconus** | 불커누스 | 악마 단검 | **[용병 — Blade Ambusher]** | 중반 주무기 2자루(§4.2) | **글로벌 드롭 — T3 유니크 무기** | 권장 |
| 15 | **Crown of Eyes** | 눈알 왕관 | 자만의 관 | **[AG / AGoS]** | 주문 피해 증가가 공격 피해에 적용 | 저티어 유니크 드롭 | 권장 |

**「The Magnate(거물, 징 박힌 허리띠)」는 원문 목록에 없다.** §5.1의 타깃 12개 어디에도, 문서 전문 검색에서도 등장하지 않는다. 사용자 목록의 해당 항목은 원문 *"3. Kaom's binding & Ceinture of Benevolence"* 가 옮겨지는 과정에서 섞인 것으로 **추정**된다.

**이 트리 범위 밖(후속 트리)의 유니크**: 카옴의 심장(King's Heart 카드), 원한의 품(Incarnation of Fear 8%), 조련, 거룩한 국왕(우버 Dread), 덧없는 자의 의복(Venarius 9%), 래스피스 구체·무덤의 속박(고대 오브 변환), 실용주의·Untouched Soul(Nameless Ritual), Arkhon's Tools(Incarnation of Neglect 38%) 등.

**필터에 노출해야 할 베이스(원문 §7 그대로)**
- 찬스용: `Crystal Sceptre (ilvl 1+)`, `Prismatic Ring (ilvl 1+)`, `Copper Plate (ilvl 1+)`
- 본체 크래프팅: Giantslayer Helmet(i81+), Leviathan Gauntlets(i81+), Leviathan Greaves(i81+/86), Vermillion Ring(i80+), Ezomyte Tower Shield(i81+), Stygian Vise(i68+), Elder 영향 장갑
- 용병 크래프팅: Jewelled Foil(i77+), Gutting Knife(i73+), Majestic Pelt / Syndicate's Garb / Velour Gloves / Velour Boots(i84+, **회피 계열만** — 두 용병이 공유하기 위함)

### 4-B. 필터 반영 현황 (2026-08-19 확인)

**정본 위치 주의**: 3.29 필터 작업은 이 레포(`D:/Pathcraft-AI`, master) 에만 있다. `C:/Users/User/orca/workspaces/Pathcraft-AI/*` 의 리서치 워크트리들은 **2026-04 브랜치(ed23e75)** 에 묶여 있어 3.29 필터·빌드 타깃이 아예 없다. 그쪽 `data/divcard_mapping.json`(16엔트리, 4월판) 등을 근거로 "필터에 없다"고 판단하면 오진이다 — 본 조사에서 실제로 그 오진이 한 번 발생했다.

| 항목 | 상태 | 근거 |
|---|---|---|
| 빌드 타깃 정의 | ✅ 존재 | `D:/Pathcraft-AI/data/filter_build_targets/poe1_luminary_bot_ssf_3_29.json` — `build_id: poe1_luminary_bot_ssf_3_29_path_of_chores`, source에 교정 번역 docx 경로 명시 |
| **Light and Truth** (→ 닉타의 등불, §5.1) | ✅ build_target | 위 JSON + 설치본 필터 9267행 전용 규칙 |
| The King's Heart (→ 카옴의 심장, §5.2) | ✅ build_target | 동일 |
| The Spark and the Flame / Pride Before the Fall (§6.2) | ✅ build_target | 동일 |
| **The Finishing Touch** (→ 풍요의 기폭제) | ✅ keep | "가이드가 명시적으로 걸러내지 말라고 함" — 일반 카드 목록(1971행)에도 포함 |
| §7 필터 베이스 13종 | ✅ 전부 존재 | 수정 셉터 / 분광 반지 / 구리 판금 갑옷 / Jewelled Foil / Gutting Knife / Giantslayer / Leviathan / Vermillion Ring / Ezomyte Tower Shield / Stygian Vise / Syndicate's Garb / Majestic Pelt / Velour |
| 배포본 | ✅ 설치됨 | `Documents/My Games/Path of Exile/Luminary_Bot_SSF_3.29.filter` (2026-08-19, 596KB). 참고 합성본 `Vortican_Luminary_SSF_3.29.filter`(08-11) |
| 감사·인계 문서 | ✅ 존재 | `D:/Pathcraft-AI/Docs/2026-08-18_LUMINARY_BOT_SSF_FULL_FILTER_AUDIT.md` — 인계 규칙 6조, 레이어 고정 순서 5단계, 입력 파일 SHA-256, 3곳 배포 절차 |

**필터 구조(감사 문서 요약)**: NeverSink 완성본 + 소수 오버라이드가 **아니다**. `SSF.txt`(Wrecker 계열)가 표시/숨김·AreaLevel 진행의 정본이고, `death oath.txt`/`allie.txt`에서 뽑은 NeverSink 규칙은 `Continue` 시각 레이어로만 얹힌다. 고정 순서는 ①NeverSink 광범위 시각 → ②일반 장비 fallback/Crimson 정규화 → ③Allie 고가치 강조 → ④**Luminary 필수품·링크·T0 terminal Show** → ⑤Wrecker SSF 진행 정본.

**혼동 주의 — `data/divcard_mapping.json` 은 필터 소스가 아니다.** master의 `divcard_mapping.json`(16엔트리)에도 Nycta's Lantern / Light and Truth는 없다. 그 파일은 빌드 가이드·추천 쪽 매핑이고, **필터가 읽는 건 `data/filter_build_targets/<build>.json`** 이다(해당 파일 `_field_notes.swapping_builds`: *"Point the generator at a different file of this shape. Nothing else in the ladder changes."*). 이 둘을 헷갈리면 "필터에 카드가 없다"는 오진이 나온다.

**따라서 본 리서치로 인한 필터 추가 작업은 없다.** §3-3(균열 운영)에서 확인된 소비 아이템의 필터 커버리지를 실측한 결과는 아래와 같다.

| 아이템 | 설치본 `Luminary_Bot_SSF_3.29.filter` 내 언급 | 판정 |
|---|---|---|
| 고대 / 베푸는 / 수수께끼 / 화려한 생명의 결실 | 각 2건 | ✅ |
| 벌레집 두뇌 분비선 (Hivebrain Gland) | 4건 | ✅ |
| 시냅스 반지 (Synaptic Ring) | 6건 | ✅ |
| 트라투스 갑충석 (Trarthan Scarab) | 4건 | ✅ |
| Warrant(영장) / Breach Ring | 3건 / 1건 | ✅ |
| Hiveblood | 0건 | ✅ **정상 — 아이템이 아님** |
| Growing Wombgift | 0건 | ✅ **정상 — 넣으면 필터 로드 실패** |

**`Hiveblood`는 필터 대상이 아니다 (GGPK 정본 확인).** `data/game_data/BaseItemTypes.json`(3.29.3.1.4 재추출본) 5,461행에 `Hiveblood`라는 아이템은 **존재하지 않는다.** Chayula/Brequel 계열 BaseItemTypes 49건을 전수 조회해도 없다. 이 이름은 오직 아틀라스 패시브·맵 모드의 **수량 스탯 이름**으로만 존재한다 — `PassiveSkills.Name = "Breach Hiveblood Quantity"`, `ModFamily.Id = "MapBreachHivebloodQuantity"`, `Mods.Id = "EagonMissionMapBreachHivebloodQuantity"`. 따라서 `BaseType == "Hiveblood"` 규칙은 애초에 매칭될 수 없다. **조치 불필요.**

**`Growing Wombgift`는 계속 제외해야 한다 (동일 확인).** 3.29 GGPK에서도 판별자가 그대로다.

| 아이템 | InheritsFrom | TagsKeys | ItemClass | 필터 유효 |
|---|---|---|---|---|
| 베푸는/화려한/고대/수수께끼 생명의 결실 | `Metadata/Items/Chayula/AbstractChayulaFruit` | `[1339]` | 96 | ✅ |
| **Growing Wombgift** | **`Metadata/Items/Item`** (루트) | **`[]`** (비어 있음) | 98 | ❌ 미출시 스텁 |

루트 상속 + 태그 없음 = 미출시 스텁이라는 기존 판별 규칙이 3.29에서도 유효하다. 필터에 넣으면 **로드 실패**한다. (참고: 이 아이템의 메타데이터는 `Metadata/Items/Chayula/GraftItemFruit` 로, Uulgraft/Xophgraft/Eshgraft/Tulgraft 계열 **Graft 아이템 20종이 BaseItemTypes에 이미 존재**한다. 즉 Graft 시스템은 데이터상 존재하지만 Growing Wombgift 자체는 아직 비활성이다 — 향후 패치에서 활성화되면 재검토 대상.)

---

## 5. 원문 오역 교정표

| 기계번역 표현 | 실제 원문 | 정확한 의미 | 근거 |
|---|---|---|---|
| **41레벨 도박** | *"A very important checkpoint is at level 41 … You will use it to gamba for a Sceptre, looking for Nycta's Lantern."* | **레벨 41 셉터 도박.** 5막 시점, Chart/Voyage로 번 **골드로 상점 도박**을 돌려 셉터를 뽑고 **닉타의 등불**을 노린다. 41인 이유는 **닉타의 등불(수정 셉터) 요구 레벨이 41**이라서 | [PoEDB KR — 닉타의 등불, 요구 레벨 41](https://poedb.tw/kr/Nyctas_Lantern) |
| **June chance 100%** | *"for 100% Jun chance"* | **Jun(준 오르토이) 100%.** 배신 마스터 Jun이지 6월(June)이 아니다. 플래너 3단계 요약이 **"Your Maps contain Jun"**(확률 표기 소멸 = 확정) | poeplanner `65Ct` 실측 |
| **30개 충돌 연구** | *"Riker to Research OR Forti OR Transport … Strongest one is Research for 30 Ancient Orbs slamming."* | **Riker를 연구(Research) 부서에 → 고대 오브 30개 슬램.** "충돌" = **slam**(투입/슬램)의 오역, "연구" = Betrayal 부서 **Research**(정역) | repo `data/syndicate_members.json` — Riker/Research = Craft: Ancient Orb |
| **화룡점정** | *"Hillock to anywhere: 'The Finishing Touch' for Fertile Catalysts."* | **오역이 아니다.** 「화룡점정」은 점술 카드 **The Finishing Touch의 공식 한국어명**. 보상 = **풍요의 기폭제 1개**, 2장 세트, 드롭 레벨 61 | [PoEDB KR](https://poedb.tw/kr/The_Finishing_Touch) / [US](https://poedb.tw/us/The_Finishing_Touch) |
| **고대 / 베푸는 / 수수께끼의 생명의 결실** | Ancient / Provisioning / Mysterious **Wombgift** | **오역이 아니다.** 셋 다 **공식 한국어명**. "Fruit of Life 계열"이라는 추정은 틀렸고, 정확히는 **Wombgift = 생명의 결실** | [고대](https://poedb.tw/kr/Ancient_Wombgift) / [베푸는](https://poedb.tw/kr/Provisioning_Wombgift) / [수수께끼](https://poedb.tw/kr/Mysterious_Wombgift) |
| **Ravish 5:1** | *"Vendor Lavish 5 to 1."* | **Lavish**(화려한 생명의 결실)의 오독. **화려한 결실 5개를 상인에게 팔아 랜덤 결실 1개로 교환**한다는 뜻. 남는 화폐용 결실을 유니크용(고대)·기타용(수수께끼)으로 돌리는 정리 작업 | 결실 5→1 벤더 레시피(3.27.0c 도입) |
| **파괴의 경야 = Dusktoe ?** | *"9. (AG) Wake of Destruction"* | **Dusktoe 아님.** 「파괴의 경야」 = **Wake of Destruction(망사 장화)**. Dusktoe의 한국어명은 **「황혼의 끝자락」(철제 비늘 장화)** 로 완전히 다른 아이템 | [파괴의 경야](https://poedb.tw/kr/Wake_of_Destruction) / [황혼의 끝자락](https://poedb.tw/kr/Dusktoe) |
| **Eye of the Void** | *"Lori's Lantern & Void Eye"* / §4.1 *"1x Voideye for +5 Flame Link level"* | 정확한 아이템명은 **Voideye(공허의 눈, 무보석 반지)**. 원문 본문의 "Void Eye"는 저자의 띄어쓰기 실수 | [PoEDB KR 공허의 눈](https://poedb.tw/kr/Voideye) |
| **장비 강탈 / 재결합** | *"Steal any usable rares/uniques"* + *"for later recomb"* | 2단계다. ① **강탈** = 결투 승리 시 전리품 1개 획득 ② **재조합(Recombinator)** = 모아둔 Infamous 장비를 재조합 재료로 사용. **Warrant(재소환)와는 별개** | 3.29.0 패치노트 + 원문 §5.1 |
| **Mercenary chance 100%** (2단계) | *"for 100% Merc chance"* | 플래너 실측은 **+90%** (100%는 3단계에서 도달). §6-1 참조 | poeplanner `6Zb4` 실측 |
| **The Magnate** | (원문에 없음) | 원문 타깃 12종에 없음. 해당 항목은 **Kaom's Binding & Ceinture of Benevolence** | 원문 전문 검색 |

---

## 6. 불확실 / 패치 확인이 필요한 사항

1. **2단계 "100% 용병 확률" ↔ 플래너 +90% 불일치 — 불확실.**
   `6Zb4` 합계는 *"Your Maps have +90% chance to be inhabited by a Mercenary"* 이고, **+100%** 는 `65Ct`에서 도달한다.
   - **추정 A**: 지도에 기본 용병 출현 확률 10%가 있어 90 + 10 = 100%. (공식 base 값 확인 실패)
   - **추정 B**: 저자가 라벨을 반올림했거나, 링크 갱신 과정에서 단계 라벨이 한 칸 어긋났다.
   - **검증 방법**: 인게임에서 아틀라스 미배분 상태의 용병 출현 확률 확인, 또는 GGG 아틀라스 패시브 노드 데이터의 base 값 확인.

2. **결실 5→1 벤더 레시피의 3.29 현행 여부 — 확인 필요.** 3.27.0c 도입은 2차 출처에서만 확인했고, 공식 3.29 패치노트에서 제거·변경 언급은 찾지 못했다(= 유지 추정).

3. **「화룡점정」 카드가 실제로 Hillock 배신 보상에서 나오는지 — 확인 필요.** 카드 자체와 보상(풍요의 기폭제)은 확정. 다만 "Hillock을 아무 부서에나 배치하면 이 카드가 나온다"는 **저자의 실플레이 관찰**이며, 공식 문서에서 Hillock ↔ 이 카드의 연결을 확인하지 못했다. 3.29에서 **기폭제가 얼티메이텀 전용**이 된 만큼 현행 패치에서 재확인이 필요하다.

4. **공식 한국어명 미확인**: `Ignomon`, `Untouched Soul`, `Arkhon's Tools`, `Grey Wind`, `Vruun`, `Grasping Coffer`, `Hiveblood`, `Foulborn`. PoEDB KR에 해당 슬러그 페이지가 없어(404) 공식 번역을 확보하지 못했다. 본문에서는 영문을 정본으로 두었다.

5. **poeplanner 스냅샷 시점.** poeplanner v2.10.8.3 / Atlas Tree Version 3.29.0 기준. 3.29.1 이후 아틀라스 패시브 수치 변경(예: Swelling Ranks 20%→10%, Evolving Hives 25%→15%)이 플래너에 반영됐는지는 노드별로 대조하지 않았다. **인게임과 1~2% 차이가 날 수 있다.**

6. **Unwavering Vision 트레이드오프 재평가 시점.** 원문 §5.2가 *"Drop Abyss or Breach if you don't like to have Unwavering Vision blocking your scarabs drop"* 라고 적은 그대로, 갑충석 경제가 돌기 시작하면(특히 Vagan 운송의 트라투스 갑충석 상자를 쓰려면) **UV를 빼는 판단**이 필요하다. 첫 트리에서는 유지가 맞다.

7. **배신 보드 세부 수치의 출처 등급 — 주의.** §3-2-B의 4가지 선택지 효과(심문 −1/투옥 3회, 처형 +1/최근 조우 분과 배정, 목격자 조건)는 **독립 2차 출처 2곳이 일치**하고 GGG 아틀라스 노드 문구(*"Members Executed … gain an additional Rank"*, *"Executing … grants intelligence … equal to 2 times their Rank"*)와도 정합한다. 다만 **보드 14 슬롯**과 분과별 슬롯 배분은 repo `data/syndicate_layouts.json`(3.28 기준)에서 온 값으로 **3.29 공식 재확인은 하지 않았다.** 배신(Betray) 옵션의 세부 결과도 2차 출처 수준이다.

8. **본 문서 범위.** §5.1(첫 아틀라스 트리)만 검증했다. §5.2 / §5.3 / §5.4 트리와 §6 럭셔리 업그레이드, §8 크래프팅은 원문 요약 수준으로만 참조했고 노드 단위 실측은 하지 않았다.

---

## 7. 출처

- 원문(1차): [Path of Chores — [SSF] Luminary Bot Build Guide](https://docs.google.com/document/d/1ssZKi-RZm29n53LDat-T5xxuRsJk6uPc) · [주차별 아틀라스 영상](https://www.youtube.com/watch?v=VQQPGBpYLmQ)
- 아틀라스 트리 실측: [6ZbQ](https://poeplanner.com/a/6ZbQ) · [6Zb4](https://poeplanner.com/a/6Zb4) · [65Ct](https://poeplanner.com/a/65Ct) · [65kJ](https://poeplanner.com/a/65kJ)
- 공식: [Content Update 3.29.0 — Curse of the Allflame 패치노트](https://www.pathofexile.com/forum/view-thread/3985332)
- Maxroll: [3.29.1 Patch Notes](https://maxroll.gg/poe/news/3-29-1-patch-notes) · [Mercenaries of Trarthus Guide](https://maxroll.gg/poe/resources/mercenaries-of-trarthus-guide)
- PoEDB(KR/US): [변함없는 시각](https://poedb.tw/kr/Unwavering_Vision) · [화룡점정](https://poedb.tw/kr/The_Finishing_Touch) · [빛과 진실](https://poedb.tw/kr/Light_and_Truth) · [고대 생명의 결실](https://poedb.tw/us/Ancient_Wombgift) · [닉타의 등불](https://poedb.tw/kr/Nyctas_Lantern) · [파괴의 경야](https://poedb.tw/kr/Wake_of_Destruction) · [공허의 눈](https://poedb.tw/kr/Voideye)
- [PoE Wiki — Light and Truth](https://pathofexile.fandom.com/wiki/Light_and_Truth) · [Meticulous Appraiser 키스톤](https://www.poewiki.net/wiki/Passive_Skill:Atlas~keystone~quantity~converted~to~rarity)
- 배신 보드 메커니즘: [PoE Vault — Immortal Syndicate Guide](https://www.poe-vault.com/guides/immortal-syndicate-guide) · [PoE Wiki — Immortal Syndicate](https://pathofexile.fandom.com/wiki/Immortal_Syndicate) · repo `data/syndicate_layouts.json`
- 리포지토리 대조: `data/syndicate_members.json`(3.28 Mirage 기준 신디케이트 보상표), `data/merged_translations.json`(유니크 ↔ 기반 아이템 대조)
