import type { CoachResult, LevelingSkillOption, LinksProgression } from "../../types";
import { useChecklist } from "../../contexts/ChecklistContext";

interface Props {
  skills: CoachResult["leveling_skills"];
}

function safetyClass(s: string): string {
  if (s === "높음") return "ui-text-success";
  if (s === "낮음") return "ui-text-danger";
  return "ui-text-warning";
}

function ProgressionList({
  items,
  prefix,
}: {
  items: LinksProgression[];
  prefix: string;
}) {
  const { checked, toggle, ck } = useChecklist();
  return (
    <div style={{ marginTop: 6 }}>
      {items.map((p, i) => {
        const chkKey = ck(`${prefix}_${i}`);
        const done = !!checked[chkKey];
        return (
          <label
            key={i}
            style={{
              display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 3,
              fontSize: 13, cursor: "pointer", opacity: done ? 0.6 : 1,
            }}
          >
            <input type="checkbox" checked={done} onChange={() => toggle(chkKey)} style={{ marginTop: 3 }} />
            <span
              style={{
                minWidth: 130, fontWeight: 600, color: "var(--status-info)",
                fontFamily: "var(--font-mono)", textDecoration: done ? "line-through" : "none",
              }}
            >
              {p.level_range}
            </span>
            <span
              className="ui-text-secondary"
              style={{ flex: 1, textDecoration: done ? "line-through" : "none" }}
            >
              {p.gems.join(" + ")}
            </span>
          </label>
        );
      })}
    </div>
  );
}

function OptionCard({ opt }: { opt: LevelingSkillOption }) {
  return (
    <div className="ui-card--inset">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <strong style={{ fontSize: 13 }}>{opt.name}</strong>
        <div style={{ display: "flex", gap: 8, fontSize: 11 }}>
          <span className="ui-text-secondary">속도 <strong>{opt.speed}</strong></span>
          <span className={safetyClass(opt.safety)}>안전 <strong>{opt.safety}</strong></span>
        </div>
      </div>
      {opt.links_progression && opt.links_progression.length > 0 ? (
        <div style={{ marginBottom: 4 }}>
          {opt.links_progression.map((p, j) => (
            <div key={j} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 2, fontSize: 12 }}>
              <span style={{
                minWidth: 120, fontWeight: 600, color: "var(--status-info)", fontFamily: "var(--font-mono)",
              }}>
                {p.level_range}
              </span>
              <span className="ui-text-secondary" style={{ flex: 1 }}>{p.gems.join(" + ")}</span>
            </div>
          ))}
        </div>
      ) : (
        opt.links && <div className="ui-text-muted" style={{ fontSize: 12, marginBottom: 4 }}>{opt.links}</div>
      )}
      <div className="ui-text-secondary" style={{ fontSize: 12 }}>{opt.reason}</div>
    </div>
  );
}

export function LevelingSkillsSection({ skills }: Props) {
  const { checked, toggle, ck } = useChecklist();

  if (!skills?.recommended) return null;

  const rec = skills.recommended;
  const recHasProgression = rec.links_progression && rec.links_progression.length > 0;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">레벨링 스킬</h3>
      <div
        className="ui-card--inset"
        style={{ marginBottom: 12, background: "var(--accent-subtle)", borderColor: "var(--accent-primary)" }}
      >
        <strong>추천: {rec.name}</strong>
        <span className="ui-text-secondary" style={{ marginLeft: 8, fontSize: 13 }}>({skills.damage_type})</span>
        {recHasProgression ? (
          <ProgressionList items={rec.links_progression!} prefix="rec_lv" />
        ) : (
          rec.links && <div style={{ fontSize: 13, marginTop: 4 }}>링크: {rec.links}</div>
        )}
        <div className="ui-text-secondary" style={{ fontSize: 13, marginTop: 6 }}>
          {rec.reason}
          {rec.transition_level && <span> — 전환: Lv.{rec.transition_level}</span>}
        </div>
      </div>
      {skills.options?.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {skills.options.map((opt, i) => <OptionCard key={i} opt={opt} />)}
        </div>
      )}
      {skills.skill_transitions?.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <strong style={{ fontSize: 13 }}>스킬 전환</strong>
          <div style={{ marginTop: 4 }}>
            {skills.skill_transitions.map((t, i) => {
              const chkKey = ck(`skillt_${i}`);
              const done = !!checked[chkKey];
              return (
                <label
                  key={i}
                  style={{
                    display: "flex", gap: 6, fontSize: 13, alignItems: "flex-start",
                    marginBottom: 2, cursor: "pointer", opacity: done ? 0.6 : 1,
                  }}
                >
                  <input type="checkbox" checked={done} onChange={() => toggle(chkKey)} style={{ marginTop: 3 }} />
                  <span style={{ textDecoration: done ? "line-through" : "none" }}>
                    <strong>Lv.{t.level}</strong>: {t.change} — {t.reason}
                  </span>
                </label>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
