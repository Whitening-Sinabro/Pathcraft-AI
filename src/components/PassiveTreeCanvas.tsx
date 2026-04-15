import { useEffect, useRef, useState } from "react";
import {
  resolveNodePosition,
  buildAdjacency,
  shortestPath,
  deallocWithCascade,
  type TreeData,
  type TreeNode,
} from "../utils/passiveTree";
import { createUndoHandler, type UndoHandler } from "../utils/passiveTreeUndo";
import { loadSpriteAtlas, type SpriteAtlas } from "../utils/passiveTreeSprites";
import {
  ATLAS_ZOOM,
  CLASS_START_IDS, ASCENDANCIES,
  CLASS_STORAGE_KEY, ASCENDANCY_STORAGE_KEY,
  NODE_RADIUS_WORLD,
  classifyNode,
} from "../utils/passiveTreeConstants";
import {
  drawFrame,
  type ResolvedNode, type ResolvedGroup, type Camera,
} from "../utils/passiveTreeRender";
import { TreeControls } from "./passive-tree/TreeControls";
import dataUrl from "../../data/skilltree-export/data.json?url";


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

      drawFrame({
        ctx,
        width, height,
        camera: cameraRef.current,
        nodes: nodesRef.current,
        groups: groupsRef.current,
        nodeById: nodeByIdRef.current,
        allocated: allocatedRef.current,
        hoveredId: hoveredIdRef.current,
        searchMatches: searchMatchesRef.current,
        atlas: atlasRef.current,
        orbitRadii: orbitRadiiRef.current,
      });

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
      <TreeControls
        loaded={loaded}
        nodeCount={nodeCount}
        selectedClass={selectedClass}
        selectedAscendancy={selectedAscendancy}
        searchQuery={searchQuery}
        searchMatchCount={searchMatchesRef.current.size}
        pointsUsed={pointsUsed}
        jewelSockets={jewelSockets}
        searchInputRef={searchInputRef}
        onPickClass={pickClass}
        onPickAscendancy={pickAscendancy}
        onSearchChange={setSearchQuery}
      />
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
