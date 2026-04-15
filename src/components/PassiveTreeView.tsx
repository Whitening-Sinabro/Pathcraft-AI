import { useMemo, useState } from "react";
import { PassiveTreeCanvas } from "./PassiveTreeCanvas";
import { decodeTreeUrl } from "../utils/passiveTreeUrl";

interface Props {
  // PoB 빌드에서 추출된 passive_tree_url. 있으면 자동 디코드 → 할당 노드 하이라이트.
  url?: string;
}

export function PassiveTreeView({ url }: Props) {
  const [expanded, setExpanded] = useState(false);
  const w = expanded ? 1400 : 900;
  const h = expanded ? 900 : 600;

  const decoded = useMemo(() => (url ? decodeTreeUrl(url) : null), [url]);
  const initialAllocated = useMemo(
    () => (decoded ? new Set(decoded.nodes) : undefined),
    [decoded],
  );
  const buildClass = decoded?.classIndex;
  const buildAsc = decoded?.ascendancyIndex;

  return (
    <section
      style={{
        padding: 16, background: "#fff", borderRadius: 8,
        border: "1px solid #e9ecef",
      }}
    >
      <div
        style={{
          display: "flex", justifyContent: "space-between",
          alignItems: "center", marginBottom: 8,
        }}
      >
        <h3 style={{ margin: 0, fontSize: 15 }}>패시브 트리</h3>
        <div style={{ display: "flex", gap: 6 }}>
          <button
            onClick={() => setExpanded((v) => !v)}
            style={{
              padding: "4px 10px", fontSize: 11,
              border: "1px solid #dee2e6", background: "#f8f9fa",
              borderRadius: 3, cursor: "pointer", color: "#495057",
            }}
          >
            {expanded ? "축소" : "크게"}
          </button>
          {url && (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: "4px 10px", fontSize: 11,
                border: "1px solid #4dabf7", background: "#e7f5ff",
                borderRadius: 3, textDecoration: "none", color: "#1864ab",
              }}
            >
              POE 공식 뷰어
            </a>
          )}
        </div>
      </div>

      <PassiveTreeCanvas
        key={url || "empty"}
        width={w}
        height={h}
        initialAllocated={initialAllocated}
        buildClass={buildClass}
        buildAscendancy={buildAsc}
      />
      {decoded && (
        <div style={{ marginTop: 6, fontSize: 11, color: "#37b24d" }}>
          빌드 로드: class {decoded.classIndex} / asc {decoded.ascendancyIndex} /
          노드 {decoded.nodes.length}개 하이라이트됨
        </div>
      )}

      <div style={{ marginTop: 6, fontSize: 11, color: "#868e96" }}>
        클래스 선택 → 클릭으로 노드 할당. 빌드 로드 시 해당 빌드의 노드가 자동 표시됨.
      </div>
    </section>
  );
}
