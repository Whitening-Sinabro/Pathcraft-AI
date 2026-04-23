import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { PassivePrioritySection } from "./PassivePriority";

describe("PassivePrioritySection", () => {
  it("renders empty when priorities is undefined (POE2 response omission guard)", () => {
    const html = renderToStaticMarkup(
      <PassivePrioritySection priorities={undefined as unknown as string[]} />,
    );
    expect(html).toBe("");
  });

  it("renders empty when priorities is an empty array", () => {
    const html = renderToStaticMarkup(<PassivePrioritySection priorities={[]} />);
    expect(html).toBe("");
  });

  it("renders an ordered list when priorities is populated", () => {
    const html = renderToStaticMarkup(
      <PassivePrioritySection priorities={["Life", "Damage"]} />,
    );
    expect(html).toContain("<section");
    expect(html).toContain("<ol");
    expect(html).toContain(">Life<");
    expect(html).toContain(">Damage<");
  });
});
