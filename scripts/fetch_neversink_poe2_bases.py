"""Fetch and verify the NeverSink POE2 base filters our overlays are built on.

The base filters are third-party and large, so they are not vendored into the
repo -- `.gitignore` excludes `*.filter`. What *is* committed is the pin: the
upstream URL plus a SHA-256 for each file, stored in the build spec under
`_meta.bases`. This script restores the files from that pin.

Why a pin rather than "just download the latest": a NeverSink release changes
the vocabulary our overlays are gated against. If that happened silently, a
BaseType could vanish from the base filter, the vocabulary gate would quietly
drop the rule, and the only symptom would be an item that stops dropping on
screen. A hash mismatch turns that into a loud failure at fetch time.

Usage:
    python scripts/fetch_neversink_poe2_bases.py                # verify + fetch missing
    python scripts/fetch_neversink_poe2_bases.py --force        # re-download everything
    python scripts/fetch_neversink_poe2_bases.py --repin        # accept upstream, rewrite hashes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("neversink-bases")

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = REPO_ROOT / "data" / "filter_build_targets"
SOURCE_DIR = REPO_ROOT / "data" / "filter_sources"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_pins(spec_path: Path) -> tuple[dict, list[dict]]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    pins = spec.get("_meta", {}).get("bases")
    if not pins:
        raise SystemExit(f"{spec_path.name} has no _meta.bases pin block")
    return spec, pins


def download(url: str) -> bytes:
    log.info("GET %s", url)
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--spec",
        default=str(SPEC_DIR / "poe2_fartfinder_skadoosh_0_5_5.json"),
        help="build spec carrying the _meta.bases pin block",
    )
    ap.add_argument("--force", action="store_true", help="re-download even if the file is present")
    ap.add_argument(
        "--repin",
        action="store_true",
        help="accept whatever upstream serves now and rewrite the pinned hashes",
    )
    args = ap.parse_args()

    spec_path = Path(args.spec)
    spec, pins = load_pins(spec_path)

    failures: list[str] = []
    repinned = 0
    for pin in pins:
        dest = SOURCE_DIR / pin["file"]
        have = dest.read_bytes() if dest.exists() else None

        if have is not None and not args.force and not args.repin:
            actual = sha256(have)
            if actual == pin["sha256"]:
                log.info("ok   %-32s %s", pin["file"], actual[:12])
            else:
                failures.append(
                    f"{pin['file']}: on-disk sha256 {actual[:12]} != pinned {pin['sha256'][:12]}"
                )
            continue

        data = download(pin["url"])
        actual = sha256(data)
        if args.repin:
            if actual != pin["sha256"]:
                log.warning("repin %-30s %s -> %s", pin["file"], pin["sha256"][:12], actual[:12])
                pin["sha256"] = actual
                pin["bytes"] = len(data)
                repinned += 1
            dest.write_bytes(data)
            continue
        if actual != pin["sha256"]:
            failures.append(
                f"{pin['file']}: upstream sha256 {actual[:12]} != pinned {pin['sha256'][:12]} "
                f"-- NeverSink probably shipped a new release; re-verify the vocabulary, "
                f"then run with --repin"
            )
            continue
        dest.write_bytes(data)
        log.info("wrote %-31s %d bytes", pin["file"], len(data))

    if repinned:
        spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        log.warning("re-pinned %d base(s) in %s -- regenerate every filter now", repinned, spec_path.name)

    for f in failures:
        log.error(f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
