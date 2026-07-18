# POE Deep Research Notes - 2026-07-16

## Scope

PathcraftAI coaching data was checked against official POE sources, PoE Wiki, PoE Vault, Mobalytics/PoE Atlas style guide sources, official forum posts, and selected Reddit community discussion.

This note separates source-backed rules from local calibration heuristics.

## Strongly Source-Backed Findings

1. PoE1 skill power is tightly bound to gear sockets, colors, and links.
   - Official POE overview: skills are gems socketed into equipment and up to five support gems can affect a skill.
   - PoE Wiki and PoE Vault both state support gems only work when linked to the active skill.
   - Product implication: PathcraftAI should show a slot-by-slot main skill link plan before deep optimization.

2. PoE2-to-PoE1 players commonly hit a skill/link mental-model mismatch.
   - Official forum beginner thread explicitly calls out that PoE2 sockets are easier to think about, while PoE1 requires linked sockets.
   - Product implication: the coach should translate "skill menu supports" into "same item, same linked group, correct colors."

3. Beginner survival checks should prioritize resistance cap, life/ES, defensive layers, and flask/ailment basics.
   - PoE Vault resistance guide uses 75% elemental resistance cap and overcap buffer.
   - Official/forum beginner advice repeatedly points to life, armour/evasion, and elemental resistance as early checkpoints.
   - Product implication: quick analysis should flag missing defenses in plain Korean, not just show raw EHP.

4. PoE is knowledge-gated by interlocking systems and third-party tools.
   - PoE Vault says systems are complex and interlocking, and recommends Path of Building.
   - Reddit and official forum threads show beginners are overwhelmed because many guides assume Harvest, Essence, Eldritch Altars, Atlas trees, PoB, and trading knowledge.
   - Product implication: PathcraftAI should not dump every mechanic. It should identify the current wall and return the next 3 actions.

5. League starters are a real classification, not just vibes.
   - PoE Vault defines league starters as builds that can reach endgame with little/no currency and no hard-to-get required items.
   - Product implication: build recommendation should detect required uniques, 6-link dependency, transition timing, and early availability before calling something beginner-safe.

## Atlas/Farming Findings

1. Atlas progression should be measured, not guessed.
   - Official 3.28 patch notes reworked Atlas structure, map items, Voidstones, Nightmare Maps, Unique Map Atlas points, and map modifier systems.
   - PoE Atlas and Mobalytics-style progression guides focus on completion, map sustain, Kirac/connected map drops, Voidstones, and avoiding over-investment while weak.
   - Product implication: ask for Atlas progress, comfortable highest tier, death rate, average clear time, Voidstones, and goal.

2. "Atlas passive 100+" and "T16 under 2 minutes" are not official phase gates.
   - They are useful local calibration signals for speed farming, but no source found treats them as universal requirements.
   - Product implication: label them as local benchmarks only. If data is missing, return a conservative estimate and one requested measurement.

3. Farming strategy needs patch refresh.
   - Official 3.29 launch is July 24, 2026 PDT, with GGG Live on July 16, 2026 PDT.
   - League mechanic rewards, scarabs, Atlas nodes, map device behavior, and economy can change per patch.
   - Product implication: keep stable readiness logic, but refresh mechanic rankings after patch notes and week-one economy data.

## Current Product Changes Applied

- `data/new_player_friction_knowledge.json`
  - Added source references.
  - Reworded Atlas readiness from hard gates to measured signals.
  - Explicitly marks Atlas 100/T16 2-minute as local calibration only.

- `data/atlas_farming_knowledge.json`
  - Added official 3.28 and 3.29 source references.
  - Added patch refresh policy.
  - Keeps phase gates as readiness signals, not deterministic proof.

## Sources Checked

- Official POE overview: https://www.pathofexile.com/game
- Official 3.28 patch notes: https://www.pathofexile.com/forum/view-thread/3913392
- Official 3.29 timeline: https://www.pathofexile.com/forum/view-thread/3955013
- Official current news / Twitch Drops: https://www.pathofexile.com/forum/view-thread/3985053
- Official item filter docs: https://www.pathofexile.com/item-filter/about
- PoE Wiki item sockets: https://www.poewiki.net/wiki/Item_socket
- PoE Wiki Atlas passive tree: https://www.poewiki.net/wiki/Atlas_passive_skill_tree
- PoE Vault beginner guide: https://www.poe-vault.com/guides/path-of-exile-beginner-guide-welcome-to-wraeclast-fresh-exiles-start-here
- PoE Vault skill gems: https://www.poe-vault.com/guides/path-of-exile-beginner-guide-skill-gems
- PoE Vault resistances: https://www.poe-vault.com/guides/path-of-exile-beginner-guide-learning-to-loot-learning-resistances
- PoE Vault passive tree: https://www.poe-vault.com/guides/path-of-exile-beginner-guide-learning-the-passive-tree
- PoE Vault league starters: https://www.poe-vault.com/guides/tag/league-starter-builds-for-path-of-exile
- PoE Vault Atlas strategies: https://www.poe-vault.com/guides/atlas-passive-skill-tree-strategies
- PoE Atlas 3.28 overview: https://poe-atlas.com/
- Mobalytics Atlas completion starter tree: https://mobalytics.gg/poe/profile/lolcohol/guides/atlas-tree-fast-completion-stater-tree
- Official forum beginner POE2-to-POE1 socket discussion: https://www.pathofexile.com/forum/view-thread/3736272
- Official forum overwhelmed after campaign: https://www.pathofexile.com/forum/view-thread/3469585
- Official forum maps for dummies: https://www.pathofexile.com/forum/view-thread/3039318
- Reddit beginner guide discussion: https://www.reddit.com/r/pathofexile/comments/1bhvfra/path_of_exile_beginners_guide_new_player_tips/
