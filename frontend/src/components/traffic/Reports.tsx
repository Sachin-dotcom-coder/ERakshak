import { useState } from "react";
import { FileDown } from "lucide-react";
import { AppShell } from "./AppShell";
import { TopStatusBar } from "./TopStatusBar";
import { ExportModal } from "./ExportModal";
import { useTrafficData } from "@/hooks/useTrafficData";
import { CONGESTION_COLOR } from "@/lib/mock-traffic";

export function Reports() {
  const { junctions, stats, connected } = useTrafficData();
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

      <div className="p-3">
        <section className="panel-surface">
          <div className="border-b border-border px-3 py-2">
            <div className="label-xs">Shift summary · adaptive vs fixed timing</div>
            <h1 className="text-sm font-semibold">Junction Performance Report</h1>
          </div>
          <div className="overflow-x-auto">
            <table className="num w-full min-w-[720px] text-left text-[11px]">
              <thead className="label-xs border-b border-border">
                <tr>
                  <th className="px-3 py-2 font-medium">Junction</th>
                  <th className="px-3 py-2 font-medium">Zone</th>
                  <th className="px-3 py-2 font-medium">Congestion</th>
                  <th className="px-3 py-2 font-medium">Avg wait</th>
                  <th className="px-3 py-2 font-medium">Throughput</th>
                  <th className="px-3 py-2 font-medium">BRTS</th>
                  <th className="px-3 py-2 font-medium">If fixed timing</th>
                </tr>
              </thead>
              <tbody>
                {junctions.map((j) => (
                  <tr key={j.id} className="border-b border-border/50 hover:bg-panel-raised">
                    <td className="px-3 py-2 font-semibold">{j.name}</td>
                    <td className="px-3 py-2 text-muted-foreground">{j.zone}</td>
                    <td className="px-3 py-2">
                      <span className="flex items-center gap-1.5">
                        <span
                          className="h-2 w-2 rounded-full"
                          style={{ backgroundColor: CONGESTION_COLOR[j.congestion] }}
                        />
                        {j.congestionIndex}
                      </span>
                    </td>
                    <td className="px-3 py-2">{j.avgWait}s</td>
                    <td className="px-3 py-2">{j.throughput.toLocaleString("en-IN")} veh/h</td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {j.onBrts ? "corridor" : "—"}
                    </td>
                    <td className="px-3 py-2 text-crit">+{j.whatIfDelta}% congestion</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <ExportModal open={exportOpen} onClose={() => setExportOpen(false)} />
    </AppShell>
  );
}
