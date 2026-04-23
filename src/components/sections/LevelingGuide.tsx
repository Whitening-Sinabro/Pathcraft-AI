import type { CoachResult } from "../../types";
import { useChecklist } from "../../contexts/ChecklistContext";
import campaignStructurePoe2 from "../../../data/campaign_structure_poe2.json";

interface Props {
  guide: CoachResult["leveling_guide"];
}

// POE1 은 Act 1~10 단일 루프 — 구조 안정, 하드코딩 유지.
const POE1_PHASE_LABEL: Record<string, string> = {
  act1_4: "Act 1-4",
  act5_10: "Act 5-10",
  early_maps: "초반 맵",
  endgame: "엔드게임",
};

// POE2 는 패치마다 Act 구조 변동 (0.3 Cruel 삭제 + Act 4 추가, 0.5 Act 5-6 예정).
// GGPK 파생 campaign_structure_poe2.json 으로 phase key → label 자동 매핑.
// 재생성: `python scripts/build_poe2_campaign_structure.py`.
type Poe2Phase = { key: string; label: string; level_range: number[]; transient?: boolean };
const POE2_PHASE_LABEL: Record<string, string> = Object.fromEntries(
  (campaignStructurePoe2.phases as Poe2Phase[]).map((p) => {
    const lo = p.level_range[0] ?? 0;
    const hi = p.level_range[1] ?? 0;
    const suffix = p.transient ? " (임시)" : "";
    return [p.key, `${p.label} Lv ${lo}-${hi}${suffix}`];
  }),
);

const PHASE_LABEL: Record<string, string> = { ...POE1_PHASE_LABEL, ...POE2_PHASE_LABEL };

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
