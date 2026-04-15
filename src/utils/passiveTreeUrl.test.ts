import { describe, it, expect } from "vitest";
import { decodeTreeUrl, extractTreeToken } from "./passiveTreeUrl";

// Helper: build a synthetic v6 payload (version=6, class=5 Templar, asc=2).
// Allocates node IDs 17765, 12345.
function makeSyntheticToken(nodeIds: number[], version = 6, classIdx = 5, ascIdx = 2): string {
  const buf = new Uint8Array(8 + nodeIds.length * 2 + 2);
  const dv = new DataView(buf.buffer);
  dv.setUint32(0, version, false);
  dv.setUint8(4, classIdx);
  dv.setUint8(5, ascIdx);
  dv.setUint8(6, 0);
  dv.setUint8(7, nodeIds.length);
  let off = 8;
  for (const id of nodeIds) { dv.setUint16(off, id, false); off += 2; }
  // cluster count 0, mastery count 0 for v6
  dv.setUint8(off, 0); off += 1;
  dv.setUint8(off, 0);
  // base64url encode
  let s = "";
  for (const b of buf) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

describe("extractTreeToken", () => {
  it("parses full URL", () => {
    expect(extractTreeToken("https://www.pathofexile.com/passive-skill-tree/ABCDEF_-"))
      .toBe("ABCDEF_-");
  });
  it("parses fullscreen URL", () => {
    expect(extractTreeToken("https://www.pathofexile.com/fullscreen-passive-skill-tree/XYZ"))
      .toBe("XYZ");
  });
  it("accepts raw token", () => {
    expect(extractTreeToken("AAAA_BBB-123")).toBe("AAAA_BBB-123");
  });
  it("rejects empty/invalid input", () => {
    expect(extractTreeToken("")).toBeNull();
    expect(extractTreeToken("   ")).toBeNull();
    expect(extractTreeToken("not a url with spaces")).toBeNull();
  });
});

describe("decodeTreeUrl", () => {
  it("decodes version + class + ascendancy", () => {
    const token = makeSyntheticToken([17765, 12345]);
    const decoded = decodeTreeUrl(token);
    expect(decoded).not.toBeNull();
    expect(decoded!.version).toBe(6);
    expect(decoded!.classIndex).toBe(5);
    expect(decoded!.ascendancyIndex).toBe(2);
    expect(decoded!.nodes).toEqual(["17765", "12345"]);
  });

  it("handles empty node list", () => {
    const token = makeSyntheticToken([]);
    const decoded = decodeTreeUrl(token);
    expect(decoded!.nodes).toEqual([]);
  });

  it("accepts full URL as input", () => {
    const token = makeSyntheticToken([100, 200]);
    const url = "https://www.pathofexile.com/passive-skill-tree/" + token;
    const decoded = decodeTreeUrl(url);
    expect(decoded!.nodes).toEqual(["100", "200"]);
  });

  it("returns null for garbage input", () => {
    expect(decodeTreeUrl("")).toBeNull();
    expect(decodeTreeUrl("not base64!!!")).toBeNull();
  });

  it("returns null for truncated payload", () => {
    const token = btoa("abc").replace(/=+$/, "");
    expect(decodeTreeUrl(token)).toBeNull();
  });
});
