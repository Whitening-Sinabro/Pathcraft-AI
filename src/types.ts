export interface BuildMeta {
  build_name: string;
  class: string;
  ascendancy: string;
}

export interface BuildStats {
  dps: number;
  life: number;
  energy_shield: number;
}

export interface BuildData {
  meta: BuildMeta;
  stats: BuildStats;
  gear: Record<string, unknown>;
  skills: Record<string, unknown>;
  passives: Record<string, unknown>;
}

export interface BuildSourceResolution {
  dataset_kind: string;
  input_url: string;
  source_type: string;
  canonical_url: string;
  title: string | null;
  pob_url: string | null;
  passive_tree_url: string | null;
  maxroll_tool_url?: string | null;
  warnings: string[];
  all_candidates?: {
    pob_urls: string[];
    passive_tree_urls: string[];
    tool_urls: string[];
  };
}

export interface LinksProgression {
  level_range: string;
  gems: string[];
}

export interface LevelingSkillOption {
  name: string;
  links?: string;  // 레거시 fallback
  links_progression?: LinksProgression[];
  speed: string;
  safety: string;
  reason: string;
}

export interface SkillTransition {
  level: number;
  change: string;
  reason: string;
}

export interface LevelingSkills {
  damage_type: string;
  recommended: {
    name: string;
    links?: string;
    links_progression?: LinksProgression[];
    reason: string;
    transition_level: string;
  };
  options: LevelingSkillOption[];
  skill_transitions: SkillTransition[];
}

export interface AuraPhase {
  phase: string;
  auras: string[];
  heralds: string[];
  reservation_total: string;
  utility: string[];
  guard: string;
  reason: string;
}

export interface BuildRating {
  newbie_friendly: number;
  gearing_difficulty: number;
  play_difficulty: number;
  league_start_viable: number;
  hcssf_viability: number;
}

// AI 검증 경고 (coach_validator.py 출력)
export type ValidationWarnings = string[];

// 코치 출력 자동 교정 이력 (coach_normalizer.py 출력) — H2 trace, H6 L2 drop
export interface NormalizationTraceEntry {
  field: string;          // 경로 (예: "leveling_skills.recommended.links_progression[0].gems[1]")
  from: string;           // LLM 원본
  to: string | null;      // 교정 결과 (valid_gems 기준). dropped면 null
  match_type: "alias" | "exact" | "fuzzy" | "dropped";
}

export interface GearPhase {
  phase: string;
  item: string;
  key_stats: string[];
  acquisition: string;
  priority: string;
}

export interface GearSlotProgression {
  slot: string;
  phases: GearPhase[];
}

export interface MapModWarnings {
  deadly: string[];
  dangerous: string[];
  caution: string[];
  regex_filter: string;
}

export interface VariantSnapshot {
  phase: string;
  level_range: string;
  main_skill: string;
  auras: string;
  gear_priority: string;
  passive_focus: string;
  defense_target: {
    life: number;
    energy_shield: number;
    resists: string;
    armour_or_evasion: string;
  };
}

export interface CoachResult {
  build_summary: string;
  tier: string;
  strengths: string[];
  weaknesses: string[];
  leveling_guide: {
    act1_4: string;
    act5_10: string;
    early_maps: string;
    endgame: string;
  };
  leveling_skills: LevelingSkills;
  key_items: {
    name: string;
    slot: string;
    importance: string;
    acquisition: string;
    ssf_difficulty: string;
    alternatives: string[];
  }[];
  aura_utility_progression: AuraPhase[];
  build_rating: BuildRating;
  gear_progression: GearSlotProgression[];
  map_mod_warnings: MapModWarnings;
  variant_snapshots: VariantSnapshot[];
  passive_priority: string[];
  danger_zones: string[];
  new_player_bridge?: NewPlayerBridge;
  farming_strategy: string | FarmingStrategy;
  _validation_warnings?: ValidationWarnings;
  _normalization_trace?: NormalizationTraceEntry[];
  _retry_info?: CoachRetryInfo;
}

// L3 Gate + Auto-retry 메타 (Phase H6)
// 1차 응답에 drop 발견 → 교정 프롬프트로 1회 재호출. attempts=2 면 재시도 1회 수행.
// recovered_from: 1차에서 drop됐던 이름들 (재시도 유발 원인).
// final_dropped: 재시도 후에도 남은 drop (비어있으면 회복 성공, 있으면 L4 차단).
export interface CoachRetryInfo {
  attempts: number;
  recovered_from: string[];
  final_dropped: string[];
}

export interface FarmingStrategy {
  recommended_mechanics: string[];
  atlas_passive_focus: string;
  readiness_assessment?: {
    current_phase: string;
    atlas_progress?: string;
    atlas_passives_100?: string;
    highest_tier_smooth?: string;
    t16_smooth?: string;
    clear_speed_state?: string;
    t16_under_2_min?: string;
    death_rate?: string;
    reason: string;
    next_measurement: string;
  };
  atlas_phase_boundaries?: {
    early_mapping: string;
    mid_mapping: string;
    late_mapping: string;
    promotion_checks: string[];
  };
  early_atlas: string;
  mid_atlas: string;
  late_atlas: string;
  scarab_priority: string[];
  ssf_crafting_focus: string;
}

export interface NewPlayerFrictionPoint {
  area: string;
  why_it_blocks: string;
  what_pathcraft_fills: string;
  next_action: string;
}

export interface NewPlayerBridge {
  likely_friction_points: NewPlayerFrictionPoint[];
  poe2_to_poe1_notes: string[];
  beginner_safe_next_steps: string[];
}

export interface FilterTargetDivcard {
  card: string;
  stack: number;
  target_unique: string;
}

export interface FilterChanceableBase {
  base: string;
  unique: string;
}

export interface FilterStats {
  unique_count: number;
  divcard_count: number;
  chanceable_count: number;
  strictness: number;
  mode?: "ssf" | "hcssf" | "trade";
  stage?: boolean;
  al_split?: number;
  game?: string;
}

export interface FilterResult {
  overlay: string;
  stats: FilterStats;
  uniques: string[];
  target_divcards: FilterTargetDivcard[];
  chanceable_bases: FilterChanceableBase[];
}

export interface DeterministicGuard {
  guard: string;
  status: string;
  reason: string;
}

export interface RepresentativeAiPolicy {
  mode: string;
  reason: string;
  allowed_slots: string[];
  forbidden_overrides: string[];
}

export interface RepresentativeVerificationStep {
  step: string;
  status: string;
  detail: unknown;
}

export interface RepresentativeVerificationLoop {
  confidence_lane: string;
  loop_state: string;
  recommended_plan: string;
  steps: RepresentativeVerificationStep[];
  promotion_requirements: string[];
  next_actions: string[];
}

export interface RepresentativeGuardrails {
  deterministic_guards: DeterministicGuard[];
  ai_policy: RepresentativeAiPolicy;
  verification_loop: RepresentativeVerificationLoop;
}

export interface RepresentativeResponseBadge {
  kind: string;
  label: string;
  tone: string;
}

export interface RepresentativeUserMessage {
  template_id: string;
  title: string;
  summary: string;
  bullets: string[];
}

export interface RepresentativeResponseDecision {
  plan: string;
  decision_state: string;
  candidate_path: string;
  confidence_lane: string;
  blocking_guards: string[];
  warning_guards: string[];
}

export interface RepresentativeAiExplanation {
  mode: string;
  instruction: string;
  allowed_slots: string[];
  forbidden_overrides: string[];
}

export interface RepresentativeResponseLayers {
  decision: RepresentativeResponseDecision;
  user_message: RepresentativeUserMessage;
  ui_panels: {
    show_deterministic_guards: boolean;
    show_ai_policy: boolean;
    show_verification_loop: boolean;
  };
  ai_explanation: RepresentativeAiExplanation;
  badges: RepresentativeResponseBadge[];
}

export interface RepresentativeCompatibility {
  selected_plan: string;
  hard_blocks: string[];
  soft_flags: string[];
  fallback_actions: string[];
  budget_fit_ratio?: number;
  deterministic_guards?: DeterministicGuard[];
  ai_policy?: RepresentativeAiPolicy;
  verification_loop?: RepresentativeVerificationLoop;
  guardrails?: RepresentativeGuardrails;
  response_layers?: RepresentativeResponseLayers;
}

export interface RepresentativeProfileIdentity {
  build_name?: string;
  patch?: string;
  class_name?: string;
  ascendancy?: string;
  main_skill?: string;
  leveling_skill?: string;
  damage_tags?: string[];
  weapon_preferences?: string[];
}

export interface RepresentativeProfilePlaystyle {
  input_style?: string;
  manual_buttons?: number;
  movement_dependence?: string;
  aim_requirement?: string;
  notes?: string;
}

export interface RepresentativeProfileBudgetCurve {
  entry_cost_divines?: number;
  comfortable_cost_divines?: number;
  aspirational_cost_divines?: number;
  respec_cost_points?: number;
  notes?: string;
}

export interface RepresentativeProfileAvailability {
  league_start_viable?: boolean;
  ssf_viable?: string;
  hc_viable?: string;
  twink_required?: boolean;
  mandatory_uniques?: string[];
  mandatory_transfigured_gems?: string[];
}

export interface RepresentativeTransitionPoint {
  stage?: string;
  main_skill?: string;
  trigger?: string;
  required_links?: number;
  required_item?: string | null;
  from_skill?: string;
  to_skill?: string;
  level?: number;
  source?: string;
}

export interface RepresentativeCampaignStep {
  stage?: string;
  stage_label?: string;
  level_range?: string;
  main_skill?: string;
  support_links?: string[];
  auras?: string[];
  utility?: string[];
  guard?: string[];
  source?: string;
  notes?: string;
}

export interface RepresentativePassivePlanStep {
  stage?: string;
  stage_label?: string;
  level_range?: string;
  tree_url?: string;
  active?: boolean;
  source?: string;
  priorities?: string[];
  notes?: string;
}

export interface RepresentativeGearStage {
  stage?: string;
  stage_label?: string;
  level_range?: string;
  priorities?: string[];
  requirements?: string[];
  source?: string;
  notes?: string;
}

export interface RepresentativeProfileProgression {
  leveling_confidence?: string;
  early_mapping_ready?: boolean;
  transition_points?: RepresentativeTransitionPoint[];
  campaign_plan?: RepresentativeCampaignStep[];
  passive_plan?: RepresentativePassivePlanStep[];
  gear_stages?: RepresentativeGearStage[];
}

export interface RepresentativeProfileConfidence {
  representative_build_status?: string;
  source_count?: number;
  notes?: string;
}

export interface RepresentativeProfileEvidence {
  type?: string;
  label?: string;
  url?: string;
  notes?: string;
}

export interface RepresentativeProfileSummary {
  build_id?: string;
  identity?: RepresentativeProfileIdentity;
  playstyle?: RepresentativeProfilePlaystyle;
  budget_curve?: RepresentativeProfileBudgetCurve;
  availability?: RepresentativeProfileAvailability;
  suitability?: Record<string, number>;
  constraints?: {
    banned_map_mods?: string[];
    pain_points?: string[];
  };
  confidence?: RepresentativeProfileConfidence;
  progression?: RepresentativeProfileProgression;
  evidence?: RepresentativeProfileEvidence[];
}

export interface RepresentativeCandidate {
  candidate_id?: string;
  league_name?: string;
  board_status?: string;
  use_policy?: string;
  source_confidence?: string;
  build_id?: string;
  build_name?: string;
  main_skill?: string;
  class_name?: string;
  ascendancy?: string;
  score?: number;
  hard_blocks?: string[];
  compatibility?: RepresentativeCompatibility;
  profile_summary?: RepresentativeProfileSummary | null;
}

export interface RepresentativeRecommendation {
  selected_plan: string;
  selected_build_id: string | null;
  selected_build_name: string | null;
  selected_score: number | null;
  selected_candidate?: RepresentativeCandidate;
  selected_profile?: RepresentativeProfileSummary | null;
  blocking_candidate?: RepresentativeCandidate | null;
  blocking_profile?: RepresentativeProfileSummary | null;
  recommendations: RepresentativeCandidate[];
  proxy_candidates: RepresentativeCandidate[];
  rejections: RepresentativeCandidate[];
  deterministic_guards: DeterministicGuard[];
  ai_policy: RepresentativeAiPolicy;
  verification_loop: RepresentativeVerificationLoop;
  guardrails: RepresentativeGuardrails;
  response_layers: RepresentativeResponseLayers;
}

export interface RepresentativeCorpusRecommendationResult {
  dataset_kind: string;
  corpus_summary: {
    profile_count: number;
    confirmed: number;
    near_confirmed: number;
    hold: number;
  };
  active_scope: string;
  candidate_pool_size: number;
  recommendation: RepresentativeRecommendation;
}
