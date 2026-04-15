// Passive tree sprite atlas loader.
// data.json:sprites contains for each category × zoom level:
//   { filename: <CDN url>, w, h, coords: { <key>: {x,y,w,h} } }
// We map the filename basename → local file under data/skilltree-export/assets/.

import type { TreeData } from "./passiveTree";

// Eager-load all asset URLs at build time. Vite produces hashed URLs.
const ASSET_URLS: Record<string, string> = import.meta.glob(
  "../../data/skilltree-export/assets/*.{png,jpg,jpeg,webp}",
  { eager: true, query: "?url", import: "default" },
) as Record<string, string>;

// basename -> URL
const BASENAME_TO_URL = new Map<string, string>();
for (const path in ASSET_URLS) {
  const base = path.split("/").pop()!;
  BASENAME_TO_URL.set(base, ASSET_URLS[path]);
}

export interface SpriteCoord {
  x: number; y: number; w: number; h: number;
}

export interface SpriteSheet {
  image: HTMLImageElement;
  loaded: boolean;
  w: number;
  h: number;
  coords: Record<string, SpriteCoord>;
}

export interface SpriteAtlas {
  // category (e.g. "normalActive", "frame", "groupBackground") -> sheet
  sheets: Map<string, SpriteSheet>;
  zoomKey: string;
}

/** Strip query string + extract basename from a CDN-style URL. */
function basenameFromUrl(url: string): string {
  const noQuery = url.split("?")[0];
  return noQuery.split("/").pop() || "";
}

/**
 * Load all sprite sheets for the given zoom key (e.g. "0.2972").
 * Returns immediately with an atlas; image .loaded flips true asynchronously.
 * `onAnyLoad` fires whenever any sheet finishes — caller should re-render.
 */
export function loadSpriteAtlas(
  data: TreeData,
  zoomKey: string,
  onAnyLoad: () => void,
): SpriteAtlas {
  const sheets = new Map<string, SpriteSheet>();
  const sprites = (data as unknown as { sprites: Record<string, Record<string, {
    filename: string; w: number; h: number; coords: Record<string, SpriteCoord>;
  }>> }).sprites;

  for (const category in sprites) {
    const zooms = sprites[category];
    const meta = zooms[zoomKey];
    if (!meta) continue;
    const base = basenameFromUrl(meta.filename);
    const url = BASENAME_TO_URL.get(base);
    if (!url) {
      // Asset missing on disk — skip silently. Caller will fall back to circle render.
      continue;
    }
    const img = new Image();
    const sheet: SpriteSheet = {
      image: img,
      loaded: false,
      w: meta.w,
      h: meta.h,
      coords: meta.coords || {},
    };
    img.onload = () => { sheet.loaded = true; onAnyLoad(); };
    img.onerror = () => { /* keep loaded=false; circle fallback */ };
    img.src = url;
    sheets.set(category, sheet);
  }

  return { sheets, zoomKey };
}

/** Pick the atlas zoom key closest to (and ≤) the desired pixel-per-world ratio. */
export function pickZoomKey(scale: number, available: number[]): string {
  // available e.g. [0.1246, 0.2109, 0.2972, 0.3835, 0.5]
  // Pick highest available ≤ scale * SOMEFACTOR; default to middle.
  const sorted = [...available].sort((a, b) => a - b);
  let chosen = sorted[Math.floor(sorted.length / 2)];
  for (const z of sorted) {
    if (z <= scale * 1.5) chosen = z;
  }
  return String(chosen);
}

/** Draw a sprite onto a canvas context using atlas coords. */
export function drawSprite(
  ctx: CanvasRenderingContext2D,
  sheet: SpriteSheet | undefined,
  coordKey: string,
  destCx: number,
  destCy: number,
  destSize: number,
): boolean {
  if (!sheet || !sheet.loaded) return false;
  const c = sheet.coords[coordKey];
  if (!c) return false;
  const aspect = c.w / c.h;
  const dw = destSize;
  const dh = destSize / aspect;
  ctx.drawImage(
    sheet.image,
    c.x, c.y, c.w, c.h,
    destCx - dw / 2, destCy - dh / 2, dw, dh,
  );
  return true;
}

/**
 * Draw a sprite at its atlas-native world size, scaled by camera.
 * coord.w/h are atlas pixels at the sheet's zoom level (e.g. 0.2972 px/world-unit).
 * world_size = coord.w / atlasScale; screen_size = world_size * cam.scale.
 */
export function drawSpriteNative(
  ctx: CanvasRenderingContext2D,
  sheet: SpriteSheet | undefined,
  coordKey: string,
  destCx: number,
  destCy: number,
  atlasScale: number,
  camScale: number,
  worldScale = 1,
): boolean {
  if (!sheet || !sheet.loaded) return false;
  const c = sheet.coords[coordKey];
  if (!c) return false;
  const dw = (c.w / atlasScale) * camScale * worldScale;
  const dh = (c.h / atlasScale) * camScale * worldScale;
  ctx.drawImage(
    sheet.image, c.x, c.y, c.w, c.h,
    destCx - dw / 2, destCy - dh / 2, dw, dh,
  );
  return true;
}
