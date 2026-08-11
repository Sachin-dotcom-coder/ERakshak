import { useState } from "react";
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
            className="num flex items-center gap-1.5 border border-primary/50 bg-primary/15 px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary transition-colors hover:bg-primary/25"
          >
            <FileDown className="h-3.5 w-3.5" />
            Export Report
          </button>
        }
      />

      <div className="space-y-3 p-3">
        <div className="grid gap-3 xl:grid-cols-[minmax(0,2.1fr)_minmax(0,1fr)]">
          <MapPanel junctions={junctions} selectedId={selected} onSelect={setSelected} />
          <KPIPanel kpis={kpis} queue={queue} />
        </div>

        <AlertsFeed
          alerts={alerts}
          predictions={predictions}
          onSelectJunction={setSelected}
        />
      </div>

      <JunctionDrawer junction={getJunction(selected)} onClose={() => setSelected(null)} />
      <ExportModal open={exportOpen} onClose={() => setExportOpen(false)} />
    </AppShell>
  );
}
