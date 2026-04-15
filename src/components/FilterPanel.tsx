import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { FilterResult } from "../types";

const STRICTNESS_OPTIONS = [
  { value: 0, label: "Soft", desc: "전부 표시" },
  { value: 1, label: "Regular", desc: "노말 장비 숨김" },
  { value: 2, label: "Semi-Strict", desc: "+ 매직 장비 숨김" },
  { value: 3, label: "Strict", desc: "+ 저가 커런시, 레어 제한" },
  { value: 4, label: "Very Strict", desc: "+ 대부분 레어 숨김" },
];

interface FilterPanelProps {
  buildJson: string;
  coachingJson: string;
  extraBuildJsons?: string[];
  stageMode?: boolean;
  alSplit?: number;
}

export function FilterPanel({
  buildJson, coachingJson,
  extraBuildJsons = [], stageMode = false, alSplit = 67,
}: FilterPanelProps) {
  const [strictness, setStrictness] = useState(3);
  const [mode, setMode] = useState<"ssf" | "hcssf" | "trade">("ssf");
  const [filterResult, setFilterResult] = useState<FilterResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function generateFilter() {
    setError("");
    setLoading(true);
    try {
      // Multi-POB 경로: 보조 POB 있으면 generate_filter_multi
      const allBuilds = [buildJson, ...extraBuildJsons];
      const raw = await invoke<string>("generate_filter_multi", {
        buildJsons: allBuilds,
        coachingJson,
        strictness,
        stage: stageMode,
        mode,
        alSplit,
      });
      setFilterResult(JSON.parse(raw));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function copyOverlay() {
    if (!filterResult) return;
    await navigator.clipboard.writeText(filterResult.overlay);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function downloadFilter() {
    if (!filterResult) return;
    const blob = new Blob([filterResult.overlay], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "PathcraftAI_overlay.filter";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
      <h3 style={{ margin: "0 0 12px", fontSize: 15, color: "#7048e8" }}>아이템 필터 생성</h3>

      {/* 엄격도 선택 */}
      <div style={{ display: "flex", gap: 4, marginBottom: 12, flexWrap: "wrap" }}>
        {STRICTNESS_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setStrictness(opt.value)}
            style={{
              padding: "6px 12px", borderRadius: 6, fontSize: 12, fontWeight: 600,
              border: strictness === opt.value ? "2px solid #7048e8" : "1px solid #dee2e6",
              background: strictness === opt.value ? "#f3f0ff" : "#fff",
              color: strictness === opt.value ? "#7048e8" : "#495057",
              cursor: "pointer",
            }}
            title={opt.desc}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* 모드 선택 */}
      <div style={{ display: "flex", gap: 4, marginBottom: 12, flexWrap: "wrap", fontSize: 12 }}>
        <span style={{ alignSelf: "center", color: "#868e96" }}>모드:</span>
        {(["ssf", "hcssf", "trade"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            style={{
              padding: "4px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600,
              border: mode === m ? "2px solid #2b8a3e" : "1px solid #dee2e6",
              background: mode === m ? "#d3f9d8" : "#fff",
              color: mode === m ? "#2b8a3e" : "#495057",
              cursor: "pointer",
            }}
          >
            {m.toUpperCase()}
          </button>
        ))}
        {extraBuildJsons.length > 0 && (
          <span style={{ alignSelf: "center", marginLeft: 8, color: "#f76707", fontWeight: 600 }}>
            Multi-POB: 주 1 + 보조 {extraBuildJsons.length} {stageMode ? "(Stage)" : "(Union)"}
          </span>
        )}
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button
          onClick={generateFilter}
          disabled={loading}
          style={{
            padding: "8px 16px", borderRadius: 6, border: "none",
            background: loading ? "#868e96" : "#7048e8", color: "#fff",
            cursor: loading ? "wait" : "pointer", fontSize: 13, fontWeight: 600,
          }}
        >
          {loading ? "생성 중..." : "필터 생성"}
        </button>
        <span style={{ fontSize: 12, color: "#868e96", alignSelf: "center" }}>
          {STRICTNESS_OPTIONS[strictness]?.desc}
        </span>
      </div>

      {error && (
        <div style={{ color: "#e03131", padding: 8, background: "#fff5f5", borderRadius: 6, marginBottom: 8, fontSize: 13 }}>
          {error}
        </div>
      )}

      {filterResult && (
        <div>
          {/* 통계 */}
          <div style={{ display: "flex", gap: 12, marginBottom: 12, flexWrap: "wrap" }}>
            <StatBadge label="유니크" count={filterResult.stats.unique_count} color="#e8590c" />
            <StatBadge label="디비카" count={filterResult.stats.divcard_count} color="#7048e8" />
            <StatBadge label="Chanceable" count={filterResult.stats.chanceable_count} color="#d9480f" />
          </div>

          {/* 타겟 디비니 카드 */}
          {filterResult.target_divcards.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <strong style={{ fontSize: 12, color: "#7048e8" }}>타겟 디비니 카드</strong>
              <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
                {filterResult.target_divcards.map((c, i) => (
                  <span key={i} style={{
                    padding: "2px 8px", borderRadius: 10, fontSize: 11,
                    background: "#f3f0ff", color: "#7048e8", border: "1px solid #d0bfff",
                  }}>
                    {c.card} ({c.stack}장) → {c.target_unique}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Chanceable 베이스 */}
          {filterResult.chanceable_bases.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <strong style={{ fontSize: 12, color: "#d9480f" }}>Chanceable 베이스</strong>
              <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
                {filterResult.chanceable_bases.map((c, i) => (
                  <span key={i} style={{
                    padding: "2px 8px", borderRadius: 10, fontSize: 11,
                    background: "#fff4e6", color: "#d9480f", border: "1px solid #ffd8a8",
                  }}>
                    {c.base} → {c.unique}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 액션 버튼 */}
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button
              onClick={copyOverlay}
              style={{
                padding: "6px 14px", borderRadius: 6, border: "1px solid #dee2e6",
                background: copied ? "#d3f9d8" : "#f8f9fa", fontSize: 12,
                cursor: "pointer", color: copied ? "#2b8a3e" : "#495057",
              }}
            >
              {copied ? "복사됨" : "클립보드 복사"}
            </button>
            <button
              onClick={downloadFilter}
              style={{
                padding: "6px 14px", borderRadius: 6, border: "1px solid #dee2e6",
                background: "#f8f9fa", fontSize: 12, cursor: "pointer", color: "#495057",
              }}
            >
              .filter 다운로드
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

function StatBadge({ label, count, color }: { label: string; count: number; color: string }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 4,
      padding: "4px 10px", borderRadius: 12, background: `${color}15`,
      fontSize: 12, fontWeight: 600, color,
    }}>
      <span>{count}</span>
      <span style={{ fontWeight: 400 }}>{label}</span>
    </div>
  );
}
