import { useState } from "react";
import {
  Download,
  FileText,
  FileSpreadsheet,
  FileJson,
  X,
  Check,
  Loader,
  Sparkles,
  Calendar,
  AlertCircle,
  ShieldCheck,
  Lock,
} from "lucide-react";

const BASE = "http://localhost:8000";

export type PeriodKey =
  | "previous_week"
  | "previous_month"
  | "last_7_days"
  | "last_30_days"
  | "custom";

const PERIOD_OPTIONS = [
  { id: "previous_week", label: "Previous Week (Mon–Sun)", desc: "Completed cycle preceding current week" },
  { id: "previous_month", label: "Previous Month", desc: "Whole prior calendar month" },
  { id: "last_7_days", label: "Last 7 Days", desc: "Past rolling 168 hours of activity" },
  { id: "last_30_days", label: "Last 30 Days", desc: "Past rolling monthly trends" },
  { id: "custom", label: "Custom Date Range…", desc: "Select arbitrary start and end dates" },
] as const;

const FORMATS = [
  {
    id: "pdf",
    label: "PDF Executive Briefing",
    desc: "Print-ready document with Gemini analysis, charts & metrics",
    icon: FileText,
    defaultFilename: "erakshak_report.pdf",
    supportsAi: true,
  },
  {
    id: "violations_csv",
    label: "Violations CSV Log",
    desc: "Period-filtered BRTS intrusion and lane discipline records",
    icon: FileSpreadsheet,
    defaultFilename: "erakshak_violations.csv",
    supportsAi: false,
  },
  {
    id: "metrics_csv",
    label: "Traffic Metrics CSV",
    desc: "Per-junction queue lengths, speeds, and sample counts",
    icon: FileSpreadsheet,
    defaultFilename: "erakshak_metrics.csv",
    supportsAi: false,
  },
  {
    id: "json",
    label: "Raw JSON Telemetry",
    desc: "Machine-readable verified statistics snapshot",
    icon: FileJson,
    defaultFilename: "erakshak_report_stats.json",
    supportsAi: false,
  },
] as const;

type FormatId = (typeof FORMATS)[number]["id"];
type Status = "idle" | "loading" | "done" | "error";

export function ExportModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [format, setFormat] = useState<FormatId>("pdf");
  const [period, setPeriod] = useState<PeriodKey>("last_7_days");
  const [useAi, setUseAi] = useState(true);

  // Custom date range state
  const todayStr = new Date().toISOString().slice(0, 10);
  const [from, setFrom] = useState("2026-10-01");
  const [to, setTo] = useState(todayStr);

  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  if (!open) return null;

  const selectedFormat = FORMATS.find((f) => f.id === format)!;

  function buildExportUrl(): string {
    const params = new URLSearchParams();
    params.set("period", period);
    if (period === "custom") {
      if (from) params.set("start", from);
      if (to) params.set("end", to);
    }

    if (format === "pdf") {
      params.set("ai", String(useAi));
      return `${BASE}/api/reports/download/pdf?${params.toString()}`;
    }
    if (format === "violations_csv") {
      params.set("type", "violations");
      return `${BASE}/api/reports/download/csv?${params.toString()}`;
    }
    if (format === "metrics_csv") {
      params.set("type", "metrics");
      return `${BASE}/api/reports/download/csv?${params.toString()}`;
    }
    // format === 'json'
    return `${BASE}/api/reports/preview?${params.toString()}`;
  }

  async function handleExport() {
    setErrorMessage(null);
    if (period === "custom") {
      if (!from || !to) {
        setErrorMessage("Please select both start and end dates.");
        return;
      }
      if (from > to) {
        setErrorMessage("Start date must be before or equal to end date.");
        return;
      }
      const diffDays = Math.ceil((new Date(to).getTime() - new Date(from).getTime()) / (1000 * 60 * 60 * 24));
      if (diffDays > 366) {
        setErrorMessage(`Selected range (${diffDays} days) exceeds maximum allowed range of 366 days.`);
        return;
      }
    }

    setStatus("loading");
    setProgress(15);

    // Animated progress simulation
    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 88) {
          clearInterval(interval);
          return p;
        }
        return p + Math.random() * 15;
      });
    }, 250);

    try {
      const url = buildExportUrl();
      const res = await fetch(url);

      if (!res.ok) {
        let detailMsg = `HTTP Error ${res.status}`;
        try {
          const errJson = await res.json();
          if (errJson.detail) detailMsg = errJson.detail;
        } catch {
          detailMsg = res.statusText || detailMsg;
        }
        throw new Error(detailMsg);
      }

      clearInterval(interval);
      setProgress(100);

      const blob = await res.blob();

      // Extract filename from Content-Disposition header if available
      const disposition = res.headers.get("Content-Disposition") || "";
      const filenameMatch = disposition.match(/filename="?([^";]+)"?/);
      let filename = filenameMatch ? filenameMatch[1] : selectedFormat.defaultFilename;

      if (format === "json") {
        filename = `erakshak_telemetry_${period}.json`;
      }

      downloadBlob(blob, filename);

      setStatus("done");
      setTimeout(() => {
        setStatus("idle");
        setProgress(0);
        onClose();
      }, 1500);
    } catch (err: any) {
      clearInterval(interval);
      console.error("Export error:", err);
      setStatus("error");
      setErrorMessage(err.message || "Failed to generate report. Ensure backend is running.");
      setProgress(0);
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
    <div className="fixed inset-0 z-[9999] grid place-items-center bg-black/80 p-4 backdrop-blur-md">
      <div className="w-full max-w-lg border border-border bg-panel rounded-xl shadow-2xl overflow-hidden animate-grid-appear">

        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-4 bg-foreground/[0.02]">
          <div className="flex items-center gap-2.5">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-foreground/10 text-foreground">
              <Download className="h-4 w-4" />
            </div>
            <div>
              <div className="label-xs flex items-center gap-1.5 text-muted-foreground">
                <span>E-Rakshak Traffic Intelligence</span>
                <span className="inline-block h-1 w-1 rounded-full bg-emerald-500"></span>
                <span className="text-emerald-400 text-[9px] font-mono">GOV-SURAT</span>
              </div>
              <h2 className="text-sm font-bold tracking-tight text-foreground">
                Executive Report & Telemetry Export
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={status === "loading"}
            className="grid h-7 w-7 place-items-center rounded-lg border border-border text-muted-foreground transition-colors hover:bg-foreground/10 hover:text-foreground disabled:opacity-50"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="space-y-4 p-5">

          {/* 1. Period Selector */}
          <div className="space-y-1.5">
            <label className="label-xs flex items-center gap-1.5 text-foreground/80">
              <Calendar className="h-3 w-3 text-emerald-400" />
              <span>Reporting Period</span>
            </label>
            <div className="relative">
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value as PeriodKey)}
                disabled={status === "loading"}
                className="w-full appearance-none rounded-lg border border-border bg-foreground/[0.04] px-3.5 py-2.5 text-xs font-medium text-foreground transition-all hover:bg-foreground/[0.08] focus:border-foreground/40 focus:outline-none"
              >
                {PERIOD_OPTIONS.map((opt) => (
                  <option key={opt.id} value={opt.id} className="bg-panel text-foreground">
                    {opt.label}
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-muted-foreground">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Custom Date Pickers */}
          {period === "custom" && (
            <div className="rounded-lg border border-border bg-foreground/[0.02] p-3 space-y-2 animate-grid-appear">
              <div className="text-[11px] font-medium text-muted-foreground">Select Custom Date Range:</div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label-xs mb-1 block">Start Date</label>
                  <input
                    type="date"
                    value={from}
                    max={todayStr}
                    onChange={(e) => setFrom(e.target.value)}
                    disabled={status === "loading"}
                    className="w-full rounded-md border border-border bg-panel px-3 py-1.5 text-xs font-mono text-foreground focus:border-foreground/40 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="label-xs mb-1 block">End Date</label>
                  <input
                    type="date"
                    value={to}
                    max={todayStr}
                    onChange={(e) => setTo(e.target.value)}
                    disabled={status === "loading"}
                    className="w-full rounded-md border border-border bg-panel px-3 py-1.5 text-xs font-mono text-foreground focus:border-foreground/40 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* 2. Format Selection Grid */}
          <div className="space-y-1.5">
            <label className="label-xs text-foreground/80">Export Format</label>
            <div className="grid grid-cols-2 gap-2">
              {FORMATS.map((f) => {
                const Icon = f.icon;
                const active = format === f.id;
                return (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => setFormat(f.id)}
                    disabled={status === "loading"}
                    className={`flex items-start gap-2.5 rounded-lg border p-2.5 text-left transition-all ${
                      active
                        ? "border-emerald-500/50 bg-emerald-500/[0.08] shadow-sm shadow-emerald-500/10"
                        : "border-border bg-foreground/[0.02] hover:bg-foreground/[0.06] text-muted-foreground"
                    }`}
                  >
                    <div
                      className={`mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-md ${
                        active ? "bg-emerald-500/20 text-emerald-400" : "bg-foreground/5 text-muted-foreground"
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className={`text-xs font-semibold ${active ? "text-foreground" : "text-muted-foreground"}`}>
                        {f.label}
                      </div>
                      <div className="text-[10px] text-muted-foreground/80 line-clamp-1 leading-snug">
                        {f.desc}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 3. Gemini AI Narrative Toggle (PDF format only) */}
          {format === "pdf" && (
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/[0.04] p-3 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="grid h-6 w-6 place-items-center rounded-md bg-emerald-500/20 text-emerald-400">
                    <Sparkles className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                      <span>Gemini AI Narrative Synthesis</span>
                      <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] font-mono text-emerald-300">
                        Pydantic Schema
                      </span>
                    </div>
                    <div className="text-[10px] text-muted-foreground">
                      Structured executive briefing strictly grounded in verified database metrics
                    </div>
                  </div>
                </div>

                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={useAi}
                    onChange={(e) => setUseAi(e.target.checked)}
                    disabled={status === "loading"}
                    className="sr-only peer"
                  />
                  <div className="h-5 w-9 rounded-full bg-border peer-checked:bg-emerald-500 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all"></div>
                </label>
              </div>

              {/* Data Privacy & Encryption Assurance Badge */}
              <div className="flex items-center gap-1.5 text-[10px] text-emerald-400/90 font-mono bg-emerald-500/[0.08] px-2 py-1 rounded border border-emerald-500/20">
                <Lock className="h-3 w-3 shrink-0" />
                <span>Zero-Leak Encryption: All infrastructure & corridor tokens salted with HMAC-SHA256 prior to cloud analysis.</span>
              </div>
            </div>
          )}

          {/* Progress / Error Alerts */}
          {errorMessage && (
            <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/[0.08] p-2.5 text-xs text-red-400 animate-grid-appear">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {status === "loading" && (
            <div className="space-y-1.5 animate-grid-appear">
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span className="flex items-center gap-1.5 font-mono">
                  <Loader className="h-3 w-3 animate-spin text-emerald-400" />
                  Building verified report artifacts...
                </span>
                <span className="font-mono">{Math.round(progress)}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-foreground/10">
                <div
                  className="h-full bg-emerald-500 transition-all duration-300 rounded-full"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between border-t border-border px-5 py-3.5 bg-foreground/[0.02]">
          <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground font-mono">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Audited & verified against SQL registers</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={status === "loading"}
              className="rounded-lg border border-border px-3 py-1.5 text-xs font-semibold text-muted-foreground transition-colors hover:bg-foreground/5 hover:text-foreground disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleExport}
              disabled={status === "loading"}
              className={`flex items-center gap-1.5 rounded-lg px-4 py-1.5 text-xs font-bold transition-all shadow-sm ${
                status === "done"
                  ? "bg-emerald-500 text-black shadow-emerald-500/20"
                  : "bg-foreground text-background hover:opacity-90"
              } disabled:opacity-50`}
            >
              {status === "loading" ? (
                <>
                  <Loader className="h-3.5 w-3.5 animate-spin" />
                  Generating…
                </>
              ) : status === "done" ? (
                <>
                  <Check className="h-3.5 w-3.5 text-black" />
                  Downloaded
                </>
              ) : (
                <>
                  <Download className="h-3.5 w-3.5" />
                  Download Report
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
