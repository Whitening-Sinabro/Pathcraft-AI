/**
 * dev/prod 분기 로거. 프로덕션 번들에서는 info/warn은 no-op, error만 유지.
 * 글로벌 CLAUDE.md: console.log/print 금지 — 모든 로깅은 이 래퍼 경유.
 */

type LogArgs = readonly unknown[];

const isDev = import.meta.env.DEV;

export const logger = {
  info(...args: LogArgs): void {
    if (!isDev) return;
    // eslint-disable-next-line no-console
    console.info(...args);
  },
  warn(...args: LogArgs): void {
    if (!isDev) return;
    // eslint-disable-next-line no-console
    console.warn(...args);
  },
  error(...args: LogArgs): void {
    // eslint-disable-next-line no-console
    console.error(...args);
  },
};
