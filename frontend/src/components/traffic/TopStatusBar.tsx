import { useEffect, useState } from "react";
import { Activity, Wifi, TriangleAlert, Circle, Clock } from "lucide-react";
import { SuratTrafficNexusLogo } from "./Logo";

type Props = {
  junctionsOnline: number;
  intrusions: number;
  avgCongestion: number;
  connected: boolean;
  right?: React.ReactNode;
};

const TOTAL_JUNCTIONS = 22;

function useClock() {
  const [clock, setClock] = useState("--:--:--");
  useEffect(() => {
    const update = () => {
      const now = new Date();
      const ist = new Date(now.getTime() + 5.5 * 60 * 60 * 1000);
      const h = String(ist.getUTCHours()).padStart(2, "0");
      const m = String(ist.getUTCMinutes()).padStart(2, "0");
      const s = String(ist.getUTCSeconds()).padStart(2, "0");
      setClock(`${h}:${m}:${s}`);
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);
  return clock;
}

/** 5-segment congestion bar — fills left to right with subtle glow */
function CongestionBar({ value }: { value: number }) {
  const filled = Math.ceil((value / 100) * 5);
  const segs = [
    { color: "#22c55e" },
    { color: "#84cc16" },
    { color: "#f59e0b" },
    { color: "#f97316" },
    { color: "#ef4444" },
  ];
  return (
    <div className="congestion-bar w-24 h-2 rounded-sm overflow-hidden flex gap-1">
      {segs.map((s, i) => (
        <div
          key={i}
          className="congestion-bar-seg flex-1 rounded-sm transition-all"
          style={{
            backgroundColor: s.color,
            opacity: i < filled ? 1 : 0.18,
            boxShadow: i < filled ? `0 0 8px ${s.color}66` : undefined,
          }}
        />
      ))}
    </div>
  );
}

export function TopStatusBar({
  junctionsOnline,
  intrusions,
  avgCongestion,
  connected,
  right,
}: Props) {
  const clock = useClock();
  const congTone =
    avgCongestion > 70 ? "text-crit" : avgCongestion > 45 ? "text-warn" : "text-ok";

  return (
    <header className="sticky top-0 z-20 border-b border-white/[0.08] bg-panel/95 backdrop-blur-xl shadow-[0_4px_24px_-4px_rgba(0,0,0,0.5)]">
      <div className="flex items-center h-16 px-6 overflow-x-auto gap-4">

        {/* ── System Branding ───────────── */}
        <div className="flex items-center gap-3 mr-2 shrink-0">
          <SuratTrafficNexusLogo showBadge />
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-base font-extrabold tracking-tight text-foreground leading-none">
                E·<span className="text-primary">RAKSHAK</span>
              </span>
              <span className="text-[9px] font-mono font-bold tracking-wider uppercase px-1.5 py-0.5 rounded border border-white/10 bg-white/5 text-muted-foreground">
                ATCS 2.6
              </span>
            </div>
            <span className="text-[9px] font-mono tracking-widest text-muted-foreground/80 uppercase pt-1 font-medium">
              SURAT ADAPTIVE TRAFFIC CONTROL
            </span>
          </div>
        </div>

        {/* ── Divider ───────────────── */}
        <div className="h-8 w-px bg-white/[0.08] shrink-0" />

        {/* ── Metric Cards ──────────── */}
        <div className="flex items-center gap-3.5 mr-auto">

          {/* Telemetry Status */}
          <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] transition-all">
            <span className="relative flex h-2.5 w-2.5 items-center justify-center">
              {connected ? (
                <>
                  <span className="absolute h-full w-full rounded-full bg-ok/40 animate-ping" />
                  <span className="h-2 w-2 rounded-full bg-ok" />
                </>
              ) : (
                <span className="h-2 w-2 rounded-full bg-crit animate-blink" />
              )}
            </span>
            <div className="flex flex-col">
              <span className="text-[9px] font-mono uppercase tracking-wider text-muted-foreground">TELEMETRY</span>
              <span className={"text-xs font-mono font-bold leading-tight " + (connected ? "text-ok" : "text-crit")}>
                {connected ? "LIVE FEED" : "OFFLINE"}
              </span>
            </div>
          </div>

          {/* Junctions Online */}
          <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] transition-all">
            <Wifi className="h-4 w-4 text-foreground/80 shrink-0" />
            <div className="flex flex-col">
              <span className="text-[9px] font-mono uppercase tracking-wider text-muted-foreground">JUNCTIONS</span>
              <div className="text-xs font-mono font-bold leading-tight text-foreground flex items-center gap-1.5">
                <span>{junctionsOnline}</span>
                <span className="text-[10px] text-muted-foreground font-medium">/ {TOTAL_JUNCTIONS}</span>
                <span className="text-[9px] text-ok bg-ok/10 border border-ok/20 px-1 py-0.2 rounded font-semibold ml-0.5">
                  100% ONLINE
                </span>
              </div>
            </div>
          </div>

          {/* BRTS Violations */}
          <div className={"flex items-center gap-2.5 px-3.5 py-2 rounded-xl border transition-all " +
            (intrusions > 0 
              ? "border-crit/50 bg-crit/15 shadow-[0_0_16px_rgba(239,68,68,0.25)]" 
              : "border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05]")}>
            <TriangleAlert className={"h-4 w-4 shrink-0 " + (intrusions > 0 ? "text-crit animate-bounce" : "text-muted-foreground")} />
            <div className="flex flex-col">
              <span className="text-[9px] font-mono uppercase tracking-wider text-muted-foreground">BRTS VIOLATIONS</span>
              <div className="flex items-center gap-2 leading-tight">
                <span className={"num text-xs font-bold font-mono " + (intrusions > 0 ? "text-crit" : "text-muted-foreground")}>
                  {intrusions}
                </span>
                {intrusions > 0 ? (
                  <span className="text-[9px] font-mono font-bold bg-crit text-white px-1.5 py-0.5 rounded-sm animate-pulse">
                    ACTIVE
                  </span>
                ) : (
                  <span className="text-[10px] font-mono text-muted-foreground/70">CLEAR</span>
                )}
              </div>
            </div>
          </div>

          {/* City Congestion Index */}
          <div className="flex items-center gap-3 px-4 py-2 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] transition-all">
            <Activity className={"h-4 w-4 shrink-0 " + congTone} />
            <div className="flex flex-col">
              <span className="text-[9px] font-mono uppercase tracking-wider text-muted-foreground">CITY CONGESTION</span>
              <div className="flex items-center gap-2.5 leading-tight pt-0.5">
                <span className={"num text-xs font-bold font-mono " + congTone}>
                  {avgCongestion}%
                </span>
                <CongestionBar value={avgCongestion} />
              </div>
            </div>
          </div>

        </div>

        {/* ── Right Section ─────────── */}
        <div className="flex items-center gap-4 shrink-0">
          {/* High-Precision IST Clock */}
          <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl border border-white/[0.06] bg-white/[0.02]">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <div className="flex flex-col items-end">
              <span className="text-[9px] font-mono uppercase tracking-wider text-muted-foreground">TIME (IST)</span>
              <span className="num text-xs font-bold font-mono text-foreground tracking-wider tabular-nums">
                {clock}
              </span>
            </div>
          </div>

          {/* Export Slot (rendered strictly when provided by Summary/Reports page) */}
          {right && (
            <>
              <div className="h-8 w-px bg-white/[0.08]" />
              {right}
            </>
          )}
        </div>
      </div>
    </header>
  );
}
