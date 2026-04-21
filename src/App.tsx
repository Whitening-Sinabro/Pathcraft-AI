import { useEffect, useRef, useState, useMemo } from "react";
import { invoke } from "@tauri-apps/api/core";
import { buildSnapshot, onOverlayRequest, sendSnapshot } from "./overlay/channel";
import { BuildRatingSection } from "./components/BuildRating";
import { VariantTabs } from "./components/VariantTabs";
import { GearTimeline } from "./components/GearTimeline";
import { MapWarnings } from "./components/MapWarnings";
import { FilterPanel } from "./components/FilterPanel";
import { SyndicateBoard } from "./components/SyndicateBoard";
import { PobInputSection } from "./components/PobInputSection";
import { PassiveTreeView } from "./components/PassiveTreeView";
import { TopBar } from "./components/shell/TopBar";
import { Sidebar, isTabId, type TabId } from "./components/shell/Sidebar";
import { BuildSummarySection } from "./components/sections/BuildSummary";
import { LevelingGuideSection } from "./components/sections/LevelingGuide";
import { LevelingSkillsSection } from "./components/sections/LevelingSkills";
import { AuraUtilitySection } from "./components/sections/AuraUtility";
import { KeyItemsSection } from "./components/sections/KeyItems";
import { PassivePrioritySection } from "./components/sections/PassivePriority";
import { DangerZonesSection } from "./components/sections/DangerZones";
import { FarmingStrategySection } from "./components/sections/FarmingStrategy";
import { ValidationWarningsBanner } from "./components/ValidationWarningsBanner";
import { useBuildAnalyzer } from "./hooks/useBuildAnalyzer";
import { ChecklistProvider } from "./contexts/ChecklistContext";
import { useActiveGame } from "./contexts/ActiveGameContext";
import { openOverlay } from "./overlay/toggle";
import { useToggleShortcut } from "./overlay/useToggleShortcut";

function App() {
  const {
    pobLink, setPobLink,
    buildData,
    coaching,
    rawBuildJson,
    rawCoachJson,
    loading,
    error,
    extraPobLinks, setExtraPobLinks,
    extraBuildJsons,
    stageMode, setStageMode,
    alSplit, setAlSplit,
    syndicateRec,
    analyzeBuild,
    cancelAnalyze,
    mode, setMode,
    coachModel, setCoachModel,
    history, selectBuild, removeBuild,
  } = useBuildAnalyzer();

  const [patchStatus, setPatchStatus] = useState("");
  const { game } = useActiveGame();

  // 메인 탭 (build / syndicate / passive) — localStorage 영속
  const [activeTab, setActiveTab] = useState<TabId>(() => {
    try {
      const saved = localStorage.getItem("pathcraftai_active_tab");
      return isTabId(saved) ? saved : "build";
    } catch {
      return "build";
    }
  });
  function switchTab(tab: TabId) {
    setActiveTab(tab);
    try { localStorage.setItem("pathcraftai_active_tab", tab); } catch { /* ignore */ }
  }

  const buildKey = buildData?.meta?.build_name || "build";
  const buildName = buildData?.meta?.build_name || "";

  // 단축키 Ctrl/Cmd+Shift+O = 오버레이 열기
  useToggleShortcut(() => { openOverlay(); });

  // 오버레이 창 동기 — coaching 변경 시 emit + 오버레이 request 시 재전송
  const latestSnapshotRef = useRef<ReturnType<typeof buildSnapshot> | null>(null);
  useEffect(() => {
    if (!coaching) {
      latestSnapshotRef.current = null;
      return;
    }
    const snap = buildSnapshot({ buildKey, buildName, coaching });
    latestSnapshotRef.current = snap;
    sendSnapshot(snap).catch(() => { /* 오버레이 창 없을 수도 있음, 조용히 무시 */ });
  }, [coaching, buildKey, buildName]);

  useEffect(() => {
    const unlistenPromise = onOverlayRequest(() => {
      const snap = latestSnapshotRef.current;
      if (snap) sendSnapshot(snap).catch(() => { /* noop */ });
    });
    return () => { unlistenPromise.then((fn) => fn()).catch(() => { /* noop */ }); };
  }, []);

  // rawBuildJson에서 passive_tree_url 추출 (progression_stages[].passive_tree_url)
  const passiveTreeUrl = useMemo(() => {
    if (!rawBuildJson) return "";
    try {
      const d = JSON.parse(rawBuildJson);
      const stages = (d as { progression_stages?: Array<{ passive_tree_url?: string }> }).progression_stages || [];
      for (const s of stages) {
        if (s.passive_tree_url) return s.passive_tree_url;
      }
      return "";
    } catch {
      return "";
    }
  }, [rawBuildJson]);

  async function updatePatchNotes() {
    setPatchStatus("수집 중...");
    try {
      await invoke("collect_patch_notes");
      setPatchStatus("완료");
      setTimeout(() => setPatchStatus(""), 3000);
    } catch (e) {
      setPatchStatus(`오류: ${e}`);
    }
  }

  return (
    <div className="app-shell">
      <TopBar
        buildData={buildData}
        patchStatus={patchStatus}
        onUpdatePatch={updatePatchNotes}
        history={history}
        onSelectBuild={selectBuild}
        onRemoveBuild={removeBuild}
      />
      <Sidebar activeTab={activeTab} onSwitchTab={switchTab} />
      <main className="app-main">

      {game === "poe2" && (
        <div
          className="ui-alert ui-alert--warning"
          style={{ marginBottom: 16 }}
          role="status"
        >
          <strong>POE 2 선택됨</strong> — GGPK 마이닝 인프라는 호환 확인됨 (942 테이블 카탈로그 완료).
          그러나 현재 빌드 분석 / 필터 / Syndicate / 패시브 트리 기능은 <strong>POE 1 데이터 기반</strong>으로
          구현돼 있어 POE 2 맥락에서는 정확하지 않거나 부적합할 수 있음. 본격 POE 2 지원은 schema 재작성
          이후 예정. 기존 기능은 그대로 사용 가능하지만 결과를 POE 2 기준으로 해석하지 마세요.
        </div>
      )}

      {activeTab === "syndicate" && (
        <SyndicateBoard buildJson={rawBuildJson} recommendation={syndicateRec} />
      )}

      {activeTab === "passive" && (
        <PassiveTreeView url={passiveTreeUrl} />
      )}

      {activeTab === "build" && <>
        <PobInputSection
        pobLink={pobLink} setPobLink={setPobLink}
        extraPobLinks={extraPobLinks} setExtraPobLinks={setExtraPobLinks}
        stageMode={stageMode} setStageMode={setStageMode}
        alSplit={alSplit} setAlSplit={setAlSplit}
        loading={loading} onAnalyze={analyzeBuild} onCancel={cancelAnalyze}
        mode={mode} setMode={setMode}
        coachModel={coachModel} setCoachModel={setCoachModel}
      />

      {error && (
        <div className="ui-alert ui-alert--danger" style={{ marginBottom: 12 }}>{error}</div>
      )}

      {buildData && (
        <div className="ui-card--inset" style={{ marginBottom: 12 }}>
          <strong>{buildData.meta?.build_name}</strong>
          <span className="ui-text-muted" style={{ marginLeft: 8 }}>
            DPS: {buildData.stats?.dps?.toLocaleString()} |
            Life: {buildData.stats?.life?.toLocaleString()} |
            ES: {buildData.stats?.energy_shield?.toLocaleString()}
          </span>
        </div>
      )}

      <ValidationWarningsBanner
        warnings={coaching?._validation_warnings}
        trace={coaching?._normalization_trace}
      />

      {coaching && (
        <ChecklistProvider buildKey={buildKey}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <BuildSummarySection
              tier={coaching.tier}
              buildSummary={coaching.build_summary}
              strengths={coaching.strengths}
              weaknesses={coaching.weaknesses}
            />

            <BuildRatingSection rating={coaching.build_rating} />
            <VariantTabs snapshots={coaching.variant_snapshots} />

            <LevelingGuideSection guide={coaching.leveling_guide} />
            <LevelingSkillsSection skills={coaching.leveling_skills} />

            <AuraUtilitySection progression={coaching.aura_utility_progression} />

            <GearTimeline progression={coaching.gear_progression} />

            {/* 핵심 장비 폴백: gear_progression 비면 key_items로 대체 */}
            {(!coaching.gear_progression || coaching.gear_progression.length === 0) && (
              <KeyItemsSection items={coaching.key_items} />
            )}

            <PassivePrioritySection priorities={coaching.passive_priority} />

            <MapWarnings warnings={coaching.map_mod_warnings} />

            <DangerZonesSection zones={coaching.danger_zones} />

            <FarmingStrategySection strategy={coaching.farming_strategy} />

            {/* 필터 생성 */}
            {rawBuildJson && (
              <FilterPanel
                buildJson={rawBuildJson}
                coachingJson={rawCoachJson}
                extraBuildJsons={extraBuildJsons}
                stageMode={stageMode}
                alSplit={alSplit}
              />
            )}

          </div>
        </ChecklistProvider>
      )}
      </>}
      </main>
    </div>
  );
}

export default App;
