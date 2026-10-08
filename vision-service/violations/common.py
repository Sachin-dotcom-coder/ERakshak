"""
common.py — Shared utilities for violation engines
===================================================
Implements cross-cutting violation detection logic:
1. ID-switch protection & episode inheritance (improvements.md § A6, B6)
2. Deduplication manager across tracks, cameras, and cooldowns (improvements.md § A6, B12.1)
3. Exemption rules & whitelist checkers (improvements.md § A6, B6)
"""

import math
import time
from dataclasses import dataclass, field
from typing import Optional, Any
import numpy as np


@dataclass
class DeadTrackCandidate:
    """Record of a recently terminated track that had candidate violation state."""
    track_id: int
    last_ts: float
    last_xy: tuple[float, float]
    velocity: tuple[float, float]
    state_payload: Any


class IDSwitchProtector:
    """
    Protects against tracker ID switches caused by occlusion (e.g. buses, autos).
    If a track terminates and a new track appears within max_gap_s and max_distance_m
    moving with similar heading, the candidate state is inherited.
    """

    def __init__(self, max_gap_s: float = 1.5, max_distance_m: float = 3.5, min_heading_cos: float = 0.5):
        self.max_gap_s = max_gap_s
        self.max_distance_m = max_distance_m
        self.min_heading_cos = min_heading_cos
        self._dead_candidates: dict[int, DeadTrackCandidate] = {}

    def record_dead_track(
        self,
        track_id: int,
        ts: float,
        xy: tuple[float, float],
        velocity: tuple[float, float],
        state_payload: Any,
    ):
        """Record a lost or dead candidate track."""
        self._dead_candidates[track_id] = DeadTrackCandidate(
            track_id=track_id,
            last_ts=ts,
            last_xy=xy,
            velocity=velocity,
            state_payload=state_payload,
        )
        self._cleanup(ts)

    def match_new_track(
        self,
        ts: float,
        xy: tuple[float, float],
        velocity: tuple[float, float],
    ) -> Optional[DeadTrackCandidate]:
        """
        Check if a newly detected track matches a recently lost candidate.
        Returns the matched DeadTrackCandidate or None.
        """
        self._cleanup(ts)
        matched_id = None
        best_dist = float("inf")

        for tid, cand in self._dead_candidates.items():
            dt = ts - cand.last_ts
            if dt < 0 or dt > self.max_gap_s:
                continue

            # Projected position based on last velocity
            pred_x = cand.last_xy[0] + cand.velocity[0] * dt
            pred_y = cand.last_xy[1] + cand.velocity[1] * dt
            dist = math.hypot(xy[0] - pred_x, xy[1] - pred_y)

            if dist > self.max_distance_m:
                continue

            # Heading cosine check
            norm_v1 = math.hypot(cand.velocity[0], cand.velocity[1])
            norm_v2 = math.hypot(velocity[0], velocity[1])
            if norm_v1 > 0.1 and norm_v2 > 0.1:
                cos_sim = (
                    cand.velocity[0] * velocity[0] + cand.velocity[1] * velocity[1]
                ) / (norm_v1 * norm_v2)
                if cos_sim < self.min_heading_cos:
                    continue

            if dist < best_dist:
                best_dist = dist
                matched_id = tid

        if matched_id is not None:
            return self._dead_candidates.pop(matched_id)
        return None

    def _cleanup(self, now_ts: float):
        expired = [
            tid
            for tid, cand in self._dead_candidates.items()
            if now_ts - cand.last_ts > self.max_gap_s * 2.0
        ]
        for tid in expired:
            self._dead_candidates.pop(tid, None)


class DedupManager:
    """
    Prevents duplicate violation notices for the same physical vehicle
    within a cooldown period, whether identified by track ID or plate.
    """

    def __init__(self, cooldown_s: float = 15.0):
        self.cooldown_s = cooldown_s
        self._emitted_tracks: dict[int, float] = {}
        self._emitted_plates: dict[str, float] = {}

    def is_duplicate(self, track_id: int, plate_text: Optional[str], ts: float) -> bool:
        """Check if an event for this track or plate was emitted recently."""
        self._cleanup(ts)
        if track_id in self._emitted_tracks:
            return True
        if plate_text:
            clean_plate = plate_text.strip().upper()
            if clean_plate in self._emitted_plates:
                return True
        return False

    def mark_emitted(self, track_id: int, plate_text: Optional[str], ts: float):
        """Mark track ID and optional plate as emitted."""
        self._emitted_tracks[track_id] = ts
        if plate_text:
            clean_plate = plate_text.strip().upper()
            self._emitted_plates[clean_plate] = ts

    def _cleanup(self, now_ts: float):
        exp_tracks = [
            tid for tid, t in self._emitted_tracks.items() if now_ts - t > self.cooldown_s
        ]
        for tid in exp_tracks:
            del self._emitted_tracks[tid]

        exp_plates = [
            p for p, t in self._emitted_plates.items() if now_ts - t > self.cooldown_s
        ]
        for p in exp_plates:
            del self._emitted_plates[p]


class ExemptionChecker:
    """
    Handles emergency, fleet, and temporary exemptions.
    """

    def __init__(
        self,
        exempt_classes: Optional[set[str]] = None,
        allowed_plates: Optional[set[str]] = None,
    ):
        self.exempt_classes = exempt_classes or {"ambulance", "fire_truck"}
        self.allowed_plates = {p.upper() for p in (allowed_plates or set())}
        self.temporary_windows: list[tuple[float, float, str]] = []  # (start_ts, end_ts, reason)

    def add_temporary_exemption(self, start_ts: float, end_ts: float, reason: str = ""):
        """Add temporary exemption window (e.g. road works, diversion)."""
        self.temporary_windows.append((start_ts, end_ts, reason))

    def is_exempt(
        self,
        vehicle_class: str,
        plate_text: Optional[str] = None,
        ts: Optional[float] = None,
    ) -> tuple[bool, str]:
        """
        Check if vehicle is exempt from violation enforcement.
        Returns (is_exempt: bool, reason: str).
        """
        if vehicle_class in self.exempt_classes:
            return True, f"Exempt vehicle class: {vehicle_class}"

        if plate_text and plate_text.strip().upper() in self.allowed_plates:
            return True, f"Authorized plate in registry: {plate_text.upper()}"

        if ts is not None:
            for s, e, r in self.temporary_windows:
                if s <= ts <= e:
                    return True, f"Temporary exemption in effect: {r}"

        return False, ""
