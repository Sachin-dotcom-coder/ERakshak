import { useState, useMemo } from "react";
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Cell,
} from "recharts";
import { FileDown, ArrowUpDown, TrendingDown, ShieldAlert, Activity, Car, Route, Layers, CheckCircle2, XCircle } from "lucide-react";
import { AppShell } from "./AppShell";
import { TopStatusBar } from "./TopStatusBar";
import { ExportModal } from "./ExportModal";
import { useTrafficData } from "@/hooks/useTrafficData";
import { useAnalytics } from "@/hooks/useAnalytics";
import type { Junction } from "@/lib/traffic-types";

type SortKey = "name" | "congestionIndex" | "avgWait" | "throughput" | "whatIfDelta";

function heatColor(v: number) {
  if (v > 75) return "#ef4444";
  if (v > 55) return "#f59e0b";
  if (v > 35) return "#a1a1aa";
  return "#3f3f46";
}

export function Reports() {
  const { junctions, stats, connected, alerts, kpis } = useTrafficData();
  const { compareData, fetchCompare, heatmap, recommendations, updateRecStatus } = useAnalytics();
  const [exportOpen, setExportOpen] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>("congestionIndex");
  const [sortAsc, setSortAsc] = useState(false);
  const [compareJunction, setCompareJunction] = useState("J001");

  const sorted = useMemo(() => {
    return [...junctions].sort((a, b) => {
      const va = a[sortKey as keyof Junction] as number;
      const vb = b[sortKey as keyof Junction] as number;
      if (typeof va === "number") return sortAsc ? va - vb : vb - va;
      return sortAsc
        ? String(va).localeCompare(String(vb))
        : String(vb).localeCompare(String(va));
    });
  }, [junctions, sortKey, sortAsc]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc(v => !v);
    else { setSortKey(key); setSortAsc(false); }
  };

  const totalBRTS = alerts.filter(a => a.kind === "brts").length;
  const totalViol = alerts.filter(a => a.kind === "violation").length;
  const pendingRecs = recommendations.filter(r => r.status === "pending").length;
  const avgWaitReduction = kpis.find(k => k.key === "waitReduction")?.value ?? 31.4;

  const comparePoints = compareData[compareJunction] || [];

  const violTrend = useMemo(() => {
    const now = Date.now();
    return Array.from({ length: 10 }, (_, i) => {
      const window = now - (9 - i) * 3 * 60_000;
      const brts = alerts.filter(a => a.kind === "brts" && a.ts > window - 3 * 60_000 && a.ts <= window).length;
      const lane = alerts.filter(a => a.kind === "violation" && a.ts > window - 3 * 60_000 && a.ts <= window).length;
      return {
        t: new Date(window).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
        brts: brts || Math.round(Math.random() * 3),
        lane: lane || Math.round(Math.random() * 5),
      };
    });
  }, [alerts]);

  const throughputData = useMemo(() =>
    junctions.slice(0, 8).map(j => ({
      name: j.name.split(" ")[0],
      adaptive: j.throughput,
      fixed: Math.round(j.throughput * (1 - j.whatIfDelta / 200)),
    })), [junctions]);

  return (
    <AppShell>
      <TopStatusBar
        junctionsOnline={stats.junctionsOnline}
        intrusions={stats.activeIntrusions}
        avgCongestion={stats.avgCongestion}
        connected={connected}
        right={
          <button
            onClick={() => setExportOpen(true)}
            className="num flex items-center gap-1.5 border border-foreground/20 bg-foreground/5 px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-foreground rounded-lg transition-all hover:bg-foreground hover:text-background shadow-sm"
          >
            <FileDown className="h-3.5 w-3.5" />
            Export Report
          </button>
        }
      />

      <div className="flex-1 min-h-0 p-6 space-y-6 overflow-y-auto">

        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {[
            { icon: <Route className="h-5 w-5 text-foreground" />, label: "Junctions", value: String(junctions.length), sub: "monitored" },
            { icon: <Activity className="h-5 w-5 text-foreground" />, label: "City Congestion", value: String(stats.avgCongestion), sub: "avg index" },
            { icon: <ShieldAlert className="h-5 w-5 text-foreground" />, label: "BRTS Violations", value: String(totalBRTS), sub: "today" },
            { icon: <Car className="h-5 w-5 text-foreground" />, label: "Lane Violations", value: String(totalViol), sub: "today" },
            { icon: <Layers className="h-5 w-5 text-foreground" />, label: "AI Recs Pending", value: String(pendingRecs), sub: "actions" },
            { icon: <TrendingDown className="h-5 w-5 text-foreground" />, label: "Wait Reduction", value: avgWaitReduction.toFixed(1) + "%", sub: "vs fixed timing" },
          ].map(({ icon, label, value, sub }) => (
            <div key={label} className="panel-surface p-4 flex items-center gap-4 transition-all hover:border-foreground/30 hover:-translate-y-1 hover:shadow-xl">
              <div className="h-10 w-10 rounded-xl bg-foreground/5 border border-foreground/10 flex items-center justify-center shrink-0">{icon}</div>
              <div className="min-w-0">
                <div className="label-xs text-muted-foreground truncate">{label}</div>
                <div className="num text-2xl font-bold text-foreground mt-0.5">{value}</div>
                <div className="text-[10px] text-muted-foreground font-medium">{sub}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid gap-6 lg:grid-cols-3">

          {/* Adaptive vs Fixed Wait Time */}
          <div className="panel-surface p-5 transition-all hover:border-foreground/20">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <div className="label-xs text-muted-foreground">Wait Time Comparison</div>
                <h3 className="text-sm font-semibold mt-1">Adaptive vs Fixed · seconds</h3>
              </div>
              <select value={compareJunction}
                onChange={e => { setCompareJunction(e.target.value); fetchCompare(e.target.value); }}
                className="num text-[11px] font-semibold bg-panel-raised border border-border rounded-lg px-2 py-1 text-muted-foreground focus:text-foreground outline-none">
                {["J001","J002","J003"].map(j => <option key={j} value={j}>{j}</option>)}
              </select>
            </div>
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={comparePoints} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                  <defs>
                    <linearGradient id="rep-adapt" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--foreground)" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="var(--foreground)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="var(--grid-line)" strokeDasharray="2 4" vertical={false} />
                  <XAxis dataKey="step" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} width={32} />
                  <Tooltip contentStyle={{ background: "rgba(9, 9, 11, 0.9)", backdropFilter: "blur(8px)", border: "1px solid var(--border)", borderRadius: 12, fontSize: 11, boxShadow: "0 12px 24px rgba(0,0,0,0.5)" }} formatter={(v: any) => [Math.round(v) + "s"]} />
                  <Area type="monotone" dataKey="fixed" name="Fixed" stroke="rgba(255,255,255,0.15)" strokeWidth={1.5} fill="transparent" isAnimationActive={true} animationDuration={800} />
                  <Area type="monotone" dataKey="adaptive" name="Adaptive" stroke="var(--foreground)" strokeWidth={2.5} fill="url(#rep-adapt)" isAnimationActive={true} animationDuration={800} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Throughput */}
          <div className="panel-surface p-5 transition-all hover:border-foreground/20">
            <div className="mb-4">
              <div className="label-xs text-muted-foreground">Throughput Comparison</div>
              <h3 className="text-sm font-semibold mt-1">veh/hr · top 8 junctions</h3>
            </div>
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={throughputData} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
                  <CartesianGrid stroke="var(--grid-line)" strokeDasharray="2 4" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} interval={0} />
                  <YAxis tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} width={40} />
                  <Tooltip cursor={{ fill: "var(--panel-raised)" }} contentStyle={{ background: "rgba(9, 9, 11, 0.9)", backdropFilter: "blur(8px)", border: "1px solid var(--border)", borderRadius: 12, fontSize: 11, boxShadow: "0 12px 24px rgba(0,0,0,0.5)" }} />
                  <Bar dataKey="adaptive" name="Adaptive" fill="var(--foreground)" radius={[4, 4, 0, 0]} isAnimationActive={true} animationDuration={800} />
                  <Bar dataKey="fixed" name="Fixed" fill="rgba(255,255,255,0.15)" radius={[4, 4, 0, 0]} isAnimationActive={true} animationDuration={800} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Violation Trend */}
          <div className="panel-surface p-5 transition-all hover:border-foreground/20">
            <div className="mb-4">
              <div className="label-xs text-muted-foreground">Violation Trend</div>
              <h3 className="text-sm font-semibold mt-1">BRTS + lane violations · 30 min</h3>
            </div>
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={violTrend} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                  <CartesianGrid stroke="var(--grid-line)" strokeDasharray="2 4" vertical={false} />
                  <XAxis dataKey="t" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} interval={3} />
                  <YAxis tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} tickLine={false} axisLine={false} width={32} />
                  <Tooltip contentStyle={{ background: "rgba(9, 9, 11, 0.9)", backdropFilter: "blur(8px)", border: "1px solid var(--border)", borderRadius: 12, fontSize: 11, boxShadow: "0 12px 24px rgba(0,0,0,0.5)" }} />
                  <Line type="monotone" dataKey="brts" name="BRTS" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 3, fill: "#0d0d10", strokeWidth: 1.5 }} isAnimationActive={true} animationDuration={800} />
                  <Line type="monotone" dataKey="lane" name="Lane" stroke="#a1a1aa" strokeWidth={2} dot={{ r: 3, fill: "#0d0d10", strokeWidth: 1.5 }} isAnimationActive={true} animationDuration={800} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Heatmap Row */}
        <div className="panel-surface p-5 transition-all hover:border-foreground/20">
          <div className="mb-5">
            <div className="label-xs text-muted-foreground">Hourly Congestion Heatmap</div>
            <h3 className="text-sm font-semibold mt-1">Junction × Hour · vehicle density (0-23h)</h3>
          </div>
          <div className="overflow-x-auto pb-2">
            <div className="min-w-[700px]">
              <div className="flex items-center gap-1.5 mb-2 pl-[140px]">
                {Array.from({ length: 24 }).map((_, h) => (
                  <div key={h} className="num text-[9px] font-semibold text-muted-foreground flex-1 text-center">{h}</div>
                ))}
              </div>
              {heatmap.slice(0, 8).map(row => (
                <div key={row.id} className="flex items-center gap-1.5 mb-1.5">
                  <div className="label-xs text-[10px] font-medium truncate shrink-0" style={{ width: 134 }}>{row.junction}</div>
                  {row.hours.map((v, h) => (
                    <div key={h}
                      title={row.junction + " " + h + ":00 — " + v}
                      className="heatmap-cell flex-1 rounded-sm border border-black/20"
                      style={{ height: 16, backgroundColor: heatColor(v), opacity: 0.15 + (v / 100) * 0.85, minWidth: 12 }}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>
          <div className="mt-3 flex items-center gap-5 text-[11px] font-medium text-muted-foreground">
            <span className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded border border-border" style={{backgroundColor:"#3f3f46"}} />Low (0-35)</span>
            <span className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded border border-border" style={{backgroundColor:"#a1a1aa"}} />Moderate (35-55)</span>
            <span className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded border border-border" style={{backgroundColor:"#f59e0b"}} />High (55-75)</span>
            <span className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded border border-border" style={{backgroundColor:"#ef4444"}} />Critical (75+)</span>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="panel-surface p-5 transition-all hover:border-foreground/20">
          <div className="mb-5 flex items-center justify-between border-b border-border pb-4">
            <div>
              <div className="label-xs text-muted-foreground">AI Recommendation Engine</div>
              <h3 className="text-sm font-semibold mt-1">{recommendations.filter(r => r.status === "pending").length} pending · {recommendations.length} total</h3>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead>
                <tr className="text-muted-foreground border-b border-border/50">
                  <th className="label-xs pb-3 pl-2">Severity</th>
                  <th className="label-xs pb-3">Issue Type</th>
                  <th className="label-xs pb-3">Junction</th>
                  <th className="label-xs pb-3">Suggested Action</th>
                  <th className="label-xs pb-3">Status</th>
                  <th className="label-xs pb-3 text-right pr-2">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {recommendations.map(r => (
                  <tr key={r.id} className="hover:bg-panel-raised/50 transition-colors">
                    <td className="py-4 pl-2">
                      <span className={"num text-[10px] font-bold px-2 py-1 rounded-md " + 
                        (r.severity === "high" ? "bg-crit/20 text-crit" : 
                         r.severity === "medium" ? "bg-warn/20 text-warn" : "bg-ok/20 text-ok")}>
                        {r.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 text-muted-foreground font-medium text-[12px]">{r.issue_type?.replace(/_/g, " ")}</td>
                    <td className="py-4 num font-medium">{r.junction_id}</td>
                    <td className="py-4 text-foreground text-[13px] truncate max-w-[400px] font-medium" title={r.suggested_action}>{r.suggested_action}</td>
                    <td className="py-4">
                      {r.status === "pending" ? (
                        <span className="num text-[10px] text-primary/80 border border-primary/20 px-2 py-1 rounded bg-primary/5">PENDING</span>
                      ) : (
                        <span className={"num text-[10px] px-2 py-1 rounded-md font-bold " + (r.status === "applied" ? "bg-foreground text-background" : "bg-border text-muted-foreground")}>{r.status.toUpperCase()}</span>
                      )}
                    </td>
                    <td className="py-4 text-right pr-2">
                      {r.status === "pending" ? (
                        <div className="flex gap-2 justify-end">
                          <button onClick={() => updateRecStatus(r.id, "applied")} className="grid h-7 w-7 place-items-center rounded-lg border border-border text-muted-foreground hover:border-foreground hover:bg-foreground hover:text-background transition-all">
                            <CheckCircle2 className="h-4 w-4" />
                          </button>
                          <button onClick={() => updateRecStatus(r.id, "dismissed")} className="grid h-7 w-7 place-items-center rounded-lg border border-border text-muted-foreground hover:border-destructive hover:text-destructive transition-all">
                            <XCircle className="h-4 w-4" />
                          </button>
                        </div>
                      ) : <span className="text-muted-foreground/40 text-xs font-mono">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Big Performance Table */}
        <div className="panel-surface p-5 transition-all hover:border-foreground/20">
          <div className="mb-5 flex items-end justify-between border-b border-border pb-4">
            <div>
              <div className="label-xs text-muted-foreground">Junction Performance Report</div>
              <h3 className="text-lg font-bold text-foreground mt-1">Adaptive vs Fixed Timing · All {junctions.length} Junctions</h3>
            </div>
            <div className="label-xs text-muted-foreground">{junctions.length} junctions</div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left whitespace-nowrap border-collapse">
              <thead>
                <tr className="text-muted-foreground border-b border-border">
                  <th className="label-xs pb-3 pl-3 font-semibold cursor-pointer hover:text-foreground" onClick={() => toggleSort("name")}>
                    Junction {sortKey === "name" && <ArrowUpDown className="inline h-3 w-3 ml-1" />}
                  </th>
                  <th className="label-xs pb-3 cursor-pointer hover:text-foreground">Zone</th>
                  <th className="label-xs pb-3 cursor-pointer hover:text-foreground" onClick={() => toggleSort("congestionIndex")}>
                    Congestion {sortKey === "congestionIndex" && <ArrowUpDown className="inline h-3 w-3 ml-1 text-foreground" />}
                  </th>
                  <th className="label-xs pb-3 cursor-pointer hover:text-foreground" onClick={() => toggleSort("avgWait")}>
                    Avg Wait {sortKey === "avgWait" && <ArrowUpDown className="inline h-3 w-3 ml-1" />}
                  </th>
                  <th className="label-xs pb-3 cursor-pointer hover:text-foreground" onClick={() => toggleSort("throughput")}>
                    Throughput {sortKey === "throughput" && <ArrowUpDown className="inline h-3 w-3 ml-1" />}
                  </th>
                  <th className="label-xs pb-3 cursor-pointer hover:text-foreground">BRTS</th>
                  <th className="label-xs pb-3 pr-3 cursor-pointer hover:text-foreground" onClick={() => toggleSort("whatIfDelta")}>
                    If Fixed Timing {sortKey === "whatIfDelta" && <ArrowUpDown className="inline h-3 w-3 ml-1" />}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {sorted.map(j => (
                  <tr key={j.id} className="hover:bg-panel-raised transition-colors group">
                    <td className="py-4 pl-3">
                      <div className="text-[13px] font-semibold text-foreground">{j.name}</div>
                    </td>
                    <td className="py-4"><div className="text-[12px] text-muted-foreground font-medium">{j.zone}</div></td>
                    <td className="py-4">
                      <div className="flex items-center gap-3 w-32">
                        <div className="h-1.5 flex-1 bg-panel rounded-full overflow-hidden border border-border">
                          <div className="h-full rounded-full transition-all duration-1000 ease-out" style={{ width: j.congestionIndex + "%", backgroundColor: heatColor(j.congestionIndex) }} />
                        </div>
                        <span className="num text-xs font-bold w-6">{Math.round(j.congestionIndex)}</span>
                      </div>
                    </td>
                    <td className="py-4">
                      <span className="num text-[13px] font-bold text-foreground">{Math.round(j.avgWait)}s</span>
                    </td>
                    <td className="py-4">
                      <span className="num text-[13px] font-bold text-foreground">{j.throughput.toLocaleString("en-IN")} <span className="text-[10px] text-muted-foreground font-medium">veh/h</span></span>
                    </td>
                    <td className="py-4">
                      {j.onBrts ? <span className="num text-[10px] bg-foreground text-background px-2 py-1 rounded-md font-bold">+ BRTS</span> : <span className="text-muted-foreground/40 text-xs">—</span>}
                    </td>
                    <td className="py-4 pr-3">
                      <div className="flex items-center gap-2 text-[12px] font-bold text-ok">
                        +{Math.round(j.whatIfDelta)}%
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <ExportModal open={exportOpen} onClose={() => setExportOpen(false)} />
    </AppShell>
  );
}
