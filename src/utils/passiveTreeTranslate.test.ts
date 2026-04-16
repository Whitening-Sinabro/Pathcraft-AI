import { describe, it, expect } from "vitest";
import {
  normalizeStatNumbers,
  injectNumbers,
  translateStat,
  type TranslationTable,
} from "./passiveTreeTranslate";

describe("normalizeStatNumbers", () => {
  it("returns stat unchanged when there are no numbers", () => {
    const { template, numbers } = normalizeStatNumbers(
      "Action Speed cannot be modified to below Base Value",
    );
    expect(template).toBe("Action Speed cannot be modified to below Base Value");
    expect(numbers).toEqual([]);
  });

  it("replaces a single integer with {0}", () => {
    const { template, numbers } = normalizeStatNumbers(
      "2% increased Effect of your Curses",
    );
    expect(template).toBe("{0}% increased Effect of your Curses");
    expect(numbers).toEqual(["2"]);
  });

  it("preserves signed numbers in the captured list", () => {
    const { template, numbers } = normalizeStatNumbers(
      "+10% chance to Suppress Spell Damage while on Full Life",
    );
    expect(template).toBe("{0}% chance to Suppress Spell Damage while on Full Life");
    expect(numbers).toEqual(["+10"]);
  });

  it("handles decimals as one literal", () => {
    const { template, numbers } = normalizeStatNumbers(
      "Favours have 0.25% chance to cost no Tribute",
    );
    expect(template).toBe("Favours have {0}% chance to cost no Tribute");
    expect(numbers).toEqual(["0.25"]);
  });

  it("numbers placeholders in order of appearance", () => {
    const { template, numbers } = normalizeStatNumbers(
      "Brands have 5% increased Area of Effect if 50% of Attached Duration expired",
    );
    expect(template).toBe(
      "Brands have {0}% increased Area of Effect if {1}% of Attached Duration expired",
    );
    expect(numbers).toEqual(["5", "50"]);
  });
});

describe("injectNumbers", () => {
  it("substitutes placeholders by index, not sequential order", () => {
    // Korean templates frequently reorder placeholders vs English source.
    const out = injectNumbers(
      "부착 지속시간의 {1}%가 경과하면 낙인의 효과 범위 {0}% 증가",
      ["5", "50"],
    );
    expect(out).toBe("부착 지속시간의 50%가 경과하면 낙인의 효과 범위 5% 증가");
  });

  it("leaves unknown indices intact so issues surface visibly", () => {
    const out = injectNumbers("A={0} B={2}", ["7", "8"]);
    expect(out).toBe("A=7 B={2}");
  });

  it("is a no-op when template has no placeholders", () => {
    const out = injectNumbers("동작 속도가 기본 수치 밑으로 내려가지 않음", ["1"]);
    expect(out).toBe("동작 속도가 기본 수치 밑으로 내려가지 않음");
  });
});

describe("translateStat", () => {
  const table: TranslationTable = {
    translations: {
      "Action Speed cannot be modified to below Base Value":
        "동작 속도가 기본 수치 밑으로 내려가지 않음",
      "{0}% increased Effect of your Curses":
        "플레이어가 시전하는 저주 효과 {0}% 증가",
      "Brands have {0}% increased Area of Effect if {1}% of Attached Duration expired":
        "부착 지속시간의 {1}%가 경과하면 낙인의 효과 범위 {0}% 증가",
    },
  };

  it("direct-matches a numberless stat", () => {
    const out = translateStat(
      "Action Speed cannot be modified to below Base Value",
      table,
    );
    expect(out).toBe("동작 속도가 기본 수치 밑으로 내려가지 않음");
  });

  it("normalizes numbers and re-injects them in Korean output", () => {
    const out = translateStat("2% increased Effect of your Curses", table);
    expect(out).toBe("플레이어가 시전하는 저주 효과 2% 증가");
  });

  it("handles Korean templates that reorder placeholders", () => {
    const out = translateStat(
      "Brands have 5% increased Area of Effect if 50% of Attached Duration expired",
      table,
    );
    expect(out).toBe("부착 지속시간의 50%가 경과하면 낙인의 효과 범위 5% 증가");
  });

  it("falls back to English on a miss", () => {
    const english = "Some brand-new stat that has no translation yet";
    expect(translateStat(english, table)).toBe(english);
  });

  it("falls back to English when table is null", () => {
    expect(translateStat("2% increased Effect of your Curses", null)).toBe(
      "2% increased Effect of your Curses",
    );
  });
});
