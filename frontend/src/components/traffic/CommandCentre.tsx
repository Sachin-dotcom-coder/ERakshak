import { useState, useRef, useEffect } from "react";
import { FileDown } from "lucide-react";
import { AppShell } from "./AppShell";
import { TopStatusBar } from "./TopStatusBar";
import { MapPanel } from "./MapPanel";
import { KPIPanel } from "./KPIPanel";
import { JunctionDrawer } from "./JunctionDrawer";
import { AlertsFeed } from "./AlertsFeed";
import { ExportModal } from "./ExportModal";
import { useTrafficData } from "@/hooks/useTrafficData";

export function CommandCentre() {
  const { junctions, kpis, queue, alerts, predictions, stats, connected, getJunction } =
    useTrafficData();
  const [selected, setSelected] = useState<string | null>(null);
  const [exportOpen, setExportOpen] = useState(false);

  // Synchronize KPI sidebar height to square map so left space is never wasted
  const [mapHeight, setMapHeight] = useState<number | null>(null);
  const mapColRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapColRef.current) return;
    const ro = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.height > 0) {
          setMapHeight(Math.round(entry.contentRect.height));
        }
      }
    });
    ro.observe(mapColRef.current);
    return () => ro.disconnect();
  }, []);

  return (
    <AppShell>
      <TopStatusBar
        junctionsOnline={stats.junctionsOnline}
        intrusions={stats.activeIntrusions}
        avgCongestion={stats.avgCongestion}
        connected={connected}
        right={
          <button
            onClick={() => setExportOpen(true)}
            className="num flex items-center gap-1.5 border border-primary/50 bg-primary/15 px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary rounded-md transition-colors hover:bg-primary/25"
          >
            <FileDown className="h-3.5 w-3.5" />
            Export
          </button>
        }
      />

      {/* Main layout */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 flex flex-col gap-3">

        <div className="grid gap-3 xl:grid-cols-[minmax(0,2.2fr)_minmax(0,1fr)] items-start">
          {/* Map — slightly smaller in length (4:3) keeping same width */}
          <div ref={mapColRef} className="w-full aspect-[4/3]">
            <MapPanel junctions={junctions} selectedId={selected} onSelect={setSelected} />
          </div>

          {/* KPI + charts scrollable sidebar matching square map height */}
          <div
            className="overflow-y-auto pr-1"
            style={{
              height: mapHeight ? `${mapHeight}px` : undefined,
              maxHeight: mapHeight ? `${mapHeight}px` : undefined,
            }}
          >
            <KPIPanel kpis={kpis} queue={queue} />
          </div>
        </div>

        {/* Alerts feed */}
        <div className="shrink-0">
          <AlertsFeed alerts={alerts} predictions={predictions} onSelectJunction={setSelected} />
        </div>
      </div>

      <JunctionDrawer junction={getJunction(selected)} onClose={() => setSelected(null)} />
      <ExportModal open={exportOpen} onClose={() => setExportOpen(false)} />
    </AppShell>
  );
}
