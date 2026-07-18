import type { CoachResult, RepresentativeProfileSummary } from "../../types";

interface Props {
  priorities: CoachResult["passive_priority"];
  representativeProfile?: RepresentativeProfileSummary | null;
}

export function PassivePrioritySection({ priorities, representativeProfile }: Props) {
  const passivePlan = representativeProfile?.progression?.passive_plan?.slice(0, 4) ?? [];
  if (!priorities?.length && passivePlan.length === 0) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">패시브 트리 우선순위</h3>

      {passivePlan.length > 0 && (
        <div className="ui-card--inset" style={{ marginBottom: 12, borderColor: "var(--status-info)" }}>
          <strong>코퍼스 패시브 방향</strong>
          <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 5 }}>
            {passivePlan.map((step, index) => (
              <div key={`${step.stage}-${step.level_range}-${index}`} style={{ fontSize: 12, lineHeight: 1.5 }}>
                <strong>{step.stage_label || step.stage || "stage"}</strong>
                {step.level_range ? <span className="ui-text-muted"> ({step.level_range})</span> : null}
                {step.active ? <span className="ui-text-success"> | active</span> : null}
                {step.priorities && step.priorities.length > 0 && (
                  <div className="ui-text-muted">{step.priorities.slice(0, 5).join(" / ")}</div>
                )}
                {step.tree_url && (
                  <a
                    href={step.tree_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "var(--status-info)", textDecoration: "none" }}
                  >
                    패시브 트리 열기
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {priorities?.length > 0 && (
        <ol style={{ margin: 0, paddingLeft: 20 }}>
          {priorities.map((p, i) => <li key={i} style={{ marginBottom: 4 }}>{p}</li>)}
        </ol>
      )}

      <div className="ui-text-muted" style={{ marginTop: 8, fontSize: 11 }}>
        실제 트리 뷰어는 좌측 사이드바 <strong>패시브 트리</strong> 탭에서 확인.
      </div>
    </section>
  );
}
