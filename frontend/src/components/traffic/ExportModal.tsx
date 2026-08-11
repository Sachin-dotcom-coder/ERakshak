import { useState } from "react";
import { Download, FileJson, FileSpreadsheet, FileText, X } from "lucide-react";

const FORMATS = [
  { id: "pdf", label: "PDF", desc: "Signed briefing document for officials", icon: FileText },
  { id: "csv", label: "CSV", desc: "Tabular junction & violation records", icon: FileSpreadsheet },
  { id: "json", label: "JSON", desc: "Raw telemetry for downstream systems", icon: FileJson },
] as const;

export function ExportModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [format, setFormat] = useState<(typeof FORMATS)[number]["id"]>("pdf");
  const [from, setFrom] = useState("2026-08-01");
  const [to, setTo] = useState("2026-08-11");
  const [done, setDone] = useState(false);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-background/70 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md border border-border bg-panel">
        <div className="flex items-center justify-between border-b border-border px-3 py-2.5">
          <div>
            <div className="label-xs">Control room reporting</div>
            <h2 className="text-sm font-semibold">Export Report</h2>
          </div>
          <button
            onClick={onClose}
            className="grid h-7 w-7 place-items-center border border-border text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-4 p-3">
          <div>
            <div className="label-xs mb-2">Format</div>
            <div className="space-y-1.5">
              {FORMATS.map((f) => (
                <button
                  key={f.id}
                  onClick={() => setFormat(f.id)}
                  className={`grid w-full grid-cols-[auto_minmax(0,1fr)] items-center gap-2 border px-2.5 py-2 text-left transition-colors ${
                    format === f.id
                      ? "border-primary/50 bg-primary/10"
                      : "border-border hover:bg-panel-raised"
                  }`}
                >
                  <f.icon
                    className={`h-4 w-4 shrink-0 ${format === f.id ? "text-primary" : "text-muted-foreground"}`}
                  />
                  <span className="min-w-0">
                    <span className="num block text-xs font-semibold">{f.label}</span>
                    <span className="block truncate text-[11px] text-muted-foreground">
                      {f.desc}
                    </span>
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <label className="block">
              <span className="label-xs">From</span>
              <input
                type="date"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
                className="num mt-1 w-full border border-border bg-panel-raised px-2 py-1.5 text-xs text-foreground outline-none focus:border-primary"
              />
            </label>
            <label className="block">
              <span className="label-xs">To</span>
              <input
                type="date"
                value={to}
                onChange={(e) => setTo(e.target.value)}
                className="num mt-1 w-full border border-border bg-panel-raised px-2 py-1.5 text-xs text-foreground outline-none focus:border-primary"
              />
            </label>
          </div>

          <div className="num border border-border bg-panel-raised p-2 text-[10px] text-muted-foreground">
            Includes: junction performance, BRTS intrusion log, lane-discipline
            violations, adaptive-vs-static baseline comparison.
          </div>

          <button
            onClick={() => {
              setDone(true);
              setTimeout(() => {
                setDone(false);
                onClose();
              }, 1200);
            }}
            className="num flex w-full items-center justify-center gap-2 border border-primary/50 bg-primary/20 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-primary transition-colors hover:bg-primary/30"
          >
            <Download className="h-4 w-4" />
            {done ? "Generating…" : `Export ${format.toUpperCase()}`}
          </button>
        </div>
      </div>
    </div>
  );
}
