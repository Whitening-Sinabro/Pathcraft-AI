import { describe, it, expect } from "vitest";
import {
  nodeAngleDeg,
  nodePosition,
  normalizePoe2Tree,
  buildAdjacency,
  type TreeConstants,
  type Poe2RawTree,
} from "./passiveTree";

const constants: TreeConstants = {
  PSSCentreInnerRadius: 130,
  skillsPerOrbit: [1, 6, 16, 16, 40, 72, 72],
  orbitRadii: [0, 82, 162, 335, 493, 662, 846],
};

describe("nodeAngleDeg", () => {
  it("orbit 0 always at 0deg", () => {
    expect(nodeAngleDeg(0, 0, constants.skillsPerOrbit)).toBe(0);
  });

  it("orbit 1 (6 slots): even 60deg spacing", () => {
    expect(nodeAngleDeg(1, 0, constants.skillsPerOrbit)).toBe(0);
    expect(nodeAngleDeg(1, 1, constants.skillsPerOrbit)).toBe(60);
    expect(nodeAngleDeg(1, 3, constants.skillsPerOrbit)).toBe(180);
    expect(nodeAngleDeg(1, 5, constants.skillsPerOrbit)).toBe(300);
  });

  it("orbit 2 (16 slots): custom angle table from 3.17", () => {
    expect(nodeAngleDeg(2, 0, constants.skillsPerOrbit)).toBe(0);
    expect(nodeAngleDeg(2, 2, constants.skillsPerOrbit)).toBe(45);
    expect(nodeAngleDeg(2, 6, constants.skillsPerOrbit)).toBe(135);
    expect(nodeAngleDeg(2, 10, constants.skillsPerOrbit)).toBe(225);
    expect(nodeAngleDeg(2, 14, constants.skillsPerOrbit)).toBe(315);
  });

  it("orbit 3 uses same 16-slot table as orbit 2", () => {
    for (let i = 0; i < 16; i++) {
      expect(nodeAngleDeg(3, i, constants.skillsPerOrbit)).toBe(
        nodeAngleDeg(2, i, constants.skillsPerOrbit),
      );
    }
  });

  it("orbit 4 (40 slots): even 9deg spacing", () => {
    expect(nodeAngleDeg(4, 0, constants.skillsPerOrbit)).toBe(0);
    expect(nodeAngleDeg(4, 10, constants.skillsPerOrbit)).toBe(90);
    expect(nodeAngleDeg(4, 20, constants.skillsPerOrbit)).toBe(180);
  });

  it("orbit 5/6 (72 slots): even 5deg spacing", () => {
    expect(nodeAngleDeg(5, 0, constants.skillsPerOrbit)).toBe(0);
    expect(nodeAngleDeg(5, 18, constants.skillsPerOrbit)).toBe(90);
    expect(nodeAngleDeg(6, 36, constants.skillsPerOrbit)).toBe(180);
  });

  it("throws for out-of-range orbit", () => {
    expect(() => nodeAngleDeg(7, 0, constants.skillsPerOrbit)).toThrow(RangeError);
    expect(() => nodeAngleDeg(-1, 0, constants.skillsPerOrbit)).toThrow(RangeError);
  });

  it("throws for out-of-range orbitIndex", () => {
    expect(() => nodeAngleDeg(1, 6, constants.skillsPerOrbit)).toThrow(RangeError);
    expect(() => nodeAngleDeg(2, 16, constants.skillsPerOrbit)).toThrow(RangeError);
  });
});

describe("nodePosition", () => {
  const group = { x: 1000, y: 500 };

  it("orbit 0 sits exactly at group center", () => {
    const pos = nodePosition(group, 0, 0, constants);
    expect(pos.x).toBeCloseTo(1000, 6);
    expect(pos.y).toBeCloseTo(500, 6);
  });

  it("orbit 1 index 0 (north): y = group.y - radius", () => {
    const pos = nodePosition(group, 1, 0, constants);
    expect(pos.x).toBeCloseTo(1000, 6);
    expect(pos.y).toBeCloseTo(500 - 82, 6);
  });

  it("orbit 1 index 3 (south): y = group.y + radius", () => {
    const pos = nodePosition(group, 1, 3, constants);
    expect(pos.x).toBeCloseTo(1000, 6);
    expect(pos.y).toBeCloseTo(500 + 82, 6);
  });

  it("orbit 4 index 10 (east): x = group.x + radius", () => {
    const pos = nodePosition(group, 4, 10, constants);
    expect(pos.x).toBeCloseTo(1000 + 493, 6);
    expect(pos.y).toBeCloseTo(500, 6);
  });

  it("orbit 5 index 54 (west): x = group.x - radius", () => {
    const pos = nodePosition(group, 5, 54, constants);
    expect(pos.x).toBeCloseTo(1000 - 662, 6);
    expect(pos.y).toBeCloseTo(500, 6);
  });
});

// ---------------------------------------------------------------------------
// POE2 adapter — normalizePoe2Tree
// ---------------------------------------------------------------------------

const poe2Constants: TreeConstants = {
  PSSCentreInnerRadius: 130,
  skillsPerOrbit: [1, 12, 24, 24, 72, 72, 72, 24, 72, 144],
  orbitRadii: [0, 82, 162, 335, 493, 662, 846, 251, 1080, 1322],
};

function makePoe2Fixture(overrides: Partial<Poe2RawTree> = {}): Poe2RawTree {
  return {
    nodes: {
      "4": {
        skill: 4,
        name: "Shock Chance",
        group: 979,
        orbit: 0,
        orbitIndex: 0,
        stats: ["15% increased chance to Shock"],
        connections: [{ id: 11578, orbit: 0 }],
      },
      "11578": {
        skill: 11578,
        name: "Lightning Damage",
        group: 979,
        orbit: 1,
        orbitIndex: 3,
        connections: [{ id: 4, orbit: 0 }],
      },
      "47175": {
        skill: 47175,
        name: "MARAUDER",
        group: 0,
        orbit: 0,
        orbitIndex: 0,
        classesStart: ["Marauder", "Warrior"],
        connections: [],
      },
    },
    groups: [
      { x: -15304, y: -7077, orbits: [0, 1], nodes: [47175] },
      { x: 1000, y: 500, orbits: [0, 1], nodes: [4, 11578] },
    ],
    classes: [{ name: "Warrior", integerId: 6, base_str: 15, base_dex: 7, base_int: 7 }],
    constants: poe2Constants,
    min_x: -20000,
    min_y: -20000,
    max_x: 20000,
    max_y: 20000,
    tree: "Default",
    ...overrides,
  };
}

describe("normalizePoe2Tree", () => {
  it("converts groups list to dict keyed by index", () => {
    const out = normalizePoe2Tree(makePoe2Fixture());
    expect(out.groups["0"]).toEqual({
      x: -15304,
      y: -7077,
      orbits: [0, 1],
      nodes: ["47175"],
      background: undefined,
    });
    expect(out.groups["1"].nodes).toEqual(["4", "11578"]);
  });

  it("synthesizes out[] from connections[{id, orbit}]", () => {
    const out = normalizePoe2Tree(makePoe2Fixture());
    expect(out.nodes["4"].out).toEqual(["11578"]);
    expect(out.nodes["11578"].out).toEqual(["4"]);
    expect(out.nodes["47175"].out).toEqual([]);
  });

  it("strips connections field from output shape", () => {
    const out = normalizePoe2Tree(makePoe2Fixture());
    expect(out.nodes["4"]).not.toHaveProperty("connections");
  });

  it("preserves classesStart on start nodes for POE2 class lookup", () => {
    const out = normalizePoe2Tree(makePoe2Fixture());
    expect(out.nodes["47175"].classesStart).toEqual(["Marauder", "Warrior"]);
  });

  it("forwards constants + bounds verbatim", () => {
    const out = normalizePoe2Tree(makePoe2Fixture());
    expect(out.constants).toBe(poe2Constants);
    expect(out.min_x).toBe(-20000);
    expect(out.max_y).toBe(20000);
  });

  it("buildAdjacency works on normalized POE2 output (connections → undirected edges)", () => {
    const normalized = normalizePoe2Tree(makePoe2Fixture());
    const ids = new Set(["4", "11578"]);
    const adj = buildAdjacency(ids, normalized.nodes);
    expect(adj.get("4")).toEqual(["11578"]);
    expect(adj.get("11578")).toEqual(["4"]);
  });
});

describe("POE2 geometry — orbit 2 (24 slots, even 15deg spacing)", () => {
  // POE2 orbit 2/3 have 24 slots — the 16-slot irregular angle table
  // (POE1 3.17+) must NOT apply; fall through to uniform distribution.
  it("orbit 2 (24 slots): 15deg even spacing, no 45deg irregular hack", () => {
    expect(nodeAngleDeg(2, 0, poe2Constants.skillsPerOrbit)).toBe(0);
    expect(nodeAngleDeg(2, 6, poe2Constants.skillsPerOrbit)).toBe(90);
    expect(nodeAngleDeg(2, 12, poe2Constants.skillsPerOrbit)).toBe(180);
    expect(nodeAngleDeg(2, 18, poe2Constants.skillsPerOrbit)).toBe(270);
  });

  it("orbit 9 (144 slots): 2.5deg even spacing", () => {
    expect(nodeAngleDeg(9, 0, poe2Constants.skillsPerOrbit)).toBe(0);
    expect(nodeAngleDeg(9, 36, poe2Constants.skillsPerOrbit)).toBe(90);
    expect(nodeAngleDeg(9, 72, poe2Constants.skillsPerOrbit)).toBe(180);
  });

  it("orbit 7 radius 251 (out-of-order with orbit 6=846 but valid)", () => {
    // Confirms the unusual POE2 radius ordering is honored at render time.
    const group = { x: 0, y: 0 };
    const pos = nodePosition(group, 7, 0, poe2Constants);
    expect(pos.y).toBeCloseTo(-251, 6);
  });
});
