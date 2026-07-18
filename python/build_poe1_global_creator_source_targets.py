# -*- coding: utf-8 -*-
"""Build a global POE1 creator/source target map.

This is an intake artifact, not a recommendation list. It intentionally mixes
known builders, current Twitch language-rank targets, and YouTube discovery
targets so later collection can decide which PoBs/guides are promotable.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "poe1_global_creator_source_targets_v1.json"

GENERATED_AT = "2026-07-17T00:00:00+07:00"
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 Pathcraft-AI source research",
    "Accept-Language": "en-US,en;q=0.9",
}


def youtube_search_url(query: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def twitchmetrics_url(lang: str) -> str:
    return f"https://www.twitchmetrics.net/channels/viewership?game=Path+of+Exile&lang={lang}"


def c(
    creator_id: str,
    display_name: str,
    *,
    roles: list[str],
    focus: list[str],
    aliases: list[str] | None = None,
    youtube_handle: str | None = None,
    youtube_query: str | None = None,
    twitch_handle: str | None = None,
    guide_urls: list[str] | None = None,
    evidence_level: str = "discovery_target_needs_confirmation",
) -> dict[str, Any]:
    query = youtube_query or f"{display_name} Path of Exile 3.29 build"
    urls: list[dict[str, str]] = []
    if youtube_handle:
        urls.append({"kind": "youtube_channel", "url": f"https://www.youtube.com/@{youtube_handle}"})
    else:
        urls.append({"kind": "youtube_search", "url": youtube_search_url(query)})
    if twitch_handle:
        urls.append({"kind": "twitch_channel", "url": f"https://www.twitch.tv/{twitch_handle}"})
    for guide_url in guide_urls or []:
        urls.append({"kind": "guide_or_build_index", "url": guide_url})

    platforms = []
    if youtube_handle or query:
        platforms.append("youtube")
    if twitch_handle:
        platforms.append("twitch")
    if guide_urls:
        platforms.append("guide_site")

    return {
        "creator_id": creator_id,
        "display_name": display_name,
        "aliases": aliases or [display_name],
        "primary_platforms": platforms,
        "source_roles": roles,
        "known_focus": focus,
        "source_urls": urls,
        "youtube_query": query,
        "evidence_level": evidence_level,
        "promotion_status": "source_target_only_requires_direct_pob_or_stage_guide_before_build_promotion",
    }


REGIONS: list[dict[str, Any]] = [
    {
        "region_id": "english_global_core",
        "country_or_language_region": "English/global core",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "en",
        "youtube_market_queries": [
            "Path of Exile 3.29 league starter build",
            "Path of Exile 3.29 farming strategy",
            "Path of Exile 3.28 build guide",
        ],
        "creator_targets": [
            c("zizaran", "Zizaran", roles=["streamer", "youtube", "hardcore_builder"], focus=["hardcore", "league_start", "leveling", "gauntlet"], youtube_handle="Zizaran", twitch_handle="zizaran", evidence_level="known_global_builder"),
            c("ghazzytv", "GhazzyTV", roles=["youtube", "streamer", "guide_author"], focus=["minion", "necromancer", "league_start"], youtube_handle="GhazzyTV", twitch_handle="ghazzytv", evidence_level="known_global_builder"),
            c("captainlance9", "CaptainLance9", roles=["streamer", "youtube", "builder"], focus=["experimental", "high_end", "energy_shield", "trigger"], youtube_handle="CaptainLance9", twitch_handle="captainlance9", evidence_level="known_global_builder"),
            c("crouching_tuna", "Crouching_Tuna", roles=["streamer", "youtube", "builder"], focus=["ranger_projectile", "bow", "high_end_mapping"], aliases=["Crouching Tuna", "Crouching_Tuna"], twitch_handle="crouching_tuna", evidence_level="known_global_builder"),
            c("fubgun", "Fubgun", roles=["streamer", "youtube", "farming_strategy"], focus=["trade_farming", "atlas_strategy", "ranger_projectile", "high_end_mapping"], youtube_handle="Fubgun", twitch_handle="fubgun", evidence_level="known_global_builder"),
            c("palsteron", "Palsteron", roles=["youtube", "builder"], focus=["league_start", "totem", "meta_roundups"], youtube_handle="Palsteron", twitch_handle="palsteron", evidence_level="known_global_builder"),
            c("ruetoo", "Ruetoo", roles=["streamer", "builder"], focus=["trade_meta", "league_start", "build_shells"], aliases=["Rue", "Ruetoo"], twitch_handle="ruetoo", evidence_level="known_global_builder"),
            c("pohx", "Pohx", roles=["youtube", "guide_author", "streamer"], focus=["righteous_fire", "new_player_guide", "league_start"], aliases=["Pohx", "Pohx Kappa"], youtube_handle="PohxKappa", twitch_handle="pohx", evidence_level="known_global_builder"),
            c("tytykiller", "tytykiller", roles=["streamer", "youtube", "racer"], focus=["leveling", "racing", "campaign_practice"], youtube_handle="tytykiller", twitch_handle="tytykiller", evidence_level="known_global_leveling_source"),
            c("ben_", "Ben_", roles=["streamer", "racer", "hardcore_builder"], focus=["hardcore", "bossing", "race_meta", "defense"], aliases=["Ben", "Ben_", "Lightee"], twitch_handle="ben_", evidence_level="known_global_builder"),
        ],
    },
    {
        "region_id": "english_specialist_builders",
        "country_or_language_region": "English specialist builders",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "en",
        "youtube_market_queries": [
            "Path of Exile 3.29 specialist build guide",
            "Path of Exile 3.28 one build creator guide",
        ],
        "creator_targets": [
            c("cptn_garbage", "Cptn Garbage", roles=["guide_author", "builder"], focus=["Exsanguinate Miner Trickster", "mine", "league_start"], aliases=["Cptn Garbage", "Captain Garbage"], guide_urls=["https://maxroll.gg/poe/build-guides/exsanguinate-miner-trickster-league-starter"], evidence_level="user_seeded_known_specialist"),
            c("jorgen", "Jorgen", roles=["youtube", "builder"], focus=["mine", "scion", "reliquarian", "defense"], youtube_query="Jorgen Path of Exile 3.29 build", evidence_level="user_seeded_known_specialist"),
            c("emiracles", "emiracles", roles=["streamer", "builder"], focus=["cws", "cast_when_stunned", "chieftain"], aliases=["emiracle", "emiracles"], twitch_handle="emiracles", evidence_level="user_seeded_known_specialist"),
            c("conner_converse", "Conner Converse", roles=["youtube", "builder"], focus=["mana_stack", "molten_strike", "mjolner", "high_end"], aliases=["Conner Converse", "onemanaleft"], evidence_level="user_seeded_known_specialist"),
            c("dconnic", "저 가련한 모독자 / dconnic", roles=["youtube", "builder"], focus=["minion", "spectre", "necromancer"], aliases=["Dconnic", "dconnic", "저 가련한 모독자"], youtube_handle="dconnic", youtube_query="dconnic Path of Exile", evidence_level="user_seeded_known_specialist"),
            c("anime_princess", "anime princess", roles=["youtube", "builder"], focus=["archmage", "spark", "caster"], aliases=["anime princess", "anime_princess"], evidence_level="expanded_discovery_known_builder"),
            c("kankar", "Kankar", roles=["youtube", "builder"], focus=["ranger_projectile", "venom_gyre", "deadeye"], youtube_query="Kankar Path of Exile", evidence_level="expanded_discovery_known_builder"),
            c("llyd", "LLYD", roles=["youtube", "builder"], focus=["scion", "cyclone", "ascendant"], aliases=["LLYD", "llyd"], evidence_level="expanded_discovery_known_builder"),
            c("poeguy", "POEGuy", roles=["youtube", "builder"], focus=["siege_ballista", "one_build_specialist"], aliases=["POEGuy", "POEGuy007"], twitch_handle="POEGuy007", evidence_level="user_seeded_one_build_specialist"),
            c(
                "sanavixx",
                "Sanavixx",
                roles=["youtube", "builder", "creator_site"],
                focus=["cyclone", "cyclone_of_tumult", "shockwave", "crafting", "one_build_specialist"],
                youtube_handle="SaNaViXX",
                guide_urls=["https://sanavixx.com/crafting/", "https://pobb.in/RH9MMGmuuro2"],
                evidence_level="user_seeded_one_build_specialist",
            ),
        ],
    },
    {
        "region_id": "english_supplemental_research",
        "country_or_language_region": "English supplemental research",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "en",
        "youtube_market_queries": [
            "Path of Exile 3.29 build shells",
            "Path of Exile 3.29 minion build",
            "Path of Exile 3.29 melee build",
        ],
        "creator_targets": [
            c("master_t", "Master T", roles=["youtube", "builder"], focus=["ignite", "autobomber", "cold_dot", "league_start"], youtube_handle="MasterT_", guide_urls=["https://www.poebuilds.cc/author/mastert/", "https://mobalytics.gg/poe/builds/righteous-cold-dot-autobomber"], evidence_level="user_seeded_known_specialist"),
            c("exiled_cat", "EXILED CAT", roles=["youtube", "builder"], focus=["zero_to_hero", "ssf", "life_stacker_gladiator", "shield_crush", "heist_farming"], aliases=["EXILED CAT", "Exiled Cat", "ExiledCat_PoE"], youtube_handle="ExiledCat_PoE", youtube_query="EXILED CAT Path of Exile 3.28", guide_urls=["https://pobarchives.com/builds?author=EXILED+CAT"], evidence_level="user_seeded_known_specialist"),
            c("goblin_inc_probable", "Goblin-Inc probable", roles=["youtube", "builder"], focus=["variety", "build_roundups", "farming_strategy"], aliases=["Goblin", "Goblin Inc", "Goblin-Inc", "Goblin-Inc and Paychak"], youtube_query="Goblin Inc Path of Exile", evidence_level="user_seeded_ambiguous_alias"),
            c("big_ducks", "Big Ducks", roles=["youtube", "builder"], focus=["league_start", "new_player", "variety"], youtube_handle="BigDucks", evidence_level="expanded_discovery_known_builder"),
            c("subtractem", "subtractem", roles=["streamer", "youtube", "builder"], focus=["bane", "league_start", "crafting", "variety"], youtube_handle="subtractem", twitch_handle="subtractem", evidence_level="expanded_discovery_known_builder"),
            c("jungroan", "Jungroan", roles=["youtube", "builder"], focus=["bossing", "league_start", "high_end"], youtube_handle="Jungroan", evidence_level="expanded_discovery_known_builder"),
            c("goratha", "Goratha", roles=["streamer", "youtube", "hardcore_builder"], focus=["ssf", "hardcore", "league_start", "defense"], youtube_handle="Goratha", twitch_handle="goratha", evidence_level="expanded_discovery_known_builder"),
            c("tatiantel2", "Tatiantel2", roles=["streamer", "youtube", "builder"], focus=["totem", "hierophant", "league_start"], aliases=["Tatiantel2", "Tati"], twitch_handle="tatiantel2", evidence_level="expanded_discovery_known_builder"),
            c("steelmage", "Steelmage", roles=["streamer", "hardcore_builder"], focus=["hardcore", "ssf", "race_meta"], twitch_handle="steelmage", evidence_level="expanded_discovery_known_builder"),
            c("carn", "Carn", roles=["streamer", "melee_builder"], focus=["melee", "slayer", "hardcore"], aliases=["Carn", "cArn"], twitch_handle="carn_", evidence_level="expanded_discovery_known_builder"),
            c("mathil", "Mathil", roles=["streamer", "youtube", "builder"], focus=["variety", "off_meta", "high_apm"], aliases=["Mathil", "Mathilification"], youtube_handle="Mathilification", twitch_handle="mathil1", evidence_level="expanded_discovery_known_builder"),
        ],
    },
    {
        "region_id": "korea",
        "country_or_language_region": "Korea/Korean",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": None,
        "youtube_market_queries": [
            "패스 오브 엑자일 3.29 빌드",
            "패스오브엑자일 3.28 스타터 빌드",
            "POE 3.29 파밍 전략",
        ],
        "creator_targets": [
            c("tori_sensei", "토리센세", roles=["youtube", "builder"], focus=["minion", "poison_carrion_golem", "league_start"], aliases=["토리센세", "Tori-sensei", "torisense"], youtube_handle="torisense", evidence_level="user_seeded_known_korean_builder"),
            c("arserina", "아르세리나", roles=["youtube", "builder"], focus=["variety", "league_start", "minion"], aliases=["아르세리나", "Arserina", "Arserina 아르"], youtube_query="아르세리나 POE", evidence_level="korean_discovery_needs_channel_confirmation"),
            c("nyangnyonghyeon", "냥냥뇽현", roles=["youtube", "builder"], focus=["variety", "league_start"], aliases=["냥냥뇽현", "냥현", "냥현이"], youtube_query="냥현 POE 3.28", evidence_level="korean_discovery_needs_channel_confirmation"),
            c("daisy_kr", "Daisy_데이지", roles=["youtube", "builder"], focus=["variety", "starter", "guide"], aliases=["Daisy_데이지", "Daisy"], evidence_level="korean_discovery_needs_channel_confirmation"),
            c("rona_kr", "Rona", roles=["youtube", "builder"], focus=["variety", "guide", "farming_strategy"], aliases=["Rona", "로나", "로나의 게임 채널 Ronatube", "Ronatube"], youtube_query="Rona POE 패스오브엑자일", evidence_level="korean_discovery_needs_channel_confirmation"),
            c("catseye7", "Catseye7", roles=["youtube", "builder"], focus=["variety", "guide"], aliases=["Catseye7", "캣츠아이"], evidence_level="korean_discovery_needs_channel_confirmation"),
            c("star_dew_valley_kr", "별이슬골짜기", roles=["youtube", "builder"], focus=["variety", "guide", "starter"], youtube_query="별이슬골짜기 POE", evidence_level="korean_discovery_needs_channel_confirmation"),
            c("amphis", "엠피스 AMPHIS", roles=["youtube", "builder"], focus=["variety", "guide"], aliases=["엠피스", "AMPHIS"], evidence_level="korean_discovery_needs_channel_confirmation"),
            c("kkakkamori", "까까모리", roles=["youtube", "builder"], focus=["melee", "gamble", "guide"], youtube_query="까까모리 POE", evidence_level="korean_discovery_needs_channel_confirmation"),
            c("black_giant_kr", "검은거인", roles=["youtube", "builder"], focus=["high_end", "righteous_fire", "autobomber", "guide"], aliases=["검은거인", "검은거인 BlackGiant", "BlackGiant"], youtube_query="검은거인 POE", evidence_level="korean_discovery_needs_channel_confirmation"),
        ],
    },
    {
        "region_id": "japan",
        "country_or_language_region": "Japan/Japanese",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "ja",
        "youtube_market_queries": [
            "Path of Exile 3.29 ビルド",
            "PoE 3.28 ビルド スターター",
            "Path of Exile 日本語 ビルド",
        ],
        "creator_targets": [
            c("miz4ry", "みざりー / miz4ry", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["みざりー", "miz4ry"], twitch_handle="miz4ry", evidence_level="twitchmetrics_language_rank"),
            c("sen10ce3", "せんてんす / sen10ce3", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["せんてんす", "sen10ce3"], twitch_handle="sen10ce3", evidence_level="twitchmetrics_language_rank"),
            c("sumitsukikakko", "sumitsukikakko", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="sumitsukikakko", evidence_level="twitchmetrics_language_rank"),
            c("yosyar", "よしゃ / yosyar", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["よしゃ", "yosyar"], twitch_handle="yosyar", evidence_level="twitchmetrics_language_rank"),
            c("buri8857", "buri8857", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="buri8857", evidence_level="twitchmetrics_language_rank"),
            c("iowof", "マンテス / iowof", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["マンテス", "iowof"], twitch_handle="iowof", evidence_level="twitchmetrics_language_rank"),
            c("r1n_game", "r1n_game", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="r1n_game", evidence_level="twitchmetrics_language_rank"),
            c("samuraimaestro", "サムライマン / samuraimaestro", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["サムライマン", "samuraimaestro"], twitch_handle="samuraimaestro", evidence_level="twitchmetrics_language_rank"),
            c("watarux", "watarux", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="watarux", evidence_level="twitchmetrics_language_rank"),
            c("gatimonking", "ガチモンキング / gatimonking", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["ガチモンキング", "gatimonking"], twitch_handle="gatimonking", evidence_level="twitchmetrics_language_rank"),
        ],
    },
    {
        "region_id": "russia_cis",
        "country_or_language_region": "Russia/CIS/Russian",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "ru",
        "youtube_market_queries": [
            "Path of Exile 3.29 билд",
            "PoE 3.28 стартер билд",
            "Path of Exile фарм стратегия",
        ],
        "creator_targets": [
            c("goodboy_tv", "GoodBoy_TV", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="GoodBoy_TV", evidence_level="twitchmetrics_language_rank"),
            c("redrebell", "REDrebell", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="REDrebell", evidence_level="twitchmetrics_language_rank"),
            c("fatmanplaypoe", "FatManPlayPoe", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="FatManPlayPoe", evidence_level="twitchmetrics_language_rank"),
            c("blizzardprogame", "blizzardprogame", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="blizzardprogame", evidence_level="twitchmetrics_language_rank"),
            c("mynm_777", "mynm_777", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="mynm_777", evidence_level="twitchmetrics_language_rank"),
            c("vurman", "Vurman", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Vurman", evidence_level="twitchmetrics_language_rank"),
            c("ded_grobovshik", "ded_grobovshik", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="ded_grobovshik", evidence_level="twitchmetrics_language_rank"),
            c("bjuboljno", "Bjuboljno", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Bjuboljno", evidence_level="twitchmetrics_language_rank"),
            c("prosto_sonyar", "prosto_sonyar", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="prosto_sonyar", evidence_level="twitchmetrics_language_rank"),
            c("jagernotd", "JagerNotD", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="JagerNotD", evidence_level="twitchmetrics_language_rank"),
        ],
    },
    {
        "region_id": "france_french",
        "country_or_language_region": "France/French",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "fr",
        "youtube_market_queries": [
            "Path of Exile 3.29 build français",
            "PoE 3.28 build français",
            "Path of Exile guide français farm",
        ],
        "creator_targets": [
            c("zeeboub", "ZeeBoub", roles=["streamer", "builder"], focus=["penance_brand", "one_build_specialist", "french_source"], twitch_handle="ZeeBoub", evidence_level="user_seeded_one_build_specialist"),
            c("welya_97", "Welya_97", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Welya_97", evidence_level="twitchmetrics_language_rank"),
            c("guormundr", "guormundr", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="guormundr", evidence_level="twitchmetrics_language_rank"),
            c("desmosaze", "DesmoSaze", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="DesmoSaze", evidence_level="twitchmetrics_language_rank"),
            c("cmdr_zolta", "CMDR_Zolta", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="CMDR_Zolta", evidence_level="twitchmetrics_language_rank"),
            c("balbuta", "Balbuta_", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Balbuta_", evidence_level="twitchmetrics_language_rank"),
            c("felptibob", "Felptibob", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Felptibob", evidence_level="twitchmetrics_language_rank"),
            c("albatrox18", "albatrox18", roles=["youtube", "builder"], focus=["youtube_discovery", "patch_summary"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
            c("peuget2", "Peuget2", roles=["youtube", "builder"], focus=["youtube_discovery", "league_start_test"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
            c("fraegorn", "Fraegorn", roles=["youtube", "builder"], focus=["youtube_discovery", "build_showcase"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
        ],
    },
    {
        "region_id": "germany_dach",
        "country_or_language_region": "Germany/DACH/German",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "de",
        "youtube_market_queries": [
            "Path of Exile 3.29 Build Deutsch",
            "PoE 3.28 Starter Build Deutsch",
            "Path of Exile Deutsch Farm Strategie",
        ],
        "creator_targets": [
            c("blagax", "Blagax", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Blagax", evidence_level="twitchmetrics_language_rank"),
            c("craftzwerg", "Craftzwerg", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Craftzwerg", evidence_level="twitchmetrics_language_rank"),
            c("ston3cold3", "Ston3Cold3", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Ston3Cold3", evidence_level="twitchmetrics_language_rank"),
            c("zeticx", "Zeticx", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Zeticx", evidence_level="twitchmetrics_language_rank"),
            c("ronarray", "ronarray", roles=["youtube", "builder"], focus=["league_start_roundup", "youtube_discovery"], evidence_level="youtube_search_discovery"),
            c("super_uber_dan", "Super Uber Dan", roles=["youtube", "builder"], focus=["league_start_roundup", "youtube_discovery"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
            c("tarekis", "Tarekis", roles=["forum_builder", "youtube"], focus=["flicker_trickster", "written_pob_notes"], guide_urls=["https://fr.pathofexile.com/forum/view-thread/3472898"], evidence_level="forum_build_discovery"),
            c("fraegorn_de", "Fraegorn", roles=["youtube", "builder"], focus=["translated_video_discovery", "build_showcase"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
            c("path_of_evening_de", "Path of Evening", roles=["youtube", "patch_analysis"], focus=["patch_summary", "market_signal"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
            c("lokati", "Lokati", roles=["youtube", "builder"], focus=["skill_showcase", "league_start_test"], aliases=["Lokati", "Lokati Gaming"], twitch_handle="Lokati_Gaming", evidence_level="youtube_search_discovery"),
        ],
    },
    {
        "region_id": "portuguese_br_pt",
        "country_or_language_region": "Brazil/Portugal/Portuguese",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "pt",
        "youtube_market_queries": [
            "Path of Exile 3.29 build brasil portugues",
            "PoE 3.28 starter build português",
            "Path of Exile farm estrategia brasil",
        ],
        "creator_targets": [
            c("oazuk", "oAzuK", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="oAzuK", evidence_level="twitchmetrics_language_rank"),
            c("shineray50cc", "shineray50cc", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="shineray50cc", evidence_level="twitchmetrics_language_rank"),
            c("masterxds", "MasTerxds", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="MasTerxds", evidence_level="twitchmetrics_language_rank"),
            c("chocomud", "ChocoMuD", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="ChocoMuD", evidence_level="twitchmetrics_language_rank"),
            c("kalibar", "kalibar_", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="kalibar_", evidence_level="twitchmetrics_language_rank"),
            c("kakarotoguto", "KakarotoGuto", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="KakarotoGuto", evidence_level="twitchmetrics_language_rank"),
            c("guardcodex", "GuardCodex", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="GuardCodex", evidence_level="twitchmetrics_language_rank"),
            c("jinshaadow", "jinshaadow", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="jinshaadow", evidence_level="twitchmetrics_language_rank"),
            c("poebuilds_pt", "Path of Exile Builds PT/BR discovery", roles=["youtube", "build_roundup"], focus=["youtube_discovery", "build_roundups"], youtube_query="Path of Exile 3.29 build português canal", evidence_level="youtube_search_discovery_slot"),
            c("poe_brasil_discovery", "POE Brasil discovery", roles=["youtube", "community"], focus=["youtube_discovery", "community_source"], youtube_query="POE Brasil Path of Exile 3.29 build", evidence_level="youtube_search_discovery_slot"),
        ],
    },
    {
        "region_id": "poland",
        "country_or_language_region": "Poland/Polish",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "pl",
        "youtube_market_queries": [
            "Path of Exile 3.29 build po polsku",
            "PoE 3.28 starter build polski",
            "Path of Exile polski farm",
        ],
        "creator_targets": [
            c("piotrmaciejczak", "PiotrMaciejczak", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="PiotrMaciejczak", evidence_level="twitchmetrics_language_rank"),
            c("pidzam", "Pidzam", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Pidzam", evidence_level="twitchmetrics_language_rank"),
            c("kurier_tv", "kurier_tv", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="kurier_tv", evidence_level="twitchmetrics_language_rank"),
            c("wrzasku", "Wrzasku", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Wrzasku", evidence_level="twitchmetrics_language_rank"),
            c("viviia", "Viviia_", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Viviia_", evidence_level="twitchmetrics_language_rank"),
            c("methil", "Methil__", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Methil__", evidence_level="twitchmetrics_language_rank"),
            c("dreamingpurple", "DreamingPurple", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="DreamingPurple", evidence_level="twitchmetrics_language_rank"),
            c("quantumsova", "QuantumSova", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="QuantumSova", evidence_level="twitchmetrics_language_rank"),
            c("rudnik2", "rudnik2_", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="rudnik2_", evidence_level="twitchmetrics_language_rank"),
            c("tomeczkoo", "tomeczkoo", roles=["streamer", "youtube"], focus=["mine", "starter", "polish_source"], aliases=["tomeczkoo", "Tomeczkoo o."], twitch_handle="tomeczkoo", evidence_level="twitchmetrics_language_rank"),
        ],
    },
    {
        "region_id": "spanish_latam_spain",
        "country_or_language_region": "Spain/Latin America/Spanish",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "es",
        "youtube_market_queries": [
            "Path of Exile 3.29 build español",
            "PoE 3.28 build español starter",
            "Path of Exile guía farm español",
        ],
        "creator_targets": [
            c("kroximatuz", "KroximatuZ", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="KroximatuZ", evidence_level="twitchmetrics_language_rank"),
            c("pinkyelpibe", "PinkyelPibe", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="PinkyelPibe", evidence_level="twitchmetrics_language_rank"),
            c("nicovicari", "NicoVicari", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="NicoVicari", evidence_level="twitchmetrics_language_rank"),
            c("elcertv", "ElcerTV", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="ElcerTV", evidence_level="twitchmetrics_language_rank"),
            c("mipoven", "Mipoven", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="Mipoven", evidence_level="twitchmetrics_language_rank"),
            c("xkhana", "xKhana", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="xKhana", evidence_level="twitchmetrics_language_rank"),
            c("lesslyrubedo", "LesslyRubedo", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="LesslyRubedo", evidence_level="twitchmetrics_language_rank"),
            c("ayeleth", "Ayeleth / El Rincón del Exiliado", roles=["guide_curator", "builder"], focus=["spanish_build_index", "league_start", "pob_curation"], aliases=["Ayeleth", "El Rincón del Exiliado"], guide_urls=["https://pathofexile.elrincondelexiliado.com/books/liga-mirage/page/builds-league-starters-328-guias-actualizadas"], evidence_level="guide_site_discovery"),
            c("yobostyle322", "YOBOSTYLE322", roles=["youtube", "builder"], focus=["golem", "youtube_discovery"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
            c("albatrox18_es", "albatrox18", roles=["youtube", "patch_summary"], focus=["youtube_discovery", "patch_summary"], evidence_level="youtube_search_discovery_needs_language_confirmation"),
        ],
    },
    {
        "region_id": "chinese_speaking",
        "country_or_language_region": "Taiwan/Hong Kong/China/Chinese",
        "region_kind": "language_market_not_nationality",
        "twitchmetrics_lang": "zh",
        "youtube_market_queries": [
            "流亡黯道 3.29 BD",
            "流放之路 3.29 BD",
            "POE 3.28 流亡黯道 BD",
        ],
        "creator_targets": [
            c("mme_poe", "MME", roles=["streamer", "youtube", "builder"], focus=["totem", "starter", "chinese_source"], aliases=["MME", "mme_poe"], twitch_handle="mme_poe", evidence_level="twitchmetrics_language_rank"),
            c("soul1027", "魂魂_ / soul1027", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["魂魂_", "soul1027"], twitch_handle="soul1027", evidence_level="twitchmetrics_language_rank"),
            c("toucruise", "toucruise", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="toucruise", evidence_level="twitchmetrics_language_rank"),
            c("mrkrys7", "虧柒 / mrkrys7", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["虧柒", "mrkrys7"], twitch_handle="mrkrys7", evidence_level="twitchmetrics_language_rank"),
            c("makotoders", "小誠まこと / makotoders", roles=["streamer"], focus=["current_twitch_presence", "discovery"], aliases=["小誠まこと", "makotoders"], twitch_handle="makotoders", evidence_level="twitchmetrics_language_rank"),
            c("solinariwu", "solinariwu", roles=["streamer"], focus=["current_twitch_presence", "discovery"], twitch_handle="solinariwu", evidence_level="twitchmetrics_language_rank"),
            c("rain_snow_boy", "雨雪BOY", roles=["youtube", "patch_summary"], focus=["youtube_discovery", "chinese_source"], evidence_level="youtube_search_discovery"),
            c("kbon", "KBON只會玩", roles=["youtube", "patch_summary", "builder"], focus=["youtube_discovery", "taiwan_source"], evidence_level="youtube_search_discovery"),
            c("devilcatwith2cats", "惡魔貓和幾吉和點點DevilCatwith2cats", roles=["youtube", "patch_summary", "builder"], focus=["youtube_discovery", "taiwan_source"], aliases=["惡魔貓和幾吉和點點", "DevilCatwith2cats"], evidence_level="youtube_search_discovery"),
            c("poe_dentist_summon", "POE牙医召唤", roles=["youtube", "builder"], focus=["minion", "summon", "chinese_source"], evidence_level="youtube_search_discovery"),
        ],
    },
]


def normalize(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def extract_yt_initial_data(html_text: str) -> dict[str, Any] | None:
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", html_text)
    if not match:
        match = re.search(r"ytInitialData\"\]\s*=\s*(\{.*?\});", html_text)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def text_runs(obj: dict[str, Any] | None) -> str:
    if not obj:
        return ""
    if "simpleText" in obj:
        return obj["simpleText"]
    return "".join(run.get("text", "") for run in obj.get("runs", []))


def youtube_search(query: str, *, limit: int = 8) -> list[dict[str, Any]]:
    url = youtube_search_url(query)
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        return [{"status": "request_failed", "error": str(exc), "source_url": url}]

    data = extract_yt_initial_data(response.text)
    if not data:
        return [{"status": "parse_failed", "source_url": url}]

    rows: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if "videoRenderer" in value:
                renderer = value["videoRenderer"]
                title = text_runs(renderer.get("title"))
                owner = text_runs(renderer.get("ownerText"))
                view_count = text_runs(renderer.get("viewCountText")) or text_runs(renderer.get("shortViewCountText"))
                title_low = title.casefold()
                if title and owner and not any(marker in title_low for marker in ("path of exile 2", "poe2", "poe 2")):
                    rows.append(
                        {
                            "status": "video_result",
                            "video_id": renderer.get("videoId"),
                            "video_url": f"https://www.youtube.com/watch?v={renderer.get('videoId')}",
                            "title": html.unescape(title),
                            "owner": html.unescape(owner),
                            "view_count_text": view_count,
                        }
                    )
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        video_id = row.get("video_id") or ""
        if not video_id or video_id in seen:
            continue
        seen.add(video_id)
        row["source_url"] = url
        row["raw_position"] = len(deduped) + 1
        deduped.append(row)
        if len(deduped) >= limit:
            break
    return deduped


def parse_twitchmetrics(lang: str) -> dict[str, dict[str, Any]]:
    url = twitchmetrics_url(lang)
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=20)
        response.raise_for_status()
    except requests.RequestException:
        return {}

    pattern = re.compile(
        r'<span class="text-muted">#(?P<rank>\d+)</span>.*?'
        r"<h5[^>]*>(?P<name>.*?)</h5>.*?"
        r'<samp[^>]*>(?P<viewer_hours>[0-9,]+)</samp>\s*</div>\s*viewer hours',
        re.S,
    )
    rows: dict[str, dict[str, Any]] = {}
    for match in pattern.finditer(response.text):
        name = html.unescape(re.sub(r"<.*?>", "", match.group("name")).strip())
        rows[normalize(name)] = {
            "status": "sampled",
            "rank": int(match.group("rank")),
            "display_name": name,
            "viewer_hours_text": match.group("viewer_hours"),
            "source_url": url,
        }
    return rows


def pick_youtube_evidence(creator: dict[str, Any]) -> dict[str, Any]:
    query = creator["youtube_query"]
    results = youtube_search(query, limit=8)
    if not results:
        return {"status": "no_results", "query": query, "source_url": youtube_search_url(query)}
    if results[0].get("status") != "video_result":
        return {"status": results[0].get("status"), "query": query, "source_url": results[0].get("source_url"), "error": results[0].get("error")}

    aliases = [normalize(alias) for alias in creator.get("aliases", []) if normalize(alias)]
    for result in results:
        owner_norm = normalize(result.get("owner", ""))
        if owner_norm and any(alias == owner_norm or alias in owner_norm or owner_norm in alias for alias in aliases):
            return {
                "status": "sampled",
                "query": query,
                "source_url": result["source_url"],
                "video_url": result["video_url"],
                "title": result["title"],
                "owner": result["owner"],
                "view_count_text": result.get("view_count_text", ""),
                "raw_position": result["raw_position"],
            }

    nearest = results[0]
    return {
        "status": "queried_no_owner_match",
        "query": query,
        "source_url": nearest["source_url"],
        "nearest_result": {
            "video_url": nearest["video_url"],
            "title": nearest["title"],
            "owner": nearest["owner"],
            "view_count_text": nearest.get("view_count_text", ""),
            "raw_position": nearest["raw_position"],
        },
    }


def build_dataset(live: bool = True) -> dict[str, Any]:
    retrieval_time = datetime.now(timezone.utc).isoformat()
    twitch_cache = {}
    if live:
        for lang in sorted({region.get("twitchmetrics_lang") for region in REGIONS if region.get("twitchmetrics_lang")}):
            twitch_cache[lang] = parse_twitchmetrics(lang)

    regions: list[dict[str, Any]] = []
    sampled_youtube = 0
    sampled_twitch = 0
    for region in REGIONS:
        lang = region.get("twitchmetrics_lang")
        market_samples = []
        if live:
            for query in region["youtube_market_queries"][:2]:
                market_samples.append(
                    {
                        "query": query,
                        "source_url": youtube_search_url(query),
                        "top_video_samples": youtube_search(query, limit=5),
                    }
                )

        targets = []
        for index, creator in enumerate(region["creator_targets"], start=1):
            row = dict(creator)
            row["target_rank"] = index
            row["youtube_view_evidence"] = (
                pick_youtube_evidence(row)
                if live
                else {"status": "not_sampled_offline_generation", "query": row["youtube_query"], "source_url": youtube_search_url(row["youtube_query"])}
            )
            if row["youtube_view_evidence"]["status"] == "sampled":
                sampled_youtube += 1
            twitch_evidence = None
            if live and lang and row.get("source_urls"):
                aliases = [normalize(alias) for alias in row.get("aliases", [])]
                for alias in aliases:
                    if alias in twitch_cache.get(lang, {}):
                        twitch_evidence = twitch_cache[lang][alias]
                        sampled_twitch += 1
                        break
            if twitch_evidence:
                row["twitchmetrics_evidence"] = twitch_evidence
            elif lang:
                row["twitchmetrics_evidence"] = {"status": "not_matched_in_current_language_top_page", "source_url": twitchmetrics_url(lang)}
            targets.append(row)

        regions.append(
            {
                "region_id": region["region_id"],
                "country_or_language_region": region["country_or_language_region"],
                "region_kind": region["region_kind"],
                "target_count": len(targets),
                "twitchmetrics_source_url": twitchmetrics_url(lang) if lang else None,
                "youtube_market_queries": [
                    {"query": query, "source_url": youtube_search_url(query)}
                    for query in region["youtube_market_queries"]
                ],
                "youtube_market_view_samples": market_samples,
                "creator_targets": targets,
            }
        )

    target_count = sum(len(region["creator_targets"]) for region in regions)
    return {
        "schema_version": "1.0",
        "dataset_kind": "poe1_global_creator_source_targets",
        "generated_at": GENERATED_AT,
        "retrieved_at_utc": retrieval_time if live else None,
        "purpose": "Worldwide POE1 source-target map for finding leveling, endgame, high-end, and farming-strategy evidence before promoting direct PoBs into the build corpus.",
        "source_policy": {
            "poe_scope": "poe1_only",
            "region_identity_rule": "Rows are grouped by language/content market. Nationality is not asserted unless the source itself says so.",
            "youtube_view_rule": "YouTube view counts are volatile retrieval snapshots from search result pages. Use them as popularity signals, not as build correctness evidence.",
            "promotion_gate": "Do not promote a build from creator popularity alone. Require accessible direct PoB or stage guide, parser validation, and patch/current-season context.",
            "poe2_policy": "POE2-only videos and channels are out of scope for this file.",
        },
        "evidence_types": [
            "twitchmetrics_path_of_exile_language_viewership",
            "youtube_search_video_view_count_snapshot",
            "known_builder_or_user_seed",
            "guide_site_or_forum_source",
        ],
        "coverage_summary": {
            "region_count": len(regions),
            "target_count": target_count,
            "minimum_target_count_per_region": 10,
            "youtube_view_sampled_creator_count": sampled_youtube,
            "twitchmetrics_sampled_creator_count": sampled_twitch,
            "known_limitations": [
                "Some regions have sparse POE1-specific local-language creators, so several targets are discovery slots that need manual channel confirmation.",
                "YouTube may auto-translate titles; language confirmation remains separate from view-count evidence.",
                "TwitchMetrics ranks reflect the retrieval window, not long-term authority.",
            ],
        },
        "regions": regions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Write data/poe1_global_creator_source_targets_v1.json")
    parser.add_argument("--offline", action="store_true", help="Skip live Twitch/YouTube sampling")
    args = parser.parse_args(argv)

    data = build_dataset(live=not args.offline)
    if args.write:
        OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {OUTPUT_PATH} ({data['coverage_summary']['target_count']} targets)")
    else:
        print(json.dumps(data["coverage_summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
