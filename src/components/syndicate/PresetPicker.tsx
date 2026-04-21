import type { SyndicateLayout } from "./types";

interface Props {
  layouts: SyndicateLayout[];
  selectedLayoutId: string;
  onApply: (id: string) => void;
  onClear: () => void;
}

export function PresetPicker({ layouts, selectedLayoutId, onApply, onClear }: Props) {
  const active = layouts.filter((l) => !l.deprecated);
  const deprecated = layouts.filter((l) => l.deprecated);
  const selectedLayout = layouts.find((l) => l.id === selectedLayoutId);

  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>프리셋 레이아웃</div>
      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
        {active.map((l) => (
          <LayoutButton
            key={l.id}
            layout={l}
            active={selectedLayoutId === l.id}
            onClick={() => onApply(l.id)}
          />
        ))}
        <button
          onClick={onClear}
          style={{
            padding: "4px 10px", borderRadius: 4, fontSize: 11,
            border: "1px dashed var(--border-strong)", background: "var(--bg-panel)",
            cursor: "pointer", color: "var(--text-muted)",
          }}
        >
          모두 비우기
        </button>
      </div>

      {deprecated.length > 0 && (
        <details style={{ marginTop: 6 }}>
          <summary style={{ fontSize: 11, color: "var(--text-muted)", cursor: "pointer" }}>
            Legacy ({deprecated.length})
          </summary>
          <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
            {deprecated.map((l) => (
              <LayoutButton
                key={l.id}
                layout={l}
                active={selectedLayoutId === l.id}
                onClick={() => onApply(l.id)}
                isLegacy
              />
            ))}
          </div>
        </details>
      )}

      {selectedLayoutId === "custom" && (
        <div style={{ marginTop: 6, fontSize: 12, color: "var(--status-success)" }}>
          <strong>커스텀 목표:</strong> Vision/수동으로 저장된 레이아웃. 프리셋 클릭 시 덮어씀.
        </div>
      )}
      {selectedLayout && selectedLayoutId !== "custom" && (
        <div style={{ marginTop: 6, fontSize: 12, color: "var(--text-secondary)" }}>
          <strong>전략:</strong> {selectedLayout.strategy}
          {selectedLayout.deprecated && (
            <span className="ui-text-warning" style={{ marginLeft: 6, fontSize: 11 }}>
              (Deprecated{selectedLayout.deprecated_since ? ` · ${selectedLayout.deprecated_since}` : ""})
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function LayoutButton({
  layout, active, onClick, isLegacy = false,
}: {
  layout: SyndicateLayout;
  active: boolean;
  onClick: () => void;
  isLegacy?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "4px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600,
        border: active ? "2px solid var(--status-warning)" : "1px solid var(--border-default)",
        background: active ? "var(--status-warning-bg)" : "var(--bg-panel)",
        cursor: "pointer", color: "var(--text-secondary)",
        opacity: isLegacy ? 0.65 : 1,
      }}
      title={layout.strategy}
    >
      {layout.hcssf_safe && <span style={{ marginRight: 4 }}>🛡</span>}
      {layout.name}
    </button>
  );
}
