"""
brts_zone.py — Footprint-overlap zone assignment for BRTS corridor
===================================================================
Implements the improved zone test that uses both:
1. A bottom-strip footprint overlap ratio (not just the ground point)
2. The ground-contact point being inside the polygon

Design rationale (improvements.md §B4):
- Simple ground-point test fails for tall vehicles near the separator (roof
  can lean over the BRTS boundary while wheels remain in Lane 1).
- Wide bounding boxes on two-wheelers (rider + body) shift the effective
  ground point with box jitter.
- Using a footprint overlap ratio + hysteresis fixes both issues.

Requires: shapely (pip install shapely)
"""

import logging
from typing import Optional, Tuple

import numpy as np

try:
    from shapely.geometry import Polygon, Point, box as shapely_box
    _SHAPELY_AVAILABLE = True
except ImportError:
    _SHAPELY_AVAILABLE = False

logger = logging.getLogger(__name__)


def footprint(bbox: tuple, strip: float = 0.25, shrink: float = 0.15) -> Optional[object]:
    """
    Build a footprint polygon representing the part of the bounding box
    that actually touches the road surface.

    Takes the bottom `strip` fraction of the box height and narrows by
    `shrink` on each side to exclude rider arms, mirrors, etc.

    Args:
        bbox: (x1, y1, x2, y2) in pixel or world coordinates.
        strip: Fraction of box height used as footprint (0.25 = bottom 25%).
        shrink: Fraction to narrow from each side (0.15 = 15% each side).

    Returns:
        Shapely Polygon, or None if shapely is unavailable.
    """
    if not _SHAPELY_AVAILABLE:
        return None
    x1, y1, x2, y2 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    h, w = y2 - y1, x2 - x1
    if h <= 0 or w <= 0:
        return None
    fp_x1 = x1 + shrink * w
    fp_x2 = x2 - shrink * w
    fp_y1 = y2 - strip * h
    fp_y2 = y2
    return Polygon([
        (fp_x1, fp_y1),
        (fp_x2, fp_y1),
        (fp_x2, fp_y2),
        (fp_x1, fp_y2),
    ])


def overlap_ratio(bbox: tuple, zone_poly) -> float:
    """
    Fraction of the footprint that overlaps the zone polygon.

    Args:
        bbox: (x1, y1, x2, y2) bounding box.
        zone_poly: Shapely Polygon of the zone.

    Returns:
        Float in [0.0, 1.0]. 0.0 if shapely unavailable or footprint empty.
    """
    if not _SHAPELY_AVAILABLE or zone_poly is None:
        return 0.0
    fp = footprint(bbox)
    if fp is None or fp.area <= 0:
        return 0.0
    try:
        intersection = fp.intersection(zone_poly)
        return float(intersection.area / fp.area)
    except Exception:
        return 0.0


def ground_point_inside(bbox: tuple, zone_poly) -> bool:
    """
    True if the bottom-centre ground contact point is inside the zone polygon.

    Args:
        bbox: (x1, y1, x2, y2) bounding box.
        zone_poly: Shapely Polygon of the zone.

    Returns:
        Boolean.
    """
    if not _SHAPELY_AVAILABLE or zone_poly is None:
        return False
    x1, y1, x2, y2 = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    gp = Point((x1 + x2) / 2.0, y2)
    try:
        return bool(zone_poly.contains(gp) or zone_poly.touches(gp))
    except Exception:
        return False


class ZoneAssigner:
    """
    Assigns a tracked vehicle to a zone using footprint overlap + ground point.

    Implements hysteresis:
    - Enter: overlap_ratio >= enter_ratio AND ground point inside, for N_enter frames
    - Exit: overlap_ratio < exit_ratio, for N_exit frames

    This prevents toggling when a vehicle is on the zone boundary.
    """

    def __init__(
        self,
        zone_poly,
        zone_id: str,
        enter_ratio: float = 0.50,
        exit_ratio: float = 0.20,
        n_enter: int = 6,       # frames at ~24fps ≈ 0.25 s
        n_exit: int = 10,       # frames at ~24fps ≈ 0.4 s
    ):
        self.zone_poly = zone_poly
        self.zone_id = zone_id
        self.enter_ratio = enter_ratio
        self.exit_ratio = exit_ratio
        self.n_enter = n_enter
        self.n_exit = n_exit
        # Per-track state: {track_id: {"inside": bool, "in_frames": int, "out_frames": int}}
        self._state: dict[int, dict] = {}

    def is_inside(self, track_id: int, bbox: tuple) -> bool:
        """
        Return True if the vehicle is definitively inside the zone (with hysteresis).

        Args:
            track_id: Vehicle track ID.
            bbox: Current bounding box (x1, y1, x2, y2).

        Returns:
            True when inside, False otherwise.
        """
        s = self._state.setdefault(
            track_id, {"inside": False, "in_frames": 0, "out_frames": 0}
        )

        currently_overlapping = (
            overlap_ratio(bbox, self.zone_poly) >= self.enter_ratio
            and ground_point_inside(bbox, self.zone_poly)
        )
        clearly_outside = overlap_ratio(bbox, self.zone_poly) < self.exit_ratio

        if not s["inside"]:
            s["in_frames"] = s["in_frames"] + 1 if currently_overlapping else 0
            if s["in_frames"] >= self.n_enter:
                s["inside"] = True
                s["out_frames"] = 0
                logger.debug(f"Track {track_id} ENTERED zone {self.zone_id}")
        else:
            s["out_frames"] = s["out_frames"] + 1 if clearly_outside else 0
            if s["out_frames"] >= self.n_exit:
                s["inside"] = False
                s["in_frames"] = 0
                logger.debug(f"Track {track_id} LEFT zone {self.zone_id}")

        return s["inside"]

    def cleanup(self, active_ids: set) -> None:
        """Remove state for tracks that are no longer active."""
        lost = [tid for tid in self._state if tid not in active_ids]
        for tid in lost:
            del self._state[tid]

    @staticmethod
    def polygon_from_px_list(points_px: list) -> Optional[object]:
        """Build a Shapely Polygon from a list of [x, y] pixel points."""
        if not _SHAPELY_AVAILABLE:
            return None
        return Polygon([(p[0], p[1]) for p in points_px])

    @staticmethod
    def polygon_from_world_list(points_world: list) -> Optional[object]:
        """Build a Shapely Polygon from a list of [x_m, y_m] world points."""
        if not _SHAPELY_AVAILABLE:
            return None
        return Polygon([(p[0], p[1]) for p in points_world])
