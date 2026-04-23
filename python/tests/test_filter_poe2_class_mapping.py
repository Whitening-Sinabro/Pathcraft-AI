"""POE2 필터 생성 시 ItemClass 매핑이 NeverSink POE2 ground truth 와 일치하는지 검증.

D5 2단계: sections_continue.py 가 game="poe2" 인자에 따라 Shields/Bucklers 분할·
Warstaves→Quarterstaves rename·미릴리스 클래스(Claws/Daggers/One Hand Axes 등) drop 을
정확히 반영하는지 확인.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python"))

from sections_continue import (  # noqa: E402
    _map_poe1_classes,
    _equip_classes_for,
    _rare_equip_exact_for,
    _endgame_rare_equip_for,
    _endgame_rare_noimpl_for,
    _droplevel_hide_for,
    generate_beta_overlay,
    layer_progressive_hide,
    layer_endgame_rare,
    layer_endgame_rare_hide,
    layer_re_show,
)


# ---------------------------------------------------------------------------
# 저수준 매핑 헬퍼
# ---------------------------------------------------------------------------

def test_map_poe1_classes_poe1_is_identity():
    src = ("Shields", "Warstaves", "Claws")
    assert _map_poe1_classes(src, "poe1") == list(src)


def test_map_poe1_classes_rejects_unknown_game():
    import pytest
    with pytest.raises(ValueError):
        _map_poe1_classes(("Shields",), "poe3")


def test_map_poe1_shields_split_to_shields_and_bucklers():
    out = _map_poe1_classes(("Shields",), "poe2")
    assert out == ["Shields", "Bucklers"]


def test_map_poe1_warstaves_renamed_to_quarterstaves():
    assert _map_poe1_classes(("Warstaves",), "poe2") == ["Quarterstaves"]


def test_map_poe1_claws_daggers_dropped_in_poe2():
    out = _map_poe1_classes(("Claws", "Daggers", "Rune Daggers"), "poe2")
    assert out == []


def test_map_poe1_one_hand_axes_and_swords_dropped_in_poe2():
    out = _map_poe1_classes((
        "One Hand Axes", "One Hand Swords", "Thrusting One Hand Swords",
        "Two Hand Axes", "Two Hand Swords",
    ), "poe2")
    assert out == []


def test_map_poe1_preserves_one_hand_maces_and_two_hand_maces():
    out = _map_poe1_classes(("One Hand Maces", "Two Hand Maces"), "poe2")
    assert out == ["One Hand Maces", "Two Hand Maces"]


def test_map_poe1_dedupes_when_two_poe1_classes_map_to_same_poe2():
    # POE1 Shields 는 POE2 에서 Shields+Bucklers. 같은 리스트에 여러 번 들어가도 순서 보존 dedup.
    out = _map_poe1_classes(("Shields", "Shields"), "poe2")
    assert out == ["Shields", "Bucklers"]


# ---------------------------------------------------------------------------
# 상위 헬퍼 문자열 출력
# ---------------------------------------------------------------------------

def test_equip_classes_poe1_includes_warstaves_and_claws():
    s = _equip_classes_for("poe1")
    assert '"Warstaves"' in s
    assert '"Claws"' in s
    assert '"Shields"' in s
    assert '"Bucklers"' not in s
    assert '"Quarterstaves"' not in s


def test_equip_classes_poe2_has_bucklers_quarterstaves_no_claws():
    s = _equip_classes_for("poe2")
    assert '"Bucklers"' in s
    assert '"Quarterstaves"' in s
    assert '"Shields"' in s  # Shields 는 유지
    assert '"Claws"' not in s
    assert '"Daggers"' not in s
    assert '"Warstaves"' not in s
    assert '"One Hand Axes"' not in s
    assert '"Two Hand Swords"' not in s


def test_rare_equip_exact_poe2_prefix_and_contents():
    s = _rare_equip_exact_for("poe2")
    assert s.startswith("Class == ")
    assert '"Bucklers"' in s
    assert '"Quarterstaves"' in s
    assert '"Claws"' not in s


def test_endgame_rare_equip_poe2_no_class_prefix():
    s = _endgame_rare_equip_for("poe2")
    assert not s.startswith("Class")
    assert '"Bucklers"' in s
    assert '"Amulets"' in s
    assert '"Rings"' in s
    assert '"Belts"' in s


def test_endgame_rare_noimpl_poe2_excludes_amulets_belts_rings():
    s = _endgame_rare_noimpl_for("poe2")
    assert '"Amulets"' not in s
    assert '"Belts"' not in s
    assert '"Rings"' not in s
    # 본체 장비는 포함
    assert '"Body Armours"' in s
    assert '"Bucklers"' in s
    assert '"Quarterstaves"' in s


def test_droplevel_hide_poe2_identical_to_poe1():
    # Body Armours/Boots/Gloves/Helmets 는 POE1/POE2 공통
    assert _droplevel_hide_for("poe1") == _droplevel_hide_for("poe2")
    assert _droplevel_hide_for("poe2") == '"Body Armours" "Boots" "Gloves" "Helmets"'


# ---------------------------------------------------------------------------
# End-to-end 오버레이
# ---------------------------------------------------------------------------

def test_generate_overlay_rejects_unknown_game():
    import pytest
    with pytest.raises(ValueError):
        generate_beta_overlay(strictness=3, game="poe3")


def test_generate_overlay_poe1_default_unchanged():
    # game 기본값이 POE1 이고, 명시적 game="poe1" 과 동일 출력 — regression guard.
    a = generate_beta_overlay(strictness=3)
    b = generate_beta_overlay(strictness=3, game="poe1")
    assert a == b


def test_generate_overlay_poe2_has_poe2_class_names():
    out = generate_beta_overlay(strictness=3, game="poe2")
    assert '"Bucklers"' in out
    assert '"Quarterstaves"' in out


def test_scoped_layers_drop_poe1_only_classes_in_poe2():
    """D5 2단계 스코프: layer_progressive_hide / layer_endgame_rare /
    layer_endgame_rare_hide / layer_re_show 4 레이어가 POE2 모드에서
    POE1-only 클래스를 Class 조건에 누수시키지 않는지.

    (id_mod_filtering / heist / flasks_quality / uniques 등 POE1 native
    데이터 의존 레이어는 D7 스코프로 이월.)
    """
    poe1_only = ('"Claws"', '"Daggers"', '"Rune Daggers"',
                 '"One Hand Axes"', '"One Hand Swords"',
                 '"Thrusting One Hand Swords"',
                 '"Two Hand Axes"', '"Two Hand Swords"',
                 '"Warstaves"', '"Hybrid Flasks"')
    layer_calls = (
        ("progressive_hide", layer_progressive_hide(3, game="poe2")),
        ("endgame_rare", layer_endgame_rare(game="poe2")),
        ("endgame_rare_hide", layer_endgame_rare_hide(game="poe2")),
        ("re_show", layer_re_show(game="poe2")),
    )
    for name, out in layer_calls:
        for line in out.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("Class"):
                for cls in poe1_only:
                    assert cls not in line, (
                        f"layer_{name} POE2 에서 POE1-only {cls} 누수: {line!r}"
                    )


def test_generate_overlay_poe2_shields_and_bucklers_coexist():
    """POE2 쉴드 블록은 Shields 와 Bucklers 두 이름을 모두 나열해야 한다."""
    out = generate_beta_overlay(strictness=3, game="poe2")
    # 적어도 한 Class 라인에 둘 다 나와야 한다.
    coexist = False
    for line in out.splitlines():
        if '"Shields"' in line and '"Bucklers"' in line and line.lstrip().startswith("Class"):
            coexist = True
            break
    assert coexist, "POE2 Shields/Bucklers 동시 나열 Class 라인 없음"


def test_generate_overlay_poe2_t1_melee_block_uses_poe2_maces():
    """POE1 T1 melee 는 Claws/Daggers/O1Axes 등이었음. POE2 매핑 후 One Hand Maces·
    Two Hand Maces·Quarterstaves 로 축소되어야 한다."""
    out = generate_beta_overlay(strictness=3, game="poe2")
    # [rare_t1_melee] 카테고리 태그 찾기
    lines = out.splitlines()
    t1_melee_idx = None
    for i, ln in enumerate(lines):
        if "rare_t1_melee" in ln:
            t1_melee_idx = i
            break
    assert t1_melee_idx is not None, "POE2 에서 rare_t1_melee 블록 발견 못함"
    # 해당 블록의 Class 라인 검증
    block = "\n".join(lines[t1_melee_idx:t1_melee_idx + 8])
    assert '"One Hand Maces"' in block
    assert '"Two Hand Maces"' in block
    assert '"Quarterstaves"' in block
    assert '"Claws"' not in block
    assert '"Daggers"' not in block


def test_generate_overlay_poe2_no_empty_class_condition():
    """매핑 결과가 빈 리스트인 블록은 생성 자체를 skip 해야 한다.
    'Class == ' (뒤 값 없음) 같은 오염된 조건이 없어야 한다."""
    out = generate_beta_overlay(strictness=3, game="poe2")
    for line in out.splitlines():
        stripped = line.strip()
        assert stripped != "Class ==", "빈 Class == 조건 발견"
        assert stripped != "Class", "빈 Class 조건 발견"
