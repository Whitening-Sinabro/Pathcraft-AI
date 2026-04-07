# -*- coding: utf-8 -*-
"""build_coach 핵심 함수 스모크 테스트 (LLM 호출 없이)"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from build_coach import detect_archetype, load_archetype_data, load_quest_rewards


class TestDetectArchetype:
    """detect_archetype: 빌드 데이터 → 아키타입 분류"""

    def _make_build(self, gem_names: list[str]) -> dict:
        setups = {name: {} for name in gem_names}
        return {"progression_stages": [{"gem_setups": setups}]}

    def test_minion_detection(self):
        build = self._make_build(["Raise Zombie", "Summon Skeletons"])
        assert detect_archetype(build) == "minion"

    def test_dot_detection(self):
        build = self._make_build(["Essence Drain", "Contagion"])
        assert detect_archetype(build) == "dot"

    def test_attack_detection(self):
        build = self._make_build(["Cyclone", "Brutality"])
        assert detect_archetype(build) == "attack"

    def test_spell_fallback(self):
        build = self._make_build(["Arc", "Spell Echo"])
        assert detect_archetype(build) == "spell"

    def test_empty_build_returns_spell(self):
        build = self._make_build([])
        assert detect_archetype(build) == "spell"

    def test_missing_progression_returns_spell(self):
        build = {}
        assert detect_archetype(build) == "spell"


class TestLoadArchetypeData:
    """load_archetype_data: JSON 템플릿 로딩"""

    def test_spell_template_loads(self):
        data = load_archetype_data("spell")
        assert isinstance(data, dict)
        # 비어있지 않아야 함 (파일이 존재하면)
        if data:
            assert len(data) > 0

    def test_nonexistent_archetype_returns_empty(self):
        data = load_archetype_data("nonexistent_type_xyz")
        assert data == {}


class TestLoadQuestRewards:
    """load_quest_rewards: 퀘스트 보상 데이터"""

    def test_loads_without_crash(self):
        data = load_quest_rewards()
        assert isinstance(data, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
