import { useMemo, useState } from "react";
import { X, Cpu, Wifi, Thermometer, Eye, SlidersHorizontal } from "lucide-react";
import { AppShell } from "./AppShell";
import { TopStatusBar } from "./TopStatusBar";
import { CameraTile } from "./CameraTile";
import { DetectionLog } from "./DetectionLog";
import { useTrafficData } from "@/hooks/useTrafficData";
import { useCameraFeeds } from "@/hooks/useCameraFeeds";
import { fmtTime } from "@/lib/mock-traffic";

const GRID_SIZE = 9; // 3×3

function useCameraHealth(feeds: any[]) {
  return feeds.map((f, i) => ({
    id: f.id,
    online: f.online,
    fps: f.online ? (24 + (i % 5)) : 0,
    signalQuality: f.online ? (72 + (i * 7) % 27) : 0,
    confidence: f.online ? (82 + (i * 5) % 16) : 0,
    weather: ["Clear", "Clear", "Haze", "Clear", "Clear", "Fog", "Clear", "Clear", "Clear"][i % 9],
    uptime: f.online ? `${String(Math.floor(i * 3.2 + 1)).padStart(2, "0")}:${String((i * 7 + 14) % 60).padStart(2, "0")}:${String((i * 13) % 60).padStart(2, "0")}` : "00:00:00",
  }));
}

export function Surveillance() {
  const { stats, connected, detections, junctions } = useTrafficData();
  const { feeds, online, total } = useCameraFeeds();
  const [overlays, setOverlays] = useState(true);
  const [brtsOnly, setBrtsOnly] = useState(false);
  const [focus, setFocus] = useState<string | null>(null);

  const health = useCameraHealth(feeds);
  const avgConfidence = Math.round(health.filter(h => h.online).reduce((a, h) => a + h.confidence, 0) / Math.max(online, 1));

  const gridFeeds = [...feeds];
  while (gridFeeds.length < GRID_SIZE) {
    gridFeeds.push({
      id: "CAM-PENDING-" + gridFeeds.length,
      junctionId: "PENDING",
      junctionName: "Camera Slot " + (gridFeeds.length + 1),
      online: false,
      hasBrtsZone: false,
      boxes: [],
      vehicleCount: 0,
      avgSpeed: 0,
      queueLength: 0,
      intrusionActive: false,
    } as any);
  }

  const focused = feeds.find((f) => f.id === focus) ?? null;
  const focusedJunction = junctions.find((j) => j.id === focused?.junctionId) ?? null;
  const focusedEvents = useMemo(() => {
    if (!focus) return [];
    return detections
      .filter((d) => d.cameraId === focus || (focused && (d.cameraId === focused.id || d.junctionName === focused.junctionName)))
      .slice(0, 25);
  }, [detections, focus, focused]);
  const focusedHealth = health.find(h => h.id === focus);

  return (
    <AppShell>
      <TopStatusBar
        junctionsOnline={stats.junctionsOnline}
        intrusions={stats.activeIntrusions}
        avgCongestion={stats.avgCongestion}
        connected={connected}
      />

      <div className="flex-1 flex flex-col min-h-0">
        {/* Telemetry Bar */}
        <div className="border-b border-border bg-panel px-6 py-4 flex items-center justify-between gap-6 shrink-0">
          <div className="flex items-center gap-8">
            <div className="flex flex-col gap-1">
              <div className="label-xs text-muted-foreground flex items-center gap-1.5"><Cpu className="h-3.5 w-3.5" /> ACTIVE CAMERAS</div>
              <div className="num text-2xl font-bold tracking-tight">
                {online}<span className="text-muted-foreground text-sm font-medium">/{total}</span>
              </div>
            </div>
            
            <div className="h-10 w-px bg-border" />
            
            <div className="flex flex-col gap-1">
              <div className="label-xs text-muted-foreground flex items-center gap-1.5"><Eye className="h-3.5 w-3.5" /> AVG CONFIDENCE</div>
              <div className="num text-2xl font-bold tracking-tight">{avgConfidence}%</div>
            </div>

            <div className="h-10 w-px bg-border" />

            <div className="flex flex-col gap-1.5">
              <div className="label-xs text-muted-foreground">SYSTEM HEALTH STATUS</div>
              <div className="flex gap-1.5">
                {feeds.map(f => (
                  <button key={f.id} onClick={() => setFocus(f.id)} title={f.id}
                    className={"h-3 w-3 rounded-full transition-all " + (f.online ? "bg-ok hover:scale-125" : "bg-border")}
                    style={{ opacity: focus === f.id ? 1 : 0.6, outline: focus === f.id ? "2px solid var(--foreground)" : "none", outlineOffset: "2px" }}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-panel-raised p-1.5 rounded-xl border border-border">
            <Toggle active={overlays} onClick={() => setOverlays(v => !v)} label="Overlays" icon={<SlidersHorizontal className="h-3 w-3" />} />
            <Toggle active={brtsOnly} onClick={() => setBrtsOnly(v => !v)} label="BRTS Events" />
          </div>
        </div>

        {/* 3x3 Grid */}
        <div className="flex-1 min-h-0 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
            {gridFeeds.slice(0, GRID_SIZE).map((f, i) => (
              <div key={f.id} className="animate-grid-appear h-full flex flex-col" style={{ animationDelay: i * 40 + "ms", opacity: 0, animationFillMode: "forwards" }}>
                <CameraTile feed={f as any} overlays={overlays} brtsOnly={brtsOnly} onClick={() => setFocus(f.id)} staggerIndex={i} />
                {f.online && (
                  <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground">
                    <span className="flex items-center gap-1.5"><div className="h-1.5 w-1.5 rounded-full bg-ok" /> Live Stream</span>
                    <span className="num font-mono">{f.id}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Full-screen Modal */}
      {focused && (
        <div className="fixed inset-0 z-[9999] grid place-items-center bg-background/90 p-6 backdrop-blur-xl">
          <div className="grid h-full max-h-[90vh] w-full max-w-6xl grid-rows-[auto_minmax(0,1fr)] overflow-hidden border border-border/50 bg-panel rounded-2xl shadow-2xl">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 border-b border-border/50 px-6 py-4 bg-panel-raised/50">
              <div className="flex items-center gap-4 min-w-0">
                <div className={"h-2.5 w-2.5 rounded-full shrink-0 " + (focused.online ? "bg-ok animate-heartbeat" : "bg-muted")} />
                <div className="min-w-0">
                  <h2 className="truncate text-lg font-bold">{focused.junctionName}</h2>
                  <div className="label-xs text-muted-foreground">{focused.id} · Focus View</div>
                </div>
                {focusedHealth && (
                  <div className="flex items-center gap-6 ml-8 pl-8 border-l border-border/50">
                    <Chip label="FPS" value={String(focusedHealth.fps)} />
                    <Chip label="Confidence" value={focusedHealth.confidence + "%"} />
                    <Chip label="Weather" value={focusedHealth.weather ?? "—"} />
                    <Chip label="Uptime" value={focusedHealth.uptime} />
                  </div>
                )}
              </div>
              <button onClick={() => setFocus(null)} className="grid h-9 w-9 shrink-0 place-items-center border border-border/50 rounded-full bg-panel-raised hover:bg-white/10 transition-colors">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="grid min-h-0 gap-6 overflow-y-auto p-6 lg:grid-cols-[2fr_1fr]">
              <div className="min-w-0 flex flex-col h-full">
                <div className="rounded-xl overflow-hidden border border-border/50 shadow-xl bg-black flex-1">
                  <CameraTile feed={focused} overlays={overlays} brtsOnly={false} large />
                </div>
              </div>

              <div className="min-w-0 flex flex-col gap-4 overflow-hidden">
                <div className="panel-surface p-4 border-border/50 bg-panel-raised/30 flex-1 overflow-hidden flex flex-col">
                  <div className="flex items-center justify-between mb-3">
                    <div className="label-xs text-muted-foreground">LIVE DETECTION STREAM</div>
                    <span className="flex items-center gap-1 text-[10px] text-ok font-mono font-bold">
                      <span className="h-1.5 w-1.5 rounded-full bg-ok animate-blink" /> ACTIVE
                    </span>
                  </div>
                  <div className="flex-1 overflow-y-auto pr-2 space-y-2">
                    {focusedEvents.map((e) => {
                      const isBrts = e.event === "brts_intrusion";
                      const isViol = e.event === "lane_violation";
                      return (
                        <div key={e.id} className={"p-2.5 rounded-lg border flex flex-col gap-1 transition-all " + 
                          (isBrts ? "border-crit/50 bg-crit/10" : isViol ? "border-warn/40 bg-warn/10" : "border-border/50 bg-panel-raised/50")}>
                          <div className="flex justify-between items-center">
                            <span className={"text-xs font-bold tracking-tight " + (isBrts ? "text-crit" : isViol ? "text-warn" : "text-foreground")}>
                              {isBrts ? "🚨 BRTS INTRUSION" : isViol ? "⚠️ LANE VIOLATION" : e.event.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="num text-[10px] text-muted-foreground font-mono">{fmtTime(e.ts)}</span>
                          </div>
                          <div className="text-[11px] text-muted-foreground flex justify-between items-center">
                            <span className="capitalize font-medium text-foreground/80">{e.objectClass}</span>
                            <span className="num font-mono text-[10px] bg-black/40 px-1.5 py-0.5 rounded border border-white/5">{e.confidence}% conf</span>
                          </div>
                          {e.note && <div className="text-[10px] text-muted-foreground font-mono">{e.note}</div>}
                        </div>
                      );
                    })}
                    {focusedEvents.length === 0 && <p className="text-sm text-muted-foreground text-center py-6">Connecting to live vision detector...</p>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

function Toggle({ active, onClick, label, icon }: { active: boolean; onClick: () => void; label: string; icon?: React.ReactNode; }) {
  return (
    <button onClick={onClick} className={"num flex items-center gap-2 px-4 py-2 text-[11px] font-semibold rounded-lg transition-all " + (active ? "bg-foreground text-background shadow-md" : "text-muted-foreground hover:bg-white/5")}>
      {icon}
      {label}
    </button>
  );
}

function Chip({ label, value }: { label: string; value: string; }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="label-xs text-muted-foreground">{label}</div>
      <div className="num text-sm font-semibold tracking-tight">{value}</div>
    </div>
  );
}
