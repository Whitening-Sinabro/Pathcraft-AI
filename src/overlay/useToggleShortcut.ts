import { useEffect } from "react";

/**
 * Ctrl/Cmd+Shift+O 단축키 — 오버레이 토글.
 *
 * 주의: 로컬(창 포커스 필요). OS-wide 글로벌 단축키는 `tauri-plugin-global-shortcut` 필요 — 별도 트랙.
 */
export function useToggleShortcut(onToggle: () => void): void {
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      // Ctrl+Shift+O (Win/Linux) 또는 Cmd+Shift+O (macOS)
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "o" || e.key === "O")) {
        e.preventDefault();
        onToggle();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onToggle]);
}
