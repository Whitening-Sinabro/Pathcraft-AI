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

## 안 한 것

오디오 전사는 하지 않았다. 공개 스냅샷만으로 "무엇이 바뀌었나"가 전부 나왔고, 남은 질문은
"왜 갑옷을 바꿨나" 하나다. 그 이유가 필요해지면 방송 구간 전사로 확인한다.
