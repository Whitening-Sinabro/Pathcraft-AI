# MAGEFIST Chaos Herald of Thunder Pathfinder 3.29 — Softcore Trade

## 결론

이 빌드는 `Ranger / Pathfinder`로 시작해 캠페인과 초기 맵을 `Poisonous Concoction of Bouncing`으로 통과한 뒤, 자본과 전환 부품을 한꺼번에 준비하고 `Herald of Thunder` 카오스 독 오토봄버로 바꾸는 소프트코어 거래 빌드다.

처음부터 천둥의 전령으로 키우는 빌드가 아니다. 제작자는 영상 당시 전환 전에 최소 15 Divine을 모으라고 했지만, 현재 `Voltaxic Rift` 최소 전환의 온라인 즉구가는 그보다 훨씬 낮다. 공개 Part 1 PoB에는 이미 `Progenesis`, `The Tides of Time`, Foulborn 변형 주얼과 고급 희귀 장비가 들어 있으므로 최소 전환과 같은 가격 단계로 보면 안 된다.

2026-08-22 18:21(+07) Allflame 공식 거래소에서 `online`과 `Buyout or Fixed Price`만 적용하고, 가격과 귓속말 버튼이 모두 있는 매물만 셌다. 핵심 5종은 `Voltaxic Rift 35c + 즉시 사용 가능한 비타락 6링크 Dendrobate 30c + Storm Secret 2개 2c + Calamitous Visions 1c + Empower 3레벨 12c = 80c`였다. 캠페인 06 트리를 전부 찍은 최악의 경우도 퀘스트 환불 20포인트 뒤 후회의 오브가 최대 47개라, 캠페인 레어를 재사용하면 핵심과 재분배를 합쳐 약 `127c`, 즉 당시 약 1 Divine 미만이다. 매물은 실시간으로 바뀌므로 링크에서 다시 확인한다.

## 설치한 PoB

세 파일을 `3.29-CotA` 빌드 폴더에 설치했다.

- `Magefist_Chaos_HoT_Pathfinder_3.29_00_Campaign_PConc.xml`: 캠페인부터 초반 맵핑까지 6단계
- `Magefist_Chaos_HoT_Pathfinder_3.29_01_Minimum_Transition_Voltaxic.xml`: 레벨 80 최소 Voltaxic 전환
- `Magefist_Chaos_HoT_Pathfinder_3.29.xml`: MAGEFIST 공개 Part 1/2 HoT 단계

캠페인 파일은 MAGEFIST가 공개한 PoB가 아니다. 영상과 같은 Pathfinder PConc 진행을 채우기 위해 [MrRonit의 3.29 PConc Starter](https://pobb.in/o39wtJ3fp-zj)에서 액트별 원본을 보존해 만든 독립 동반 파일이다. 원본 PoB 안의 캠페인 트리는 `3_27` 태그였으므로, 설치된 PoB의 3.29 트리 데이터에서 모든 노드 ID와 숙련 효과가 존재하는지 확인된 여섯 단계만 `3_29`로 변환했다. 원본의 별도 Endgame 탭은 제외했다.

| 캠페인 탭 | 구간 | 주력 | 패시브 노드 |
|---|---|---|---:|
| `01` | Act 1, Lv1-11 | Caustic Arrow | 16 |
| `02` | Act 1-4, Lv12-40 | Poisonous Concoction | 50 |
| `03` | Act 5-6, Lv41-55 | PConc / 획득 시 Bouncing | 63 |
| `04` | Act 7-8, Lv56-67 | PConc / Bouncing | 80 |
| `05` | Act 9-10, Lv68-72 | PConc / Bouncing | 96 |
| `06` | 초기 맵, Lv73-90 | PConc of Bouncing으로 HoT 세트 파밍 | 111 |

각 번호에서 패시브 트리, 젬 세트, 장비 세트, 설정 세트를 같은 번호로 함께 바꾼다. 처음 열면 `01`과 레벨 11이 활성화된다.

최소 전환 파일은 영상의 레벨 80 장면을 복원한 독립 동반 PoB다. MAGEFIST가 이 중간 상태를 PoB로 공개하지 않았기 때문에, Part 1 공개 PoB의 현재 젬 구조와 [비클러스터 Voltaxic Poison HoT 90포인트 트리](https://odealo.com/articles/herald-of-thunder-poison-auto-bomber-pathfinder-build)를 결합했다. 90 일반 패시브와 6 어센던시 포인트의 모든 노드/숙련이 설치된 3.29 트리에 존재하는지 검증했고, `Calamitous Visions`는 61834 주얼 소켓에 장착했다. 우버 미궁 뒤에는 남겨 둔 `Nature's Boon` 두 노드를 찍는다.

HoT 파일인 `Magefist_Chaos_HoT_Pathfinder_3.29.xml`에는 공개된 두 PoB의 활성 상태만 합쳤다.

| 단계 | 원본 | 캐릭터 | Combined DPS | Total EHP | 핵심 변화 |
|---|---|---:|---:|---:|---|
| `01 Lv95 Part 1` | `GXoW7hsWd6` | 95 | 7.09M | 36.0k | 쌍 Nebulis, 100% 카오스 전환, Progenesis |
| `02 Lv98 Part 2` | `gcNfqrGAAe` | 98 | 16.50M | 104.6k | 희귀 셉터+방패, 75/53 막기, 새 클러스터와 젬 |

각 단계는 패시브 트리, 장비 세트, 젬 세트, 설정 세트를 같은 번호로 함께 바꿔야 한다. 주력 스킬 그룹은 두 단계 모두 7번으로 정규화했다.

원본에 있던 `Animated Guardian` 장비 세트는 통합본에서 제외했다. Part 2에서 제작자가 이 플레이 방식에서는 소환수 생명력 투자가 부족해 AG와 망령이 생존하지 못했다고 확인했기 때문이다. `Leer Cast`, `Dying Breath`, `Belly of the Beast`, `Vixen's Entrapment`는 플레이어용 구매 목표가 아니다.

## 실제 진행 순서

### 0. 캠페인과 초기 맵

- 설치한 `00_Campaign_PConc.xml`의 `01` 탭에서 활 스킬 `Caustic Arrow`로 시작하고, 레벨 12부터 `Poisonous Concoction`으로 바꾼다.
- 영상에서는 첫 미궁에서 `Poisonous Concoction of Bouncing`을 얻은 뒤 `Fury Valve`, `Thief's Torment`, 추가 투사체 보조를 사용했다.
- 첫 미궁에서 Bouncing을 못 얻어도 일반 PConc로 계속 진행할 수 있다. 캠페인 원본 탭은 이 경우를 위해 일반 PConc를 유지하며, `06` 초기 맵 탭에는 Bouncing 6링크가 들어 있다.
- MAGEFIST 공개 PoB 두 개에는 캠페인/PConc 트리가 없다. 최종 HoT 트리를 캠페인 트리처럼 따라가면 안 된다.
- Kitava 처치 직후 제작자 보유액은 37 chaos였고, 그 상태에서는 전환하지 않고 PConc를 계속 사용했다.
- 영상의 실제 전환 시점은 레벨 80이다.

### 1. 임시 Voltaxic Rift HoT 전환

다음 항목을 창고에 모두 모은 뒤 한 번에 바꾼다.

- 현재 핵심 즉구 합계 80c와 패시브 재분배 비용. 영상의 15 Divine은 2026-08-22 현재 최저가가 아니라 당시의 보수적 파밍 기준이다.
- `Voltaxic Rift`
- 비타락 6링크 `Dendrobate`; 메인 링크 색은 `3B2G1R`이고 흰 소켓으로 대체 가능
- `Storm Secret` 2개
- `Calamitous Visions`와 `Lone Messenger`
- 생명력, 원소 저항, 카오스 저항, 주문 억제
- `Dendrobate` 조건인 민첩 300과 지능 150
- `Topaz Flask`를 포함해 `Used when Charges reach full`을 붙인 유틸리티 플라스크
- 천둥의 전령 6링크 젬

즉구 검색은 모두 온라인 상태와 고정가/즉구만 사용했다.

| 항목 | 수량/조건 | 확인가 | 공식 거래소 |
|---|---|---:|---|
| Voltaxic Rift | 1개 | 35c | [검색](https://www.pathofexile.com/trade/search/Allflame/jWQwy3VbuX) |
| Dendrobate | 비타락, 정확히 6링크 | 30c | [검색](https://www.pathofexile.com/trade/search/Allflame/7nEPm3Oru5) |
| Storm Secret | 2개 | 2c | [검색](https://www.pathofexile.com/trade/search/Allflame/4mKzbJwLc9) |
| Calamitous Visions | 1개 | 1c | [검색](https://www.pathofexile.com/trade/search/Allflame/EBPqmveBt5) |
| Empower Support | 정확히 3레벨 | 12c | [검색](https://www.pathofexile.com/trade/search/Allflame/lg0wOqq6uV) |
| 합계 | 핵심 5종 | **80c** | — |

30c `Dendrobate` 매물의 소켓은 `G-W-W-W-W-W`라 흰 소켓 다섯 개로 `3B2G1R`을 그대로 수용한다. 정확히 `3B2G1R`로만 검색한 온라인 비타락 6링크 [완제품은 확인 시점 0개](https://www.pathofexile.com/trade/search/Allflame/yYv2O3mrSR)였지만, 흰 소켓 매물이 있으므로 별도 색칠 없이 즉시 장착할 수 있었다.

Divine은 온라인 대량 매물 기준 약 [184~195c](https://www.pathofexile.com/trade/exchange/Allflame/4D6MKEu9), 후회의 오브는 대량 매물 기준 약 [1c당 1개](https://www.pathofexile.com/trade/exchange/Allflame/mw7Dwh6)였다. 캠페인 06 트리와 최소 전환 트리의 차이는 환불 67포인트이고, 퀘스트 환불 20개를 모두 남겼다면 후회의 오브 최대 47개가 필요하다. 따라서 캠페인 레어가 속성·저항 조건을 이미 만족하면 `80c + 최대 47c`, 새 희귀 장비까지 전부 사면 2~3 Divine을 안전 예산으로 잡는다.

`Voltaxic Rift`는 이 단계에서 번개 피해를 카오스로 전환하면서 감전도 담당한다. 완전 전환 혈통을 아직 열지 못한 상태에서 가장 단순한 다리 역할이다.

`Calamitous Visions`를 빼먹으면 `Lone Messenger`가 없어져 피해가 크게 떨어진다. 영상에서도 첫 전환 직후 피해가 낮았던 원인이 이것이었다.

### 2. Sinner Saint 100% 카오스 전환

`Voltaxic Rift`를 빼기 전에 다음 조건을 모두 만족한다.

1. 금단의 성역 한 바퀴를 완료하고 Lycia를 처치해 Lycia Bloodline을 진행한다.
2. 우버 미궁을 완료한다.
3. `Sinner Saint`를 확보한다. 이 노드는 번개·냉기·화염 피해의 67%를 카오스 피해로 전환한다.
4. `Foulborn The Blue Nightmare`를 원본 PoB 위치에 장착한다.
5. 주얼 반경의 할당 소형 패시브에 `Tattoo of the Valako Stormrider`를 원본 단계와 동일하게 배치한다.
6. `Vessel of Vinktar`를 준비한다.
7. 감전 회피 플라스크가 먼저 켜진 뒤 Vinktar가 작동하도록 확인한다.

Foulborn 주얼은 반경 내 번개 저항/모든 원소 저항 패시브가 주는 수치만큼 번개 피해를 카오스로 전환한다. 문신 개수와 위치는 임의로 외우지 말고 각 PoB 단계의 실제 Overrides를 따른다.

`Voltaxic Rift`를 제거하면 `Vessel of Vinktar`가 주변 적을 감전시켜 천둥의 전령을 시작한다. Vinktar는 플레이어도 50% 감전시키므로 자동 플라스크가 동시에 켜질 때 감전 회피가 늦게 적용될 수 있다. 영상의 Part 1에서는 다른 네 플라스크가 먼저 오른 뒤 Vinktar를 한 번 수동으로 눌렀다.

### 3. Part 1 방어 기준선

다음은 단순 사치품이 아니라 Part 1 공개 상태의 방어 구조다.

- `The Tides of Time`: 플라스크 효과와 지속 충전
- `Progenesis`: 피격 생명력 손실 일부를 시간에 걸쳐 받음
- 플라스크 효과와 충전 유지
- 생명력 재생 보충(recoup)
- 인내 충전: `Enduring Composure`
- 원소 상태 이상 면역: `Stormshroud`와 감전 회피
- 주문 억제 약 96%

Part 1 원본은 생명력 3,338, 에너지 보호막 466, 84/84/83/75 저항, 36k Total EHP다. 원소 최대 피격은 약 34~36k지만 물리 최대 피격은 약 7.0k다.

### 4. Part 2 최종 업그레이드

Part 2는 쌍 `Nebulis`를 다음 제작 장비로 바꾼다.

- 무기: `Oscillating Sceptre`, Elemental Overload 암시, 파쇄된 `+1 to Level of all Spell Skill Gems`
- 방패: `Transfer-attuned Spirit Shield`, 높은 막기, 번개 피해, 파쇄된 `+1 to Level of all Lightning Spell Skill Gems`
- 목걸이: `Scrabbler Talisman`, `+2 to Level of all Herald Skill Gems` 암시, 파쇄된 `+1 to Level of all Lightning Skill Gems`
- 장갑: 카오스 피해 생명력 흡수 암시를 반드시 포함
- `Rumi's Concoction`, Jade Flask, `Tempest Shield`
- `Replica Reckless Defence` 2개
- `Runegraft of Treachery`로 점유 효율 확보
- 거미의 위상 4중첩

Part 2 원본은 생명력 3,696, 에너지 보호막 471, 회피 13,978, 방어도 3,414, 공격 막기 75%, 주문 막기 53%, 주문 억제 95.59%, 104.6k Total EHP다. 단, 물리 최대 피격은 여전히 약 7.9k다.

## 핵심 메커니즘

- `Herald of Thunder`는 주문이지만 주문 피해 증가로 피해가 오르지 않는다.
- 기본 치명타 확률이 0이므로 Part 1은 `Self-Fulfilling Prophecy`로 최소 치명타를 만들고, Part 2는 셉터의 `Elemental Overload` 암시로 패시브 포인트를 절약한다.
- 천둥의 전령 자체는 감전을 걸 수 없다.
- `Storm Secret` 2개가 폭풍을 유지하고 더 자주 명중시키는 대신 명중할 때마다 번개 자해를 준다.
- 자해가 `Cast when Damage Taken` 보조 기술, 최근 피격, 인내 충전, 재생 보충을 계속 작동시킨다.
- `Nature's Reprisal`은 위축 확률과 효과를, `Master Toxicist`는 독 확산과 플라스크 중 20% 확률 100% 증폭 독을 제공한다.
- `Nature's Adrenaline`과 `The Tides of Time`이 고유 플라스크 상시 유지의 기반이다.
- Part 2 영상에서 장갑의 `0.2% of Chaos Damage Leeched as Life` 암시가 주 유지력임을 뒤늦게 확인했다. 이 암시가 없는 장갑은 최종 장갑으로 보지 않는다.

## 젬 구성

### 레벨 80 최소 전환

- 몸통: `Herald of Thunder` + `Empower 3` + `Unbound Ailments` + `Void Manipulation` + `Elemental Focus` + `Added Lightning Damage`
- 활: `Lightning Arrow` + `Overcharge`; 첫 감전과 보스에서 끊긴 HoT 재시작용
- 장갑: `Despair` + `Crackling Lance of Branching` + `Hextouch` + `Cast when Damage Taken 1`
- 장화: `Withering Step` + `More Duration` + `Automation`
- 투구: `Cast when Damage Taken 1` + `Lightning Conduit` + `Added Lightning Damage` + `Elemental Focus`
- 활: `Cast when Damage Taken 1` + `Immortal Call 3` + `More Duration`

### Part 1 몸통

`Herald of Thunder` + `Empower` + `Unbound Ailments` + `Void Manipulation` + `Elemental Focus` + `Added Lightning Damage`

### Part 2 몸통

`Herald of Thunder` + `Empower` + `Unbound Ailments` + `Void Manipulation` + `Elemental Focus` + `Cruelty`

### Part 2 보조 그룹

- `Despair` + `Crackling Lance of Branching` + `Hextouch` + `Cast when Damage Taken`
- `Phase Run` + `Automation` + `Withering Step` + `More Duration`
- `Flame Dash` + `Vaal Blight` + `More Duration`
- `Tempest Shield`
- `Summon Chaos Golem` + `Enhance`
- `Aspect of the Spider`

정확한 레벨·퀄리티·소켓 위치는 통합 PoB의 각 젬 세트를 기준으로 한다.

## 제작 순서

### 셉터

1. Elemental Overload 암시가 있는 `Oscillating Sceptre`를 사용한다.
2. 파쇄된 `+1 all Spell Skill Gems`를 목표로 한다.
3. 영상은 `Aetheric + Corroded + Shuddering Fossil` 조합으로 +1을 찾았다.
4. `+1 Lightning Spell Skill Gems`를 번개 Harvest 재련으로 찾는다.
5. 접두 고정 후 Veiled Chaos를 사용해 번개 또는 카오스 피해 계열을 노린다.
6. 주문 피해는 HoT를 증폭하지 않으므로 좋은 옵션으로 계산하지 않는다.
7. 제작대 번개 피해/감전 확률 또는 필요한 마무리 옵션을 붙인다.

### 목걸이

1. `+2 all Herald Skill Gems` 암시의 `Scrabbler Talisman`을 사용한다.
2. 파쇄된 `+1 all Lightning Skill Gems`를 목표로 한다.
3. 지능이 크게 필요하므로 영상은 `Deafening Essence of Spite`를 사용했다.
4. 높은 생명력과 지속 피해 배율을 노린다.

### 장갑·장화·방패

- 장갑: 힘+민첩 파쇄 베이스, 생명력/저항/회피, 카오스 지속 피해 배율과 카오스 피해 흡수 암시
- 장화: 주문 억제 파쇄, 35% 이동 속도, 생명력, 원소 상태 이상 회피
- 방패: 높은 막기, 번개 피해, +1 번개 주문, 부족한 저항

희귀 장비의 정확한 베이스는 유일한 정답이 아니다. `Majestic Pelt`, `Shagreen Gloves`, `Harpyskin Boots`는 원본 착용 예시이며, 필요한 옵션 기능을 맞추는 것이 우선이다.

## 지도와 콘텐츠 주의

피하거나 매우 주의할 조건:

- 생명력 흡수 불가
- 플라스크 충전 획득/지속/효과를 크게 낮추는 조건
- 회복률 감소
- 몬스터의 독 회피 또는 카오스 저항 증가
- 상태 이상 회피로 Vinktar 감전 시작이 불안정해지는 조건
- 큰 물리 피해가 겹치는 콘텐츠

PoB의 104k EHP만 보고 모든 상황에서 단단하다고 판단하면 안 된다. 최종 수치는 플라스크 사용, 15 위축, 인내 충전, 최근 치명타, 생명력 흡수 중, 거미줄 4중첩 등을 켠 조건부 수치다.

## 필터 타깃 후보 — 사용자 승인 전

PoB Notes가 비어 있어 영상에서 명시한 역할과 실제 두 PoB를 대조했다. 아래 후보는 아직 필터 정본에 승인 저장하지 않았다.

| 분류 | 후보 | 근거 | 필터 한계 |
|---|---|---|---|
| 필수/임시 | Voltaxic Rift | 첫 HoT 전환 다리 | Spine Bow 고유 베이스 |
| 필수 | Storm Secret 2개 | 영상에서 가장 중요한 아이템으로 명시 | 고유 Topaz Ring 전체가 보일 수 있음 |
| 필수 | Dendrobate | 영상에서 Best in Slot로 명시 | Sentinel Jacket 고유 베이스 |
| 필수 | Calamitous Visions | Lone Messenger 없을 때 피해 급락 | 고유 Small Cluster Jewel |
| 완전 전환 필수 | Foulborn The Blue Nightmare | 100% 카오스 전환 | 고유 Cobalt Jewel 전체가 보일 수 있음 |
| 완전 전환 필수 | Vessel of Vinktar | Voltaxic 제거 후 감전 시작 | Topaz Flask 고유 베이스 |
| 중요 | The Tides of Time | Pathfinder 플라스크 엔진 | Vanguard Belt 고유 베이스 |
| 중요 | Progenesis | 제작자가 거의 필수라고 명시 | Amethyst Flask 고유 베이스 |
| 중요 | Stormshroud | 상태 이상 면역 | Viridian Jewel 고유 베이스 |
| 업그레이드 | The Light of Meaning | 번개 피해 변형만 사용 | 변형을 필터에서 구분 불가 |
| Part 2 | Replica Reckless Defence, Rumi's Concoction | 막기 전환 | Cobalt Jewel은 공유 베이스 |
| 제작 | Oscillating Sceptre, Transfer-attuned Spirit Shield, Scrabbler Talisman | Part 2 직접 제작 | 파쇄/아이템 레벨 조건 필요 |
| 제작 | 4패시브 Herald Medium, 8패시브 Chaos Large Cluster | 최종 클러스터 | 인챈트·패시브 수 조건 필요 |

## 원본과 생성 경로

- Part 1 영상: <https://www.youtube.com/watch?v=9KGgy7ofDZk>
- Part 2 영상: <https://www.youtube.com/watch?v=qtB0hKvP3hA>
- Part 1 PoB: <https://poedb.tw/pob/GXoW7hsWd6>
- Part 2 PoB: <https://poedb.tw/us/pob/gcNfqrGAAe>
- 캠페인 원본 가이드: <https://mobalytics.gg/poe/profile/mrronit/builds/mrronit-s-poisonous-concoction-starters-noob-friendly>
- 캠페인 원본 PoB: <https://pobb.in/o39wtJ3fp-zj>
- 최소 전환 비클러스터 트리 출처: <https://odealo.com/articles/herald-of-thunder-poison-auto-bomber-pathfinder-build>
- 정본: `config/build_setups/magefist_chaos_hot_pathfinder_3_29.spec.json`
- 캠페인 생성기: `python/build_magefist_campaign_pob.py`
- 최소 전환 생성기: `python/build_magefist_min_transition_pob.py`
- HoT 생성기: `scripts/build_magefist_chaos_hot_pathfinder_3_29_pob.ps1`
- 캠페인 설치본: `C:\Users\User\Desktop\Game\PoeCharm3_20260307\POE1 POB\Builds\3.29-CotA\Magefist_Chaos_HoT_Pathfinder_3.29_00_Campaign_PConc.xml`
- 최소 전환 설치본: `C:\Users\User\Desktop\Game\PoeCharm3_20260307\POE1 POB\Builds\3.29-CotA\Magefist_Chaos_HoT_Pathfinder_3.29_01_Minimum_Transition_Voltaxic.xml`
- HoT 설치본: `C:\Users\User\Desktop\Game\PoeCharm3_20260307\POE1 POB\Builds\3.29-CotA\Magefist_Chaos_HoT_Pathfinder_3.29.xml`

캠페인과 최소 전환 생성기는 원본 해시, 3.29 트리 호환 결과와 최종 설치본 해시를 출력한다. HoT 생성기는 원본의 활성 플레이어 장비만 가져오고, 각 원본과 최종 설치본 해시를 출력한다.
