import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { BuildData, CoachResult } from "./types";
import { BuildRatingSection } from "./components/BuildRating";
import { VariantTabs } from "./components/VariantTabs";
import { GearTimeline } from "./components/GearTimeline";
import { MapWarnings } from "./components/MapWarnings";
import { FilterPanel } from "./components/FilterPanel";

const tierColor: Record<string, string> = {
  S: "#ff6b6b", A: "#ffa94d", B: "#69db7c", C: "#74c0fc", D: "#868e96",
};

function App() {
  const [pobLink, setPobLink] = useState("");
  const [buildData, setBuildData] = useState<BuildData | null>(null);
  const [coaching, setCoaching] = useState<CoachResult | null>(null);
  const [rawBuildJson, setRawBuildJson] = useState("");
  const [rawCoachJson, setRawCoachJson] = useState("");
  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const [patchStatus, setPatchStatus] = useState("");

  async function analyzeBuild() {
    setError("");
    setBuildData(null);
    setCoaching(null);
    setRawBuildJson("");
    setRawCoachJson("");

    const trimmed = pobLink.trim();
    if (!trimmed) return;

    setLoading("POB 파싱 중...");
    try {
      const raw = await invoke<string>("parse_pob", { link: trimmed });
      const parsed: BuildData = JSON.parse(raw);
      setBuildData(parsed);
      setRawBuildJson(raw);

      setLoading("AI 코치 분석 중...");
      const coachRaw = await invoke<string>("coach_build", { buildJson: raw });
      setCoaching(JSON.parse(coachRaw));
      setRawCoachJson(coachRaw);
      setLoading("");
    } catch (e) {
      setError(String(e));
      setLoading("");
    }
  }

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
    <main style={{ padding: "1.5rem", fontFamily: "Pretendard, sans-serif", maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1 style={{ fontSize: "1.5rem", margin: 0 }}>PathcraftAI — Build Coach</h1>
        <button onClick={updatePatchNotes} disabled={patchStatus === "수집 중..."} style={{
          padding: "4px 10px", borderRadius: 4, border: "1px solid #dee2e6",
          background: "#f8f9fa", fontSize: 11, cursor: "pointer", color: "#495057",
        }}>
          {patchStatus || "패치노트 갱신"}
        </button>
      </div>

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

          <BuildRatingSection rating={coaching.build_rating} />
          <VariantTabs snapshots={coaching.variant_snapshots} />

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
                <div style={{ fontSize: 13, marginTop: 4 }}>링크: {coaching.leveling_skills.recommended.links}</div>
                <div style={{ fontSize: 13, color: "#495057" }}>
                  {coaching.leveling_skills.recommended.reason}
                  {coaching.leveling_skills.recommended.transition_level && (
                    <span> — 전환: Lv.{coaching.leveling_skills.recommended.transition_level}</span>
                  )}
                </div>
              </div>
              {coaching.leveling_skills.options?.length > 0 && (
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
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

          {/* 오라/유틸리티 */}
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

          <GearTimeline progression={coaching.gear_progression} />

          {/* 핵심 장비 폴백 */}
          {(!coaching.gear_progression || coaching.gear_progression.length === 0) && coaching.key_items?.length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>핵심 장비 (SSF 획득)</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #dee2e6", textAlign: "left" }}>
                    <th style={{ padding: 6 }}>아이템</th><th style={{ padding: 6 }}>중요도</th>
                    <th style={{ padding: 6 }}>SSF 난이도</th><th style={{ padding: 6 }}>획득 방법</th>
                  </tr>
                </thead>
                <tbody>
                  {coaching.key_items.map((item, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #f1f3f5" }}>
                      <td style={{ padding: 6 }}><strong>{item.name}</strong><br /><span style={{ color: "#868e96", fontSize: 12 }}>{item.slot}</span></td>
                      <td style={{ padding: 6 }}>{item.importance}</td>
                      <td style={{ padding: 6, color: item.ssf_difficulty === "어려움" ? "#e03131" : item.ssf_difficulty === "보통" ? "#f59f00" : "#2b8a3e" }}>{item.ssf_difficulty}</td>
                      <td style={{ padding: 6, fontSize: 12 }}>{item.acquisition}{item.alternatives?.length > 0 && <div style={{ color: "#868e96", marginTop: 2 }}>대체: {item.alternatives.join(", ")}</div>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}

          {/* 패시브 */}
          <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
            <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>패시브 트리 우선순위</h3>
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {coaching.passive_priority.map((p, i) => <li key={i} style={{ marginBottom: 4 }}>{p}</li>)}
            </ol>
          </section>

          <MapWarnings warnings={coaching.map_mod_warnings} />

          {/* 위험 요소 */}
          {coaching.danger_zones?.length > 0 && (
            <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#e03131" }}>위험 요소</h3>
              <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13 }}>
                {coaching.danger_zones.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </section>
          )}

          {/* 파밍 전략 */}
          {coaching.farming_strategy && (
            typeof coaching.farming_strategy === "string" ? (
              <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
                <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#2b8a3e" }}>파밍 전략</h3>
                <p style={{ margin: 0, fontSize: 13 }}>{coaching.farming_strategy}</p>
              </section>
            ) : (
              <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
                <h3 style={{ margin: "0 0 8px", fontSize: 15, color: "#2b8a3e" }}>파밍 전략</h3>

                {coaching.farming_strategy.recommended_mechanics?.length > 0 && (
                  <div style={{ marginBottom: 12 }}>
                    <strong style={{ fontSize: 13 }}>추천 메카닉</strong>
                    <div style={{ display: "flex", gap: 6, marginTop: 4, flexWrap: "wrap" }}>
                      {coaching.farming_strategy.recommended_mechanics.map((m, i) => (
                        <span key={i} style={{
                          padding: "3px 10px", borderRadius: 12, fontSize: 12, fontWeight: 600,
                          background: i === 0 ? "#d3f9d8" : "#e7f5ff",
                          color: i === 0 ? "#2b8a3e" : "#1971c2",
                        }}>{m}</span>
                      ))}
                    </div>
                  </div>
                )}

                {coaching.farming_strategy.atlas_passive_focus && (
                  <div style={{ marginBottom: 10, padding: 8, background: "#f8f9fa", borderRadius: 6, fontSize: 13 }}>
                    <strong>아틀라스 패시브:</strong> {coaching.farming_strategy.atlas_passive_focus}
                  </div>
                )}

                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <tbody>
                    {coaching.farming_strategy.early_atlas && (
                      <tr style={{ borderBottom: "1px solid #f1f3f5" }}>
                        <td style={{ padding: 6, fontWeight: 600, whiteSpace: "nowrap", color: "#868e96" }}>초반</td>
                        <td style={{ padding: 6 }}>{coaching.farming_strategy.early_atlas}</td>
                      </tr>
                    )}
                    {coaching.farming_strategy.mid_atlas && (
                      <tr style={{ borderBottom: "1px solid #f1f3f5" }}>
                        <td style={{ padding: 6, fontWeight: 600, whiteSpace: "nowrap", color: "#868e96" }}>중반</td>
                        <td style={{ padding: 6 }}>{coaching.farming_strategy.mid_atlas}</td>
                      </tr>
                    )}
                    {coaching.farming_strategy.late_atlas && (
                      <tr style={{ borderBottom: "1px solid #f1f3f5" }}>
                        <td style={{ padding: 6, fontWeight: 600, whiteSpace: "nowrap", color: "#868e96" }}>후반</td>
                        <td style={{ padding: 6 }}>{coaching.farming_strategy.late_atlas}</td>
                      </tr>
                    )}
                    {coaching.farming_strategy.ssf_crafting_focus && (
                      <tr>
                        <td style={{ padding: 6, fontWeight: 600, whiteSpace: "nowrap", color: "#868e96" }}>크래프팅</td>
                        <td style={{ padding: 6 }}>{coaching.farming_strategy.ssf_crafting_focus}</td>
                      </tr>
                    )}
                  </tbody>
                </table>

                {coaching.farming_strategy.scarab_priority?.length > 0 && (
                  <div style={{ marginTop: 8, fontSize: 12, color: "#868e96" }}>
                    스카랍: {coaching.farming_strategy.scarab_priority.join(", ")}
                  </div>
                )}
              </section>
            )
          )}

          {/* 필터 생성 */}
          {rawBuildJson && (
            <FilterPanel buildJson={rawBuildJson} coachingJson={rawCoachJson} />
          )}
        </div>
      )}
    </main>
  );
}

export default App;
