"""Splice the generated divination-card ladder into the single progressive filter.

The ladder replaces the previous single build-target block and lives inside the
Luminary override region, which the rebuild script carries over on regeneration.
Re-running this script is idempotent: an existing ladder is replaced in place.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import List, Sequence

from luminary_divcard_layer import (
    BEGIN_MARKER,
    END_MARKER,
    DivcardLayerError,
    build_ladder_lines,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_FILTER = REPO_ROOT / "filters" / "Luminary_Bot_SSF_3.29_Progressive.filter"
INSTALLED_FILTER = Path(
    r"C:\Users\User\Documents\My Games\Path of Exile\Luminary_Bot_SSF_3.29.filter"
)
DOWNLOAD_FILTER = Path(r"C:\Users\User\Downloads\Luminary_Bot_SSF_3.29.filter")

LEGACY_ANCHOR = "# Primary SSF divination-card farms:"
LEGACY_BLOCK_TITLE = "Show # LUMINARY - TARGET DIVINATION CARDS"


def _find_legacy_span(lines: Sequence[str]) -> tuple[int, int]:
    """Locate the pre-ladder build-target block, comment line included."""
    try:
        title_index = next(
            i for i, line in enumerate(lines) if line.strip() == LEGACY_BLOCK_TITLE
        )
    except StopIteration as exc:
        raise DivcardLayerError("Neither ladder markers nor the legacy block were found") from exc
    start = title_index
    while start > 0 and lines[start - 1].startswith("#"):
        start -= 1
    end = title_index
    while end + 1 < len(lines) and lines[end + 1].strip():
        end += 1
    return start, end + 1


def splice(lines: Sequence[str], ladder: Sequence[str]) -> List[str]:
    if BEGIN_MARKER in lines and END_MARKER in lines:
        start = lines.index(BEGIN_MARKER)
        end = lines.index(END_MARKER) + 1
    else:
        start, end = _find_legacy_span(lines)
    return list(lines[:start]) + list(ladder) + list(lines[end:])


def write_filter(path: Path, lines: Sequence[str]) -> str:
    payload = "\r\n".join(lines) + "\r\n"
    path.write_bytes(payload.encode("utf-8"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    original = WORKSPACE_FILTER.read_text(encoding="utf-8").splitlines()
    updated = splice(original, build_ladder_lines())
    logger.info("Filter lines: %d -> %d", len(original), len(updated))
    for target in (WORKSPACE_FILTER, INSTALLED_FILTER, DOWNLOAD_FILTER):
        if not target.parent.exists():
            logger.warning("Skipping missing destination directory: %s", target.parent)
            continue
        digest = write_filter(target, updated)
        logger.info("%s  %s", digest[:16], target)


if __name__ == "__main__":
    main()
