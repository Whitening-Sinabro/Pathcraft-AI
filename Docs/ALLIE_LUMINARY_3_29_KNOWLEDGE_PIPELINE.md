# Allie Bob & Friends Luminary 3.29 knowledge pipeline

Snapshot: 2026-08-07 (Asia/Bangkok)

## Canonical scope

This pack is locked to Allie's PoE 1 patch 3.29 **Bob & Friends Luminary Solo Aurabot**. It must not silently mix CaptainLance9, Nerotox, old 3.26 mercenary builds, or Reliquarian shells into Allie's current prescription.

Authority order:

1. GGG patch notes and mechanics clarifications for game rules.
2. Allie's current Mobalytics guide, embedded PoB/Notes, variants, and changelog for build choices.
3. Newer Allie corrections/PSAs, then dated progression videos.
4. Timestamped Twitch observations.
5. Specialist and community evidence, clearly labelled as secondary.
6. User observations, retained as observations rather than universal rules.

The current creator authority is the Mobalytics page updated 2026-08-07 (v2.4 lineage). Old Stormblast Mine, Flesh and Stone, and Spectre Empower/Pain Artist states are stored only so stale setups can be diagnosed.

## Entity model

This build cannot be represented by the player PoB alone:

- `player`: current guide variant, life/ES phase, auras, links, flasks, map defenses.
- `mercenary`: class, level, inherent active skills/supports, equipment, accuracy, resistance, leech, AI behavior.
- `bob`: Animate Guardian equipment, Hallowed Monarch link state, survivability gate.
- `spectres`: identities, Raise Spectre level breakpoint, weapon-swap loss risk.

All diagnosis and future UI forms should keep these entities separate.

## Files

- `data/guide_sources/poe1_luminary_allie_bob_friends_3_29_v1.json`: versioned source/claim/variant/rule/media pack.
- `python/allie_luminary_knowledge.py`: validation, local FTS5 + hashing-vector retrieval, deterministic diagnosis CLI.
- `python/cws_twitch_collector.py`: shared official Helix metadata collector; supports this pack with `--channel Allliee_` or automatic inference.
- `python/knowledge_router.py`: routes explicit Allie/Bob & Friends questions into this pack.
- `python/tests/test_allie_luminary_knowledge.py`: integrity, retrieval, diagnosis, and vector-index tests.
- `data/indexes/allie_luminary_3_29.db`: disposable generated local index; the JSON remains canonical.

## Commands

```powershell
python python/allie_luminary_knowledge.py index --db data/indexes/allie_luminary_3_29.db
python python/allie_luminary_knowledge.py search "앨리 용병이 T4 레어를 못 잡아" --db data/indexes/allie_luminary_3_29.db
python python/allie_luminary_knowledge.py diagnose --state '{"merc_source":"campaign","merc_effective_supports":2,"flame_link_active":false}'
python python/cws_twitch_collector.py --pack data/guide_sources/poe1_luminary_allie_bob_friends_3_29_v1.json --output data/indexes/allie_twitch_vods.json --offline
```

Live Twitch refresh needs `TWITCH_CLIENT_ID` plus either `TWITCH_ACCESS_TOKEN` or `TWITCH_CLIENT_SECRET`. Never store or print those values in the knowledge pack.

## Current media inventory

- 10 edited YouTube videos: eight build/update/correction videos and two mapping/economy videos.
- 11 Twitch archives from 2026-07-24 through 2026-08-06, about 79 hours total, stored as metadata with timestamp audits pending.

YouTube automatic captions are the first transcript target. Twitch should be audited by revision event (merc selection, Hallowed Monarch, Uber testing, ES conversion), not transcribed blindly in full. Store derived atomic claims and timestamps, not mirrored transcript bodies or VOD media.

## Known gates

- Mobalytics exposes the canonical PoB through a dynamic Copy Code field; a stable pobb.in snapshot is not yet available.
- The user-supplied `activeVariantId=598ccb91-...` remains unmapped; never guess its visible variant name.
- Exact campaign mercenary class/skill/support spawn weights are unknown.
- Endgame Part 3 was still being extended in the v2.4 changelog, so future guide updates require a new revision rather than overwriting history.
