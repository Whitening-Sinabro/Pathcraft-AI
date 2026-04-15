// Syndicate Engine 스모크 테스트 — TS 테스트 프레임워크 미설치 상태의 임시 검증.
// 실행: `node _analysis/syndicate_engine_smoke.mjs` (프로젝트 루트에서)
//
// 본 파일은 src/utils/syndicateEngine.ts 로직과 src/components/SyndicateBoard.tsx의
// setCurrentRank/addOrMoveCurrentMember 핸들러를 모사. 회귀 방지 임시 가드.
// 향후 vitest 도입 시 .test.ts로 마이그레이션.

const DIVISIONS = ["Transportation", "Fortification", "Research", "Intervention"];

// ---- 핸들러 모사 ----
function setCurrentRank(prev, div, memberId, rank) {
  return {
    ...prev,
    [div]: prev[div].map((s) => (s.memberId === memberId ? { ...s, rank } : s)),
  };
}

function addOrMoveCurrentMember(prev, div, memberId) {
  const next = { ...prev };
  for (const d of DIVISIONS) next[d] = next[d].filter((s) => s.memberId !== memberId);
  if (next[div].length >= 4) return prev;
  next[div] = [...next[div], { memberId, rank: "Member" }];
  return next;
}

// ---- 미니 엔진 (computeRecommendations 핵심 로직 모사) ----
function computeRecs(current, target) {
  const currentLoc = new Map();
  for (const div of DIVISIONS) {
    current[div].forEach((s, i) => currentLoc.set(s.memberId, { div, i, rank: s.rank }));
  }
  const targetLoc = new Map();
  for (const div of DIVISIONS) target[div].forEach((id) => targetLoc.set(id, div));
  const recs = [];
  for (const div of DIVISIONS) {
    const lead = target[div][0];
    if (!lead) continue;
    const loc = currentLoc.get(lead);
    if (!loc) recs.push({ action: "Capture", id: lead, div, p: 100 });
    else if (loc.div !== div) recs.push({ action: "Bargain", id: lead, div, p: 95 });
    else if (loc.rank !== "Leader") recs.push({ action: "Betray", id: lead, p: 90 });
  }
  for (const [id, loc] of currentLoc.entries()) {
    if (!targetLoc.has(id)) {
      recs.push({ action: loc.rank === "Leader" ? "Execute" : "Interrogate", id, p: loc.rank === "Leader" ? 75 : 40 });
    }
  }
  recs.sort((a, b) => b.p - a.p);
  return recs;
}

// ---- 테스트 ----
const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
function eq(a, b, msg) {
  const aS = JSON.stringify(a), bS = JSON.stringify(b);
  if (aS !== bS) throw new Error(`${msg || ""}\n  expected ${bS}\n  got      ${aS}`);
}

const empty = () => ({ Transportation: [], Fortification: [], Research: [], Intervention: [] });

test("setCurrentRank: 슬롯 0 토글 시 다른 슬롯 보존", () => {
  let s = { ...empty(), Transportation: [
    { memberId: "a", rank: "Member" }, { memberId: "b", rank: "Member" },
  ]};
  s = setCurrentRank(s, "Transportation", "a", "Leader");
  eq(s.Transportation, [{ memberId: "a", rank: "Leader" }, { memberId: "b", rank: "Member" }]);
});

test("setCurrentRank: 3-슬롯 div에서 슬롯 0 토글", () => {
  let s = { ...empty(), Transportation: [
    { memberId: "a", rank: "Member" },
    { memberId: "b", rank: "Member" },
    { memberId: "c", rank: "Member" },
  ]};
  s = setCurrentRank(s, "Transportation", "a", "Leader");
  eq(s.Transportation, [
    { memberId: "a", rank: "Leader" },
    { memberId: "b", rank: "Member" },
    { memberId: "c", rank: "Member" },
  ]);
});

test("addOrMoveCurrentMember: 다른 div에서 이동", () => {
  let s = { ...empty(), Fortification: [{ memberId: "b", rank: "Leader" }]};
  s = addOrMoveCurrentMember(s, "Research", "b");
  eq(s.Fortification, []);
  eq(s.Research, [{ memberId: "b", rank: "Member" }]);
});

test("addOrMoveCurrentMember: 4명 한도 시 차단", () => {
  const full = { ...empty(), Transportation: [
    { memberId: "a", rank: "Member" }, { memberId: "b", rank: "Member" },
    { memberId: "c", rank: "Member" }, { memberId: "d", rank: "Member" },
  ]};
  const next = addOrMoveCurrentMember(full, "Transportation", "e");
  if (next !== full) throw new Error("expected same ref (blocked)");
});

test("Engine: 빈 보드 → target Leader 모두 Capture 추천 (priority 100)", () => {
  const target = { Transportation: ["a","b"], Fortification: [], Research: [], Intervention: [] };
  const recs = computeRecs(empty(), target);
  if (recs[0].action !== "Capture" || recs[0].id !== "a") {
    throw new Error("expected Capture a first, got " + JSON.stringify(recs[0]));
  }
});

test("Engine: 목표 Leader가 잘못된 div에 → Bargain 추천", () => {
  const current = { ...empty(), Fortification: [{ memberId: "aisling", rank: "Leader" }] };
  const target = { Transportation: [], Fortification: [], Research: ["aisling"], Intervention: [] };
  const recs = computeRecs(current, target);
  const first = recs[0];
  if (first.action !== "Bargain" || first.div !== "Research") {
    throw new Error("expected Bargain to Research, got " + JSON.stringify(first));
  }
});

test("Engine: 목표 Leader가 맞는 div에 Member rank → Betray 추천", () => {
  const current = { ...empty(), Research: [{ memberId: "aisling", rank: "Member" }]};
  const target = { Transportation: [], Fortification: [], Research: ["aisling"], Intervention: [] };
  const recs = computeRecs(current, target);
  const first = recs[0];
  if (first.action !== "Betray") throw new Error("expected Betray, got " + JSON.stringify(first));
});

test("Engine: 목표 외 Leader → Execute, Member → Interrogate", () => {
  const current = { ...empty(),
    Transportation: [{ memberId: "x", rank: "Leader" }, { memberId: "y", rank: "Member" }],
  };
  const target = empty();
  const recs = computeRecs(current, target);
  const exec = recs.find((r) => r.id === "x");
  const interr = recs.find((r) => r.id === "y");
  if (!exec || exec.action !== "Execute") throw new Error("x should Execute");
  if (!interr || interr.action !== "Interrogate") throw new Error("y should Interrogate");
});

let pass = 0, fail = 0;
for (const t of tests) {
  try { t.fn(); console.log("  ✓", t.name); pass++; }
  catch (e) { console.error("  ✗", t.name, "\n   ", e.message); fail++; }
}
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail > 0 ? 1 : 0);
