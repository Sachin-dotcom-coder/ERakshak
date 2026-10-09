import React, { useState } from "react";
import { Check, X, Sparkles } from "lucide-react";
import type { RecommendationGrouped } from "@/hooks/useReportsData";

interface RecsTableProps {
  recommendations: RecommendationGrouped[];
  onDecision: (id: number, action: "approve" | "reject" | "defer", reason?: string) => void;
  onSelectJunction: (id: string) => void;
}

export const RecommendationsTable: React.FC<RecsTableProps> = ({
  recommendations,
  onDecision,
  onSelectJunction,
}) => {
  const [filter, setFilter] = useState<"ALL" | "OPERATIONAL" | "INFRASTRUCTURE" | "APPLIED">("ALL");
  const [rejectModalRecId, setRejectModalRecId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("Planned roadwork conflicts");

  const filtered = recommendations.filter((r) => {
    if (filter === "ALL") return true;
    if (filter === "APPLIED") return r.status === "APPLIED";
    return r.category === filter;
  });

  const pendingCount = recommendations.filter((r) => r.status === "PENDING").length;

  return (
    <div className="rounded-[24px] border border-[#1C1C20] bg-[#0E0E10] p-5 transition-all hover:border-[#6B6B73]/40">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1C1C20] pb-3">
        <div className="flex items-center gap-2.5">
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.14em] text-[#6B6B73]">
            AI RECOMMENDATIONS
          </span>
          <span className="rounded-full border border-[#FFFFFF]/20 bg-[#FFFFFF]/10 px-2 py-0.2 font-mono text-[10px] font-bold text-[#FFFFFF]">
            {pendingCount} PENDING
          </span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center rounded-full border border-[#1C1C20] bg-[#1A1A1D] p-0.5">
          {(["ALL", "OPERATIONAL", "INFRASTRUCTURE", "APPLIED"] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`rounded-full px-2.5 py-0.5 font-mono text-[10px] font-semibold capitalize transition-all ${
                filter === cat
                  ? "bg-[#FFFFFF] text-[#0A0A0B] shadow-sm"
                  : "text-[#A1A1A8] hover:text-[#FFFFFF]"
              }`}
            >
              {cat === "ALL" ? "All" : cat.toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Clean, Streamlined Table */}
      <div className="mt-3 overflow-x-auto">
        <table className="w-full border-collapse text-left whitespace-nowrap">
          <thead>
            <tr className="border-b border-[#1C1C20] font-mono text-[10px] uppercase tracking-[0.14em] text-[#6B6B73]">
              <th className="pb-2.5 pl-2">Severity</th>
              <th className="pb-2.5">Issue</th>
              <th className="pb-2.5">Where</th>
              <th className="pb-2.5 whitespace-normal min-w-[260px]">Suggested Action</th>
              <th className="pb-2.5">Impact</th>
              <th className="pb-2.5">Status</th>
              <th className="pb-2.5 pr-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1C1C20]/40 text-[12px]">
            {filtered.map((r) => {
              // Severity badge color: Critical = RED, High = AMBER, Medium = NEUTRAL
              let sevBg = "bg-[#D9534F]/15 text-[#D9534F] border-[#D9534F]/35";
              if (r.severity === "HIGH") {
                sevBg = "bg-[#E8A838]/15 text-[#E8A838] border-[#E8A838]/35";
              } else if (r.severity === "MEDIUM" || r.severity === "LOW") {
                sevBg = "bg-[#FFFFFF]/10 text-[#A1A1A8] border-[#FFFFFF]/15";
              }

              return (
                <tr
                  key={r.id}
                  className="group transition-colors hover:bg-[#1A1A1D]/40"
                >
                  {/* Severity Badge */}
                  <td className="py-3 pl-2 align-middle">
                    <span
                      className={`inline-block rounded-md border px-2 py-0.5 font-mono text-[9px] font-bold ${sevBg}`}
                    >
                      {r.severity}
                    </span>
                  </td>

                  {/* Issue Title */}
                  <td className="py-3 align-middle font-medium text-[#FFFFFF]">
                    {r.issue_title}
                  </td>

                  {/* Junction chips */}
                  <td className="py-3 align-middle">
                    <div className="flex flex-wrap gap-1">
                      {r.junction_ids.map((jid) => (
                        <button
                          key={jid}
                          onClick={() => onSelectJunction(jid)}
                          className="rounded border border-[#1C1C20] bg-[#141416] px-1.5 py-0.2 font-mono text-[10px] text-[#A1A1A8] hover:text-[#FFFFFF]"
                        >
                          {jid}
                        </button>
                      ))}
                    </div>
                  </td>

                  {/* Suggested Action (Clean, concise) */}
                  <td className="py-3 align-middle whitespace-normal max-w-[420px]">
                    <div className="text-[#A1A1A8] group-hover:text-[#FFFFFF] leading-snug">
                      {r.suggested_action}
                    </div>
                    {r.measured_outcome && (
                      <div className="mt-1 flex items-center gap-1 font-mono text-[10px] text-[#5CB85C]">
                        <Sparkles className="h-3 w-3 shrink-0" />
                        <span>{r.measured_outcome}</span>
                      </div>
                    )}
                  </td>

                  {/* Impact */}
                  <td className="py-3 align-middle font-mono font-bold text-[#5CB85C]">
                    {r.expected_impact.split("·")[0]}
                  </td>

                  {/* Status Badge */}
                  <td className="py-3 align-middle">
                    {r.status === "PENDING" ? (
                      <span className="rounded border border-[#FFFFFF]/30 px-1.5 py-0.5 font-mono text-[9px] font-bold text-[#FFFFFF]">
                        PENDING
                      </span>
                    ) : r.status === "APPLIED" ? (
                      <span className="rounded bg-[#FFFFFF] px-1.5 py-0.5 font-mono text-[9px] font-bold text-[#0A0A0B]">
                        APPLIED
                      </span>
                    ) : (
                      <span className="rounded border border-[#1C1C20] px-1.5 py-0.5 font-mono text-[9px] text-[#6B6B73]">
                        {r.status}
                      </span>
                    )}
                  </td>

                  {/* Actions */}
                  <td className="py-3 pr-2 align-middle text-right">
                    {r.status === "PENDING" ? (
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => onDecision(r.id, "approve")}
                          title="Approve & Apply"
                          className="flex h-6 w-6 items-center justify-center rounded border border-[#1C1C20] bg-[#141416] text-[#5CB85C] hover:border-[#5CB85C] hover:bg-[#5CB85C] hover:text-[#0A0A0B]"
                        >
                          <Check className="h-3 w-3" />
                        </button>
                        <button
                          onClick={() => setRejectModalRecId(r.id)}
                          title="Reject"
                          className="flex h-6 w-6 items-center justify-center rounded border border-[#1C1C20] bg-[#141416] text-[#D9534F] hover:border-[#D9534F] hover:bg-[#D9534F] hover:text-[#FFFFFF]"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    ) : (
                      <span className="font-mono text-xs text-[#6B6B73]">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Reject Modal */}
      {rejectModalRecId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="w-[380px] rounded-2xl border border-[#1C1C20] bg-[#0E0E10] p-5 shadow-2xl">
            <h4 className="text-[15px] font-bold text-[#FFFFFF]">Reject Recommendation</h4>
            <div className="mt-3 space-y-2">
              {[
                "Planned roadwork conflicts",
                "Warden already stationed",
                "Sensor measurement inaccurate",
                "Other override",
              ].map((reason) => (
                <label
                  key={reason}
                  className="flex cursor-pointer items-center gap-2 rounded-lg border border-[#1C1C20] bg-[#141416] p-2 text-[11px] text-[#FFFFFF] hover:border-[#6B6B73]"
                >
                  <input
                    type="radio"
                    name="reject-reason"
                    checked={rejectReason === reason}
                    onChange={() => setRejectReason(reason)}
                    className="accent-white"
                  />
                  <span>{reason}</span>
                </label>
              ))}
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <button
                onClick={() => setRejectModalRecId(null)}
                className="rounded-lg border border-[#1C1C20] px-3 py-1.5 font-mono text-[10px] text-[#A1A1A8]"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onDecision(rejectModalRecId, "reject", rejectReason);
                  setRejectModalRecId(null);
                }}
                className="rounded-lg bg-[#D9534F] px-3 py-1.5 font-mono text-[10px] font-bold text-[#FFFFFF]"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
