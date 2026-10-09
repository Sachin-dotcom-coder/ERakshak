import React from "react";
import { Leaf, Clock, TrendingDown } from "lucide-react";
import type { AdaptiveBenefitData } from "@/hooks/useReportsData";

interface BenefitPanelProps {
  data: AdaptiveBenefitData | null;
}

export const AdaptiveBenefitPanel: React.FC<BenefitPanelProps> = ({ data }) => {
  if (!data) return null;

  return (
    <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1C1C20] pb-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
            {data.eyebrow}
          </span>
          <span className="rounded-full border border-[#5CB85C]/30 bg-[#5CB85C]/10 px-2 py-0.2 font-mono text-[9px] font-bold text-[#5CB85C]">
            ESTIMATED
          </span>
        </div>
        <div className="font-mono text-[10px] text-[#A1A1A8]">
          {data.method}
        </div>
      </div>

      {/* Main Metrics Row - Clean, crisp, no clutter */}
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {/* Metric 1 */}
        <div className="flex items-center gap-3.5 rounded-xl border border-[#1C1C20] bg-[#141416] p-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1A1A1D] border border-[#1C1C20]">
            <TrendingDown className="h-5 w-5 text-[#5CB85C]" />
          </div>
          <div>
            <div className="text-[11px] text-[#A1A1A8] font-medium">Delay vs Fixed Timing</div>
            <div className="font-mono text-[24px] font-bold text-[#FFFFFF] leading-tight">
              ▼ {data.delay_reduction_pct}%
            </div>
            <div className="font-mono text-[10px] text-[#5CB85C]">{data.confidence_interval}</div>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="flex items-center gap-3.5 rounded-xl border border-[#1C1C20] bg-[#141416] p-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1A1A1D] border border-[#1C1C20]">
            <Clock className="h-5 w-5 text-[#FFFFFF]" />
          </div>
          <div>
            <div className="text-[11px] text-[#A1A1A8] font-medium">Commuter Hours Saved</div>
            <div className="font-mono text-[24px] font-bold text-[#FFFFFF] leading-tight">
              {data.vehicle_hours_saved} h
            </div>
            <div className="font-mono text-[10px] text-[#A1A1A8]">Today across 22 junctions</div>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="flex items-center gap-3.5 rounded-xl border border-[#1C1C20] bg-[#141416] p-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1A1A1D] border border-[#1C1C20]">
            <Leaf className="h-5 w-5 text-[#5CB85C]" />
          </div>
          <div>
            <div className="text-[11px] text-[#A1A1A8] font-medium">Idling Emissions Avoided</div>
            <div className="font-mono text-[24px] font-bold text-[#FFFFFF] leading-tight">
              ≈ {data.emissions_avoided_tonnes} t CO₂
            </div>
            <div className="font-mono text-[10px] text-[#5CB85C]">Reduced queue dwell time</div>
          </div>
        </div>
      </div>

      {/* Per-Zone Benefit Breakdown - Compact Row */}
      <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-[#1C1C20] pt-3">
        <span className="font-mono text-[10px] text-[#6B6B73] mr-2">PER ZONE:</span>
        {data.zones.map((z) => (
          <div
            key={z.zone}
            className="flex items-center gap-1.5 rounded-lg border border-[#1C1C20] bg-[#141416] px-2.5 py-1 font-mono text-[10px]"
          >
            <span className="text-[#A1A1A8]">{z.zone}</span>
            <span className={z.benefit_pct !== null ? "font-bold text-[#5CB85C]" : "text-[#6B6B73]"}>
              {z.benefit_pct !== null ? `▼ ${z.benefit_pct}%` : "No Baseline"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
