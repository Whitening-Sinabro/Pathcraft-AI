import { useEffect, useMemo, useState } from "react";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import { logger } from "../utils/logger";
import { onSnapshot, requestSnapshot, type OverlaySnapshot } from "./channel";
import { restore, subscribe } from "./windowState";
import { closeOverlay } from "./toggle";
import { useToggleShortcut } from "./useToggleShortcut";
import { ValidationWarningsBanner } from "../components/ValidationWarningsBanner";

type PhaseKey = "act1_4" | "act5_10" | "early_maps" | "endgame";

const PHASES: { key: PhaseKey; label: string; range: [number, number] }[] = [
  { key: "act1_4",    label: "Act 1-4",  range: [1, 40] },
  { key: "act5_10",   label: "Act 5-10", range: [41, 70] },
  { key: "early_maps", label: "초반 맵",  range: [71, 85] },
  { key: "endgame",   label: "엔드게임", range: [86, 100] },
];

/** "Lv 1-12" / "1-12" / "Lv 12+" / "85+" / "Lv 68" 등 유연 파싱. */
function parseLevelRange(raw: string): [number, number] {
  const m = raw.match(/(\d+)(?:\s*[-~]\s*(\d+)|\s*\+)?/);
  if (!m) return [1, 100];
  const start = parseInt(m[1], 10);
  if (m[2]) return [start, parseInt(m[2], 10)];
  if (raw.includes("+")) return [start, 100];
  return [start, start];
}

function overlaps(a: [number, number], b: [number, number]): boolean {
  return a[0] <= b[1] && a[1] >= b[0];
}

/**
 * 오버레이 창 — 반투명 + always-on-top + 프레임리스.
 * 메인 창에서 coaching 스냅샷을 Tauri 이벤트로 수신하여 표시.
 */
export function OverlayApp() {
  const [snap, setSnap] = useState<OverlaySnapshot | null>(null);

  useEffect(() => {
    const unlistenP = onSnapshot(setSnap);
    requestSnapshot().catch((e) => logger.warn("[overlay] requestSnapshot failed", e));
    return () => {
      unlistenP.then((fn) => fn()).catch(() => { /* noop */ });
    };
  }, []);

  // 창 위치/크기 복원 + resize/move 구독
  useEffect(() => {
    const win = getCurrentWebviewWindow();
    let unsub: (() => void) | null = null;
    restore(win)
      .then(() => subscribe(win))
      .then((fn) => { unsub = fn; })
      .catch((e) => logger.warn("[overlay] window state setup failed", e));
    return () => { if (unsub) unsub(); };
  }, []);

  // 단축키 Ctrl/Cmd+Shift+O = 메인 복귀
  useToggleShortcut(() => { closeOverlay(); });

  function startDrag(e: React.MouseEvent) {
    if (e.button !== 0) return;
    // 닫기 버튼/기타 인터랙티브 자식 클릭은 드래그로 가로채지 않음
    const target = e.target as HTMLElement;
    if (target.closest("button, a, input, [data-no-drag]")) return;
    getCurrentWebviewWindow().startDragging().catch((err) => {
      logger.error("[overlay] startDragging failed", err);
    });
  }

  return (
    <div className="overlay-root">
      <header className="overlay-drag" onMouseDown={startDrag}>
        <span className="overlay-drag__title">
          {snap?.buildName || "PathcraftAI"}
          {snap?.tier && <span className="overlay-drag__tier">{snap.tier}</span>}
        </span>
        <button
          type="button"
          className="overlay-drag__close"
          onClick={closeOverlay}
          aria-label="메인 창으로 복귀"
          title="메인 창으로 (Ctrl/Cmd+Shift+O)"
        >
          ×
        </button>
      </header>

      <section className="overlay-body">
        {!snap ? (
          <p className="ui-text-muted" style={{ fontSize: 12, textAlign: "center", marginTop: 40 }}>
            분석 결과 대기 중…<br />메인에서 빌드를 먼저 분석하세요.
          </p>
        ) : (
          <OverlayContent snap={snap} />
        )}
      </section>
    </div>
  );
}

function OverlayContent({ snap }: { snap: OverlaySnapshot }) {
  const [activePhase, setActivePhase] = useState<PhaseKey>("act1_4");

  const activePhaseMeta = PHASES.find((p) => p.key === activePhase) ?? PHASES[0];
  const phaseParagraph = snap.levelingGuide[activePhase];

  const phaseLinks = useMemo(() => {
    const progs = snap.levelingSkills?.links_progression ?? [];
    return progs.filter((p) => overlaps(parseLevelRange(p.level_range), activePhaseMeta.range));
  }, [snap.levelingSkills, activePhaseMeta]);

  const phaseTransitions = useMemo(() => {
    return snap.skillTransitions.filter((t) => {
      const lv = t.level;
      return lv >= activePhaseMeta.range[0] && lv <= activePhaseMeta.range[1];
    });
  }, [snap.skillTransitions, activePhaseMeta]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <ValidationWarningsBanner
        warnings={snap.validationWarnings}
        trace={snap.normalizationTrace}
        compact
      />

      {/* 탭 네비 */}
      <div className="overlay-phase-tabs">
        {PHASES.map((p) => (
          <button
            key={p.key}
            type="button"
            className={"overlay-phase-tab" + (p.key === activePhase ? " is-active" : "")}
            onClick={() => setActivePhase(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* 활성 phase 카드 */}
      <OverlaySection title={activePhaseMeta.label}>
        {phaseParagraph && (
          <p className="ui-text-secondary" style={{ fontSize: 12, margin: "0 0 6px", lineHeight: 1.4 }}>
            {phaseParagraph}
          </p>
        )}

        {snap.levelingSkills?.recommended_name && (
          <div style={{ fontSize: 11, marginBottom: 4 }} className="ui-text-muted">
            주 스킬: <strong className="ui-text-success">{snap.levelingSkills.recommended_name}</strong>
            {snap.levelingSkills.damage_type && (
              <span style={{ marginLeft: 6 }}>· {snap.levelingSkills.damage_type}</span>
            )}
          </div>
        )}

        {phaseLinks.length > 0 && (
          <>
            <div className="ui-text-muted" style={{ fontSize: 11, marginTop: 6, marginBottom: 2 }}>젬 링크</div>
            {phaseLinks.map((p, i) => (
              <div key={i} style={{ fontSize: 12, marginBottom: 2 }}>
                <strong style={{ color: "var(--status-info)" }}>{p.level_range}</strong>
                <span style={{ marginLeft: 6 }}>{p.gems.join(" - ")}</span>
              </div>
            ))}
          </>
        )}

        {phaseTransitions.length > 0 && (
          <>
            <div className="ui-text-muted" style={{ fontSize: 11, marginTop: 6, marginBottom: 2 }}>스킬 전환</div>
            {phaseTransitions.map((t, i) => (
              <div key={i} style={{ fontSize: 12, marginBottom: 2 }}>
                <strong style={{ color: "var(--status-info)" }}>Lv.{t.level}</strong>
                <span style={{ marginLeft: 6 }}>{t.change}</span>
              </div>
            ))}
          </>
        )}

        {!phaseParagraph && phaseLinks.length === 0 && phaseTransitions.length === 0 && (
          <p className="ui-text-muted" style={{ fontSize: 11, margin: 0 }}>이 구간 데이터가 없습니다.</p>
        )}
      </OverlaySection>

      {snap.mapDeadly.length > 0 && (
        <OverlaySection title="맵 금지 모드" titleClass="ui-text-danger">
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12 }}>
            {snap.mapDeadly.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </OverlaySection>
      )}

      {snap.dangerZones.length > 0 && (
        <OverlaySection title="위험 요소" titleClass="ui-text-warning">
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12 }}>
            {snap.dangerZones.map((d, i) => <li key={i}>{d}</li>)}
          </ul>
        </OverlaySection>
      )}
    </div>
  );
}

function OverlaySection({
  title,
  titleClass,
  children,
}: {
  title: string;
  titleClass?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="overlay-section">
      <h4 className={`overlay-section__title${titleClass ? " " + titleClass : ""}`}>{title}</h4>
      {children}
    </div>
  );
}
