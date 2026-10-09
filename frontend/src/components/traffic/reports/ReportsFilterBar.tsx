import React from "react";
import { RefreshCw, Download, ChevronDown, CheckCircle2, Clock } from "lucide-react";

interface FilterBarProps {
  range: "today" | "24h" | "7d" | "30d" | "custom";
  setRange: (r: "today" | "24h" | "7d" | "30d" | "custom") => void;
  compare: string;
  setCompare: (c: string) => void;
  zone: string;
  setZone: (z: string) => void;
  corridor: string;
  setCorridor: (c: string) => void;
  freshnessSeconds: number;
  isStale: boolean;
  onExportClick: () => void;
}

const RANGES: { id: "today" | "24h" | "7d" | "30d" | "custom"; label: string }[] = [
  { id: "today", label: "Today" },
  { id: "24h", label: "24h" },
  { id: "7d", label: "7d" },
  { id: "30d", label: "30d" },
  { id: "custom", label: "Custom" },
];

const COMPARES = [
  "vs yesterday",
  "vs same weekday last week",
  "vs 7-day average",
  "vs fixed-timing baseline",
  "none",
];

const ZONES = [
  "All zones",
  "South Zone",
  "Central Surat",
  "Ring Road",
  "West Zone",
  "East Zone",
  "North Zone",
  "Dumas Road",
];

const CORRIDORS = [
  "All corridors",
  "BRTS Corridor 1",
  "Ring Road Arterial",
  "Diamond Corridor",
  "Airport Corridor",
  "Hazira Link Corridor",
];

export const ReportsFilterBar: React.FC<FilterBarProps> = ({
  range,
  setRange,
  compare,
  setCompare,
  zone,
  setZone,
  corridor,
  setCorridor,
  freshnessSeconds,
  isStale,
  onExportClick,
}) => {
  return (
    <div className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-3 border-b border-[#1C1C20] bg-[#0A0A0B]/95 px-6 py-3 backdrop-blur-md">
      {/* Left controls */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Range Selector */}
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[11px] font-semibold tracking-wider text-[#6B6B73]">RANGE</span>
          <div className="flex items-center rounded-full border border-[#1C1C20] bg-[#0E0E10] p-0.5">
            {RANGES.map((r) => (
              <button
                key={r.id}
                onClick={() => setRange(r.id)}
                className={`rounded-full px-3 py-1 font-mono text-[11px] font-semibold transition-all ${
                  range === r.id
                    ? "bg-[#FFFFFF] text-[#0A0A0B] shadow-sm"
                    : "text-[#A1A1A8] hover:text-[#FFFFFF]"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Compare Selector */}
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[11px] font-semibold tracking-wider text-[#6B6B73]">COMPARE</span>
          <div className="relative">
            <select
              value={compare}
              onChange={(e) => setCompare(e.target.value)}
              className="appearance-none rounded-full border border-[#1C1C20] bg-[#1A1A1D] px-3 py-1 pr-7 font-mono text-[11px] font-medium text-[#FFFFFF] outline-none transition-colors hover:border-[#6B6B73] focus:border-[#FFFFFF]"
            >
              {COMPARES.map((c) => (
                <option key={c} value={c} className="bg-[#0E0E10] text-[#FFFFFF]">
                  {c}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-2 h-3 w-3 text-[#A1A1A8]" />
          </div>
        </div>

        {/* Zone Selector */}
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[11px] font-semibold tracking-wider text-[#6B6B73]">ZONE</span>
          <div className="relative">
            <select
              value={zone}
              onChange={(e) => setZone(e.target.value)}
              className="appearance-none rounded-full border border-[#1C1C20] bg-[#1A1A1D] px-3 py-1 pr-7 font-mono text-[11px] font-medium text-[#FFFFFF] outline-none transition-colors hover:border-[#6B6B73] focus:border-[#FFFFFF]"
            >
              {ZONES.map((z) => (
                <option key={z} value={z === "All zones" ? "all" : z} className="bg-[#0E0E10] text-[#FFFFFF]">
                  {z}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-2 h-3 w-3 text-[#A1A1A8]" />
          </div>
        </div>

        {/* Corridor Selector */}
        <div className="hidden items-center gap-1.5 xl:flex">
          <span className="font-mono text-[11px] font-semibold tracking-wider text-[#6B6B73]">CORRIDOR</span>
          <div className="relative">
            <select
              value={corridor}
              onChange={(e) => setCorridor(e.target.value)}
              className="appearance-none rounded-full border border-[#1C1C20] bg-[#1A1A1D] px-3 py-1 pr-7 font-mono text-[11px] font-medium text-[#FFFFFF] outline-none transition-colors hover:border-[#6B6B73] focus:border-[#FFFFFF]"
            >
              {CORRIDORS.map((c) => (
                <option key={c} value={c === "All corridors" ? "all" : c} className="bg-[#0E0E10] text-[#FFFFFF]">
                  {c}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-2 h-3 w-3 text-[#A1A1A8]" />
          </div>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-4">
        {/* Freshness Indicator */}
        <div
          className={`flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-[11px] font-medium ${
            isStale
              ? "border-[#E8A838]/40 bg-[#E8A838]/10 text-[#E8A838]"
              : "border-[#1C1C20] bg-[#1A1A1D] text-[#A1A1A8]"
          }`}
          title="Telemetry freshness. Turns amber if stale > 60s"
        >
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${
              isStale ? "bg-[#E8A838]" : "bg-[#5CB85C] animate-pulse"
            }`}
          />
          <span>Live · {freshnessSeconds}s ago</span>
        </div>

        {/* Export Button */}
        <button
          onClick={onExportClick}
          className="flex items-center gap-2 rounded-full border border-[#FFFFFF]/20 bg-[#FFFFFF] px-4 py-1.5 font-mono text-[11px] font-bold uppercase tracking-wider text-[#0A0A0B] shadow-sm transition-all hover:bg-[#FFFFFF]/90 hover:scale-[1.02]"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Export ⌄</span>
        </button>
      </div>
    </div>
  );
};
