import { useState } from "react";
import { space, radius, font } from "../theme";

export interface VerbalBuildInput {
  class: string;
  ascendancy: string;
  level: number;
  mainSkill: string;
  supports: string[];
  secondarySkills: string[];
  notes: string;
}

interface Props {
  loading: string;
  onSubmit: (input: VerbalBuildInput) => void;
  onCancel: () => void;
}

const POE2_CLASSES = [
  "Warrior", "Monk", "Ranger", "Mercenary",
  "Sorceress", "Witch", "Huntress", "Druid",
];

const POE2_ASCENDANCIES: Record<string, string[]> = {
  Warrior: ["Titan", "Warbringer", "Smith of Kitava"],
  Monk: ["Invoker", "Acolyte of Chayula"],
  Ranger: ["Deadeye", "Pathfinder"],
  Mercenary: ["Witchhunter", "Gemling Legionnaire", "Tactician"],
  Sorceress: ["Stormweaver", "Chronomancer", "Disciple of Varashta"],
  Witch: ["Infernalist", "Blood Mage", "Lich", "Abyssal Lich"],
  Huntress: ["Amazon", "Ritualist"],
  Druid: ["Shaman", "Oracle"],
};

/**
 * POE2 전용 — POB 없이 구두/폼으로 빌드 정보를 직접 입력해 코치 분석 요청.
 * D6 + L2 + L3 파이프라인 위에서 PoB2 없는 사용자 경로 제공.
 *
 * POE1 은 이미 POB URL 입력이 메인 경로 (`PobInputSection`) 로 정착해 구두 입력
 * 필요가 없음. 호출부 `App.tsx` 는 `game === "poe2"` 에서만 이 컴포넌트를 렌더.
 * POE1 fallback 경로는 의도적으로 제공하지 않음 — PoB2 fork 포맷 확정(D1) 전까지의
 * POE2 임시 우회로라는 스코프가 분명해야 기능 경계가 깨지지 않음.
 */
export function VerbalBuildInputSection({ loading, onSubmit, onCancel }: Props) {
  const [charClass, setCharClass] = useState("Huntress");
  const [ascendancy, setAscendancy] = useState("Amazon");
  const [level, setLevel] = useState(45);
  const [mainSkill, setMainSkill] = useState("");
  const [supportsRaw, setSupportsRaw] = useState("");
  const [secondaryRaw, setSecondaryRaw] = useState("");
  const [notes, setNotes] = useState("");

  const ascendancyOptions = charClass ? POE2_ASCENDANCIES[charClass] ?? [] : [];
  const classOptions = POE2_CLASSES;

  function handleSubmit() {
    const supports = supportsRaw
      .split(/[,\n]/)
      .map((s) => s.trim())
      .filter(Boolean);
    const secondarySkills = secondaryRaw
      .split(/[,\n]/)
      .map((s) => s.trim())
      .filter(Boolean);
    onSubmit({
      class: charClass.trim(),
      ascendancy: ascendancy.trim(),
      level,
      mainSkill: mainSkill.trim(),
      supports,
      secondarySkills,
      notes: notes.trim(),
    });
  }

  const canSubmit = charClass && mainSkill && !loading;

  return (
    <section className="ui-card" style={{ padding: space.lg, marginBottom: space.lg }}>
      <h3 className="ui-section-title" style={{ marginTop: 0 }}>
        구두 빌드 입력 <span className="ui-section-title__hint">(POB 없이 직접 폼)</span>
      </h3>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: space.md }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm }}>
          <span style={{ fontWeight: 600 }}>클래스</span>
          <select
            value={charClass}
            onChange={(e) => {
              setCharClass(e.target.value);
              setAscendancy(POE2_ASCENDANCIES[e.target.value]?.[0] ?? "");
            }}
            style={selectStyle}
          >
            <option value="">선택...</option>
            {classOptions.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm }}>
          <span style={{ fontWeight: 600 }}>어센던시</span>
          {ascendancyOptions.length > 0 ? (
            <select value={ascendancy} onChange={(e) => setAscendancy(e.target.value)} style={selectStyle}>
              <option value="">선택...</option>
              {ascendancyOptions.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          ) : (
            <input type="text" value={ascendancy} onChange={(e) => setAscendancy(e.target.value)} style={inputStyle} />
          )}
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm }}>
          <span style={{ fontWeight: 600 }}>현재 레벨</span>
          <input
            type="number"
            min={1}
            max={100}
            value={level}
            onChange={(e) => setLevel(Math.max(1, Math.min(100, parseInt(e.target.value) || 1)))}
            style={inputStyle}
          />
        </label>
      </div>

      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm, marginTop: space.md }}>
        <span style={{ fontWeight: 600 }}>메인 스킬 <span className="ui-text-danger">*</span></span>
        <input
          type="text"
          placeholder="예: Twister / Rake / Lightning Arrow"
          value={mainSkill}
          onChange={(e) => setMainSkill(e.target.value)}
          style={inputStyle}
        />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm, marginTop: space.md }}>
        <span style={{ fontWeight: 600 }}>서포트 젬 (쉼표/줄바꿈 구분)</span>
        <textarea
          rows={2}
          placeholder="예: Chance to Bleed Support, Retreating Assault Support, Deep Cuts Support"
          value={supportsRaw}
          onChange={(e) => setSupportsRaw(e.target.value)}
          style={{ ...inputStyle, resize: "vertical", fontFamily: "var(--font-mono)" }}
        />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm, marginTop: space.md }}>
        <span style={{ fontWeight: 600 }}>보조 스킬 (선택)</span>
        <textarea
          rows={2}
          placeholder="예: Whirling Slash, Whirlwind Lance, Herald of Blood"
          value={secondaryRaw}
          onChange={(e) => setSecondaryRaw(e.target.value)}
          style={{ ...inputStyle, resize: "vertical", fontFamily: "var(--font-mono)" }}
        />
      </label>

      <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: font.sm, marginTop: space.md }}>
        <span style={{ fontWeight: 600 }}>자유 설명 (선택)</span>
        <textarea
          rows={3}
          placeholder="빌드 방향, 현재 막힌 부분, 하고 싶은 질문 등 자유롭게"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          style={{ ...inputStyle, resize: "vertical" }}
        />
      </label>

      <div style={{ display: "flex", gap: space.md, marginTop: space.lg }}>
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="ui-button ui-button--primary"
          style={{ padding: "10px 20px", fontSize: font.lg, fontWeight: 600 }}
        >
          {loading || "코치 분석 요청"}
        </button>
        {loading && (
          <button
            onClick={onCancel}
            className="ui-button ui-button--secondary"
            style={{ padding: "10px 20px", fontSize: font.lg, fontWeight: 600 }}
          >
            정지
          </button>
        )}
      </div>

      {!charClass && (
        <div className="ui-text-muted" style={{ fontSize: font.sm, marginTop: space.sm }}>
          클래스 + 메인 스킬은 필수.
        </div>
      )}
    </section>
  );
}

const inputStyle: React.CSSProperties = {
  padding: "8px 10px",
  borderRadius: radius.sm,
  border: "1px solid var(--border-default)",
  fontSize: font.md,
  boxSizing: "border-box",
  width: "100%",
};

const selectStyle: React.CSSProperties = { ...inputStyle };
