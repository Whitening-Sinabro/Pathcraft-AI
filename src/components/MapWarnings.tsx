import type { MapModWarnings } from "../types";

export function MapWarnings({ warnings }: { warnings: MapModWarnings }) {
  if (!warnings || (!warnings.deadly?.length && !warnings.dangerous?.length)) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title ui-text-danger">맵 모드 경고</h3>
      <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
        {warnings.deadly?.length > 0 && (
          <div style={{ flex: 1 }}>
            <div className="ui-text-danger" style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>금지</div>
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
              {warnings.deadly.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        )}
        {warnings.dangerous?.length > 0 && (
          <div style={{ flex: 1 }}>
            <div className="ui-text-warning" style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>주의</div>
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
              {warnings.dangerous.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        )}
        {warnings.caution?.length > 0 && (
          <div style={{ flex: 1 }}>
            <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>참고</div>
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
              {warnings.caution.map((m, i) => <li key={i}>{m}</li>)}
            </ul>
          </div>
        )}
      </div>
      {warnings.regex_filter && (
        <div className="ui-card--inset" style={{ padding: 8, fontSize: 12, fontFamily: "var(--font-mono)" }}>
          <span className="ui-text-muted">regex: </span>
          <code style={{ userSelect: "all", color: "var(--accent-hover)" }}>{warnings.regex_filter}</code>
        </div>
      )}
    </section>
  );
}
