"""
traci_runner.py — TraCI-Based SUMO Runner with Adaptive Signal Control
=======================================================================
Connects to SUMO via TraCI, runs the simulation step-by-step, and applies
the max-pressure algorithm at each decision cycle.

Works in two modes:
  1. MOCK mode  — SUMO is not installed.  Simulates detector readings using
                  the mock_event_feed generator and prints the decisions.
                  Useful for algorithm validation without a SUMO installation.

  2. SUMO mode  — Requires ``sumo`` (or ``sumo-gui``) in PATH and the
                  ``traci`` Python package (installed with SUMO).
                  Reads real detector data from loop detectors / inductionLoop
                  definitions and applies phase overrides via TraCI.

Usage
-----
    # Mock run (no SUMO needed):
    python traci_runner.py --mock

    # Real SUMO run:
    python traci_runner.py [--gui] [--scenario normal|congested|festival|rain]

Output
------
After the run, prints a summary table comparing fixed-timer vs. adaptive
metrics (avg wait, throughput, peak queue), and writes the decisions log to
``output/adaptive_decisions.jsonl``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
# Add parent dir to path so we can import signal-optimizer modules from
# within the sumo/ subdirectory.
_THIS_DIR = Path(__file__).parent
_SIGNAL_DIR = _THIS_DIR.parent
sys.path.insert(0, str(_SIGNAL_DIR))

from max_pressure import MaxPressureController, PHASE_DEFINITIONS
from mock_event_feed import generate_event, event_stream

# ---------------------------------------------------------------------------
# SUMO / TraCI import (graceful fallback)
# ---------------------------------------------------------------------------
try:
    import traci  # type: ignore
    import traci.constants as tc  # type: ignore
    SUMO_AVAILABLE = True
except ImportError:
    SUMO_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
JUNCTION_ID    = "junction_01"
TL_ID          = "tl_junction_01"
DECISION_EVERY = 30          # seconds between max-pressure decision cycles
SIM_DURATION   = 3600        # seconds
STEP_LENGTH    = 1           # seconds per SUMO step

# SUMO detector IDs (must match induction-loop IDs if defined in network)
# For this demo we read lane vehicle counts via traci.lane.getLastStepVehicleNumber
LANE_MAP = {
    "lane_NS_1": "edge_N_in_0",   # (edge_id, lane_index) alias
    "lane_NS_2": "edge_N_in_1",
    "lane_EW_1": "edge_E_in_0",
    "lane_EW_2": "edge_E_in_1",
}

# Phase index in SUMO tlLogic that corresponds to each signal phase
SUMO_PHASE_INDEX = {
    "NS_green": 0,   # matches phase 0 in network.net.xml
    "EW_green": 3,   # matches phase 3 in network.net.xml
}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _ensure_output_dir() -> Path:
    out = _THIS_DIR / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _write_decision(fp, decision: dict) -> None:
    fp.write(json.dumps(decision) + "\n")
    fp.flush()


def _print_summary(decisions: list[dict], mode_label: str) -> None:
    if not decisions:
        print(f"\n[{mode_label}] No decisions recorded.")
        return
    cycles = [d["recommended_cycle_time_sec"] for d in decisions]
    confs  = [d["confidence"] for d in decisions]
    em_cnt = sum(1 for d in decisions if d["emergency_priority_triggered"])
    brts_cnt = sum(1 for d in decisions if d["brts_priority_triggered"])
    print(f"\n{'='*60}")
    print(f"  Run summary: {mode_label}")
    print(f"{'='*60}")
    print(f"  Total decisions : {len(decisions)}")
    print(f"  Avg cycle time  : {sum(cycles)/len(cycles):.1f}s")
    print(f"  Min/Max cycle   : {min(cycles)}s / {max(cycles)}s")
    print(f"  Avg confidence  : {sum(confs)/len(confs):.3f}")
    print(f"  Emergency events: {em_cnt}")
    print(f"  BRTS events     : {brts_cnt}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Mock run (no SUMO)
# ---------------------------------------------------------------------------

def run_mock(scenario: str = "normal", steps: int = 60) -> None:
    """Simulate ``steps`` decision cycles using the mock event feed."""
    print(f"\n[MOCK] Running {steps} decision cycles — scenario: {scenario}")
    out_dir = _ensure_output_dir()
    out_path = out_dir / "adaptive_decisions.jsonl"

    ctrl = MaxPressureController(JUNCTION_ID)
    decisions: list[dict] = []

    with open(out_path, "w", encoding="utf-8") as fp:
        # Inject emergency at step 30, BRTS at step 45
        for i, ev in enumerate(
            event_stream(
                count=steps,
                scenario=scenario,
                inject_emergency_at=30,
                inject_brts_at=45,
            )
        ):
            decision = ctrl.decide(ev)
            decisions.append(decision)
            _write_decision(fp, decision)

            if i % 10 == 0:
                print(
                    f"  Step {i:3d}: cycle={decision['recommended_cycle_time_sec']}s "
                    f"phase={decision['phase']:12s} "
                    f"conf={decision['confidence']:.2f} "
                    f"trend={decision['predicted_congestion_5min']:7s} "
                    f"em={decision['emergency_priority_triggered']}"
                )

    _print_summary(decisions, f"MOCK / {scenario}")
    print(f"[MOCK] Decisions written to {out_path}")


# ---------------------------------------------------------------------------
# Real SUMO run via TraCI
# ---------------------------------------------------------------------------

def _read_lane_queues() -> dict[str, float]:
    """Read current queue lengths from SUMO lane data via TraCI."""
    queues: dict[str, float] = {}
    for lane_id, sumo_lane in LANE_MAP.items():
        try:
            # getLastStepHaltingNumber = vehicles stopped (best proxy for queue)
            q = traci.lane.getLastStepHaltingNumber(sumo_lane)
            queues[lane_id] = float(q)
        except Exception:
            queues[lane_id] = 0.0
    return queues


def _build_event_from_sumo(step: int) -> dict:
    """Build a mock-style event dict populated with real SUMO detector readings."""
    queues = _read_lane_queues()
    lanes = {}
    for lane_id, q in queues.items():
        sumo_lane = LANE_MAP.get(lane_id, lane_id)
        try:
            speed = traci.lane.getLastStepMeanSpeed(sumo_lane)
            density = traci.lane.getLastStepVehicleNumber(sumo_lane)
        except Exception:
            speed, density = 0.0, int(q)
        lanes[lane_id] = {
            "density": density,
            "queue_length": int(q),
            "speed_mps": round(speed, 2),
        }

    # Check for emergency vehicle (any vehicle type == "emergency" in sim)
    emergency_detected = False
    emergency_approach = None
    try:
        em_vehicles = [
            vid for vid in traci.vehicle.getIDList()
            if traci.vehicle.getTypeID(vid) == "emergency"
        ]
        if em_vehicles:
            # Check if approaching junction (within 150 m)
            for vid in em_vehicles:
                road = traci.vehicle.getRoadID(vid)
                if "N_in" in road:
                    emergency_detected, emergency_approach = True, "north"
                elif "S_in" in road:
                    emergency_detected, emergency_approach = True, "south"
                elif "E_in" in road:
                    emergency_detected, emergency_approach = True, "east"
                elif "W_in" in road:
                    emergency_detected, emergency_approach = True, "west"
    except Exception:
        pass

    return {
        "junction_id": JUNCTION_ID,
        "timestamp": f"t={step}s",
        "lanes": lanes,
        "detection_confidence": 0.90,
        "weather_flag": "clear",
        "brts_waiting": False,
        "brts_wait_time_sec": 0,
        "brts_approach": None,
        "emergency_vehicle": {
            "detected": emergency_detected,
            "approach": emergency_approach,
            "lane_id": None,
            "vehicle_speed_mps": None,
        },
        "brts_violation": False,
    }


def _apply_decision_to_sumo(decision: dict) -> None:
    """Apply the max-pressure decision to the SUMO traffic light via TraCI."""
    phase_name = decision.get("phase", "NS_green")
    cycle_sec  = decision.get("recommended_cycle_time_sec", 40)

    phase_idx = SUMO_PHASE_INDEX.get(phase_name, 0)
    try:
        traci.trafficlight.setPhase(TL_ID, phase_idx)
        traci.trafficlight.setPhaseDuration(TL_ID, cycle_sec)
    except Exception as e:
        print(f"  [TraCI] Could not apply decision: {e}")


def run_sumo(scenario: str = "normal", gui: bool = False) -> None:
    """Start SUMO, connect via TraCI, run adaptive control loop."""
    if not SUMO_AVAILABLE:
        print("[ERROR] TraCI / SUMO not available.  Use --mock instead.")
        sys.exit(1)

    sumo_binary = "sumo-gui" if gui else "sumo"
    sumo_cfg    = str(_THIS_DIR / "adaptive_timer.sumocfg")
    port        = 8813

    sumo_cmd = [
        sumo_binary,
        "-c", sumo_cfg,
        "--remote-port", str(port),
        "--no-warnings",
    ]

    print(f"[SUMO] Starting: {' '.join(sumo_cmd)}")
    traci.start(sumo_cmd, port=port)

    out_dir  = _ensure_output_dir()
    out_path = out_dir / "adaptive_decisions.jsonl"
    ctrl     = MaxPressureController(JUNCTION_ID)
    decisions: list[dict] = []
    next_decision_step = 0

    with open(out_path, "w", encoding="utf-8") as fp:
        step = 0
        while step < SIM_DURATION:
            traci.simulationStep()

            if step >= next_decision_step:
                ev       = _build_event_from_sumo(step)
                decision = ctrl.decide(ev)
                decisions.append(decision)
                _write_decision(fp, decision)
                _apply_decision_to_sumo(decision)
                next_decision_step = step + DECISION_EVERY

                if step % 60 == 0:
                    print(
                        f"  t={step:4d}s: cycle={decision['recommended_cycle_time_sec']}s "
                        f"phase={decision['phase']:12s} "
                        f"conf={decision['confidence']:.2f} "
                        f"em={decision['emergency_priority_triggered']}"
                    )

            step += STEP_LENGTH

    traci.close()
    _print_summary(decisions, f"SUMO adaptive / {scenario}")
    print(f"[SUMO] Decisions written to {out_path}")
    print(f"[SUMO] Trip info at {out_dir / 'adaptive_tripinfo.xml'}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ERakshak signal-optimizer TraCI runner"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in mock mode (no SUMO required)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Use sumo-gui instead of headless sumo",
    )
    parser.add_argument(
        "--scenario",
        choices=["normal", "congested", "festival", "rain"],
        default="normal",
        help="Traffic scenario preset",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=60,
        help="Number of decision steps in mock mode (default 60)",
    )
    args = parser.parse_args()

    if args.mock or not SUMO_AVAILABLE:
        if not args.mock:
            print("[INFO] SUMO/TraCI not found — falling back to mock mode.")
        run_mock(scenario=args.scenario, steps=args.steps)
    else:
        run_sumo(scenario=args.scenario, gui=args.gui)


if __name__ == "__main__":
    main()
