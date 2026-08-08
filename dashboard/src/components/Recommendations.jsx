import React, { useState } from 'react';
import { Lightbulb, CheckCircle2, ChevronRight, Filter, AlertTriangle } from 'lucide-react';

export default function Recommendations({ recommendations, onApproveRecommendation }) {
  const [filter, setFilter] = useState('pending'); // 'pending' or 'history'

  const filteredRecs = recommendations.filter(r => {
    if (filter === 'pending') return r.status === 'pending';
    return r.status !== 'pending';
  });

  const getSeverityStyle = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-500/10 text-red-400 border-red-500/30';
      case 'high':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      case 'medium':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  const getIssueLabel = (type) => {
    return type.replace(/_/g, ' ').toUpperCase();
  };

  return (
    <div className="glass-card p-4 flex flex-col h-full overflow-hidden">
      {/* Header and Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 mb-3 gap-2">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Lightbulb className="text-amber-400" size={20} />
          Predictive Infrastructure Planning
        </h2>
        
        {/* Toggle Filters */}
        <div className="flex bg-slate-900 p-0.5 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setFilter('pending')}
            className={`px-3 py-1 rounded-md font-medium transition-all ${
              filter === 'pending'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Pending Suggestions
          </button>
          <button
            onClick={() => setFilter('history')}
            className={`px-3 py-1 rounded-md font-medium transition-all ${
              filter === 'history'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Action Log
          </button>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {filteredRecs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 py-12">
            <CheckCircle2 size={36} className="text-slate-600 mb-2 stroke-1" />
            <p className="text-sm">No engineering suggestions</p>
            <p className="text-xs text-slate-600 mt-1">
              {filter === 'pending' 
                ? 'Infrastructure thresholds are currently satisfied.' 
                : 'No approved civil engineering actions logged yet.'}
            </p>
          </div>
        ) : (
          filteredRecs.map((r) => (
            <div 
              key={r.id} 
              className={`p-3.5 rounded-lg border bg-slate-900/40 transition-all duration-200 ${
                r.severity === 'critical' ? 'border-l-4 border-l-red-500' : 
                r.severity === 'high' ? 'border-l-4 border-l-orange-500' : 'border-l-4 border-l-blue-500'
              } border-slate-800`}
            >
              <div className="flex justify-between items-start">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getSeverityStyle(r.severity)}`}>
                  {getIssueLabel(r.issue_type)}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {new Date(r.timestamp).toLocaleTimeString()}
                </span>
              </div>

              <div className="mt-2 text-sm font-semibold text-slate-200">
                📍 {r.junction_name}
              </div>

              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                {r.description}
              </p>

              {/* Proposed Engineering Action */}
              <div className="mt-2.5 p-2 bg-slate-950/70 border border-slate-800/80 rounded-md">
                <div className="text-[10px] font-bold uppercase tracking-wider text-amber-500 flex items-center gap-1">
                  <AlertTriangle size={10} /> Proactive Recommendation:
                </div>
                <div className="text-xs text-slate-300 mt-1 font-medium leading-relaxed">
                  {r.suggested_action}
                </div>
              </div>

              {/* Action Buttons */}
              {r.status === 'pending' ? (
                <div className="mt-3 flex justify-end gap-2 border-t border-slate-800/50 pt-2.5">
                  <button
                    onClick={() => onApproveRecommendation(r.id, 'dismissed')}
                    className="text-xs text-slate-400 hover:text-slate-200 px-3 py-1 rounded hover:bg-slate-800 font-medium transition-colors"
                  >
                    Archive
                  </button>
                  <button
                    onClick={() => onApproveRecommendation(r.id, 'applied')}
                    className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1 rounded font-semibold flex items-center gap-0.5 shadow transition-colors"
                  >
                    Send to Planners <ChevronRight size={12} />
                  </button>
                </div>
              ) : (
                <div className="mt-3 border-t border-slate-800/50 pt-2 flex justify-between items-center text-[11px]">
                  <span className="text-slate-500">Status Update Logged</span>
                  <span className={`font-semibold flex items-center gap-1 ${
                    r.status === 'applied' ? 'text-emerald-400' : 'text-slate-500'
                  }`}>
                    <CheckCircle2 size={12} /> 
                    {r.status === 'applied' ? 'Applied to Municipal Planning' : 'Archived'}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
