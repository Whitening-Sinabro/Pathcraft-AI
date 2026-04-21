/**
 * Syndicate 전용 인라인 SVG 아이콘 — POE 게임 미감 참조.
 * 원본: 직접 작성. 이모지(👑/✓) 대체.
 *
 * 디자인 원칙:
 *  - 각진 엣지 (POE 아이템 프레임 / 스킬 젬 스타일)
 *  - filled + outline 병용
 *  - 크라운: 5-peak medieval, 중앙 peak 가장 높음
 *  - seal: 육각형(커런시 오브 형태) + 내부 체크
 */

interface IconProps {
  size?: number;
  className?: string;
  title?: string;
}

// POE 5-peak 크라운 — Leader 슬롯 표시
// 중앙 peak 최고점 + 양옆 단계적 하강 + 하단 밴드
export function CrownIcon({ size = 14, className, title }: IconProps) {
  const a11y = title ? { role: "img" as const, "aria-label": title } : { "aria-hidden": true as const };
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={className}
      {...a11y}
    >
      {title ? <title>{title}</title> : null}
      {/* 크라운 본체 — 5 peak, 각진 엣지 */}
      <path
        d="M2.5 18 L5 8 L8.5 13 L12 3 L15.5 13 L19 8 L21.5 18 L2.5 18 Z"
        fill="currentColor"
        stroke="currentColor"
        strokeWidth="0.5"
        strokeLinejoin="miter"
      />
      {/* 하단 밴드 */}
      <path
        d="M2.5 18 L21.5 18 L21 21 L3 21 Z"
        fill="currentColor"
        stroke="currentColor"
        strokeWidth="0.5"
        strokeLinejoin="miter"
      />
      {/* peak 내부 보석 홈 */}
      <circle cx="5" cy="8" r="0.8" fill="none" stroke="var(--bg-panel)" strokeWidth="0.6" />
      <circle cx="12" cy="3" r="1" fill="none" stroke="var(--bg-panel)" strokeWidth="0.6" />
      <circle cx="19" cy="8" r="0.8" fill="none" stroke="var(--bg-panel)" strokeWidth="0.6" />
      {/* 밴드 구분선 */}
      <path
        d="M3 19.5 L21 19.5"
        stroke="var(--bg-panel)"
        strokeWidth="0.6"
        opacity="0.6"
      />
    </svg>
  );
}

// POE 육각형 seal — 확정/저장 표시 (커런시 오브 / 프래그먼트 형태 차용)
export function CheckSealIcon({ size = 14, className, title }: IconProps) {
  const a11y = title ? { role: "img" as const, "aria-label": title } : { "aria-hidden": true as const };
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={className}
      {...a11y}
    >
      {title ? <title>{title}</title> : null}
      {/* 육각형 외곽 (POE currency orb shape) */}
      <path
        d="M12 2 L21 7 L21 17 L12 22 L3 17 L3 7 Z"
        fill="currentColor"
        fillOpacity="0.15"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="miter"
      />
      {/* 내부 각진 체크 — miter 린조인으로 날카로운 각도 */}
      <path
        d="M7.5 12.5 L10.5 15.5 L16.5 9"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinejoin="miter"
        strokeLinecap="square"
      />
    </svg>
  );
}
