# Skadoosh 배포 가이드 캡처 원본 (Mobalytics)

9/13 기준선 이동의 근거다. 받은 자리가 `.tmp/`(gitignore) 라 휘발성이어서 여기로 옮겼다.
받는 방법은 `scripts/fetch_mobalytics_builds.py` — Mobalytics 가 평범한 HTTP 에 403 을 주므로
Playwright MCP(Chrome)로 내려받는다. 탭을 하나씩 누를 필요 없이 zip 하나에 전부 들어온다.

- `warbringer_0_5_5_2026-09-12.zip` — 본 가이드 `mobalytics.gg/poe-2/builds/corrupting-cry-warbringer-skadoosh` (2026-09-12 캡처)
- `leveling_1_33_2026-09-13.zip` — 별도 레벨링 가이드 `mobalytics.gg/poe-2/builds/skadoosh-warbringer-leveling-41` (2026-09-13 캡처)
- `*_result.json` — 캡처 당시 탭별 성공/실패 기록

## 탭 목록 (실측)

| 출처 | 탭 파일 | 패시브 | 스킬 |
|---|---|---|---|
| 본 가이드 | Endgame (Outdated) - [0.5.5] Skadoosh's.build | 160 | SeismicCry, FortifyingCry, InfernalCry, ShockwaveTotem, ForgeHammer, Earthquake, MagmaBarrier, ScavengedPlating, WarBanner, AscendancyAncestralSpirits, AscendancyEncasedInJade |
| 본 가이드 | Endgame - [0.5.5] Skadoosh's Corrupting.build | 190 | FortifyingCry, AncestralWarriorTotem, SeismicCry, AscendancyAncestralSpirits, PurityOfLightning, PurityOfLightning, Sunder, MagmaBarrier, ScavengedPlating |
| 본 가이드 | Leveling - [0.5.5] Skadoosh's Corrupting.build | 85 | FortifyingCry, ShockwaveTotem, ForgeHammer, VolcanicFissure, MagmaBarrier |
| 본 가이드 | Starter - [0.5.5] Skadoosh's Corrupting.build | 83 | FortifyingCry, AncestralWarriorTotem, SeismicCry, MagmaBarrier, AscendancyAncestralSpirits |
| 본 가이드 | Uber Endgame (outdated) - [0.5.5] Skadoo.build | 170 | SeismicCry, FortifyingCry, InfernalCry, AncestralWarriorTotem, ForgeHammer, ShockwaveTotem, ScavengedPlating, ChargeInfusion, AscendancyAncestralSpirits, AscendancyEncasedInJade, ShieldBlock |
| 별도 레벨링 1-33 | Level 1 - 10 - Skadoosh's Warrior Leveli.build | 10 | PlayerDefault2HMace, Boneshatter, RollingSlam, InfernalCry, ShieldBlock |
| 별도 레벨링 1-33 | Level 11 - 20 - Skadoosh's Warrior Level.build | 34 | PlayerDefault2HMace, Boneshatter, RollingSlam, ShockwaveTotem, Earthquake, InfernalCry, MagmaBarrier |
| 별도 레벨링 1-33 | Level 21 - 30 - Skadoosh's Warrior Level.build | 52 | PlayerDefault2HMace, Boneshatter, RollingSlam, ShockwaveTotem, Earthquake, VolcanicFissure, MagmaBarrier, InfernalCry, HeraldOfAsh |
| 별도 레벨링 1-33 | Level 31 - 41 - Skadoosh's Warrior Level.build | 64 | Boneshatter, RollingSlam, ForgeHammer, ShockwaveTotem, Earthquake, InfernalCry, MagmaBarrier, HeraldOfAsh |

주의: `(outdated)` 표시가 붙은 탭은 제작자가 구버전으로 남겨 둔 것이다. 현재 탭은
Leveling(85) · Starter(83) · Endgame(190) 셋이다. 별도 레벨링 가이드는 네 탭 모두 세트 I 이
한손 철퇴 + 타워 방패이고 세트 II 가 양손 철퇴다 — `PlayerDefault2HMace` 는 기본 공격 항목일 뿐이라
무기 종류의 근거가 되지 않는다(31-41 탭엔 그 항목조차 없다).

Starter 탭의 보강하는 함성은 파콰테의 맹약(요구 65) + 메아리치는 함성을 달고 있어서 우리 06 에
해당한다. 05 에 대응하는 탭은 없다.
