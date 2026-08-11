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
        zoomControl: true,
        attributionControl: false,
      });

      const cartoDarkTile = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          maxZoom: 19,
          subdomains: "abcd",
        }
      );
      cartoDarkTile.addTo(map);

      mapInstanceRef.current = map;
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
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
              <span style="color:#8b949e; display:block; font-size:9px;">Congestion</span>
              <span style="color:#00f3ff; font-weight:bold;">${j.congestionIndex}%</span>
            </div>
            <div>
              <span style="color:#8b949e; display:block; font-size:9px;">Avg Wait</span>
              <span style="color:#f0f6fc; font-weight:bold;">${j.avgWait}s</span>
            </div>
          </div>
          <button id="btn-select-${j.id}" style="width:100%; background:#00f3ff22; border:1px solid #00f3ff; color:#00f3ff; font-size:11px; font-weight:600; padding:4px 0; cursor:pointer; text-transform:uppercase; border-radius:3px;">
            Open Junction Telemetry
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
    <div className="relative flex h-full flex-col overflow-hidden bg-panel border border-border">
      {/* Map Header Overlay Bar */}
      <div className="absolute top-3 left-3 right-3 z-[400] flex items-center justify-between pointer-events-none">
        {/* Left Side: Signal Filter Badges */}
        <div className="flex items-center gap-1.5 bg-panel/90 backdrop-blur-md border border-border px-2 py-1.5 shadow-xl pointer-events-auto">
          <Filter className="h-3.5 w-3.5 text-primary" />
          <span className="label-xs text-muted-foreground mr-1 hidden sm:inline">Filter Signals:</span>
          {(["all", "green", "red", "gridlock"] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setSignalFilter(filter)}
              className={`px-2 py-0.5 text-[10px] font-mono font-semibold uppercase tracking-wider transition-colors ${
                signalFilter === filter
                  ? "bg-primary text-primary-foreground"
                  : "bg-panel-raised text-muted-foreground hover:text-foreground border border-border"
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Right Side: Surat Corridor Layers Toggle Button */}
        <button
          onClick={() => setShowLanesPanel((prev) => !prev)}
          className="flex items-center gap-1.5 bg-panel/90 backdrop-blur-md border border-border px-3 py-1.5 text-xs font-semibold text-foreground hover:border-primary/50 shadow-xl pointer-events-auto transition-colors"
        >
          <Layers className="h-4 w-4 text-primary" />
          <span>Corridors ({activeLaneIds.length})</span>
        </button>
      </div>

      {/* Corridor Layers Dropdown Drawer */}
      {showLanesPanel && (
        <div className="absolute top-14 right-3 z-[400] w-64 bg-panel/95 backdrop-blur-md border border-border p-3 shadow-2xl space-y-2">
          <div className="flex items-center justify-between border-b border-border pb-1.5">
            <span className="label-xs text-primary font-bold">Surat Dedicated Corridors</span>
            <span className="text-[10px] text-muted-foreground font-mono">GIS Layers</span>
          </div>

          <div className="space-y-1.5 max-h-48 overflow-y-auto">
            {SURAT_LANES.map((lane) => {
              const active = activeLaneIds.includes(lane.id);
              return (
                <button
                  key={lane.id}
                  onClick={() => toggleLane(lane.id)}
                  className={`flex w-full items-center justify-between border px-2 py-1.5 text-left text-xs transition-colors ${
                    active
                      ? "border-primary/40 bg-primary/10 text-foreground"
                      : "border-border text-muted-foreground hover:bg-panel-raised"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className="h-2.5 w-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: lane.color }}
                    />
                    <span className="truncate text-[11px] font-medium">{lane.name}</span>
                  </div>
                  <Eye
                    className={`h-3.5 w-3.5 shrink-0 ${
                      active ? "text-primary" : "text-muted-foreground/40"
                    }`}
                  />
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Leaflet GIS Map Canvas */}
      <div ref={mapContainerRef} className="h-full w-full z-0 bg-[#07090e]" />
    </div>
  );
}
