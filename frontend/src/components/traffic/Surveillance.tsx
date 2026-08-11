import { useMemo, useState } from "react";
import { X } from "lucide-react";
import { AppShell } from "./AppShell";
import { TopStatusBar } from "./TopStatusBar";
import { CameraTile } from "./CameraTile";
import { DetectionLog } from "./DetectionLog";
import { useTrafficData } from "@/hooks/useTrafficData";
import { useCameraFeeds } from "@/hooks/useCameraFeeds";
import { fmtTime } from "@/lib/mock-traffic";

export function Surveillance() {
  const { stats, connected, detections, junctions } = useTrafficData();
  const { feeds, online, total } = useCameraFeeds();
  const [overlays, setOverlays] = useState(true);
  const [brtsOnly, setBrtsOnly] = useState(false);
  const [focus, setFocus] = useState<string | null>(null);

  const focused = feeds.find((f) => f.id === focus) ?? null;
  const focusedJunction = junctions.find((j) => j.id === focused?.junctionId) ?? null;
  const focusedEvents = useMemo(
    () => detections.filter((d) => d.cameraId === focus).slice(0, 12),
    [detections, focus],
  );

  return (
    <AppShell>
      <TopStatusBar
        junctionsOnline={stats.junctionsOnline}
        intrusions={stats.activeIntrusions}
        avgCongestion={stats.avgCongestion}
        connected={connected}
      />

      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 border-b border-border bg-panel/60 px-3 py-2">
        <div className="flex min-w-0 flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="label-xs">Camera health</span>
            <span className="num text-xs font-semibold">
              {online}/{total} online
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-1">
            {feeds.map((f) => (
              <span
                key={f.id}
                title={`${f.id} · ${f.online ? "online" : "offline"}`}
                className="h-2 w-2 rounded-full"
                style={{
                  backgroundColor: f.online ? "var(--ok)" : "var(--crit)",
                  boxShadow: `0 0 6px ${f.online ? "var(--ok)" : "var(--crit)"}`,
                }}
              />
            ))}
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap gap-1.5">
          <Toggle active={overlays} onClick={() => setOverlays((v) => !v)} label="Detection overlays" />
          <Toggle active={brtsOnly} onClick={() => setBrtsOnly((v) => !v)} label="BRTS zones only" tone="crit" />
        </div>
      </div>

      <div className="grid gap-3 p-3 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="grid min-w-0 auto-rows-max items-start gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {feeds.map((f) => (
            <CameraTile
              key={f.id}
              feed={f}
              overlays={overlays}
              brtsOnly={brtsOnly}
              onClick={() => setFocus(f.id)}
            />
          ))}
        </div>
        <div className="min-h-[420px] xl:h-[calc(100vh-8.5rem)] xl:sticky xl:top-[4.5rem]">
          <DetectionLog
            events={detections}
            cameras={feeds.map((f) => ({ id: f.id, junctionName: f.junctionName }))}
          />
        </div>
      </div>

      {focused && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-background/80 p-3 backdrop-blur-sm">
          <div className="grid max-h-[92vh] w-full max-w-5xl grid-rows-[auto_minmax(0,1fr)] overflow-hidden border border-border bg-panel">
            <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 border-b border-border px-3 py-2">
              <div className="min-w-0">
                <div className="label-xs truncate">{focused.id} · focused view</div>
                <h2 className="truncate text-sm font-semibold">{focused.junctionName}</h2>
              </div>
              <button
                onClick={() => setFocus(null)}
                className="grid h-7 w-7 shrink-0 place-items-center border border-border text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="grid min-h-0 gap-3 overflow-y-auto p-3 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
              <div className="min-w-0">
                <CameraTile feed={focused} overlays={overlays} brtsOnly={brtsOnly} large />
              </div>
              <div className="min-w-0 space-y-3">
                <div className="panel-surface p-2.5">
                  <div className="label-xs mb-2">Lane-by-lane breakdown</div>
                  <div className="space-y-2">
                    {(focusedJunction?.lanes ?? []).map((l) => (
                      <div key={l.id}>
                        <div className="num flex justify-between text-[10px]">
                          <span>{l.name}</span>
                          <span className="text-muted-foreground">
                            {l.density}% · Q{l.queue}
                          </span>
                        </div>
                        <div className="mt-1 h-1.5 bg-secondary">
                          <div
                            className="h-full"
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
                <div className="panel-surface p-2.5">
                  <div className="label-xs mb-2">Camera event log</div>
                  <div className="num max-h-56 space-y-0.5 overflow-y-auto text-[10px]">
                    {focusedEvents.map((e) => (
                      <div key={e.id} className="border-b border-border/40 pb-0.5">
                        <span className="text-muted-foreground">{fmtTime(e.ts)}</span>{" "}
                        <span
                          className={
                            e.event === "brts_intrusion"
                              ? "text-crit"
                              : e.event === "lane_violation"
                                ? "text-warn"
                                : ""
                          }
                        >
                          {e.event}
                        </span>{" "}
                        <span className="text-muted-foreground">
                          {e.objectClass} · {e.confidence}%
                          {e.note ? ` · ${e.note}` : ""}
                        </span>
                      </div>
                    ))}
                    {focusedEvents.length === 0 && (
                      <p className="p-2 text-muted-foreground">awaiting events…</p>
                    )}
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

function Toggle({
  active,
  onClick,
  label,
  tone = "primary",
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  tone?: "primary" | "crit";
}) {
  const on =
    tone === "crit"
      ? "border-crit/50 bg-crit/15 text-crit"
      : "border-primary/50 bg-primary/15 text-primary";
  return (
    <button
      onClick={onClick}
      role="switch"
      aria-checked={active}
      className={`num flex items-center gap-2 border px-2 py-1 text-[11px] font-medium transition-colors ${
        active ? on : "border-border bg-panel-raised text-muted-foreground hover:text-foreground"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${active ? "bg-current" : "bg-muted-foreground"}`}
      />
      {label}
    </button>
  );
}
