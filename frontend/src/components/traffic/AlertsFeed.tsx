import { useMemo, useState } from "react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { Brain, Radio, ShieldAlert, TriangleAlert } from "lucide-react";
import { ago, fmtTime } from "@/lib/mock-traffic";
import type { Alert, Prediction } from "@/lib/traffic-types";

type Filter = "all" | "violations" | "brts" | "predictions";

const TABS: { id: Filter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "violations", label: "Violations" },
  { id: "brts", label: "BRTS" },
  { id: "predictions", label: "Predictions" },
];

export function AlertsFeed({
  alerts,
  predictions,
  onSelectJunction,
}: {
  alerts: Alert[];
  predictions: Prediction[];
  onSelectJunction: (id: string) => void;
}) {
  const [filter, setFilter] = useState<Filter>("all");

  const visibleAlerts = useMemo(() => {
    if (filter === "predictions") return [];
    if (filter === "violations") return alerts.filter((a) => a.kind === "violation");
    if (filter === "brts") return alerts.filter((a) => a.kind === "brts");
    return alerts;
  }, [alerts, filter]);

  const showPredictions = filter === "all" || filter === "predictions";

  return (
    <section className="panel-surface flex min-h-0 flex-col">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-2 border-b border-border px-3 py-2">
        <div className="min-w-0">
          <div className="label-xs">Operations feed</div>
          <h2 className="truncate text-sm font-semibold">
            Alerts &amp; Predictive Recommendations
          </h2>
        </div>
        <div className="flex shrink-0 flex-wrap gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setFilter(t.id)}
              className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold transition-all ${
                filter === t.id
                  ? "bg-foreground text-background shadow-sm"
                  : "bg-panel-raised text-muted-foreground hover:text-foreground border border-border"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid min-h-0 flex-1 gap-3 p-3 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
        <div className="min-w-0">
          <div className="label-xs mb-2 flex items-center gap-1.5">
            <Radio className="h-3.5 w-3.5 text-crit" /> Real-time alerts
          </div>
          <div className="max-h-36 2xl:max-h-52 space-y-1.5 overflow-y-auto pr-1">
            {visibleAlerts.map((a) => (
              <AlertRow key={a.id} alert={a} onClick={() => onSelectJunction(a.junctionId)} />
            ))}
            {visibleAlerts.length === 0 && (
              <p className="num p-4 text-center text-[11px] text-muted-foreground">
                No alerts in this filter.
              </p>
            )}
          </div>
        </div>

        {showPredictions && (
          <div className="min-w-0 border-l-0 lg:border-l lg:border-border lg:pl-3">
            <div className="label-xs mb-2 flex items-center gap-1.5 text-muted-foreground font-semibold">
              <Brain className="h-3.5 w-3.5 text-sky-400" />
              <span>AI Simple Traffic Actions</span>
              <span className="num rounded-md border border-sky-500/30 bg-sky-500/10 px-1.5 py-0.5 text-[9px] font-mono font-bold text-sky-400 tracking-wider">
                OPERATOR ACTION GUIDE
              </span>
            </div>
            <div className="max-h-36 2xl:max-h-52 space-y-2 overflow-y-auto pr-1">
              {predictions.map((p) => (
                <PredictionCard
                  key={p.id}
                  prediction={p}
                  onClick={() => onSelectJunction(p.junctionId)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function AlertRow({ alert, onClick }: { alert: Alert; onClick: () => void }) {
  const tone =
    alert.severity === "critical"
      ? { c: "text-crit", b: "border-l-crit", bg: "bg-crit/[0.07]" }
      : alert.severity === "warning"
        ? { c: "text-warn", b: "border-l-warn", bg: "bg-warn/[0.07]" }
        : { c: "text-muted-foreground", b: "border-l-border", bg: "" };

  const Icon = alert.kind === "brts" ? ShieldAlert : TriangleAlert;

  return (
    <button
      onClick={onClick}
      className={`grid w-full grid-cols-[auto_minmax(0,1fr)_auto] items-start gap-2.5 rounded-lg border border-border border-l-2 ${tone.b} ${tone.bg} px-2.5 py-2 text-left transition-colors hover:bg-panel-raised`}
    >
      <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${tone.c}`} />
      <span className="min-w-0">
        <span className="flex flex-wrap items-baseline gap-x-2">
          <span className="num text-[11px] font-semibold">{alert.junctionName}</span>
          <span className={`num text-[9px] uppercase tracking-wider ${tone.c}`}>
            {alert.severity}
          </span>
        </span>
        <span className="block truncate text-[11px] text-muted-foreground">
          {alert.message}
        </span>
      </span>
      <span className="num shrink-0 text-right text-[10px] text-muted-foreground">
        <span className="block">{fmtTime(alert.ts)}</span>
        <span className="block opacity-70">{ago(alert.ts)}</span>
      </span>
    </button>
  );
}

function PredictionCard({
  prediction,
  onClick,
}: {
  prediction: Prediction;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full rounded-xl border border-sky-500/25 bg-sky-500/[0.04] p-3 text-left transition-all hover:bg-sky-500/[0.08] hover:border-sky-500/45 shadow-sm"
    >
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-2">
        <div className="min-w-0">
          <div className="num text-[10px] uppercase font-mono font-bold tracking-wider text-sky-400">
            {prediction.junctionName} · {prediction.window}
          </div>
          <div className="mt-1 text-[13px] font-bold text-foreground leading-snug">
            {prediction.title}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <div className="label-xs text-muted-foreground">Confidence</div>
          <div className="num text-sm font-mono font-bold text-sky-400">
            {prediction.confidence}%
          </div>
        </div>
      </div>
      <p className="mt-1.5 text-[11px] leading-relaxed text-muted-foreground">
        {prediction.detail}
      </p>
      <div className="mt-2.5 h-10 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={prediction.series} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`pr-${prediction.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke="#38bdf8"
              strokeWidth={1.5}
              fill={`url(#pr-${prediction.id})`}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </button>
  );
}
