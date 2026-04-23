import type { CoachResult } from "../../types";

interface Props {
  priorities: CoachResult["passive_priority"];
}

export function PassivePrioritySection({ priorities }: Props) {
  if (!priorities?.length) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">패시브 트리 우선순위</h3>
      <ol style={{ margin: 0, paddingLeft: 20 }}>
        {priorities.map((p, i) => <li key={i} style={{ marginBottom: 4 }}>{p}</li>)}
      </ol>
      <div className="ui-text-muted" style={{ marginTop: 8, fontSize: 11 }}>
        실제 트리 뷰어는 좌측 사이드바 <strong>패시브 트리</strong> 탭에서 확인.
      </div>
    </section>
  );
}
