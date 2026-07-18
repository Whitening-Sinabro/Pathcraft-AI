# POE1 Build Corpus Schema

## 목적

이 문서는 POE1 빌드 코퍼스를 `빌드 이름 모음`이 아니라 `아키타입 + 구간별 운영 상태 + 근거` 데이터로 저장하기 위한 기준이다.

핵심 목표는 세 가지다.

1. 최신 리그 빌드를 추천 가능한 형태로 저장한다.
2. 자막/메모가 부실해도 액트 운영을 일정 수준 복원한다.
3. 기존 `build_coach.py` 출력 스키마를 채울 수 있는 입력 구조를 만든다.

## 왜 기존 방식이 부족한가

- 카테고리별로 빌드 이름만 2~3개 넣으면 중복이 폭증한다.
- 같은 빌드의 리그 초기/중기/후기 상태가 분리되지 않는다.
- `유행하던 빌드` 기준이 모호하면 수집자 취향 데이터가 된다.
- 메모가 없을 때 `액트 스킬`, `오라`, `전환 시점`을 복원할 수 없다.

## 저장 단위

저장 단위는 `개별 빌드 글`이 아니라 `archetype record`다.

예:

- `strength_stacker_juggernaut`
- `lightning_arrow_deadeye`
- `righteous_fire_chieftain`
- `hexblast_miner_trickster`

하나의 아키타입 레코드 안에 아래를 넣는다.

- 패치/리그 메타 정보
- 역할 태그
- 레벨링 복원 템플릿
- phase variants
- evidence
- 최근 메타 스냅샷

## 계층 구조

### 1. Era Layer

역사 보관용.

- `legacy_pre_ascendancy`
- `legacy_atlas`
- `modern_transfigured`
- `modern_current`

추천 엔진의 1차 입력은 아님.

### 2. Patch Layer

실사용 핵심 축.

- `3.22`
- `3.23` Affliction
- `3.24`
- `3.25`
- `3.26`
- `3.27`
- `3.28`

패치별로 아키타입 성능과 운영이 달라지므로 별도 레코드를 허용한다.

### 최소 지원 범위

현 시점 최소 지원 범위는 `3.22 ~ 3.28`이다.

- `3.22` Trial of the Ancestors
- `3.23` Affliction
- `3.24` Necropolis
- `3.25` Settlers of Kalguur
- `3.26` Secrets of the Atlas / Mercenaries of Trarthus
- `3.27` Keepers of the Flame
- `3.28` Mirage

이 범위보다 오래된 시즌은 역사 보관 대상으로만 넣고, 추천 엔진의 필수 코퍼스에는 포함하지 않는다.

### 미래 패치 규칙

`3.29`처럼 아직 출시 확인이 되지 않은 패치는 `live corpus`에 넣지 않는다.

- 허용 상태: `watchlist`, `announced`, `speculative`
- 금지 상태: `early/mid/late meta snapshot`, `live archetype record`

즉, 미래 패치는 코퍼스 엔트리가 아니라 감시 대상 메타데이터로만 취급한다.

### 3. League Window Layer

리그 내 메타 시점.

- `early`
- `mid`
- `late`

이건 별도 빌드 3개가 아니라, 같은 아키타입 안의 메타 상태다.

### 4. Build Phase Layer

실제 플레이 구간.

- `campaign_start`
- `campaign_mid`
- `campaign_late`
- `maps_entry`
- `early_endgame`
- `mid_endgame`
- `late_endgame`
- `high_end`

### 5. Evidence Layer

근거를 별도 저장한다.

- `pob`
- `video_transcript`
- `video_description`
- `poe_ninja`
- `forum_guide`
- `manual_curated`

## 카테고리 설계 원칙

카테고리는 단순 장르가 아니라 검색 질의에 바로 연결되는 태그여야 한다.

### 역할 태그

- `league_starter`
- `campaign_smooth`
- `mapper`
- `bosser`
- `tanky`
- `ssf_friendly`
- `hc_viable`
- `cheap_entry`
- `high_ceiling`
- `reroll_target`

### 콘텐츠 태그

- `delve_good`
- `sanctum_good`
- `heist_good`
- `legion_good`
- `expedition_good`
- `blight_good`
- `boss_rush_good`

### 구조 태그

- `requires_respec`
- `requires_unique_to_function`
- `attribute_stacker`
- `crit_scaler`
- `totem`
- `mine`
- `dot`
- `trigger`
- `minion`

## 최소 코퍼스 기준

`카테고리마다 2~3개`라는 말은 유지하되, 저장 단위는 아키타입 기준으로 본다.

권장 최소선:

- 최신 패치 핵심 아키타입: 20~30개
- 아키타입당 phase variants: 3~5개
- 역할 태그당 대표 아키타입: 최소 3개
- 최신 패치별 메타 스냅샷: early/mid/late

최소 히스토리 범위 `3.22 ~ 3.28`에 대해선 아래를 우선 충족한다.

- 패치당 대표 아키타입: 최소 12개
- 역할 태그 핵심군: `league_starter`, `mapper`, `bosser`, `tanky`, `ssf_friendly`, `reroll_target`
- 각 역할 태그당 패치별 대표 아키타입: 최소 2개

즉, 빌드 이름 100개보다 `상태가 분화된 60~150 records`가 더 낫다.

## 메모 없는 경우 복원 규칙

각 아키타입 레코드는 아래 복원 필드를 반드시 가진다.

- `campaign_primary_skill`
- `campaign_fallback_skill`
- `first_lab_power_spike`
- `switch_conditions`
- `aura_priority_early`
- `aura_priority_mid`
- `link_priority_3l`
- `link_priority_4l`
- `weapon_upgrade_rules`
- `gear_checkpoints`

이 필드가 있어야 자막이 부실해도 `액트 1~10 운영표`를 만들 수 있다.

## build_coach 호환 목표

기존 `build_coach.py`는 아래 입력을 요구한다.

- `leveling_skill_progression`
- `aura_progression`
- `aura_herald_utility_by_level`
- `curse_setup`
- `movement_skill`

새 스키마는 그보다 넓게 저장하되, 아래 호환 섹션을 제공한다.

- `coach_compat.leveling_skill_progression`
- `coach_compat.aura_progression`
- `coach_compat.aura_herald_utility_by_level`
- `coach_compat.curse_setup`
- `coach_compat.movement_skill`

## 수집 기준

### `patch_status`

패치 상태를 반드시 구분한다.

- `historical_supported`
- `current_live`
- `watchlist`
- `announced_only`
- `speculative_only`

예:

- `3.22 ~ 3.27`은 보통 `historical_supported`
- `현재 최신 공개 리그`는 `current_live`
- `3.29`처럼 미출시면 `watchlist` 또는 `announced_only`

### `meta_popularity_basis`

유행 판단 기준을 명시해야 한다.

- `poe_ninja_share`
- `creator_coverage`
- `race_presence`
- `community_index_presence`
- `manual_curator_weight`

### `confidence`

권장 4단계:

- `high`
- `medium`
- `low`
- `speculative`

예:

- PoB + 영상 + poe.ninja + 포럼이 다 있으면 `high`
- 자막만 있고 PoB가 없으면 `medium`
- 영상 일부 언급만 있으면 `low`
- 운영 추정만 있으면 `speculative`

## 권장 수집 순서

1. `3.22 ~ 3.28` 패치별 대표 아키타입 풀 선정
2. 아키타입별 대표 evidence 2개 이상 확보
3. 각 패치의 league window early/mid/late 메타 요약
4. phase variants 작성
5. 메모 없는 경우 복원 템플릿 작성
6. `coach_compat` 필드 생성
7. 미래 패치는 `watchlist`에만 적재

## 비목표

- 모든 빌드의 완전한 PoB 복제
- 역사상 모든 niche build 보관
- 하나의 정답 빌드 강제

이 스키마의 목적은 `추천`, `복원`, `비교`, `질의 응답`이다.


