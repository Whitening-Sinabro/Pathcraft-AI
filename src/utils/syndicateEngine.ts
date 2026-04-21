// PathcraftAI Syndicate Path Engine — current board state → ordered next-action recommendations.

export type Division = "Transportation" | "Fortification" | "Research" | "Intervention";
export type Rank = "Member" | "Leader";

export const DIVISIONS: Division[] = ["Transportation", "Fortification", "Research", "Intervention"];

export interface SlotState {
  memberId: string;
  rank: Rank;
}

export type DivisionBoard = Record<Division, SlotState[]>;
export type TargetBoard = Record<Division, string[]>;

export interface SyndicateMember {
  id: string;
  name: string;
  default_division: string | null;
  tags: string[];
  rewards: Record<string, string>;
}

export type ActionType = "Bargain" | "Interrogate" | "Betray" | "Execute" | "Capture";

/**
 * 액션 비용 벡터 — 실 게임 인카운터/부작용 모델링.
 * encounterTurns: 평균 Jun 인카운터 수 (Capture는 포획 + Bargain 배치 = 2턴)
 * sideEffects: 예상 부작용 키 (UI에서 인덱스해서 경고 표시 가능)
 */
export interface ActionCost {
  encounterTurns: number;
  sideEffects: readonly string[];
}

export const ACTION_COSTS: Record<ActionType, ActionCost> = {
  Capture:     { encounterTurns: 2, sideEffects: [] },
  Bargain:     { encounterTurns: 1, sideEffects: [] },
  Betray:      { encounterTurns: 1, sideEffects: ["same_division_witness_promoted"] },
  Execute:     { encounterTurns: 1, sideEffects: ["same_division_witness_removed"] },
  Interrogate: { encounterTurns: 1, sideEffects: ["rank_down"] },
};

export interface Recommendation {
  action: ActionType;
  targetMemberId: string;
  targetMemberName: string;
  toDivision?: Division;
  reason: string;
  priority: number;
  cost?: ActionCost;
}

export const EMPTY_BOARD: DivisionBoard = {
  Transportation: [],
  Fortification: [],
  Research: [],
  Intervention: [],
};

interface MemberLocation {
  division: Division;
  index: number;
  rank: Rank;
}

function indexCurrent(current: DivisionBoard): Map<string, MemberLocation> {
  const map = new Map<string, MemberLocation>();
  for (const div of DIVISIONS) {
    current[div].forEach((slot, index) => {
      map.set(slot.memberId, { division: div, index, rank: slot.rank });
    });
  }
  return map;
}

function targetMemberIndex(target: TargetBoard): Map<string, { division: Division; isLeader: boolean }> {
  const map = new Map<string, { division: Division; isLeader: boolean }>();
  for (const div of DIVISIONS) {
    target[div].forEach((id, i) => map.set(id, { division: div, isLeader: i === 0 }));
  }
  return map;
}

/** Execute의 목격자(같은 분과 다른 멤버) 존재 여부. 없으면 게임 내 Execute 액션 제안 불가. */
function hasExecuteWitness(current: DivisionBoard, division: Division, memberId: string): boolean {
  return current[division].some((s) => s.memberId !== memberId);
}

function pushRec(
  recs: Recommendation[],
  action: ActionType,
  partial: Omit<Recommendation, "action" | "cost">,
): void {
  recs.push({ ...partial, action, cost: ACTION_COSTS[action] });
}

export function computeRecommendations(
  current: DivisionBoard,
  target: TargetBoard,
  members: SyndicateMember[],
): Recommendation[] {
  const memberMap = new Map(members.map((m) => [m.id, m]));
  const currentLoc = indexCurrent(current);
  const targetLoc = targetMemberIndex(target);
  const recs: Recommendation[] = [];

  // 1) Target Leaders (slot 0 of each target division)
  for (const div of DIVISIONS) {
    const wantedLeaderId = target[div][0];
    if (!wantedLeaderId) continue;
    const member = memberMap.get(wantedLeaderId);
    if (!member) continue;
    const loc = currentLoc.get(wantedLeaderId);

    if (!loc) {
      pushRec(recs, "Capture", {
        targetMemberId: wantedLeaderId,
        targetMemberName: member.name,
        toDivision: div,
        reason: `${div} Leader 자리 비어있음 — 다음 Jun 인카운터에서 ${member.name} 캡처 후 ${div}로 Bargain.`,
        priority: 100,
      });
    } else if (loc.division !== div) {
      pushRec(recs, "Bargain", {
        targetMemberId: wantedLeaderId,
        targetMemberName: member.name,
        toDivision: div,
        reason: `${member.name}이 ${loc.division}에 있음. 목표 ${div}로 Bargain 이동 (Rank 유지).`,
        priority: 95,
      });
    } else if (loc.rank !== "Leader") {
      pushRec(recs, "Betray", {
        targetMemberId: wantedLeaderId,
        targetMemberName: member.name,
        reason: `${member.name}이 ${div}에 있으나 Member 등급. 같은 분과 다른 멤버를 Betray하면 Rank 1↑ → Leader 승격.`,
        priority: 90,
      });
    }
  }

  // 2) Target Members (non-leader slots)
  for (const div of DIVISIONS) {
    target[div].slice(1).forEach((id) => {
      const member = memberMap.get(id);
      if (!member) return;
      const loc = currentLoc.get(id);
      if (!loc) {
        pushRec(recs, "Capture", {
          targetMemberId: id,
          targetMemberName: member.name,
          toDivision: div,
          reason: `${div} Member 슬롯 채울 ${member.name} 미보유 — 캡처 후 Bargain.`,
          priority: 60,
        });
      } else if (loc.division !== div) {
        pushRec(recs, "Bargain", {
          targetMemberId: id,
          targetMemberName: member.name,
          toDivision: div,
          reason: `${member.name}이 ${loc.division}에 있음. 목표 ${div}로 Bargain.`,
          priority: 55,
        });
      } else if (loc.rank === "Leader") {
        // Demotion 케이스: 목표는 Member인데 현재 Leader. rank 낮춰야 함.
        pushRec(recs, "Interrogate", {
          targetMemberId: id,
          targetMemberName: member.name,
          reason: `${member.name}이 ${div} Leader지만 목표에서는 Member. Interrogate로 Rank↓ → Member로 강등 (이탈 위험 주의).`,
          priority: 50,
        });
      }
    });
  }

  // 3) Unwanted members (in current but not in target anywhere)
  for (const [memberId, loc] of currentLoc.entries()) {
    if (targetLoc.has(memberId)) continue;
    const member = memberMap.get(memberId);
    if (!member) continue;

    if (loc.rank === "Leader") {
      // Execute는 같은 분과 목격자 존재가 전제. 없으면 Interrogate로 폴백.
      if (hasExecuteWitness(current, loc.division, memberId)) {
        pushRec(recs, "Execute", {
          targetMemberId: memberId,
          targetMemberName: member.name,
          reason: `${member.name}이 ${loc.division} Leader지만 목표 레이아웃에 없음. Execute로 즉시 제거 + 친구 1명 동반 제거.`,
          priority: 75,
        });
      } else {
        pushRec(recs, "Interrogate", {
          targetMemberId: memberId,
          targetMemberName: member.name,
          reason: `${member.name}이 ${loc.division} Leader지만 목격자 부재 — Execute 불가. Interrogate로 Rank↓ 유도.`,
          priority: 45,
        });
      }
    } else {
      pushRec(recs, "Interrogate", {
        targetMemberId: memberId,
        targetMemberName: member.name,
        reason: `${member.name}이 ${loc.division} Member로 있으나 목표 외. Interrogate로 Rank↓ → 결국 syndicate 이탈.`,
        priority: 40,
      });
    }
  }

  recs.sort((a, b) => b.priority - a.priority);
  return recs;
}

export function summarizeBoardDelta(current: DivisionBoard, target: TargetBoard): {
  matched: number;
  total: number;
  byDivision: Record<Division, { matched: number; total: number }>;
} {
  const byDivision = {} as Record<Division, { matched: number; total: number }>;
  let matched = 0;
  let total = 0;
  for (const div of DIVISIONS) {
    const t = target[div];
    const currentIds = new Set(current[div].map((s) => s.memberId));
    const m = t.filter((id) => currentIds.has(id)).length;
    byDivision[div] = { matched: m, total: t.length };
    matched += m;
    total += t.length;
  }
  return { matched, total, byDivision };
}
