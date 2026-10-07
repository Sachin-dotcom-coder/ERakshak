import { useMemo, useState } from "react";
import { Filter, BarChart3, Terminal, Activity, ShieldAlert, Car } from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { fmtTime } from "@/lib/mock-traffic";
import type { DetectionEvent } from "@/lib/traffic-types";

const EVENT_TONE: Record<DetectionEvent["event"], string> = {
  vehicle_entry: "text-ok",
  vehicle_exit: "text-muted-foreground",
  lane_violation: "text-warn",
  brts_intrusion: "text-crit font-bold",
};

const PIE_COLORS: Record<string, string> = {
  vehicle_entry: "var(--ok)",
  vehicle_exit: "#00f3ff",
  lane_violation: "var(--warn)",
  brts_intrusion: "var(--crit)",
};

export function DetectionLog({
  events,
  cameras,
}: {
  events: DetectionEvent[];
  cameras: { id: string; junctionName: string }[];
}) {
  const [camera, setCamera] = useState("all");
  const [type, setType] = useState("all");
  const [viewMode, setViewMode] = useState<"visual" | "stdout">("visual");

  const rows = useMemo(
    () =>
      events.filter(
        (e) =>
          (camera === "all" || e.cameraId === camera) &&
          (type === "all" || e.event === type),
      ),
    [events, camera, type],
  );

  // Compute Traffic Flow Visualizer Data
  const flowTimeSeries = useMemo(() => {
    // Group events into 5-minute time buckets
    const map: Record<string, { time: string; cars: number; autos: number; buses: number; trucks: number; twoWheelers: number }> = {};
    rows.forEach((e) => {
      const timeStr = fmtTime(e.ts);
      if (!map[timeStr]) {
        map[timeStr] = { time: timeStr, cars: 0, autos: 0, buses: 0, trucks: 0, twoWheelers: 0 };
      }
      const cls = (e.objectClass || "").toLowerCase();
      if (cls === "car" || cls === "suv") map[timeStr].cars++;
      else if (cls === "auto") map[timeStr].autos++;
      else if (cls === "bus" || cls === "citybus") map[timeStr].buses++;
      else if (cls === "truck") map[timeStr].trucks++;
      else map[timeStr].twoWheelers++;
    });
    return Object.values(map).slice(-15);
  }, [rows]);

  const eventDistribution = useMemo(() => {
    const counts: Record<string, number> = {
      vehicle_entry: 0,
      vehicle_exit: 0,
      lane_violation: 0,
      brts_intrusion: 0,
    };
    rows.forEach((e) => {
      if (e.event in counts) counts[e.event] = (counts[e.event] ?? 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [rows]);

  const totalIntrusions = rows.filter((r) => r.event === "brts_intrusion").length;
  const totalViolations = rows.filter((r) => r.event === "lane_violation").length;

  return (
    <aside className="panel-surface flex min-h-0 flex-col">
      <div className="border-b border-border px-3 py-2">
        <div className="flex items-center justify-between gap-2">
          <div>
            <div className="label-xs flex items-center gap-1.5">
              <Activity className="h-3 w-3 text-primary animate-pulse" /> Vision Telemetry Engine
            </div>
            <h2 className="text-sm font-semibold">Traffic Flow & Event Analytics</h2>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center border border-border p-0.5 bg-panel-raised">
            <button
              onClick={() => setViewMode("visual")}
              className={`flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium transition-colors ${
                viewMode === "visual"
                  ? "bg-primary text-background font-bold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <BarChart3 className="h-3 w-3" /> Visual Flow
            </button>
            <button
              onClick={() => setViewMode("stdout")}
              className={`flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium transition-colors ${
                viewMode === "stdout"
                  ? "bg-primary text-background font-bold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Terminal className="h-3 w-3" /> Raw Console
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="mt-2 grid grid-cols-2 gap-1.5">
          <label className="block">
            <span className="sr-only">Filter by camera</span>
            <select
              value={camera}
              onChange={(e) => setCamera(e.target.value)}
              className="num w-full border border-border bg-panel-raised px-1.5 py-1 text-[10px] text-foreground outline-none focus:border-primary"
            >
              <option value="all">ALL CAMERAS ({cameras.length})</option>
              {cameras.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.id} · {c.junctionName}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="sr-only">Filter by event type</span>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="num w-full border border-border bg-panel-raised px-1.5 py-1 text-[10px] text-foreground outline-none focus:border-primary"
            >
              <option value="all">ALL EVENT TYPES</option>
              <option value="vehicle_entry">vehicle_entry</option>
              <option value="vehicle_exit">vehicle_exit</option>
              <option value="lane_violation">lane_violation</option>
              <option value="brts_intrusion">brts_intrusion</option>
            </select>
          </label>
        </div>
      </div>

      {viewMode === "visual" ? (
        <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-3">
          {/* Quick Metrics Header */}
          <div className="grid grid-cols-3 gap-2">
            <div className="panel-surface p-2 border border-border">
              <div className="label-xs flex items-center gap-1">
                <Car className="h-3 w-3 text-primary" /> Inflow Events
              </div>
              <div className="num text-base font-bold text-foreground">{rows.length}</div>
            </div>
            <div className="panel-surface p-2 border border-warn/40 bg-warn/5">
              <div className="label-xs text-warn">Lane Violations</div>
              <div className="num text-base font-bold text-warn">{totalViolations}</div>
            </div>
            <div className="panel-surface p-2 border border-crit/40 bg-crit/5">
              <div className="label-xs flex items-center gap-1 text-crit">
                <ShieldAlert className="h-3 w-3" /> Intrusions
              </div>
              <div className="num text-base font-bold text-crit">{totalIntrusions}</div>
            </div>
          </div>

          {/* Traffic Flow Rate Chart */}
          <div className="panel-surface p-2.5">
            <div className="label-xs mb-1.5 flex items-center justify-between">
              <span>Vehicle Class Flow Rate (Volume Over Time)</span>
              <span className="text-[9px] text-primary font-mono">LIVE FEED</span>
            </div>
            <div className="h-36 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={flowTimeSeries.length > 0 ? flowTimeSeries : [{ time: "Now", cars: 5, autos: 3, buses: 1 }]} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <CartesianGrid stroke="var(--grid-line)" strokeDasharray="2 4" vertical={false} />
                  <XAxis dataKey="time" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      fontSize: 10,
                    }}
                  />
                  <Area type="monotone" dataKey="cars" name="Cars" stackId="1" stroke="#00f3ff" fill="#00f3ff" fillOpacity={0.4} />
                  <Area type="monotone" dataKey="autos" name="Autos" stackId="1" stroke="#ffcc00" fill="#ffcc00" fillOpacity={0.4} />
                  <Area type="monotone" dataKey="twoWheelers" name="2-Wheelers" stackId="1" stroke="#a855f7" fill="#a855f7" fillOpacity={0.4} />
                  <Area type="monotone" dataKey="buses" name="Buses" stackId="1" stroke="#00ff88" fill="#00ff88" fillOpacity={0.4} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Event Category Distribution Donut */}
          <div className="panel-surface p-2.5">
            <div className="label-xs mb-1">Detection Event Proportions</div>
            <div className="flex items-center gap-3">
              <div className="h-28 w-28 shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={eventDistribution}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={22}
                      outerRadius={40}
                      strokeWidth={1}
                    >
                      {eventDistribution.map((entry) => (
                        <Cell key={entry.name} fill={PIE_COLORS[entry.name] || "#00f3ff"} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-1 text-[10px]">
                {eventDistribution.map((d) => (
                  <div key={d.name} className="flex items-center gap-1.5">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: PIE_COLORS[d.name] || "#00f3ff" }}
                    />
                    <span className="capitalize text-muted-foreground">{d.name.replace("_", " ")}:</span>
                    <span className="num font-bold text-foreground">{d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Raw Console Stream */
        <div className="num min-h-0 flex-1 space-y-px overflow-y-auto bg-[oklch(0.15_0.025_264)] p-1.5 text-[10px] leading-[16px]">
          {rows.map((e) => (
            <div
              key={e.id}
              className="grid grid-cols-[auto_auto_minmax(0,1fr)] gap-2 border-b border-border/40 px-1 py-0.5 hover:bg-panel-raised"
            >
              <span className="text-muted-foreground">{fmtTime(e.ts)}</span>
              <span className="text-primary">{e.cameraId}</span>
              <span className="truncate">
                <span className={EVENT_TONE[e.event]}>{e.event}</span>
                <span className="text-muted-foreground">
                  {" "}
                  cls={e.objectClass} conf={(e.confidence / 100).toFixed(2)}
                  {e.note ? ` ${e.note}` : ""}
                </span>
              </span>
            </div>
          ))}
          {rows.length === 0 && (
            <p className="flex items-center justify-center gap-1.5 p-4 text-center text-muted-foreground">
              <Filter className="h-3 w-3" /> no events match filter
            </p>
          )}
        </div>
      )}
    </aside>
  );
}

