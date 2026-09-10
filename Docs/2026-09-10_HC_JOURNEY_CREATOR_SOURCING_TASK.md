# HC 여정 DB #2 — 크리에이터 소싱·적재 플랜 (다음 세션 실행 지시)

사용자 지시(2026-09-10): "hc 스트리머·유튜버 찾아서 DB 쌓을 계획 세워봐. HCSSF·HC 상관하지 말고."
이 문서는 그 세션의 실행 지시다. 요약이나 계획만 쓰고 멈추지 말고, **플랜 문서 + 첫 적재**까지 간다.

작업 폴더 D:/Pathcraft-AI. master 최신 = `7f09ed9`. 소싱은 외부(유튜브·Mobalytics·poe.ninja)를 건드리므로
다운로드는 사용자 허락이 필요하고, 크리에이터 이름·리그 플래그는 근거 없이 적지 않는다.

## 먼저 읽기

1. 메모리 `project_hc_journey_db`(제품 축) · `project_hc_journey_rule_autodraft`(규칙 초안·판정·support_added·크리에이터 4명)
   · `project_hc_trade_link_strategy`(거래 API 는 검증 탐침만) · `feedback_find_people_by_identity`(제목 말고 정체성으로)
   · `project_poe2_hardcore_sources`(명부 함정) · `project_creator_sourcing_backlog`(발견=discord-admin YT API, 추출=PathcraftAI).
2. `python/hc_journey/README.md` — 적재 현황 4명, 규칙 27, 트리거(keystone·skill_added·support_added·item_slot_change·ascendancy·league),
   거래 링크, 여정 뷰. `build_db.py` 의 `CREATORS` 가 적재 입력 스펙이다.
3. `.claude/status/poe2_hardcore_sources.md` — 이미 확보한 명부(채널 URL·ID·빌드 계열·자막 파일). **여기서 시작**하고 새로 검색하지 않는다.
4. `scripts/import_poe2_planner_files.py`(Mobalytics/PoB export → 레포 표준 `.build`) · `scripts/track_poe2_character.py`(poe.ninja 실캐릭 폴링·전환 레벨 보존본).

## 지금 상태 (인계)

- DB: 크리에이터 4(임성빈·Skadoosh·ds lily·Fubgun) · 스냅샷 21 · 전환 17 · 규칙 27 · 규칙 노트 82 · 손노트 7 · 거래 링크 466(live 43).
- 4명째도 손노동 0 으로 규칙을 상속했다 — 크리에이터를 늘리면 자동층은 공짜, 큐레이션은 규칙 상속. 즉 **병목은 소싱**이다.
- 로컬에 이미 있는 미적재 플래너: `build_planner/Kitava Endgame 2.0 - Tangjeong.build`(1밴드, 전환 없음), `Ignite * - Arserina.build`(소프트코어 점화, 5밴드).

## 크리에이터 1명을 적재하는 데 필요한 것 (입력 스펙)

| 항목 | 필수 | 어디서 | 없으면 |
|------|------|--------|--------|
| 밴드 플래너 ≥2 (`.build`) | 예 | Mobalytics "Export to game"·인게임 플래너·PoB 코드 → `import_poe2_planner_files.py` | ninja 실캐릭 1밴드만 → 전환 0. `track_poe2_character.py` 폴링으로 전환 레벨 보존본을 만들어 밴드로 쓴다 |
| ninja 계정·캐릭터 | 권장 | poe.ninja 캐릭터 페이지(키스톤·실캐릭 스냅샷) | 키스톤 규칙 못 붙음(비워 둔다, 지어내지 않음) |
| 이름·채널 URL·리그·HC/SSF | 예 | 명부·본인 발언·리그명 | HC 플래그를 근거 없이 1로 두지 말 것(Fubgun 은 0 + 노트) |
| 자막·판독 | 선택 | `data/_cache/subs/`, 판독은 브라우저 캡처 | 규칙 후보 없음(상속만) |

## 이번에 만들 것

1. **소스 매트릭스** `.claude/status/hc_creator_sourcing.md` — 명부의 크리에이터를 전부 행으로: 이름(정체성으로 확정한 채널 URL/ID) · 언어 ·
   빌드 계열/전직 · HC/HCSSF/사설리그(근거) · 플래너 있나(Mobalytics 링크 등) · ninja 있나 · 자막 있나 · 적재 우선순위 · 필요한 허락(다운로드).
   후보 ≥10명, HC/HCSSF 섞어서. 검색은 하지 말고 명부 + 채널 열거(yt-dlp `--flat-playlist`, `PYTHONIOENCODING=utf-8`)로.
2. **우선순위 규칙**: ① 밴드 플래너가 공개된 사람(자동층 공짜) ② 다른 빌드 계열(젬링 3명은 충분 — 바라시타·키타바·인보커·리치 등) ③ ninja 만 있는 사람은
   폴링으로 밴드를 만들 수 있을 때만 ④ 한국어 소스는 자막 판독까지 가능하니 규칙 후보 가치가 높다.
3. **첫 적재 3명 선정 + 허락 목록** — 각자 무엇을 내려받아야 하는지(파일명·출처 URL·크기)를 적어 사용자에게 한 번에 묻는다. 허락 전엔 내려받지 않는다.
4. 허락 없이 되는 것은 바로: `Kitava Endgame 2.0 - Tangjeong.build` 를 1밴드로 적재해 파이프라인이 전환 0 빌드를 어떻게 다루는지 확인
   (전환 없으면 규칙·링크도 없다 — 그게 맞는 동작인지 결정).
5. 적재 파이프라인(1명당): 픽스처 복사 `data/hc_journey/creators/<slug>/` → `CREATORS` 항목 → `build_db.py --build` → 상속 규칙 확인(`--query`)
   → `trade_links.py --realm both` → `render_journey.py` → 테스트(크리에이터 수는 CREATORS 에 묶여 있어 리터럴 수정 불필요) → 커밋.

## DoD

- `.claude/status/hc_creator_sourcing.md` 에 후보 ≥10명 매트릭스 + 우선순위 + 첫 3명 + 허락 목록.
- 허락 없이 가능한 적재 1건 이상 완료(예: Tangjeong 1밴드) 또는 그것이 무의미한 이유를 문서에 기록.
- 새 크리에이터가 손노동 0 으로 규칙을 상속하는지 `--query` 로 확인, 테스트 green, 커밋·푸시(master), Co-Authored-By + Claude-Session.

## 경계

- 자막으로 고유명사 확정 금지(이름은 채널·PoB·GGPK). 제목 키워드로 사람 찾지 말 것(하코를 하는 사람이 제목에 하코를 안 쓴다).
- 거래 API 는 검증 탐침만(헤더 페이싱, 429 Retry-After 준수). 제품은 `?q=` 링크.
- 스키마 변경·다운로드·외부 게시는 사용자 확인 뒤. `.db`·`journey*.html` 은 산출물(gitignore).
- 규칙 텍스트를 새로 쓰면 적대검증(1차에서 오독 2건 잡힌 전력).
