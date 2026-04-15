/**
 * PathcraftAI UI 디자인 토큰.
 * 인라인 스타일 하드코딩 제거 — 중앙에서 브랜드/색상/간격 관리.
 */

export const colors = {
  // 주요 (1단계 POB, 분석 버튼)
  primary: "#228be6",
  primaryDark: "#1971c2",
  primaryLight: "#e7f5ff",

  // 보조 (2단계 POB, Multi-POB 배지)
  secondary: "#f76707",
  secondaryDark: "#9c3d00",
  secondaryLight: "#fff4e6",

  // 상태
  success: "#2b8a3e",
  successLight: "#d3f9d8",
  successDim: "#ebfbee",
  warning: "#f59f00",
  warningLight: "#fff9db",
  warningDark: "#5c3c00",
  danger: "#e03131",
  dangerLight: "#fff5f5",
  info: "#7048e8",
  infoLight: "#f3f0ff",

  // 그레이스케일
  text: "#495057",
  textMuted: "#868e96",
  textLight: "#adb5bd",
  border: "#dee2e6",
  borderLight: "#e9ecef",
  borderSoft: "#f1f3f5",
  bg: "#fff",
  bgSoft: "#f8f9fa",
  bgFaded: "#fafbfc",

  // Syndicate 분과 색
  syndicate: {
    transportation: { bg: "#fff4e6", text: "#d9480f", border: "#fd7e14" },
    fortification: { bg: "#e7f5ff", text: "#1864ab", border: "#339af0" },
    research: { bg: "#f3f0ff", text: "#5f3dc4", border: "#7950f2" },
    intervention: { bg: "#fff5f5", text: "#c92a2a", border: "#fa5252" },
  },

  // Tier 색 (S/A/B/C/D)
  tier: {
    S: "#ff6b6b", A: "#ffa94d", B: "#69db7c", C: "#74c0fc", D: "#868e96",
  },
} as const;

export const space = {
  xs: 4, sm: 6, md: 8, lg: 12, xl: 16, xxl: 24,
} as const;

export const radius = {
  sm: 4, md: 6, lg: 8, full: 9999,
} as const;

export const font = {
  xs: 10, sm: 11, md: 12, base: 13, lg: 14, xl: 15, xxl: 16,
  h1: 24, h2: 18, h3: 15,
} as const;

// 반응형 breakpoints
export const breakpoints = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
} as const;

// 미디어 쿼리 helper (CSS-in-JS 용)
export const mq = {
  mobile: `@media (max-width: ${breakpoints.mobile}px)`,
  tablet: `@media (max-width: ${breakpoints.tablet}px)`,
} as const;
