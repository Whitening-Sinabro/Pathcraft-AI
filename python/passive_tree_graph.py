# -*- coding: utf-8 -*-
"""Passive tree graph/pathing helpers for POE1 skilltree export."""

from __future__ import annotations

import json
from collections import deque
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Optional

from ggpk_index import DATA_ROOT


DEFAULT_TREE_PATH = DATA_ROOT / "skilltree-export" / "data.json"


class PassiveTreeGraph:
    """Undirected graph over GGG passive tree export nodes."""

    def __init__(self, tree_data: dict[str, Any]):
        self.tree_data = tree_data
        self.nodes: dict[str, dict[str, Any]] = {
            str(node_id): node
            for node_id, node in (tree_data.get("nodes") or {}).items()
            if isinstance(node, dict)
        }
        self.class_start_ids = self._build_class_start_ids()
        self.adjacency = self._build_adjacency(set(self.nodes))

    @classmethod
    def from_path(cls, path: Path = DEFAULT_TREE_PATH) -> "PassiveTreeGraph":
        with path.open("r", encoding="utf-8") as f:
            return cls(json.load(f))

    def _build_class_start_ids(self) -> dict[int, str]:
        starts: dict[int, str] = {}
        for node_id, node in self.nodes.items():
            class_index = node.get("classStartIndex")
            if isinstance(class_index, int):
                starts[class_index] = node_id
        return starts

    def _build_adjacency(self, allowed_ids: set[str]) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {}

        def push(a: str, b: str) -> None:
            adjacency.setdefault(a, [])
            if b not in adjacency[a]:
                adjacency[a].append(b)

        for node_id in allowed_ids:
            node = self.nodes.get(node_id)
            if not node:
                continue
            for target in node.get("out") or []:
                target_id = str(target)
                if target_id not in allowed_ids:
                    continue
                push(node_id, target_id)
                push(target_id, node_id)
        return adjacency

    def shortest_path(
        self,
        from_ids: Iterable[str | int],
        target_id: str | int,
        *,
        allowed_ids: Optional[set[str]] = None,
    ) -> list[str]:
        """Shortest path from any start to target.

        Return path excludes already-owned start nodes and includes the target,
        matching the TS `shortestPath` helper used by the UI.
        """
        target = str(target_id)
        starts = {str(node_id) for node_id in from_ids if str(node_id) in self.nodes}
        if not starts or target not in self.nodes:
            return []
        if target in starts:
            return [target]

        adjacency = self.adjacency
        if allowed_ids is not None:
            adjacency = self._build_adjacency(allowed_ids)

        previous: dict[str, str] = {}
        visited = set(starts)
        queue: deque[str] = deque(starts)
        while queue:
            current = queue.popleft()
            for neighbor in adjacency.get(current, []):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                previous[neighbor] = current
                if neighbor == target:
                    path: list[str] = []
                    cursor: Optional[str] = target
                    while cursor and cursor not in starts:
                        path.append(cursor)
                        cursor = previous.get(cursor)
                    path.reverse()
                    return path
                queue.append(neighbor)
        return []

    def path_cost(self, from_ids: Iterable[str | int], target_id: str | int) -> Optional[int]:
        path = self.shortest_path(from_ids, target_id)
        if not path:
            return None
        if len(path) == 1 and path[0] in {str(node_id) for node_id in from_ids}:
            return 0
        return len(path)

    def connectivity_summary(
        self,
        allocated_node_ids: Iterable[str | int],
        *,
        class_index: Optional[int] = None,
    ) -> dict[str, Any]:
        allocated = {str(node_id) for node_id in allocated_node_ids if str(node_id) in self.nodes}
        anchor = self.class_start_ids.get(class_index) if class_index is not None else None
        anchors = {anchor} if anchor else set()
        graph_nodes = allocated | anchors
        adjacency = self._build_adjacency(graph_nodes)

        reachable: set[str] = set()
        queue: deque[str] = deque()
        for node_id in anchors:
            if node_id in graph_nodes:
                reachable.add(node_id)
                queue.append(node_id)

        while queue:
            current = queue.popleft()
            for neighbor in adjacency.get(current, []):
                if neighbor in reachable:
                    continue
                reachable.add(neighbor)
                queue.append(neighbor)

        connected_allocated = sorted(allocated & reachable)
        orphaned = sorted(allocated - reachable) if anchors else []
        return {
            "class_index": class_index,
            "class_start_id": anchor,
            "allocated_count": len(allocated),
            "connected_allocated_count": len(connected_allocated),
            "orphaned_allocated_count": len(orphaned),
            "orphaned_allocated_node_ids": orphaned,
            "connectivity_status": (
                "no_class_anchor"
                if not anchors
                else "connected"
                if not orphaned
                else "has_orphaned_allocations"
            ),
        }

    def node_summary(self, node_id: str | int) -> Optional[dict[str, Any]]:
        node = self.nodes.get(str(node_id))
        if not node:
            return None
        return {
            "node_id": str(node_id),
            "name": node.get("name"),
            "is_notable": bool(node.get("isNotable")),
            "is_keystone": bool(node.get("isKeystone")),
            "is_jewel_socket": bool(node.get("isJewelSocket")),
            "is_mastery": bool(node.get("isMastery")),
            "ascendancy_name": node.get("ascendancyName"),
            "class_start_index": node.get("classStartIndex"),
        }


@lru_cache(maxsize=1)
def load_default_tree_graph() -> PassiveTreeGraph:
    return PassiveTreeGraph.from_path(DEFAULT_TREE_PATH)


__all__ = ["PassiveTreeGraph", "load_default_tree_graph"]
