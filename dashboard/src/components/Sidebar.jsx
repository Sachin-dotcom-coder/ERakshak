import React from 'react';
import { Map, AlertTriangle, Lightbulb, Wifi, WifiOff, FileDown, ShieldCheck } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, connected, onDownloadReport }) {
  const tabs = [
    { id: 'map', name: 'Command Overview', icon: Map },
    { id: 'violations', name: 'Violations Control', icon: AlertTriangle },
    { id: 'recommendations', name: 'Civil Infrastructure', icon: Lightbulb }
  ];

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="bg-blue-600/20 p-2 rounded-lg text-blue-400 border border-blue-500/20">
          <ShieldCheck size={24} />
        </div>
        <div>
          <h1 className="font-extrabold text-base tracking-wider text-slate-100 uppercase font-mono">
            E-Rakshak
          </h1>
          <p className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">
            Surat Traffic Control
          </p>
        </div>
      </div>

      {/* Connection HUD status */}
      <div className="px-5 py-3.5 border-b border-slate-800/60 bg-slate-950/20 flex items-center justify-between">
        <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
          Connection Status
        </span>
        <div className="flex items-center gap-1.5">
          <span className={`w-2.5 h-2.5 rounded-full ${connected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500'} block`}></span>
          <span className="text-[10px] font-mono font-bold text-slate-300">
            {connected ? 'WS LIVE' : 'WS OFF'}
          </span>
        </div>
      </div>

      {/* Navigation Tab Links */}
      <nav className="flex-1 px-3 py-4 space-y-1.5">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Icon size={16} />
              {tab.name}
            </button>
          );
        })}
      </nav>

      {/* Reports Export Area */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/30">
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2.5 px-1">
          Export Log Summaries
        </div>
        <div className="space-y-2">
          <button
            onClick={() => onDownloadReport('pdf')}
            className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
          >
            <FileDown size={14} /> PDF Operations Summary
          </button>
          <button
            onClick={() => onDownloadReport('csv')}
            className="w-full bg-slate-800/50 hover:bg-slate-700/60 text-slate-300 border border-dashed border-slate-800 py-1.5 rounded-lg text-[10px] font-semibold flex items-center justify-center gap-1.5 transition-colors"
          >
            <FileDown size={12} /> CSV Violations Data
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800 text-[10px] text-slate-600 font-mono text-center">
        © 2026 SURAT POLICE IT CELL
      </div>
    </div>
  );
}
