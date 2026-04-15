import type { GearSlotProgression } from "../types";

interface GearTimelineProps {
  progression: GearSlotProgression[];
  checked?: Record<string, boolean>;
  onToggle?: (key: string) => void;
  buildKey?: string;
}

export function GearTimeline({
  progression, checked = {}, onToggle, buildKey = "build",
}: GearTimelineProps) {
  if (!progression?.length) return null;

  return (
    <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
      <h3 style={{ margin: "0 0 12px", fontSize: 15 }}>
        장비 진행 <span style={{ fontSize: 11, fontWeight: 400, color: "#868e96" }}>(체크로 획득 완료 표시)</span>
      </h3>
      {progression.map((slot, si) => {
        const prioColor = (p: string) =>
          p === "필수" ? "#e03131" : p === "권장" ? "#f59f00" : "#2b8a3e";
        return (
          <div key={si} style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#495057", marginBottom: 6 }}>{slot.slot}</div>
            <div style={{ display: "flex", alignItems: "stretch", gap: 0, flexWrap: "wrap" }}>
              {slot.phases.map((p, pi) => {
                const chkKey = `${buildKey}::gear_${si}_${pi}`;
                const done = !!checked[chkKey];
                return (
                  <div key={pi} style={{ display: "flex", alignItems: "center" }}>
                    <label style={{
                      padding: "8px 12px", borderRadius: 6, border: "1px solid #e9ecef",
                      background: done ? "#ebfbee" : "#f8f9fa", minWidth: 130, fontSize: 12,
                      cursor: "pointer", opacity: done ? 0.75 : 1,
                      display: "flex", flexDirection: "column", gap: 3,
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                        <input
                          type="checkbox" checked={done}
                          onChange={() => onToggle && onToggle(chkKey)}
                          style={{ margin: 0 }}
                        />
                        <span style={{ fontSize: 10, color: "#868e96" }}>{p.phase}</span>
                      </div>
                      <div style={{ fontWeight: 600, textDecoration: done ? "line-through" : "none" }}>{p.item}</div>
                      <div style={{ color: "#868e96", fontSize: 11 }}>
                        {p.key_stats?.join(", ")}
                      </div>
                      <div style={{ fontSize: 11 }}>{p.acquisition}</div>
                      <span style={{
                        display: "inline-block", marginTop: 2, fontSize: 10, padding: "1px 6px",
                        borderRadius: 3, background: prioColor(p.priority) + "18",
                        color: prioColor(p.priority), fontWeight: 600, alignSelf: "flex-start",
                      }}>{p.priority}</span>
                    </label>
                    {pi < slot.phases.length - 1 && (
                      <span style={{ padding: "0 6px", color: "#ced4da", fontSize: 18, fontWeight: 700 }}>→</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </section>
  );
}
