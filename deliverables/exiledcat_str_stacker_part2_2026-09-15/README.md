# Exiled Cat — SSF Strength Stacker Part 2 (3.29) 확인

우리 `Docs/2026-08-28_EXILEDCAT_SSF_STRENGTH_STACKER_JUGGERNAUT_3_29_GUIDE_DOC.html` 는
"**Part 2 미공개**"로 적고 여러 항목을 "Part 2 예고 / 대기 검증"으로 남겨 뒀다. 그 Part 2 가 나왔다.

- 영상 `edhq1gFj7BQ` — **2026-09-06** 공개, 19:10.
  `How To Make SSF Strength Stacker - From Zero to Hero | Part 2 | Path of Exile 3.29`
  (Part 1 `Oo7j-hC1ELk` 는 2026-08-27, 20:09 — 우리 가이드가 쓴 그 영상이다.)
- 채널 열거로만 찾았다(검색 0회): `yt-dlp --flat-playlist https://www.youtube.com/@ExiledCat_PoE/videos`.
- `part2.txt` — 자동 자막(en-orig) 388줄, 00:19:07 까지. `to_text.py` 는 임성빈 폴더 것 재사용.
- `pob_replica.xml` — 설명란에 **새로 추가된 다섯 번째 PoB** `pobb.in/ayV-9wM2AxAx` (Replica) 를
  base64url + zlib 로 푼 것. Part 1 설명란엔 PoB 4개뿐이었다.

## 이건 "또" 가 맞다 — 리그마다 내는 SSF 스태커 시리즈

채널 전체 148편을 열거해 확인했다. `From Zero to Hero` SSF 스태커 시리즈는 리그마다 나온다.

| 리그 | 시리즈 | 편수 |
|---|---|---|
| 3.25 | SSF **Juggernaut Armour** Stacker | Part 1~3 |
| 3.26 | SSF **Champion Armour** Stacker | Part 1~3 |
| 3.28 | SSF **Life** Stacker Gladiator | Part 1~2 |
| 3.29 | SSF **Strength** Stacker (주가노트) | Part 1~2 |

3.27(Phrecia)만 스태커가 없고 Architect of Chaos 계열로 갔다. 3.25 도 주가노트였으니 이번 3.29 는
같은 어센던시로 돌아온 것이다. **다음 리그에도 SSF 스태커가 나온다고 보고 소싱 케이던스를 잡을 수 있다.**

## 예고로 남겼던 항목의 결말

| 8/28 가이드가 남긴 것 | Part 2 결과 |
|---|---|
| Legion 타임리스 주얼 (Lethal Pride) | **확인.** 아틀라스를 Legion 으로 돌려 emblem 을 모으고(00:01:34~01:42) 3-way Legion 을 돌아 **Lethal Pride 를 두 개** 얻는다(00:02:38, 00:03:00). 최종 PoB 에 장착돼 있다 |
| Large/Medium 클러스터 주얼 | **확인.** 클러스터 때문에 Delirium 을 돈다(00:04:11). **대형 클러스터 3개**가 필요하다고 말한다(00:10:36~10:48) |
| Harvest 제작 (계획, 미실행이었음) | **확인.** 속성 리포지·juice·하베스트 보스까지 실제 운용으로 나온다(00:16:21~17:14) |
| The Iron Fortress (대기 검증) | **최종 PoB 에 장착.** 다만 **자막에서는 이름을 한 번도 말하지 않는다** — 화면·PoB 로만 확인된다 |
| 레벨 98 | **PoB level 98.** 영상에서는 99 까지 올린다고 말한다(00:14:42, 00:15:14) |
| Blight 성유·촉매 | **언급 0.** Part 2 에서 다루지 않는다 |
| Delirium Split Personality | **언급 0.** Delirium 은 클러스터·시뮬라크럼 용도로만 나온다 |

## 최종(Replica) PoB 의 고유 아이템

Juggernaut / Marauder, level 98. 고유 7종:

| 아이템 | 베이스 |
|---|---|
| Lethal Pride | Timeless Jewel |
| Kalandra's Touch | Ring |
| Foulborn Meginord's Girdle | Heavy Belt |
| The Iron Fortress | Crusader Plate |
| Crown of Eyes | Hubris Circlet |
| Paradoxica | Vaal Rapier |
| Replica Alberon's Warpath | Soldier Boots |

그 밖에 자막에는 Headhunter 복제본 두 번째 사본(00:09:41), Paradoxica 를 쓰게 해 주는 슬롯
구성(00:13:10), 이미 Mageblood 를 갖고 있다는 언급(00:16:01)이 있다.

## 우리 필터 스펙과의 차이

`data/filter_build_targets/poe1_exiledcat_ssf_strength_stacker_juggernaut_3_29.json` 의
`unique_targets` 8개와 대조했다.

- **6/7 은 이미 덮고 있다** — Replica Alberon's Warpath · Crown of Eyes · Foulborn Meginord's Girdle ·
  The Iron Fortress · Paradoxica · Lethal Pride.
- **누락 1건: `Kalandra's Touch`(Ring).** 스펙 어디에도 없다. 그가 최종 빌드에서 실제로 끼고 있다.
- **`Lethal Pride` 는 `optional` 이고 `unresolved_targets` 에도 들어 있다.** Part 2 에서 직접 얻어
  장착하는 것이 확인됐으므로 `required` 로 올릴 근거가 생겼다.

이 두 가지는 필터 산출물을 바꾸므로 여기서는 기록만 하고 적용하지 않았다.
