import { useState, useRef, useEffect } from "react";
import { AppShell } from "./AppShell";
import { TopStatusBar } from "./TopStatusBar";
import { MapPanel } from "./MapPanel";
import { KPIPanel } from "./KPIPanel";
import { JunctionDrawer } from "./JunctionDrawer";
import { AlertsFeed } from "./AlertsFeed";
import { useTrafficData } from "@/hooks/useTrafficData";
import { getRoadDensityColor, getRoadDensityBadgeText } from "@/lib/signal-intelligence";
import { Activity, Clock, ChevronRight, Cpu } from "lucide-react";

export function CommandCentre() {
  const { junctions, kpis, queue, alerts, predictions, stats, connected, getJunction } =
    useTrafficData();
  const [selected, setSelected] = useState<string | null>(null);

  // Synchronize KPI sidebar height to square map so space is never wasted
  const [mapHeight, setMapHeight] = useState<number | null>(null);
  const mapColRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapColRef.current) return;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.height > 0) {
          setMapHeight(Math.round(entry.contentRect.height));
        }
      }
    });
    ro.observe(mapColRef.current);
    return () => ro.disconnect();
  }, []);

  // Summary counts of road density states across all signals
  const densityCounts = {
    free: junctions.filter((j) => (j.congestionIndex || 0) < 45).length,
    moderate: junctions.filter((j) => (j.congestionIndex || 0) >= 45 && (j.congestionIndex || 0) < 65).length,
    heavy: junctions.filter((j) => (j.congestionIndex || 0) >= 65 && (j.congestionIndex || 0) < 80).length,
    critical: junctions.filter((j) => (j.congestionIndex || 0) >= 80).length,
  };

  return (
    <AppShell>
      <TopStatusBar
        junctionsOnline={stats.junctionsOnline}
        intrusions={stats.activeIntrusions}
        avgCongestion={stats.avgCongestion}
        connected={connected}
      />

      {/* Main layout */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 flex flex-col gap-3">

        {/* ── Live Signals Road Density & Real-Time Timers Quick Strip ── */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-2.5 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 mb-2 border-b border-zinc-800/80 gap-2">
            <div className="flex items-center gap-2">
              <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-200 font-mono">
                Real-Time Road Density & Signal Phase Timers
              </span>
              <span className="text-[10px] text-zinc-500 font-mono hidden md:inline">
                · {junctions.length} Monitored Intersections
              </span>
            </div>

            {/* Density breakdown badges */}
            <div className="flex items-center gap-2 text-[10px] font-mono">
              <span className="text-zinc-500 hidden lg:inline">City Status:</span>
              <span className="flex items-center gap-1 text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-1.5 py-0.5 rounded">
                Free Flow: {densityCounts.free}
              </span>
              <span className="flex items-center gap-1 text-amber-400 bg-amber-950/40 border border-amber-500/30 px-1.5 py-0.5 rounded">
                Moderate: {densityCounts.moderate}
              </span>
              <span className="flex items-center gap-1 text-orange-400 bg-orange-950/40 border border-orange-500/30 px-1.5 py-0.5 rounded">
                Heavy: {densityCounts.heavy}
              </span>
              <span className="flex items-center gap-1 text-rose-400 bg-rose-950/40 border border-rose-500/30 px-1.5 py-0.5 rounded font-bold">
                Gridlock: {densityCounts.critical}
              </span>
            </div>
          </div>

          {/* Horizontal scrollable signals quick-strip */}
          <div className="flex items-center gap-2.5 overflow-x-auto pb-1 scrollbar-thin">
            {junctions.map((j) => {
              const dens = j.congestionIndex || 50;
              const densColor = getRoadDensityColor(dens);
              const sigColor =
                j.signalStatus === "GREEN"
                  ? "#22c55e"
                  : j.signalStatus === "YELLOW"
                  ? "#f59e0b"
                  : "#ef4444";
              const isSelected = selected === j.id;

              return (
                <button
                  key={j.id}
                  onClick={() => setSelected(j.id)}
                  className={`flex items-center gap-2.5 px-3 py-1.5 rounded-xl border text-left shrink-0 transition-all active:scale-95 ${
                    isSelected
                      ? "border-sky-500 bg-sky-950/30 shadow-[0_0_14px_rgba(56,189,248,0.3)]"
                      : "border-zinc-800/80 bg-zinc-900/60 hover:bg-zinc-800/60 hover:border-zinc-700"
                  }`}
                  title={`Inspect ${j.name}: Road Density ${dens}%, Phase: ${j.signalStatus} ${j.signalCountdown}s`}
                >
                  {/* Traffic Signal LED Pill */}
                  <div
                    className="flex items-center gap-1 px-1.5 py-0.5 rounded-md font-mono text-[10px] font-bold border"
                    style={{
                      borderColor: `${sigColor}60`,
                      color: sigColor,
                      backgroundColor: `${sigColor}15`,
                    }}
                  >
                    <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: sigColor }} />
                    <span>{j.signalCountdown}s</span>
                  </div>

                  {/* Junction Title */}
                  <div className="flex flex-col min-w-0 max-w-[130px]">
                    <span className="text-[11px] font-bold text-zinc-200 truncate">
                      {j.name.split("/")[0]}
                    </span>
                    <span className="text-[9px] font-mono text-zinc-500 uppercase truncate">
                      {j.id} · {j.zone.split(" ")[0]}
                    </span>
                  </div>

                  {/* Road Density Badge */}
                  <div
                    className="flex flex-col items-end font-mono text-[10px] font-bold pl-1 border-l border-zinc-800"
                    style={{ color: densColor }}
                  >
                    <span>{dens}%</span>
                    <span className="text-[8px] opacity-80 uppercase">DENS</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Map & KPI Grid */}
        <div className="grid gap-3 xl:grid-cols-[minmax(0,2.2fr)_minmax(0,1fr)] items-start">
          {/* Map Column */}
          <div ref={mapColRef} className="w-full aspect-[4/3]">
            <MapPanel junctions={junctions} selectedId={selected} onSelect={setSelected} />
          </div>

          {/* KPI + charts scrollable sidebar matching map height */}
          <div
            className="overflow-y-auto pr-1"
            style={{
              height: mapHeight ? `${mapHeight}px` : undefined,
              maxHeight: mapHeight ? `${mapHeight}px` : undefined,
            }}
          >
            <KPIPanel kpis={kpis} queue={queue} />
          </div>
        </div>

        {/* Alerts feed */}
        <div className="shrink-0">
          <AlertsFeed alerts={alerts} predictions={predictions} onSelectJunction={setSelected} />
        </div>
      </div>

      {/* Full Signal Telemetry, Density, Timer History & AI Learning Report Inspector */}
      <JunctionDrawer junction={getJunction(selected)} onClose={() => setSelected(null)} />
    </AppShell>
  );
}
