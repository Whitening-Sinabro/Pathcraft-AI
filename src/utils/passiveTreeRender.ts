// Pure Canvas rendering for the passive tree.
// Separated from React so the draw logic is framework-agnostic and testable.

import type { TreeGroup, TreeNode } from "./passiveTree";
import type { SpriteAtlas } from "./passiveTreeSprites";
import { drawSpriteNative } from "./passiveTreeSprites";
import {
  SKILLS_PER_ORBIT, FRAME_UNALLOCATED, FRAME_ALLOCATED,
  NODE_COLORS,
  type NodeKind,
} from "./passiveTreeConstants";

export interface ResolvedNode {
  id: string;
  node: TreeNode;
  x: number;
  y: number;
  kind: NodeKind;
  radius: number;
}

export interface ResolvedGroup {
  id: string;
  group: TreeGroup;
  bgKey: string | null;
  isHalf: boolean;
}

export interface Camera {
  cx: number;
  cy: number;
  scale: number;
}

export interface RenderState {
  ctx: CanvasRenderingContext2D;
  width: number;
  height: number;
  camera: Camera;
  nodes: ResolvedNode[];
  groups: ResolvedGroup[];
  nodeById: Map<string, ResolvedNode>;
  allocated: Set<string>;
  hoveredId: string | null;
  searchMatches: Set<string>;
  atlas: SpriteAtlas | null;
  orbitRadii: number[];
}

const ICON_SCALE = 0.55;
const FRAME_SCALE = 0.65;

/** Draw a full frame using the given state. */
export function drawFrame(state: RenderState): void {
  const { ctx, width, height, camera, atlas } = state;
  const w2sx = (wx: number) => (wx - camera.cx) * camera.scale + width / 2;
  const w2sy = (wy: number) => (wy - camera.cy) * camera.scale + height / 2;

  ctx.fillStyle = "#0c0c0c";
  ctx.fillRect(0, 0, width, height);

  drawBackgroundTile(state, w2sx, w2sy);
  drawGroupBackgrounds(state, w2sx, w2sy);
  drawEdges(state, w2sx, w2sy);

  ctx.shadowBlur = 0;
  drawNodes(state, w2sx, w2sy);

  void atlas;  // referenced via state
}

function drawBackgroundTile(
  state: RenderState,
  _w2sx: (x: number) => number,
  _w2sy: (y: number) => number,
): void {
  const { ctx, atlas, camera, width, height } = state;
  const atlasScale = atlas ? parseFloat(atlas.zoomKey) : 0.2972;
  const bgSheet = atlas?.sheets.get("background");
  if (!bgSheet?.loaded) return;
  const coord = bgSheet.coords["Background2"]
    || bgSheet.coords[Object.keys(bgSheet.coords)[0]];
  if (!coord) return;
  const tileW = (coord.w / atlasScale) * camera.scale;
  const tileH = (coord.h / atlasScale) * camera.scale;
  if (tileW <= 2 || tileH <= 2) return;

  const worldLeft = camera.cx - width / 2 / camera.scale;
  const worldTop = camera.cy - height / 2 / camera.scale;
  const startX = Math.floor(worldLeft / (coord.w / atlasScale)) * (coord.w / atlasScale);
  const startY = Math.floor(worldTop / (coord.h / atlasScale)) * (coord.h / atlasScale);
  for (let wy = startY; wy < worldTop + height / camera.scale; wy += coord.h / atlasScale) {
    for (let wx = startX; wx < worldLeft + width / camera.scale; wx += coord.w / atlasScale) {
      const sx = (wx - camera.cx) * camera.scale + width / 2;
      const sy = (wy - camera.cy) * camera.scale + height / 2;
      ctx.drawImage(bgSheet.image, coord.x, coord.y, coord.w, coord.h, sx, sy, tileW, tileH);
    }
  }
}

function drawGroupBackgrounds(
  state: RenderState,
  w2sx: (x: number) => number,
  w2sy: (y: number) => number,
): void {
  const { ctx, atlas, groups, camera } = state;
  const bgSheet = atlas?.sheets.get("groupBackground");
  if (!bgSheet?.loaded) return;
  const atlasScale = parseFloat(atlas!.zoomKey);
  for (const g of groups) {
    if (!g.bgKey) continue;
    const coord = bgSheet.coords[g.bgKey];
    if (!coord) continue;
    const sx = w2sx(g.group.x);
    const sy = w2sy(g.group.y);
    const dw = (coord.w / atlasScale) * camera.scale;
    const dh = (coord.h / atlasScale) * camera.scale;
    if (g.isHalf) {
      ctx.drawImage(bgSheet.image, coord.x, coord.y, coord.w, coord.h, sx - dw / 2, sy - dh, dw, dh);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.scale(1, -1);
      ctx.drawImage(bgSheet.image, coord.x, coord.y, coord.w, coord.h, -dw / 2, 0, dw, dh);
      ctx.restore();
    } else {
      ctx.drawImage(bgSheet.image, coord.x, coord.y, coord.w, coord.h, sx - dw / 2, sy - dh / 2, dw, dh);
    }
  }
}

function drawEdges(
  state: RenderState,
  w2sx: (x: number) => number,
  w2sy: (y: number) => number,
): void {
  const { ctx, nodes, nodeById, groups, allocated, camera, atlas, orbitRadii } = state;

  const dimStyle = "rgba(95, 80, 60, 0.85)";
  const activeStyle = "rgba(255, 200, 100, 0.95)";
  ctx.lineWidth = Math.max(2, Math.min(10, 14 * camera.scale));
  ctx.lineCap = "round";

  const groupById = new Map<string, TreeGroup>();
  for (const g of groups) groupById.set(g.id, g.group);

  const lineSheet = atlas?.sheets.get("line");
  const lineCoordNormal = lineSheet?.coords["LineConnectorNormal"];
  const strokeWidth = Math.max(2, Math.min(10, 14 * camera.scale));
  const spriteHeight = strokeWidth;
  const useLineSprite = !!(lineSheet?.loaded && lineCoordNormal && camera.scale > 0.05);

  for (const r of nodes) {
    const outs = r.node.out;
    if (!outs) continue;
    const sax = w2sx(r.x);
    const say = w2sy(r.y);
    for (const targetId of outs) {
      const t = nodeById.get(targetId);
      if (!t) continue;
      if (r.kind === "classStart" && t.kind === "classStart") continue;
      if (r.kind === "mastery" || t.kind === "mastery") continue;
      const dxw = r.x - t.x, dyw = r.y - t.y;
      if (dxw * dxw + dyw * dyw > 1500 * 1500) continue;

      const sbx = w2sx(t.x);
      const sby = w2sy(t.y);

      const sameGroup = r.node.group != null && r.node.group === t.node.group;
      const sameOrbit = r.node.orbit != null && r.node.orbit === t.node.orbit;
      const bothAllocated = allocated.has(r.id) && allocated.has(t.id);
      ctx.strokeStyle = bothAllocated ? activeStyle : dimStyle;

      let isAdjacentOrbit = false;
      if (sameGroup && sameOrbit && r.node.orbit != null
          && r.node.orbitIndex != null && t.node.orbitIndex != null) {
        const slots = SKILLS_PER_ORBIT[r.node.orbit];
        if (slots) {
          let sd = Math.abs(r.node.orbitIndex - t.node.orbitIndex);
          if (sd > slots / 2) sd = slots - sd;
          isAdjacentOrbit = sd === 1;
        }
      }

      if (isAdjacentOrbit && r.node.orbit != null) {
        const g = groupById.get(String(r.node.group));
        if (g) {
          const gcx = w2sx(g.x);
          const gcy = w2sy(g.y);
          const radius = orbitRadii[r.node.orbit] * camera.scale;
          const a1 = Math.atan2(say - gcy, sax - gcx);
          const a2 = Math.atan2(sby - gcy, sbx - gcx);
          let diff = a2 - a1;
          while (diff > Math.PI) diff -= Math.PI * 2;
          while (diff < -Math.PI) diff += Math.PI * 2;
          const anticlockwise = diff < 0;
          ctx.beginPath();
          ctx.arc(gcx, gcy, radius, a1, a2, anticlockwise);
          ctx.stroke();
          continue;
        }
      }

      if (!bothAllocated && useLineSprite && lineSheet && lineCoordNormal) {
        const dx = sbx - sax;
        const dy = sby - say;
        const len = Math.hypot(dx, dy);
        const angle = Math.atan2(dy, dx);
        ctx.save();
        ctx.translate(sax, say);
        ctx.rotate(angle);
        ctx.drawImage(
          lineSheet.image,
          lineCoordNormal.x, lineCoordNormal.y, lineCoordNormal.w, lineCoordNormal.h,
          0, -spriteHeight / 2, len, spriteHeight,
        );
        ctx.restore();
      } else {
        ctx.beginPath();
        ctx.moveTo(sax, say);
        ctx.lineTo(sbx, sby);
        ctx.stroke();
      }
    }
  }
}

function drawNodes(
  state: RenderState,
  w2sx: (x: number) => number,
  w2sy: (y: number) => number,
): void {
  const { ctx, nodes, allocated, hoveredId, searchMatches, atlas, camera, width, height } = state;
  const margin = 80;
  const atlasScale = atlas ? parseFloat(atlas.zoomKey) : 0.2972;

  const normalIconActive = atlas?.sheets.get("normalActive");
  const normalIconInactive = atlas?.sheets.get("normalInactive");
  const notableIconActive = atlas?.sheets.get("notableActive");
  const notableIconInactive = atlas?.sheets.get("notableInactive");
  const keystoneIconActive = atlas?.sheets.get("keystoneActive");
  const keystoneIconInactive = atlas?.sheets.get("keystoneInactive");
  const frameSheet = atlas?.sheets.get("frame");
  const masterySheet = atlas?.sheets.get("mastery");

  for (const r of nodes) {
    const sx = w2sx(r.x);
    const sy = w2sy(r.y);
    if (sx < -margin || sx > width + margin || sy < -margin || sy > height + margin) continue;

    let drewSprite = false;

    if (r.kind === "mastery") {
      if (r.node.icon && masterySheet) {
        const ok = drawSpriteNative(
          ctx, masterySheet, r.node.icon, sx, sy, atlasScale, camera.scale, ICON_SCALE,
        );
        if (ok) drewSprite = true;
      }
    } else {
      const isAllocated = allocated.has(r.id);
      if (r.node.icon) {
        let iconSrc = isAllocated ? normalIconActive : normalIconInactive;
        if (r.kind === "keystone") iconSrc = isAllocated ? keystoneIconActive : keystoneIconInactive;
        else if (r.kind === "notable") iconSrc = isAllocated ? notableIconActive : notableIconInactive;
        if (iconSrc) {
          const ok = drawSpriteNative(
            ctx, iconSrc, r.node.icon, sx, sy, atlasScale, camera.scale, ICON_SCALE,
          );
          if (ok) drewSprite = true;
        }
      }
      const frameKey = (isAllocated ? FRAME_ALLOCATED : FRAME_UNALLOCATED)[r.kind];
      if (frameKey && frameSheet) {
        const ok = drawSpriteNative(
          ctx, frameSheet, frameKey, sx, sy, atlasScale, camera.scale, FRAME_SCALE,
        );
        if (ok) drewSprite = true;
      }
    }

    if (!drewSprite) {
      const radius = Math.max(1.5, r.radius * camera.scale);
      ctx.beginPath();
      ctx.arc(sx, sy, radius, 0, Math.PI * 2);
      ctx.fillStyle = NODE_COLORS[r.kind];
      ctx.fill();
    }

    if (hoveredId === r.id) {
      const hr = Math.max(8, r.radius * camera.scale * 1.4);
      ctx.beginPath();
      ctx.arc(sx, sy, hr, 0, Math.PI * 2);
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    if (searchMatches.has(r.id)) {
      const hr = Math.max(10, r.radius * camera.scale * 1.6);
      ctx.beginPath();
      ctx.arc(sx, sy, hr, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(93, 173, 226, 0.95)";
      ctx.lineWidth = 3;
      ctx.stroke();
    }
  }
}
