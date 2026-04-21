import { useEffect, useState } from "react";
import { SyndicateTutorial } from "./SyndicateTutorial";
import { PresetPicker } from "./syndicate/PresetPicker";
import { TargetPreview } from "./syndicate/TargetPreview";
import { CurrentBoard } from "./syndicate/CurrentBoard";
import { Recommendations } from "./syndicate/Recommendations";
import { MemberDetail } from "./syndicate/MemberDetail";
import { AssignPalette } from "./syndicate/AssignPalette";
import { useSyndicateBoard } from "./syndicate/useSyndicateBoard";

interface Props {
  buildJson?: string;
  recommendation?: { layout_id: string; reason: string } | null;
}

export function SyndicateBoard({ buildJson: _buildJson, recommendation }: Props) {
  const s = useSyndicateBoard({ recommendation });
  // 추천 hover → 보드 슬롯 강조 (S3b)
  const [hoveredMemberId, setHoveredMemberId] = useState<string | null>(null);
  // Cmd+K 멤버 할당 팔레트 (S3c)
  const [paletteOpen, setPaletteOpen] = useState(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && (e.key === "k" || e.key === "K")) {
        e.preventDefault();
        setPaletteOpen((v) => !v);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <section className="ui-card">
      <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "var(--status-warning)" }}>
        Syndicate 보드 (Jun Betrayal)
      </h3>

      <SyndicateTutorial />

      {s.recommendedLayout && recommendation && (
        <div
          style={{
            padding: 10, marginBottom: 10, borderRadius: 6, fontSize: 13,
            background: "var(--status-success-bg)", color: "var(--status-success)",
          }}
        >
          <strong>AI 추천 레이아웃: {s.recommendedLayout.name}</strong>
          <p style={{ margin: "4px 0 6px", fontSize: 12, color: "var(--text-secondary)" }}>
            {recommendation.reason}
          </p>
          <button
            onClick={() => s.applyLayout(s.recommendedLayout!.id)}
            className="ui-button ui-button--primary"
            style={{ padding: "4px 12px", fontSize: 12, fontWeight: 600 }}
          >
            이 레이아웃 적용
          </button>
        </div>
      )}

      <PresetPicker
        layouts={s.layouts}
        selectedLayoutId={s.selectedLayoutId}
        onApply={s.applyLayout}
        onClear={s.clearBoard}
      />

      {s.selectedLayoutId && (
        <TargetPreview
          board={s.board}
          currentBoard={s.currentBoard}
          memberMap={s.memberMap}
          onSelectMember={s.setSelectedMember}
          hoveredMemberId={hoveredMemberId}
        />
      )}

      <CurrentBoard
        currentBoard={s.currentBoard}
        members={s.members}
        memberMap={s.memberMap}
        delta={s.delta}
        fileInputRef={s.fileInputRef}
        visionLoading={s.visionLoading}
        visionStatus={s.visionStatus}
        onFileSelected={s.onFileSelected}
        onPasteFromClipboard={s.onPasteFromClipboard}
        onCopyTargetToCurrent={s.copyTargetToCurrent}
        onPromoteCurrentToTarget={s.promoteCurrentToTarget}
        onClearCurrentBoard={s.clearCurrentBoard}
        onAddOrMoveMember={s.addOrMoveCurrentMember}
        onSetRank={s.setCurrentRank}
        onRemoveSlot={s.removeCurrentSlot}
      />

      <Recommendations recs={s.recs} delta={s.delta} onHoverMember={setHoveredMemberId} />

      {s.selectedMember && (
        <MemberDetail
          member={s.selectedMember}
          onClose={() => s.setSelectedMember(null)}
        />
      )}

      <AssignPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        members={s.members}
        currentBoard={s.currentBoard}
        onAssign={(memberId, division, rank) => {
          s.addOrMoveCurrentMember(division, memberId);
          s.setCurrentRank(division, memberId, rank);
        }}
      />
    </section>
  );
}
