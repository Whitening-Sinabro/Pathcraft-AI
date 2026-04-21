/**
 * PathcraftAI 다크 디자인 토큰.
 *
 * 단일 진실원: `src/styles/global.css` :root.
 * 이 파일은 CSS 변수의 TypeScript alias만 제공 — 인라인 style에서
 *   `style={{ background: colors.bg.panel }}` 처럼 쓰면 var(--bg-panel) 자동 적용.
 *
 * 색을 추가/변경할 때는 global.css의 :root를 먼저 수정한 뒤 이 파일에 매핑 추가.
 *
 * 대비 검증 (bg.base 기준): WCAG AA 이상 통과.
 *   text.primary 15.44 / text.secondary 7.49 / text.muted 6.01
 *   accent.primary 5.39 / rarity.unique 7.51 / tier.s 6.98
 */

const v = (name: string) => `var(--${name})`;

export const colors = {
  bg: {
    base:     v("bg-base"),
    panel:    v("bg-panel"),
    elevated: v("bg-elevated"),
    overlay:  v("bg-overlay"),
  },
  border: {
    default: v("border-default"),
    strong:  v("border-strong"),
    gold:    v("border-gold"),
  },
  text: {
    primary:   v("text-primary"),
    secondary: v("text-secondary"),
    muted:     v("text-muted"),
    onAccent:  v("text-on-accent"),
  },
  accent: {
    primary: v("accent-primary"),
    hover:   v("accent-hover"),
    subtle:  v("accent-subtle"),
  },
  rarity: {
    normal: v("rarity-normal"),
    magic:  v("rarity-magic"),
    rare:   v("rarity-rare"),
    unique: v("rarity-unique"),
  },
  tier: {
    s: v("tier-s"),
    a: v("tier-a"),
    b: v("tier-b"),
    c: v("tier-c"),
    d: v("tier-d"),
  },
  status: {
    success:       v("status-success"),
    successSubtle: v("status-success-bg"),
    warning:       v("status-warning"),
    warningSubtle: v("status-warning-bg"),
    danger:        v("status-danger"),
    dangerSubtle:  v("status-danger-bg"),
    info:          v("status-info"),
    infoSubtle:    v("status-info-bg"),
  },
  syndicate: {
    transportation: {
      bg:     v("syndicate-transportation-bg"),
      text:   v("syndicate-transportation-text"),
      border: v("syndicate-transportation-border"),
    },
    fortification: {
      bg:     v("syndicate-fortification-bg"),
      text:   v("syndicate-fortification-text"),
      border: v("syndicate-fortification-border"),
    },
    research: {
      bg:     v("syndicate-research-bg"),
      text:   v("syndicate-research-text"),
      border: v("syndicate-research-border"),
    },
    intervention: {
      bg:     v("syndicate-intervention-bg"),
      text:   v("syndicate-intervention-text"),
      border: v("syndicate-intervention-border"),
    },
  },
} as const;

export const space = {
  xs: 4, sm: 6, md: 8, lg: 12, xl: 16, xxl: 24, xxxl: 32,
} as const;

export const radius = {
  sm: 4, md: 6, lg: 8, xl: 12, full: 9999,
} as const;

export const font = {
  xs: 10, sm: 11, md: 12, base: 13, lg: 14, xl: 15, xxl: 16,
  h1: 24, h2: 18, h3: 15,
  family: {
    sans: "var(--font-sans)",
    mono: "var(--font-mono)",
  },
} as const;

export const anim = {
  fast:    "var(--anim-fast)",
  default: "var(--anim-default)",
  slow:    "var(--anim-slow)",
  easing:  "var(--anim-easing)",
} as const;

export const z = {
  base: 0,
  dropdown: 10,
  sticky: 50,
  modal: 100,
  overlayWindow: 1000,
  toast: 10000,
} as const;

export const breakpoints = {
  sidebarCollapse: 1100,
  sidebarHide: 900,
  tablet: 768,
  mobile: 480,
} as const;

export const mq = {
  sidebarCollapse: `@media (max-width: ${breakpoints.sidebarCollapse}px)`,
  sidebarHide:     `@media (max-width: ${breakpoints.sidebarHide}px)`,
  tablet:          `@media (max-width: ${breakpoints.tablet}px)`,
  mobile:          `@media (max-width: ${breakpoints.mobile}px)`,
} as const;
