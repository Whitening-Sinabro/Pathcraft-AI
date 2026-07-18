import type { CoachResult } from "../../types";

interface Props {
  bridge?: CoachResult["new_player_bridge"];
}

export function NewPlayerBridgeSection({ bridge }: Props) {
  if (!bridge) return null;

  const frictionPoints = bridge.likely_friction_points ?? [];
  const poe2Notes = bridge.poe2_to_poe1_notes ?? [];
  const nextSteps = bridge.beginner_safe_next_steps ?? [];

  if (frictionPoints.length === 0 && poe2Notes.length === 0 && nextSteps.length === 0) {
    return null;
  }

  return (
    <section className="ui-card">
      <h3 className="ui-section-title ui-text-info">초보자 막힘 해소</h3>

      {nextSteps.length > 0 && (
        <div
          className="ui-card--inset"
          style={{ marginBottom: 12, padding: 10, fontSize: 13 }}
        >
          <strong>다음 3개 행동</strong>
          <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
            {nextSteps.slice(0, 3).map((step, index) => (
              <div key={`${index}-${step}`} style={{ display: "flex", gap: 8, lineHeight: 1.5 }}>
                <span className="ui-badge ui-badge--accent" style={{ flex: "0 0 auto" }}>
                  {index + 1}
                </span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {frictionPoints.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 12 }}>
          {frictionPoints.slice(0, 3).map((point) => (
            <div key={point.area} className="ui-card--inset" style={{ padding: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                <strong>{point.area}</strong>
                {point.next_action && (
                  <span className="ui-text-success" style={{ fontSize: 12, fontWeight: 700 }}>
                    다음 행동 있음
                  </span>
                )}
              </div>
              {point.why_it_blocks && (
                <div className="ui-text-muted" style={{ marginTop: 6, fontSize: 12, lineHeight: 1.55 }}>
                  왜 막히나: {point.why_it_blocks}
                </div>
              )}
              {point.what_pathcraft_fills && (
                <div className="ui-text-info" style={{ marginTop: 6, fontSize: 12, lineHeight: 1.55 }}>
                  앱이 채울 부분: {point.what_pathcraft_fills}
                </div>
              )}
              {point.next_action && (
                <div className="ui-text-success" style={{ marginTop: 6, fontSize: 12, lineHeight: 1.55 }}>
                  실행: {point.next_action}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {poe2Notes.length > 0 && (
        <div className="ui-card--inset" style={{ padding: 10 }}>
          <strong>POE2 유입자가 헷갈릴 차이</strong>
          <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 5 }}>
            {poe2Notes.slice(0, 4).map((note) => (
              <div key={note} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.55 }}>
                • {note}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
