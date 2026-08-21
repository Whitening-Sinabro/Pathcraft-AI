## Phase 0: Tauri + Python sidecar ✅
- [x] Tauri 프로젝트 초기화
- [x] Python sidecar 연결 (Tauri Command ↔ Python)
- [x] 기존 Python 코드 정리 (19개 살림, 나머지 _archive)
- [x] data/ 폴더 복구

## Phase 1: 빌드 코치 핵심
- [x] POB 파싱 CLI (pob_parser.py URL 인자 추가)
- [x] AI 코치 모듈 (build_coach.py → Claude Sonnet)
- [x] 아키타입 자동 감지 (dot/attack/spell/minion)
- [x] 아키타입별 레벨링/오라/저주 데이터 로드
- [x] 퀘스트 젬 보상 데이터 연동
- [x] Wiki Cargo API 연동 (wiki_data_provider.py)
  - [x] 유니크 드롭 제한/chanceable 조회
  - [x] 디비니 카드 + 드롭 맵 조회
  - [x] 리그 접두어 정규화 (Foulborn 등)
- [x] Tauri UI (빌드 분석 + 코칭 결과 카드)
- [x] print → logger 교체 + UTF-8 인코딩 수정
- [x] 프롬프트 보강 (오라/유틸리티/전령 구간별, 보이드스톤, 장비 타이밍, 10구간)
- [x] UI에 leveling_skills 섹션 표시
- [x] 빌드 평가 5카테고리 별점 (PoE Vault 패턴)
- [x] 장비 진행 타임라인 (슬롯별 카드 흐름)
- [x] 맵 모드 경고 + regex 필터
- [x] 구간별 스냅샷 탭 (Mobalytics 패턴)
- [x] 파밍 전략 (타겟 맵 추천)
- [x] 필터 생성 (SSF 모드 — 디비카/유니크/chanceable/엄격도 Hide/UI)

## Phase 2: OAuth + 프로필 추적
- [ ] GGG OAuth 2.1 연동 (기존 승인 활용)
- [ ] 프로필 상태 읽기
- [ ] 변화 감지 → 전략 자동 조정

## Phase 3: 확장
- [ ] 크래프팅 가이드
- [ ] 보스별 전략
- [ ] Trade 리그 모드 (가격 표시 전환)
- [ ] 수익화 (티어/도네이션)

## 기존 코드 정리
- [ ] 필터 3세대 → Phase 8만 남기고 아카이브
- [ ] 레거시 파일 ~15개 정리
- [ ] 번역 데이터 5개 → merged_translations.json 기준 정리
- [ ] 젬 데이터 이원화 해소 (gems.json 단일 소스)

## Phase F 감사 Fix (2026-04-19 F2+F7 감사 결과)
- [x] **F7-fix-1 (🔴)** — `data/mod_pool.json` → `_archive/phase_f_legacy/` (2026-04-19 완료)
- [x] **F7-fix-2 (🔴)** — `scripts/extract_id_mod_filtering.py` 신설 + `_meta` 완비 (2026-04-19 완료). 기존 데이터 5 mod 오분류 정정 (Boots/Gloves/Helmets의 Carbonising 등 스펠 mod 제거)
- [x] **F7-fix-3 (🟡)** — `t1_craft_bases.json` `_meta`에 source_urls/verified_at/poe_league/collection_method/review_cadence 추가 (2026-04-19 완료)
- [x] **F7-fix-4 (🟡)** — `HIGH_FOSSILS` + `OILS_*` 출처 주석 보강 (2026-04-19 완료)
- [x] **F2-fix-1 (🟡)** — `_EXCEPTIONAL` / `_UNIQUE_FRAGMENTS` 출처 주석 추가 (2026-04-19 완료, F2 감사 근거 명시)
- [x] **F2-fix-2 (🟡)** — `layer_endgame_content` / `layer_stacked_currency` 스모크 (이미 기존 `TestLayerEndgameContent.test_signature_basetypes` + `test_p1_base_routed` 파라미터화 커버 확인, 신규 작업 불필요)
- [x] **F3a-fix-1 (🔴)** — `farming_mechanics.json` + `farming_strategies.json` + `farming_strategy_system.py` (1450 lines) → `_archive/phase_f_legacy/` (2026-04-19 완료)
- [x] **F3a-fix-3 (🟡)** — `Inscribed Ultimatum` 주석에 Cobalt 8.19.x / GGPK 확인 추가 (2026-04-19)
- [x] **F3b-fix-1 (🟡)** — `_HEIST_OBJECTIVES` 출처 주석 (GGPK 47/47, Heist 3.12) (2026-04-19)
- [x] **F3b-fix-2 (🟡)** — `_HEIST_HANDPICKED_AREAS` 선정 근거 주석 (Wreckers L937 + Wiki) (2026-04-19)
- [x] **F4-fix-1 (🔴)** — `sanavi_tier_data.json` + `sanavi_tier_parser.py` → `_archive/phase_f_legacy/` (2026-04-19 완료)
- [x] **F5-fix-1 (🟡)** — `syndicate_layouts.json` `_meta`에 source/source_url/verified_at/poe_league 추가 (2026-04-19)
- [x] **Phase F legacy cleanup 묶음** — 6 파일 `_archive/phase_f_legacy/` 완료 (2026-04-19, README 첨부, 535 pytest PASS)

## 빌드 생성 (novel build origination) — 미착수
> 계기: 2026-08-19 MAGEFIST "Chaos Herald of Thunder Pathfinder" (`poedb.tw/pob/GXoW7hsWd6`).
> 요구는 기존 빌드 분석이 아니라 **없던 빌드를 새로 고안해 내는 것**.

관측된 목표 퀄리티 (저 영상이 실제로 갖춘 것):
- 축 발견 — Herald of Thunder 는 입력 없이 발동한다 → "walking simulator". 거기에 카오스 스케일링을 얹음
- 진행 경로 — 제로 → 히어로, 레벨링·장비 단계
- 자금 조달 — Incursion + Heist 로 필요한 고유 아이템 값을 번다
- 실측 — 리그를 실제로 돌려 찍은 연재 (Part 1, 2 …)

우리 자산 대비 격차:
- [x] 스킬 성질 원본 — `active_skill_types.json` (GGPK ActiveSkillTypes = PoB SkillType enum)
- [x] 속성·유니크 원본 — GGPK 파생 Mods / ModType / BaseItemTypes
- [x] 기존 빌드 코퍼스 500+ (중복 판별용)
- [x] 아틀라스 메커니즘 42 + 갑충석 계열 (자금 조달 설계는 우리 본진)
- [x] 기존 PoB 의 수치 읽기 — export 에 `<PlayerStat>` 이 박혀 있고 `pob_parser` 가 읽는다
- [ ] **아직 없는 조합의 수치** — export 가 없으므로 PoB 를 실제로 돌려야 한다

설계 결정 (재논쟁 방지):
- **데미지 수식을 우리가 구현하지 않는다.** PoB 를 채점기로 쓴다.
  후보 빌드 → PoB import 코드 생성 → PoB 계산 → 수치 회수 → 후보 선별.
  PoE 전환 사슬·more/increased·태그 상속을 재구현하는 건 PoB 를 다시 만드는 일이다.

단계:
1. 조합 탐색기 — "입력 없이 발동 × 피해 전환 × 스케일러" 를 GGPK 에서 기계적으로 교차
2. 코퍼스 대조 — 이미 알려진 조합 제거, 남는 것이 후보
3. PoB 헤드리스 왕복 — 후보를 PoB 로 채점 (이 단계가 미구현)

선행 조건 (발견된 구멍):
- delivery 축이 자동 발동형을 표현 못 함 → 그 축으로 탐색이 불가능했다. **이번에 착수**
- damage element 를 메인 스킬 *이름만* 보고 판정 → 보조 젬(Void Manipulation)·고유 아이템에 의한
  실제 피해 타입을 못 본다. 카오스 빌드를 lightning 으로 라벨함. **미착수**
- CWDT 로 굴리는 빌드도 같은 사각 — 메인 그룹의 트리거 보조 젬을 delivery 근거로 못 씀. **미착수**

## 크리에이터 감시 배관 (기확인, 미연결)
- `D:/discord-admin/` 에 `YOUTUBE_API_KEY` + `poe-build-watch.mjs` / `poe-creator-discovery.mjs` 가 이미 있다.
- 경로: YT API 신규 영상 → 설명에서 PoB 링크 추출 → base64url+zlib 해제 → `pob_parser` → 택소노미 레이블링.
- poedb.tw/pob 은 `/raw` 로 PoB 코드를 그대로 준다. 기존 수집기는 pobb.in / pastebin 만 안다 — poedb 미지원.

### A안 착수 지점 (네트워크 복구 후 여기서 재개)
목표: **PoB 를 채점기로 세운다.** 이게 빌드 생성의 유일한 병목.

1. PoB Community 소스 확보 — `PathOfBuildingCommunity/PathOfBuilding`.
   레포는 이미 `extract_gem_damage_types.py` / `extract_gem_weapon_reqs.py` 에서
   `raw.githubusercontent.com/.../master/src/Data/Skills/` 를 받아 쓰고 있다(전체 소스는 미보유).
2. `HeadlessWrapper.lua` 가 루트에 있는지 **실물 확인** — 아직 추정이다. 없으면 이 경로는 재설계.
3. LuaJIT 설치 (이 PC 에 lua/luajit 없음, winget 사용 가능).
4. MAGEFIST PoB(`poedb.tw/pob/GXoW7hsWd6`)를 헤드리스로 먹인다.

**PASS 조건 (이것 하나뿐)**: 헤드리스 결과가 아래를 재현하는가.
`CombinedDPS 7,094,854` / `Life 3,338` / `Evasion 9,280`
정답 숫자를 이미 갖고 있으므로 "대충 비슷"은 없다. 재현 실패면 이 경로를 버린다.

막힌 지점(2026-08-19): 이 PC 네트워크가 WinError 10055(소켓 버퍼/큐 고갈)로 전면 불능.
github 뿐 아니라 직전까지 되던 poedb.tw 도 실패. 호스트 차단이 아니라 머신 레벨 문제.
