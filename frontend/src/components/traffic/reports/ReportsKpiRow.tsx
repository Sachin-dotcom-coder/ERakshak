import React from "react";
import { Clock, ArrowRightLeft, AlertTriangle, Siren, Shield, Activity } from "lucide-react";
import type { KpiCardData } from "@/hooks/useReportsData";

interface KpiRowProps {
  kpis: KpiCardData[];
  onCardClick: (kpiId: string) => void;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  clock: <Clock className="h-4 w-4 text-[#FFFFFF]" />,
  "arrow-through-gate": <ArrowRightLeft className="h-4 w-4 text-[#FFFFFF]" />,
  "alert-triangle": <AlertTriangle className="h-4 w-4 text-[#FFFFFF]" />,
  siren: <Siren className="h-4 w-4 text-[#FFFFFF]" />,
  shield: <Shield className="h-4 w-4 text-[#FFFFFF]" />,
  activity: <Activity className="h-4 w-4 text-[#FFFFFF]" />,
};

// Clean, short labels that never truncate
const SHORT_LABELS: Record<string, string> = {
  network_delay: "NETWORK DELAY",
  throughput: "THROUGHPUT",
  congested_junctions: "CONGESTED",
  open_incidents: "INCIDENTS",
  violations: "VIOLATIONS",
  system_health: "SYSTEM HEALTH",
};

// Clean, uncluttered single badge text
const CLEAN_BADGES: Record<string, { text: string; tone: "good" | "bad" | "warn" | "neutral" }> = {
  network_delay: { text: "▼ 6% vs yesterday", tone: "good" },
  throughput: { text: "▲ 3% vs baseline", tone: "neutral" },
  congested_junctions: { text: "4 Critical / High", tone: "bad" },
  open_incidents: { text: "3 Active Alerts", tone: "warn" },
  violations: { text: "▲ 12% vs last Sat", tone: "bad" },
  system_health: { text: "21/22 Cameras Live", tone: "good" },
};

export const ReportsKpiRow: React.FC<KpiRowProps> = ({ kpis, onCardClick }) => {
  // Mini SVG Sparkline generator dedicated to its own container (never overlapping text)
  const renderSparkline = (data: number[], color: string) => {
    if (!data || data.length < 2) return null;
    const min = Math.min(...data);
    const max = Math.max(...data) || 1;
    const range = max - min || 1;
    const width = 64;
    const height = 24;
    const step = width / (data.length - 1);

    const points = data
      .map((val, idx) => {
        const x = idx * step;
        const y = height - ((val - min) / range) * (height - 4) - 2;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");

    return (
      <svg
        className="h-6 w-16"
        viewBox={`0 0 ${width} ${height}`}
        fill="none"
      >
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  };

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {kpis.map((kpi) => {
        const shortLabel = SHORT_LABELS[kpi.id] || kpi.label;
        const badgeInfo = CLEAN_BADGES[kpi.id] || { text: kpi.delta_formatted, tone: "neutral" };

        let badgeStyle = "text-[#A1A1A8] bg-[#A1A1A8]/10 border-[#A1A1A8]/20";
        let sparkColor = "#A1A1A8";

        if (badgeInfo.tone === "good") {
          badgeStyle = "text-[#5CB85C] bg-[#5CB85C]/10 border-[#5CB85C]/30";
          sparkColor = "#5CB85C";
        } else if (badgeInfo.tone === "bad") {
          badgeStyle = "text-[#D9534F] bg-[#D9534F]/10 border-[#D9534F]/30";
          sparkColor = "#D9534F";
        } else if (badgeInfo.tone === "warn") {
          badgeStyle = "text-[#E8A838] bg-[#E8A838]/10 border-[#E8A838]/30";
          sparkColor = "#E8A838";
        }

        return (
          <div
            key={kpi.id}
            onClick={() => onCardClick(kpi.id)}
            className="group flex h-[152px] cursor-pointer flex-col justify-between rounded-[20px] border border-[#1C1C20] bg-[#0E0E10] p-4.5 transition-all hover:-translate-y-0.5 hover:border-[#6B6B73]/60 hover:bg-[#141416] hover:shadow-xl"
            title={kpi.tooltip}
          >
            {/* Top row: Chip + Short Label + Dedicated Sparkline in top right */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-[#1C1C20] bg-[#1A1A1D]">
                  {ICON_MAP[kpi.icon] || <Activity className="h-4 w-4 text-[#FFFFFF]" />}
                </div>
                <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73] truncate">
                  {shortLabel}
                </span>
              </div>

              {/* Sparkline cleanly positioned in top-right with zero overlap */}
              <div className="shrink-0 pl-2 opacity-75 group-hover:opacity-100 transition-opacity">
                {renderSparkline(kpi.sparkline, sparkColor)}
              </div>
            </div>

            {/* Middle: Big Value */}
            <div className="my-auto pt-1">
              <div className="font-mono text-[30px] font-bold tracking-tight text-[#FFFFFF] leading-none">
                {kpi.value}
              </div>
            </div>

            {/* Bottom: Clean single badge without cluttered extra sentences */}
            <div className="pt-1">
              <span
                className={`inline-flex items-center rounded-md border px-2 py-0.5 font-mono text-[10px] font-semibold ${badgeStyle}`}
              >
                {badgeInfo.text}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
