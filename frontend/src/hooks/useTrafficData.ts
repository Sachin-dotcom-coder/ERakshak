import { useCallback, useEffect, useMemo, useReducer } from "react";
import {
  BRTS_INTRUSIONS,
  INITIAL_ALERTS,
  INITIAL_DETECTIONS,
  INITIAL_KPIS,
  INITIAL_PREDICTIONS,
  JUNCTIONS,
  QUEUE_JUNCTIONS,
  QUEUE_SERIES,
} from "@/lib/mock-traffic";
import type {
  Alert,
  DetectionEvent,
  Junction,
  Kpi,
  Prediction,
} from "@/lib/traffic-types";

/**
 * Single integration point for live traffic telemetry.
 *
 * Today this reducer is driven by a local mock ticker. To go live, replace the
 * ticker effect with a WebSocket subscription that dispatches the exact same
 * actions (`TICK`, `ALERT`, `DETECTION`) from server events — nothing in the UI
 * layer needs to change.
 */

type QueueRow = { t: string } & Record<string, number | string>;

type State = {
  connected: boolean;
  junctions: Junction[];
  kpis: Kpi[];
  queue: QueueRow[];
  alerts: Alert[];
  predictions: Prediction[];
  detections: DetectionEvent[];
  lastUpdate: number;
};

type Action =
  | { type: "TICK" }
  | { type: "ALERT"; payload: Alert }
  | { type: "DETECTION"; payload: DetectionEvent }
  | { type: "CONNECTION"; payload: boolean };

const initialState: State = {
  connected: true,
  junctions: JUNCTIONS,
  kpis: INITIAL_KPIS,
  queue: QUEUE_SERIES,
  alerts: INITIAL_ALERTS,
  predictions: INITIAL_PREDICTIONS,
  detections: INITIAL_DETECTIONS,
  lastUpdate: Date.now(),
};

const drift = (v: number, amp: number, min: number, max: number) =>
  Math.min(max, Math.max(min, v + (Math.random() - 0.5) * amp));

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "CONNECTION":
      return { ...state, connected: action.payload };
    case "TICK": {
      const junctions = state.junctions.map((j) => {
        const ci = Math.round(drift(j.congestionIndex, 6, 12, 97));
        const newCountdown = j.signalCountdown > 1 ? j.signalCountdown - 1 : (j.signalStatus === "GREEN" ? 5 : j.signalStatus === "YELLOW" ? 45 : 35);
        const newStatus = j.signalCountdown <= 1
          ? (j.signalStatus === "GREEN" ? "YELLOW" : j.signalStatus === "YELLOW" ? "RED" : "GREEN")
          : j.signalStatus;

        return {
          ...j,
          congestionIndex: ci,
          congestion:
            ci > 80
              ? ("gridlock" as const)
              : ci > 65
                ? ("heavy" as const)
                : ci > 40
                  ? ("moderate" as const)
                  : ("optimal" as const),
          avgWait: Math.round(drift(j.avgWait, 8, 20, 160)),
          throughput: Math.round(drift(j.throughput, 90, 900, 4200)),
          signalStatus: newStatus,
          signalCountdown: newCountdown,
          lanes: j.lanes.map((l) => ({
            ...l,
            density: Math.round(drift(l.density, 8, 5, 99)),
            queue: Math.round(drift(l.queue, 5, 1, 90)),
            arrivalRate: Math.round(drift(l.arrivalRate, 4, 4, 70)),
          })),
        };
      });

      const kpis = state.kpis.map((k) => {
        const value =
          k.key === "throughput"
            ? Math.round(drift(k.value, 420, 15000, 24000))
            : k.key === "waitReduction"
              ? Number(drift(k.value, 1.2, 22, 40).toFixed(1))
              : Math.round(drift(k.value, 1.6, 1, 999));
        const spark = [
          ...k.spark.slice(1).map((p, i) => ({ ...p, i })),
          { i: k.spark.length - 1, v: value },
        ];
        return { ...k, value, spark };
      });

      const d = new Date();
      const nextRow: QueueRow = {
        t: `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`,
      };
      QUEUE_JUNCTIONS.forEach((qj) => {
        const live = junctions.find((x) => x.id === qj.id);
        nextRow[qj.id] = Math.max(3, Math.round((live?.congestionIndex ?? 40) / 2.4));
      });

      return {
        ...state,
        junctions,
        kpis,
        queue: [...state.queue.slice(1), nextRow],
        lastUpdate: Date.now(),
      };
    }
    case "ALERT":
      return { ...state, alerts: [action.payload, ...state.alerts].slice(0, 60) };
    case "DETECTION":
      return {
        ...state,
        detections: [action.payload, ...state.detections].slice(0, 120),
      };
    default:
      return state;
  }
}

const MESSAGES: {
  kind: Alert["kind"];
  severity: Alert["severity"];
  message: string;
}[] = [
  {
    kind: "brts",
    severity: "critical",
    message: "BRTS corridor intrusion — vehicle in dedicated lane",
  },
  {
    kind: "violation",
    severity: "warning",
    message: "Lane-discipline violation — improper lane change captured",
  },
  {
    kind: "congestion",
    severity: "warning",
    message: "Congestion spike — queue growth 2.4x baseline",
  },
  {
    kind: "congestion",
    severity: "info",
    message: "Adaptive optimizer re-phased cycle (+9s green)",
  },
];

export function useTrafficData() {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    const tick = setInterval(() => dispatch({ type: "TICK" }), 3000);
    const alerts = setInterval(() => {
      const j = JUNCTIONS[Math.floor(Math.random() * JUNCTIONS.length)]!;
      const m = MESSAGES[Math.floor(Math.random() * MESSAGES.length)]!;
      dispatch({
        type: "ALERT",
        payload: {
          id: `A-${Math.floor(Math.random() * 1e6)}`,
          type: "alert",
          kind: m.kind,
          severity: m.severity,
          junctionId: j.id,
          junctionName: j.name,
          message: m.message,
          ts: Date.now(),
        },
      });
    }, 9000);
    const detections = setInterval(() => {
      const j = JUNCTIONS[Math.floor(Math.random() * JUNCTIONS.length)]!;
      const classes: DetectionEvent["objectClass"][] = [
        "car",
        "bus",
        "two-wheeler",
        "truck",
        "auto",
      ];
      const events: DetectionEvent["event"][] = [
        "vehicle_entry",
        "vehicle_exit",
        "vehicle_entry",
        "lane_violation",
        "brts_intrusion",
      ];
      dispatch({
        type: "DETECTION",
        payload: {
          id: `D-${Math.floor(Math.random() * 1e6)}`,
          ts: Date.now(),
          cameraId: j.camera.id,
          junctionName: j.name,
          event: events[Math.floor(Math.random() * events.length)]!,
          objectClass: classes[Math.floor(Math.random() * classes.length)]!,
          confidence: 70 + Math.floor(Math.random() * 29),
        },
      });
    }, 2200);
    return () => {
      clearInterval(tick);
      clearInterval(alerts);
      clearInterval(detections);
    };
  }, []);

  const stats = useMemo(() => {
    const online = state.junctions.filter((j) => j.camera.online).length;
    const avgCongestion = Math.round(
      state.junctions.reduce((a, j) => a + j.congestionIndex, 0) /
        state.junctions.length,
    );
    return {
      junctionsOnline: state.junctions.length,
      camerasOnline: online,
      camerasTotal: state.junctions.length,
      avgCongestion,
      activeIntrusions: BRTS_INTRUSIONS.length,
    };
  }, [state.junctions]);

  const getJunction = useCallback(
    (id: string | null) => state.junctions.find((j) => j.id === id) ?? null,
    [state.junctions],
  );

  return { ...state, stats, getJunction };
}

export type TrafficData = ReturnType<typeof useTrafficData>;
