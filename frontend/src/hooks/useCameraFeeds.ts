import { useEffect, useState } from "react";
import { CAMERA_FEEDS } from "@/lib/mock-traffic";
import type { CameraFeed } from "@/lib/traffic-types";

/**
 * Sibling integration point for the vision service. Replace the interval with a
 * WebSocket subscription that pushes annotated frames / detection payloads.
 */
export function useCameraFeeds() {
  const [feeds, setFeeds] = useState<CameraFeed[]>(CAMERA_FEEDS);

  useEffect(() => {
    const id = setInterval(() => {
      setFeeds((prev) =>
        prev.map((f) => {
          if (!f.online) return f;
          return {
            ...f,
            vehicleCount: Math.max(
              2,
              f.vehicleCount + Math.round((Math.random() - 0.5) * 4),
            ),
            avgSpeed: Math.max(
              5,
              Math.min(62, f.avgSpeed + Math.round((Math.random() - 0.5) * 5)),
            ),
            queueLength: Math.max(
              8,
              f.queueLength + Math.round((Math.random() - 0.5) * 18),
            ),
            boxes: f.boxes.map((b) => ({
              ...b,
              x: Math.max(2, Math.min(84, b.x + (Math.random() - 0.5) * 5)),
              y: Math.max(2, Math.min(74, b.y + (Math.random() - 0.5) * 4)),
              conf: Math.max(64, Math.min(99, b.conf + Math.round((Math.random() - 0.5) * 4))),
            })),
          };
        }),
      );
    }, 1400);
    return () => clearInterval(id);
  }, []);

  const online = feeds.filter((f) => f.online).length;
  return { feeds, online, total: feeds.length };
}
