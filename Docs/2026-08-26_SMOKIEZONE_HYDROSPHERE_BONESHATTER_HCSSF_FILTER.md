# Smokiezone Hydrosphere Boneshatter 3.29 HCSSF 진행형 필터

작성일: 2026-08-26 / 최종 시각 개정: 2026-08-27  
출력 방식: 자동 진행형 1개  
메인 색: Violet Velvet `#7C3AED`  
게임 모드: HCSSF

## 결론

이 필터는 `Wreckers SSF Filter for Everyone`의 자동 `AreaLevel` 진행을 표시 논리의 뼈대로 사용한다. Smokie의 메인 PoB Notes, 계획 장비, Day 1·2·3 실제 PoB와 공유 제작표를 다시 대조해 빌드 제작 베이스를 별도로 확정했다.

- 지역 레벨 82 이하: 아직 장비가 갖춰지지 않은 HCSSF 진행을 위해 관련 희귀 장비와 차선 순수 Armour 베이스를 C단계로 표시한다.
- 지역 레벨 83 이상: 모든 희귀 장비를 무조건 표시하지 않는다. 정확히 승인된 최적 제작 베이스만 계속 terminal `Show`한다.
- 엔드게임 제작 등급은 `AreaLevel`이 아니라 드롭된 아이템 자체의 `ItemLevel`로 판정한다.
- 빌드 필수 고유 후보 베이스, 6링크, 승인된 제작 베이스, 전직 젬 및 핵심 재료는 뒤의 Wrecker Hide보다 먼저 판정된다.
- 시장 가격은 전역 T0/T1 안전 규칙에만 쓰고, HCSSF의 생존 장비 가시성은 시장 가격으로 결정하지 않는다.

## 승인된 Violet Velvet 시각 체계

Allie 3.29의 Velvet 가치 반전과 Luminary SSF의 제한된 의미색 사용을 대조한 뒤, 화면 전체를 보라색으로 덮던 이전 정규화 레이어를 제거했다. 최종 규칙은 다음 네 채널을 분리한다.

| 채널 | 전달하는 정보 | 최종 규칙 |
|---|---|---|
| 글자색 | 희귀도·익숙한 POE 카테고리 | Normal `200 200 200`, Magic `136 136 255`, Rare `255 255 119`, 일반 Unique `175 96 37`, Gem `27 217 217` |
| 배경 명도 | 가치 | T0 흰색, T1 메인 보라, 빌드 재료 Orchid, 일반 수집품 암색 |
| 테두리·아이콘 | 빌드 관련성과 종류 | 제작 베이스 Violet Diamond, Unique Star, Currency Cross, Card Square, Breach Hexagon |
| 광선·소리 | 즉시 행동 필요성 | T0/T1·필수품은 강하게, 빌드 재료는 임시 광선, 일반 화폐는 광선 없이 조용하게 |

### 공통 가치 계단

| 단계 | 글자 / 테두리 / 배경 | 행동 알림 |
|---|---|---|
| T0 | Violet `124 58 237` / Violet / 거의 흰색 `248 248 250` | 45, 강한 전용음, 영구 Purple, 아이콘 0 |
| T1 | 거의 흰색 / Lavender `218 200 250` / Violet | 45, 강한 전용음, 영구 Purple, 아이콘 0 |
| 빌드 재료 | 짙은 Ink `19 10 29` / Violet / Orchid `200 101 242` | 42, 보통 소리, 임시 Purple, 아이콘 1 |
| 일반 수집품 | Muted Lavender `172 160 188` / 중립 / 암색 `18 16 22` | 34~38, 무음 또는 작은 소리, 광선 없음 |

화폐·Essence·점술 카드는 카테고리별 새 원색을 추가하지 않고 이 계단을 공유한다. 6링크 Red, 퀘스트 Green, 젬 Cyan, 일반 Unique Brown, 지도 고유 문법은 즉시 인지를 위해 그대로 둔다.

### 에센스 가치 계단

기존 Death Oath 레이어의 저단계 에센스용 흰 배경·빨간 글씨는 가치 의미가 불명확하고 Violet Velvet 체계와 충돌하므로 최종 색상에서 제거했다. 3.29 `BaseItemTypes`의 에센스 화폐 106종을 다음 네 단계로 서로 배타적으로 분류한다.

| 단계 | 대상 | 최종 색상 |
|---|---|---|
| High | Deafening, 특수 `Essence of ...`, Remnant of Corruption | 거의 흰 글씨 / Lavender 테두리 / Violet 배경 |
| Important | Shrieking | 밝은 Lavender 글씨·테두리 / `P-700` 배경 |
| Routine | Screaming, Wailing | `P-300` 글씨 / Violet 테두리 / `P-900` 배경 |
| Quiet | Whispering, Muttering, Weeping | 중립 밝은 글씨 / `P-700` 테두리 / `P-950` 배경 |

이 네 규칙은 색상만 지정하고 `Continue`한다. 기존 Show/Hide, 글자 크기, 소리, 광선, 아이콘은 바꾸지 않는다. Contempt, Zeal, Greed, Envy, Anger, Hatred, Wrath, Scorn, Misery 계열과 `Essence of Insanity`는 뒤의 빌드/HCSSF terminal 규칙이 Orchid 배경으로 다시 덮어써서 일반 에센스보다 강하게 구분한다.

### 고유 아이템 우선순위

- 일반 고유: POE 기본 갈색 글씨를 유지하고 별도 빌드 빔을 주지 않는다.
- 필수 후보 `Cloth Belt`, `Crystal Belt`: 거의 흰 글씨, Aubergine `37 17 71` 배경, Orchid 테두리, Purple Star/영구 빔, `MyPrecious.mp3`.
- 선택 후보 `Sapphire Flask`: 갈색 글씨와 얇은 Violet 테두리만 사용하고 소리·빔은 제거한다.
- 필수 후보 스타일은 T0/T1보다 배경을 어둡게 해, “빌드에 필요함”과 “전역 최고가치”를 서로 혼동하지 않게 했다.

기준서의 일반적인 필수 고유 Red 예외보다 사용자가 승인한 Violet 전용 후보 표현을 우선 적용했다. 6링크와 위험 표식의 Red 의미는 그대로 예약한다.

미리보기: [`assets/smokiezone_violet_velvet_overview.png`](assets/smokiezone_violet_velvet_overview.png)

## 공유 시트와 PoB 베이스 재조사

공유 시트의 `04_장비제작` 탭은 장착 중인 모든 아이템을 필터에 넣으라는 뜻이 아니다. 제작자가 지정한 베이스를 모아 Essence, Harvest, Recombination과 Eldritch 제작에 사용하라는 진행표다.

| 베이스 | 재검증 근거 | 필터 정책 |
|---|---|---|
| `Vaal Axe` | 메인 Notes가 엔드게임 피해·공속 균형의 최적 베이스라고 명시. Day 2·3 실제 무기는 모두 `ilvl 83` | `ItemLevel >= 83` B단계, 그 미만도 조용한 제작용 C단계 |
| `Despot Axe`, `Ezomyte Axe` | 메인 Notes가 일반 Trauma 단계에서 빠른 램핑용으로 `Despot > Ezomyte`를 지정. Day 1은 `ilvl 85 Despot Axe` | 단일 진행형이 Complex Trauma 전환 여부를 알 수 없으므로 전 지역 C단계 terminal `Show` |
| `Royal Plate` | 계획 장비와 Day 1·2·3가 모두 사용. 3.29 데이터상 DropLevel 84, 기본 Armour 최대 1,360 | `ItemLevel >= 84` B단계 terminal `Show` |
| `Giantslayer Helmet` | 계획 장비와 Day 1·2·3가 모두 사용. DropLevel 84, 기본 Armour 최대 669 | `ItemLevel >= 84` B단계 terminal `Show` |
| `Leviathan Gauntlets` | 계획 장비와 Day 1·2·3가 모두 사용. DropLevel 84, 기본 Armour 최대 413 | `ItemLevel >= 84` B단계 terminal `Show` |
| `Leviathan Greaves` | 계획 장비와 Day 1·2·3가 모두 사용. DropLevel 84, 기본 Armour 최대 413 | `ItemLevel >= 84` B단계 terminal `Show` |
| `Amethyst Ring`, `Turquoise Amulet` | 메인 Notes와 공유 시트가 Harvest/후기 제작 베이스로 지정. 실제 진행본은 `ilvl 84–85` | `ItemLevel >= 83` B단계, 낮은 레벨 사본도 진행 제작용 C단계 |

메인 PoB Notes의 “use breach to get optimal armor bases in each slot”은 위 네 순수 Armour 베이스를 가리킨다. 계획 장비와 세 실제 스냅샷이 모두 같은 베이스를 사용하므로 단순 장착품 복사가 아니라 반복 검증된 제작 목표로 승인했다.

## 영문 HCSSF/SSF 필터 대조

### 1. Wrecker of Days — SSF Filter for Everyone 3.29.1

현재 프로필: <https://poe.kakaogames.com/account/view-profile/Wrecker_of_Days-7691/item-filters>

프로필 설명과 실제 3.29 소스를 함께 확인했다.

- 레벨 1부터 최고 지역까지 한 필터가 자동으로 엄격해진다.
- 주로 장비만 걸러 내고, 화폐·지도·점술 카드·품질 젬/플라스크·제작 레시피는 거의 모두 보여 준다.
- 더 높은 장비 베이스가 열리면 이전 베이스를 `AreaLevel`로 퇴장시킨다.
- 생명력/마나 플라스크도 현재 구간에 맞는 등급을 중심으로 진행한다.

채택: 자동 진행, SSF 비장비 수집 정책, 87개 Hide 진행 조건.  
보완: HCSSF 핵심 플라스크와 승인된 빌드 제작 베이스는 83+에서도 사라지지 않는다.

### 2. StupidFatHobbit — Sovereign 3.29.1

현재 프로필: <https://poe.kakaogames.com/account/view-profile/StupidFatHobbit-5880/item-filters>  
설계 설명: <https://www.pathofexile.com/forum/view-thread/1595976>  
3.29.1 변경: <https://www.reddit.com/r/pathofexile/comments/1v9e1dq/stupidfathobbits_filter_v3291_allflame_league/>

제작자가 구분한 용도는 다음과 같다.

- General: 레이스, 리그 시작, 장비가 부족한 상황
- Strict: 매핑 중반, 이미 준비된 레벨링 장비
- Uberstrict: 완성 장비로 고밀도 파밍과 100레벨을 빠르게 노리는 상황

Strict는 비품질 젬, 거의 모든 비강조 희귀 장비, 흰 장신구, 일부 품질 플라스크 등을 숨긴다. HCSSF 자동 필터가 캐릭터의 장비 완성 여부나 창고 상태를 알 수 없으므로 Strict/Uberstrict의 가정을 자동으로 적용하지 않았다.

채택: General의 리그 시작/저장비 안전 철학, 새 리그 아이템의 보수적 표시.  
제외: 장비 완성을 전제로 하는 Strict/Uberstrict 자동 전환.

### 3. NeverSink Hardcore 8.20.1d

현재 프로필: <https://poe.kakaogames.com/account/view-profile/NeverSink-3349/item-filters>  
공식 소스: <https://github.com/NeverSinkDev/NeverSink-Filter>

2026-08-26 현재 Hardcore Regular 프로필은 `8.20.1d.2026.238.11`이며 경제 정보로 주기적으로 갱신된다. 이 필터의 가격·가치 계층은 유용하지만, 거래 경제를 기준으로 하는 엄격도는 HCSSF 표시 논리의 정본으로 쓰지 않았다.

채택: 공식 8.20.1d의 T0/T1 화폐·고유 베이스, 시각 계층과 신규 3.29 데이터.  
제외: HC 거래 경제가 낮게 평가한 재료나 장비를 SSF에서도 숨기는 정책.

### 4. Narnach SSF

소스: <https://github.com/Narnach/path_of_exile_loot_filters>

3.15 이후 은퇴한 필터라 현재 BaseType/경제 목록에는 사용하지 않았다. 다만 다음 구조는 여전히 타당하다.

- 레벨 1~100 단일 진행형
- 현재 지도보다 높은 지도에 더 강한 표시
- 품질 젬/플라스크의 장기 가시성
- 미분류 신규 항목을 강한 경고색으로 보여 주는 디버그 안전망

채택: 구조적 원칙만 사용.  
제외: 오래된 아이템명과 가치 티어 전체.

### 5. Allie 3.29 — Velvet

공개 필터: <https://www.pathofexile.com/item-filter/Nyy78fV>  
검증한 로컬 원본: `C:\Users\User\Documents\My Games\Path of Exile\OnlineFilters\Nyy78fV`

3.29.3 / NeverSink 8.20.1c 기반 `4-VERY STRICT`, `VELVET` 소스를 직접 대조했다. Allie는 화폐·Essence·카드·고유에 매번 새로운 색을 부여하지 않고 다음 명도 반전을 반복한다.

- 최상단: 흰 배경 + 마젠타 글씨/테두리
- 다음: 마젠타 배경 + 흰 글씨/밝은 테두리
- 중간: Orchid/Lavender 배경 + 검은 글씨
- 하단: 어두운 중립 배경

채택: 같은 계열 안에서 배경과 글씨 명도를 반전하는 가치 계단.  
변환: Allie의 마젠타를 사용자 메인 Violet `#7C3AED`와 한 개의 Orchid 중간 토큰으로 번역했다.

### 6. Goratha Luminary SSF / 로컬 Luminary 조합

현재 공개 프로필: <https://poe.kakaogames.com/account/view-profile/Goratha-2898/item-filters>  
검증한 로컬 조합: `C:\Users\User\Documents\My Games\Path of Exile\Luminary_Bot_SSF_3.29.filter`

현재 공개 Luminary SSF 3.29.3 필터 ID는 `zXla6NIz`다. 공개 원문 다운로드는 로그인 없이 완료할 수 없어 계정 변경이나 Follow를 하지 않았고, 로컬 Luminary 조합과 공개 메타데이터만 사용했다. 로컬 조합은 일반 범주의 익숙한 색은 Death Oath 계열에서 유지하고, 높은 가치만 Allie의 밝은 Velvet 계단으로 승격한다.

채택: 전 화면을 테마색으로 정규화하지 않고 일반 범주는 익숙하게, 빌드·고가치만 제한적으로 강조하는 구조.

## 로컬 소스 정량 비교

NeverSink HC 두 파일은 로컬에 있던 `8.19.2a`이므로 최신 경제 정본이 아니라 엄격도 차이 확인용이다.

| 소스 | Show | Hide | Continue | Rare 조건 | Flask 조건 |
|---|---:|---:|---:|---:|---:|
| Wrecker SSF 3.29.1 | 173 | 87 | 260 | 16 | 26 |
| NeverSink HC Regular 8.19.2a | 766 | 21 | 42 | 330 | 72 |
| NeverSink HC Strict 8.19.2a | 693 | 60 | 42 | 310 | 69 |

NeverSink HC Regular도 최종 매핑 희귀 장비 전체를 숨기는 catch-down 블록을 가지며, Strict는 희귀/플라스크 Hide가 더 많다. 따라서 새 HCSSF 캐릭터의 한 개짜리 자동 필터에는 Wrecker + Sovereign General 쪽이 더 안전하다.

## 실제 HCSSF 오버라이드

### 항상 표시하거나 등급을 올리는 항목

- 6링크
- 미확인 Unique `Cloth Belt`: Soul Tether 또는 Replica Soul Tether 후보
- 미확인 Unique `Crystal Belt`: The Burden of Truth 후보
- `ItemLevel >= 83` Vaal Axe
- `ItemLevel >= 84` Royal Plate, Giantslayer Helmet, Leviathan Gauntlets, Leviathan Greaves
- `ItemLevel >= 83` Amethyst Ring, Turquoise Amulet
- Despot Axe, Ezomyte Axe와 더 낮은 ItemLevel의 승인 베이스는 조용한 제작 단계로 계속 표시
- Boneshatter 변형 젬 계열(목표: Boneshatter of Complex Trauma)
- Less Duration Support
- Cyaxan's Ducat, Essence of Insanity, Gemcutter's Prism, Vaal Orb
- Vivid Crystallised Lifeforce, Opalescent Oil
- Breachstone/Splinter, Blueprint, Divine Vessel

### HCSSF 진행 표시

- 지역 레벨 82 이하의 희귀 Amulet, Belt, Body Armour, Boots, Gloves, Helmet, Ring
- 지역 레벨 82 이하의 희귀 Two Hand Axe
- Divine Life Flask, Quicksilver Flask, Ruby Flask, Sapphire Flask, Topaz Flask
- 생명력/저항/무기 제작용 Essence
- 지역 레벨 82 이하의 차선 순수 Armour 베이스

83+에서는 모든 희귀 장비를 고정 표시하던 이전 규칙을 제거했다. 대신 정확한 최적 베이스와 핵심 플라스크만 terminal `Show`한다. 이로써 제작할 가치가 있는 베이스는 Normal/Magic/Rare 모두 남고, 관계없는 희귀 장비가 계속 쌓이는 문제는 줄어든다.

### 해석이 필요한 항목

- 아이템 필터는 미확인 고유의 이름을 알 수 없어 `Cloth Belt`, `Crystal Belt`, `Sapphire Flask` 베이스 전체를 표시한다. 다른 고유가 나올 수 있다.
- `Boneshatter of Complex Trauma`는 `BaseItemTypes`의 실제 `BaseType`이 아니라 `ActiveSkills` 표시 이름이다. POE 필터에는 `TransfiguredGem "Boneshatter"`를 사용한다. 이 조건은 Boneshatter 변형 계열을 표시하므로 `Boneshatter of Carnage`도 같은 강조를 받을 수 있다.
- `MercenaryModAddCritPerExert`는 필터에서 내부 ID로 정확히 식별할 수 없다. 표시 접미사 `of Infamy`가 붙은 식별된 Helmet을 알리고 직접 확인한다.
- 가이드의 `Allflame Divine`은 검증된 드롭 BaseType을 특정하지 못해 추측 규칙을 만들지 않았다. 앱의 한/영 아이템명 검색 흐름에 남겼다.

## 점술 카드와 신규 항목 안전망

- 공식 NeverSink 8.20.1d와 Wrecker 목록을 합쳐 현재 470장을 서로 배타적인 terminal `Show` 티어로 분류했다.
- 3.29 신규 카드 16장은 별도 리그 신규 단계다.
- 알려지지 않았거나 향후 추가된 카드는 분홍색 `UpsideDownHouse` 안전 규칙으로 표시한다.
- 전체 클래스의 미분류 항목은 unconditional magenta `Continue` 장식에서 시작하고, 알려진 클래스가 뒤에서 정상 테마로 덮는다. 따라서 알려진 Hide 정책은 유지하면서 분류되지 않은 항목만 마젠타가 남는다.

## 정본과 생성 구조

- 정본: `data/filter_build_targets/poe1_smokiezone_hydrosphere_boneshatter_hcssf_3_29.json`
- 생성기: `scripts/build_smokiezone_hcssf_filter.py`
- 원본 표시 논리: `C:\Users\User\Desktop\SSF.txt`
- 원본 광역 시각 레이어: `C:\Users\User\Desktop\death oath.txt`
- 원본 고가치 강조 레이어: `C:\Users\User\Desktop\allie.txt`
- 공식 경제 스냅샷: NeverSink `8.20.1d`, commit `903189340cdafa1f4ed73c9968380826312a51f0`

원본 파일은 수정하지 않았다. 빌드·SSF 타깃과 우선순위는 한 JSON 정본에서 관리하고, 생성기의 중앙 Violet Velvet 토큰 렌더러가 모든 출력 블록에 동일하게 적용된다. RGB를 개별 규칙마다 새로 만들지 않는다.

## 검증 결과

- [x] 따옴표와 블록 구조 검사
- [x] 원본에 없는 조건/스타일 지시어 유입 검사
- [x] 3.29 `BaseItemTypes`와 `ActiveSkills.TransfigureBase`를 분리해 일반/변형 젬 이름 대조
- [x] 공유 시트, 메인 PoB Notes, 계획 장비, Day 1·2·3 PoB의 베이스와 ItemLevel 재대조
- [x] 최적 순수 Armour 베이스 4종의 DropLevel과 기본 Armour를 3.29 `ArmourTypes`로 검증
- [x] 미확인 고유 베이스의 다중 고유 가능성 문서화
- [x] 6링크와 필수 HCSSF 규칙이 첫 Hide보다 앞선 terminal `Show`인지 검사
- [x] `always_show` 제작 그룹 전체가 AreaLevel 상한 없이 첫 Hide보다 앞선 terminal `Show`인지 검사
- [x] 광범위한 83+ 희귀 방어구·장신구·양손 도끼 catch-all 제거 검사
- [x] 3/4/5/6링크를 크기·소리·아이콘으로 구분
- [x] Normal/Magic/Rare 장비 글씨를 각각 회색/파랑/노랑으로 강제하고 제작 베이스가 이를 덮지 않는지 검사
- [x] 일반/필수/선택 Unique의 갈색·Violet 강조 위계를 서로 다르게 검사
- [x] T0/T1/빌드 재료/일반 수집품이 하나의 Violet Velvet 가치 계단을 사용하는지 검사
- [x] 3.29 에센스 화폐 106종이 High/Important/Routine/Quiet 중 정확히 한 단계에 속하는지 검사
- [x] 에센스 색상 규칙에 Show/Hide, 글자 크기, 소리, 광선, 아이콘 변경이 없는지 검사
- [x] 캠페인 저단계 에센스의 레거시 흰 배경·빨간 글씨가 최종 Violet 계단에 의해 덮이는 순서 검사
- [x] 젬·화폐·퀘스트·지도·고유를 색 외에도 아이콘 모양으로 구분
- [x] 커스텀 사운드 10종이 게임 필터 폴더에 존재
- [x] 한 규칙에 내장/커스텀 사운드 중복 없음
- [x] 단일 출력의 모든 규칙이 동일 정본/보라색 토큰에서 생성
- [x] 미분류 카드 terminal 안전망과 전체 클래스 magenta fallback 검사
- [x] 원본 87개 Hide 진행 조건 보존
- [x] 두 번 생성한 SHA-256 일치
- [x] 전용 회귀 테스트 9개 통과(변형 젬 조건 및 에센스 106종 분할/레이어 순서 검사 포함)
- [x] 작업본과 설치본 SHA-256 일치
- [x] `production_Config.ini`의 `item_filter_loaded_successfully`로 실제 게임 로드 확인

## 출력

- 작업본: `filters/Smokiezone_Hydrosphere_Boneshatter_HCSSF_3.29_Progressive.filter`
- 설치본: `C:\Users\User\Documents\My Games\Path of Exile\Smokiezone_Hydrosphere_Boneshatter_HCSSF_3.29_Progressive.filter`
- 에센스 색상 수정 전 백업: `C:\Users\User\Documents\My Games\Path of Exile\Smokiezone_Hydrosphere_Boneshatter_HCSSF_3.29_Progressive.pre-20260827-092129.filter`
- 크기 / 줄 수: 590,076 bytes / 11,975
- Show / Hide / Continue: 1,179 / 87 / 1,199
- 커스텀 사운드 호출: 23회 / 실제 파일 10종
- 미니맵 아이콘 / 광선 지시어: 148 / 126
- SHA-256: `0F61D5260D9E0C55026FC39626CF6DE77B041803A47DE155EFC57BE68B1EA90D`

에센스 색상 수정 전 백업의 SHA-256은 `C02F27C34FD258E4498753B348D64BADE17CBC702F0BF01D9B6AD8C84BB77AA9`이며, 설치 후 작업본과 설치본의 SHA-256이 일치한다.

현재 `production_Config.ini`의 `item_filter`와 `item_filter_loaded_successfully`가 모두 `Smokiezone_Hydrosphere_Boneshatter_HCSSF_3.29_Progressive.filter`를 기록하므로 수정본의 실제 게임 로드까지 확인됐다.
