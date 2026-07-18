import { useEffect, useMemo, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { buildSnapshot, onOverlayRequest, sendSnapshot } from "./overlay/channel";
import { BuildRatingSection } from "./components/BuildRating";
import { VariantTabs } from "./components/VariantTabs";
import { GearTimeline } from "./components/GearTimeline";
import { MapWarnings } from "./components/MapWarnings";
import { FilterPanel } from "./components/FilterPanel";
import { SyndicateBoard } from "./components/SyndicateBoard";
import { PobInputSection } from "./components/PobInputSection";
import { VerbalBuildInputSection } from "./components/VerbalBuildInput";
import { PassiveTreeView } from "./components/PassiveTreeView";
import { ResearchDashboard, type ResearchBuildSelection } from "./components/ResearchDashboard";
import { TopBar } from "./components/shell/TopBar";
import { Sidebar, type TabId } from "./components/shell/Sidebar";
import { BuildSummarySection } from "./components/sections/BuildSummary";
import { LevelingGuideSection } from "./components/sections/LevelingGuide";
import { LevelingSkillsSection } from "./components/sections/LevelingSkills";
import { AuraUtilitySection } from "./components/sections/AuraUtility";
import { KeyItemsSection } from "./components/sections/KeyItems";
import { PassivePrioritySection } from "./components/sections/PassivePriority";
import { DangerZonesSection } from "./components/sections/DangerZones";
import { FarmingStrategySection } from "./components/sections/FarmingStrategy";
import { NewPlayerBridgeSection } from "./components/sections/NewPlayerBridge";
import { ValidationWarningsBanner } from "./components/ValidationWarningsBanner";
import { CoachBlockedBanner, isCoachBlocked } from "./components/CoachBlockedBanner";
import { useBuildAnalyzer } from "./hooks/useBuildAnalyzer";
import { ChecklistProvider } from "./contexts/ChecklistContext";
import { useActiveGame } from "./contexts/ActiveGameContext";
import { openOverlay } from "./overlay/toggle";
import { useToggleShortcut } from "./overlay/useToggleShortcut";

const REPRESENTATIVE_TEMPLATE_COPY: Record<string, { title: string; summary: string; bullets: string[] }> = {
  plan_a_exact: {
    title: "바로 따라갈 수 있는 후보입니다",
    summary: "입력한 빌드와 코퍼스의 기준이 잘 맞습니다. 레벨링, 예산, 패치 위험을 함께 확인하면서 진행하면 됩니다.",
    bullets: [
      "입력한 스킬과 클래스 경로를 유지합니다.",
      "레벨링과 장비 전환 포인트를 먼저 확인하세요.",
      "최신 패치 이후 실제 poe.ninja 사례로 한 번 더 대조합니다.",
    ],
  },
  plan_b_hold_exact: {
    title: "연습은 가능하지만 검증이 더 필요합니다",
    summary: "빌드 방향은 유지할 수 있지만, 지금 상태에서 확정 추천으로 올리기에는 근거가 부족합니다.",
    bullets: [
      "입력한 스킬과 클래스 경로는 유지합니다.",
      "레벨링 PoB나 최근 영상/poe.ninja 사례를 더 확인하세요.",
      "검증 전에는 고비용 전환을 미루는 편이 낫습니다.",
    ],
  },
  plan_b_budget_tight: {
    title: "예산을 먼저 맞춰야 하는 후보입니다",
    summary: "빌드 방향은 맞지만 현재 예산 기준으로는 초반 체감이 나쁠 수 있습니다.",
    bullets: [
      "저가 스타터 구간과 최종 전환 구간을 분리하세요.",
      "필수 유니크와 5링크/6링크 시점을 먼저 확인합니다.",
      "비용이 맞기 전에는 대체 스킬이나 같은 클래스 프록시를 고려합니다.",
    ],
  },
  plan_b_soft_content_miss: {
    title: "목표 콘텐츠와 일부 맞지 않습니다",
    summary: "스킬과 클래스는 유지할 수 있지만, 선택한 콘텐츠에서는 성능이나 편의성이 부족할 수 있습니다.",
    bullets: [
      "어느 콘텐츠에서 약한지 먼저 확인합니다.",
      "파밍 전략은 빌드가 잘하는 콘텐츠 중심으로 조정하세요.",
      "목표 콘텐츠가 고정이면 다른 후보와 비교가 필요합니다.",
    ],
  },
  plan_b_watch_exact: {
    title: "가능성은 높지만 관찰이 필요합니다",
    summary: "기본 조건은 맞지만 시즌 초반 데이터가 더 쌓여야 확정 추천으로 올릴 수 있습니다.",
    bullets: [
      "같은 스킬의 최근 캐릭터 분포를 계속 확인합니다.",
      "레벨링 루트와 초반 장비 가격을 따로 확인하세요.",
      "초반에는 낮은 투자 버전으로 연습하는 쪽이 안전합니다.",
    ],
  },
  plan_c_skill_proxy: {
    title: "같은 계열의 대체 경로가 필요합니다",
    summary: "요청한 스킬 그대로는 추천하기 어렵고, 같은 클래스나 같은 플레이 방식의 대체 후보를 봐야 합니다.",
    bullets: [
      "대체 후보를 원래 빌드처럼 표시하지 않습니다.",
      "전환 비용과 후반 복귀 가능성을 함께 봅니다.",
      "레벨링은 안정적인 스타터를 먼저 선택하세요.",
    ],
  },
  plan_c_proxy_bridge: {
    title: "브릿지 빌드가 필요한 상태입니다",
    summary: "현재 조건에서는 최종 빌드로 바로 가기 어렵습니다. 먼저 안정적인 중간 경로를 잡아야 합니다.",
    bullets: [
      "중간 빌드를 최종 빌드와 구분해서 봅니다.",
      "전환 레벨, 필수 아이템, 후회 포인트를 확인합니다.",
      "최종 빌드는 전환 조건이 맞을 때 다시 검증합니다.",
    ],
  },
  plan_d_patch_block: {
    title: "패치 확인 전까지 보류합니다",
    summary: "이번 패치 변경점 때문에 바로 추천하기 어렵습니다. 최신 패치 노트와 실제 캐릭터 사례 확인이 필요합니다.",
    bullets: [
      "핵심 젬, 전직, 유니크 변경 여부를 확인합니다.",
      "3.29 poe.ninja 분포가 잡힌 뒤 다시 비교합니다.",
      "검증 전에는 연습 후보 또는 관찰 후보로만 둡니다.",
    ],
  },
  plan_d_budget_block: {
    title: "현재 예산으로는 보류합니다",
    summary: "지금 예산에서는 안정적으로 시작하기 어렵습니다. 더 싼 스타터나 전환형 경로가 필요합니다.",
    bullets: [
      "필수 아이템 가격을 먼저 확인합니다.",
      "초반 스타터와 최종 빌드를 분리합니다.",
      "예산이 맞기 전에는 고비용 전환을 피하세요.",
    ],
  },
  plan_d_character_lock: {
    title: "현재 캐릭터로는 맞지 않습니다",
    summary: "클래스나 전직 조건이 맞지 않아 그대로 추천할 수 없습니다. 리롤 허용 여부가 필요합니다.",
    bullets: [
      "현재 캐릭터 유지 여부를 먼저 정합니다.",
      "같은 클래스 안에서 가능한 대체 후보를 확인합니다.",
      "리롤이 가능하면 더 넓은 후보군으로 다시 봅니다.",
    ],
  },
  plan_d_proxy_scope_block: {
    title: "대체 후보 범위를 벗어났습니다",
    summary: "현재 조건에서는 같은 클래스/전직 안에서 자연스럽게 이어지는 후보를 찾기 어렵습니다.",
    bullets: [
      "같은 클래스 안의 전환 후보를 먼저 확인합니다.",
      "전직 변경이나 리롤을 허용할지 정해야 합니다.",
      "조건이 풀리면 후보군을 다시 넓힙니다.",
    ],
  },
  plan_d_input_block: {
    title: "조작 난도가 높아 보류합니다",
    summary: "요청한 난도 기준을 넘습니다. 더 단순한 플레이 방식의 후보를 먼저 보는 편이 좋습니다.",
    bullets: [
      "버튼 수와 유지해야 하는 버프를 확인합니다.",
      "초반에는 단순한 맵핑 후보를 우선합니다.",
      "익숙해진 뒤 고난도 버전으로 전환하세요.",
    ],
  },
  plan_d_leveling_block: {
    title: "레벨링 경로가 부족합니다",
    summary: "최종 빌드 정보만으로는 시작 루트를 안전하게 만들기 어렵습니다. 레벨링 PoB나 빌더의 캠페인 루트가 필요합니다.",
    bullets: [
      "레벨링 PoB, Act 구간 젬, 전환 레벨을 확인합니다.",
      "최종 PoB만 있으면 연습 후보로만 취급합니다.",
      "같은 빌더의 스타터/전환 영상을 우선 확인합니다.",
    ],
  },
  plan_d_abstain_generic: {
    title: "아직 확정 추천 없음",
    summary: "현재 입력만으로는 바로 추천할 후보가 없습니다. 리서치 큐에서 후보를 고르거나 추가 근거를 넣어 다시 확인해야 합니다.",
    bullets: [
      "후보 빌드, 레벨링 경로, 예산 조건 중 빠진 항목을 채웁니다.",
      "poe.ninja와 빌더 영상에서 최근 사례를 먼저 확인합니다.",
      "검증 전에는 추천이 아니라 관찰 후보로 둡니다.",
    ],
  },
};

function getRepresentativeCopy(templateId?: string, fallback?: { title?: string; summary?: string; bullets?: string[] }) {
  if (templateId && REPRESENTATIVE_TEMPLATE_COPY[templateId]) {
    return REPRESENTATIVE_TEMPLATE_COPY[templateId];
  }
  return {
    title: fallback?.title || "추천 상태 안내",
    summary: fallback?.summary || "응답 계층 정보가 없습니다.",
    bullets: fallback?.bullets || [],
  };
}

const REPRESENTATIVE_SKILL_KO: Record<string, string> = {
  Arc: "연쇄 번개",
  "Ball Lightning": "구형 번개",
  Boneshatter: "뼈박살",
  "Caustic Arrow": "부식성 화살",
  Cleave: "가르기",
  "Cold Snap of Power": "권능의 한파",
  "Corrupting Fever": "타락한 열병",
  "Detonate Dead": "시체 폭발",
  "Dominating Blow": "지배의 일격",
  "Explosive Arrow Ballista": "폭발 화살 쇠뇌",
  "Exsanguinate Mine": "출혈 마인",
  "Freezing Pulse": "동결 파동",
  Frostbolt: "서리 구체",
  "Ground Slam": "대지 강타",
  "Hexblast Mine": "사술 폭발 마인",
  "Holy Flame Totem": "신성한 화염 토템",
  "Ice Nova": "얼음 폭발",
  "Ice Shot": "얼음 화살",
  "Kinetic Fusillade of Detonation": "폭발의 동력 탄막",
  Lacerate: "찢기",
  "Lightning Arrow": "번개 화살",
  "Lightning Strike": "번개 타격",
  "Penance Brand": "속죄의 낙인",
  "Power Siphon": "권능 착취",
  "Pyroclast Mine": "화염질주 마인",
  "Rain of Arrows": "화살비",
  "Rolling Magma": "용암 구체",
  "Shock Nova of Procession": "행렬의 충격 폭발",
  "Shockwave Totem": "충격파 토템",
  "Shrapnel Ballista": "파편 쇠뇌",
  "Siege Ballista": "공성 쇠뇌",
  "Split Arrow": "분할 화살",
  "Splitting Steel": "분열 강철",
  "Storm Brand": "폭풍 낙인",
  "Stormblast Mine": "폭풍 점사 마인",
  "Summon Holy Relic": "성스러운 유물 소환",
  "Toxic Rain": "맹독성 비",
};

const REPRESENTATIVE_CLASS_KO: Record<string, string> = {
  Marauder: "머라우더",
  Duelist: "듀얼리스트",
  Ranger: "레인저",
  Shadow: "쉐도우",
  Witch: "위치",
  Templar: "템플러",
  Scion: "사이온",
  Juggernaut: "저거넛",
  Champion: "챔피언",
  Deadeye: "데드아이",
  Pathfinder: "패스파인더",
  Hierophant: "하이로펀트",
  Saboteur: "사보추어",
  Trickster: "트릭스터",
  Elementalist: "엘리멘탈리스트",
  Gladiator: "글래디에이터",
  Guardian: "가디언",
  Inquisitor: "인퀴지터",
};

const REPRESENTATIVE_STATUS_KO: Record<string, string> = {
  confirmed: "확인됨",
  near_confirmed: "준확인",
  hold: "보류",
  inferred: "추정",
  high: "높음",
  medium: "보통",
  low: "낮음",
  early_maps: "초기 맵",
  late_endgame: "고점 세팅",
};

function formatRepresentativeBool(value?: boolean, yes = "예", no = "아니오") {
  if (typeof value !== "boolean") return "-";
  return value ? yes : no;
}

function formatRepresentativeCost(value?: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "-";
  return `${value}딥`;
}

function formatRepresentativeStageLabel(stage?: string, fallback?: string) {
  return formatRepresentativeText(stage || fallback || "단계");
}

function formatRepresentativeText(value?: string) {
  if (!value) return "-";
  return REPRESENTATIVE_STATUS_KO[value]
    || REPRESENTATIVE_SKILL_KO[value]
    || REPRESENTATIVE_CLASS_KO[value]
    || value
      .replace(/Campaign Start/g, "캠페인 시작")
      .replace(/Maps Entry/g, "맵 진입")
      .replace(/High End/g, "고점 세팅")
      .replace(/starter/g, "스타터")
      .replace(/final/g, "최종")
      .replace(/level/g, "레벨")
      .replace(/_/g, " ");
}

function formatRepresentativeSkill(value?: string) {
  return value ? REPRESENTATIVE_SKILL_KO[value] || value : "";
}

function formatRepresentativeClass(value?: string) {
  return value ? REPRESENTATIVE_CLASS_KO[value] || value : "";
}

function formatRepresentativeLinks(values?: string[]) {
  return values?.slice(0, 3).map(formatRepresentativeSkill).join(" + ") || "";
}

function formatResearchStepLabel(step: { level?: number; from_skill?: string; main_skill?: string; to_skill?: string; required_links?: number }) {
  const from = formatRepresentativeSkill(step.from_skill || step.main_skill) || "시작";
  const to = formatRepresentativeSkill(step.to_skill);
  const parts = [`레벨 ${step.level ?? "?"}: ${from}${to ? ` -> ${to}` : ""}`];
  if (step.required_links) parts.push(`${step.required_links}링크`);
  return parts.join(" | ");
}

function sourceKindText(value?: string) {
  const lower = (value || "").toLowerCase();
  if (lower.includes("pobb") || lower.includes("pob") || lower.includes("pastebin")) return "PoB";
  if (lower.includes("youtube")) return "유튜브";
  if (lower.includes("twitch")) return "트위치";
  if (lower.includes("ninja")) return "poe.ninja";
  if (lower.includes("maxroll")) return "Maxroll";
  if (lower.includes("poe_vault")) return "PoE Vault";
  if (lower.includes("manual")) return "수동 큐레이션";
  return value || "소스";
}

function evidenceMatches(entry: { type?: string; label?: string; url?: string | null; notes?: string }, tokens: string[]) {
  const text = [entry.type, entry.label, entry.url, entry.notes].filter(Boolean).join(" ").toLowerCase();
  return tokens.some((token) => text.includes(token));
}

function buildSourceSlots(evidence: Array<{ type?: string; label?: string; url?: string | null; notes?: string }>) {
  const linkedEvidence = evidence.filter((entry) => entry.url);
  const slots = [
    { id: "guide", label: "원본 가이드/영상", tokens: ["youtube", "twitch", "guide", "maxroll", "poe_vault", "creator"] },
    { id: "endgame_pob", label: "엔드게임 PoB", tokens: ["pobb", "pob", "pastebin", "endgame"] },
    { id: "leveling_pob", label: "레벨링 PoB", tokens: ["leveling pob", "campaign pob", "act pob", "starter pob"] },
    { id: "ninja", label: "poe.ninja/캐릭터", tokens: ["poe.ninja", "ninja", "character"] },
  ];

  const assignedUrls = new Set<string>();
  const grouped = slots
    .map((slot) => {
      const entries = linkedEvidence
        .filter((entry) => evidenceMatches(entry, slot.tokens))
        .slice(0, 3);
      entries.forEach((entry) => assignedUrls.add(entry.url || ""));
      return { ...slot, entries };
    })
    .filter((slot) => slot.entries.length > 0);

  const otherEntries = linkedEvidence.filter((entry) => !assignedUrls.has(entry.url || "")).slice(0, 3);
  if (otherEntries.length > 0) {
    grouped.push({ id: "other", label: "기타 원본", tokens: [], entries: otherEntries });
  }

  return grouped;
}

function researchPobUrls(build: ResearchBuildSelection) {
  const seen = new Set<string>();
  const urls: string[] = [];
  for (const entry of build.evidence) {
    const url = entry.url || "";
    if (!/pobb\.in|pastebin\.com|pathofbuilding/i.test(url)) continue;
    if (seen.has(url)) continue;
    seen.add(url);
    urls.push(url);
  }
  return urls;
}

function SelectedResearchBuildPanel({
  build,
  onBack,
  onClear,
}: {
  build: ResearchBuildSelection;
  onBack: () => void;
  onClear: () => void;
}) {
  const sourceSlots = buildSourceSlots(build.evidence);

  return (
    <section className="ui-card--inset research-selected-build" style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <div>
          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>
            선택한 추천 빌드
          </div>
          <h3 className="ui-section-title" style={{ marginTop: 4 }}>{build.title}</h3>
          {build.originalName && build.originalName !== build.title && (
            <div className="ui-text-muted" style={{ marginTop: 4, fontSize: 12 }}>
              원본 표기: {build.originalName}
            </div>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 6, flexWrap: "wrap" }}>
          <span className="ui-badge ui-badge--accent">{build.categoryLabel}</span>
          <span className="ui-badge ui-badge--success">{build.judgement}</span>
          {build.patch && <span className="ui-badge ui-badge--info">출처 패치 {build.patch}</span>}
        </div>
      </div>

      <p className="ui-text-muted" style={{ margin: "10px 0 0", fontSize: 12, lineHeight: 1.55 }}>
        {build.reason}
      </p>

      {researchPobUrls(build).length > 0 && (
        <div className="ui-alert ui-alert--info" style={{ marginTop: 10, fontSize: 12 }}>
          이 후보의 PoB가 아래 입력칸에 자동으로 들어갔습니다. 바로 <strong>분석 시작</strong>을 누르면 스킬셋과 패시브 트리를 파싱합니다.
        </div>
      )}

      <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        <div>
          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>빌드 경로</div>
          <div style={{ marginTop: 5, fontSize: 12, lineHeight: 1.55 }}>
            {[
              build.className,
              build.ascendancy,
              build.routeLabel,
            ].filter(Boolean).join(" / ")}
          </div>
          <div className="ui-text-muted" style={{ marginTop: 5, fontSize: 12, lineHeight: 1.55 }}>
            메인 {build.mainSkill || "-"} · 레벨링 {build.levelingSkill || "-"}
          </div>
        </div>

        <div>
          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>예산/가용성</div>
          <div className="ui-text-muted" style={{ marginTop: 5, fontSize: 12, lineHeight: 1.55 }}>
            초기 {formatRepresentativeCost(build.budget.entry)}
            {" | 안정권 "}
            {formatRepresentativeCost(build.budget.comfortable)}
          </div>
          <div className="ui-text-muted" style={{ marginTop: 5, fontSize: 12, lineHeight: 1.55 }}>
            리그 스타트 {formatRepresentativeBool(build.availability.leagueStart, "가능", "불가")}
            {" | SSF "}
            {formatRepresentativeText(build.availability.ssf)}
            {" | HC "}
            {formatRepresentativeText(build.availability.hc)}
            {" | 트윙크 "}
            {formatRepresentativeBool(build.availability.twink, "필요", "불필요")}
          </div>
        </div>
      </div>

      {build.transitions.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>전환 포인트</div>
          <div style={{ marginTop: 6, display: "flex", gap: 6, flexWrap: "wrap" }}>
            {build.transitions.slice(0, 6).map((step, index) => (
              <span key={`${step.stage}-${step.level}-${index}`} className="ui-badge ui-badge--info">
                {formatResearchStepLabel(step)}
              </span>
            ))}
          </div>
        </div>
      )}

      {(build.campaignPlan.length > 0 || build.passivePlan.length > 0 || build.painPoints.length > 0) && (
        <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
          {build.campaignPlan.length > 0 && (
            <div>
              <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>캠페인/맵 단계</div>
              <div style={{ marginTop: 5, display: "flex", flexDirection: "column", gap: 4 }}>
                {build.campaignPlan.slice(0, 6).map((step, index) => (
                  <div key={`${step.stage}-${step.level_range}-${index}`} className="ui-card--inset" style={{ fontSize: 12, lineHeight: 1.45 }}>
                    <strong>{formatRepresentativeStageLabel(step.stage_label || step.stage)}</strong>
                    <div className="ui-text-muted" style={{ marginTop: 3 }}>
                      {step.level_range ? `${step.level_range} | ` : ""}
                      {step.main_skill ? formatRepresentativeSkill(step.main_skill) : ""}
                    </div>
                    {step.support_links && step.support_links.length > 0 && (
                      <div style={{ marginTop: 5, display: "flex", gap: 5, flexWrap: "wrap" }}>
                        {step.support_links.slice(0, 5).map((skill) => (
                          <span key={skill} className="ui-badge ui-badge--info">{formatRepresentativeText(skill)}</span>
                        ))}
                      </div>
                    )}
                    {step.notes && (
                      <div className="ui-text-muted" style={{ marginTop: 5 }}>
                        {formatRepresentativeText(step.notes)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {build.passivePlan.length > 0 && (
            <div>
              <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>패시브 방향</div>
              <div style={{ marginTop: 5, display: "flex", flexDirection: "column", gap: 4 }}>
                {build.passivePlan.slice(0, 3).map((step, index) => (
                  <div key={`${step.stage}-${step.level_range}-${index}`} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.45 }}>
                    {formatRepresentativeStageLabel(step.stage_label || step.stage, step.level_range)}
                    {step.priorities?.length ? ` | ${step.priorities.slice(0, 3).map(formatRepresentativeText).join(" / ")}` : ""}
                  </div>
                ))}
              </div>
            </div>
          )}

          {build.painPoints.length > 0 && (
            <div>
              <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>주의점</div>
              <div style={{ marginTop: 5, display: "flex", flexDirection: "column", gap: 4 }}>
                {build.painPoints.slice(0, 3).map((point) => (
                  <div key={point} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.45 }}>
                    {formatRepresentativeText(point)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {sourceSlots.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700 }}>원본/PoB 링크</div>
          <div style={{ marginTop: 6, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 8 }}>
            {sourceSlots.map((slot) => (
              <div
                key={slot.id}
                style={{
                  padding: 9,
                  borderRadius: 6,
                  border: "1px solid var(--border-default)",
                  background: "rgba(255, 255, 255, 0.015)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                  <strong style={{ fontSize: 12 }}>{slot.label}</strong>
                  <span className="ui-badge ui-badge--success">링크</span>
                </div>
                <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 4 }}>
                  {slot.entries.map((entry, index) => (
                    <div key={`${slot.id}-${entry.label || entry.type}-${index}`} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.45 }}>
                      <a href={entry.url || "#"} target="_blank" rel="noreferrer" style={{ color: "var(--status-info)", textDecoration: "none" }}>
                        {entry.label || entry.url}
                      </a>
                      <span> · {sourceKindText(entry.type)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button type="button" className="ui-button ui-button--secondary" onClick={onBack}>
          리서치로 돌아가기
        </button>
        <button type="button" className="ui-button ui-button--secondary" onClick={onClear}>
          선택 해제
        </button>
      </div>
    </section>
  );
}

type QuickGemSetupValue =
  | string
  | string[]
  | { links?: string | string[] | null; reasoning?: string | null }
  | Record<string, unknown>
  | null
  | undefined;

interface QuickStage {
  stage_name?: string;
  passive_tree_url?: string;
  gem_setups?: Record<string, QuickGemSetupValue>;
  alternate_gem_sets?: Record<string, QuickGemSetupValue>;
  bandit?: string;
  pantheon?: { major?: string; minor?: string };
}

interface QuickBuild {
  meta?: {
    build_name?: string;
    class?: string;
    ascendancy?: string;
    class_level?: number;
    pob_link?: string;
    version?: string;
  };
  stats?: {
    dps?: number;
    life?: number;
    energy_shield?: number;
    ehp?: number;
    armour?: number;
    evasion?: number;
    block?: number;
    spell_block?: number;
    resistances?: Record<string, number>;
  };
  progression_stages?: QuickStage[];
}

function formatCompactNumber(value?: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "-";
  const trimTrailingZero = (text: string) => text.replace(/\.0$/, "");
  const abs = Math.abs(value);
  if (Math.abs(value) >= 1_000_000) {
    return `${trimTrailingZero((value / 1_000_000).toFixed(abs >= 10_000_000 ? 0 : 1))}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${trimTrailingZero((value / 1_000).toFixed(abs >= 10_000 ? 0 : 1))}k`;
  }
  return value.toLocaleString();
}

function formatPercent(value?: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "-";
  return `${value}%`;
}

function getGemLinks(value: QuickGemSetupValue): string {
  if (!value) return "";
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(String).join(" - ");
  if (typeof value === "object") {
    const links = (value as { links?: unknown }).links;
    if (typeof links === "string") return links;
    if (Array.isArray(links)) return links.map(String).join(" - ");
  }
  return "";
}

function flattenAlternateGemSetups(alternate?: Record<string, QuickGemSetupValue>) {
  const rows: Array<{ label: string; links: string }> = [];
  if (!alternate) return rows;

  for (const [groupLabel, groupValue] of Object.entries(alternate)) {
    const directLinks = getGemLinks(groupValue);
    if (directLinks) {
      rows.push({ label: groupLabel, links: directLinks });
      continue;
    }
    if (!groupValue || typeof groupValue !== "object" || Array.isArray(groupValue)) continue;
    for (const [setupLabel, setupValue] of Object.entries(groupValue as Record<string, QuickGemSetupValue>)) {
      const links = getGemLinks(setupValue);
      if (links) rows.push({ label: `${groupLabel} / ${setupLabel}`, links });
    }
  }

  return rows;
}

function countLinkedGems(links: string) {
  return links.split(/\s+-\s+/).map((part) => part.trim()).filter(Boolean).length;
}

function getQuickBeginnerChecks(build: QuickBuild | null, gemSetups: Array<{ label: string; links: string }>) {
  if (!build) return [];

  const checks: Array<{ title: string; reason: string; action: string; tone: "warning" | "info" | "success" }> = [];
  const stats = build.stats ?? {};
  const res = stats.resistances ?? {};
  const mainLinkCount = gemSetups.reduce((max, setup) => Math.max(max, countLinkedGems(setup.links)), 0);
  const lowElementalRes = [
    ["화염", res.fire],
    ["냉기", res.cold],
    ["번개", res.lightning],
  ].filter(([, value]) => typeof value === "number" && value < 75);

  if (lowElementalRes.length > 0) {
    checks.push({
      title: "저항 캡 미달",
      reason: `${lowElementalRes.map(([label, value]) => `${label} ${value}%`).join(", ")} 상태라 맵에서 급사가 늘어납니다.`,
      action: "장비/벤치 크래프트로 화염·냉기·번개 저항을 먼저 75%까지 맞추세요.",
      tone: "warning",
    });
  }

  if (typeof res.chaos === "number" && res.chaos < 0) {
    checks.push({
      title: "카오스 저항 음수",
      reason: "캠페인은 버틸 수 있어도 레드맵부터 카오스 피해가 갑자기 아프게 느껴질 수 있습니다.",
      action: "반지, 벨트, 장갑 중 한 슬롯에 카오스 저항을 붙여 최소 0% 이상을 목표로 잡으세요.",
      tone: "warning",
    });
  }

  const ehp = typeof stats.ehp === "number" ? stats.ehp : (stats.life ?? 0) + (stats.energy_shield ?? 0);
  if (ehp > 0 && ehp < 4500) {
    checks.push({
      title: "생존 최소선 확인",
      reason: `현재 EHP가 ${formatCompactNumber(ehp)}라 얼리레드/T16에서 실수가 바로 죽음으로 이어질 수 있습니다.`,
      action: "라이프/ES가 없는 장비부터 교체하고, 플라스크 접미어와 에일먼트 면역을 같이 확인하세요.",
      tone: "warning",
    });
  }

  if ((stats.armour ?? 0) <= 0 && (stats.evasion ?? 0) <= 0 && (stats.block ?? 0) <= 0 && (stats.spell_block ?? 0) <= 0) {
    checks.push({
      title: "방어 레이어 확인",
      reason: "Armour/Evasion/Block이 0으로 잡혀 있습니다. PoB 설정 누락이 아니라면 피격을 줄여줄 방어층이 거의 없는 상태입니다.",
      action: "플라스크, Grace/Determination, 회피/방어 베이스, Spell Suppression 또는 Block 중 이 빌드가 쓰는 방어축을 먼저 확인하세요.",
      tone: "warning",
    });
  }

  if (mainLinkCount > 0 && mainLinkCount < 4) {
    checks.push({
      title: "메인 링크 부족",
      reason: `메인 스킬이 ${mainLinkCount}링크로 보입니다. 3.29에서는 색상 장착 제한보다 링크 수와 같은 색 소켓 품질 보너스를 분리해서 봐야 합니다.`,
      action: "최소 4링크를 먼저 맞추고, 색상은 메인 젬 품질 효과가 좋은 경우에 우선순위를 올리세요.",
      tone: "warning",
    });
  } else if (mainLinkCount >= 4 && mainLinkCount < 6) {
    checks.push({
      title: "다음 딜 상승점",
      reason: `현재 메인 스킬은 ${mainLinkCount}링크입니다. 초보자는 링크 수가 딜 차이를 만드는 구간에서 자주 막힙니다.`,
      action: "맵 진입 후에는 5링크, 레드맵 전에는 6링크 또는 동급 무기 업그레이드를 목표로 잡고, 색 맞춤은 핵심 젬 품질 보너스가 클 때만 우선하세요.",
      tone: "info",
    });
  }

  checks.push({
    title: "아틀라스 판단은 실측 필요",
    reason: "아틀라스/파밍 단계는 고정 숫자 하나로 확정하지 않고, 진행도·반복 가능한 최고 티어·사망 빈도·맵 시간·투자 회수를 같이 봐야 합니다.",
    action: "지금 편하게 도는 최고 맵 티어, 죽는 빈도, 평균 클리어 시간, 보이드스톤 수를 기록해 다음 판단 기준으로 쓰세요.",
    tone: "info",
  });

  return checks.slice(0, 4);
}

function App() {
  const {
    pobLink, setPobLink,
    buildData,
    coaching,
    rawBuildJson,
    rawCoachJson,
    loading,
    error,
    sourceResolution,
    corpusRecommendation,
    corpusLoading,
    corpusError,
    extraPobLinks, setExtraPobLinks,
    extraBuildJsons,
    stageMode, setStageMode,
    alSplit, setAlSplit,
    syndicateRec,
    analyzeBuild,
    analyzeVerbalBuild,
    cancelAnalyze,
    resetCurrentAnalysis,
    mode, setMode,
    coachModel: _coachModel,
    history, selectBuild, removeBuild,
  } = useBuildAnalyzer();

  const [patchStatus, setPatchStatus] = useState("");
  const { game } = useActiveGame();

  // 메인 탭 — 리서치가 시작점, PoB는 선택한 후보 검증 단계.
  const [activeTab, setActiveTab] = useState<TabId>("research");
  function switchTab(tab: TabId) {
    setActiveTab(tab);
  }
  const [selectedResearchBuild, setSelectedResearchBuild] = useState<ResearchBuildSelection | null>(null);
  function selectResearchBuild(build: ResearchBuildSelection) {
    setSelectedResearchBuild(build);
    resetCurrentAnalysis();
    const pobUrls = researchPobUrls(build);
    if (pobUrls.length > 0) {
      setPobLink(pobUrls[0]);
      setExtraPobLinks(pobUrls.slice(1, 8));
      setStageMode(true);
      setAlSplit(67);
    }
    if (build.categoryLabel === "CWS 리서치") {
      setMode("ssf");
    }
    switchTab("build");
  }

  const buildKey = buildData?.meta?.build_name || "build";
  const buildName = buildData?.meta?.build_name || "";
  const representativeRecommendation = corpusRecommendation?.recommendation;
  const representativeTopCandidates = representativeRecommendation?.recommendations.slice(0, 3) ?? [];
  const representativeProxyCandidates = representativeRecommendation?.proxy_candidates.slice(0, 2) ?? [];
  const representativeResponseLayers = representativeRecommendation?.response_layers;
  const representativeCopy = getRepresentativeCopy(
    representativeResponseLayers?.user_message.template_id,
    representativeResponseLayers?.user_message,
  );
  const selectedRepresentativeProfile =
    representativeRecommendation?.selected_profile
    ?? representativeRecommendation?.selected_candidate?.profile_summary
    ?? null;
  const selectedProfileIdentity = selectedRepresentativeProfile?.identity;
  const selectedProfileProgression = selectedRepresentativeProfile?.progression;
  const selectedProfileBudget = selectedRepresentativeProfile?.budget_curve;
  const selectedProfileAvailability = selectedRepresentativeProfile?.availability;
  const selectedProfileConfidence = selectedRepresentativeProfile?.confidence;
  const selectedProfileTransitions = selectedProfileProgression?.transition_points?.slice(0, 4) ?? [];
  const selectedProfileCampaign = selectedProfileProgression?.campaign_plan?.slice(0, 4) ?? [];
  const selectedProfilePassivePlan = selectedProfileProgression?.passive_plan?.slice(0, 3) ?? [];
  const selectedProfileEvidence = selectedRepresentativeProfile?.evidence
    ?.filter((entry) => entry.label || entry.url)
    .slice(0, 4) ?? [];
  const selectedProfilePainPoints = selectedRepresentativeProfile?.constraints?.pain_points?.slice(0, 3) ?? [];

  // 단축키 Ctrl/Cmd+Shift+O = 오버레이 열기
  useToggleShortcut(() => { openOverlay(); });

  // 오버레이 창 동기 — coaching 변경 시 emit + 오버레이 request 시 재전송.
  // L4 blocked 상태면 오버레이에도 반쪽 결과가 가지 않도록 차단.
  const latestSnapshotRef = useRef<ReturnType<typeof buildSnapshot> | null>(null);
  useEffect(() => {
    if (!coaching || isCoachBlocked(coaching)) {
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

  // rawBuildJson 또는 source resolver에서 passive_tree_url 추출.
  const passiveTreeUrl = useMemo(() => {
    if (sourceResolution?.passive_tree_url) return sourceResolution.passive_tree_url;
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
  }, [rawBuildJson, sourceResolution]);

  const quickBuild = buildData as QuickBuild | null;
  const quickStats = quickBuild?.stats;
  const quickStage = quickBuild?.progression_stages?.[0];
  const quickPassiveTreeUrl = quickStage?.passive_tree_url || passiveTreeUrl;
  const quickGemSetups = Object.entries(quickStage?.gem_setups ?? {})
    .map(([label, setup]) => ({ label, links: getGemLinks(setup) }))
    .filter((setup) => setup.links)
    .slice(0, 4);
  const quickAlternateSetups = flattenAlternateGemSetups(quickStage?.alternate_gem_sets).slice(0, 3);
  const quickResistances: Record<string, number> = quickStats?.resistances ?? {};
  const quickMetrics = [
    { label: "DPS", raw: quickStats?.dps, value: formatCompactNumber(quickStats?.dps), tone: "ui-badge--accent", showZero: false },
    { label: "Life", raw: quickStats?.life, value: formatCompactNumber(quickStats?.life), tone: "ui-badge--success", showZero: false },
    { label: "ES", raw: quickStats?.energy_shield, value: formatCompactNumber(quickStats?.energy_shield), tone: "ui-badge--info", showZero: true },
    { label: "EHP", raw: quickStats?.ehp, value: formatCompactNumber(quickStats?.ehp), tone: "ui-badge--info", showZero: false },
    { label: "Armour", raw: quickStats?.armour, value: formatCompactNumber(quickStats?.armour), tone: "ui-badge--info", showZero: false },
    { label: "Evasion", raw: quickStats?.evasion, value: formatCompactNumber(quickStats?.evasion), tone: "ui-badge--info", showZero: false },
  ].filter((metric) => metric.value !== "-" && (metric.showZero || metric.raw !== 0));
  const quickResistanceRows = [
    { key: "fire", label: "화염", value: quickResistances.fire },
    { key: "cold", label: "냉기", value: quickResistances.cold },
    { key: "lightning", label: "번개", value: quickResistances.lightning },
    { key: "chaos", label: "카오스", value: quickResistances.chaos },
  ].filter((resistance) => typeof resistance.value === "number" && Number.isFinite(resistance.value));
  const quickBeginnerChecks = getQuickBeginnerChecks(quickBuild, quickGemSetups);
  const activePassiveTreeUrl = quickPassiveTreeUrl || passiveTreeUrl;

  async function updatePatchNotes() {
    setPatchStatus("수집 중...");
    try {
      await invoke("collect_patch_notes", { game });
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
        onSelectBuild={(id) => {
          selectBuild(id);
          switchTab("build");
        }}
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
        <PassiveTreeView
          url={activePassiveTreeUrl}
          representativeProfile={selectedRepresentativeProfile}
          buildClassName={quickBuild?.meta?.class}
          buildAscendancyName={quickBuild?.meta?.ascendancy}
        />
      )}

      {activeTab === "research" && (
        <ResearchDashboard
          selectedBuildId={selectedResearchBuild?.id}
          onSelectBuild={selectResearchBuild}
        />
      )}

      {activeTab === "build" && <>
        {selectedResearchBuild && (
          <SelectedResearchBuildPanel
            build={selectedResearchBuild}
            onBack={() => switchTab("research")}
            onClear={() => setSelectedResearchBuild(null)}
          />
        )}

        {game === "poe2" ? (
          <VerbalBuildInputSection
            loading={loading}
            onSubmit={analyzeVerbalBuild}
            onCancel={cancelAnalyze}
          />
        ) : (
          <PobInputSection
            pobLink={pobLink} setPobLink={setPobLink}
            extraPobLinks={extraPobLinks} setExtraPobLinks={setExtraPobLinks}
            stageMode={stageMode} setStageMode={setStageMode}
            alSplit={alSplit} setAlSplit={setAlSplit}
            loading={loading} onAnalyze={analyzeBuild} onCancel={cancelAnalyze}
            mode={mode} setMode={setMode}
          />
        )}

      {error && (
        <div className="ui-alert ui-alert--danger" style={{ marginBottom: 12 }}>{error}</div>
      )}

      {sourceResolution && (
        <div className="ui-card--inset" style={{ marginBottom: 12 }}>
          <strong>입력 소스</strong>
          <span className="ui-text-muted" style={{ marginLeft: 8 }}>
            {sourceResolution.source_type}
          </span>
          {sourceResolution.pob_url && (
            <div className="ui-text-success" style={{ marginTop: 6, fontSize: 12 }}>
              PoB 해석 경로: {sourceResolution.pob_url}
            </div>
          )}
          {sourceResolution.passive_tree_url && (
            <div style={{ marginTop: 6, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <span className="ui-text-success" style={{ fontSize: 12 }}>
                패시브 트리 해석 경로: {sourceResolution.passive_tree_url}
              </span>
              <button
                type="button"
                className="ui-button ui-button--secondary"
                onClick={() => switchTab("passive")}
                style={{ padding: "4px 10px", fontSize: 12 }}
              >
                앱에서 패시브 보기
              </button>
            </div>
          )}
          {sourceResolution.warnings?.length > 0 && (
            <div className="ui-text-warning" style={{ marginTop: 6, fontSize: 12 }}>
              {sourceResolution.warnings.join(" ")}
            </div>
          )}
        </div>
      )}

      {quickBuild && (
        <section className="ui-card--inset" style={{ marginBottom: 12, padding: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "flex-start" }}>
            <div style={{ flex: "1 1 320px", minWidth: 240 }}>
              <div className="ui-text-info" style={{ fontSize: 12, fontWeight: 700, marginBottom: 4 }}>
                PoB 요약
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <strong style={{ fontSize: 16 }}>{quickBuild.meta?.build_name || "이름 없는 빌드"}</strong>
                {quickBuild.meta?.version && (
                  <span className="ui-badge ui-badge--info" style={{ padding: "2px 8px" }}>
                    {quickBuild.meta.version}
                  </span>
                )}
              </div>
              <div className="ui-text-muted" style={{ marginTop: 5, fontSize: 12, lineHeight: 1.5 }}>
                {[quickBuild.meta?.class, quickBuild.meta?.ascendancy].filter(Boolean).join(" / ") || "직업 정보 없음"}
                {typeof quickBuild.meta?.class_level === "number" ? ` | Lv ${quickBuild.meta.class_level}` : ""}
                {quickStage?.stage_name ? ` | ${quickStage.stage_name}` : ""}
              </div>
            </div>

            {quickMetrics.length > 0 && (
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end", flex: "1 1 260px" }}>
                {quickMetrics.map((metric) => (
                  <span key={metric.label} className={`ui-badge ${metric.tone}`} style={{ minWidth: 72, textAlign: "center" }}>
                    {metric.label} {metric.value}
                  </span>
                ))}
              </div>
            )}
          </div>

          {quickResistanceRows.length > 0 && (
            <div style={{ marginTop: 12, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
              <span className="ui-text-muted" style={{ fontSize: 12, fontWeight: 700, marginRight: 2 }}>
                저항
              </span>
              {quickResistanceRows.map((resistance) => (
                <span
                  key={resistance.key}
                  className="ui-badge"
                  style={{
                    background: resistance.value >= 75 ? "var(--status-success-bg)" : "var(--status-warning-bg)",
                    color: resistance.value >= 75 ? "var(--status-success)" : "var(--status-warning)",
                  }}
                >
                  {resistance.label} {formatPercent(resistance.value)}
                </span>
              ))}
            </div>
          )}

          {quickGemSetups.length > 0 && (
            <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid var(--border-default)" }}>
              <div className="ui-text-secondary" style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>
                메인 젬 세팅
              </div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {quickGemSetups.map((setup) => (
                  <div key={setup.label} style={{ flex: "1 1 280px", minWidth: 240 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 3 }}>{setup.label}</div>
                    <div className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.5, fontFamily: "var(--font-mono)" }}>
                      {setup.links}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {quickAlternateSetups.length > 0 && (
            <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid var(--border-default)" }}>
              <div className="ui-text-secondary" style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>
                레벨링 / 전환 젬
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
                {quickAlternateSetups.map((setup) => (
                  <div key={`${setup.label}-${setup.links}`} style={{ fontSize: 12, lineHeight: 1.5 }}>
                    <strong>{setup.label}:</strong>
                    <span className="ui-text-muted" style={{ marginLeft: 8, fontFamily: "var(--font-mono)" }}>
                      {setup.links}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {quickBeginnerChecks.length > 0 && (
            <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid var(--border-default)" }}>
              <div className="ui-text-secondary" style={{ fontSize: 12, fontWeight: 700, marginBottom: 6 }}>
                초보자 빠른 체크
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {quickBeginnerChecks.map((check) => (
                  <div
                    key={check.title}
                    style={{
                      flex: "1 1 260px",
                      minWidth: 240,
                      padding: 9,
                      borderRadius: 6,
                      border: `1px solid ${check.tone === "warning" ? "var(--status-warning)" : "var(--status-info)"}`,
                      background: check.tone === "warning" ? "var(--status-warning-bg)" : "var(--status-info-bg)",
                    }}
                  >
                    <strong style={{ fontSize: 12 }}>{check.title}</strong>
                    <div className="ui-text-muted" style={{ marginTop: 5, fontSize: 12, lineHeight: 1.5 }}>
                      {check.reason}
                    </div>
                    <div style={{ marginTop: 5, fontSize: 12, lineHeight: 1.5 }}>
                      {check.action}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(quickPassiveTreeUrl || quickStage?.bandit || quickStage?.pantheon?.major || representativeRecommendation?.selected_build_name) && (
            <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid var(--border-default)", display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              {quickPassiveTreeUrl && (
                <>
                  <button
                    type="button"
                    className="ui-button ui-button--primary"
                    onClick={() => switchTab("passive")}
                    style={{ padding: "5px 10px", fontSize: 12 }}
                  >
                    앱에서 패시브 보기
                  </button>
                  <a
                    className="ui-button ui-button--secondary"
                    href={quickPassiveTreeUrl}
                    target="_blank"
                    rel="noreferrer"
                    style={{ padding: "5px 10px", fontSize: 12, textDecoration: "none" }}
                  >
                    공식 뷰어 열기
                  </a>
                </>
              )}
              {quickStage?.bandit && (
                <span className="ui-badge ui-badge--accent">밴딧 {quickStage.bandit}</span>
              )}
              {quickStage?.pantheon?.major && (
                <span className="ui-badge ui-badge--info">
                  판테온 {quickStage.pantheon.major}{quickStage.pantheon.minor ? ` / ${quickStage.pantheon.minor}` : ""}
                </span>
              )}
              {representativeRecommendation?.selected_build_name && (
                <span className="ui-text-success" style={{ fontSize: 12 }}>
                  코퍼스 대조: {representativeRecommendation.selected_build_name}
                </span>
              )}
            </div>
          )}
        </section>
      )}

      {(corpusLoading || corpusError || corpusRecommendation) && (
        <div className="ui-card--inset" style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
            <div>
              <strong>PoB 코퍼스 대조</strong>
            </div>
            {corpusRecommendation && (
              <span className={`ui-badge ${representativeRecommendation?.selected_build_name ? "ui-badge--success" : "ui-badge--info"}`}>
                {representativeRecommendation?.selected_build_name ? "후보 매칭" : "확정 추천 없음"}
              </span>
            )}
          </div>

          {corpusLoading && (
            <div className="ui-text-muted" style={{ marginTop: 8, fontSize: 12 }}>
              대표 빌드 코퍼스 대조 중...
            </div>
          )}

          {corpusError && (
            <div className="ui-text-warning" style={{ marginTop: 8, fontSize: 12 }}>
              대표 빌드 추천 실패: {corpusError}
            </div>
          )}

          {representativeRecommendation && (
            <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 10 }}>
              <div>
                <strong>{representativeRecommendation.selected_build_name || representativeCopy.title}</strong>
                <div className="ui-text-muted" style={{ marginTop: 4, fontSize: 12, lineHeight: 1.5 }}>
                  {representativeRecommendation.selected_build_name
                    ? [
                        formatRepresentativeSkill(representativeRecommendation.selected_candidate?.main_skill),
                        formatRepresentativeClass(representativeRecommendation.selected_candidate?.class_name),
                        formatRepresentativeClass(representativeRecommendation.selected_candidate?.ascendancy),
                      ].filter(Boolean).join(" / ")
                    : representativeCopy.summary}
                </div>
              </div>

              {!representativeRecommendation.selected_build_name && representativeCopy.bullets.length > 0 && (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  {representativeCopy.bullets.slice(0, 3).map((bullet) => (
                    <div key={bullet} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.5 }}>
                      • {bullet}
                    </div>
                  ))}
                </div>
              )}

              {selectedRepresentativeProfile && representativeRecommendation.selected_build_name && (
                <div style={{ paddingTop: 10, borderTop: "1px solid var(--border-default)", display: "flex", flexDirection: "column", gap: 10 }}>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                    {selectedProfileIdentity?.patch && (
                      <span className="ui-badge ui-badge--info">출처 패치 {selectedProfileIdentity.patch}</span>
                    )}
                    {selectedProfileProgression?.leveling_confidence && (
                      <span className="ui-badge ui-badge--success">
                        레벨링 {formatRepresentativeText(selectedProfileProgression.leveling_confidence)}
                      </span>
                    )}
                    {selectedProfileConfidence?.representative_build_status && (
                      <span className="ui-badge ui-badge--accent">
                        프로필 {formatRepresentativeText(selectedProfileConfidence.representative_build_status)}
                      </span>
                    )}
                    {typeof selectedProfileConfidence?.source_count === "number" && (
                      <span className="ui-badge ui-badge--info">
                        근거 {selectedProfileConfidence.source_count}개
                      </span>
                    )}
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                    <div>
                      <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>레벨링 경로</div>
                      <div style={{ marginTop: 4, fontSize: 12, lineHeight: 1.55 }}>
                        {formatRepresentativeSkill(selectedProfileIdentity?.leveling_skill) || "스타터 미기록"}
                        {" -> "}
                        {formatRepresentativeSkill(selectedProfileIdentity?.main_skill) || representativeRecommendation.selected_build_name || "최종 미기록"}
                      </div>
                      {selectedProfileTransitions.length > 0 && (
                        <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 4 }}>
                          {selectedProfileTransitions.map((step, index) => (
                            <div key={`${step.stage}-${step.level}-${index}`} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.5 }}>
                              {formatResearchStepLabel(step)}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div>
                      <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>예산/가용성</div>
                      <div className="ui-text-muted" style={{ marginTop: 4, fontSize: 12, lineHeight: 1.55 }}>
                        초기 {formatRepresentativeCost(selectedProfileBudget?.entry_cost_divines)}
                        {" | 안정권 "}
                        {formatRepresentativeCost(selectedProfileBudget?.comfortable_cost_divines)}
                      </div>
                      <div className="ui-text-muted" style={{ marginTop: 4, fontSize: 12, lineHeight: 1.55 }}>
                        리그 스타트 {formatRepresentativeBool(selectedProfileAvailability?.league_start_viable, "가능", "불가")}
                        {" | SSF "}
                        {formatRepresentativeText(selectedProfileAvailability?.ssf_viable)}
                        {" | HC "}
                        {formatRepresentativeText(selectedProfileAvailability?.hc_viable)}
                        {" | 트윙크 "}
                        {formatRepresentativeBool(selectedProfileAvailability?.twink_required, "필요", "불필요")}
                      </div>
                    </div>
                  </div>

                  {selectedProfileCampaign.length > 0 && (
                    <div>
                      <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>캠페인/맵 단계</div>
                      <div style={{ marginTop: 5, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 8 }}>
                        {selectedProfileCampaign.map((step, index) => (
                          <div key={`${step.stage}-${step.level_range}-${index}`} style={{ fontSize: 12, lineHeight: 1.45 }}>
                            <strong>{step.stage_label || formatRepresentativeStageLabel(step.stage)}</strong>
                            <div className="ui-text-muted">
                              {step.level_range || "레벨 ?"} | {formatRepresentativeSkill(step.main_skill) || "-"}
                            </div>
                            {step.support_links && step.support_links.length > 0 && (
                              <div className="ui-text-muted">
                                {formatRepresentativeLinks(step.support_links)}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedProfilePassivePlan.length > 0 && (
                    <div>
                      <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>패시브 방향</div>
                      <div style={{ marginTop: 5, display: "flex", flexDirection: "column", gap: 4 }}>
                        {selectedProfilePassivePlan.map((step, index) => (
                          <div key={`${step.stage}-${step.level_range}-${index}`} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.5 }}>
                            {step.stage_label || formatRepresentativeStageLabel(step.stage, step.level_range)}
                            {step.level_range ? ` (${step.level_range})` : ""}
                            {step.priorities && step.priorities.length > 0 ? ` | ${step.priorities.slice(0, 4).map(formatRepresentativeText).join(" / ")}` : ""}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(selectedProfileEvidence.length > 0 || selectedProfilePainPoints.length > 0) && (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                      {selectedProfileEvidence.length > 0 && (
                        <div>
                          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>근거 링크</div>
                          <div style={{ marginTop: 5, display: "flex", flexDirection: "column", gap: 4 }}>
                            {selectedProfileEvidence.map((entry, index) => (
                              <div key={`${entry.url || entry.label}-${index}`} style={{ fontSize: 12, lineHeight: 1.45 }}>
                                {entry.url ? (
                                  <a href={entry.url} target="_blank" rel="noreferrer" style={{ color: "var(--status-info)", textDecoration: "none" }}>
                                    {entry.label || entry.url}
                                  </a>
                                ) : (
                                  <span>{entry.label}</span>
                                )}
                                {entry.type && <span className="ui-text-muted"> | {sourceKindText(entry.type)}</span>}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {selectedProfilePainPoints.length > 0 && (
                        <div>
                          <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>주의점</div>
                          <div style={{ marginTop: 5, display: "flex", flexDirection: "column", gap: 4 }}>
                            {selectedProfilePainPoints.map((point) => (
                              <div key={point} className="ui-text-muted" style={{ fontSize: 12, lineHeight: 1.45 }}>
                                {point}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {representativeTopCandidates.length > 0 && (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>
                    비슷한 후보
                  </div>
                  {representativeTopCandidates.map((candidate) => (
                    <div
                      key={candidate.build_id || candidate.candidate_id || candidate.build_name}
                      className="ui-card--inset"
                      style={{ padding: 8 }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                        <strong style={{ fontSize: 13 }}>
                          {candidate.build_name || formatRepresentativeSkill(candidate.main_skill) || "이름 미기록"}
                        </strong>
                      </div>
                      <div className="ui-text-muted" style={{ marginTop: 4, fontSize: 12, lineHeight: 1.5 }}>
                        {formatRepresentativeSkill(candidate.main_skill) || "스킬 미기록"}
                        {candidate.class_name ? ` / ${formatRepresentativeClass(candidate.class_name)}` : ""}
                        {candidate.ascendancy ? ` ${formatRepresentativeClass(candidate.ascendancy)}` : ""}
                        {candidate.profile_summary?.progression?.leveling_confidence
                          ? ` | 레벨링 ${formatRepresentativeText(candidate.profile_summary.progression.leveling_confidence)}`
                          : ""}
                        {typeof candidate.profile_summary?.confidence?.source_count === "number"
                          ? ` | 근거 ${candidate.profile_summary.confidence.source_count}개`
                          : ""}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {representativeProxyCandidates.length > 0 && !representativeRecommendation.selected_build_name && (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <div className="ui-text-muted" style={{ fontSize: 12, fontWeight: 600 }}>
                    대체 후보
                  </div>
                  {representativeProxyCandidates.map((candidate) => (
                    <div key={candidate.build_id || candidate.candidate_id || candidate.build_name} style={{ fontSize: 12 }}>
                      {candidate.build_name || formatRepresentativeSkill(candidate.main_skill) || "이름 미기록"}
                      {candidate.profile_summary?.progression?.leveling_confidence
                        ? ` | 레벨링 ${formatRepresentativeText(candidate.profile_summary.progression.leveling_confidence)}`
                        : ""}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {!buildData && !coaching && activePassiveTreeUrl && (
        <PassiveTreeView
          url={activePassiveTreeUrl}
          representativeProfile={selectedRepresentativeProfile}
          buildClassName={quickBuild?.meta?.class}
          buildAscendancyName={quickBuild?.meta?.ascendancy}
        />
      )}

      {coaching && isCoachBlocked(coaching) ? (
        <CoachBlockedBanner
          droppedEntries={(coaching._normalization_trace ?? []).filter(
            (t) => t.match_type === "dropped",
          )}
          onReanalyze={analyzeBuild}
          analyzing={loading !== ""}
        />
      ) : (
        <>
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

                <NewPlayerBridgeSection bridge={coaching.new_player_bridge} />

                <BuildRatingSection rating={coaching.build_rating} />
                <VariantTabs snapshots={coaching.variant_snapshots} />

                <LevelingGuideSection
                  guide={coaching.leveling_guide}
                  representativeProfile={selectedRepresentativeProfile}
                />
                <LevelingSkillsSection
                  skills={coaching.leveling_skills}
                  representativeProfile={selectedRepresentativeProfile}
                />

                <AuraUtilitySection progression={coaching.aura_utility_progression} />

                <GearTimeline progression={coaching.gear_progression} />

                {/* 핵심 장비 폴백: gear_progression 비면 key_items로 대체 */}
                {(!coaching.gear_progression || coaching.gear_progression.length === 0) && (
                  <KeyItemsSection items={coaching.key_items} />
                )}

                <PassivePrioritySection
                  priorities={coaching.passive_priority}
                  representativeProfile={selectedRepresentativeProfile}
                />

                <MapWarnings warnings={coaching.map_mod_warnings} />

                <DangerZonesSection zones={coaching.danger_zones} />

                <FarmingStrategySection
                  strategy={coaching.farming_strategy}
                  representativeProfile={selectedRepresentativeProfile}
                />

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
        </>
      )}
      </>}
      </main>
    </div>
  );
}

export default App;
