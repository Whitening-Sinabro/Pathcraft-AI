# Luminary Bot SSF 3.29 — 전체 필터 감사 기록

감사일: 2026-08-18

## 후속 작업자 인계 규칙

플레이 중 새로운 표시·소리·우선순위 문제가 발견되면 완성본 `.filter`만 임시 수정하고 끝내지 않는다.

1. 실제로 매칭되는 선행/후행 블록과 `Continue` 덮어쓰기 순서를 확인한다.
2. 같은 범주의 Normal/Magic/Rare, 링크 수, AreaLevel 및 스택 조건까지 함께 검사한다.
3. 재생성 후에도 남도록 생성 스크립트 또는 보존되는 Luminary 오버라이드에 수정한다.
4. 필터 내부에는 현재 동작의 이유를 짧은 영문 주석으로 남기고, 이 감사 문서에는 문제·원인·최종 정책을 기록한다.
5. 수정 뒤에는 원본 SSF Hide 조건 87개 보존, Hide 활성 알림 누출, 소리 파일 존재, 내장음/커스텀음 충돌, 수치 범위, 세 배포본 SHA-256을 다시 검증한다.
6. 작업본, 게임 설치본, 다운로드본을 같은 파일로 교체한다.

현재 최종 예외 정책:

- 퀘스트 아이템: 어두운 초록 배색, `Quest Item.mp3` 전용 사용, `PlayEffect Green Temp`, `MinimapIcon 0 Green Circle`.
- Allflame Chart(해저 지도): 짙은 청록 배색, `PlayAlertSound None`, `PlayEffect Blue`, 미니맵 아이콘 없음.
- 퀘스트 소리를 다른 범주에 재사용하지 않는다.
- 해저 지도에는 퀘스트 소리나 퀘스트 아이콘을 추가하지 않는다.

## 결론

이 필터의 올바른 구조는 `NeverSink 완성본 + 소수 SSF 오버라이드`가 아니다. 바탕화면의 Wrecker 계열 `SSF.txt`가 실제 표시/숨김과 AreaLevel 진행을 결정하고, `death oath.txt`와 `allie.txt`에서 추출한 NeverSink 규칙은 `Continue` 시각 레이어로만 적용한다.

고정 순서:

1. NeverSink 광범위 시각 `Continue` 레이어
2. 일반 장비 희귀도 fallback과 Crimson 일반 카테고리 정규화
3. Allie 고가치 `Continue` 강조 레이어
4. Luminary 필수품, 링크, 최신 경제 T0 terminal `Show`
5. 활성 색상 지시어만 제거한 Wrecker SSF 진행 정본

## 감사 입력

| 역할 | 파일 | SHA-256 |
|---|---|---|
| SSF 표시/진행 정본 | `C:\Users\User\Desktop\SSF.txt` | `94CC3493AD7374B8AD8C54A88D3C43527E4DA557CA1D5723719064E3A98971E9` |
| NeverSink 광범위 시각 | `C:\Users\User\Desktop\death oath.txt` | `E637B4BB917E670CA332B350CA094DDB0AF467364B75B0922240507C81A1F8CF` |
| NeverSink 고가치 강조 | `C:\Users\User\Desktop\allie.txt` | `BEE3CC4352B3403DA752796FD764E45EEB25E9F1F76C491091CA6A59FD90B497` |
| 검증된 레이어 합성 참고본 | `Vortican_Luminary_SSF_3.29.filter` | `0AA567DBD9961DED76C38DDA9C51B1B82D06F4CCC92469FC8A0120584C93172F` |

## 정정 기록: 일반 무기 규칙

일반 무기 규칙이 아예 없다는 이전 판단은 틀렸다. 실제 합성본에는 다음 규칙이 이미 있었다.

- `Pathcraft Death Oath visual rule 742`: 알려진 장비 전체의 회색 기본 표시
- `visual rule 739~737`: Kinetic/Blasting/Somatic Wand 일반 등급
- `visual rule 736` 이하: 3소켓 이상 일반 무기의 DropLevel/ItemLevel 진행 규칙
- `visual rule 741~740`: 마법 장비 진행 규칙
- 희귀 무기의 ItemLevel·크기·부패·고가치 규칙

실제 문제는 **부재가 아니라 범위와 표현**이었다. 3소켓 미만이고 NeverSink 진행 베이스 조건에도 걸리지 않는 Wrecker SSF 표시 무기는 `rule 742`의 회색 공통 스타일만 받았다. 그 결과 일반 무기, 일반 방어구, 일부 플라스크가 서로 비슷해 보였다.

해결 규칙은 기존 규칙을 삭제하지 않는다. `rule 742` 직후에 장비 클래스 한정 Normal/Magic/Rare fallback 세 개를 `Continue`로 넣고, 이후의 더 구체적인 NeverSink 규칙이 다시 덮어쓸 수 있게 한다.

## 범주별 감사

| 범주 | 판정 | 확인 및 조치 |
|---|---|---|
| 일반/마법/희귀 무기·방어구 | 부분 통과 → 보완 | 기존 규칙 존재 확인. 비매칭 장비용 희귀도 fallback 3개 추가: Normal 흰색, Magic 저채도 청색, Rare 옅은 금색. 무음·아이콘 없음. |
| 3/4/5/6링크 | 통과 | 희귀도별 텍스트와 링크별 크기·배경·테두리·소리·광선·아이콘 분리. 6링크와 5링크는 terminal `Show`. |
| 빌드 필수 고유 | 통과 | 흰 글씨/흰 테두리/붉은 배경, 가장 강한 알림. 일반 고유보다 먼저 평가. |
| 경제 T0/T1 | 통과 | NeverSink 8.20.1d의 고유 베이스·화폐 최상위 목록을 별도 terminal `Show`로 유지. 미확인 고유는 이름이 아니라 베이스로만 판별 가능. |
| 기본 화폐·지혜·포탈 | 통과 | 캠페인/맵/스택 분리. 일반 제작 화폐는 시각 강조만 하고 무음. 지혜와 포탈은 서로 다른 색·소리 정책. |
| 일반 화폐/공명기 | 부분 통과 → 보완 | `Stackable Currency`만이 아니라 Wrecker 관례의 부분 Class `Currency`를 사용해 공명기도 일반 Crimson 범주 스타일에 포함. |
| 젬 | 통과 | 일반/품질/변형/각성·특수 젬 분리. 구식 `AlternateQuality` 블록은 원본을 보존한 채 생성 시 제외. |
| 지도 | 통과 | 일반 지도는 Crimson Square, 가이드 파밍 지도는 상위 terminal 규칙. 지도 티어/특수 지도 세부 표현은 NeverSink와 SSF 원본 유지. |
| 조각·스카라브·기타 지도 아이템 | 통과 | Crimson Hexagon 일반 범주 추가, SSF 원본의 가치별 글자 크기·소리·아이콘은 유지. |
| 점술 카드 | 판정 폐기 → 재작업 | 이 판정은 불완전했다. 아래 "점술 카드 전수 사다리" 절이 정본이다. |
| 플라스크·팅크 | 통과 | 일반 Crimson Raindrop fallback 추가, 품질·진행 플라스크 세부 규칙 유지. |
| 퀘스트 | 통과 | 어두운 초록 고정 예외. `Quest Item.mp3`는 이 범주에서만 사용하며, 초록색 임시 광선과 초록색 원 아이콘을 사용한다. |
| Dead Man's Sulphur | 통과 | 산성 연두 고정 예외. 일반 Crimson 범주와 분리. |
| Chart | 통과 | 짙은 청록/해양 계열 고정 예외. 큰 글씨와 파란 광선만 사용하고, 소리와 미니맵 아이콘은 끈다. 퀘스트 음성을 재사용하지 않는다. |
| 미분류 신규 아이템 | 통과 | NeverSink 추출 레이어의 마젠타 catch-all 유지. |
| SSF 진행 Hide | 통과 | 원본의 Hide 87개 유지. Hide 블록의 소리·광선·아이콘 누출 없음. |

## 필터 내부에 남기는 규칙

생성 스크립트와 `.filter`에는 다음 주석/규칙을 영구 삽입한다.

- `PATHCRAFT FULL AUDIT BASELINE - ORDINARY EQUIPMENT RARITY COVERAGE`
- `PATHCRAFT FULL AUDIT - CRIMSON CATEGORY NORMALIZATION`
- Normal/Magic/Rare 장비 fallback 3개
- Unique/Currency/Gem/Divination Card/Map/Fragment/Flask/Gold 일반 범주 8개

이 11개는 모두 `Continue`다. SSF Show/Hide를 바꾸지 않으며, 뒤의 고가치·빌드 필수·링크 규칙이 우선할 수 있다.

## 검사기 정정

기존 임시 통계 명령은 `Show ` 또는 `Hide `처럼 뒤 공백이 있는 원본 줄을 블록 시작으로 세지 못했다. 앞으로 블록 시작 정규식은 다음을 사용한다.

```regex
^(Show|Hide)(?:\s+#.*)?\s*$
```

따라서 이전에 기록한 일부 Show 개수는 폐기하고 이 감사의 수치를 정본으로 사용한다.

## 최종 후보 검증 수치

- 11,769줄
- Show 1,161 / Hide 87 / Continue 1,198
- 감사 보완 규칙 11개
- CustomAlertSound 호출 21개 / 고유 MP3 12개
- MinimapIcon 131개 / PlayEffect 100개
- 따옴표 오류 0
- 색상 범위 오류 0
- 폰트 범위 오류 0
- 존재하지 않는 커스텀 음원 0
- 내장음+커스텀음 중복 블록 0
- Hide 알림 누출 0
- 공식 NeverSink 기준 미확인 지시어 0
- `python/tests/test_sections_continue.py`: 312개 통과

최종 감사본 설치 시 게임 프로세스가 실행 중이었다. 설정 파일에는 같은 필터명이 선택·성공 기록으로 남아 있지만 이는 이전 리비전에서도 같았으므로, 이 정확한 해시의 라이브 로드 증거로 간주하지 않는다. 게임 옵션에서 필터를 한 번 다시 불러온 뒤 오류 유무를 확인해야 한다.

## 점술 카드 전수 사다리 (2026-08-18 추가)

이전 판정 "점술 카드 통과"는 불완전했다. 가이드 지정 카드 4장만 Luminary 전용 규칙을 받았고, 나머지 카드의 최종 표현은 NeverSink 추출 레이어와 Wrecker SSF 섹션 중 마지막으로 매칭된 블록이 결정했다. 세 소스의 티어 목록이 서로 달라 같은 카드가 소스마다 다른 등급을 받았다.

교체 결과: 단일 필터 안에서 점술 카드는 Luminary 전용 사다리 12개 블록이 전부 결정한다. 모두 terminal `Show`이므로 뒤의 카드 레이어에는 도달하지 않는다. 뒤 레이어는 삭제하지 않고 티어 근거로 남긴다.

| 섹션 | 카드 수 | 근거 | 표현 |
|---|---|---|---|
| BUILD TARGET | 4 | 가이드 5.1/5.2/6.2 | 필수 고유와 동일 배색(흰 글씨·흰 테두리·`190 0 0`), `DivinationCard.mp3`, 붉은 광선, Red Square |
| GUIDE KEEP | 1 | 가이드 8.6 (힐록 → 풍요의 기폭제) | 크림슨 강조, 전용 소리 |
| LEAGUE NEW | 16 | SSF 3.29 신규 목록 | 주황, 큰 글씨, 소리 |
| T0 | 42 | NeverSink `$tier->t1` | 흰 배경 크림슨 글씨, `HolyMotherfuckingShit.mp3`, 아이콘 0 |
| T1 | 34 | NeverSink `$tier->t2` | 크림슨 배경 흰 글씨, `Thatsworthsomething.mp3`, 아이콘 0 |
| SSF WANTED | 31 | Wrecker SSF "You've Got to be Kidding ME!!!" | 45pt, `PlayAlertSound 1 300`, 붉은 광선, White Square 0 |
| T2 | 52 | NeverSink `$tier->t3` | 42pt, 내장음, 노란 광선, 아이콘 1 |
| SSF NOTABLE | 107 | Wrecker SSF "Absolutely!" | 40pt, `PlayAlertSound 12 280`, White Square 1 |
| T3 | 8 | NeverSink `$tier->t4c` | 40pt, 내장음, White Square 2 |
| STACK 3+ | 조건 규칙 | 하위 티어 스택 보호 | 40pt, 내장음, Grey Square 1 |
| T4 / BULK / LOW | 74 / 9 / 85 | NeverSink `t4` / `t5c` / `t5` | 32~38pt, `PlayAlertSoundPositional 12 200`, 아이콘 2 |
| UNTIERED CATCH-ALL | 7 | 어느 목록에도 없는 레거시·신규 | 마젠타, `UpsideDownHouse` 안전망 |

카드 유니버스는 470장이다. GGPK 덤프의 `Metadata/Items/DivinationCards/` + `ItemClassesKey == 42` 467장에, 필터 소스에만 존재하는 3장(`Divine Shard`, `Energy Sword`, `Pearls Before Swine`)을 합쳤다.

이 과정에서 확인된 데이터 결함 2건:

- `data/game_data/BaseItemTypes.json`은 3.29 이전 추출본이다. 위 3장이 없다. GGPK 덤프만으로 "카드 전부"를 주장하면 안 된다.
- `Stacked Deck`은 `Metadata/Items/DivinationCards/DivinationCardDeck` 경로에 있지만 `ItemClassesKey`가 30(화폐)이다. 경로만으로 카드를 세면 오염된다.

`NeverSink t5`는 원본에서 Hide다. SSF 정책은 카드를 숨기지 않으므로 LOW 섹션은 표시하되 축소·무음 처리한다. Hide 87개는 그대로다.

생성 경로: `python/luminary_divcard_layer.py`(사다리 생성) → `python/apply_luminary_divcard_layer.py`(마커 사이 교체 + 세 사본 기록). 두 번 실행해도 결과가 같다. 검증: `python/tests/test_luminary_divcard_layer.py` 12개.

검증 수치(교체 후):

- 11,932줄 / Show 1,174 / Hide 87 / Continue 1,198
- 따옴표·RGB·폰트 범위 오류 0, Hide 알림 누출 0
- CustomAlertSound 호출 24개 / 고유 MP3 12개, 전부 게임 필터 폴더에 존재
- 세 사본 SHA-256 동일: `F138435E3FA69983...`
- 백업: `C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.pre-divcard-ladder.filter`

**인게임 로드 확인 완료 (2026-08-19)**: 사용자가 게임에서 필터를 다시 불러왔고 오류 없이 로드됐다.
설치본 해시가 검증본과 동일(`F138435E3FA69983...`)하고 `production_Config.ini`의
`item_filter_loaded_successfully`도 같은 파일명을 기록한다. 이 리비전은 정적 검증과 라이브 로드를 모두 통과했다.

### 제작 기준서 대조에서 나온 수정 2건

`Docs/POE1_LOOT_FILTER_DESIGN_SYSTEM.md`와 사다리를 대조한 결과:

- §7 미분류 안전망 모양은 `UpsideDownHouse`다. 초기 사다리는 NeverSink 관례를 따라 `Pink Circle`을 썼다. `MinimapIcon 0 Pink UpsideDownHouse`로 교체했다.
- §6.3 C 단계(수집/제작)는 아이콘 크기 2다. T3가 아이콘 1이었다. NeverSink `t4c`의 흰색 등급에 맞춰 `MinimapIcon 2 White Square`로 교체했다.
- §7 카테고리 모양 표에 점술 카드 행이 아예 없었다. 지도와 같은 Square를 공유한다는 실제 구현을 기준서에 추가했다.

남은 기준서 부채(이번 범위 아님): §6.1은 규칙마다 RGB 직접 기입 금지, 메인 컬러 토큰 파생을 요구한다. 사다리는 기존 Pathcraft 블록과 같은 직접 RGB를 쓴다. 토큰화는 §8에 이미 기록된 기존 부채이며 필터 전체 재작성 시점에 함께 처리한다.

### 소스 충돌 해소: NeverSink 경제 티어 vs Wrecker SSF 픽업 목록

첫 사다리는 NeverSink 티어만 근거로 삼았다. 교체 전후를 카드 단위로 재생해 보니 **216장이 소리를 잃고 46장이 작아졌다.** 원인은 Wrecker SSF 원본이 최상위로 지정한 카드(`Bowyer's Dream`, `Baited Expectations`, `Nook's Crown`, `The Awakened` 등)가 NeverSink 기준으로는 `t4`/`t5c`였기 때문이다. 두 소스는 서로 다른 것을 안다. NeverSink는 리그 경제를, Wrecker SSF는 이 플레이어가 실제로 멈춰 서는 카드를 안다.

따라서 배정은 **두 소스 중 더 큰 쪽**을 따른다. `SSF WANTED`(Kidding ME 잔여)와 `SSF NOTABLE`(Absolutely 잔여) 섹션을 경제 티어 사이에 넣었다.

`Don't Care if I Miss Them` 목록은 섹션으로 만들지 않는다. SSF는 어디서 잭팟이 나올지 모르므로 "안 줍는" 등급을 두지 않는다. 해당 카드도 경제 티어로 떨어져 소리와 미니맵 아이콘을 받는다.

교체 후 재생 결과:

- 숨겨진 카드 0장, 무음 카드 0장, 미니맵 아이콘 없는 카드 0장
- 이전 리비전보다 조용해진 카드 0장, 2pt 넘게 작아진 카드 0장
- 470장 전부가 Luminary 사다리 블록에서 종료

검증 스크립트의 초기 블록 파서에도 결함이 있었다. SSF 섹션 블록은 본문이 들여쓰기 없이 flush-left라서 "들여쓰기된 줄만 본문"으로 읽으면 SSF 레이어 전체가 통째로 무시된다. 블록 종료 조건은 들여쓰기가 아니라 **빈 줄**이다. `python/tests/test_luminary_divcard_layer.py`의 파서도 같은 규칙으로 고쳤다.

### 빌드 의존 부분의 분리

필터는 빌드와 무관하게 모든 카드를 표시한다. 빌드가 바꾸는 것은 **중요도(어느 섹션으로 올라가는가)뿐이다.** 그런데 그 빌드 부분이 생성기 코드에 하드코딩돼 있으면 빌드를 바꿀 때 코드를 고쳐야 한다.

빌드 타깃을 `data/filter_build_targets/poe1_luminary_bot_ssf_3_29.json`으로 분리했다. 카드마다 보상 고유·가이드 섹션·사유를 함께 기록한다. 다른 빌드는 같은 모양의 파일을 하나 더 만들어 생성기가 그것을 읽게 하면 되고, 사다리의 나머지 구조는 손대지 않는다.

테스트 2개를 추가했다.

- `test_build_target_file_names_only_real_cards`: JSON의 카드 이름이 실제 존재하는 카드인지 (오타 차단)
- `test_build_emphasis_never_removes_a_card`: 빌드 강조가 카드를 사다리에서 떨어뜨리지 못하는지

`python/tests/test_luminary_divcard_layer.py` 14개 통과.

### 독립 적대검증 결과 (2026-08-19)

fresh 서브에이전트가 "모든 점술 카드가 사다리에서 terminal 규칙 하나로 해소되고 숨겨지지 않는다"를 반박 시도했다. 판정 **SURVIVES**, 결함 3건 보고.

반박 실패한 항목:

- `Class == "Divination Cards"`(복수형)이 맞다. NeverSink 레퍼런스 10개 블록 전부 이 문자열이고, GGPK 467행이 단일 `ItemClassesKey 42`다.
- 사다리 위쪽 terminal 블록 23개(전부 9008+)의 조건은 링크 수·특정 BaseType·Quest/Chart뿐이다. 467개 카드명과 교차 검사해 **충돌 0**. 첫 Hide는 9851줄로 사다리보다 아래다.
- 재생성 스크립트는 사다리를 온전히 보존한다. `AlternateQuality` 절단 로직의 역방향 탐색이 사다리 `Show` 줄에서 멈출 수 있지만, 대상 블록이 Luminary 구간 **뒤** suffix에 있어 발동하지 않는다.
- 생성기 재실행은 자기 출력을 먹지 않는다. 현재 파일로 재생성하면 사다리 171줄이 바이트 단위로 동일하고, 사다리 티어에 손으로 카드를 심어도 유니버스에 들어오지 않는다.

수정한 결함:

- **STACK 3+ 규칙이 catch-all을 가렸다.** 스택 규칙에 BaseType이 없어서, 분류되지 않은 신규 카드가 3장 스택으로 떨어지면 마젠타 경보 대신 조용한 스택 스타일을 받았다. 신규 카드 경보가 필요한 바로 그 상황이다. 스택 규칙 범위를 T4/BULK/LOW 카드 목록으로 한정했다. 검증: 미지의 카드는 스택 1이든 3이든 catch-all로 간다.
- **헤더 주석이 근거보다 과했다.** "GGPK의 모든 카드"라고 썼지만 그 덤프는 3.28 앵커다. 커버리지는 목록 완전성이 아니라 **무조건 catch-all**이 보장한다고 고쳐 적었다.
- **소스 파서가 순서에 취약했다.** `BaseType`이 `Class`보다 먼저 오거나 한 블록에 `BaseType` 줄이 둘이면 놓쳤다. 블록 단위(빈 줄 종료) 파싱으로 교체했다.

수정하지 않고 남기는 것:

- ~~`Energy Sword` 미확인~~ → **해소(2026-08-19)**. 사용자가 3.29 카드임을 확인했다. `Pearls Before Swine`·`Divine Shard`는 poe.ninja Allflame에서 확인. LEAGUE NEW 16장 전부 실재 카드다.
- PowerShell 재생성 스크립트는 cp949 로케일 + PS 5.1 조합에서 파일 내 `U+00F6` 11줄을 깨뜨릴 수 있다. Luminary 구간 밖이고 이번 적용 경로는 Python UTF-8이라 현재는 무해하지만, PS 스크립트로 재생성할 때 확인해야 한다.
- 사다리에 손으로 심은 카드는 재생성 시 사라진다. 정본은 `data/filter_build_targets/`와 소스 레이어이며 이것이 의도된 동작이다.

`python/tests/test_luminary_divcard_layer.py` 15개 통과 (스택-catch-all 회귀 테스트 포함).

### GGPK 3.29 재추출 (2026-08-19)

repo의 `data/game_data/`는 3.28 Mirage 추출본이었다. 라이브 클라이언트(`C:\Program Files (x86)\Grinding Gear Games\Path of Exile\Content.ggpk`, 69.7GB, 2026-08-18)로 재추출했다. 클라 패치 `3.29.3.1.4`, 리그 `3.29 Curse of the Allflame`.

결과: 23/24 테이블 성공. `AttributeRequirements`만 실패했는데 3.28 추출본에도 없던 기존 결함이며 이번 회귀가 아니다. 신규 확보: Quest / UniqueStashTypes / Words / WorldAreas (19 → 23).

점술 카드는 **467 → 470, 추가된 3장이 `Divine Shard` / `Energy Sword` / `Pearls Before Swine`, 제거 0**이다. 필터 소스 합집합으로 메워둔 유니버스와 정확히 일치했고, 사다리를 재생성한 결과 **필터가 바이트 단위로 동일**했다(SHA `F138435E3FA69983` 유지). 즉 3.28 덤프로도 결과는 옳았고, 이제 그 근거가 추정이 아니라 GGPK 실측이 됐다.

추출본이 진짜 3.29임을 확인한 교차 증거: Ascendancy에 **`Luminary`** 추가(20 → 21). 이 빌드가 쓰는 신규 사이온 전직이다. 그 외 Mods +1063, ModType +315, PassiveSkills +114, GemTags 신규 태그 `pact`.

**Truth reference 재앵커**: `anchored_to`를 3.29로 갱신하고 `ggpk_truth_builder.py` 재실행. Layer 2(독립 추출기 `pathofexile-dat`) 는 `_analysis/crosscheck/config.json`의 patch를 `3.29.3.1.4`로 올려 재실행했고, 두 독립 파이프라인이 7개 테이블 전부 일치했다.

이 과정에서 고친 것 3건:

- `.gitignore`에 `Content.ggpk` / `HashCache.dat` 추가. 69GB가 추적 대상이 아니었다.
- `ggpk_truth_builder.py` docstring이 `> _analysis/ggpk_truth_reference.json` 리다이렉트를 안내하는데, 스크립트가 파일을 직접 쓰므로 그렇게 하면 진행 메시지가 방금 쓴 파일을 덮어써 깨진다. 실제로 한 번 깨뜨렸고 docstring을 고쳤다.
- `test_ggpk_index`가 숫자 `stats_key`(6149/3955)를 하드코딩해 3.29에서 6160/3960으로 밀리며 깨졌다. 의미가 아니라 인덱스를 pin한 전형적 함정이라 stat 텍스트 기준으로 재작성했다.

### 재추출이 끌어낸 후속 갱신

전체 스위트를 3.29 데이터로 돌려 3건이 깨졌다. 전부 "데이터가 바뀌었으니 갱신하라"는 설계된 감지였고, 그중 하나는 pin 방식 자체가 문제였다.

- **`test_data_integrity::test_coach_normalizer_loads_without_drift`** — BaseItemTypes 해시 드리프트 감지. 경고 문구가 안내하는 대로 `scripts/refresh_valid_gems.py` 재실행. `valid_gems` 1130 → 1144 (+18 / −4).
  3.29 개명이 데이터로 드러났다: **Dark Pact → Dark Bargain**, **Minion Pact → Communion**. 신규 젬은 Coursing Current / Crystalfall / Divine Blast of Radiance / Chain Hook of Angling 등.
- **`test_sections_continue::test_snapshot_tag_based_classification`** — `scarabs_all` 190 → 194. Trarthan 4종(가이드가 배신 보드에서 언급하는 그 스카랩) + Abyss of Crystals/the Consort 추가, Abyss of Edifice/Profound Depth 제거.
  개수만 pin 하면 **추가와 삭제가 상쇄될 때 못 잡는다.** 개수 갱신에 더해 신규 6종 포함·삭제 2종 부재를 함께 단언하도록 고쳤다.
- **`test_representative_build_board`** — GGPK와 무관한 기존 실패(빌드 코퍼스). 재추출 이전 스위트에서도 동일하게 실패했다.
