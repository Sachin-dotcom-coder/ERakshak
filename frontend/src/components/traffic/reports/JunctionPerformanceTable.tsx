import React, { useState, useMemo } from "react";
import { ArrowUpDown, Search } from "lucide-react";
import type { JunctionReportRow } from "@/hooks/useReportsData";

interface JunctionTableProps {
  junctions: JunctionReportRow[];
  onSelectJunction: (id: string) => void;
}

type SortField =
  | "name"
  | "congestion_index"
  | "avg_delay_s"
  | "p95_queue_m"
  | "throughput_pcu"
  | "adaptive_gain_pct";

export const JunctionPerformanceTable: React.FC<JunctionTableProps> = ({
  junctions,
  onSelectJunction,
}) => {
  const [search, setSearch] = useState("");
  const [selectedZone, setSelectedZone] = useState("all");
  const [sortField, setSortField] = useState<SortField>("congestion_index");
  const [sortAsc, setSortAsc] = useState(false);

  const zones = useMemo(() => {
    const set = new Set(junctions.map((j) => j.zone));
    return ["all", ...Array.from(set)];
  }, [junctions]);

  const sortedAndFiltered = useMemo(() => {
    return junctions
      .filter((j) => {
        const matchesSearch =
          j.name.toLowerCase().includes(search.toLowerCase()) ||
          j.id.toLowerCase().includes(search.toLowerCase());
        const matchesZone = selectedZone === "all" || j.zone === selectedZone;
        return matchesSearch && matchesZone;
      })
      .sort((a, b) => {
        let va = a[sortField];
        let vb = b[sortField];
        if (typeof va === "string") {
          return sortAsc
            ? va.localeCompare(vb as string)
            : (vb as string).localeCompare(va);
        }
        return sortAsc ? (va as number) - (vb as number) : (vb as number) - (va as number);
      });
  }, [junctions, search, selectedZone, sortField, sortAsc]);

  const handleSort = (field: SortField) => {
    if (sortField === field) setSortAsc((v) => !v);
    else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const getCongestionColor = (idx: number) => {
    if (idx >= 75) return "#D9534F";
    if (idx >= 55) return "#E8A838";
    if (idx >= 35) return "#5A5A60";
    return "#1E1E22";
  };

  const getLosBadge = (los: string) => {
    if (los === "F") return "bg-[#D9534F]/20 text-[#D9534F] border-[#D9534F]/40";
    if (los === "E") return "bg-[#E8A838]/20 text-[#E8A838] border-[#E8A838]/40";
    return "bg-[#FFFFFF]/10 text-[#A1A1A8] border-[#FFFFFF]/20";
  };

  return (
    <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1C1C20] pb-3">
        <div>
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
            JUNCTION PERFORMANCE REPORT
          </span>
          <h3 className="mt-0.5 text-[15px] font-semibold text-[#FFFFFF]">
            All 22 Monitored Junctions
          </h3>
        </div>

        {/* Search & Filter pills */}
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-2 h-3 w-3 text-[#6B6B73]" />
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rounded-full border border-[#1C1C20] bg-[#1A1A1D] pl-7 pr-3 py-1 font-mono text-[10px] text-[#FFFFFF] placeholder-[#6B6B73] outline-none hover:border-[#6B6B73] focus:border-[#FFFFFF]"
            />
          </div>

          <select
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
            className="rounded-full border border-[#1C1C20] bg-[#1A1A1D] px-2.5 py-1 font-mono text-[10px] text-[#FFFFFF] outline-none hover:border-[#6B6B73]"
          >
            {zones.map((z) => (
              <option key={z} value={z} className="bg-[#0E0E10]">
                {z === "all" ? "All Zones" : z}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Clean, Streamlined Table */}
      <div className="mt-3 overflow-x-auto">
        <table className="w-full border-collapse text-left whitespace-nowrap">
          <thead>
            <tr className="border-b border-[#1C1C20] font-mono text-[10px] uppercase tracking-[0.14em] text-[#6B6B73]">
              <th
                onClick={() => handleSort("name")}
                className="cursor-pointer pb-2.5 pl-3 hover:text-[#FFFFFF]"
              >
                Junction <ArrowUpDown className="inline h-2.5 w-2.5 ml-1" />
              </th>
              <th className="pb-2.5">Zone</th>
              <th className="pb-2.5">LOS</th>
              <th
                onClick={() => handleSort("congestion_index")}
                className="cursor-pointer pb-2.5 hover:text-[#FFFFFF]"
              >
                Congestion <ArrowUpDown className="inline h-2.5 w-2.5 ml-1" />
              </th>
              <th
                onClick={() => handleSort("avg_delay_s")}
                className="cursor-pointer pb-2.5 hover:text-[#FFFFFF]"
              >
                Avg Delay <ArrowUpDown className="inline h-2.5 w-2.5 ml-1" />
              </th>
              <th
                onClick={() => handleSort("p95_queue_m")}
                className="cursor-pointer pb-2.5 hover:text-[#FFFFFF]"
              >
                Queue P95 <ArrowUpDown className="inline h-2.5 w-2.5 ml-1" />
              </th>
              <th
                onClick={() => handleSort("throughput_pcu")}
                className="cursor-pointer pb-2.5 hover:text-[#FFFFFF]"
              >
                Throughput <ArrowUpDown className="inline h-2.5 w-2.5 ml-1" />
              </th>
              <th
                onClick={() => handleSort("adaptive_gain_pct")}
                className="cursor-pointer pb-2.5 pr-3 text-right hover:text-[#FFFFFF]"
              >
                Adaptive Gain <ArrowUpDown className="inline h-2.5 w-2.5 ml-1" />
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1C1C20]/40 text-[12px]">
            {sortedAndFiltered.map((j) => (
              <tr
                key={j.id}
                onClick={() => onSelectJunction(j.id)}
                className="group cursor-pointer transition-colors hover:bg-[#1A1A1D]/60"
              >
                {/* Junction Name */}
                <td className="py-2.5 pl-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        j.health === "live" ? "bg-[#5CB85C]" : "bg-[#E8A838]"
                      }`}
                    />
                    <div>
                      <span className="font-semibold text-[#FFFFFF] group-hover:text-[#E8A838]">
                        {j.name}
                      </span>
                      <span className="font-mono text-[10px] text-[#6B6B73] ml-2">
                        {j.id}
                      </span>
                    </div>
                  </div>
                </td>

                {/* Zone */}
                <td className="py-2.5 text-[#A1A1A8] font-medium text-[11px]">
                  {j.zone}
                </td>

                {/* LOS Grade */}
                <td className="py-2.5">
                  <span
                    className={`rounded border px-1.5 py-0.2 font-mono text-[9px] font-bold ${getLosBadge(
                      j.los
                    )}`}
                  >
                    {j.los}
                  </span>
                </td>

                {/* Congestion Bar */}
                <td className="py-2.5">
                  <div className="flex items-center gap-2 w-28">
                    <div className="h-1 flex-1 rounded-full bg-[#1A1A1D] overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${j.congestion_index}%`,
                          backgroundColor: getCongestionColor(j.congestion_index),
                        }}
                      />
                    </div>
                    <span className="font-mono text-[10px] font-bold text-[#FFFFFF] w-5">
                      {Math.round(j.congestion_index)}
                    </span>
                  </div>
                </td>

                {/* Avg Delay */}
                <td className="py-2.5 font-mono text-[11px] text-[#FFFFFF]">
                  {j.avg_delay_s}s{" "}
                  <span className="text-[9px] text-[#5CB85C]">▼{Math.abs(j.delay_delta_pct)}%</span>
                </td>

                {/* P95 Queue */}
                <td className="py-2.5 font-mono text-[11px] text-[#A1A1A8]">
                  {j.p95_queue_m}m
                </td>

                {/* Throughput */}
                <td className="py-2.5 font-mono text-[11px] text-[#FFFFFF]">
                  {j.throughput_pcu.toLocaleString("en-IN")}{" "}
                  <span className="text-[9px] text-[#6B6B73]">PCU</span>
                </td>

                {/* Adaptive Gain */}
                <td className="py-2.5 pr-3 text-right">
                  <span className="font-mono text-[11px] font-bold text-[#5CB85C]">
                    −{j.adaptive_gain_pct}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
