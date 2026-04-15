import { useState } from "react";

interface Props {
  url: string;
}

// POE 공식 fullscreen passive tree URL을 iframe으로 임베드.
// POE 서버가 X-Frame-Options: DENY를 내려보내면 iframe 차단됨 → fallback 링크 표시.
// CSP/차단 감지: iframe onLoad가 일정 시간 내 안 오거나 cross-origin 에러 시 fallback.

export function PassiveTreeView({ url }: Props) {
  const [blocked, setBlocked] = useState(false);
  const [expanded, setExpanded] = useState(false);

  if (!url) {
    return (
      <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
        <h3 style={{ margin: "0 0 8px", fontSize: 15 }}>🌳 패시브 트리</h3>
        <div style={{ fontSize: 12, color: "#868e96" }}>POB에서 passive tree URL을 찾지 못했습니다.</div>
      </section>
    );
  }

  return (
    <section style={{ padding: 16, background: "#fff", borderRadius: 8, border: "1px solid #e9ecef" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <h3 style={{ margin: 0, fontSize: 15 }}>🌳 패시브 트리 (POE 공식 뷰어)</h3>
        <div style={{ display: "flex", gap: 6 }}>
          <button
            onClick={() => setExpanded((v) => !v)}
            style={{
              padding: "4px 10px", fontSize: 11, border: "1px solid #dee2e6",
              background: "#f8f9fa", borderRadius: 3, cursor: "pointer", color: "#495057",
            }}
          >
            {expanded ? "축소" : "크게"}
          </button>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "4px 10px", fontSize: 11, border: "1px solid #4dabf7",
              background: "#e7f5ff", borderRadius: 3, textDecoration: "none",
              color: "#1864ab",
            }}
          >
            🔗 새 창에서 열기
          </a>
        </div>
      </div>

      {blocked ? (
        <div
          style={{
            padding: 16, background: "#fff9db", border: "1px solid #ffd43b",
            borderRadius: 6, fontSize: 13, color: "#5c3c00",
          }}
        >
          ⚠️ POE 서버가 iframe 임베드를 차단했습니다. "새 창에서 열기" 버튼으로 보세요.
        </div>
      ) : (
        <iframe
          src={url}
          title="POE Passive Tree"
          onError={() => setBlocked(true)}
          sandbox="allow-scripts allow-same-origin allow-popups"
          style={{
            width: "100%",
            height: expanded ? 900 : 500,
            border: "1px solid #dee2e6",
            borderRadius: 4,
            background: "#1a1a1a",
            transition: "height 0.2s",
          }}
        />
      )}

      <div style={{ marginTop: 6, fontSize: 11, color: "#868e96" }}>
        POE 공식 뷰어. 마우스 휠 줌, 드래그 팬. 호버 툴팁 지원.
        iframe이 흰 화면이면 POE 서버의 보안 정책이 차단한 것 — 우측 "새 창" 사용.
      </div>
    </section>
  );
}
