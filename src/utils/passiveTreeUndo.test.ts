import { describe, it, expect } from "vitest";
import { createUndoHandler } from "./passiveTreeUndo";

describe("createUndoHandler", () => {
  it("starts with empty stacks", () => {
    const h = createUndoHandler();
    expect(h.canUndo()).toBe(false);
    expect(h.canRedo()).toBe(false);
    expect(h.undo(new Set())).toBeNull();
    expect(h.redo(new Set())).toBeNull();
  });

  it("push → undo restores previous state", () => {
    const h = createUndoHandler();
    const s1 = new Set(["a"]);
    h.push(s1);
    const s2 = new Set(["a", "b"]);
    const restored = h.undo(s2);
    expect(restored).toEqual(s1);
    expect(h.canRedo()).toBe(true);
  });

  it("undo → redo round-trips", () => {
    const h = createUndoHandler();
    h.push(new Set(["a"]));
    const after = new Set(["a", "b"]);
    const undone = h.undo(after)!;
    const redone = h.redo(undone)!;
    expect(redone).toEqual(after);
  });

  it("new push clears redo stack", () => {
    const h = createUndoHandler();
    h.push(new Set(["a"]));
    h.undo(new Set(["a", "b"]));
    expect(h.canRedo()).toBe(true);
    h.push(new Set(["c"]));
    expect(h.canRedo()).toBe(false);
  });

  it("caps stack depth at 100", () => {
    const h = createUndoHandler();
    for (let i = 0; i < 150; i++) h.push(new Set([String(i)]));
    // 100 undo should succeed, 101st null
    const cur = new Set(["end"]);
    let last: Set<string> | null = cur;
    let count = 0;
    while ((last = h.undo(last || new Set())) !== null) count++;
    expect(count).toBe(100);
  });

  it("clear empties both stacks", () => {
    const h = createUndoHandler();
    h.push(new Set(["a"]));
    h.undo(new Set(["b"]));
    h.clear();
    expect(h.canUndo()).toBe(false);
    expect(h.canRedo()).toBe(false);
  });
});
