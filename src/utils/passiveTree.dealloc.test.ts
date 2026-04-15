import { describe, it, expect } from "vitest";
import { buildAdjacency, deallocWithCascade, type TreeNode } from "./passiveTree";

function mk(id: string, out: string[]): TreeNode {
  return { skill: parseInt(id, 10), name: id, out } as TreeNode;
}

// Graph:
//    S (start) — A — B — C
//                |       |
//                D       E
const nodes: Record<string, TreeNode> = {
  S: mk("S", ["A"]),
  A: mk("A", ["B", "D"]),
  B: mk("B", ["C"]),
  C: mk("C", ["E"]),
  D: mk("D", []),
  E: mk("E", []),
};
const adj = buildAdjacency(new Set(["S", "A", "B", "C", "D", "E"]), nodes);

describe("deallocWithCascade", () => {
  it("removes just the target when no downstream gets orphaned", () => {
    const alloc = new Set(["S", "A", "B"]);
    deallocWithCascade("B", alloc, new Set(["S"]), adj);
    expect([...alloc].sort()).toEqual(["A", "S"]);
  });

  it("removes orphaned downstream when middle node is dropped", () => {
    const alloc = new Set(["S", "A", "B", "C", "E"]);
    deallocWithCascade("B", alloc, new Set(["S"]), adj);
    // B gone → C + E also lose path to S
    expect([...alloc].sort()).toEqual(["A", "S"]);
  });

  it("preserves siblings that have independent paths", () => {
    const alloc = new Set(["S", "A", "B", "D"]);
    deallocWithCascade("B", alloc, new Set(["S"]), adj);
    // D still reachable via S→A
    expect([...alloc].sort()).toEqual(["A", "D", "S"]);
  });

  it("does nothing when target not allocated", () => {
    const alloc = new Set(["S", "A"]);
    deallocWithCascade("Z", alloc, new Set(["S"]), adj);
    expect([...alloc].sort()).toEqual(["A", "S"]);
  });

  it("clears everything when anchor itself is removed", () => {
    const alloc = new Set(["S", "A", "B"]);
    deallocWithCascade("S", alloc, new Set(["S"]), adj);
    // S gone → A, B orphaned
    expect([...alloc]).toEqual([]);
  });
});
