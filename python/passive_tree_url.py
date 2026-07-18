# -*- coding: utf-8 -*-
"""POE official passive tree URL decoder."""

from __future__ import annotations

import base64
import re
import struct
from typing import Any, Optional

TREE_TOKEN_RE = re.compile(r"(?:fullscreen-)?passive-skill-tree/([A-Za-z0-9_-]+)")
RAW_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def extract_tree_token(url_or_token: str) -> Optional[str]:
    """Extract the base64url passive tree token from a URL or raw token."""
    trimmed = str(url_or_token or "").strip()
    if not trimmed:
        return None
    match = TREE_TOKEN_RE.search(trimmed)
    if match:
        return match.group(1)
    if RAW_TOKEN_RE.match(trimmed):
        return trimmed
    return None


def _base64url_decode(token: str) -> bytes:
    padding = "=" * ((4 - len(token) % 4) % 4)
    return base64.urlsafe_b64decode((token + padding).encode("ascii"))


def _read_u16_be(payload: bytes, offset: int) -> tuple[int, int]:
    return struct.unpack_from(">H", payload, offset)[0], offset + 2


def decode_tree_url(url_or_token: str) -> Optional[dict[str, Any]]:
    """Decode an official POE passive-tree URL payload.

    Format reference mirrors `src/utils/passiveTreeUrl.ts`:
    u32 version, u8 class, u8 ascendancy, u8 fullscreen, u8 node count,
    u16 node ids, optional cluster nodes for v5+, optional mastery effects for
    v6+ as (effectId u16, nodeId u16).
    """
    token = extract_tree_token(url_or_token)
    if not token:
        return None
    try:
        payload = _base64url_decode(token)
    except Exception:
        return None
    if len(payload) < 8:
        return None

    version = struct.unpack_from(">I", payload, 0)[0]
    class_index = payload[4]
    ascendancy_index = payload[5]
    fullscreen_flag = payload[6]
    declared_node_count = payload[7]
    offset = 8
    warnings: list[str] = []
    nodes: list[str] = []

    for _ in range(declared_node_count):
        if offset + 2 > len(payload):
            warnings.append("truncated_allocated_nodes")
            break
        node_id, offset = _read_u16_be(payload, offset)
        nodes.append(str(node_id))

    cluster_nodes: list[str] = []
    if version >= 5 and offset < len(payload):
        cluster_count = payload[offset]
        offset += 1
        for _ in range(cluster_count):
            if offset + 2 > len(payload):
                warnings.append("truncated_cluster_nodes")
                break
            node_id, offset = _read_u16_be(payload, offset)
            node = str(node_id)
            cluster_nodes.append(node)
            nodes.append(node)

    mastery_effects: dict[str, str] = {}
    if version >= 6 and offset < len(payload):
        mastery_count = payload[offset]
        offset += 1
        for _ in range(mastery_count):
            if offset + 4 > len(payload):
                warnings.append("truncated_mastery_effects")
                break
            effect_id, offset = _read_u16_be(payload, offset)
            node_id, offset = _read_u16_be(payload, offset)
            mastery_effects[str(node_id)] = str(effect_id)

    if offset < len(payload):
        warnings.append("unused_payload_bytes")

    return {
        "version": version,
        "class_index": class_index,
        "ascendancy_index": ascendancy_index,
        "fullscreen_flag": fullscreen_flag,
        "node_count_declared": declared_node_count,
        "nodes": nodes,
        "cluster_nodes": cluster_nodes,
        "mastery_effects": mastery_effects,
        "decode_warnings": warnings,
    }


__all__ = ["decode_tree_url", "extract_tree_token"]
