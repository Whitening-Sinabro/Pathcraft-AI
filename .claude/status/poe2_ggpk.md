# POE2 GGPK 추출 — 운용 메모

## 추출 커맨드 (자동 탐지는 실패한다)

폴더명이 `Path of Exile 2 - poe2_production` 이라 자동 탐지가 못 찾는다. 경로를 직접 준다.

```
src-tauri/target/release/extract_data.exe --game poe2 "<설치경로>" --json
```

## 2026-09-04 추출 결과

- **23/24 성공, 총 62,019행.** 실패 1건은 `ScarabTypes` — POE1 전용이라 POE2 에 없다(4월과 동일).
- `_.index.bin`: 113,945,065B 압축 -> 147,899,533B, 565 청크, compressor=12.
- **번들 61,214 · 파일 4,227,128 · 디렉토리 95,255 · MurmurHash64A.**
- 스키마 드리프트 경고는 0.4 스키마로 0.5 데이터를 읽어서 나는 것.

## 지금 데이터는 0.5 시점이지 0.5.5 가 아니다

0.5.5 신규 영혼핵 17종(Jiquani's 13 · Atziri's 4)이 `BaseItemTypes` 에 없다.
영혼핵 자체는 40개 다 있는데 신규만 빠졌다.

**9/5 05:00 KST 리그 시작 후 클라이언트가 다시 패치하면 재추출할 것.** 그때 17종이
나오면 0.5.5 데이터가 맞고, 하코 문서의 "신규 영혼핵 17종 효과 미확인" 행을 채울 수 있다.

## 추출이 안 될 때 — 먼저 이걸 본다

2026-09-04 에 원인을 두 번 오진했다(리더 결함 -> 포맷 변경). **둘 다 틀렸고 실제 원인은
중단된 패치였다.** 8/30 에 인덱스 포함 72,878개 파일을 큐에 넣고 받다가 연결이 끊겨 있었다.
게임 클라이언트로 다시 받으니 그대로 풀렸다.

판별법: GGPK 의 FILE 레코드는 내용의 SHA256 을 32바이트로 들고 있는데, **패치가 덜 받아진
파일은 그 자리가 전부 0** 이다. 리버싱하기 전에 이걸 먼저 확인한다.

```
python scripts/ggpk_explore.py verify Bundles2
python scripts/ggpk_explore.py verify Bundles2/_.index.bin --deep
```

## 한국어명은 이 경로로 못 푼다

추출본에 한국어 문자열이 없다(영문 클라이언트). 중재자 등 한국어명은 poe2db/kr 이나
인게임 확인이 필요하다.

## 재추출이 파생 DB 를 낡게 만든다 (2026-09-04 실측)

`data/game_data_poe2/` 는 **gitignore** 라 git 이 드리프트를 못 본다. 9/4 재추출로
`SkillGems.json` / `BaseItemTypes.json` 이 갱신됐는데 `data/valid_gems_poe2.json` 은
**4월 22일자** 그대로다. 그래서 지금 이 테스트 1건이 빨간불이다:

    test_valid_gems_poe2_categories.py::TestMetaGemsInActiveCategory
      -> GemType=2 메타 젬 3건 없음: Animus Splinters · Hollow Form · Spirit Vessel

**재생성하면 어떻게 되는지 실측해 봤다** (`python scripts/build_valid_gems_poe2.py`):

    active   420 -> 475  (+55)
    support  592 -> 624  (+33, -1 Shock Conduction I)
    spirit     2 ->   3  (+1 Spirit Vessel)

빠져 있던 젬이 88개다. 다만 **재생성은 연쇄를 일으킨다** — 통과하던 3건이 빨간불이 된다:

    test_build_poe2_planner_files.py::TestGemPaths::test_only_two_gems_are_missing_from_the_table
    test_build_poe2_planner_files.py::TestGemPaths::test_gem_missing_from_the_stale_table_keeps_pobs_plural_form
    test_derived_data_inventory.py::test_pinned_content_hash_matches_current_scan

앞의 둘은 플래너 젬 표의 검증된 핀이고, 셋째는 파생 DB staleness 게이트가 설계대로
작동한 것이다(`--accept-ggpk-change` 로 받는다).

**그래서 지금은 재생성하지 않고 되돌렸다.** 지금 데이터가 0.5 시점이라 9/5 0.5.5
재추출 후에 어차피 다시 해야 하고, 핀 3개를 두 번 갱신하면 두 번째가 "테스트를
초록으로 만들려고 핀을 고친" 것과 구분되지 않는다. **재추출 직후 한 번에 처리할 것** —
재생성 -> 플래너 핀 2건이 왜 바뀌는지 확인 -> `--accept-ggpk-change`.

## 9/5 0.5.5 재추출 직후 처리 목록 (한 번에)

재추출로 `data/game_data_poe2/` 가 갱신되면 파생 DB 두 개가 같이 낡는다.
**두 번 갱신하지 말고 재추출 직후 한 묶음으로 처리한다** — 핀을 두 번 고치면
두 번째가 "테스트를 초록으로 만들려고 핀을 고친 것"과 구분되지 않는다.

1. **`data/valid_gems_poe2.json`** — `python scripts/build_valid_gems_poe2.py`
   - 젬 88개가 돌아온다(active +55 · support +33 · spirit +1, -1 Shock Conduction I)
   - 그 뒤 빨간불 3건을 확인하고 받는다:
     `test_build_poe2_planner_files.py::TestGemPaths` 2건(플래너 젬 표 핀 — 왜 바뀌는지 먼저 확인),
     `test_derived_data_inventory.py::test_pinned_content_hash_matches_current_scan`(`--accept-ggpk-change`)

2. **`data/base_items_poe2.json`** (4/25, GGPK BaseItemTypes + AttributeRequirements JOIN)
   - **`Runeforged *` 가 0종**인데 GGPK 에는 **535종** 있다(메타데이터가 `...Verisium` 으로 끝나는 별개 베이스).
   - 이것 때문에 하코 필터의 어휘 게이트가 fubgun·ds lily 의 마감 장비
     (Runeforged Cryptic Crown / Adherent Cuffs / Cryptic Leggings / Falconer's Jacket /
     Commander Gauntlets / Sombre Gloves)를 막았고, 지금은 룬각인 안 된 쌍둥이 베이스로 대체해 뒀다.
   - 갱신 후 `scratchpad/make_hc_spec.py` 의 `ENDGAME_ARMOUR` 에 룬각인 이름을 되살리고 재빌드.
   - **급하지 않다** — 룬각인은 최후 엔드게임 장비다(사용자 판단 2026-09-04).

3. 재추출 자체가 성공했는지: 0.5.5 신규 영혼핵 17종(Jiquani's 13 · Atziri's 4)이
   `BaseItemTypes` 에 나오는지로 확인한다. 안 나오면 아직 0.5 데이터다.
