import { describe, it, expect } from "vitest";
import { buildAdjacency, shortestPath, type TreeNode } from "./passiveTree";

function makeNode(id: string, out: string[]): TreeNode {
  return { skill: parseInt(id, 10), name: id, out } as TreeNode;
}

describe("buildAdjacency", () => {
  it("converts one-directional out edges into undirected graph", () => {
    const nodes: Record<string, TreeNode> = {
      "a": makeNode("a", ["b"]),
      "b": makeNode("b", []),
      "c": makeNode("c", ["b"]),
    };
    const adj = buildAdjacency(new Set(["a", "b", "c"]), nodes);
    expect(adj.get("a")).toEqual(["b"]);
    expect(adj.get("b")?.sort()).toEqual(["a", "c"]);
    expect(adj.get("c")).toEqual(["b"]);
  });

  it("skips nodes not in allowed set", () => {
    const nodes: Record<string, TreeNode> = {
      "a": makeNode("a", ["b", "z"]),
      "b": makeNode("b", []),
    };
    const adj = buildAdjacency(new Set(["a", "b"]), nodes);
    expect(adj.get("a")).toEqual(["b"]);
  });
});

describe("shortestPath", () => {
  const nodes: Record<string, TreeNode> = {
    "1": makeNode("1", ["2", "3"]),
    "2": makeNode("2", ["4"]),
    "3": makeNode("3", ["4", "5"]),
    "4": makeNode("4", ["6"]),
    "5": makeNode("5", []),
    "6": makeNode("6", []),
  };
  const adj = buildAdjacency(new Set(["1","2","3","4","5","6"]), nodes);

  it("returns [target] when target already in from-set", () => {
    expect(shortestPath(new Set(["1"]), "1", adj)).toEqual(["1"]);
  });

  it("finds shortest path from single start", () => {
    expect(shortestPath(new Set(["1"]), "6", adj)).toEqual(["2", "4", "6"]);
    // 1→2→4→6 and 1→3→4→6 both length 3; BFS picks first discovered.
  });

  it("uses any node in from-set as start (closest wins)", () => {
    // from includes 4, path to 6 should be [6] (length 1)
    expect(shortestPath(new Set(["1", "4"]), "6", adj)).toEqual(["6"]);
  });

  it("returns [] for unreachable target", () => {
    const smallAdj = buildAdjacency(new Set(["1", "2"]), nodes);
    expect(shortestPath(new Set(["1"]), "6", smallAdj)).toEqual([]);
  });

  it("path excludes nodes already in from-set", () => {
    const result = shortestPath(new Set(["1", "3"]), "5", adj);
    expect(result).toEqual(["5"]);
  });
});
