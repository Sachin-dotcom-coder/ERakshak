import { useEffect, useRef, useState } from "react";
import { Layers, Activity, Radio, Filter, Eye, Navigation } from "lucide-react";
import { SURAT_LANES } from "@/lib/mock-traffic";
import type { Junction } from "@/lib/traffic-types";

export function MapPanel({
  junctions,
  selectedId,
  onSelect,
}: {
  junctions: Junction[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const tileRef = useRef<any>(null);
  const mapInstanceRef = useRef<any>(null);
  const leafletRef = useRef<any>(null);
  const markersRef = useRef<{ [key: string]: any }>({});
  const polylinesRef = useRef<{ [key: string]: any[] }>({});

  const [activeLaneIds, setActiveLaneIds] = useState<string[]>([
    "LANE-BRTS",
    "LANE-RING",
    "LANE-EMERGENCY",
  ]);
  const [signalFilter, setSignalFilter] = useState<"all" | "red" | "green" | "gridlock">("all");
  const [showLanesPanel, setShowLanesPanel] = useState(false);

  // Filter junctions based on selected filter tag
  const filteredJunctions = junctions.filter((j) => {
    if (signalFilter === "red") return j.signalStatus === "RED";
    if (signalFilter === "green") return j.signalStatus === "GREEN";
    if (signalFilter === "gridlock") return j.congestionIndex > 75;
    return true;
  });

  // Initialize Map dynamically on client
  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current || mapInstanceRef.current) return;

    import("leaflet").then((L) => {
      leafletRef.current = L;
      if (mapInstanceRef.current) return;

      const map = L.map(mapContainerRef.current!, {
        center: [21.1850, 72.8300],
        zoom: 13,
        zoomControl: false,
        attributionControl: false,
      });

      // Add zoom control at bottom-right to prevent overlap with top toolbar
      L.control.zoom({ position: "bottomright" }).addTo(map);

      // Stadia Maps Alidade Smooth Dark — OSM-based, ideal for Surat
      const darkMapTile = L.tileLayer(
        "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
        {
          maxZoom: 20,
          attribution: '&copy; <a href="https://stadia.com">Stadia Maps</a>, &copy; OpenStreetMap contributors',
        }
      );
      darkMapTile.addTo(map);
      tileRef.current = darkMapTile;

      mapInstanceRef.current = map;

      // Force tile refresh once rendered
      setTimeout(() => {
        map.invalidateSize();
      }, 100);
      setTimeout(() => {
        map.invalidateSize();
      }, 400);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Continuously invalidate size if container or shell resizes
  useEffect(() => {
    if (!mapContainerRef.current) return;
    const observer = new ResizeObserver(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    });
    observer.observe(mapContainerRef.current);
    return () => observer.disconnect();
  }, []);

  // Update Junction Markers when state changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const L = leafletRef.current;
    if (!map || !L) return;

    // Clear old markers
    Object.values(markersRef.current).forEach((m) => m.remove());
    markersRef.current = {};

    filteredJunctions.forEach((j) => {
      const isSelected = selectedId === j.id;
      const statusClass =
        j.signalStatus === "GREEN"
          ? "green"
          : j.signalStatus === "YELLOW"
            ? "yellow"
            : "red";

      // Size marker by congestion severity
      const sz = isSelected ? 36 : j.congestionIndex > 75 ? 30 : j.congestionIndex > 45 ? 26 : 22;
      const showPulse = j.congestionIndex > 75;

      const customIcon = L.divIcon({
        className: "custom-leaflet-signal-marker",
        html: `
          <div class="signal-marker-container" style="width:${sz}px;height:${sz}px">
            ${showPulse ? `<div class="signal-pulse ${statusClass}" style="width:${sz + 8}px;height:${sz + 8}px;top:-4px;left:-4px"></div>` : ""}
            <div class="signal-beacon ${statusClass}" style="width:${sz}px;height:${sz}px;${isSelected ? "box-shadow:0 0 0 3px rgba(0,244,255,0.7),0 0 16px rgba(0,244,255,0.3)" : ""}">
              <span class="signal-badge" style="font-size:${sz > 26 ? 10 : 8}px">${j.signalCountdown}s</span>
            </div>
          </div>
        `,
        iconSize: [sz, sz],
        iconAnchor: [sz / 2, sz / 2],
      });


      const marker = L.marker([j.lat, j.lng], { icon: customIcon }).addTo(map);

      const sigColor = j.signalStatus === "GREEN" ? "#22d35a" : j.signalStatus === "YELLOW" ? "#f59e0b" : "#ef4444";
      const congColor = j.congestionIndex > 75 ? "#ef4444" : j.congestionIndex > 45 ? "#f59e0b" : "#22d35a";
      const popupHtml = `
        <div style="font-family:Inter,sans-serif;width:230px;padding:6px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span style="font-size:9px;font-weight:700;color:#71717a;text-transform:uppercase;letter-spacing:.1em">${j.zone}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 6px;border-radius:4px;font-weight:700;background:${sigColor}22;color:${sigColor};border:1px solid ${sigColor}60">${j.signalStatus} · ${j.signalCountdown}s</span>
          </div>
          <h4 style="margin:0 0 8px;font-size:13px;font-weight:700;color:#e4e4e7;line-height:1.2">${j.name}</h4>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:10px;background:#09090b;padding:8px;border-radius:6px;border:1px solid #1c1c22">
            <div style="text-align:center">
              <div style="font-size:8px;color:#71717a;text-transform:uppercase;letter-spacing:.08em;margin-bottom:2px">Congestion</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:${congColor}">${j.congestionIndex}</div>
            </div>
            <div style="text-align:center;border-left:1px solid #1c1c22;border-right:1px solid #1c1c22">
              <div style="font-size:8px;color:#71717a;text-transform:uppercase;letter-spacing:.08em;margin-bottom:2px">Avg Wait</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:#e4e4e7">${j.avgWait}s</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:8px;color:#71717a;text-transform:uppercase;letter-spacing:.08em;margin-bottom:2px">veh/hr</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;color:#e4e4e7">${(j.throughput/1000).toFixed(1)}k</div>
            </div>
          </div>
          ${j.onBrts ? '<div style="font-size:9px;color:#00f4ff;background:#00f4ff12;border:1px solid #00f4ff30;border-radius:4px;padding:2px 6px;display:inline-block;margin-bottom:8px;font-weight:700">✦ BRTS CORRIDOR</div>' : ''}
          <button id="btn-select-${j.id}" style="width:100%;background:#00f4ff18;border:1px solid #00f4ff50;color:#00f4ff;font-size:11px;font-weight:700;padding:5px 0;cursor:pointer;text-transform:uppercase;letter-spacing:.06em;border-radius:6px;transition:background .15s">
            Open Junction Telemetry →
          </button>
        </div>
      `;

      marker.bindPopup(popupHtml);
      marker.on("click", () => {
        onSelect(j.id);
      });

      marker.on("popupopen", () => {
        const btn = document.getElementById(`btn-select-${j.id}`);
        if (btn) {
          btn.onclick = () => onSelect(j.id);
        }
      });

      markersRef.current[j.id] = marker;
    });
  }, [filteredJunctions, selectedId, onSelect]);

  // Update Highlighted Polylines for Lanes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const L = leafletRef.current;
    if (!map || !L) return;

    Object.values(polylinesRef.current).forEach((lines) =>
      lines.forEach((line) => line.remove())
    );
    polylinesRef.current = {};

    SURAT_LANES.forEach((lane) => {
      if (!activeLaneIds.includes(lane.id)) return;

      const glowLine = L.polyline(lane.coordinates, {
        color: lane.color,
        weight: 9,
        opacity: 0.3,
        lineCap: "round",
        lineJoin: "round",
      }).addTo(map);

      const coreLine = L.polyline(lane.coordinates, {
        color: lane.color,
        weight: 3.5,
        opacity: 0.95,
        lineCap: "round",
        lineJoin: "round",
        dashArray: lane.type === "emergency" ? "6, 6" : undefined,
      }).addTo(map);

      coreLine.bindTooltip(`<b>${lane.name}</b><br/>${lane.description}`, {
        sticky: true,
      });

      polylinesRef.current[lane.id] = [glowLine, coreLine];
    });
  }, [activeLaneIds]);

  const toggleLane = (id: string) => {
    setActiveLaneIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  return (
    <div className="relative flex h-full w-full aspect-[4/3] flex-col overflow-hidden bg-panel border border-border rounded-2xl">
      {/* Map Header Overlay Bar */}
      <div className="absolute top-3 left-3 right-3 z-20 flex items-center justify-between pointer-events-none">
        {/* Left Side: Signal Filter Badges */}
        <div className="flex items-center gap-1.5 rounded-xl bg-zinc-950/85 backdrop-blur-md border border-zinc-800/80 px-2.5 py-1.5 shadow-2xl pointer-events-auto">
          <Filter className="h-3.5 w-3.5 text-zinc-400" />
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 mr-1 hidden sm:inline">
            Filter Signals:
          </span>
          {(["all", "green", "red", "gridlock"] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setSignalFilter(filter)}
              className={`rounded-lg px-2.5 py-1 text-[10px] font-mono font-semibold uppercase tracking-wider transition-all duration-150 active:scale-95 ${
                signalFilter === filter
                  ? "bg-white text-zinc-950 shadow-sm"
                  : "bg-zinc-900/60 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 border border-zinc-800/60"
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Right Side: Surat Corridor Layers Toggle Button */}
        <button
          onClick={() => setShowLanesPanel((prev) => !prev)}
          className="flex items-center gap-2 rounded-xl bg-zinc-950/85 backdrop-blur-md border border-zinc-800/80 px-3 py-1.5 text-xs font-semibold text-zinc-200 hover:text-white hover:border-zinc-700 shadow-2xl pointer-events-auto transition-all active:scale-95"
        >
          <Layers className="h-3.5 w-3.5 text-zinc-400" />
          <span>Corridors</span>
          <span className="text-[10px] font-mono font-bold bg-zinc-800/90 text-zinc-300 px-1.5 py-0.5 rounded-md border border-zinc-700/60">
            {activeLaneIds.length}
          </span>
        </button>
      </div>

      {/* Corridor Layers Dropdown Drawer */}
      {showLanesPanel && (
        <div className="absolute top-14 right-3 z-30 w-64 rounded-xl bg-zinc-950/95 backdrop-blur-md border border-zinc-800 p-3 shadow-2xl space-y-2.5 animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
            <span className="text-xs font-bold text-zinc-200">Surat Dedicated Corridors</span>
            <span className="text-[10px] text-zinc-500 font-mono">GIS Layers</span>
          </div>

          <div className="space-y-1.5 max-h-48 overflow-y-auto">
            {SURAT_LANES.map((lane) => {
              const active = activeLaneIds.includes(lane.id);
              return (
                <button
                  key={lane.id}
                  onClick={() => toggleLane(lane.id)}
                  className={`flex w-full items-center justify-between rounded-lg border px-2.5 py-2 text-left text-xs transition-all ${
                    active
                      ? "border-zinc-700 bg-zinc-800/60 text-white font-medium"
                      : "border-zinc-800/60 text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className="h-2.5 w-2.5 rounded-full shrink-0 shadow-sm"
                      style={{ backgroundColor: lane.color }}
                    />
                    <span className="truncate text-[11px]">{lane.name}</span>
                  </div>
                  <Eye
                    className={`h-3.5 w-3.5 shrink-0 transition-colors ${
                      active ? "text-white" : "text-zinc-600"
                    }`}
                  />
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Leaflet GIS Map Canvas */}
      <div ref={mapContainerRef} className="h-full w-full flex-1 min-h-0 z-0 bg-[#07090e]" />
    </div>
  );
}
