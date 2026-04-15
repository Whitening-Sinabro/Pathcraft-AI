import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { BuildData, CoachResult } from "./types";
import { BuildRatingSection } from "./components/BuildRating";
import { VariantTabs } from "./components/VariantTabs";
import { GearTimeline } from "./components/GearTimeline";
import { MapWarnings } from "./components/MapWarnings";
import { FilterPanel } from "./components/FilterPanel";
import { SyndicateBoard } from "./components/SyndicateBoard";
import { PobInputSection } from "./components/PobInputSection";
import { colors, space, radius, font } from "./theme";

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

  // Multi-POB 확장 — 보조 빌드 링크 (필터 생성 시 union/stage 자동 분기)
  const [extraPobLinks, setExtraPobLinks] = useState<string[]>([]);
  const [extraBuildJsons, setExtraBuildJsons] = useState<string[]>([]);
  // Stage 모드 기본 ON — 2+ POB 시 Lv 차이로 레벨링/엔드게임 자동 분기
  const [stageMode, setStageMode] = useState(true);
  // 2-POB 전환 AL (기본 67 = Kitava 후). 사용자가 실제 전환 시점에 맞게 조절 가능.
  const [alSplit, setAlSplit] = useState(67);

  // Syndicate 레이아웃 AI 추천
  const [syndicateRec, setSyndicateRec] = useState<{ layout_id: string; reason: string } | null>(null);

  // 메인 탭 (build / syndicate) — localStorage 영속
  const [activeTab, setActiveTab] = useState<"build" | "syndicate">(() => {
    try {
      const saved = localStorage.getItem("pathcraftai_active_tab");
      return saved === "syndicate" ? "syndicate" : "build";
    } catch {
      return "build";
    }
  });
  function switchTab(tab: "build" | "syndicate") {
    setActiveTab(tab);
    try { localStorage.setItem("pathcraftai_active_tab", tab); } catch { /* ignore */ }
  }

  // 진행도 체크 (빌드명 기준 localStorage 영속화)
  const [checked, setChecked] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem("pathcraftai_progress");
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  const toggleCheck = (key: string) => {
    setChecked((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      try {
        localStorage.setItem("pathcraftai_progress", JSON.stringify(next));
      } catch { /* quota full, ignore */ }
      return next;
    });
  };
  const buildKey = buildData?.meta?.build_name || "build";
  const ck = (suffix: string) => `${buildKey}::${suffix}`;

  // 간단 hash (POB raw JSON → 32-bit int)
  function hashString(s: string): string {
    let h = 0;
    for (let i = 0; i < s.length; i++) {
      h = ((h << 5) - h + s.charCodeAt(i)) | 0;
    }
    return h.toString(36);
  }

  async function analyzeBuild() {
    setError("");
    setBuildData(null);
    setCoaching(null);
    setRawBuildJson("");
    setRawCoachJson("");
    setExtraBuildJsons([]);

    const trimmed = pobLink.trim();
    if (!trimmed) return;

    try {
      setLoading("1번 POB 파싱 중...");
      const raw = await invoke<string>("parse_pob", { link: trimmed });
      const parsed: BuildData = JSON.parse(raw);
      setBuildData(parsed);
      setRawBuildJson(raw);

      // 보조 POB 자동 파싱 (있으면, 병렬)
      const extras = extraPobLinks.map((l) => l.trim()).filter(Boolean);
      let parsedExtras: string[] = [];
      if (extras.length > 0) {
        setLoading(`2단계 POB ${extras.length}개 병렬 파싱 중...`);
        parsedExtras = await Promise.all(
          extras.map((link) => invoke<string>("parse_pob", { link }))
        );
        setExtraBuildJsons(parsedExtras);
      }

      // AI 코치에 4-stage 전체 progression 전달 — 1단계 + 2단계 POB의 skills/gears를 함께 보게 함
      const coachInput = JSON.stringify({
        ...parsed,
        __extra_builds__: parsedExtras.map((j) => JSON.parse(j)),
      });

      // Coach 캐시 — 전체 입력(extras 포함) hash로 키 생성
      const cacheKey = `pathcraftai_coach_${hashString(coachInput)}`;
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        setLoading("캐시 적중 — 이전 분석 결과 로드 중...");
        try {
          setCoaching(JSON.parse(cached));
          setRawCoachJson(cached);
          setLoading("");
          return;
        } catch {
          // 캐시 파싱 실패 시 새로 요청
        }
      }

      // POB 개수별 예상 시간 (경험적 수치)
      const totalPobs = parsedExtras.length + 1;
      const estMin = 20 + totalPobs * 15;  // 1 POB=35s, 2=50s, 3=65s, 4=80s
      const estMax = 40 + totalPobs * 25;
      setLoading(
        `AI 코치 분석 중 (POB ${totalPobs}개 통합) — 예상 ${estMin}~${estMax}초. ` +
        `POB가 많을수록 컨텍스트가 커져 오래 걸립니다. 창 닫지 말고 대기하세요.`
      );
      const coachStartTs = Date.now();
      const coachRaw = await invoke<string>("coach_build", { buildJson: coachInput });
      const coachSec = Math.round((Date.now() - coachStartTs) / 1000);
      console.info(`[coach] ${totalPobs} POB(s) completed in ${coachSec}s`);
      setCoaching(JSON.parse(coachRaw));
      setRawCoachJson(coachRaw);
      try {
        localStorage.setItem(cacheKey, coachRaw);
      } catch { /* quota, ignore */ }

      // Syndicate 레이아웃 추천 (휴리스틱, <1초)
      try {
        const synRaw = await invoke<string>("syndicate_recommend", { buildJson: raw });
        const synParsed = JSON.parse(synRaw);
        if (synParsed.layout_id) {
          setSyndicateRec({ layout_id: synParsed.layout_id, reason: synParsed.reason });
        }
      } catch { /* Syndicate 추천 실패는 무시 (선택 기능) */ }

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
    <main style={{
      padding: "clamp(12px, 3vw, 24px)",
      fontFamily: "Pretendard, sans-serif",
      maxWidth: 800, margin: "0 auto",
      color: colors.text,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1 style={{ fontSize: "1.5rem", margin: 0 }}>PathcraftAI — Build Coach</h1>
        <button onClick={updatePatchNotes} disabled={patchStatus === "수집 중..."} style={{
          padding: "4px 10px", borderRadius: 4, border: "1px solid #dee2e6",
          background: "#f8f9fa", fontSize: 11, cursor: "pointer", color: "#495057",
        }}>
          {patchStatus || "패치노트 갱신"}
        </button>
      </div>

      {/* 메인 탭 */}
      <div style={{ display: "flex", gap: 4, marginBottom: 16, borderBottom: "2px solid #e9ecef" }}>
        {[
          { id: "build" as const, label: "🔨 빌드 분석" },
          { id: "syndicate" as const, label: "🎭 Syndicate" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => switchTab(t.id)}
            style={{
              padding: "8px 16px", border: "none", borderBottom: activeTab === t.id ? "3px solid #228be6" : "3px solid transparent",
              background: "transparent", cursor: "pointer", fontSize: 14,
              fontWeight: activeTab === t.id ? 700 : 400,
              color: activeTab === t.id ? "#1864ab" : "#868e96",
              marginBottom: -2,
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "syndicate" && (
        <SyndicateBoard buildJson={rawBuildJson} recommendation={syndicateRec} />
      )}

      {activeTab === "build" && <>
        <PobInputSection
        pobLink={pobLink} setPobLink={setPobLink}
        extraPobLinks={extraPobLinks} setExtraPobLinks={setExtraPobLinks}
        stageMode={stageMode} setStageMode={setStageMode}
        alSplit={alSplit} setAlSplit={setAlSplit}
        loading={loading} onAnalyze={analyzeBuild}
      />

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

      {coaching && coaching._validation_warnings && coaching._validation_warnings.length > 0 && (
        <div style={{
          padding: space.md, marginBottom: space.lg,
          background: colors.warningLight, borderRadius: radius.md,
          border: `1px solid ${colors.warning}`, fontSize: font.md, color: colors.warningDark,
        }}>
          <strong>⚠️ AI 생성 데이터 — 게임 데이터와 일부 차이</strong>
          <ul style={{ margin: "4px 0 0", paddingLeft: 20, fontSize: font.sm }}>
            {coaching._validation_warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
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
            <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>레벨링 가이드 <span style={{ fontSize: 11, fontWeight: 400, color: "#868e96" }}>(체크로 진행도 추적)</span></h3>
            {Object.entries(coaching.leveling_guide).map(([key, val]) => {
              const chkKey = ck(`lvguide_${key}`);
              const done = !!checked[chkKey];
              return (
                <div key={key} style={{ marginBottom: 8, padding: 8, borderRadius: 4, background: done ? "#ebfbee" : "transparent", opacity: done ? 0.7 : 1 }}>
                  <label style={{ display: "flex", alignItems: "flex-start", gap: 8, cursor: "pointer" }}>
                    <input type="checkbox" checked={done} onChange={() => toggleCheck(chkKey)} style={{ marginTop: 3 }} />
                    <div style={{ flex: 1 }}>
                      <strong style={{ color: done ? "#2b8a3e" : "#495057", textDecoration: done ? "line-through" : "none" }}>
                        {key === "act1_4" ? "Act 1-4" : key === "act5_10" ? "Act 5-10" : key === "early_maps" ? "초반 맵" : "엔드게임"}
                      </strong>
                      <p style={{ margin: "2px 0 0", color: "#495057", fontSize: 14 }}>{val}</p>
                    </div>
                  </label>
                </div>
              );
            })}
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
                {/* 레벨 구간별 젬 progression + 체크박스 */}
                {coaching.leveling_skills.recommended.links_progression &&
                 coaching.leveling_skills.recommended.links_progression.length > 0 ? (
                  <div style={{ marginTop: 6 }}>
                    {coaching.leveling_skills.recommended.links_progression.map((p, i) => {
                      const chkKey = ck(`rec_lv_${i}`);
                      const done = !!checked[chkKey];
                      return (
                        <label key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 3, fontSize: 13, cursor: "pointer", opacity: done ? 0.6 : 1 }}>
                          <input type="checkbox" checked={done} onChange={() => toggleCheck(chkKey)} style={{ marginTop: 3 }} />
                          <span style={{ minWidth: 130, fontWeight: 600, color: "#1971c2", fontFamily: "monospace", textDecoration: done ? "line-through" : "none" }}>
                            {p.level_range}
                          </span>
                          <span style={{ flex: 1, color: "#495057", textDecoration: done ? "line-through" : "none" }}>{p.gems.join(" + ")}</span>
                        </label>
                      );
                    })}
                  </div>
                ) : (
                  coaching.leveling_skills.recommended.links && (
                    <div style={{ fontSize: 13, marginTop: 4 }}>링크: {coaching.leveling_skills.recommended.links}</div>
                  )
                )}
                <div style={{ fontSize: 13, color: "#495057", marginTop: 6 }}>
                  {coaching.leveling_skills.recommended.reason}
                  {coaching.leveling_skills.recommended.transition_level && (
                    <span> — 전환: Lv.{coaching.leveling_skills.recommended.transition_level}</span>
                  )}
                </div>
              </div>
              {coaching.leveling_skills.options?.length > 0 && (
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {coaching.leveling_skills.options.map((opt, i) => (
                    <div key={i} style={{ padding: 10, border: "1px solid #e9ecef", borderRadius: 6, background: "#fafbfc" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                        <strong style={{ fontSize: 13 }}>{opt.name}</strong>
                        <div style={{ display: "flex", gap: 8, fontSize: 11 }}>
                          <span style={{ color: "#495057" }}>속도 <strong>{opt.speed}</strong></span>
                          <span style={{ color: opt.safety === "높음" ? "#2b8a3e" : opt.safety === "낮음" ? "#e03131" : "#f59f00" }}>
                            안전 <strong>{opt.safety}</strong>
                          </span>
                        </div>
                      </div>
                      {opt.links_progression && opt.links_progression.length > 0 ? (
                        <div style={{ marginBottom: 4 }}>
                          {opt.links_progression.map((p, j) => (
                            <div key={j} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 2, fontSize: 12 }}>
                              <span style={{ minWidth: 120, fontWeight: 600, color: "#1971c2", fontFamily: "monospace" }}>
                                {p.level_range}
                              </span>
                              <span style={{ flex: 1, color: "#495057" }}>{p.gems.join(" + ")}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        opt.links && (
                          <div style={{ color: "#868e96", fontSize: 12, marginBottom: 4 }}>{opt.links}</div>
                        )
                      )}
                      <div style={{ fontSize: 12, color: "#495057" }}>{opt.reason}</div>
                    </div>
                  ))}
                </div>
              )}
              {coaching.leveling_skills.skill_transitions?.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <strong style={{ fontSize: 13 }}>스킬 전환</strong>
                  <div style={{ marginTop: 4 }}>
                    {coaching.leveling_skills.skill_transitions.map((t, i) => {
                      const chkKey = ck(`skillt_${i}`);
                      const done = !!checked[chkKey];
                      return (
                        <label key={i} style={{ display: "flex", gap: 6, fontSize: 13, alignItems: "flex-start", marginBottom: 2, cursor: "pointer", opacity: done ? 0.6 : 1 }}>
                          <input type="checkbox" checked={done} onChange={() => toggleCheck(chkKey)} style={{ marginTop: 3 }} />
                          <span style={{ textDecoration: done ? "line-through" : "none" }}>
                            <strong>Lv.{t.level}</strong>: {t.change} — {t.reason}
                          </span>
                        </label>
                      );
                    })}
                  </div>
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

          <GearTimeline
            progression={coaching.gear_progression}
            checked={checked}
            onToggle={toggleCheck}
            buildKey={buildKey}
          />

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
            <FilterPanel
              buildJson={rawBuildJson}
              coachingJson={rawCoachJson}
              extraBuildJsons={extraBuildJsons}
              stageMode={stageMode}
              alSplit={alSplit}
            />
          )}

        </div>
      )}
      </>}
    </main>
  );
}

export default App;
