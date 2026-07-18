# POE1 Site Index Probe Report

작성 시각: 2026-07-08 23:05 +07:00

## 1. Summary

- candidate_count: `19`
- candidate_with_any_match_count: `12`
- candidate_with_maxroll_match_count: `7`
- candidate_with_poe_vault_match_count: `6`
- candidate_with_upgradeable_match_count: `1`

해석:
- direct site index match는 `12개` 있었지만, temporal + archetype guard를 통과한 건 `1개`뿐이다.
- 즉 대부분의 매치는 `현재 가이드 존재`만 보여줄 뿐, historical patch evidence나 정확한 archetype confirmation으로는 부족하다.

## 2. Upgradeable Candidate

- `3.28_shock_nova_of_procession_hierophant` / lane `conversion_lane` / families `maxroll, poe_vault`
  - maxroll / maxroll_league_starter_index / alias `shock nova of procession`
  - maxroll / maxroll_build_guides_index / alias `shock nova of procession`
  - poe_vault / poe_vault_builds_index / alias `shock nova of procession`

## 3. False Positive Lessons

- `3.28_kinetic_fusillade_of_detonation`: Maxroll hit가 있었지만 `Ballista Hierophant`라 wander archetype과 불일치.
- `3.28_penance_brand_inquisitor`: Maxroll hit가 있었지만 `Ignite Elementalist`라 class mismatch.
- `3.28_cold_snap_of_power_hierophant`: PoE Vault hit가 있었지만 `Occultist`라 class mismatch.

결론: direct index evidence는 보조 근거로 유용하지만, strict 승격에는 temporal/archetype guard가 필수다.
