/**
 * Syndicate data 무결성 회귀 테스트.
 * - layouts.json의 모든 board member id가 members.json에 존재
 * - members.json 구조 기본 불변성 (17 lieutenants + Catarina, 4 분과)
 * - layouts deprecated 필드는 boolean 타입
 */
import { describe, expect, test } from "vitest";
import layouts from "../../data/syndicate_layouts.json";
import members from "../../data/syndicate_members.json";

const DIVISIONS = ["Transportation", "Fortification", "Research", "Intervention"] as const;

describe("syndicate data integrity", () => {
  const memberIds = new Set(members.members.map((m) => m.id));

  test("members.json: 17 lieutenants + Catarina (18 entries)", () => {
    expect(members.members).toHaveLength(18);
    expect(memberIds.has("catarina")).toBe(true);
    // Catarina는 default_division=null, 나머지는 4 분과 중 하나
    const lieutenants = members.members.filter((m) => m.id !== "catarina");
    expect(lieutenants).toHaveLength(17);
    for (const m of lieutenants) {
      expect(DIVISIONS).toContain(m.default_division as typeof DIVISIONS[number]);
    }
  });

  test("every layout board member id exists in members.json", () => {
    for (const layout of layouts.layouts) {
      const entries = Object.entries(layout.board) as [string, string[]][];
      for (const [division, ids] of entries) {
        expect(DIVISIONS).toContain(division as typeof DIVISIONS[number]);
        for (const id of ids) {
          expect(memberIds).toContain(id);
        }
      }
    }
  });

  test("deprecated flag is boolean when present", () => {
    for (const layout of layouts.layouts) {
      const dep = (layout as { deprecated?: unknown }).deprecated;
      if (dep !== undefined) {
        expect(typeof dep).toBe("boolean");
      }
    }
  });

  test("each member has rewards for all 4 divisions (except Catarina)", () => {
    for (const m of members.members) {
      if (m.id === "catarina") continue;
      for (const div of DIVISIONS) {
        expect(m.rewards[div]).toBeTruthy();
      }
    }
  });

  test("meta_2x2_5 and HCSSF presets exist after S1", () => {
    const ids = new Set(layouts.layouts.map((l) => l.id));
    expect(ids.has("meta_2x2_5")).toBe(true);
    expect(ids.has("hcssf_safe_start")).toBe(true);
    expect(ids.has("ssf_crafting_core")).toBe(true);
    expect(ids.has("ssf_currency_sustain")).toBe(true);
  });

  test("ss22 is marked deprecated (3.26 Mastermind 분리 이후)", () => {
    const ss22 = layouts.layouts.find((l) => l.id === "ss22");
    expect(ss22).toBeDefined();
    expect((ss22 as { deprecated?: boolean }).deprecated).toBe(true);
  });

  test("legacy aisling_fixed id preserved for localStorage compatibility", () => {
    const ids = new Set(layouts.layouts.map((l) => l.id));
    expect(ids.has("aisling_fixed")).toBe(true);
  });
});
