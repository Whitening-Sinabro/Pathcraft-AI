import type { CoachResult, RepresentativeProfileSummary } from "../../types";
import { useChecklist } from "../../contexts/ChecklistContext";
import campaignStructurePoe2 from "../../../data/campaign_structure_poe2.json";

interface Props {
  guide: CoachResult["leveling_guide"];
  representativeProfile?: RepresentativeProfileSummary | null;
}

// POE1 은 Act 1~10 단일 루프 — 구조 안정, 하드코딩 유지.
const POE1_PHASE_LABEL: Record<string, string> = {
  act1_4: "액트 1-4",
  act5_10: "액트 5-10",
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

function formatStatus(value?: string) {
  const labels: Record<string, string> = {
    confirmed: "확인됨",
    near_confirmed: "준확인",
    hold: "보류",
    inferred: "추정",
    early_maps: "초반 맵",
    late_endgame: "고점 세팅",
  };
  return value ? labels[value] || value.replace(/_/g, " ") : "-";
}

function formatStage(value?: string) {
  if (!value) return "단계 미기록";
  return formatStatus(value)
    .replace(/Campaign Start/g, "캠페인 시작")
    .replace(/Maps Entry/g, "맵 진입")
    .replace(/High End/g, "고점 세팅");
}

export function LevelingGuideSection({ guide, representativeProfile }: Props) {
  const { checked, toggle, ck } = useChecklist();
  const safeGuide = guide && typeof guide === "object" ? guide : {};
  const profileIdentity = representativeProfile?.identity;
  const profileProgression = representativeProfile?.progression;
  const campaignPlan = profileProgression?.campaign_plan?.slice(0, 5) ?? [];
  const evidence = representativeProfile?.evidence?.filter((entry) => entry.label || entry.url).slice(0, 3) ?? [];

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">
        레벨링 가이드 <span className="ui-section-title__hint">(체크로 진행도 추적)</span>
      </h3>

      {representativeProfile && (
        <div className="ui-card--inset" style={{ marginBottom: 12, borderColor: "var(--status-info)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
            <strong>코퍼스 레벨링 근거</strong>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {profileProgression?.leveling_confidence && (
                <span className="ui-badge ui-badge--success">
                  {formatStatus(profileProgression.leveling_confidence)}
                </span>
              )}
              {representativeProfile.confidence?.representative_build_status && (
                <span className="ui-badge ui-badge--accent">
                  {formatStatus(representativeProfile.confidence.representative_build_status)}
                </span>
              )}
            </div>
          </div>

          <div className="ui-text-muted" style={{ marginTop: 6, fontSize: 12, lineHeight: 1.55 }}>
            {profileIdentity?.leveling_skill || "스타터 미기록"} -&gt; {profileIdentity?.main_skill || "최종 미기록"}
            {" | "}poe.ninja는 엔드게임 변형 근거로만 보고, 레벨링 검증은 단계별 PoB/빌더 루트가 있을 때만 표시합니다.
          </div>

          {campaignPlan.length > 0 && (
            <div style={{ marginTop: 8, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 8 }}>
              {campaignPlan.map((step, index) => (
                <div key={`${step.stage}-${step.level_range}-${index}`} style={{ fontSize: 12, lineHeight: 1.45 }}>
                  <strong>{formatStage(step.stage_label || step.stage)}</strong>
                  <div className="ui-text-muted">
                    {step.level_range || "레벨 ?"} | {step.main_skill || "-"}
                  </div>
                  {step.support_links && step.support_links.length > 0 && (
                    <div className="ui-text-muted">{step.support_links.slice(0, 3).join(" + ")}</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {evidence.length > 0 && (
            <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 8 }}>
              {evidence.map((entry, index) => (
                entry.url ? (
                  <a
                    key={`${entry.url}-${index}`}
                    href={entry.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "var(--status-info)", fontSize: 12, textDecoration: "none" }}
                  >
                    {entry.label || entry.url}
                  </a>
                ) : (
                  <span key={`${entry.label}-${index}`} className="ui-text-muted" style={{ fontSize: 12 }}>
                    {entry.label}
                  </span>
                )
              ))}
            </div>
          )}
        </div>
      )}

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
