import { colors, space, radius, font } from "../theme";

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
  loading, onAnalyze,
}: PobInputSectionProps) {
  const activeExtraCount = extraPobLinks.filter((l) => l.trim()).length;

  return (
    <>
      {/* 1단계 안내 */}
      <div style={{
        padding: space.md, background: colors.primaryLight,
        borderRadius: radius.md, marginBottom: space.sm,
        fontSize: font.md, color: colors.primaryDark, lineHeight: 1.5,
      }}>
        <strong>🎯 1단계 — 최종 빌드 POB</strong> (필수):
        당신이 도달할 <strong>엔드게임 빌드</strong>를 넣으세요.
        AI 코치가 이 빌드를 분석해서 레벨링 가이드 + 장비 진행 + 오라 세팅 + 레이팅을 생성합니다.
      </div>

      <div style={{
        display: "flex", gap: space.md, marginBottom: space.lg,
        flexWrap: "wrap",
      }}>
        <input
          type="text"
          placeholder="최종/엔드게임 빌드 POB 링크 (pobb.in, pastebin 등)"
          value={pobLink}
          onChange={(e) => setPobLink(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onAnalyze()}
          style={{
            flex: 1, minWidth: 250,
            padding: "10px 12px", borderRadius: radius.md,
            border: `2px solid ${colors.primary}`, fontSize: font.lg,
          }}
        />
        <button
          onClick={onAnalyze}
          disabled={!pobLink || !!loading}
          style={{
            padding: "10px 20px", borderRadius: radius.md, border: "none",
            background: loading ? colors.textMuted : colors.primary, color: "#fff",
            cursor: loading ? "wait" : "pointer",
            fontSize: font.lg, fontWeight: 600,
          }}
        >
          {loading || "분석"}
        </button>
      </div>

      {/* 2단계 안내 */}
      <div style={{
        padding: space.md, background: colors.secondaryLight,
        borderRadius: radius.md, marginBottom: space.sm,
        fontSize: font.md, color: colors.secondaryDark, lineHeight: 1.5,
      }}>
        <strong>📎 2단계 — 레벨링/중간 빌드 POB</strong> (선택):
        레벨링/맵핑용 POB가 따로 있으면 추가. <strong>필터에만 통합</strong>됩니다 (AI 분석은 1단계만).
        <br />
        <span style={{ color: colors.success, fontWeight: 600 }}>✓ Stage 분기 ON</span> 상태면
        각 POB의 <strong>캐릭터 레벨 차이</strong>로 자동 정렬: 낮은 Lv → 캠페인, 높은 Lv → 엔드게임.
        <br />
        <span style={{ fontSize: font.sm, color: colors.warningDark }}>
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
            border: `1px solid ${colors.secondary}`, fontSize: font.base,
            fontFamily: "monospace", resize: "vertical", boxSizing: "border-box",
          }}
        />
        <div style={{
          display: "flex", gap: space.md, alignItems: "center",
          flexWrap: "wrap", marginTop: space.sm,
        }}>
          <span style={{ fontSize: font.md, color: colors.secondary, fontWeight: 600 }}>
            📎 레벨링/중간 POB {activeExtraCount}개 입력됨
          </span>
          <label
            style={{
              display: "flex", alignItems: "center", gap: space.xs,
              fontSize: font.md, cursor: "pointer", marginLeft: "auto",
              padding: "4px 8px", borderRadius: radius.sm,
              background: stageMode ? colors.successLight : "transparent",
            }}
            title="권장 ON: 낮은 Lv POB → 초반 AL / 높은 Lv POB → 후반 AL 자동 분기. OFF = 전체 union"
          >
            <input
              type="checkbox" checked={stageMode}
              onChange={(e) => setStageMode(e.target.checked)}
            />
            <span style={{
              fontWeight: stageMode ? 600 : 400,
              color: stageMode ? colors.success : colors.text,
            }}>
              Stage 분기 {stageMode ? "✓ ON" : "OFF"}
            </span>
          </label>
        </div>
        {stageMode && activeExtraCount === 1 && (
          <div style={{
            marginTop: space.md, padding: space.md, background: colors.bgSoft,
            borderRadius: radius.sm, display: "flex", alignItems: "center",
            gap: space.md, flexWrap: "wrap",
          }}>
            <label style={{ fontSize: font.md, color: colors.text, fontWeight: 600 }}>
              🎯 전환 AreaLevel:
            </label>
            <input
              type="number" min={14} max={85} step={1}
              value={alSplit}
              onChange={(e) => setAlSplit(Math.max(14, Math.min(85, parseInt(e.target.value) || 67)))}
              style={{
                width: 60, padding: "4px 8px", borderRadius: radius.sm,
                border: `1px solid ${colors.border}`, fontSize: font.md,
              }}
            />
            <span style={{ fontSize: font.sm, color: colors.textMuted }}>
              레벨링 POB → AL 1~{alSplit} / 엔드게임 POB → AL {alSplit + 1}~∞
              {alSplit === 67 && " (Kitava 후 기본값)"}
              {alSplit >= 75 && alSplit <= 81 && " (Yellow Map T6~T10)"}
              {alSplit >= 82 && " (Red Map T11+)"}
            </span>
          </div>
        )}
        {activeExtraCount > 0 && (
          <div style={{ marginTop: space.sm, fontSize: font.sm, color: colors.textMuted }}>
            ⓘ 상단 "분석" 버튼 누르면 1단계+2단계 POB 전부 한번에 파싱됩니다
          </div>
        )}
      </div>
    </>
  );
}
