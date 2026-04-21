/**
 * 오버레이 창 위치/크기 영속.
 * Tauri `onResized`/`onMoved` 이벤트 구독 → localStorage 저장.
 * 창 show 전에 restore() 호출 → 이전 위치/크기 복원.
 */
import { LogicalPosition, LogicalSize, type Window } from "@tauri-apps/api/window";
import type { UnlistenFn } from "@tauri-apps/api/event";
import { logger } from "../utils/logger";

const STORAGE_KEY = "pathcraftai_overlay_window_state";

interface WindowState {
  x: number;
  y: number;
  width: number;
  height: number;
}

function load(): WindowState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (
      typeof parsed?.x === "number" &&
      typeof parsed?.y === "number" &&
      typeof parsed?.width === "number" &&
      typeof parsed?.height === "number"
    ) {
      return parsed as WindowState;
    }
    return null;
  } catch {
    return null;
  }
}

function save(state: WindowState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch { /* quota, ignore */ }
}

/** 창 현재 상태 snapshot → localStorage. 디바운스 없음 (이벤트 자체가 저빈도). */
async function captureAndSave(win: Window): Promise<void> {
  try {
    const [pos, size] = await Promise.all([win.outerPosition(), win.innerSize()]);
    const factor = await win.scaleFactor();
    save({
      x: Math.round(pos.x / factor),
      y: Math.round(pos.y / factor),
      width: Math.round(size.width / factor),
      height: Math.round(size.height / factor),
    });
  } catch (e) {
    logger.warn("[overlay.windowState] capture failed", e);
  }
}

/** 오버레이 mount 시 복원. 스토리지에 없으면 noop. */
export async function restore(win: Window): Promise<void> {
  const state = load();
  if (!state) return;
  try {
    await win.setSize(new LogicalSize(state.width, state.height));
    await win.setPosition(new LogicalPosition(state.x, state.y));
  } catch (e) {
    logger.warn("[overlay.windowState] restore failed", e);
  }
}

/** resize/move 이벤트 구독. 반환된 함수로 구독 해제. */
export async function subscribe(win: Window): Promise<UnlistenFn> {
  const unlistenResized = await win.onResized(() => { captureAndSave(win); });
  const unlistenMoved = await win.onMoved(() => { captureAndSave(win); });
  return () => {
    unlistenResized();
    unlistenMoved();
  };
}
