import { useEffect, useRef, useState } from "react";
import {
  resolveNodePosition,
  buildAdjacency,
  shortestPath,
  deallocWithCascade,
  type TreeData,
  type TreeNode,
  type TreeGroup,
} from "../utils/passiveTree";
import { createUndoHandler, type UndoHandler } from "../utils/passiveTreeUndo";
import {
  loadSpriteAtlas,
  drawSpriteNative,
  type SpriteAtlas,
} from "../utils/passiveTreeSprites";
import dataUrl from "../../data/skilltree-export/data.json?url";

// Atlas zoom level. Single level for Phase 1b — auto-switching deferred.
const ATLAS_ZOOM = "0.2972";

interface ResolvedGroup {
  id: string;
  group: TreeGroup;
  bgKey: string | null;
  isHalf: boolean;
}

const SKILLS_PER_ORBIT = [1, 6, 16, 16, 40, 72, 72];

// Class start node IDs (from data.json sampling)
const CLASS_START_IDS: Record<number, string> = {
  0: "58833", // Scion
  1: "47175", // Marauder
  2: "50459", // Ranger
  3: "54447", // Witch
  4: "50986", // Duelist
  5: "61525", // Templar
  6: "44683", // Shadow
};
const CLASS_NAMES = ["Scion", "Marauder", "Ranger", "Witch", "Duelist", "Templar", "Shadow"];
// Ascendancy 구성 (data.classes 구조 기준, bloodline 제외)
const ASCENDANCIES: Record<number, string[]> = {
  0: ["Ascendant", "Reliquarian"],
  1: ["Juggernaut", "Berserker", "Chieftain"],
  2: ["Warden", "Deadeye", "Pathfinder"],
  3: ["Occultist", "Elementalist", "Necromancer"],
  4: ["Slayer", "Gladiator", "Champion"],
  5: ["Inquisitor", "Hierophant", "Guardian"],
  6: ["Assassin", "Trickster", "Saboteur"],
};
const CLASS_STORAGE_KEY = "pathcraftai_passive_class";
const ASCENDANCY_STORAGE_KEY = "pathcraftai_passive_ascendancy";

const FRAME_UNALLOCATED: Record<string, string> = {
  normal: "PSSkillFrame",
  notable: "NotableFrameUnallocated",
  keystone: "KeystoneFrameUnallocated",
  jewel: "JewelFrameUnallocated",
  ascendancy: "PSSkillFrame",
  classStart: "PSSkillFrame",
};

const FRAME_ALLOCATED: Record<string, string> = {
  normal: "PSSkillFrameActive",
  notable: "NotableFrameAllocated",
  keystone: "KeystoneFrameAllocated",
  jewel: "JewelFrameAllocated",
  ascendancy: "PSSkillFrameActive",
  classStart: "PSSkillFrameActive",
};

interface Props {
  width?: number;
  height?: number;
  showAscendancy?: boolean;
  // 외부(Phase 2: PoB URL 디코드)에서 사전 할당된 노드 ID 주입 가능
  initialAllocated?: Set<string>;
  // 빌드에서 추출된 class/ascendancy index (주입 시 사용자 선택 무시)
  buildClass?: number;
  buildAscendancy?: number;  // 0 = 없음, 1..3 = ascendancy 슬롯
  // 할당 변경 콜백 (상위에 allocated 노드 알림)
  onAllocationChange?: (allocated: Set<string>) => void;
}

interface Camera {
  cx: number;
  cy: number;
  scale: number;
}

interface ResolvedNode {
  id: string;
  node: TreeNode;
  x: number;
  y: number;
  kind: NodeKind;
  radius: number;
}

type NodeKind =
  | "normal" | "notable" | "keystone" | "mastery"
  | "jewel" | "ascendancy" | "classStart";

const NODE_COLORS: Record<NodeKind, string> = {
  normal: "#a89572",
  notable: "#e8c068",
  keystone: "#e74c3c",
  mastery: "#9b59b6",
  jewel: "#5dade2",
  ascendancy: "#f1c40f",
  classStart: "#ecf0f1",
};

const NODE_RADIUS_WORLD: Record<NodeKind, number> = {
  normal: 22, notable: 38, keystone: 50, mastery: 32,
  jewel: 36, classStart: 70, ascendancy: 24,
};

function classifyNode(node: TreeNode): NodeKind {
  if (node.classStartIndex != null) return "classStart";
  if (node.isKeystone) return "keystone";
  if (node.isJewelSocket) return "jewel";
  if (node.isMastery) return "mastery";
  if (node.isNotable) return "notable";
  if (node.ascendancyName) return "ascendancy";
  return "normal";
}

function computeBounds(nodes: ResolvedNode[]): {
  minX: number; minY: number; maxX: number; maxY: number;
} {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const n of nodes) {
    if (n.x < minX) minX = n.x;
    if (n.y < minY) minY = n.y;
    if (n.x > maxX) maxX = n.x;
    if (n.y > maxY) maxY = n.y;
  }
  return { minX, minY, maxX, maxY };
}

export function PassiveTreeCanvas({
  width = 900, height = 600, showAscendancy = false,
  initialAllocated, buildClass, buildAscendancy, onAllocationChange,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Mutable state lives in refs to avoid React re-renders on every interaction.
  const cameraRef = useRef<Camera>({ cx: 0, cy: 0, scale: 0.1 });
  const nodesRef = useRef<ResolvedNode[]>([]);
  const nodeByIdRef = useRef<Map<string, ResolvedNode>>(new Map());
  const groupsRef = useRef<ResolvedGroup[]>([]);
  const atlasRef = useRef<SpriteAtlas | null>(null);
  const orbitRadiiRef = useRef<number[]>([]);
  const hoveredIdRef = useRef<string | null>(null);
  const allocatedRef = useRef<Set<string>>(initialAllocated ?? new Set());
  const adjRef = useRef<Map<string, string[]>>(new Map());
  const rawNodesRef = useRef<Record<string, TreeNode>>({});
  const anchorsRef = useRef<Set<string>>(new Set());
  const undoRef = useRef<UndoHandler>(createUndoHandler());
  const dirtyRef = useRef(true);
  const rafRef = useRef(0);
  const onAllocationChangeRef = useRef(onAllocationChange);
  onAllocationChangeRef.current = onAllocationChange;

  // React state only for things that affect DOM (tooltip text, loading status).
  const [tooltip, setTooltip] = useState<{ name: string; stats: string[]; sx: number; sy: number } | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nodeCount, setNodeCount] = useState(0);
  // 포인트 카운터 (classStart/ascendancyStart 제외 + jewel sockets)
  const [pointsUsed, setPointsUsed] = useState(0);
  const [jewelSockets, setJewelSockets] = useState(0);
  // 검색 하이라이트
  const [searchQuery, setSearchQuery] = useState("");
  const searchMatchesRef = useRef<Set<string>>(new Set());
  const searchInputRef = useRef<HTMLInputElement>(null);
  // 선택된 클래스 — buildClass가 있으면 그 값 우선, 없으면 localStorage
  const [selectedClass, setSelectedClass] = useState<number | null>(() => {
    if (buildClass != null && buildClass >= 0 && buildClass <= 6) return buildClass;
    try {
      const saved = localStorage.getItem(CLASS_STORAGE_KEY);
      if (saved == null) return null;
      const n = parseInt(saved, 10);
      return Number.isFinite(n) && n >= 0 && n <= 6 ? n : null;
    } catch { return null; }
  });
  const [selectedAscendancy, setSelectedAscendancy] = useState<string | null>(() => {
    if (buildClass != null && buildAscendancy != null && buildAscendancy > 0) {
      const list = ASCENDANCIES[buildClass];
      if (list && list[buildAscendancy - 1]) return list[buildAscendancy - 1];
    }
    try { return localStorage.getItem(ASCENDANCY_STORAGE_KEY); } catch { return null; }
  });
  // 어센던시 start 노드 ID 맵 (ascendancyName → node id), 로드 후 채움
  const ascStartIdsRef = useRef<Record<string, string>>({});

  // 검색 매칭 계산 (검색어 또는 노드 변경 시)
  useEffect(() => {
    const q = searchQuery.trim().toLowerCase();
    const out = new Set<string>();
    if (q.length >= 2) {
      for (const r of nodesRef.current) {
        const name = (r.node.name || "").toLowerCase();
        if (name.includes(q)) { out.add(r.id); continue; }
        for (const s of r.node.stats || []) {
          if (s.toLowerCase().includes(q)) { out.add(r.id); break; }
        }
      }
    }
    searchMatchesRef.current = out;
    dirtyRef.current = true;
  }, [searchQuery, loaded]);

  // 클래스 변경 시 트리 리셋 + 해당 class start 자동 할당
  function pickClass(classIdx: number) {
    const startId = CLASS_START_IDS[classIdx];
    if (!startId) return;
    undoRef.current.push(allocatedRef.current);
    const next = new Set<string>([startId]);
    allocatedRef.current = next;
    setSelectedClass(classIdx);
    setSelectedAscendancy(null);
    try {
      localStorage.setItem(CLASS_STORAGE_KEY, String(classIdx));
      localStorage.removeItem(ASCENDANCY_STORAGE_KEY);
    } catch { /* quota full */ }
    anchorsRef.current = new Set([startId]);
    dirtyRef.current = true;
    recomputePoints();
    onAllocationChangeRef.current?.(new Set(next));
  }

  // 어센던시 변경 — 기존 ascendancy 노드 제거 + 새 ascendancy start 포함
  function pickAscendancy(ascName: string | null) {
    const alloc = allocatedRef.current;
    undoRef.current.push(alloc);
    // 기존 모든 ascendancy 노드 제거
    const rawNodes = rawNodesRef.current;
    for (const id of [...alloc]) {
      const n = rawNodes[id];
      if (n?.ascendancyName) alloc.delete(id);
    }
    if (ascName) {
      const startId = ascStartIdsRef.current[ascName];
      if (startId) alloc.add(startId);
    }
    setSelectedAscendancy(ascName);
    try {
      if (ascName) localStorage.setItem(ASCENDANCY_STORAGE_KEY, ascName);
      else localStorage.removeItem(ASCENDANCY_STORAGE_KEY);
    } catch { /* quota full */ }
    dirtyRef.current = true;
    recomputePoints();
    onAllocationChangeRef.current?.(new Set(alloc));
  }

  // allocated 기반 카운트 재계산
  function recomputePoints() {
    const alloc = allocatedRef.current;
    const rawNodes = rawNodesRef.current;
    let used = 0, sockets = 0;
    for (const id of alloc) {
      const n = rawNodes[id];
      if (!n) continue;
      if (n.classStartIndex != null) continue;
      if (n.isAscendancyStart) continue;
      used++;
      if (n.isJewelSocket) sockets++;
    }
    setPointsUsed(used);
    setJewelSockets(sockets);
  }

  // Load tree data — reload nodes when ascendancy changes (filter dependency)
  useEffect(() => {
    let cancelled = false;
    fetch(dataUrl)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<TreeData>;
      })
      .then((d) => {
        if (cancelled) return;
        const nodes: ResolvedNode[] = [];
        for (const id in d.nodes) {
          const node = d.nodes[id];
          // 선택된 ascendancy 노드만 표시 (또는 showAscendancy 옵션 시 전체)
          if (node.ascendancyName) {
            if (!showAscendancy && node.ascendancyName !== selectedAscendancy) continue;
          }
          if (node.isProxy || node.expansionJewel) continue;
          if (node.isAscendancyStart && !showAscendancy
              && node.ascendancyName !== selectedAscendancy) continue;
          const pos = resolveNodePosition(node, d.groups, d.constants);
          if (!pos) continue;
          const kind = classifyNode(node);
          nodes.push({
            id, node, x: pos.x, y: pos.y, kind,
            radius: NODE_RADIUS_WORLD[kind],
          });
        }
        nodesRef.current = nodes;
        nodeByIdRef.current = new Map(nodes.map((n) => [n.id, n]));

        // 인접 리스트 구축 (BFS 경로 탐색용)
        const allowedIds = new Set(nodes.map((n) => n.id));
        rawNodesRef.current = d.nodes;
        adjRef.current = buildAdjacency(allowedIds, d.nodes);
        // Ascendancy start 노드 매핑 수집
        const ascMap: Record<string, string> = {};
        for (const id in d.nodes) {
          const n = d.nodes[id];
          if (n.isAscendancyStart && n.ascendancyName) ascMap[n.ascendancyName] = id;
        }
        ascStartIdsRef.current = ascMap;

        // Dealloc cascade 앵커 = class start + 선택된 ascendancy start
        if (selectedClass != null && CLASS_START_IDS[selectedClass]) {
          const startId = CLASS_START_IDS[selectedClass];
          const anchors = new Set<string>([startId]);
          if (selectedAscendancy && ascMap[selectedAscendancy]) {
            anchors.add(ascMap[selectedAscendancy]);
          }
          anchorsRef.current = anchors;
          if (allocatedRef.current.size === 0) {
            allocatedRef.current.add(startId);
            if (selectedAscendancy && ascMap[selectedAscendancy]) {
              allocatedRef.current.add(ascMap[selectedAscendancy]);
            }
          }
        } else {
          const anchors = new Set<string>();
          for (const n of nodes) if (n.node.classStartIndex != null) anchors.add(n.id);
          anchorsRef.current = anchors;
        }

        // Filter groups whose nodes survived (i.e. main tree only when ascendancy hidden).
        const usedGroupIds = new Set<string>();
        for (const n of nodes) if (n.node.group != null) usedGroupIds.add(String(n.node.group));
        const groups: ResolvedGroup[] = [];
        for (const gid of usedGroupIds) {
          const g = d.groups[gid];
          if (!g) continue;
          groups.push({
            id: gid,
            group: g,
            bgKey: g.background?.image || null,
            isHalf: !!g.background?.isHalfImage,
          });
        }
        groupsRef.current = groups;
        orbitRadiiRef.current = d.constants.orbitRadii;

        // Kick off sprite atlas load (re-renders on each sheet ready).
        atlasRef.current = loadSpriteAtlas(d, ATLAS_ZOOM, () => {
          dirtyRef.current = true;
        });

        const b = computeBounds(nodes);
        const w = b.maxX - b.minX;
        const h = b.maxY - b.minY;
        const scale = Math.min(width / w, height / h) * 0.9;
        cameraRef.current = {
          cx: (b.minX + b.maxX) / 2,
          cy: (b.minY + b.maxY) / 2,
          scale,
        };
        dirtyRef.current = true;
        setNodeCount(nodes.length);
        setLoaded(true);
      })
      .catch((e) => { if (!cancelled) setError(String(e)); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showAscendancy, width, height, selectedAscendancy]);

  // Single rAF loop — only redraws when dirtyRef is set.
  useEffect(() => {
    if (!loaded) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const draw = () => {
      if (!dirtyRef.current) {
        rafRef.current = requestAnimationFrame(draw);
        return;
      }
      dirtyRef.current = false;

      const cam = cameraRef.current;
      const nodes = nodesRef.current;
      const groups = groupsRef.current;
      const byId = nodeByIdRef.current;
      const hoveredId = hoveredIdRef.current;
      const atlas = atlasRef.current;

      ctx.fillStyle = "#0c0c0c";
      ctx.fillRect(0, 0, width, height);

      // 0) Background tile — POE의 별/대륙 텍스처
      const atlasScaleBg = atlas ? parseFloat(atlas.zoomKey) : 0.2972;
      const bgSheet2 = atlas?.sheets.get("background");
      if (bgSheet2?.loaded) {
        const coord = bgSheet2.coords["Background2"] || bgSheet2.coords[Object.keys(bgSheet2.coords)[0]];
        if (coord) {
          // 타일 크기 world 단위
          const tileW = (coord.w / atlasScaleBg) * cam.scale;
          const tileH = (coord.h / atlasScaleBg) * cam.scale;
          if (tileW > 2 && tileH > 2) {
            // 화면 좌상단의 world 좌표
            const worldLeft = cam.cx - width / 2 / cam.scale;
            const worldTop = cam.cy - height / 2 / cam.scale;
            // 첫 타일 시작 위치 (world 좌표 기준)
            const startX = Math.floor(worldLeft / (coord.w / atlasScaleBg)) * (coord.w / atlasScaleBg);
            const startY = Math.floor(worldTop / (coord.h / atlasScaleBg)) * (coord.h / atlasScaleBg);
            for (let wy = startY; wy < worldTop + height / cam.scale; wy += coord.h / atlasScaleBg) {
              for (let wx = startX; wx < worldLeft + width / cam.scale; wx += coord.w / atlasScaleBg) {
                const sx = (wx - cam.cx) * cam.scale + width / 2;
                const sy = (wy - cam.cy) * cam.scale + height / 2;
                ctx.drawImage(bgSheet2.image, coord.x, coord.y, coord.w, coord.h, sx, sy, tileW, tileH);
              }
            }
          }
        }
      }

      const w2sx = (wx: number) => (wx - cam.cx) * cam.scale + width / 2;
      const w2sy = (wy: number) => (wy - cam.cy) * cam.scale + height / 2;

      // 1) Group backgrounds (drawn behind nodes/lines)
      const bgSheet = atlas?.sheets.get("groupBackground");
      if (bgSheet?.loaded) {
        // World→atlas pixel scale: atlas was authored at zoom level 0.2972 (px per world unit).
        const atlasScale = parseFloat(atlas!.zoomKey);
        for (const g of groups) {
          if (!g.bgKey) continue;
          const coord = bgSheet.coords[g.bgKey];
          if (!coord) continue;
          const sx = w2sx(g.group.x);
          const sy = w2sy(g.group.y);
          const dw = (coord.w / atlasScale) * cam.scale;
          const dh = (coord.h / atlasScale) * cam.scale;
          if (g.isHalf) {
            // Draw the half image at offset, then mirror for bottom half.
            ctx.drawImage(
              bgSheet.image, coord.x, coord.y, coord.w, coord.h,
              sx - dw / 2, sy - dh, dw, dh,
            );
            ctx.save();
            ctx.translate(sx, sy);
            ctx.scale(1, -1);
            ctx.drawImage(
              bgSheet.image, coord.x, coord.y, coord.w, coord.h,
              -dw / 2, 0, dw, dh,
            );
            ctx.restore();
          } else {
            ctx.drawImage(
              bgSheet.image, coord.x, coord.y, coord.w, coord.h,
              sx - dw / 2, sy - dh / 2, dw, dh,
            );
          }
        }
      }

      // 2) Edges — 기본은 dim(unallocated), 양끝 allocated면 bright
      const allocatedSet = allocatedRef.current;
      const dimStyle = "rgba(95, 80, 60, 0.85)";  // unallocated
      const activeStyle = "rgba(255, 200, 100, 0.95)";  // allocated
      ctx.lineWidth = Math.max(2, Math.min(10, 14 * cam.scale));
      ctx.lineCap = "round";
      const groupById = new Map<string, TreeGroup>();
      for (const g of groups) groupById.set(g.id, g.group);
      const orbitRadii = orbitRadiiRef.current;

      // Unallocated 직선: POE line sprite (텍스처). Allocated: stroke bright.
      const lineSheet = atlas?.sheets.get("line");
      const lineCoordNormal = lineSheet?.coords["LineConnectorNormal"];
      // sprite 높이를 stroke 두께에 맞춰 비율 계산
      const strokeWidth = Math.max(2, Math.min(10, 14 * cam.scale));
      const spriteHeight = strokeWidth;
      const useLineSprite = lineSheet?.loaded && lineCoordNormal && cam.scale > 0.05;

      for (const r of nodes) {
        const outs = r.node.out;
        if (!outs) continue;
        const sax = w2sx(r.x);
        const say = w2sy(r.y);
        // POE 데이터의 out은 단방향 — 각 엣지가 정확히 한 쪽의 out에만 존재하므로
        // string-id dedup 하면 절반이 사라진다. 중복 없이 바로 순회.
        for (const targetId of outs) {
          const t = byId.get(targetId);
          if (!t) continue;
          // Filter cross-class start links (Scion-style class start interconnects)
          if (r.kind === "classStart" && t.kind === "classStart") continue;
          // Filter mastery links (mastery has its own visual, not connected by lines)
          if (r.kind === "mastery" || t.kind === "mastery") continue;
          // Filter long cross-group jumps that are usually data artifacts
          const dx = r.x - t.x, dy = r.y - t.y;
          if (dx * dx + dy * dy > 1500 * 1500) continue;

          const sbx = w2sx(t.x);
          const sby = w2sy(t.y);

          const sameGroup = r.node.group != null && r.node.group === t.node.group;
          const sameOrbit = r.node.orbit != null && r.node.orbit === t.node.orbit;

          // 양끝 할당 여부에 따라 색 결정
          const bothAllocated = allocatedSet.has(r.id) && allocatedSet.has(t.id);
          ctx.strokeStyle = bothAllocated ? activeStyle : dimStyle;

          // 인접 orbitIndex (slot diff=1, wrap 포함)일 때만 arc로. 비인접은 chord.
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
              const radius = orbitRadii[r.node.orbit] * cam.scale;
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

          // 직선: unallocated는 sprite, allocated는 stroke
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

      ctx.shadowBlur = 0;  // Reset shadow before node draws
      // 3) Nodes — sprite (icon + frame) with circle fallback. Sized at atlas-native scale.
      const margin = 80;
      const atlasScale = atlas ? parseFloat(atlas.zoomKey) : 0.2972;
      const allocated = allocatedRef.current;
      // Active/Inactive 시트 분리 — 기본은 Inactive, 할당된 노드만 Active
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

        // POE 렌더 관례: atlas-native 크기의 약 0.55배가 실제 노드 크기
        // (atlas coord에 프레임 아트 외 여백 포함). 이렇게 하면 인접 orbit에서 선이 보임.
        const ICON_SCALE = 0.55;
        const FRAME_SCALE = 0.65;

        if (r.kind === "mastery") {
          if (r.node.icon && masterySheet) {
            const ok = drawSpriteNative(
              ctx, masterySheet, r.node.icon, sx, sy, atlasScale, cam.scale, ICON_SCALE,
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
                ctx, iconSrc, r.node.icon, sx, sy, atlasScale, cam.scale, ICON_SCALE,
              );
              if (ok) drewSprite = true;
            }
          }

          const frameKey = (isAllocated ? FRAME_ALLOCATED : FRAME_UNALLOCATED)[r.kind];
          if (frameKey && frameSheet) {
            const ok = drawSpriteNative(
              ctx, frameSheet, frameKey, sx, sy, atlasScale, cam.scale, FRAME_SCALE,
            );
            if (ok) drewSprite = true;
          }
        }

        if (!drewSprite) {
          const radius = Math.max(1.5, r.radius * cam.scale);
          ctx.beginPath();
          ctx.arc(sx, sy, radius, 0, Math.PI * 2);
          ctx.fillStyle = NODE_COLORS[r.kind];
          ctx.fill();
        }

        if (hoveredId === r.id) {
          const hr = Math.max(8, r.radius * cam.scale * 1.4);
          ctx.beginPath();
          ctx.arc(sx, sy, hr, 0, Math.PI * 2);
          ctx.strokeStyle = "#fff";
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        // 검색 매칭 링 (밝은 시안, 호버와 구분)
        if (searchMatchesRef.current.has(r.id)) {
          const hr = Math.max(10, r.radius * cam.scale * 1.6);
          ctx.beginPath();
          ctx.arc(sx, sy, hr, 0, Math.PI * 2);
          ctx.strokeStyle = "rgba(93, 173, 226, 0.95)";
          ctx.lineWidth = 3;
          ctx.stroke();
        }
      }

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(rafRef.current);
  }, [loaded, width, height]);

  // Keyboard: Ctrl+Z / Ctrl+Y → undo / redo
  useEffect(() => {
    if (!loaded) return;
    const onKey = (e: KeyboardEvent) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      const key = e.key.toLowerCase();
      if (key === "f") {
        e.preventDefault();
        searchInputRef.current?.focus();
        searchInputRef.current?.select();
        return;
      }
      if (key === "z" && !e.shiftKey) {
        const restored = undoRef.current.undo(allocatedRef.current);
        if (restored) {
          allocatedRef.current = restored;
          dirtyRef.current = true;
          recomputePoints();
          onAllocationChangeRef.current?.(new Set(restored));
          e.preventDefault();
        }
      } else if (key === "y" || (key === "z" && e.shiftKey)) {
        const restored = undoRef.current.redo(allocatedRef.current);
        if (restored) {
          allocatedRef.current = restored;
          dirtyRef.current = true;
          recomputePoints();
          onAllocationChangeRef.current?.(new Set(restored));
          e.preventDefault();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loaded]);

  // Pointer interactions — mutate refs, mark dirty, no React state churn.
  useEffect(() => {
    if (!loaded) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    let dragging = false;
    let lastX = 0, lastY = 0;

    const pickNode = (sx: number, sy: number): ResolvedNode | null => {
      const cam = cameraRef.current;
      const wx = (sx - width / 2) / cam.scale + cam.cx;
      const wy = (sy - height / 2) / cam.scale + cam.cy;
      let best: ResolvedNode | null = null;
      let bestDist = Infinity;
      for (const r of nodesRef.current) {
        const dx = r.x - wx, dy = r.y - wy;
        const rr = r.radius;
        const d2 = dx * dx + dy * dy;
        if (d2 <= rr * rr && d2 < bestDist) {
          bestDist = d2; best = r;
        }
      }
      return best;
    };

    let downX = 0, downY = 0;
    const onMouseDown = (e: MouseEvent) => {
      if (e.button !== 0) return;  // 왼클릭만 드래그 시작
      dragging = true;
      downX = e.clientX; downY = e.clientY;
      lastX = e.clientX; lastY = e.clientY;
      canvas.style.cursor = "grabbing";
    };
    const onMouseUp = (e: MouseEvent) => {
      if (e.button !== 0) return;  // 왼클릭만 allocation 처리
      dragging = false;
      canvas.style.cursor = "grab";
      // 드래그가 아닌 클릭이면 할당 — 우클릭은 contextmenu 핸들러에서 dealloc
      const moved = Math.abs(e.clientX - downX) + Math.abs(e.clientY - downY);
      if (moved < 4) {
        const rect = canvas.getBoundingClientRect();
        const sx = e.clientX - rect.left;
        const sy = e.clientY - rect.top;
        const hit = pickNode(sx, sy);
        if (hit && hit.kind !== "mastery") {
          // 선택된 class/ascendancy start는 해제 불가
          if (selectedClass != null && hit.id === CLASS_START_IDS[selectedClass]) {
            return;
          }
          if (selectedAscendancy && hit.id === ascStartIdsRef.current[selectedAscendancy]) {
            return;
          }
          const alloc = allocatedRef.current;
          undoRef.current.push(alloc);
          if (alloc.has(hit.id)) {
            // 할당된 노드 클릭 → cascade dealloc (고아 정리)
            deallocWithCascade(hit.id, alloc, anchorsRef.current, adjRef.current);
          } else if (alloc.size === 0) {
            alloc.add(hit.id);
          } else {
            const path = shortestPath(alloc, hit.id, adjRef.current);
            if (path.length === 0) {
              alloc.add(hit.id);
            } else {
              for (const nid of path) alloc.add(nid);
            }
          }
          dirtyRef.current = true;
          recomputePoints();
          onAllocationChangeRef.current?.(new Set(alloc));
        }
      }
    };
    const onMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;

      if (dragging) {
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX; lastY = e.clientY;
        const cam = cameraRef.current;
        cam.cx -= dx / cam.scale;
        cam.cy -= dy / cam.scale;
        dirtyRef.current = true;
        // Hide tooltip while dragging
        if (tooltip) setTooltip(null);
        hoveredIdRef.current = null;
        return;
      }

      const hit = pickNode(sx, sy);
      const newId = hit?.id ?? null;
      if (newId !== hoveredIdRef.current) {
        hoveredIdRef.current = newId;
        dirtyRef.current = true;
        if (hit) {
          setTooltip({
            name: hit.node.name || "",
            stats: hit.node.stats || [],
            sx, sy,
          });
        } else {
          setTooltip(null);
        }
      } else if (hit) {
        // Same node, just update tooltip position
        setTooltip((prev) =>
          prev ? { ...prev, sx, sy } : prev,
        );
      }
    };
    const onMouseLeave = () => {
      hoveredIdRef.current = null;
      dirtyRef.current = true;
      setTooltip(null);
    };
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left;
      const sy = e.clientY - rect.top;
      const cam = cameraRef.current;
      const wx = (sx - width / 2) / cam.scale + cam.cx;
      const wy = (sy - height / 2) / cam.scale + cam.cy;
      const factor = Math.exp(-e.deltaY * 0.0015);
      cam.scale = Math.max(0.02, Math.min(3, cam.scale * factor));
      cam.cx = wx - (sx - width / 2) / cam.scale;
      cam.cy = wy - (sy - height / 2) / cam.scale;
      dirtyRef.current = true;
    };

    canvas.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mouseup", onMouseUp);
    canvas.addEventListener("mousemove", onMouseMove);
    canvas.addEventListener("mouseleave", onMouseLeave);
    canvas.addEventListener("wheel", onWheel, { passive: false });
    canvas.style.cursor = "grab";
    return () => {
      canvas.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mouseup", onMouseUp);
      canvas.removeEventListener("mousemove", onMouseMove);
      canvas.removeEventListener("mouseleave", onMouseLeave);
      canvas.removeEventListener("wheel", onWheel);
    };
    // dragMoved is local; tooltip read intentionally tracked.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loaded, width, height]);

  if (error) {
    return (
      <div style={{ padding: 16, color: "#ff6b6b" }}>
        패시브 트리 데이터 로드 실패: {error}
      </div>
    );
  }

  return (
    <div style={{ position: "relative", width, height }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          display: "block",
          border: "1px solid #dee2e6",
          borderRadius: 4,
          background: "#1a1a1a",
        }}
      />
      {!loaded && (
        <div
          style={{
            position: "absolute", left: 0, top: 0, width, height,
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "#868e96", fontSize: 13, pointerEvents: "none",
          }}
        >
          패시브 트리 데이터 로드 중…
        </div>
      )}
      {loaded && (
        <>
          {/* 좌상단 클래스 + 어센던시 드롭다운 */}
          <div
            style={{
              position: "absolute", left: 8, top: 8,
              display: "flex", gap: 6, alignItems: "center",
            }}
          >
            <select
              value={selectedClass ?? ""}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "") return;
                pickClass(parseInt(v, 10));
              }}
              style={{
                padding: "5px 10px", fontSize: 12,
                background: selectedClass != null ? "#e8c068" : "rgba(0,0,0,0.75)",
                color: selectedClass != null ? "#000" : "#ccc",
                border: `1px solid ${selectedClass != null ? "#e8c068" : "#4a3f2a"}`,
                borderRadius: 3, cursor: "pointer",
                fontWeight: selectedClass != null ? 700 : 400,
                outline: "none",
              }}
            >
              <option value="" disabled>클래스 선택</option>
              {CLASS_NAMES.map((name, i) => (
                <option key={i} value={i}>{name}</option>
              ))}
            </select>
            {selectedClass != null && ASCENDANCIES[selectedClass] && (
              <select
                value={selectedAscendancy ?? ""}
                onChange={(e) => pickAscendancy(e.target.value || null)}
                style={{
                  padding: "5px 10px", fontSize: 12,
                  background: selectedAscendancy ? "#5dade2" : "rgba(0,0,0,0.75)",
                  color: selectedAscendancy ? "#000" : "#ccc",
                  border: `1px solid ${selectedAscendancy ? "#5dade2" : "#2a3f4a"}`,
                  borderRadius: 3, cursor: "pointer",
                  fontWeight: selectedAscendancy ? 700 : 400,
                  outline: "none",
                }}
              >
                <option value="">어센던시 없음</option>
                {ASCENDANCIES[selectedClass].map((asc) => (
                  <option key={asc} value={asc}>{asc}</option>
                ))}
              </select>
            )}
          </div>
          <div style={{ position: "absolute", right: 8, top: 8, display: "flex", gap: 6, alignItems: "center" }}>
            <input
              ref={searchInputRef}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="검색 (Ctrl+F)"
              style={{
                width: 160, padding: "3px 8px", fontSize: 11,
                background: "rgba(0,0,0,0.75)", color: "#fff",
                border: "1px solid #4a3f2a", borderRadius: 3,
                outline: "none",
              }}
            />
            {searchQuery && (
              <span
                style={{
                  background: "rgba(0,0,0,0.75)", color: "#5dade2",
                  padding: "2px 8px", borderRadius: 3, fontSize: 10,
                }}
              >
                {searchMatchesRef.current.size} matches
              </span>
            )}
            <span
              style={{
                background: "rgba(0,0,0,0.6)", color: "#aaa",
                padding: "2px 8px", borderRadius: 3, fontSize: 10,
              }}
            >
              {nodeCount} nodes
            </span>
          </div>
          <div
            style={{
              position: "absolute", left: 8, bottom: 8,
              background: "rgba(0,0,0,0.75)", color: "#e8c068",
              padding: "4px 10px", borderRadius: 3, fontSize: 12,
              border: "1px solid #4a3f2a", pointerEvents: "none",
              fontWeight: 600,
            }}
          >
            {pointsUsed} pts{jewelSockets > 0 && ` · ${jewelSockets} sockets`}
          </div>
          <div
            style={{
              position: "absolute", right: 8, bottom: 8,
              background: "rgba(0,0,0,0.82)", color: "#bbb",
              padding: "8px 12px", borderRadius: 4, fontSize: 11,
              border: "1px solid #4a3f2a", pointerEvents: "none",
              maxWidth: 260, lineHeight: 1.5,
            }}
          >
            <div style={{ color: "#e8c068", fontWeight: 600, marginBottom: 4 }}>
              사용법
            </div>
            <div><b style={{ color: "#fff" }}>좌클릭</b> 빈 노드 — 최단 경로로 자동 할당</div>
            <div><b style={{ color: "#fff" }}>좌클릭</b> 할당된 노드 — 해당 노드 + 도달 불가 하위 해제</div>
            <div><b style={{ color: "#fff" }}>드래그</b> — 이동 · <b style={{ color: "#fff" }}>휠</b> — 줌</div>
            <div><b style={{ color: "#fff" }}>Ctrl+Z / Ctrl+Y</b> — 되돌리기 / 다시</div>
            <div><b style={{ color: "#fff" }}>Ctrl+F</b> — 노드 검색 (이름/옵션)</div>
          </div>
        </>
      )}
      {tooltip && (
        <div
          style={{
            position: "absolute",
            left: Math.min(tooltip.sx + 14, width - 320),
            top: Math.min(tooltip.sy + 14, height - 100),
            background: "rgba(0,0,0,0.92)",
            color: "#fff",
            padding: "8px 12px",
            borderRadius: 4,
            fontSize: 12,
            maxWidth: 320,
            pointerEvents: "none",
            border: "1px solid #4a3f2a",
            zIndex: 10,
          }}
        >
          <div style={{ fontWeight: "bold", marginBottom: 4, color: "#e8c068" }}>
            {tooltip.name || "(unnamed)"}
          </div>
          {tooltip.stats.length === 0 ? (
            <div style={{ color: "#666", fontStyle: "italic" }}>(no stats)</div>
          ) : (
            tooltip.stats.map((s, i) => (
              <div key={i} style={{ color: "#bbb" }}>{s}</div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
