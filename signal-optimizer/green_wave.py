"""
green_wave.py — Multi-Junction Coordination
============================================
Coordinates signal timing across 2–3 sequential junctions to enable a
"green wave" — a progression of green phases timed so a vehicle travelling
at the design speed hits green at each junction in sequence.

Also handles **emergency corridor cascading**: when an emergency vehicle is
detected, propagate the green override to the next 1–2 junctions along its
path so the corridor is clear before the vehicle arrives.

Architecture
------------
A :class:`GreenWaveCoordinator` owns multiple :class:`MaxPressureController`
instances (one per junction).  On each step it:
  1. Calls each controller's ``decide()`` individually (local decision).
  2. Adjusts each junction's next green-start time so the phase progression
     aligns with the design travel speed between junctions.
  3. If an emergency corridor is active, overrides downstream junctions
     unconditionally.
"""

from __future__ import annotations

import datetime
import time
from dataclasses import dataclass, field
from typing import Optional

from max_pressure import MaxPressureController
from mock_event_feed import generate_event

# ---------------------------------------------------------------------------
# Coordinator configuration
# ---------------------------------------------------------------------------

@dataclass
class JunctionConfig:
    """Static config for one junction in the corridor."""
    junction_id: str
    distance_to_next_m: Optional[float] = None   # metres to the next junction
    design_speed_mps: float = 8.33               # 30 km/h default


@dataclass
class CoordinatedDecision:
    """Combined output for all junctions in one coordination step."""
    timestamp: str
    decisions: dict[str, dict] = field(default_factory=dict)  # junction_id → contract
    emergency_corridor_active: bool = False
    offset_recommendations: dict[str, float] = field(default_factory=dict)  # junction_id → offset (s)


# ---------------------------------------------------------------------------
# Coordinator
# ---------------------------------------------------------------------------

class GreenWaveCoordinator:
    """Manages adaptive signal control for a chain of junctions.

    Parameters
    ----------
    junction_configs:
        Ordered list of :class:`JunctionConfig` objects from upstream to
        downstream (the direction of travel for the green wave).
    mode_override:
        Optional mode string applied to all junctions.
    """

    def __init__(
        self,
        junction_configs: list[JunctionConfig],
        mode_override: Optional[str] = None,
    ) -> None:
        self.configs = junction_configs
        self._controllers: dict[str, MaxPressureController] = {
            cfg.junction_id: MaxPressureController(
                junction_id=cfg.junction_id,
                mode_override=mode_override,
            )
            for cfg in junction_configs
        }
        self._emergency_path: list[str] = []   # junction IDs in emergency corridor

    # ------------------------------------------------------------------
    # Main coordination step
    # ------------------------------------------------------------------

    def step(self, events: dict[str, dict]) -> CoordinatedDecision:
        """Execute one coordination step.

        Parameters
        ----------
        events:
            Mapping of junction_id → event dict (from Person A or mock feed).
            Missing junctions receive a default empty event.

        Returns
        -------
        CoordinatedDecision
        """
        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        raw_decisions: dict[str, dict] = {}

        # --- 1. Local decisions ---
        for cfg in self.configs:
            jid = cfg.junction_id
            ev = events.get(jid, generate_event(junction_id=jid))
            decision = self._controllers[jid].decide(ev)
            raw_decisions[jid] = decision

        # --- 2. Emergency corridor detection ---
        corridor_active = False
        for jid, dec in raw_decisions.items():
            if dec.get("emergency_priority_triggered"):
                corridor_active = True
                self._emergency_path = self._downstream_ids(jid)
                break

        # --- 3. Apply emergency cascade to downstream junctions ---
        if corridor_active and self._emergency_path:
            for jid in self._emergency_path:
                if jid in raw_decisions:
                    # Override to force green on the emergency approach
                    dec = raw_decisions[jid]
                    dec["emergency_priority_triggered"] = True
                    dec["phase"] = "NS_green"  # simplified; real impl uses vehicle path
                    dec["reason"] = (
                        "Emergency corridor cascaded from upstream junction; "
                        "pre-clearing approach."
                    )

        # --- 4. Compute green-wave offsets ---
        offsets: dict[str, float] = {}
        cumulative_offset = 0.0
        for i, cfg in enumerate(self.configs[:-1]):
            next_cfg = self.configs[i + 1]
            if cfg.distance_to_next_m:
                travel_time = cfg.distance_to_next_m / cfg.design_speed_mps
            else:
                travel_time = 0.0
            cumulative_offset += travel_time
            offsets[next_cfg.junction_id] = round(cumulative_offset, 1)
        offsets[self.configs[0].junction_id] = 0.0

        return CoordinatedDecision(
            timestamp=now,
            decisions=raw_decisions,
            emergency_corridor_active=corridor_active,
            offset_recommendations=offsets,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _downstream_ids(self, from_junction_id: str) -> list[str]:
        """Return the IDs of the next 1–2 junctions downstream."""
        ids = [cfg.junction_id for cfg in self.configs]
        try:
            idx = ids.index(from_junction_id)
        except ValueError:
            return []
        return ids[idx + 1: idx + 3]   # next 1–2


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    configs = [
        JunctionConfig("junction_01", distance_to_next_m=300, design_speed_mps=8.33),
        JunctionConfig("junction_02", distance_to_next_m=250, design_speed_mps=8.33),
        JunctionConfig("junction_03"),
    ]
    coordinator = GreenWaveCoordinator(configs)

    print("=== Normal coordination step ===")
    result = coordinator.step({})
    for jid, dec in result.decisions.items():
        print(f"  {jid}: cycle={dec['recommended_cycle_time_sec']}s "
              f"phase={dec['phase']}")
    print("  Offsets:", result.offset_recommendations)

    print("\n=== Emergency corridor step ===")
    em_event = generate_event("junction_01", emergency_approach="north")
    result2 = coordinator.step({"junction_01": em_event})
    for jid, dec in result2.decisions.items():
        print(f"  {jid}: emergency={dec['emergency_priority_triggered']} "
              f"phase={dec['phase']}")
    print("  Corridor active:", result2.emergency_corridor_active)
