import { useEffect, useRef, useState } from "react";
import { Layers, Activity, Radio, Filter, Eye, Navigation, Siren, CheckCircle2, RotateCcw } from "lucide-react";
import { SURAT_LANES } from "@/lib/mock-traffic";
import type { Junction } from "@/lib/traffic-types";

// Emergency route from Top-Right (Kapodra) to Bottom-Left (Piplod)
const AMBULANCE_ROUTE = [
  { id: "JN-18", name: "Kapodra Junction", lat: 21.2270, lng: 72.8850 },
  { id: "JN-11", name: "Hirabaug Circle", lat: 21.2185, lng: 72.8710 },
  { id: "JN-05", name: "Varachha / Sardar Chowk", lat: 21.2150, lng: 72.8600 },
  { id: "JN-20", name: "Station Circle", lat: 21.2050, lng: 72.8410 },
  { id: "JN-02", name: "Ring Road / Delhi Gate", lat: 21.2005, lng: 72.8385 },
  { id: "JN-09", name: "Majura Gate Circle", lat: 21.1798, lng: 72.8188 },
  { id: "JN-07", name: "Athwalines / Athwa Gate", lat: 21.1834, lng: 72.8092 },
  { id: "JN-08", name: "Dumas Road / SVNIT Circle", lat: 21.1650, lng: 72.7840 },
  { id: "JN-04", name: "Piplod Junction", lat: 21.1550, lng: 72.7750 },
];

// Cross-traffic junctions held on RED to clear conflicting traffic
const CROSS_STREET_JUNCTIONS_TO_HOLD = ["JN-01", "JN-10", "JN-14", "JN-17", "JN-21"];

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

  // ── Ambulance Emergency Wave State ─────────────────────
  const [ambulanceActive, setAmbulanceActive] = useState(false);
  const [ambulanceProgress, setAmbulanceProgress] = useState(0); // 0 to AMBULANCE_ROUTE.length - 1
  const [ambulanceArrived, setAmbulanceArrived] = useState(false);
  const ambulanceMarkerRef = useRef<any>(null);
  const ambulancePathLinesRef = useRef<any[]>([]);
  const animFrameRef = useRef<any>(null);

  // Determine current preemption targets
  const currentWaypointIndex = Math.floor(ambulanceProgress);
  const upcomingJunction = AMBULANCE_ROUTE[Math.min(AMBULANCE_ROUTE.length - 1, currentWaypointIndex + 1)];
  const nextUpcomingJunction = AMBULANCE_ROUTE[Math.min(AMBULANCE_ROUTE.length - 1, currentWaypointIndex + 2)];

  // Apply dynamic AI green wave overrides to junctions
  const processedJunctions = junctions.map((j) => {
    if (!ambulanceActive) return j;

    const isUpcoming = (upcomingJunction && j.id === upcomingJunction.id) ||
                       (nextUpcomingJunction && j.id === nextUpcomingJunction.id);
    const isCrossHeld = CROSS_STREET_JUNCTIONS_TO_HOLD.includes(j.id);

    if (isUpcoming) {
      return {
        ...j,
        signalStatus: "GREEN" as const,
        signalCountdown: 60,
        isPreempted: true,
      } as Junction & { isPreempted?: boolean; isHeld?: boolean };
    }

    if (isCrossHeld) {
      return {
        ...j,
        signalStatus: "RED" as const,
        signalCountdown: 45,
        isHeld: true,
      } as Junction & { isPreempted?: boolean; isHeld?: boolean };
    }

    return j as Junction & { isPreempted?: boolean; isHeld?: boolean };
  });

  // Filter junctions based on selected filter tag
  const filteredJunctions = processedJunctions.filter((j) => {
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

  // ── Ambulance Simulation Loop ─────────────────────────────
  useEffect(() => {
    const map = mapInstanceRef.current;
    const L = leafletRef.current;
    if (!map || !L) return;

    if (!ambulanceActive) {
      // Clean up ambulance marker and path lines
      if (ambulanceMarkerRef.current) {
        ambulanceMarkerRef.current.remove();
        ambulanceMarkerRef.current = null;
      }
      ambulancePathLinesRef.current.forEach((line) => line.remove());
      ambulancePathLinesRef.current = [];
      setAmbulanceProgress(0);
      setAmbulanceArrived(false);
      if (animFrameRef.current) {
        clearInterval(animFrameRef.current);
        animFrameRef.current = null;
      }
      return;
    }

    // 1. Draw glowing emergency corridor path from Top-Right to Bottom-Left
    ambulancePathLinesRef.current.forEach((line) => line.remove());
    ambulancePathLinesRef.current = [];

    const routeLatLngs = AMBULANCE_ROUTE.map((w) => [w.lat, w.lng]);

    // Outer emergency pulse glow
    const glowPath = L.polyline(routeLatLngs, {
      color: "#22c55e",
      weight: 12,
      opacity: 0.35,
      lineCap: "round",
      lineJoin: "round",
    }).addTo(map);

    // Inner bright animated dashed emergency corridor
    const corePath = L.polyline(routeLatLngs, {
      color: "#4ade80",
      weight: 4,
      opacity: 0.95,
      dashArray: "8, 8",
      lineCap: "round",
      lineJoin: "round",
    }).addTo(map);

    ambulancePathLinesRef.current = [glowPath, corePath];

    // 2. Create the animated Ambulance Marker with Siren Pulse
    const startPoint = AMBULANCE_ROUTE[0];
    const ambulanceIcon = L.divIcon({
      className: "custom-leaflet-ambulance-marker",
      html: `
        <div style="position:relative;display:flex;align-items:center;justify-content:center;cursor:pointer;">
          <div style="position:absolute;width:44px;height:44px;border-radius:50%;background:rgba(239,68,68,0.35);animation:ts-pulse-ring 1.5s cubic-bezier(0.2,0.6,0.4,1) infinite;"></div>
          <div style="position:absolute;width:34px;height:34px;border-radius:50%;background:rgba(56,189,248,0.4);animation:ts-pulse-ring 1.5s cubic-bezier(0.2,0.6,0.4,1) infinite;animation-delay:0.75s;"></div>
          
          <div style="position:relative;width:36px;height:36px;border-radius:12px;background:#09090b;border:2px solid #ef4444;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(239,68,68,0.8),0 0 30px rgba(56,189,248,0.5);">
            <span style="font-size:18px;line-height:1;transform:scaleX(-1);">🚑</span>
          </div>

          <div style="position:absolute;top:-26px;white-space:nowrap;background:rgba(9,9,11,0.95);border:1px solid #ef4444;color:#fecaca;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;box-shadow:0 4px 12px rgba(0,0,0,0.8);letter-spacing:0.04em;display:flex;align-items:center;gap:4px;">
            <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#ef4444;animation:ts-blink 0.8s infinite;"></span>
            AMBULANCE 108 · GREEN WAVE
          </div>
        </div>
      `,
      iconSize: [44, 44],
      iconAnchor: [22, 22],
    });

    if (ambulanceMarkerRef.current) {
      ambulanceMarkerRef.current.remove();
    }
    const ambMarker = L.marker([startPoint.lat, startPoint.lng], {
      icon: ambulanceIcon,
      zIndexOffset: 1000,
    }).addTo(map);
    ambulanceMarkerRef.current = ambMarker;

    // Pan smoothly to focus the emergency corridor
    map.flyTo([21.1920, 72.8350], 13, { duration: 1 });

    // 3. Interpolation animation loop
    let currentP = 0;
    const maxP = AMBULANCE_ROUTE.length - 1;
    const stepDuration = 60; // ms per tick (~20s total traversal)
    const stepIncrement = 0.024;

    animFrameRef.current = setInterval(() => {
      currentP += stepIncrement;
      if (currentP >= maxP) {
        currentP = maxP;
        setAmbulanceProgress(maxP);
        setAmbulanceArrived(true);
        const lastPt = AMBULANCE_ROUTE[maxP];
        ambMarker.setLatLng([lastPt.lat, lastPt.lng]);
        clearInterval(animFrameRef.current);
        animFrameRef.current = null;
        return;
      }

      const idx = Math.floor(currentP);
      const frac = currentP - idx;
      const p1 = AMBULANCE_ROUTE[idx];
      const p2 = AMBULANCE_ROUTE[Math.min(maxP, idx + 1)];

      const currLat = p1.lat + frac * (p2.lat - p1.lat);
      const currLng = p1.lng + frac * (p2.lng - p1.lng);

      ambMarker.setLatLng([currLat, currLng]);
      setAmbulanceProgress(currentP);
    }, stepDuration);

    return () => {
      if (animFrameRef.current) {
        clearInterval(animFrameRef.current);
        animFrameRef.current = null;
      }
    };
  }, [ambulanceActive]);

  // Update Junction Markers when state changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const L = leafletRef.current;
    if (!map || !L) return;

    // Clear old markers
    Object.values(markersRef.current).forEach((m) => m.remove());
    markersRef.current = {};

    filteredJunctions.forEach((j: any) => {
      const isSelected = selectedId === j.id;
      const isPreempted = !!j.isPreempted;
      const isHeld = !!j.isHeld;

      const statusClass =
        j.signalStatus === "GREEN"
          ? "green"
          : j.signalStatus === "YELLOW"
            ? "yellow"
            : "red";

      // Size marker by congestion severity
      const sz = isSelected ? 36 : j.congestionIndex > 75 ? 30 : j.congestionIndex > 45 ? 26 : 22;
      const showPulse = j.congestionIndex > 75 || isPreempted;

      const customIcon = L.divIcon({
        className: "custom-leaflet-signal-marker",
        html: `
          <div class="signal-marker-container" style="width:${sz}px;height:${sz}px">
            ${isPreempted ? `
              <div class="signal-pulse green" style="width:${sz + 16}px;height:${sz + 16}px;top:-8px;left:-8px;background:rgba(34,211,90,0.45);border:2px solid #22d35a;box-shadow:0 0 24px #22d35a;"></div>
            ` : showPulse ? `
              <div class="signal-pulse ${statusClass}" style="width:${sz + 8}px;height:${sz + 8}px;top:-4px;left:-4px"></div>
            ` : ""}
            <div class="signal-beacon ${statusClass}" style="width:${sz}px;height:${sz}px;${isSelected ? "box-shadow:0 0 0 3px rgba(0,244,255,0.7),0 0 16px rgba(0,244,255,0.3)" : ""}${isPreempted ? ";border:2px solid #22d35a;box-shadow:0 0 16px #22d35a" : ""}">
              <span class="signal-badge" style="font-size:${sz > 26 ? 10 : 8}px;${isPreempted ? "color:#22d35a;font-weight:900" : isHeld ? "color:#ef4444;font-weight:900" : ""}">
                ${isPreempted ? "🟢 WAVE" : isHeld ? "HOLD" : `${j.signalCountdown}s`}
              </span>
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
        <div style="font-family:Inter,sans-serif;width:240px;padding:6px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <span style="font-size:9px;font-weight:700;color:#71717a;text-transform:uppercase;letter-spacing:.1em">${j.zone}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:2px 6px;border-radius:4px;font-weight:700;background:${sigColor}22;color:${sigColor};border:1px solid ${sigColor}60">
              ${isPreempted ? "🚨 AI GREEN WAVE" : isHeld ? "⛔ CROSS TRAFFIC HELD" : `${j.signalStatus} · ${j.signalCountdown}s`}
            </span>
          </div>
          <h4 style="margin:0 0 8px;font-size:13px;font-weight:700;color:#e4e4e7;line-height:1.2">${j.name}</h4>
          ${isPreempted ? '<div style="font-size:10px;color:#22d35a;background:#22d35a15;border:1px solid #22d35a40;border-radius:6px;padding:4px 8px;margin-bottom:8px;font-weight:600">🚨 PREEMPTION ACTIVE: Signal locked GREEN for approaching Ambulance #108.</div>' : ''}
          ${isHeld ? '<div style="font-size:10px;color:#ef4444;background:#ef444415;border:1px solid #ef444440;border-radius:6px;padding:4px 8px;margin-bottom:8px;font-weight:600">⛔ CROSS-STREET HOLD: Signal locked RED to clear conflicting lanes.</div>' : ''}
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

  const toggleAmbulanceDemo = () => {
    setAmbulanceActive((prev) => !prev);
  };

  const resetAmbulanceDemo = () => {
    setAmbulanceActive(false);
    setTimeout(() => {
      setAmbulanceActive(true);
    }, 150);
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

        {/* Right Side: Ambulance Demo & Surat Corridor Layers */}
        <div className="flex items-center gap-2 pointer-events-auto">
          {/* Ambulance Emergency Wave Button */}
          <button
            onClick={toggleAmbulanceDemo}
            className={`flex items-center gap-1.5 rounded-xl backdrop-blur-md px-3 py-1.5 text-xs font-semibold shadow-2xl transition-all active:scale-95 border ${
              ambulanceActive
                ? "bg-red-950/90 border-red-500 text-red-200 shadow-[0_0_20px_rgba(239,68,68,0.4)] animate-pulse"
                : "bg-zinc-950/85 border-red-500/40 text-red-300 hover:text-white hover:bg-red-500/15 hover:border-red-400"
            }`}
            title="Demonstrate AI Emergency Green Wave Signal Preemption"
          >
            <span className="text-sm">🚑</span>
            <span className="hidden sm:inline font-mono uppercase tracking-wider text-[11px]">
              {ambulanceActive ? "Priority Active" : "Ambulance Demo"}
            </span>
            {ambulanceActive && (
              <span className="h-2 w-2 rounded-full bg-red-500 animate-ping" />
            )}
          </button>

          {/* Corridors Button */}
          <button
            onClick={() => setShowLanesPanel((prev) => !prev)}
            className="flex items-center gap-2 rounded-xl bg-zinc-950/85 backdrop-blur-md border border-zinc-800/80 px-3 py-1.5 text-xs font-semibold text-zinc-200 hover:text-white hover:border-zinc-700 shadow-2xl transition-all active:scale-95"
          >
            <Layers className="h-3.5 w-3.5 text-zinc-400" />
            <span>Corridors</span>
            <span className="text-[10px] font-mono font-bold bg-zinc-800/90 text-zinc-300 px-1.5 py-0.5 rounded-md border border-zinc-700/60">
              {activeLaneIds.length}
            </span>
          </button>
        </div>
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

      {/* ── Active Ambulance Emergency HUD Overlay ─────────── */}
      {ambulanceActive && (
        <div className="absolute bottom-5 left-3 right-3 sm:right-auto sm:w-96 z-20 rounded-2xl bg-zinc-950/95 backdrop-blur-xl border border-red-500/50 p-3.5 shadow-[0_8px_32px_rgba(0,0,0,0.8),0_0_24px_rgba(239,68,68,0.25)] flex flex-col gap-2.5 animate-in slide-in-from-bottom-4 duration-200 pointer-events-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
              </span>
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-red-400 font-mono flex items-center gap-1.5">
                AI GREEN WAVE PREEMPTION
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              {ambulanceArrived && (
                <button
                  onClick={resetAmbulanceDemo}
                  className="flex items-center gap-1 text-[10px] font-mono uppercase bg-ok/20 hover:bg-ok/30 text-ok px-2 py-0.5 rounded border border-ok/40 transition-colors"
                >
                  <RotateCcw className="h-3 w-3" /> Replay
                </button>
              )}
              <button
                onClick={() => setAmbulanceActive(false)}
                className="text-[10px] font-mono uppercase bg-red-500/20 hover:bg-red-500/30 text-red-300 px-2 py-0.5 rounded border border-red-500/40 transition-colors"
              >
                Close
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs bg-zinc-900/80 p-2 rounded-xl border border-zinc-800/80 font-mono">
            <div className="flex flex-col">
              <span className="text-[9px] text-zinc-400 uppercase">Emergency Path</span>
              <span className="font-bold text-zinc-200 text-[11px] truncate">
                Kapodra (Top-Right) ➔ Piplod (Bottom-Left)
              </span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-[9px] text-zinc-400 uppercase">Dispatch Status</span>
              <span className={`font-bold text-[11px] flex items-center gap-1 ${ambulanceArrived ? "text-ok" : "text-amber-400"}`}>
                {ambulanceArrived ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Siren className="h-3.5 w-3.5 animate-bounce text-red-400" />}
                {ambulanceArrived ? "REACHED SAFELY" : "CLEARING ROUTE"}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-zinc-300 px-0.5">
            <span className="text-ok font-bold flex items-center gap-1 truncate max-w-[210px]">
              <span>🟢</span> Next: {upcomingJunction ? upcomingJunction.name : "Destination Reached"}
            </span>
            <span className="text-zinc-400 shrink-0">
              ⏱️ 4.8m saved via AI
            </span>
          </div>

          {/* Emergency progress indicator */}
          <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-red-500 via-amber-400 to-emerald-400 h-full transition-all duration-150"
              style={{ width: `${(ambulanceProgress / (AMBULANCE_ROUTE.length - 1)) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Leaflet GIS Map Canvas */}
      <div ref={mapContainerRef} className="h-full w-full flex-1 min-h-0 z-0 bg-[#07090e]" />
    </div>
  );
}
