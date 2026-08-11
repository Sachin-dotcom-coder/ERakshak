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
              className={`border px-2 py-1 text-[11px] font-medium transition-colors ${
                filter === t.id
                  ? "border-primary/50 bg-primary/15 text-primary"
                  : "border-border bg-panel-raised text-muted-foreground hover:text-foreground"
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
          <div className="max-h-72 space-y-1.5 overflow-y-auto pr-1">
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
            <div className="label-xs mb-2 flex items-center gap-1.5">
              <Brain className="h-3.5 w-3.5 text-predict" /> Predictive recommendations
              <span className="num border border-predict/40 bg-predict/10 px-1 text-[9px] text-predict">
                MODEL v2.4
              </span>
            </div>
            <div className="max-h-72 space-y-2 overflow-y-auto pr-1">
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
      className={`grid w-full grid-cols-[auto_minmax(0,1fr)_auto] items-start gap-2 border border-border border-l-2 ${tone.b} ${tone.bg} px-2 py-1.5 text-left transition-colors hover:bg-panel-raised`}
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
      className="w-full border border-predict/40 bg-predict/[0.08] p-2.5 text-left transition-colors hover:bg-predict/[0.14]"
    >
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-2">
        <div className="min-w-0">
          <div className="num text-[10px] uppercase tracking-wider text-predict">
            {prediction.junctionName} · {prediction.window}
          </div>
          <div className="mt-0.5 text-[12px] font-semibold leading-snug">
            {prediction.title}
          </div>
        </div>
        <div className="shrink-0 text-right">
          <div className="label-xs">Confidence</div>
          <div className="num text-sm font-semibold text-predict">
            {prediction.confidence}%
          </div>
        </div>
      </div>
      <p className="mt-1.5 text-[11px] leading-relaxed text-muted-foreground">
        {prediction.detail}
      </p>
      <div className="mt-2 h-10 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={prediction.series} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`pr-${prediction.id}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--predict)" stopOpacity={0.55} />
                <stop offset="100%" stopColor="var(--predict)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke="var(--predict)"
              strokeWidth={1.3}
              fill={`url(#pr-${prediction.id})`}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </button>
  );
}
