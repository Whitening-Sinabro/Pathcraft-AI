# Emiracle CWS 3.29 knowledge pipeline

## Canonical inputs

- `data/guide_sources/poe1_cws_chieftain_emiracles_3_29_v2.json` is the versioned source-of-truth pack.
- It keeps creator claims, source locators, revision/supersession state, PoB variants, deterministic death rules, VOD metadata, and known gaps separate.
- The older `poe1_cws_chieftain_emiracles_3_29_v1.json` is preserved as an import snapshot; it is not overwritten.

## Build and query the local hybrid index

```powershell
python python/cws_knowledge.py index --db data/indexes/cws_emiracles_3_29.db
python python/cws_knowledge.py search "Emiracle 방송은 안 죽는데 나는 왜 끔살당하지?" --db data/indexes/cws_emiracles_3_29.db
```

The generated DB uses SQLite FTS5 plus 384-dimensional local character n-gram vectors. This dependency-free vectorizer is a multilingual baseline. `CWSKnowledgeBase.build_index()` accepts a stronger embedding callable without changing the DB or retrieval contract. Lexical and vector ranks are fused with reciprocal rank fusion; exact metadata filters are applied after retrieval.

The generated `.db` is disposable and gitignored. Rebuild it whenever the canonical JSON changes.

## Deterministic diagnosis

```powershell
python python/cws_knowledge.py diagnose --state '{"pob_url":"https://pobb.in/example","pantheon":"Soul of the Brine King","stun_avoidance_percent":0,"content":"ultimatum","variant":"first_bloodnotch","has_bloodnotch":true,"map_mods":[],"death_pattern":"multi_hit","damage_pattern":"hit"}'
```

Useful observations include `pob_url`, `content`, `variant`, `map_mods`, `death_pattern`, `damage_pattern`, `pantheon`, `stun_avoidance_percent`, `has_bloodnotch`, and `has_defiance_of_destiny`. A result is a ranked hypothesis with internal source references, not a fabricated PoE death log.

`knowledge_router.build_context_pack()` automatically attaches this CWS pack for CWS, Bloodnotch, Emiracle, and Korean sudden-death questions.

## Twitch VOD metadata

Offline export requires no credentials:

```powershell
python python/cws_twitch_collector.py --offline --output data/indexes/cws_twitch_vods.json
```

Live refresh uses the official Helix API:

```powershell
$env:TWITCH_CLIENT_ID="..."
$env:TWITCH_CLIENT_SECRET="..."
python python/cws_twitch_collector.py --output data/indexes/cws_twitch_vods.json
```

`TWITCH_ACCESS_TOKEN` may be supplied instead of the client secret. The pipeline stores only metadata and manual timestamp evidence; it does not mirror VOD media or transcripts. VOD scene/timestamp auditing remains a separate evidence-collection step because Twitch retention and API availability do not guarantee long-term access.

