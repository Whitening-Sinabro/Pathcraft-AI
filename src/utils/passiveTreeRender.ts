// Pure Canvas rendering for the passive tree.
// Separated from React so the draw logic is framework-agnostic and testable.

import type { TreeGroup, TreeNode } from "./passiveTree";
import type { SpriteAtlas } from "./passiveTreeSprites";
import { drawSpriteNative } from "./passiveTreeSprites";
import {
  FRAME_UNALLOCATED, FRAME_ALLOCATED,
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
  /** 클래스/어센던시 시작점 — "할당" 아니나 시각적으로 active 프레임 사용 (캐릭터 마커) */
  anchors: Set<string>;
  hoveredId: string | null;
  searchMatches: Set<string>;
  atlas: SpriteAtlas | null;
  orbitRadii: number[];
  /** 게임별 슬롯 분포. POE1 7-orbit / POE2 10-orbit. 같은 group/같은 orbit 인접 판정에 사용. */
  skillsPerOrbit: number[];
  /**
   * 직선 fallback 전용 cutoff (world units). 호 분기는 cutoff 무관 (drawEdges 가 분리 처리).
   * POE1=1500 (직선 fallback 1.7% 잘림). POE2=5000 — 1500-5000 거리 inter-cluster path 보존,
   * 5000+ 거리 거미줄 sweep 차단. 실측 직선 fallback 거리 분포 기반.
   */
  edgeMaxDist: number;
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
  const { ctx, width, height, nodes, nodeById, groups, allocated, anchors, camera, atlas, orbitRadii, skillsPerOrbit, edgeMaxDist } = state;
  // Viewport culling margin (화면 밖 N px 까지 허용 — 호의 일부가 boundary 걸쳐도 자연스럽게).
  const VIEWPORT_MARGIN = 100;
  const isLit = (id: string) => allocated.has(id) || anchors.has(id);

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
    // POE2 의 connection orbit 메타. PoB-PoE2 BuildConnector 알고리즘 — 직선 대신 호.
    // POE1 은 미정의 → 기존 isAdjacentOrbit 분기 + 직선 fallback.
    const outConn = r.node.outConn;
    const sax = w2sx(r.x);
    const say = w2sy(r.y);
    for (let i = 0; i < outs.length; i++) {
      const targetId = outs[i];
      const t = nodeById.get(targetId);
      if (!t) continue;
      // PoB-PoE2 PassiveTree.lua:282-288 전처리 filter — 거미줄 방지의 핵심.
      //  - 한쪽이라도 class start (classStartIndex 또는 classesStart) 면 connection skip
      //  - 두 노드의 ascendancyName 이 다르면 skip (main ↔ ascendancy boundary 직선 방지)
      const rIsClassStart = r.node.classStartIndex != null
        || (r.node.classesStart != null && r.node.classesStart.length > 0);
      const tIsClassStart = t.node.classStartIndex != null
        || (t.node.classesStart != null && t.node.classesStart.length > 0);
      if (rIsClassStart || tIsClassStart) continue;
      if ((r.node.ascendancyName ?? null) !== (t.node.ascendancyName ?? null)) continue;
      if (r.kind === "mastery" || t.kind === "mastery") continue;
      const connOrbit = outConn?.[i]?.orbit;
      const isPoe2Arc = connOrbit != null;

      const sbx = w2sx(t.x);
      const sby = w2sy(t.y);

      const sameGroup = r.node.group != null && r.node.group === t.node.group;
      const sameOrbit = r.node.orbit != null && r.node.orbit === t.node.orbit;
      const bothAllocated = isLit(r.id) && isLit(t.id);
      ctx.strokeStyle = bothAllocated ? activeStyle : dimStyle;

      // [POE2] 외부 호: connection.orbit != 0 + 그 orbit 반경 정의 + dist < r*2.
      // PoB-PoE2 PassiveTree.lua:574-622 BuildConnector 분기 1.
      if (isPoe2Arc && connOrbit !== 0) {
        const arcR = orbitRadii[Math.abs(connOrbit)];
        if (arcR) {
          const dxw = t.x - r.x, dyw = t.y - r.y;
          const dist = Math.hypot(dxw, dyw);
          if (dist > 0 && dist < arcR * 2) {
            const perpSign = connOrbit > 0 ? 1 : -1;
            const perp = Math.sqrt(arcR * arcR - (dist * dist) / 4) * perpSign;
            const cxW = r.x + dxw / 2 + perp * (dyw / dist);
            const cyW = r.y + dyw / 2 - perp * (dxw / dist);
            const a1 = Math.atan2(r.y - cyW, r.x - cxW);
            const a2 = Math.atan2(t.y - cyW, t.x - cxW);
            let diff = a2 - a1;
            while (diff > Math.PI) diff -= Math.PI * 2;
            while (diff < -Math.PI) diff += Math.PI * 2;
            if (Math.abs(diff) <= Math.PI) {
              const anticlockwise = diff < 0;
              const cxs = w2sx(cxW), cys = w2sy(cyW);
              const radius = arcR * camera.scale;
              ctx.beginPath();
              ctx.arc(cxs, cys, radius, a1, a2, anticlockwise);
              ctx.stroke();
              continue;
            }
          }
        }
      }

      // [POE2] 내부 호: 같은 group + 같은 orbit + connection.orbit == 0.
      // PoB-PoE2 PassiveTree.lua:625-657 BuildConnector 분기 2.
      // POE1 의 기존 isAdjacentOrbit 와 별개로 outConn 메타가 있을 때만 적용.
      let didInnerArc = false;
      if (isPoe2Arc && connOrbit === 0 && sameGroup && sameOrbit && r.node.orbit != null) {
        const orbR = orbitRadii[r.node.orbit];
        const g = groupById.get(String(r.node.group));
        if (orbR && g) {
          const gcx = w2sx(g.x);
          const gcy = w2sy(g.y);
          const radius = orbR * camera.scale;
          const a1 = Math.atan2(say - gcy, sax - gcx);
          const a2 = Math.atan2(sby - gcy, sbx - gcx);
          let diff = a2 - a1;
          while (diff > Math.PI) diff -= Math.PI * 2;
          while (diff < -Math.PI) diff += Math.PI * 2;
          if (Math.abs(diff) <= Math.PI) {
            const anticlockwise = diff < 0;
            ctx.beginPath();
            ctx.arc(gcx, gcy, radius, a1, a2, anticlockwise);
            ctx.stroke();
            didInnerArc = true;
          }
        }
      }
      if (didInnerArc) continue;

      // 직선 fallback 대상에만 cutoff 적용 — 호 분기는 PoB 처럼 거리 무관.
      {
        const dxw = r.x - t.x, dyw = r.y - t.y;
        if (dxw * dxw + dyw * dyw > edgeMaxDist * edgeMaxDist) continue;
        // Viewport culling — 양 끝점 모두 화면 밖이면 skip. PoB 의 줌 인 기본값으로 화면 밖
        // sweep 가 자연스레 안 보이는 효과를 명시적 clip 으로 재현. 짧은 직선/호는 영향 없음.
        const inR = sax >= -VIEWPORT_MARGIN && sax <= width + VIEWPORT_MARGIN
          && say >= -VIEWPORT_MARGIN && say <= height + VIEWPORT_MARGIN;
        const inT = sbx >= -VIEWPORT_MARGIN && sbx <= width + VIEWPORT_MARGIN
          && sby >= -VIEWPORT_MARGIN && sby <= height + VIEWPORT_MARGIN;
        if (!inR && !inT) continue;
      }

      // [POE1 호환] orbitIndex 차이 1 이면 group orbit 호. POE1 은 outConn 없음.
      let isAdjacentOrbit = false;
      if (!isPoe2Arc && sameGroup && sameOrbit && r.node.orbit != null
          && r.node.orbitIndex != null && t.node.orbitIndex != null) {
        const slots = skillsPerOrbit[r.node.orbit];
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
  const { ctx, nodes, allocated, anchors, hoveredId, searchMatches, atlas, camera, width, height } = state;
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
      // classStart/ascendancyStart는 anchors 기반 active (캐릭터 마커이지 "할당" 아님)
      const isAllocated = allocated.has(r.id) || (r.kind === "classStart" && anchors.has(r.id));
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
