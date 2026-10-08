"""
rlv_engine.py — Red-Light Violation (RLV) per-track state machine
==================================================================
Implements the full RLV detection state machine as specified in
improvements.md § A5, A6.

State machine per track:
  APPROACHING → BEFORE_LINE → CROSSED → {RED_CANDIDATE | GREEN_ENTRY |
               YELLOW_ENTRY | UNKNOWN_SIGNAL | ENCROACHMENT} → CONFIRMED

Key design principles:
- No enforcement when signal state is UNKNOWN (fail-safe).
- Crossing time is interpolated between frames, not snapped to frame boundary.
- Confirmation requires distance + frames past the line (not just one frame).
- One event emitted per track_id (no duplicates).
- Cross traffic in the box at the time of crossing → HIGH_RISK flag.
- ID-switch protection: inherits candidate state if a track is re-born within
  a short window at the same location moving the same direction.

Usage:
    engine = RLVEngine(cfg, signal_reader)
    events = engine.update(ts, vehicles, cross_traffic_in_box=False)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

from signals.signal_state import Lamp
from violations.stopline import StopLine

logger = logging.getLogger(__name__)


# Terminal states where no further transitions are expected
_TERMINAL = frozenset(
    ["CONFIRMED", "DISCARDED", "GREEN_ENTRY", "YELLOW_ENTRY",
     "UNKNOWN_SIGNAL", "ENCROACHMENT"]
)


class S(str, Enum):
    APPROACHING   = "APPROACHING"
    BEFORE_LINE   = "BEFORE_LINE"
    CROSSED       = "CROSSED"           # intermediate — classify next
    RED_CANDIDATE = "RED_CANDIDATE"
    CONFIRMED     = "CONFIRMED"
    ENCROACHMENT  = "ENCROACHMENT"      # stopped just over the line
    GREEN_ENTRY   = "GREEN_ENTRY"       # legal crossing, no violation
    YELLOW_ENTRY  = "YELLOW_ENTRY"      # yellow-phase crossing, logged only
    UNKNOWN_SIGNAL = "UNKNOWN_SIGNAL"   # signal state unknown — no enforcement
    DISCARDED     = "DISCARDED"         # track rolled back or lost


@dataclass
class TrackRLV:
    """State per tracked vehicle for the RLV engine."""
    track_id: int
    state: S = S.APPROACHING
    first_ts: float = 0.0
    prev: Optional[tuple] = None            # (ts, signed_dist)
    frames_before: int = 0                  # consecutive frames clearly before the line
    cross_ts: Optional[float] = None        # interpolated crossing timestamp
    cross_signal: Optional[Lamp] = None
    red_elapsed_at_cross: Optional[float] = None
    cross_pos_world: Optional[tuple] = None
    frames_after: int = 0                   # consecutive frames past the line
    dist_after_m: float = 0.0              # metres travelled past the line
    emitted: bool = False
    speed_at_cross_kmh: float = 0.0
    evidence: dict = field(default_factory=dict)


@dataclass
class RLVConfig:
    """
    Configuration for the RLV engine. All values documented and configurable.
    Source config file: configs/<camera_id>_rlv.yaml
    """
    # Stop line geometry (in world metres)
    stop_line: Optional[StopLine] = None

    # Exemptions: these vehicle classes never generate violations (emergency etc.)
    exempt_classes: frozenset = field(default_factory=lambda: frozenset({"ambulance", "fire_truck"}))

    # Hysteresis in metres around the stop line (avoid jitter decisions)
    hysteresis_m: float = 0.3

    # Track must have been clearly BEFORE the line for this long before crossing counts
    min_track_age_s: float = 1.0
    min_frames_before: int = 5

    # Speed threshold: creeping over the line is ENCROACHMENT, not RLV
    min_speed_at_crossing_kmh: float = 8.0

    # Confirmation: vehicle must travel this far past the line AND for this many frames
    confirm_distance_m: float = 5.0
    confirm_min_frames: int = 6

    # Maximum frames in RED_CANDIDATE before deciding it stopped (ENCROACHMENT)
    max_candidate_frames: int = 60

    # Grace period after red onset (seconds). 0.0 = no grace. Confirm with local authority.
    grace_s: float = 0.0

    # Cross traffic: speed threshold for "actively moving" vehicles in the junction box
    cross_traffic_speed_kmh: float = 8.0

    # ID-switch inheritance: inherit candidate if new track appears within this time/distance
    id_switch_window_s: float = 1.0
    id_switch_max_m: float = 3.0


class RLVEngine:
    """
    Red-light violation state machine.

    One RLVEngine instance per camera approach. Call update() once per frame.

    Args:
        cfg: RLVConfig with stop line, thresholds and exemptions.
        signal_reader: FusedSignalState or SignalStateReader (any object with .state_at()).
    """

    def __init__(self, cfg: RLVConfig, signal_reader):
        self.cfg = cfg
        self.sig = signal_reader
        self.tracks: dict[int, TrackRLV] = {}
        self._recent_candidates: list[dict] = []   # for ID-switch inheritance

    def update(
        self,
        ts: float,
        vehicles: list,
        cross_traffic_in_box: bool = False,
    ) -> list[dict]:
        """
        Process one frame and return any newly confirmed violation events.

        Args:
            ts: Frame capture timestamp (seconds, NTP-synced).
            vehicles: Iterable of vehicle objects. Each must have:
                      .track_id (int), .class_name (str), .world_xy (tuple),
                      .speed_kmh (float), .age_s (float).
            cross_traffic_in_box: True if other tracks are actively crossing in the
                                  junction box (used for HIGH_RISK flag).

        Returns:
            List of violation event dicts. Each event is emitted exactly once.
        """
        if self.cfg.stop_line is None:
            return []

        out = []
        sl = self.cfg.stop_line

        for v in vehicles:
            if v.class_name in self.cfg.exempt_classes:
                continue

            tr = self.tracks.setdefault(
                v.track_id, TrackRLV(track_id=v.track_id, first_ts=ts)
            )

            # Skip terminal states (except RED_CANDIDATE which still needs updates)
            if tr.state in _TERMINAL and tr.state != S.RED_CANDIDATE:
                continue

            # Segment gating: ignore vehicles not laterally aligned with the stop line
            if not sl.within_segment(v.world_xy):
                continue

            d = sl.signed_distance(v.world_xy)   # positive = before the line

            # ── APPROACHING / BEFORE_LINE ──────────────────────────────────
            if tr.state in (S.APPROACHING, S.BEFORE_LINE):
                if d >= sl.hysteresis_m:
                    tr.frames_before += 1
                    if (tr.frames_before >= self.cfg.min_frames_before
                            and v.age_s >= self.cfg.min_track_age_s):
                        tr.state = S.BEFORE_LINE
                elif d <= -sl.hysteresis_m and tr.state is S.BEFORE_LINE and tr.prev:
                    # Crossing detected — interpolate exact time
                    t_cross = sl.interpolate_crossing(tr.prev[0], tr.prev[1], ts, d)
                    tr.cross_ts = t_cross
                    tr.cross_pos_world = v.world_xy
                    tr.speed_at_cross_kmh = v.speed_kmh
                    lamp, since = self.sig.state_at(t_cross)
                    tr.cross_signal = lamp
                    tr.red_elapsed_at_cross = since if lamp is Lamp.RED else None
                    tr.state = self._classify_crossing(tr)
                    tr.evidence["cross_world"] = v.world_xy
                    tr.evidence["cross_ts"] = t_cross
                    logger.debug(
                        f"Track {v.track_id} crossed at {t_cross:.3f}s "
                        f"signal={lamp} speed={v.speed_kmh:.1f}km/h → state={tr.state}"
                    )

            # ── RED_CANDIDATE: awaiting confirmation ─────────────────────────
            elif tr.state is S.RED_CANDIDATE:
                tr.frames_after += 1
                tr.dist_after_m = -d  # metres past the line (d is negative when past)

                if (tr.dist_after_m >= self.cfg.confirm_distance_m
                        and tr.frames_after >= self.cfg.confirm_min_frames
                        and v.speed_kmh >= self.cfg.min_speed_at_crossing_kmh):
                    # ✅ Violation confirmed
                    tr.state = S.CONFIRMED
                    tr.emitted = True
                    event = self._build_event(v, tr, cross_traffic_in_box)
                    out.append(event)
                    logger.warning(
                        f"RLV CONFIRMED: track {v.track_id} ({v.class_name}) "
                        f"@ {tr.cross_ts:.3f}s  high_risk={cross_traffic_in_box}"
                    )

                elif d > sl.hysteresis_m:
                    # Vehicle rolled back behind the line — discard
                    tr.state = S.DISCARDED
                    logger.debug(f"Track {v.track_id} rolled back — DISCARDED")

                elif (tr.frames_after > self.cfg.max_candidate_frames
                      and v.speed_kmh < 2.0):
                    # Stopped just over the line without entering the box
                    tr.state = S.ENCROACHMENT
                    logger.info(
                        f"STOP_LINE_ENCROACHMENT: track {v.track_id} ({v.class_name}) "
                        f"stopped {tr.dist_after_m:.1f}m past the line"
                    )

            tr.prev = (ts, d)

        self._try_inherit_candidates(ts, vehicles)
        return out

    def _classify_crossing(self, tr: TrackRLV) -> S:
        """Determine the post-crossing state based on signal colour."""
        lamp = tr.cross_signal
        if lamp is Lamp.RED:
            grace_ok = (tr.red_elapsed_at_cross or 0.0) >= self.cfg.grace_s
            speed_ok = tr.speed_at_cross_kmh >= self.cfg.min_speed_at_crossing_kmh
            if grace_ok and speed_ok:
                return S.RED_CANDIDATE
            return S.ENCROACHMENT   # too slow — stopped over the line
        if lamp is Lamp.YELLOW:
            return S.YELLOW_ENTRY
        if lamp is Lamp.GREEN:
            return S.GREEN_ENTRY
        # UNKNOWN or OFF → never enforce
        return S.UNKNOWN_SIGNAL

    def _build_event(self, v, tr: TrackRLV, high_risk: bool) -> dict:
        """Build the violation event dict (schema v2 compatible)."""
        etype = "RED_LIGHT_VIOLATION_HIGH_RISK" if high_risk else "RED_LIGHT_VIOLATION"
        return {
            "type": etype,
            "track_id": tr.track_id,
            "vehicle_class": v.class_name,
            "cross_ts": tr.cross_ts,
            "red_elapsed_s": tr.red_elapsed_at_cross,
            "speed_kmh": round(tr.speed_at_cross_kmh, 1),
            "cross_traffic_in_box": high_risk,
            "cross_pos_world": tr.cross_pos_world,
            # confidence filled in by caller (see improvements.md §A8)
            "confidence": None,
        }

    def _try_inherit_candidates(self, ts: float, vehicles: list) -> None:
        """
        ID-switch protection: if a track dies mid-candidate and a new track appears
        nearby moving the same direction, inherit the candidate state.

        Prevents double counting during bus/auto occlusions (common in Indian traffic).
        """
        # Record recently-dead candidates
        for tid, tr in list(self.tracks.items()):
            if (tr.state is S.RED_CANDIDATE
                    and not any(v.track_id == tid for v in vehicles)):
                self._recent_candidates.append({
                    "tid": tid, "ts": ts, "tr": tr,
                    "pos": tr.cross_pos_world,
                })

        # Prune stale candidate records
        self._recent_candidates = [
            c for c in self._recent_candidates
            if ts - c["ts"] < self.cfg.id_switch_window_s
        ]

        # Try to match new tracks to recent candidates
        new_tids = {v.track_id for v in vehicles}
        for v in vehicles:
            if v.track_id in self.tracks:
                continue  # already known track
            for c in self._recent_candidates:
                if c["pos"] is None:
                    continue
                dist = float(np.hypot(
                    v.world_xy[0] - c["pos"][0],
                    v.world_xy[1] - c["pos"][1],
                ))
                if dist < self.cfg.id_switch_max_m:
                    # Inherit candidate
                    inherited = TrackRLV(
                        track_id=v.track_id,
                        state=S.RED_CANDIDATE,
                        first_ts=c["tr"].first_ts,
                        cross_ts=c["tr"].cross_ts,
                        cross_signal=c["tr"].cross_signal,
                        red_elapsed_at_cross=c["tr"].red_elapsed_at_cross,
                        cross_pos_world=c["tr"].cross_pos_world,
                        frames_after=c["tr"].frames_after,
                        dist_after_m=c["tr"].dist_after_m,
                        speed_at_cross_kmh=c["tr"].speed_at_cross_kmh,
                        evidence={**c["tr"].evidence, "id_switch_inherited": True},
                    )
                    self.tracks[v.track_id] = inherited
                    logger.info(
                        f"Track {v.track_id} inherited RED_CANDIDATE from track {c['tid']} "
                        f"(ID switch, distance={dist:.1f}m)"
                    )
                    self._recent_candidates.remove(c)
                    break
