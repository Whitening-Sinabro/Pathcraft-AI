"""poe2_filter_eval 파서/매처 — 스윕이 '무음'·'안 걸림'으로 오판하던 조건들.

스윕은 이 평가기로 우리 필터와 NeverSink 를 비교한다. 여기서 소리나 조건을 못 읽으면
스윕이 거짓 회귀를 내거나(커스텀 소리 블록이 전부 무음으로 보임) 블록을 영영 못 맞춘다.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def ev():
    spec = importlib.util.spec_from_file_location(
        "poe2_filter_eval", REPO_ROOT / "scripts" / "poe2_filter_eval.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _one(ev, body: str):
    blocks = ev.parse("Show\n" + body + "\n")
    assert len(blocks) == 1
    return blocks[0]


class TestCustomAlertSound:
    def test_volume_is_the_token_after_the_quoted_file(self, ev):
        block = _one(ev, '\tBaseType == "Gold Ring"\n\tCustomAlertSound "POE2 Whetstones.mp3" 300')
        assert block.volume == 300

    def test_missing_volume_defaults_to_100(self, ev):
        block = _one(ev, '\tBaseType == "Gold Ring"\n\tCustomAlertSound "ring.mp3"')
        assert block.volume == 100

    def test_custom_sound_block_is_not_silent_in_evaluation(self, ev):
        blocks = ev.parse('Show\n\tBaseType == "Gold Ring"\n\tCustomAlertSound "ring.mp3" 250\n')
        assert ev.evaluate(blocks, ev.Item(base_type="Gold Ring")).volume == 250


class TestDropLevel:
    def test_drop_level_condition_uses_the_base_unlock_level(self, ev):
        block = _one(ev, "\tDropLevel >= 60")
        assert not block.unmodelled
        assert ev.matches(block, ev.Item(base_type="x", drop_level=65))
        assert not ev.matches(block, ev.Item(base_type="x", drop_level=1))


class TestAlwaysShow:
    def test_always_show_true_does_not_match_a_plain_drop(self, ev):
        block = _one(ev, "\tAlwaysShow True")
        assert not ev.matches(block, ev.Item(base_type="x"))
        assert ev.matches(block, ev.Item(base_type="x", always_show=True))

    def test_always_show_false_matches_a_plain_drop(self, ev):
        block = _one(ev, "\tAlwaysShow False")
        assert ev.matches(block, ev.Item(base_type="x"))
        assert not ev.matches(block, ev.Item(base_type="x", always_show=True))
