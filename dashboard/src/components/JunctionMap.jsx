import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Polygon } from 'react-leaflet';

export default function JunctionMap({ junctions, selectedJunctionId, onSelectJunction }) {
  // Center of Surat City (Majura Gate coordinates)
  const mapCenter = [21.1850, 72.8250];

  // Helper to color junction circles based on queue lengths
  const getJunctionColor = (j) => {
    const avgQueue = j.avg_queue_length_m || 0;
    if (j.brts_intrusion_count > 0) return '#ef4444'; // Red flash for intrusions
    if (avgQueue >= 65) return '#ef4444'; // Red for heavy congestion
    if (avgQueue >= 30) return '#f59e0b'; // Amber for moderate queue
    return '#10b981'; // Green for free flow
  };

  return (
    <div className="w-full h-full relative" style={{ minHeight: '350px' }}>
      <MapContainer 
        center={mapCenter} 
        zoom={14} 
        scrollWheelZoom={true} 
        style={{ width: '100%', height: '100%' }}
      >
        {/* Dark-themed Map Tiles for clean police command center dashboard */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Render Lanes Polygons */}
        {Object.values(junctions).map((junction) => (
          (junction.lanes || []).map((lane) => {
            if (!lane.polygon_coords) return null;
            
            // Choose colors
            let pathColor = '#475569'; // default slate gray for regular lanes
            let fillColor = '#334155';
            let opacity = 0.4;

            if (lane.is_brts) {
              pathColor = '#a855f7'; // Purple for BRTS corridor
              fillColor = '#a855f7';
              // Check if this specific lane has a high vehicle count (which is a violation)
              if (lane.vehicle_count > 0) {
                pathColor = '#ef4444'; // Flash red for intrusion
                fillColor = '#ef4444';
                opacity = 0.7;
              } else {
                opacity = 0.25;
              }
            } else {
              // Standard lane: highlight if queue length is heavy (> 70m)
              if (lane.queue_length_m > 70) {
                pathColor = '#f97316'; // Orange warning
                fillColor = '#f97316';
                opacity = 0.55;
              }
            }

            return (
              <Polygon
                key={lane.lane_id || lane.id}
                positions={lane.polygon_coords}
                pathOptions={{
                  color: pathColor,
                  fillColor: fillColor,
                  fillOpacity: opacity,
                  weight: 2
                }}
              >
                <Popup>
                  <div className="text-slate-900 font-sans">
                    <strong className="text-xs">{lane.lane_name}</strong>
                    <div className="grid grid-cols-2 gap-1 text-[10px] mt-1.5 font-mono">
                      <span>Queue Length:</span> <strong>{lane.queue_length_m} m</strong>
                      <span>Vehicle Count:</span> <strong>{lane.vehicle_count}</strong>
                      <span>Avg Speed:</span> <strong>{lane.average_speed_kmh} km/h</strong>
                    </div>
                  </div>
                </Popup>
              </Polygon>
            );
          })
        ))}

        {/* Render Junction Hotspots */}
        {Object.values(junctions).map((j) => (
          <CircleMarker
            key={j.junction_id}
            center={[j.latitude, j.longitude]}
            radius={j.junction_id === selectedJunctionId ? 14 : 10}
            pathOptions={{
              color: j.junction_id === selectedJunctionId ? '#ffffff' : getJunctionColor(j),
              fillColor: getJunctionColor(j),
              fillOpacity: 0.85,
              weight: j.junction_id === selectedJunctionId ? 3 : 1
            }}
            eventHandlers={{
              click: () => {
                onSelectJunction(j.junction_id);
              }
            }}
          >
            <Popup>
              <div className="text-slate-900 font-sans">
                <h4 className="font-bold text-sm leading-tight">{j.name}</h4>
                <p className="text-[10px] text-slate-500 uppercase font-semibold mt-0.5">
                  Controller Mode: {j.signal_mode.toUpperCase()}
                </p>
                <div className="border-t border-slate-200 mt-2 pt-1 text-[11px] grid grid-cols-2 gap-x-2 gap-y-1 font-mono">
                  <span>Phase Indicator:</span> <span className="font-bold text-slate-700">{j.current_phase}</span>
                  <span>Avg Queue:</span> <strong>{j.avg_queue_length_m} m</strong>
                  <span>Total Density:</span> <strong>{j.total_vehicles} vehicles</strong>
                  <span>Intrusions:</span> <strong className={j.brts_intrusion_count > 0 ? 'text-red-600' : ''}>{j.brts_intrusion_count}</strong>
                </div>
                <button
                  onClick={() => onSelectJunction(j.junction_id)}
                  className="w-full bg-slate-900 text-white font-semibold text-[10px] py-1 mt-3.5 rounded text-center block hover:bg-slate-800 transition-colors"
                >
                  Inspect Junction Analytics
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      
      {/* Legend Overlay on Map */}
      <div className="absolute bottom-4 left-4 bg-slate-950/90 border border-slate-800 p-2.5 rounded-lg z-[400] text-[10px] font-mono shadow-lg pointer-events-auto">
        <div className="font-bold text-slate-400 mb-1.5 uppercase tracking-wide">Infrastructure Legend</div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 block"></span>
            <span>Junction Clear (&lt;30m delay)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500 block"></span>
            <span>Moderate Queue (30m - 60m)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 block"></span>
            <span>Spillback / Alert (&gt;60m delay)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-5 h-2.5 border border-purple-500 bg-purple-500/25 block rounded-sm"></span>
            <span>Dedicated BRTS Bus Lane</span>
          </div>
        </div>
      </div>
    </div>
  );
}
