// PoB-style undo/redo for the allocated node set.
// Each snapshot = sorted string[] of node IDs. Stack depth capped at 100.
// Reference: PathOfBuildingCommunity UndoHandler.lua (two arrays, snapshot push
// on every mutation, redo cleared on new action).

const MAX_DEPTH = 100;

export interface UndoHandler {
  push(current: Set<string>): void;
  undo(current: Set<string>): Set<string> | null;
  redo(current: Set<string>): Set<string> | null;
  canUndo(): boolean;
  canRedo(): boolean;
  clear(): void;
}

export function createUndoHandler(): UndoHandler {
  const undoStack: string[][] = [];
  const redoStack: string[][] = [];

  const snapshot = (set: Set<string>): string[] => [...set].sort();
  const restore = (arr: string[]): Set<string> => new Set(arr);

  return {
    push(current) {
      undoStack.push(snapshot(current));
      if (undoStack.length > MAX_DEPTH) undoStack.shift();
      redoStack.length = 0;
    },
    undo(current) {
      if (undoStack.length === 0) return null;
      redoStack.push(snapshot(current));
      if (redoStack.length > MAX_DEPTH) redoStack.shift();
      const prev = undoStack.pop()!;
      return restore(prev);
    },
    redo(current) {
      if (redoStack.length === 0) return null;
      undoStack.push(snapshot(current));
      if (undoStack.length > MAX_DEPTH) undoStack.shift();
      const next = redoStack.pop()!;
      return restore(next);
    },
    canUndo() { return undoStack.length > 0; },
    canRedo() { return redoStack.length > 0; },
    clear() { undoStack.length = 0; redoStack.length = 0; },
  };
}
