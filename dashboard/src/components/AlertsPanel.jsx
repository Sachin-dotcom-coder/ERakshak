import React, { useState } from 'react';
import { Camera, AlertCircle, Calendar, Eye, X } from 'lucide-react';

export default function AlertsPanel({ violations }) {
  const [selectedViolation, setSelectedViolation] = useState(null);

  const getVehicleLabel = (type) => {
    switch (type.toLowerCase()) {
      case 'auto': return '🛺 Auto Rickshaw';
      case 'motorcycle': return '🏍️ Motorcycle';
      case 'car': return '🚗 Private Car';
      case 'suv': return '🚙 SUV';
      default: return '🚗 Vehicle';
    }
  };

  return (
    <div className="glass-card p-4 flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <AlertCircle className="text-rose-500 animate-pulse" size={20} />
          Live Violations Log
        </h2>
        <span className="bg-rose-500/10 text-rose-400 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-rose-500/20">
          Real-time Feed
        </span>
      </div>

      {/* Scrollable Feed List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {violations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 py-10">
            <Camera size={36} className="stroke-1 mb-2" />
            <p className="text-sm">Monitoring cameras...</p>
            <p className="text-xs text-slate-600 mt-1">No violations logged in this session.</p>
          </div>
        ) : (
          violations.map((v) => (
            <div 
              key={v.id || Math.random()} 
              className="bg-slate-900/50 hover:bg-slate-900/90 border border-slate-800 hover:border-slate-700 p-3 rounded-lg transition-all duration-200"
            >
              <div className="flex justify-between items-start">
                <span className="bg-rose-500/15 text-rose-400 text-xs font-semibold px-2 py-0.5 rounded border border-rose-500/10">
                  {v.violation_type === 'brts_intrusion' ? 'BRTS Intrusion' : 'Lane Discipline'}
                </span>
                <span className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
                  <Calendar size={10} /> {v.timestamp ? new Date(v.timestamp).toLocaleTimeString() : 'Live'}
                </span>
              </div>
              
              <div className="mt-2 text-sm text-slate-300">
                <strong className="text-slate-100">{getVehicleLabel(v.vehicle_type)}</strong> detected encroaching.
              </div>
              
              <div className="mt-1 text-[11px] text-slate-400">
                📍 {v.junction_name} • {v.lane_name}
              </div>

              <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex justify-end">
                <button
                  onClick={() => setSelectedViolation(v)}
                  className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition-colors"
                >
                  <Eye size={12} /> View Frame Bounding Box
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* YOLO Camera Frame Overlay Modal */}
      {selectedViolation && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full overflow-hidden shadow-2xl">
            <div className="bg-slate-950 p-4 border-b border-slate-800 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
                  <Camera size={16} className="text-rose-500" />
                  Junction Camera Feed ID: {selectedViolation.lane_id}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {selectedViolation.junction_name} — {selectedViolation.lane_name}
                </p>
              </div>
              <button 
                onClick={() => setSelectedViolation(null)}
                className="text-slate-400 hover:text-slate-200 p-1 hover:bg-slate-800 rounded-full transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Simulated CV Bounding Box Frame */}
            <div className="relative bg-slate-950 aspect-video flex items-center justify-center overflow-hidden">
              {/* Fake Street Background using a structured abstract dark grid */}
              <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-30"></div>
              
              {/* Simulated Lane Divider Lines */}
              <div className="absolute inset-x-0 top-1/2 h-1 border-t border-dashed border-slate-700 transform -skew-x-12"></div>
              <div className="absolute inset-x-0 top-1/2 h-4 border-y border-solid border-purple-500/20 transform skew-y-6 bg-purple-500/5">
                <span className="absolute left-4 top-0.5 text-[8px] text-purple-400 uppercase tracking-widest font-mono">DEDICATED BRTS CORRIDOR</span>
              </div>

              {/* Bounding Box Render */}
              <div 
                className="absolute border-2 border-rose-500 bg-rose-500/10 rounded-sm flex flex-col p-1 cursor-default select-none animate-pulse"
                style={{
                  width: '140px',
                  height: '110px',
                  left: '35%',
                  top: '30%',
                  boxShadow: '0 0 16px rgba(239, 68, 68, 0.4)'
                }}
              >
                {/* YOLO Bounding Box Tag */}
                <div className="absolute -top-6 left-[-2px] bg-rose-600 text-white font-mono text-[9px] font-bold px-1.5 py-0.5 rounded-t-sm flex items-center gap-1 uppercase">
                  <span>{selectedViolation.vehicle_type}</span>
                  <span className="bg-black/30 px-1 rounded">94.8%</span>
                </div>
                
                {/* CV Intrusion Zone Warning */}
                <div className="m-auto text-[8px] font-bold text-center text-rose-200 uppercase tracking-wide bg-rose-950/70 py-0.5 px-1 rounded">
                  Zone Intruded
                </div>
              </div>

              {/* General Camera HUD */}
              <div className="absolute top-2 left-2 text-[9px] font-mono text-slate-400 bg-black/60 px-1.5 py-0.5 rounded">
                REC • 1080P • 30 FPS
              </div>
              <div className="absolute top-2 right-2 text-[9px] font-mono text-slate-400 bg-black/60 px-1.5 py-0.5 rounded">
                {selectedViolation.timestamp ? new Date(selectedViolation.timestamp).toLocaleTimeString() : 'Live'}
              </div>
              <div className="absolute bottom-2 left-2 text-[9px] font-mono text-rose-400 bg-rose-950/80 border border-rose-900 px-2 py-0.5 rounded">
                VIOLATION: DEDICATED BRTS LANE INTRUSION
              </div>
              <div className="absolute bottom-2 right-2 text-[9px] font-mono text-emerald-400 bg-black/60 px-1.5 py-0.5 rounded">
                CAM_ZONE_{selectedViolation.lane_id.substring(selectedViolation.lane_id.length - 3)}
              </div>
            </div>

            {/* Modal Info Footer */}
            <div className="p-4 bg-slate-900 border-t border-slate-800 flex justify-between items-center text-xs">
              <span className="text-slate-400">
                Action: Automated fine request issued via e-challan integration.
              </span>
              <button
                onClick={() => setSelectedViolation(null)}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium px-4 py-1.5 rounded transition-colors"
              >
                Acknowledge Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
