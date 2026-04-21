import { describe, it, expect } from "vitest";
import { isCoachBlocked } from "./CoachBlockedBanner";
import type { CoachResult } from "../types";

function _mk(overrides: Partial<CoachResult> = {}): CoachResult {
  return {
    build_summary: "",
    tier: "",
    strengths: [],
    weaknesses: [],
    leveling_guide: { act1_4: "", act5_10: "", early_maps: "", endgame: "" },
    leveling_skills: {
      damage_type: "",
      recommended: { name: "", reason: "", transition_level: "" },
      options: [],
      skill_transitions: [],
    },
    key_items: [],
    aura_utility_progression: [],
    build_rating: {
      newbie_friendly: 0, gearing_difficulty: 0, play_difficulty: 0,
      league_start_viable: 0, hcssf_viability: 0,
    },
    gear_progression: [],
    map_mod_warnings: { deadly: [], dangerous: [], caution: [], regex_filter: "" },
    variant_snapshots: [],
    passive_priority: [],
    danger_zones: [],
    farming_strategy: "",
    ...overrides,
  };
}

describe("isCoachBlocked", () => {
  it("returns false when coaching is null/undefined", () => {
    expect(isCoachBlocked(null)).toBe(false);
    expect(isCoachBlocked(undefined)).toBe(false);
  });

  it("returns false when trace is missing", () => {
    expect(isCoachBlocked(_mk())).toBe(false);
  });

  it("returns false when trace is empty", () => {
    expect(isCoachBlocked(_mk({ _normalization_trace: [] }))).toBe(false);
  });

  it("returns false when trace has only corrections (no drops)", () => {
    const r = _mk({
      _normalization_trace: [
        { field: "a", from: "bleed chance", to: "Chance to Bleed Support", match_type: "alias" },
        { field: "b", from: "Cleave", to: "Cleave", match_type: "exact" },
      ],
    });
    expect(isCoachBlocked(r)).toBe(false);
  });

  it("returns true when trace has at least one dropped entry", () => {
    const r = _mk({
      _normalization_trace: [
        { field: "a", from: "Cleave", to: "Cleave", match_type: "exact" },
        { field: "b", from: "Onslaught Support", to: null, match_type: "dropped" },
      ],
    });
    expect(isCoachBlocked(r)).toBe(true);
  });
});
