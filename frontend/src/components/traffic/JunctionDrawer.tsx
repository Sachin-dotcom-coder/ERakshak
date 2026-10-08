import { useState, useEffect } from "react";
import { X, Video, Gauge, SplitSquareHorizontal } from "lucide-react";
import { CONGESTION_COLOR } from "@/lib/mock-traffic";
import { getVideoForFeed } from "@/lib/video-feeds";
import type { Junction } from "@/lib/traffic-types";

export function JunctionDrawer({
  junction,
  onClose,
}: {
  junction: Junction | null;
  onClose: () => void;
}) {
  const [whatIf, setWhatIf] = useState(false);
  const open = !!junction;

  // Close on Escape key press
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open || !junction) return null;

  const videoSrc = getVideoForFeed(junction.camera?.id || junction.id);
  const hasVideo = !!videoSrc;

  const statusColor = (st: string) =>
    st === "GREEN" ? "#22c55e" : st === "YELLOW" ? "#f59e0b" : "#ef4444";

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      {/* Backdrop click to dismiss */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Modal Popup Window */}
      <div className="relative w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl border border-zinc-800 bg-[#0d0d10] shadow-2xl overflow-hidden z-10 animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800/80 px-5 py-3.5 bg-zinc-950/60 backdrop-blur-md shrink-0">
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-zinc-300 bg-zinc-900 px-2 py-0.5 rounded-md border border-zinc-800">
                {junction.id}
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-500">
                {junction.zone}
              </span>
              <span
                className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md border"
                style={{
                  borderColor: `${statusColor(junction.signalStatus)}50`,
                  color: statusColor(junction.signalStatus),
                  backgroundColor: `${statusColor(junction.signalStatus)}15`,
                }}
              >
                {junction.signalStatus} · {junction.signalCountdown}s
              </span>
            </div>
            <h2 className="mt-1 text-base font-bold text-zinc-100 truncate">{junction.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="h-8 w-8 rounded-full border border-zinc-700/80 bg-zinc-800/80 hover:bg-zinc-700 text-zinc-300 hover:text-white transition-all flex items-center justify-center shrink-0 active:scale-95"
            title="Close popup (Esc)"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4 sm:p-5">
          {/* Camera / Video Feed */}
          <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950">
            {hasVideo ? (
              <video
                src={videoSrc}
                autoPlay
                loop
                muted
                playsInline
                className="absolute inset-0 h-full w-full object-cover"
              />
            ) : (
              <div className="absolute inset-0 bg-[#07090e]">
                <div className="absolute inset-0 opacity-20 [background-image:repeating-linear-gradient(0deg,transparent_0_3px,#27272a_3px_4px)]" />
                <div className="absolute inset-x-0 h-8 bg-white/5 animate-scan" />
                <Video className="absolute inset-0 m-auto h-10 w-10 text-zinc-700" />
              </div>
            )}
            <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5 rounded-md border border-crit/60 bg-crit/20 backdrop-blur-md px-2 py-0.5">
              <span className="h-1.5 w-1.5 animate-blink rounded-full bg-crit" />
              <span className="num text-[10px] font-bold text-crit tracking-wider">LIVE</span>
            </div>
            <div className="num absolute bottom-2.5 left-2.5 text-[10px] font-mono text-zinc-300 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-md border border-white/10">
              {junction.camera.id} · 1920x1080 · 24fps
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <Metric label="Congestion" value={String(junction.congestionIndex)} color={CONGESTION_COLOR[junction.congestion]} />
            <Metric
              label="Signal Phase"
              value={`${junction.signalStatus}`}
              color={statusColor(junction.signalStatus)}
            />
            <Metric label="Phase Timer" value={`${junction.signalCountdown}s`} color="#38bdf8" />
            <Metric label="Avg wait" value={`${junction.avgWait}s`} />
          </div>

          {/* 4-Way Intersection Arms */}
          <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-bold text-zinc-300">4-Way Intersection Arms</span>
              <span className="text-[10px] text-zinc-400 font-mono font-bold bg-zinc-800 px-2 py-0.5 rounded">
                4 Intersecting Roads
              </span>
            </div>
            <FourWayIntersectionDiagram junction={junction} />
          </div>

          {/* Per-Lane Approach Density & Queues */}
          <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-4">
            <div className="text-xs font-bold text-zinc-300 mb-3">Per-lane approach density & queues</div>
            <div className="space-y-3">
              {junction.lanes.map((l) => (
                <div key={l.id}>
                  <div className="flex items-baseline justify-between gap-2 text-xs">
                    <span className="truncate text-zinc-200 font-medium">{l.name}</span>
                    <span className="num shrink-0 text-zinc-400 font-mono text-[11px]">
                      Q {l.queue} veh · {l.arrivalRate}/min
                    </span>
                  </div>
                  <div className="mt-1.5 h-2 w-full rounded-full bg-zinc-800/80 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${l.density}%`,
                        backgroundColor:
                          l.density > 80
                            ? "var(--crit)"
                            : l.density > 55
                              ? "var(--warn)"
                              : "var(--ok)",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Signal cycle comparison */}
          <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-4">
            <div className="text-xs font-bold text-zinc-300 mb-3 flex items-center gap-1.5">
              <SplitSquareHorizontal className="h-4 w-4 text-zinc-400" />
              <span>Signal cycle comparison</span>
            </div>
            <CycleBar label="Adaptive (live)" cycle={junction.adaptiveCycle} highlight />
            <CycleBar label="Static timer (baseline)" cycle={junction.staticCycle} />
          </div>

          {/* What-if simulation */}
          <div
            className={`rounded-xl border p-4 transition-all ${
              whatIf ? "border-crit/50 bg-crit/10" : "border-zinc-800 bg-zinc-900/40"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="min-w-0">
                <div className="text-xs font-bold text-zinc-200 flex items-center gap-1.5">
                  <Gauge className="h-4 w-4 text-zinc-400" /> What-if simulation
                </div>
                <p className="mt-1 text-[11px] text-zinc-400">
                  Revert this junction to fixed timing (SUMO run #418)
                </p>
              </div>
              <button
                onClick={() => setWhatIf((v) => !v)}
                role="switch"
                aria-checked={whatIf}
                className={`relative h-6 w-11 shrink-0 rounded-full border transition-colors ${
                  whatIf ? "border-crit bg-crit/40" : "border-zinc-700 bg-zinc-800"
                }`}
              >
                <span
                  className={`absolute top-0.5 h-4.5 w-4.5 rounded-full transition-all ${
                    whatIf ? "left-[22px] bg-crit" : "left-0.5 bg-zinc-400"
                  }`}
                />
              </button>
            </div>
            {whatIf && (
              <div className="mt-3.5 grid grid-cols-3 gap-2.5">
                <Metric label="Congestion" value={`+${junction.whatIfDelta}%`} color="var(--crit)" />
                <Metric
                  label="Avg wait"
                  value={`${Math.round(junction.avgWait * (1 + junction.whatIfDelta / 100))}s`}
                  color="var(--crit)"
                />
                <Metric
                  label="Throughput"
                  value={`-${Math.round(junction.whatIfDelta * 0.7)}%`}
                  color="var(--crit)"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-800/80 bg-zinc-900/50 p-2.5">
      <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider truncate">
        {label}
      </div>
      <div className="num text-base font-bold mt-0.5" style={color ? { color } : undefined}>
        {value}
      </div>
    </div>
  );
}

function CycleBar({
  label,
  cycle,
  highlight = false,
}: {
  label: string;
  cycle: { phase: string; seconds: number; color: string }[];
  highlight?: boolean;
}) {
  const total = cycle.reduce((a, c) => a + c.seconds, 0);
  return (
    <div className="mb-2.5 last:mb-0">
      <div className="flex items-baseline justify-between text-xs mb-1">
        <span className={highlight ? "text-zinc-200 font-semibold" : "text-zinc-400"}>{label}</span>
        <span className="num text-zinc-400 font-mono text-[11px]">{total}s cycle</span>
      </div>
      <div className={`flex h-4 w-full rounded-md overflow-hidden border ${highlight ? "border-zinc-600" : "border-zinc-800"}`}>
        {cycle.map((c) => (
          <div
            key={c.phase}
            className="num grid place-items-center text-[9px] font-bold text-zinc-950 font-mono"
            style={{
              width: `${(c.seconds / total) * 100}%`,
              backgroundColor: c.color,
              opacity: highlight ? 0.95 : 0.6,
            }}
          >
            {c.seconds}
          </div>
        ))}
      </div>
    </div>
  );
}

function FourWayIntersectionDiagram({ junction }: { junction: Junction }) {
  const nLane = junction.lanes.find((l) => l.name.toLowerCase().includes("north")) || junction.lanes[0];
  const sLane = junction.lanes.find((l) => l.name.toLowerCase().includes("south")) || junction.lanes[1];
  const eLane = junction.lanes.find((l) => l.name.toLowerCase().includes("east")) || junction.lanes[2];
  const wLane = junction.lanes.find((l) => l.name.toLowerCase().includes("west")) || junction.lanes[3];

  let activeArm: "N" | "E" | "S" | "W" = "N";
  
  const phaseLower = ((junction as any).current_phase || "").toLowerCase();
  if (phaseLower.includes("south")) {
    activeArm = "S";
  } else if (phaseLower.includes("east")) {
    activeArm = "E";
  } else if (phaseLower.includes("west")) {
    activeArm = "W";
  } else if (phaseLower.includes("north")) {
    activeArm = "N";
  } else {
    const armList: ("N" | "E" | "S" | "W")[] = ["N", "E", "S", "W"];
    const jNum = parseInt(junction.id.replace(/\D/g, "") || "1", 10);
    const timeBucket = Math.floor((junction.signalCountdown || 10) / 12);
    activeArm = armList[(jNum + timeBucket) % 4] || "N";
  }

  const isYellow = junction.signalStatus === "YELLOW";
  const nStatus = activeArm === "N" ? (isYellow ? "YELLOW" : "GREEN") : "RED";
  const sStatus = activeArm === "S" ? (isYellow ? "YELLOW" : "GREEN") : "RED";
  const eStatus = activeArm === "E" ? (isYellow ? "YELLOW" : "GREEN") : "RED";
  const wStatus = activeArm === "W" ? (isYellow ? "YELLOW" : "GREEN") : "RED";

  const statusColor = (st: string) =>
    st === "GREEN" ? "#22c55e" : st === "YELLOW" ? "#f59e0b" : "#ef4444";

  return (
    <div className="relative mx-auto my-2 flex h-52 w-full max-w-[320px] items-center justify-center rounded-xl border border-zinc-800 bg-[#05070c] p-2">
      {/* Road Cross Overlay */}
      <div className="absolute inset-x-0 top-1/2 h-14 -translate-y-1/2 bg-[#121722] border-y border-zinc-800/60" />
      <div className="absolute inset-y-0 left-1/2 w-14 -translate-x-1/2 bg-[#121722] border-x border-zinc-800/60" />

      {/* Junction Box Center */}
      <div className="relative z-10 flex h-14 w-14 flex-col items-center justify-center rounded-xl border border-zinc-700 bg-zinc-950 text-center shadow-xl">
        <span className="text-[8px] font-bold text-zinc-300 uppercase tracking-wider">PROTECTED</span>
        <span className="num text-[12px] font-bold text-white">{junction.signalCountdown}s</span>
        <span className="text-[7px] text-zinc-400 uppercase font-mono">1-ARM GREEN</span>
      </div>

      {/* NORTH ARM (Top) */}
      <div className="absolute top-1 left-1/2 z-20 flex -translate-x-1/2 flex-col items-center">
        <span className="text-[9px] font-mono font-bold text-zinc-400">NORTH (N)</span>
        <div
          className="my-0.5 flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-bold"
          style={{
            borderColor: statusColor(nStatus),
            color: statusColor(nStatus),
            backgroundColor: `${statusColor(nStatus)}18`,
          }}
        >
          <span>⬆️ {nStatus}</span>
          <span className="num font-mono text-zinc-200">Q:{nLane?.queue ?? 0}</span>
        </div>
      </div>

      {/* SOUTH ARM (Bottom) */}
      <div className="absolute bottom-1 left-1/2 z-20 flex -translate-x-1/2 flex-col items-center">
        <div
          className="my-0.5 flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-bold"
          style={{
            borderColor: statusColor(sStatus),
            color: statusColor(sStatus),
            backgroundColor: `${statusColor(sStatus)}18`,
          }}
        >
          <span>⬇️ {sStatus}</span>
          <span className="num font-mono text-zinc-200">Q:{sLane?.queue ?? 0}</span>
        </div>
        <span className="text-[9px] font-mono font-bold text-zinc-400">SOUTH (S)</span>
      </div>

      {/* WEST ARM (Left) */}
      <div className="absolute left-1 top-1/2 z-20 flex -translate-y-1/2 flex-col items-start">
        <span className="text-[9px] font-mono font-bold text-zinc-400">WEST (W)</span>
        <div
          className="my-0.5 flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-bold"
          style={{
            borderColor: statusColor(wStatus),
            color: statusColor(wStatus),
            backgroundColor: `${statusColor(wStatus)}18`,
          }}
        >
          <span>⬅️ {wStatus}</span>
          <span className="num font-mono text-zinc-200">Q:{wLane?.queue ?? 0}</span>
        </div>
      </div>

      {/* EAST ARM (Right) */}
      <div className="absolute right-1 top-1/2 z-20 flex -translate-y-1/2 flex-col items-end">
        <span className="text-[9px] font-mono font-bold text-zinc-400">EAST (E)</span>
        <div
          className="my-0.5 flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[9px] font-bold"
          style={{
            borderColor: statusColor(eStatus),
            color: statusColor(eStatus),
            backgroundColor: `${statusColor(eStatus)}18`,
          }}
        >
          <span>➡️ {eStatus}</span>
          <span className="num font-mono text-zinc-200">Q:{eLane?.queue ?? 0}</span>
        </div>
      </div>
    </div>
  );
}
