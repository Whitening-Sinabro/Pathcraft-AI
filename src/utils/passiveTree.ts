// Passive tree geometry + data loader.
// Source: data/skilltree-export/data.json (GGG official export, 3.20+ format)
// Coordinate convention: angle 0 = north (up), clockwise. y-axis grows downward.

export interface TreeNode {
  skill: number;
  name: string;
  icon?: string;
  stats?: string[];
  group?: number;
  orbit?: number;
  orbitIndex?: number;
  in?: string[];
  out?: string[];
  isNotable?: boolean;
  isKeystone?: boolean;
  isMastery?: boolean;
  isJewelSocket?: boolean;
  isProxy?: boolean;
  isAscendancyStart?: boolean;
  isBlighted?: boolean;
  expansionJewel?: unknown;
  ascendancyName?: string;
  classStartIndex?: number;
}

export interface TreeGroup {
  x: number;
  y: number;
  orbits: number[];
  nodes: string[];
  background?: {
    image: string;
    isHalfImage?: boolean;
    offsetX?: number;
    offsetY?: number;
  };
}

export interface TreeConstants {
  PSSCentreInnerRadius: number;
  skillsPerOrbit: number[];
  orbitRadii: number[];
}

export interface TreeData {
  nodes: Record<string, TreeNode>;
  groups: Record<string, TreeGroup>;
  constants: TreeConstants;
  min_x: number;
  min_y: number;
  max_x: number;
  max_y: number;
}

// 16-orbit angle table (orbits 2 and 3 since 3.17).
// Reference: data/skilltree-export/README.md "3.17.0".
const ORBIT_16_ANGLES_DEG = [
  0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330,
];

const DEG_TO_RAD = Math.PI / 180;

/**
 * Compute the polar angle (degrees) for a node at (orbit, orbitIndex).
 * Angle 0 = north (up), clockwise. Caller must convert to radians.
 */
export function nodeAngleDeg(
  orbit: number,
  orbitIndex: number,
  skillsPerOrbit: number[],
): number {
  if (orbit < 0 || orbit >= skillsPerOrbit.length) {
    throw new RangeError(`orbit ${orbit} out of range`);
  }
  const slots = skillsPerOrbit[orbit];
  if (orbitIndex < 0 || orbitIndex >= slots) {
    throw new RangeError(
      `orbitIndex ${orbitIndex} out of range for orbit ${orbit} (slots=${slots})`,
    );
  }
  if (slots === 16) return ORBIT_16_ANGLES_DEG[orbitIndex];
  return (orbitIndex / slots) * 360;
}

/** Absolute (x, y) of a node given its group + orbit indexing. */
export function nodePosition(
  group: { x: number; y: number },
  orbit: number,
  orbitIndex: number,
  constants: TreeConstants,
): { x: number; y: number } {
  const radius = constants.orbitRadii[orbit];
  if (radius == null) {
    throw new RangeError(`orbitRadii missing for orbit ${orbit}`);
  }
  const angle = nodeAngleDeg(orbit, orbitIndex, constants.skillsPerOrbit) * DEG_TO_RAD;
  return {
    x: group.x + radius * Math.sin(angle),
    y: group.y - radius * Math.cos(angle),
  };
}

/**
 * Resolve absolute position for a TreeNode using its group reference.
 * Returns null for orbit-less nodes (e.g. some virtual/proxy nodes).
 */
export function resolveNodePosition(
  node: TreeNode,
  groups: Record<string, TreeGroup>,
  constants: TreeConstants,
): { x: number; y: number } | null {
  if (node.group == null || node.orbit == null || node.orbitIndex == null) {
    return null;
  }
  const group = groups[String(node.group)];
  if (!group) return null;
  return nodePosition(group, node.orbit, node.orbitIndex, constants);
}

/**
 * Build undirected adjacency from a node set's `out` edges.
 * POE data stores each edge in exactly one `out` array.
 */
export function buildAdjacency(
  allowedIds: Set<string>,
  nodes: Record<string, TreeNode>,
): Map<string, string[]> {
  const adj = new Map<string, string[]>();
  const push = (a: string, b: string) => {
    let arr = adj.get(a);
    if (!arr) { arr = []; adj.set(a, arr); }
    if (!arr.includes(b)) arr.push(b);
  };
  for (const id of allowedIds) {
    const node = nodes[id];
    if (!node) continue;
    for (const tid of node.out || []) {
      if (!allowedIds.has(tid)) continue;
      push(id, tid);
      push(tid, id);
    }
  }
  return adj;
}

/**
 * Remove a node and every downstream node that loses its path to `anchors`
 * (class starts) once the node is gone. Mutates `allocated` in place.
 *
 * Reference: PoB PassiveSpec.lua:799-806 (DeallocNode + depends[] cascade).
 */
export function deallocWithCascade(
  nodeId: string,
  allocated: Set<string>,
  anchors: Set<string>,
  adj: Map<string, string[]>,
): void {
  if (!allocated.has(nodeId)) return;
  allocated.delete(nodeId);

  // For each still-allocated node, check reachability to any anchor
  // without passing through already-deallocated nodes.
  const reachable = new Set<string>();
  const queue: string[] = [];
  for (const a of anchors) {
    if (allocated.has(a)) { reachable.add(a); queue.push(a); }
  }
  let head = 0;
  while (head < queue.length) {
    const cur = queue[head++];
    const neighbors = adj.get(cur);
    if (!neighbors) continue;
    for (const nb of neighbors) {
      if (!allocated.has(nb)) continue;
      if (reachable.has(nb)) continue;
      reachable.add(nb);
      queue.push(nb);
    }
  }

  // Drop any allocated node that is not reachable from an anchor.
  for (const id of [...allocated]) {
    if (!reachable.has(id)) allocated.delete(id);
  }
}

/**
 * BFS shortest path from any node in `from` to `target`, traversing only nodes
 * in `adj`. Returns path including target (and excluding from-start interior
 * only if from already contains start). Empty array = unreachable.
 */
export function shortestPath(
  from: Set<string>,
  target: string,
  adj: Map<string, string[]>,
): string[] {
  if (from.has(target)) return [target];
  const prev = new Map<string, string>();
  const visited = new Set<string>(from);
  const queue: string[] = [...from];
  let head = 0;
  while (head < queue.length) {
    const cur = queue[head++];
    const neighbors = adj.get(cur);
    if (!neighbors) continue;
    for (const nb of neighbors) {
      if (visited.has(nb)) continue;
      visited.add(nb);
      prev.set(nb, cur);
      if (nb === target) {
        const path: string[] = [];
        let c: string | undefined = target;
        while (c && !from.has(c)) {
          path.push(c);
          c = prev.get(c);
        }
        return path.reverse();
      }
      queue.push(nb);
    }
  }
  return [];
}
