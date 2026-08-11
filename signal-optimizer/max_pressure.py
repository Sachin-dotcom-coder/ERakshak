"""
max_pressure.py — Enhanced Multi-Factor Adaptive Signal Controller
====================================================================
Implements the enhanced Max-Pressure adaptive signal control algorithm with:

- Queue growth rate & acceleration bonuses
- Predicted pressure (not just predicted queue)
- Phase starvation prevention with fairness guarantees
- Hysteresis to prevent signal thrashing
- Phase switching cost penalty
- Downstream congestion & spillback protection
- Adaptive green duration (demand-responsive)
- Confidence-aware decision making (bands)
- Traffic anomaly awareness
- Decision confidence scoring
- Full decision trace for audit/debugging
- Safety constraint layer

Improvements #1–#6, #10–#14, #19–#21, #26, #30, #33, #40, #42
from new_instruct.md.
"""

from __future__ import annotations

import datetime
import time
from typing import Optional

from confidence import (
    CONFIDENCE_THRESHOLD,
    adaptive_hysteresis,
    blend_density,
    cap_cycle_delta,
    compute_confidence,
    compute_decision_confidence,
    confidence_band,
    is_cautious,
)
from controller_config import ControllerConfig, get_config
from event_modes import ModeProfile, get_mode_params, select_mode
from explain import build_reason
from health import HealthTracker
from historical import HistoricalProfileStore
from prediction import JunctionPredictor, TrendLabel, congestion_label
from priority import (
    BRTSEvent,
    EmergencyEvent,
    PriorityResult,
    apply_brts_boost,
    evaluate_priority,
)
from safety import SafetyValidator
from traffic_state import TrafficStateEngine
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

# Phase definitions
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

FALLBACK_CYCLE_SEC: int = 40
DEFAULT_SATURATION: float = 1800.0


# ---------------------------------------------------------------------------
# Main controller
# ---------------------------------------------------------------------------

class MaxPressureController:
    """Stateful enhanced adaptive signal controller for one junction."""

    def __init__(
        self,
        junction_id: str = "junction_01",
        mode_override: Optional[str] = None,
        historical_density: Optional[dict[str, float]] = None,
        config: Optional[ControllerConfig] = None,
    ) -> None:
        self.junction_id = junction_id
        self.mode_override = mode_override
        self._cfg = config or get_config()
        self._historical = historical_density or DEFAULT_HISTORICAL_DENSITY

        # Core components
        self._predictor = JunctionPredictor(junction_id, self._cfg.prediction_window)
        self._traffic_state = TrafficStateEngine(self._cfg)
        self._historical_store = HistoricalProfileStore(self._cfg)
        self._safety = SafetyValidator(self._cfg)
        self._health = HealthTracker(self._cfg.health_window_size)

        # Phase tracking
        self._current_cycle_sec: int = FALLBACK_CYCLE_SEC
        self._current_phase: Optional[str] = None
        self._phase_last_green: dict[str, float] = {}  # phase → timestamp of last green
        self._decision_count: int = 0

    @property
    def health(self) -> HealthTracker:
        """Expose health tracker for external monitoring."""
        return self._health

    @property
    def historical_store(self) -> HistoricalProfileStore:
        """Expose historical store for persistence."""
        return self._historical_store

    # ------------------------------------------------------------------
    # Main decision method
    # ------------------------------------------------------------------

    def decide(self, event: dict) -> dict:
        """Consume one event from Person A's feed and return the full
        enhanced output contract dict."""
        t_start = time.time()
        self._decision_count += 1
        timestamp = event.get("timestamp",
                              datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        lanes: dict[str, dict] = event.get("lanes", {})
        cfg = self._cfg

        # ---- 1. Confidence scoring ----
        det_conf: float = event.get("detection_confidence", 0.85)
        weather_flag: str = event.get("weather_flag", "clear")
        confidence = compute_confidence(det_conf, weather_flag)
        conf_band = confidence_band(confidence, cfg)

        # ---- 2. Traffic state update (smoothing + derived metrics) ----
        self._traffic_state.update(lanes, confidence, self._current_phase)

        # ---- 3. Blend live vs. historical density ----
        blended_density: dict[str, float] = {}
        for lane_id, lane_data in lanes.items():
            live = float(lane_data.get("queue_length", lane_data.get("density", 0)))
            hist = self._historical.get(lane_id, live)
            # Also check historical store
            hist_stored = self._historical_store.get_historical_queue(
                self.junction_id, lane_id
            )
            if hist_stored > 0:
                hist = hist_stored
            blended_density[lane_id] = blend_density(live, hist, confidence)

        # ---- 4. Update predictor with blended density ----
        self._predictor.update({lid: blended_density[lid] for lid in blended_density})

        # Set historical values for ensemble prediction
        hist_values = {}
        for lid in blended_density:
            hv = self._historical_store.get_historical_queue(self.junction_id, lid)
            if hv > 0:
                hist_values[lid] = hv
        if hist_values:
            self._predictor.set_historical_values(hist_values)

        trend: TrendLabel = congestion_label(self._predictor)

        # ---- 5. Anomaly detection ----
        anomaly_level = "normal"
        for lane_id in blended_density:
            level, _ = self._historical_store.detect_anomaly(
                self.junction_id, lane_id, blended_density[lane_id]
            )
            if level != "normal":
                anomaly_level = level  # take worst anomaly

        # ---- 6. Record to historical store ----
        for lane_id in blended_density:
            ls = self._traffic_state.get_lane(lane_id)
            self._historical_store.record(
                self.junction_id, lane_id,
                queue=ls.smoothed_queue,
                speed=ls.smoothed_speed,
                density=ls.density,
                growth=ls.growth_rate,
            )

        # ---- 7. Event mode ----
        weather_for_mode = weather_flag if is_cautious(confidence) else None
        active_mode_name = select_mode(
            manual_override=self.mode_override,
            weather_flag=weather_for_mode if weather_for_mode else
                         (weather_flag if weather_flag.lower() in ("rain", "fog", "snow", "night") else None),
        )
        mode: ModeProfile = get_mode_params(active_mode_name)

        # ---- 8. Priority evaluation ----
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

        priority: PriorityResult = evaluate_priority(emergency_event, brts_event,
                                                      config=cfg)

        # ---- 9. Emergency override — skip normal algorithm ----
        if priority.emergency_triggered:
            em_approach = priority.emergency_approach or "north"
            hold_sec = int(priority.emergency_hold_sec)
            reason_str, all_factors = build_reason(
                dominant_approach=em_approach,
                dominant_queue=self._approx_queue(blended_density, em_approach),
                secondary_approach="other",
                secondary_queue=0,
                recommended_cycle_sec=hold_sec,
                confidence=confidence,
                weather_flag=weather_flag,
                priority=priority,
            )
            # Safety: emergency bypass
            self._safety.validate(f"{em_approach}_green", hold_sec,
                                   emergency_override=True)
            self._current_phase = f"{em_approach}_green"

            latency = (time.time() - t_start) * 1000
            self._health.record_decision(
                phase=self._current_phase, cycle_sec=hold_sec,
                latency_ms=latency, emergency=True,
            )
            return self._contract(
                timestamp=timestamp, cycle_sec=hold_sec,
                phase=f"{em_approach}_green", confidence=confidence,
                mode=active_mode_name, trend=trend, priority=priority,
                reason=reason_str, anomaly_level=anomaly_level,
                all_factors=all_factors,
            )

        # ---- 10. Phase starvation tracking (Improvement #10, #11) ----
        now_ts = time.time()
        starvation_sec: dict[str, float] = {}
        for phase_name in PHASE_DEFINITIONS:
            last_green = self._phase_last_green.get(phase_name, now_ts)
            if self._current_phase == phase_name:
                starvation_sec[phase_name] = 0.0
                self._phase_last_green[phase_name] = now_ts
            else:
                starvation_sec[phase_name] = now_ts - last_green

        # ---- 11. Enhanced max-pressure calculation ----
        pressure_scores: dict[str, float] = {}
        growth_rates_by_approach: dict[str, float] = {}

        for phase_name, phase_def in PHASE_DEFINITIONS.items():
            approach = phase_def["approach"]
            upstream_lanes = phase_def["upstream_lanes"]
            downstream_lanes = phase_def["downstream_lanes"]

            # Get approach-level traffic state
            up_state = self._traffic_state.get_approach_state(upstream_lanes)
            down_state = self._traffic_state.get_approach_state(downstream_lanes)

            upstream_q = up_state["total_queue"]
            downstream_q = down_state["total_queue"]

            # --- Base pressure ---
            base_pressure = (upstream_q - downstream_q) * mode.pressure_weight

            # --- Growth bonus (Improvement #1, #2) ---
            growth_bonus = (
                cfg.growth_bonus_weight * up_state["total_growth"]
                + cfg.acceleration_bonus_weight * up_state["total_acceleration"]
            ) * mode.aggressiveness

            # --- Prediction bonus (Improvement #6) ---
            predicted_upstream = sum(
                self._predictor.get_predicted_queue(lid) for lid in upstream_lanes
            )
            predicted_downstream = sum(
                self._predictor.get_predicted_queue(lid) for lid in downstream_lanes
            )
            predicted_pressure = (predicted_upstream - predicted_downstream) * mode.pressure_weight
            prediction_bonus = cfg.prediction_bonus_weight * (
                predicted_pressure - base_pressure
            ) * mode.aggressiveness

            # --- Starvation bonus (Improvement #10) ---
            starv_time = starvation_sec.get(phase_name, 0.0)
            if starv_time > cfg.starvation_bonus_start_sec:
                progress = min(1.0, (starv_time - cfg.starvation_bonus_start_sec)
                               / (cfg.max_starvation_sec - cfg.starvation_bonus_start_sec))
                starvation_bonus = cfg.starvation_bonus_max * progress
            else:
                starvation_bonus = 0.0

            # Force service if starved beyond limit (Improvement #11)
            if starv_time >= cfg.max_starvation_sec:
                starvation_bonus = cfg.starvation_bonus_max * 3  # overwhelming bonus

            # --- Downstream / spillback penalty (Improvement #19, #20) ---
            downstream_penalty = 0.0
            if down_state["max_occupancy"] > cfg.spillback_threshold:
                if down_state["max_occupancy"] > cfg.spillback_critical:
                    downstream_penalty = cfg.downstream_penalty_weight * 10.0
                else:
                    progress = ((down_state["max_occupancy"] - cfg.spillback_threshold)
                                / (cfg.spillback_critical - cfg.spillback_threshold))
                    downstream_penalty = cfg.downstream_penalty_weight * progress * 5.0

            # --- Switching penalty (Improvement #13) ---
            switching_pen = 0.0
            if self._current_phase is not None and phase_name != self._current_phase:
                switching_pen = cfg.switching_penalty * mode.switching_penalty_mult

            # --- Final enhanced pressure ---
            enhanced_pressure = (
                base_pressure
                + growth_bonus
                + prediction_bonus
                + starvation_bonus
                - switching_pen
                - downstream_penalty
            )

            pressure_scores[phase_name] = enhanced_pressure
            growth_rates_by_approach[approach] = round(up_state["total_growth"], 3)

        # Apply BRTS boost
        pressure_scores = apply_brts_boost(pressure_scores, priority)

        # ---- 12. Phase selection with hysteresis (Improvement #12) ----
        best_phase = max(pressure_scores, key=lambda p: pressure_scores[p])
        hysteresis = adaptive_hysteresis(confidence, cfg)

        if (self._current_phase is not None
                and best_phase != self._current_phase
                and self._current_phase in pressure_scores):
            margin = pressure_scores[best_phase] - pressure_scores[self._current_phase]
            if margin < hysteresis:
                best_phase = self._current_phase  # not enough margin → keep current

        phase_def = PHASE_DEFINITIONS[best_phase]
        dom_approach = phase_def["approach"]
        sec_approach = "EW" if dom_approach == "NS" else "NS"

        # ---- 13. Adaptive green duration (Improvement #14) ----
        dom_state = self._traffic_state.get_approach_state(phase_def["upstream_lanes"])
        sec_lanes = PHASE_DEFINITIONS[
            "EW_green" if best_phase == "NS_green" else "NS_green"
        ]["upstream_lanes"]
        sec_state = self._traffic_state.get_approach_state(sec_lanes)

        dom_q = dom_state["total_queue"]
        sec_q = sec_state["total_queue"]

        # Adaptive green = base + demand components
        green_duration = (
            cfg.green_base_sec
            + cfg.green_queue_factor * dom_q
            + cfg.green_growth_factor * max(0, dom_state["total_growth"])
        )
        # Add prediction component if rising
        if trend == "rising":
            for lid in phase_def["upstream_lanes"]:
                pred = self._predictor.get_predicted_queue(lid)
                extra = max(0, pred - dom_q)
                green_duration += cfg.green_prediction_factor * extra

        # Add safety margin from mode
        green_duration += mode.safety_margin_sec

        # Clamp to mode bounds
        effective_min = mode.min_green + mode.safety_margin_sec
        raw_cycle = int(max(effective_min, min(mode.max_green, green_duration)))

        # ---- 14. Confidence: cap the delta from the last cycle ----
        proposed_delta = raw_cycle - self._current_cycle_sec
        # Also cap by mode's max_cycle_delta
        if abs(proposed_delta) > mode.max_cycle_delta:
            sign = 1 if proposed_delta > 0 else -1
            proposed_delta = sign * mode.max_cycle_delta
        capped_delta = cap_cycle_delta(proposed_delta, confidence)
        new_cycle = int(self._current_cycle_sec + capped_delta)
        new_cycle = max(mode.min_green, min(mode.max_green, new_cycle))
        self._current_cycle_sec = new_cycle

        # ---- 15. Safety validation (Improvement #32) ----
        safety_result = self._safety.validate(
            best_phase, new_cycle,
            emergency_override=priority.emergency_triggered,
        )
        if safety_result.validated_phase != best_phase:
            best_phase = safety_result.validated_phase
        new_cycle = safety_result.validated_cycle_sec

        # Advance safety timer
        self._safety.advance_time(new_cycle)

        # Update phase tracking
        self._current_phase = best_phase
        self._phase_last_green[best_phase] = now_ts

        # ---- 16. Decision confidence (Improvement #33) ----
        sorted_pressures = sorted(pressure_scores.values(), reverse=True)
        pressure_margin = sorted_pressures[0] - sorted_pressures[1] if len(sorted_pressures) > 1 else sorted_pressures[0]

        # Prediction agreement: check if all predictors agree on trend direction
        pred_agreement = 1.0
        if trend == "stable":
            pred_agreement = 0.8  # less confident when stable

        # Historical agreement
        hist_agreement = 1.0
        if anomaly_level == "extreme_anomaly":
            hist_agreement = 0.3
        elif anomaly_level == "high_anomaly":
            hist_agreement = 0.5
        elif anomaly_level == "elevated":
            hist_agreement = 0.7

        decision_conf = compute_decision_confidence(
            sensor_confidence=confidence,
            pressure_margin=pressure_margin,
            prediction_agreement=pred_agreement,
            historical_agreement=hist_agreement,
            config=cfg,
        )

        # ---- 17. Prediction uncertainty ----
        avg_uncertainty = 0.0
        uncert_count = 0
        for lid in phase_def["upstream_lanes"]:
            u = self._predictor.get_prediction_uncertainty(lid)
            if u > 0:
                avg_uncertainty += u
                uncert_count += 1
        if uncert_count > 0:
            avg_uncertainty /= uncert_count

        # ---- 18. Build reason (quantitative) ----
        dom_queue_int = int(round(dom_q))
        sec_queue_int = int(round(sec_q))
        predicted_extra: Optional[float] = None
        if trend == "rising":
            predicted_extra = max(
                0.0,
                self._predictor.get_predicted_queue(phase_def["upstream_lanes"][0]) - dom_q,
            )

        # Get downstream penalty for explanation
        down_state_final = self._traffic_state.get_approach_state(phase_def["downstream_lanes"])
        ds_penalty_val = 0.0
        if down_state_final["max_occupancy"] > cfg.spillback_threshold:
            ds_penalty_val = down_state_final["max_occupancy"]

        reason_str, all_factors = build_reason(
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
            pressure_scores=pressure_scores,
            growth_rates=growth_rates_by_approach,
            starvation_sec=starvation_sec,
            decision_confidence=decision_conf,
            anomaly_level=anomaly_level,
            downstream_penalty=ds_penalty_val,
            prediction_uncertainty=avg_uncertainty if avg_uncertainty > 0 else None,
        )

        # ---- 19. Health tracking ----
        latency = (time.time() - t_start) * 1000
        self._health.record_decision(
            phase=best_phase, cycle_sec=new_cycle,
            latency_ms=latency,
            emergency=priority.emergency_triggered,
            brts=priority.brts_triggered,
            safety_violation=not safety_result.is_safe,
            queue_on_approach=dom_q,
        )

        # Record predictions for future error tracking
        for lid in blended_density:
            pred_q = self._predictor.get_predicted_queue(lid)
            self._health.record_prediction(lid, pred_q)

        # Update prediction actuals from previous decisions
        self._health.update_prediction_actuals(
            {lid: blended_density[lid] for lid in blended_density}
        )

        return self._contract(
            timestamp=timestamp, cycle_sec=new_cycle, phase=best_phase,
            confidence=confidence, mode=active_mode_name, trend=trend,
            priority=priority, reason=reason_str,
            # Enhanced fields
            decision_confidence=decision_conf,
            growth_rates=growth_rates_by_approach,
            anomaly_level=anomaly_level,
            starvation_sec=starvation_sec,
            pressure_scores=pressure_scores,
            prediction_uncertainty=avg_uncertainty,
            all_factors=all_factors,
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
        # Enhanced fields
        decision_confidence: Optional[float] = None,
        growth_rates: Optional[dict] = None,
        anomaly_level: str = "normal",
        starvation_sec: Optional[dict] = None,
        pressure_scores: Optional[dict] = None,
        prediction_uncertainty: float = 0.0,
        all_factors: Optional[list] = None,
    ) -> dict:
        """Assemble the full enhanced output contract dict."""
        contract = {
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
            # --- Enhanced fields (backward-compatible additions) ---
            "decision_confidence": round(decision_confidence, 3) if decision_confidence else None,
            "growth_rates": growth_rates or {},
            "anomaly_level": anomaly_level,
            "starvation_sec": {k: round(v, 1) for k, v in (starvation_sec or {}).items()},
            "pressure_scores": {k: round(v, 2) for k, v in (pressure_scores or {}).items()},
            "prediction_uncertainty": round(prediction_uncertainty, 3),
            "all_factors": all_factors or [],
        }
        return contract

    @staticmethod
    def _approx_queue(blended_density: dict[str, float], approach: str) -> int:
        """Rough total queue for an approach."""
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

    print("\n=== 10-step stream (rising congestion) ===")
    ctrl2 = MaxPressureController("junction_01")
    for i, ev in enumerate(event_stream(10, scenario="congested")):
        d = ctrl2.decide(ev)
        print(f"  Step {i}: cycle={d['recommended_cycle_time_sec']}s "
              f"phase={d['phase']} conf={d['confidence']} "
              f"trend={d['predicted_congestion_5min']} "
              f"decision_conf={d['decision_confidence']} "
              f"anomaly={d['anomaly_level']}")

    print("\n=== Controller Health Report ===")
    for k, v in ctrl2.health.report().items():
        print(f"  {k:35s} = {v}")
