import { describe, expect, it } from "vitest";
import { resolvePoe1AscendancyIndex, resolvePoe1ClassIndex } from "./PassiveTreeView";

describe("PassiveTreeView POE1 class fallback", () => {
  it("resolves POE1 class names into tree indices", () => {
    expect(resolvePoe1ClassIndex("Ranger")).toBe(2);
    expect(resolvePoe1ClassIndex("shadow")).toBe(6);
    expect(resolvePoe1ClassIndex("Unknown")).toBeUndefined();
  });

  it("resolves ascendancy names within the selected class", () => {
    const shadow = resolvePoe1ClassIndex("Shadow");

    expect(resolvePoe1AscendancyIndex(shadow, "Trickster")).toBe(2);
    expect(resolvePoe1AscendancyIndex(shadow, "Deadeye")).toBeUndefined();
    expect(resolvePoe1AscendancyIndex(undefined, "Trickster")).toBeUndefined();
  });
});
