// Constants shared by PassiveTreeCanvas and its helpers.
// Kept in /utils since they have no React / DOM dependency.

import type { TreeNode } from "./passiveTree";

// Atlas zoom level. Single level for Phase 1b — auto-switching deferred.
export const ATLAS_ZOOM = "0.2972";

export const SKILLS_PER_ORBIT = [1, 6, 16, 16, 40, 72, 72];

// Class start node IDs (from data.json sampling)
export const CLASS_START_IDS: Record<number, string> = {
  0: "58833", // Scion
  1: "47175", // Marauder
  2: "50459", // Ranger
  3: "54447", // Witch
  4: "50986", // Duelist
  5: "61525", // Templar
  6: "44683", // Shadow
};

export const CLASS_NAMES = [
  "Scion", "Marauder", "Ranger", "Witch", "Duelist", "Templar", "Shadow",
];

// Ascendancy 구성 (data.classes 구조 기준, bloodline 제외)
export const ASCENDANCIES: Record<number, string[]> = {
  0: ["Ascendant", "Reliquarian"],
  1: ["Juggernaut", "Berserker", "Chieftain"],
  2: ["Warden", "Deadeye", "Pathfinder"],
  3: ["Occultist", "Elementalist", "Necromancer"],
  4: ["Slayer", "Gladiator", "Champion"],
  5: ["Inquisitor", "Hierophant", "Guardian"],
  6: ["Assassin", "Trickster", "Saboteur"],
};

export const CLASS_STORAGE_KEY = "pathcraftai_passive_class";
export const ASCENDANCY_STORAGE_KEY = "pathcraftai_passive_ascendancy";

export const FRAME_UNALLOCATED: Record<string, string> = {
  normal: "PSSkillFrame",
  notable: "NotableFrameUnallocated",
  keystone: "KeystoneFrameUnallocated",
  jewel: "JewelFrameUnallocated",
  ascendancy: "PSSkillFrame",
  classStart: "PSSkillFrame",
};

export const FRAME_ALLOCATED: Record<string, string> = {
  normal: "PSSkillFrameActive",
  notable: "NotableFrameAllocated",
  keystone: "KeystoneFrameAllocated",
  jewel: "JewelFrameAllocated",
  ascendancy: "PSSkillFrameActive",
  classStart: "PSSkillFrameActive",
};

export type NodeKind =
  | "normal" | "notable" | "keystone" | "mastery"
  | "jewel" | "ascendancy" | "classStart";

export const NODE_COLORS: Record<NodeKind, string> = {
  normal: "#a89572",
  notable: "#e8c068",
  keystone: "#e74c3c",
  mastery: "#9b59b6",
  jewel: "#5dade2",
  ascendancy: "#f1c40f",
  classStart: "#ecf0f1",
};

export const NODE_RADIUS_WORLD: Record<NodeKind, number> = {
  normal: 22, notable: 38, keystone: 50, mastery: 32,
  jewel: 36, classStart: 70, ascendancy: 24,
};

export function classifyNode(node: TreeNode): NodeKind {
  if (node.classStartIndex != null) return "classStart";
  if (node.isKeystone) return "keystone";
  if (node.isJewelSocket) return "jewel";
  if (node.isMastery) return "mastery";
  if (node.isNotable) return "notable";
  if (node.ascendancyName) return "ascendancy";
  return "normal";
}
