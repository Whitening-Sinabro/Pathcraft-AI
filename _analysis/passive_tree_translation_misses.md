# Passive Tree 번역 미스 분석

총 고유 stat: 2559 | 매칭: 2352 | 미스: **207** (8.1%)

생성 스크립트: `_analysis/_gen_translation_misses.py` (일회성)

## 분류

| 패턴 | 건수 | 설명 |
|------|------|------|
| 멀티라인 (`\n` 포함) | 82 | 공식 데이터에 개행이 있음. mods 사전 개행 규칙과 불일치. 공백 치환해도 82 중 2건만 복구. |
| Trigger Level 고정 | 2 | "Trigger Level 20 ..." 형태 — mods에 level 추상화 없음 |
| 기타 | 123 | mods 사전 자체 누락 추정 (POE 업데이트로 추가된 신규 stat) |

## 개선 옵션

1. **mods 사전 업데이트** (근본 해결) — `poe_translations.json`을 최신 소스에서 재수집. 프로젝트 범위 외, 별도 작업 필요.
2. **문장 유사도 매칭** — 현재 exact match만. 미스 하나당 `difflib` 또는 임베딩으로 최근접 mods 키 찾기. ROI 불확실 (false match 위험).
3. **수동 사전 오버레이** — `data/skilltree-export/passive_tree_overlay.json`에 미스된 stat만 직접 한국어 작성. 207건 번역 가능하나 유지보수 부담.

**현재 권고: 보류.** 91.9% 커버는 실용적 임계. 인게임 검증에서 구체적 pain이 나오면 그때 3번 오버레이 도입 재검토.

## 샘플

### multiline (82)

- `+10% to all Elemental Resistances and maximum Elemental Resistances while affected by a Non-Vaal Guard Skill / 20% additional Physical Damage Reduction while affected by a Non-Vaal Guard Skill / 20% more Damage taken if a Non-Vaal Guard Buff was lost Recently`
- `+2 to maximum number of Sacred Wisps / +2 to number of Sacred Wisps Summoned`
- `+4% to Critical Strike Multiplier for each Mine Detonated / Recently, up to 40%`
- `-1 to maximum number of Summoned Totems / You can have an additional Brand Attached to an Enemy`
- `-10% to maximum Chance to Block Attack Damage / -10% to maximum Chance to Block Spell Damage / +2% Chance to Block Spell Damage for each 1% Overcapped Chance to Block Attack Damage`
- `1.5% of Physical Damage prevented from Hits in the past / 10 seconds is Regenerated as Life per second`
- `10% increased Critical Strike Chance for each Mine Detonated / Recently, up to 100%`
- `10% increased Effect of Arcane Surge on you per / 200 Mana spent Recently, up to 50%`
- `100% chance to Defend with 200% of Armour / Maximum Damage Reduction for any Damage Type is 50%`
- `20% increased Maximum total Life Recovery per second from / Leech if you've dealt a Critical Strike recently`
- `20% less Attack Damage taken if you haven't been Hit by an Attack Recently / 10% more chance to Evade Attacks if you have been Hit by an Attack Recently / 20% more Attack Damage taken if you have been Hit by an Attack Recently`
- `40% more Attack Damage if Accuracy Rating is higher than Maximum Life / Never deal Critical Strikes`
- `5% chance to Defend with 200% of Armour for each / time you've been Hit by an Enemy Recently, up to 30%`
- `5% increased Poison Duration for each Poison you have inflicted Recently, up / to a maximum of 100%`
- `50% less Life Regeneration Rate / 50% less maximum Total Life Recovery per Second from Leech / Energy Shield Recharge instead applies to Life`
- `50% of Physical, Cold and Lightning Damage Converted to Fire Damage / Deal no Non-Fire Damage`
- `Attack Projectiles always inflict Bleeding and Maim, and Knock Back Enemies / Projectiles cannot Pierce, Fork or Chain`
- `Auras from your Skills can only affect you / Aura Skills have 1% more Aura Effect per 2% of maximum Mana they Reserve / 40% more Mana Reservation of Aura Skills`
- `Auras from your Skills grant 2% increased Attack and Cast / Speed to you and Allies`
- `Auras from your Skills grant 3% increased Attack and Cast / Speed to you and Allies`
- ... (+62 more)

### trigger (2)

- `Trigger Level 20 Summon Spectral Tiger on Critical Strike`
- `Trigger Level 20 Ward Shatter when your Ward Breaks`

### other (123)

- `+1 Ring Slot`
- `+100% to Critical Strike Multiplier against Enemies that are not on Low Life`
- `+100% to Critical Strike Multiplier against Enemies that are on Low Life`
- `+12% to Damage Over Time Multiplier with Spell Skills`
- `+2 to Level of all Aura Skill Gems`
- `+2 to Level of all Cold Skill Gems if at least 4 Foulborn Unique Items are Equipped`
- `+2 to Level of all Lightning Skill Gems if at least 4 Foulborn Unique Items are Equipped`
- `+4% to Damage Over Time Multiplier with Spell Skills`
- `+6% to Damage Over Time Multiplier with Spell Skills`
- `-25 Damage taken of each Damage Type from Spell Hits per Bark`
- `10% increased Defences per Raised Spectre`
- `100% more Critical Strike Chance against Enemies that are not on Low Life`
- `12% increased Damage Over Time with Spell Skills`
- `15% increased Area of Effect for Attacks while you have at least 1 nearby Ally`
- `15% increased Attack Damage per Raised Zombie`
- `15% increased Ward from Equipped Armour Items`
- `16% increased Damage Over Time with Spell Skills`
- `2% increased Movement Speed per Summoned Phantasm`
- `20% increased magnitude of Hallowing Flame you inflict`
- `3% increased Attack Speed per Fortification above 20`
- ... (+103 more)
