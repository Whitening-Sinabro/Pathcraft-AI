# SANAVIXX Cyclone Shockwave Slayer 3.29 HCSSF knowledge pipeline

Snapshot: 2026-08-08

## Scope

This pack models SANAVIXX's current 3.29 Cyclone Shockwave Slayer as staged
creator guidance plus an explicit HCSSF safety overlay. It does not silently
promote the creator's calculated level-96 state or giga-endgame crafts into
hardcore guarantees.

Canonical source order:

1. Current 3.29 PoB linked by `sanavixx.com` (`eiGimGWmzNXm`).
2. Current 3.29 creator video and Mobalytics explanation.
3. Current creator crafting page and slot-specific videos.
4. Official patch notes for game rules and drop-pool changes.
5. Older creator material only when cross-checked and labelled historical.

## Structured stages

The PoB contains twelve separate tree, skill and item stages:

1. Level 1-12 Spectral Throw.
2. Level 12-32 Static Strike.
3. Level 32 Cyclone and staff swap.
4. Level 58 Cyclone + Shockwave.
5. Level 68 Merciless Lab.
6. Level 77 Uber Lab.
7. Level 90 Cyclone of Tumult + Void Shockwave.
8. Level 96 rare Ezomyte Staff.
9. Level 100 high budget.
10. Giga speed.
11. Giga bossing.
12. Giga deep delve.

Never mix the passive tree, gem set or item set from different stages without
checking all lost requirements.

## HCSSF guardrails

The displayed level-96 PoB has 4,304 life, 18,515 physical max hit, 73%
lightning resistance, 16,249 armour, 65/47 block and no spell suppression. It
also reports about 1,904 life-leech gain rate versus about 155 regeneration.
These are configuration-dependent facts, not proof that the build is safe for
hardcore.

For HCSSF, progression is blocked when elemental resistances are uncapped,
recovery depends on a forbidden map modifier, the next weapon is unfinished,
or a scarce crafting resource would destroy the only safe equipped item.

## Twitch audit

The corpus includes all fourteen currently surviving PoE archives on
`twitch.tv/sanavixx`. The two August CWC Cyclone Assassin broadcasts are
catalogued but explicitly excluded from Shockwave Slayer progression.

The launch HCSSF character dies in VOD `2828010609`. Replay chat provides a
cluster of independent RIP reactions at 09:43:05-09:43:21; at 10:29:06 chat
asks whether HCSSF is over and only SSF remains, and the next archive is titled
`3.29 SSF Cyclone Shockwave Day 2`. This proves the mode transition, but chat
alone does not prove the exact damage source that killed the character.

Consequently, Day 2-7 footage is authoritative evidence for progression,
mana fixes and crafts, but it is not evidence that those choices completed
HCSSF deathlessly. HCSSF coaching applies an additional safety gate before
copying those SSF transitions.

## Crafting model

Crafts are stored as first-class documents with:

- stage and slot;
- SSF fit and risk;
- base and target affixes;
- required currencies or systems;
- safe stopping point;
- fallback or warning.

The current early-endgame staff recipe is an ilvl 83+ Ezomyte Staff
recombination project for increased physical damage, flat physical damage and
attack speed. Socket/link finishers are applied only after the affix result is
successful.

The published `Starter Body Armor` procedure is internally inconsistent: its
steps duplicate a minion sceptre/Essence of Fear recipe. The database preserves
the defensive target but marks the written procedure `do not follow`.

The elevated double-influence chest and Tailwind/Onslaught/Elusive boots are
aspirational. They are not fresh-HCSSF prerequisites.

Two current-version corrections override older instructions:

- Void Shockwave is an Uber Elder-family restricted drop, so ordinary
  Shockwave remains the SSF fallback through first pinnacle progression.
- Content Update 3.29 removed unveiling and crafting reduced mana cost on
  rings. The PoB/FAQ `-3 channeling cost` ring is stale; use the creator's
  July 30 mana-fix update instead.

## Korean regex profiles

PoE1 currently permits 250 characters in the map search field. Put the whole
expression, including the leading `!`, inside double quotes. `|` means OR,
`!` rejects every map matching any branch, `.*` spans arbitrary text, and
`^`/`$` anchor the start/end of a searchable line.

SANAVIXX regular maps, localized:

```text
"!회복 속도.*감폭|방어도.*감폭|흡수 대상|재생 불가|기절 면역"
```

SANAVIXX Nightmare maps, localized and expanded to avoid fragile English
fragments. The creator PoB still labels this block `T17 Maps`, but Tier 17 Maps
were changed into Nightmare Maps in 3.28; `T17` is not the current content name:

```text
"!회복 속도.*감폭|재생 불가|방어도.*감폭|막기 확률.*감소|결합 보스 대동|모든 저항 최대치|불안정한 촉수|질식의 구체|물리 피해 감소|흡수 대상|취약성 저주|총주교의 룬|피얼룩 톱날|유성의 대상|방어력.*감폭|기절 면역|폭발성 중심부"
```

Fresh-HCSSF conservative overlay, not a creator quote:

```text
"!회복 속도.*감폭|방어도.*감폭|흡수 대상|재생 불가|기절 면역|모든 저항 최대치|취약성 저주|치명타 피해 배율|추가 물리 피해|오라 스킬로 받는 효과|공격 명중 시 중독"
```

For map rolling, highlighted maps are the survivors of the blacklist. A
corrupted eight-mod map cannot be rerolled; use the same expression only to
select safe maps. Re-check one known bad map after every client-language or
patch change.

Korean vendor and gem searches are stored in the structured pack. Socket
letters remain `R/G/B`, but the tooltip label is localized from `Sockets:` to
`소켓:`.

## Commands

```powershell
python python/sanavixx_cyclone_knowledge.py index --db data/indexes/sanavixx_cyclone_3_29.db
python python/sanavixx_cyclone_knowledge.py search "HCSSF 지팡이 재조합"
python python/sanavixx_cyclone_knowledge.py diagnose --state '{"mode":"hcssf","elemental_res_capped":false}'
python python/knowledge_router.py --query "SANAVIXX Cyclone HCSSF 제작"
```

## User evidence required

For a death or low-damage diagnosis, collect the user's current PoB, level,
selected creator stage, weapon and links, life and resistances, recovery/leech,
content and map modifiers, and the death scene where available.
