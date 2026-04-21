import type { CoachResult } from "../../types";

interface Props {
  items: CoachResult["key_items"];
}

function difficultyClass(d: string): string {
  if (d === "어려움") return "ui-text-danger";
  if (d === "보통") return "ui-text-warning";
  return "ui-text-success";
}

export function KeyItemsSection({ items }: Props) {
  if (!items?.length) return null;

  return (
    <section className="ui-card">
      <h3 className="ui-section-title">핵심 장비 (SSF 획득)</h3>
      <table className="ui-table">
        <thead>
          <tr>
            <th>아이템</th><th>중요도</th>
            <th>SSF 난이도</th><th>획득 방법</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i}>
              <td>
                <strong>{item.name}</strong><br />
                <span className="ui-text-muted" style={{ fontSize: 12 }}>{item.slot}</span>
              </td>
              <td>{item.importance}</td>
              <td className={difficultyClass(item.ssf_difficulty)}>{item.ssf_difficulty}</td>
              <td style={{ fontSize: 12 }}>
                {item.acquisition}
                {item.alternatives?.length > 0 && (
                  <div className="ui-text-muted" style={{ marginTop: 2 }}>대체: {item.alternatives.join(", ")}</div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
