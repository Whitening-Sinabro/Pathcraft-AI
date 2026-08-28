## 2026-08-28 — Exiled Cat SSF Strength Stacker Juggernaut(3.29 Part 1) 가이드 납품

**지금**: 원고 `Docs/2026-08-28_EXILEDCAT_SSF_STRENGTH_STACKER_JUGGERNAUT_3_29_GUIDE_DOC.html`(0~8장 + 출처 + **9장 보강(비제작자 출처)**) →
사용자 계정 Google Doc `https://docs.google.com/document/d/1kOH5Q5v9iy1ECuUwru9hEJ-JnXxi8mlcTsS7WwHqV2c/edit` (다크 페이지 + 밝은 글자, 새로고침 검증 완료).
근거 = 영상 자동자막(20:09) + pobb.in PoB 4개 실파싱. adversarial-verifier 17건 반영. 9장은 리서치 에이전트 결과(Maxroll/poedb/poe-atlas 등, 행마다 URL·신뢰도), poewiki 차단으로 정본 미확인 항목은 "미확인" 표기. 9장 fresh adversarial-verifier(URL 실접속) REFUTED 7건 정정(PoE2 0.5 수치 제거, 변칙 조건 패치노트 확정, Heist 15% 임플리싯 재귀속, Black Market 문구 축소, graph blood 14:21, Paradoxica 한손 티어, URL 누락 보완) → 문서 전체 재주입 완료.
**필터(2026-08-28)**: `filters/ExiledCat_SSF_Strength_Stacker_Juggernaut_3.29_Progressive.filter` 생성·설치(sha 474EBDD8…). 빌더 `scripts/build_smokiezone_hcssf_filter.py` 를 스펙 주도(`--spec`, labels/local_source_hashes/safety_weapon_classes/progression_key)로 일반화 — Smokiezone 재빌드는 헤더·식별 투구 라벨만 변경, 규칙 동일. 필터 적대검증(fresh verifier) REFUTED 5건 반영: 빌더 REQUIRED_TARGET_IDS pin(스펙 자기참조 검증 해소), 시뮬레이터 Hide+Continue fallthrough·boolean 오파싱 수정, OPTIONAL 고유 블록을 경제 티어 앞으로(Timeless Jewel dead code), 카드 주석 생성, 문서 과장 정정. 테스트 26 passed(뮤테이션 6 + 시뮬 회귀 포함). 상세 `Docs/2026-08-28_EXILEDCAT_SSF_STRENGTH_STACKER_FILTER.md`. 인게임 라벨 확인은 사용자 영역.
**다음**: 사용자 검토(문서·필터 인게임). Exiled Cat Part 2 공개 시 5.5/6장 + 스펙(타임리스/클러스터) 갱신. 수정 시 HTML 고치고 재주입([[reference-google-docs-delivery-via-browser]] — 페이지 색은 키보드 선택만 됨).

---

## 2026-08-28 — 필터 라벨 글자=배경 충돌 수정 (Unique Crude Bow 신고)

**지금**: 원인 = Continue 캐스케이드(Death Oath 고유 티어 갈색 배경 + Smokiezone 글자색 가드). 수정: 가드 4종 제거(젬만 유지),
`Rarity Unique` 마젠타 센티널 → ORDINARY UNIQUE DEFAULT 치환, 무조건 센티널 제거, 배경 칠하는 생성 블록은 희귀도별 분할로 글자색 소유,
`scripts/filter_cascade.py` 시뮬레이터가 검증 게이트(아키타입 4,548 조합 대비<1.6 → 빌드 실패). 재빌드·설치 완료(sha 021A04CD…).
**다음**: 인게임 재확인(사용자). 남은 sub-2.5 대비 4건은 허용 범위 — 신고 시 조정.

---

## 2026-08-27 — Smokiezone Boneshatter 가이드를 문서형(Google Docs)으로 재납품

**지금**: 시트 트래커가 아니라 Path of Chores 루미너리 가이드식 0~8장 문서를 원했던 것. 원고
`Docs/2026-08-27_SMOKIEZONE_HYDROSPHERE_BONESHATTER_3_29_SSF_GUIDE_DOC.html` → 사용자 계정 Google Doc
`https://docs.google.com/document/d/1wS6VWfSAhukqzuT3Nvr6XixlTu5OMgklwCWLu2lxM4w/edit` (2026-08-28 표 중심으로 재구성한 최신본; 이전 100yeA0… 문서는 휴지통).
PoB 4개(934b0/936d2/9386f/93dc2) 실파싱 근거. adversarial-verifier 13건 지적 전부 반영(탭3 Molten Shell[off]·Momentum 없음,
플라스크 Turf Moss=감전 회피, VMS[off], 근거 없는 설명문 삭제, 전직 순서 추정 제거, 필터 Essence 명시 대상만).

**다음**: 사용자 검토 후 수정 요청 시 HTML 고치고 재주입(절차 [[reference-google-docs-delivery-via-browser]], 형식 지시 [[feedback-guide-doc-format]]). 2026-08-28 반영: 표 중심 재구성, 다크 페이지, PoB 표 전체 URL — 사용자 OK.
시트 트래커(xlsx + 생성 스크립트)는 사용자 지시로 삭제·푸시 완료(2026-08-28).

**블로커**: 없음. 8월 작업 전부 커밋·푸시 완료.

---

## 2026-08-21 — 갑충석 생성기 적대검증 결함 3건 해결

**지금**: `51a6e92`에 남긴 결함 3건 전부 해결.
1. 갑충석 우주를 이름 필터에서 `Metadata/Items/Scarabs/` 네임스페이스 + `scarab` 태그
   합집합으로 교체. 198 = 현행 130 + 구 티어 64 + Bestiary Lure 4로 전수 분류.
2. `Uniques` 갑충석은 Unique Maps와 의미가 다르므로 아틀라스 조인을 명시적으로 `null` 처리.
3. 테스트 우주를 GGPK 구조로 독립 정의하고, 태그 없는 Lure 4개와 전수 합계를 회귀 가드화.
   반복 우주 계산으로 생긴 일시적 성능 회귀도 제거(갑충석 테스트 약 1.7초).

**검증**: 갑충석+파생 인벤토리 49 passed. 전체 Python **1440 passed / 1 failed**.
실패 1건은 기존 red `test_representative_build_board_marks_3_28_shock_nova_confirmed`
(`near_confirmed != confirmed`)와 동일하며 이번 변경과 무관.

**착지**: 관련 변경을 `3edf2ae`~`ba35ef3` 5개 로컬 커밋으로 확정. 워킹 트리 clean,
미푸시. 다음 세션은 backlog의 **빌드 생성 A안(PoB 헤드리스 채점기 실물 검증)** 또는
사용자 지정 주제로 시작한다.

---

## 2026-08-20 — 필터 카드 시각 분리 + 가이드 docx 3차 교정

**지금**: 둘 다 착지. 워킹 트리 미커밋.
1. 필터 — 점술 카드 사다리 13블록 라벨 배경을 청록 전용화(화폐·유니크 붉은 계열과 분리).
   `python/luminary_divcard_layer.py` → `apply_luminary_divcard_layer.py` 로 3곳 동기
   (레포 / 게임 설치본 / Downloads, md5 `bbef45ac753b`).
2. 가이드 docx — 표 27개·셀 533개 + 본문 전수 대조. 산출물
   `C:/Users/User/Downloads/(POE용어 3차교정) …docx` + 같은 이름 대조표.
   재번역 534 / 용어 치환 126, 미적용 0. 전역 스윕 0건(존댓말·~요체·번역투·조사).
   입력은 `(POE용어 교정 번역)` docx 고정 — 이 판본만 문단 804로 영문과 1:1 정렬.

**다음**: ① 갑충석 계열 결함 3건(`51a6e92`) — 2026-08-21 해결 완료.
② 이번 변경 커밋(미커밋 12 + 신규 3).

**블로커**: 없음. **인게임 검증 미완**(사용자 영역) — 카드 시안 팔레트 실물 확인 대기.

**미해결(요청 범위 밖이라 손 안 댐)**: T0/T1 카드 알림음이 아직 화폐와 같다
(`HolyMotherfuckingShit.mp3` / `Thatsworthsomething.mp3`).
카드 Cyan 빛기둥이 변신·각성 젬과 겹친다 — 11개 열거색이 전부 사용 중이라 감수한 값
(근거는 `luminary_divcard_layer.py` 상단 주석, 재논쟁 금지).

**가이드 해석 주의**: 4.x 장비표에 유니크가 적혀 있다고 **필수가 아니다**.
p37 원문 = "The build functions unique-less" — 닉타의 등불·로리의 등불 전부 선택이다.
실제 요구는 **최대 생명력 → 시야 반경** 스탯 두 개. 시야 반경은 희귀템 접미어
`Of Radiance`(시야 반경/전역 정확도 15%)와 패시브 트리 40%(p139)로 채운다.
p700 = 로리 2개는 임시, **최종형은 오히려 희귀 주색 반지**. 수정 셉터 DropLevel 41 이라
골드 도박은 레벨 41 부캐가 최적(레벨 오를수록 셉터 풀이 커져 지분이 떨어진다).
3.29 골드 도박 확률표는 GGG 미공개 — 레포·웹 모두 근거 없음.

**세션 함정은 메모리로 이관, 여기선 포인터만**:
[[reference_poe_filter_block_parsing]] · [[feedback_mt_source_no_authorial_intent]] ·
[[project_guide_docx_retranslation]] · [[reference_poe_korean_terms_from_repo]]

---

## 2026-08-19 — 점술 카드 전수 사다리 + GGPK 3.29 재추출

**지금**: 필터 점술 카드 470장을 Luminary 사다리 13섹션(terminal Show)으로 재편 완료. 빌드 타깃은
`data/filter_build_targets/`로 분리. GGPK를 3.29(클라 3.29.3.1.4)로 재추출하고 truth reference 재앵커 + Layer 2 교차검증 통과.

**지금(2)**: 8월 미커밋 56건을 7개 레이어 커밋으로 확정 완료(`15551d7`~`38ea611`). 워킹 트리 clean, 미푸시.
빌드 택소노미 v2 착지 — 주체 4 + 정체성 축 6 + v1 이관 맵 + 픽스처 8빌드. 테스트 **1193 passed / 1 failed**(기존 red).

**지금(3)**: 자동 레이블러 착지(`af27b75`~`4d128b8`). 메인 스킬 판정은 PoB `mainSocketGroup` 기준 61/63.
축 커버리지(63빌드): delivery 62 / defense 62 / 원소 40 / range 33확정+21후보. 테스트 **1247 passed / 1 failed**.
GGPK `ActiveSkillTypes` = PoB `SkillType` enum 확인 → PoB Lua 불필요. 상세 → 메모리 [[reference-ggpk-active-skill-types]].

**지금(4)**: 지식 소스 레지스트리 외부화(`8f53c5b`, 죽은 소스 4건 적발) + 팩 선언 블록(`ccf81cf`).
어댑터는 미착수 — `cws_knowledge`(특정 크리에이터 모듈)가 파이프라인 본체 노릇을 하는 구조라 그 위에 얹는 방향을 폐기했다.

**다음 세션 = GGPK 파생 DB 정리 (근본 원인).** 계획서:
`~/.claude/projects/D--Pathcraft-AI/2026-08-19-derived-db-from-ggpk-handoff.md`
- 오늘 오진 7건이 전부 같은 원인: 파생 JSON에 생성경로·drift 감지가 없다. 상세 → 메모리 [[project-derived-db-drift-root-cause]]
- 3.29 실측: 아틀라스 메커니즘 **42개**(`PassiveSkills.AtlasGroup`) / 갑충석 **28계열 130종**(`Scarabs`+`BaseItemTypes`, 미분류 66)
- `atlas_farming_knowledge.json` 은 10개만 앎. `atlastree-export`·`farming_meta` 는 stale
- 전략 선택 키: archetype 폐기 → 메커니즘별 `applies_to`(택소노미 v2 축 + phase + econ). 기존 signals 17개 중 축 어휘와 맞는 건 5개뿐
- 미조사: 갑충석 슬롯 수, 공허석 0~4 게이트, 미분류 갑충석 66
- 순서: ①파생 JSON 전수 인벤토리 → ②메커니즘/갑충석 생성기 → ③staleness 테스트 → ④슬롯·게이트 리서치 → ⑤applies_to 재작성 → ⑥지식 어댑터
- 이월: `weapon` 축, 지식 파이프라인 어댑터

**블로커**: 없음.

**문서 포인터**: `Docs/2026-08-19_LUMINARY_BOT_SSF_ATLAS_TREE_AND_BETRAYAL.md` — Path of Chores 가이드 §5.1(첫 아틀라스 트리) poeplanner 4단계 실측 + 배신 보드 조작 절차 + 오역 교정표 + 필터 반영 현황. **필터 조치 불필요**: 균열 소비 아이템 커버리지 전수 확인 완료. `Hiveblood`는 BaseItemTypes에 없는 스탯 이름이라 필터 대상 자체가 아니고, `Growing Wombgift`는 3.29 GGPK에서도 루트 상속 + 태그 없음 = 미출시 스텁이라 계속 제외가 맞다.

**알려진 기존 실패(이번 작업 무관)**: `test_representative_build_board_marks_3_28_shock_nova_confirmed` — 빌드 코퍼스 쪽, 재추출 이전부터 red.

---

## 2026-07-18 Handoff — CWS 가이드 재설계 완료 + 별건 fix (미커밋)

**이번 세션 = POE1 CWS 가이드 구조 재설계 (완료, master 병합).**
- 크리에이터 빌드가이드 = **단일 템플릿** `poe1_external_guide_source` (JSON). 하드코딩 dict 소멸.
  템플릿 `data/guide_sources/_template.poe1_external_guide_source.json`, 인스턴스 CWS + zeeboub.
  검증기+투영기 `python/cws_guide_loader.py`. 다음 가이드는 JSON만 추가. 상세 → 메모리 [[project-build-guide-template]].
- master 커밋 `c1c7072`~`41911c7` (9커밋) + `84a017a` (Pohx RF Chieftain PoB `pobb.in/Sit6hlQU1uuZ`
  레벨링 링크 추가, 87+ 스왑 게이트 강화). 전체 스위트 1092 passed / 0 failed.
- 설계·플랜 문서: `~/.claude/projects/D--Pathcraft-AI/2026-07-17-cws-guide-structure-redesign-{design,plan}.md`.

**[2026-07-18 S2] build-corpus WIP 전체 커밋 완료 (5 레이어 커밋, 로컬 only, 미푸시).**
`06207d4` chore(gitignore) → `953d918` data(코퍼스 41MB) → `58c46bd` rust(+993) →
`14e952e` python(46 신규모듈 + 2 fix) → `7ccac32` ui(+3026). 별건 2 fix 포함:
- PoB probe 패치 누수 fix (커밋 `14e952e`). 상세 → 메모리 [[project-pob-probe-patch-leak]].
- 잠복 스냅샷 단언 fix 4파일 (커밋 `14e952e`). 상세 → [[project-snapshot-assert-trap]].
제외(gitignore): `data/ggpk_derived/`(69MB 재생성) · `tmp/` · `data/.claude/` · 검증 png.
스위트 1091 passed / 1 fail(env: `data/game_data/` gitignore 부재, 회귀 아님).

**아래 2026-07-17 핸드오프 숫자 정정** (그대로 두면 스냅샷 단언 함정 재발):
- expanded queue `161→163`, 3.28 `21→23` (누적, 정상).
- 골렘 `3.28_poison_carrion_golem_witch` = 3.28 direct PoB 3개 확보로 `ready_for_pob_parse` 승격됨
  (line 14 의 `needs_direct_pob_link`/3.26-only 기술은 낡음). 3.26 PoB 는 이제 패치 가드로 3.28 후보 승격 불가.

---

## 2026-07-17 Handoff — POE1 Build Corpus Collection
- 현재 큰 목표는 `3.22`부터 `3.29`까지 실제 빌드를 넓게 수집해서 Pathcraft AI 전용 build corpus / candidate queue / source evidence DB로 정리하는 것.
- 다음 세션은 특정 빌드 하나를 고정하지 말고 `래딧 / 커뮤니티 / 빌드 사이트 / 유튜브 / PoB 링크 / 패치노트 / poe.ninja류`를 같이 보며 부족한 빌드군을 계속 채우는 수집 세션으로 시작한다.
- 기존 데이터 축: `data/build_corpus_collection_targets_v1.json`, `data/build_corpus_expanded_collection_queue_v1.json`, `data/build_variant_collection_queue_v1.json`, `data/build_variant_real_cases_v1.json`, `data/build_corpus_manual_pob_sources_v1.json`, `data/guide_sources/`.
- 목표 구조는 단순 인기 빌드 5개가 아니라 `archetype / sub_archetype / variant / phase_state / source_evidence / patch_delta / item_mod_pressure / passive_tree_shape / farming_fit`까지 파생 DB로 연결하는 것.
- 이번 이어가기에서 수동 PoB source를 `6 -> 28`건으로 늘렸고, promoted artifact는 `6 -> 50`, promoted state snapshot은 `83 -> 403`으로 갱신했다. 세부 기록은 `Docs/2026-07-08_BUILD_CORPUS_PROGRESS_REPORT.md`의 `2026-07-17 Manual PoB Source Expansion` 섹션.
- poe.ninja 빌드 탭은 같은 archetype 안의 사람별 커스터마이징을 보는 `variant_evidence_candidate` 소스로 분리했다. 계약 파일은 `data/poe_ninja_build_variant_sampling_plan_v1.json`, 레벨링 caveat는 `Docs/POE1_LEVELING_CONFIRMATION_PACK.md`에 반영했다.
- poe.ninja evidence 큐는 `data/poe_ninja_build_variant_evidence_queue_v1.json`로 추가했고, 레벨링 route family 계획은 `data/poe1_leveling_archetype_route_plan_v1.json`로 추가했다. caster/minion/totem은 3.27~3.28 stage PoB 근거가 강하고, ranger hit bow/melee 최신화는 추가 stage PoB가 필요하다. mine lane은 Hexblast가 아니라 `Exsanguinate/Reap Miner Trickster` 기준이며, Cptn Garbage / Maxroll Exsanguinate Miner Trickster를 1순위 source hunt로 둔다. 토리센세는 mine 보조 확인과 소환수/Spectre creator source로 별도 추적한다.
- creator-first 수집 레지스트리는 `data/poe1_creator_source_registry_v1.json`로 추가했다. CWS=`emiracle`, mine=`Cptn Garbage/Jorgen/Conner Converse/FearlessDumb0`, experimental=`CaptainLance9`, minion=`GhazzyTV/토리센세/Dconnic`, HC=`Zizaran`, one-build specialists=`POEGuy/ZeeBoub/Sanavixx`. `Goblin`은 검색상 Goblin-Inc가 유력하지만 POE1 source로 쓰기 전 확인 필요.
- 최신 promotion 상태: manual PoB source `33`, direct PoB candidate `68`, promoted artifact `57`, state snapshot `501`. `3.28` mine transition slot은 `Exsanguinate Reap Mines Trickster`로 교체했고, Exsang mine 7개 PoB + 토리센세 Spectre 1개 PoB가 parser 검증을 통과했다.
- `poe1_representative_build_profiles.latest.json`에 `3.28_exsanguinate_reap_mines_trickster` supplemental profile을 추가했다. 3.28 Shadow Trickster + `Exsanguinate Mine` + confirmed leveling required smoke에서 `Plan A / plan_a_exact`로 선택된다. 추천 API는 이제 `selected_profile` / 후보별 `profile_summary`로 leveling route, passive direction, source evidence를 UI에 전달한다.
- `poe_ninja_build_variant_evidence_queue_v1.json`에는 creator source track 10개를 추가했다: CWS/emiracle, mine/Jorgen+Conner+Cptn+Fearless, experimental/CaptainLance9, minion/Ghazzy+토리센세+Dconnic, current Tori Poison Carrion Golem, HC/Zizaran, variety/Goblin, one-build specialists.
- 2026-07-17 correction: 수집 queue는 패치당 20개 상한이 아니라 최소 baseline이다. 새 후보는 기존 후보를 빼지 않고 누적한다. `3.28_poison_carrion_golem_witch`를 추가했고 `3.28_volatile_dead_spellslinger_necromancer`는 유지했다. expanded queue는 `161`, 3.28은 `21`개.
- 토리센세 current-season minion lane은 사용자 제보 기준 `Poison Carrion Golem`로 분리했다. 과거 공개 reference는 3.26 영상/PoB `https://pobb.in/Gji0uiu1Aoog`; 이번 시즌 direct PoB는 아직 `needs_direct_pob_link`.
- creator registry는 `34`명으로 확장했다. 추가 discovery set: Kankar, anime princess, LLYD, Palsteron, Fubgun, Ruetoo, Crouching_Tuna, Big Ducks, subtractem, Pohx, Jungroan, Goratha, Tatiantel2, Ventrua, Ben_, Steelmage, Carn, ds lily, Mathil, Travic.
- 현재 작업 범위에서 POE2는 일단 보류한다. POE1 build corpus 추천 UI 연결, 전략/레벨링 상태 표시 수정, POE1 passive tree 개선 1차는 완료했다.
- 방금 이야기한 Spectre 약화와 Dominating Blow 가능성은 전체 수집 작업 안의 `3.29 minion lane` 부분 발견일 뿐이다. `Dominating Blow Guardian`은 후보로 올리되, 다음 세션의 주 작업은 전체 빌드 콜렉트와 근거 정규화다.
- 세부 기록: `Docs/2026-07-08_BUILD_CORPUS_PROGRESS_REPORT.md`의 `2026-07-17 Handoff: Continue Corpus Collection` 섹션, `Docs/2026-07-16_SCION_RELIQUARIAN_3_29_RESEARCH.md`의 `2026-07-17 Subfinding: 3.29 Minion Lane` 섹션.

## 지금
- **[2026-07-18 S2] build-corpus WIP 전체를 5 레이어 커밋으로 확정** (상단 핸드오프 참조). 로컬 only, 미푸시. 유실 리스크 해소.
- 다음 세션 = 코퍼스 추가 수집 재개 (아래 "다음 할 것" 3) 또는 커밋된 backend/frontend 컴파일 헬스 확인.
- **이전 세션 (S12, 2026-04-26)**: POE2 패시브 트리 거미줄 부분 해소 + 갭 매핑 (8-에이전트 분석)
  - **근본 원인 1 (data)**: PoB-PoE2 `tree_0_4.json` 의 `groups` 가 sparse list (1497 슬롯 중 16 null). `normalizePoe2Tree` 가 null 슬롯도 그대로 인덱싱 → `TypeError: Cannot read properties of null (reading 'x')` 로 트리 로드 실패
  - **근본 원인 2 (render)**: POE2 `connection.orbit` 메타데이터 (외부 호 반지름 인덱스 + 방향 부호) 가 normalizer 단계에서 손실. `passiveTreeRender` 가 PoB 의 3-branch BuildConnector (외부 호 / 내부 호 / 직선) 분기 없이 직선만 그림 + POE1 하드코딩 SKILLS_PER_ORBIT 사용 → cross-group 거미줄 sweep 발생
  - **수정 1 (data)**: `passiveTree.ts` null 가드 + `TreeNode.outConn?: Array<{id:string;orbit:number}>` 신설. `connections` 메타 보존. 회귀 가드 3건 추가 (sparse null skip / orbit metadata / out·outConn index alignment) → 22→25 테스트
  - **수정 2 (render)**: `passiveTreeRender.ts` 에서 `SKILLS_PER_ORBIT` 제거, RenderState 에 `skillsPerOrbit: number[]` / `edgeMaxDist` 동적 주입. PoB pre-filter 이식 (classStart skip + ascendancyName 불일치 skip), 외부 호 분기 (perp 부호 = `connOrbit > 0 ? 1 : -1`), straight cutoff 후 viewport culling (Cohen-Sutherland). POE2=5000 / POE1=1500
  - **CSS 토큰화**: `PassiveTreeCanvas.tsx` 8 hex literal → 기존 var + `--passive-notable: #E8C068` / `--passive-notable-border: #4A3F2A` 2개 신규 토큰 (POE notable gold/brown). design-exception #1 등록 (cap 2 의 1)
  - **검증 한계**: 거미줄 부분 해소만. sweep 일부 잔존 — sprite atlas 도입 또는 viewer 재설계 필요. **D4 DoD #11 인게임 검증 미완** (사용자 영역, deferred)
  - **갭 매핑**: 8-에이전트 병렬 (PoB / mobalytics / maxroll / community / POE1 own / POE2 own / 한국어 / 차별화) → `passive_tree_gap_audit.md` 신규 (Tier 0/1/2 + POE1+POE2 양쪽 매핑). 핵심 발견 = 커뮤니티 뷰어 시각 차별화 zero / 한국어 로컬라이제이션 갭 / heatmap×planner 갭
  - **커밋**: `a847ef0` data fix → `ddea176` WIP render + viewport culling → `8c85472` docs (8-agent gap audit). 워킹 트리 클린
  - **검증**: vitest 96 → **99** (+3 sparse null/orbit/index alignment) / pytest 745 / cargo unaffected / tsc 0
- **이전 세션 (S11, 2026-04-26)**: dat64 schema parser fix — POE2 Mods Tags/SpawnWeight 3 list 공백 해소 + List element-type 분기. 커밋 `ed23e75` / `9792033` / `0121d9c`. Rust 45 / pytest 745 / vitest 110 / tsc 0
- **이전 세션 (S3~S10)** — git log 참조. 주제별 도메인 파일 포인터로 이관

## 다음 세션 진입 절차
- 한 세션당 주제 하나. 현재는 POE2 보류, POE1 우선.
- build corpus / recommendation result UI 연결은 완료했다.
- 전략/레벨링 상태 표시는 corpus evidence 기준으로 수정 완료했다.
- passive tree는 POE1만 대상으로 1차 개선 완료했다. POE2 D4/D6 후속은 사용자가 다시 요청할 때까지 건드리지 않는다.

## 다음 할 것 (우선순위순)

0. [x] **POE1 recommendation UI 연결** — `poe1_representative_build_profiles.latest.json` / `recommend_from_corpus` 결과를 UI에 노출. Plan A/B/C/D, confidence, leveling status, source evidence 표시. 검증: `pytest test_recommend_from_corpus`, 코퍼스 추천 회귀 68개, `pnpm test`, `pnpm build`.
1. [x] **POE1 전략/레벨링 표시 수정** — poe.ninja=endgame variant, creator/stage PoB=leveling evidence 구분을 UI/문구에 반영. 레벨링/스킬/파밍/패시브 우선순위 섹션이 `selected_profile`을 받아 corpus route, transition point, passive direction, suitability/evidence split을 표시한다.
2. [x] **POE1 passive tree 개선** — POE1 tree 표시/전환/마일스톤 UX부터 정리. 트리 탭은 current PoB tree URL, representative passive plan, class/ascendancy fallback을 함께 사용한다. POE2 passive tree 후속은 보류.
3. [ ] **POE1 corpus 추가 수집** — creator registry 34명 기준으로 current-season PoB를 계속 누적. 기존 후보는 빼지 않는다.
4. [ ] **기존 POE1 잔여** (이월):
   - L3 auto-retry 인게임 검증 (POE1)
   - DoD 수동 검증 (FilterPanel / 오버레이 / 히스토리)
   - Strict 모드 실측
   - 필터 생성 인게임 검증
   - Passive P2~P6 / Syndicate S4 / Phase 5b/5c
   - alias 맵 재감사

## 도메인 파일 포인터

- [패시브 트리 시각/UX 갭 매핑](passive_tree_gap_audit.md) — 2026-04-26 S12: 8-에이전트 병렬 분석. Tier 0/1/2 + POE1+POE2 양쪽 매핑
- [POE2 통합 Diff (2026-04-22)](poe2_integration_diff.md) — §0 scope-bounded claim / §6.6 spirit gems / §7 마이닝 실측 / §8 drift / §10 빌드 방향
- [POE2 D6 DoD](poe2_d6_dod.md) — 인프라 체크리스트 + 해제 조건 3건
- [코치 품질 Phase H 백로그](coach_quality_backlog.md) — H1~H6 완료, L3 인게임/alias 누적
- [POE2 D7 플랜+Phase2 회고](poe2_d7_plan.md) — Phase 1 (S8) + Phase 2 (S9) 완료 기록
- [POE2 통합 backlog](poe2_integration_backlog.md) — D0+D6(CONDITIONAL) / D1/D2/D3/D4/D5/D7/D8 대기
- [POE2 D4 패시브 트리 계획](passive_tree_poe2_plan.md) — 데이터 소스/schema 매핑/Canvas 통합 (2026-04-22 S3)
- [디자인 Phase 0~5 플랜](design_phase_plan.md) — P5 미완. **Design enforcement 2026-04-22 설치 완료**
- [Syndicate 전면 개편 S1~S4](syndicate_phase_plan.md) — S1~S3 완료
- [패시브 asset 플랜](passive_tree_assets_plan.md) — P1 완료, P2~P6 대기
- [Continue 아키텍처](continue_architecture.md)
- [Design Exceptions](design-exceptions.md) — Exception #1 (--passive-notable*) 등록 (cap 2 의 1)
- _analysis/ggpk_truth_reference.json — POE1 19 테이블 진실 anchor
- _analysis/poe2_tables.json — POE2 942 테이블 카탈로그
- data/game_data_poe2/ — GGPK 실측 19 datc64 + **19 JSON** (S11 dat64 fix 후 Tags/SpawnWeight 정상 채워짐)
- data/base_items_poe2.json — 283 무기 + 562 방어구 + 98 기타 + 791 entry attribute requirements
- data/uniques_poe2.json — 393 visible uniques (stash_type_label 100%)
- data/valid_gems_poe2.json — 1079 gems (active 477 / support 600 / spirit 2)
- data/schema/schema_poe2_override.json — drift 보정 (SchemaStore auto-merge)
- data/id_mod_filtering_poe2.json — D7 Phase 2 Recombinator [[0400]]
- docs/league_refresh.md

## Class Start 노드 매핑 (POE1, data.json 수동)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## POE2 클래스·어센던시 실측 (2026-04-22 GGPK)
- 출시 8: Warrior / Monk / Ranger / Mercenary / Sorceress / Witch / Huntress (0.2) / Druid (0.4)
- 미출시 4 (Characters 테이블 잔존): Marauder / Duelist / Shadow / Templar
- 정식 어센 21: Warrior 3 / Ranger 2 / Huntress 2 / Witch 4 (**Abyssal Lich 확정**) / Sorceress 3 (**Disciple of Varashta 확정**) / Mercenary 3 / Druid 2 / Monk 2

## 잔존 이슈 (허용/추후 처리)

- **D4 거미줄 sweep 부분 해소만** (우선순위 0) — PoB pre-filter + viewport culling 적용 후에도 일부 잔존. sprite atlas 또는 viewer 재설계 필요
- **D4 DoD #11 인게임 검증 미완** (우선순위 1) — 사용자 영역
- **D6 해제 조건 3건 중 2건 이상 관찰 대기**
- **GameData POE2 QuestRewards 구조 차이** — `Characters` / `Reward` 필드 호환성 미검증
- **GameData POE2 SkillGems `is_support` 판별** — POE2 는 `IsSupport` 필드 없음, `GemType` 으로 판별 추후
- **L3 인게임 미검증** (POE1) — 재시도 교정 프롬프트 실 효과 측정 필요
- **Phase E subagent 제기 미패치 5건** (이전 세션 이월) — Claim gate / hook stdin 스키마 실측 대기
- **Tier 2 C / SyndicateBoard ss22 / Cmd+K / PassiveTreeCanvas 623줄 / Syndicate OCR / Coach zombie / Model toggle test** — 전부 이전 이월

## UX 결정 기록 (누적)
- 우클릭 dealloc 분리 → 되돌림 (왼클릭 토글 유지)
- 수동 URL import UI 스킵 (자동 디코드 대체)
- AI 이모지 제거, UI 이모지 → SVG 아이콘
- 전면 리디자인 = 다크 단일 + POE Rarity + Linear 레이아웃 + 2-창 오버레이
- 기본 리그 모드 = SC
- **빌드 분석 = 진입점** 원칙
- 패시브 class start = anchor only
- **코치 모델 기본 Haiku** — 3버튼
- **게임 토글 TopBar** — POE1 기본, POE2는 경고 배너 + VerbalBuildInput 폼
- **빌드 히스토리 (pobb 스타일)** — localStorage 최근 20개
- **오버레이 레벨링 = 탭 네비 + 활성 phase bullet**
- **FilterPanel 3모드 유지**
- **코치 정식화 = 코드 레이어 hard constraint** — normalizer 가 주 제약 (Phase H)
- **4-Layer hallucination 방어** — L1 prompt + L2 strict + L3 retry + L4 풀스크린 블록. **POE2 이식 완료 (2026-04-22)**
- **자가-PASS 방어 Tier 2** — Claim-gate + Phase E audit-all subagent + Fast/Strict 모드 분리 (2026-04-21)
- **POE2 D6 인프라** — SYSTEM_PROMPT_POE2 + valid_gems_poe2 + normalizer/validator POE2 분기 + VerbalBuildInput + activeGame invoke 전파 + GameData POE2 분기 (2026-04-22, CONDITIONAL DONE)
- **schema drift override auto-merge** — `SchemaStore::load_for_game(Poe2)` 자동 로드 + append (2026-04-22 S2)
- **extract_data `--reuse-datc64`** — GGPK 재파싱 없이 schema 적용 (2026-04-22 S2)
- **dat64 List/String 방어적 reject** — 45 GB OOM 차단 (2026-04-22 S2)
- **dat64 interval 8B + List element-type 분기** (2026-04-26 S11) — `interval: true` = 8B (i32 min/max), `array` = element type 별 16/8/4 B. POE2 Mods 6 list 공백 해소
- **POE2 D3 base_items / uniques** — BaseItemTypes + UniqueStashLayout × Words JOIN (2026-04-22 S2)
- **POE2 구두 빌드 입력 경로** — VerbalBuildInput → analyzeVerbalBuild → coach_build 직행 (2026-04-22)
- **Design enforcement** 2026-04-22 설치 (contract 4필드: Primary Action / mobalytics ref / #0A84FF / Pretendard)
- **POE2 D7 필터 레이어 완료** — heist/special_uniques POE2 skip + flasks_quality 재설계 + id_mod_filtering Recombinator [[0400]] 실구현 (S8/S9, 2026-04-24)
- **VerbalBuildInput POE2 전용 확정** (2026-04-25 S9) — `game` prop 제거, POE2 상수 고정. POE1 은 `PobInputSection` 유지
- **POE2 D4 viewer PoB BuildConnector 부분 이식** (2026-04-26 S12) — null 가드 + outConn 메타 보존 + PoB pre-filter (classStart/ascendancy) + 외부 호 분기 + viewport culling. 거미줄 부분 해소만, sprite atlas 후속 필요
- **--passive-notable* 도메인 토큰** (2026-04-26 S12, design-exception #1) — POE notable gold/brown 시각 언어 보존. accent 1개로 표현 불가
