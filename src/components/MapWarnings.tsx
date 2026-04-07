import type { MapModWarnings } from "../types";

export function MapWarnings({ warnings }: { warnings: MapModWarnings }) {
  if (!warnings || (!warnings.deadly?.length && !warnings.dangerous?.length)) return null;

  return (
    <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
      <h3 style={{ margin: "0 0 10px", fontSize: 15, color: "#e03131" }}>맵 모드 경고</h3>
      <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
        {warnings.deadly?.length > 0 && (
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#e03131", marginBottom: 4 }}>금지</div>
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
              {warnings.deadly.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        )}
        {warnings.dangerous?.length > 0 && (
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#f59f00", marginBottom: 4 }}>주의</div>
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
              {warnings.dangerous.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        )}
        {warnings.caution?.length > 0 && (
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#868e96", marginBottom: 4 }}>참고</div>
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
              {warnings.caution.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        )}
      </div>
      {warnings.regex_filter && (
        <div style={{ padding: 8, background: "#f8f9fa", borderRadius: 4, fontSize: 12, fontFamily: "monospace" }}>
          <span style={{ color: "#868e96" }}>regex: </span>
          <code style={{ userSelect: "all", color: "#228be6" }}>{warnings.regex_filter}</code>
        </div>
      )}
    </section>
  );
}
