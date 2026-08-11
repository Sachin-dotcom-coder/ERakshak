import { useMemo, useState } from "react";
import { Filter } from "lucide-react";
import { fmtTime } from "@/lib/mock-traffic";
import type { DetectionEvent } from "@/lib/traffic-types";

const EVENT_TONE: Record<DetectionEvent["event"], string> = {
  vehicle_entry: "text-muted-foreground",
  vehicle_exit: "text-muted-foreground",
  lane_violation: "text-warn",
  brts_intrusion: "text-crit",
};

export function DetectionLog({
  events,
  cameras,
}: {
  events: DetectionEvent[];
  cameras: { id: string; junctionName: string }[];
}) {
  const [camera, setCamera] = useState("all");
  const [type, setType] = useState("all");

  const rows = useMemo(
    () =>
      events.filter(
        (e) =>
          (camera === "all" || e.cameraId === camera) &&
          (type === "all" || e.event === type),
      ),
    [events, camera, type],
  );

  return (
    <aside className="panel-surface flex min-h-0 flex-col">
      <div className="border-b border-border px-3 py-2">
        <div className="label-xs">Vision service · stdout</div>
        <h2 className="text-sm font-semibold">Detection Event Log</h2>
        <div className="mt-2 grid grid-cols-2 gap-1.5">
          <label className="block">
            <span className="sr-only">Filter by camera</span>
            <select
              value={camera}
              onChange={(e) => setCamera(e.target.value)}
              className="num w-full border border-border bg-panel-raised px-1.5 py-1 text-[10px] text-foreground outline-none focus:border-primary"
            >
              <option value="all">ALL CAMERAS</option>
              {cameras.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.id}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="sr-only">Filter by event type</span>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="num w-full border border-border bg-panel-raised px-1.5 py-1 text-[10px] text-foreground outline-none focus:border-primary"
            >
              <option value="all">ALL EVENTS</option>
              <option value="vehicle_entry">vehicle_entry</option>
              <option value="vehicle_exit">vehicle_exit</option>
              <option value="lane_violation">lane_violation</option>
              <option value="brts_intrusion">brts_intrusion</option>
            </select>
          </label>
        </div>
      </div>

      <div className="num min-h-0 flex-1 space-y-px overflow-y-auto bg-[oklch(0.15_0.025_264)] p-1.5 text-[10px] leading-[16px]">
        {rows.map((e) => (
          <div
            key={e.id}
            className="grid grid-cols-[auto_auto_minmax(0,1fr)] gap-2 border-b border-border/40 px-1 py-0.5 hover:bg-panel-raised"
          >
            <span className="text-muted-foreground">{fmtTime(e.ts)}</span>
            <span className="text-primary">{e.cameraId}</span>
            <span className="truncate">
              <span className={EVENT_TONE[e.event]}>{e.event}</span>
              <span className="text-muted-foreground">
                {" "}
                cls={e.objectClass} conf={(e.confidence / 100).toFixed(2)}
                {e.note ? ` ${e.note}` : ""}
              </span>
            </span>
          </div>
        ))}
        {rows.length === 0 && (
          <p className="flex items-center justify-center gap-1.5 p-4 text-center text-muted-foreground">
            <Filter className="h-3 w-3" /> no events match filter
          </p>
        )}
      </div>
    </aside>
  );
}
