import { useEffect, useMemo, useRef, useState } from "react";
import {
  resolveNodePosition,
  buildAdjacency,
  shortestPath,
  deallocWithCascade,
  normalizePoe2Tree,
  type TreeData,
  type TreeNode,
  type Poe2RawTree,
} from "../utils/passiveTree";
import { createUndoHandler, type UndoHandler } from "../utils/passiveTreeUndo";
import { loadSpriteAtlas, type SpriteAtlas } from "../utils/passiveTreeSprites";
import {
  ATLAS_ZOOM,
  CLASS_START_IDS, ASCENDANCIES, CLASS_NAMES,
  POE2_CLASS_START_IDS_BY_INDEX, POE2_ASCENDANCIES, POE2_CLASS_NAMES,
  CLASS_STORAGE_KEY, ASCENDANCY_STORAGE_KEY,
  NODE_RADIUS_WORLD,
  classifyNode,
} from "../utils/passiveTreeConstants";
import {
  drawFrame,
  type ResolvedNode, type ResolvedGroup, type Camera,
} from "../utils/passiveTreeRender";
import {
  translateStat,
  type TranslationTable,
} from "../utils/passiveTreeTranslate";
import { TreeControls } from "./passive-tree/TreeControls";
import { ClassPortrait } from "./passive-tree/ClassPortrait";
import { logger } from "../utils/logger";
import poe1DataUrl from "../../data/skilltree-export/data.json?url";
import poe2DataUrl from "../../data/skilltree-export-poe2/tree_0_4.json?url";
import translationsUrl from "../../data/skilltree-export/passive_tree_translations.json?url";

type Game = "poe1" | "poe2";

interface Props {
  width?: number;
  height?: number;
  showAscendancy?: boolean;
  // POE1/POE2 분기. 기본 "poe1" 유지 (기존 호출부 무변경).
  game?: Game;
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
  game = "poe1",
  initialAllocated, buildClass, buildAscendancy, onAllocationChange,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Game-aware look-up tables. POE2 는 classesStart[] 기반이라 POE1 의 0~6 index
  // 와 다른 0~7 레인지. 모든 소비 코드는 여기서 받은 테이블만 참조.
  const gameTables = useMemo(() => {
    if (game === "poe2") {
      return {
        classStartIds: POE2_CLASS_START_IDS_BY_INDEX,
        ascendancies: POE2_ASCENDANCIES,
        classNames: POE2_CLASS_NAMES,
        dataUrl: poe2DataUrl,
        maxClassIdx: POE2_CLASS_NAMES.length - 1,
      };
    }
    return {
      classStartIds: CLASS_START_IDS,
      ascendancies: ASCENDANCIES,
      classNames: CLASS_NAMES,
      dataUrl: poe1DataUrl,
      maxClassIdx: CLASS_NAMES.length - 1,
    };
  }, [game]);

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
  // P1: 7 class portrait DOM overlay refs (ClassPortrait wrappers, position: absolute).
  // Imperative style.transform 업데이트로 camera pan/zoom sync. pointer-events: none.
  const portraitRefs = useRef<Array<HTMLDivElement | null>>([null, null, null, null, null, null, null]);
  const onAllocationChangeRef = useRef(onAllocationChange);
  onAllocationChangeRef.current = onAllocationChange;

  // React state only for things that affect DOM (tooltip text, loading status).
  const [tooltip, setTooltip] = useState<{ name: string; stats: string[]; sx: number; sy: number } | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // 한국어 stat 템플릿 사전 — 로드 실패 시 영문 fallback (POE1 전용)
  const [translations, setTranslations] = useState<TranslationTable | null>(null);
  const [nodeCount, setNodeCount] = useState(0);
  // 포인트 카운터 (classStart/ascendancyStart 제외 + jewel sockets)
  const [pointsUsed, setPointsUsed] = useState(0);
  const [jewelSockets, setJewelSockets] = useState(0);
  // 검색 하이라이트
  const [searchQuery, setSearchQuery] = useState("");
  const searchMatchesRef = useRef<Set<string>>(new Set());
  const searchInputRef = useRef<HTMLInputElement>(null);
  // localStorage 키는 game 별 분리 — POE1/POE2 클래스 index 공간이 다르기 때문.
  const classStorageKey = game === "poe2" ? `${CLASS_STORAGE_KEY}_poe2` : CLASS_STORAGE_KEY;
  const ascStorageKey = game === "poe2" ? `${ASCENDANCY_STORAGE_KEY}_poe2` : ASCENDANCY_STORAGE_KEY;
  // 선택된 클래스 — buildClass가 있으면 그 값 우선, 없으면 localStorage
  const [selectedClass, setSelectedClass] = useState<number | null>(() => {
    const max = gameTables.maxClassIdx;
    if (buildClass != null && buildClass >= 0 && buildClass <= max) return buildClass;
    try {
      const saved = localStorage.getItem(classStorageKey);
      if (saved == null) return null;
      const n = parseInt(saved, 10);
      return Number.isFinite(n) && n >= 0 && n <= max ? n : null;
    } catch { return null; }
  });
  const [selectedAscendancy, setSelectedAscendancy] = useState<string | null>(() => {
    if (buildClass != null && buildAscendancy != null && buildAscendancy > 0) {
      const list = gameTables.ascendancies[buildClass];
      if (list && list[buildAscendancy - 1]) return list[buildAscendancy - 1];
    }
    try { return localStorage.getItem(ascStorageKey); } catch { return null; }
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

  // 클래스 변경 시 트리 완전 리셋. class start는 **anchor**로만 유지 (캐릭터 마커), 할당 세트는 비움.
  function pickClass(classIdx: number) {
    const startId = gameTables.classStartIds[classIdx];
    if (!startId) return;
    const prevSize = allocatedRef.current.size;
    undoRef.current.push(allocatedRef.current);

    // 완전히 빈 할당 — 클래스 선택 ≠ 노드 찍기. 클래스 시작점은 anchor로만 유지.
    allocatedRef.current = new Set<string>();
    hoveredIdRef.current = null;
    searchMatchesRef.current = new Set();
    setSearchQuery("");
    logger.info(`[passiveTree:${game}] pickClass ${classIdx} → startId=${startId} (anchor only), allocated ${prevSize} → 0`);

    setSelectedClass(classIdx);
    setSelectedAscendancy(null);
    try {
      localStorage.setItem(classStorageKey, String(classIdx));
      localStorage.removeItem(ascStorageKey);
    } catch { /* quota full */ }
    anchorsRef.current = new Set([startId]);

    // 클래스 시작점으로 카메라 이동 + 적당한 줌인
    const startNode = nodeByIdRef.current.get(startId);
    if (startNode) {
      cameraRef.current = {
        cx: startNode.x,
        cy: startNode.y,
        scale: Math.max(cameraRef.current.scale, 0.05),
      };
    }

    dirtyRef.current = true;
    recomputePoints();
    onAllocationChangeRef.current?.(new Set(allocatedRef.current));
  }

  // 어센던시 변경 — 기존 ascendancy 노드 제거. 새 ascendancy start는 anchor 업데이트(할당 아님)
  function pickAscendancy(ascName: string | null) {
    const alloc = allocatedRef.current;
    undoRef.current.push(alloc);
    // 기존 모든 ascendancy 노드 제거 (할당된 것만 — anchor는 Set 외)
    const rawNodes = rawNodesRef.current;
    for (const id of [...alloc]) {
      const n = rawNodes[id];
      if (n?.ascendancyName) alloc.delete(id);
    }
    // ascendancy start는 anchors에 포함, 할당에 넣지 않음
    const startClassId = selectedClass != null ? gameTables.classStartIds[selectedClass] : null;
    const nextAnchors = new Set<string>();
    if (startClassId) nextAnchors.add(startClassId);
    if (ascName) {
      const startId = ascStartIdsRef.current[ascName];
      if (startId) nextAnchors.add(startId);
    }
    anchorsRef.current = nextAnchors;
    setSelectedAscendancy(ascName);
    try {
      if (ascName) localStorage.setItem(ascStorageKey, ascName);
      else localStorage.removeItem(ascStorageKey);
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

  // Load Korean translation table once (POE1 전용 — POE2 번역은 D4 범위 밖).
  // Failure is non-fatal — tooltip falls back to English source strings.
  useEffect(() => {
    if (game !== "poe1") { setTranslations(null); return; }
    let cancelled = false;
    fetch(translationsUrl)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<TranslationTable>;
      })
      .then((t) => {
        if (cancelled) return;
        setTranslations(t);
      })
      .catch((err: unknown) => {
        // Translation is best-effort; English fallback is acceptable.
        // Still surface the failure so stale/missing translations don't go unnoticed.
        logger.warn("[passiveTree] translation load failed:", err);
      });
    return () => { cancelled = true; };
  }, [game]);

  // Load tree data — reload nodes when ascendancy changes (filter dependency).
  // POE2 tree.json 은 normalizePoe2Tree 로 POE1-shape 로 변환 후 동일 파이프라인.
  useEffect(() => {
    let cancelled = false;
    fetch(gameTables.dataUrl)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<TreeData | Poe2RawTree>;
      })
      .then((raw) => {
        if (cancelled) return;
        const d: TreeData = game === "poe2"
          ? normalizePoe2Tree(raw as Poe2RawTree)
          : (raw as TreeData);
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
        // 앵커는 "할당 세트"와 별도 — 시각만 active로 렌더, 할당 카운트 0 유지
        if (selectedClass != null && gameTables.classStartIds[selectedClass]) {
          const startId = gameTables.classStartIds[selectedClass];
          const anchors = new Set<string>([startId]);
          if (selectedAscendancy && ascMap[selectedAscendancy]) {
            anchors.add(ascMap[selectedAscendancy]);
          }
          anchorsRef.current = anchors;
        } else {
          // POE1: classStartIndex 로 앵커. POE2: classesStart 존재로 앵커.
          const anchors = new Set<string>();
          for (const n of nodes) {
            if (n.node.classStartIndex != null) anchors.add(n.id);
            else if (n.node.classesStart && n.node.classesStart.length > 0) anchors.add(n.id);
          }
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
        const overviewScale = Math.min(width / w, height / h) * 0.9;
        // 선택된 클래스가 있으면 시작점으로 줌인, 아니면 전체 뷰
        const nodeMap = new Map(nodes.map((n) => [n.id, n]));
        if (selectedClass != null) {
          const startId = gameTables.classStartIds[selectedClass];
          const startNode = startId ? nodeMap.get(startId) : null;
          if (startNode) {
            cameraRef.current = {
              cx: startNode.x,
              cy: startNode.y,
              scale: Math.max(overviewScale, 0.05),
            };
          } else {
            cameraRef.current = {
              cx: (b.minX + b.maxX) / 2,
              cy: (b.minY + b.maxY) / 2,
              scale: overviewScale,
            };
          }
        } else {
          cameraRef.current = {
            cx: (b.minX + b.maxX) / 2,
            cy: (b.minY + b.maxY) / 2,
            scale: overviewScale,
          };
        }
        dirtyRef.current = true;
        setNodeCount(nodes.length);
        setLoaded(true);
      })
      .catch((e) => { if (!cancelled) setError(String(e)); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showAscendancy, width, height, selectedAscendancy, game]);

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
        anchors: anchorsRef.current,
        hoveredId: hoveredIdRef.current,
        searchMatches: searchMatchesRef.current,
        atlas: atlasRef.current,
        orbitRadii: orbitRadiiRef.current,
      });

      // P1: class portrait overlay 재배치. POE1 전용 — POE2 portrait 은 D4 범위 밖.
      // NODE_RADIUS_WORLD.classStart=70 대비 직경 = 2*radius*portraitScale.
      // 호버 링이 1.4x 반경이므로 포트레이트 < 호버 링이어야 함.
      if (game === "poe1") {
        const cam = cameraRef.current;
        const nodeMap = nodeByIdRef.current;
        for (let i = 0; i < 7; i++) {
          const el = portraitRefs.current[i];
          if (!el) continue;
          const nodeId = CLASS_START_IDS[i];
          const node = nodeId ? nodeMap.get(nodeId) : null;
          if (!node) {
            el.style.display = "none";
            continue;
          }
          const diameter = node.radius * 2 * cam.scale;
          const sx = (node.x - cam.cx) * cam.scale + width / 2;
          const sy = (node.y - cam.cy) * cam.scale + height / 2;
          const offscreen = sx < -diameter || sx > width + diameter
                         || sy < -diameter || sy > height + diameter;
          if (offscreen || diameter < 6) {
            el.style.display = "none";
          } else {
            el.style.display = "block";
            el.style.width = `${diameter}px`;
            el.style.height = `${diameter}px`;
            el.style.transform =
              `translate3d(${sx - diameter / 2}px, ${sy - diameter / 2}px, 0)`;
          }
        }
      } else {
        // POE2: portrait refs 모두 숨김
        for (let i = 0; i < 7; i++) {
          const el = portraitRefs.current[i];
          if (el) el.style.display = "none";
        }
      }

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(rafRef.current);
  }, [loaded, width, height, game]);


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
          if (selectedClass != null && hit.id === gameTables.classStartIds[selectedClass]) {
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
          } else {
            // 경로 탐색은 anchors(캐릭터 시작점) ∪ 이미 할당된 노드에서 시작
            const from = new Set<string>([...alloc, ...anchorsRef.current]);
            if (from.size === 0) {
              alloc.add(hit.id);
            } else {
              const path = shortestPath(from, hit.id, adjRef.current);
              if (path.length === 0) {
                alloc.add(hit.id);
              } else {
                for (const nid of path) {
                  // anchors는 "할당"에 포함하지 않음 — 시작점은 영구 marker
                  if (!anchorsRef.current.has(nid)) alloc.add(nid);
                }
              }
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
  }, [loaded, width, height, game]);

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
      {/* P1: 7 class portrait overlay. display:none 초기값, rAF가 좌표 주입. */}
      {[0, 1, 2, 3, 4, 5, 6].map((classIdx) => (
        <div
          key={classIdx}
          ref={(el) => { portraitRefs.current[classIdx] = el; }}
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            display: "none",
            pointerEvents: "none",
            willChange: "transform",
          }}
        >
          <ClassPortrait classIndex={classIdx} />
        </div>
      ))}
      <TreeControls
        loaded={loaded}
        nodeCount={nodeCount}
        classNames={gameTables.classNames}
        ascendancies={gameTables.ascendancies}
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
              <div key={i} style={{ color: "#bbb" }}>
                {translateStat(s, translations)}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
