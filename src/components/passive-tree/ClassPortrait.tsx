// P1: SVG placeholder portraits for 7 classes. Bundled, works without POE install.
// Rendered as DOM overlay above Canvas at classStart world positions.
// P2~P4에서 DDS 추출 portrait으로 교체 예정 (manifest fallback 유지).

interface ClassMeta {
  name: string;
  initial: string;
  // Primary/secondary hue — STR red, DEX green, INT blue, mixed = bi-color halves.
  primary: string;
  secondary: string | null;
  ring: string;
}

const CLASS_META: ClassMeta[] = [
  // Scion — tri-attribute. Rendered with 3 wedges (special case in render below).
  { name: "Scion",    initial: "S", primary: "#b89060", secondary: null,      ring: "#e8d090" },
  // Marauder — pure STR
  { name: "Marauder", initial: "M", primary: "#8b2020", secondary: null,      ring: "#d04040" },
  // Ranger — pure DEX
  { name: "Ranger",   initial: "R", primary: "#1e6e2e", secondary: null,      ring: "#4ad070" },
  // Witch — pure INT
  { name: "Witch",    initial: "W", primary: "#1e4a7a", secondary: null,      ring: "#4a80d0" },
  // Duelist — STR+DEX
  { name: "Duelist",  initial: "D", primary: "#8b2020", secondary: "#1e6e2e", ring: "#c8a040" },
  // Templar — STR+INT
  { name: "Templar",  initial: "T", primary: "#8b2020", secondary: "#1e4a7a", ring: "#a858c8" },
  // Shadow — DEX+INT
  { name: "Shadow",   initial: "S", primary: "#1e6e2e", secondary: "#1e4a7a", ring: "#40c0c0" },
];

interface Props {
  classIndex: number;
}

// SVG는 부모 div의 크기(100%)를 채움. 부모가 rAF에서 style.width/height 갱신.
export function ClassPortrait({ classIndex }: Props) {
  const meta = CLASS_META[classIndex];
  if (!meta) return null;

  const isScion = classIndex === 0;
  const isMixed = !isScion && meta.secondary != null;

  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid meet"
      style={{ display: "block", filter: "drop-shadow(0 0 4px rgba(0,0,0,0.8))" }}
    >
      <defs>
        <radialGradient id={`grad-${classIndex}`} cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="rgba(255,255,255,0.25)" />
          <stop offset="70%" stopColor="rgba(255,255,255,0)" />
        </radialGradient>
      </defs>

      {/* Disc background */}
      {isScion ? (
        // Scion: tri-wedge STR/DEX/INT (120° each, top-start)
        <>
          <path d="M 50 50 L 50 5 A 45 45 0 0 1 88.97 72.5 Z" fill="#8b2020" />
          <path d="M 50 50 L 88.97 72.5 A 45 45 0 0 1 11.03 72.5 Z" fill="#1e6e2e" />
          <path d="M 50 50 L 11.03 72.5 A 45 45 0 0 1 50 5 Z" fill="#1e4a7a" />
        </>
      ) : isMixed ? (
        // Left half primary, right half secondary
        <>
          <path d="M 50 5 A 45 45 0 0 0 50 95 Z" fill={meta.primary} />
          <path d="M 50 5 A 45 45 0 0 1 50 95 Z" fill={meta.secondary!} />
        </>
      ) : (
        <circle cx="50" cy="50" r="45" fill={meta.primary} />
      )}

      {/* Specular highlight */}
      <circle cx="50" cy="50" r="45" fill={`url(#grad-${classIndex})`} />

      {/* Outer ring */}
      <circle cx="50" cy="50" r="46" fill="none" stroke={meta.ring} strokeWidth="2.5" opacity="0.9" />
      <circle cx="50" cy="50" r="46" fill="none" stroke="rgba(0,0,0,0.6)" strokeWidth="1" />

      {/* Initial */}
      <text
        x="50"
        y="66"
        fontSize="44"
        fontWeight="700"
        textAnchor="middle"
        fill="#f4e4c0"
        stroke="rgba(0,0,0,0.7)"
        strokeWidth="1.5"
        paintOrder="stroke"
        fontFamily="'Cinzel', 'Trajan Pro', Georgia, serif"
      >
        {meta.initial}
      </text>
    </svg>
  );
}

export const CLASS_PORTRAIT_COUNT = CLASS_META.length;
