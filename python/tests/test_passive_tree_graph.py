# -*- coding: utf-8 -*-
"""Passive tree graph/pathing tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passive_tree_graph import PassiveTreeGraph, load_default_tree_graph  # noqa: E402


def _node(name: str, out: list[str], **extra):
    return {"skill": name, "name": name, "out": out, **extra}


def test_shortest_path_matches_frontend_semantics():
    graph = PassiveTreeGraph({
        "nodes": {
            "1": _node("1", ["2", "3"], classStartIndex=0),
            "2": _node("2", ["4"]),
            "3": _node("3", ["4", "5"]),
            "4": _node("4", ["6"]),
            "5": _node("5", []),
            "6": _node("6", []),
        }
    })

    assert graph.shortest_path(["1"], "1") == ["1"]
    assert graph.shortest_path(["1"], "6") == ["2", "4", "6"]
    assert graph.shortest_path(["1", "4"], "6") == ["6"]
    assert graph.shortest_path(["1"], "99") == []
    assert graph.path_cost(["1"], "6") == 3
    assert graph.path_cost(["1"], "1") == 0


def test_connectivity_summary_detects_orphaned_allocations():
    graph = PassiveTreeGraph({
        "nodes": {
            "S": _node("S", ["A"], classStartIndex=0),
            "A": _node("A", ["B"]),
            "B": _node("B", []),
            "X": _node("X", ["Y"]),
            "Y": _node("Y", []),
        }
    })

    summary = graph.connectivity_summary(["A", "B", "X"], class_index=0)

    assert summary["class_start_id"] == "S"
    assert summary["connected_allocated_count"] == 2
    assert summary["orphaned_allocated_node_ids"] == ["X"]
    assert summary["connectivity_status"] == "has_orphaned_allocations"


def test_real_reliquarian_graph_path_from_scion_start_to_armour_display():
    graph = load_default_tree_graph()

    path = graph.shortest_path(["58833"], "36489")

    assert path == ["10108", "35936", "22441", "36489"]
    assert graph.path_cost(["58833"], "36489") == 4
    assert graph.node_summary("36489")["name"] == "Armour Display"
    assert graph.node_summary("36489")["ascendancy_name"] == "Reliquarian"
