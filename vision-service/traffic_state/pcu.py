"""
traffic_state/pcu.py — Confidence-Weighted PCU Calculation (Section 46)
========================================================================
Upgrades PCU counting from simple class weights to confidence-weighted PCU.

PCU_effective = Σ w_class(i) * C_i

Where C_i is the detection/classification confidence for vehicle i.
This prevents uncertain detections from contributing the same weight
as highly reliable ones.
"""

import logging
from typing import Optional

import numpy as np
import yaml

logger = logging.getLogger(__name__)


class PCUCalculator:
    """Confidence-weighted Passenger Car Unit calculator.

    Args:
        pcu_weights: Dict mapping class_name → PCU weight.
        confidence_weighted: Whether to weight PCU by detection confidence.
    """

    # Default IRC:106 PCU weights for Indian traffic
    DEFAULT_WEIGHTS: dict[str, float] = {
        "car": 1.0,
        "bus": 3.0,
        "brts_bus": 3.0,
        "truck": 3.0,
        "two_wheeler": 0.5,
        "auto_rickshaw": 0.8,
        "cycle": 0.2,
    }

    def __init__(
        self,
        pcu_weights: Optional[dict[str, float]] = None,
        confidence_weighted: bool = True,
    ) -> None:
        self._weights = pcu_weights or self.DEFAULT_WEIGHTS
        self._confidence_weighted = confidence_weighted

    @classmethod
    def from_config(cls, config_path: str) -> "PCUCalculator":
        """Create PCUCalculator from classes.yaml config file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            weights = cfg.get("pcu_weights", cls.DEFAULT_WEIGHTS)
            return cls(pcu_weights=weights)
        except Exception as e:
            logger.warning(f"Failed to load PCU config: {e}. Using defaults.")
            return cls()

    def compute_lane_pcu(
        self,
        vehicles: list[dict],
    ) -> tuple[float, float]:
        """Compute total PCU for a set of vehicles in a lane.

        Args:
            vehicles: List of dicts with 'class_name' and 'detection_confidence'.

        Returns:
            (pcu_weighted, pcu_raw) — confidence-weighted and raw PCU totals.
        """
        pcu_raw = 0.0
        pcu_weighted = 0.0

        for v in vehicles:
            class_name = v.get("class_name", "car")
            confidence = v.get("detection_confidence", 1.0)
            class_weight = self._weights.get(class_name, 1.0)

            pcu_raw += class_weight

            if self._confidence_weighted:
                pcu_weighted += class_weight * confidence
            else:
                pcu_weighted += class_weight

        return (pcu_weighted, pcu_raw)

    def compute_per_class_pcu(
        self,
        vehicles: list[dict],
    ) -> dict[str, float]:
        """Compute PCU breakdown by vehicle class.

        Args:
            vehicles: List of vehicle dicts.

        Returns:
            Dict mapping class_name → PCU contribution.
        """
        breakdown: dict[str, float] = {}

        for v in vehicles:
            class_name = v.get("class_name", "car")
            confidence = v.get("detection_confidence", 1.0)
            class_weight = self._weights.get(class_name, 1.0)

            contribution = (
                class_weight * confidence if self._confidence_weighted
                else class_weight
            )
            breakdown[class_name] = breakdown.get(class_name, 0.0) + contribution

        return breakdown

    def compute_per_movement_pcu(
        self,
        vehicles: list[dict],
    ) -> dict[str, float]:
        """Compute PCU breakdown by maneuver type.

        Args:
            vehicles: List of dicts with 'maneuver', 'class_name', 'detection_confidence'.

        Returns:
            Dict mapping maneuver → PCU total.
        """
        by_movement: dict[str, float] = {}

        for v in vehicles:
            maneuver = v.get("maneuver", "unknown")
            class_name = v.get("class_name", "car")
            confidence = v.get("detection_confidence", 1.0)
            class_weight = self._weights.get(class_name, 1.0)

            contribution = (
                class_weight * confidence if self._confidence_weighted
                else class_weight
            )
            by_movement[maneuver] = by_movement.get(maneuver, 0.0) + contribution

        return by_movement

    def get_weight(self, class_name: str) -> float:
        """Get PCU weight for a vehicle class."""
        return self._weights.get(class_name, 1.0)

    def compute_pcu_confidence(
        self,
        vehicles: list[dict],
    ) -> float:
        """Estimate confidence in the PCU calculation.

        Based on the average classification confidence of contributing vehicles.

        Args:
            vehicles: List of vehicle dicts.

        Returns:
            PCU confidence in [0.0, 1.0].
        """
        if not vehicles:
            return 0.5

        confidences = [v.get("detection_confidence", 1.0) for v in vehicles]
        # Weight by PCU contribution (heavy vehicles matter more)
        weighted_conf = 0.0
        total_weight = 0.0
        for v in vehicles:
            w = self._weights.get(v.get("class_name", "car"), 1.0)
            c = v.get("detection_confidence", 1.0)
            weighted_conf += w * c
            total_weight += w

        if total_weight <= 0:
            return 0.5

        return float(np.clip(weighted_conf / total_weight, 0.0, 1.0))
