# -*- coding: utf-8 -*-
"""Collect Twitch VOD metadata for creator-build evidence pipelines.

Only official Helix metadata and user-authored timestamp notes are stored. The
collector intentionally does not download or mirror VOD media/transcripts.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from cws_knowledge import DEFAULT_PACK, load_pack as load_cws_pack

HELIX = "https://api.twitch.tv/helix"


class TwitchCredentialsError(RuntimeError):
    pass


def _request(path: str, token: str, client_id: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{HELIX}/{path}",
        headers={"Authorization": f"Bearer {token}", "Client-Id": client_id},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def app_access_token(client_id: str, client_secret: str) -> str:
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode("ascii")
    with urllib.request.urlopen(urllib.request.Request(
        "https://id.twitch.tv/oauth2/token", data=body, method="POST"
    ), timeout=30) as response:
        return str(json.load(response)["access_token"])


def collect_channel_videos(login: str, *, client_id: str, token: str, page_limit: int = 4) -> list[dict[str, Any]]:
    users = _request(f"users?login={urllib.parse.quote(login)}", token, client_id).get("data", [])
    if not users:
        return []
    broadcaster_id = users[0]["id"]
    videos: list[dict[str, Any]] = []
    cursor = ""
    for _ in range(page_limit):
        query = f"videos?user_id={broadcaster_id}&type=archive&first=100"
        if cursor:
            query += f"&after={urllib.parse.quote(cursor)}"
        payload = _request(query, token, client_id)
        videos.extend(payload.get("data", []))
        cursor = (payload.get("pagination") or {}).get("cursor", "")
        if not cursor:
            break
    return videos


def _load_supported_pack(pack_path: Path | str) -> dict[str, Any]:
    raw = json.loads(Path(pack_path).read_text(encoding="utf-8-sig"))
    if raw.get("dataset_kind") == "pathcraft_cws_knowledge_pack":
        return load_cws_pack(pack_path)
    if raw.get("build_id") == "poe1_3_29_allie_bob_friends_luminary":
        from allie_luminary_knowledge import load_pack as load_luminary_pack
        return load_luminary_pack(pack_path)
    raise ValueError("unsupported creator knowledge pack")


def merge_catalog(
    pack_path: Path | str, live_videos: list[dict[str, Any]], *, channel: str | None = None
) -> dict[str, Any]:
    pack = _load_supported_pack(pack_path)
    if "vod_catalog" in pack:
        catalog = pack["vod_catalog"]
        default_channel = "emiracles"
        dataset_kind = "pathcraft_cws_twitch_vod_metadata"
    else:
        catalog = [row for row in pack.get("media_catalog", []) if row.get("platform") == "twitch"]
        default_channel = "Allliee_"
        dataset_kind = "pathcraft_creator_twitch_vod_metadata"
    known = {row["video_id"]: dict(row) for row in catalog}
    for video in live_videos:
        video_id = str(video["id"])
        row = known.setdefault(video_id, {"video_id": video_id, "audit_status": "metadata_only"})
        row.update({
            "title": video.get("title"), "url": video.get("url"), "created_at": video.get("created_at"),
            "published_at": video.get("published_at"), "duration": video.get("duration"),
            "view_count": video.get("view_count"), "language": video.get("language"),
        })
    return {
        "dataset_kind": dataset_kind,
        "schema_version": 1,
        "channel": channel or default_channel,
        "source_policy": "Official Helix metadata plus manual timestamp evidence; no VOD media mirror.",
        "videos": sorted(known.values(), key=lambda row: (row.get("created_at") or row.get("date") or "", row["video_id"])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect Twitch VOD metadata for a supported creator knowledge pack.")
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--channel", help="Twitch login; inferred for bundled CWS/Allie packs when omitted.")
    parser.add_argument("--offline", action="store_true", help="Export the known catalog without API credentials.")
    args = parser.parse_args(argv)
    pack_preview = _load_supported_pack(args.pack)
    channel = args.channel or (
        "Allliee_" if pack_preview.get("build_id") == "poe1_3_29_allie_bob_friends_luminary" else "emiracles"
    )

    live: list[dict[str, Any]] = []
    if not args.offline:
        client_id = os.getenv("TWITCH_CLIENT_ID", "").strip()
        token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
        secret = os.getenv("TWITCH_CLIENT_SECRET", "").strip()
        if not client_id or (not token and not secret):
            raise TwitchCredentialsError(
                "Set TWITCH_CLIENT_ID and TWITCH_ACCESS_TOKEN, or TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET; use --offline for the bundled catalog."
            )
        if not token:
            token = app_access_token(client_id, secret)
        live = collect_channel_videos(channel, client_id=client_id, token=token)

    payload = merge_catalog(args.pack, live, channel=channel)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "videos": len(payload["videos"]), "live": len(live)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
