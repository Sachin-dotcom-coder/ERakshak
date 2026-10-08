import { useState } from "react";
import { Download, FileText, FileSpreadsheet, FileJson, X, Check, Loader } from "lucide-react";

const BASE = "http://localhost:8000";

const FORMATS = [
  {
    id: "pdf",
    label: "PDF Report",
    desc: "Signed operational briefing — junctions, signals, BRTS log",
    icon: FileText,
    endpoint: BASE + "/api/reports/download/pdf",
    mimeType: "application/pdf",
    filename: "erakshak_report.pdf",
  },
  {
    id: "violations_csv",
    label: "Violations CSV",
    desc: "Full BRTS + lane violation log with timestamps",
    icon: FileSpreadsheet,
    endpoint: BASE + "/api/reports/download/csv",
    mimeType: "text/csv",
    filename: "erakshak_violations.csv",
  },
  {
    id: "metrics_csv",
    label: "Metrics CSV",
    desc: "Junction KPIs — throughput, wait time, congestion index",
    icon: FileSpreadsheet,
    endpoint: BASE + "/api/junctions",
    mimeType: "text/csv",
    filename: "erakshak_metrics.csv",
  },
  {
    id: "json",
    label: "Raw JSON",
    desc: "Full telemetry snapshot for downstream analysis",
    icon: FileJson,
    endpoint: BASE + "/api/junctions",
    mimeType: "application/json",
    filename: "erakshak_telemetry.json",
  },
] as const;

type FormatId = (typeof FORMATS)[number]["id"];
type Status = "idle" | "loading" | "done" | "error";

export function ExportModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [format, setFormat] = useState<FormatId>("pdf");
  const [from, setFrom] = useState("2026-10-01");
  const [to, setTo] = useState(new Date().toISOString().slice(0, 10));
  const [status, setStatus] = useState<Status>("idle");
  const [progress, setProgress] = useState(0);

  if (!open) return null;

  const selected = FORMATS.find((f) => f.id === format)!;

  async function handleExport() {
    setStatus("loading");
    setProgress(0);

    // Animate progress bar
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 85) { clearInterval(interval); return p; }
        return p + Math.random() * 18;
      });
    }, 220);

    try {
      const res = await fetch(selected.endpoint);
      if (!res.ok) throw new Error("Export failed: " + res.status);

      clearInterval(interval);
      setProgress(100);

      const blob = await res.blob();

      if (format === "metrics_csv") {
        // Convert junction JSON to CSV client-side
        const json = JSON.parse(await blob.text());
        const rows = Array.isArray(json) ? json : [];
        const csv = [
          "Junction,Zone,Congestion,Avg Wait (s),Throughput (veh/h),On BRTS",
          ...rows.map((j: any) =>
            [j.name, j.zone, j.congestion_index ?? "", j.avg_wait ?? "", j.throughput ?? "", j.on_brts ? "Yes" : "No"].join(",")
          ),
        ].join("\n");
        downloadBlob(new Blob([csv], { type: "text/csv" }), selected.filename);
      } else if (format === "json") {
        const json = JSON.parse(await blob.text());
        downloadBlob(new Blob([JSON.stringify(json, null, 2)], { type: "application/json" }), selected.filename);
      } else {
        downloadBlob(blob, selected.filename);
      }

      setStatus("done");
      setTimeout(() => {
        setStatus("idle");
        setProgress(0);
        onClose();
      }, 1400);
    } catch (err) {
      clearInterval(interval);
      console.error("Export error:", err);
      setStatus("error");
      setProgress(0);
      setTimeout(() => setStatus("idle"), 2500);
    }
  }

  function downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="fixed inset-0 z-[9999] grid place-items-center bg-background/85 p-4 backdrop-blur-md">
      <div className="w-full max-w-md border border-border bg-panel rounded-xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <div>
            <div className="label-xs">E-Rakshak Control Room</div>
            <h2 className="text-sm font-bold">Export Report</h2>
          </div>
          <button onClick={onClose}
            className="grid h-7 w-7 place-items-center border border-border rounded-lg text-muted-foreground hover:text-foreground transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-4 p-4">

          {/* Format selection */}
          <div>
            <div className="label-xs mb-2">Export Format</div>
            <div className="space-y-1.5">
              {FORMATS.map((f) => (
                <button key={f.id} onClick={() => setFormat(f.id)}
                  className={"grid w-full grid-cols-[auto_minmax(0,1fr)] items-center gap-3 border px-3 py-2.5 text-left transition-colors rounded-lg " +
                    (format === f.id ? "border-primary/50 bg-primary/10" : "border-border hover:bg-panel-raised")}>
                  <f.icon className={"h-4 w-4 shrink-0 " + (format === f.id ? "text-primary" : "text-muted-foreground")} />
                  <span className="min-w-0">
                    <span className="num block text-xs font-semibold">{f.label}</span>
                    <span className="block truncate text-[10px] text-muted-foreground">{f.desc}</span>
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Date range */}
          <div className="grid grid-cols-2 gap-2">
            <label className="block">
              <span className="label-xs">From</span>
              <input type="date" value={from} onChange={(e) => setFrom(e.target.value)}
                className="num mt-1 w-full border border-border bg-panel-raised px-2 py-1.5 text-xs text-foreground outline-none focus:border-primary rounded-md" />
            </label>
            <label className="block">
              <span className="label-xs">To</span>
              <input type="date" value={to} onChange={(e) => setTo(e.target.value)}
                className="num mt-1 w-full border border-border bg-panel-raised px-2 py-1.5 text-xs text-foreground outline-none focus:border-primary rounded-md" />
            </label>
          </div>

          {/* Includes note */}
          <div className="num border border-border bg-panel-raised p-2.5 text-[10px] text-muted-foreground rounded-lg leading-relaxed">
            <span className="text-foreground font-semibold block mb-1">Includes:</span>
            Junction performance · BRTS intrusion log · lane-discipline violations · adaptive-vs-fixed baseline · AI recommendations
          </div>

          {/* Progress bar */}
          {status === "loading" && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="label-xs">Generating report…</span>
                <span className="num text-[10px] text-primary">{Math.round(Math.min(progress, 100))}%</span>
              </div>
              <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-300"
                  style={{ width: Math.min(progress, 100) + "%" }}
                />
              </div>
            </div>
          )}

          {status === "error" && (
            <div className="num text-[11px] text-crit border border-crit/30 bg-crit/10 rounded-lg px-3 py-2">
              Export failed. Backend may be offline. Check console for details.
            </div>
          )}

          {/* CTA button */}
          <button
            onClick={handleExport}
            disabled={status === "loading" || status === "done"}
            className={"num flex w-full items-center justify-center gap-2 border px-3 py-2.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all " +
              (status === "done"
                ? "border-ok/50 bg-ok/15 text-ok"
                : status === "loading"
                  ? "border-border text-muted-foreground cursor-not-allowed"
                  : "border-primary/50 bg-primary/20 text-primary hover:bg-primary/30")}
          >
            {status === "done" ? (
              <><Check className="h-4 w-4" /> Downloaded!</>
            ) : status === "loading" ? (
              <><Loader className="h-4 w-4 animate-spin" /> Generating…</>
            ) : (
              <><Download className="h-4 w-4" /> Export {selected.label}</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
