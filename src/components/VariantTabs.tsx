import { useState } from "react";
import type { VariantSnapshot } from "../types";

export function VariantTabs({ snapshots }: { snapshots: VariantSnapshot[] }) {
  const [active, setActive] = useState(0);

  if (!snapshots?.length) return null;

  const v = snapshots[active];

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">구간별 진행</h3>
      <div style={{ display: "flex", gap: 4, marginBottom: 12, flexWrap: "wrap" }}>
        {snapshots.map((s, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            className={active === i ? "ui-button ui-button--primary" : "ui-button ui-button--secondary"}
            style={{ fontSize: 12 }}
          >
            {s.phase}
          </button>
        ))}
      </div>
      {v && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 13 }}>
          <div>
            <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 2 }}>레벨</div>
            <div style={{ fontWeight: 600 }}>{v.level_range}</div>
          </div>
          <div>
            <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 2 }}>메인 스킬</div>
            <div>{v.main_skill}</div>
          </div>
          <div>
            <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 2 }}>오라</div>
            <div>{v.auras}</div>
          </div>
          <div>
            <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 2 }}>패시브 방향</div>
            <div>{v.passive_focus}</div>
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 2 }}>장비 우선순위</div>
            <div>{v.gear_priority}</div>
          </div>
          {v.defense_target && (
            <div className="ui-card--inset" style={{ gridColumn: "1 / -1", display: "flex", gap: 16, padding: 8 }}>
              <span>Life: <strong>{v.defense_target.life?.toLocaleString()}</strong></span>
              {v.defense_target.energy_shield > 0 && <span>ES: <strong>{v.defense_target.energy_shield?.toLocaleString()}</strong></span>}
              <span>저항: <strong>{v.defense_target.resists}</strong></span>
              {v.defense_target.armour_or_evasion && <span>방어: <strong>{v.defense_target.armour_or_evasion}</strong></span>}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
