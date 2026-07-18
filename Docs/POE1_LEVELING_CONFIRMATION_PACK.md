# POE1 Leveling Confirmation Pack

작성 시각: 2026-07-09 +07:00

## 목적

최종 PoB/PoBB만 받은 상태에서는 레벨링 가이드를 `추론`으로 만들 수는 있어도 `확정`으로 만들 수는 없다.
`확정 레벨링`으로 승격하려면, 엔드게임 PoB 외에 `캠페인 진행 정보`가 별도 입력으로 필요하다.

이 문서는 PathcraftAI가 새 빌드를 받을 때 어떤 입력이 있으면 `추론`이 아니라 `확정`으로 레벨링을 생성할 수 있는지 정의한다.

## 핵심 결론

최종 PoB 1개만으로는 부족하다.
최소한 아래 4개 축이 있어야 한다.

- `스킬 전환 축`: Act/레벨별 메인 스킬, 보조젬, 전환 시점
- `패시브 축`: 레벨/액트별 패시브 우선순위, 트리 마일스톤
- `오라/유틸 축`: 각 구간 예약 세팅, 이동기, 가드, 자동화
- `기어/체크포인트 축`: 캠페인 동안 실제로 노리는 장비 목표와 전환 조건

## poe.ninja 표본과 레벨링 분리

poe.ninja 빌드 탭/캐릭터 표본은 `엔드게임 실제 사용례`를 확인하는 데 강하다.
하지만 대부분 이미 고레벨 캐릭터 스냅샷이므로, 그 자체만으로는 캠페인 레벨링 루트를 확정하지 않는다.

운영 원칙:

- `poe.ninja_profile`: endgame variant evidence
- `creator guide / forum guide / PoB notes`: leveling route evidence
- `stage PoB / stage snapshot`: confirmed leveling evidence

따라서 같은 Lightning Arrow, Hexblast, Spectre 빌드라도 사람마다 장비, 오라, 방어, 클러스터, 콘텐츠 목적이 다르면 같은 archetype 안의 다른 `variant`로 본다.
반대로 poe.ninja 최종 스냅샷만 있으면 레벨링은 계속 `추론` 상태로 남긴다.

관련 표본 계약:

- `data/poe1_creator_source_registry_v1.json`
- `data/poe_ninja_build_variant_sampling_plan_v1.json`
- `data/poe_ninja_build_variant_evidence_queue_v1.json`
- `data/poe1_leveling_archetype_route_plan_v1.json`

현재 운영 분리:

- caster: 3.27 Ice Nova Hierophant stage PoB를 우선 사용
- ranger: chaos bow는 기존 Toxic Rain stage PoB로 확정 가능, hit bow/Lightning Arrow는 최신 stage PoB가 더 필요
- melee: 3.25 Lightning Strike, 3.23 Boneshatter stage PoB를 우선 fallback으로 사용
- minion: 3.27 SRS, 3.28 Holy Relic stage PoB를 우선 사용한다. 토리센세의 이번 시즌 우선 source hunt는 Poison Carrion Golem로 분리하고, GhazzyTV/토리센세/dconnic 자료는 Spectre/소환수 쪽 추가 cross-check로 둔다
- totem: 3.28 Kinetic Fusillade Totem stage PoB를 우선 사용
- mine: Exsanguinate/Reap Miner Trickster를 기준으로 잡고, Cptn Garbage / Maxroll과 FearlessDumb0 staged PoB를 우선한다. 현재 `3.28_exsanguinate_reap_mines_trickster`는 `Rolling Magma -> Pyroclast Mine -> Exsanguinate Mine` profile smoke까지 통과했다. Jorgen/Conner Converse는 mine cross-check, 토리센세는 한국어 보조 확인과 소환수/Spectre 쪽 creator source로 유지한다

현재 creator source track:

- CWS: emiracle, Jorgen cross-check
- mine: Cptn Garbage, FearlessDumb0, Jorgen, Conner Converse
- experimental: CaptainLance9, Conner Converse
- minion: GhazzyTV, 토리센세, dconnic
- current Tori minion: Poison Carrion Golem, current-season PoB 수집 대기
- HC/SSF: Zizaran
- one-build specialists: POEGuy, ZeeBoub, Sanavixx

## 확정으로 올리기 위한 필수 준비물

### 1. Stage PoB 또는 Stage Snapshot

최소 3단계가 필요하다.

- `campaign_start`: Act 1~3 기준
- `campaign_mid`: Act 4~7 기준
- `campaign_end_or_early_maps`: Act 8~10 또는 맵 진입 기준

가장 좋은 형태:

- 단계별 PoB 3개 이상
- 또는 단계별 skill/tree/aura/gear snapshot JSON

없으면:

- 전 구간 `추론` 처리

### 2. Skill Timeline

반드시 필요하다.

최소 포함 항목:

- `level_range`
- `main_skill`
- `support_links`
- `swap_reason`
- `quest_source` 또는 `vendor_source`

예시:

- `Lv 1-11`: Stormblast Mine
- `Lv 12-27`: Arc
- `Lv 28+`: Ball Lightning
- `Lv 38+`: Guard skill + CWDT 자동화

이 정보가 없으면:

- 스킬 추천은 가능해도 `확정`이 아니라 archetype 기반 `추론`

### 3. Passive Milestones

최종 트리 URL만으로는 부족하다.

최소 필요 마일스톤:

- `Act 2 end`
- `Act 4 end`
- `Act 7 end`
- `Act 10 end`
- `early_maps`

각 마일스톤마다 필요한 것:

- 우선 노드 방향
- keystone 획득 시점
- life/accuracy/cast speed/minion/offense 등 왜 먼저 찍는지

가장 좋은 형태:

- stage별 passive tree URL
- 또는 `passive_priority`와 `milestone_nodes`

### 4. Aura / Utility Timeline

예약 스킬은 추측하면 오류가 많이 난다.

최소 필요:

- 각 구간 사용 오라
- 전령 사용 여부
- 이동기
- 가드 스킬
- curse/mark
- mana sustain 방식

특히 확인 필요:

- `Act 1-3`
- `Act 4-6`
- `Act 7-10`
- `early maps`

### 5. Gear Checkpoints

확정 레벨링은 “무슨 스킬을 쓴다”에서 끝나면 안 된다.
캠페인 동안 실제 전환 조건이 있어야 한다.

최소 필요:

- 3-link 시점
- 4-link 시점
- 첫 무기 업그레이드 기준
- 저항 목표
- 라이프 목표
- 특정 유니크/레어 조건

예시:

- `Act 3`: 3-link 확보
- `Act 5`: 저항 재정비
- `Act 8`: 4-link + 주요 오라 완성
- `Maps`: 75 all res, life threshold, main skill full link

### 6. Transition Trigger

전환은 레벨만으로 확정하면 안 되는 경우가 많다.
레벨 + 조건이 같이 필요하다.

최소 필요:

- `specific_level`
- `required_item_state`
- `required_links`
- `required_reservation_state`

예시:

- `Lv 28` and `4-link available`
- `Act 6 Lilly access`
- `Normal Lab complete`
- `Weapon upgrade acquired`

## 있으면 정확도가 크게 올라가는 추가 준비물

### 7. 실제 플레이 로그 또는 영상 근거

가장 강한 증거다.

예시:

- 액트별 vod timestamp
- pob notes
- creator guide notes
- pob custom modifiers / notes tab

이게 있으면:

- `추론`이 아니라 실제 route를 복원 가능

### 8. Quest Reward Intent

젬 획득 경로를 확정하려면 필요하다.

최소 필요:

- 클래스/전직
- 어떤 퀘스트에서 어떤 젬을 바로 집는지
- Siosa/Lilly 구매 전제 여부

### 9. Trade / SSF 모드 선언

이게 없으면 레벨링 장비 추천이 흔들린다.

필수 선언값:

- `trade_league_start`
- `ssf_league_start`
- `twink_leveling`

같은 빌드라도 이 값에 따라 레벨링 확정안이 달라진다.

## 확정 판정 규칙

### 확정

아래가 모두 있으면 가능:

- stage snapshot 3개 이상
- skill timeline 존재
- passive milestone 존재
- aura/utility timeline 존재
- gear checkpoint 존재
- transition trigger 존재

### 준확정

아래면 가능:

- final PoB 존재
- skill timeline 존재
- passive milestone 일부 존재
- aura 또는 gear checkpoint 일부 존재

이 경우는 기본 골격은 확정, 세부 수치 일부 추론

### 추론

아래 상태:

- final PoB만 있음
- leveling memo 없음
- 단계별 tree/skill snapshot 없음

이 경우는 archetype 기반 추천만 가능

## PathcraftAI 입력 패키지 권장 포맷

### 최소 권장 세트

- `final_pob_url`
- `build_mode` (`trade_league_start` / `ssf_league_start` / `twink_leveling`)
- `class_name`
- `ascendancy`
- `skill_timeline`
- `passive_milestones`
- `aura_utility_timeline`
- `gear_checkpoints`
- `transition_triggers`

### 베스트 세트

- 위 항목 전부
- `stage_pob_urls` 3~5개
- `creator_notes`
- `vod_timestamps`
- `quest_reward_plan`

## 현실적 운영 방안

새 빌드 PoB를 받을 때 입력 등급을 3단계로 받으면 된다.

- `Tier A`: final PoB only -> 추론 레벨링
- `Tier B`: final PoB + timeline memo -> 준확정 레벨링
- `Tier C`: final PoB + stage snapshots + timeline + checkpoints -> 확정 레벨링

## 결론

`추론 레벨링`을 `확정 레벨링`으로 바꾸려면 필요한 건 모델 성능이 아니라 입력 계약이다.
핵심은 `최종 PoB 1개`가 아니라 `캠페인 단계 정보 패키지`를 같이 받는 것이다.

이 패키지만 고정하면 PathcraftAI는 액트별 스킬, 오라, 전환, 패시브를 확정 상태로 생성할 수 있다.
