import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  ReferenceLine,
  ReferenceArea,
} from "recharts";
import { ChevronDown } from "lucide-react";
import type { DelayPoint, LosBlock, ViolationHour } from "@/hooks/useReportsData";

interface ChartsRowProps {
  delaySeries: DelayPoint[];
  delayScope: string;
  setDelayScope: (s: string) => void;
  losBlocks: LosBlock[];
  violations: ViolationHour[];
  onOpenCongestion: () => void;
  onOpenEnforcement: () => void;
}

const SCOPES = [
  { id: "network", label: "Network Avg" },
  { id: "junction:J001", label: "J001 · Udhna" },
  { id: "junction:J002", label: "J002 · Sahara" },
  { id: "junction:J008", label: "J008 · Kharwarnagar" },
];

export const ReportsChartsRow: React.FC<ChartsRowProps> = ({
  delaySeries,
  delayScope,
  setDelayScope,
  losBlocks,
  violations,
  onOpenCongestion,
  onOpenEnforcement,
}) => {
  // Keep 4 key blocks for concise, uncluttered presentation
  const displayBlocks = losBlocks.length > 4 ? [
    losBlocks[0], // Night
    losBlocks[2], // AM Peak
    losBlocks[3], // Midday
    losBlocks[5], // PM Peak
  ] : losBlocks;

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {/* 1. DELAY OVER TIME */}
      <div className="flex flex-col justify-between rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
        <div>
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
              DELAY OVER TIME
            </span>
            <div className="relative">
              <select
                value={delayScope}
                onChange={(e) => setDelayScope(e.target.value)}
                className="appearance-none rounded-full border border-[#1C1C20] bg-[#1A1A1D] px-2.5 py-0.5 font-mono text-[10px] font-medium text-[#FFFFFF] outline-none hover:border-[#6B6B73]"
              >
                {SCOPES.map((s) => (
                  <option key={s.id} value={s.id} className="bg-[#0E0E10] text-[#FFFFFF]">
                    {s.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-1.5 top-1.5 h-3 w-3 text-[#A1A1A8]" />
            </div>
          </div>
          <h3 className="mt-1 text-[15px] font-semibold text-[#FFFFFF]">
            Adaptive vs Baseline · Delay (s/veh)
          </h3>
        </div>

        {/* Chart */}
        <div className="mt-3 h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={delaySeries} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
              <CartesianGrid stroke="#1C1C20" strokeDasharray="3 3" vertical={false} />
              <ReferenceArea x1="08:00" x2="10:00" fill="#1C1C20" fillOpacity={0.6} />
              <ReferenceArea x1="17:00" x2="20:00" fill="#1C1C20" fillOpacity={0.6} />
              <XAxis
                dataKey="t"
                tick={{ fontSize: 9, fill: "#6B6B73", fontFamily: "monospace" }}
                tickLine={false}
                axisLine={{ stroke: "#1C1C20" }}
                interval={4}
              />
              <YAxis
                tick={{ fontSize: 9, fill: "#6B6B73", fontFamily: "monospace" }}
                tickLine={false}
                axisLine={false}
                unit="s"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0A0A0B",
                  border: "1px solid #1C1C20",
                  borderRadius: "8px",
                  fontFamily: "monospace",
                  fontSize: "10px",
                }}
                formatter={(val: any, name: string) => [
                  `${val}s`,
                  name === "adaptive" ? "Adaptive" : "Fixed Baseline",
                ]}
              />
              <Line
                type="monotone"
                dataKey="baseline"
                stroke="#5A5A60"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="adaptive"
                stroke="#FFFFFF"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="mt-2 flex items-center justify-between border-t border-[#1C1C20] pt-2 text-[10px] font-mono text-[#A1A1A8]">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="inline-block h-1.5 w-3 rounded-sm bg-[#FFFFFF]" />
              Adaptive
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-0.5 w-3 border-b border-dashed border-[#5A5A60]" />
              Fixed Baseline
            </span>
          </div>
          <button onClick={onOpenCongestion} className="text-[#6B6B73] hover:text-[#FFFFFF]">
            More ↗
          </button>
        </div>
      </div>

      {/* 2. LEVEL OF SERVICE DISTRIBUTION */}
      <div className="flex flex-col justify-between rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
        <div>
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
            LEVEL OF SERVICE
          </span>
          <h3 className="mt-1 text-[15px] font-semibold text-[#FFFFFF]">
            Junction-Hours by Grade (A–F)
          </h3>
        </div>

        {/* Simplified 4 Stacked Bars */}
        <div className="mt-3 flex flex-col justify-center space-y-3">
          {displayBlocks.map((block) => {
            const total = block.A_C + block.D + block.E + block.F || 100;
            const wAC = (block.A_C / total) * 100;
            const wD = (block.D / total) * 100;
            const wE = (block.E / total) * 100;
            const wF = (block.F / total) * 100;

            return (
              <div key={block.block} className="space-y-1">
                <div className="flex items-center justify-between font-mono text-[10px]">
                  <span className="text-[#FFFFFF]">{block.label}</span>
                  <span className="text-[#E8A838] font-bold">{block.E + block.F}% E/F</span>
                </div>
                <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-[#1A1A1D]">
                  <div style={{ width: `${wAC}%` }} className="bg-[#5A5A60]" />
                  <div style={{ width: `${wD}%` }} className="bg-[#A1A1A8]" />
                  <div style={{ width: `${wE}%` }} className="bg-[#E8A838]" />
                  <div style={{ width: `${wF}%` }} className="bg-[#D9534F]" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-2 flex items-center justify-between border-t border-[#1C1C20] pt-2 text-[10px] font-mono text-[#A1A1A8]">
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm bg-[#5A5A60]" />
            A–C Free
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm bg-[#A1A1A8]" />
            D Sub-optimal
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm bg-[#E8A838]" />
            E Unstable
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm bg-[#D9534F]" />
            F Breakdown
          </span>
        </div>
      </div>

      {/* 3. VIOLATIONS & INCIDENTS TREND */}
      <div className="flex flex-col justify-between rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
        <div>
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
            VIOLATIONS
          </span>
          <h3 className="mt-1 text-[15px] font-semibold text-[#FFFFFF]">
            Hourly Violations by Type
          </h3>
        </div>

        {/* Stacked Bar Chart */}
        <div className="mt-3 h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={violations} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
              <CartesianGrid stroke="#1C1C20" strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="t"
                tick={{ fontSize: 9, fill: "#6B6B73", fontFamily: "monospace" }}
                tickLine={false}
                axisLine={{ stroke: "#1C1C20" }}
                interval={4}
              />
              <YAxis
                tick={{ fontSize: 9, fill: "#6B6B73", fontFamily: "monospace" }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0A0A0B",
                  border: "1px solid #1C1C20",
                  borderRadius: "8px",
                  fontFamily: "monospace",
                  fontSize: "10px",
                }}
              />
              <ReferenceLine y={15} stroke="#D9534F" strokeDasharray="3 3" />
              <Bar dataKey="brts_intrusion" stackId="a" fill="#D9534F" />
              <Bar dataKey="lane_discipline" stackId="a" fill="#E8A838" />
              <Bar dataKey="wrong_way" stackId="a" fill="#FFFFFF" />
              <Bar dataKey="other" stackId="a" fill="#5A5A60" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="mt-2 flex items-center justify-between border-t border-[#1C1C20] pt-2 text-[10px] font-mono text-[#A1A1A8]">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#D9534F]" />
              BRTS
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#E8A838]" />
              Lane
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-sm bg-[#FFFFFF]" />
              Wrong-way
            </span>
          </div>
          <button onClick={onOpenEnforcement} className="text-[#6B6B73] hover:text-[#FFFFFF]">
            Review ↗
          </button>
        </div>
      </div>
    </div>
  );
};
