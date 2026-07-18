# -*- coding: utf-8 -*-
"""Passive tree URL decoder tests."""

from __future__ import annotations

import base64
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passive_tree_url import decode_tree_url, extract_tree_token  # noqa: E402


def make_synthetic_token(
    node_ids: list[int],
    *,
    version: int = 6,
    class_index: int = 5,
    ascendancy_index: int = 2,
    mastery_effects: dict[int, int] | None = None,
) -> str:
    mastery_effects = mastery_effects or {}
    payload = bytearray()
    payload.extend(struct.pack(">I", version))
    payload.extend(bytes([class_index, ascendancy_index, 0, len(node_ids)]))
    for node_id in node_ids:
        payload.extend(struct.pack(">H", node_id))
    if version >= 5:
        payload.append(0)
    if version >= 6:
        payload.append(len(mastery_effects))
        for node_id, effect_id in mastery_effects.items():
            payload.extend(struct.pack(">H", effect_id))
            payload.extend(struct.pack(">H", node_id))
    return base64.urlsafe_b64encode(bytes(payload)).decode("ascii").rstrip("=")


def test_extract_tree_token_accepts_urls_and_raw_tokens():
    assert extract_tree_token("https://www.pathofexile.com/passive-skill-tree/ABCDEF_-") == "ABCDEF_-"
    assert extract_tree_token("https://www.pathofexile.com/fullscreen-passive-skill-tree/XYZ") == "XYZ"
    assert extract_tree_token("AAAA_BBB-123") == "AAAA_BBB-123"
    assert extract_tree_token("not a url with spaces") is None


def test_decode_tree_url_reads_nodes_and_mastery_effects():
    token = make_synthetic_token([17765, 12345], mastery_effects={12345: 678})
    decoded = decode_tree_url(token)

    assert decoded is not None
    assert decoded["version"] == 6
    assert decoded["class_index"] == 5
    assert decoded["ascendancy_index"] == 2
    assert decoded["nodes"] == ["17765", "12345"]
    assert decoded["mastery_effects"] == {"12345": "678"}
    assert decoded["decode_warnings"] == []


def test_decode_tree_url_accepts_full_url_and_rejects_garbage():
    token = make_synthetic_token([100, 200])
    decoded = decode_tree_url("https://www.pathofexile.com/passive-skill-tree/" + token)

    assert decoded is not None
    assert decoded["nodes"] == ["100", "200"]
    assert decode_tree_url("") is None
    assert decode_tree_url("not base64!!!") is None
    assert decode_tree_url(base64.urlsafe_b64encode(b"abc").decode("ascii").rstrip("=")) is None
