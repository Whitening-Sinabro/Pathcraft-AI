import { useEffect, useMemo, useRef, useState } from "react";
import { DIVISIONS, type Division, type SyndicateMember } from "./types";
import type { DivisionBoard, Rank } from "../../utils/syndicateEngine";

interface Candidate {
  member: SyndicateMember;
  division: Division;
  rank: Rank;
  currentLocation: string | null; // "Research Leader" 등
}

interface Props {
  open: boolean;
  onClose: () => void;
  members: SyndicateMember[];
  currentBoard: DivisionBoard;
  onAssign: (memberId: string, division: Division, rank: Rank) => void;
}

/** 토큰 하나가 candidate의 textBlob에 포함되면 match. 대소문자 무시. */
function matchesQuery(blob: string, tokens: string[]): boolean {
  if (tokens.length === 0) return true;
  const lower = blob.toLowerCase();
  return tokens.every((t) => lower.includes(t));
}

/** "aisling res l" → member=aisling, division=Research, rank=Leader 후보를 상위로. */
function filterCandidates(query: string, members: SyndicateMember[], currentBoard: DivisionBoard): Candidate[] {
  const tokens = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const currentLocMap = new Map<string, string>();
  for (const div of DIVISIONS) {
    for (const s of currentBoard[div]) {
      currentLocMap.set(s.memberId, `${div} ${s.rank}`);
    }
  }

  const result: Candidate[] = [];
  for (const m of members) {
    if (!m.default_division) continue; // Catarina 제외
    for (const division of DIVISIONS) {
      for (const rank of ["Leader", "Member"] as Rank[]) {
        const blob = `${m.name} ${m.id} ${division} ${rank}`;
        if (!matchesQuery(blob, tokens)) continue;
        result.push({
          member: m,
          division,
          rank,
          currentLocation: currentLocMap.get(m.id) ?? null,
        });
      }
    }
  }

  // 정렬: default_division + Leader가 상위. 이미 현재 보드에 있는 조합은 하위.
  result.sort((a, b) => {
    const aDefault = a.member.default_division === a.division ? 1 : 0;
    const bDefault = b.member.default_division === b.division ? 1 : 0;
    if (aDefault !== bDefault) return bDefault - aDefault;
    const aLeader = a.rank === "Leader" ? 1 : 0;
    const bLeader = b.rank === "Leader" ? 1 : 0;
    if (aLeader !== bLeader) return bLeader - aLeader;
    return a.member.name.localeCompare(b.member.name);
  });

  return result.slice(0, 12);
}

export function AssignPalette({ open, onClose, members, currentBoard, onAssign }: Props) {
  const [query, setQuery] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const candidates = useMemo(
    () => (open ? filterCandidates(query, members, currentBoard) : []),
    [query, members, currentBoard, open],
  );

  // 쿼리 바뀌면 선택 0으로 리셋
  useEffect(() => { setSelectedIdx(0); }, [query]);

  // 오픈 시 input focus + 쿼리 초기화
  useEffect(() => {
    if (!open) return;
    setQuery("");
    setSelectedIdx(0);
    // 다음 tick에 focus (모달 마운트 후)
    const t = setTimeout(() => inputRef.current?.focus(), 0);
    return () => clearTimeout(t);
  }, [open]);

  // 키보드 네비
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIdx((i) => Math.min(i + 1, Math.max(0, candidates.length - 1)));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIdx((i) => Math.max(0, i - 1));
      } else if (e.key === "Enter") {
        e.preventDefault();
        const c = candidates[selectedIdx];
        if (c) {
          onAssign(c.member.id, c.division, c.rank);
          onClose();
        }
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, candidates, selectedIdx, onAssign, onClose]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-label="멤버 할당 팔레트"
      onClick={onClose}
      style={{
        position: "fixed", inset: 0, zIndex: 10000,
        background: "rgba(0,0,0,0.55)",
        display: "flex", alignItems: "flex-start", justifyContent: "center",
        paddingTop: "10vh",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(560px, 90vw)",
          background: "var(--bg-panel)",
          border: "1px solid var(--border-default)",
          borderRadius: 8,
          boxShadow: "0 10px 32px rgba(0,0,0,0.5)",
          overflow: "hidden",
        }}
      >
        <input
          ref={inputRef}
          type="text"
          placeholder="멤버 이름 + 분과 + rank (예: aisling res l) · Esc 닫기 / ↑↓ 선택 / Enter 적용"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: "100%", padding: "12px 14px", fontSize: 14,
            background: "transparent",
            border: "none",
            borderBottom: "1px solid var(--border-default)",
            color: "var(--text-primary)",
            outline: "none",
            boxSizing: "border-box",
          }}
        />
        <ul
          role="listbox"
          aria-label="멤버 후보"
          style={{ listStyle: "none", margin: 0, padding: 0, maxHeight: "50vh", overflowY: "auto" }}
        >
          {candidates.length === 0 ? (
            <li style={{ padding: "12px 14px", fontSize: 12, color: "var(--text-muted)" }}>
              일치하는 멤버 없음. 쿼리를 다듬거나 Esc로 닫기.
            </li>
          ) : (
            candidates.map((c, i) => (
              <li
                key={`${c.member.id}-${c.division}-${c.rank}`}
                role="option"
                aria-selected={i === selectedIdx}
                onMouseEnter={() => setSelectedIdx(i)}
                onClick={() => {
                  onAssign(c.member.id, c.division, c.rank);
                  onClose();
                }}
                style={{
                  padding: "8px 14px", cursor: "pointer",
                  display: "flex", alignItems: "center", gap: 8, fontSize: 13,
                  background: i === selectedIdx ? "var(--bg-elevated)" : "transparent",
                  borderLeft: i === selectedIdx
                    ? "3px solid var(--accent-primary)"
                    : "3px solid transparent",
                  color: "var(--text-primary)",
                }}
              >
                <strong style={{ minWidth: 140 }}>{c.member.name}</strong>
                <span className="ui-text-secondary">{c.division}</span>
                <span
                  style={{
                    fontSize: 10, padding: "1px 6px", borderRadius: 3,
                    background: c.rank === "Leader" ? "var(--status-warning-bg)" : "var(--bg-elevated)",
                    color: c.rank === "Leader" ? "var(--status-warning)" : "var(--text-muted)",
                    fontWeight: 700,
                  }}
                >
                  {c.rank === "Leader" ? "L" : "M"}
                </span>
                {c.currentLocation && (
                  <span className="ui-text-muted" style={{ fontSize: 10, marginLeft: "auto" }}>
                    현: {c.currentLocation}
                  </span>
                )}
              </li>
            ))
          )}
        </ul>
        <div
          style={{
            padding: "6px 14px", fontSize: 11, color: "var(--text-muted)",
            borderTop: "1px solid var(--border-default)", background: "var(--bg-base)",
          }}
        >
          팁: "aisling res l" = Aisling을 Research Leader로 · Enter 적용 · Esc 닫기
        </div>
      </div>
    </div>
  );
}
