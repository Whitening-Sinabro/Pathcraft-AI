import { describe, expect, test } from "vitest";
import {
  computeRecommendations,
  summarizeBoardDelta,
  EMPTY_BOARD,
  DIVISIONS,
  ACTION_COSTS,
  type DivisionBoard,
  type TargetBoard,
  type SyndicateMember,
} from "./syndicateEngine";

const M = (id: string, div = "Research"): SyndicateMember => ({
  id, name: id, default_division: div, tags: [], rewards: {},
});

const MEMBERS: SyndicateMember[] = [
  M("aisling", "Research"),
  M("vorici", "Research"),
  M("cameria", "Intervention"),
  M("gravicius", "Transportation"),
  M("elreon", "Fortification"),
  M("haku", "Fortification"),
];

function boardOf(init: Partial<DivisionBoard>): DivisionBoard {
  return { ...EMPTY_BOARD, ...init };
}

function emptyTarget(): TargetBoard {
  return { Transportation: [], Fortification: [], Research: [], Intervention: [] };
}

describe("computeRecommendations — greedy 1-step baseline (S2a)", () => {
  test("빈 현재 + 풀 target → 모든 Leader/Member Capture 추천, Leader 먼저", () => {
    const target: TargetBoard = {
      Transportation: ["gravicius"],
      Fortification: ["elreon", "haku"],
      Research: ["aisling", "vorici"],
      Intervention: ["cameria"],
    };
    const recs = computeRecommendations(EMPTY_BOARD, target, MEMBERS);

    // 6명 모두 Capture 추천
    expect(recs.every((r) => r.action === "Capture")).toBe(true);
    expect(recs).toHaveLength(6);

    // Leader 4명이 Member 앞에 (priority 100 > 60)
    const leaderIds = ["gravicius", "elreon", "aisling", "cameria"];
    const first4 = recs.slice(0, 4).map((r) => r.targetMemberId);
    for (const id of leaderIds) expect(first4).toContain(id);
  });

  test("잘못된 분과에 있는 Leader → Bargain 추천 (priority 95)", () => {
    const current = boardOf({
      Research: [{ memberId: "gravicius", rank: "Leader" }],
    });
    const target: TargetBoard = { ...emptyTarget(), Transportation: ["gravicius"] };
    const recs = computeRecommendations(current, target, MEMBERS);

    const bargain = recs.find((r) => r.targetMemberId === "gravicius");
    expect(bargain?.action).toBe("Bargain");
    expect(bargain?.toDivision).toBe("Transportation");
    expect(bargain?.priority).toBe(95);
  });

  test("target Leader가 같은 분과 Member rank → Betray 추천 (priority 90)", () => {
    const current = boardOf({
      Research: [{ memberId: "aisling", rank: "Member" }],
    });
    const target: TargetBoard = { ...emptyTarget(), Research: ["aisling"] };
    const recs = computeRecommendations(current, target, MEMBERS);

    const betray = recs.find((r) => r.targetMemberId === "aisling");
    expect(betray?.action).toBe("Betray");
    expect(betray?.priority).toBe(90);
  });

  test("현재 Leader인데 target에 없음 (목격자 존재) → Execute 추천 (priority 75)", () => {
    const current = boardOf({
      Intervention: [
        { memberId: "haku", rank: "Leader" },
        { memberId: "cameria", rank: "Member" },  // 같은 분과 목격자
      ],
    });
    const target: TargetBoard = emptyTarget();
    const recs = computeRecommendations(current, target, MEMBERS);

    const exec = recs.find((r) => r.targetMemberId === "haku");
    expect(exec?.action).toBe("Execute");
    expect(exec?.priority).toBe(75);
  });

  test("현재 Member인데 target에 없음 → Interrogate 추천 (priority 40)", () => {
    const current = boardOf({
      Intervention: [{ memberId: "haku", rank: "Member" }],
    });
    const target: TargetBoard = emptyTarget();
    const recs = computeRecommendations(current, target, MEMBERS);

    const interr = recs.find((r) => r.targetMemberId === "haku");
    expect(interr?.action).toBe("Interrogate");
    expect(interr?.priority).toBe(40);
  });

  test("추천은 priority 내림차순 정렬", () => {
    const current = boardOf({
      Intervention: [{ memberId: "haku", rank: "Leader" }],  // Execute 75
      Research: [{ memberId: "vorici", rank: "Member" }],    // Interrogate 40
    });
    const target: TargetBoard = { ...emptyTarget(), Transportation: ["gravicius"] }; // Capture 100
    const recs = computeRecommendations(current, target, MEMBERS);

    for (let i = 1; i < recs.length; i++) {
      expect(recs[i - 1].priority).toBeGreaterThanOrEqual(recs[i].priority);
    }
    expect(recs[0].action).toBe("Capture");
  });

  test("target이 빈 경우 → 현재 모두 Execute/Interrogate만", () => {
    const current = boardOf({
      Research: [
        { memberId: "aisling", rank: "Leader" },
        { memberId: "vorici", rank: "Member" },
      ],
    });
    const target: TargetBoard = emptyTarget();
    const recs = computeRecommendations(current, target, MEMBERS);

    expect(recs).toHaveLength(2);
    expect(recs.find((r) => r.targetMemberId === "aisling")?.action).toBe("Execute");
    expect(recs.find((r) => r.targetMemberId === "vorici")?.action).toBe("Interrogate");
  });

  test("현재 = target 일치 → 추천 없음", () => {
    const current = boardOf({
      Research: [{ memberId: "aisling", rank: "Leader" }],
    });
    const target: TargetBoard = { ...emptyTarget(), Research: ["aisling"] };
    const recs = computeRecommendations(current, target, MEMBERS);

    expect(recs).toHaveLength(0);
  });

  test("알 수 없는 member id (memberMap 누락) → 추천 생성 skip", () => {
    const current = boardOf({
      Research: [{ memberId: "ghost_id_not_in_members", rank: "Leader" }],
    });
    const target: TargetBoard = emptyTarget();
    const recs = computeRecommendations(current, target, MEMBERS);

    expect(recs).toHaveLength(0);
  });
});

describe("summarizeBoardDelta", () => {
  test("빈 current + 풀 target → matched 0, total 합산", () => {
    const target: TargetBoard = {
      Transportation: ["gravicius"],
      Fortification: ["elreon", "haku"],
      Research: ["aisling", "vorici"],
      Intervention: ["cameria"],
    };
    const delta = summarizeBoardDelta(EMPTY_BOARD, target);
    expect(delta.matched).toBe(0);
    expect(delta.total).toBe(6);
  });

  test("부분 매칭 — 분과별 카운트 정확", () => {
    const current: DivisionBoard = {
      ...EMPTY_BOARD,
      Research: [{ memberId: "aisling", rank: "Leader" }],
      Fortification: [{ memberId: "elreon", rank: "Leader" }],
    };
    const target: TargetBoard = {
      ...emptyTarget(),
      Research: ["aisling", "vorici"],     // 1/2
      Fortification: ["elreon", "haku"],   // 1/2
    };
    const delta = summarizeBoardDelta(current, target);

    expect(delta.matched).toBe(2);
    expect(delta.total).toBe(4);
    expect(delta.byDivision.Research).toEqual({ matched: 1, total: 2 });
    expect(delta.byDivision.Fortification).toEqual({ matched: 1, total: 2 });
  });

  test("rank 불일치는 matched로 카운트됨 (member id만 비교)", () => {
    // 현재 동작 baseline — target Leader(slot 0)인데 현재 Member rank여도 matched
    const current: DivisionBoard = {
      ...EMPTY_BOARD,
      Research: [{ memberId: "aisling", rank: "Member" }],
    };
    const target: TargetBoard = { ...emptyTarget(), Research: ["aisling"] };
    const delta = summarizeBoardDelta(current, target);

    expect(delta.matched).toBe(1);
    expect(delta.total).toBe(1);
  });
});

describe("S2c — 액션 비용 벡터 + 목격자 제약 + demotion", () => {
  test("모든 추천에 cost 필드(ActionCost) 포함", () => {
    const current = boardOf({ Research: [{ memberId: "aisling", rank: "Member" }] });
    const target: TargetBoard = { ...emptyTarget(), Research: ["aisling"] };
    const recs = computeRecommendations(current, target, MEMBERS);
    expect(recs.length).toBeGreaterThan(0);
    for (const r of recs) {
      expect(r.cost).toBeDefined();
      expect(typeof r.cost!.encounterTurns).toBe("number");
      expect(Array.isArray(r.cost!.sideEffects)).toBe(true);
    }
  });

  test("demotion: target Member + current Leader → Interrogate priority 50", () => {
    // target Research[0]=aisling(Leader) + slice(1)=vorici(Member)
    // current: vorici가 Leader rank로 이미 Research에 있음 → demotion 필요
    const current = boardOf({
      Research: [
        { memberId: "aisling", rank: "Leader" },
        { memberId: "vorici", rank: "Leader" },
      ],
    });
    const target: TargetBoard = { ...emptyTarget(), Research: ["aisling", "vorici"] };
    const recs = computeRecommendations(current, target, MEMBERS);

    const demote = recs.find((r) => r.targetMemberId === "vorici");
    expect(demote?.action).toBe("Interrogate");
    expect(demote?.priority).toBe(50);
    expect(demote?.cost?.sideEffects).toContain("rank_down");
  });

  test("witness 존재 시 unwanted Leader → Execute (priority 75)", () => {
    const current = boardOf({
      Intervention: [
        { memberId: "haku", rank: "Leader" },
        { memberId: "vorici", rank: "Member" },  // 목격자
      ],
    });
    const target: TargetBoard = emptyTarget();
    const recs = computeRecommendations(current, target, MEMBERS);

    const exec = recs.find((r) => r.targetMemberId === "haku");
    expect(exec?.action).toBe("Execute");
    expect(exec?.priority).toBe(75);
  });

  test("witness 부재 시 unwanted Leader → Execute 대신 Interrogate (priority 45)", () => {
    // haku 혼자 Intervention Leader — 목격자 없음
    const current = boardOf({
      Intervention: [{ memberId: "haku", rank: "Leader" }],
    });
    const target: TargetBoard = emptyTarget();
    const recs = computeRecommendations(current, target, MEMBERS);

    const fallback = recs.find((r) => r.targetMemberId === "haku");
    expect(fallback?.action).toBe("Interrogate");
    expect(fallback?.priority).toBe(45);
    expect(fallback?.reason).toContain("목격자 부재");
  });

  test("ACTION_COSTS 상수: 모든 ActionType 커버 + 값 일치", () => {
    expect(ACTION_COSTS.Capture.encounterTurns).toBe(2);
    expect(ACTION_COSTS.Bargain.encounterTurns).toBe(1);
    expect(ACTION_COSTS.Betray.sideEffects).toContain("same_division_witness_promoted");
    expect(ACTION_COSTS.Execute.sideEffects).toContain("same_division_witness_removed");
    expect(ACTION_COSTS.Interrogate.sideEffects).toContain("rank_down");
  });
});

describe("DIVISIONS / EMPTY_BOARD 상수", () => {
  test("DIVISIONS는 4개 고정", () => {
    expect(DIVISIONS).toHaveLength(4);
    expect(new Set(DIVISIONS).size).toBe(4);
  });

  test("EMPTY_BOARD는 모든 분과 빈 배열", () => {
    for (const div of DIVISIONS) {
      expect(EMPTY_BOARD[div]).toEqual([]);
    }
  });
});
