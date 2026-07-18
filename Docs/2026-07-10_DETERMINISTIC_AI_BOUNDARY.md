# Deterministic + AI Boundary Addendum

작성 시각: 2026-07-10 +07:00

이 문서는 기존 `Docs/POE1_RECOMMENDATION_FILTER_SYSTEM.md` 위에 얹는 보충 규칙이다.
목표는 세 가지다.

- 어떤 판정을 절대 규칙 기반으로 고정할지 분리
- AI를 어디까지 허용할지 경계 정의
- low-confidence 케이스에서 `Plan B / C / D` 와 검증 루프를 고정

## 1. 절대 규칙 기반으로 고정할 판정

아래는 AI가 뒤집으면 안 되는 guard다.

- `patch_guard`
  - 유저 패치와 build patch가 다르면 차단
  - patch survival 검증 전까지 AI가 `현역이다` 라고 승격 금지
- `character_guard`
  - `character_locked = true` 이고 클래스/전직이 다르면 차단
  - AI가 reroll 전제를 몰래 삽입하면 안 됨
- `skill_guard`
  - `must_use_skill` 불일치면 exact 추천 차단
  - 다만 same-class + same-ascendancy in-place proxy로 내리는 것은 허용
- `input_guard`
  - `max_input_style` 상한 초과 시 차단
  - 조작 난도를 AI 문장으로 완화 금지
- `availability_guard`
  - `trade_mode = ssf` 이고 `ssf_viable = low` 면 차단
  - 거래 전제를 AI가 숨기면 안 됨
- `budget_guard`
  - `budget_fit_ratio > 1.80` 이면 차단
  - `1.35 < ratio <= 1.80` 은 soft-tight로 유지
- `confidence_guard`
  - `require_confirmed_leveling = true` 인데 leveling 확정이 아니면 차단
  - `representative_build_status = hold` 는 soft 경고로 유지

정리하면 `패치 / 캐릭터 고정 / 스킬 강제 / 입력 상한 / SSF 가능성 / 예산 바닥 / 확정 레벨링 요구` 는 deterministic 레이어다.

## 2. AI 허용 경계

AI는 `결정자`가 아니라 `설명자` 또는 `정리자` 로만 쓴다.

### 허용 모드

- `explain_only`
  - deterministic 추천이 이미 안정적일 때만 허용
  - 허용: 랭킹 이유 설명, 업그레이드 순서 설명, 콘텐츠 tradeoff 요약
- `bounded_fill`
  - core guard는 통과했지만 일부 구조화 필드가 약할 때 허용
  - 허용: progression 요약, evidence 부족 설명, 업그레이드 TODO 정리
- `proxy_only`
  - exact build는 막혔고 proxy만 가능한 경우
  - 허용: same-class proxy 제안, starter phase bridge, respec vs reroll 설명
- `verification_only`
  - confidence가 fragile한 경우
  - 허용: 무엇이 비었는지, 어떤 증거가 더 필요한지, 왜 abstain인지 설명
- `disabled`
  - hard deterministic conflict가 있으면 추천 판단에 AI 사용 금지

### AI 금지 오버라이드

아래는 AI가 문장으로도 덮어쓰면 안 된다.

- `patch_guard`
- `character_guard`
- `input_guard`
- `availability_guard`
- `budget_guard`
- `representative_build_status`
- `leveling_confidence`

즉 AI는 `추천 가능 여부` 자체를 바꾸지 못하고, 이미 결정된 상태를 해설하거나 proxy/verification 루프를 정리하는 데만 쓴다.

## 3. low-confidence Plan B / C / D

### Plan B

조건:

- hard block 없음
- exact build 자체는 유지 가능
- 다만 `hold_status`, `budget_tight`, `content soft miss`, `leveling inferred` 같은 약점 존재

행동:

- exact candidate는 유지
- UI/응답에 soft-relaxed 상태를 노출
- confidence 승격 전까지 `confirmed` 식 표현 금지

### Plan C

조건:

- exact build는 유지 불가
- same-class + same-ascendancy in-place proxy 또는 starter bridge는 가능

대표 트리거:

- `skill_mismatch`
- exact endgame skill은 비싸지만 starter shell은 가능
- reroll 없이 현재 클래스에서 proxy만 실전 가능

행동:

- same-class proxy 또는 earlier starter phase로 강등
- exact build가 왜 막혔는지 trace 유지

### Plan D

조건:

- hard deterministic conflict 존재
- patch survival 불명
- 예산 바닥 미달
- 입력 정보/증거가 너무 부족

행동:

- 추천 보류
- 가장 작은 blocking set 반환
- 승격에 필요한 추가 입력 또는 추가 evidence 반환

## 4. 검증 루프

low-confidence exact candidate는 아래 루프를 통과해야 한다.

1. `deterministic_guard_replay`
   - hard block 유무 재확인
2. `representative_evidence_check`
   - source type 수, hold 여부, patch 생존성 재확인
3. `leveling_route_check`
   - leveling confidence가 `confirmed / near_confirmed / inferred` 중 어디인지 확인
4. `budget_floor_check`
   - exact entry 가능 여부와 starter split 필요 여부 확인
5. `plan_resolution`
   - 그대로 `B` 유지, `C` 로 강등, `D` 로 abstain 중 하나 확정

## 5. 승격 조건

fragile case가 A/B로 올라가려면 아래 중 해당 항목을 채워야 한다.

- hold exact build: 독립 source type 1개 이상 추가
- inferred leveling: transition evidence 또는 campaign progression 증거 추가
- budget-tight build: starter entry package 분리 또는 예산 상향
- patch mismatch: patch survival 재검증
- skill mismatch exact demand: proxy 허용 또는 exact lock 해제

## 6. 코드 반영 위치

현재 이 규칙은 아래 코드에서 실행된다.

- `python/recommendation_contract_audit.py`
  - deterministic guard 결과
  - AI policy mode
  - verification loop
- `python/recommendation_engine.py`
  - 최종 recommendation payload에 guardrail 메타데이터 노출


## 7. API / UI 응답 계약

`recommend_from_corpus` 와 `recommendation_engine` 의 최종 recommendation payload는 아래 두 레이어를 같이 노출한다.
기존 top-level 필드도 유지하지만, 소비자는 아래 두 묶음을 우선 사용한다.

### `guardrails`

추천 판단 자체를 설명하는 canonical 메타.

- `deterministic_guards`
  - 각 guard의 `guard / status / reason`
  - `pass / soft / proxy / block` 중 하나로 고정
- `ai_policy`
  - `mode`
  - `allowed_slots`
  - `forbidden_overrides`
- `verification_loop`
  - `confidence_lane`
  - `loop_state`
  - `steps`
  - `promotion_requirements`
  - `next_actions`

### `response_layers`

UI와 AI 설명 계층을 분리한 deterministic 응답 레이어.

- `decision`
  - `plan`
  - `decision_state`
  - `candidate_path`
  - `blocking_guards`
  - `warning_guards`
- `user_message`
  - `template_id`
  - `title`
  - `summary`
  - `bullets`
- `ui_panels`
  - `show_deterministic_guards`
  - `show_ai_policy`
  - `show_verification_loop`
- `ai_explanation`
  - `mode`
  - `instruction`
  - `allowed_slots`
  - `forbidden_overrides`
- `badges`
  - `plan / lane / ai_mode / guard` badge 배열

예시 스케치:

```json
{
  "selected_plan": "B",
  "guardrails": {
    "deterministic_guards": [...],
    "ai_policy": {...},
    "verification_loop": {...}
  },
  "response_layers": {
    "decision": {
      "plan": "B",
      "decision_state": "exact_with_warnings",
      "candidate_path": "exact"
    },
    "user_message": {
      "template_id": "plan_b_hold_exact"
    },
    "ai_explanation": {
      "mode": "verification_only"
    }
  }
}
```

## 8. Plan B / C / D 메시지 템플릿 고정

AI는 아래 템플릿을 선택하지 않는다.
AI는 deterministic이 선택한 `template_id` 를 보고 허용 슬롯만 채운다.

### Plan B

- `plan_b_hold_exact`
  - exact candidate 유지 + hold 경고
- `plan_b_budget_tight`
  - exact candidate 유지 + near-budget 경고
- `plan_b_soft_content_miss`
  - exact candidate 유지 + content soft miss 경고
- `plan_b_watch_exact`
  - exact candidate 유지 + watch 상태 경고

### Plan C

- `plan_c_skill_proxy`
  - exact skill mismatch로 same-class + same-ascendancy proxy 또는 bridge만 허용
- `plan_c_proxy_bridge`
  - exact path 전체가 막혀 bridge/proxy만 허용

### Plan D

- `plan_d_patch_block`
- `plan_d_budget_block`
- `plan_d_character_lock`
- `plan_d_input_block`
- `plan_d_leveling_block`
- `plan_d_abstain_generic`

정리하면 deterministic은 `plan + template_id + guardrails` 를 고정하고,
AI는 `response_layers.ai_explanation.allowed_slots` 안에서만 설명을 추가한다.

## 9. 실제 코퍼스 시뮬레이션

회귀 테스트와 UI 확인용 실제 케이스는 아래 조합으로 고정한다.

### B: hold -> B

- user patch/class/asc: `3.28 / Shadow / Trickster`
- desired skill: `Kinetic Fusillade of Detonation`
- `allow_hold_fallback = true`
- expected:
  - `active_scope = fallback_with_hold`
  - `selected_plan = B`
  - `selected_candidate.candidate_id = 3.28_kinetic_fusillade_of_detonation`
  - `template_id = plan_b_hold_exact`

### C: skill mismatch -> C

- same input as above
- `allow_hold_fallback = false`
- expected:
  - `active_scope = default_non_hold`
  - `selected_plan = C`
  - `template_id = plan_c_skill_proxy`

### D: patch hard block -> D

- user patch/class/asc lock: `3.27 / Templar / Hierophant`
- desired skill: `Shock Nova of Procession`
- `character_locked = true`
- `allow_hold_fallback = false`
- expected:
  - `selected_plan = D`
  - `blocking_candidate.candidate_id = 3.28_shock_nova_of_procession_hierophant`
  - `ai_policy.mode = disabled`
  - `template_id = plan_d_patch_block`
  - `loop_state = abstain`

### D: budget hard block -> D

- user patch/class/asc: `3.28 / Templar / Hierophant`
- desired skill: `Shock Nova of Procession`
- `character_locked = true`
- `liquid_divines = 0.2`
- expected:
  - `selected_plan = D`
  - `blocking_candidate.candidate_id = 3.28_shock_nova_of_procession_hierophant`
  - `ai_policy.mode = disabled`
  - `template_id = plan_d_budget_block`
  - `loop_state = abstain`

## 9. Actual QA Case Set

실제 representative row를 재사용하는 경계 QA 케이스는 `python/build_recommendation_boundary_cases.py` 에서 생성한다.
이 리포트는 corpus API 응답과 단일 profile compatibility 둘 다 재현한다.

고정 케이스:

- `corpus_hold_exact_fallback_plan_b`
  - `3.28_kinetic_fusillade_of_detonation`
  - hold-only exact skill을 hold fallback으로 재진입시키면 `Plan B` + `plan_b_hold_exact`
- `profile_hold_skill_mismatch_plan_c`
  - `3.26_ball_lightning_caster`
  - same-class + same-ascendancy에서 exact skill만 바꾸면 `Plan C` + `plan_c_skill_proxy`
- `profile_hold_patch_block_plan_d`
  - `3.26_ball_lightning_caster`
  - patch만 어긋나면 `Plan D` + `plan_d_patch_block`
- `profile_hold_budget_block_plan_d`
  - `3.26_ball_lightning_caster`
  - 예산 바닥 미달이면 `Plan D` + `plan_d_budget_block`
- `corpus_cross_class_proxy_scope_plan_d`
  - cross-class `Ball Lightning` 요구는 in-place proxy로 새지 않고 `Plan D` + `plan_d_proxy_scope_block`

이 케이스들은 다음 회귀를 같이 막는다.

- hold exact fallback이 `Plan B` 대신 무조건 abstain으로 붕괴되는 회귀
- same-class + same-ascendancy proxy가 `Plan C` 밖으로 밀리는 회귀
- cross-class/cross-ascendancy skill mismatch가 `Plan C` 로 잘못 노출되는 회귀
- patch/budget hard block에서 AI 설명 계층이 recommendation decision을 침범하는 회귀
