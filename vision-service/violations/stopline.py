"""
stopline.py — Stop-line geometry utilities for red-light violation detection
=============================================================================
Provides signed-distance and crossing-time calculation for a virtual stop line.

Design (improvements.md § A4.2):
- Uses signed perpendicular distance so "before" and "after" are unambiguous
- Interpolates the exact crossing time between two frames (not just the frame boundary)
- Applies hysteresis: a vehicle must cross cleanly, not jitter on the boundary
- Segment gating ensures cross traffic cannot accidentally "cross" the line

All coordinates are in world units (metres) after homography projection.
"""

import numpy as np


def signed_dist(p, a, b) -> float:
    """
    Signed perpendicular distance from point p to the directed line from a to b.

    Positive = left of the directed line (before stop line when facing normal direction).
    Negative = right of the directed line (past the stop line).

    Args:
        p: Point (x, y) in world metres.
        a: First endpoint of the stop line.
        b: Second endpoint of the stop line.

    Returns:
        Signed distance in metres. Positive = before line, negative = past line.
    """
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    p_arr = np.asarray(p, dtype=float)
    d = b_arr - a_arr
    norm = float(np.linalg.norm(d))
    if norm < 1e-9:
        return 0.0
    # 2D cross product: d.x*(p.y-a.y) - d.y*(p.x-a.x), divided by |d|
    return float((d[0] * (p_arr[1] - a_arr[1]) - d[1] * (p_arr[0] - a_arr[0])) / norm)


def within_segment(p, a, b, margin_m: float = 0.5) -> bool:
    """
    True if the projection of point p lies on the stop-line segment (with a lateral margin).

    This prevents cross traffic moving along the far end of the stop line from being
    misidentified as crossing vehicles.

    Args:
        p: Point (x, y) in world metres.
        a: First endpoint of the stop line.
        b: Second endpoint of the stop line.
        margin_m: Extra metres allowed beyond each end of the segment.

    Returns:
        True if p projects within the segment ± margin.
    """
    a_arr = np.asarray(a, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    p_arr = np.asarray(p, dtype=float)
    ab = b_arr - a_arr
    ab_sq = float(np.dot(ab, ab))
    if ab_sq < 1e-9:
        return False
    t = float(np.dot(p_arr - a_arr, ab)) / ab_sq
    seg_len = float(np.linalg.norm(ab))
    margin_t = margin_m / (seg_len + 1e-9)
    return -margin_t <= t <= 1.0 + margin_t


def crossing_time(t0: float, d0: float, t1: float, d1: float) -> float:
    """
    Linear interpolation of the exact crossing moment between two consecutive frames.

    Args:
        t0: Timestamp of the earlier frame (seconds).
        d0: Signed distance at t0.
        t1: Timestamp of the later frame (seconds).
        d1: Signed distance at t1.

    Returns:
        Interpolated crossing timestamp in seconds.

    Why this matters: At 24 fps, one frame is ~42 ms. A vehicle at 30 km/h moves ~35 cm
    per frame. If the signal changes within that window, the wrong state could be assigned
    without interpolation.
    """
    if abs(d0 - d1) < 1e-9:
        return t1
    # Linear interpolation: find t where d(t) = 0
    alpha = d0 / (d0 - d1)
    return t0 + alpha * (t1 - t0)


class StopLine:
    """
    Represents a virtual stop line for one camera approach.

    Encapsulates both world-coordinate and pixel-coordinate representations,
    the travel sign (which side is "before" the line), and the hysteresis band.

    Args:
        world_a: First endpoint in world metres (x, y).
        world_b: Second endpoint in world metres (x, y).
        travel_sign: +1 if positive signed_dist means "before" the line (approach side),
                     -1 if negative means "before". Depends on camera orientation.
        hysteresis_m: Distance band (metres) around zero. Vehicle must be outside ±hysteresis
                      to have a definite side. Values in the band are "ambiguous".
        margin_m: Lateral segment margin for within_segment().
    """

    def __init__(
        self,
        world_a: tuple,
        world_b: tuple,
        travel_sign: int = 1,
        hysteresis_m: float = 0.3,
        margin_m: float = 0.5,
    ):
        self.world_a = world_a
        self.world_b = world_b
        self.travel_sign = travel_sign      # +1 or -1: sign of d when "before" the line
        self.hysteresis_m = hysteresis_m
        self.margin_m = margin_m

    def side(self, world_xy: tuple) -> str:
        """
        Classify a point relative to the stop line.

        Returns:
            "before"    — clearly on the approach side (d >= +hysteresis)
            "past"      — clearly past the stop line (d <= -hysteresis)
            "ambiguous" — within the hysteresis band (do not use for crossing decisions)
        """
        d = signed_dist(world_xy, self.world_a, self.world_b) * self.travel_sign
        if d >= self.hysteresis_m:
            return "before"
        if d <= -self.hysteresis_m:
            return "past"
        return "ambiguous"

    def signed_distance(self, world_xy: tuple) -> float:
        """Signed distance with travel sign applied. Positive = before line."""
        return signed_dist(world_xy, self.world_a, self.world_b) * self.travel_sign

    def within_segment(self, world_xy: tuple) -> bool:
        """True if the point projects within the line's span."""
        return within_segment(world_xy, self.world_a, self.world_b, self.margin_m)

    def interpolate_crossing(
        self, t0: float, d0: float, t1: float, d1: float
    ) -> float:
        """Compute exact crossing time from two consecutive frames."""
        return crossing_time(t0, d0, t1, d1)
