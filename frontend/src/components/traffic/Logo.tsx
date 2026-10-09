import { useId } from "react";

export function SuratTrafficNexusLogo({
  className = "h-6 w-6",
  showBadge = false,
}: {
  className?: string;
  showBadge?: boolean;
}) {
  const id = useId();
  const uid = id.replace(/:/g, "");
  const whiteGradId = `whiteGrad-${uid}`;
  const shieldGradId = `shieldGrad-${uid}`;
  const redGlowId = `redGlow-${uid}`;
  const amberGlowId = `amberGlow-${uid}`;
  const greenGlowId = `greenGlow-${uid}`;

  const icon = (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        {/* White / Platinum Silver Shield Gradient */}
        <linearGradient id={whiteGradId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="50%" stopColor="#f1f5f9" />
          <stop offset="100%" stopColor="#00f3ff" />
        </linearGradient>

        {/* Shield Border Gradient */}
        <linearGradient id={shieldGradId} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#cbd5e1" />
        </linearGradient>

        {/* Traffic Light Glows */}
        <radialGradient id={redGlowId} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ff3355" stopOpacity="1" />
          <stop offset="70%" stopColor="#ff1a40" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#ff1a40" stopOpacity="0" />
        </radialGradient>
        <radialGradient id={amberGlowId} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ffcc00" stopOpacity="1" />
          <stop offset="70%" stopColor="#ff9900" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#ff9900" stopOpacity="0" />
        </radialGradient>
        <radialGradient id={greenGlowId} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#00ff88" stopOpacity="1" />
          <stop offset="70%" stopColor="#00cc66" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#00cc66" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Outer White / Platinum Shield Crest */}
      <path
        d="M24 3 L40 10 V34 L24 45 L8 34 V10 Z"
        stroke={`url(#${shieldGradId})`}
        strokeWidth="2"
        strokeLinejoin="round"
        fill={`url(#${whiteGradId})`}
        fillOpacity="0.95"
      />

      {/* Outer Glow Outline */}
      <path
        d="M24 5 L38 11.5 V33 L24 43 L10 33 V11.5 Z"
        stroke="#ffffff"
        strokeWidth="1"
        fill="none"
        opacity="0.8"
      />

      {/* Dark Contrast Housing for Traffic Light Lenses */}
      <rect
        x="16.5"
        y="9.5"
        width="15"
        height="29"
        rx="7.5"
        fill="#0f172a"
        stroke="#334155"
        strokeWidth="1.6"
      />

      {/* Visor / Light Lens Hoods (White / Cyan) */}
      <path d="M17 14.5 C 20 12, 28 12, 31 14.5" stroke="#f8fafc" strokeWidth="1.2" fill="none" opacity="0.9" />
      <path d="M17 23.5 C 20 21, 28 21, 31 23.5" stroke="#f8fafc" strokeWidth="1.2" fill="none" opacity="0.9" />
      <path d="M17 32.5 C 20 30, 28 30, 31 32.5" stroke="#f8fafc" strokeWidth="1.2" fill="none" opacity="0.9" />

      {/* ── 1. RED TRAFFIC LIGHT ── */}
      <circle cx="24" cy="15" r="5" fill={`url(#${redGlowId})`} />
      <circle cx="24" cy="15" r="3.2" fill="#ff2a4b" />
      <circle cx="22.8" cy="13.8" r="1.1" fill="#ffffff" opacity="0.9" />

      {/* ── 2. AMBER TRAFFIC LIGHT ── */}
      <circle cx="24" cy="24" r="5" fill={`url(#${amberGlowId})`} />
      <circle cx="24" cy="24" r="3.2" fill="#ffb700" />
      <circle cx="22.8" cy="22.8" r="1.1" fill="#ffffff" opacity="0.9" />

      {/* ── 3. GREEN TRAFFIC LIGHT ── */}
      <circle cx="24" cy="33" r="5" fill={`url(#${greenGlowId})`} />
      <circle cx="24" cy="33" r="3.2" fill="#00ff88" />
      <circle cx="22.8" cy="31.8" r="1.1" fill="#ffffff" opacity="0.9" />
    </svg>
  );

  if (showBadge) {
    return (
      <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-white/30 bg-white/10 backdrop-blur-md shadow-[0_0_20px_rgba(255,255,255,0.2)] transition-all hover:scale-105 hover:bg-white/20 hover:border-white/50">
        <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-white/20 via-transparent to-white/5 pointer-events-none" />
        {icon}
      </div>
    );
  }

  return icon;
}
