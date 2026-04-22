// UI controls overlay — class/ascendancy dropdowns, search, points counter, guide.
// Pure presentational component: reads props, dispatches callbacks.
// classNames / ascendancies 는 game-aware (POE1 7 + POE2 8) 로 Canvas 에서 주입.

import type { RefObject } from "react";

interface Props {
  // state
  loaded: boolean;
  nodeCount: number;
  // game-aware tables
  classNames: readonly string[];
  ascendancies: Record<number, string[]>;
  selectedClass: number | null;
  selectedAscendancy: string | null;
  searchQuery: string;
  searchMatchCount: number;
  pointsUsed: number;
  jewelSockets: number;
  // refs/handlers
  searchInputRef: RefObject<HTMLInputElement | null>;
  onPickClass: (idx: number) => void;
  onPickAscendancy: (asc: string | null) => void;
  onSearchChange: (q: string) => void;
}

export function TreeControls({
  loaded, nodeCount,
  classNames, ascendancies,
  selectedClass, selectedAscendancy,
  searchQuery, searchMatchCount,
  pointsUsed, jewelSockets,
  searchInputRef,
  onPickClass, onPickAscendancy, onSearchChange,
}: Props) {
  if (!loaded) return null;

  return (
    <>
      {/* 좌상단 클래스 + 어센던시 드롭다운 */}
      <div
        style={{
          position: "absolute", left: 8, top: 8,
          display: "flex", gap: 6, alignItems: "center",
        }}
      >
        <select
          value={selectedClass ?? ""}
          onChange={(e) => {
            const v = e.target.value;
            if (v === "") return;
            onPickClass(parseInt(v, 10));
          }}
          style={{
            padding: "5px 10px", fontSize: 12,
            background: selectedClass != null ? "#e8c068" : "rgba(0,0,0,0.75)",
            color: selectedClass != null ? "#000" : "#ccc",
            border: `1px solid ${selectedClass != null ? "#e8c068" : "#4a3f2a"}`,
            borderRadius: 3, cursor: "pointer",
            fontWeight: selectedClass != null ? 700 : 400,
            outline: "none",
          }}
        >
          <option value="" disabled>클래스 선택</option>
          {classNames.map((name, i) => (
            <option key={i} value={i}>{name}</option>
          ))}
        </select>
        {selectedClass != null && ascendancies[selectedClass] && (
          <select
            value={selectedAscendancy ?? ""}
            onChange={(e) => onPickAscendancy(e.target.value || null)}
            style={{
              padding: "5px 10px", fontSize: 12,
              background: selectedAscendancy ? "#5dade2" : "rgba(0,0,0,0.75)",
              color: selectedAscendancy ? "#000" : "#ccc",
              border: `1px solid ${selectedAscendancy ? "#5dade2" : "#2a3f4a"}`,
              borderRadius: 3, cursor: "pointer",
              fontWeight: selectedAscendancy ? 700 : 400,
              outline: "none",
            }}
          >
            <option value="">어센던시 없음</option>
            {ascendancies[selectedClass].map((asc) => (
              <option key={asc} value={asc}>{asc}</option>
            ))}
          </select>
        )}
      </div>

      {/* 우상단 검색 + 노드 카운트 */}
      <div style={{ position: "absolute", right: 8, top: 8, display: "flex", gap: 6, alignItems: "center" }}>
        <input
          ref={searchInputRef}
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="검색 (Ctrl+F)"
          style={{
            width: 160, padding: "3px 8px", fontSize: 11,
            background: "rgba(0,0,0,0.75)", color: "#fff",
            border: "1px solid #4a3f2a", borderRadius: 3,
            outline: "none",
          }}
        />
        {searchQuery && (
          <span
            style={{
              background: "rgba(0,0,0,0.75)", color: "#5dade2",
              padding: "2px 8px", borderRadius: 3, fontSize: 10,
            }}
          >
            {searchMatchCount} matches
          </span>
        )}
        <span
          style={{
            background: "rgba(0,0,0,0.6)", color: "#aaa",
            padding: "2px 8px", borderRadius: 3, fontSize: 10,
          }}
        >
          {nodeCount} nodes
        </span>
      </div>

      {/* 좌하단 포인트 카운터 */}
      <div
        style={{
          position: "absolute", left: 8, bottom: 8,
          background: "rgba(0,0,0,0.75)", color: "#e8c068",
          padding: "4px 10px", borderRadius: 3, fontSize: 12,
          border: "1px solid #4a3f2a", pointerEvents: "none",
          fontWeight: 600,
        }}
      >
        {pointsUsed} pts{jewelSockets > 0 && ` · ${jewelSockets} sockets`}
      </div>

      {/* 우하단 사용법 가이드 */}
      <div
        style={{
          position: "absolute", right: 8, bottom: 8,
          background: "rgba(0,0,0,0.82)", color: "#bbb",
          padding: "8px 12px", borderRadius: 4, fontSize: 11,
          border: "1px solid #4a3f2a", pointerEvents: "none",
          maxWidth: 260, lineHeight: 1.5,
        }}
      >
        <div style={{ color: "#e8c068", fontWeight: 600, marginBottom: 4 }}>
          사용법
        </div>
        <div><b style={{ color: "#fff" }}>좌클릭</b> 빈 노드 — 최단 경로로 자동 할당</div>
        <div><b style={{ color: "#fff" }}>좌클릭</b> 할당된 노드 — 해당 + 도달 불가 하위 해제</div>
        <div><b style={{ color: "#fff" }}>드래그</b> 이동 · <b style={{ color: "#fff" }}>휠</b> 줌</div>
        <div><b style={{ color: "#fff" }}>Ctrl+Z / Ctrl+Y</b> 되돌리기 / 다시</div>
        <div><b style={{ color: "#fff" }}>Ctrl+F</b> 노드 검색 (이름/옵션)</div>
      </div>
    </>
  );
}
