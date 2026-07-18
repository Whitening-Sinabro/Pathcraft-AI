import { space, radius, font } from "../theme";
import {
  LEAGUE_MODES, LEAGUE_MODE_LABEL, type LeagueMode,
} from "../hooks/useBuildAnalyzer";

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
}

/**
 * 후보 빌드 PoB + 레벨링/전환 PoB 검증 섹션.
 * App.tsx에서 분리 — 관심사 분리 + 재사용성.
 */
export function PobInputSection({
  pobLink, setPobLink,
  extraPobLinks, setExtraPobLinks,
  stageMode, setStageMode,
  alSplit, setAlSplit,
  loading, onAnalyze, onCancel,
  mode, setMode,
}: PobInputSectionProps) {
  const activeExtraCount = extraPobLinks.filter((l) => l.trim()).length;

  return (
    <>
      {/* PoB 검증 안내 */}
      <div
        style={{
          padding: space.md, marginBottom: space.sm, borderRadius: radius.md,
          background: "var(--accent-subtle)", color: "var(--accent-hover)",
          fontSize: font.md, lineHeight: 1.5,
        }}
      >
        <strong>PoB 검증</strong>:
        리서치 탭에서 고른 후보나 이미 가진 빌드 링크를 넣어 확인합니다.
        최종 PoB만 있으면 엔드게임 검증, 레벨링 PoB까지 있으면 전환 구간까지 같이 봅니다.
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
              m === "sc"    ? "소프트코어 거래 리그 - 기본값. 거래 경제 전제" :
              m === "ssf"   ? "솔로 셀프파운드 - 자급 크래프팅/커런시 중심" :
                              "하드코어 SSF - 생존 우선 + 자급 기준"
            }
          >
            {LEAGUE_MODE_LABEL[m]}
          </button>
        ))}
        <span className="ui-text-muted" style={{ fontSize: font.sm }}>
          필터/Syndicate 프리셋이 모드별로 달라짐
        </span>
      </div>

      <div style={{ display: "flex", gap: space.md, marginBottom: space.lg, flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="후보 빌드 URL (pobb.in, pastebin, Maxroll, poedb, 공식 passive tree URL)"
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
          title="PoB를 파싱하고 베타 고정 모델로 레벨링, 장비 진행, 위험 요소를 검증"
        >
          분석 시작
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
      {loading && (
        <div className="ui-text-muted" style={{ marginTop: -space.md, marginBottom: space.lg, fontSize: font.sm }}>
          {loading}
        </div>
      )}

      {/* 레벨링/전환 PoB 안내 */}
      <div
        style={{
          padding: space.md, marginBottom: space.sm, borderRadius: radius.md,
          background: "var(--status-warning-bg)", color: "var(--status-warning)",
          fontSize: font.md, lineHeight: 1.5,
        }}
      >
        <strong>레벨링/전환 PoB</strong> (선택):
        같은 빌드의 액트/초기 맵핑용 PoB가 있으면 추가합니다. 최종 PoB와 함께 파싱해서 단계별 차이를 봅니다.
        <br />
        <span className="ui-text-success" style={{ fontWeight: 600 }}>단계 분기 켜짐</span> 상태면
        각 POB의 <strong>캐릭터 레벨 차이</strong>로 자동 정렬: 낮은 레벨 → 캠페인, 높은 레벨 → 엔드게임.
        <br />
        <span style={{ fontSize: font.sm }}>
          예시: 엔드게임 레벨 98 + 레벨링 레벨 60 → 지역 레벨 67 기준 자동 분기
        </span>
      </div>

      <div style={{ marginBottom: space.xl }}>
        <textarea
          placeholder={`레벨링/전환 PoB - 한 줄에 하나씩 (비워둬도 됨)\nhttps://pobb.in/LEVELING_BUILD\nhttps://pobb.in/TRANSITION_BUILD`}
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
            레벨링/전환 PoB {activeExtraCount}개 입력됨
          </span>
          <label
            style={{
              display: "flex", alignItems: "center", gap: space.xs,
              fontSize: font.md, cursor: "pointer", marginLeft: "auto",
              padding: "4px 8px", borderRadius: radius.sm,
              background: stageMode ? "var(--status-success-bg)" : "transparent",
            }}
            title="권장 켜짐: 낮은 레벨 POB → 초반 지역 레벨 / 높은 레벨 POB → 후반 지역 레벨 자동 분기. 꺼짐 = 전체 합산"
          >
            <input
              type="checkbox" checked={stageMode}
              onChange={(e) => setStageMode(e.target.checked)}
            />
            <span
              className={stageMode ? "ui-text-success" : ""}
              style={{ fontWeight: stageMode ? 600 : 400 }}
            >
              단계 분기 {stageMode ? "켜짐" : "꺼짐"}
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
            <label style={{ fontSize: font.md, fontWeight: 600 }}>전환 지역 레벨:</label>
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
              레벨링 POB → 지역 레벨 1~{alSplit} / 엔드게임 POB → 지역 레벨 {alSplit + 1}~∞
              {alSplit === 67 && " (키타바 후 기본값)"}
              {alSplit >= 75 && alSplit <= 81 && " (옐로 맵 T6~T10)"}
              {alSplit >= 82 && " (레드 맵 T11+)"}
            </span>
          </div>
        )}
        {activeExtraCount > 0 && (
          <div className="ui-text-muted" style={{ marginTop: space.sm, fontSize: font.sm }}>
            상단 "분석 시작" 버튼을 누르면 입력한 PoB를 전부 한번에 파싱합니다.
          </div>
        )}
      </div>
    </>
  );
}
