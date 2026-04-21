import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

const STORAGE_KEY = "pathcraftai_progress";

interface ChecklistValue {
  /** 빌드별 체크키 조합용 prefix (buildData.meta.build_name 등) */
  buildKey: string;
  /** 체크키 → bool 맵 (localStorage 영속) */
  checked: Record<string, boolean>;
  /** 체크 토글 */
  toggle: (key: string) => void;
  /** 빌드 스코프 체크키 생성 */
  ck: (suffix: string) => string;
}

const Ctx = createContext<ChecklistValue | null>(null);

interface Props {
  buildKey: string;
  children: ReactNode;
}

export function ChecklistProvider({ buildKey, children }: Props) {
  const [checked, setChecked] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  const toggle = useCallback((key: string) => {
    setChecked((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch { /* quota full, ignore */ }
      return next;
    });
  }, []);

  const value = useMemo<ChecklistValue>(() => ({
    buildKey,
    checked,
    toggle,
    ck: (suffix: string) => `${buildKey}::${suffix}`,
  }), [buildKey, checked, toggle]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useChecklist(): ChecklistValue {
  const v = useContext(Ctx);
  if (!v) throw new Error("useChecklist must be used inside ChecklistProvider");
  return v;
}
