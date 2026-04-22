import type { CoachResult } from "../../types";
import { useChecklist } from "../../contexts/ChecklistContext";

interface Props {
  guide: CoachResult["leveling_guide"];
}

const PHASE_LABEL: Record<string, string> = {
  act1_4: "Act 1-4",
  act5_10: "Act 5-10",
  early_maps: "초반 맵",
  endgame: "엔드게임",
};

export function LevelingGuideSection({ guide }: Props) {
  const { checked, toggle, ck } = useChecklist();
  const safeGuide = guide && typeof guide === "object" ? guide : {};

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">
        레벨링 가이드 <span className="ui-section-title__hint">(체크로 진행도 추적)</span>
      </h3>
      {Object.entries(safeGuide).map(([key, val]) => {
        const chkKey = ck(`lvguide_${key}`);
        const done = !!checked[chkKey];
        return (
          <div
            key={key}
            style={{
              marginBottom: 8,
              padding: 8,
              borderRadius: 4,
              background: done ? "var(--status-success-bg)" : "transparent",
              opacity: done ? 0.7 : 1,
            }}
          >
            <label style={{ display: "flex", alignItems: "flex-start", gap: 8, cursor: "pointer" }}>
              <input type="checkbox" checked={done} onChange={() => toggle(chkKey)} style={{ marginTop: 3 }} />
              <div style={{ flex: 1 }}>
                <strong
                  className={done ? "ui-text-success" : ""}
                  style={{ textDecoration: done ? "line-through" : "none" }}
                >
                  {PHASE_LABEL[key] ?? "엔드게임"}
                </strong>
                <p className="ui-text-secondary" style={{ margin: "2px 0 0", fontSize: 14 }}>{typeof val === "string" ? val : JSON.stringify(val)}</p>
              </div>
            </label>
          </div>
        );
      })}
    </section>
  );
}
