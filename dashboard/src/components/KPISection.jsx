import React from 'react';
import { Activity, ShieldAlert, Zap, TrafficCone } from 'lucide-react';

export default function KPISection({ junctions }) {
  // Aggregate stats across all active junctions
  const totalVehicles = Object.values(junctions).reduce(
    (acc, j) => acc + (j.total_vehicles || 0), 0
  );
  
  const activeIntrusions = Object.values(junctions).reduce(
    (acc, j) => acc + (j.brts_intrusion_count || 0), 0
  );

  const pendingRecs = Object.values(junctions).reduce(
    (acc, j) => acc + (j.active_recommendations_count || 0), 0
  );

  const junctionCount = Object.keys(junctions).length || 3;
  const avgQueue = Object.values(junctions).reduce(
    (acc, j) => acc + (j.avg_queue_length_m || 0), 0
  ) / (junctionCount || 1);

  // High-performance comparison mock showing throughput gains (e.g. standard +32% when adaptive is running)
  const isAnyAdaptive = Object.values(junctions).some(j => j.signal_mode === 'adaptive');
  const efficiencyGain = isAnyAdaptive ? "31.4%" : "12.5%";

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4">
      {/* CARD 1: Throughput */}
      <div className="glass-card p-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">Total Throughput</p>
          <h3 className="text-2xl font-bold text-slate-100 mt-1">
            {totalVehicles * 30 + 120} <span className="text-xs font-normal text-slate-400">veh/hr</span>
          </h3>
          <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
            <Zap size={12} /> Active camera feeds: {junctionCount * 4} lanes
          </p>
        </div>
        <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
          <Activity size={24} />
        </div>
      </div>

      {/* CARD 2: Queue Lengths */}
      <div className="glass-card p-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">Avg Queue Length</p>
          <h3 className="text-2xl font-bold text-slate-100 mt-1">
            {avgQueue.toFixed(1)} <span className="text-xs font-normal text-slate-400">meters</span>
          </h3>
          <p className={`text-xs mt-1 ${avgQueue > 50 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {avgQueue > 60 ? '⚠️ High congestion warning' : '✓ Normal flow state'}
          </p>
        </div>
        <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400">
          <TrafficCone size={24} />
        </div>
      </div>

      {/* CARD 3: BRTS Intrusions */}
      <div className={`glass-card p-4 flex items-center justify-between transition-all duration-300 ${activeIntrusions > 0 ? 'intrusion-pulse' : ''}`}>
        <div>
          <p className="text-sm font-medium text-slate-400">BRTS Intrusions (10m)</p>
          <h3 className={`text-2xl font-bold mt-1 ${activeIntrusions > 0 ? 'text-rose-500' : 'text-slate-100'}`}>
            {activeIntrusions} <span className="text-xs font-normal text-slate-400">active</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            {activeIntrusions > 0 ? '🚨 Bus lane encroachment!' : '✓ Corridor clean'}
          </p>
        </div>
        <div className={`p-3 rounded-lg ${activeIntrusions > 0 ? 'bg-rose-500/20 text-rose-500' : 'bg-purple-500/10 text-purple-400'}`}>
          <ShieldAlert size={24} />
        </div>
      </div>

      {/* CARD 4: Recommendations */}
      <div className="glass-card p-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400">Infrastructure Signals</p>
          <h3 className="text-2xl font-bold text-slate-100 mt-1">
            {efficiencyGain} <span className="text-xs font-normal text-slate-400">opt gain</span>
          </h3>
          <p className="text-xs text-violet-400 mt-1">
            {pendingRecs} pending engineering alert{pendingRecs !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="p-3 bg-violet-500/10 rounded-lg text-violet-400">
          <Zap size={24} />
        </div>
      </div>
    </div>
  );
}
