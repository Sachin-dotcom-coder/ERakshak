"""
controller_config.py — Centralized Configuration for the Signal Optimizer
==========================================================================
Single source of truth for all tunable parameters.  Every module reads
its constants from here so that the controller can be retuned without
touching algorithm code.

Supports optional YAML file loading for external calibration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import json


# ---------------------------------------------------------------------------
# Master configuration
# ---------------------------------------------------------------------------

@dataclass
class ControllerConfig:
    """All tunable parameters for the signal optimizer."""

    # --- Temporal smoothing (Improvement #23, #24) ---
    smoothing_alpha: float = 0.35          # EMA alpha for queue smoothing
    smoothing_alpha_high_conf: float = 0.5 # α when confidence ≥ 0.80
    smoothing_alpha_low_conf: float = 0.15 # α when confidence < 0.40

    # --- Hysteresis (Improvement #12, #25) ---
    hysteresis_threshold: float = 3.0      # minimum pressure advantage to switch phase
    hysteresis_high_conf: float = 2.0      # threshold when confidence ≥ 0.80
    hysteresis_low_conf: float = 5.0       # threshold when confidence < 0.60

    # --- Switching cost (Improvement #13) ---
    switching_penalty: float = 2.0         # pressure penalty for phase change
    yellow_clearance_sec: float = 3.0      # yellow time (seconds)
    all_red_clearance_sec: float = 2.0     # all-red clearance (seconds)

    # --- Phase starvation (Improvement #10, #11) ---
    max_starvation_sec: float = 90.0       # hard limit — force service after this
    starvation_bonus_start_sec: float = 20.0  # bonus starts after this wait
    starvation_bonus_max: float = 5.0      # maximum additive bonus

    # --- Downstream / Spillback (Improvement #19, #20) ---
    downstream_penalty_weight: float = 0.5 # multiplier for downstream congestion
    spillback_threshold: float = 0.80      # queue_occupancy danger level
    spillback_critical: float = 0.95       # near-full → strong penalty
    default_lane_capacity: int = 40        # max vehicles per lane (for occupancy calc)

    # --- Growth weighting (Improvement #1, #2, #5) ---
    growth_bonus_weight: float = 0.4       # weight for queue growth in enhanced pressure
    acceleration_bonus_weight: float = 0.1 # weight for queue acceleration

    # --- Predicted pressure (Improvement #6) ---
    predicted_pressure_alpha: float = 0.3  # blend: α*current + (1-α)*predicted
    prediction_bonus_weight: float = 0.3   # weight of prediction bonus in enhanced pressure

    # --- Congestion score (Improvement #3, #4) ---
    congestion_queue_weight: float = 0.5   # weight of queue in congestion score
    congestion_speed_weight: float = 0.3   # weight of speed in congestion score
    congestion_growth_weight: float = 0.2  # weight of growth in congestion score
    free_flow_speed_mps: float = 8.33      # 30 km/h default free-flow speed

    # --- Adaptive green duration (Improvement #14) ---
    green_base_sec: float = 25.0           # base green time
    green_queue_factor: float = 0.5        # seconds per queued vehicle
    green_growth_factor: float = 1.0       # seconds per veh/min growth
    green_prediction_factor: float = 0.3   # seconds per predicted extra vehicle

    # --- Prediction ensemble (Improvement #7) ---
    ensemble_weight_linear: float = 0.35
    ensemble_weight_ma: float = 0.20
    ensemble_weight_ema: float = 0.20
    ensemble_weight_historical: float = 0.25

    # --- Prediction (existing + extensions) ---
    prediction_window: int = 10            # rolling window size (samples)
    prediction_horizon: int = 10           # forecast horizon (samples ahead)
    rising_threshold: float = 0.5          # veh/sample slope for "rising"
    falling_threshold: float = 0.5         # veh/sample slope for "falling"

    # --- Confidence bands (Improvement #22) ---
    confidence_normal: float = 0.80        # ≥ this = normal adaptive mode
    confidence_cautious: float = 0.60      # ≥ this = cautious mode
    confidence_smoothed: float = 0.40      # ≥ this = heavily smoothed mode
    # < smoothed = fallback mode

    # --- BRTS priority (Improvement #28) ---
    brts_smooth_start_sec: float = 10.0    # wait time when bonus begins (0 bonus)
    brts_smooth_full_sec: float = 60.0     # wait time at which bonus reaches max
    brts_max_bonus: float = 3.0            # maximum pressure boost

    # --- Emergency (Improvement #27) ---
    emergency_hold_sec: float = 15.0       # minimum green hold for emergency
    emergency_approach_distance_m: float = 150.0  # default approach distance

    # --- Safety (Improvement #32) ---
    min_green_lock_sec: float = 7.0        # absolute min green before any switch
    max_cycle_sec: int = 180
    min_cycle_sec: int = 20

    # --- Historical (Improvement #8, #9) ---
    historical_time_slot_min: int = 5      # granularity of historical buckets
    anomaly_z_elevated: float = 1.5        # z-score threshold for "elevated"
    anomaly_z_high: float = 2.0            # z-score for "high_anomaly"
    anomaly_z_extreme: float = 3.0         # z-score for "extreme_anomaly"

    # --- Health metrics (Improvement #43–45) ---
    health_window_size: int = 100          # rolling window for health stats

    # --- Decision confidence (Improvement #33) ---
    decision_conf_sensor_weight: float = 0.30
    decision_conf_margin_weight: float = 0.35
    decision_conf_prediction_weight: float = 0.20
    decision_conf_historical_weight: float = 0.15


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_CONFIG: Optional[ControllerConfig] = None


def get_config() -> ControllerConfig:
    """Return the global configuration, creating a default if needed."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = ControllerConfig()
    return _CONFIG


def set_config(config: ControllerConfig) -> None:
    """Replace the global configuration."""
    global _CONFIG
    _CONFIG = config


def load_config_from_json(path: str | Path) -> ControllerConfig:
    """Load configuration from a JSON file, merging with defaults."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cfg = ControllerConfig()
    for key, value in data.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)
    set_config(cfg)
    return cfg


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cfg = get_config()
    print("=== Controller Configuration ===")
    for k, v in cfg.__dict__.items():
        print(f"  {k:40s} = {v}")
    print(f"\nTotal parameters: {len(cfg.__dict__)}")
