# 임성빈 엔드게임 빌드플래너 (Lv93 검은화염 카오스)

첫날 유탄/화염파 사본(DAY1_1/2/3)과 별개로, **9/9 이후 검은화염 카오스로 완성된 실제 엔드게임 빌드**를 실캐릭 export로 뽑은 플래너다. 연구 조각으로 트리를 지어내지 않고 poe.ninja 실측 export를 정본으로 썼다.

## 파일

| 파일 | 용도 |
|---|---|
| `임성빈 엔드게임 Lv93 검은화염 카오스.build` | repo 표준 .build(패시브 151·스킬 14·장비 15). 검증기(import_poe2_planner_files.py) 통과 |
| `임성빈_엔드게임_실캐릭.pob.xml` | **Path of Building에 바로 import** 가능한 원본 PoB export |
| `endgame_source/ninja_lv93_*.json` | poe.ninja character API 원본 응답(스킬·장비·키스톤·주얼·방어 스탯) |

## 출처와 시점

- 계정 `dtq03087-0345` · 캐릭터 `임성빈_화염파_젬링` · 리그 `hc-forbidden-rites`
- poe.ninja `latest` 엔드포인트(브라우저 없이 폴링됨). export는 base64url+zlib.
- 조회 시점 **레벨 93**. 클래스 **Gemling Legionnaire(젬링)**. 방어 스탯: 생명력 1962 · 에너지 보호막 3081 · 정신력 100 · 저항 화75/냉72/번75/**카오스65**.

## 정지 화면 연구와 실캐릭 export 교차검증 (전부 일치)

- 키스톤 **Blackflame Covenant**(검은화염 계약) = 화염 주문 화염 피해 100% 카오스 전환. (연구: E8876·F75)
- **Virtuous Barrier**(고결한 방어막) 보유 = 버프 줄 빨강·초록·파랑 **티끌**의 원천(힘=생명력, 민첩=방어/ES, 지능=재생). Gemling 전직 스킬. (연구: D19306)
- 세트II **Chiming Staff**(용의 돛대) = 모든 주문 레벨+5·동결 축적78%·상태 이상 강도56%·피해47% 추가 화염. (연구: F2400)
- 갑옷 **The Mutable Star - Cleric Vestments**(변이하는 별). (연구: C1531·C9172)
- 발동 메타 **Cast on Elemental Ailment**(원소 상태 이상 시 시전) + Contagion(전염)·Magnified Area·Efficiency·Acrimony. (연구: F207·F115 전염 후보 → 실제 보조로 채택)
- 저주 **Despair**(절망), **Tornado**(회오리), **Infernal Cry**(지옥불 함성), **Arctic Armour**(극지 갑주=동결 공급), 충격파 토템, 쇠뇌 사격, 기름/섬광 유탄 — 연구 스킬 목록과 일치.

## 주의

- 이 export는 **레벨 93 현재 상태**다. 9/9(F, 레벨 91) 방송 시점과 보조 젬 일부가 다르다(예: 원소 상태 이상 시 시전 보조가 에너지 유지·무한한 에너지 II → Contagion·Magnified Area 등으로 진화). 방송 시점 구성은 첫날/전환 사본과 원본_정밀확인.md를 본다.
- 첫날 사본(DAY1_1/2/3)과 원본 .build는 유탄/화염파 육성 기준이라 이 엔드게임과 다르다. 육성 순서는 그쪽, 완성형은 이 파일.
- Virtuous Barrier 젬만 GGPK 0.4.0d 표에 없어 PoB 경로를 그대로 썼다(전직 스킬이라 정상).
