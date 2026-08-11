import { useState } from "react";
import { X, Video, Gauge, SplitSquareHorizontal } from "lucide-react";
import { CONGESTION_COLOR } from "@/lib/mock-traffic";
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

  return (
    <>
      {open && (
        <button
          aria-label="Close detail"
          onClick={onClose}
          className="fixed inset-0 z-30 bg-background/60 backdrop-blur-[2px] lg:hidden"
        />
      )}
      <aside
        className={`fixed right-0 top-0 z-40 flex h-screen w-full max-w-[420px] flex-col border-l border-border bg-panel transition-transform duration-300 ${
          open ? "translate-x-0" : "pointer-events-none translate-x-full"
        }`}
      >
        {junction && (
          <>
            <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-2 border-b border-border px-3 py-2.5">
              <div className="min-w-0">
                <div className="label-xs truncate">
                  {junction.id} · {junction.zone}
                </div>
                <h2 className="truncate text-sm font-semibold">{junction.name}</h2>
              </div>
              <button
                onClick={onClose}
                className="grid h-7 w-7 shrink-0 place-items-center border border-border text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
              {/* camera */}
              <div className="relative aspect-video w-full overflow-hidden border border-border bg-[oklch(0.14_0.02_264)]">
                <div className="absolute inset-0 opacity-30 [background-image:repeating-linear-gradient(0deg,transparent_0_3px,oklch(0.3_0.03_258)_3px_4px)]" />
                <div className="absolute inset-x-0 h-8 bg-primary/10 animate-scan" />
                <div className="absolute left-2 top-2 flex items-center gap-1.5 border border-crit/60 bg-crit/15 px-1.5 py-0.5">
                  <span className="h-1.5 w-1.5 animate-blink rounded-full bg-crit" />
                  <span className="num text-[10px] font-semibold text-crit">LIVE</span>
                </div>
                <div className="num absolute bottom-2 left-2 text-[10px] text-muted-foreground">
                  {junction.camera.id} · 1920x1080 · 24fps
                </div>
                <Video className="absolute inset-0 m-auto h-8 w-8 text-muted-foreground/40" />
              </div>

              <div className="grid grid-cols-4 gap-2">
                <Metric label="Congestion" value={String(junction.congestionIndex)} color={CONGESTION_COLOR[junction.congestion]} />
                <Metric
                  label="Signal Phase"
                  value={`${junction.signalStatus}`}
                  color={
                    junction.signalStatus === "GREEN"
                      ? "#00ff88"
                      : junction.signalStatus === "YELLOW"
                        ? "#ffcc00"
                        : "#ff3366"
                  }
                />
                <Metric label="Phase Timer" value={`${junction.signalCountdown}s`} color="#00f3ff" />
                <Metric label="Avg wait" value={`${junction.avgWait}s`} />
              </div>

              {/* lanes */}
              <div className="panel-surface p-3">
                <div className="label-xs mb-2">Per-lane density</div>
                <div className="space-y-2.5">
                  {junction.lanes.map((l) => (
                    <div key={l.id}>
                      <div className="flex items-baseline justify-between gap-2 text-[11px]">
                        <span className="truncate">{l.name}</span>
                        <span className="num shrink-0 text-muted-foreground">
                          Q {l.queue} · {l.arrivalRate}/min
                        </span>
                      </div>
                      <div className="mt-1 h-1.5 w-full bg-secondary">
                        <div
                          className="h-full transition-all duration-700"
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

              {/* cycles */}
              <div className="panel-surface p-3">
                <div className="label-xs mb-2 flex items-center gap-1.5">
                  <SplitSquareHorizontal className="h-3.5 w-3.5" /> Signal cycle comparison
                </div>
                <CycleBar label="Adaptive (live)" cycle={junction.adaptiveCycle} highlight />
                <CycleBar label="Static timer (baseline)" cycle={junction.staticCycle} />
              </div>

              {/* what-if */}
              <div
                className={`border p-3 transition-colors ${
                  whatIf ? "border-crit/50 bg-crit/10" : "border-border bg-panel"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="min-w-0">
                    <div className="label-xs flex items-center gap-1.5">
                      <Gauge className="h-3.5 w-3.5" /> What-if simulation
                    </div>
                    <p className="mt-0.5 text-[11px] text-muted-foreground">
                      Revert this junction to fixed timing (SUMO run #418)
                    </p>
                  </div>
                  <button
                    onClick={() => setWhatIf((v) => !v)}
                    role="switch"
                    aria-checked={whatIf}
                    className={`relative h-5 w-9 shrink-0 border transition-colors ${
                      whatIf ? "border-crit bg-crit/30" : "border-border bg-secondary"
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 h-3.5 w-3.5 transition-all ${
                        whatIf ? "left-[18px] bg-crit" : "left-0.5 bg-muted-foreground"
                      }`}
                    />
                  </button>
                </div>
                {whatIf && (
                  <div className="mt-3 grid grid-cols-3 gap-2">
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
          </>
        )}
      </aside>
    </>
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
    <div className="panel-surface p-2">
      <div className="label-xs truncate">{label}</div>
      <div className="num text-base font-semibold" style={color ? { color } : undefined}>
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
    <div className="mb-2 last:mb-0">
      <div className="flex items-baseline justify-between text-[11px]">
        <span className={highlight ? "text-primary" : "text-muted-foreground"}>{label}</span>
        <span className="num text-muted-foreground">{total}s cycle</span>
      </div>
      <div className={`mt-1 flex h-4 w-full overflow-hidden border ${highlight ? "border-primary/40" : "border-border"}`}>
        {cycle.map((c) => (
          <div
            key={c.phase}
            className="num grid place-items-center text-[9px] font-semibold text-background"
            style={{
              width: `${(c.seconds / total) * 100}%`,
              backgroundColor: c.color,
              opacity: highlight ? 0.95 : 0.5,
            }}
          >
            {c.seconds}
          </div>
        ))}
      </div>
    </div>
  );
}
