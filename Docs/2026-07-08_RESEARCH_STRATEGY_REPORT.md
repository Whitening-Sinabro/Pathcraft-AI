# POE1 Research Strategy Report

작성 시각: 2026-07-08 21:35 +07:00

## 1. Two-Lane Summary

- foundation lane: `5`
- conversion lane: `14`

해석:
- `foundation lane`은 아직 외부 가이드 0개라 strict까지 최소 2히트가 필요하다.
- `conversion lane`은 이미 외부 가이드 1개가 있어, 1히트만 더 넣으면 strict로 전환된다.

## 2. Foundation Lane

- `3.28_kinetic_fusillade_of_detonation` / patch `3.28` / score `167` / hits_to_strict `2`
- `3.28_penance_brand_inquisitor` / patch `3.28` / score `167` / hits_to_strict `2`
- `3.27_ice_nova_caster` / patch `3.27` / score `166` / hits_to_strict `2`
- `3.26_ball_lightning_caster` / patch `3.26` / score `165` / hits_to_strict `2`
- `3.26_ice_nova_caster` / patch `3.26` / score `160` / hits_to_strict `2`

## 3. Conversion Lane Top

- `3.28_cold_snap_of_power_hierophant` / patch `3.28` / score `137` / hits_to_strict `1`
- `3.27_pyroclast_mine_saboteur` / patch `3.27` / score `136` / hits_to_strict `1`
- `3.26_boneshatter_juggernaut` / patch `3.26` / score `135` / hits_to_strict `1`
- `3.26_siege_ballista_hierophant` / patch `3.26` / score `135` / hits_to_strict `1`
- `3.27_dominating_blow_guardian` / patch `3.27` / score `116` / hits_to_strict `1`
- `3.27_lacerate_duelist` / patch `3.27` / score `116` / hits_to_strict `1`
- `3.27_toxic_rain_pathfinder` / patch `3.27` / score `116` / hits_to_strict `1`
- `3.28_dominating_blow_guardian` / patch `3.28` / score `112` / hits_to_strict `1`
- `3.28_shock_nova_of_procession_hierophant` / patch `3.28` / score `112` / hits_to_strict `1`
- `3.26_lightning_arrow_ranger` / patch `3.26` / score `110` / hits_to_strict `1`

## 4. Operational Reading

- strict count를 가장 빨리 올리려면 `conversion lane`을 먼저 친다.
- 데이터 기반이 아예 없는 구간을 메우려면 `foundation lane`을 먼저 친다.
- 현재 약점이 가장 큰 patch는 여전히 `3.28`, `3.27`, `3.26` 순이다.
