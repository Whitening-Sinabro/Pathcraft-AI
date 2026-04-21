import { DIVISIONS, DIVISION_COLORS, type SyndicateMember } from "./types";

interface Props {
  member: SyndicateMember;
  onClose: () => void;
}

export function MemberDetail({ member, onClose }: Props) {
  return (
    <div
      style={{
        padding: 10, background: "var(--bg-elevated)", borderRadius: 6,
        border: "1px solid var(--border-default)",
        fontSize: 12, color: "var(--text-secondary)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
        <strong style={{ fontSize: 13 }}>
          {member.name}
          <span style={{ marginLeft: 6, color: "var(--text-muted)", fontSize: 11 }}>
            기본 분과: {member.default_division || "—"}
          </span>
        </strong>
        <button
          onClick={onClose}
          style={{
            padding: "2px 8px", fontSize: 11, background: "transparent",
            border: "1px solid var(--border-default)", borderRadius: 3,
            cursor: "pointer", color: "var(--text-muted)",
          }}
        >
          닫기
        </button>
      </div>
      <div style={{ fontSize: 11, marginBottom: 4 }}>
        태그: {member.tags.map((t) => (
          <span
            key={t}
            style={{
              display: "inline-block", padding: "1px 6px", margin: "0 3px 0 0",
              background: "var(--bg-elevated)", borderRadius: 10, fontSize: 10,
            }}
          >
            {t}
          </span>
        ))}
      </div>
      {DIVISIONS.map((div) => (
        <div key={div} style={{ fontSize: 11, marginTop: 2 }}>
          <strong style={{ color: DIVISION_COLORS[div].text }}>{div}:</strong>{" "}
          {member.rewards[div] || "—"}
        </div>
      ))}
    </div>
  );
}
