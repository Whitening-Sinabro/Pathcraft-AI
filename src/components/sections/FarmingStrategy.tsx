import type { CoachResult } from "../../types";

interface Props {
  strategy: CoachResult["farming_strategy"];
}

export function FarmingStrategySection({ strategy }: Props) {
  if (!strategy) return null;

  if (typeof strategy === "string") {
    return (
      <section className="ui-card">
        <h3 className="ui-section-title ui-text-success">파밍 전략</h3>
        <p style={{ margin: 0, fontSize: 13 }}>{strategy}</p>
      </section>
    );
  }

  return (
    <section className="ui-card">
      <h3 className="ui-section-title ui-text-success">파밍 전략</h3>

      {strategy.recommended_mechanics?.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <strong style={{ fontSize: 13 }}>추천 메카닉</strong>
          <div style={{ display: "flex", gap: 6, marginTop: 4, flexWrap: "wrap" }}>
            {strategy.recommended_mechanics.map((m, i) => (
              <span key={i} className={i === 0 ? "ui-badge ui-badge--success" : "ui-badge ui-badge--info"}>
                {m}
              </span>
            ))}
          </div>
        </div>
      )}

      {strategy.atlas_passive_focus && (
        <div
          className="ui-card--inset"
          style={{ marginBottom: 10, padding: 8, fontSize: 13 }}
        >
          <strong>아틀라스 패시브:</strong> {strategy.atlas_passive_focus}
        </div>
      )}

      <table className="ui-table">
        <tbody>
          {strategy.early_atlas && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>초반</td>
              <td>{strategy.early_atlas}</td>
            </tr>
          )}
          {strategy.mid_atlas && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>중반</td>
              <td>{strategy.mid_atlas}</td>
            </tr>
          )}
          {strategy.late_atlas && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>후반</td>
              <td>{strategy.late_atlas}</td>
            </tr>
          )}
          {strategy.ssf_crafting_focus && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>크래프팅</td>
              <td>{strategy.ssf_crafting_focus}</td>
            </tr>
          )}
        </tbody>
      </table>

      {strategy.scarab_priority?.length > 0 && (
        <div className="ui-text-muted" style={{ marginTop: 8, fontSize: 12 }}>
          스카랍: {strategy.scarab_priority.join(", ")}
        </div>
      )}
    </section>
  );
}
