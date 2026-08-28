# Exiled Cat SSF Strength Stacker Juggernaut 3.29 — 필터

- 산출물: `filters/ExiledCat_SSF_Strength_Stacker_Juggernaut_3.29_Progressive.filter` (레벨 1~100 자동 진행형 1개)
- 설치: `C:\Users\User\Documents\My Games\Path of Exile\` 동일 파일명 (2026-08-28, sha256 `474EBDD8…`)
- 스펙(정본): `data/filter_build_targets/poe1_exiledcat_ssf_strength_stacker_juggernaut_3_29.json`
- 근거 가이드: `Docs/2026-08-28_EXILEDCAT_SSF_STRENGTH_STACKER_JUGGERNAUT_3_29_GUIDE_DOC.html` 7장(필터에 띄울 베이스) — 스펙의 모든 타깃은 가이드 장·행을 `source_section` 으로 인용한다. 9장(비제작자 출처) 유래 항목은 그렇게 표기했다.

## 빌드·검증

```powershell
python scripts/build_smokiezone_hcssf_filter.py --spec data/filter_build_targets/poe1_exiledcat_ssf_strength_stacker_juggernaut_3_29.json --install
python -m pytest python/tests/test_build_exiledcat_ssf_filter.py python/tests/test_build_smokiezone_hcssf_filter.py -q
```

빌더는 2026-08-28 부터 **스펙 주도**다: 라벨(`labels.creator/mode/layer_title/filter_title`), 로컬 소스 해시(`source.local_source_hashes`), 생존 레이어의 무기 클래스(`progression.safety_weapon_classes`), 연구 임계값(`crafting_base_groups[].progression_key`), 필수 마커 목록이 전부 JSON 에서 나온다. Smokiezone HCSSF 스펙은 기본값이며 재빌드 결과는 헤더/주석과 식별 투구 블록 라벨(`IDENTIFIED BUILD.LATE.HELMET.INFAMY`) 외 규칙 동일.

검증 게이트(빌드 실패 조건): 3.29 GGPK `BaseItemTypes`/`ActiveSkills` 에 없는 이름, Wrecker SSF Hide 블록 87개 변경, 생성 블록이 배경만 칠하고 글자색 미소유, 캐스케이드 대비 < 1.6(`scripts/filter_cascade.py`, 장비 아키타입 전수), 사운드 파일 부재, Hide 블록의 소리/빔/아이콘 누출.

## 이 필터가 띄우는 것 (Exiled Cat 전용 레이어)

| 구분 | 규칙 | 가이드 근거 |
|---|---|---|
| 핵심 고유 베이스 (최상단 알림) | 미감정 Unique: Ritual Sceptre(Brutus' Lead Sprinkler) · Soldier Boots(Alberon's / Replica) · Hubris Circlet(Crown of Eyes) · Heavy Belt(Meginord's Girdle) · Amber Amulet(Xoph's Blood) · Crusader Plate(The Iron Fortress) · Vaal Rapier(Paradoxica) | 3.1 / 3.3 / 4.1·4.2 / 5.2 / 5.3 |
| 선택 고유 베이스 (조용히) | Timeless Jewel — Part 2 예고 Lethal Pride, 다른 타임리스 주얼도 같이 표시 | 5.5 / 9.6 |
| 제작 베이스 (항상 표시, Normal/Magic/Rare 각각) | Ancient·Walnut Spirit Shield(주문 피해 방패), Goliath·Leviathan Gauntlets, Amethyst·Two-Stone Ring | 0 피해 변환 사슬 / 4.1·4.2 / 8.1·8.2·8.3 |
| 제작 베이스 (조용히) | Astral Plate(AreaLevel ≤ 82, 전환기 갑옷), Large/Medium Cluster Jewel(Part 2) | 4.1 / 5.5 |
| 자원 | Cyaxan's Ducat · Crystallised Lifeforce 3종 · Rogue's Marker / Eldritch Ember·Ichor 8종 / Essence of Rage·Greed / Breachstone·Splinter·Wombgift / Blueprints(전부) · Contracts(조용히) | 8.1·8.2 / 4.2 임플리싯 / 5.1·5.3·9.5 / 5.2 |
| 젬 | Smite(변형 Smite of Divine Judgement) 필수 / Sunder / Fire Penetration · EDwA · Multistrike · Inspiration | 3.2 / 2.1~2.4 |
| 플라스크 | Diamond · Granite · Quicksilver · Eternal Life Flask · Prismatic Tincture (품질 10+, 레드맵까지, 엔드게임 조용히) | 4.1 / 7 |
| 점술 카드 | 빌드 타깃 The Watcher(Crown of Eyes) / 보관 Burning Blood(Xoph's Blood) — 나머지 470장은 NeverSink 8.20.1d 경제 + Wrecker 선호 사다리 | 3.3 / 7 / poedb |
| SC SSF 생존 | 희귀 방어구·장신구 AreaLevel ≤ 82 까지 표시(제작자가 전환 후 반지·장갑을 새로 제작함). 무기는 고유라 희귀 무기 클래스 없음 | 8.1·8.2 |

공통 레이어(6링크, 5링크, 캠페인 4링크, 퀘스트/차트/Dead Man's Sulphur, NeverSink T0/T1 고유·화폐, 에센스 시각 사다리, 두루마리/기본 화폐 진행)는 Smokiezone 필터와 같은 Violet Velvet 토큰이다.

## 미해결 (필터 규칙으로 안 만든 것)

- **Allflame Ember(DEX→STR 변환)** — 영상 15:20 이 구체적 Ember 이름을 말하지 않음. Allflame Ember 베이스 20종 이상이라 추측 금지.
- **Deception 계약** — 계약 직업은 필터 언어에 노출되지 않음. Contracts 전체를 조용히 표시.
- **Lethal Pride 시드** — SSF 는 시드 선택 불가. Timeless Jewel 베이스만 선택 고유로.
- 에센스 종류(Rage=힘, Greed=생명력)는 영상이 말하지 않아 게임 데이터 기준 선택 — 스펙 `source_section` 에 명시.

## 인게임 미검증

라벨 가독성은 캐스케이드 시뮬레이터 + 프로브 9종(Unique Ritual Sceptre lvl 28, Soldier Boots, Hubris Circlet, Crusader Plate, Timeless Jewel, Rare Amethyst Ring, Normal Walnut Spirit Shield, Magic Leviathan Gauntlets, Rare Astral Plate)으로만 확인했다. 실물 드롭 확인은 사용자 영역.
