import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";

interface BuildMeta {
  build_name: string;
  class: string;
  ascendancy: string;
}

interface BuildStats {
  dps: number;
  life: number;
  energy_shield: number;
}

interface BuildData {
  meta: BuildMeta;
  stats: BuildStats;
  gear: Record<string, unknown>;
  skills: Record<string, unknown>;
  passives: Record<string, unknown>;
}

interface LevelingSkillOption {
  name: string;
  links: string;
  speed: string;
  safety: string;
  reason: string;
}

interface SkillTransition {
  level: number;
  change: string;
  reason: string;
}

interface LevelingSkills {
  damage_type: string;
  recommended: {
    name: string;
    links: string;
    reason: string;
    transition_level: string;
  };
  options: LevelingSkillOption[];
  skill_transitions: SkillTransition[];
}

interface AuraPhase {
  phase: string;
  auras: string[];
  heralds: string[];
  reservation_total: string;
  utility: string[];
  guard: string;
  reason: string;
}

interface BuildRating {
  newbie_friendly: number;
  gearing_difficulty: number;
  play_difficulty: number;
  league_start_viable: number;
  hcssf_viability: number;
}

interface GearPhase {
  phase: string;
  item: string;
  key_stats: string[];
  acquisition: string;
  priority: string;
}

interface GearSlotProgression {
  slot: string;
  phases: GearPhase[];
}

interface MapModWarnings {
  deadly: string[];
  dangerous: string[];
  caution: string[];
  regex_filter: string;
}

interface VariantSnapshot {
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

interface CoachResult {
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
  farming_strategy: string;
}

function App() {
  const [pobLink, setPobLink] = useState("");
  const [buildData, setBuildData] = useState<BuildData | null>(null);
  const [coaching, setCoaching] = useState<CoachResult | null>(null);
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const [activeVariant, setActiveVariant] = useState(0);

  async function analyzeBuild() {
    setError("");
    setBuildData(null);
    setCoaching(null);

    const trimmed = pobLink.trim();
    if (!trimmed) return;

    setLoading("POB 파싱 중...");
    try {
      const raw = await invoke<string>("parse_pob", { link: trimmed });
      const parsed: BuildData = JSON.parse(raw);
      setBuildData(parsed);

      setLoading("AI 코치 분석 중...");
      const coachRaw = await invoke<string>("coach_build", { buildJson: raw });
      const coachResult = JSON.parse(coachRaw);
      setCoaching(coachResult);
      setLoading("");
    } catch (e) {
      setError(String(e));
      setLoading("");
    }
  }

  const tierColor: Record<string, string> = {
    S: "#ff6b6b", A: "#ffa94d", B: "#69db7c", C: "#74c0fc", D: "#868e96",
  };

  return (
    <main style={{ padding: "1.5rem", fontFamily: "Pretendard, sans-serif", maxWidth: 800, margin: "0 auto" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>PathcraftAI — Build Coach</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="POB 링크 입력 (pobb.in, pastebin 등)"
          value={pobLink}
          onChange={(e) => setPobLink(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && analyzeBuild()}
          style={{ flex: 1, padding: "10px 12px", borderRadius: 6, border: "1px solid #dee2e6", fontSize: 14 }}
        />
        <button
          onClick={analyzeBuild}
          disabled={!pobLink || !!loading}
          style={{
            padding: "10px 20px", borderRadius: 6, border: "none",
            background: loading ? "#868e96" : "#228be6", color: "#fff",
            cursor: loading ? "wait" : "pointer", fontSize: 14, fontWeight: 600,
          }}
        >
          {loading || "분석"}
        </button>
      </div>

      {error && <div style={{ color: "#e03131", padding: 12, background: "#fff5f5", borderRadius: 6, marginBottom: 12 }}>{error}</div>}

      {buildData && (
        <div style={{ padding: 12, background: "#f8f9fa", borderRadius: 8, marginBottom: 12 }}>
          <strong>{buildData.meta?.build_name}</strong>
          <span style={{ marginLeft: 8, color: "#868e96" }}>
            DPS: {buildData.stats?.dps?.toLocaleString()} |
            Life: {buildData.stats?.life?.toLocaleString()} |
            ES: {buildData.stats?.energy_shield?.toLocaleString()}
          </span>
        </div>
      )}

      {coaching && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* 요약 */}
          <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
              <span style={{
                display: "inline-block", width: 36, height: 36, borderRadius: "50%",
                background: tierColor[coaching.tier] || "#868e96", color: "#fff",
                textAlign: "center", lineHeight: "36px", fontWeight: 700, fontSize: 18,
              }}>{coaching.tier}</span>
              <span style={{ fontSize: 16, fontWeight: 600 }}>{coaching.build_summary}</span>
            </div>
            <div style={{ display: "flex", gap: 16 }}>
              <div style={{ flex: 1 }}>
                <strong style={{ color: "#2b8a3e" }}>강점</strong>
                <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
                  {coaching.strengths.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
              <div style={{ flex: 1 }}>
                <strong style={{ color: "#e03131" }}>약점</strong>
                <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
                  {coaching.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                </ul>
              </div>
            </div>
          </section>

          {/* 빌드 평가 */}
          {coaching.build_rating && Object.keys(coaching.build_rating).length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 10px", fontSize: 15 }}>빌드 평가</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, textAlign: "center" }}>
                {([
                  ["hcssf_viability", "HCSSF"],
                  ["league_start_viable", "리그 스타터"],
                  ["newbie_friendly", "뉴비 친화"],
                  ["gearing_difficulty", "기어링"],
                  ["play_difficulty", "조작 난이도"],
                ] as const).map(([key, label]) => {
                  const val = coaching.build_rating[key] || 0;
                  return (
                    <div key={key}>
                      <div style={{ fontSize: 12, color: "#868e96", marginBottom: 4 }}>{label}</div>
                      <div style={{ display: "flex", justifyContent: "center", gap: 2 }}>
                        {[1, 2, 3, 4, 5].map(n => (
                          <span key={n} style={{
                            width: 10, height: 10, borderRadius: 2,
                            background: n <= val
                              ? (val >= 4 ? "#2b8a3e" : val >= 3 ? "#f59f00" : "#e03131")
                              : "#e9ecef",
                          }} />
                        ))}
                      </div>
                      <div style={{ fontSize: 11, color: "#495057", marginTop: 2 }}>{val}/5</div>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* 구간별 스냅샷 탭 */}
          {coaching.variant_snapshots?.length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 10px", fontSize: 15 }}>구간별 진행</h3>
              <div style={{ display: "flex", gap: 4, marginBottom: 12, flexWrap: "wrap" }}>
                {coaching.variant_snapshots.map((v, i) => (
                  <button key={i} onClick={() => setActiveVariant(i)} style={{
                    padding: "6px 12px", borderRadius: 4, border: "1px solid #dee2e6",
                    background: activeVariant === i ? "#228be6" : "#f8f9fa",
                    color: activeVariant === i ? "#fff" : "#495057",
                    fontSize: 12, fontWeight: activeVariant === i ? 600 : 400,
                    cursor: "pointer",
                  }}>{v.phase}</button>
                ))}
              </div>
              {(() => {
                const v = coaching.variant_snapshots[activeVariant];
                if (!v) return null;
                return (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 13 }}>
                    <div>
                      <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>레벨</div>
                      <div style={{ fontWeight: 600 }}>{v.level_range}</div>
                    </div>
                    <div>
                      <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>메인 스킬</div>
                      <div>{v.main_skill}</div>
                    </div>
                    <div>
                      <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>오라</div>
                      <div>{v.auras}</div>
                    </div>
                    <div>
                      <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>패시브 방향</div>
                      <div>{v.passive_focus}</div>
                    </div>
                    <div style={{ gridColumn: "1 / -1" }}>
                      <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>장비 우선순위</div>
                      <div>{v.gear_priority}</div>
                    </div>
                    {v.defense_target && (
                      <div style={{ gridColumn: "1 / -1", display: "flex", gap: 16, padding: 8, background: "#f8f9fa", borderRadius: 6 }}>
                        <span>Life: <strong>{v.defense_target.life?.toLocaleString()}</strong></span>
                        {v.defense_target.energy_shield > 0 && <span>ES: <strong>{v.defense_target.energy_shield?.toLocaleString()}</strong></span>}
                        <span>저항: <strong>{v.defense_target.resists}</strong></span>
                        {v.defense_target.armour_or_evasion && <span>방어: <strong>{v.defense_target.armour_or_evasion}</strong></span>}
                      </div>
                    )}
                  </div>
                );
              })()}
            </section>
          )}

          {/* 레벨링 */}
          <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
            <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>레벨링 가이드</h3>
            {Object.entries(coaching.leveling_guide).map(([key, val]) => (
              <div key={key} style={{ marginBottom: 8 }}>
                <strong style={{ color: "#495057" }}>
                  {key === "act1_4" ? "Act 1-4" : key === "act5_10" ? "Act 5-10" : key === "early_maps" ? "초반 맵" : "엔드게임"}
                </strong>
                <p style={{ margin: "2px 0 0", color: "#495057", fontSize: 14 }}>{val}</p>
              </div>
            ))}
          </section>

          {/* 레벨링 스킬 */}
          {coaching.leveling_skills?.recommended && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>레벨링 스킬</h3>
              <div style={{ marginBottom: 12, padding: 10, background: "#e7f5ff", borderRadius: 6 }}>
                <strong>추천: {coaching.leveling_skills.recommended.name}</strong>
                <span style={{ marginLeft: 8, color: "#495057", fontSize: 13 }}>
                  ({coaching.leveling_skills.damage_type})
                </span>
                <div style={{ fontSize: 13, marginTop: 4 }}>
                  링크: {coaching.leveling_skills.recommended.links}
                </div>
                <div style={{ fontSize: 13, color: "#495057" }}>
                  {coaching.leveling_skills.recommended.reason}
                  {coaching.leveling_skills.recommended.transition_level && (
                    <span> — 전환 시점: Lv.{coaching.leveling_skills.recommended.transition_level}</span>
                  )}
                </div>
              </div>
              {coaching.leveling_skills.options?.length > 0 && (
                <>
                  <strong style={{ fontSize: 13 }}>옵션</strong>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, marginTop: 4 }}>
                    <thead>
                      <tr style={{ borderBottom: "2px solid #dee2e6", textAlign: "left" }}>
                        <th style={{ padding: 6 }}>스킬</th>
                        <th style={{ padding: 6 }}>속도</th>
                        <th style={{ padding: 6 }}>안전도</th>
                        <th style={{ padding: 6 }}>설명</th>
                      </tr>
                    </thead>
                    <tbody>
                      {coaching.leveling_skills.options.map((opt, i) => (
                        <tr key={i} style={{ borderBottom: "1px solid #f1f3f5" }}>
                          <td style={{ padding: 6 }}>
                            <strong>{opt.name}</strong>
                            <br /><span style={{ color: "#868e96", fontSize: 12 }}>{opt.links}</span>
                          </td>
                          <td style={{ padding: 6 }}>{opt.speed}</td>
                          <td style={{ padding: 6, color: opt.safety === "높음" ? "#2b8a3e" : opt.safety === "낮음" ? "#e03131" : "#f59f00" }}>
                            {opt.safety}
                          </td>
                          <td style={{ padding: 6 }}>{opt.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              )}
              {coaching.leveling_skills.skill_transitions?.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <strong style={{ fontSize: 13 }}>스킬 전환</strong>
                  <ul style={{ margin: "4px 0 0", paddingLeft: 20, fontSize: 13 }}>
                    {coaching.leveling_skills.skill_transitions.map((t, i) => (
                      <li key={i}>Lv.{t.level}: {t.change} — {t.reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}

          {/* 오라/유틸리티 진행 */}
          {coaching.aura_utility_progression?.length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>오라 / 유틸리티 진행</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #dee2e6", textAlign: "left" }}>
                    <th style={{ padding: 6 }}>구간</th>
                    <th style={{ padding: 6 }}>오라 / 전령</th>
                    <th style={{ padding: 6 }}>예약</th>
                    <th style={{ padding: 6 }}>유틸리티 / 가드</th>
                  </tr>
                </thead>
                <tbody>
                  {coaching.aura_utility_progression.map((phase, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #f1f3f5", verticalAlign: "top" }}>
                      <td style={{ padding: 6, fontWeight: 600, whiteSpace: "nowrap" }}>{phase.phase}</td>
                      <td style={{ padding: 6 }}>
                        {phase.auras?.length > 0 && <div>{phase.auras.join(", ")}</div>}
                        {phase.heralds?.length > 0 && <div style={{ color: "#5c7cfa" }}>{phase.heralds.join(", ")}</div>}
                      </td>
                      <td style={{ padding: 6 }}>{phase.reservation_total}</td>
                      <td style={{ padding: 6 }}>
                        {phase.utility?.length > 0 && <div>{phase.utility.join(", ")}</div>}
                        {phase.guard && <div style={{ color: "#495057" }}>가드: {phase.guard}</div>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {/* 장비 진행 타임라인 */}
          {coaching.gear_progression?.length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 12px", fontSize: 15 }}>장비 진행</h3>
              {coaching.gear_progression.map((slot, si) => (
                <div key={si} style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#495057", marginBottom: 6 }}>{slot.slot}</div>
                  <div style={{ display: "flex", alignItems: "stretch", gap: 0 }}>
                    {slot.phases.map((p, pi) => {
                      const prioColor = p.priority === "필수" ? "#e03131" : p.priority === "권장" ? "#f59f00" : "#2b8a3e";
                      return (
                        <div key={pi} style={{ display: "flex", alignItems: "center" }}>
                          <div style={{
                            padding: "8px 12px", borderRadius: 6, border: "1px solid #e9ecef",
                            background: "#f8f9fa", minWidth: 130, fontSize: 12,
                          }}>
                            <div style={{ fontSize: 10, color: "#868e96", marginBottom: 2 }}>{p.phase}</div>
                            <div style={{ fontWeight: 600, marginBottom: 3 }}>{p.item}</div>
                            <div style={{ color: "#868e96", fontSize: 11, marginBottom: 2 }}>
                              {p.key_stats?.join(", ")}
                            </div>
                            <div style={{ fontSize: 11 }}>{p.acquisition}</div>
                            <span style={{
                              display: "inline-block", marginTop: 4, fontSize: 10, padding: "1px 6px",
                              borderRadius: 3, background: prioColor + "18", color: prioColor, fontWeight: 600,
                            }}>{p.priority}</span>
                          </div>
                          {pi < slot.phases.length - 1 && (
                            <span style={{ padding: "0 6px", color: "#ced4da", fontSize: 18, fontWeight: 700 }}>→</span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </section>
          )}

          {/* 핵심 장비 (레거시 — gear_progression 없으면 폴백) */}
          {(!coaching.gear_progression || coaching.gear_progression.length === 0) && coaching.key_items?.length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>핵심 장비 (SSF 획득)</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #dee2e6", textAlign: "left" }}>
                    <th style={{ padding: 6 }}>아이템</th>
                    <th style={{ padding: 6 }}>중요도</th>
                    <th style={{ padding: 6 }}>SSF 난이도</th>
                    <th style={{ padding: 6 }}>획득 방법</th>
                  </tr>
                </thead>
                <tbody>
                  {coaching.key_items.map((item, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #f1f3f5" }}>
                      <td style={{ padding: 6 }}>
                        <strong>{item.name}</strong>
                        <br /><span style={{ color: "#868e96", fontSize: 12 }}>{item.slot}</span>
                      </td>
                      <td style={{ padding: 6 }}>{item.importance}</td>
                      <td style={{ padding: 6, color: item.ssf_difficulty === "어려움" ? "#e03131" : item.ssf_difficulty === "보통" ? "#f59f00" : "#2b8a3e" }}>
                        {item.ssf_difficulty}
                      </td>
                      <td style={{ padding: 6, fontSize: 12 }}>
                        {item.acquisition}
                        {item.alternatives?.length > 0 && (
                          <div style={{ color: "#868e96", marginTop: 2 }}>대체: {item.alternatives.join(", ")}</div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {/* 패시브 우선순위 */}
          <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
            <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>패시브 트리 우선순위</h3>
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {coaching.passive_priority.map((p, i) => <li key={i} style={{ marginBottom: 4 }}>{p}</li>)}
            </ol>
          </section>

          {/* 맵 모드 경고 */}
          {coaching.map_mod_warnings && (coaching.map_mod_warnings.deadly?.length > 0 || coaching.map_mod_warnings.dangerous?.length > 0) && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 10px", fontSize: 15, color: "#e03131" }}>맵 모드 경고</h3>
              <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
                {coaching.map_mod_warnings.deadly?.length > 0 && (
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "#e03131", marginBottom: 4 }}>금지</div>
                    <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
                      {coaching.map_mod_warnings.deadly.map((m, i) => <li key={i}>{m}</li>)}
                    </ul>
                  </div>
                )}
                {coaching.map_mod_warnings.dangerous?.length > 0 && (
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "#f59f00", marginBottom: 4 }}>주의</div>
                    <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
                      {coaching.map_mod_warnings.dangerous.map((m, i) => <li key={i}>{m}</li>)}
                    </ul>
                  </div>
                )}
                {coaching.map_mod_warnings.caution?.length > 0 && (
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "#868e96", marginBottom: 4 }}>참고</div>
                    <ul style={{ margin: 0, paddingLeft: 16, fontSize: 13 }}>
                      {coaching.map_mod_warnings.caution.map((m, i) => <li key={i}>{m}</li>)}
                    </ul>
                  </div>
                )}
              </div>
              {coaching.map_mod_warnings.regex_filter && (
                <div style={{ padding: 8, background: "#f8f9fa", borderRadius: 4, fontSize: 12, fontFamily: "monospace" }}>
                  <span style={{ color: "#868e96" }}>regex: </span>
                  <code style={{ userSelect: "all", color: "#228be6" }}>{coaching.map_mod_warnings.regex_filter}</code>
                </div>
              )}
            </section>
          )}

          {/* 위험 & 파밍 */}
          <div style={{ display: "flex", gap: 12 }}>
            {coaching.danger_zones?.length > 0 && (
              <section style={{ flex: 1, padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
                <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#e03131" }}>위험 요소</h3>
                <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13 }}>
                  {coaching.danger_zones.map((d, i) => <li key={i}>{d}</li>)}
                </ul>
              </section>
            )}
            <section style={{ flex: 1, padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#2b8a3e" }}>파밍 전략</h3>
              <p style={{ margin: 0, fontSize: 13 }}>{coaching.farming_strategy}</p>
            </section>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
