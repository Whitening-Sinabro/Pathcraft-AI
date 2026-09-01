# Tangjeong (탱정-탱커의정석) — POE2 0.5 Build Deep-Dive: Cursemaster Chronomancer & Shield Wall Kitava

- Date: 2026-09-01. Requested scope: "커스마스터, 방패벽 키타바 — 3개월전 영상부터 정밀분석".
- Channel: **탱정-탱커의정석** (`UCSlN0zTczYpNJHCbskGuYaw`, ~1.32k subs). Tank-first POE2 creator, self-described: prefers sturdy/no-death builds over fast/glassy ones. Community hub: https://cafe.naver.com/tankjung + Discord. Regular lives Mon/Wed/Fri.
- **Both requested builds are POE2 0.5-season builds** (league "Runes of Aldur" per PoB metadata), not POE1.
- Evidence tiers used here: ① guide-video auto-captions (timestamped), ② poe.ninja POE2 PoB snapshots (decoded XML, `poe.ninja/poe2/pob/raw/{id}`), ③ creator's public Google Doc (wand Q&A/crafting), ④ video descriptions. Live streams (2.5–4h, 16 of them) were NOT transcribed — only their descriptions/PoB links were used.

## 1. Upload timeline (2026-05-28 → 2026-08-28, 36 uploads)

| Date | Video | Role |
|---|---|---|
| 05-28 | `S0qmdg6RttI` 0.5 저주 빌드 스타팅 플랜 (4m) | season plan: Chronomancer & Abyssal Lich curse lanes |
| 06-12~06-14 | Abyssal Lich alt leveling lives | curse lane warm-up |
| 06-15~06-28 | Cursemaster Chronomancer research lives ×4 | setting evolution |
| **06-20** | `az5BHq58QU8` **커스마스터 커스텀 빌드 가이드** (16:00, 14.9k views) | guide v1 (10-divine contest winner build) |
| **07-04** | `Y-SyfaeYyeo` **커스마스터 최종 가이드** (21:40, 17.6k views) | guide FINAL |
| 07-06~07-12 | "불사 리치" (immortal Lich) research lives ×4 | side lane, abandoned for warrior |
| 07-13~08-08 | Warrior/Shield Wall research lives ×8 | Shield Wall born 07-18 |
| **08-02** | `ncQUAsv0HsI` **방패벽 키타바 하이엔드 가이드** (30:42, 23.0k views) | guide (high-end, ~500div entry) |
| **08-17** | `QcSeQ0OOENI` **방패벽 키타바 저자본 빌드업 가이드** (18:36, 6.5k views) | guide (≈15div bridge build) |
| 08-17~08-21 | "마샬 아티스트" alt lives ×4 (martial-artist experiment) | verdict: failed → return to Kitava |
| **08-23** | `lYkslTUZfA4` 키타바 방패벽 **2.0** 출시 live (3h25m) | 2.0 first reveal (0 deaths / ~1-button) |
| 08-25 | `wbWGFYHEi-E` 2.0 예고편 (2:09, no speech) | trailer; mechanism note in description |
| 08-26 | `k9qAUtJerig` 2.0 Q&A/메커니즘 분석 live | latest ninja snapshot |
| 08-28 | next-league prep live | — |

**As of 2026-09-01 the full "2.0 guide" video is NOT yet uploaded** (trailer promised it "this week"; last upload is 08-28). Latest 2.0 ground truth = ninja `278f6` (08-26) + trailer description + 08-23 live.

## 2. PoB snapshot chain (all decoded from `poe.ninja/poe2/pob/raw/{id}`)

Cursemaster: `21a7e` (100div, 06-20) · `21a90`/`22c27` (pre-high-end, 06-20) · **`25f87` (FINAL guide, 07-04)** · plus v1 10-div-contest build at `poe2db.tw/pob/ssooqAzPid` (not parsed).
Shield Wall: `25e1c` (birth 07-18) · `25b36`/`260eb` (07-19) · `26341` (07-22) · **`26e5d` (high-end guide 08-02)** · `26b82` (lives 08-02~08) · **`274b9` (low-budget guide 08-17)** · `277af` (2.0 release 08-23) · `278a0` (2.0 trailer 08-25) · **`278f6` (2.0 latest 08-26)**. Ninja nickname for 2.0: `ROA_WarriorTanker_Build`.

### Key computed stats (PoB cache inside each snapshot)

| Snapshot | Class | DPS (Combined) | Life | ES | Armour | EHP | MaxHit phys/ele | Res |
|---|---|---|---|---|---|---|---|---|
| Cursemaster FINAL `25f87` | Chronomancer 97 | 1.9k (PoB fails to model doom-blast loop; not real DPS) | 1,629 | 5,948 | — | 24.6k | 10.9k / 39.0k | 75/75/75/75 |
| Shield Wall high-end `26e5d` | Smith of Kitava 97 | 165k (wall-break amp not modeled) | 2,113 | — | 28.9k | 31.3k | 4.7k / 16.0k | 87/87/87/75 |
| Shield Wall low-budget `274b9` | Smith of Kitava 97 | 113k | 2,375 | — | 4.6k | 11.8k | 3.3k / 11.2k | 80/80/80/73 |
| Shield Wall 2.0 `278f6` | Smith of Kitava 97 | 114k | 2,024 | — | 24.3k | 26.5k | 4.6k / 15.5k | 86/86/86/75 |

## 3. Build 1 — Cursemaster Chronomancer (Sorceress)

**Core damage loop**: Despair (곡 quality 23) + **Impending Doom**(임박한 멸망) + Doedre's Undoing + Spell Cascade/Controlled Destruction/Efficiency → doom-blast pops when the curse ends. Keystone **멸망의 속삭임** (curse-limit +1) is mandatory — Blasphemy keeps Temporal Chains permanently on enemies, so without +1 limit Despair never lands and *nothing explodes* (guide 17:03; #1 FAQ item). "Speed style" uses Spell Cascade: cursed-ground cap is 2, cascade lays 3 → the 1st ground expires instantly → curse-end → instant pop (v1 guide 2:41).

**Two operating styles** (v1 guide): 안전형 (cast-and-forget, best single-target) vs 속도형 (cascade chain-popping, screen-wipe feel; higher mana cost, weaker vs bosses — swap Spell Cascade→Overabundance(과잉 추정) for bosses).

**Self-curse engine (the "Cursemaster" identity)**: Enfeeble linked with **Atziri's Allure** (혈통잼) reflects the curse to yourself, on purpose. Tree node **수호하는 숭배물** gives +30% damage per curse on you; map-mod curses (Enfeeble/Ele Weakness/Temporal Chains) then become damage buffs. Requires **reduced-curse-effect-on-self ≥ 120%**: 수호하는 숭배물+path 45% + 내면의 믿음 25% + Kraken-guard rune(크라칸의 수호) in body armour (FINAL 18:59). v1/Google-Doc used a 100% recipe (숭배물 60% + 내면의 믿음 25% + 노쇠의 저주-adjacent 15%); FINAL raised it to 120% because the Impending-Doom passive adds +20% curse effect at half-duration, which would flip the reflect into a debuff at exactly 100%.

**Weapon axes** (FINAL 1:46–5:43):
- **Staff (지팡이) = default below high-end.** Any staff; Chiming/"타임벨" base preferred for its bonus skill. Suffix: +7 to fire/cold/lightning/chaos spell skills (one). Prefix: 2 of 3 "gain % as extra ele" + 1 increased-damage line (일반: gain ≥50%, increase ≥180%). Then socket rune **Betrayal of Aldur** (알두르의 배신) → converts all elemental to chaos. Item must be un-corrupted/un-consecrated and **not fractured on the damage mods** or conversion breaks.
- **Wand+focus = high-end**: wand +4 all spell skills / +5 chaos spell skills, 3× gain-as-extra prefixes (≥28% each at top end); focus +2 all spells + chaos/spell damage ≥160%. Ultra option: "쇠스랑"-type item (+9 curse skill levels, +3 all spells; contributed by viewer Wraeclast; untested by creator himself — enables 몽상가의 손바닥/helmet freedom).
- **Mandatory utility wand in weapon-set II**: Withered Wand (말라버린 마법봉) with +3~5 chaos spell skills + cast speed + 부패의 고대 rune → hard-casts **Wither** (위축). "위축은 매우매우 중요" — boss/chaos-resist killer. Even staff users must keep one on swap. Boss opener uses X-swap: Blasphemy runs only on set I; on unstoppable-phase bosses the Blasphemy curses vanish, so you swap and hard-cast curses (v1 14:47).
- Google Doc has a full wand **crafting ladder** (1–3ex budget → mid → high-end/SSF): perfect essence for +3 spells, Abyssal Echo + Ancient Jawbone + omens at the Well of Souls for gain-mods, fracture trick ("un-revealed 훼손 can't be hit by fracturing → 1/3 odds on +spell level"), finishing with 초월의 합금 for cast speed. Also: **스루드의 완력's elemental mods do NOT convert to chaos** (tested; chaos-mod copies only).

**Ascendancy**: Time Snap + Time Freeze fixed. FINAL locks 4: + 위상 형상 (30% less DoT; hits are *suspended 4s*, not reduced — must top up HP immediately after a big hit or the delayed packet kills you; 16:07) + 필연 (boss burst). v1 offered 3 loadouts (안정: 위상+필연 / 편의: 위상+지금 또다시 / 공격: 필연+지금 또다시).

**Gear (FINAL snapshot `25f87`)**: The Vertex (Tribal Mask, +5 all curse skills — build's end goal; buy helmet WITHOUT res because of it), rare wand+focus, rare ES armour pieces, Breach Ring + **Kalandra's Touch**, **Mageblood** (Utility Belt) with 유산 flask combo (비스무트/금/수훈), **Uhtred's Chalice** mana flask (needs Rune-guard ≥1 anywhere), charms: Rite of Passage / Nascent Hope / The Fall of the Axe. Gloves high-end: 2-socket with Soul Core (curse/wither magnitude) + 페누무스 rune. Tree jewels: Split Personality (×with Templar-start relocation trick for aura effect → stronger Blasphemy-Temporal Chains), Prism of Belief, Eagle Essence, Chimeric Breath. Budget tiers defined by creator: 저자본 <10div (clears normal T15s), 일반 <200div, 하이엔드 200div+ (target content: 환영 200% = Delirium-style juiced).

**Utility kit**: Time Freeze (+Uhtred's Constellation = 3 charges, recharge via Time Snap; opening a map: 1× Time Freeze to proc 넘치는 성배 flask buff), Convalescence(요양) + Second Wind, Inevitable Agony (boss amp; cast Temporal Chains first → +25% duration on Freeze/Agony), Chaos Bolt + Chain/Multishot/Zarokh's Revolt (instant max wither stacks; Cospri's Will's Withering Presence is too slow — v1 12:31), Unearth + Gorge + Brutus' Brain (flask charges / anti-melee), Blasphemy-Temporal Chains + Ritualistic Curse/Slow Potency/Magnified Area.

**v1→FINAL diffs**: dropped Cospri's Will + Vorana-shackle self-curse armour package (100div v1 setting ran Withering Presence from Cospri's) → rare ES armour; staff axis introduced as the value option; curse-effect recipe 100→120%; ascendancy fixed to 4 nodes; Mobility support on Chaos Bolt → Zarokh's Revolt.
**Alternate ascendancies** (Google Doc): Lich/Abyssal Lich = both curses on Blasphemy, comfier + higher ES, better general survival, but Chronomancer survives hard content (에센스/아즈메리/환영) better; Blood Mage only as crit variant; Gemling → see 다린's channel.
**Death causes** (FAQ): over-juicing before spec is ready, unsolved mana, and side-strafing habits — creator teaches diagonal-backward roll + always Enfeeble.

## 4. Build 2 — Shield Wall "Kitava" (Warrior, Smith of Kitava)

**Design chain (high-end guide 5:31–15:52)** — each item solves the previous item's weakness:
1. **Defiance of Destiny** (운명의 저항): recovers 30→36%(q) of missing life *before* being hit (+10~12% max life). Weakness: recovery-based → HP oscillates 50–70%, one-shots still kill; occupies the amulet slot. Anoint 살상 본능 (Adorned/fire-avatar variant: 넘치는 힘).
2. **Rune Guard (룬수호, new 0.5 mechanic)** as the real anti-one-shot layer: HP can't drop below 1 while rune-guard pool (≈2k) absorbs. Source: **The Brass Dome** on the *Runeforged* Champion Cuirass base ("룬수호" 1,600–1,700+; buy by -1% max-all-res line + rune value). Brass Dome also removes crit bonus damage → covers armour's big-hit weakness.
3. **Damage via Surrounded + Low-Life**: **Constricting Command** (Runemastered Viper Cap) with "-4 enemies required to count as Surrounded" → surrounded with 1 enemy (melee-only value after the ranged nerf). Buy order: -4 mod > all attributes > max life; clean (uncorrupted) matters — later takes 큰 까마귀의 손길 shard (allocates: 1st 광택나는 철, 2nd 자로크의 선물). **Don't allocate surrounded tree nodes before owning the helmet** (low-budget guide 10:30). Low-life package requires **Atziri's Communion** (혈통잼-support, linked Trinity→later Eternal Rage). Until you own it, 극한 타격 support and 살상 본능 are dead — use replacements (11:04).
4. **Resist compression via ascendancy**: 석탄때기 (fire res grants 50% of it as cold/lightning) → gear only needs fire + chaos res. 0.5 "유동체" currency retypes any resist mod (맹렬한 유동체 → fire).
5. **Sacred Flame** (Shrine Sceptre, weapon-slot): grants Purity of Fire, +60% gain-as-extra-fire, allies regen/damage, and **"Enemies in your Presence Resist Elemental Damage based on their Lowest Resistance"** (verbatim from item XML) — the "sneaky OP" line. Sceptre socketed gems cost no Spirit; big Spirit roll (115 on his). Must buy uncorrupted (Perfect Jeweller 5-link later). Budget substitutes (low-budget guide): 심장에 인도하는 손바닥 sceptre → plain melee-mod mace → (pricier) 내룩 혐오받는 망치.
6. **Mageblood** + Ruby/Basalt/Granite-or-Jade(+수훈/은/금) — tested: Basalt+Jade/Granite ≻ Jade+Granite. "급사가 사라진다". Budget: plain res belt or Ryslatha's Coil.
7. Everything else: Iron-Reflexes-style keystone (회피→방어도) so buy armour/evasion hybrids; final armour ≈50k with "% armour applies to elemental damage" gloves/shield mods → "사실상 원소 면역". Gloves: +2 melee skills / attack speed / %armour-to-ele. Shield (= the actual weapon, wall damage scales off shield armour): armour > phys-taken-reduction > +max res > %armour-to-chaos > %armour-to-ele; warrior gear gets scarce+expensive late-season (buy early). Rings: res + flat attack damage; second ring = Kalandra's Touch. Flasks: **Olroth's Resolve** (on expiry grants Guard = current rune-guard, up to 1.5× max — with Mageblood instant-refill ≈2–3k guard) + Uhtred's Chalice. Charms: Rite of Passage / The Fall of the Axe / Ngamahu's Chosen (2.0 latest swaps Ngamahu → Valako's Roar). Jewels: +max fire res & +max Valour(경로); notable uniques: Voices, Megalomaniac, Heart of the Well, Prism of Belief, Blight Joy, Empyrean Bliss, Hypnotic Essence/Hope; 2.0 adds **Against the Darkness** (Time-Lost Diamond) + Split Personality.
8. Rune/soul-core plan (23:09): sceptre=Rabbit Idol, shield=Perfect Iron Rune, armour=보강하는 수호 line, helmet=raven shard, boots 1-socket=**방랑벽의 유산** (made by using 알두르의 유산 on 방랑벽 boots → immunity to all slows) or +테크로트의 응시 (low-life +10% MS) at 2-socket, gloves=Idol of Sirrius (or Hedigan's insight for +1 jewel). Alternatives: Idol of Eeshta / Tzamoto's Soul Core of Ferocity (+4 max Valour) / 과틸리치의 명제 (ancient: +35% of recently-lost life as armour, ~10div, "가성비 미침" — mutually exclusive with 테크로트의 응시). Soul Core of Tacati appears in his sceptre setup.

**Ascendancy (low-budget order, survival skeleton)**: ①석탄때기 → ②대장장이의 걸작 line — after taking it **only white (normal) body armour works** (mods are granted onto a white base; +200 armour per node applied to character): 탄탈룸의 합금 (+75% fire res cap line) → 녹아내린 상징 (25% phys taken as fire; FINAL note: mandatory — if you can't route it, drop 원시적 성장) → 키타바에 대한 헌신 (armour applies to chaos at 100%) → damaging-ailment immunity node → crit-bonus-taken -100% node → 키타바의 각인 (+15% life). Re-spec ascendancy toward the damage-oriented high-end layout only once Defiance + Brass Dome are equipped (12:32). High-end ascendancy exact nodes: shown as an image in the video only (not in captions; recoverable from tree node IDs if needed).

**Main loop (1.x high-end)**: place **Shield Wall** → destroying your own wall grants ≈150% damage amplification → break it instantly with **Resonating Shield** (no wind-up, usable mid-animation; cancels Shield Wall's recovery — input it the moment the wall-raise sound plays, 29:34). Supports: Shield Wall = Rapid Attacks II/Execute III/Close Combat II/격돌(or Defy II for 탐험 — guardian mobs sit at 1 HP where 격돌's HP-ratio condition backfires; Defy also beats mana-leech mods)/Vorana's Siege (optional, expensive). Resonating Shield = Rapid Attacks/Execute/Styrn's Mountain/Styrn's Ferocity/(Atalui's Bloodletting|Uruk's Smelting). Warcry = Infernal Cry (beats 보강하는 함성 at high-end due to flat-damage stacking) + Olroth's Conviction/Tireless/Raging Cry/Uhtred's Rite. War Banner when more damage needed. Alternatives rejected in 1.x (26:57): warcry-loop (button-light but needs endurance/valour upkeep unless Warbringer, slower cast), Shield Charge (slowest), **thorns/Repulsion one-button with Living Lightning — "not yet": unreliable procs, needs damage threshold, costs Spirit** → this exact idea becomes 2.0.

**Weapon-set bug (21:10, 1.x)**: prepare ①Sacred Flame w/ Rabbit Idol ②2-socket sceptre with Purity of Ice/Lightning + Rabbit+Greust idols ③cheap uncorrupted **Svalinn** (quality + block-cast Perfect Jeweller + Greust idol) → link Purity supports (Vitality II/Cool Headed/Warm Blooded/Strong Hearted/극한 타격) → stash-shuffle sequence → after one map transition you permanently keep: ignite/freeze/shock immunity, 4%/s life regen, **+140% attack damage while on Low Life**. Creator expects it to survive the league; build not crippled if fixed. (2.0 snapshots keep the Purity-of-Ice swap-set donor groups but no longer carry Svalinn — consistent with "plant once, remove the tool"; unverified.)

**Low-budget bridge (≈15div, guide 08-17)**: sacrifice **convenience** (of 편의성/재미/속도/생존/딜, only convenience is droppable). No Resonating Shield (can't one-shot the wall yet) → **warcry rotation**: 보강하는 함성 / Infernal Cry / 지진 함성 (3 separate cooldowns + 3 buffs/debuffs: flat dmg / extra fire / enemy res shred). Warcries bypass cooldown by consuming Endurance Charges; charges come from armour-break on the shield ("방호파계산" support). Infinite-loop cheat: add 분노한 함성(Enraged Warcry II)+포효 노드 — minimum wisdom(위세) floor 15 → refunds 15 Valour per cry ⇒ cooldown-free spam; bosses count as 20+10 → sustained boss uptime. Plus Blasphemy-**Enfeeble** as a defensive aura (−≈28% enemy total damage — armour efficiency rises against smaller hits; dropped at high-end). Buy order (uniques only): DMG: Sacred Flame(→substitutes) → Constricting Command → Atziri's Communion (100div early → 400div late; **buy early, never wait**) → Rite of Passage golden charm (gets cheaper later; until then run Armour Break III support). SURV: Defiance of Destiny → Brass Dome (+ascendancy re-spec moment) → Olroth's Resolve immediately after → 과틸리치의 명제 → Mageblood last. Jewels: +max res / warcry speed. Market timing: warrior uniques are bubble-priced days 1–3 of a league — farm currency first, buy after the bubble.

**2.0 (08-23~26) — what actually changed** (snapshot diff `26e5d` → `277af/278a0/278f6`):
- **Resonating Shield group deleted** → one-button: the wall now dies on its own. Mechanism (trailer desc): ① weak mobs hit the wall and die to its retaliation → **Detonate Dead auto-cast (Fire Spell on Hit trigger) destroys the wall** → amp explosion; ② with high **Thorns(반발)** the contact itself breaks the wall instantly → "faster one-button (bosses too)".
- **Blasphemy + Repulsion(20/20q) + Living Lightning II + Ritualistic Curse + Culling Strike II** — the previously-rejected thorns loop, made reliable by aura-fying Repulsion.
- Shield Wall links now **Ahn's Citadel + Kaom's Madness + Clash + Execute III + Atalui's Bloodletting**.
- **Trinity → Eternal Rage** (both carry Atziri's Communion); Cast-on-Block/Profane-Ritual and Magma Barrier groups dropped; **Overwhelming Presence + Precision** added; Shield Charge kept as movement with Armour Break III/Uruk's Smelting; Infernal Cry gains Enraged Warcry II.
- Gear churn: 08-23 tried **Living Bomb** instead of Detonate Dead, reverted by 08-25; Ngamahu's Chosen→Valako's Roar; +Against the Darkness & Split Personality jewels; 0.5 limb slots filled (Combat/Guarding Arm, Sturdy/Sprinters Leg).
- Claimed profile: 사망 0회, "원버튼(1.5버튼)", same core gear. PoB-cached stats of 2.0 sit slightly below 1.x high-end (armour 24.3k vs 28.9k, DPS cache 114k vs 165k) — the cache can't model the DD/thorns pop loop, so treat those numbers as floor, not comparison.

**Referenced external leveling source**: act guide by 별이슬골짜기 — "PoE2 0.5.0 워리어 방패의 벽 액트 가이드" (`dcSWTFyF9TQ`, 05-16, 1:06:11). Tangjeong's 3 deltas: take FIRE at the Act-2 Buried Shrine altar for Kitava; prefer Smith of Kitava over Warbringer; Act-4 Magma Twins kill-order picks the ruby-ring (kill lightning golem first).

## 5. Name-resolution table (ASR Korean → confirmed English via PoB XML)

절망=Despair · 임박한 멸망=Impending Doom · 멸망의 속삭임=curse-limit keystone · 피할 수 없는 고뇌=Inevitable Agony · 시간 동결/단절=Time Freeze/Time Snap · 요양=Convalescence · 카오스 화살=Chaos Bolt · 발굴=Unearth · 신성 모독=Blasphemy · 시간의 사슬=Temporal Chains · 쇠약화=Enfeeble · 아찌리의 매혹=Atziri's Allure · 아찌리의 성찬식=Atziri's Communion · 우트레드의 별자리/의뢰=Uhtred's Constellation/Rite · 알두르의 배신=Betrayal of Aldur (rune) · 말라버린 마법봉=Withered Wand · 최정점=The Vertex · 코스프리의 의지=Cospri's Will(v1) · 도이드리(SSF 대체)=Doedre's Undoing · 방패의 벽=Shield Wall · 공명하는 방패=Resonating Shield · 반발=Repulsion(+ThornsPlayer calc) · 살아있는 번개=Living Lightning II · 지옥불 함성=Infernal Cry · 분노한 함성=Enraged Warcry II · 방어 부수기=Armour Break III · 운명의 저항=Defiance of Destiny · 황동 요새=The Brass Dome (Runeforged base=룬수호) · 명령 독사 모자(포위 투구)=Constricting Command (Runemastered Viper Cap) · 신성한 불꽃=Sacred Flame (Shrine Sceptre) · 스발린=Svalinn · 올로스의 결의=Olroth's Resolve · 우트레드의 성배=Uhtred's Chalice · 마법사의 피=Mageblood · 칼란드라의 손길=Kalandra's Touch · 통과 의례=Rite of Passage · 도끼의 추락=The Fall of the Axe · 응가마후의 선택=Ngamahu's Chosen · 발라코의 포효=Valako's Roar · 어둠을 거슬러=Against the Darkness (Time-Lost Diamond) · idols/runes: Rabbit Idol, Idol of Greust, Idol of Sirrius, Idol of Eeshta, Perfect Iron Rune, Warding Rune, Soul Core of Tacati, Tzamoto's Soul Core of Ferocity.

## 6. Known gaps / uncertainties

- High-end **ascendancy node layout** shown only as an image (caption gap); recoverable from snapshot tree node IDs but needs a POE2 0.5 tree mapping (repo has 0.4 only).
- "쇠스랑" (+9 curse / +3 spells item) — exact item identity unverified (viewer-contributed, creator did not test).
- Svalinn's absence in 2.0 snapshots interpreted (not confirmed) as "bug planted, donor removed".
- ASR items not cross-confirmed: 하욕시의 뇌전 (SSF starter gem alt), 과틸리치의 명제/테크로트의 응시/방랑벽의 유산 (not present in parsed snapshots' item text; from captions only).
- Live-stream content (16 streams, ~50h) untranscribed — evolution rationale between snapshots is inferred from titles/descriptions/PoBs.
- 2.0 full guide video pending; numbers may shift when it lands.

## 7. Reproduction

```
# uploads (YT Data API key lives in D:/discord-admin/.env)
node scratchpad/yt_enum_tangjeong.mjs
# subtitles
python -m yt_dlp --skip-download --write-auto-subs --sub-langs "ko.*" --sub-format json3 -o "subs/%(id)s" <watch-url>
# PoB snapshots
curl https://poe.ninja/poe2/pob/raw/{id}  # base64(zlib) -> XML
```

Working artifacts (transcripts, 14 decoded XMLs, wand doc) live in this session's scratchpad; re-fetchable with the commands above.
