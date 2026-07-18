import { useEffect, useMemo, useState } from "react";
import { PassiveTreeCanvas } from "./PassiveTreeCanvas";
import { decodeTreeUrl } from "../utils/passiveTreeUrl";
import { useActiveGame } from "../contexts/ActiveGameContext";
import { ASCENDANCIES, CLASS_NAMES } from "../utils/passiveTreeConstants";
import type { RepresentativeProfileSummary } from "../types";

interface Props {
  // PoB 빌드에서 추출된 passive_tree_url. 있으면 자동 디코드 → 할당 노드 하이라이트.
  // POE1 URL 인코딩 전용 — POE2 는 decoded 무시.
  url?: string;
  representativeProfile?: RepresentativeProfileSummary | null;
  buildClassName?: string | null;
  buildAscendancyName?: string | null;
}

function normalizePassiveName(value?: string | null) {
  return (value || "").trim().toLowerCase().replace(/\s+/g, " ");
}

export function resolvePoe1ClassIndex(className?: string | null): number | undefined {
  const normalized = normalizePassiveName(className);
  if (!normalized) return undefined;
  const index = CLASS_NAMES.findIndex((name) => normalizePassiveName(name) === normalized);
  return index >= 0 ? index : undefined;
}

export function resolvePoe1AscendancyIndex(classIndex: number | undefined, ascendancy?: string | null): number | undefined {
  if (classIndex == null) return undefined;
  const normalized = normalizePassiveName(ascendancy);
  if (!normalized) return undefined;
  const options = ASCENDANCIES[classIndex] ?? [];
  const index = options.findIndex((name) => normalizePassiveName(name) === normalized);
  return index >= 0 ? index + 1 : undefined;
}

export function PassiveTreeView({
  url,
  representativeProfile,
  buildClassName,
  buildAscendancyName,
}: Props) {
  const { game } = useActiveGame();
  const [expanded, setExpanded] = useState(false);
  const [selectedPlanUrl, setSelectedPlanUrl] = useState("");
  const w = expanded ? 1400 : 900;
  const h = expanded ? 900 : 600;
  const passivePlan = representativeProfile?.progression?.passive_plan?.slice(0, 5) ?? [];
  const activeUrl = selectedPlanUrl || url || "";

  // POE2 는 POE1-form PoB URL 디코드를 적용하지 않음.
  const decoded = useMemo(
    () => (activeUrl && game === "poe1" ? decodeTreeUrl(activeUrl) : null),
    [activeUrl, game],
  );
  const initialAllocated = useMemo(
    () => (decoded ? new Set(decoded.nodes) : undefined),
    [decoded],
  );
  const fallbackClassName = representativeProfile?.identity?.class_name || buildClassName;
  const fallbackAscendancyName = representativeProfile?.identity?.ascendancy || buildAscendancyName;
  const fallbackClass = game === "poe1" ? resolvePoe1ClassIndex(fallbackClassName) : undefined;
  const fallbackAsc = game === "poe1" ? resolvePoe1AscendancyIndex(fallbackClass, fallbackAscendancyName) : undefined;
  const buildClass = decoded?.classIndex ?? fallbackClass;
  const buildAsc = decoded?.ascendancyIndex ?? fallbackAsc;

  useEffect(() => {
    setSelectedPlanUrl("");
  }, [url, representativeProfile?.build_id]);

  return (
    <section className="app-main__full ui-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <h3 className="ui-section-title" style={{ margin: 0 }}>패시브 트리</h3>
        <div style={{ display: "flex", gap: 6 }}>
          <button
            onClick={() => setExpanded((v) => !v)}
            className="ui-button ui-button--secondary"
            style={{ padding: "4px 10px", fontSize: 11 }}
          >
            {expanded ? "축소" : "크게"}
          </button>
          {selectedPlanUrl && (
            <button
              onClick={() => setSelectedPlanUrl("")}
              className="ui-button ui-button--secondary"
              style={{ padding: "4px 10px", fontSize: 11 }}
            >
              현재 PoB
            </button>
          )}
          {activeUrl && (
            <a
              href={activeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="ui-button ui-button--secondary"
              style={{ padding: "4px 10px", fontSize: 11, textDecoration: "none", color: "var(--accent-hover)" }}
            >
              POE 공식 뷰어
            </a>
          )}
        </div>
      </div>

      {passivePlan.length > 0 && (
        <div className="ui-card--inset" style={{ marginBottom: 10, borderColor: "var(--status-info)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
            <strong>코퍼스 패시브 마일스톤</strong>
            {fallbackClassName && (
              <span className="ui-text-info" style={{ fontSize: 12, fontWeight: 700 }}>
                {fallbackClassName}{fallbackAscendancyName ? ` / ${fallbackAscendancyName}` : ""}
              </span>
            )}
          </div>
          <div style={{ marginTop: 8, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 8 }}>
            {passivePlan.map((step, index) => (
              <div key={`${step.stage}-${step.level_range}-${index}`} style={{ fontSize: 12, lineHeight: 1.45 }}>
                <strong>{step.stage_label || step.stage || "stage"}</strong>
                {step.level_range ? <span className="ui-text-muted"> ({step.level_range})</span> : null}
                {step.priorities && step.priorities.length > 0 && (
                  <div className="ui-text-muted">{step.priorities.slice(0, 4).join(" / ")}</div>
                )}
                {step.tree_url && (
                  <button
                    onClick={() => setSelectedPlanUrl(step.tree_url || "")}
                    className="ui-button ui-button--secondary"
                    style={{ marginTop: 5, padding: "3px 8px", fontSize: 11 }}
                  >
                    이 단계 보기
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <PassiveTreeCanvas
        key={`${game}:${activeUrl || "empty"}:${buildClass ?? "class"}:${buildAsc ?? "asc"}`}
        game={game}
        width={w}
        height={h}
        initialAllocated={initialAllocated}
        buildClass={buildClass}
        buildAscendancy={buildAsc}
      />
      {decoded && (
        <div className="ui-text-success" style={{ marginTop: 6, fontSize: 11 }}>
          빌드 로드: class {decoded.classIndex} / asc {decoded.ascendancyIndex} /
          노드 {decoded.nodes.length}개 하이라이트됨
        </div>
      )}
      {!decoded && game === "poe1" && buildClass != null && (
        <div className="ui-text-info" style={{ marginTop: 6, fontSize: 11 }}>
          트리 URL은 없지만 class/ascendancy 기준 시작점으로 열었습니다:
          {" "}{CLASS_NAMES[buildClass]}{fallbackAscendancyName ? ` / ${fallbackAscendancyName}` : ""}
        </div>
      )}

      <div className="ui-text-muted" style={{ marginTop: 6, fontSize: 11 }}>
        클래스 선택 → 클릭으로 노드 할당. 빌드 로드 시 해당 빌드의 노드가 자동 표시됨.
      </div>
    </section>
  );
}
