import { describe, it, expect } from "vitest";
import { nodeAngleDeg, nodePosition, type TreeConstants } from "./passiveTree";

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
