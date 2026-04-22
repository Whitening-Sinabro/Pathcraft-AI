import type { CoachResult } from "../../types";
import { colors } from "../../theme";

interface Props {
  tier: CoachResult["tier"];
  buildSummary: CoachResult["build_summary"];
  strengths: CoachResult["strengths"];
  weaknesses: CoachResult["weaknesses"];
}

function tierColor(tier: string | undefined | null): string {
  const key = (tier ?? "d").toLowerCase() as keyof typeof colors.tier;
  return colors.tier[key] ?? colors.tier.d;
}

export function BuildSummarySection({ tier, buildSummary, strengths, weaknesses }: Props) {
  const safeStrengths = Array.isArray(strengths) ? strengths : [];
  const safeWeaknesses = Array.isArray(weaknesses) ? weaknesses : [];
  return (
    <section className="ui-card">
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
        <span style={{
          display: "inline-block", width: 36, height: 36, borderRadius: "50%",
          background: tierColor(tier), color: "#fff",
          textAlign: "center", lineHeight: "36px", fontWeight: 700, fontSize: 18,
        }}>{tier ?? "-"}</span>
        <span style={{ fontSize: 16, fontWeight: 600 }}>{buildSummary ?? ""}</span>
      </div>
      <div style={{ display: "flex", gap: 16 }}>
        <div style={{ flex: 1 }}>
          <strong className="ui-text-success">강점</strong>
          <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
            {safeStrengths.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
        <div style={{ flex: 1 }}>
          <strong className="ui-text-danger">약점</strong>
          <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
            {safeWeaknesses.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}
