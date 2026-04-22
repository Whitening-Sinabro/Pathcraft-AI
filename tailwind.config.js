// Design enforcement — AI slop 방지를 위해 장식 플러그인 비활성.
// 이 설정을 풀려면 반드시 design-exception 주석 + .claude/status/design-exceptions.md 기록.
// 프로젝트당 예외 캡 2개 (pre-commit에서 강제).

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx,vue,svelte,astro,mdx,html}',
    './app/**/*.{js,jsx,ts,tsx,vue,svelte,astro,mdx}',
    './pages/**/*.{js,jsx,ts,tsx,vue,svelte,astro,mdx}',
    './components/**/*.{js,jsx,ts,tsx,vue,svelte,astro,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        fg: 'var(--color-fg)',
        accent: 'var(--color-accent)',
      },
      fontFamily: {
        sans: ['Inter', 'Pretendard', 'system-ui', 'sans-serif'],
      },
    },
  },
  corePlugins: {
    // 장식 원천 차단 — 클래스 자체가 빌드 산출물에 존재하지 않음
    backgroundImage: false,
    gradientColorStops: false,
    boxShadow: false,
    dropShadow: false,
  },
  plugins: [],
};
