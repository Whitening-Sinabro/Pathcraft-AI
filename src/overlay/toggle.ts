import { WebviewWindow } from "@tauri-apps/api/webviewWindow";
import { logger } from "../utils/logger";

/** 메인 창 → 오버레이 창. 메인은 hide. */
export async function openOverlay(): Promise<void> {
  try {
    const overlay = await WebviewWindow.getByLabel("overlay");
    const main = await WebviewWindow.getByLabel("main");
    if (!overlay) {
      logger.error("[overlay] window handle not found");
      return;
    }
    await overlay.show();
    await overlay.setFocus();
    if (main) await main.hide();
  } catch (e) {
    logger.error("[overlay] openOverlay failed", e);
  }
}

/** 오버레이 창 → 메인 창. 오버레이는 hide. */
export async function closeOverlay(): Promise<void> {
  try {
    const overlay = await WebviewWindow.getByLabel("overlay");
    const main = await WebviewWindow.getByLabel("main");
    if (main) {
      await main.show();
      await main.setFocus();
    }
    if (overlay) await overlay.hide();
  } catch (e) {
    logger.error("[overlay] closeOverlay failed", e);
  }
}
