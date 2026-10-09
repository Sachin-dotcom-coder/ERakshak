import React from "react";
import {
  AlertTriangle,
  Siren,
  Shield,
  Activity,
  Zap,
  ArrowRight,
  Download,
  CheckCircle2,
  Clock,
  Camera,
  Server,
  Cpu,
} from "lucide-react";

interface SecondaryTabsProps {
  activeTab: "CONGESTION" | "SIGNALS" | "ENFORCEMENT" | "INCIDENTS" | "SYSTEM HEALTH";
  incidents: any;
  signals: any;
  systemHealth: any;
  onSelectJunction: (id: string) => void;
  onExportPdf: () => void;
}

export const ReportsSecondaryTabs: React.FC<SecondaryTabsProps> = ({
  activeTab,
  incidents,
  signals,
  systemHealth,
  onSelectJunction,
  onExportPdf,
}) => {
  if (activeTab === "INCIDENTS") {
    return (
      <div className="space-y-6">
        {/* KPI Strip */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">MEAN TIME TO CLEAR (MTTR)</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#FFFFFF]">
              {incidents?.mttr_mean_min ?? 18.4} min
            </div>
            <span className="text-[11px] text-[#A1A1A8]">p90: {incidents?.mttr_p90_min ?? 32} min</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">EMERGENCY RESPONSE LATENCY</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#5CB85C]">
              {incidents?.emergency_avg_latency_s ?? 9.4} s
            </div>
            <span className="text-[11px] text-[#A1A1A8]">Target &lt; 12.0s achieved</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">THROUGHPUT LOST TODAY</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#E8A838]">
              {incidents?.throughput_lost_pcu_h ?? 4820} PCU
            </div>
            <span className="text-[11px] text-[#A1A1A8]">Due to curb lane blockages</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5 flex flex-col justify-between">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">SHIFT HANDOVER</span>
            <button
              onClick={onExportPdf}
              className="mt-2 flex items-center justify-center gap-2 rounded-xl bg-[#FFFFFF] px-3 py-2 font-mono text-[11px] font-bold text-[#0A0A0B] hover:bg-[#FFFFFF]/90"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export Handover PDF</span>
            </button>
          </div>
        </div>

        {/* Active Incident Log */}
        <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-6">
          <div className="border-b border-[#1C1C20] pb-4">
            <h3 className="text-[17px] font-semibold text-[#FFFFFF]">Active Incidents Log</h3>
            <p className="text-[12px] text-[#A1A1A8]">Real-time stalls, wrong-way entries, and emergency preemption events</p>
          </div>

          <div className="mt-4 space-y-3">
            {(incidents?.active_incidents || []).map((inc: any) => (
              <div
                key={inc.id}
                onClick={() => onSelectJunction(inc.junction_id)}
                className="flex cursor-pointer items-center justify-between rounded-xl border border-[#1C1C20] bg-[#141416] p-4 transition-all hover:border-[#6B6B73] hover:bg-[#1A1A1D]"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1A1A1D] border border-[#1C1C20]">
                    <Siren className="h-5 w-5 text-[#D9534F]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 font-mono text-[12px]">
                      <span className="font-bold text-[#FFFFFF]">{inc.type}</span>
                      <span className="text-[#6B6B73]">·</span>
                      <span className="text-[#E8A838]">{inc.id}</span>
                      <span className="rounded bg-[#D9534F]/10 text-[#D9534F] px-1.5 py-0.2 text-[9px] border border-[#D9534F]/30 font-bold">
                        {inc.status}
                      </span>
                    </div>
                    <div className="mt-1 text-[13px] text-[#A1A1A8]">
                      {inc.junction_name} ({inc.junction_id}) · {inc.lane}
                    </div>
                  </div>
                </div>

                <div className="text-right font-mono text-[12px]">
                  <div className="text-[#FFFFFF]">Active {inc.duration_min} min</div>
                  <div className="text-[10px] text-[#6B6B73]">{inc.handler}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === "SIGNALS") {
    return (
      <div className="space-y-6">
        {/* KPI Strip */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">PREEMPTIONS TODAY</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#FFFFFF]">
              {signals?.preemptions_today ?? 14}
            </div>
            <span className="text-[11px] text-[#5CB85C]">
              {signals?.preemption_success_rate ?? 98.2}% success rate
            </span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">CROSS-STREET DELAY COST</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#A1A1A8]">
              {signals?.avg_cross_street_cost_s ?? 18.5} s
            </div>
            <span className="text-[11px] text-[#6B6B73]">Normalizes in 2 cycles</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">MODE DISTRIBUTION</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#FFFFFF]">
              {signals?.adaptive_junctions_count ?? 20} / 22
            </div>
            <span className="text-[11px] text-[#A1A1A8]">20 Adaptive · 1 Fixed · 1 Fallback</span>
          </div>
        </div>

        {/* Mode Timeline & Green Utilization */}
        <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-6">
          <div className="border-b border-[#1C1C20] pb-4">
            <h3 className="text-[17px] font-semibold text-[#FFFFFF]">Green Split Utilization & Safety Validator</h3>
            <p className="text-[12px] text-[#A1A1A8]">Quantified retiming opportunities based on saturated discharge</p>
          </div>

          <div className="mt-4 space-y-3">
            {(signals?.mode_timeline || []).map((sig: any) => (
              <div
                key={sig.id}
                onClick={() => onSelectJunction(sig.id)}
                className="flex cursor-pointer items-center justify-between rounded-xl border border-[#1C1C20] bg-[#141416] p-4 transition-all hover:border-[#6B6B73] hover:bg-[#1A1A1D]"
              >
                <div>
                  <div className="font-semibold text-[#FFFFFF]">{sig.name}</div>
                  <div className="font-mono text-[10px] text-[#6B6B73]">{sig.id}</div>
                </div>

                <div className="flex items-center gap-6 font-mono text-[12px]">
                  <div className="text-right">
                    <span className="text-[10px] text-[#6B6B73] block">GREEN UTILIZATION</span>
                    <span className="font-bold text-[#5CB85C]">{sig.green_utilization}</span>
                  </div>

                  <span
                    className={`rounded border px-2 py-0.5 font-mono text-[10px] font-bold ${
                      sig.mode === "ADAPTIVE"
                        ? "border-[#FFFFFF]/40 text-[#FFFFFF]"
                        : "border-[#E8A838]/40 text-[#E8A838]"
                    }`}
                  >
                    {sig.mode}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === "ENFORCEMENT") {
    return (
      <div className="space-y-6">
        {/* Challan Funnel */}
        <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-6">
          <div className="border-b border-[#1C1C20] pb-4">
            <h3 className="text-[17px] font-semibold text-[#FFFFFF]">Challan Issuance & Enforcement Funnel</h3>
            <p className="text-[12px] text-[#A1A1A8]">Vision detection pipeline throughput to Surat Police Traffic Branch</p>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-5 text-center">
            {[
              { step: "Detected", count: 420, rate: "100%", sub: "AI Vision" },
              { step: "Auto-validated", count: 392, rate: "93.3%", sub: "License OCR" },
              { step: "Officer Reviewed", count: 378, rate: "90.0%", sub: "Manual review" },
              { step: "Challan Issued", count: 365, rate: "86.9%", sub: "SMS dispatched" },
              { step: "Paid", count: 242, rate: "57.6%", sub: "e-Challan portal" },
            ].map((f, i) => (
              <div key={f.step} className="rounded-xl border border-[#1C1C20] bg-[#141416] p-4 relative">
                <span className="font-mono text-[10px] uppercase text-[#6B6B73]">{f.step}</span>
                <div className="mt-2 font-mono text-[26px] font-bold text-[#FFFFFF]">{f.count}</div>
                <div className="font-mono text-[11px] font-semibold text-[#5CB85C]">{f.rate}</div>
                <div className="text-[10px] text-[#A1A1A8] mt-1">{f.sub}</div>
              </div>
            ))}
          </div>
        </div>

        {/* BRTS Speed Impact */}
        <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-6">
          <h3 className="text-[17px] font-semibold text-[#FFFFFF]">BRTS Corridor Intrusion Impact</h3>
          <p className="text-[12px] text-[#A1A1A8] mt-1">
            During intrusion minutes, BRTS bus speed drops from 48.2 km/h to 36.4 km/h (−24.5%).
          </p>
          <div className="mt-4 rounded-xl border border-[#D9534F]/30 bg-[#D9534F]/5 p-4 font-mono text-[12px] text-[#D9534F]">
            ● 43 intrusions today cost Surat BRTS buses an aggregate of 4.1 hours in schedule delay.
          </div>
        </div>
      </div>
    );
  }

  if (activeTab === "SYSTEM HEALTH") {
    return (
      <div className="space-y-6">
        {/* KPI Strip */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">NETWORK UPTIME</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#5CB85C]">
              {systemHealth?.network_uptime_pct ?? 98.4}%
            </div>
            <span className="text-[11px] text-[#A1A1A8]">Past 30 days verified</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">CAMERA STATUS</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#FFFFFF]">
              {systemHealth?.cameras_online ?? 21} / {systemHealth?.cameras_total ?? 22}
            </div>
            <span className="text-[11px] text-[#E8A838]">1 degraded (CAM-A20)</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">INFERENCE LATENCY</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#FFFFFF]">
              {systemHealth?.pipeline_latency_p50_ms ?? 18} ms
            </div>
            <span className="text-[11px] text-[#A1A1A8]">p95: {systemHealth?.pipeline_latency_p95_ms ?? 38} ms</span>
          </div>

          <div className="rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5">
            <span className="font-mono text-[10px] uppercase text-[#6B6B73]">CALIBRATION DRIFT</span>
            <div className="mt-2 font-mono text-[28px] font-bold text-[#5CB85C]">0.4 px</div>
            <span className="text-[11px] text-[#A1A1A8]">Homography reprojection OK</span>
          </div>
        </div>

        {/* Camera Status Grid */}
        <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-6">
          <div className="border-b border-[#1C1C20] pb-4">
            <h3 className="text-[17px] font-semibold text-[#FFFFFF]">Edge Camera Health & Lighting Confidence</h3>
            <p className="text-[12px] text-[#A1A1A8]">Live telemetry heartbeats across all 22 intersections</p>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {(systemHealth?.cameras || []).map((cam: any) => (
              <div
                key={cam.id}
                className="rounded-xl border border-[#1C1C20] bg-[#141416] p-3 flex items-center justify-between"
              >
                <div>
                  <div className="font-mono text-[11px] font-bold text-[#FFFFFF]">{cam.id}</div>
                  <div className="text-[11px] text-[#A1A1A8] truncate max-w-[140px]">{cam.junction}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] text-[#6B6B73]">{cam.fps} fps</span>
                  <span
                    className={`h-2 w-2 rounded-full ${
                      cam.status === "online" ? "bg-[#5CB85C]" : "bg-[#E8A838]"
                    }`}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Fallback / CONGESTION tab
  return (
    <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-6 text-center">
      <h3 className="text-[17px] font-semibold text-[#FFFFFF]">Congestion In-Depth Diagnostics</h3>
      <p className="text-[12px] text-[#A1A1A8] mt-1">
        Explore full 22-junction heatmaps, queue spillback durations, and speed profiles on the Overview tab.
      </p>
    </div>
  );
};
