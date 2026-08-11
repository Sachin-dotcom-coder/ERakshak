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
  | { type: "SET_INITIAL_DATA"; payload: { junctions?: Junction[]; alerts?: Alert[]; predictions?: Prediction[] } }
  | { type: "UPDATE_JUNCTION_WS"; payload: any }
  | { type: "ALERT"; payload: Alert }
  | { type: "PREDICTION"; payload: Prediction }
  | { type: "DETECTION"; payload: DetectionEvent }
  | { type: "CONNECTION"; payload: boolean }
  | { type: "TICK_DECAY" };

const initialState: State = {
  connected: false,
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

    case "SET_INITIAL_DATA":
      return {
        ...state,
        junctions: action.payload.junctions?.length ? action.payload.junctions : state.junctions,
        alerts: action.payload.alerts?.length ? action.payload.alerts : state.alerts,
        predictions: action.payload.predictions?.length ? action.payload.predictions : state.predictions,
      };

    case "UPDATE_JUNCTION_WS": {
      const eventData = action.payload;

      const updatedJunctions = state.junctions.map((j) => {
        if (j.id === eventData.junction_id || j.name === eventData.name) {
          const avgQ = eventData.avg_queue_length_m ?? 0;
          const ci = Math.min(100, Math.max(5, Math.round(avgQ * 1.1)));
          // Allocate dynamic green duration calculated by Backend Max-Pressure Controller
          const allocatedGreen = eventData.cycle_length 
            ? Math.round(eventData.cycle_length)
            : Math.min(85, Math.max(18, Math.round(20 + avgQ * 0.6)));

          const signalStatus = eventData.current_phase?.toLowerCase().includes("red")
            ? ("RED" as const)
            : eventData.current_phase?.toLowerCase().includes("yellow")
            ? ("YELLOW" as const)
            : ("GREEN" as const);

          return {
            ...j,
            congestionIndex: ci,
            signalCountdown: allocatedGreen,
            congestion:
              ci > 80
                ? ("gridlock" as const)
                : ci > 65
                ? ("heavy" as const)
                : ci > 40
                ? ("moderate" as const)
                : ("optimal" as const),
            avgWait: Math.round(avgQ * 1.8 + 15),
            throughput: eventData.total_vehicles ? eventData.total_vehicles * 40 : j.throughput,
            signalStatus,
            lanes: eventData.lanes?.length
              ? eventData.lanes.map((l: any, idx: number) => ({
                  id: l.lane_id || `l-${idx}`,
                  name: l.lane_name || `Lane ${idx + 1}`,
                  density: Math.round(l.occupancy_ratio * 100),
                  queue: Math.round(l.queue_length_m / 6),
                  arrivalRate: Math.round(l.vehicle_count * 2),
                }))
              : j.lanes,
          };
        }
        return j;
      });

      // Update KPI metrics dynamically
      const kpis = state.kpis.map((k) => {
        if (k.key === "interventions") {
          const val = state.alerts.length + 12;
          return { ...k, value: val };
        }
        if (k.key === "brtsIntrusions") {
          const totalIntrusions = updatedJunctions.reduce(
            (acc, j) => acc + (j.camera.online ? 1 : 0),
            0
          );
          return { ...k, value: totalIntrusions };
        }
        return k;
      });

      return {
        ...state,
        junctions: updatedJunctions,
        kpis,
        lastUpdate: Date.now(),
      };
    }

    case "TICK_DECAY": {
      // Local timer tick to smoothly decrement signal countdowns and transition states
      const updatedJunctions = state.junctions.map((j) => {
        let newCountdown = j.signalCountdown - 1;
        let newStatus = j.signalStatus;

        if (newCountdown <= 0) {
          // Transition state realistically when countdown reaches zero
          if (j.signalStatus === "GREEN") {
            newStatus = "YELLOW";
            newCountdown = 5;
          } else if (j.signalStatus === "YELLOW") {
            newStatus = "RED";
            newCountdown = 45;
          } else {
            newStatus = "GREEN";
            newCountdown = 35;
          }
        }

        return {
          ...j,
          signalCountdown: newCountdown,
          signalStatus: newStatus,
        };
      });

      return {
        ...state,
        junctions: updatedJunctions,
      };
    }

    case "ALERT":
      return { ...state, alerts: [action.payload, ...state.alerts].slice(0, 60) };

    case "PREDICTION":
      return { ...state, predictions: [action.payload, ...state.predictions].slice(0, 30) };

    case "DETECTION":
      return {
        ...state,
        detections: [action.payload, ...state.detections].slice(0, 120),
      };

    default:
      return state;
  }
}

export function useTrafficData() {
  const [state, dispatch] = useReducer(reducer, initialState);

  // 1. Initial REST API Fetch
  useEffect(() => {
    async function loadBackendData() {
      try {
        const [jRes, vRes, rRes] = await Promise.all([
          fetch("http://localhost:8000/api/junctions").catch(() => null),
          fetch("http://localhost:8000/api/violations").catch(() => null),
          fetch("http://localhost:8000/api/recommendations").catch(() => null),
        ]);

        let fetchedJunctions: Junction[] | undefined;
        let fetchedAlerts: Alert[] | undefined;
        let fetchedPredictions: Prediction[] | undefined;

        if (jRes && jRes.ok) {
          const rawJunctions = await jRes.json();
          if (Array.isArray(rawJunctions) && rawJunctions.length > 0) {
            fetchedJunctions = JUNCTIONS.map((j) => {
              const matched = rawJunctions.find((rj: any) => rj.id === j.id || rj.name === j.name);
              if (matched) {
                return {
                  ...j,
                  name: matched.name || j.name,
                  lat: matched.latitude || j.lat,
                  lng: matched.longitude || j.lng,
                };
              }
              return j;
            });
          }
        }

        if (vRes && vRes.ok) {
          const rawViolations = await vRes.json();
          if (Array.isArray(rawViolations)) {
            fetchedAlerts = rawViolations.map((v: any) => ({
              id: `V-${v.id}`,
              type: "alert" as const,
              kind: v.violation_type?.includes("brts") ? ("brts" as const) : ("violation" as const),
              severity: "critical" as const,
              junctionId: v.lane_id?.split("_")[0] || "J001",
              junctionName: `Junction ${v.lane_id?.split("_")[0] || "J001"}`,
              message: `${v.vehicle_type?.toUpperCase() || "Vehicle"} detected violating ${v.violation_type?.replace("_", " ")}`,
              ts: new Date(v.timestamp).getTime() || Date.now(),
            }));
          }
        }

        if (rRes && rRes.ok) {
          const rawRecs = await rRes.json();
          if (Array.isArray(rawRecs)) {
            fetchedPredictions = rawRecs.map((r: any) => ({
              id: `P-${r.id}`,
              type: "prediction" as const,
              junctionId: r.junction_id,
              junctionName: `Junction ${r.junction_id}`,
              title: r.issue_type?.replace("_", " ").toUpperCase() || "INFRASTRUCTURE REC",
              detail: r.suggested_action || r.description,
              confidence: r.severity === "critical" ? 96 : 88,
              window: "Next 15m",
              series: [
                { t: "10m ago", v: 40 },
                { t: "5m ago", v: 65 },
                { t: "Now", v: 85 },
                { t: "In 5m", v: 92 },
              ],
            }));
          }
        }

        dispatch({
          type: "SET_INITIAL_DATA",
          payload: {
            junctions: fetchedJunctions,
            alerts: fetchedAlerts,
            predictions: fetchedPredictions,
          },
        });
      } catch (e) {
        console.warn("Failed to load initial REST traffic data, falling back to mock defaults", e);
      }
    }

    loadBackendData();
  }, []);

  // 2. Real-time WebSocket Stream Subscriber
  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimeout: any = null;

    function connect() {
      try {
        socket = new WebSocket("ws://localhost:8000/api/ws/traffic");

        socket.onopen = () => {
          console.log("Connected to E-Rakshak Live Traffic WebSocket Stream");
          dispatch({ type: "CONNECTION", payload: true });
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === "junction_update") {
              dispatch({ type: "UPDATE_JUNCTION_WS", payload: data });
            } else if (data.type === "new_violation") {
              dispatch({
                type: "ALERT",
                payload: {
                  id: `V-${data.id}-${Date.now()}`,
                  type: "alert",
                  kind: data.violation_type?.includes("brts") ? "brts" : "violation",
                  severity: "critical",
                  junctionId: data.lane_id?.split("_")[0] || "J001",
                  junctionName: data.junction_name || "Surat Junction",
                  message: `${data.vehicle_type?.toUpperCase()} intruded ${data.lane_name}`,
                  ts: Date.now(),
                },
              });
            } else if (data.type === "new_recommendation") {
              dispatch({
                type: "PREDICTION",
                payload: {
                  id: `P-${data.id}-${Date.now()}`,
                  type: "prediction",
                  junctionId: data.junction_id,
                  junctionName: data.junction_name,
                  title: data.issue_type?.replace("_", " ").toUpperCase(),
                  detail: data.suggested_action,
                  confidence: data.severity === "critical" ? 95 : 85,
                  window: "Next 15m",
                  series: [
                    { t: "10m ago", v: 30 },
                    { t: "5m ago", v: 60 },
                    { t: "Now", v: 80 },
                    { t: "In 5m", v: 95 },
                  ],
                },
              });
            }
          } catch (err) {
            console.error("Error parsing WebSocket message:", err);
          }
        };

        socket.onclose = () => {
          dispatch({ type: "CONNECTION", payload: false });
          reconnectTimeout = setTimeout(connect, 3000);
        };

        socket.onerror = (err) => {
          console.warn("WebSocket error:", err);
          socket?.close();
        };
      } catch (err) {
        console.error("Failed to connect WebSocket:", err);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    }

    connect();

    const countdownTimer = setInterval(() => {
      dispatch({ type: "TICK_DECAY" });
    }, 1000);

    return () => {
      if (socket) socket.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      clearInterval(countdownTimer);
    };
  }, []);

  const stats = useMemo(() => {
    const online = state.junctions.filter((j: Junction) => j.camera.online).length;
    const avgCongestion = Math.round(
      state.junctions.reduce((a: number, j: Junction) => a + j.congestionIndex, 0) /
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
    (id: string | null) => state.junctions.find((j: Junction) => j.id === id) ?? null,
    [state.junctions],
  );

  return { ...state, stats, getJunction };
}

export type TrafficData = ReturnType<typeof useTrafficData>;
