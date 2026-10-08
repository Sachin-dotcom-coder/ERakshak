"""
traffic_state/density.py — Per-Lane Vehicle Density & Occupancy
================================================================
Computes per-lane vehicle density, occupancy ratios, and congestion levels.
"""

import logging
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class CongestionLevel(str, Enum):
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    GRIDLOCK = "gridlock"


class DensityEstimator:
    """Per-lane vehicle density and congestion estimation.

    Args:
        lanes_config: Dict from lanes.yaml with lane widths/lengths.
    """

    def __init__(self, lanes_config: Optional[dict] = None) -> None:
        self._lane_areas: dict[str, float] = {}  # lane_id → area_m²
        self._lane_lengths: dict[str, float] = {}

        if lanes_config:
            for lane_id, cfg in lanes_config.get("lanes", {}).items():
                width = cfg.get("width_m", 3.5)
                capacity = cfg.get("max_queue_capacity_m", 100.0)
                self._lane_areas[lane_id] = width * capacity
                self._lane_lengths[lane_id] = capacity

    def compute_density(
        self,
        lane_id: str,
        vehicle_count: int,
        pcu_total: float,
    ) -> dict:
        """Compute density metrics for a lane.

        Args:
            lane_id: Lane identifier.
            vehicle_count: Number of vehicles in the lane.
            pcu_total: PCU-weighted vehicle count.

        Returns:
            Dict with density metrics.
        """
        area = self._lane_areas.get(lane_id, 350.0)  # Default: 3.5m × 100m
        length = self._lane_lengths.get(lane_id, 100.0)

        # Vehicles per 100m of lane
        linear_density = (vehicle_count / length * 100) if length > 0 else 0
        pcu_density = (pcu_total / length * 100) if length > 0 else 0

        # Occupancy ratio (fraction of lane capacity used)
        # Approximate: each PCU occupies ~7m of lane (car length + gap)
        pcu_length_m = 7.0
        occupied_length = pcu_total * pcu_length_m
        occupancy = min(1.0, occupied_length / length) if length > 0 else 0

        # Congestion level
        congestion = self._classify_congestion(occupancy, pcu_density)

        return {
            "vehicle_count": vehicle_count,
            "pcu_total": round(pcu_total, 2),
            "linear_density_per_100m": round(linear_density, 2),
            "pcu_density_per_100m": round(pcu_density, 2),
            "occupancy_ratio": round(occupancy, 3),
            "congestion_level": congestion.value,
        }

    def _classify_congestion(
        self,
        occupancy: float,
        pcu_density: float,
    ) -> CongestionLevel:
        """Classify congestion level from occupancy and density."""
        if occupancy < 0.15:
            return CongestionLevel.FREE_FLOW
        elif occupancy < 0.35:
            return CongestionLevel.LIGHT
        elif occupancy < 0.55:
            return CongestionLevel.MODERATE
        elif occupancy < 0.80:
            return CongestionLevel.HEAVY
        else:
            return CongestionLevel.GRIDLOCK
