import { describe, it, expect } from "vitest";
import {
  CLASS_NAMES,
  CLASS_START_IDS,
  ASCENDANCIES,
  POE2_CLASS_NAMES,
  POE2_CLASS_START_IDS,
  POE2_CLASS_START_IDS_BY_INDEX,
  POE2_ASCENDANCIES,
} from "./passiveTreeConstants";

describe("POE1 constants sanity", () => {
  it("7 classes, indexes 0..6 map to start node ids", () => {
    expect(CLASS_NAMES).toHaveLength(7);
    for (let i = 0; i < 7; i++) {
      expect(CLASS_START_IDS[i]).toMatch(/^\d+$/);
    }
  });

  it("every class (non-Scion) has an ascendancy list", () => {
    for (let i = 1; i <= 6; i++) {
      expect(ASCENDANCIES[i]).toBeInstanceOf(Array);
      expect(ASCENDANCIES[i].length).toBeGreaterThan(0);
    }
  });
});

describe("POE2 constants — 2026-04-22 GGPK + tree.json alignment", () => {
  it("POE2 has 8 classes", () => {
    expect(POE2_CLASS_NAMES).toHaveLength(8);
    expect(POE2_CLASS_NAMES[0]).toBe("Warrior");
    expect(POE2_CLASS_NAMES[POE2_CLASS_NAMES.length - 1]).toBe("Druid");
  });

  it("every POE2 class has ascendancies", () => {
    for (let i = 0; i < 8; i++) {
      expect(POE2_ASCENDANCIES[i]).toBeInstanceOf(Array);
      expect(POE2_ASCENDANCIES[i].length).toBeGreaterThan(0);
    }
  });

  it("POE2 ascendancies total 21 (3+2+2+2+3+4+3+2)", () => {
    const total = Object.values(POE2_ASCENDANCIES)
      .reduce((n, arr) => n + arr.length, 0);
    expect(total).toBe(21);
  });

  it("Witch 4 ascendancies include Abyssal Lich (confirmed 2026-04-22)", () => {
    const witchIdx = POE2_CLASS_NAMES.indexOf("Witch");
    expect(witchIdx).toBeGreaterThanOrEqual(0);
    expect(POE2_ASCENDANCIES[witchIdx]).toHaveLength(4);
    expect(POE2_ASCENDANCIES[witchIdx]).toContain("Abyssal Lich");
  });

  it("Sorceress 3 ascendancies include Disciple of Varashta (confirmed 2026-04-22)", () => {
    const sorcIdx = POE2_CLASS_NAMES.indexOf("Sorceress");
    expect(sorcIdx).toBeGreaterThanOrEqual(0);
    expect(POE2_ASCENDANCIES[sorcIdx]).toHaveLength(3);
    expect(POE2_ASCENDANCIES[sorcIdx]).toContain("Disciple of Varashta");
  });

  it("Witch and Sorceress share start node 54447", () => {
    expect(POE2_CLASS_START_IDS.Witch).toBe(POE2_CLASS_START_IDS.Sorceress);
    expect(POE2_CLASS_START_IDS.Witch).toBe("54447");
  });

  it("Ranger and Huntress share start node 50459", () => {
    expect(POE2_CLASS_START_IDS.Ranger).toBe(POE2_CLASS_START_IDS.Huntress);
    expect(POE2_CLASS_START_IDS.Ranger).toBe("50459");
  });

  it("by-index and by-name start tables agree", () => {
    for (let i = 0; i < POE2_CLASS_NAMES.length; i++) {
      const name = POE2_CLASS_NAMES[i];
      expect(POE2_CLASS_START_IDS_BY_INDEX[i]).toBe(POE2_CLASS_START_IDS[name]);
    }
  });

  it("POE2 by-index covers all 8 slots with valid node ids", () => {
    for (let i = 0; i < 8; i++) {
      expect(POE2_CLASS_START_IDS_BY_INDEX[i]).toMatch(/^\d+$/);
    }
  });
});
