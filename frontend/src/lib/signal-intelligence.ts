import type { Junction } from "./traffic-types";

export type RoadDensityLevel = "optimal" | "moderate" | "heavy" | "gridlock";

export function getRoadDensityLevel(density: number): RoadDensityLevel {
  if (density < 45) return "optimal";
  if (density < 65) return "moderate";
  if (density < 80) return "heavy";
  return "gridlock";
}

export function getRoadDensityColor(density: number): string {
  if (density < 45) return "#10b981"; // Emerald Free Flow
  if (density < 65) return "#f59e0b"; // Amber Moderate
  if (density < 80) return "#f97316"; // Orange Heavy
  return "#ef4444"; // Rose / Red Saturated Gridlock
}

export function getRoadDensityBadgeText(density: number): string {
  if (density < 45) return "Free Flow";
  if (density < 65) return "Moderate Density";
  if (density < 80) return "Heavy Congestion";
  return "Critical Gridlock";
}

export function getRoadDensityLOS(density: number): { los: string; desc: string } {
  if (density < 30) return { los: "LOS A", desc: "Free flow, minimum delay" };
  if (density < 45) return { los: "LOS B", desc: "Stable flow, slight delay" };
  if (density < 60) return { los: "LOS C", desc: "Stable flow, moderate delay" };
  if (density < 75) return { los: "LOS D", desc: "Approaching capacity, notable delay" };
  if (density < 88) return { los: "LOS E", desc: "Unstable flow, capacity saturated" };
  return { los: "LOS F", desc: "Breakdown, forced flow, severe queues" };
}

export type TimerCycleHistoryPoint = {
  cycleId: string;
  timestamp: string;
  adaptiveGreen: number; // dynamically allocated green duration in seconds
  staticBaseline: number; // fixed baseline timer
  roadDensity: number; // density % at that cycle
  queueCleared: number; // vehicles cleared
  avgWaitSec: number; // average vehicle wait time
  reward: number; // RL agent reward
};

export function generateSignalTimerHistory(junction: Junction): TimerCycleHistoryPoint[] {
  const points: TimerCycleHistoryPoint[] = [];
  const baseStatic = junction.staticCycle.find((p) => p.phase === "GREEN")?.seconds || 35;
  const currentDensity = junction.congestionIndex || 60;
  const now = Date.now();

  for (let i = 14; i >= 0; i--) {
    const cycleTime = now - i * 110_000;
    const timeStr = new Date(cycleTime).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

    // Create realistic cyclic variation mimicking traffic pulses & AI response
    const wave = Math.sin((14 - i) * 0.55);
    const densityNoise = Math.sin((14 - i) * 0.9) * 12;
    const histDensity = Math.min(98, Math.max(22, Math.round(currentDensity + densityNoise)));

    // AI adapts green time directly proportional to road density
    // High density -> longer green; Low density -> shorter green to prevent wasted green
    const greenBoost = Math.round((histDensity - 40) * 0.52);
    const histAdaptiveGreen = Math.min(75, Math.max(18, baseStatic + greenBoost + Math.round(wave * 4)));
    const histQueueCleared = Math.round(histAdaptiveGreen * 0.68 + (histDensity / 10));
    const histWaitSec = Math.max(16, Math.round(85 - (histAdaptiveGreen * 0.75)));
    const histReward = Number((12.5 + (histAdaptiveGreen / baseStatic) * 5.2 - (histWaitSec / 12)).toFixed(1));

    points.push({
      cycleId: `C-${15 - i}`,
      timestamp: timeStr,
      adaptiveGreen: histAdaptiveGreen,
      staticBaseline: baseStatic,
      roadDensity: histDensity,
      queueCleared: histQueueCleared,
      avgWaitSec: histWaitSec,
      reward: histReward,
    });
  }

  return points;
}

export type PhaseSplitData = {
  cycle: string;
  northSouthGreen: number;
  eastWestGreen: number;
  amberClearance: number;
  allRedSafety: number;
};

export function generatePhaseSplitHistory(junction: Junction): PhaseSplitData[] {
  const result: PhaseSplitData[] = [];
  const baseGreen = junction.signalCountdown || 45;
  for (let i = 8; i >= 1; i--) {
    const ns = Math.min(65, Math.max(22, Math.round(baseGreen + Math.sin(i) * 10)));
    const ew = Math.min(55, Math.max(20, Math.round(40 - Math.sin(i) * 8)));
    result.push({
      cycle: `Cycle ${i}`,
      northSouthGreen: ns,
      eastWestGreen: ew,
      amberClearance: 4,
      allRedSafety: 2,
    });
  }
  return result;
}

export type AIDecisionLog = {
  id: string;
  time: string;
  action: string;
  rationale: string;
  impact: string;
  severity: "boost" | "truncate" | "corridor" | "balanced";
};

export function generateAIDecisionLogs(junction: Junction): AIDecisionLog[] {
  const now = Date.now();
  const formatTime = (offsetSec: number) =>
    new Date(now - offsetSec * 1000).toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  const highDensityArm =
    junction.lanes.reduce((prev, curr) => (curr.density > prev.density ? curr : prev), junction.lanes[0])?.name ||
    "North Approach";

  return [
    {
      id: "LOG-1",
      time: formatTime(25),
      action: "Extended Green Phase (+14s)",
      rationale: `${highDensityArm} reached ${junction.congestionIndex}% road density with queued vehicles. Prolonged green phase dynamically to prevent gridlock.`,
      impact: "+22 vehicles cleared; queue reduced by 42m",
      severity: "boost",
    },
    {
      id: "LOG-2",
      time: formatTime(130),
      action: "Early Phase Truncation (-8s)",
      rationale: "Approach sensors detected empty queue on cross-traffic arm. Cut green early to eliminate idle waiting.",
      impact: "Saved 8s cycle delay; zero empty green waste",
      severity: "truncate",
    },
    {
      id: "LOG-3",
      time: formatTime(245),
      action: "Corridor Green Wave Synchronization",
      rationale: "Coordinated downstream phase split with adjacent Ring Road signal JN-02 for platoon progression.",
      impact: "Reduced stops by 36% along arterial route",
      severity: "corridor",
    },
    {
      id: "LOG-4",
      time: formatTime(380),
      action: "Max-Pressure Arm Balancing",
      rationale: "Equalized pressure gradient between North and West approaches based on real-time vehicle arrival rates.",
      impact: "Balanced saturation across all 4 intersection arms",
      severity: "balanced",
    },
  ];
}

export type LearningConvergencePoint = {
  episode: string;
  agentReward: number;
  baselineReward: number;
  avgDelaySec: number;
};

export function generateLearningConvergenceData(): LearningConvergencePoint[] {
  return [
    { episode: "Ep 1k", agentReward: -68, baselineReward: -65, avgDelaySec: 74 },
    { episode: "Ep 20k", agentReward: -52, baselineReward: -65, avgDelaySec: 66 },
    { episode: "Ep 40k", agentReward: -38, baselineReward: -65, avgDelaySec: 58 },
    { episode: "Ep 60k", agentReward: -24, baselineReward: -65, avgDelaySec: 49 },
    { episode: "Ep 80k", agentReward: -16, baselineReward: -65, avgDelaySec: 42 },
    { episode: "Ep 100k", agentReward: -9, baselineReward: -65, avgDelaySec: 36 },
    { episode: "Ep 120k", agentReward: -5, baselineReward: -65, avgDelaySec: 32 },
    { episode: "Ep 140k", agentReward: -3, baselineReward: -65, avgDelaySec: 29 },
  ];
}

export type SignalReportSummary = {
  junctionId: string;
  name: string;
  zone: string;
  overallDensity: number;
  los: string;
  losDesc: string;
  waitReductionPct: number;
  queueReductionPct: number;
  throughputGainPct: number;
  fuelSavedLitersDay: number;
  co2SavedKgDay: number;
  economicSavingsInrDay: number;
  spillbackAvoidancePct: number;
  phaseAudit: {
    arm: string;
    density: number;
    staticGreen: number;
    adaptiveGreen: number;
    queueCleared: number;
    delaySavedPct: number;
    status: string;
  }[];
};

export function generateSignalReportSummary(junction: Junction): SignalReportSummary {
  const density = junction.congestionIndex || 60;
  const losData = getRoadDensityLOS(density);
  const waitReduction = Math.round(28 + (density / 100) * 18);
  const queueReduction = Math.round(35 + (density / 100) * 24);
  const throughputGain = Number((14 + (density / 100) * 15.5).toFixed(1));
  const fuelSaved = Math.round(85 + (density / 100) * 80);
  const co2Saved = Math.round(fuelSaved * 2.38);
  const inrSaved = Math.round(fuelSaved * 96.5);

  const phaseAudit = junction.lanes.map((l, idx) => {
    const staticG = 30 + (idx % 2) * 5;
    const adaptiveG = Math.round(staticG * (1 + (l.density - 40) / 100));
    return {
      arm: l.name,
      density: l.density,
      staticGreen: staticG,
      adaptiveGreen: Math.max(20, adaptiveG),
      queueCleared: Math.round(adaptiveG * 0.72),
      delaySavedPct: Math.round(25 + (l.density / 100) * 25),
      status: l.density > 75 ? "Saturated Demand" : l.density > 50 ? "Balanced Flow" : "Free Flow",
    };
  });

  return {
    junctionId: junction.id,
    name: junction.name,
    zone: junction.zone,
    overallDensity: density,
    los: losData.los,
    losDesc: losData.desc,
    waitReductionPct: waitReduction,
    queueReductionPct: queueReduction,
    throughputGainPct: throughputGain,
    fuelSavedLitersDay: fuelSaved,
    co2SavedKgDay: co2Saved,
    economicSavingsInrDay: inrSaved,
    spillbackAvoidancePct: 99.2,
    phaseAudit,
  };
}
