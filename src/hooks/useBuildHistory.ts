import { useCallback, useMemo, useState } from "react";
import type { LeagueMode, CoachModel } from "./useBuildAnalyzer";
import { logger } from "../utils/logger";

export interface SavedBuild {
  id: string;
  pobLink: string;
  buildName: string;
  tier: string;
  rawBuildJson: string;
  rawCoachJson: string;
  extraPobLinks: string[];
  extraBuildJsons: string[];
  mode: LeagueMode;
  stageMode: boolean;
  alSplit: number;
  coachModel: CoachModel;
  createdAt: number;
  updatedAt: number;
}

export const BUILD_HISTORY_KEY = "pathcraftai_build_history_v1";
const BUILD_HISTORY_VERSION = 1;
const BUILD_HISTORY_MAX = 20;

function hashPobLink(s: string): string {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  }
  return h.toString(36);
}

function loadHistoryFromStorage(): SavedBuild[] {
  try {
    const raw = localStorage.getItem(BUILD_HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (parsed?.v !== BUILD_HISTORY_VERSION) return [];
    return Array.isArray(parsed.builds) ? parsed.builds : [];
  } catch (e) {
    logger.warn("[history] load failed", e);
    return [];
  }
}

function persistHistory(builds: SavedBuild[]): void {
  try {
    localStorage.setItem(
      BUILD_HISTORY_KEY,
      JSON.stringify({ v: BUILD_HISTORY_VERSION, builds }),
    );
  } catch (e) {
    logger.warn("[history] persist failed (quota?)", e);
  }
}

export type AddBuildInput = Omit<SavedBuild, "id" | "createdAt" | "updatedAt">;

export function useBuildHistory() {
  const [history, setHistory] = useState<SavedBuild[]>(() => loadHistoryFromStorage());

  const latest = useMemo<SavedBuild | null>(() => {
    if (history.length === 0) return null;
    return [...history].sort((a, b) => b.updatedAt - a.updatedAt)[0];
  }, [history]);

  const addOrUpdate = useCallback((build: AddBuildInput): void => {
    const id = hashPobLink(build.pobLink);
    const now = Date.now();
    setHistory((prev) => {
      const existing = prev.find((b) => b.id === id);
      const saved: SavedBuild = existing
        ? { ...existing, ...build, id, updatedAt: now }
        : { ...build, id, createdAt: now, updatedAt: now };
      const filtered = prev.filter((b) => b.id !== id);
      const next = [saved, ...filtered]
        .sort((a, b) => b.updatedAt - a.updatedAt)
        .slice(0, BUILD_HISTORY_MAX);
      persistHistory(next);
      return next;
    });
  }, []);

  const remove = useCallback((id: string): void => {
    setHistory((prev) => {
      const next = prev.filter((b) => b.id !== id);
      persistHistory(next);
      return next;
    });
  }, []);

  const getById = useCallback((id: string): SavedBuild | null => {
    return history.find((b) => b.id === id) ?? null;
  }, [history]);

  return { history, latest, addOrUpdate, remove, getById };
}
