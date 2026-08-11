import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowUpRight, TrendingDown } from "lucide-react";
import { QUEUE_JUNCTIONS } from "@/lib/mock-traffic";
import type { Kpi } from "@/lib/traffic-types";

const LINE_COLORS = [
  "var(--live)",
  "var(--warn)",
  "var(--crit)",
  "var(--ok)",
  "var(--predict)",
];

export function KPIPanel({
  kpis,
  queue,
}: {
  kpis: Kpi[];
  queue: ({ t: string } & Record<string, number | string>)[];
}) {
  return (
    <section className="flex min-w-0 flex-col gap-2">
      {kpis.map((k) => (
        <KpiCard key={k.key} kpi={k} />
      ))}

      <div className="panel-surface min-w-0 p-3">
        <div className="mb-1 flex items-baseline justify-between gap-2">
          <div>
            <div className="label-xs">Queue length per junction</div>
            <h3 className="text-xs font-semibold">Last 30 minutes · live</h3>
          </div>
          <span className="num text-[10px] text-primary">
            <span className="mr-1 inline-block h-1.5 w-1.5 animate-blink rounded-full bg-primary align-middle" />
            AUTO-SCROLL
          </span>
        </div>
        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={queue} margin={{ top: 6, right: 6, left: -22, bottom: 0 }}>
              <CartesianGrid stroke="var(--grid-line)" strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="t"
                tick={{ fontSize: 9, fill: "var(--muted-foreground)" }}
                tickLine={false}
                axisLine={{ stroke: "var(--border)" }}
                interval={6}
              />
              <YAxis
                tick={{ fontSize: 9, fill: "var(--muted-foreground)" }}
                tickLine={false}
                axisLine={false}
                width={38}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--popover)",
                  border: "1px solid var(--border)",
                  borderRadius: 2,
                  fontSize: 11,
                }}
                labelStyle={{ color: "var(--muted-foreground)" }}
              />
              {QUEUE_JUNCTIONS.map((j, i) => (
                <Line
                  key={j.id}
                  type="monotone"
                  dataKey={j.id}
                  name={j.name}
                  stroke={LINE_COLORS[i % LINE_COLORS.length]}
                  strokeWidth={1.4}
                  dot={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1">
          {QUEUE_JUNCTIONS.map((j, i) => (
            <span key={j.id} className="flex items-center gap-1 text-[10px] text-muted-foreground">
              <span
                className="h-0.5 w-3"
                style={{ backgroundColor: LINE_COLORS[i % LINE_COLORS.length] }}
              />
              {j.name}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function KpiCard({ kpi }: { kpi: Kpi }) {
  const toneClass =
    kpi.baselineTone === "ok"
      ? "border-ok/40 bg-ok/10 text-ok"
      : kpi.baselineTone === "warn"
        ? "border-warn/40 bg-warn/10 text-warn"
        : "border-crit/40 bg-crit/10 text-crit";

  const value =
    kpi.key === "throughput"
      ? kpi.value.toLocaleString("en-IN")
      : kpi.key === "waitReduction"
        ? kpi.value.toFixed(1)
        : String(Math.round(kpi.value));

  return (
    <div className="panel-surface min-w-0 p-3">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-2">
        <div className="min-w-0">
          <div className="label-xs truncate">{kpi.label}</div>
          <div className="mt-0.5 flex items-baseline gap-1">
            <span className="num text-2xl font-semibold leading-none transition-all duration-500">
              {value}
            </span>
            <span className="num text-[10px] text-muted-foreground">{kpi.unit}</span>
          </div>
        </div>
        <div className="h-9 w-20 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={kpi.spark} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id={`sp-${kpi.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--live)" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="var(--live)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="v"
                stroke="var(--live)"
                strokeWidth={1.2}
                fill={`url(#sp-${kpi.key})`}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div
        className={`num mt-2 inline-flex items-center gap-1 border px-1.5 py-0.5 text-[10px] font-medium ${toneClass}`}
      >
        {kpi.baselineTone === "ok" ? (
          <ArrowUpRight className="h-3 w-3" />
        ) : (
          <TrendingDown className="h-3 w-3" />
        )}
        {kpi.baseline}
      </div>
    </div>
  );
}
