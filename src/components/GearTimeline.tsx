import type { GearSlotProgression } from "../types";
import { useChecklist } from "../contexts/ChecklistContext";

interface GearTimelineProps {
  progression: GearSlotProgression[];
}

function priorityVar(p: string): string {
  if (p === "필수") return "var(--status-danger)";
  if (p === "권장") return "var(--status-warning)";
  return "var(--status-success)";
}

function priorityBg(p: string): string {
  if (p === "필수") return "var(--status-danger-bg)";
  if (p === "권장") return "var(--status-warning-bg)";
  return "var(--status-success-bg)";
}

export function GearTimeline({ progression }: GearTimelineProps) {
  const { checked, toggle, ck } = useChecklist();

  if (!progression?.length) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">
        장비 진행 <span className="ui-section-title__hint">(체크로 획득 완료 표시)</span>
      </h3>
      {progression.map((slot, si) => (
        <div key={si} style={{ marginBottom: 16 }}>
          <div className="ui-text-secondary" style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{slot.slot}</div>
          <div style={{ display: "flex", alignItems: "stretch", gap: 0, flexWrap: "wrap" }}>
            {slot.phases.map((p, pi) => {
              const chkKey = ck(`gear_${si}_${pi}`);
              const done = !!checked[chkKey];
              return (
                <div key={pi} style={{ display: "flex", alignItems: "center" }}>
                  <label style={{
                    padding: "8px 12px", borderRadius: 6,
                    border: "1px solid var(--border-default)",
                    background: done ? "var(--status-success-bg)" : "var(--bg-elevated)",
                    minWidth: 130, fontSize: 12, cursor: "pointer", opacity: done ? 0.75 : 1,
                    display: "flex", flexDirection: "column", gap: 3,
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <input
                        type="checkbox" checked={done}
                        onChange={() => toggle(chkKey)}
                        style={{ margin: 0 }}
                      />
                      <span className="ui-text-muted" style={{ fontSize: 10 }}>{p.phase}</span>
                    </div>
                    <div style={{ fontWeight: 600, textDecoration: done ? "line-through" : "none" }}>{p.item}</div>
                    <div className="ui-text-muted" style={{ fontSize: 11 }}>
                      {p.key_stats?.join(", ")}
                    </div>
                    <div style={{ fontSize: 11 }}>{p.acquisition}</div>
                    <span style={{
                      display: "inline-block", marginTop: 2, fontSize: 10, padding: "1px 6px",
                      borderRadius: 3, background: priorityBg(p.priority),
                      color: priorityVar(p.priority), fontWeight: 600, alignSelf: "flex-start",
                    }}>{p.priority}</span>
                  </label>
                  {pi < slot.phases.length - 1 && (
                    <span className="ui-text-muted" style={{ padding: "0 6px", fontSize: 18, fontWeight: 700 }}>→</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </section>
  );
}
