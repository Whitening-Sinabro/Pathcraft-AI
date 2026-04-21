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
  early_atlas: string;
  mid_atlas: string;
  late_atlas: string;
  scarab_priority: string[];
  ssf_crafting_focus: string;
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
}

export interface FilterResult {
  overlay: string;
  stats: FilterStats;
  uniques: string[];
  target_divcards: FilterTargetDivcard[];
  chanceable_bases: FilterChanceableBase[];
}
