import { DIVISIONS, DIVISION_COLORS, type Division, type SyndicateMember } from "./types";
import { CrownIcon } from "./icons";
import type { DivisionBoard } from "../../utils/syndicateEngine";

type DiffState = "matched" | "needed" | "extra";

interface Props {
  /** 목표 보드 (프리셋 또는 커스텀) */
  board: Record<Division, string[]>;
  /** 현재 인게임 보드 (diff 대조용) */
  currentBoard: DivisionBoard;
  memberMap: Record<string, SyndicateMember>;
  onSelectMember: (m: SyndicateMember) => void;
  /** hover 시 강조 대상 (S3b) */
  hoveredMemberId?: string | null;
}

interface DivisionRow {
  memberId: string;
  name: string;
  isLeaderInTarget: boolean;
  state: DiffState;
  currentRank?: "Leader" | "Member";
}

function diffStateColor(state: DiffState): { bg: string; border: string; text: string } {
  switch (state) {
    case "matched":
      return {
        bg: "var(--status-success-bg)",
        border: "var(--status-success)",
        text: "var(--status-success)",
      };
    case "needed":
      return {
        bg: "var(--status-info-bg)",
        border: "var(--status-info)",
        text: "var(--status-info)",
      };
    case "extra":
      return {
        bg: "var(--status-danger-bg)",
        border: "var(--status-danger)",
        text: "var(--status-danger)",
      };
  }
}

function diffLabel(state: DiffState): string {
  switch (state) {
    case "matched": return "OK";
    case "needed":  return "배치 필요";
    case "extra":   return "이동/제거";
  }
}

export function TargetPreview({ board, currentBoard, memberMap, onSelectMember, hoveredMemberId }: Props) {
  return (
    <div
      style={{
        display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 12,
        padding: 8, background: "var(--bg-elevated)", borderRadius: 6,
        border: "1px dashed var(--border-default)",
      }}
    >
      {DIVISIONS.map((div) => (
        <DivisionCard
          key={div}
          division={div}
          targetIds={board[div]}
          currentSlots={currentBoard[div]}
          memberMap={memberMap}
          onSelectMember={onSelectMember}
          hoveredMemberId={hoveredMemberId}
        />
      ))}
    </div>
  );
}

function DivisionCard({
  division, targetIds, currentSlots, memberMap, onSelectMember, hoveredMemberId,
}: {
  division: Division;
  targetIds: string[];
  currentSlots: { memberId: string; rank: "Leader" | "Member" }[];
  memberMap: Record<string, SyndicateMember>;
  onSelectMember: (m: SyndicateMember) => void;
  hoveredMemberId?: string | null;
}) {
  const divColor = DIVISION_COLORS[division];
  const targetSet = new Set(targetIds);
  const currentMap = new Map(currentSlots.map((s) => [s.memberId, s.rank]));

  // 1) 목표 ids — matched or needed
  const rows: DivisionRow[] = [];
  targetIds.forEach((id, i) => {
    const m = memberMap[id];
    if (!m) return;
    rows.push({
      memberId: id,
      name: m.name,
      isLeaderInTarget: i === 0,
      state: currentMap.has(id) ? "matched" : "needed",
      currentRank: currentMap.get(id),
    });
  });

  // 2) 현재에만 있는 멤버 — extra
  for (const slot of currentSlots) {
    if (!targetSet.has(slot.memberId)) {
      const m = memberMap[slot.memberId];
      if (!m) continue;
      rows.push({
        memberId: slot.memberId,
        name: m.name,
        isLeaderInTarget: false,
        state: "extra",
        currentRank: slot.rank,
      });
    }
  }

  const matchedCount = rows.filter((r) => r.state === "matched").length;

  return (
    <div style={{ fontSize: 11 }}>
      <div
        style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          fontWeight: 700, color: divColor.text, marginBottom: 4,
        }}
      >
        <span>{division}</span>
        <span
          className={matchedCount === targetIds.length && targetIds.length > 0 ? "ui-text-success" : "ui-text-muted"}
          style={{ fontSize: 10 }}
        >
          {matchedCount}/{targetIds.length}
        </span>
      </div>
      {rows.length === 0 ? (
        <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>—</span>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {rows.map((r) => (
            <DiffRow
              key={r.memberId}
              row={r}
              hovered={hoveredMemberId === r.memberId}
              onClick={() => {
                const m = memberMap[r.memberId];
                if (m) onSelectMember(m);
              }}
              title={memberMap[r.memberId]?.rewards[division] || "—"}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function DiffRow({
  row, hovered, onClick, title,
}: {
  row: DivisionRow;
  hovered: boolean;
  onClick: () => void;
  title: string;
}) {
  const color = diffStateColor(row.state);
  return (
    <div
      onClick={onClick}
      title={`${diffLabel(row.state)} · ${title}`}
      style={{
        display: "flex", alignItems: "center", gap: 4,
        padding: "2px 6px", borderRadius: 3, cursor: "pointer",
        background: color.bg,
        border: `1px solid ${color.border}`,
        color: "var(--text-primary)",
        outline: hovered ? "2px solid var(--accent-primary)" : "none",
        outlineOffset: hovered ? "1px" : 0,
        transition: "outline var(--anim-fast) var(--anim-easing)",
      }}
    >
      {row.isLeaderInTarget && (
        <CrownIcon size={10} className="ui-text-warning" title="목표 Leader" />
      )}
      <span style={{ flex: 1 }}>{row.name}</span>
      {row.currentRank && (
        <span style={{ fontSize: 9, color: color.text, fontWeight: 700 }}>
          [{row.currentRank === "Leader" ? "L" : "M"}]
        </span>
      )}
    </div>
  );
}
