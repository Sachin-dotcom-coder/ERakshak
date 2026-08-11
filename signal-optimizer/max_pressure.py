"""
max_pressure.py — Core Adaptive Signal-Timing Algorithm (Max-Pressure Control)
================================================================================
Implements the Max-Pressure (back-pressure) adaptive signal control algorithm.

Algorithm overview
------------------
At each decision cycle the controller computes a *pressure* score for each
competing signal phase.  Pressure for a phase is the weighted sum of queue
lengths on the approaches that go green in that phase, minus the weighted sum
of queue lengths on the downstream approaches that would receive the discharged
vehicles.

  pressure(phase) = Σ (weight_i × queue_upstream_i) − Σ (weight_j × queue_downstream_j)

The phase with the highest pressure is selected.  The recommended cycle time is
then bounded by the active :mod:`event_modes` profile and further constrained
by :mod:`confidence` when sensor trust is low.

Integration points
------------------
- :mod:`confidence`  — blends live density with historical, caps cycle deltas
- :mod:`prediction`  — feeds predicted queue into the pressure score
- :mod:`event_modes` — supplies per-mode min/max green + pressure weight
- :mod:`priority`    — BRTS boost and emergency override
- :mod:`explain`     — generates the reason string for the output contract
- :mod:`webster_formula` — used as fallback when sensor data is absent

Output contract (Section 3 of instructions.md)
----------------------------------------------
{
  "junction_id": "junction_01",
  "timestamp": "...",
  "recommended_cycle_time_sec": 38,
  "phase": "NS_green",
  "confidence": 0.62,
  "mode": "office_hours",
  "predicted_congestion_5min": "rising",
  "brts_priority_triggered": false,
  "emergency_priority_triggered": false,
  "reason": "..."
}
"""

from __future__ import annotations

import datetime
from typing import Optional

from confidence import (
    CONFIDENCE_THRESHOLD,
    blend_density,
    cap_cycle_delta,
    compute_confidence,
    is_cautious,
)
from event_modes import ModeProfile, get_mode_params, select_mode
from explain import build_reason
from prediction import JunctionPredictor, TrendLabel, congestion_label
from priority import (
    BRTSEvent,
    EmergencyEvent,
    PriorityResult,
    apply_brts_boost,
    evaluate_priority,
)
from webster_formula import Phase, optimal_cycle

# ---------------------------------------------------------------------------
# Historical density defaults (placeholder — wire up Person C's DB later)
# ---------------------------------------------------------------------------
DEFAULT_HISTORICAL_DENSITY: dict[str, float] = {
    "lane_NS_1": 8.0,
    "lane_NS_2": 7.0,
    "lane_EW_1": 6.0,
    "lane_EW_2": 5.0,
}

# Phase definitions: each phase maps phase name → list of approach names whose
# upstream lanes go green, and list of downstream approach names that receive
# the discharge.
PHASE_DEFINITIONS: dict[str, dict] = {
    "NS_green": {
        "upstream_lanes":   ["lane_NS_1", "lane_NS_2"],
        "downstream_lanes": ["lane_EW_1", "lane_EW_2"],
        "approach":         "NS",
    },
    "EW_green": {
        "upstream_lanes":   ["lane_EW_1", "lane_EW_2"],
        "downstream_lanes": ["lane_NS_1", "lane_NS_2"],
        "approach":         "EW",
    },
}

# Base cycle time when we have no data at all (seconds)
FALLBACK_CYCLE_SEC: int = 40

# Saturation flow used by Webster fallback (veh/h of green)
DEFAULT_SATURATION: float = 1800.0


# ---------------------------------------------------------------------------
# Main controller
# ---------------------------------------------------------------------------

class MaxPressureController:
    """Stateful adaptive signal controller for one junction."""

    def __init__(
        self,
        junction_id: str = "junction_01",
        mode_override: Optional[str] = None,
        historical_density: Optional[dict[str, float]] = None,
    ) -> None:
        self.junction_id = junction_id
        self.mode_override = mode_override
        self._historical = historical_density or DEFAULT_HISTORICAL_DENSITY
        self._predictor = JunctionPredictor(junction_id)
        self._current_cycle_sec: int = FALLBACK_CYCLE_SEC

    # ------------------------------------------------------------------
    # Main decision method
    # ------------------------------------------------------------------

    def decide(self, event: dict) -> dict:
        """Consume one event from Person A's feed and return the full output
        contract dict.

        Parameters
        ----------
        event:
            Parsed event dict (matches the mock_event_feed / Person A contract).

        Returns
        -------
        dict
            Full output contract ready for Person C's backend.
        """
        timestamp = event.get("timestamp", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        lanes: dict[str, dict] = event.get("lanes", {})

        # ---- 1. Confidence scoring ----
        det_conf: float = event.get("detection_confidence", 0.85)
        weather_flag: str = event.get("weather_flag", "clear")
        confidence = compute_confidence(det_conf, weather_flag)

        # ---- 2. Blend live vs. historical density ----
        blended_density: dict[str, float] = {}
        for lane_id, lane_data in lanes.items():
            live = float(lane_data.get("queue_length", lane_data.get("density", 0)))
            hist = self._historical.get(lane_id, live)
            blended_density[lane_id] = blend_density(live, hist, confidence)

        # ---- 3. Update predictor ----
        self._predictor.update({lid: blended_density[lid] for lid in blended_density})
        trend: TrendLabel = congestion_label(self._predictor)

        # ---- 4. Event mode ----
        weather_for_mode = weather_flag if is_cautious(confidence) else None
        active_mode_name = select_mode(
            manual_override=self.mode_override,
            weather_flag=weather_for_mode,
        )
        mode: ModeProfile = get_mode_params(active_mode_name)

        # ---- 5. Priority evaluation ----
        em_data = event.get("emergency_vehicle", {})
        emergency_event: Optional[EmergencyEvent] = None
        if em_data.get("detected"):
            emergency_event = EmergencyEvent(
                detected=True,
                approach=em_data.get("approach", "north"),
                lane_id=em_data.get("lane_id", "lane_1"),
                vehicle_speed_mps=em_data.get("vehicle_speed_mps"),
            )

        brts_event: Optional[BRTSEvent] = None
        if event.get("brts_waiting"):
            brts_event = BRTSEvent(
                approach=event.get("brts_approach", "north"),
                lane_id="lane_brts",
                wait_time_sec=float(event.get("brts_wait_time_sec", 0)),
            )

        priority: PriorityResult = evaluate_priority(emergency_event, brts_event)

        # ---- 6. Emergency override — skip normal algorithm ----
        if priority.emergency_triggered:
            em_approach = priority.emergency_approach or "north"
            hold_sec = int(priority.emergency_hold_sec)
            reason_str, _ = build_reason(
                dominant_approach=em_approach,
                dominant_queue=self._approx_queue(blended_density, em_approach),
                secondary_approach="other",
                secondary_queue=0,
                recommended_cycle_sec=hold_sec,
                confidence=confidence,
                weather_flag=weather_flag,
                priority=priority,
            )
            return self._contract(
                timestamp=timestamp,
                cycle_sec=hold_sec,
                phase=f"{em_approach}_green",
                confidence=confidence,
                mode=active_mode_name,
                trend=trend,
                priority=priority,
                reason=reason_str,
            )

        # ---- 7. Max-pressure calculation ----
        pressure_scores: dict[str, float] = {}
        for phase_name, phase_def in PHASE_DEFINITIONS.items():
            upstream_q = sum(
                blended_density.get(lid, 0.0) for lid in phase_def["upstream_lanes"]
            )
            downstream_q = sum(
                blended_density.get(lid, 0.0) for lid in phase_def["downstream_lanes"]
            )

            # Optionally blend in predicted queue for rising lanes
            if trend == "rising":
                for lid in phase_def["upstream_lanes"]:
                    predicted = self._predictor.get_predicted_queue(lid)
                    upstream_q = max(upstream_q, predicted)

            pressure = (upstream_q - downstream_q) * mode.pressure_weight
            pressure_scores[phase_name] = pressure

        # Apply BRTS boost
        pressure_scores = apply_brts_boost(
            {ph: sc for ph, sc in pressure_scores.items()},
            priority,
        )

        best_phase = max(pressure_scores, key=lambda p: pressure_scores[p])
        phase_def = PHASE_DEFINITIONS[best_phase]
        dom_approach = phase_def["approach"]
        sec_approach = "EW" if dom_approach == "NS" else "NS"

        # ---- 8. Cycle time calculation ----
        dom_q = sum(blended_density.get(lid, 0.0) for lid in phase_def["upstream_lanes"])
        sec_lanes = PHASE_DEFINITIONS[
            "EW_green" if best_phase == "NS_green" else "NS_green"
        ]["upstream_lanes"]
        sec_q = sum(blended_density.get(lid, 0.0) for lid in sec_lanes)

        # Webster as the numeric backbone for the cycle duration
        phases_w = [
            Phase(dom_approach, volume=dom_q * 60, saturation=DEFAULT_SATURATION),
            Phase(sec_approach, volume=sec_q * 60, saturation=DEFAULT_SATURATION),
        ]
        raw_cycle = optimal_cycle(phases_w)
        raw_cycle = max(mode.min_green, min(mode.max_green, raw_cycle))

        # Confidence: cap the delta from the last cycle
        proposed_delta = raw_cycle - self._current_cycle_sec
        capped_delta = cap_cycle_delta(proposed_delta, confidence)
        new_cycle = int(self._current_cycle_sec + capped_delta)
        new_cycle = max(mode.min_green, min(mode.max_green, new_cycle))
        self._current_cycle_sec = new_cycle

        # ---- 9. Build reason ----
        dom_queue_int = int(round(dom_q))
        sec_queue_int = int(round(sec_q))
        predicted_extra: Optional[float] = None
        if trend == "rising":
            predicted_extra = max(
                0.0,
                self._predictor.get_predicted_queue(phase_def["upstream_lanes"][0]) - dom_q,
            )

        reason_str, _ = build_reason(
            dominant_approach=dom_approach,
            dominant_queue=dom_queue_int,
            secondary_approach=sec_approach,
            secondary_queue=sec_queue_int,
            recommended_cycle_sec=new_cycle,
            confidence=confidence,
            weather_flag=weather_flag,
            cycle_delta_sec=capped_delta,
            trend=trend,
            predicted_extra_vehicles=predicted_extra,
            priority=priority,
        )

        return self._contract(
            timestamp=timestamp,
            cycle_sec=new_cycle,
            phase=best_phase,
            confidence=confidence,
            mode=active_mode_name,
            trend=trend,
            priority=priority,
            reason=reason_str,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _contract(
        self,
        timestamp: str,
        cycle_sec: int,
        phase: str,
        confidence: float,
        mode: str,
        trend: TrendLabel,
        priority: PriorityResult,
        reason: str,
    ) -> dict:
        """Assemble the full output contract dict (Section 3)."""
        return {
            "junction_id": self.junction_id,
            "timestamp": timestamp,
            "recommended_cycle_time_sec": cycle_sec,
            "phase": phase,
            "confidence": round(confidence, 3),
            "mode": mode,
            "predicted_congestion_5min": trend,
            "brts_priority_triggered": priority.brts_triggered,
            "emergency_priority_triggered": priority.emergency_triggered,
            "reason": reason,
        }

    @staticmethod
    def _approx_queue(blended_density: dict[str, float], approach: str) -> int:
        """Rough total queue for an approach (for emergency reason string)."""
        total = sum(
            v for k, v in blended_density.items()
            if approach.lower()[0] in k.lower()
        )
        return max(0, int(round(total)))


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    from mock_event_feed import generate_event, event_stream

    ctrl = MaxPressureController("junction_01")

    print("=== Normal event decision ===")
    ev = generate_event(scenario="normal")
    decision = ctrl.decide(ev)
    print(json.dumps(decision, indent=2))

    print("\n=== Rain / low-confidence event ===")
    ev2 = generate_event(scenario="rain")
    decision2 = ctrl.decide(ev2)
    print(json.dumps(decision2, indent=2))

    print("\n=== Emergency vehicle event ===")
    ev3 = generate_event(emergency_approach="north")
    decision3 = ctrl.decide(ev3)
    print(json.dumps(decision3, indent=2))

    print("\n=== 5-step stream (rising congestion) ===")
    ctrl2 = MaxPressureController("junction_01")
    for i, ev in enumerate(event_stream(5, scenario="congested")):
        d = ctrl2.decide(ev)
        print(f"  Step {i}: cycle={d['recommended_cycle_time_sec']}s "
              f"phase={d['phase']} conf={d['confidence']} "
              f"trend={d['predicted_congestion_5min']}")
