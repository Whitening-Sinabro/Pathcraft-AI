import type { CoachResult } from "../../types";

interface Props {
  progression: CoachResult["aura_utility_progression"];
}

export function AuraUtilitySection({ progression }: Props) {
  if (!progression?.length) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">오라 / 유틸리티 진행</h3>
      <table className="ui-table">
        <thead>
          <tr>
            <th>구간</th>
            <th>오라 / 전령</th>
            <th>예약</th>
            <th>유틸리티 / 가드</th>
          </tr>
        </thead>
        <tbody>
          {progression.map((phase, i) => (
            <tr key={i}>
              <td style={{ fontWeight: 600, whiteSpace: "nowrap" }}>{phase.phase}</td>
              <td>
                {phase.auras?.length > 0 && <div>{phase.auras.join(", ")}</div>}
                {phase.heralds?.length > 0 && (
                  <div className="ui-text-info">{phase.heralds.join(", ")}</div>
                )}
              </td>
              <td>{phase.reservation_total}</td>
              <td>
                {phase.utility?.length > 0 && <div>{phase.utility.join(", ")}</div>}
                {phase.guard && <div className="ui-text-secondary">가드: {phase.guard}</div>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
