import { useState } from "react";

export function SyndicateTutorial() {
  const [open, setOpen] = useState(false);

  return (
    <div
      style={{
        marginBottom: 12, borderRadius: 6,
        border: "1px solid var(--status-warning)", background: "var(--status-warning-bg)",
      }}
    >
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          width: "100%", padding: "8px 12px", textAlign: "left", border: "none",
          background: "transparent", cursor: "pointer", fontSize: 13, fontWeight: 700,
          color: "var(--status-warning)",
        }}
      >
        {open ? "▼" : "▶"} Syndicate 처음 보세요? 1분 설명서 (Mid-League 진입자용)
      </button>
      {open && (
        <div className="ui-text-secondary" style={{ padding: "0 12px 12px", fontSize: 12, lineHeight: 1.6 }}>
          <Section title="① 4가지 액션 (인카운터 후 캡처된 멤버에게)">
            <Row k="Bargain (협상)" v="멤버를 원하는 분과로 이동 + 보상 1개. Rank 변동 없음. 가장 자주 씀." />
            <Row k="Interrogate (심문)" v="Rank −1 (Member→이탈). 다른 멤버 위치 정보 노출. 원치 않는 멤버 청소용." />
            <Row k="Betray (배신)" v="본인 syndicate 이탈 + 같은 분과 다른 멤버 Rank +1. 목표 멤버를 Leader로 승격할 때." />
            <Row k="Execute (처형)" v="멤버 + 친구 1명 동시 제거 + 무작위 대형 보상. 두 명 한꺼번에 비울 때." />
          </Section>

          <Section title="② 분과 4종 (각 멤버의 보상이 달라짐)">
            <Row k="Transportation (수송)" v="카펫 보상 (맵에 영구 트랩) — 멤버 보상이 자동 누적." />
            <Row k="Fortification (방어)" v="장비 강화 — Leader가 보상을 직접 인챈트 (Elreon 레지 등)." />
            <Row k="Research (연구)" v="벤치 크래프팅 — Aisling Veiled T4 = mirror-tier 크래프팅의 핵심." />
            <Row k="Intervention (개입)" v="직접 드롭 — Cameria Currency Scarab + Mirror Shard." />
          </Section>

          <Section title="③ Rank 시스템">
            <Row k="Member (1)" v="기본 등급. Bargain으로 분과 이동 시 Rank 유지." />
            <Row k="Leader (2)" v="해당 분과 보상 지배. 같은 분과 다른 멤버를 Betray하면 승격." />
            <Row k="Mastermind (3)" v="Catarina (전체 1명). 4 분과 합쳐 Leader 7명 등장 후 트리거." />
          </Section>

          <Section title="④ 자주 쓰는 약어">
            <Row k="SS22 / 5522" v="2-Safehouse Standard. 2개 safehouse를 풀(4명)로 채움. Leader 2 + Member 6 분포." />
            <Row k="Aisling T4" v="Aisling Research Leader → Veiled mod T4 크래프팅 반복. Mirror-tier 빌드 핵심." />
            <Row k="Mastermind farm" v="Catarina 주기적 캐치 → 모든 멤버 보상 한번에 트리거." />
            <Row k="Gravicius+Cameria" v="Currency 페어 — Transportation Gravicius + Intervention Cameria 동시 운용." />
          </Section>

          <Section title="⑤ 빠른 시작 (Mid-League 진입자)">
            <ol style={{ margin: "4px 0", paddingLeft: 18 }}>
              <li>위 보드에서 프리셋 1개 선택 (예: SS22) → 목표 레이아웃 표시.</li>
              <li>아래 "현재 인게임 상태"에 본인의 실제 syndicate 입력.</li>
              <li>"다음 액션 추천"이 우선순위별로 무엇을 할지 알려줌.</li>
              <li>인카운터마다 추천 따라 액션 → 목표에 점진 수렴.</li>
            </ol>
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 8 }}>
      <div className="ui-text-warning" style={{ fontWeight: 700, fontSize: 12, marginBottom: 2 }}>{title}</div>
      {children}
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div style={{ marginLeft: 8, marginBottom: 2 }}>
      <strong>{k}</strong> — <span className="ui-text-secondary">{v}</span>
    </div>
  );
}
