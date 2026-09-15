# Skadoosh 9/14 방송(VOD 2874116335) 뒤 공개 스냅샷 대조

- VOD `2874116335` — 2026-09-14T17:14:34Z 시작, 3:26:55. 제목은 이전 방송들과 같은
  `0.5.5 HC OG Warbringer Corrupting Cry Totems !Builds Come an…`
- `creator_latest.json` — poe.ninja `latest` 조회(계정 ITheCon-2183 · SkadooshShoutedHard ·
  hc-forbidden-rites). `updatedUtc = 2026-09-14T20:37:19Z` 로 **방송 종료 직후 상태**다.
- `live_pob_lv90.xml` — 위 응답의 `pathOfBuildingExport`(base64url + zlib)를 푼 것.
- `diff_character.py` — 88레벨(9/12 갱신) 스냅샷과 대조한다.

## 88 → 90 에서 실제로 바뀐 것

젬
- 지진 함성에 **Magnified Area II 유지** — 89레벨 관측이 이틀 뒤에도 그대로다.
- 레벨만 오름: 선대의 혼백 19→20 · 지면 분쇄 18→19 · 비취에 갇힘 19→20. Sunder 퀄리티 0→20.
- 패시브 111 → 113 (전직 8 · 각인 1 은 그대로).

장비 — 세 슬롯이 바뀌었지만 **실질 교체는 갑옷 하나**다.
- 투구: 88 스냅샷은 크래프트 **전** 투구(Noble Greathelm)였고, 90 스냅샷이 9/12 방송에서 만든
  그 투구(Imperial Greathelm · 방어도 749 · Q20 · ilvl 80 · 타락)다. 가이드에 적은 수치와 같다 —
  방어도 67% · 생명력 +139 · 냉기 36% · 방어도 37% 원소 적용 · 함성 시 생명력 5% 회복 ·
  함성 피해 59%. 추가로 룬 모드: 카오스 저항 13% · "Bonded: 근접 타격 시 격노 2 획득".
- 장갑: 88 은 화염 피해를 더하는 Detailed Mitts, 90 은 Massive Mitts(방어도 74% · 생명력 +140 ·
  마나 +56 · 근접 스킬 +2 · 냉기 30%). 가이드가 적은 "직전 장갑의 화염 추가는 버렸다"가 이것이다.
- 갑옷: Elegant Plate(방어도 +92 · 정신력 +42 · 재생 16.2) → **Ornate Plate**(생명력 +196 ·
  정신력 +47 · 냉기 31% · **방어도 38% 원소 적용** · 재생 23.9). 이번 방송의 새 정보다.

## 파서 함정 (다음에 또 걸린다)

이 스냅샷의 장비 모드는 `explicitMods` 가 **비어 있고** `desecratedMods` 에 들어 있다.
`explicitMods` 만 읽으면 투구가 "모드 없는 아이템"으로 보여서 "그가 크래프트 투구를 버렸다"는
정반대 결론이 나온다. 보조 젬 이름도 `allGems[].name` 이 아니라 소켓된 아이템의 `typeLine` 이다.
`diff_character.py` 는 두 가지를 모두 처리한다 — 이전 폴더의 같은 이름 스크립트는 구버전
응답 구조(`itemData.socketedItems` + `explicitMods`)를 가정해서 이 스냅샷에서는 빈 결과를 낸다.

## 방송 전사 (기존 파이프라인 그대로)

- `fetch_chat.py` → `chat.json` / `chat.txt` — 150건, 42요청(300초 재시드). 시청자 중 Palsteron·CeinorZero
  가 방어도·정신력을 놓고 대화한다. Nightbot 이 올린 빌드 목록의 워브링어 주소가
  `mobalytics.gg/poe-2/builds/corrupting-cry-warbringer-skadoosh` 로, 우리가 캡처한 배포 가이드 주소와 같다.
- `transcribe.py` → `chunks/` + `transcript.txt` + `asr_coverage.json` — 12415.7초 전 구간(1200초 창 11개,
  겹침 5초), 세그먼트 134. 앞 30분은 대부분 WoW 클래식 베타 잡담이고 빌드 이야기는 01:10 이후에 몰려 있다.
- `verify_windows.py` → `verified_asr/` — VAD 끄고 3구간 재전사.
  `body_armour_ornate`(00:42:40~00:46:00) · `boots_shopping`(00:50:40~00:55:40) ·
  `armour_break_weapon_swap`(01:11:10~01:14:20).

### 전사에서 나온 것

**갑옷을 왜 바꿨나.** 발화 시각이 다르니 붙여 읽지 않는다 — 00:43:31 `There we go or Nate`("Ornate"의
ASR 오인식, 고르는 순간) · 00:43:40 `This thing is good.` · **00:43:51 `It's more spirit, less HP, bit more.`**
· 00:44:34 `I got 2% regen as well.` · 00:44:59 `Way too much cold res, which is a good thing.` ·
00:45:02 `I need to turn something into lightning.`
→ 본인 말은 "정신력 더, 생명력 덜". **실물과 갈린다**: 아이템 기여 생명력은 직전 갑옷이 룬 60 + 제작 113 +
Bonded 20 = 193, 새 갑옷이 접두 196 으로 사실상 같다. 실제로 오른 것은 방어도 612 → 997, 정신력 42 → 47,
재생 16.2 → 23.9(+ 암시 1.85%/s), 원소 적용 27% → 38% 다. 빠진 것은 Bonded 생명력·마나 룬이고 새로
들어온 것은 피격 치명타 피해 50% 감소 룬이다. "생명력 덜"이 무엇과 비교한 말인지는 확정하지 못했다 — 교체 직전에 무엇을 입고 있었는지 관측한
스냅샷이 없다. 대조본(88레벨)은 `updatedUtc 2026-09-11T23:03Z` 로 사흘 전이고, 그 사이 투구도 바뀌었다.

**방어도 파괴를 누가 하나(01:12:08).** ASR 원문 그대로: `I stun with Seismic Cry, which means I also break
armor` / `with Scavenger's Plating. It's not my totems that break armor. It's me that break armor.` /
`means i always get scavenged bugging stacks that's from uh this anoint here` / `lettering blow`.
뒤 두 줄의 `scavenged bugging`·`lettering blow` 는 오인식이다 — 90레벨 목걸이의 `enchantMods` 가
`Allocates Shattering Blow` 이고, 9/12 방송에서도 같은 성유를 원문으로 읽는다. 교정 전 원문을 남긴다.
→ 9/12 기록과 같은 말을 이틀 뒤 다시 했다. 기절원이 지진 함성이라는 것까지 명시했다.

**무기 세트 구조(01:12:41).** "I'm using two scepters. So I weapon swap, put down my totem, which is a
scepter and a mace, and then I war cry with a shield and a scepter. I always have the spirit I need for my
totems, but I gain the benefit by having a shield as well."
→ 이 문서의 05~07 세트 I(셉터+방패, 함성) / 세트 II(철퇴+셉터, 토템) 구성과 같다.

**회복 축(01:11:51).** "I recover tons of life with Urgent Call and my helmet, so I have 5% max life when I
use the Warcry." → 07 투구 목표 2순위(함성 사용 시 생명력 4~5% 회복)가 실제 회복의 축이라는 확인이다.

**시장 관찰(01:13:20).** ASR 원문: `life builds are you don't see people playing life builds at all the
hardcore like gear i have is` / `like i i would consider really good and it's just so cheap because nobody
plays this shit`. ("내가 보기엔 꽤 좋은 축"이라는 유보가 원문에 있다.) 핀나클 보스는 아직 피한다(01:11:26).

## 안 한 것

프레임 추출은 하지 않았다. 이번 회차의 질문(장비 교체 사유·방어도 파괴 주체)은 전사와 공개 스냅샷으로
답이 나왔고, 화면으로만 읽히는 수치를 물은 항목이 없었다.
