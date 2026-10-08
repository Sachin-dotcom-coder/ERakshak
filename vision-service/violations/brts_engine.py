"""
brts_engine.py — BRTS corridor violation detection state machine
================================================================
Implements the episode-based BRTS intrusion detector as specified in
improvements.md § B5.

Violation subtypes:
  BRTS_INTRUSION        — Unauthorised vehicle occupies corridor for dwell_s + distance
  BRTS_WRONG_WAY        — Intrusion where vehicle moves against legal direction
  BRTS_PARKING_STOP     — Stationary intrusion beyond stop_s threshold
  BRTS_CUT_IN_AT_GAP    — Entry via a separator gap (for infrastructure analytics)

Key improvements over the original violations.py:
  1. Uses footprint overlap + ground point (not just ground point) via brts_zone.py
  2. Both dwell time AND distance criteria must be met (or stationary_s for parking)
  3. Wrong-way test requires minimum displacement + majority direction votes (no jitter)
  4. Episode merging for ID switches inside the corridor
  5. One event per track_id + cooldown (no per-frame spam)
  6. Authorisation: class allowlist + optional plate registry + time-window exemptions

Usage:
    engine = BRTSEngine(cfg)
    events = engine.update(ts, vehicles)
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from zones.brts_zone import ZoneAssigner, overlap_ratio, ground_point_inside

logger = logging.getLogger(__name__)


@dataclass
class BRTSConfig:
    """
    Configuration for the BRTS corridor violation engine.
    Loaded from configs/<camera_id>_brts.yaml at runtime.
    """
    zone_id: str = "J00X-BRTS-1"

    # ZoneAssigner (set by loader from polygon + thresholds)
    zone_assigner: Optional[ZoneAssigner] = None

    # Authorised vehicle classes — never trigger a violation
    allowed_classes: frozenset = field(
        default_factory=lambda: frozenset({"brts_bus", "ambulance", "fire_truck"})
    )

    # Optional plate registry for BRTS fleet (plate string → True/False)
    # When present, a confirmed plate match overrides class-based allowance.
    allowed_plates: frozenset = field(default_factory=frozenset)

    # Dwell and distance thresholds
    dwell_s: float = 3.0           # minimum time inside corridor
    min_distance_m: float = 10.0   # minimum distance moved inside corridor
    stop_s: float = 30.0           # stationary time for BRTS_PARKING_STOP

    # Track quality: only count after this many seconds of tracking
    min_track_age_s: float = 0.8   # ~0.25 s at 24 fps before episode starts

    # Direction (corridor legal travel direction unit vector in world coords)
    corridor_dir: tuple = (0.0, 1.0)   # override with surveyed value

    # Wrong-way detection
    wrong_way_min_m: float = 5.0       # minimum displacement for wrong-way
    min_dir_samples: int = 5           # minimum direction votes needed

    # ID-switch inheritance
    id_switch_window_s: float = 1.5
    id_switch_max_m: float = 2.0

    # Gate definitions: mapping gate_id → "segment" or "mouth" or "gap"
    gates: dict = field(default_factory=dict)
    separator_poly = None   # Shapely Polygon; if set, crossing it logs CUT_IN_AT_GAP

    # Cooldown: same track cannot fire again for this long
    cooldown_s: float = 60.0


@dataclass
class BRTSEpisode:
    """Per-track episode inside the BRTS corridor."""
    track_id: int
    entry_ts: Optional[float] = None
    entry_xy: Optional[tuple] = None
    entry_gate: Optional[str] = None
    in_frames: int = 0
    out_frames: int = 0
    inside: bool = False
    dist_inside_m: float = 0.0
    last_xy: Optional[tuple] = None
    stationary_s: float = 0.0
    dir_votes: list = field(default_factory=list)
    emitted: bool = False
    emitted_ts: Optional[float] = None
    cut_in_at_gap: bool = False


class BRTSEngine:
    """
    BRTS corridor intrusion detector.

    Maintains one BRTSEpisode per active track. When dwell + distance (or
    dwell + stationary) criteria are met for an unauthorised vehicle, one
    event is emitted and the episode is marked done.

    Args:
        cfg: BRTSConfig with zone, thresholds and corridor direction.
    """

    def __init__(self, cfg: BRTSConfig):
        self.cfg = cfg
        self.eps: dict[int, BRTSEpisode] = {}
        self._recent_inside: list[dict] = []   # for ID-switch inheritance

    def update(self, ts: float, vehicles: list) -> list[dict]:
        """
        Process one frame. Returns newly confirmed BRTS violation events.

        Args:
            ts: Frame capture timestamp (NTP-synced seconds).
            vehicles: Iterable with .track_id, .class_name, .bbox, .world_xy,
                      .speed_kmh, .age_s, .velocity_world, .dt (seconds per frame).

        Returns:
            List of event dicts, one per confirmed violation (emitted once each).
        """
        events = []
        active_ids = {v.track_id for v in vehicles}
        za = self.cfg.zone_assigner

        for v in vehicles:
            # Skip authorised classes unless plate overrides
            if self._is_authorised(v):
                continue

            ep = self.eps.setdefault(v.track_id, BRTSEpisode(v.track_id))

            # Skip cooldown
            if ep.emitted and ep.emitted_ts and (ts - ep.emitted_ts) < self.cfg.cooldown_s:
                continue

            # Zone assignment with hysteresis
            if za is not None:
                inside_now = za.is_inside(v.track_id, v.bbox)
            else:
                inside_now = ground_point_inside(v.bbox, None)  # fallback: always False

            if not ep.inside:
                if inside_now and v.age_s >= self.cfg.min_track_age_s:
                    ep.inside = True
                    ep.entry_ts = ts
                    ep.entry_xy = v.world_xy
                    ep.last_xy = v.world_xy
                    ep.entry_gate = self._nearest_gate(v.world_xy)
                    ep.cut_in_at_gap = (ep.entry_gate is not None and
                                        self.cfg.gates.get(ep.entry_gate, {}).get("type") == "separator_gap")
                    logger.debug(f"Track {v.track_id} ({v.class_name}) entered BRTS via {ep.entry_gate}")
            else:
                if not inside_now:
                    # Vehicle has left
                    ep.inside = False
                    continue

                # Update episode metrics
                if ep.last_xy is not None:
                    step = float(np.hypot(
                        v.world_xy[0] - ep.last_xy[0],
                        v.world_xy[1] - ep.last_xy[1],
                    ))
                    ep.dist_inside_m += step

                    # Direction vote (ignore jitter)
                    if step > 0.05 and hasattr(v, "velocity_world") and v.velocity_world is not None:
                        ep.dir_votes.append(self._dot_corridor(v.velocity_world))

                ep.last_xy = v.world_xy
                dt = getattr(v, "dt", 1.0 / 24.0)
                ep.stationary_s = ep.stationary_s + dt if v.speed_kmh < 2.0 else 0.0

                # Check if threshold is met
                dwell = ts - ep.entry_ts
                moved = ep.dist_inside_m >= self.cfg.min_distance_m
                stuck = ep.stationary_s >= self.cfg.stop_s

                if not ep.emitted and dwell >= self.cfg.dwell_s and (moved or stuck):
                    ep.emitted = True
                    ep.emitted_ts = ts
                    evt = self._build_event(v, ep, dwell, stuck)
                    events.append(evt)
                    logger.warning(
                        f"BRTS VIOLATION: track {v.track_id} ({v.class_name}) "
                        f"type={evt['type']} dwell={dwell:.1f}s dist={ep.dist_inside_m:.1f}m"
                    )

        # ID-switch inheritance: save recently-inside tracks
        for tid, ep in list(self.eps.items()):
            if ep.inside and tid not in active_ids:
                self._recent_inside.append({
                    "tid": tid, "ts": ts, "ep": ep,
                    "last_xy": ep.last_xy,
                })

        # Prune stale
        self._recent_inside = [
            r for r in self._recent_inside
            if ts - r["ts"] < self.cfg.id_switch_window_s
        ]

        # Inherit episodes for new tracks
        for v in vehicles:
            if v.track_id in self.eps:
                continue
            for r in self._recent_inside:
                if r["last_xy"] is None:
                    continue
                dist = float(np.hypot(
                    v.world_xy[0] - r["last_xy"][0],
                    v.world_xy[1] - r["last_xy"][1],
                ))
                if dist < self.cfg.id_switch_max_m:
                    old_ep = r["ep"]
                    inherited = BRTSEpisode(
                        track_id=v.track_id,
                        entry_ts=old_ep.entry_ts,
                        entry_xy=old_ep.entry_xy,
                        entry_gate=old_ep.entry_gate,
                        inside=True,
                        dist_inside_m=old_ep.dist_inside_m,
                        last_xy=old_ep.last_xy,
                        stationary_s=old_ep.stationary_s,
                        dir_votes=list(old_ep.dir_votes),
                        emitted=old_ep.emitted,
                        emitted_ts=old_ep.emitted_ts,
                        cut_in_at_gap=old_ep.cut_in_at_gap,
                    )
                    self.eps[v.track_id] = inherited
                    logger.info(
                        f"BRTS: track {v.track_id} inherited episode from track {r['tid']} "
                        f"(ID switch, dist={dist:.1f}m)"
                    )
                    self._recent_inside.remove(r)
                    break

        # Cleanup zone assigner state
        if za is not None:
            za.cleanup(active_ids)

        return events

    def _is_authorised(self, v) -> bool:
        """True if the vehicle is allowed in the BRTS corridor."""
        if v.class_name in self.cfg.allowed_classes:
            return True
        # Check plate registry if available
        plate = getattr(v, "plate_text", None)
        if plate and plate in self.cfg.allowed_plates:
            return True
        return False

    def _nearest_gate(self, world_xy: tuple) -> Optional[str]:
        """Find the nearest configured gate to the vehicle's entry point."""
        if not self.cfg.gates or world_xy is None:
            return None
        best_gate = None
        best_dist = float("inf")
        for gate_id, gate in self.cfg.gates.items():
            seg = gate.get("segment_world")
            if seg is None:
                continue
            mid = (
                (seg[0][0] + seg[1][0]) / 2,
                (seg[0][1] + seg[1][1]) / 2,
            )
            d = float(np.hypot(world_xy[0] - mid[0], world_xy[1] - mid[1]))
            if d < best_dist:
                best_dist = d
                best_gate = gate_id
        return best_gate if best_dist < 5.0 else "corridor_mouth"

    def _dot_corridor(self, velocity_world: tuple) -> float:
        """Dot product of velocity with the legal corridor direction. +1 = correct way, -1 = wrong."""
        d = np.asarray(self.cfg.corridor_dir, dtype=float)
        v = np.asarray(velocity_world, dtype=float)
        denom = float(np.linalg.norm(v) * np.linalg.norm(d))
        if denom < 1e-9:
            return 0.0
        return float(np.dot(v, d) / denom)

    def _build_event(self, v, ep: BRTSEpisode, dwell: float, stuck: bool) -> dict:
        """Build the BRTS violation event dict (schema v2 events[] compatible)."""
        votes = ep.dir_votes
        wrong_way = (
            len(votes) >= self.cfg.min_dir_samples
            and float(np.mean(votes)) < -0.5
            and ep.dist_inside_m >= self.cfg.wrong_way_min_m
        )

        if wrong_way:
            etype = "BRTS_WRONG_WAY"
        elif ep.cut_in_at_gap:
            etype = "BRTS_CUT_IN_AT_GAP"
        elif stuck:
            etype = "BRTS_PARKING_STOP"
        else:
            etype = "BRTS_INTRUSION"

        return {
            "type": etype,
            "track_id": v.track_id,
            "vehicle_class": v.class_name,
            "zone_id": self.cfg.zone_id,
            "entry_gate": ep.entry_gate,
            "entry_ts": ep.entry_ts,
            "duration_s": round(dwell, 2),
            "distance_inside_m": round(ep.dist_inside_m, 1),
            "direction_cos": round(float(np.mean(votes)), 3) if votes else None,
            "confidence": None,  # filled by caller (improvements.md §B9)
        }
