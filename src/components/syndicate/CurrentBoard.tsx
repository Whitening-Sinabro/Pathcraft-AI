import type { RefObject } from "react";
import { DIVISIONS, type Division, type Rank, type SyndicateMember } from "./types";
import type { DivisionBoard } from "../../utils/syndicateEngine";
import { VisionControls } from "./VisionControls";

interface Props {
  currentBoard: DivisionBoard;
  members: SyndicateMember[];
  memberMap: Record<string, SyndicateMember>;
  delta: {
    matched: number;
    total: number;
    byDivision: Record<Division, { matched: number; total: number }>;
  };

  // vision props (passed through to VisionControls)
  fileInputRef: RefObject<HTMLInputElement | null>;
  visionLoading: boolean;
  visionStatus: { kind: "ok" | "warn" | "err"; msg: string } | null;
  onFileSelected: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onPasteFromClipboard: () => void;
  onCopyTargetToCurrent: () => void;
  onPromoteCurrentToTarget: () => void;
  onClearCurrentBoard: () => void;

  // slot edit handlers
  onAddOrMoveMember: (div: Division, memberId: string) => void;
  onSetRank: (div: Division, memberId: string, rank: Rank) => void;
  onRemoveSlot: (div: Division, memberId: string) => void;
}

export function CurrentBoard(props: Props) {
  const {
    currentBoard, members, memberMap, delta,
    onAddOrMoveMember, onSetRank, onRemoveSlot,
  } = props;

  return (
    <div
      style={{
        marginTop: 12, padding: 10,
        background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
        borderRadius: 6,
      }}
    >
      <VisionControls
        fileInputRef={props.fileInputRef}
        visionLoading={props.visionLoading}
        visionStatus={props.visionStatus}
        currentBoard={currentBoard}
        onFileSelected={props.onFileSelected}
        onPasteFromClipboard={props.onPasteFromClipboard}
        onCopyTargetToCurrent={props.onCopyTargetToCurrent}
        onPromoteCurrentToTarget={props.onPromoteCurrentToTarget}
        onClearCurrentBoard={props.onClearCurrentBoard}
      />

      <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 6 }}>
        진행률: {delta.matched} / {delta.total} 슬롯 일치 (
        {DIVISIONS.map((d) => `${d[0]}${delta.byDivision[d].matched}/${delta.byDivision[d].total}`).join(" · ")})
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
        {DIVISIONS.map((div) => (
          <DivisionSlot
            key={div}
            division={div}
            slots={currentBoard[div]}
            memberMap={memberMap}
            members={members}
            currentBoard={currentBoard}
            onAddOrMove={(id) => onAddOrMoveMember(div, id)}
            onSetRank={(id, rank) => onSetRank(div, id, rank)}
            onRemove={(id) => onRemoveSlot(div, id)}
          />
        ))}
      </div>
    </div>
  );
}

function DivisionSlot({
  division, slots, memberMap, members, currentBoard, onAddOrMove, onSetRank, onRemove,
}: {
  division: Division;
  slots: { memberId: string; rank: Rank }[];
  memberMap: Record<string, SyndicateMember>;
  members: SyndicateMember[];
  currentBoard: DivisionBoard;
  onAddOrMove: (memberId: string) => void;
  onSetRank: (memberId: string, rank: Rank) => void;
  onRemove: (memberId: string) => void;
}) {
  return (
    <div style={{
      background: "var(--bg-panel)", border: "1px solid var(--border-default)",
      borderRadius: 4, padding: 6,
    }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 4 }}>
        {division} ({slots.length}/4)
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {slots.map((slot) => {
          const m = memberMap[slot.memberId];
          if (!m) return null;
          return (
            <div
              key={slot.memberId}
              style={{
                display: "flex", gap: 3, fontSize: 10, alignItems: "center",
                padding: "2px 4px", background: "var(--bg-elevated)", borderRadius: 3,
              }}
            >
              <strong style={{ flex: 1 }}>{m.name}</strong>
              <select
                value={slot.rank}
                onChange={(e) => onSetRank(slot.memberId, e.target.value as Rank)}
                style={{
                  fontSize: 10, padding: "1px 2px",
                  border: "1px solid var(--border-default)", borderRadius: 2,
                }}
              >
                <option value="Member">M</option>
                <option value="Leader">L</option>
              </select>
              <button
                onClick={() => onRemove(slot.memberId)}
                style={{
                  padding: "0 4px", fontSize: 10, background: "transparent",
                  border: "none", color: "var(--text-muted)", cursor: "pointer",
                }}
                aria-label={`${m.name} 제거`}
              >
                ✕
              </button>
            </div>
          );
        })}
        {slots.length < 4 && (
          <select
            value=""
            onChange={(e) => { if (e.target.value) onAddOrMove(e.target.value); }}
            style={{
              padding: "2px 4px", fontSize: 10,
              border: "1px dashed var(--border-strong)", borderRadius: 3,
              background: "var(--bg-panel)", color: "var(--text-muted)",
            }}
          >
            <option value="">+ 멤버</option>
            {members
              .filter((m) => m.default_division !== null)
              .filter((m) => !DIVISIONS.some((d) => currentBoard[d].some((s) => s.memberId === m.id)))
              .map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
          </select>
        )}
      </div>
    </div>
  );
}
