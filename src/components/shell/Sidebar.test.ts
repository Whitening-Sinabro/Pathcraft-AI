import { describe, expect, test } from "vitest";
import { isTabId } from "./Sidebar";

describe("isTabId — localStorage TabId guard", () => {
  test("accepts valid tab ids", () => {
    expect(isTabId("build")).toBe(true);
    expect(isTabId("syndicate")).toBe(true);
    expect(isTabId("passive")).toBe(true);
  });

  test("rejects unknown strings", () => {
    expect(isTabId("foo")).toBe(false);
    expect(isTabId("")).toBe(false);
    expect(isTabId("BUILD")).toBe(false);
  });

  test("rejects non-string values", () => {
    expect(isTabId(null)).toBe(false);
    expect(isTabId(undefined)).toBe(false);
    expect(isTabId(123)).toBe(false);
    expect(isTabId({})).toBe(false);
    expect(isTabId(["build"])).toBe(false);
  });
});
