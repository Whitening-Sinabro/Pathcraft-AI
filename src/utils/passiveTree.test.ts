import { describe, it, expect } from "vitest";
import {
  nodeAngleDeg,
  nodePosition,
  normalizePoe2Tree,
  buildAdjacency,
  resolveNodePosition,
  type TreeConstants,
  type Poe2RawTree,
  type Poe2RawGroup,
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

  it("preserves connection.orbit metadata as outConn (PoB BuildConnector ground truth)", () => {
    // POE2 의 connection.orbit 은 호 반경 인덱스 + 부호 (방향). 직선 fallback 만으로
    // 그리면 inter-group connection 이 거미줄처럼 보임 — outConn 으로 PoB 알고리즘 적용.
    const out = normalizePoe2Tree(makePoe2Fixture({
      nodes: {
        "1": { skill: 1, name: "A", group: 0, orbit: 0, orbitIndex: 0,
          connections: [{ id: 2, orbit: 3 }, { id: 3, orbit: -5 }] },
        "2": { skill: 2, name: "B", group: 1, orbit: 0, orbitIndex: 0, connections: [] },
        "3": { skill: 3, name: "C", group: 1, orbit: 1, orbitIndex: 0, connections: [] },
      },
    }));
    expect(out.nodes["1"].outConn).toEqual([
      { id: "2", orbit: 3 },
      { id: "3", orbit: -5 },
    ]);
    // out 도 동일 ID 순서 보존 (buildAdjacency 등 호환)
    expect(out.nodes["1"].out).toEqual(["2", "3"]);
  });

  it("guarantees out[] and outConn[] index alignment (drawEdges 가 outs[i]/outConn[i] 동시 참조)", () => {
    // drawEdges 의 외부 호 분기는 `outs[i]` 의 target ID 와 `outConn[i].orbit` 를 같은
    // 인덱스로 묶는다. 두 배열의 길이/순서 불일치는 wrong-orbit 으로 잘못된 호를 그리게 됨.
    const out = normalizePoe2Tree(makePoe2Fixture({
      nodes: {
        "100": { skill: 100, name: "Hub", group: 0, orbit: 0, orbitIndex: 0,
          connections: [
            { id: 200, orbit: 0 },
            { id: 300, orbit: 7 },
            { id: 400, orbit: -3 },
            { id: 500, orbit: 0 },
          ] },
        "200": { skill: 200, name: "A", group: 1, orbit: 1, orbitIndex: 0, connections: [] },
        "300": { skill: 300, name: "B", group: 2, orbit: 1, orbitIndex: 0, connections: [] },
        "400": { skill: 400, name: "C", group: 3, orbit: 1, orbitIndex: 0, connections: [] },
        "500": { skill: 500, name: "D", group: 4, orbit: 1, orbitIndex: 0, connections: [] },
      },
      groups: [
        { x: 0, y: 0, orbits: [0], nodes: [100] },
        { x: 100, y: 0, orbits: [0, 1], nodes: [200] },
        { x: 200, y: 0, orbits: [0, 1], nodes: [300] },
        { x: 300, y: 0, orbits: [0, 1], nodes: [400] },
        { x: 400, y: 0, orbits: [0, 1], nodes: [500] },
      ],
    }));
    const node = out.nodes["100"];
    expect(node.out).toBeDefined();
    expect(node.outConn).toBeDefined();
    expect(node.out!.length).toBe(node.outConn!.length);
    for (let i = 0; i < node.out!.length; i++) {
      expect(node.outConn![i].id).toBe(node.out![i]);
    }
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

  it("skips null group slots — PoB-PoE2 sparse list (실측 16 null / 1497)", () => {
    // groups 배열에 null 슬롯이 있어도 normalize 가 폭발하지 않아야 함.
    // null 슬롯은 dict 에 키 자체를 만들지 않아 resolveNodePosition 이 null 반환.
    const fixture = makePoe2Fixture({
      groups: [
        { x: 0, y: 0, orbits: [0], nodes: [47175] },
        null as unknown as Poe2RawGroup,  // sparse slot
        { x: 1000, y: 500, orbits: [0, 1], nodes: [4, 11578] },
      ],
      nodes: {
        "47175": { skill: 47175, name: "X", group: 0, orbit: 0, orbitIndex: 0, connections: [] },
        // group=1 is null — 합법, 다만 좌표 계산은 불가
        "999": { skill: 999, name: "Orphan", group: 1, orbit: 0, orbitIndex: 0, connections: [] },
        "4": { skill: 4, name: "Y", group: 2, orbit: 0, orbitIndex: 0, connections: [] },
        "11578": { skill: 11578, name: "Z", group: 2, orbit: 1, orbitIndex: 3, connections: [] },
      },
    });
    const out = normalizePoe2Tree(fixture);
    expect(out.groups["0"]).toBeDefined();
    expect(out.groups["1"]).toBeUndefined();  // null slot — 키 없음
    expect(out.groups["2"]).toBeDefined();
    // null group 참조 노드는 nodes 에는 남되, resolveNodePosition 은 null 반환
    expect(out.nodes["999"]).toBeDefined();
    expect(resolveNodePosition(out.nodes["999"], out.groups, out.constants)).toBeNull();
    expect(resolveNodePosition(out.nodes["47175"], out.groups, out.constants)).not.toBeNull();
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
