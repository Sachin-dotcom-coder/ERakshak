import React, { useState } from "react";
import { AppShell } from "./AppShell";
import { ExportModal } from "./ExportModal";
import { useReportsData } from "@/hooks/useReportsData";
import { ReportsFilterBar } from "./reports/ReportsFilterBar";
import { ReportsKpiRow } from "./reports/ReportsKpiRow";
import { ReportsChartsRow } from "./reports/ReportsChartsRow";
import { ReportsHeatmapRow } from "./reports/ReportsHeatmapRow";
import { AdaptiveBenefitPanel } from "./reports/AdaptiveBenefitPanel";
import { RecommendationsTable } from "./reports/RecommendationsTable";
import { JunctionPerformanceTable } from "./reports/JunctionPerformanceTable";
import { JunctionDetailDrawer } from "./reports/JunctionDetailDrawer";
import { ReportsSecondaryTabs } from "./reports/ReportsSecondaryTabs";

type SubTab =
  | "OVERVIEW"
  | "CONGESTION"
  | "SIGNALS"
  | "ENFORCEMENT"
  | "INCIDENTS"
  | "RECOMMENDATIONS"
  | "SYSTEM HEALTH";

const SUB_TABS: SubTab[] = [
  "OVERVIEW",
  "CONGESTION",
  "SIGNALS",
  "ENFORCEMENT",
  "INCIDENTS",
  "RECOMMENDATIONS",
  "SYSTEM HEALTH",
];

export function Reports() {
  const [activeTab, setActiveTab] = useState<SubTab>("OVERVIEW");
  const [exportOpen, setExportOpen] = useState(false);

  const {
    range,
    setRange,
    compare,
    setCompare,
    zone,
    setZone,
    corridor,
    setCorridor,
    delayScope,
    setDelayScope,
    heatmapMetric,
    setHeatmapMetric,
    summary,
    delaySeries,
    losDistribution,
    violations,
    heatmapRows,
    bottlenecks,
    adaptiveBenefit,
    junctions,
    recommendations,
    drawerJunction,
    drawerOpen,
    setDrawerOpen,
    openJunctionDrawer,
    handleRecDecision,
    incidents,
    signals,
    systemHealth,
  } = useReportsData();

  // Click on KPI card routes directly to deep tab
  const handleKpiCardClick = (kpiId: string) => {
    if (kpiId === "network_delay" || kpiId === "throughput" || kpiId === "congested_junctions") {
      setActiveTab("CONGESTION");
    } else if (kpiId === "open_incidents") {
      setActiveTab("INCIDENTS");
    } else if (kpiId === "violations") {
      setActiveTab("ENFORCEMENT");
    } else if (kpiId === "system_health") {
      setActiveTab("SYSTEM HEALTH");
    }
  };

  const pendingRecsCount = recommendations.filter((r) => r.status === "PENDING").length;

  return (
    <AppShell>
      <div className="flex h-full w-full flex-col bg-[#0A0A0B] text-[#FFFFFF] overflow-hidden">
        {/* Sub-Navigation Tabs Bar */}
        <div className="flex items-center justify-between border-b border-[#1C1C20] bg-[#0E0E10] px-6 pt-3">
          <div className="flex items-center gap-6 overflow-x-auto">
            {SUB_TABS.map((tab) => {
              const isActive = activeTab === tab;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`relative pb-3 font-mono text-[12px] font-semibold uppercase tracking-[0.14em] transition-colors ${
                    isActive ? "text-[#FFFFFF]" : "text-[#6B6B73] hover:text-[#A1A1A8]"
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    {tab}
                    {tab === "RECOMMENDATIONS" && pendingRecsCount > 0 && (
                      <span className="rounded-full bg-[#E8A838] px-1.5 py-0.2 text-[9px] font-bold text-[#0A0A0B]">
                        {pendingRecsCount}
                      </span>
                    )}
                  </span>
                  {isActive && (
                    <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#FFFFFF]" />
                  )}
                </button>
              );
            })}
          </div>

          <div className="hidden pb-3 text-right font-mono text-[11px] text-[#6B6B73] md:block">
            <span>22 JUNCTIONS · 6 ZONES · SURAT SMART CITY</span>
          </div>
        </div>

        {/* Global Filter Bar */}
        <ReportsFilterBar
          range={range}
          setRange={setRange}
          compare={compare}
          setCompare={setCompare}
          zone={zone}
          setZone={setZone}
          corridor={corridor}
          setCorridor={setCorridor}
          freshnessSeconds={summary.freshness_seconds}
          isStale={summary.is_stale}
          onExportClick={() => setExportOpen(true)}
        />

        {/* Main Content Area */}
        <div className="flex-1 min-h-0 overflow-y-auto p-6 space-y-6">
          {activeTab === "OVERVIEW" && (
            <>
              {/* Row 1: 6 KPI Cards */}
              <ReportsKpiRow
                kpis={summary.kpis}
                onCardClick={handleKpiCardClick}
              />

              {/* Row 2: 3 Charts */}
              <ReportsChartsRow
                delaySeries={delaySeries}
                delayScope={delayScope}
                setDelayScope={setDelayScope}
                losBlocks={losDistribution}
                violations={violations}
                onOpenCongestion={() => setActiveTab("CONGESTION")}
                onOpenEnforcement={() => setActiveTab("ENFORCEMENT")}
              />

              {/* Row 3: Heatmap (2/3) + Top Bottlenecks (1/3) */}
              <ReportsHeatmapRow
                heatmapRows={heatmapRows}
                bottlenecks={bottlenecks}
                heatmapMetric={heatmapMetric}
                setHeatmapMetric={setHeatmapMetric}
                onSelectJunction={openJunctionDrawer}
              />

              {/* Row 4: Adaptive Benefit Panel */}
              <AdaptiveBenefitPanel data={adaptiveBenefit} />

              {/* Row 5: AI Recommendations Table */}
              <RecommendationsTable
                recommendations={recommendations}
                onDecision={handleRecDecision}
                onSelectJunction={openJunctionDrawer}
              />

              {/* Row 6: Junction Performance Report Table */}
              <JunctionPerformanceTable
                junctions={junctions}
                onSelectJunction={openJunctionDrawer}
              />
            </>
          )}

          {activeTab === "RECOMMENDATIONS" && (
            <div className="space-y-6">
              <RecommendationsTable
                recommendations={recommendations}
                onDecision={handleRecDecision}
                onSelectJunction={openJunctionDrawer}
              />
            </div>
          )}

          {activeTab !== "OVERVIEW" && activeTab !== "RECOMMENDATIONS" && (
            <ReportsSecondaryTabs
              activeTab={activeTab}
              incidents={incidents}
              signals={signals}
              systemHealth={systemHealth}
              onSelectJunction={openJunctionDrawer}
              onExportPdf={() => setExportOpen(true)}
            />
          )}
        </div>
      </div>

      {/* Junction Detail Drawer */}
      <JunctionDetailDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        data={drawerJunction}
      />

      {/* Export Report Modal */}
      <ExportModal open={exportOpen} onClose={() => setExportOpen(false)} />
    </AppShell>
  );
}
