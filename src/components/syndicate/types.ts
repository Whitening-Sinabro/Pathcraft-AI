import { colors } from "../../theme";
import {
  DIVISIONS as ENGINE_DIVISIONS,
  type Division as EngineDivision,
  type Rank,
  type SyndicateMember,
} from "../../utils/syndicateEngine";

export type { Rank, SyndicateMember };

// engine이 canonical — 단일 진실원 유지 (2-source drift 방지)
export const DIVISIONS = ENGINE_DIVISIONS as readonly EngineDivision[];
export type Division = EngineDivision;

export interface VisionDivisionSlot { member_id: string; rank: Rank; }
export interface VisionResult {
  divisions: Record<string, VisionDivisionSlot[]>;
  confidence: "high" | "medium" | "low";
  notes: string;
  diagnostics: { unknown_members: Array<{ div: string; raw: string }>; invalid_ranks: unknown[] };
  error?: string;
}

export interface SyndicateLayout {
  id: string;
  name: string;
  strategy: string;
  priority: string;
  board: Record<string, string[]>;
  rewards_focus: string[];
  /** S1 이후 deprecated 프리셋 마킹 (ss22 등). UI는 숨기거나 legacy 섹션으로 분리. */
  deprecated?: boolean;
  deprecated_since?: string;
  deprecated_reason?: string;
  /** HCSSF 전용 프리셋 표시 */
  hcssf_safe?: boolean;
  /** 선결 rank (UI 힌트용, 선택) */
  required_ranks?: Record<string, number>;
}

export interface SyndicateData { members: SyndicateMember[]; }
export interface LayoutData { layouts: SyndicateLayout[]; }

/** 액션 타입별 색상 — UI 공통 */
export function actionColor(action: string): string {
  switch (action) {
    case "Bargain":     return "var(--status-info)";
    case "Interrogate": return "var(--accent-hover)";
    case "Betray":      return "var(--status-danger)";
    case "Execute":     return "var(--status-warning)";
    case "Capture":     return "var(--status-success)";
    default:            return "var(--text-secondary)";
  }
}

/** 분과 색 — theme.ts colors.syndicate (CSS 변수 alias) 단일 진실원 */
export const DIVISION_COLORS: Record<Division, { bg: string; text: string; border: string }> = {
  Transportation: colors.syndicate.transportation,
  Fortification:  colors.syndicate.fortification,
  Research:       colors.syndicate.research,
  Intervention:   colors.syndicate.intervention,
};
