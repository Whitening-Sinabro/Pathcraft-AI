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
