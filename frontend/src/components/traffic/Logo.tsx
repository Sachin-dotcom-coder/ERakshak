export function SuratTrafficNexusLogo({
  className = "h-6 w-6",
  showBadge = false,
}: {
  className?: string;
  showBadge?: boolean;
}) {
  const icon = (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        {/* Electric Cyan to Emerald Green Gradient */}
        <linearGradient id="nexusGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00f3ff" />
          <stop offset="50%" stopColor="#00ff88" />
          <stop offset="100%" stopColor="#ffb700" />
        </linearGradient>

        {/* Ambient Center Glow */}
        <radialGradient id="nexusGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#00f3ff" stopOpacity="0.6" />
          <stop offset="60%" stopColor="#00ff88" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Background Central Pulse Glow */}
      <circle cx="24" cy="24" r="18" fill="url(#nexusGlow)" />

      {/* Outer Hexagonal Shield Brackets */}
      <path
        d="M24 3 L41 12.5 V35.5 L24 45 L7 35.5 V12.5 Z"
        stroke="url(#nexusGrad)"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.4"
      />

      {/* Dynamic Road Intersection Lanes */}
      <path
        d="M12 24 H36 M24 12 V36"
        stroke="url(#nexusGrad)"
        strokeWidth="3.2"
        strokeLinecap="round"
      />

      {/* Traffic Signal Waveform Crossing */}
      <path
        d="M10 20 Q 17 30, 24 24 T 38 28"
        stroke="#00f3ff"
        strokeWidth="2.2"
        strokeLinecap="round"
        fill="none"
        opacity="0.9"
      />
      <path
        d="M20 10 Q 30 17, 24 24 T 28 38"
        stroke="#00ff88"
        strokeWidth="2.2"
        strokeLinecap="round"
        fill="none"
        opacity="0.9"
      />

      {/* Central Nexus Core Node */}
      <circle cx="24" cy="24" r="4.5" fill="#040810" stroke="#00f3ff" strokeWidth="2" />
      <circle cx="24" cy="24" r="2" fill="#00ff88" />

      {/* 4 Cardinal Intersection Signal Nodes */}
      <circle cx="24" cy="12" r="2.2" fill="#00ff88" />
      <circle cx="36" cy="24" r="2.2" fill="#00f3ff" />
      <circle cx="24" cy="36" r="2.2" fill="#ff3366" />
      <circle cx="12" cy="24" r="2.2" fill="#ffcc00" />
    </svg>
  );

  if (showBadge) {
    return (
      <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded border border-[#00f3ff]/40 bg-[#0a0d14] shadow-[0_0_15px_rgba(0,243,255,0.25)] transition-transform hover:scale-105">
        <div className="absolute inset-0 rounded bg-gradient-to-br from-[#00f3ff]/10 via-transparent to-[#00ff88]/10 pointer-events-none" />
        {icon}
      </div>
    );
  }

  return icon;
}
