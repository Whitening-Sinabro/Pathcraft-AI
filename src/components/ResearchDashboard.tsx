import { useEffect, useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";

interface LuminaryHypothesis {
  hypothesis_id: string;
  label: string;
  player_role: string;
  mercenary_role: string;
  risk: string;
}

interface LuminaryTask {
  task_id: string;
  required_input: string;
  output: string;
}

interface LuminaryIntake {
  link_skill_hypotheses: LuminaryHypothesis[];
  live_validation_tasks: LuminaryTask[];
  item_watchlist: Array<{ item_name: string }>;
  practice_judgement: {
    player_facing_label: string;
    reason: string;
  };
}

interface ReuseTrack {
  track_id: string;
  label: string;
  judgement: string;
  why?: string;
  check?: string;
  applies_to?: string[];
  practice_focus?: string[];
}

interface CorpusReuseReview {
  category_matrix: Array<{
    category_id: string;
    tracks: ReuseTrack[];
  }>;
}

interface WatchlistSource {
  source_id?: string;
  label?: string;
  url?: string | null;
  family?: string;
}

interface WatchlistPracticeStage {
  stage: string;
  goal?: string;
  source_note?: string;
  pob_url?: string | null;
  source_links?: WatchlistSource[];
  skill_setups?: string[];
  checks?: string[];
}

interface WatchlistMapModGroup {
  severity: string;
  label: string;
  mods: string[];
}

interface WatchlistCard {
  candidate_id: string;
  display_name: string;
  patch?: string;
  main_skill?: string;
  class_name?: string;
  ascendancy?: string;
  lane_label?: string;
  player_label: string;
  reason: string;
  tags?: string[];
  source_count?: number;
  sources?: WatchlistSource[];
  pob_urls?: string[];
  playstyle_summary?: string[];
  mirage_notes?: string[];
  anytime_upgrades?: Array<{ node_id: string; label: string; note?: string }>;
  additional_pob_urls?: string[];
  practice_route?: WatchlistPracticeStage[];
  map_mods_to_avoid?: WatchlistMapModGroup[];
  upgrade_notes?: string[];
  red_flags?: string[];
  promotion_checks?: string[];
  next_actions?: string[];
}

interface WatchlistCandidateCardsPayload {
  summary: {
    card_count: number;
  };
  cards: WatchlistCard[];
}

const CWS_RESEARCH_CARD_ID = "3.29_cws_chieftain_emiracle_watch";

const FALLBACK_LUMINARY_INTAKE: LuminaryIntake = {
  practice_judgement: {
    player_facing_label: "검증 필요",
    reason: "리서치 데이터가 완전히 로드되지 않아 기본 검증 항목만 표시합니다.",
  },
  link_skill_hypotheses: [],
  live_validation_tasks: [],
  item_watchlist: [],
};

interface BuildIdentity {
  build_name?: string;
  patch?: string;
  class_name?: string;
  ascendancy?: string;
  main_skill?: string;
  leveling_skill?: string;
  damage_tags?: string[];
}

interface BudgetCurve {
  entry_cost_divines?: number;
  comfortable_cost_divines?: number;
  aspirational_cost_divines?: number;
}

interface Availability {
  league_start_viable?: boolean;
  ssf_viable?: string;
  hc_viable?: string;
  twink_required?: boolean;
  mandatory_uniques?: string[];
  mandatory_transfigured_gems?: string[];
}

interface Playstyle {
  input_style?: string;
  manual_buttons?: number;
  movement_dependence?: string;
  aim_requirement?: string;
  notes?: string;
}

interface TransitionPoint {
  stage?: string;
  level?: number;
  main_skill?: string;
  from_skill?: string;
  to_skill?: string;
  required_links?: number;
  required_item?: string | null;
  trigger?: string;
}

interface CampaignStep {
  stage?: string;
  stage_label?: string;
  level_range?: string;
  main_skill?: string;
  support_links?: string[];
  auras?: string[];
  utility?: string[];
  guard?: string[];
  notes?: string;
}

interface PassiveStep {
  stage?: string;
  stage_label?: string;
  level_range?: string;
  priorities?: string[];
  notes?: string;
}

interface Progression {
  leveling_confidence?: string;
  early_mapping_ready?: boolean;
  transition_points?: TransitionPoint[];
  campaign_plan?: CampaignStep[];
  passive_plan?: PassiveStep[];
}

interface Suitability {
  mapping?: number;
  bossing?: number;
  sanctum?: number;
  heist?: number;
  expedition?: number;
}

interface BuildConfidence {
  representative_build_status?: string;
  source_count?: number;
  notes?: string;
}

interface BuildEvidence {
  type?: string;
  label?: string;
  url?: string | null;
  notes?: string;
}

interface BuildConstraints {
  pain_points?: string[];
}

interface RepresentativeBuildProfile {
  build_id?: string;
  identity: BuildIdentity;
  budget_curve?: BudgetCurve;
  availability?: Availability;
  playstyle?: Playstyle;
  progression?: Progression;
  suitability?: Suitability;
  confidence?: BuildConfidence;
  evidence?: BuildEvidence[];
  constraints?: BuildConstraints;
}

interface RepresentativeProfileRow {
  candidate_id: string;
  league_name?: string;
  board_status?: string;
  source_confidence?: string;
  build_profile: RepresentativeBuildProfile;
}

interface RepresentativeProfilesPayload {
  summary: {
    profile_count: number;
    confirmed: number;
    near_confirmed: number;
    hold: number;
  };
  profiles: RepresentativeProfileRow[];
}

interface ResearchPayload {
  dataset_kind: "poe1_research_dashboard_payload";
  representative_profiles: RepresentativeProfilesPayload;
  watchlist_candidate_cards?: WatchlistCandidateCardsPayload;
  luminary_intake: LuminaryIntake;
  corpus_reuse_review: CorpusReuseReview;
  live_validation_queue: unknown;
}

function makeFallbackResearchPayload(): ResearchPayload {
  return {
    dataset_kind: "poe1_research_dashboard_payload",
    representative_profiles: {
      summary: {
        profile_count: 0,
        confirmed: 0,
        near_confirmed: 0,
        hold: 0,
      },
      profiles: [],
    },
    watchlist_candidate_cards: {
      summary: {
        card_count: 0,
      },
      cards: [],
    },
    luminary_intake: FALLBACK_LUMINARY_INTAKE,
    corpus_reuse_review: {
      category_matrix: [],
    },
    live_validation_queue: null,
  };
}

function normalizeResearchPayload(raw: unknown): ResearchPayload {
  const fallback = makeFallbackResearchPayload();
  if (!raw || typeof raw !== "object") return fallback;

  const input = raw as Partial<ResearchPayload>;
  const profiles = Array.isArray(input.representative_profiles?.profiles)
    ? input.representative_profiles.profiles
    : [];
  const representative_profiles: RepresentativeProfilesPayload = {
    summary: {
      profile_count: input.representative_profiles?.summary?.profile_count ?? profiles.length,
      confirmed: input.representative_profiles?.summary?.confirmed ?? 0,
      near_confirmed: input.representative_profiles?.summary?.near_confirmed ?? 0,
      hold: input.representative_profiles?.summary?.hold ?? 0,
    },
    profiles,
  };

  const loadedCards = Array.isArray(input.watchlist_candidate_cards?.cards)
    ? input.watchlist_candidate_cards.cards
    : [];
  const cards = loadedCards;
  const watchlist_candidate_cards: WatchlistCandidateCardsPayload = {
    summary: {
      card_count: input.watchlist_candidate_cards?.summary?.card_count ?? cards.length,
    },
    cards,
  };

  return {
    dataset_kind: "poe1_research_dashboard_payload",
    representative_profiles,
    watchlist_candidate_cards,
    luminary_intake: input.luminary_intake ?? FALLBACK_LUMINARY_INTAKE,
    corpus_reuse_review: input.corpus_reuse_review ?? fallback.corpus_reuse_review,
    live_validation_queue: input.live_validation_queue ?? null,
  };
}

export interface ResearchBuildSelection {
  id: string;
  category: "leveling" | "endgame" | "all_in_one";
  categoryLabel: string;
  title: string;
  originalName: string;
  judgement: string;
  reason: string;
  patch?: string;
  className?: string;
  ascendancy?: string;
  mainSkill?: string;
  levelingSkill?: string;
  routeLabel: string;
  tags: string[];
  budget: {
    entry?: number;
    comfortable?: number;
    aspirational?: number;
  };
  availability: {
    leagueStart?: boolean;
    ssf?: string;
    hc?: string;
    twink?: boolean;
  };
  scores: {
    mapping?: number;
    bossing?: number;
  };
  transitions: TransitionPoint[];
  campaignPlan: CampaignStep[];
  passivePlan: PassiveStep[];
  evidence: BuildEvidence[];
  painPoints: string[];
}

interface ResearchBuildCard {
  id: string;
  title: string;
  subtitle: string;
  judgement: string;
  reason: string;
  chips: string[];
  scoreText: string;
  detail: ResearchBuildSelection;
}

interface BuildCategory {
  id: ResearchBuildSelection["category"];
  title: string;
  subtitle: string;
  cards: ResearchBuildCard[];
}

interface Props {
  onSelectBuild?: (build: ResearchBuildSelection) => void;
  selectedBuildId?: string;
}

const JUDGEMENT_CLASS: Record<string, string> = {
  "가능성 높음": "ui-badge--success",
  "연습해도 됨": "ui-badge--info",
  "손봐야 가능": "ui-badge--accent",
  "구경만": "ui-badge--info",
  "위험 신호": "ui-badge--accent",
};

const CLASS_KO: Record<string, string> = {
  Marauder: "머라우더",
  Duelist: "듀얼리스트",
  Ranger: "레인저",
  Shadow: "쉐도우",
  Witch: "위치",
  Templar: "템플러",
  Scion: "사이온",
};

const ASCENDANCY_KO: Record<string, string> = {
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
  Chieftain: "치프틴",
  Necromancer: "네크로맨서",
  Reliquarian: "렐리쿼리언",
  Luminary: "루미너리",
};

const SKILL_KO: Record<string, string> = {
  Boneshatter: "뼈박살",
  "Ground Slam": "대지 강타",
  "Corrupting Fever": "타락한 열병",
  "Splitting Steel": "분열 강철",
  "Lightning Arrow": "번개 화살",
  "Rain of Arrows": "화살비",
  "Split Arrow": "분할 화살",
  "Caustic Arrow": "부식성 화살",
  "Ice Shot": "얼음 화살",
  "Toxic Rain": "맹독성 비",
  "Shockwave Totem": "충격파 토템",
  "Holy Flame Totem": "신성한 화염 토템",
  "Hexblast Mine": "사술 폭발 마인",
  "Stormblast Mine": "폭풍 점사 마인",
  "Detonate Dead": "시체 폭발",
  "Explosive Arrow Ballista": "폭발 화살 쇠뇌",
  "Exsanguinate Mine": "출혈 마인",
  "Reap": "수확",
  Lacerate: "찢기",
  "Lightning Strike": "번개 타격",
  "Ball Lightning": "구형 번개",
  "Ice Nova": "얼음 폭발",
  Frostbolt: "서리 구체",
  "Freezing Pulse": "동결 파동",
  Arc: "연쇄 번개",
  "Storm Brand": "폭풍 낙인",
  "Rolling Magma": "용암 구체",
  "Siege Ballista": "공성 쇠뇌",
  "Shrapnel Ballista": "파편 쇠뇌",
  "Dominating Blow": "지배의 일격",
  "Summon Holy Relic": "성스러운 유물 소환",
  "Power Siphon": "권능 착취",
  Cleave: "가르기",
  "Pyroclast Mine": "화염질주 마인",
  "Cold Snap of Power": "권능의 한파",
  "Kinetic Fusillade of Detonation": "폭발의 동력 탄막",
  "Penance Brand": "속죄의 낙인",
  "Shock Nova of Procession": "행렬의 충격 폭발",
  "Exsanguinate Mines": "방혈 마인",
  "Summon Carrion Golem": "부패 골렘 소환",
  "Cast When Stunned": "기절 시 시전",
  "Righteous Fire": "정의의 화염",
  "Vaal Cold Snap": "바알 한파",
  Sunder: "대지 가르기",
  "Herald of Thunder": "천둥의 전령",
  "Blight of Contagion": "전염의 역병",
  "Static Strike": "정전기 타격",
  "Kinetic Blast": "동력 폭발",
  "Link Skill": "링크 스킬",
};

const COMMON_TEXT_KO: Record<string, string> = {
  Campaign: "캠페인",
  "Campaign Start": "캠페인 시작",
  "Maps Entry": "맵 진입",
  "High End": "고점 세팅",
  "early_maps": "초기 맵",
  "late_endgame": "고점 세팅",
  confirmed: "확인됨",
  near_confirmed: "준확인",
  hold: "보류",
  high: "높음",
  medium: "보통",
  low: "낮음",
  physical: "물리",
  chaos: "카오스",
  fire: "화염",
  cold: "냉기",
  lightning: "번개",
  attack: "공격",
  spell: "주문",
  minion: "소환수",
  mine: "마인",
  totem: "토템",
  projectile: "투사체",
  bow: "활",
  ailment: "상태 이상",
  "1_button": "1버튼",
  "2_button": "2버튼",
  "3_button": "3버튼",
  "needs_patch_verification": "패치 재검증 필요",
  "provisional_seeded": "임시 근거",
  "strict_two_source_pass": "두 개 이상 근거 통과",
  "single_external_family_only": "외부 빌드 계열 1개만 확인",
  "missing_second_external_build_guide": "두 번째 외부 가이드 필요",
  "single_source_only": "단일 소스",
};

function koClass(value?: string) {
  return value ? CLASS_KO[value] || value : "";
}

function koAscendancy(value?: string) {
  return value ? ASCENDANCY_KO[value] || value : "";
}

function koSkill(value?: string) {
  return value ? SKILL_KO[value] || value : "";
}

function koValue(value?: string) {
  if (!value) return "-";
  return COMMON_TEXT_KO[value] || value.replace(/_/g, " ");
}

function koText(value?: string) {
  if (!value) return "";
  return value
    .replace(/No Bloodnotch Swap/g, "No Bloodnotch 전환")
    .replace(/Bloodnotch Initial Swap/g, "Bloodnotch 초기 전환")
    .replace(/Midgame 1 - Nebulis/g, "중반 1 - Nebulis")
    .replace(/Midgame 2 - Initial Large Cluster/g, "중반 2 - 첫 Large Cluster")
    .replace(/Midgame 3 - Triple Large Cluster/g, "중반 3 - Triple Large Cluster")
    .replace(/Midgame 4 - Prism Guardian Malevolence Aura/g, "중반 4 - Prism Guardian Malevolence 오라")
    .replace(/Midgame 5 - Unearth\/DD/g, "중반 5 - Unearth/DD")
    .replace(/Ultra Aspirational - Hybrid Mageblood\/Imbue/g, "초고투자 - Hybrid Mageblood/Imbue")
    .replace(/Mobalytics guide/g, "Mobalytics 가이드")
    .replace(/Mobalytics body lists/g, "Mobalytics 본문 기준")
    .replace(/emiracles guide/g, "emiracles 가이드")
    .replace(/Practice note/g, "연습 메모")
    .replace(/keep RF leveling until roughly 78-87 depending on gear, then test No Bloodnotch CWS/g, "장비 상태에 따라 대략 78-87까지 RF로 진행한 뒤 No Bloodnotch CWS 전환을 테스트")
    .replace(/Recommend 87\+ for swap/g, "전환 권장 레벨 87+")
    .replace(/Pohx RF recommended/g, "Pohx RF 권장")
    .replace(/Experienced players may use Sunder until RF swap/g, "숙련자는 RF 전환 전까지 Sunder 사용 가능")
    .replace(/Pohx RF campaign and early-map setup/g, "Pohx RF 캠페인 및 초반 맵 세팅")
    .replace(/Experienced option from emiracles: Sunder until level 19 RF swap or around 55 swap/g, "emiracles 숙련자 옵션: 19레벨 RF 전환 또는 55 전후 전환까지 Sunder 사용")
    .replace(/Punishment - Cast when Stunned - Purifying Flame - Flame Surge - Cold Snap/g, "Punishment - Cast when Stunned - Purifying Flame - Flame Surge - Cold Snap")
    .replace(/Detonate Dead of Scavenging - Cast when Stunned - Burning Damage - Deadly Ailments/g, "Detonate Dead of Scavenging - Cast when Stunned - Burning Damage - Deadly Ailments")
    .replace(/Malevolence - Eternal Blessing outside Prism Guardian/g, "Malevolence - Eternal Blessing은 Prism Guardian 밖에 연결")
    .replace(/Detonate Dead, not Detonate Dead of Scavenging/g, "Detonate Dead 사용, Detonate Dead of Scavenging 금지")
    .replace(/Do not enable stun immunity sources/g, "스턴 면역 요소를 켜지 않음")
    .replace(/Optional degen bandaid: Brink of Death/g, "지속 피해로 생명이 빠지면 임시 보정: Brink of Death")
    .replace(/avoid ignite/g, "점화 회피")
    .replace(/less effect of curses on monsters/g, "몬스터에게 적용되는 저주 효과 감소")
    .replace(/- maximum resistances/g, "최대 저항 감소")
    .replace(/less recovery rate of Life and ES/g, "생명력/에너지 보호막 회복 속도 감소")
    .replace(/less area of effect/g, "효과 범위 감소")
    .replace(/cannot regenerate life\/mana\/es/g, "생명력/마나/에너지 보호막 재생 불가")
    .replace(/steal endurance charges/g, "인내 충전 강탈")
    .replace(/less flask charges/g, "플라스크 충전 획득 감소")
    .replace(/monster impale on hit/g, "몬스터 명중 시 꿰뚫기")
    .replace(/critical strike multiplier/g, "치명타 피해 배율")
    .replace(/less flask effect/g, "플라스크 효과 감소")
    .replace(/Searing Exarch runes/g, "작열의 총주교 룬")
    .replace(/Drowning orbs/g, "익사 오브")
    .replace(/gain as random extra element/g, "무작위 원소 추가 피해 획득")
    .replace(/monster remove % Life on hit before Defiance/g, "Defiance 전 몬스터 명중 시 생명력 % 제거")
    .replace(/Campaign, act-to-map, league-start, and From Zero to Hero route extraction\./g, "캠페인, 액트-맵 진입, 리그 스타트, 제로투히어로 루트를 수집합니다.")
    .replace(/Early maps through voidstones and normal endgame build state extraction\./g, "초기 맵부터 보이드스톤까지의 일반 엔드게임 빌드 상태를 수집합니다.")
    .replace(/Expensive scaling, min-max, mirror-tier, high-APM, and late reroll research\./g, "고비용 스케일링, 극한 최적화, 미러급 세팅, 고조작 빌드, 후반 리롤을 조사합니다.")
    .replace(/Atlas, economy, heist, mapping, and strategy-per-hour source collection\./g, "아틀라스, 경제, 강탈, 맵핑, 시간당 수익 전략 소스를 모읍니다.")
    .replace(/HC\/SSF\/gauntlet survivability and defensive baseline cross-checks\./g, "하드코어, SSF, 건틀릿 생존성과 방어 기준선을 대조합니다.")
    .replace(/Minion, Spectre, SRS, Golem, and Animate Guardian source collection\./g, "소환수, 스펙터, SRS, 골렘, 수호자 기동 소스를 수집합니다.")
    .replace(/Exsanguinate\/Reap\/Pyroclast\/Hexblast mine source separation\./g, "출혈/수확/화염질주/사술 폭발 마인 소스를 분리해서 봅니다.")
    .replace(/Self-cast, Archmage, Spark, Cold DoT, Brand, and spell transition extraction\./g, "셀프캐스트, 아크메이지, 스파크, 냉기 지속 피해, 낙인, 주문 전환 루트를 뽑습니다.")
    .replace(/Bow, projectile, Deadeye, Pathfinder, Venom Gyre and mapping route extraction\./g, "활, 투사체, 데드아이, 패스파인더, 맹독성 선회, 맵핑 루트를 봅니다.")
    .replace(/Melee starter, Slayer, Gladiator, Shield Crush, Cyclone, Slam and weapon cadence research\./g, "근접 스타터, 슬레이어, 글래디에이터, 방패 쇄도, 회오리바람, 강타, 무기 교체 흐름을 봅니다.")
    .replace(/Spell\/Ballista\/Flamewood\/Totem leveling and post-3\.29 nerf check targets\./g, "주문/쇠뇌/화염나무/토템 레벨링과 3.29 이후 너프 확인 대상을 봅니다.")
    .replace(/Ascendant\/Reliquarian\/Luminary split and 3\.29 shell tracking\./g, "어센던트, 리리쿼리언, 루미너리 분기와 3.29 빌드 틀을 추적합니다.")
    .replace(/Campaign Start/g, "캠페인 시작")
    .replace(/Maps Entry/g, "맵 진입")
    .replace(/High End/g, "고점 세팅")
    .replace(/Transition from/g, "전환:")
    .replace(/into/g, "->")
    .replace(/Representative board verified guide family\./g, "대표 보드에서 확인한 가이드 계열")
    .replace(/guide family/g, "가이드 계열")
    .replace(/source/g, "소스")
    .replace(/leveling/g, "레벨링")
    .replace(/endgame/g, "엔드게임")
    .replace(/mapping/g, "맵핑")
    .replace(/starter/g, "스타터")
    .replace(/budget/g, "저예산")
    .replace(/high_end/g, "고점")
    .replace(/package/g, "묶음")
    .replace(/clusters/g, "클러스터")
    .replace(/campaign/g, "캠페인");
}

function judgementClass(label?: string) {
  return label ? JUDGEMENT_CLASS[label] || "ui-badge--info" : "ui-badge--info";
}

function formatCost(value?: number) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "-";
  if (value < 1) return `${value}딥 이하`;
  return `${value}딥`;
}

function scoreLabel(mapping?: number, bossing?: number) {
  const parts = [];
  if (typeof mapping === "number") parts.push(`맵핑 ${mapping}`);
  if (typeof bossing === "number") parts.push(`보스 ${bossing}`);
  return parts.join(" / ") || "점수 미기록";
}

function buildTitle(identity: BuildIdentity) {
  const main = koSkill(identity.main_skill);
  const asc = koAscendancy(identity.ascendancy);
  return [main, asc].filter(Boolean).join(" ");
}

function routeLabel(identity: BuildIdentity) {
  const from = koSkill(identity.leveling_skill);
  const to = koSkill(identity.main_skill);
  if (from && to && from !== to) return `${from} -> ${to}`;
  return to || from || "경로 미기록";
}

function playerLabel(row: RepresentativeProfileRow, category: ResearchBuildSelection["category"]) {
  const patch = row.build_profile.identity.patch || "";
  const status = row.board_status || row.build_profile.confidence?.representative_build_status || "";
  if (status === "hold") return "구경만";
  if (patch && !patch.startsWith("3.29")) return "연습해도 됨";
  if (patch.startsWith("3.27") && category !== "leveling") return "연습해도 됨";
  if (status === "confirmed") return "가능성 높음";
  if (status === "near_confirmed") return "연습해도 됨";
  return "손봐야 가능";
}

function reasonFor(row: RepresentativeProfileRow, category: ResearchBuildSelection["category"]) {
  const profile = row.build_profile;
  const identity = profile.identity;
  const mapping = profile.suitability?.mapping;
  const bossing = profile.suitability?.bossing;
  const sourcePatch = identity.patch ? `${identity.patch} 출처 기준` : "과거 출처 기준";
  const patchCaveat = identity.patch?.startsWith("3.29") ? "" : " 3.29 최종 PoB 확인 전까지는 연습 후보로 봅니다.";
  if (category === "leveling") {
    return `${sourcePatch} ${routeLabel(identity)} 경로가 있고 레벨링 근거가 ${koValue(profile.progression?.leveling_confidence)} 상태입니다.${patchCaveat}`;
  }
  if (category === "endgame") {
    return `${sourcePatch} 엔드게임 지표는 ${scoreLabel(mapping, bossing)}입니다.${patchCaveat}`;
  }
  return `${sourcePatch} 리그 시작과 맵 진입 흐름이 같이 잡힌 후보입니다. ${routeLabel(identity)} 전환을 확인합니다.${patchCaveat}`;
}

function toSelection(row: RepresentativeProfileRow, category: ResearchBuildSelection["category"], categoryLabel: string): ResearchBuildSelection {
  const profile = row.build_profile;
  const identity = profile.identity;
  const title = buildTitle(identity) || identity.build_name || row.candidate_id;
  return {
    id: `${category}:${row.candidate_id}`,
    category,
    categoryLabel,
    title,
    originalName: identity.build_name || row.candidate_id,
    judgement: playerLabel(row, category),
    reason: reasonFor(row, category),
    patch: identity.patch,
    className: koClass(identity.class_name),
    ascendancy: koAscendancy(identity.ascendancy),
    mainSkill: koSkill(identity.main_skill),
    levelingSkill: koSkill(identity.leveling_skill),
    routeLabel: routeLabel(identity),
    tags: [
      ...(identity.damage_tags || []).map(koText),
      profile.playstyle?.input_style ? koText(profile.playstyle.input_style) : "",
      profile.availability?.league_start_viable ? "리그 스타트" : "",
      profile.progression?.early_mapping_ready ? "맵 진입 가능" : "",
    ].filter(Boolean).slice(0, 6),
    budget: {
      entry: profile.budget_curve?.entry_cost_divines,
      comfortable: profile.budget_curve?.comfortable_cost_divines,
      aspirational: profile.budget_curve?.aspirational_cost_divines,
    },
    availability: {
      leagueStart: profile.availability?.league_start_viable,
      ssf: koValue(profile.availability?.ssf_viable),
      hc: koValue(profile.availability?.hc_viable),
      twink: profile.availability?.twink_required,
    },
    scores: {
      mapping: profile.suitability?.mapping,
      bossing: profile.suitability?.bossing,
    },
    transitions: profile.progression?.transition_points || [],
    campaignPlan: profile.progression?.campaign_plan || [],
    passivePlan: profile.progression?.passive_plan || [],
    evidence: profile.evidence || [],
    painPoints: (profile.constraints?.pain_points || []).map(koValue),
  };
}

function toCard(row: RepresentativeProfileRow, category: ResearchBuildSelection["category"], categoryLabel: string): ResearchBuildCard {
  const detail = toSelection(row, category, categoryLabel);
  return {
    id: detail.id,
    title: detail.title,
    subtitle: [
      detail.className,
      detail.ascendancy,
      detail.patch ? `${detail.patch} 출처` : "",
    ].filter(Boolean).join(" / "),
    judgement: detail.judgement,
    reason: detail.reason,
    chips: [
      detail.routeLabel,
      `진입 ${formatCost(detail.budget.entry)}`,
      `SSF ${detail.availability.ssf || "-"}`,
      `HC ${detail.availability.hc || "-"}`,
    ],
    scoreText: scoreLabel(detail.scores.mapping, detail.scores.bossing),
    detail,
  };
}

function watchlistToSelection(card: WatchlistCard): ResearchBuildSelection {
  const routeStages = card.practice_route || [];
  const mapModWarnings = (card.map_mods_to_avoid || []).flatMap((group) =>
    group.mods.map((mod) => `${group.label}: ${mod}`),
  );

  return {
    id: `watchlist:${card.candidate_id}`,
    category: "all_in_one",
    categoryLabel: card.candidate_id === CWS_RESEARCH_CARD_ID ? "CWS 리서치" : "검토 후보",
    title: koSkill(card.display_name) || card.display_name,
    originalName: card.display_name,
    judgement: card.player_label,
    reason: koText(card.reason),
    patch: card.patch,
    className: koClass(card.class_name),
    ascendancy: koAscendancy(card.ascendancy),
    mainSkill: koSkill(card.main_skill),
    levelingSkill: routeStages.length > 0 ? "RF/Fire Trap 연습 루트" : undefined,
    routeLabel: routeStages.length > 0 ? routeStages.map((stage) => stage.stage).join(" -> ") : card.lane_label || "검토 경로",
    tags: (card.tags || []).map(koValue).filter(Boolean).slice(0, 6),
    budget: {},
    availability: {
      leagueStart: card.candidate_id === CWS_RESEARCH_CARD_ID ? false : undefined,
      ssf: card.candidate_id === CWS_RESEARCH_CARD_ID ? "연습용" : undefined,
      hc: card.candidate_id === CWS_RESEARCH_CARD_ID ? "SSF 검증 후" : undefined,
      twink: false,
    },
    scores: {},
    transitions: routeStages.map((stage, index) => ({
      stage: stage.stage,
      level: undefined,
      main_skill: card.main_skill,
      from_skill: index === 0 ? "RF/Fire Trap" : routeStages[index - 1]?.stage,
      to_skill: stage.stage,
      trigger: stage.goal,
    })),
    campaignPlan: routeStages.map((stage) => ({
      stage: stage.stage,
      stage_label: stage.stage,
      main_skill: card.main_skill,
      support_links: stage.skill_setups,
      notes: [stage.goal, ...(stage.checks || [])].filter(Boolean).join(" / "),
    })),
    passivePlan: [],
    evidence: [
      ...(card.sources || [])
        .filter((source) => source.url)
        .map((source) => ({
          type: source.family || "source",
          label: sourceLabel(source),
          url: source.url,
        })),
      ...routeStages
        .filter((stage) => stage.pob_url)
        .map((stage) => ({
          type: "practice_route_pob",
          label: stage.stage,
          url: stage.pob_url,
          notes: stage.source_note,
        })),
      ...(card.pob_urls || []).slice(0, 8).map((url, index) => ({
        type: index === 0 ? "leveling_pob" : "pob",
        label: `PoB ${index + 1}`,
        url,
      })),
    ],
    painPoints: [
      ...(card.red_flags || []),
      ...(card.promotion_checks || []),
      ...(card.upgrade_notes || []).slice(0, 4),
      ...mapModWarnings.slice(0, 8),
    ].map(koText),
  };
}

function sortByStarterQuality(a: RepresentativeProfileRow, b: RepresentativeProfileRow) {
  const ap = a.build_profile;
  const bp = b.build_profile;
  const score = (profile: RepresentativeBuildProfile, row: RepresentativeProfileRow) =>
    (row.board_status === "confirmed" ? 60 : row.board_status === "near_confirmed" ? 40 : 10)
    + (profile.availability?.league_start_viable ? 30 : 0)
    + (profile.progression?.early_mapping_ready ? 20 : 0)
    + (profile.progression?.leveling_confidence === "confirmed" ? 20 : profile.progression?.leveling_confidence === "near_confirmed" ? 12 : 0)
    - (profile.availability?.twink_required ? 15 : 0)
    - Math.max(0, (profile.budget_curve?.entry_cost_divines || 0) - 1) * 5;
  return score(bp, b) - score(ap, a);
}

function sortByEndgamePower(a: RepresentativeProfileRow, b: RepresentativeProfileRow) {
  const score = (row: RepresentativeProfileRow) => {
    const p = row.build_profile;
    return (p.suitability?.mapping || 0) + (p.suitability?.bossing || 0) + (row.board_status === "confirmed" ? 20 : 0);
  };
  return score(b) - score(a);
}

function uniqueByBuildName(rows: RepresentativeProfileRow[]) {
  const seen = new Set<string>();
  return rows.filter((row) => {
    const identity = row.build_profile.identity;
    const key = `${identity.build_name || identity.main_skill}:${identity.ascendancy}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function buildCategories(profiles: RepresentativeProfileRow[]): BuildCategory[] {
  const usable = profiles.filter((row) => row.board_status !== "hold");
  const leveling = uniqueByBuildName(
    usable
      .filter((row) => row.build_profile.progression?.leveling_confidence !== "inferred")
      .sort(sortByStarterQuality),
  ).slice(0, 6);
  const endgame = uniqueByBuildName([...usable].sort(sortByEndgamePower)).slice(0, 6);
  const allInOne = uniqueByBuildName(
    usable
      .filter((row) =>
        row.build_profile.availability?.league_start_viable
        && row.build_profile.progression?.early_mapping_ready
        && (row.build_profile.budget_curve?.entry_cost_divines || 99) <= 2
        && (row.build_profile.progression?.transition_points?.length || 0) > 0,
      )
      .sort(sortByStarterQuality),
  );
  const allInOneCards = (allInOne.length > 0 ? allInOne : leveling).slice(0, 6);

  return [
    {
      id: "leveling",
      title: "레벨링 카테고리",
      subtitle: "액트 시작, 초반 맵 진입, 손 연습 가치가 높은 후보",
      cards: leveling.map((row) => toCard(row, "leveling", "레벨링")),
    },
    {
      id: "endgame",
      title: "엔드게임 카테고리",
      subtitle: "맵핑, 보스, 고점 세팅 기준으로 다시 볼 후보",
      cards: endgame.map((row) => toCard(row, "endgame", "엔드게임")),
    },
    {
      id: "all_in_one",
      title: "레벨링 -> 엔드게임 한방 카테고리",
      subtitle: "스타터부터 맵 진입과 최종 전환까지 한 흐름으로 볼 후보",
      cards: allInOneCards.map((row) => toCard(row, "all_in_one", "레벨링 -> 엔드게임")),
    },
  ];
}

function flattenReuseTracks(review: CorpusReuseReview) {
  return review.category_matrix.flatMap((category) => category.tracks);
}

function trackNextAction(track: ReuseTrack) {
  if (track.check) return koText(track.check);
  if (track.judgement === "가능성 높음") return "최근 PoB나 영상이 나오면 우선 검증";
  if (track.judgement === "연습해도 됨") return "레벨링과 조작감 연습 후 최신 수치 재확인";
  if (track.judgement === "손봐야 가능") return "변경된 젬, 패시브, 아이템을 반영해서 PoB 수정";
  if (track.judgement === "구경만") return "실제 플레이 사례와 PoB가 나올 때까지 관찰";
  return "패치 영향과 실제 사례 확인";
}

function SummaryMetric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="research-metric">
      <div className="research-metric__value">{value}</div>
      <div className="research-metric__label">{label}</div>
    </div>
  );
}

function BuildCard({
  card,
  selected,
  onSelect,
}: {
  card: ResearchBuildCard;
  selected: boolean;
  onSelect?: (build: ResearchBuildSelection) => void;
}) {
  return (
    <button
      type="button"
      className={`research-build-card${selected ? " is-selected" : ""}`}
      onClick={() => onSelect?.(card.detail)}
    >
      <div className="research-build-card__head">
        <div>
          <strong>{card.title}</strong>
          <span>{card.subtitle}</span>
        </div>
        <em className={`ui-badge ${judgementClass(card.judgement)}`}>{card.judgement}</em>
      </div>
      <p>{card.reason}</p>
      <div className="research-build-card__chips">
        {card.chips.map((chip) => (
          <span key={chip}>{chip}</span>
        ))}
      </div>
      <small>{card.scoreText}</small>
    </button>
  );
}

function BuildCategorySection({
  category,
  selectedBuildId,
  onSelectBuild,
}: {
  category: BuildCategory;
  selectedBuildId?: string;
  onSelectBuild?: (build: ResearchBuildSelection) => void;
}) {
  return (
    <section className="ui-card">
      <div className="research-section-head">
        <div>
          <h3 className="ui-section-title">{category.title}</h3>
          <p className="research-header__copy">{category.subtitle}</p>
        </div>
        <span className="ui-text-muted">추천 빌드 {category.cards.length}개</span>
      </div>
      <div className="research-build-grid">
        {category.cards.map((card) => (
          <BuildCard
            key={card.id}
            card={card}
            selected={selectedBuildId === card.id}
            onSelect={onSelectBuild}
          />
        ))}
      </div>
    </section>
  );
}

function sourceLabel(source: WatchlistSource) {
  return source.label || source.source_id || source.family || "출처";
}

function WatchlistBuildCard({
  card,
  selected,
  onSelect,
}: {
  card: WatchlistCard;
  selected?: boolean;
  onSelect?: (build: ResearchBuildSelection) => void;
}) {
  const subtitle = [
    card.patch ? `${card.patch} 출처` : "",
    koClass(card.class_name),
    koAscendancy(card.ascendancy),
    card.lane_label,
  ].filter(Boolean).join(" / ");
  const tags = (card.tags || [])
    .map((tag) => koValue(tag))
    .filter(Boolean)
    .slice(0, 5);
  const sources = (card.sources || []).filter((source) => source.url).slice(0, 3);
  const pobUrls = (card.pob_urls || []).slice(0, 4);
  const canSelect = Boolean(onSelect);
  const select = () => {
    if (onSelect) onSelect(watchlistToSelection(card));
  };

  return (
    <article
      className={`research-watch-card${selected ? " is-selected" : ""}${canSelect ? " is-clickable" : ""}`}
      role={canSelect ? "button" : undefined}
      tabIndex={canSelect ? 0 : undefined}
      onClick={canSelect ? select : undefined}
      onKeyDown={canSelect ? (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          select();
        }
      } : undefined}
    >
      <div className="research-build-card__head">
        <div>
          <strong>{koSkill(card.display_name) || card.display_name}</strong>
          <span>{subtitle}</span>
        </div>
        <em className={`ui-badge ${judgementClass(card.player_label)}`}>{card.player_label}</em>
      </div>
      <p>{koText(card.reason)}</p>
      <div className="research-build-card__chips">
        {[koSkill(card.main_skill), ...tags].filter(Boolean).slice(0, 6).map((chip) => (
          <span key={chip}>{chip}</span>
        ))}
      </div>
      {sources.length > 0 && (
        <div className="research-watch-card__links">
          {sources.map((source) => (
            <a
              key={source.source_id || source.url || source.label}
              href={source.url || undefined}
              target="_blank"
              rel="noreferrer"
              onClick={(event) => event.stopPropagation()}
            >
              {sourceLabel(source)}
            </a>
          ))}
        </div>
      )}
      {pobUrls.length > 0 && (
        <div className="research-watch-card__pobs">
          {pobUrls.map((url, index) => (
            <a key={url} href={url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>PoB {index + 1}</a>
          ))}
          {(card.pob_urls?.length || 0) > pobUrls.length && (
            <span>외 {(card.pob_urls?.length || 0) - pobUrls.length}개</span>
          )}
        </div>
      )}
      <ul className="research-watch-card__actions">
        {(card.next_actions || []).slice(0, 3).map((action) => (
          <li key={action}>{koText(action)}</li>
        ))}
      </ul>
    </article>
  );
}

function WatchlistSection({
  cards,
  selectedBuildId,
  onSelectBuild,
}: {
  cards: WatchlistCard[];
  selectedBuildId?: string;
  onSelectBuild?: (build: ResearchBuildSelection) => void;
}) {
  if (cards.length === 0) return null;

  return (
    <section className="ui-card">
      <div className="research-section-head">
        <div>
          <h3 className="ui-section-title">고민 중인 빌드</h3>
          <p className="research-header__copy">
            기본 추천과 분리해서 보는 연습, 관찰, 승격 검토 후보입니다.
          </p>
        </div>
        <span className="ui-text-muted">검토 후보 {cards.length}개</span>
      </div>
      <div className="research-watch-grid">
        {cards.map((card) => (
          <WatchlistBuildCard
            key={card.candidate_id}
            card={card}
            selected={selectedBuildId === `watchlist:${card.candidate_id}`}
            onSelect={onSelectBuild}
          />
        ))}
      </div>
    </section>
  );
}

function CwsResearchSection({
  card,
  selectedBuildId,
  onSelectBuild,
}: {
  card?: WatchlistCard;
  selectedBuildId?: string;
  onSelectBuild?: (build: ResearchBuildSelection) => void;
}) {
  if (!card) return null;

  const pobCount = card.pob_urls?.length || 0;
  const sourceCount = card.source_count || card.sources?.length || 0;

  return (
    <section className="ui-card research-cws-feature">
      <div className="research-section-head">
        <div>
          <h3 className="ui-section-title">CWS 리서치</h3>
          <p className="research-header__copy">
            이번 시즌 직접 연습하면서 검증할 기준 빌드입니다. 일반 추천과 분리해서 전환, 실패 지점, SSF 재현성을 기록합니다.
          </p>
        </div>
        <span className={`ui-badge ${judgementClass(card.player_label)}`}>{card.player_label}</span>
      </div>
      {onSelectBuild && (
        <button
          type="button"
          className="ui-button ui-button--primary research-cws-feature__open"
          onClick={() => onSelectBuild(watchlistToSelection(card))}
        >
          CWS 상세 / PoB 검증으로 열기
        </button>
      )}
      <div className="research-cws-feature__summary">
        <div>
          <strong>{koSkill(card.display_name) || card.display_name}</strong>
          <span>{[card.patch, koClass(card.class_name), koAscendancy(card.ascendancy)].filter(Boolean).join(" / ")}</span>
        </div>
        <div>
          <strong>{pobCount}</strong>
          <span>단계별 PoB</span>
        </div>
        <div>
          <strong>{sourceCount}</strong>
          <span>원본 근거</span>
        </div>
      </div>
      {((card.playstyle_summary?.length || 0) > 0
        || (card.mirage_notes?.length || 0) > 0
        || (card.upgrade_notes?.length || 0) > 0) && (
        <div className="research-cws-feature__note-grid">
          {(card.playstyle_summary?.length || 0) > 0 && (
            <div>
              <h4>빌드 성격</h4>
              <ul>
                {card.playstyle_summary?.slice(0, 5).map((item) => (
                  <li key={item}>{koText(item)}</li>
                ))}
              </ul>
            </div>
          )}
          {(card.mirage_notes?.length || 0) > 0 && (
            <div>
              <h4>Mirage 리그 노트</h4>
              <ul>
                {card.mirage_notes?.slice(0, 9).map((item) => (
                  <li key={item}>{koText(item)}</li>
                ))}
              </ul>
            </div>
          )}
          {(card.upgrade_notes?.length || 0) > 0 && (
            <div>
              <h4>업그레이드 메모</h4>
              <ul>
                {card.upgrade_notes?.slice(0, 8).map((item) => (
                  <li key={item}>{koText(item)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      {(card.practice_route?.length || 0) > 0 && (
        <div className="research-cws-feature__route">
          {card.practice_route?.map((stage) => (
            <div key={stage.stage} className="research-cws-feature__stage">
              <div>
                <strong>{koText(stage.stage)}</strong>
                {stage.pob_url && (
                  <a href={stage.pob_url} target="_blank" rel="noreferrer">PoB</a>
                )}
                {stage.source_links?.map((source) => (
                  source.url ? (
                    <a key={source.source_id || source.url} href={source.url} target="_blank" rel="noreferrer">
                      {koText(source.label)}
                    </a>
                  ) : null
                ))}
              </div>
              <p>{koText(stage.goal)}</p>
              {(stage.skill_setups?.length || 0) > 0 && (
                <div className="research-cws-feature__skills">
                  {stage.skill_setups?.map((skill) => (
                    <span key={skill}>{koText(skill)}</span>
                  ))}
                </div>
              )}
              {stage.source_note && <em>{koText(stage.source_note)}</em>}
              <ul>
                {(stage.checks || []).slice(0, 3).map((check) => (
                  <li key={check}>{koText(check)}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
      {(card.anytime_upgrades?.length || 0) > 0 && (
        <div className="research-cws-feature__anytime">
          <h4>언제든 교체 가능한 업그레이드</h4>
          <ul>
            {card.anytime_upgrades?.map((u) => (
              <li key={u.node_id}><strong>{koText(u.label)}</strong>{u.note ? ` — ${koText(u.note)}` : ""}</li>
            ))}
          </ul>
        </div>
      )}
      {(card.map_mods_to_avoid?.length || 0) > 0 && (
        <div className="research-cws-feature__map-mods">
          <h4>맵 모드 금지/주의</h4>
          <div>
            {card.map_mods_to_avoid?.map((group) => (
              <section key={group.severity}>
                <strong>{koText(group.label)}</strong>
                <div className="research-cws-feature__skills">
                  {group.mods.slice(0, 8).map((mod) => (
                    <span key={mod}>{koText(mod)}</span>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      )}
      {((card.red_flags?.length || 0) > 0 || (card.promotion_checks?.length || 0) > 0) && (
        <div className="research-cws-feature__checks">
          {(card.red_flags?.length || 0) > 0 && (
            <div>
              <h4>위험 체크</h4>
              <ul>
                {card.red_flags?.map((item) => (
                  <li key={item}>{koText(item)}</li>
                ))}
              </ul>
            </div>
          )}
          {(card.promotion_checks?.length || 0) > 0 && (
            <div>
              <h4>추천 승격 조건</h4>
              <ul>
                {card.promotion_checks?.map((item) => (
                  <li key={item}>{koText(item)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      <WatchlistBuildCard
        card={card}
        selected={selectedBuildId === `watchlist:${card.candidate_id}`}
        onSelect={onSelectBuild}
      />
    </section>
  );
}

export function ResearchDashboard({ onSelectBuild, selectedBuildId }: Props) {
  const [payload, setPayload] = useState<ResearchPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [usedFallback, setUsedFallback] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setUsedFallback(false);
      try {
        const raw = await invoke<string>("load_poe1_research_dashboard");
        if (cancelled) return;
        setPayload(normalizeResearchPayload(JSON.parse(raw)));
      } catch (e) {
        console.warn("research dashboard fallback", e);
        if (!cancelled) {
          setPayload(makeFallbackResearchPayload());
          setUsedFallback(true);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => { cancelled = true; };
  }, []);

  const reviewTracks = useMemo(
    () => payload ? flattenReuseTracks(payload.corpus_reuse_review) : [],
    [payload],
  );
  const practiceTracks = reviewTracks
    .filter((track) => ["가능성 높음", "연습해도 됨", "손봐야 가능", "구경만"].includes(track.judgement))
    .slice(0, 8);
  const categories = useMemo(
    () => buildCategories(payload?.representative_profiles.profiles ?? []),
    [payload],
  );
  const levelingCount = categories.find((category) => category.id === "leveling")?.cards.length ?? 0;
  const endgameCount = categories.find((category) => category.id === "endgame")?.cards.length ?? 0;
  const allInOneCount = categories.find((category) => category.id === "all_in_one")?.cards.length ?? 0;
  const watchlistCards = payload?.watchlist_candidate_cards?.cards ?? [];
  const cwsResearchCard = watchlistCards.find((card) => card.candidate_id === CWS_RESEARCH_CARD_ID);
  const otherWatchlistCards = watchlistCards.filter((card) => card.candidate_id !== CWS_RESEARCH_CARD_ID);

  if (loading) {
    return (
      <section className="ui-card">
        <h2 className="ui-section-title">빌드 리서치</h2>
        <p className="ui-text-muted" style={{ margin: 0 }}>추천 후보를 불러오는 중입니다.</p>
      </section>
    );
  }

  if (!payload) {
    return (
      <section className="ui-card">
        <h2 className="ui-section-title">빌드 리서치</h2>
        <div className="ui-alert ui-alert--danger">리서치 데이터를 읽지 못했습니다.</div>
      </section>
    );
  }

  return (
    <div className="research-dashboard">
      <section className="ui-card">
        <div className="research-header">
          <div>
            <h2 className="ui-section-title">POE1 3.29 추천 빌드 리서치</h2>
            <p className="research-header__copy">
              후보를 먼저 고르고, 선택한 빌드는 PoB 검증 탭에서 전환 경로와 검증 포인트를 이어서 봅니다.
            </p>
          </div>
          <span className={`ui-badge ${usedFallback ? "ui-badge--warning" : "ui-badge--accent"}`}>
            {usedFallback ? "핵심 루트 우선" : "추천 전 검증"}
          </span>
        </div>

        <div className="research-metrics">
          <SummaryMetric label="추천 프로필" value={payload.representative_profiles.summary.profile_count} />
          <SummaryMetric label="레벨링 후보" value={levelingCount} />
          <SummaryMetric label="엔드게임 후보" value={endgameCount} />
          <SummaryMetric label="한방 후보" value={allInOneCount} />
          <SummaryMetric label="검토 후보" value={watchlistCards.length} />
          <SummaryMetric label="CWS PoB" value={cwsResearchCard?.pob_urls?.length ?? 0} />
        </div>
      </section>

      <CwsResearchSection
        card={cwsResearchCard}
        selectedBuildId={selectedBuildId}
        onSelectBuild={onSelectBuild}
      />

      {categories.map((category) => (
        <BuildCategorySection
          key={category.id}
          category={category}
          selectedBuildId={selectedBuildId}
          onSelectBuild={onSelectBuild}
        />
      ))}

      <WatchlistSection
        cards={otherWatchlistCards}
        selectedBuildId={selectedBuildId}
        onSelectBuild={onSelectBuild}
      />

      <section className="ui-card">
        <div className="research-section-head">
          <h3 className="ui-section-title">후보 판단 보드</h3>
          <span className="ui-text-muted">카테고리별 연습 가치</span>
        </div>
        <div className="research-candidate-board">
          {practiceTracks.map((track) => (
            <div key={track.track_id} className="research-candidate">
              <div className="research-candidate__head">
                <strong>{track.label}</strong>
                <span className={`ui-badge ${judgementClass(track.judgement)}`}>{track.judgement}</span>
              </div>
              <p>{koText(track.why) || trackNextAction(track)}</p>
              <div className="research-candidate__meta">
                {(track.applies_to || track.practice_focus || []).slice(0, 3).map((item) => (
                  <span key={item}>{koText(item)}</span>
                ))}
              </div>
              <em>{trackNextAction(track)}</em>
            </div>
          ))}
        </div>
      </section>

      <section className="ui-card">
        <div className="research-section-head">
          <h3 className="ui-section-title">루미너리 / 용병 링크 검증</h3>
          <span className={`ui-badge ${judgementClass(payload.luminary_intake.practice_judgement.player_facing_label)}`}>
            {payload.luminary_intake.practice_judgement.player_facing_label}
          </span>
        </div>
        <p className="research-lane-purpose">{payload.luminary_intake.practice_judgement.reason}</p>

        <div className="research-split">
          <div>
            <h4>핵심 가설</h4>
            <ul className="research-plain-list">
              {payload.luminary_intake.link_skill_hypotheses.slice(0, 6).map((row) => (
                <li key={row.hypothesis_id}>
                  <strong>{row.label}</strong>
                  <span>{koText(row.player_role)}{" -> "}{koText(row.mercenary_role)}</span>
                  <em>{koText(row.risk)}</em>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4>검증 태스크</h4>
            <ul className="research-plain-list">
              {payload.luminary_intake.live_validation_tasks.map((task) => (
                <li key={task.task_id}>
                  <strong>{koText(task.task_id)}</strong>
                  <span>{koText(task.required_input)}</span>
                  <em>{koText(task.output)}</em>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="research-chip-row">
          {payload.luminary_intake.item_watchlist.map((item) => (
            <span key={item.item_name} className="ui-badge ui-badge--accent">
              {item.item_name}
            </span>
          ))}
        </div>
      </section>

    </div>
  );
}
