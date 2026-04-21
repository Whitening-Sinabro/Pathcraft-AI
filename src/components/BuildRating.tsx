import type { BuildRating as BuildRatingType } from "../types";

const CATEGORIES: readonly [keyof BuildRatingType, string][] = [
  ["hcssf_viability", "HCSSF"],
  ["league_start_viable", "리그 스타터"],
  ["newbie_friendly", "뉴비 친화"],
  ["gearing_difficulty", "기어링"],
  ["play_difficulty", "조작 난이도"],
];

function dotColor(val: number, position: number): string {
  if (position > val) return "var(--border-default)";
  if (val >= 4) return "var(--status-success)";
  if (val >= 3) return "var(--status-warning)";
  return "var(--status-danger)";
}

export function BuildRatingSection({ rating }: { rating: BuildRatingType }) {
  if (!rating || Object.keys(rating).length === 0) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">빌드 평가</h3>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, textAlign: "center" }}>
        {CATEGORIES.map(([key, label]) => {
          const val = rating[key] || 0;
          return (
            <div key={key}>
              <div className="ui-text-muted" style={{ fontSize: 12, marginBottom: 4 }}>{label}</div>
              <div style={{ display: "flex", justifyContent: "center", gap: 2 }}>
                {[1, 2, 3, 4, 5].map(n => (
                  <span key={n} style={{
                    width: 10, height: 10, borderRadius: 2,
                    background: dotColor(val, n),
                  }} />
                ))}
              </div>
              <div className="ui-text-secondary" style={{ fontSize: 11, marginTop: 2 }}>{val}/5</div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
