import type { RefObject } from "react";
import { DIVISIONS } from "./types";
import type { DivisionBoard } from "../../utils/syndicateEngine";
import { CheckSealIcon } from "./icons";

interface Props {
  fileInputRef: RefObject<HTMLInputElement | null>;
  visionLoading: boolean;
  visionStatus: { kind: "ok" | "warn" | "err"; msg: string } | null;
  currentBoard: DivisionBoard;
  onFileSelected: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onPasteFromClipboard: () => void;
  onCopyTargetToCurrent: () => void;
  onPromoteCurrentToTarget: () => void;
  onClearCurrentBoard: () => void;
}

export function VisionControls({
  fileInputRef, visionLoading, visionStatus, currentBoard,
  onFileSelected, onPasteFromClipboard,
  onCopyTargetToCurrent, onPromoteCurrentToTarget, onClearCurrentBoard,
}: Props) {
  const allEmpty = DIVISIONS.every((d) => currentBoard[d].length === 0);

  return (
    <>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        marginBottom: 6, flexWrap: "wrap", gap: 4,
      }}>
        <strong style={{ fontSize: 13, color: "var(--text-primary)" }}>현재 인게임 상태</strong>
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
              padding: "3px 8px", fontSize: 11, border: "1px solid var(--status-warning)",
              background: "var(--status-warning-bg)", color: "var(--status-warning)",
              borderRadius: 3, cursor: visionLoading ? "wait" : "pointer", fontWeight: 600,
            }}
            title="POE Syndicate 패널 스크린샷 → Claude Vision으로 자동 입력"
          >
            {visionLoading ? "분석중..." : "이미지에서"}
          </button>
          <button
            onClick={onPasteFromClipboard}
            disabled={visionLoading}
            style={{
              padding: "3px 8px", fontSize: 11, border: "1px solid var(--status-warning)",
              background: "var(--status-warning-bg)", color: "var(--status-warning)",
              borderRadius: 3, cursor: visionLoading ? "wait" : "pointer",
            }}
            title="클립보드의 스크린샷에서 가져오기 (PrtScr 후 클릭)"
          >
            붙여넣기
          </button>
          <button
            onClick={onCopyTargetToCurrent}
            style={{
              padding: "3px 8px", fontSize: 11, border: "1px solid var(--status-info)",
              background: "var(--status-info-bg)", color: "var(--status-info)",
              borderRadius: 3, cursor: "pointer",
            }}
            title="목표 레이아웃을 현재 상태로 복사 (이미 도달했을 때)"
          >
            ← 목표
          </button>
          <button
            onClick={onPromoteCurrentToTarget}
            disabled={allEmpty}
            style={{
              padding: "3px 8px", fontSize: 11, border: "1px solid var(--status-success)",
              background: "var(--status-success-bg)", color: "var(--status-success)",
              borderRadius: 3, cursor: "pointer", fontWeight: 600,
            }}
            title="현재 상태를 목표로 설정 (예: 가이드 이미지 분석 후 저장). 커스텀 프리셋으로 잠김."
          >
            <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
              현재 → 목표 <CheckSealIcon size={12} title="확정" />
            </span>
          </button>
          <button
            onClick={onClearCurrentBoard}
            style={{
              padding: "3px 8px", fontSize: 11, border: "1px dashed var(--border-strong)",
              background: "var(--bg-panel)", color: "var(--text-muted)",
              borderRadius: 3, cursor: "pointer",
            }}
          >
            비우기
          </button>
        </div>
      </div>
      {visionStatus && (
        <div
          style={{
            marginBottom: 6, padding: "4px 8px", fontSize: 11, borderRadius: 3,
            background:
              visionStatus.kind === "ok" ? "var(--status-success-bg)" :
              visionStatus.kind === "warn" ? "var(--status-warning-bg)" : "var(--status-danger-bg)",
            color:
              visionStatus.kind === "ok" ? "var(--status-success)" :
              visionStatus.kind === "warn" ? "var(--status-warning)" : "var(--status-danger)",
          }}
          aria-live="polite"
        >
          {visionStatus.msg}
        </div>
      )}
    </>
  );
}
