# -*- coding: utf-8 -*-
"""Operational status for fast PoE1 3.29 information intake."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "data" / "poe1_3_29_information_intake_plan.json"
STATUS_PATH = ROOT / "data" / "poe1_3_29_information_intake_status.latest.json"


def load_plan(path: Path = PLAN_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_minutes(cadence: str) -> int | None:
    """Extract the first minute cadence from text like '15m first 48h'."""
    import re

    match = re.search(r"(\d+)\s*m", cadence.lower())
    if not match:
        return None
    return int(match.group(1))


def _path_age_minutes(path: Path, now: datetime) -> float | None:
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return max(0.0, (now - mtime).total_seconds() / 60.0)


def build_intake_status(plan: dict[str, Any] | None = None, now: datetime | None = None) -> dict[str, Any]:
    plan = plan or load_plan()
    now = now or datetime.now(timezone.utc)
    tracks = []

    for track in plan.get("intake_tracks", []):
        rel_path = track.get("last_success_path", "")
        path = ROOT / rel_path if rel_path else ROOT
        age = _path_age_minutes(path, now)
        target = _parse_minutes(track.get("cadence", "")) or _parse_minutes(
            f"{plan.get('latency_targets', {}).get(track.get('id') + '_minutes', '')}m"
        )

        if age is None:
            freshness = "missing"
        elif target is None:
            freshness = "present_unbounded"
        elif age <= target:
            freshness = "fresh"
        elif age <= target * 3:
            freshness = "stale"
        else:
            freshness = "overdue"

        tracks.append({
            "id": track.get("id"),
            "tier": track.get("tier"),
            "family": track.get("family"),
            "freshness": freshness,
            "age_minutes": None if age is None else round(age, 2),
            "target_minutes": target,
            "last_success_path": rel_path,
            "command": track.get("command"),
            "promotion_power": track.get("promotion_power"),
        })

    summary = {
        "track_count": len(tracks),
        "fresh": sum(1 for row in tracks if row["freshness"] == "fresh"),
        "stale": sum(1 for row in tracks if row["freshness"] == "stale"),
        "overdue": sum(1 for row in tracks if row["freshness"] == "overdue"),
        "missing": sum(1 for row in tracks if row["freshness"] == "missing"),
    }

    return {
        "dataset_kind": "poe1_3_29_information_intake_status",
        "generated_at": now.isoformat(),
        "plan_path": str(PLAN_PATH.relative_to(ROOT)).replace("\\", "/"),
        "patch": plan.get("patch"),
        "league": plan.get("league"),
        "summary": summary,
        "tracks": tracks,
        "fastlane_commands": plan.get("fastlane_commands", []),
        "promotion_gates": plan.get("promotion_gates", []),
    }


def write_status(path: Path = STATUS_PATH) -> dict[str, Any]:
    status = build_intake_status()
    path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check PoE1 3.29 information intake freshness.")
    parser.add_argument("--status", action="store_true", help="Print current freshness status.")
    parser.add_argument("--write-status", action="store_true", help="Write status JSON to data/.")
    parser.add_argument("--commands", action="store_true", help="Print fastlane commands only.")
    args = parser.parse_args(argv)

    if args.commands:
        plan = load_plan()
        print(json.dumps(plan.get("fastlane_commands", []), ensure_ascii=False, indent=2))
        return 0

    if args.write_status:
        print(json.dumps(write_status(), ensure_ascii=False, indent=2))
        return 0

    if args.status or not any(vars(args).values()):
        print(json.dumps(build_intake_status(), ensure_ascii=False, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
