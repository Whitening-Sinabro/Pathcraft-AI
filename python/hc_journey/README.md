# HC Journey DB (POE2 하드코어 니치)

크리에이터의 **발행 밴드 PoB + 실캐릭 ninja 스냅샷**을 diff 해서 "따라 할 여정"을 자동으로 만들고,
VOD/자막/연구에서 뽑은 **비용·조건·함정·왜(20%)**를 붙이는 SQLite DB. POE2 하드코어(→이후 SSF) 전용.

## 왜 이 구조인가

임성빈 케이스로 검증한 사실: 밴드 PoB diff만으로 **WHAT/WHEN(무엇을 언제 바꾸나)은 자동 100%** 나온다.
자동이 못 주는 것(전환 비용·조건·함정·오프스트림 구매)이 정확히 **HC/SSF가 가장 원하는 것**이라,
그 20%를 `transition_note`로 물리적으로 분리해 담는다.

## 큐레이션은 초반 창에서만 손으로 한다 — 이후는 규칙이 대신한다

손 큐레이션(`source='hand'`)은 DB가 커지면 노동이 안 따라온다. 그래서 **초반 창에 해야 할 일은 손노트를 다는 게
아니라, 그 지식을 `curation_rule`로 뽑아내는 것**이다. 규칙은 한 번 정의되면 이후 **모든 빌드에 자동 적용**된다:

- `keystone` 규칙 — 그 키스톤을 든 빌드에 자동. (예: 혈마법 = 생명력으로 비용 지불)
- `skill_added` 규칙 — 그 스킬을 쓰는 빌드에 자동. (예: 화염파 = 집중 유지형·요구 지능 높음)
- `support_added` 규칙 — 그 보조 젬을 어느 스킬에든 새로 끼우는 빌드에 자동(diff `support_added`, 새 스킬의 보조 포함). (예: 이글거리는 화염 II = 명중 감폭·점화 증폭)
- `item_slot_change` 규칙 — 그 슬롯 변화가 있는 빌드에 자동. (예: 세트 II 무기 도입 주의)
- `league` 규칙 — 빌드의 리그 모드(`trade` | `ssf`)에 자동, 첫 전환에 한 번. 슬롯 무관 거래 지식(엑잘 + 골드 수수료, 빨간 요구 매물,
  검색 요령)은 여기. SSF 빌드는 `ssf` 키로 갈라져 거래 규칙을 상속하지 않는다(SSF 규칙은 소스가 생기면 추가).
  `league/ssf` 규칙이 0건인 동안 SSF 빌드의 리그 노트는 조용히 0건이다 — SSF 소스를 넣을 때 규칙부터 채운다.

**증명:** Skadoosh는 손노동 0인데도 혈마법·선대의 유대 큐레이션을 규칙에서 **공짜로 상속**했다.
즉 초반에 규칙을 쌓아두면, DB가 커진 뒤 새 크리에이터는 큐레이션을 상속만 받는다. 손노동은 **진짜 그 빌드에만
해당하는 것**(정확한 비용 수치·오프스트림 구매 등)으로 줄어든다.

## 스키마 3층 (`schema.sql`)

1. **정본 게임데이터** — (후속) GGPK 파생 연결. 현재 증명본은 미포함.
2. **빌드·스냅샷** — `creator` / `build` / `snapshot` / `snapshot_skill` / `snapshot_item`.
3. **여정** — `transition` + `transition_change`(자동 diff) + `transition_note`(큐레이션 20%).

`game` 컬럼은 'poe2' 고정이나 이후 POE1 포팅 시 데이터만 추가한다.

## 적재 현황 (다중 크리에이터)

- **임성빈** — 젬링 화염파 → 검은화염 카오스 (Gemling Legionnaire). 손노트 7 + 규칙 상속.
- **Skadoosh** — 워브링어 타락 함성 토템 (Warbringer, Ancestral Bond·Blood Magic). 손노동 0, 규칙 상속만.
- **ds lily** — 기름 유탄 화염파 젬링(Mobalytics 5탭, Lvl 51 트리 탭은 제외). 채널은 HC(릴리리그 운영자)지만 이 빌드의 HC 근거가 없어
  hardcore=0(근거 등급 I, 2026-09-10 에 1→0). 손노동 0.
- **Fubgun** — 화염파 기름 유탄 젬링(Mobalytics 7탭). 하코 표기 미확인이라 hardcore=0. 손노동 0.
- **탱정** — 방패벽 키타바 2.0 (Smith of Kitava). 제작자 PoB 한 세트(poe.ninja pob/28010, 0.5 소프트코어)라 **밴드 1개 = 전환 0**.
  규칙 노트·거래 링크는 전환에 붙으므로 0 이 맞는 동작이고 스냅샷(스킬 11·장비 12칸)만 남는다 — `--query` 와 여정 뷰가 "전환 없음"을 명시한다(조용히 비지 않게).
  하코 근거 없음 → hardcore=0. 0.5.5 실캐릭 PoB 4개(90→94, `deliverables/tangjung_0_5_5_research_2026-09-07/sources/`)는 별도 빌드 적재 후보.
- **Blazeworks** — SSF 모래·화염 진 바라시타 (Disciple of Varashta). Mobalytics 8탭 중 5탭(Lv1-21 대안 3개 중 유탄만, 빈 Min-Maxed 탭 제외) +
  ninja 실캐릭 `Blaze_MinionToWin` 96렙(league 'HC Forbidden Rites' → hardcore=1, 근거 N). 키스톤 Chaos Inoculation. 손노동 0. 원본 zip·ninja JSON = `blazeworks/_source/`.
- **MisoxShiru** — 나비라의 균열 바라시타 리그 스타터. Mobalytics 7탭 전부(막 경계 레벨 힌트). 이 빌드의 HC 근거 없음 → hardcore=0, 리그 `forbidden-rites`. 손노동 0.
- **디넬** — 바라시타 실캐릭(ninja `DNEL-7382` / `디넬바라시타` 98렙, league 'HC Forbidden Rites' → hardcore=1). 플래너 없음 → 밴드 1개(전환 0),
  폴링(`track_poe2_character.py`)이 변화를 잡으면 앞 밴드로. 캐릭터명은 ninja 래더 search API(protobuf, `name=` 필터)로 찾았다.

바라시타 세 제작자(Blazeworks·MisoxShiru·디넬)가 나란히 있어 두 번째 "같은 빌드 대조" 계열이 됐다 — 바라시타 전환이 Blazeworks Lv22-36 / MisoxShiru 2막.

같은 빌드(화염파 젬링) 세 제작자가 나란히 있어 "같은 빌드도 내부가 갈린다"를 DB 가 보여 준다 — 화염파 도입이 임성빈 ACT3-4→엔드게임,
ds lily 47→72, Fubgun 33-51→52. 크리에이터를 늘리면 **자동층(밴드 diff)은 공짜로 커지고, 큐레이션(20%)만 노동**이다 — 4명째도 손노동 0 으로 규칙 67건 상속.

입력 .build 는 `data/hc_journey/creators/<slug>/` 에 커밋된 픽스처(재현 가능). 크리에이터 추가 = 픽스처 넣고 `CREATORS` 에 한 항목.

## 사용

```
python -X utf8 python/hc_journey/build_db.py --build         # DB 생성 + 전체 적재
python -X utf8 python/hc_journey/build_db.py --query         # 전체 빌드 여정
python -X utf8 python/hc_journey/build_db.py --query --id 2  # 특정 빌드
python -X utf8 -m pytest python/tests/test_hc_journey_db.py -q
```

DB 파일 `data/hc_journey/pathcraft_hc.db`는 적재로 재생성되는 산출물이라 git 제외.

## 규칙 자동 초안 (`rule_autodraft.py`) — 규칙 쓰기 자체를 반자동화

규칙을 손으로 쓰는 것이 마지막 병목이라, 전환점 근처 자막에서 규칙 **후보**를 뽑아 승인 대기 파일로 낸다.

```
python -X utf8 python/hc_journey/rule_autodraft.py            # data/hc_journey/rule_candidates.json
python -X utf8 python/hc_journey/rule_autodraft.py --dry-run  # 요약만
python -X utf8 -m pytest python/tests/test_rule_autodraft.py -q
```

- **전환점** = `build_db` 와 같은 diff(`skill_added`·`item_changed`) + 설정(어센던시·키스톤). trigger_key 는 여기서만 온다.
- **시각 앵커** = 사람 판독(`deliverables/.../precision_findings.py` ROWS 의 (영상, 초, 관측)). 판독의 "N레벨"을 forward-fill 해
  전환 시작 레벨 이전 판독은 버리고, 시간순 앞쪽 클러스터(기본 3개)만 본다.
- **신호** = 앵커 전후 90초 자막에서 cost/condition/pitfall/why/survival 정규식. 후보 text 는 자막 **원문 그대로**.
- **정직성**: 자동 자막은 고유명사가 깨지므로 이름을 자막에서 확정하지 않는다(별칭은 판독 검색 힌트일 뿐).
  같은 자막 창이 여러 트리거에 걸리면(스킬 창 판독은 스킬을 전부 나열) 하나에만 귀속하고 나머지는 `also_matches`.
- **신호원 둘**: 자막 창(`evidence.kind=caption`, 신호 줄 ≥2)과 판독 줄(`readout`, 사람이 화면 보고 적은 글이라 한 줄로도 후보 — 1 엑잘·요구 지능 92 같은 화면 수치는 자막에 없다). 판독은 HUD 수치가 매 줄이라 전용 정규식(`READOUT_SIGNALS`, 사건성 낱말만).
- **승인 게이트**: `CURATION_RULES` 를 읽기만 한다. 판정은 `data/hc_journey/rule_decisions.json`(후보 id → adopted/rejected/deferred + 사유 + rule)에 기록하고,
  초안기가 재생성할 때 id 로 병합해 `status` 를 채운다. 채택분만 사람이(또는 위임받은 쪽이) `CURATION_RULES` 에 옮긴다. 테스트가 채택 판정 ↔ 규칙 존재를 대조한다.
  이미 있는 (kind,key,note_type) 은 `existing_rule` 표시.
- 소스는 크리에이터별(`CREATOR_SOURCES`). 소스 없는 크리에이터(Skadoosh)는 후보 0 — 다른 크리에이터의 영상을 빌리지 않는다.

## 거래소 링크 (`trade_links.py`) — "무엇을 사라"를 즉시 구입 링크로, 옵션까지

전환의 `item_changed` 마다 제작자가 그 시점에 낀 아이템(베이스 + 옵션)을 공식 trade2 검색 쿼리로 바꿔 링크를 낸다.

```
python -X utf8 python/hc_journey/trade_links.py --realm both            # ?q= 링크(무상태, 국제+한국) → data/hc_journey/trade_links.json
python -X utf8 python/hc_journey/trade_links.py --creator 임성빈 --live  # 공식 API 에 POST 해 검색 id·매물 수(1.5초 간격)
python -X utf8 -m pytest python/tests/test_trade_links.py -q
```

- **실측이 설계를 정했다**: 같은 베이스 + 옵션 전부 AND 는 HC 온라인 매물 0건, 투구 카테고리 + "6개 중 3개, 60% 하한"은 353건.
  그래서 사다리 — T1 그대로(베이스 + 옵션 전부 80%) → T2 핵심(베이스 + 절반 이상 60%) → T3 같은 부위(카테고리 + 3개 이상 60%).
- **옵션 → 스탯 id** 는 공식 `/api/trade2/data/stats` 인덱스와 정확 일치(숫자→`#`, `+#`→`#`)만. `reduced`↔`increased` 한 번 폴백(음수는 존재만).
  못 맞춘 옵션은 `unmapped` 로 남기고 필터에서 뺀다. 픽스처 167개 중 3개 → 폴백 후 0.
- **베이스 → 카테고리** 는 GGPK `BaseItemTypes.Id` 경로(`/Armours/Helmets/` 등)에서 유도. 유니크는 trade2 items 카탈로그의 이름으로 검색.
- **요구 레벨 상한** = 그 스냅샷의 `level_hint`. 즉시 구입(`status: securable`) 기본. 정렬 가격 오름차순.
- **한국 서버**(`poe.kakaogames.com`)는 별도 시장 — `?q=` 링크는 같지만 검색 id 는 서버별로 POST 해야 한다.
- **속도 제한(2026-09-10 실측 헤더)**: `X-Rate-Limit-Ip: 5:10:60,15:60:300,30:300:1800,600:21600:3600`(요청수:초:벌칙초).
  300초에 30건이 병목이라 지속 간격 약 11초, 6시간 600건. `--live` 는 기본으로 응답 헤더를 읽어 다음 대기를 계산하고(`pace_seconds`),
  429 는 Retry-After 를 지킨다. 정책은 시즌·부하마다 바뀌므로 코드에 숫자를 박지 않는다.
- **live 실측(임성빈 30건, T1·T3)**: T1(베이스+옵션 전부 80%) 8/30 매물 있음, T3(같은 부위) 21/30. 0건은 22레벨 이하 장비와 옵션 3개↑ 조합에 몰림 → T3 를 "2개 이상"으로 완화.
- 캐시 `data/_cache/trade2/`(gitignore, `--refresh` 로 갱신). 산출물 `trade_links.json` 은 재생성 가능.
- **DB**: `build_db.py --build` 가 `trade_links.json`(+ `trade_links_live_*.json` 의 검색 id·매물 수)을 읽어 `trade_target`(변화당 아이템 사실)
  + `trade_link`(단계×서버 링크)에 넣는다. 파일이 없으면 두 테이블만 비고 적재는 그대로 — 적재는 네트워크·캐시 없이 돈다.
  `--query` 는 슬롯마다 `🛒 Helm1 Hallowed Crown (요구≤93) T1 · T2 · T3` 로 요약하고 URL 은 `trade_link.url` 에 있다.

## 여정 뷰 (`render_journey.py`)

```
python -X utf8 python/hc_journey/render_journey.py --open        # data/hc_journey/journey.html (gitignore, 재생성)
python -X utf8 python/hc_journey/render_journey.py --id 1
```

빌드마다 타임라인 → 전환 카드(자동 diff 접힘 · 손/규칙 노트 · 🛒 거래 링크 T1/T2/T3 국제/한국, 요구 레벨 상한).
목차(`journey.html`)에는 같은 전직 빌드가 2개 이상일 때 **핵심 스킬 도입 시점 대조표**(제작자 × 스킬 → 전환·요구 레벨)가 붙는다.
매물 수는 live 검색 시각이 24시간 안일 때만 표시. 스타일은 문서 규칙(흑백 + 강조 1색, rgb, 시스템 폰트, 그라데이션·그림자 없음).

## 다음

- 크리에이터 다수 적재: 소스 매트릭스 `.claude/status/hc_creator_sourcing.md`(후보·정체성·플래너·HC 근거·우선순위·허락 목록)를 따라
  허락받은 것부터 밴드 PoB·ninja ID 를 받아 적재. 명부는 `.claude/status/poe2_hardcore_sources.md`.
- 규칙 후보 승인 루프: `rule_candidates.json` 검토 → 채택분을 `CURATION_RULES` 로. 판독(사람 검증 텍스트)도 신호원으로 쓸지 결정.
- 정본 게임데이터(Layer 1) 연결: 스킬/아이템/트리 노드 → GGPK 파생.
- 그다음 UI/API.
