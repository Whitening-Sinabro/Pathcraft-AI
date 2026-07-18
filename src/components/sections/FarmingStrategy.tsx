import type { CoachResult, RepresentativeProfileSummary } from "../../types";

interface Props {
  strategy: CoachResult["farming_strategy"];
  representativeProfile?: RepresentativeProfileSummary | null;
}

const DEFAULT_PHASE_BOUNDARIES = {
  early_mapping: "아틀라스 진행도, 반복 가능한 최고 티어, 사망 빈도, 클리어 시간 중 하나라도 약하거나 모르면 얼리/전환 맵핑으로 보수적으로 봅니다.",
  mid_mapping: "레드/T16을 낮은 사망률로 반복 가능하고, 한 가지 메카닉에 아틀라스 포인트를 투자할 여유가 있으면 미드 맵핑으로 봅니다.",
  late_mapping: "4 voidstone 또는 동급 진행도, 고티어 안정성, scarab/리그 메카닉 투자 비용 회수 가능성이 확인되면 후반 파밍으로 봅니다.",
  promotion_checks: ["아틀라스 진행도", "반복 가능한 최고 티어", "사망 빈도", "평균 클리어 시간", "보이드스톤/투자 회수"],
};

function formatAvailability(value: boolean | string | undefined) {
  if (typeof value === "boolean") return value ? "가능" : "불가";
  if (value === "high") return "높음";
  if (value === "medium") return "보통";
  if (value === "low") return "낮음";
  return value || "미기록";
}

function formatLabel(value: string) {
  const labels: Record<string, string> = {
    mapping: "맵핑",
    bossing: "보스",
    sanctum: "성역",
    heist: "강탈",
    expedition: "탐험",
    confirmed: "확인됨",
    near_confirmed: "준확인",
    hold: "보류",
    inferred: "추정",
    early_mapping: "초반 맵핑",
    mid_mapping: "중반 맵핑",
    late_mapping: "후반 파밍",
  };
  return labels[value] || value.replace(/_/g, " ");
}

export function FarmingStrategySection({ strategy, representativeProfile }: Props) {
  if (!strategy) return null;

  const suitability = representativeProfile?.suitability ?? {};
  const suitabilityRows = Object.entries(suitability)
    .filter(([, value]) => typeof value === "number")
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);
  const availability = representativeProfile?.availability;
  const painPoints = representativeProfile?.constraints?.pain_points?.slice(0, 3) ?? [];

  if (typeof strategy === "string") {
    return (
      <section className="ui-card">
        <h3 className="ui-section-title ui-text-success">파밍 전략</h3>
        {representativeProfile && (
          <div className="ui-card--inset" style={{ marginBottom: 12, borderColor: "var(--status-info)" }}>
            <strong>근거 분리</strong>
            <div className="ui-text-muted" style={{ marginTop: 6, fontSize: 12, lineHeight: 1.55 }}>
              poe.ninja는 엔드게임 변형 확인용이고, 실제 파밍 단계는 현재 PoB의 안정성/속도/진행도로 판단합니다.
            </div>
          </div>
        )}
        <p style={{ margin: 0, fontSize: 13 }}>{strategy}</p>
      </section>
    );
  }

  return (
    <section className="ui-card">
      <h3 className="ui-section-title ui-text-success">파밍 전략</h3>

      {representativeProfile && (
        <div
          className="ui-card--inset"
          style={{ marginBottom: 12, padding: 10, fontSize: 13, borderColor: "var(--status-info)" }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
            <strong>근거 분리</strong>
            <span className="ui-text-info" style={{ fontSize: 12, fontWeight: 700 }}>
              엔드게임 변형과 레벨링 근거 분리
            </span>
          </div>
          <div className="ui-text-muted" style={{ marginTop: 6, lineHeight: 1.55 }}>
            poe.ninja 스냅샷은 커스터마이징/엔드게임 변형 확인에 쓰고, 레벨링 검증 여부는 stage PoB와 creator route를 우선합니다.
          </div>

          <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span className="ui-badge ui-badge--info">
              리그 스타트 {formatAvailability(availability?.league_start_viable)}
            </span>
            <span className="ui-badge ui-badge--info">
              SSF {formatAvailability(availability?.ssf_viable)}
            </span>
            <span className="ui-badge ui-badge--info">
              HC {formatAvailability(availability?.hc_viable)}
            </span>
            {representativeProfile.progression?.leveling_confidence && (
              <span className="ui-badge ui-badge--success">
                레벨링 {formatLabel(representativeProfile.progression.leveling_confidence)}
              </span>
            )}
          </div>

          {suitabilityRows.length > 0 && (
            <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
              {suitabilityRows.map(([key, value]) => (
                <span key={key} className="ui-badge ui-badge--accent">
                  {formatLabel(key)} {value}
                </span>
              ))}
            </div>
          )}

          {painPoints.length > 0 && (
            <div className="ui-text-muted" style={{ marginTop: 8, fontSize: 12, lineHeight: 1.55 }}>
              주의: {painPoints.join(" / ")}
            </div>
          )}
        </div>
      )}

      {strategy.readiness_assessment && (
        <div
          className="ui-card--inset"
          style={{ marginBottom: 12, padding: 10, fontSize: 13 }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
            <strong>현재 파밍 단계 판정</strong>
            <span className="ui-badge ui-badge--accent">
              {formatLabel(strategy.readiness_assessment.current_phase)}
            </span>
          </div>
          <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span className="ui-badge ui-badge--info">
              아틀라스: {strategy.readiness_assessment.atlas_progress ?? strategy.readiness_assessment.atlas_passives_100 ?? "미기록"}
            </span>
            <span className="ui-badge ui-badge--info">
              최고 티어: {strategy.readiness_assessment.highest_tier_smooth ?? strategy.readiness_assessment.t16_smooth ?? "미기록"}
            </span>
            <span className="ui-badge ui-badge--info">
              속도: {strategy.readiness_assessment.clear_speed_state ?? strategy.readiness_assessment.t16_under_2_min ?? "미기록"}
            </span>
            <span className="ui-badge ui-badge--info">
              사망: {strategy.readiness_assessment.death_rate ?? "미기록"}
            </span>
          </div>
          {strategy.readiness_assessment.reason && (
            <div className="ui-text-muted" style={{ marginTop: 8, lineHeight: 1.55 }}>
              {strategy.readiness_assessment.reason}
            </div>
          )}
          {strategy.readiness_assessment.next_measurement && (
            <div className="ui-text-warning" style={{ marginTop: 6, lineHeight: 1.55 }}>
              다음 확인: {strategy.readiness_assessment.next_measurement}
            </div>
          )}
        </div>
      )}

      <div
        className="ui-card--inset"
        style={{ marginBottom: 12, padding: 10, fontSize: 13 }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
          <strong>얼리 / 미드 맵핑 구분선</strong>
          <span className="ui-text-info" style={{ fontSize: 12, fontWeight: 700 }}>
            진행도 + 안정성 + 속도 + 투자 회수
          </span>
        </div>
        <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
          {(strategy.atlas_phase_boundaries?.promotion_checks ?? DEFAULT_PHASE_BOUNDARIES.promotion_checks).map((check) => (
            <span key={check} className="ui-badge ui-badge--info">
              {check}
            </span>
          ))}
        </div>
        <div className="ui-text-muted" style={{ marginTop: 8, lineHeight: 1.55 }}>
          {strategy.atlas_phase_boundaries?.mid_mapping ?? DEFAULT_PHASE_BOUNDARIES.mid_mapping}
        </div>
      </div>

      {strategy.recommended_mechanics?.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <strong style={{ fontSize: 13 }}>추천 메카닉</strong>
          <div style={{ display: "flex", gap: 6, marginTop: 4, flexWrap: "wrap" }}>
            {strategy.recommended_mechanics.map((m, i) => (
              <span key={i} className={i === 0 ? "ui-badge ui-badge--success" : "ui-badge ui-badge--info"}>
                {m}
              </span>
            ))}
          </div>
        </div>
      )}

      {strategy.atlas_passive_focus && (
        <div
          className="ui-card--inset"
          style={{ marginBottom: 10, padding: 8, fontSize: 13 }}
        >
          <strong>아틀라스 패시브:</strong> {strategy.atlas_passive_focus}
        </div>
      )}

      <table className="ui-table">
        <tbody>
          <tr>
            <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>얼리 기준</td>
            <td>{strategy.atlas_phase_boundaries?.early_mapping ?? DEFAULT_PHASE_BOUNDARIES.early_mapping}</td>
          </tr>
          {strategy.early_atlas && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>초반</td>
              <td>{strategy.early_atlas}</td>
            </tr>
          )}
          {strategy.mid_atlas && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>중반</td>
              <td>{strategy.mid_atlas}</td>
            </tr>
          )}
          <tr>
            <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>후반 기준</td>
            <td>{strategy.atlas_phase_boundaries?.late_mapping ?? DEFAULT_PHASE_BOUNDARIES.late_mapping}</td>
          </tr>
          {strategy.late_atlas && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>후반</td>
              <td>{strategy.late_atlas}</td>
            </tr>
          )}
          {strategy.ssf_crafting_focus && (
            <tr>
              <td className="ui-text-muted" style={{ fontWeight: 600, whiteSpace: "nowrap" }}>크래프팅</td>
              <td>{strategy.ssf_crafting_focus}</td>
            </tr>
          )}
        </tbody>
      </table>

      {strategy.scarab_priority?.length > 0 && (
        <div className="ui-text-muted" style={{ marginTop: 8, fontSize: 12 }}>
          스카랍: {strategy.scarab_priority.join(", ")}
        </div>
      )}
    </section>
  );
}
