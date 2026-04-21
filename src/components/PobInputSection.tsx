import { space, radius, font } from "../theme";
import {
  LEAGUE_MODES, LEAGUE_MODE_LABEL, type LeagueMode,
  COACH_MODEL_LABEL, type CoachModel,
} from "../hooks/useBuildAnalyzer";

const COACH_MODELS: CoachModel[] = [
  "claude-haiku-4-5-20251001",
  "claude-sonnet-4-6",
  "claude-opus-4-7",
];

interface PobInputSectionProps {
  pobLink: string;
  setPobLink: (v: string) => void;
  extraPobLinks: string[];
  setExtraPobLinks: (v: string[]) => void;
  stageMode: boolean;
  setStageMode: (v: boolean) => void;
  alSplit: number;
  setAlSplit: (v: number) => void;
  loading: string;
  onAnalyze: () => void;
  onCancel: () => void;
  mode: LeagueMode;
  setMode: (v: LeagueMode) => void;
  coachModel: CoachModel;
  setCoachModel: (m: CoachModel) => void;
}

/**
 * 1단계(최종 빌드) + 2단계(레벨링/중간) POB 입력 섹션.
 * App.tsx에서 분리 — 관심사 분리 + 재사용성.
 */
export function PobInputSection({
  pobLink, setPobLink,
  extraPobLinks, setExtraPobLinks,
  stageMode, setStageMode,
  alSplit, setAlSplit,
  loading, onAnalyze, onCancel,
  mode, setMode,
  coachModel, setCoachModel,
}: PobInputSectionProps) {
  const activeExtraCount = extraPobLinks.filter((l) => l.trim()).length;

  return (
    <>
      {/* 1단계 안내 */}
      <div
        style={{
          padding: space.md, marginBottom: space.sm, borderRadius: radius.md,
          background: "var(--accent-subtle)", color: "var(--accent-hover)",
          fontSize: font.md, lineHeight: 1.5,
        }}
      >
        <strong>1단계 — 최종 빌드 POB</strong> (필수):
        당신이 도달할 <strong>엔드게임 빌드</strong>를 넣으세요.
        AI 코치가 이 빌드를 분석해서 레벨링 가이드 + 장비 진행 + 오라 세팅 + 레이팅을 생성합니다.
      </div>

      {/* 리그 모드 선택 — 필터/Syndicate 프리셋에 영향 */}
      <div
        style={{
          display: "flex", alignItems: "center", gap: space.md,
          marginBottom: space.lg, flexWrap: "wrap",
          fontSize: font.md,
        }}
      >
        <span className="ui-text-secondary" style={{ fontWeight: 600 }}>리그 모드:</span>
        {LEAGUE_MODES.map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={mode === m ? "ui-button ui-button--primary" : "ui-button ui-button--secondary"}
            style={{ padding: "4px 12px", fontSize: font.sm, fontWeight: 600 }}
            title={
              m === "sc"    ? "Softcore Trade — 기본. 트레이드 경제 전제" :
              m === "ssf"   ? "Solo Self-Found — 자급 크래프팅/커런시 중심" :
                              "Hardcore SSF — 위험 회피 + 자급. 프리셋도 HC-safe 우선"
            }
          >
            {LEAGUE_MODE_LABEL[m]}
          </button>
        ))}
        <span className="ui-text-muted" style={{ fontSize: font.sm }}>
          필터/Syndicate 프리셋이 모드별로 달라짐
        </span>
      </div>

      {/* 코치 모델 선택 — Haiku(저가) vs Sonnet(정확). 기본 Haiku. */}
      <div
        style={{
          display: "flex", alignItems: "center", gap: space.md,
          marginBottom: space.lg, flexWrap: "wrap",
          fontSize: font.md,
        }}
      >
        <span className="ui-text-secondary" style={{ fontWeight: 600 }}>코치 모델:</span>
        {COACH_MODELS.map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setCoachModel(m)}
            disabled={!!loading}
            className={coachModel === m ? "ui-button ui-button--primary" : "ui-button ui-button--secondary"}
            style={{ padding: "4px 12px", fontSize: font.sm, fontWeight: 600 }}
            title={
              m === "claude-haiku-4-5-20251001"
                ? "가장 빠름 — 반복 테스트/간단 분석"
                : m === "claude-sonnet-4-6"
                  ? "중간 속도 — 기본 정확도"
                  : "가장 느림 — 최상 디테일"
            }
          >
            {COACH_MODEL_LABEL[m]}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", gap: space.md, marginBottom: space.lg, flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="최종/엔드게임 빌드 POB 링크 (pobb.in, pastebin 등)"
          value={pobLink}
          onChange={(e) => setPobLink(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onAnalyze()}
          style={{
            flex: 1, minWidth: 250,
            padding: "10px 12px", borderRadius: radius.md,
            border: "2px solid var(--accent-primary)", fontSize: font.lg,
          }}
        />
        <button
          onClick={onAnalyze}
          disabled={!pobLink || !!loading}
          className="ui-button ui-button--primary"
          style={{ padding: "10px 20px", fontSize: font.lg, fontWeight: 600, cursor: loading ? "wait" : "pointer" }}
        >
          {loading || "분석"}
        </button>
        {loading && (
          <button
            onClick={onCancel}
            className="ui-button ui-button--secondary"
            style={{ padding: "10px 20px", fontSize: font.lg, fontWeight: 600, cursor: "pointer" }}
            title="코치 분석 중단 (Python subprocess 종료)"
          >
            정지
          </button>
        )}
      </div>

      {/* 2단계 안내 */}
      <div
        style={{
          padding: space.md, marginBottom: space.sm, borderRadius: radius.md,
          background: "var(--status-warning-bg)", color: "var(--status-warning)",
          fontSize: font.md, lineHeight: 1.5,
        }}
      >
        <strong>2단계 — 레벨링/중간 빌드 POB</strong> (선택):
        레벨링/맵핑용 POB가 따로 있으면 추가. <strong>필터에만 통합</strong>됩니다 (AI 분석은 1단계만).
        <br />
        <span className="ui-text-success" style={{ fontWeight: 600 }}>Stage 분기 ON</span> 상태면
        각 POB의 <strong>캐릭터 레벨 차이</strong>로 자동 정렬: 낮은 Lv → 캠페인, 높은 Lv → 엔드게임.
        <br />
        <span style={{ fontSize: font.sm }}>
          예시: 엔드게임 Lv 98(1단계) + 레벨링 Lv 60(2단계) → AL 67 기준 자동 분기
        </span>
      </div>

      <div style={{ marginBottom: space.xl }}>
        <textarea
          placeholder={`레벨링/중간 빌드 POB — 한 줄에 하나씩 (비워둬도 됨)\nhttps://pobb.in/LEVELING_BUILD\nhttps://pobb.in/TRANSITION_BUILD`}
          value={extraPobLinks.join("\n")}
          onChange={(e) => setExtraPobLinks(e.target.value.split("\n"))}
          rows={Math.max(3, activeExtraCount + 1)}
          style={{
            width: "100%", padding: "8px 12px", borderRadius: radius.md,
            border: "1px solid var(--status-warning)", fontSize: font.base,
            fontFamily: "var(--font-mono)", resize: "vertical", boxSizing: "border-box",
          }}
        />
        <div
          style={{
            display: "flex", gap: space.md, alignItems: "center",
            flexWrap: "wrap", marginTop: space.sm,
          }}
        >
          <span className="ui-text-warning" style={{ fontSize: font.md, fontWeight: 600 }}>
            레벨링/중간 POB {activeExtraCount}개 입력됨
          </span>
          <label
            style={{
              display: "flex", alignItems: "center", gap: space.xs,
              fontSize: font.md, cursor: "pointer", marginLeft: "auto",
              padding: "4px 8px", borderRadius: radius.sm,
              background: stageMode ? "var(--status-success-bg)" : "transparent",
            }}
            title="권장 ON: 낮은 Lv POB → 초반 AL / 높은 Lv POB → 후반 AL 자동 분기. OFF = 전체 union"
          >
            <input
              type="checkbox" checked={stageMode}
              onChange={(e) => setStageMode(e.target.checked)}
            />
            <span
              className={stageMode ? "ui-text-success" : ""}
              style={{ fontWeight: stageMode ? 600 : 400 }}
            >
              Stage 분기 {stageMode ? "ON" : "OFF"}
            </span>
          </label>
        </div>
        {stageMode && activeExtraCount === 1 && (
          <div
            className="ui-card--inset"
            style={{
              marginTop: space.md, padding: space.md, display: "flex",
              alignItems: "center", gap: space.md, flexWrap: "wrap",
            }}
          >
            <label style={{ fontSize: font.md, fontWeight: 600 }}>전환 AreaLevel:</label>
            <input
              type="number" min={14} max={85} step={1}
              value={alSplit}
              onChange={(e) => setAlSplit(Math.max(14, Math.min(85, parseInt(e.target.value) || 67)))}
              style={{
                width: 60, padding: "4px 8px", borderRadius: radius.sm,
                border: "1px solid var(--border-default)", fontSize: font.md,
              }}
            />
            <span className="ui-text-muted" style={{ fontSize: font.sm }}>
              레벨링 POB → AL 1~{alSplit} / 엔드게임 POB → AL {alSplit + 1}~∞
              {alSplit === 67 && " (Kitava 후 기본값)"}
              {alSplit >= 75 && alSplit <= 81 && " (Yellow Map T6~T10)"}
              {alSplit >= 82 && " (Red Map T11+)"}
            </span>
          </div>
        )}
        {activeExtraCount > 0 && (
          <div className="ui-text-muted" style={{ marginTop: space.sm, fontSize: font.sm }}>
            상단 "분석" 버튼 누르면 1단계+2단계 POB 전부 한번에 파싱됩니다
          </div>
        )}
      </div>
    </>
  );
}
