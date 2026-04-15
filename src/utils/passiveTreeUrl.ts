// POE official passive-tree URL decoder.
// URL format: https://www.pathofexile.com/passive-skill-tree/<base64url>
// or pathofexile.com/fullscreen-passive-skill-tree/<base64url>.
// Payload (version 4+, big-endian):
//   [0..3]  u32  version
//   [4]     u8   class (0..6)
//   [5]     u8   ascendancy (0..3)
//   [6]     u8   fullscreen flag
//   [7]     u8   node count N
//   [8..]   u16×N  node IDs
//   then optional: cluster nodes (u8 count + u16×), masteries (u8 count + (u16+u16)×)
//
// Reference: PathOfBuildingCommunity PassiveSpec.lua:316-456

export interface DecodedTree {
  version: number;
  classIndex: number;
  ascendancyIndex: number;
  nodes: string[];
  masteryEffects: Map<string, string>;  // nodeId → effectId
}

function base64UrlDecode(input: string): Uint8Array {
  const padded = input.replace(/-/g, "+").replace(/_/g, "/");
  const padLen = (4 - (padded.length % 4)) % 4;
  const b64 = padded + "=".repeat(padLen);
  if (typeof atob === "function") {
    const bin = atob(b64);
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  throw new Error("base64 decoder unavailable");
}

/** Extract the base64url token from a full URL or raw token string. */
export function extractTreeToken(urlOrToken: string): string | null {
  const trimmed = urlOrToken.trim();
  if (!trimmed) return null;
  const match = trimmed.match(/passive-skill-tree\/([A-Za-z0-9_-]+)/);
  if (match) return match[1];
  // Already looks like a raw token
  if (/^[A-Za-z0-9_-]+$/.test(trimmed)) return trimmed;
  return null;
}

export function decodeTreeUrl(urlOrToken: string): DecodedTree | null {
  const token = extractTreeToken(urlOrToken);
  if (!token) return null;
  let bytes: Uint8Array;
  try {
    bytes = base64UrlDecode(token);
  } catch {
    return null;
  }
  if (bytes.length < 8) return null;
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const version = dv.getUint32(0, false);
  const classIndex = dv.getUint8(4);
  const ascendancyIndex = dv.getUint8(5);
  // bytes[6] = fullscreen flag (ignored)
  const nodeCount = dv.getUint8(7);
  const nodes: string[] = [];
  let offset = 8;
  for (let i = 0; i < nodeCount && offset + 2 <= bytes.length; i++) {
    nodes.push(String(dv.getUint16(offset, false)));
    offset += 2;
  }

  // Optional: cluster jewel nodes
  const masteryEffects = new Map<string, string>();
  if (version >= 5 && offset < bytes.length) {
    const clusterCount = dv.getUint8(offset); offset += 1;
    for (let i = 0; i < clusterCount && offset + 2 <= bytes.length; i++) {
      nodes.push(String(dv.getUint16(offset, false)));
      offset += 2;
    }
  }
  // Optional: mastery effects (version 6+)
  if (version >= 6 && offset < bytes.length) {
    const masteryCount = dv.getUint8(offset); offset += 1;
    for (let i = 0; i < masteryCount && offset + 4 <= bytes.length; i++) {
      // Layout: effectId u16 BE, nodeId u16 BE
      const effectId = dv.getUint16(offset, false); offset += 2;
      const nodeId = dv.getUint16(offset, false); offset += 2;
      masteryEffects.set(String(nodeId), String(effectId));
    }
  }

  return { version, classIndex, ascendancyIndex, nodes, masteryEffects };
}
