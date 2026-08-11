import { useEffect, useRef, useState } from "react";
import L from "leaflet";
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
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<{ [key: string]: L.Marker }>({});
  const polylinesRef = useRef<{ [key: string]: L.Polyline[] }>({});

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
    if (signalFilter === "gridlock") return j.congestionIndex >= 70;
    return true;
  });

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Center over Surat Metropolitan City Center
    const map = L.map(mapContainerRef.current, {
      center: [21.1850, 72.8300],
      zoom: 13,
      zoomControl: true,
      attributionControl: false,
    });

    // Dark Map Tile Layer (CartoDB Dark Matter with OSM Fallback)
    const cartoDarkTile = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        maxZoom: 19,
        subdomains: "abcd",
      }
    );
    cartoDarkTile.addTo(map);

    mapInstanceRef.current = map;

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update Markers for Traffic Signals
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old markers
    Object.values(markersRef.current).forEach((marker) => marker.remove());
    markersRef.current = {};

    filteredJunctions.forEach((j) => {
      const isSelected = selectedId === j.id;
      const statusClass =
        j.signalStatus === "GREEN"
          ? "green"
          : j.signalStatus === "YELLOW"
            ? "yellow"
            : "red";

      // Custom high-tech dark signal beacon icon
      const customIcon = L.divIcon({
        className: "custom-leaflet-signal-marker",
        html: `
          <div class="signal-marker-container ${isSelected ? "scale-125" : ""}">
            <div class="signal-pulse ${statusClass}"></div>
            <div class="signal-beacon ${statusClass}">
              <span class="signal-badge">${j.signalCountdown}s</span>
            </div>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      const marker = L.marker([j.lat, j.lng], { icon: customIcon }).addTo(map);

      // Interactive Popup Content
      const popupHtml = `
        <div style="font-family: var(--font-sans); width: 220px; padding: 4px;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 6px;">
            <span style="font-size: 11px; font-weight: 700; color: #00f3ff; text-transform: uppercase; letter-spacing: 0.05em;">
              ${j.zone}
            </span>
            <span style="font-family: var(--font-mono); font-size: 10px; padding: 2px 6px; border-radius: 3px; font-weight: bold; background: ${
              j.signalStatus === "GREEN"
                ? "#00ff8822"
                : j.signalStatus === "YELLOW"
                  ? "#ffcc0022"
                  : "#ff336622"
            }; color: ${
              j.signalStatus === "GREEN"
                ? "#00ff88"
                : j.signalStatus === "YELLOW"
                  ? "#ffcc00"
                  : "#ff3366"
            }; border: 1px solid ${
              j.signalStatus === "GREEN"
                ? "#00ff88"
                : j.signalStatus === "YELLOW"
                  ? "#ffcc00"
                  : "#ff3366"
            }">
              SIGNAL: ${j.signalStatus} (${j.signalCountdown}s)
            </span>
          </div>
          <h4 style="margin: 0 0 6px 0; font-size: 13px; font-weight: 700; color: #f0f6fc;">
            ${j.name}
          </h4>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px; margin-bottom: 8px; background: #050608; padding: 6px; border-radius: 4px; border: 1px solid #1a2233;">
            <div>
              <span style="color: #7d8f9f; display: block; font-size: 9px; uppercase">Congestion</span>
              <strong style="color: ${j.congestionIndex > 70 ? "#ff3366" : j.congestionIndex > 45 ? "#ffcc00" : "#00ff88"}; font-family: var(--font-mono); font-size: 12px;">
                ${j.congestionIndex}%
              </strong>
            </div>
            <div>
              <span style="color: #7d8f9f; display: block; font-size: 9px; uppercase">Avg Wait</span>
              <strong style="color: #00f3ff; font-family: var(--font-mono); font-size: 12px;">
                ${j.avgWait}s
              </strong>
            </div>
          </div>
          <button id="btn-select-${j.id}" style="width: 100%; background: #00f3ff; color: #040810; font-weight: 700; font-size: 11px; padding: 6px; border: none; border-radius: 3px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em;">
            Open Signal Telemetry →
          </button>
        </div>
      `;

      marker.bindPopup(popupHtml);

      marker.on("popupopen", () => {
        const btn = document.getElementById(`btn-select-${j.id}`);
        if (btn) {
          btn.onclick = () => {
            onSelect(j.id);
          };
        }
      });

      marker.on("click", () => {
        onSelect(j.id);
      });

      markersRef.current[j.id] = marker;
    });
  }, [filteredJunctions, selectedId, onSelect]);

  // Center map on selected junction
  useEffect(() => {
    if (!selectedId || !mapInstanceRef.current) return;
    const junction = junctions.find((j) => j.id === selectedId);
    if (junction) {
      mapInstanceRef.current.flyTo([junction.lat, junction.lng], 15, {
        duration: 1.2,
      });
    }
  }, [selectedId, junctions]);

  // Update Highlighted Polylines for Lanes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear old polylines
    Object.values(polylinesRef.current).forEach((lines) =>
      lines.forEach((line) => line.remove())
    );
    polylinesRef.current = {};

    SURAT_LANES.forEach((lane) => {
      if (!activeLaneIds.includes(lane.id)) return;

      // Glow backdrop polyline
      const glowLine = L.polyline(lane.coordinates, {
        color: lane.color,
        weight: 9,
        opacity: 0.3,
        lineCap: "round",
        lineJoin: "round",
      }).addTo(map);

      // Core sharp neon polyline
      const coreLine = L.polyline(lane.coordinates, {
        color: lane.color,
        weight: 3.5,
        opacity: 0.95,
        lineCap: "round",
        lineJoin: "round",
        dashArray: lane.type === "emergency" ? "6, 6" : undefined,
      }).addTo(map);

      coreLine.bindTooltip(
        `<div style="font-family: var(--font-sans); padding: 2px 4px;">
          <strong style="color:${lane.color};">${lane.name}</strong><br/>
          <span style="font-size:10px; color:#7d8f9f;">Active Vehicles: ${lane.activeVehicles} | Avg Speed: ${lane.avgSpeedKmh} km/h</span>
        </div>`,
        { sticky: true, opacity: 0.9 }
      );

      polylinesRef.current[lane.id] = [glowLine, coreLine];
    });
  }, [activeLaneIds]);

  const toggleLane = (laneId: string) => {
    setActiveLaneIds((prev) =>
      prev.includes(laneId) ? prev.filter((id) => id !== laneId) : [...prev, laneId]
    );
  };

  return (
    <section className="panel-surface relative flex min-h-[520px] flex-col overflow-hidden border border-border bg-[#050608]">
      {/* Top Map Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/80 bg-[#0a0d14] px-3 py-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <div className="label-xs text-primary">Surat OpenStreetMap · Live Signals Grid</div>
          </div>
          <h2 className="truncate text-sm font-bold text-foreground">
            Surat Metropolitan Command Center ({junctions.length} Traffic Signals)
          </h2>
        </div>

        {/* Signal Filters */}
        <div className="flex flex-wrap items-center gap-1.5">
          <FilterBtn
            active={signalFilter === "all"}
            onClick={() => setSignalFilter("all")}
            label={`All (${junctions.length})`}
          />
          <FilterBtn
            active={signalFilter === "red"}
            onClick={() => setSignalFilter("red")}
            label={`Red (${junctions.filter((j) => j.signalStatus === "RED").length})`}
            color="text-red-400 border-red-500/30"
          />
          <FilterBtn
            active={signalFilter === "green"}
            onClick={() => setSignalFilter("green")}
            label={`Green (${junctions.filter((j) => j.signalStatus === "GREEN").length})`}
            color="text-emerald-400 border-emerald-500/30"
          />
          <FilterBtn
            active={signalFilter === "gridlock"}
            onClick={() => setSignalFilter("gridlock")}
            label={`Congested (${junctions.filter((j) => j.congestionIndex >= 70).length})`}
            color="text-amber-400 border-amber-500/30"
          />

          <button
            onClick={() => setShowLanesPanel((v) => !v)}
            className={`flex items-center gap-1.5 border px-2.5 py-1 text-[11px] font-semibold transition-all ${
              showLanesPanel
                ? "border-primary bg-primary/20 text-primary shadow-[0_0_12px_rgba(0,243,255,0.2)]"
                : "border-border bg-[#0f141f] text-muted-foreground hover:text-foreground"
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            Highlighted Lanes ({activeLaneIds.length})
          </button>
        </div>
      </div>

      {/* Highlighted Lanes Selector Drawer Overlay */}
      {showLanesPanel && (
        <div className="absolute top-[48px] right-3 z-[1000] w-80 border border-border bg-[#0a0d14]/95 p-3 shadow-2xl backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-border/60 pb-2 mb-2">
            <span className="label-xs text-primary flex items-center gap-1.5">
              <Navigation className="h-3.5 w-3.5" />
              Surat Highlighted Lane Corridors
            </span>
            <button
              onClick={() => setShowLanesPanel(false)}
              className="text-[10px] text-muted-foreground hover:text-foreground"
            >
              Close ✕
            </button>
          </div>
          <div className="space-y-2 max-h-[260px] overflow-y-auto pr-1">
            {SURAT_LANES.map((lane) => {
              const active = activeLaneIds.includes(lane.id);
              return (
                <div
                  key={lane.id}
                  onClick={() => toggleLane(lane.id)}
                  className={`group flex cursor-pointer items-start gap-2.5 rounded border p-2 text-xs transition-all ${
                    active
                      ? "border-border bg-[#0f141f]"
                      : "border-border/40 bg-[#050608]/60 opacity-60 hover:opacity-100"
                  }`}
                >
                  <span
                    className="mt-1 h-3 w-3 shrink-0 rounded-full border border-white/40"
                    style={{
                      backgroundColor: lane.color,
                      boxShadow: active ? `0 0 10px ${lane.color}` : "none",
                    }}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground truncate">
                        {lane.name}
                      </span>
                      <Eye
                        className={`h-3.5 w-3.5 ${
                          active ? "text-primary" : "text-muted-foreground"
                        }`}
                      />
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-1 mt-0.5">
                      {lane.description}
                    </p>
                    <div className="mt-1 flex items-center gap-3 num text-[10px] text-muted-foreground">
                      <span>Flow: <strong className="text-foreground">{lane.activeVehicles} veh</strong></span>
                      <span>Speed: <strong className="text-emerald-400">{lane.avgSpeedKmh} km/h</strong></span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main OpenStreetMap Container */}
      <div className="relative flex-1 min-h-[460px] w-full">
        <div ref={mapContainerRef} className="absolute inset-0 h-full w-full z-[1]" />

        {/* Floating Map Legend */}
        <div className="absolute bottom-3 left-3 z-[1000] flex flex-wrap items-center gap-3 border border-border/80 bg-[#0a0d14]/90 px-3 py-1.5 backdrop-blur shadow-lg text-[10px]">
          <span className="flex items-center gap-1.5 text-muted-foreground font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-[#00ff88] shadow-[0_0_8px_#00ff88]" />
            Green Phase
          </span>
          <span className="flex items-center gap-1.5 text-muted-foreground font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ffcc00] shadow-[0_0_8px_#ffcc00]" />
            Yellow Amber
          </span>
          <span className="flex items-center gap-1.5 text-muted-foreground font-medium">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff3366] shadow-[0_0_8px_#ff3366]" />
            Red Stop Phase
          </span>
          <span className="border-l border-border pl-3 flex items-center gap-1.5 text-primary font-medium">
            <Activity className="h-3 w-3" /> 22 Signals Monitored
          </span>
        </div>
      </div>
    </section>
  );
}

function FilterBtn({
  active,
  onClick,
  label,
  color,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  color?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`border px-2 py-0.5 text-[11px] font-semibold transition-colors ${
        active
          ? "border-primary bg-primary/20 text-primary"
          : color
            ? `bg-[#0f141f] ${color} hover:bg-[#131a26]`
            : "border-border bg-[#0f141f] text-muted-foreground hover:text-foreground"
      }`}
    >
      {label}
    </button>
  );
}
