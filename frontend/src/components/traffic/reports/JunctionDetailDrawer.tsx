import React from "react";
import { X, ExternalLink, Download, Clock, ShieldAlert, Route } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import type { JunctionDetailData } from "@/hooks/useReportsData";
import { apiUrl } from "../../../config";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  data: JunctionDetailData | null;
}

export const JunctionDetailDrawer: React.FC<DrawerProps> = ({ open, onClose, data }) => {
  if (!open || !data) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="h-full w-full max-w-[540px] overflow-y-auto border-l border-[#1C1C20] bg-[#0E0E10] p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-[#1C1C20] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[14px] font-bold text-[#FFFFFF]">
                {data.id} · {data.name}
              </span>
              <span className="rounded border border-[#FFFFFF]/30 px-1.5 py-0.5 font-mono text-[9px] font-bold text-[#FFFFFF]">
                {data.mode}
              </span>
              {data.on_brts && (
                <span className="rounded bg-[#FFFFFF] px-1.5 py-0.5 font-mono text-[9px] font-bold text-[#0A0A0B]">
                  +BRTS
                </span>
              )}
            </div>
            <div className="mt-1 flex items-center gap-2 font-mono text-[11px] text-[#A1A1A8]">
              <span>{data.zone}</span>
              <span>·</span>
              <span className="flex items-center gap-1 text-[#5CB85C]">
                <span className="h-1.5 w-1.5 rounded-full bg-[#5CB85C]" />
                live ({data.last_update})
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#1C1C20] text-[#A1A1A8] hover:border-[#FFFFFF] hover:text-[#FFFFFF]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Quick Summary Ribbon */}
        <div className="mt-5 grid grid-cols-5 gap-2 rounded-xl border border-[#1C1C20] bg-[#141416] p-3 text-center">
          <div>
            <div className="font-mono text-[9px] text-[#6B6B73]">DELAY</div>
            <div className="font-mono text-[13px] font-bold text-[#FFFFFF]">
              {data.summary.delay_s}s
            </div>
            <div className="font-mono text-[9px] text-[#5CB85C]">▼ 21%</div>
          </div>
          <div>
            <div className="font-mono text-[9px] text-[#6B6B73]">P95 QUEUE</div>
            <div className="font-mono text-[13px] font-bold text-[#FFFFFF]">
              {data.summary.p95_queue_m}m
            </div>
          </div>
          <div>
            <div className="font-mono text-[9px] text-[#6B6B73]">v/c RATIO</div>
            <div className="font-mono text-[13px] font-bold text-[#E8A838]">
              {data.summary.saturation_vc}
            </div>
          </div>
          <div>
            <div className="font-mono text-[9px] text-[#6B6B73]">CYCLE FAIL</div>
            <div className="font-mono text-[13px] font-bold text-[#FFFFFF]">
              {data.summary.cycle_failure_pct}%
            </div>
          </div>
          <div>
            <div className="font-mono text-[9px] text-[#6B6B73]">LOS</div>
            <div className="font-mono text-[13px] font-bold text-[#FFFFFF]">
              {data.summary.los}
            </div>
          </div>
        </div>

        {/* Per-Approach Table */}
        <div className="mt-6">
          <div className="font-mono text-[11px] font-semibold uppercase tracking-wider text-[#6B6B73]">
            PER-APPROACH PERFORMANCE
          </div>
          <div className="mt-2 overflow-x-auto">
            <table className="w-full text-left font-mono text-[11px]">
              <thead>
                <tr className="border-b border-[#1C1C20] text-[#6B6B73]">
                  <th className="pb-2">Approach</th>
                  <th className="pb-2">Flow (PCU/h)</th>
                  <th className="pb-2">Queue (m)</th>
                  <th className="pb-2">Speed</th>
                  <th className="pb-2">Green Split</th>
                  <th className="pb-2 text-right">Delay</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1C1C20]/40 text-[#FFFFFF]">
                {data.approaches.map((app) => (
                  <tr key={app.approach} className="hover:bg-[#1A1A1D]">
                    <td className="py-2.5 font-semibold">{app.approach}</td>
                    <td className="py-2.5 text-[#A1A1A8]">{app.flow_pcu}</td>
                    <td className="py-2.5">{app.queue_m}m</td>
                    <td className="py-2.5 text-[#A1A1A8]">{app.avg_speed} km/h</td>
                    <td className="py-2.5">{app.green_split}</td>
                    <td className="py-2.5 text-right font-bold">{app.delay_s}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 24h Index Curve */}
        <div className="mt-6">
          <div className="flex items-center justify-between font-mono text-[11px] font-semibold uppercase tracking-wider text-[#6B6B73]">
            <span>24H CONGESTION PROFILE</span>
            <span className="text-[10px] text-[#A1A1A8]">Today vs 4-wk Typical</span>
          </div>
          <div className="mt-3 h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.index_curve_24h} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                <XAxis dataKey="hour" tick={{ fontSize: 9, fill: "#6B6B73" }} interval={3} />
                <YAxis tick={{ fontSize: 9, fill: "#6B6B73" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0A0A0B",
                    border: "1px solid #1C1C20",
                    borderRadius: "8px",
                    fontSize: "11px",
                  }}
                />
                <Line type="monotone" dataKey="typical" stroke="#5A5A60" strokeDasharray="3 3" dot={false} />
                <Line type="monotone" dataKey="today" stroke="#FFFFFF" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Events Log */}
        <div className="mt-6 border-t border-[#1C1C20] pt-4">
          <div className="font-mono text-[11px] font-semibold uppercase tracking-wider text-[#6B6B73]">
            RECENT EVENTS (LAST 24H)
          </div>
          <div className="mt-3 space-y-2">
            {data.events.map((ev, i) => (
              <div
                key={i}
                className="flex items-start gap-3 rounded-lg border border-[#1C1C20] bg-[#141416] p-2.5 text-[11px]"
              >
                <span className="font-mono text-[#6B6B73] shrink-0">{ev.time}</span>
                <div>
                  <span className="rounded bg-[#FFFFFF]/10 px-1 py-0.2 font-mono text-[9px] font-bold text-[#E8A838] mr-1.5">
                    {ev.type}
                  </span>
                  <span className="text-[#A1A1A8]">{ev.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="mt-8 flex gap-3 border-t border-[#1C1C20] pt-4">
          <button
            onClick={() => {
              window.location.href = "/command";
            }}
            className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-[#FFFFFF]/20 bg-[#FFFFFF] py-2 font-mono text-[11px] font-bold text-[#0A0A0B] hover:bg-[#FFFFFF]/90"
          >
            <Route className="h-3.5 w-3.5" />
            <span>Open in Command Map</span>
          </button>
          <button
            onClick={() => {
              window.open(apiUrl(`/api/reports/download/pdf?period=last_7_days`), "_blank");
            }}
            className="flex items-center justify-center gap-2 rounded-xl border border-[#1C1C20] bg-[#1A1A1D] px-4 py-2 font-mono text-[11px] font-bold text-[#FFFFFF] hover:border-[#6B6B73]"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Export Report</span>
          </button>
        </div>
      </div>
    </div>
  );
};
