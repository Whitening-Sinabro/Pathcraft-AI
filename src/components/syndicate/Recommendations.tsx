import type { Recommendation } from "../../utils/syndicateEngine";
import { actionColor } from "./types";

interface Props {
  recs: Recommendation[];
  delta: { matched: number; total: number };
  /** S3b — 추천 hover 시 targetMemberId를 외부에 알림 (TargetPreview/CurrentBoard 하이라이트용) */
  onHoverMember?: (memberId: string | null) => void;
}

export function Recommendations({ recs, delta, onHoverMember }: Props) {
  if (recs.length === 0) {
    if (delta.total > 0 && delta.matched === delta.total) {
      return (
        <div
          style={{
            marginTop: 10, padding: 10, borderRadius: 6,
            background: "var(--status-success-bg)", color: "var(--status-success)", fontSize: 12,
          }}
        >
          목표 레이아웃 도달. 이제 farm 단계.
        </div>
      );
    }
    return null;
  }

  return (
    <div
      style={{
        marginTop: 10, padding: 10, borderRadius: 6,
        background: "var(--status-warning-bg)", border: "2px solid var(--status-warning)",
      }}
    >
      <div style={{ fontWeight: 700, fontSize: 13, color: "var(--status-warning)", marginBottom: 6 }}>
        다음 액션 추천 (우선순위 순)
      </div>
      <ol style={{ margin: 0, paddingLeft: 20, fontSize: 12, color: "var(--text-primary)", lineHeight: 1.6 }}>
        {recs.slice(0, 8).map((r, i) => (
          <li
            key={`${r.action}-${r.targetMemberId}-${i}`}
            style={{ marginBottom: 4, padding: "2px 4px", borderRadius: 3, transition: "background var(--anim-fast) var(--anim-easing)" }}
            onMouseEnter={() => onHoverMember?.(r.targetMemberId)}
            onMouseLeave={() => onHoverMember?.(null)}
          >
            <span style={{ fontWeight: 700, color: actionColor(r.action) }}>{r.action}</span>
            {" "}<strong>{r.targetMemberName}</strong>
            {r.toDivision && <span style={{ color: "var(--text-secondary)" }}> → {r.toDivision}</span>}
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginLeft: 4 }}>{r.reason}</div>
          </li>
        ))}
      </ol>
      {delta.matched === delta.total && delta.total > 0 && (
        <div
          style={{
            marginTop: 6, padding: 6, borderRadius: 4, fontSize: 12,
            background: "var(--status-success-bg)", color: "var(--status-success)",
          }}
        >
          목표 레이아웃 도달. 이제 farm 단계.
        </div>
      )}
    </div>
  );
}
