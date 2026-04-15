import { useState, useEffect, useMemo, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { SyndicateTutorial } from "./SyndicateTutorial";
import {
  computeRecommendations,
  summarizeBoardDelta,
  EMPTY_BOARD,
  type DivisionBoard,
  type Rank,
  type SyndicateMember,
} from "../utils/syndicateEngine";

interface VisionDivisionSlot { member_id: string; rank: Rank; }
interface VisionResult {
  divisions: Record<string, VisionDivisionSlot[]>;
  confidence: "high" | "medium" | "low";
  notes: string;
  diagnostics: { unknown_members: Array<{ div: string; raw: string }>; invalid_ranks: unknown[] };
  error?: string;
}

interface SyndicateLayout {
  id: string;
  name: string;
  strategy: string;
  priority: string;
  board: Record<string, string[]>;
  rewards_focus: string[];
}

interface SyndicateData {
  members: SyndicateMember[];
}

interface LayoutData {
  layouts: SyndicateLayout[];
}

const DIVISIONS = ["Transportation", "Fortification", "Research", "Intervention"] as const;
type Division = typeof DIVISIONS[number];

function actionColor(action: string): string {
  switch (action) {
    case "Bargain": return "#1864ab";
    case "Interrogate": return "#5f3dc4";
    case "Betray": return "#c92a2a";
    case "Execute": return "#5c3c00";
    case "Capture": return "#2b8a3e";
    default: return "#495057";
  }
}

const DIVISION_COLORS: Record<Division, { bg: string; text: string; border: string }> = {
  Transportation: { bg: "#fff4e6", text: "#d9480f", border: "#fd7e14" },
  Fortification: { bg: "#e7f5ff", text: "#1864ab", border: "#339af0" },
  Research: { bg: "#f3f0ff", text: "#5f3dc4", border: "#7950f2" },
  Intervention: { bg: "#fff5f5", text: "#c92a2a", border: "#fa5252" },
};

interface Props {
  buildJson?: string;
  recommendation?: { layout_id: string; reason: string } | null;
}

export function SyndicateBoard({ buildJson: _buildJson, recommendation }: Props) {
  const [members, setMembers] = useState<SyndicateMember[]>([]);
  const [layouts, setLayouts] = useState<SyndicateLayout[]>([]);
  const [board, setBoard] = useState<Record<Division, string[]>>({
    Transportation: [],
    Fortification: [],
    Research: [],
    Intervention: [],
  });
  const [selectedLayoutId, setSelectedLayoutId] = useState<string>("");
  const [selectedMember, setSelectedMember] = useState<SyndicateMember | null>(null);
  const [currentBoard, setCurrentBoard] = useState<DivisionBoard>(EMPTY_BOARD);

  useEffect(() => {
    // JSON 데이터 fetch (public/ 경로나 임베드)
    import("../../data/syndicate_members.json")
      .then((mod) => setMembers((mod.default as unknown as SyndicateData).members))
      .catch(() => setMembers([]));
    import("../../data/syndicate_layouts.json")
      .then((mod) => setLayouts((mod.default as unknown as LayoutData).layouts))
      .catch(() => setLayouts([]));
  }, []);

  // localStorage 영속
  useEffect(() => {
    try {
      const saved = localStorage.getItem("pathcraftai_syndicate");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.board) setBoard(parsed.board);
        if (parsed.layoutId) setSelectedLayoutId(parsed.layoutId);
        if (parsed.currentBoard) setCurrentBoard(parsed.currentBoard);
      }
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(
        "pathcraftai_syndicate",
        JSON.stringify({ board, layoutId: selectedLayoutId, currentBoard })
      );
    } catch {
      /* ignore */
    }
  }, [board, selectedLayoutId, currentBoard]);

  function applyLayout(id: string) {
    const layout = layouts.find((l) => l.id === id);
    if (!layout) return;
    setBoard({
      Transportation: [...(layout.board.Transportation || [])],
      Fortification: [...(layout.board.Fortification || [])],
      Research: [...(layout.board.Research || [])],
      Intervention: [...(layout.board.Intervention || [])],
    });
    setSelectedLayoutId(id);
  }

  function clearBoard() {
    setBoard({ Transportation: [], Fortification: [], Research: [], Intervention: [] });
    setSelectedLayoutId("");
  }

  const memberMap = Object.fromEntries(members.map((m) => [m.id, m]));

  const recommendedLayout = recommendation
    ? layouts.find((l) => l.id === recommendation.layout_id)
    : null;

  // Path engine: target = board (preset 적용 후), current = currentBoard (유저 인게임 상태)
  const targetBoard = useMemo(
    () => ({
      Transportation: board.Transportation,
      Fortification: board.Fortification,
      Research: board.Research,
      Intervention: board.Intervention,
    }),
    [board],
  );
  const recs = useMemo(
    () => (members.length > 0 ? computeRecommendations(currentBoard, targetBoard, members) : []),
    [currentBoard, targetBoard, members],
  );
  const delta = useMemo(
    () => summarizeBoardDelta(currentBoard, targetBoard),
    [currentBoard, targetBoard],
  );

  function addOrMoveCurrentMember(div: Division, memberId: string) {
    setCurrentBoard((prev) => {
      const next = { ...prev };
      for (const d of DIVISIONS) {
        next[d] = next[d].filter((s) => s.memberId !== memberId);
      }
      if (next[div].length >= 4) return prev;
      next[div] = [...next[div], { memberId, rank: "Member" }];
      return next;
    });
  }

  function setCurrentRank(div: Division, memberId: string, rank: Rank) {
    setCurrentBoard((prev) => ({
      ...prev,
      [div]: prev[div].map((s) => (s.memberId === memberId ? { ...s, rank } : s)),
    }));
  }

  function removeCurrentSlot(div: Division, memberId: string) {
    setCurrentBoard((prev) => ({
      ...prev,
      [div]: prev[div].filter((s) => s.memberId !== memberId),
    }));
  }

  function clearCurrentBoard() {
    setCurrentBoard(EMPTY_BOARD);
  }

  function copyTargetToCurrent() {
    const next: DivisionBoard = { ...EMPTY_BOARD };
    for (const div of DIVISIONS) {
      next[div] = board[div].map((id, i) => ({ memberId: id, rank: i === 0 ? "Leader" : "Member" }));
    }
    setCurrentBoard(next);
  }

  function promoteCurrentToTarget() {
    // 현재 보드를 목표로 변환 (Vision으로 가이드 이미지 분석 후 목표 저장 흐름).
    // Leader(slot 0) 순서 유지: 각 div에서 rank=Leader가 앞으로 오도록 정렬.
    const nextTarget: Record<Division, string[]> = {
      Transportation: [], Fortification: [], Research: [], Intervention: [],
    };
    for (const div of DIVISIONS) {
      const sorted = [...currentBoard[div]].sort((a, b) => {
        if (a.rank === b.rank) return 0;
        return a.rank === "Leader" ? -1 : 1;
      });
      nextTarget[div] = sorted.map((s) => s.memberId);
    }
    setBoard(nextTarget);
    setSelectedLayoutId("custom");
    setCurrentBoard(EMPTY_BOARD);
  }

  // Vision API — 스크린샷에서 currentBoard 자동 채움
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [visionLoading, setVisionLoading] = useState(false);
  const [visionStatus, setVisionStatus] = useState<{ kind: "ok" | "warn" | "err"; msg: string } | null>(null);

  async function fileToBase64(file: File | Blob): Promise<string> {
    const buffer = await file.arrayBuffer();
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  }

  async function analyzeImage(file: File | Blob) {
    setVisionLoading(true);
    setVisionStatus(null);
    try {
      const b64 = await fileToBase64(file);
      const raw = await invoke<string>("analyze_syndicate_image", { imageBase64: b64 });
      const parsed = JSON.parse(raw) as VisionResult;
      if (parsed.error) {
        setVisionStatus({ kind: "err", msg: parsed.error });
        return;
      }
      // VisionResult.divisions → DivisionBoard
      const next: DivisionBoard = { ...EMPTY_BOARD };
      for (const div of DIVISIONS) {
        const slots = parsed.divisions[div] || [];
        next[div] = slots.map((s) => ({ memberId: s.member_id, rank: s.rank }));
      }
      setCurrentBoard(next);
      const filled = DIVISIONS.reduce((sum, d) => sum + next[d].length, 0);
      const unknownCount = parsed.diagnostics?.unknown_members?.length ?? 0;
      const conf = parsed.confidence;
      const kind = conf === "high" && unknownCount === 0 ? "ok" : "warn";
      const parts = [`${filled}명 인식 (신뢰도: ${conf})`];
      if (unknownCount > 0) parts.push(`미식별 ${unknownCount}건`);
      if (parsed.notes) parts.push(parsed.notes);
      setVisionStatus({ kind, msg: parts.join(" · ") });
    } catch (e) {
      setVisionStatus({ kind: "err", msg: e instanceof Error ? e.message : String(e) });
    } finally {
      setVisionLoading(false);
    }
  }

  function onFileSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) void analyzeImage(file);
    e.target.value = "";
  }

  async function onPasteFromClipboard() {
    try {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        const imgType = item.types.find((t) => t.startsWith("image/"));
        if (imgType) {
          const blob = await item.getType(imgType);
          await analyzeImage(blob);
          return;
        }
      }
      setVisionStatus({ kind: "err", msg: "클립보드에 이미지가 없습니다 (PrtScr 또는 캡처툴 후 다시 시도)" });
    } catch (e) {
      setVisionStatus({ kind: "err", msg: `클립보드 접근 실패: ${e instanceof Error ? e.message : String(e)}` });
    }
  }

  return (
    <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
      <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#5c3c00" }}>
        🎭 Syndicate 보드 (Jun Betrayal)
      </h3>

      <SyndicateTutorial />

      {/* AI 추천 배지 */}
      {recommendedLayout && (
        <div style={{ padding: 10, background: "#d3f9d8", borderRadius: 6, marginBottom: 10, fontSize: 13, color: "#2b8a3e" }}>
          <strong>✨ AI 추천 레이아웃: {recommendedLayout.name}</strong>
          <p style={{ margin: "4px 0 6px", fontSize: 12, color: "#495057" }}>{recommendation!.reason}</p>
          <button
            onClick={() => applyLayout(recommendedLayout.id)}
            style={{
              padding: "4px 12px", fontSize: 12, fontWeight: 600,
              background: "#2b8a3e", color: "#fff", border: "none",
              borderRadius: 4, cursor: "pointer",
            }}
          >
            이 레이아웃 적용
          </button>
        </div>
      )}

      {/* 프리셋 레이아웃 */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: "#868e96", marginBottom: 4 }}>프리셋 레이아웃</div>
        <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
          {layouts.map((l) => (
            <button
              key={l.id}
              onClick={() => applyLayout(l.id)}
              style={{
                padding: "4px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600,
                border: selectedLayoutId === l.id ? "2px solid #5c3c00" : "1px solid #dee2e6",
                background: selectedLayoutId === l.id ? "#fff9db" : "#fff",
                cursor: "pointer", color: "#495057",
              }}
              title={l.strategy}
            >
              {l.name}
            </button>
          ))}
          <button
            onClick={clearBoard}
            style={{
              padding: "4px 10px", borderRadius: 4, fontSize: 11,
              border: "1px dashed #adb5bd", background: "#fff", cursor: "pointer", color: "#868e96",
            }}
          >
            모두 비우기
          </button>
        </div>
        {selectedLayoutId === "custom" && (
          <div style={{ marginTop: 6, fontSize: 12, color: "#2b8a3e" }}>
            <strong>✨ 커스텀 목표:</strong> Vision/수동으로 저장된 레이아웃. 프리셋 클릭 시 덮어씀.
          </div>
        )}
        {selectedLayoutId && selectedLayoutId !== "custom" && (
          <div style={{ marginTop: 6, fontSize: 12, color: "#495057" }}>
            <strong>전략:</strong>{" "}
            {layouts.find((l) => l.id === selectedLayoutId)?.strategy}
          </div>
        )}
      </div>

      {/* 목표 미리보기 (read-only, 프리셋 선택 시) */}
      {selectedLayoutId && (
        <div style={{
          display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 12,
          padding: 8, background: "#f8f9fa", borderRadius: 6, border: "1px dashed #ced4da",
        }}>
          {DIVISIONS.map((div) => {
            const colors = DIVISION_COLORS[div];
            const ids = board[div];
            return (
              <div key={div} style={{ fontSize: 11 }}>
                <div style={{ fontWeight: 700, color: colors.text, marginBottom: 2 }}>
                  {div} ({ids.length})
                </div>
                {ids.length === 0 ? (
                  <span style={{ color: "#adb5bd", fontStyle: "italic" }}>—</span>
                ) : (
                  ids.map((memberId, i) => {
                    const m = memberMap[memberId];
                    if (!m) return null;
                    return (
                      <div
                        key={memberId}
                        onClick={() => setSelectedMember(m)}
                        style={{ cursor: "pointer", color: "#212529", paddingLeft: 4 }}
                        title={m.rewards[div] || "—"}
                      >
                        {i === 0 ? <strong>👑 {m.name}</strong> : <span>· {m.name}</span>}
                      </div>
                    );
                  })
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* 현재 인게임 상태 입력 */}
      <div
        style={{
          marginTop: 12, padding: 10, background: "#f8f9fa", border: "1px solid #dee2e6",
          borderRadius: 6,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6, flexWrap: "wrap", gap: 4 }}>
          <strong style={{ fontSize: 13, color: "#212529" }}>📋 현재 인게임 상태</strong>
          <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={onFileSelected}
              style={{ display: "none" }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={visionLoading}
              style={{
                padding: "3px 8px", fontSize: 11, border: "1px solid #ffd43b",
                background: "#fff9db", color: "#5c3c00", borderRadius: 3,
                cursor: visionLoading ? "wait" : "pointer", fontWeight: 600,
              }}
              title="POE Syndicate 패널 스크린샷 → Claude Vision으로 자동 입력"
            >
              {visionLoading ? "분석중..." : "📷 이미지에서"}
            </button>
            <button
              onClick={onPasteFromClipboard}
              disabled={visionLoading}
              style={{
                padding: "3px 8px", fontSize: 11, border: "1px solid #ffd43b",
                background: "#fff9db", color: "#5c3c00", borderRadius: 3,
                cursor: visionLoading ? "wait" : "pointer",
              }}
              title="클립보드의 스크린샷에서 가져오기 (PrtScr 후 클릭)"
            >
              📋 붙여넣기
            </button>
            <button
              onClick={copyTargetToCurrent}
              style={{
                padding: "3px 8px", fontSize: 11, border: "1px solid #4dabf7",
                background: "#e7f5ff", color: "#1864ab", borderRadius: 3, cursor: "pointer",
              }}
              title="목표 레이아웃을 현재 상태로 복사 (이미 도달했을 때)"
            >
              ← 목표
            </button>
            <button
              onClick={promoteCurrentToTarget}
              disabled={DIVISIONS.every((d) => currentBoard[d].length === 0)}
              style={{
                padding: "3px 8px", fontSize: 11, border: "1px solid #51cf66",
                background: "#d3f9d8", color: "#2b8a3e", borderRadius: 3, cursor: "pointer",
                fontWeight: 600,
              }}
              title="현재 상태를 목표로 설정 (예: 가이드 이미지 분석 후 저장). 커스텀 프리셋으로 잠김."
            >
              현재 → 목표 ✓
            </button>
            <button
              onClick={clearCurrentBoard}
              style={{
                padding: "3px 8px", fontSize: 11, border: "1px dashed #adb5bd",
                background: "#fff", color: "#868e96", borderRadius: 3, cursor: "pointer",
              }}
            >
              비우기
            </button>
          </div>
        </div>
        {visionStatus && (
          <div style={{
            marginBottom: 6, padding: "4px 8px", fontSize: 11, borderRadius: 3,
            background: visionStatus.kind === "ok" ? "#d3f9d8" : visionStatus.kind === "warn" ? "#fff9db" : "#ffe3e3",
            color: visionStatus.kind === "ok" ? "#2b8a3e" : visionStatus.kind === "warn" ? "#5c3c00" : "#c92a2a",
          }}>
            {visionStatus.kind === "ok" ? "✅" : visionStatus.kind === "warn" ? "⚠️" : "❌"} {visionStatus.msg}
          </div>
        )}
        <div style={{ fontSize: 11, color: "#868e96", marginBottom: 6 }}>
          진행률: {delta.matched} / {delta.total} 슬롯 일치 (
          {DIVISIONS.map((d) => `${d[0]}${delta.byDivision[d].matched}/${delta.byDivision[d].total}`).join(" · ")})
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
          {DIVISIONS.map((div) => (
            <div key={div} style={{ background: "#fff", border: "1px solid #dee2e6", borderRadius: 4, padding: 6 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "#495057", marginBottom: 4 }}>
                {div} ({currentBoard[div].length}/4)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                {currentBoard[div].map((slot) => {
                  const m = memberMap[slot.memberId];
                  if (!m) return null;
                  return (
                    <div
                      key={slot.memberId}
                      style={{
                        display: "flex", gap: 3, fontSize: 10,
                        padding: "2px 4px", background: "#f1f3f5", borderRadius: 3,
                        alignItems: "center",
                      }}
                    >
                      <strong style={{ flex: 1 }}>{m.name}</strong>
                      <select
                        value={slot.rank}
                        onChange={(e) => setCurrentRank(div, slot.memberId, e.target.value as Rank)}
                        style={{ fontSize: 10, padding: "1px 2px", border: "1px solid #dee2e6", borderRadius: 2 }}
                      >
                        <option value="Member">M</option>
                        <option value="Leader">L</option>
                      </select>
                      <button
                        onClick={() => removeCurrentSlot(div, slot.memberId)}
                        style={{ padding: "0 4px", fontSize: 10, background: "transparent", border: "none", color: "#868e96", cursor: "pointer" }}
                      >
                        ✕
                      </button>
                    </div>
                  );
                })}
                {currentBoard[div].length < 4 && (
                  <select
                    value=""
                    onChange={(e) => {
                      if (!e.target.value) return;
                      addOrMoveCurrentMember(div, e.target.value);
                    }}
                    style={{
                      padding: "2px 4px", fontSize: 10, border: "1px dashed #adb5bd",
                      borderRadius: 3, background: "#fff", color: "#868e96",
                    }}
                  >
                    <option value="">+ 멤버</option>
                    {members
                      .filter((m) => m.default_division !== null)
                      .filter((m) => !DIVISIONS.some((d) => currentBoard[d].some((s) => s.memberId === m.id)))
                      .map((m) => (
                        <option key={m.id} value={m.id}>
                          {m.name}
                        </option>
                      ))}
                  </select>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 다음 액션 추천 */}
      {recs.length > 0 && (
        <div
          style={{
            marginTop: 10, padding: 10, background: "#fff9db", border: "2px solid #ffd43b",
            borderRadius: 6,
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 13, color: "#5c3c00", marginBottom: 6 }}>
            🎯 다음 액션 추천 (우선순위 순)
          </div>
          <ol style={{ margin: 0, paddingLeft: 20, fontSize: 12, color: "#212529", lineHeight: 1.6 }}>
            {recs.slice(0, 8).map((r, i) => (
              <li key={`${r.action}-${r.targetMemberId}-${i}`} style={{ marginBottom: 4 }}>
                <span style={{ fontWeight: 700, color: actionColor(r.action) }}>{r.action}</span>
                {" "}<strong>{r.targetMemberName}</strong>
                {r.toDivision && <span style={{ color: "#495057" }}> → {r.toDivision}</span>}
                <div style={{ fontSize: 11, color: "#495057", marginLeft: 4 }}>{r.reason}</div>
              </li>
            ))}
          </ol>
          {delta.matched === delta.total && delta.total > 0 && (
            <div style={{ marginTop: 6, padding: 6, background: "#d3f9d8", borderRadius: 4, fontSize: 12, color: "#2b8a3e" }}>
              ✅ 목표 레이아웃 도달. 이제 farm 단계.
            </div>
          )}
        </div>
      )}

      {/* 선택된 멤버 상세 */}
      {selectedMember && (
        <div
          style={{
            padding: 10, background: "#f8f9fa", borderRadius: 6, border: "1px solid #dee2e6",
            fontSize: 12, color: "#495057",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
            <strong style={{ fontSize: 13 }}>
              {selectedMember.name}
              <span style={{ marginLeft: 6, color: "#868e96", fontSize: 11 }}>
                기본 분과: {selectedMember.default_division || "—"}
              </span>
            </strong>
            <button
              onClick={() => setSelectedMember(null)}
              style={{
                padding: "2px 8px", fontSize: 11, background: "transparent",
                border: "1px solid #dee2e6", borderRadius: 3, cursor: "pointer", color: "#868e96",
              }}
            >
              닫기
            </button>
          </div>
          <div style={{ fontSize: 11, marginBottom: 4 }}>
            태그: {selectedMember.tags.map((t) => (
              <span
                key={t}
                style={{
                  display: "inline-block", padding: "1px 6px", margin: "0 3px 0 0",
                  background: "#e9ecef", borderRadius: 10, fontSize: 10,
                }}
              >
                {t}
              </span>
            ))}
          </div>
          {DIVISIONS.map((div) => (
            <div key={div} style={{ fontSize: 11, marginTop: 2 }}>
              <strong style={{ color: DIVISION_COLORS[div].text }}>{div}:</strong>{" "}
              {selectedMember.rewards[div] || "—"}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
