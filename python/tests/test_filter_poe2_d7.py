"""POE2 D7 Phase 1 — POE1 native 의존 4레이어 중 3레이어 game 분기 검증.

D7-A: layer_heist(game="poe2") → 빈 반환 (Heist 리그 POE2 미존재)
D7-D: layer_special_uniques(game="poe2") → 빈 반환 (Replica/Foulborn POE2 부재)
D7-B: layer_flasks_quality(game="poe2") → Ultimate Life/Mana Flask + Charm Quality 재설계

Ground truth: NeverSink POE2 필터 0.9.1 실측 ([[0800]] Endgame Flasks,
[[0900]] Endgame Charms, Trinket/Blueprint/Contract/Replica/Foulborn 0건).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python"))

from sections_continue import (  # noqa: E402
    generate_beta_overlay,
    layer_flasks_quality,
    layer_heist,
    layer_id_mod_filtering,
    layer_special_uniques,
)


class TestLayerHeistGameBranch:
    def test_heist_poe2_empty(self):
        assert layer_heist(mode="ssf", game="poe2") == ""

    def test_heist_poe1_regression(self):
        text = layer_heist(mode="ssf", game="poe1")
        for tag in ("heist_blueprint", "heist_contract", "heist_trinket",
                    "heist_blueprint_handpicked", "heist_contract_handpicked",
                    "heist_rogue_marker", "wombgifts"):
            assert f"[L8|{tag}]" in text, f"POE1 {tag} 블록 회귀 누락"


class TestLayerSpecialUniquesGameBranch:
    def test_special_uniques_poe2_empty(self):
        assert layer_special_uniques(mode="ssf", game="poe2") == ""

    def test_special_uniques_poe1_regression(self):
        text = layer_special_uniques(mode="ssf", game="poe1")
        assert "Replica True" in text
        assert "Foulborn True" in text
        assert "[L8|unique_replica]" in text
        assert "[L8|unique_foulborn]" in text


class TestLayerFlasksQualityPoe2:
    def test_poe2_ultimate_flask_top_quality(self):
        """Ultimate Life/Mana Flask Q11+ 블록 — NeverSink [[0800]] 대응."""
        text = layer_flasks_quality(mode="ssf", game="poe2")
        assert '"Ultimate Life Flask"' in text
        assert '"Ultimate Mana Flask"' in text
        assert "Quality > 10" in text
        assert "ItemLevel >= 83" in text
        assert "AreaLevel >= 65" in text
        assert "[L8|poe2_flask_ultimate_quality]" in text

    def test_poe2_ultimate_flask_baseline(self):
        """Ultimate Flask baseline (no Quality) 블록."""
        text = layer_flasks_quality(mode="ssf", game="poe2")
        assert "[L8|poe2_flask_ultimate_baseline]" in text

    def test_poe2_charm_quality(self):
        """Charm Q18+ 블록 — POE1 Utility Flask 대체, NeverSink [[0900]]."""
        text = layer_flasks_quality(mode="ssf", game="poe2")
        assert 'Class == "Charms"' in text
        assert "Quality >= 18" in text
        assert "ItemLevel >= 82" in text
        assert "[L8|poe2_charm_quality]" in text

    def test_poe2_no_poe1_only_classes(self):
        """POE2 블록에 POE1 전용 Class 이름 누수 없음."""
        text = layer_flasks_quality(mode="ssf", game="poe2")
        assert '"Utility Flasks"' not in text, "POE2 에는 Utility Flasks 없음"
        assert 'Class "Flasks"' not in text, "POE2 는 Class == Flasks 사용 안 함"

    def test_poe1_regression(self):
        """POE1 기존 Q10/Q20/Q21 블록 유지."""
        text = layer_flasks_quality(mode="ssf", game="poe1")
        for q in (10, 20, 21):
            assert f"Quality >= {q}" in text
        assert '[L8|utility_flask]' in text
        assert 'Class "Flasks"' in text


class TestLayerIdModFilteringGameBranch:
    """D7-C Phase 1 임시 skip — Phase 2 에서 POE2 Recombinator Mods 데이터로 대체."""

    def test_id_mod_poe2_empty(self):
        assert layer_id_mod_filtering(mode="ssf", strictness=0, game="poe2") == ""
        assert layer_id_mod_filtering(mode="ssf", strictness=3, game="poe2") == ""

    def test_id_mod_poe1_regression(self):
        text = layer_id_mod_filtering(mode="ssf", strictness=0, game="poe1")
        assert "Identified True" in text
        assert "HasExplicitMod" in text
        assert "[L8|id_mod_" in text


class TestOverlayE2EPoe2:
    """generate_beta_overlay(game="poe2") 전체 출력 누수 검증."""

    @staticmethod
    def _overlay_poe2() -> str:
        build_data = {
            "character_class": "Witch",
            "ascendancy": "Occultist",
            "main_skill": {"name": "Fireball"},
            "support_gems": [],
        }
        return generate_beta_overlay(
            strictness=3, build_data=build_data, mode="ssf", game="poe2",
        )

    def test_overlay_poe2_no_heist_keywords(self):
        text = self._overlay_poe2()
        for kw in ("Blueprints", "Contracts", "Trinkets", "Wombgifts",
                   "Rogue's Marker"):
            assert kw not in text, f"POE2 overlay 에 POE1-only {kw} 누수"

    def test_overlay_poe2_no_replica_foulborn(self):
        text = self._overlay_poe2()
        assert "Replica True" not in text
        assert "Foulborn True" not in text

    def test_overlay_poe2_has_d7b_blocks(self):
        text = self._overlay_poe2()
        assert "Ultimate Life Flask" in text
        assert "Ultimate Mana Flask" in text
        assert 'Class == "Charms"' in text

    def test_overlay_poe2_no_poe1_only_classes_leak(self):
        """POE2 overlay 에 POE1 전용 ItemClass (Claws/Daggers/Warstaves 등) 누수 부재.

        D7-C Phase 1 임시 skip 이 layer_id_mod_filtering 경유 누수를 막는지 검증.
        """
        text = self._overlay_poe2()
        for kw in ("Claws", "Daggers", "Warstaves", "Rune Daggers",
                   "Thrusting One Hand Swords"):
            assert kw not in text, f"POE2 overlay 에 POE1-only {kw} 누수"
