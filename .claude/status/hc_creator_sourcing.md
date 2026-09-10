# HC 크리에이터 소싱 매트릭스 — 여정 DB #2 (2026-09-10)

> 지시서 `Docs/2026-09-10_HC_JOURNEY_CREATOR_SOURCING_TASK.md`. 사용자 지시: "HC·HCSSF 상관없이 하코 스트리머·유튜버 찾아 DB 쌓을 계획".
> **검색 0회.** 명부(`poe2_hardcore_sources.md`)의 사람만, 정체성은 캐시 자막의 영상 id → `yt-dlp -j`(메타) 로 채널 ID 확정,
> 콘텐츠는 `yt-dlp --flat-playlist --playlist-end 40` 채널 열거 + 가이드 영상 설명란(플래너·ninja 링크). 미디어·플래너·ninja 는 **아무것도 안 받았다.**

## 근거 등급 (HC 플래그는 이 등급 없이 1 을 주지 않는다)

| 등급 | 뜻 | 예 |
|---|---|---|
| **N** | poe.ninja **HC 리그** 캐릭터 링크가 그 빌드 설명란에 있다 | `…/forbiddenriteshc/character/…` |
| **S** | 본인 제목·발언이 그 빌드를 HC/HCSSF 라고 말한다(자막은 *주장* 근거로만, 이름 확정엔 안 씀) | "Hardcore SSF Verified" |
| **I** | 채널 정체성은 하코지만 **그 빌드**가 하코라는 근거는 없다 → `hardcore=0` + 노트 | Sarge2 "HC friendly" |
| — | 근거 없음 → `hardcore=0` | 탱정, Fubgun |

플래너 열: **M**=Mobalytics(탭=밴드, "Export to game" 다운로드), **X**=maxroll 플래너, **P**=pobb.in/PoB 코드(→ `build_poe2_planner_files.py --pob`),
**J**=poe.ninja PoB 스냅샷(`pob/raw/<id>`, 1세트=1밴드), **L**=로컬 보유(허락 불필요). 자막 열은 `data/_cache/subs/` 보유 편수.

## A. 정체성 확정 후보 (채널 ID = yt-dlp 2026-09-10, 17명 · eltriki 만 명부 ID)

| # | 이름 | 채널 (ID · 핸들) | 언어 | 빌드 계열 / 전직 (최신 패치) | HC/HCSSF 근거 | 플래너 | ninja | 자막 | 우선 | 필요한 허락 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Blazeworks TV** | `UCCgInTe6xn-n6650g2PrimA` · @BlazeworksTV | en | **바라시타 SSF 캠페인+엔드게임 (0.5.5)** — Disciple of Varashta 소환수. 0.5: Pin2Win 유탄 택티션 | **N** `poe.ninja/poe2/profile/BlazeW-3944/forbiddenriteshc/character/Blaze_MinionToWin`(RE9_SlCF4lk 설명란) + **S** "BEST HCSSF Class"(1-sKhCgt1Xg) + 팟캐스트 허브(@lexdtv·@MisoxShiru 게스트) | **M** `mobalytics.gg/poe-2/profile/blazeworkstv/builds/0-5-ssf-minion2win-varashta-campaign-build-guide` (캠페인 가이드 = 탭 다수 추정, 미확인) | `BlazeW-3944` (HC FR) | 8 | **1** | M 탭 export · ninja 캐릭터 JSON · 자막 RE9_SlCF4lk |
| 2 | **MisoxShiru** | `UCQe-5sJhva7DIeWS1L_SgkQ` · @MisoxShiru | en | **나비라의 균열 바라시타 리그 스타터 (0.5.5)** + Day1 영상. HCSSF Adventures 연재(크로노맨서, 0.5) | **S** 연재 제목·설명 "PoE 2 HCSSF Adventures"(TBD5-pYF3dE·yIpT8XoD7-Q·fIRGNy55Jyg). 단 **바라시타 스타터 자체의 HC 근거는 없음** → 그 빌드는 `hardcore=0`+노트, HCSSF 캐릭터가 ninja 에 있으면 N 으로 승격 | **M** `mobalytics.gg/poe-2/builds/naviras-fracturing-varashta-league-starter` (탭 수 미확인) | 미확보 | 4 | **2** | M 탭 export · 자막 Jrj2YtLSJSk |
| 3 | **디넬** | `UC2Rbd4Wz9MC8yt8xQQtJe_g` · @DI_NEL | **ko** | **바라시타 1~100 (0.5.5)** ktg8phbLQw8 · 켈라리&나비라 바라시타 YR0BtaTug_k · 크산테 전기불꽃 리치 0.5.5 DSdSbtKU76E · 위치 스타터 | **N** `poe.ninja/poe2/builds/runesofaldurhc/character/DNEL-7382/_디넬_`(DSdSbtKU76E 설명란, 0.5 HC) + **S** 제목 "하드코어 랭커의…"·"하드코어 100렙"·자막 xUy9qUSTr1k 1:21 "시즌1부터 쭉 하드코어, 전체 36등·리치 1등"(주장 근거) | **없음** — 설명란에 플래너 링크 0(5편 확인). 밴드는 ninja **폴링**으로만 | `DNEL-7382` (0.5.5 캐릭터명 미확인) | 6 | **3** | ninja 계정 캐릭터 조회 + 폴링(`track_poe2_character.py`) · 자막 YR0BtaTug_k·DSdSbtKU76E |
| 4 | **Gressoul** | `UChufbMxF9ZiMTXb_Gy0e7Vw` · @Gressoul | en | **롤링 슬램/지진 스미스 오브 키타바 (0.5)** — 방패벽 아님. 0.5.5 콘텐츠 없음(채널이 디아블로4 로) | **N** `poe.ninja/poe2/builds/runesofaldurhc/character/sdd9-5499/MeleePlayer`(acQnYvisJow) + **S** "CLEARS All Hardcode Content"·"I Trust This Slam Build With My Hardcore Character" | **M** `mobalytics.gg/poe-2/profile/deadly-flower-yuspak/builds/a155e5bb-…` + **P** `pobb.in/JXClL5dMwhD4` | `sdd9-5499` (0.5 HC) | 4 | 4 | M 탭 export · ninja(0.5 리그, 스냅샷 남아 있으면) |
| 5 | **Sarge2** | `UCXFZF8jhpIzOHVRSOScgY3w` · @sarge2254 | en | **스파크 토템 인보커 (0.5, "HC and SSF friendly")** 8kZ9G5CNyYM · 방패벽 인보커 HCSSF(0.3/0.4) zfU0YTibkpI. POE1 도 섞어 올림(Mirage=POE1) | **S** "I Reached 100 in Hardcore SSF"·"Hardcore Rank 1 Build Overview"(정체성). 스파크 토템 빌드 자체는 "friendly" → **I** | **M** `mobalytics.gg/poe-2/profile/sargetwo/builds/invoker-spark-totems` + **P** `pobb.in/gZRHGrwQgQjs` · 방패벽 인보커 **X** `maxroll.gg/poe2/planner/l34tp0q0` + P | 미확보 | 4 | 5 | M 탭 export |
| 6 | **Oscrix** | `UCx1nSsDc8Xqp7DJMg2mTcbA` · @Oscrix | en | **차율라 개 소환수 (0.5.5)** 12i7NhSeuY4 · 기름 패스파인더 for HC(0.4) · 코이어 오라클 for HC | 0.5.5 빌드는 ninja **소프트코어** `forbiddenrites/character/Oscrix-1876/Oscrix_LET_DA_DAWGS_OUT` → 그 빌드 `hardcore=0`. 정체성은 THC 사설 하코 리그(IauNVXcS4TQ 설명란 `pathofexile.com/private-leagues/league/THC+League+III` + 0:08 발언) → **I** | **J** 0.4 코이어 `pob/15268` · 0.5.5 는 ninja 캐릭터만 | `Oscrix-1876` (0.5.5 SC) | 6 | 6 | ninja 캐릭터 JSON(1밴드) — 폴링 가치 낮음(SC) |
| 7 | **Skadutch Gaming** | `UCtt9vhBafdJ3m2L99R-pk_Q` · @SkadutchGaming | en | **바라시타 진 소서리스 (0.5)** ph4cQGdnm70·mZMpuKjtlVo. 0.5.5 없음 | **S** 채널 정체성 14/36 제목이 HC("Hardcore Duo Challenge" 연재·"HC Bro SF"). 바라시타 빌드 자체 근거 없음 → **I** | **M** `mobalytics.gg/poe-2/profile/deadly-shadow-jbunmc/builds/4387a3e4-…` | 미확보 | 8 | 7 | M 탭 export |
| 8 | **LexD** | `UCrl_nSbmfs0FurHtq3uLDLA` · @lexdtv | en | 창+방패 출혈 타이탄 (0.5.5) vQibmfLbKFE · 방패벽 키타바 Avatar of Fire (0.5) | ninja **소프트코어** `TheMasterBlaster-2484/runesofaldur/…`(두 빌드 다) → `hardcore=0` | **M** `mobalytics.gg/poe-2/profile/lexd/builds/poison-bleed-titan` · `mobalytics.gg/poe-2/builds/avatar-of-fire-smith-of-kitava-lexd` | `TheMasterBlaster-2484` (SC) | 11 | 8 (SC 대조군) | M 탭 export |
| 9 | **ds lily** *(적재됨)* | `UCSDZkgmigfYbdw7hJ-6Wo6A` · @dslily | en | 적재: 기름 유탄 화염파 젬링. **신규: 기름 연사 무술가 (0.5.5)** TuUFlxoZUMQ | 채널 정체성은 HC(릴리리그 운영, "Starting A New HC SSF Run" 0.5)지만 **적재된 젬링 빌드의 HC 근거 없음**(설명란 "1 divine budget"·WIP, 자막 HC 0회) → **I**, `hardcore` **1→0 으로 내림**(이번 커밋). 무술가 0.5.5 도 **I** | 무술가: **M 캐릭터 페이지** `mobalytics.gg/poe-2/profile/ds_lily/characters/lily_invade_poe_for_oil`(빌드 탭 아님) | 미확보 | 5 | 9 (2번째 빌드) | M 캐릭터 export(1밴드) |
| 10 | **Kris Droverson** | `UCe_DP6cQ2FzZWofxfc3JiOA` · @KrisDroverson | en | 데몬 베어 키타바 (0.5) · 불멸 키타바 (0.4) | ninja **소프트코어** `KrisDroverson-5430/runesofaldur/…` → 0 | **M** `mobalytics.gg/poe-2/profile/krisdroverson-dqfr7a/builds/9fdcd35c-…` + **J** `pob/1e36a`·`pob/16309` | `KrisDroverson-5430` (SC) | 6 | 10 | M 탭 export |
| 11 | **Big Ducks** | `UC8XfFGnTEJH1CXjucYDA5ng` · @BigDucks | en | 폭발 위치헌터 (0.5.5) fXdNmYE5t9Q · 시체 폭발 방패벽 키타바 (0.4) | 근거 없음 → 0 | **M** `mobalytics.gg/poe-2/builds/explosive-witchhunter` · `…/detonate-dead-on-hit-smith` | 미확보 | 4 | 11 | M 탭 export |
| 12 | **Angormus** | `UCy_0NfveSBkKAx2QNAy_xMg` · @Angormus | en | 방패벽 키타바 (0.5, 레이서 관점) | 근거 없음 → 0 | **X** `maxroll.gg/poe2/planner/i75hqm0h` | 미확보 | 2 | 12 | X export |
| 13 | **Z3mos** | `UCPuFjk05I4n2kM7ZKR3MoNg` · @Z3mosAU | en | 그레이프/그레이트 월 키타바 (0.5, 너프됨) | 근거 없음 → 0 | **J** `pob/1a1c7`·`pob/24221` (1세트씩) | 미확보 | 8 | 13 | J raw 2건 |
| 14 | **josiahyeet** | `UC36b1tD7EdSLR3q0yOryRyg` · @josiahyeeet | en | 화염파 기름 유탄 젬링 (0.5.5) -oltGK1JP9I 외 젬링 연재 | 0/37 제목 HC → 0 | **M** `mobalytics.gg/poe-2/profile/deadly-golem-wt8y0n/builds/e0a4c07c-…` | 미확보 | 2 | 14 (젬링 4번째) | — |
| 15 | **Peuget2** | `UCFzGidn_t6Mtw_hV3Ve9o2Q` · @Peuget2 | en | 화염파 기름 유탄 젬링 (0.5.5) + 레벨링 가이드 6XZgDnpPDPc | 0/40 제목 HC → 0 | **M** `mobalytics.gg/poe-2/builds/hellfire-gemling-flameblast-oil-grenade` | 미확보 | 2 | 15 (젬링 5번째) | — |
| 16 | **POEGuy** | `UCvICZHerbUEr3eM6q3kISIg` · @poeguy007 | en | 워브링어 유탄 발리스타 토템 스타터 (0.5.5) | 근거 없음 → 0 | 설명란 3편 모두 **poe-vault** `poe-vault.com/poe2/warrior/warbringer/totems-build-guide`(+`totems-leveling-build`) — 인게임 플래너 아님, 밴드 없음 | 미확보 | 0(scratchpad 만) | 16 | — |
| 17 | **탱정** *(적재됨, 1밴드)* | `UCSlN0zTczYpNJHCbskGuYaw` · @탱정-탱커의정석 | ko | 방패벽 키타바 2.0 (0.5, PoB 97렙) · **0.5.5 실캐릭 90→94 (낭만 워리어)** | 본인 저자본 가이드 자막(QcSeQ0OOENI 3:01 "하드코어 유저분들까지 참고하시기에 생존은 절대 포기할 수 없습니다", 10:43 하코용 대체품) = 소프트코어 빌드 + 하코 대체안. 0.5.5 방송 자막의 하코 언급은 미래 가정뿐(day3 4:06:29, h:mm:ss) → 0 | **J** `pob/28010`(적재) · **L** 0.5.5 `deliverables/tangjung_0_5_5_research_2026-09-07/sources/pob_{28509,285e2,28604,28695}.xml` | 계정명 미확보(ninja 닉 `ROA_WarriorTanker_Build`) | 1+2(0.5.5 방송 전사) | 적재됨 | L 4개는 허락 불필요 |
| 19 | **MajorAimless** *(팟캐스트 축 신규)* | `UCSU3AtPCUdOroXcHO5T9qcA` · @MajorAimless · 트위치 `majoraimless` | en | 차율라 Last Lament (0.5) · Whirling Assault 무술가 (0.5) · Twister SpiritWalker 스타터 (0.5) — 전부 HCSSF | **S** 14편 중 13편 제목 HCSSF, 설명란 트위치 링크 | **M** 3개 `mobalytics.gg/poe-2/profile/majoraimless-zcp87o/builds/…` | 미확보 | 0 | **6.5** (0.5 이지만 HCSSF 전용·새 계열 3종) | E: M 탭 export ×3 |
| 20 | **lolmalice** *(래더 축 신규)* | 트위치 `lolmalice`(유튜브 없음) · ninja `lolmalice-3623` | en | 0.5.5 HC 트레이드 리그 스타트 몽크("sw monkey") — HC 래더 4위 98렙 | **N** HC 래더 캐릭터 `lolmalicem` + VOD 제목 "poe2 0.5 league start (hc trade)" | 없음 — ninja 폴링만 | `lolmalice-3623` (HC FR) | 0 (VOD 전사 필요) | **3.5** (현역 HC 최상위, 영상 30시간+) | F: ninja 폴링 + VOD 오디오 구간 전사 |
| 18 | **eltriki** | `UC1543074v44JJ959q6ckzyQ` (명부 ID, yt-dlp 미확인) | es | 하드코어 액트 완주 #1~#29 연재 | **S** 연재 제목(명부) | 없음 | 미확보 | 0 | 보류 | — (캠페인 문서용) |

이미 적재된 임성빈(`UCvj_myZNbqdHBBFT2IjKJWw` @임성빈POE2하드코어, 채널명 자체가 "POE2 하드코어"; HC 근거는 설명란이 아니라 **ninja API 응답** `overview=hc-forbidden-rites`·league "HC Forbidden Rites"(`.claude/status/poe2_hc_gemling.md`) = N 급), Skadoosh(`UChDo6WKvR6szS46KY_dL_zg` @SkadooshPoE; `SkadooshShoutedHard` ninja API 응답 league "HC Forbidden Rites"(`deliverables/skadoosh_early_survival_2026-09-08/stage_05_06_audit/ninja_latest.json`) = N 급 — 설명란 링크는 0.5 SC 캐릭터라 설명란 기준으론 N 아님), Fubgun(HC 0)은 위 표에서 뺐다. ds lily 는 9행에서 1→0 으로 갱신.
임성빈의 **2번째 빌드 후보** = 하코 100렙 바라시타(PBWgtjN4Amw·E8A6HbzPQjM) — 설명란에 플래너 링크 0, Mobalytics 프로필 `seongbin-poe2-hardcore-zaxjdu` 에 바라시타 탭이 있는지는 열람해야 안다(허락 목록 D).

**같은 빌드 대조 효과:** 바라시타를 1·2·3·7 네 명이 다룬다(Blazeworks 소환수 축 · MisoxShiru 나비라 · 디넬 켈라리&나비라 · Skadutch 진). 젬링 3명 대조가 보여 준 "같은 빌드도 내부가 갈린다"를 두 번째 계열에서 재현할 수 있다.

## B. 명부에 이름만 있고 정체성 미확정 (검색 금지라 이번엔 안 팠다)

Ben_ · Augvald(HCSSF 100렙 랭크 8, Blazeworks 팟캐스트 게스트) · PhazePlays("World First Arbiter +4 HCSSF" 검색 요약만) · Kripparrian(상시 하코 아님) ·
Woolie · skr1mps · DarthMicrotransaction · barricadettv · 호진 · 혜미 Ham · 겜창의삶 · JungRoan(채널 없음, 기름 유탄 원작자) · KrushR · PietSmiet · AlphaReplay · Rakin.
확정 경로 = Blazeworks 팟캐스트 제목의 `@핸들`(qbwGpRZakpw @Barricade, ubgMGye7ypA @DEADRABB1T, 8-yx4LkrZFo @Lolcohol 등 — 채널 열거에 이미 찍혀 있다) → `yt-dlp -j` 로 채널 ID. 다음 회차.

## 우선순위 규칙 (지시서 그대로) → 위 "우선" 열

① 밴드 플래너가 공개된 사람(자동층 공짜) — M/X/P 있는 1·2·4·5·7·8·10·11 ② 다른 빌드 계열(젬링 3명은 충분) — 바라시타·키타바 슬램·인보커·리치·소환수
③ ninja 만 있는 사람은 폴링으로 밴드를 만들 수 있을 때만 — 디넬(0.5.5 현역, 09-08 업로드)은 가능, Oscrix 0.5.5 는 SC 라 가치 낮음
④ 한국어 소스는 자막 판독까지 가능 → 규칙 후보 가치 — 디넬(6편)·임성빈 바라시타. 여기에 **HC 근거 등급(N>S>I)** 을 곱했다.

## 첫 적재 3명 + 허락 목록 (한 번에 답해 주세요 — 허락 전엔 아무것도 받지 않는다)

| 항목 | 출처 URL | 무엇을 받나 | 크기(추정) | 쓰임 |
|---|---|---|---|---|
| **A-1** Blazeworks Mobalytics 열람+export | `https://mobalytics.gg/poe-2/profile/blazeworkstv/builds/0-5-ssf-minion2win-varashta-campaign-build-guide` | 탭 수 확인 후 탭마다 "Export to game" `.build` → `import_poe2_planner_files.py` → `data/hc_journey/creators/blazeworks/` | 탭당 3~15KB × 탭 수(≥2 여야 적재) | 밴드(자동층) |
| **A-2** Blazeworks ninja | `https://poe.ninja/poe2/profile/BlazeW-3944/forbiddenriteshc/character/Blaze_MinionToWin` (API `…/builds/latest/character?account=BlazeW-3944&name=Blaze_MinionToWin&overview=hc-forbidden-rites`) | 캐릭터 JSON 1회(키스톤·실캐릭 밴드) — 폴링은 안 함 | 50~100KB | 키스톤 규칙 + 마지막 밴드 |
| **A-3** Blazeworks 자막 | `https://www.youtube.com/watch?v=RE9_SlCF4lk` (엔드게임 가이드 0.5.5) | 자동 자막 en json3 | ~200KB | 규칙 후보(선택) |
| **B-1** MisoxShiru Mobalytics 열람+export | `https://mobalytics.gg/poe-2/builds/naviras-fracturing-varashta-league-starter` | 탭마다 `.build` → `creators/misoxshiru/` | 탭당 3~15KB | 밴드. HC 근거 없으면 `hardcore=0`+노트로 적재 |
| **B-2** MisoxShiru 자막 | `https://www.youtube.com/watch?v=Jrj2YtLSJSk` (Day 1) | 자동 자막 en json3 | ~150KB | 규칙 후보(선택) |
| **C-1** 디넬 ninja 계정 조회 | `https://poe.ninja/poe2/profile/DNEL-7382` (0.5.5 HC 캐릭터명 확인) | 프로필 1회 → 캐릭터명 | ~50KB | 폴링 대상 확정 |
| **C-2** 디넬 ninja 폴링 | `track_poe2_character.py --account DNEL-7382 --name <C-1 결과> --overview hc-forbidden-rites --interval 180 --hours 8` | 변화 시점마다 캐릭터 JSON(전환 레벨 보존본 = 밴드) | 50~100KB/회, 8시간에 수십 회 | 밴드(폴링) — 플래너가 없는 사람의 유일한 경로 |
| **C-3** 디넬 자막 | `YR0BtaTug_k`(켈라리&나비라 바라시타) · `DSdSbtKU76E`(리치 0.5.5) | 자동 자막 ko json3 | ~150KB × 2 | 한국어 규칙 후보 |
| **D**(선택) 임성빈 Mobalytics 프로필 열람 | `https://mobalytics.gg/poe-2/profile/seongbin-poe2-hardcore-zaxjdu` | 바라시타 빌드 탭 존재 여부만 | — | 2번째 빌드 후보 판단 |
| **E**(신규, 팟캐스트 축에서 발견) MajorAimless Mobalytics export ×3 | `mobalytics.gg/poe-2/profile/majoraimless-zcp87o/builds/fcad0476-808e-40df-83a5-c380c2c80bc4`(차율라 Last Lament) · `…/7d5b9ebe-83b4-4c27-ac57-f298a2ac7fd9`(무술가) · `…/2c88a8d0-081c-4fec-8991-870db4427b73`(스피릿워커 스타터) | 탭마다 `.build` zip(A-1 과 같은 방식) | 탭당 3~15KB | HCSSF(S) 0.5 빌드 3개 — 새 계열 3종. **아직 안 받음(허락 대기)** |
| **F**(신규, 래더 축에서 발견) lolmalice | ninja `lolmalice-3623` / `lolmalicem` / `hc-forbidden-rites` 폴링(`track_poe2_character.py`) · 트위치 VOD `v2865278209`(33h)·`v2866780837`(26h)·`v2867898432`(20h)·`v2868807599`(12h) 구간 오디오 → Whisper 전사(`reference_twitch_vod_reading`) | 캐릭터 JSON(50~100KB/회) + VOD 오디오 구간(구간당 수십 MB, 재인코딩 없음) | 크다 — 구간만 | HC 4위 현역 스트리머의 리그 스타트 여정. 밴드는 폴링(98렙이라 장비 변화만), 규칙은 VOD. **아직 안 받음(허락 대기)** |
| **G**(신규, 래더 축) roxTITAN | ninja `roxTITAN-1798` / `richBEACH_N_ROX` / `hc-forbidden-rites` 폴링 · 트위치 VOD `v2868406263`(7h)·`v2869303646`(6h) "top1 Warrior on HC!" 구간 전사 | 캐릭터 JSON + VOD 오디오 구간 | 크다 — 구간만 | HC 9위 현역 워리어 스트리머. 워브링어(Skadoosh)와 다른 워리어 축이면 대조 계열. **아직 안 받음(허락 대기)** |
| 나머지 미결 | 래더 미조회 로그인 54건은 에이전트 최종 실행에서 전부 완료(0 pending). 러시아어 `Graf_Irdis`(HC 92렙, VOD 5)만 POE2 여부 미확인 | — | — | 필요하면 VOD 제목 1회 조회 |

주의: Mobalytics 는 Fubgun 때 403 을 낸 적이 있다(브라우저 세션 필요). ninja 는 개별 캐릭터 조회만(집계 없음), 폴링은 `track_poe2_character.py` 의 3분 간격.

### 허락 결과 (2026-09-10 저녁, 사용자 "해보자" 승인 후)

| 항목 | 결과 |
|---|---|
| A-1 Blazeworks | Playwright(`browser_run_code_unsafe` + `page.waitForEvent('download')` → `download.saveAs`)로 "Download Build File" zip 수신 — 8탭. **Lv1-21 은 대안 3개**(유탄·ED/C+소환수·ED/C+원소), "Min-Maxed Endgame" 탭은 **빈 파일**(패시브·스킬 0). 유탄 라인 + 22-36 + 36-65 + 65-85 + 90+ = 5밴드. 페이지의 "Live Seasonal Characters: Level 96 Disciple of Varashta · HC Forbidden Rites" 로 N 재확인 |
| A-2 Blazeworks ninja | `Blaze_MinionToWin` 96렙, API 응답 league "HC Forbidden Rites", 키스톤 Chaos Inoculation → 6번째 밴드(ninja_live). 원본 JSON = `creators/blazeworks/_source/` |
| A-3 자막 | `blaze_RE9_SlCF4lk.en` 수신 |
| B-1 MisoxShiru | zip 7탭 전부 밴드(막 경계 레벨 힌트). Live Seasonal Characters 없음 → HC 근거 없음 → `hardcore=0`, 리그 `forbidden-rites` |
| B-2 자막 | `miso_Jrj2YtLSJSk.en` 수신 |
| C-1 디넬 계정 조회 | **프로필 페이지 불필요** — ninja 래더 search API(`/poe2/api/builds/latest/search?overview=hc-forbidden-rites&name=디넬`, protobuf)가 계정 `DNEL-7382` · 캐릭터 `디넬바라시타`(98렙, EHP 59k) 를 돌려줬다 |
| C-2 디넬 폴링 | 1회 조회 → PoB → 밴드 1개(`dinel/01_live_lv98.build`, league "HC Forbidden Rites" = N). 6시간 폴링 가동(scratchpad `dinel_track/`) — 98렙이라 전환은 장비·젬 변화에서만 나온다 |
| C-3 자막 | `dinel_YR0BtaTug_k.ko` · `dinel_DSdSbtKU76E.ko` 수신 |
| D 임성빈 Mobalytics | 프로필에 빌드 **1개뿐**(젬링 리그 스타터, 9/6 갱신). 바라시타 탭 없음 → 2번째 빌드는 플래너 경로 없음(ninja 폴링만) |

적재 결과: creator 8 · snapshot 36 · transition 28 · 규칙 노트 82→101 · 거래 링크 466→770. 바라시타 3명(Blazeworks·MisoxShiru·디넬)이 두 번째 대조 계열.

### 넓히기 — 검색어가 아니라 정체성 축 두 개 (2026-09-10, 언어 무관)

1. **ninja HC 래더 → 스트리머**: search API 는 protobuf(`application/x-protobuf`)이고 요청당 상위 100명(계정·캐릭터명·클래스·레벨·EHP·DPS)을 준다. `class=` 필터로 계열별 100명씩 넓힐 수 있다.
   twitch 컬럼은 없다 — 캐릭터명의 `ttv`·`twitch`·`live` 같은 자기표기 + 계정명을 트위치/치지직 로그인으로 **실제 조회**해 "스트리머인가·영상이 있는가"를 확인한다(사용자 기준). 결과 = `scratchpad/ninja_streamers/streamers.md` → 아래 표로 옮긴다.
2. **팟캐스트 @핸들**: Blazeworks·MisoxShiru 채널 전체 열거에서 @핸들 56개(TalkativeTri·Lolcohol·YungYdoc·XTheFarmerX·Raxxanterax·DEADR4BB1T·Palsteron·GhazzyTV·CaptainLance9·barricadettv·Timmy_P_onTwitch·JorgenPOE·KadachiPOE2 …). 각 채널 40편 열거 + POE2 가이드 설명란의 HC 링크 검사(`scratchpad/handles/sweep.json`, 50 채널 성공 / 6 핸들 404).

#### 래더 축 결과 (2026-09-10) — HC 1320 + HCSSF 949 계정(상위 100 × 어센던시 필터 21종), 스트리머 실조회 164 로그인 전부 완료(영상 있음 10 · 채널만 52 · 없음 102)

사용자 기준 "스트리머/유튜버인가 → 영상이 있는가"로 판정. 트위치는 `yt-dlp --flat-playlist twitch.tv/<login>/videos`(채널 존재·VOD 수), 한국어 이름은 치지직 채널 API. 원자료 `data/hc_journey/sourcing/ninja_ladder_2026-09-10/`.

| 계정 · 캐릭터 | 래더 | 플랫폼 · 영상 | 판정 |
|---|---|---|---|
| **lolmalice-3623 · lolmalicem** | HC **4위** 98렙 | 트위치 `lolmalice`, VOD 8+ — 제목 "poe2 0.5 league start (hc trade) starting build sw monkey", 리그 스타트 VOD 4편 각 12~33시간 | **신규 후보 20번** — 영어 트위치 전용(유튜브 없음). 밴드 = ninja 폴링, 규칙 = VOD 전사(`reference_twitch_vod_reading`). HC 근거 **N**(HC 래더 캐릭터) |
| **roxTITAN-1798 · richBEACH_N_ROX** | HC **9위** 98렙 | 트위치 `roxTITAN`, VOD 8 — 제목 "top1 Warrior on HC! richBEACH_N_ROX"·"HC warrior"·"Mageblood!", 1~7시간 | **신규 후보 21번** — 현역 HC 워리어 스트리머(트위치 전용). HC 근거 **N**(HC 래더) + VOD 제목. 허락 목록 **G** |
| Oskarmln-1292 · essenceshard | HCSSF **1위** 98렙 | 트위치 `Oskarmln`, VOD 7 — 전부 POE1 SSFHC 클립(Ruthless·Archnemesis·Synthesis 100렙) | POE2 영상 없음 → 보류(HCSSF 1위라 ninja 폴링 가치는 있음) |
| Richaimyte-6785 · Richainadess | HC 91렙 | 트위치 VOD 2 — 2019년대 POE1 Blight 하이라이트 | 현역 아님 → 제외 |
| Zeref-TR-9091 · Zereffffff | HC **1위** 100렙 | 트위치 `ZerefTR` 채널 존재, VOD 0 | 영상 없음 → 보류 |
| GDDLive-0150 · GDVarashta | HCSSF | 트위치 `GDDLive` 존재, VOD 0 | 보류(이름이 Live 표기) |
| PinkApple-1905 · PinkAppleHCttv | HCSSF | 트위치 `PinkApple` 존재, VOD 0 | 보류 |
| Szymon-2472 · Szymon_x | HC 98렙 | 트위치 존재, VOD 0 | 보류 |
| Graf_Irdis-3816 · TTV_Graf_Irdis_FR_I | HC 92렙 | 트위치 VOD 5, 러시아어 제목("Учусь играть") | 러시아어 후보 — POE2 여부 미확인, 보류 |
| GrappLr · Yeti · garrickdr · Saasinho · Jimmythevu | — | VOD 있으나 Valheim·WoW·Gungeon·스웨덴어 | 짧은 아이디 충돌(다른 사람) → 제외 |
| 채널 존재·VOD 0 (Nartwoo·Blaise·acolyte·yuto·Palanteer·… 33건) | — | 대부분 흔한 아이디 | 동일인 근거 없음 → 제외 |

**한국어 이름 61계정 → 치지직**(`chzzk_results.json`, 에이전트의 chzzk 조회가 오타로 빠져 직접 재실행): 채널 API 정확 일치 3건(신기하당·디스코·토템)뿐이고 전부 영상 0·POE 언급 0 → 흔한 이름 충돌, 스트리머 없음. 즉 HC 래더의 한국인 상위권(하데스일주년·차율라사용·헤롱헤롱쿨쿨방울·이호기 계열 …)은 치지직 채널을 그 이름으로 운영하지 않는다. 한국어 HC 소스는 여전히 유튜브(임성빈·디넬·탱정) 경로다.

알려진 제작자 교차: 임성빈·디넬·Blazeworks·Skadoosh·Kris Droverson·CololadoBurger 는 래더에 있음. Oscrix·Gressoul·LexD·Arserina 는 없음(SC 또는 0.5).
한계: 스트리머 판정은 채널 존재+영상 유무이지 "그 캐릭터의 주인"이라는 증명이 아니다(짧은 아이디는 충돌). 이름에 `ttv/twitch/live` 표기가 있거나 VOD 제목이 POE2 인 경우만 채택. 164 로그인 전부 조회 완료.

#### 팟캐스트 축 결과 (2026-09-10) — 대부분 소프트코어, 신규 HC 는 1명

| 채널 | ID · 핸들 | 근거 | 플래너 | 판정 |
|---|---|---|---|---|
| **MajorAimless** | `UCSU3AtPCUdOroXcHO5T9qcA` · @MajorAimless (465 구독, 트위치 `majoraimless`) | **S** — 14편 중 13편 제목이 HCSSF: 0.5 Acolyte of Chayula "Last Lament"(7Roc4jDxdqA) · Whirling Assault 무술가(kKQODvdp4kE) · Twister SpiritWalker 스타터(cvOiJ5-DI4U) | **M** 3개 `mobalytics.gg/poe-2/profile/majoraimless-zcp87o/builds/{fcad0476…, 7d5b9ebe…, 2c88a8d0…}` | **신규 후보 19번** — 0.5 이지만 HCSSF 전용 + 플래너 3개 + 새 계열(차율라·무술가·스피릿워커). 허락 목록 **E** |
| CrimsonCasts | `UC0T7CsWXQv7ORzCvhJV9e-A` | "Tierlist Update: Notes for Hardcore Players in 0.5.5" 1편 | 없음 | 빌드 제작자 아님 — 티어리스트 참고용 |
| Schwingy | `UC2ju0j2-6NZd8i8qqOIWZWA` | "Can A Random Build Survive in Hardcore?" 1편(영화형) | 없음 | 보류 |
| DarthMicrotransaction · Woolie | — | HC 제목은 **POE1**(Keepers of the Flame) · **테라리아 Calamity** | — | POE2 하코 아님 |
| 나머지 44채널(Zizaran·Raxxanterax·Palsteron·GhazzyTV·Jorgen·TalkativeTri·Lolcohol·Dr3adful·Dreamcore·KallTorak·KingKongor·Scorpius …) | — | HC 제목 0·설명란 HC 링크 0 | — | 소프트코어 |

핸들 404: @DEADRABB1T(실제 @DEADR4BB1T)·@Lexd(@lexdtv)·@Pohx·@Timmy_P_onTwitch·@XTheFarmerX(@XTheFarmerX_POE2)·@ZiggyD(@ZiggyDGaming). Timmy 는 트위치 전용이라 유튜브 핸들이 없다 — 래더/트위치 축에서 본다.

## 허락 없이 한 것 — 탱정 1밴드 적재 (완료)

- 픽스처 `data/hc_journey/creators/tangjeong/01_endgame_2_0.build` = `build_planner/Kitava Endgame 2.0 - Tangjeong.build` 복사(PoB 28010, 0.5, 97렙). `CREATORS` 5번째. `hardcore=0`, `league=runes-of-aldur`(0.5 소프트코어; trade2 리그 목록에 아직 있어 링크 생성기가 풀 수 있다).
- 결과: creator 5 · snapshot 22 · transition 17(변화 없음) · 규칙 노트 82(변화 없음) · 링크 466(변화 없음). `--query --id 5` = 스냅샷 1 + **"전환 없음 — 밴드 1개. 규칙 노트·거래 링크는 전환에 붙으므로 0 이 맞다(스냅샷만 적재)."**
- **결정: 전환 0 은 맞는 동작이다.** 여정 DB 의 단위는 전환이고 규칙·링크는 전환에 붙는다. 밴드 1개 빌드는 "완성 상태"만 있어 PoB/ninja 와 다를 게 없다 — 그래서 적재 가치는 낮지만, 스냅샷(스킬 11·장비 12칸)은 남고 나중에 앞 밴드가 생기면 전환이 생긴다.
  조용히 비는 것은 막았다: `query_journey`·`render_build` 가 "전환 없음"을 한 줄로 말하고, 테스트 `test_single_band_build_has_no_transitions_notes_or_links`(--query)와 `test_render_all_builds_has_journey_notes_and_trade_links`(여정 뷰 문구)가 이 계약을 고정한다.
  같은 커밋에서 ds lily `hardcore` 1→0 (빌드 단위 HC 근거 없음, 근거 등급 I) — 적대검증 1차가 잡은 자기모순.
  `league/trade` 첫-전환 테스트와 초안기 리그 트리거 테스트는 "전환 0 빌드엔 트리거가 없다"로 갈래를 넣었다(리터럴 아님, `len(bands)>=2`).
- **잠복 함정:** `trade_links.generate` 는 전환이 없어도 리그 슬러그를 먼저 푼다. 0.5 리그가 trade2 목록에서 빠지는 날 탱정 항목이 `resolve_league` 에서 죽는다 → 그때 lazy 로 바꾸거나 밴드를 0.5.5 로 교체.

### 허락 없이 더 할 수 있는 것 (로컬 보유, 미실행)

| 후보 | 근거 | 왜 안 했나 |
|---|---|---|
| 탱정 0.5.5 실캐릭 4밴드(90→91→93→94) | `deliverables/tangjung_0_5_5_research_2026-09-07/sources/pob_*.xml`, 방송 설명란이 ninja id 를 명시(fxyFr-Sde0U·LPVyK8hzlCQ). `build_poe2_planner_files.py --pob` → `.build` | 같은 사람의 **두 번째 빌드** — `CREATORS` 는 항목=크리에이터+빌드 1개라 creator 행이 중복된다. 항목 병합(이름 같으면 creator 재사용) 결정이 먼저. 지시서 범위(1밴드) 밖 |
| Arserina 점화 젬링 5밴드 | `build_planner/Ignite 1~5 - Arserina.build`(PoB 27e13) | 소프트코어 젬링 4번째 — ②③ 규칙에서 후순위 |

## 적재 파이프라인 (1명당, 지시서 5)

`data/hc_journey/creators/<slug>/` 픽스처 → `CREATORS` 항목(hardcore 는 근거 등급대로) → `build_db.py --build` → `--query --id N` 으로 상속 규칙 확인
→ `trade_links.py --realm both` → `render_journey.py` → `pytest python/tests/test_hc_journey_db.py test_render_journey.py test_trade_links.py test_rule_autodraft.py`
(크리에이터 수는 `CREATORS` 에 묶여 있고, 이름 집합만 `test_multi_creator_and_rules` 에 핀) → 커밋. 규칙 텍스트를 새로 쓰면 적대검증.
