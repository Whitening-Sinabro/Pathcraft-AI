// Passive tree stat translation (EN → KO).
//
// The tree's raw stats are English strings with concrete numbers
// ("2% increased Effect of your Curses"). The translation table stores
// Korean templates with {0}, {1}, ... placeholders.
//
// Matching pipeline:
//   1. Replace each numeric literal with {0}, {1}, ... (in order of appearance).
//   2. Look up the normalized template in the translation map.
//      The map also keeps a few entries that contain no numbers, so we also
//      check the raw string as a fast path.
//   3. Re-inject the captured numbers into the Korean template.
//   4. On miss, return the original English string (fallback).
//
// Measured coverage on the current skilltree export: 2352/2559 = 91.9%.

// Matches one numeric literal at a time. Signed + integer + optional decimals.
// Scans left-to-right; numbers never overlap so a single global regex is enough.
const NUMERIC_RE = /[+-]?\d+(?:\.\d+)?/g;

export interface TranslationTable {
  translations: Record<string, string>;
}

/**
 * Replace each numeric literal in `stat` with {0}, {1}, ... in order.
 * The captured literals are returned in the same order as `numbers`.
 */
export function normalizeStatNumbers(stat: string): {
  template: string;
  numbers: string[];
} {
  const numbers: string[] = [];
  const template = stat.replace(NUMERIC_RE, (m) => {
    const placeholder = `{${numbers.length}}`;
    numbers.push(m);
    return placeholder;
  });
  return { template, numbers };
}

/**
 * Re-inject numbers into a Korean template that uses {0}, {1}, ... placeholders.
 *
 * Korean ordering can differ from English, so placeholders may appear in a
 * different order than the source (e.g. "{1}초 동안 {0}%"). We substitute by
 * index, not by sequence position.
 */
export function injectNumbers(template: string, numbers: string[]): string {
  return template.replace(/\{(\d+)\}/g, (match, idxStr: string) => {
    const idx = Number.parseInt(idxStr, 10);
    if (!Number.isFinite(idx) || idx < 0 || idx >= numbers.length) {
      // Leave unknown placeholders intact rather than silently dropping them.
      return match;
    }
    return numbers[idx];
  });
}

/**
 * Translate a single English stat string using the provided translation table.
 * Returns the original string when no translation is found (fallback).
 */
export function translateStat(
  stat: string,
  table: TranslationTable | null | undefined,
): string {
  if (!table) return stat;
  const map = table.translations;

  // Fast path: numberless stat matched as-is.
  const direct = map[stat];
  if (direct != null) return direct;

  const { template, numbers } = normalizeStatNumbers(stat);
  const korean = map[template];
  if (korean == null) return stat;
  return injectNumbers(korean, numbers);
}
