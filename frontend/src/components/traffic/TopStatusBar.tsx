import { useEffect, useState } from "react";
import { Activity, Radio, TriangleAlert, Signal } from "lucide-react";
import { fmtTime } from "@/lib/mock-traffic";
import { SuratTrafficNexusLogo } from "./Logo";

type Props = {
  junctionsOnline: number;
  intrusions: number;
  avgCongestion: number;
  connected: boolean;
  right?: React.ReactNode;
};

export function TopStatusBar({
  junctionsOnline,
  intrusions,
  avgCongestion,
  connected,
  right,
}: Props) {
  const [clock, setClock] = useState<string>("--:--:--");
  useEffect(() => {
    const set = () => setClock(fmtTime(Date.now()));
    set();
    const id = setInterval(set, 1000);
    return () => clearInterval(id);
  }, []);

  const tone =
    avgCongestion > 70 ? "text-crit" : avgCongestion > 45 ? "text-warn" : "text-ok";

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-panel/95 backdrop-blur">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 px-3 py-2 lg:flex lg:flex-wrap lg:justify-between lg:px-4">
        <div className="flex min-w-0 items-center gap-2.5">
          <SuratTrafficNexusLogo className="h-6 w-6 shrink-0" />
          <div className="min-w-0">
            <div className="truncate text-sm font-bold tracking-tight">
              TrafficSense <span className="text-primary">Surat</span>
            </div>
            <div className="label-xs truncate">
              Surat City Police · Adaptive Traffic Control Room
            </div>
          </div>
        </div>

        <div className="col-span-2 flex flex-wrap items-center gap-x-5 gap-y-2 lg:col-auto">
          <Stat
            icon={<Signal className="h-3.5 w-3.5 text-ok" />}
            label="Junctions online"
            value={`${junctionsOnline}/${junctionsOnline}`}
          />
          <div className="flex items-center gap-2">
            <TriangleAlert
              className={`h-3.5 w-3.5 ${intrusions > 0 ? "text-crit" : "text-muted-foreground"}`}
            />
            <div>
              <div className="label-xs">Active BRTS violations</div>
              <div className="flex items-center gap-2">
                <span
                  className={`num inline-flex min-w-6 items-center justify-center border px-1.5 text-sm font-semibold ${
                    intrusions > 0
                      ? "animate-blink border-crit/60 bg-crit/15 text-crit"
                      : "border-border text-muted-foreground"
                  }`}
                >
                  {intrusions}
                </span>
              </div>
            </div>
          </div>
          <Stat
            icon={<Activity className={`h-3.5 w-3.5 ${tone}`} />}
            label="City congestion index"
            value={`${avgCongestion}`}
            valueClass={tone}
          />
          <Stat
            icon={<Radio className="h-3.5 w-3.5 text-primary" />}
            label="Telemetry"
            value={connected ? "STREAMING" : "OFFLINE"}
            valueClass={connected ? "text-primary" : "text-crit"}
            dot
          />
          <div>
            <div className="label-xs">IST</div>
            <div className="num text-sm font-semibold tabular-nums">{clock}</div>
          </div>
          {right}
        </div>
      </div>
    </header>
  );
}

function Stat({
  icon,
  label,
  value,
  valueClass = "",
  dot = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  valueClass?: string;
  dot?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="shrink-0">{icon}</span>
      <div>
        <div className="label-xs">{label}</div>
        <div className={`num flex items-center gap-1.5 text-sm font-semibold ${valueClass}`}>
          {dot && <span className="h-1.5 w-1.5 animate-blink rounded-full bg-current" />}
          {value}
        </div>
      </div>
    </div>
  );
}
