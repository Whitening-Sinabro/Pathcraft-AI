import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

/** POE1 vs POE2 — 앱 전역에서 어느 게임 맥락인지 지시.
 * Phase 0 마이닝 결과 POE2 GGPK 포맷 100% 호환 확인됨 (2026-04-20).
 * 그러나 현 시점 coach/filter/syndicate/passive는 POE1 전제 → POE2 선택 시 gate. */
export type ActiveGame = "poe1" | "poe2";

export const ACTIVE_GAME_STORAGE_KEY = "pathcraftai_active_game";

export const GAME_LABEL: Record<ActiveGame, string> = {
  poe1: "POE 1",
  poe2: "POE 2",
};

interface ActiveGameContextValue {
  game: ActiveGame;
  setGame: (g: ActiveGame) => void;
}

const ActiveGameContext = createContext<ActiveGameContextValue | null>(null);

function loadInitial(): ActiveGame {
  try {
    const saved = localStorage.getItem(ACTIVE_GAME_STORAGE_KEY);
    if (saved === "poe1" || saved === "poe2") return saved;
  } catch { /* quota/privacy mode */ }
  return "poe1";
}

export function ActiveGameProvider({ children }: { children: ReactNode }) {
  const [game, setGameState] = useState<ActiveGame>(loadInitial);

  const setGame = useCallback((g: ActiveGame) => {
    setGameState(g);
    try { localStorage.setItem(ACTIVE_GAME_STORAGE_KEY, g); } catch { /* quota */ }
  }, []);

  return (
    <ActiveGameContext.Provider value={{ game, setGame }}>
      {children}
    </ActiveGameContext.Provider>
  );
}

export function useActiveGame(): ActiveGameContextValue {
  const ctx = useContext(ActiveGameContext);
  if (!ctx) throw new Error("useActiveGame must be inside <ActiveGameProvider>");
  return ctx;
}
