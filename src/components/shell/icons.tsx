/**
 * Sidebar 용 인라인 SVG 아이콘. Lucide(ISC) path 차용.
 * - React 19와 lucide-react peer 충돌 회피 (--force 룰 위반 방지)
 * - 4개만 필요해서 자체 인라인
 * - 추가 아이콘 필요 시 lucide.dev에서 path 복사
 */

interface IconProps {
  size?: number;
  strokeWidth?: number;
  className?: string;
}

const baseProps = (size: number, strokeWidth: number) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
});

// Lucide: hammer
export function BuildIcon({ size = 16, strokeWidth = 2, className }: IconProps) {
  return (
    <svg {...baseProps(size, strokeWidth)} className={className}>
      <path d="m15 12-8.373 8.373a1 1 0 1 1-3-3L12 9" />
      <path d="m18 15 4-4" />
      <path d="m21.5 11.5-1.914-1.914A2 2 0 0 1 19 8.172V7l-2.26-2.26a6 6 0 0 0-4.202-1.756L9 2.96l.92.82A6.18 6.18 0 0 1 12 8.4V10l2 2h1.172a2 2 0 0 1 1.414.586L18.5 14.5" />
    </svg>
  );
}

// Lucide: network
export function SyndicateIcon({ size = 16, strokeWidth = 2, className }: IconProps) {
  return (
    <svg {...baseProps(size, strokeWidth)} className={className}>
      <rect x="16" y="16" width="6" height="6" rx="1" />
      <rect x="2" y="16" width="6" height="6" rx="1" />
      <rect x="9" y="2" width="6" height="6" rx="1" />
      <path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3" />
      <path d="M12 12V8" />
    </svg>
  );
}

// Lucide: git-branch (패시브 트리 분기 의미)
export function PassiveIcon({ size = 16, strokeWidth = 2, className }: IconProps) {
  return (
    <svg {...baseProps(size, strokeWidth)} className={className}>
      <line x1="6" y1="3" x2="6" y2="15" />
      <circle cx="18" cy="6" r="3" />
      <circle cx="6" cy="18" r="3" />
      <path d="M18 9a9 9 0 0 1-9 9" />
    </svg>
  );
}

// Lucide: picture-in-picture-2 (오버레이 의미)
export function OverlayIcon({ size = 16, strokeWidth = 2, className }: IconProps) {
  return (
    <svg {...baseProps(size, strokeWidth)} className={className}>
      <path d="M21 9V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h7" />
      <rect x="12" y="13" width="10" height="8" rx="2" />
    </svg>
  );
}
