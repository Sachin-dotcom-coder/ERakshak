import { useState, useEffect, useCallback } from "react";
import { apiUrl } from "../config";

const BASE = ""; // resolved via apiUrl() helper

export type KpiCardData = {
  id: string;
  label: string;
  value: string;
  unit: string;
  sub_label: string;
  delta: number | null;
  delta_formatted: string;
  delta_is_good: boolean | null;
  status_dot: "green" | "amber" | "red" | null;
  icon: string;
  sparkline: number[];
  tooltip: string;
};

export type DelayPoint = {
  t: string;
  adaptive: number;
  baseline: number;
  savings_s: number;
  savings_pct: number;
  vehicles_served: number;
  is_peak: boolean;
};

export type LosBlock = {
  block: string;
  label: string;
  A_C: number;
  D: number;
  E: number;
  F: number;
};

export type ViolationHour = {
  t: string;
  brts_intrusion: number;
  lane_discipline: number;
  wrong_way: number;
  other: number;
  total: number;
  escalated: boolean;
  is_current_hour: boolean;
};

export type HeatmapRowData = {
  id: string;
  name: string;
  short_name: string;
  zone: string;
  on_brts: boolean;
  mode: string;
  health: string;
  peak_index: number;
  peak_hour: string;
  hours: number[];
};

export type BottleneckRow = {
  rank: string;
  id: string;
  name: string;
  zone: string;
  minutes_above_75: number;
  peak_index: number;
  peak_time: string;
  flags: string[];
};

export type AdaptiveBenefitData = {
  eyebrow: string;
  method: string;
  delay_reduction_pct: number;
  confidence_interval: string;
  sample_coverage: string;
  vehicle_hours_saved: number;
  emissions_avoided_tonnes: number;
  zones: { zone: string; benefit_pct: number | null; status: string }[];
};

export type JunctionReportRow = {
  id: string;
  name: string;
  short_name: string;
  zone: string;
  los: "A" | "B" | "C" | "D" | "E" | "F";
  congestion_index: number;
  avg_delay_s: number;
  delay_delta_pct: number;
  p95_queue_m: number;
  saturation_vc: number;
  throughput_pcu: number;
  cycle_failures_pct: number;
  violations_today: number;
  mode: string;
  on_brts: boolean;
  adaptive_gain_pct: number;
  health: "live" | "degraded" | "offline";
  sparkline: number[];
};

export type RecommendationGrouped = {
  id: number;
  category: "OPERATIONAL" | "INFRASTRUCTURE";
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  issue_title: string;
  junction_ids: string[];
  junction_names: string;
  evidence: string;
  suggested_action: string;
  expected_impact: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  age: string;
  status: "PENDING" | "APPLIED" | "DEFERRED" | "REJECTED";
  measured_outcome: string | null;
};

export type JunctionDetailData = {
  id: string;
  name: string;
  zone: string;
  mode: string;
  on_brts: boolean;
  health: string;
  camera_id: string;
  last_update: string;
  summary: {
    delay_s: number;
    delay_delta_pct: number;
    p95_queue_m: number;
    saturation_vc: number;
    cycle_failure_pct: number;
    los: string;
  };
  approaches: {
    approach: string;
    flow_pcu: number;
    queue_m: number;
    avg_speed: number;
    green_split: string;
    delay_s: number;
  }[];
  index_curve_24h: { hour: string; today: number; typical: number }[];
  events: { time: string; type: string; desc: string }[];
};

export function useReportsData() {
  // Global Filters
  const [range, setRange] = useState<"today" | "24h" | "7d" | "30d" | "custom">("today");
  const [compare, setCompare] = useState<string>("vs yesterday");
  const [zone, setZone] = useState<string>("all");
  const [corridor, setCorridor] = useState<string>("all");
  const [delayScope, setDelayScope] = useState<string>("network");
  const [heatmapMetric, setHeatmapMetric] = useState<"index" | "delay" | "queue" | "deviation">("index");

  // State
  const [summary, setSummary] = useState<{
    kpis: KpiCardData[];
    freshness_seconds: number;
    is_stale: boolean;
    period_label: string;
    compare_label: string;
  }>({
    kpis: [],
    freshness_seconds: 12,
    is_stale: false,
    period_label: "Today (10 Oct 2026)",
    compare_label: "vs yesterday (09 Oct 2026)",
  });

  const [delaySeries, setDelaySeries] = useState<DelayPoint[]>([]);
  const [losDistribution, setLosDistribution] = useState<LosBlock[]>([]);
  const [violations, setViolations] = useState<ViolationHour[]>([]);
  const [heatmapRows, setHeatmapRows] = useState<HeatmapRowData[]>([]);
  const [bottlenecks, setBottlenecks] = useState<BottleneckRow[]>([]);
  const [adaptiveBenefit, setAdaptiveBenefit] = useState<AdaptiveBenefitData | null>(null);
  const [junctions, setJunctions] = useState<JunctionReportRow[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationGrouped[]>([]);
  const [drawerJunction, setDrawerJunction] = useState<JunctionDetailData | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Secondary tab data
  const [incidents, setIncidents] = useState<any>(null);
  const [signals, setSignals] = useState<any>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);

  // Fetch Summary KPIs
  const fetchSummary = useCallback(async () => {
    try {
      const res = await fetch(apiUrl(`/api/reports/summary?range=${range}&compare=${encodeURIComponent(compare)}&zone=${zone}&corridor=${corridor}`));
      if (res.ok) {
        const data = await res.json();
        setSummary(data);
      }
    } catch (e) {
      console.warn("Failed to fetch summary, using fallback", e);
    }
  }, [range, compare, zone, corridor]);

  // Fetch Delay series
  const fetchDelaySeries = useCallback(async () => {
    try {
      const res = await fetch(apiUrl(`/api/reports/delay-series?scope=${delayScope}&range=${range}`));
      if (res.ok) {
        const data = await res.json();
        setDelaySeries(data.data || []);
      }
    } catch (e) {
      console.warn("Failed to fetch delay series", e);
    }
  }, [delayScope, range]);

  // Fetch LOS distribution
  const fetchLos = useCallback(async () => {
    try {
      const res = await fetch(apiUrl(`/api/reports/los-distribution?range=${range}`));
      if (res.ok) {
        const data = await res.json();
        setLosDistribution(data.blocks || []);
      }
    } catch (e) {
      console.warn("Failed to fetch LOS distribution", e);
    }
  }, [range]);

  // Fetch Violations trend
  const fetchViolations = useCallback(async () => {
    try {
      const res = await fetch(apiUrl(`/api/reports/violations?range=${range}`));
      if (res.ok) {
        const data = await res.json();
        setViolations(data.data || []);
      }
    } catch (e) {
      console.warn("Failed to fetch violations trend", e);
    }
  }, [range]);

  // Fetch Heatmap
  const fetchHeatmap = useCallback(async () => {
    try {
      const res = await fetch(apiUrl(`/api/reports/heatmap?metric=${heatmapMetric}&range=${range}`));
      if (res.ok) {
        const data = await res.json();
        setHeatmapRows(data.rows || []);
      }
    } catch (e) {
      console.warn("Failed to fetch heatmap", e);
    }
  }, [heatmapMetric, range]);

  // Fetch Bottlenecks
  const fetchBottlenecks = useCallback(async () => {
    try {
      const res = await fetch(apiUrl('/api/reports/bottlenecks'));
      if (res.ok) {
        const data = await res.json();
        setBottlenecks(data || []);
      }
    } catch (e) {
      console.warn("Failed to fetch bottlenecks", e);
    }
  }, []);

  // Fetch Adaptive Benefit
  const fetchAdaptiveBenefit = useCallback(async () => {
    try {
      const res = await fetch(apiUrl('/api/reports/adaptive-benefit'));
      if (res.ok) {
        const data = await res.json();
        setAdaptiveBenefit(data);
      }
    } catch (e) {
      console.warn("Failed to fetch adaptive benefit", e);
    }
  }, []);

  // Fetch Junctions Table
  const fetchJunctions = useCallback(async () => {
    try {
      const res = await fetch(apiUrl('/api/reports/junctions-performance'));
      if (res.ok) {
        const data = await res.json();
        setJunctions(data || []);
      }
    } catch (e) {
      console.warn("Failed to fetch junctions", e);
    }
  }, []);

  // Fetch Recommendations
  const fetchRecommendations = useCallback(async () => {
    try {
      const res = await fetch(apiUrl('/api/reports/recommendations-grouped'));
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data || []);
      }
    } catch (e) {
      console.warn("Failed to fetch recommendations", e);
    }
  }, []);

  // Fetch Secondary Tabs
  const fetchSecondaryData = useCallback(async () => {
    try {
      const [incRes, sigRes, sysRes] = await Promise.all([
        fetch(apiUrl('/api/reports/incidents')),
        fetch(apiUrl('/api/reports/signals')),
        fetch(apiUrl('/api/reports/system-health')),
      ]);
      if (incRes.ok) setIncidents(await incRes.json());
      if (sigRes.ok) setSignals(await sigRes.json());
      if (sysRes.ok) setSystemHealth(await sysRes.json());
    } catch (e) {
      console.warn("Failed to fetch secondary tab data", e);
    }
  }, []);

  // Open Drawer for a Junction
  const openJunctionDrawer = useCallback(async (junctionId: string) => {
    try {
      const res = await fetch(apiUrl(`/api/reports/junction/${junctionId}`));
      if (res.ok) {
        const data = await res.json();
        setDrawerJunction(data);
        setDrawerOpen(true);
      }
    } catch (e) {
      console.warn("Failed to load junction drawer", e);
    }
  }, []);

  // Approve / Reject recommendation
  const handleRecDecision = useCallback(async (recId: number, action: "approve" | "reject" | "defer", reason?: string) => {
    try {
      await fetch(apiUrl(`/api/reports/recommendations/${recId}/decision?action=${action}&reason=${encodeURIComponent(reason || "")}`), {
        method: "POST",
      });
      setRecommendations(prev =>
        prev.map(r => (r.id === recId ? { ...r, status: action === "approve" ? "APPLIED" : (action === "reject" ? "REJECTED" : "DEFERRED") } : r))
      );
    } catch (e) {
      console.warn("Failed to send recommendation decision", e);
    }
  }, []);

  // Initial load and periodic soft refresh
  useEffect(() => {
    async function loadAll() {
      setLoading(true);
      await Promise.all([
        fetchSummary(),
        fetchDelaySeries(),
        fetchLos(),
        fetchViolations(),
        fetchHeatmap(),
        fetchBottlenecks(),
        fetchAdaptiveBenefit(),
        fetchJunctions(),
        fetchRecommendations(),
        fetchSecondaryData(),
      ]);
      setLoading(false);
    }
    loadAll();

    const interval = setInterval(() => {
      fetchSummary();
      fetchHeatmap();
    }, 60000);
    return () => clearInterval(interval);
  }, [fetchSummary, fetchDelaySeries, fetchLos, fetchViolations, fetchHeatmap, fetchBottlenecks, fetchAdaptiveBenefit, fetchJunctions, fetchRecommendations, fetchSecondaryData]);

  return {
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
    loading,
    refresh: fetchSummary,
  };
}
