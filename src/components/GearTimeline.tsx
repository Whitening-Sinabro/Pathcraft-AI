import type { GearSlotProgression } from "../types";

export function GearTimeline({ progression }: { progression: GearSlotProgression[] }) {
  if (!progression?.length) return null;

  return (
    <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
      <h3 style={{ margin: "0 0 12px", fontSize: 15 }}>장비 진행</h3>
      {progression.map((slot, si) => {
        const prioColor = (p: string) =>
          p === "필수" ? "#e03131" : p === "권장" ? "#f59f00" : "#2b8a3e";
        return (
          <div key={si} style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#495057", marginBottom: 6 }}>{slot.slot}</div>
            <div style={{ display: "flex", alignItems: "stretch", gap: 0 }}>
              {slot.phases.map((p, pi) => (
                <div key={pi} style={{ display: "flex", alignItems: "center" }}>
                  <div style={{
                    padding: "8px 12px", borderRadius: 6, border: "1px solid #e9ecef",
                    background: "#f8f9fa", minWidth: 130, fontSize: 12,
                  }}>
                    <div style={{ fontSize: 10, color: "#868e96", marginBottom: 2 }}>{p.phase}</div>
                    <div style={{ fontWeight: 600, marginBottom: 3 }}>{p.item}</div>
                    <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>
                      {p.key_stats?.join(", ")}
                    </div>
                    <div style={{ fontSize: 11 }}>{p.acquisition}</div>
                    <span style={{
                      display: "inline-block", marginTop: 4, fontSize: 10, padding: "1px 6px",
                      borderRadius: 3, background: prioColor(p.priority) + "18",
                      color: prioColor(p.priority), fontWeight: 600,
                    }}>{p.priority}</span>
                  </div>
                  {pi < slot.phases.length - 1 && (
                    <span style={{ padding: "0 6px", color: "#ced4da", fontSize: 18, fontWeight: 700 }}>→</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </section>
  );
}
