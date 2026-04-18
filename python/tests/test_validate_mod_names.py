"""F0-fix-3 — tier JSON mod 이름이 GGPK Mods에 resolveable한지 검증.

`data/game_data/Mods.json`가 있을 때만 실행 (없으면 skip).
missing (neither exact nor substring match) 시 실패.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python" / "scripts"))

from validate_mod_names import (  # noqa: E402
    DATA_DIR,
    MODS_PATH,
    build_mods_index,
    collect_accessory_mods,
    collect_defense_mods,
    collect_weapon_mods,
    validate_file,
)


@pytest.fixture(scope="module")
def mods_idx():
    if not MODS_PATH.exists():
        pytest.skip(f"{MODS_PATH.relative_to(ROOT)} 없음 — extract_data 먼저")
    import json as _json
    return build_mods_index(_json.loads(MODS_PATH.read_text(encoding="utf-8")))


@pytest.mark.parametrize("label,filename,collector", [
    ("defense",   "defense_mod_tiers.json",   collect_defense_mods),
    ("accessory", "accessory_mod_tiers.json", collect_accessory_mods),
    ("weapon",    "weapon_mod_tiers.json",    collect_weapon_mods),
])
def test_all_mod_names_resolve(label, filename, collector, mods_idx):
    """tier JSON의 모든 mod 이름이 exact 또는 substring으로 GGPK Mods에 존재."""
    report = validate_file(label, DATA_DIR / filename, collector, mods_idx)
    assert report.get("missing", -1) == 0, (
        f"{label}: {report['missing']}개 mod 이름 resolve 불가.\n"
        f"전체: {report}"
    )
