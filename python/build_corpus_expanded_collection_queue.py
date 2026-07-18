# -*- coding: utf-8 -*-
"""Build an expanded source-hunt queue for the POE1 build corpus."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "data" / "build_corpus_expanded_collection_queue_v1.json"


SOURCE_REGISTRY: dict[str, dict[str, str]] = {
    "reddit_322_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/15qfyqy/322_trial_of_the_ancestors_league_start_build/",
        "label": "3.22 Trial of the Ancestors League Start Build Index",
    },
    "reddit_322_streamer": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/pathofexile/comments/15ulgjh/compiled_list_of_streamer_starter_builds_for/",
        "label": "Compiled streamer starter builds for 3.22 Ancestor",
    },
    "poe_vault_322": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/news/2023/08/18/path-of-exile-trial-of-the-ancestors-league-starters",
        "label": "PoE Vault 3.22 Trial of the Ancestors starter roundup",
    },
    "youtube_322_top10": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=kLJ6Yo3XdLg",
        "label": "3.22 Trial of the Ancestors top league starter video roundup",
    },
    "reddit_323_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/18bqsnb/323_affliction_league_start_build_index/",
        "label": "3.23 Affliction League Start Build Index",
    },
    "reddit_323_list6": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/18bptfx/my_list_of_6_good_league_starter_builds_for_323/",
        "label": "Community 3.23 list of starter builds with PoBs in comments",
    },
    "poe_vault_323": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/guides/affliction-league-league-starters",
        "label": "PoE Vault 3.23 Affliction league starters",
    },
    "youtube_323_best_specific": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=cd_jGdcBsYM",
        "label": "PoE 3.23 best league starter builds for specific content",
    },
    "youtube_323_tripolar_playlist": {
        "family": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLba5C_stYQXUpd-6_do4JrSIJASsyKQv_",
        "label": "TripolarBear 3.23 Affliction video playlist",
    },
    "reddit_324_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1bmbqp6/324_necropolis_league_start_build_index/",
        "label": "3.24 Necropolis League Start Build Index",
    },
    "poe_vault_324": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/guides/necropolis-league-league-starters",
        "label": "PoE Vault 3.24 Necropolis league starters",
    },
    "youtube_324_top5": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=4JLcckNeu6I",
        "label": "PoE 3.24 top league start build guide roundup",
    },
    "youtube_324_zizaran_dd": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=FdzzesMof4Y",
        "label": "Zizaran and imexile 3.24 Detonate Dead league starter",
    },
    "reddit_325_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1eaudsu/325_settlers_of_kalguur_league_start_build_index/",
        "label": "3.25 Settlers of Kalguur League Start Build Index",
    },
    "poe_vault_325": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/guides/settlers-of-kalguur-league-starters",
        "label": "PoE Vault 3.25 Settlers of Kalguur league starters",
    },
    "odealo_325": {
        "family": "build_site",
        "url": "https://odealo.com/articles/best-starter-builds-for-settlers-of-kalguur-league-and-patch-3-25",
        "label": "Odealo 3.25 Settlers of Kalguur starter builds",
    },
    "youtube_325_zizaran_playlist": {
        "family": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLbpExg9_Xax3tVeJIhkyWDx_ZRl9Nb_OL",
        "label": "Zizaran 3.25 Settlers league starter guide playlist",
    },
    "youtube_325_top_builds": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=s7DUBSSncWU",
        "label": "PoE 3.25 top builds tier list and league start plans",
    },
    "reddit_326_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1l5xyzt/326_secrets_of_the_atlas_league_start_build_index/",
        "label": "3.26 Secrets of the Atlas League Start Build Index",
    },
    "poe_vault_326": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/guides/secrets-of-the-atlas-league-starters",
        "label": "PoE Vault 3.26 Secrets of the Atlas league starters",
    },
    "youtube_326_top7": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=gAr8cigPlCA",
        "label": "Top 7 3.26 Secrets of the Atlas league starters",
    },
    "youtube_326_zizaran_playlist": {
        "family": "youtube",
        "url": "https://www.youtube.com/playlist?list=PLbpExg9_Xax3l4dqw4-OF17wEgfiJ6t6B",
        "label": "Zizaran 3.26 Secrets league starter guide playlist",
    },
    "reddit_327_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1oit0of/327_keepers_of_the_flame_league_start_build_index/",
        "label": "3.27 Keepers of the Flame League Start Build Index",
    },
    "poe_vault_327": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/guides/keepers-of-the-flame-league-starters",
        "label": "PoE Vault 3.27 Keepers of the Flame league starters",
    },
    "odealo_327": {
        "family": "build_site",
        "url": "https://odealo.com/articles/best-starter-builds-for-keepers-of-the-flame-league-and-patch-3-27",
        "label": "Odealo 3.27 Keepers starter builds",
    },
    "icy_veins_327": {
        "family": "build_site",
        "url": "https://www.icy-veins.com/forums/topic/85213-best-guides-for-path-of-exile-league-keepers-of-the-flame-327/",
        "label": "Icy Veins 3.27 Keepers guide roundup",
    },
    "youtube_327_top6": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=_ASnDh4HNYQ",
        "label": "Top 6 3.27 Keepers league starter video roundup",
    },
    "youtube_327_mobalytics": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=xxjtrRisPoY",
        "label": "Mobalytics 3.27 league starter video",
    },
    "reddit_328_index": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1rk0s9m/328_mirage_league_start_build_index/",
        "label": "3.28 Mirage League Start Build Index",
    },
    "poe_vault_328": {
        "family": "build_site",
        "url": "https://www.poe-vault.com/guides/mirage-league-starters",
        "label": "PoE Vault 3.28 Mirage league starters",
    },
    "odealo_328": {
        "family": "build_site",
        "url": "https://odealo.com/articles/best-starter-builds-for-mirage-league-and-patch-3-28",
        "label": "Odealo 3.28 Mirage starter builds",
    },
    "youtube_328_top10": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=jLxxjmg6xy0",
        "label": "PoE 3.28 ten league starter builds video",
    },
    "youtube_328_flowchart": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=54Ih9qAHeC8",
        "label": "PoE 3.28 league starter build flow chart video",
    },
    "youtube_328_fearlessdumb0_exsanguinate_reap_miner": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=ZEvuQ5krLwQ",
        "label": "FearlessDumb0 Exsanguinate Reap Miner league start build guide for 3.28",
    },
    "youtube_328_poison_carrion_golem_necromancer": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=WMHepc5VN4M",
        "label": "PoE 3.28 Poison Carrion Golem Necromancer league start guide",
    },
    "youtube_tori_sensei_poison_carrion_golem": {
        "family": "youtube",
        "url": "https://www.youtube.com/@torisense",
        "label": "Tori-sensei current-season Poison Carrion Golem source hunt",
    },
    "youtube_326_tori_poison_carrion_golem": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=WO2bjIZMrtQ",
        "label": "Tori-sensei 3.26 Poison Carrion Golem reference with public PoB",
    },
    "youtube_328_mastert_ignite_slamentalist": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=0dJFLujq-tc",
        "label": "MasterT 3.28 Ignite Slamentalist Elementalist build guide",
    },
    "mobalytics_328_mastert_righteous_cold_autobomber": {
        "family": "build_site",
        "url": "https://mobalytics.gg/poe/builds/righteous-cold-dot-autobomber",
        "label": "MasterT 3.28 Righteous Cold Dot Autobomber Mobalytics guide",
    },
    "youtube_328_mastert_righteous_cold_autobomber": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=gJF4EKLpIag",
        "label": "MasterT 3.28 Righteous Cold Dot Autobomber transition guide video",
    },
    "official_329_reliquarian": {
        "family": "official",
        "url": "https://www.pathofexile.com/forum/view-thread/3984866",
        "label": "Official 3.29 Reliquarian Ascendancy Changes announcement",
    },
    "reddit_329_reliquarian": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/pathofexile/comments/1uwtvuy/329_reliquarian_ascendancy_changes/",
        "label": "3.29 Reliquarian Ascendancy Changes discussion",
    },
    "reddit_329_specialists": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1upopd1/the_specialists_index_best_329_league_starter_for/",
        "label": "3.29 specialist league starter discussion by mechanic",
    },
    "reddit_329_text_nodes": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1uwuqtn/text_based_list_of_329_reliquarian_ascendancy/",
        "label": "Text-based 3.29 Reliquarian ascendancy node community transcription",
    },
    "reddit_329_standout_reliquarian": {
        "family": "reddit",
        "url": "https://www.reddit.com/r/PathOfExileBuilds/comments/1sv8gt3/any_standout_reliquarian_build_this_league/",
        "label": "Community discussion of standout Reliquarian builds",
    },
    "mobalytics_329_reliquarian": {
        "family": "build_site",
        "url": "https://mobalytics.gg/poe/reliquarian-starter-builds",
        "label": "Mobalytics Reliquarian starter builds hub",
    },
    "youtube_329_goratha_reliquarian": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=kHbzCW57Unw",
        "label": "Goratha 3.29 Reliquarian build shells",
    },
    "youtube_329_allflame": {
        "family": "youtube",
        "url": "https://www.youtube.com/watch?v=CEBlViZ3p0U",
        "label": "3.29 Curse of the Allflame starter planning video",
    },
    "pob_archives_global": {
        "family": "community_archive",
        "url": "https://pobarchives.com/",
        "label": "PoB Archives daily updated builds from YouTube and Reddit",
    },
}


PATCH_SOURCE_BACKFILL: dict[str, list[str]] = {
    "3.22": ["pob_archives_global", "poe_vault_322", "youtube_322_top10"],
    "3.23": [
        "pob_archives_global",
        "reddit_323_list6",
        "poe_vault_323",
        "youtube_323_best_specific",
        "youtube_323_tripolar_playlist",
    ],
    "3.24": [
        "pob_archives_global",
        "poe_vault_324",
        "youtube_324_top5",
        "youtube_324_zizaran_dd",
    ],
    "3.25": [
        "pob_archives_global",
        "poe_vault_325",
        "odealo_325",
        "youtube_325_zizaran_playlist",
        "youtube_325_top_builds",
    ],
    "3.26": [
        "pob_archives_global",
        "poe_vault_326",
        "youtube_326_top7",
        "youtube_326_zizaran_playlist",
    ],
    "3.27": [
        "pob_archives_global",
        "poe_vault_327",
        "odealo_327",
        "icy_veins_327",
        "youtube_327_top6",
        "youtube_327_mobalytics",
    ],
    "3.28": [
        "pob_archives_global",
        "poe_vault_328",
        "odealo_328",
        "youtube_328_top10",
        "youtube_328_flowchart",
    ],
    "3.29": [
        "pob_archives_global",
        "mobalytics_329_reliquarian",
        "reddit_329_text_nodes",
        "reddit_329_standout_reliquarian",
        "youtube_329_allflame",
    ],
}


def cand(
    patch: str,
    slug: str,
    name: str,
    lane_id: str,
    skill: str,
    class_name: str,
    ascendancy: str,
    role: str,
    source_refs: list[str],
    status: str = "source_hunted",
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "candidate_id": f"{patch}_{slug}",
        "patch": patch,
        "display_name": name,
        "lane_id": lane_id,
        "main_skill": skill,
        "class_name": class_name,
        "ascendancy": ascendancy,
        "collection_role": role,
        "source_status": status,
        "source_refs": source_refs,
        "required_next_steps": [
            "find_or_archive_pob",
            "normalize_two_state_snapshots",
            "run_build_instance_readiness",
            "record_beginner_failure_lens",
        ],
        "notes": notes,
    }


PATCH_CANDIDATES: dict[str, list[dict[str, Any]]] = {
    "3.22": [
        cand("3.22", "boneshatter_slayer", "Boneshatter Slayer", "melee_strike_slam", "Boneshatter", "Duelist", "Slayer", "stable_shell", ["reddit_322_index"]),
        cand("3.22", "boneshatter_juggernaut", "Boneshatter Juggernaut", "melee_strike_slam", "Boneshatter", "Marauder", "Juggernaut", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "cold_dot_elementalist", "Cold DoT Elementalist", "dot_ailment_dot", "Cold DoT", "Witch", "Elementalist", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "cold_dot_trickster", "Cold DoT Trickster", "dot_ailment_dot", "Cold DoT", "Shadow", "Trickster", "stable_shell", ["reddit_322_index"]),
        cand("3.22", "explosive_arrow_champion", "Explosive Arrow Ballista Champion", "trap_mine_totem", "Explosive Arrow", "Duelist", "Champion", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "hexblast_mines_saboteur", "Hexblast Mines Saboteur", "trap_mine_totem", "Hexblast Mines", "Shadow", "Saboteur", "stable_shell", ["reddit_322_index"]),
        cand("3.22", "lightning_arrow_deadeye", "Lightning Arrow Deadeye", "bow_projectile_attack_mapper", "Lightning Arrow", "Ranger", "Deadeye", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "ice_shot_deadeye", "Ice Shot Deadeye", "bow_projectile_attack_mapper", "Ice Shot", "Ranger", "Deadeye", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "spark_inquisitor", "Spark Inquisitor", "spell_hit_brand_selfcast", "Spark", "Templar", "Inquisitor", "stable_shell", ["reddit_322_index"]),
        cand("3.22", "detonate_dead_elementalist", "Detonate Dead Elementalist", "spell_hit_brand_selfcast", "Detonate Dead", "Witch", "Elementalist", "stable_shell", ["reddit_322_index"]),
        cand("3.22", "poison_srs_necromancer", "Poison SRS Necromancer", "minion_trigger_autobomber_special", "Summon Raging Spirits", "Witch", "Necromancer", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "minion_army_necromancer", "Minion Army Necromancer", "minion_trigger_autobomber_special", "Mixed Minions", "Witch", "Necromancer", "stable_shell", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "righteous_fire_inquisitor", "Righteous Fire Inquisitor", "dot_ailment_dot", "Righteous Fire", "Templar", "Inquisitor", "transition_case", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "righteous_fire_juggernaut", "Righteous Fire Juggernaut", "dot_ailment_dot", "Righteous Fire", "Marauder", "Juggernaut", "transition_case", ["reddit_322_index"]),
        cand("3.22", "toxic_rain_pathfinder", "Toxic Rain Pathfinder", "dot_ailment_dot", "Toxic Rain", "Ranger", "Pathfinder", "transition_case", ["reddit_322_index", "reddit_322_streamer"]),
        cand("3.22", "toxic_rain_champion", "Toxic Rain Champion", "dot_ailment_dot", "Toxic Rain", "Duelist", "Champion", "transition_case", ["reddit_322_index"]),
        cand("3.22", "impending_doom_pathfinder", "Impending Doom Pathfinder", "dot_ailment_dot", "Impending Doom", "Ranger", "Pathfinder", "failure_edge_case", ["reddit_322_index", "reddit_322_streamer"], notes="Index flags possible bug or nerf; useful as a negative/edge check."),
        cand("3.22", "holy_relic_ascendant", "Holy Relic Ascendant", "minion_trigger_autobomber_special", "Holy Relic", "Scion", "Ascendant", "failure_edge_case", ["reddit_322_index"]),
        cand("3.22", "pyroclast_mines_saboteur", "Pyroclast Mines Saboteur", "trap_mine_totem", "Pyroclast Mine", "Shadow", "Saboteur", "failure_edge_case", ["reddit_322_index"]),
        cand("3.22", "poison_blade_vortex_pathfinder", "Poison Blade Vortex Pathfinder", "dot_ailment_dot", "Blade Vortex", "Ranger", "Pathfinder", "failure_edge_case", ["reddit_322_index"]),
    ],
    "3.23": [
        cand("3.23", "boneshatter_slayer", "Boneshatter Slayer", "melee_strike_slam", "Boneshatter", "Duelist", "Slayer", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "boneshatter_juggernaut", "Boneshatter Juggernaut", "melee_strike_slam", "Boneshatter", "Marauder", "Juggernaut", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "detonate_dead_elementalist", "Detonate Dead Elementalist", "spell_hit_brand_selfcast", "Detonate Dead", "Witch", "Elementalist", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "storm_brand_inquisitor", "Storm Brand Inquisitor", "spell_hit_brand_selfcast", "Storm Brand", "Templar", "Inquisitor", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "explosive_arrow_elementalist", "Explosive Arrow Ballista Elementalist", "trap_mine_totem", "Explosive Arrow", "Witch", "Elementalist", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "explosive_trap_trickster", "Explosive Trap Trickster", "trap_mine_totem", "Explosive Trap", "Shadow", "Trickster", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "lightning_arrow_deadeye", "Lightning Arrow Deadeye", "bow_projectile_attack_mapper", "Lightning Arrow", "Ranger", "Deadeye", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "ice_shot_deadeye", "Ice Shot Deadeye", "bow_projectile_attack_mapper", "Ice Shot", "Ranger", "Deadeye", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "toxic_rain_pathfinder", "Toxic Rain Pathfinder", "dot_ailment_dot", "Toxic Rain", "Ranger", "Pathfinder", "stable_shell", ["reddit_323_index", "poe_vault_323"]),
        cand("3.23", "caustic_arrow_poison_ballista", "Caustic Arrow Poison Ballista Pathfinder", "dot_ailment_dot", "Caustic Arrow", "Ranger", "Pathfinder", "stable_shell", ["reddit_323_index"]),
        cand("3.23", "guardian_srs", "Guardian SRS", "minion_trigger_autobomber_special", "Summon Raging Spirits", "Templar", "Guardian", "stable_shell", ["reddit_323_index", "poe_vault_323"]),
        cand("3.23", "poison_srs_necromancer", "Poison SRS Necromancer", "minion_trigger_autobomber_special", "Summon Raging Spirits", "Witch", "Necromancer", "stable_shell", ["reddit_323_index", "poe_vault_323"]),
        cand("3.23", "toxic_rain_champion", "Toxic Rain Champion", "dot_ailment_dot", "Toxic Rain", "Duelist", "Champion", "transition_case", ["reddit_323_index"]),
        cand("3.23", "corrupting_fever_champion", "Corrupting Fever Champion", "dot_ailment_dot", "Corrupting Fever", "Duelist", "Champion", "transition_case", ["reddit_323_index"]),
        cand("3.23", "bladefall_bladeblast_assassin", "Bladefall Blade Blast Assassin", "spell_hit_brand_selfcast", "Bladefall / Blade Blast", "Shadow", "Assassin", "transition_case", ["reddit_323_index"]),
        cand("3.23", "maw_of_mischief_elementalist", "Maw of Mischief Ignite Elementalist", "dot_ailment_dot", "Maw of Mischief", "Witch", "Elementalist", "transition_case", ["reddit_323_index"]),
        cand("3.23", "hexblast_mines_occultist", "Hexblast Mines Occultist", "trap_mine_totem", "Hexblast Mines", "Witch", "Occultist", "failure_edge_case", ["reddit_323_index"]),
        cand("3.23", "energy_blade_coc_inquisitor", "Energy Blade CoC Inquisitor", "minion_trigger_autobomber_special", "Cast on Critical Strike", "Templar", "Inquisitor", "failure_edge_case", ["reddit_323_index"]),
        cand("3.23", "reap_hierophant", "Reap Hierophant", "spell_hit_brand_selfcast", "Reap", "Templar", "Hierophant", "failure_edge_case", ["reddit_323_index"], notes="Community comments call out high unique pressure; good for cost-gate checks."),
        cand("3.23", "falling_zombies_guardian", "Falling Zombies Guardian", "minion_trigger_autobomber_special", "Raise Zombie", "Templar", "Guardian", "failure_edge_case", ["reddit_323_index"]),
    ],
    "3.24": [
        cand("3.24", "detonate_dead_elementalist", "Detonate Dead Elementalist", "spell_hit_brand_selfcast", "Detonate Dead", "Witch", "Elementalist", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "detonate_dead_necromancer", "Detonate Dead Necromancer", "spell_hit_brand_selfcast", "Detonate Dead", "Witch", "Necromancer", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "archmage_ice_nova_hierophant", "Archmage Ice Nova Hierophant", "spell_hit_brand_selfcast", "Ice Nova of Frostbolts", "Templar", "Hierophant", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "lightning_arrow_deadeye", "Lightning Arrow Deadeye", "bow_projectile_attack_mapper", "Lightning Arrow", "Ranger", "Deadeye", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "elemental_hit_deadeye", "Elemental Hit Deadeye", "bow_projectile_attack_mapper", "Elemental Hit", "Ranger", "Deadeye", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "lightning_strike_champion", "Lightning Strike Champion", "melee_strike_slam", "Lightning Strike", "Duelist", "Champion", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "righteous_fire_chieftain", "Righteous Fire Chieftain", "dot_ailment_dot", "Righteous Fire", "Marauder", "Chieftain", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "explosive_arrow_champion", "Explosive Arrow Champion", "trap_mine_totem", "Explosive Arrow", "Duelist", "Champion", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "exsanguinate_mines_trickster", "Exsanguinate Mines Trickster", "trap_mine_totem", "Exsanguinate Mines", "Shadow", "Trickster", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "zoomancer_necromancer", "Zoomancer Necromancer", "minion_trigger_autobomber_special", "Mixed Minions", "Witch", "Necromancer", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "bama_necromancer", "Blink Arrow Mirror Arrow Necromancer", "minion_trigger_autobomber_special", "Blink Arrow / Mirror Arrow", "Witch", "Necromancer", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "penance_brand_inquisitor", "Penance Brand Inquisitor", "spell_hit_brand_selfcast", "Penance Brand", "Templar", "Inquisitor", "stable_shell", ["reddit_324_index"]),
        cand("3.24", "archmage_ball_lightning_hierophant", "Archmage Ball Lightning Hierophant", "spell_hit_brand_selfcast", "Ball Lightning", "Templar", "Hierophant", "transition_case", ["reddit_324_index"]),
        cand("3.24", "coc_detonate_dead_inquisitor", "CoC Detonate Dead Inquisitor", "minion_trigger_autobomber_special", "Cast on Critical Strike Detonate Dead", "Templar", "Inquisitor", "transition_case", ["reddit_324_index"], notes="Index keeps it out of beginner section; useful for trigger-transition checks."),
        cand("3.24", "spark_hierophant", "Spark Hierophant", "spell_hit_brand_selfcast", "Spark", "Templar", "Hierophant", "transition_case", ["reddit_324_index"]),
        cand("3.24", "holy_relic_necromancer", "Holy Relic Necromancer", "minion_trigger_autobomber_special", "Summon Holy Relic", "Witch", "Necromancer", "transition_case", ["reddit_324_index"]),
        cand("3.24", "energy_blade_inquisitor", "Energy Blade Inquisitor", "spell_hit_brand_selfcast", "Energy Blade", "Templar", "Inquisitor", "failure_edge_case", ["reddit_324_index"]),
        cand("3.24", "maw_ignite_elementalist", "Maw of Mischief Ignite Elementalist", "dot_ailment_dot", "Maw of Mischief", "Witch", "Elementalist", "failure_edge_case", ["reddit_324_index"]),
        cand("3.24", "rage_cleave_berserker", "Rage Cleave Berserker", "melee_strike_slam", "Cleave", "Marauder", "Berserker", "failure_edge_case", ["reddit_324_index"]),
        cand("3.24", "reap_scion", "Reap Scion", "spell_hit_brand_selfcast", "Reap", "Scion", "Ascendant", "failure_edge_case", ["reddit_324_index"]),
    ],
    "3.25": [
        cand("3.25", "lightning_strike_slayer", "Lightning Strike Slayer", "melee_strike_slam", "Lightning Strike", "Duelist", "Slayer", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "ground_slam_slayer", "Ground Slam Slayer", "melee_strike_slam", "Ground Slam", "Duelist", "Slayer", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "archmage_ice_nova_hierophant", "Archmage Ice Nova Hierophant", "spell_hit_brand_selfcast", "Ice Nova of Frostbolts", "Templar", "Hierophant", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "archmage_spark_hierophant", "Archmage Spark Hierophant", "spell_hit_brand_selfcast", "Spark", "Templar", "Hierophant", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "explosive_arrow_elementalist", "Explosive Arrow Elementalist", "trap_mine_totem", "Explosive Arrow", "Witch", "Elementalist", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "hexblast_mines_trickster", "Hexblast Mines Trickster", "trap_mine_totem", "Hexblast Mines", "Shadow", "Trickster", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "elemental_hit_deadeye", "Elemental Hit of the Spectrum Deadeye", "bow_projectile_attack_mapper", "Elemental Hit", "Ranger", "Deadeye", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "power_siphon_locus_mine_trickster", "Power Siphon Locus Mine Trickster", "bow_projectile_attack_mapper", "Power Siphon", "Shadow", "Trickster", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "righteous_fire_chieftain", "Righteous Fire Chieftain", "dot_ailment_dot", "Righteous Fire", "Marauder", "Chieftain", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "poisonous_concoction_pathfinder", "Poisonous Concoction Pathfinder", "dot_ailment_dot", "Poisonous Concoction", "Ranger", "Pathfinder", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "holy_relic_necromancer", "Holy Relic Necromancer", "minion_trigger_autobomber_special", "Summon Holy Relic", "Witch", "Necromancer", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "zoomancer_necromancer", "Zoomancer Necromancer", "minion_trigger_autobomber_special", "Mixed Minions", "Witch", "Necromancer", "stable_shell", ["reddit_325_index"]),
        cand("3.25", "frost_blades_slayer", "Frost Blades Slayer", "melee_strike_slam", "Frost Blades", "Duelist", "Slayer", "transition_case", ["reddit_325_index"]),
        cand("3.25", "eviscerate_bleed_gladiator", "Eviscerate Bleed Gladiator", "melee_strike_slam", "Eviscerate", "Duelist", "Gladiator", "transition_case", ["reddit_325_index"]),
        cand("3.25", "lacerate_bleed_gladiator", "Lacerate Bleed Gladiator", "dot_ailment_dot", "Lacerate", "Duelist", "Gladiator", "transition_case", ["reddit_325_index"]),
        cand("3.25", "bama_necromancer", "BAMA Necromancer", "minion_trigger_autobomber_special", "Blink Arrow / Mirror Arrow", "Witch", "Necromancer", "transition_case", ["reddit_325_index"]),
        cand("3.25", "energy_blade_inquisitor", "Energy Blade Inquisitor", "spell_hit_brand_selfcast", "Energy Blade", "Templar", "Inquisitor", "failure_edge_case", ["reddit_325_index"]),
        cand("3.25", "retaliate_eviscerate_gladiator", "Retaliate Eviscerate Gladiator", "melee_strike_slam", "Eviscerate", "Duelist", "Gladiator", "failure_edge_case", ["reddit_325_index"], notes="New-skill warning candidate."),
        cand("3.25", "splitting_steel_champion", "Splitting Steel Champion", "bow_projectile_attack_mapper", "Splitting Steel", "Duelist", "Champion", "failure_edge_case", ["reddit_325_index"]),
        cand("3.25", "storm_burst_totems_hierophant", "Storm Burst Totems Hierophant", "trap_mine_totem", "Storm Burst Totems", "Templar", "Hierophant", "failure_edge_case", ["reddit_325_index"]),
    ],
    "3.26": [
        cand("3.26", "volcanic_fissure_berserker", "Volcanic Fissure of Snaking Berserker", "melee_strike_slam", "Volcanic Fissure", "Marauder", "Berserker", "stable_shell", ["reddit_326_index", "poe_vault_326"]),
        cand("3.26", "earthquake_bleed_gladiator", "Earthquake Bleed Gladiator", "melee_strike_slam", "Earthquake", "Duelist", "Gladiator", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "lightning_conduit_elementalist", "Lightning Conduit Elementalist", "spell_hit_brand_selfcast", "Lightning Conduit", "Witch", "Elementalist", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "penance_brand_inquisitor", "Penance Brand Inquisitor", "spell_hit_brand_selfcast", "Penance Brand", "Templar", "Inquisitor", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "explosive_trap_trickster", "Explosive Trap Trickster", "trap_mine_totem", "Explosive Trap", "Shadow", "Trickster", "stable_shell", ["reddit_326_index", "poe_vault_326"]),
        cand("3.26", "rolling_magma_mines_saboteur", "Rolling Magma Mines Saboteur", "trap_mine_totem", "Rolling Magma Mines", "Shadow", "Saboteur", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "elemental_hit_deadeye", "Elemental Hit Deadeye", "bow_projectile_attack_mapper", "Elemental Hit", "Ranger", "Deadeye", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "cobra_lash_deadeye", "Cobra Lash Deadeye", "bow_projectile_attack_mapper", "Cobra Lash", "Ranger", "Deadeye", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "righteous_fire_chieftain", "Righteous Fire Chieftain", "dot_ailment_dot", "Righteous Fire", "Marauder", "Chieftain", "stable_shell", ["reddit_326_index", "poe_vault_326"]),
        cand("3.26", "blight_of_contagion_trickster", "Blight of Contagion Trickster", "dot_ailment_dot", "Blight of Contagion", "Shadow", "Trickster", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "poison_srs_necromancer", "Poison SRS Necromancer", "minion_trigger_autobomber_special", "Summon Raging Spirits", "Witch", "Necromancer", "stable_shell", ["reddit_326_index", "poe_vault_326"]),
        cand("3.26", "minion_army_necromancer", "Minion Army Necromancer", "minion_trigger_autobomber_special", "Mixed Minions", "Witch", "Necromancer", "stable_shell", ["reddit_326_index"]),
        cand("3.26", "explosive_arrow_elementalist", "Explosive Arrow Elementalist", "trap_mine_totem", "Explosive Arrow", "Witch", "Elementalist", "transition_case", ["reddit_326_index"]),
        cand("3.26", "exsanguinate_mines_trickster", "Exsanguinate Mines Trickster", "trap_mine_totem", "Exsanguinate Mines", "Shadow", "Trickster", "transition_case", ["reddit_326_index"]),
        cand("3.26", "poisonous_concoction_pathfinder", "Poisonous Concoction Pathfinder", "dot_ailment_dot", "Poisonous Concoction", "Ranger", "Pathfinder", "transition_case", ["reddit_326_index"]),
        cand("3.26", "molten_strike_zenith_juggernaut", "Molten Strike of the Zenith Juggernaut", "melee_strike_slam", "Molten Strike", "Marauder", "Juggernaut", "transition_case", ["reddit_326_index"]),
        cand("3.26", "power_siphon_archmage_hierophant", "Power Siphon Archmage Hierophant", "bow_projectile_attack_mapper", "Power Siphon", "Templar", "Hierophant", "failure_edge_case", ["reddit_326_index"]),
        cand("3.26", "winter_orb_occultist", "Winter Orb Occultist", "spell_hit_brand_selfcast", "Winter Orb", "Witch", "Occultist", "failure_edge_case", ["reddit_326_index"]),
        cand("3.26", "soulrend_occultist", "Soulrend Occultist", "dot_ailment_dot", "Soulrend", "Witch", "Occultist", "failure_edge_case", ["reddit_326_index"]),
        cand("3.26", "animate_weapon_poison_necromancer", "Animate Weapon Poison Necromancer", "minion_trigger_autobomber_special", "Animate Weapon", "Witch", "Necromancer", "failure_edge_case", ["reddit_326_index"]),
    ],
    "3.27": [
        cand("3.27", "earthshatter_berserker", "Earthshatter Berserker", "melee_strike_slam", "Earthshatter", "Marauder", "Berserker", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "ground_slam_slayer", "Ground Slam Slayer", "melee_strike_slam", "Ground Slam", "Duelist", "Slayer", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "ice_nova_hierophant", "Ice Nova of Frostbolts Hierophant", "spell_hit_brand_selfcast", "Ice Nova of Frostbolts", "Templar", "Hierophant", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "lightning_conduit_elementalist", "Lightning Conduit Elementalist", "spell_hit_brand_selfcast", "Lightning Conduit", "Witch", "Elementalist", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "pyroclast_mine_saboteur", "Pyroclast Mine Saboteur", "trap_mine_totem", "Pyroclast Mine", "Shadow", "Saboteur", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "storm_burst_totems_hierophant", "Storm Burst Totems Hierophant", "trap_mine_totem", "Storm Burst Totems", "Templar", "Hierophant", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "kinetic_blast_deadeye", "Kinetic Blast Deadeye", "bow_projectile_attack_mapper", "Kinetic Blast", "Ranger", "Deadeye", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "lightning_arrow_deadeye", "Lightning Arrow Deadeye", "bow_projectile_attack_mapper", "Lightning Arrow", "Ranger", "Deadeye", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "righteous_fire_chieftain", "Righteous Fire Chieftain", "dot_ailment_dot", "Righteous Fire", "Marauder", "Chieftain", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "blight_of_contagion_trickster", "Blight of Contagion Trickster", "dot_ailment_dot", "Blight of Contagion", "Shadow", "Trickster", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "raise_spectre_necromancer", "Raise Spectre Necromancer", "minion_trigger_autobomber_special", "Raise Spectre", "Witch", "Necromancer", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "poison_srs_necromancer", "Poison SRS Necromancer", "minion_trigger_autobomber_special", "Summon Raging Spirits", "Witch", "Necromancer", "stable_shell", ["reddit_327_index"]),
        cand("3.27", "frost_blades_slayer", "Frost Blades Slayer", "melee_strike_slam", "Frost Blades", "Duelist", "Slayer", "transition_case", ["reddit_327_index"]),
        cand("3.27", "penance_brand_inquisitor", "Penance Brand Inquisitor", "spell_hit_brand_selfcast", "Penance Brand", "Templar", "Inquisitor", "transition_case", ["reddit_327_index"]),
        cand("3.27", "exsanguinate_reap_mines_trickster", "Exsanguinate Reap Mines Trickster", "trap_mine_totem", "Exsanguinate Mines", "Shadow", "Trickster", "transition_case", ["reddit_327_index"]),
        cand("3.27", "summon_holy_relic_necromancer", "Summon Holy Relic Necromancer", "minion_trigger_autobomber_special", "Summon Holy Relic", "Witch", "Necromancer", "transition_case", ["reddit_327_index"]),
        cand("3.27", "poison_coc_detonate_dead_assassin", "Poison CoC Detonate Dead Assassin", "minion_trigger_autobomber_special", "Cast on Critical Strike Detonate Dead", "Shadow", "Assassin", "failure_edge_case", ["reddit_327_index"]),
        cand("3.27", "flicker_champion", "Flicker Champion", "melee_strike_slam", "Flicker Strike", "Duelist", "Champion", "failure_edge_case", ["reddit_327_index"]),
        cand("3.27", "viper_strike_mamba_pathfinder", "Viper Strike of the Mamba Pathfinder", "dot_ailment_dot", "Viper Strike", "Ranger", "Pathfinder", "failure_edge_case", ["reddit_327_index"]),
        cand("3.27", "volatile_dead_spellslinger_elementalist", "Volatile Dead Spellslinger Elementalist", "minion_trigger_autobomber_special", "Spellslinger Volatile Dead", "Witch", "Elementalist", "failure_edge_case", ["reddit_327_index"]),
    ],
    "3.28": [
        cand("3.28", "bleed_slam_slayer", "Bleed Slam Slayer", "melee_strike_slam", "Bleed Slam", "Duelist", "Slayer", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "boneshatter_juggernaut", "Boneshatter Complex Trauma Juggernaut", "melee_strike_slam", "Boneshatter", "Marauder", "Juggernaut", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "shock_nova_archmage_hierophant", "Shock Nova Archmage Hierophant", "spell_hit_brand_selfcast", "Shock Nova", "Templar", "Hierophant", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "spark_hierophant", "Spark Hierophant", "spell_hit_brand_selfcast", "Spark", "Templar", "Hierophant", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "kinetic_fusillade_totem_hierophant", "Kinetic Fusillade Totem Hierophant", "trap_mine_totem", "Kinetic Fusillade Totems", "Templar", "Hierophant", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "holy_flame_totem_hierophant", "Holy Flame Totem Hierophant", "trap_mine_totem", "Holy Flame Totem", "Templar", "Hierophant", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "elemental_hit_deadeye", "Elemental Hit Deadeye", "bow_projectile_attack_mapper", "Elemental Hit", "Ranger", "Deadeye", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "kinetic_blast_deadeye", "Kinetic Blast Deadeye", "bow_projectile_attack_mapper", "Kinetic Blast", "Ranger", "Deadeye", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "righteous_fire_chieftain", "Righteous Fire Chieftain", "dot_ailment_dot", "Righteous Fire", "Marauder", "Chieftain", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "poisonous_concoction_pathfinder", "Poisonous Concoction Pathfinder", "dot_ailment_dot", "Poisonous Concoction", "Ranger", "Pathfinder", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "raise_spectre_necromancer", "Raise Spectre Necromancer", "minion_trigger_autobomber_special", "Raise Spectre", "Witch", "Necromancer", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "summon_holy_relic_necromancer", "Summon Holy Relic Necromancer", "minion_trigger_autobomber_special", "Summon Holy Relic", "Witch", "Necromancer", "stable_shell", ["reddit_328_index"]),
        cand("3.28", "impending_doom_reliquarian", "Impending Doom Reliquarian", "dot_ailment_dot", "Impending Doom", "Scion", "Reliquarian", "transition_case", ["reddit_328_index"]),
        cand("3.28", "exsanguinate_reap_mines_trickster", "Exsanguinate Reap Mines Trickster", "trap_mine_totem", "Exsanguinate Mines", "Shadow", "Trickster", "transition_case", ["reddit_328_index", "youtube_328_fearlessdumb0_exsanguinate_reap_miner"], notes="User-corrected mine lane priority: track Exsanguinate/Reap Miner Trickster instead of generic Pyroclast/Hexblast mine fallback."),
        cand("3.28", "storm_brand_elementalist", "Storm Brand Elementalist", "spell_hit_brand_selfcast", "Storm Brand", "Witch", "Elementalist", "transition_case", ["reddit_328_index"]),
        cand("3.28", "poison_carrion_golem_witch", "Poison Carrion Golem Necromancer", "minion_trigger_autobomber_special", "Summon Carrion Golem", "Witch", "Necromancer", "transition_case", ["youtube_tori_sensei_poison_carrion_golem", "youtube_328_poison_carrion_golem_necromancer", "youtube_326_tori_poison_carrion_golem", "pob_archives_global"], notes="User-corrected current minion lane: Tori-sensei is preparing Poison Carrion Golem this season. A parser-valid 3.28 Necromancer staged PoB is collected; keep searching for Tori-sensei's exact current-season PoB as a separate source check."),
        cand("3.28", "ignite_slamentalist_elementalist", "Ignite Slamentalist Elementalist", "melee_strike_slam", "Sunder", "Witch", "Elementalist", "transition_case", ["youtube_328_mastert_ignite_slamentalist", "pob_archives_global"], notes="User-added Master T lane. Parser-valid staged PoB covers Rolling Magma/RF campaign into Sunder ignite Elementalist; treat as Witch melee/ignite transition evidence, not generic Duelist melee."),
        cand("3.28", "righteous_cold_dot_autobomber_elementalist", "Righteous Cold Dot Autobomber Elementalist", "dot_ailment_dot", "Vaal Cold Snap", "Witch", "Elementalist", "transition_case", ["mobalytics_328_mastert_righteous_cold_autobomber", "youtube_328_mastert_righteous_cold_autobomber", "pob_archives_global"], notes="User-added Master T lane. Mobalytics guide marks this as a 3.28 endgame transition build; use as transition/economy evidence rather than campaign leveling."),
        cand("3.28", "volatile_dead_spellslinger_necromancer", "Volatile Dead Spellslinger Necromancer", "minion_trigger_autobomber_special", "Spellslinger Volatile Dead", "Witch", "Necromancer", "transition_case", ["reddit_328_index"]),
        cand("3.28", "holy_hammers_berserker", "Holy Hammers Berserker", "melee_strike_slam", "Holy Hammers", "Marauder", "Berserker", "failure_edge_case", ["reddit_328_index"], notes="New skill warning candidate."),
        cand("3.28", "holy_strike_chieftain", "Holy Strike Chieftain", "melee_strike_slam", "Holy Strike", "Marauder", "Chieftain", "failure_edge_case", ["reddit_328_index"], notes="New skill warning candidate."),
        cand("3.28", "eye_of_winter_mines_inquisitor", "Eye of Winter Mines Inquisitor", "trap_mine_totem", "Eye of Winter Mines", "Templar", "Inquisitor", "failure_edge_case", ["reddit_328_index"]),
        cand("3.28", "wintertide_brand_elementalist", "Wintertide Brand Elementalist", "dot_ailment_dot", "Wintertide Brand", "Witch", "Elementalist", "failure_edge_case", ["reddit_328_index"]),
    ],
    "3.29": [
        cand("3.29", "reliquarian_dawnbreaker_rf", "Reliquarian Dawnbreaker RF Fire Conversion", "dot_ailment_dot", "Righteous Fire", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian", "youtube_329_goratha_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_hot_autobomber", "Reliquarian Herald of Thunder Autobomber", "minion_trigger_autobomber_special", "Herald of Thunder", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_blight_contagion", "Reliquarian Blight of Contagion", "dot_ailment_dot", "Blight of Contagion", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_specialists"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_static_strike", "Reliquarian Static Strike Mapper", "melee_strike_slam", "Static Strike", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_lightning_strike", "Reliquarian Lightning Strike Fire-Taken Defense", "melee_strike_slam", "Lightning Strike", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_gloomfang_wander", "Reliquarian Gloomfang Wander", "bow_projectile_attack_mapper", "Kinetic Blast", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "toxic_rain_pathfinder", "Toxic Rain Pathfinder Specialist", "dot_ailment_dot", "Toxic Rain", "Ranger", "Pathfinder", "stable_shell", ["reddit_329_specialists"], "watchlist_pre_patch_notes"),
        cand("3.29", "pconc_pathfinder", "Poisonous Concoction Pathfinder Specialist", "bow_projectile_attack_mapper", "Poisonous Concoction", "Ranger", "Pathfinder", "stable_shell", ["reddit_329_specialists"], "watchlist_pre_patch_notes", notes="Projectile attack lens; poison scaling is captured later in ailment-state normalization."),
        cand("3.29", "hexblast_mines_bosser", "Hexblast Mines Bossing Specialist", "trap_mine_totem", "Hexblast Mines", "Shadow", "Trickster", "stable_shell", ["reddit_329_specialists"], "watchlist_pre_patch_notes"),
        cand("3.29", "penance_brand_sanctum", "Penance Brand Sanctum Specialist", "spell_hit_brand_selfcast", "Penance Brand", "Templar", "Inquisitor", "stable_shell", ["reddit_329_specialists"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_black_cane_spell", "Reliquarian Black Cane Spell Shell", "spell_hit_brand_selfcast", "Self-Cast Spell", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian", "youtube_329_goratha_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_explosive_trap_fire_taken", "Reliquarian Explosive Trap Fire-Taken Defense", "trap_mine_totem", "Explosive Trap", "Scion", "Reliquarian", "stable_shell", ["official_329_reliquarian", "reddit_329_reliquarian", "reddit_329_specialists"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_life_stacker_rathpith", "Reliquarian Life Stacker Rathpith Shell", "spell_hit_brand_selfcast", "Rathpith Spell", "Scion", "Reliquarian", "transition_case", ["official_329_reliquarian", "reddit_329_reliquarian", "youtube_329_goratha_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_arakaali_poison_attack", "Reliquarian Arakaali Poison Attack", "minion_trigger_autobomber_special", "Poison Attack", "Scion", "Reliquarian", "transition_case", ["official_329_reliquarian", "reddit_329_reliquarian", "youtube_329_goratha_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_sacred_chalice_bladefall", "Reliquarian Sacred Chalice Bladefall", "spell_hit_brand_selfcast", "Bladefall / Blade Blast", "Scion", "Reliquarian", "transition_case", ["official_329_reliquarian", "reddit_329_reliquarian", "youtube_329_goratha_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_molten_burst_on_hit", "Reliquarian Molten Burst On-Hit", "melee_strike_slam", "Molten Burst", "Scion", "Reliquarian", "transition_case", ["official_329_reliquarian", "reddit_329_reliquarian", "youtube_329_goratha_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_melding_defense", "Reliquarian Melding Defense Shell", "spell_hit_brand_selfcast", "Any Spell", "Scion", "Reliquarian", "failure_edge_case", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_screams_no_flask", "Reliquarian Screams No-Flask Defense", "minion_trigger_autobomber_special", "Any Skill", "Scion", "Reliquarian", "failure_edge_case", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes"),
        cand("3.29", "reliquarian_molten_burst_support_gap", "Reliquarian Molten Burst Support-Gap Check", "melee_strike_slam", "Molten Burst", "Scion", "Reliquarian", "failure_edge_case", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes", notes="Community flags support-link uncertainty."),
        cand("3.29", "reliquarian_phantasm_survival_gap", "Reliquarian Phantasm Survival Gap Check", "minion_trigger_autobomber_special", "Phantasms", "Scion", "Reliquarian", "failure_edge_case", ["official_329_reliquarian", "reddit_329_reliquarian"], "watchlist_pre_patch_notes", notes="Community flags minion survival risk for pure spell investment."),
    ],
}


def _source_families(source_refs: list[str]) -> list[str]:
    return sorted({SOURCE_REGISTRY[source]["family"] for source in source_refs})


def build_expanded_collection_queue() -> dict[str, Any]:
    patches: list[dict[str, Any]] = []
    for patch in sorted(PATCH_CANDIDATES):
        patch_backfill = PATCH_SOURCE_BACKFILL[patch]
        candidates = [dict(candidate) for candidate in PATCH_CANDIDATES[patch]]
        for candidate in candidates:
            source_refs = list(dict.fromkeys(candidate["source_refs"] + patch_backfill))
            candidate["source_refs"] = source_refs
        lane_counts = Counter(candidate["lane_id"] for candidate in candidates)
        role_counts = Counter(candidate["collection_role"] for candidate in candidates)
        source_family_counts: Counter[str] = Counter()
        for candidate in candidates:
            candidate["source_families"] = _source_families(candidate["source_refs"])
            source_family_counts.update(candidate["source_families"])

        patches.append(
            {
                "patch": patch,
                "patch_target_status": "watchlist" if patch == "3.29" else "confirmed_collection",
                "target_candidate_count": 20,
                "candidate_count": len(candidates),
                "lane_counts": dict(sorted(lane_counts.items())),
                "collection_role_counts": dict(sorted(role_counts.items())),
                "source_family_counts": dict(sorted(source_family_counts.items())),
                "candidates": candidates,
            }
        )

    totals = {
        "patch_count": len(patches),
        "candidate_count": sum(patch["candidate_count"] for patch in patches),
        "confirmed_candidate_count": sum(
            patch["candidate_count"]
            for patch in patches
            if patch["patch_target_status"] == "confirmed_collection"
        ),
        "watchlist_candidate_count": sum(
            patch["candidate_count"]
            for patch in patches
            if patch["patch_target_status"] == "watchlist"
        ),
    }

    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_build_corpus_expanded_collection_queue",
        "updated_at": "2026-07-16",
        "purpose": "Source-hunted candidate slots for the minimum 20-build-case-per-patch corpus baseline. Additional creator/user-discovered candidates are kept instead of replacing existing rows. These are not complete BuildInstance cases until PoBs/state snapshots are normalized.",
        "source_registry": SOURCE_REGISTRY,
        "totals": totals,
        "patches": patches,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help=f"Write {OUTPUT_PATH.relative_to(ROOT)}")
    args = parser.parse_args()

    result = build_expanded_collection_queue()
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.write:
        OUTPUT_PATH.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
