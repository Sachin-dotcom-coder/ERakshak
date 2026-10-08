import { useEffect, useState } from "react";
import { Activity, Wifi, WifiOff, TriangleAlert, Circle } from "lucide-react";

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

/** 5-segment congestion bar — fills left to right */
function CongestionBar({ value }: { value: number }) {
  const filled = Math.ceil((value / 100) * 5);
  const segs = [
    { color: "#22d35a" },
    { color: "#84cc16" },
    { color: "#f59e0b" },
    { color: "#f97316" },
    { color: "#ef4444" },
  ];
  return (
    <div className="congestion-bar w-20">
      {segs.map((s, i) => (
        <div
          key={i}
          className="congestion-bar-seg"
          style={{
            backgroundColor: s.color,
            opacity: i < filled ? 1 : 0.15,
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
    <header className="sticky top-0 z-20 border-b border-border bg-panel/98 backdrop-blur-md">
      <div className="flex items-center gap-0 h-12 px-4 overflow-x-auto">

        {/* ── System name ───────────── */}
        <div className="flex items-center gap-2.5 mr-6 shrink-0">
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-bold tracking-tight leading-none">
              E·<span className="text-primary">RAKSHAK</span>
            </span>
            <span className="label-xs" style={{ fontSize: 8 }}>
              SURAT ADAPTIVE TRAFFIC CONTROL
            </span>
          </div>
        </div>

        {/* ── Divider ───────────────── */}
        <div className="h-7 w-px bg-border mr-6 shrink-0" />

        {/* ── Status chips ──────────── */}
        <div className="flex items-center gap-5 mr-auto">

          {/* WS Connection */}
          <Chip
            icon={
              connected ? (
                <Circle className="h-2 w-2 fill-ok text-ok animate-heartbeat" />
              ) : (
                <Circle className="h-2 w-2 fill-crit text-crit animate-blink" />
              )
            }
            label="TELEMETRY"
            value={connected ? "LIVE" : "OFFLINE"}
            valueClass={connected ? "text-ok" : "text-crit"}
          />

          {/* Junctions online */}
          <Chip
            icon={<Wifi className="h-3.5 w-3.5 text-primary" />}
            label="JUNCTIONS"
            value={`${junctionsOnline} / ${TOTAL_JUNCTIONS}`}
            valueClass="text-foreground"
          />

          {/* BRTS Violations */}
          <div className="flex items-center gap-2">
            <TriangleAlert
              className={`h-3.5 w-3.5 shrink-0 ${intrusions > 0 ? "text-crit" : "text-muted-foreground"}`}
            />
            <div>
              <div className="label-xs">BRTS VIOLATIONS</div>
              <div className="flex items-center gap-1.5">
                <span
                  className={`num inline-flex items-center justify-center min-w-[28px] h-5 border px-1.5 text-sm font-bold rounded-sm ${
                    intrusions > 0
                      ? "animate-blink border-crit/50 bg-crit/15 text-crit"
                      : "border-border text-muted-foreground"
                  }`}
                >
                  {intrusions}
                </span>
                {intrusions > 0 && (
                  <span className="label-xs text-crit/70">ACTIVE</span>
                )}
              </div>
            </div>
          </div>

          {/* Congestion index */}
          <div className="flex items-center gap-2">
            <Activity className={`h-3.5 w-3.5 shrink-0 ${congTone}`} />
            <div>
              <div className="label-xs">CITY CONGESTION</div>
              <div className="flex items-center gap-2">
                <span className={`num text-sm font-bold ${congTone}`}>
                  {avgCongestion}
                </span>
                <CongestionBar value={avgCongestion} />
              </div>
            </div>
          </div>
        </div>

        {/* ── Right side ────────────── */}
        <div className="flex items-center gap-4 ml-6 shrink-0">
          {/* IST Clock */}
          <div className="flex flex-col items-end">
            <div className="label-xs">IST</div>
            <div className="num text-sm font-semibold tabular-nums text-primary">
              {clock}
            </div>
          </div>

          {right && (
            <>
              <div className="h-7 w-px bg-border" />
              {right}
            </>
          )}
        </div>
      </div>
    </header>
  );
}

function Chip({
  icon,
  label,
  value,
  valueClass = "",
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  valueClass?: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="shrink-0">{icon}</span>
      <div>
        <div className="label-xs">{label}</div>
        <div className={`num text-sm font-semibold ${valueClass}`}>{value}</div>
      </div>
    </div>
  );
}
