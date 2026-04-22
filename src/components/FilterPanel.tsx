import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { FilterResult } from "../types";
import { useActiveGame } from "../contexts/ActiveGameContext";

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
  const { game } = useActiveGame();
  const [strictness, setStrictness] = useState(3);
  const [mode, setMode] = useState<"ssf" | "hcssf" | "trade">("ssf");
  const [filterResult, setFilterResult] = useState<FilterResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);

  async function generateFilter() {
    setError("");
    setLoading(true);
    try {
      const allBuilds = [buildJson, ...extraBuildJsons];
      const raw = await invoke<string>("generate_filter_multi", {
        buildJsons: allBuilds,
        coachingJson,
        strictness,
        stage: stageMode,
        mode,
        alSplit,
        game,
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
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 2000);
  }

  return (
    <section className="ui-card">
      <h3 className="ui-section-title" style={{ color: "var(--accent-hover)" }}>아이템 필터 생성</h3>

      {/* 소개 */}
      <p className="ui-text-muted" style={{ fontSize: 12, marginTop: 0, marginBottom: 12, lineHeight: 1.5 }}>
        이 빌드가 필요한 유니크·디비카·chanceable 베이스를 게임 안에서 강조 표시하는
        <strong style={{ color: "var(--accent-hover)" }}> POE 아이템 필터(<code>.filter</code>)</strong>를 만듭니다.
        <br />
        <span style={{ color: "var(--accent-hover)" }}>Wreckers 스타일 단일 파일</span> — <code>AreaLevel</code>/<code>ItemLevel</code>/<code>DropLevel</code> 조건으로 레벨링→엔드게임 자동 전환. 필터 하나로 전 구간 커버.
        <br />
        생성 후 <code>.filter</code> 다운로드 → POE 설정 폴더(<code>Documents/My Games/Path of Exile/</code>)에 넣고 게임 내 UI Options에서 선택하세요.
      </p>

      {/* 엄격도 선택 */}
      <div style={{ display: "flex", gap: 4, marginBottom: 4, flexWrap: "wrap", fontSize: 12 }}>
        <span className="ui-text-muted" style={{ alignSelf: "center" }}>엄격도:</span>
        {STRICTNESS_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setStrictness(opt.value)}
            className={strictness === opt.value ? "ui-button ui-button--primary" : "ui-button ui-button--secondary"}
            style={{ fontSize: 12 }}
            title={opt.desc}
          >
            {opt.label}
          </button>
        ))}
      </div>
      <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 12 }}>
        낮을수록 많이 표시, 높을수록 핵심만 표시 — 입문자는 Regular, 고레벨 파밍은 Strict 권장
      </div>

      {/* 모드 선택 */}
      <div style={{ display: "flex", gap: 4, marginBottom: 4, flexWrap: "wrap", fontSize: 12 }}>
        <span className="ui-text-muted" style={{ alignSelf: "center" }}>모드:</span>
        {(["ssf", "hcssf", "trade"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={mode === m ? "ui-button ui-button--primary" : "ui-button ui-button--secondary"}
            style={{ fontSize: 11, padding: "4px 10px" }}
            title={
              m === "ssf" ? "솔로 셀프파운드 — 거래 불가, 자력으로 모든 아이템 수급"
              : m === "hcssf" ? "하드코어 SSF — 사망 시 스탠다드로 전환, 생존 우선"
              : "거래 리그 — 거래 가능, 가성비 base 우선 표시"
            }
          >
            {m.toUpperCase()}
          </button>
        ))}
        {extraBuildJsons.length > 0 && (
          <span className="ui-text-warning" style={{ alignSelf: "center", marginLeft: 8, fontWeight: 600 }}>
            Multi-POB: 주 1 + 보조 {extraBuildJsons.length} {stageMode ? "(Stage)" : "(Union)"}
          </span>
        )}
      </div>
      <div className="ui-text-muted" style={{ fontSize: 11, marginBottom: 12 }}>
        SSF=솔로 셀프파운드 · HCSSF=하드코어 SSF · TRADE=거래 리그. 리그 규칙에 맞춰 필터 기준이 달라집니다.
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button
          onClick={generateFilter}
          disabled={loading}
          className="ui-button ui-button--primary"
          style={{ padding: "8px 16px", fontWeight: 600, cursor: loading ? "wait" : "pointer" }}
        >
          {loading ? "생성 중..." : "필터 생성"}
        </button>
        <span className="ui-text-muted" style={{ fontSize: 12, alignSelf: "center" }}>
          {STRICTNESS_OPTIONS[strictness]?.desc}
        </span>
      </div>

      {error && (
        <div className="ui-alert ui-alert--danger" style={{ marginBottom: 8, padding: 8, fontSize: 13 }}>{error}</div>
      )}

      {filterResult && (
        <div>
          {/* 통계 */}
          <div style={{ display: "flex", gap: 12, marginBottom: 12, flexWrap: "wrap" }}>
            <StatBadge label="유니크" count={filterResult.stats.unique_count} accent="warning" />
            <StatBadge label="디비카" count={filterResult.stats.divcard_count} accent="accent" />
            <StatBadge label="Chanceable" count={filterResult.stats.chanceable_count} accent="warning" />
          </div>

          {/* 타겟 디비니 카드 */}
          {filterResult.target_divcards.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <strong style={{ fontSize: 12, color: "var(--accent-hover)" }}>타겟 디비니 카드</strong>
              <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
                {filterResult.target_divcards.map((c, i) => (
                  <span key={i} className="ui-badge ui-badge--accent" style={{ fontSize: 11, padding: "2px 8px" }}>
                    {c.card} ({c.stack}장) → {c.target_unique}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Chanceable 베이스 */}
          {filterResult.chanceable_bases.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <strong className="ui-text-warning" style={{ fontSize: 12 }}>Chanceable 베이스</strong>
              <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
                {filterResult.chanceable_bases.map((c, i) => (
                  <span
                    key={i}
                    style={{
                      padding: "2px 8px", borderRadius: 10, fontSize: 11,
                      background: "var(--status-warning-bg)", color: "var(--status-warning)",
                      border: "1px solid var(--status-warning)",
                    }}
                  >
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
              className={copied ? "ui-button ui-button--secondary" : "ui-button ui-button--secondary"}
              style={{ padding: "6px 14px", fontSize: 12, color: copied ? "var(--status-success)" : undefined }}
            >
              {copied ? "복사됨" : "클립보드 복사"}
            </button>
            <button
              onClick={downloadFilter}
              className="ui-button ui-button--secondary"
              style={{ padding: "6px 14px", fontSize: 12, color: downloaded ? "var(--status-success)" : undefined }}
            >
              {downloaded ? "다운로드됨" : ".filter 다운로드"}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

function StatBadge({ label, count, accent }: { label: string; count: number; accent: "accent" | "warning" | "info" | "success" }) {
  const cls = `ui-badge ui-badge--${accent}`;
  return (
    <div className={cls} style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px" }}>
      <span>{count}</span>
      <span style={{ fontWeight: 400 }}>{label}</span>
    </div>
  );
}
