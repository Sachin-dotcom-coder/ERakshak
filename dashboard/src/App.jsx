import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import KPISection from './components/KPISection';
import JunctionMap from './components/JunctionMap';
import AlertsPanel from './components/AlertsPanel';
import Recommendations from './components/Recommendations';
import WhatIfToggle from './components/WhatIfToggle';
import { ShieldAlert, RefreshCw, Cpu, Activity } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('map');
  const [junctions, setJunctions] = useState({});
  const [violations, setViolations] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedJunctionId, setSelectedJunctionId] = useState('J001');
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  // 1. Initial REST API load of history (runs once on mount)
  useEffect(() => {
    // Load all junctions
    fetch('http://localhost:8000/api/junctions')
      .then(res => res.json())
      .then(data => {
        const initialJunctions = {};
        data.forEach(j => {
          initialJunctions[j.id] = {
            ...j,
            total_vehicles: 0,
            avg_queue_length_m: 0.0,
            brts_intrusion_count: 0,
            active_recommendations_count: 0,
            lanes: j.lanes.map(l => ({ ...l, vehicle_count: 0, queue_length_m: 0.0, average_speed_kmh: 40.0 }))
          };
        });
        setJunctions(initialJunctions);
      })
      .catch(err => console.error("Failed to load junctions:", err));

    // Load recent violations
    fetch('http://localhost:8000/api/violations')
      .then(res => res.json())
      .then(data => setViolations(data))
      .catch(err => console.error("Failed to load violations:", err));

    // Load recommendations
    fetch('http://localhost:8000/api/recommendations')
      .then(res => res.json())
      .then(data => setRecommendations(data))
      .catch(err => console.error("Failed to load recommendations:", err));
  }, []);

  // 2. Establish WebSocket pipeline for live feeds
  useEffect(() => {
    const connectWS = () => {
      console.log("WebSocket: Connecting to traffic feed...");
      const socket = new WebSocket('ws://localhost:8000/api/ws/traffic');
      
      socket.onopen = () => {
        console.log("WebSocket: Connection established.");
        setConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          
          if (msg.type === 'junction_update') {
            setJunctions(prev => ({
              ...prev,
              [msg.junction_id]: {
                ...prev[msg.junction_id],
                ...msg
              }
            }));
          } else if (msg.type === 'new_violation') {
            setViolations(prev => [msg, ...prev].slice(0, 50));
          } else if (msg.type === 'new_recommendation') {
            setRecommendations(prev => [msg, ...prev]);
          }
        } catch (e) {
          console.error("Error parsing WebSocket event content:", e);
        }
      };

      socket.onclose = () => {
        console.log("WebSocket: Connection closed. Retrying in 3 seconds...");
        setConnected(false);
        setTimeout(connectWS, 3000);
      };

      socket.onerror = (err) => {
        console.error("WebSocket: connection encountered an error:", err);
      };

      wsRef.current = socket;
    };

    connectWS();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // 3. Action Handler: Toggle Junction optimization mode (Fixed vs Adaptive)
  const handleToggleSignalMode = (junctionId, nextMode) => {
    fetch(`http://localhost:8000/api/junctions/${junctionId}/mode?mode=${nextMode}`, {
      method: 'PUT'
    })
      .then(res => res.json())
      .then(data => {
        setJunctions(prev => ({
          ...prev,
          [junctionId]: {
            ...prev[junctionId],
            signal_mode: data.signal_mode,
            current_phase: data.current_phase
          }
        }));
      })
      .catch(err => console.error("Error toggling junction mode:", err));
  };

  // 4. Action Handler: Resolve / Approve Civil Recommendations
  const handleApproveRecommendation = (recId, nextStatus) => {
    fetch(`http://localhost:8000/api/recommendations/${recId}/status?status=${nextStatus}`, {
      method: 'PUT'
    })
      .then(res => res.json())
      .then(data => {
        setRecommendations(prev => 
          prev.map(r => r.id === recId ? { ...r, status: data.status } : r)
        );
      })
      .catch(err => console.error("Error updating recommendation status:", err));
  };

  // 5. Action Handler: Download CSV or ReportLab PDF
  const handleDownloadReport = (format) => {
    if (format === 'pdf') {
      window.open('http://localhost:8000/api/reports/download/pdf', '_blank');
    } else {
      window.open('http://localhost:8000/api/reports/download/csv?type=violations', '_blank');
    }
  };

  const selectedJunction = junctions[selectedJunctionId] || {
    name: "Majura Gate Intersection",
    signal_mode: "fixed",
    current_phase: "Inactive"
  };

  return (
    <div className="flex bg-[#0b0f19] text-[#f8fafc] h-screen overflow-hidden">
      {/* Navigation Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        connected={connected}
        onDownloadReport={handleDownloadReport}
      />

      {/* Main Core Window */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header Bar */}
        <header className="h-16 border-b border-[#1e2d4a] bg-[#0e172a] px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="bg-[#3b82f6]/10 text-[#3b82f6] text-xs px-2.5 py-1 rounded font-bold uppercase tracking-wider font-mono border border-[#3b82f6]/20">
              Command Node 01
            </span>
            <h2 className="text-sm font-semibold text-slate-300">
              Surat City Traffic Analytics Engine
            </h2>
          </div>
          
          {/* Real-time stats ticker */}
          <div className="hidden lg:flex items-center gap-6 text-xs text-slate-400 font-mono">
            <div className="flex items-center gap-1.5">
              <Activity size={14} className="text-emerald-400" />
              <span>Camera feeds online: 12</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Cpu size={14} className="text-blue-400" />
              <span>Junction clusters: 3</span>
            </div>
          </div>
        </header>

        {/* Global KPIs Section */}
        <KPISection junctions={junctions} />

        {/* Tab-driven View Swapper */}
        <main className="flex-1 overflow-hidden p-4 pt-0">
          {activeTab === 'map' && (
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 h-full overflow-hidden pb-4">
              
              {/* Map & Chart Column (2/3 width) */}
              <div className="xl:col-span-2 flex flex-col gap-4 h-full overflow-hidden">
                {/* Live Geo Leaflet Overlay */}
                <div className="flex-1 min-h-[300px] bg-slate-900 border border-[#1e2d4a] rounded-xl overflow-hidden shadow-lg">
                  <JunctionMap 
                    junctions={junctions} 
                    selectedJunctionId={selectedJunctionId} 
                    onSelectJunction={setSelectedJunctionId}
                  />
                </div>
                
                {/* SUMO comparative chart (what-if toggle) */}
                <div className="h-[280px] min-h-[280px]">
                  <WhatIfToggle
                    selectedJunctionId={selectedJunctionId}
                    selectedJunctionName={selectedJunction.name}
                    currentMode={selectedJunction.signal_mode}
                    onToggleSignalMode={handleToggleSignalMode}
                  />
                </div>
              </div>

              {/* Sidebar Feeds Column (1/3 width) */}
              <div className="flex flex-col gap-4 h-full overflow-hidden">
                {/* Live signals controller display */}
                <div className="glass-card p-4 bg-slate-900 flex flex-col justify-center gap-1">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    Selected Node Phase Status
                  </div>
                  <div className="text-sm font-bold text-slate-100 mt-1 flex items-center justify-between">
                    <span>{selectedJunction.name}</span>
                    <span className="font-mono text-xs uppercase text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                      {selectedJunction.signal_mode}
                    </span>
                  </div>
                  <div className="mt-3 p-3 bg-slate-950 rounded-lg flex items-center gap-3 border border-slate-800">
                    <div className="flex flex-col items-center gap-1">
                      {/* Styled glowing physical traffic signal light indicator */}
                      <span className={`w-3.5 h-3.5 rounded-full ${selectedJunction.current_phase.includes('Green') || selectedJunction.current_phase.includes('Priority') ? 'bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse' : 'bg-emerald-950'} block`}></span>
                      <span className={`w-3.5 h-3.5 rounded-full ${selectedJunction.current_phase.includes('All Red') || selectedJunction.current_phase.includes('Inactive') ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-red-950'} block`}></span>
                    </div>
                    <div className="flex-1">
                      <span className="text-[10px] text-slate-500 font-bold tracking-wide uppercase">Active Phase</span>
                      <div className="text-xs font-bold text-emerald-400 font-mono mt-0.5">
                        {selectedJunction.current_phase}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Live scrolling violations list */}
                <div className="flex-1 overflow-hidden">
                  <AlertsPanel violations={violations} />
                </div>
              </div>

            </div>
          )}

          {activeTab === 'violations' && (
            <div className="h-full pb-4">
              <AlertsPanel violations={violations} />
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="h-full pb-4">
              <Recommendations 
                recommendations={recommendations} 
                onApproveRecommendation={handleApproveRecommendation}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
