import type { CoachResult } from "../../types";

interface Props {
  zones: CoachResult["danger_zones"];
}

export function DangerZonesSection({ zones }: Props) {
  if (!zones?.length) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title ui-text-danger">위험 요소</h3>
      <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13 }}>
        {zones.map((d, i) => <li key={i}>{d}</li>)}
      </ul>
    </section>
  );
}
