import { useEffect, useRef, useState } from "react";
import type { BuildData } from "../../types";
import { useActiveGame, GAME_LABEL, type ActiveGame } from "../../contexts/ActiveGameContext";
import type { SavedBuild } from "../../hooks/useBuildHistory";

interface Props {
  buildData: BuildData | null;
  patchStatus: string;
  onUpdatePatch: () => void;
  history: SavedBuild[];
  onSelectBuild: (id: string) => void;
  onRemoveBuild: (id: string) => void;
}

const GAMES: ActiveGame[] = ["poe1", "poe2"];

function formatRelative(ts: number): string {
  const diff = Date.now() - ts;
  const min = Math.floor(diff / 60000);
  if (min < 1) return "방금";
  if (min < 60) return `${min}분 전`;
  const h = Math.floor(min / 60);
  if (h < 24) return `${h}시간 전`;
  const d = Math.floor(h / 24);
  if (d < 30) return `${d}일 전`;
  const mo = Math.floor(d / 30);
  return `${mo}개월 전`;
}

export function TopBar({
  buildData, patchStatus, onUpdatePatch,
  history, onSelectBuild, onRemoveBuild,
}: Props) {
  const { game, setGame } = useActiveGame();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    function onDocClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  return (
    <header className="app-topbar">
      <div className="app-topbar__brand">
        <h1 className="app-topbar__title">PathcraftAI</h1>
        {buildData?.meta?.build_name && (
          <span className="app-topbar__build">— {buildData.meta.build_name}</span>
        )}
      </div>

      <div className="app-topbar__history" ref={menuRef}>
        <button
          type="button"
          className="app-topbar__history-btn"
          onClick={() => setOpen((v) => !v)}
          title="저장된 빌드 히스토리"
        >
          히스토리 ({history.length})
        </button>
        {open && (
          <div className="app-topbar__history-menu" role="menu">
            {history.length === 0 ? (
              <p className="ui-text-muted" style={{ margin: 8, fontSize: 12 }}>
                저장된 빌드 없음. 분석하면 자동 저장됩니다.
              </p>
            ) : (
              <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                {history.map((b) => (
                  <li key={b.id} className="app-topbar__history-item">
                    <button
                      type="button"
                      className="app-topbar__history-load"
                      onClick={() => { onSelectBuild(b.id); setOpen(false); }}
                    >
                      <div className="app-topbar__history-line1">
                        <span className="app-topbar__history-tier">{b.tier}</span>
                        <span className="app-topbar__history-name">{b.buildName}</span>
                      </div>
                      <div className="app-topbar__history-line2">
                        <span>{formatRelative(b.updatedAt)}</span>
                        {b.extraPobLinks.length > 0 && (
                          <span>· +{b.extraPobLinks.length} 보조</span>
                        )}
                        <span>· {b.mode.toUpperCase()}</span>
                      </div>
                    </button>
                    <button
                      type="button"
                      className="app-topbar__history-del"
                      onClick={(e) => { e.stopPropagation(); onRemoveBuild(b.id); }}
                      aria-label="삭제"
                      title="삭제"
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      <div className="app-topbar__game-toggle" role="group" aria-label="게임 선택">
        {GAMES.map((g) => (
          <button
            key={g}
            type="button"
            className={
              "app-topbar__game-btn" + (game === g ? " is-active" : "")
            }
            onClick={() => setGame(g)}
            title={
              g === "poe1"
                ? "POE 1 (Mirage 3.28) — 모든 기능 지원"
                : "POE 2 — GGPK 마이닝 인프라 호환. 코치/필터/Syndicate/패시브는 준비 중"
            }
          >
            {GAME_LABEL[g]}
          </button>
        ))}
      </div>

      <button
        className="app-topbar__patch"
        onClick={onUpdatePatch}
        disabled={patchStatus === "수집 중..."}
        type="button"
      >
        {patchStatus || "패치노트 갱신"}
      </button>
    </header>
  );
}
