"""
queue_length.py — Contiguous queue measurement along lane centerline
=====================================================================
P0-9 FIX: Replaces the "furthest stationary vehicle" definition with
a contiguous-queue definition measured along the lane centerline.

Problem with the old definition (improvements.md §2, item 9):
  One parked or broken-down vehicle far upstream makes the queue look huge.
  Also used straight-line distance, not distance along the lane.

New definition:
  The queue is the chain of slow/stopped vehicles starting at the stop line,
  broken wherever the gap to the next vehicle exceeds gap_max_m.
  Only vehicles within the first gap from the stop line are in the queue.

Also provides:
  - queue_pcu: PCU sum inside the queue (better than metres for Max-Pressure,
    because heavy vehicles take more road space)
  - Hysteresis on the speed threshold (enter at 5 km/h, exit at 8 km/h)
    so the queue does not flicker during stop-and-go

Usage:
    from queue_length import QueueEstimator, queue_length_m
    q_m, q_pcu = queue_length_m(vehicles, v_thr_kmh=5.0)
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Simple functional form (improvements.md §3.5)
# ---------------------------------------------------------------------------

def queue_length_m(
    vehicles,
    v_thr_kmh: float = 5.0,
    gap_max_m: float = 8.0,
    first_gap_max_m: float = 15.0,
    pcu_weights: Optional[dict] = None,
) -> tuple:
    """
    Contiguous queue length measured along the lane centerline.

    Args:
        vehicles: Iterable of vehicle objects. Each must have:
                  .s (float) — distance in metres from stop line along lane centerline.
                  .speed_kmh (float) — current speed.
                  .class_name (str) — for PCU lookup.
        v_thr_kmh: Speed threshold below which a vehicle is considered stopped/queued.
        gap_max_m: Maximum gap between consecutive queued vehicles.
                   Larger gaps break the queue.
        first_gap_max_m: Maximum distance of the first vehicle from the stop line.
                         If the first slow vehicle is farther than this, queue = 0.
        pcu_weights: Optional dict class_name → PCU weight. If None, all vehicles
                     count as 1.0 PCU.

    Returns:
        (queue_m, queue_pcu) — queue length in metres and PCU sum.

    Example:
        vehicles = [v for v in lane.vehicles if v.is_active]
        q_m, q_pcu = queue_length_m(vehicles)
    """
    if pcu_weights is None:
        pcu_weights = {}

    slow = sorted(
        [(v.s, v.class_name) for v in vehicles if v.speed_kmh < v_thr_kmh],
        key=lambda x: x[0],
    )

    if not slow or slow[0][0] > first_gap_max_m:
        return 0.0, 0.0

    q_end = slow[0][0]
    q_pcu = pcu_weights.get(slow[0][1], 1.0)

    for s, cls in slow[1:]:
        if s - q_end > gap_max_m:
            break       # gap: later slow vehicles are not part of this queue
        q_end = s
        q_pcu += pcu_weights.get(cls, 1.0)

    return round(q_end, 2), round(q_pcu, 2)


# ---------------------------------------------------------------------------
# Stateful estimator with hysteresis (improvements.md §3.5)
# ---------------------------------------------------------------------------

@dataclass
class _VehicleQueueState:
    """Per-vehicle hysteresis state."""
    is_queued: bool = False


class QueueEstimator:
    """
    Stateful queue estimator with hysteresis on the speed threshold.

    Vehicles enter the "slow" set at v_enter_kmh and leave at v_exit_kmh.
    This prevents flickering counts during stop-and-go.

    NOTE (P0-4 / naming fix): The value this returns is `queue_fill_ratio`
    (fraction of lane storage capacity occupied by the queue), NOT
    `occupancy_ratio`. The old code called this "occupancy_ratio" but
    that term means fraction of time a detector is covered (from loop-
    detector terminology). To avoid confusion, we use `queue_fill_ratio`.

    Args:
        v_enter_kmh: Speed below which a vehicle joins the queue state.
        v_exit_kmh: Speed above which a vehicle leaves the queue state.
        gap_max_m: Max gap for contiguous queue definition.
        first_gap_max_m: Max distance of first vehicle from stop line.
        pcu_weights: class_name → PCU weight dict.
        lane_capacity_pcu: Storage capacity of the lane in PCU (for fill-ratio).
    """

    def __init__(
        self,
        v_enter_kmh: float = 5.0,
        v_exit_kmh: float = 8.0,
        gap_max_m: float = 8.0,
        first_gap_max_m: float = 15.0,
        pcu_weights: Optional[dict] = None,
        lane_capacity_pcu: float = 120.0,
    ):
        self.v_enter = v_enter_kmh
        self.v_exit = v_exit_kmh
        self.gap_max_m = gap_max_m
        self.first_gap_max_m = first_gap_max_m
        self.pcu_weights = pcu_weights or {}
        self.lane_capacity_pcu = max(1.0, lane_capacity_pcu)
        self._vehicle_state: dict[int, _VehicleQueueState] = {}

    def update(self, vehicles) -> tuple:
        """
        Update queue estimate from the current frame's active vehicles.

        Args:
            vehicles: Iterable with .track_id, .s, .speed_kmh, .class_name.

        Returns:
            (queue_m, queue_pcu, queue_fill_ratio) where:
              queue_m: metres from stop line to end of contiguous queue
              queue_pcu: PCU sum inside the queue
              queue_fill_ratio: queue_pcu / lane_capacity_pcu ∈ [0, 1]
                               (previously mislabelled "occupancy_ratio" — P0-4 fix)
        """
        active_ids = set()

        for v in vehicles:
            active_ids.add(v.track_id)
            state = self._vehicle_state.setdefault(v.track_id, _VehicleQueueState())

            # Hysteresis update
            if state.is_queued:
                if v.speed_kmh > self.v_exit:
                    state.is_queued = False
            else:
                if v.speed_kmh < self.v_enter:
                    state.is_queued = True

        # Remove inactive tracks
        lost = [tid for tid in self._vehicle_state if tid not in active_ids]
        for tid in lost:
            del self._vehicle_state[tid]

        # Compute queue from hysteresis-filtered "slow" vehicles
        slow = sorted(
            [(v.s, v.class_name)
             for v in vehicles
             if self._vehicle_state.get(v.track_id, _VehicleQueueState()).is_queued],
            key=lambda x: x[0],
        )

        if not slow or slow[0][0] > self.first_gap_max_m:
            return 0.0, 0.0, 0.0

        q_end = slow[0][0]
        q_pcu = self.pcu_weights.get(slow[0][1], 1.0)

        for s, cls in slow[1:]:
            if s - q_end > self.gap_max_m:
                break
            q_end = s
            q_pcu += self.pcu_weights.get(cls, 1.0)

        # P0-4 FIX: renamed from occupancy_ratio to queue_fill_ratio
        queue_fill_ratio = min(1.0, q_pcu / self.lane_capacity_pcu)

        return round(q_end, 2), round(q_pcu, 2), round(queue_fill_ratio, 4)


# ---------------------------------------------------------------------------
# Normalised Max-Pressure formula (improvements.md §6.2)
# ---------------------------------------------------------------------------

def normalised_pressure(
    q_in_pcu: float,
    c_in_pcu: float,
    q_out_pcu: float,
    c_out_pcu: float,
    sat_flow: float = 1.0,
) -> float:
    """
    Normalised Max-Pressure per movement (improvements.md §6.2).

    P(m) = s_m × (q_in(m)/C_in(m) − q_out(m)/C_out(m))

    Where:
      q = queue in PCU (contiguous definition, from queue_length_m)
      C = storage capacity of the link in PCU
      s_m = saturation flow of the movement (calibrate from Surat data)

    Spillback protection is built into the formula: when the downstream link
    is full (q_out → C_out), the ratio → 1 and pressure naturally falls.

    Args:
        q_in_pcu: Incoming queue in PCU.
        c_in_pcu: Incoming link capacity in PCU. Must be > 0.
        q_out_pcu: Downstream queue in PCU.
        c_out_pcu: Downstream link capacity in PCU. Must be > 0.
        sat_flow: Saturation flow of the movement (normalised). Default 1.0.

    Returns:
        Normalised pressure value (float). Higher = more benefit from green.
    """
    if c_in_pcu <= 0 or c_out_pcu <= 0:
        logger.warning("normalised_pressure: capacity must be > 0. Returning 0.")
        return 0.0
    return sat_flow * (q_in_pcu / c_in_pcu - q_out_pcu / c_out_pcu)
