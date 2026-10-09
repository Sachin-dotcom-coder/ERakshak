import React from "react";
import type { HeatmapRowData, BottleneckRow } from "@/hooks/useReportsData";

interface HeatmapRowProps {
  heatmapRows: HeatmapRowData[];
  bottlenecks: BottleneckRow[];
  heatmapMetric: "index" | "delay" | "queue" | "deviation";
  setHeatmapMetric: (m: "index" | "delay" | "queue" | "deviation") => void;
  onSelectJunction: (id: string) => void;
}

export const ReportsHeatmapRow: React.FC<HeatmapRowProps> = ({
  heatmapRows,
  bottlenecks,
  heatmapMetric,
  setHeatmapMetric,
  onSelectJunction,
}) => {
  const getCellColor = (val: number) => {
    if (val >= 75) return "#D9534F";
    if (val >= 55) return "#E8A838";
    if (val >= 35) return "#5A5A60";
    return "#1E1E22";
  };

  const currentHour = 18;

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {/* 1. CONGESTION HEATMAP (2/3 width) */}
      <div className="flex flex-col justify-between rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 lg:col-span-2 transition-all hover:border-[#6B6B73]/40">
        <div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
                CONGESTION HEATMAP
              </span>
              <h3 className="mt-0.5 text-[15px] font-semibold text-[#FFFFFF]">
                All 22 Junctions × 24h Profile
              </h3>
            </div>

            {/* Metric Toggle Pill */}
            <div className="flex items-center rounded-full border border-[#1C1C20] bg-[#1A1A1D] p-0.5">
              {(["index", "delay", "queue", "deviation"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setHeatmapMetric(m)}
                  className={`rounded-full px-2.5 py-0.5 font-mono text-[9px] font-semibold capitalize transition-all ${
                    heatmapMetric === m
                      ? "bg-[#FFFFFF] text-[#0A0A0B] shadow-sm"
                      : "text-[#A1A1A8] hover:text-[#FFFFFF]"
                  }`}
                >
                  {m === "deviation" ? "Deviation" : m}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="mt-4 overflow-x-auto pb-1">
          <div className="min-w-[700px]">
            {/* Header row with hours */}
            <div className="mb-1.5 flex items-center pl-[160px]">
              {Array.from({ length: 24 }).map((_, h) => (
                <div
                  key={h}
                  className={`flex-1 text-center font-mono text-[9px] ${
                    h === currentHour ? "font-bold text-[#FFFFFF]" : "text-[#6B6B73]"
                  }`}
                >
                  {h === currentHour ? (
                    <span className="rounded bg-[#FFFFFF] px-1 py-0.2 text-[8px] text-[#0A0A0B]">NOW</span>
                  ) : (
                    `${h.toString().padStart(2, "0")}`
                  )}
                </div>
              ))}
            </div>

            {/* Junction rows */}
            <div className="space-y-1 max-h-[380px] overflow-y-auto pr-1">
              {heatmapRows.map((row) => (
                <div
                  key={row.id}
                  onClick={() => onSelectJunction(row.id)}
                  className="group flex cursor-pointer items-center rounded p-0.5 transition-colors hover:bg-[#1A1A1D]/60"
                >
                  {/* Junction Name */}
                  <div className="flex w-[160px] shrink-0 items-center justify-between pr-2">
                    <div className="truncate">
                      <span className="truncate text-[11px] font-medium text-[#FFFFFF] group-hover:text-[#E8A838]">
                        {row.name}
                      </span>
                    </div>
                    <span className="font-mono text-[9px] text-[#6B6B73]">{row.id}</span>
                  </div>

                  {/* 24 Hour Cells */}
                  <div className="flex flex-1 items-center gap-0.5">
                    {row.hours.map((val, h) => {
                      const isNow = h === currentHour;
                      const cellBg = getCellColor(val);
                      return (
                        <div
                          key={h}
                          title={`${row.name} @ ${h.toString().padStart(2, "0")}:00 IST — ${val}`}
                          className={`h-3.5 flex-1 rounded-[1px] transition-all hover:scale-110 ${
                            isNow ? "ring-1 ring-white" : ""
                          }`}
                          style={{
                            backgroundColor: cellBg,
                            opacity: val === 0 ? 0.3 : 1,
                          }}
                        />
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-3 flex items-center justify-between border-t border-[#1C1C20] pt-2 text-[10px] font-mono text-[#A1A1A8]">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#1E1E22] border border-[#1C1C20]" />
              0–35
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#5A5A60]" />
              35–55
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#E8A838]" />
              55–75
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#D9534F]" />
              75+
            </span>
          </div>
          <span className="text-[9px] text-[#6B6B73]">Click to view details</span>
        </div>
      </div>

      {/* 2. TOP BOTTLENECKS · TODAY (1/3 width) - Clean & Compact */}
      <div className="flex flex-col justify-between rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
        <div>
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
            PERSISTENT BOTTLENECKS
          </span>
          <h3 className="mt-0.5 text-[15px] font-semibold text-[#FFFFFF]">
            Longest Gridlock Today
          </h3>
        </div>

        {/* Top 3 Bottlenecks */}
        <div className="mt-3 space-y-2.5">
          {bottlenecks.slice(0, 3).map((b) => (
            <div
              key={b.id}
              onClick={() => onSelectJunction(b.id)}
              className="group cursor-pointer rounded-xl border border-[#1C1C20] bg-[#141416] p-3 transition-all hover:border-[#6B6B73] hover:bg-[#1A1A1D]"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[12px] font-bold text-[#E8A838]">
                    {b.rank}
                  </span>
                  <div>
                    <h4 className="text-[12px] font-semibold text-[#FFFFFF] group-hover:text-[#E8A838]">
                      {b.name}
                    </h4>
                    <span className="font-mono text-[9px] text-[#6B6B73]">
                      {b.id} · {b.zone}
                    </span>
                  </div>
                </div>

                {b.flags.length > 0 && (
                  <span className="rounded border border-[#D9534F]/30 bg-[#D9534F]/10 px-1.5 py-0.2 font-mono text-[8px] font-bold text-[#D9534F]">
                    {b.flags[0]}
                  </span>
                )}
              </div>

              <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-[#A1A1A8]">
                <span className="text-[#D9534F] font-semibold">{b.minutes_above_75} min in gridlock</span>
                <span className="text-[#6B6B73]">peak @ {b.peak_time}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Footer info */}
        <div className="mt-3 border-t border-[#1C1C20] pt-2 text-[9px] font-mono text-[#6B6B73]">
          Sorted by total minutes in High/Critical threshold.
        </div>
      </div>
    </div>
  );
};
