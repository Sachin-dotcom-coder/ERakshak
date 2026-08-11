"""
zones/zone_utils.py — Lane Assignment & Zone Occupancy Logic
=============================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Handles the spatial logic for assigning tracked vehicles to lanes and
detecting presence in the BRTS corridor. All operations work in
ground-plane (meter) coordinates after homography projection.

Key operations:
- Point-in-polygon testing (which lane is this vehicle in?)
- Per-lane occupancy counting (how many vehicles, what PCU total?)
- BRTS corridor presence detection
- Motion-direction analysis (for violation angle checks)

Uses Shapely for robust polygon operations (handles edge cases like
points exactly on boundaries, degenerate polygons, etc.)

Usage:
    from zones.zone_utils import ZoneManager
    zone_mgr = ZoneManager(zone_config["junction_01"], pcu_factors)
    lane_id = zone_mgr.assign_to_lane((world_x, world_y))
    occupancy = zone_mgr.get_lane_occupancy(tracked_vehicles)
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.prepared import prep

logger = logging.getLogger(__name__)


@dataclass
class LaneOccupancy:
    """Occupancy statistics for a single lane.

    Attributes:
        lane_id: Identifier for this lane (e.g., "lane_1").
        vehicle_count: Raw count of vehicles in this lane.
        pcu_weighted_count: PCU-weighted count using IRC:106 factors.
        vehicle_types: Breakdown by vehicle class {"car": 3, "bus": 1, ...}.
        vehicle_positions: List of (world_x, world_y) positions for queue computation.
        avg_confidence: Mean detection confidence of vehicles in this lane.
    """
    lane_id: str
    vehicle_count: int = 0
    pcu_weighted_count: float = 0.0
    vehicle_types: dict[str, int] = field(default_factory=dict)
    vehicle_positions: list[tuple[float, float]] = field(default_factory=list)
    avg_confidence: float = 0.0


class ZoneManager:
    """Manages lane polygons and BRTS corridor for a single junction.

    Loads polygon definitions from zone_config.yaml and provides spatial
    query operations (point-in-polygon, lane assignment, occupancy counting).

    Uses Shapely's PreparedGeometry for fast repeated point-in-polygon tests
    (important when checking every tracked vehicle every frame).

    Args:
        junction_config: Dict from zone_config.yaml for one junction.
        pcu_factors: Dict mapping vehicle class names to PCU values
                     (e.g., {"car": 1.0, "bus": 3.0, ...}).
    """

    def __init__(self, junction_config: dict, pcu_factors: dict[str, float]) -> None:
        self._config = junction_config
        self._pcu_factors = pcu_factors

        # Build lane polygons (Shapely PreparedGeometry for fast queries)
        self._lane_polygons: dict[str, Polygon] = {}
        self._lane_prepared: dict[str, object] = {}  # PreparedGeometry objects
        self._lane_directions: dict[str, str] = {}

        # BRTS corridor
        self._brts_polygon: Optional[Polygon] = None
        self._brts_prepared: Optional[object] = None
        self._brts_direction_axis: Optional[np.ndarray] = None

        self._is_configured: bool = False

        self._load_zones()

    def _load_zones(self) -> None:
        """Parse zone_config.yaml data into Shapely polygon objects."""
        lanes_config = self._config.get("lanes", {})

        if not lanes_config:
            logger.warning(
                "No lane polygons configured — zone assignment will be unavailable. "
                "Fill in zones/zone_config.yaml with lane polygon coordinates."
            )

        for lane_id, lane_data in lanes_config.items():
            polygon_coords = lane_data.get("polygon", [])
            if not polygon_coords or len(polygon_coords) < 3:
                logger.warning(f"Lane '{lane_id}' has insufficient polygon points — skipping")
                continue

            try:
                poly = Polygon(polygon_coords)
                if not poly.is_valid:
                    logger.warning(f"Lane '{lane_id}' polygon is invalid — attempting fix")
                    poly = poly.buffer(0)  # Common fix for self-intersecting polygons

                self._lane_polygons[lane_id] = poly
                self._lane_prepared[lane_id] = prep(poly)
                self._lane_directions[lane_id] = lane_data.get("direction", "unknown")

            except Exception as e:
                logger.error(f"Failed to create polygon for lane '{lane_id}': {e}")

        # BRTS corridor
        brts_config = self._config.get("brts_corridor", {})
        brts_poly_coords = brts_config.get("polygon") if brts_config else None

        if brts_poly_coords and len(brts_poly_coords) >= 3:
            try:
                self._brts_polygon = Polygon(brts_poly_coords)
                if not self._brts_polygon.is_valid:
                    self._brts_polygon = self._brts_polygon.buffer(0)
                self._brts_prepared = prep(self._brts_polygon)

                direction_axis = brts_config.get("direction_axis")
                if direction_axis:
                    axis = np.array(direction_axis, dtype=np.float64)
                    norm = np.linalg.norm(axis)
                    if norm > 0:
                        self._brts_direction_axis = axis / norm  # Normalize to unit vector
                    else:
                        logger.warning("BRTS direction_axis is zero vector — angle check disabled")

                logger.info("BRTS corridor polygon loaded successfully")

            except Exception as e:
                logger.error(f"Failed to create BRTS corridor polygon: {e}")
        else:
            logger.info("No BRTS corridor configured for this junction")

        if self._lane_polygons:
            self._is_configured = True
            logger.info(
                f"Zone manager configured: {len(self._lane_polygons)} lanes"
                f"{' + BRTS corridor' if self._brts_polygon else ''}"
            )

    def assign_to_lane(
        self, ground_point: tuple[float, float]
    ) -> Optional[str]:
        """Determine which lane a vehicle's ground-plane position falls in.

        Args:
            ground_point: (world_x, world_y) in meters (from homography projection).

        Returns:
            Lane ID string (e.g., "lane_1"), or None if the point doesn't fall
            in any configured lane polygon.
        """
        if not self._is_configured:
            return None

        point = Point(ground_point[0], ground_point[1])

        for lane_id, prepared_poly in self._lane_prepared.items():
            if prepared_poly.contains(point):
                return lane_id

        return None  # Vehicle is outside all lane polygons (e.g., on sidewalk, in between)

    def is_in_brts_corridor(
        self, ground_point: tuple[float, float]
    ) -> bool:
        """Check if a point is inside the BRTS corridor polygon.

        Args:
            ground_point: (world_x, world_y) in meters.

        Returns:
            True if inside the BRTS corridor, False otherwise.
            Returns False if no BRTS corridor is configured.
        """
        if self._brts_prepared is None:
            return False

        point = Point(ground_point[0], ground_point[1])
        return bool(self._brts_prepared.contains(point))

    def compute_angle_to_brts_axis(
        self, motion_vector: tuple[float, float]
    ) -> Optional[float]:
        """Compute the angle between a vehicle's motion vector and the BRTS corridor axis.

        Used for intrusion detection: a vehicle crossing perpendicular to the corridor
        (e.g., making a turn) is NOT an intrusion. Only vehicles moving roughly parallel
        to the corridor axis are flagged.

        Args:
            motion_vector: (dx, dy) displacement vector in ground-plane meters.

        Returns:
            Angle in degrees (0° = perfectly parallel, 90° = perpendicular),
            or None if BRTS direction axis is not configured.
        """
        if self._brts_direction_axis is None:
            return None

        mv = np.array(motion_vector, dtype=np.float64)
        mv_norm = np.linalg.norm(mv)

        if mv_norm < 1e-6:
            # Vehicle is essentially stationary — can't determine direction
            return None

        mv_unit = mv / mv_norm

        # Angle between vectors: cos(θ) = dot(a, b) / (|a| × |b|)
        # Both are unit vectors, so just dot product
        dot = float(np.clip(np.dot(mv_unit, self._brts_direction_axis), -1.0, 1.0))
        angle_rad = math.acos(abs(dot))  # abs() because direction can be either way
        angle_deg = math.degrees(angle_rad)

        return float(angle_deg)

    def get_lane_occupancy(
        self,
        vehicles: list[dict],
    ) -> dict[str, LaneOccupancy]:
        """Compute per-lane occupancy statistics from a list of tracked vehicles.

        Args:
            vehicles: List of dicts with at least:
                - "ground_point": (world_x, world_y) in meters
                - "class_name": vehicle class string
                - "confidence": detection confidence (0–1)
                Each vehicle dict is produced by the tracking pipeline.

        Returns:
            Dict mapping lane_id → LaneOccupancy dataclass.
            Lanes with zero vehicles are included (useful for the event contract).
        """
        # Initialize all lanes with empty occupancy
        occupancy: dict[str, LaneOccupancy] = {
            lane_id: LaneOccupancy(lane_id=lane_id)
            for lane_id in self._lane_polygons
        }

        if not self._is_configured:
            return occupancy

        for vehicle in vehicles:
            pixel_point = vehicle.get("pixel_point") or vehicle.get("ground_point")
            world_point = vehicle.get("world_point") or vehicle.get("ground_point")
            if pixel_point is None:
                continue

            lane_id = self.assign_to_lane(pixel_point)
            if lane_id is None:
                continue  # Vehicle not in any lane

            occ = occupancy[lane_id]
            class_name = vehicle.get("class_name", "car")
            confidence = vehicle.get("confidence", 0.0)

            occ.vehicle_count += 1
            occ.pcu_weighted_count += self._pcu_factors.get(class_name, 1.0)
            occ.vehicle_types[class_name] = occ.vehicle_types.get(class_name, 0) + 1
            if world_point is not None:
                occ.vehicle_positions.append(world_point)

            # Running average of confidence
            n = occ.vehicle_count
            occ.avg_confidence = occ.avg_confidence * (n - 1) / n + confidence / n

        return occupancy

    def get_motion_vector(
        self,
        trajectory: list[tuple[float, float]],
        window: int = 5,
    ) -> Optional[tuple[float, float]]:
        """Compute a smoothed motion vector from a vehicle's recent trajectory.

        Args:
            trajectory: List of (world_x, world_y) positions, most recent last.
            window: Number of recent positions to consider.

        Returns:
            (dx, dy) motion vector in meters, or None if insufficient data.
        """
        if len(trajectory) < 2:
            return None

        recent = trajectory[-window:]
        if len(recent) < 2:
            return None

        # Vector from oldest to newest position in the window
        dx = recent[-1][0] - recent[0][0]
        dy = recent[-1][1] - recent[0][1]
        return (float(dx), float(dy))

    @property
    def is_configured(self) -> bool:
        """Whether lane polygons have been loaded successfully."""
        return self._is_configured

    @property
    def lane_ids(self) -> list[str]:
        """List of configured lane IDs."""
        return list(self._lane_polygons.keys())

    @property
    def has_brts_corridor(self) -> bool:
        """Whether a BRTS corridor polygon is configured."""
        return self._brts_polygon is not None
