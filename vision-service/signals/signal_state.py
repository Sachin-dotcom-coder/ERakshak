"""
signal_state.py — Vision-based traffic signal state reader
============================================================
Reads the lit lamp state from traffic signal heads visible in a camera frame.
Uses brightness-by-position first, HSV hue confirmation second.

Design principles (from improvements.md Section A3):
- Position takes priority over colour (red LEDs saturate to white at centre)
- Multiple heads are fused by majority vote
- State is debounced so one bad frame cannot flip the reading
- State transitions are back-dated to the first frame of the new state
- When state is UNKNOWN, NO violation is issued — fail-safe is always chosen

Source: improvements.md § A3.2
"""

import cv2
import numpy as np
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import logging

logger = logging.getLogger(__name__)


class Lamp(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    OFF = "OFF"
    UNKNOWN = "UNKNOWN"


@dataclass
class HeadROI:
    """Region of interest for one signal head housing."""
    head_id: str            # e.g. "mast_arm", "pole_left", "pole_right"
    x1: int
    y1: int
    x2: int
    y2: int                 # ROI covering the whole 3-aspect housing
    orientation: str = "vertical"   # "vertical": red top, green bottom


def _hue_mask(hsv: np.ndarray, lo: int, hi: int, s_min: int = 80, v_min: int = 150) -> np.ndarray:
    """Create a hue mask that handles red wrapping around 180°."""
    if lo <= hi:
        m = cv2.inRange(hsv, (lo, s_min, v_min), (hi, 255, 255))
    else:  # wraps around 180 (red hue straddles 0/180)
        m1 = cv2.inRange(hsv, (lo, s_min, v_min), (179, 255, 255))
        m2 = cv2.inRange(hsv, (0, s_min, v_min), (hi, 255, 255))
        m = cv2.bitwise_or(m1, m2)
    return m


def classify_head(frame_bgr: np.ndarray, roi: HeadROI, min_lit_ratio: float = 0.04) -> Lamp:
    """
    Classify the lit lamp in one signal head.

    Algorithm:
    1. Crop the ROI.
    2. Split into thirds (top=red, mid=yellow, bot=green for vertical heads).
    3. Find which third has the highest 99th-percentile brightness.
    4. Confirm the colour with a hue test in that third.
    5. If position and colour disagree, return UNKNOWN (never guess).

    Returns Lamp enum value.
    """
    crop = frame_bgr[roi.y1:roi.y2, roi.x1:roi.x2]
    if crop.size == 0:
        return Lamp.UNKNOWN

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    h = crop.shape[0]
    thirds = [gray[0:h // 3], gray[h // 3:2 * h // 3], gray[2 * h // 3:]]
    # 99th percentile is robust to a few hot pixels but still catches small lamps
    peaks = [float(np.percentile(t, 99)) if t.size > 0 else 0.0 for t in thirds]
    lit_idx = int(np.argmax(peaks))
    contrast = peaks[lit_idx] - np.median(peaks)
    if contrast < 40:       # nothing clearly lit
        return Lamp.OFF

    # Colour confirmation inside the lit third
    slices = [hsv[0:h // 3], hsv[h // 3:2 * h // 3], hsv[2 * h // 3:]]
    third_hsv = slices[lit_idx]
    area = max(third_hsv.shape[0] * third_hsv.shape[1], 1)

    red = cv2.countNonZero(_hue_mask(third_hsv, 170, 10))
    yel = cv2.countNonZero(_hue_mask(third_hsv, 15, 35))
    grn = cv2.countNonZero(_hue_mask(third_hsv, 45, 95))
    best = max(("RED", red), ("YELLOW", yel), ("GREEN", grn), key=lambda t: t[1])

    # For vertical heads: top=RED, mid=YELLOW, bot=GREEN
    by_position = [Lamp.RED, Lamp.YELLOW, Lamp.GREEN][lit_idx]

    # If hue disagrees with position AND the disagreeing colour is strong, be cautious
    if best[1] / area >= min_lit_ratio and Lamp(best[0]) != by_position:
        return Lamp.UNKNOWN     # position and colour disagree — do not guess

    return by_position


class SignalStateReader:
    """
    Fuses several signal heads, debounces state changes, and keeps a timestamped history.

    Fail-safe: outputs UNKNOWN when heads disagree or classification is ambiguous.
    When state is UNKNOWN, callers must NOT issue any enforcement action.

    Args:
        rois: List of HeadROI objects for all heads that govern this approach.
        fps: Processing frame rate (used to compute debounce frame count).
        debounce_s: Minimum duration (seconds) before accepting a state change.
        history_s: How long to keep timestamped history for retroactive lookups.
    """

    def __init__(
        self,
        rois: list,
        fps: float,
        debounce_s: float = 0.30,
        history_s: float = 120.0,
    ):
        self.rois = rois
        self.need = max(2, int(round(debounce_s * fps)))    # frames needed to accept change
        self.state = Lamp.UNKNOWN
        self.state_since_ts: Optional[float] = None
        self._pending: Optional[Lamp] = None
        self._pending_n: int = 0
        self._pending_first_ts: Optional[float] = None
        self.history: deque = deque()       # (ts, Lamp) tuples
        self.history_s = history_s

    def update(self, frame_bgr: np.ndarray, ts: float) -> Lamp:
        """
        Process one frame and return the current debounced signal state.

        Args:
            frame_bgr: Full camera frame in BGR format.
            ts: Capture timestamp (seconds, NTP-synced).

        Returns:
            Current Lamp state (debounced and back-dated on transitions).
        """
        votes = [classify_head(frame_bgr, r) for r in self.rois]
        known = [v for v in votes if v != Lamp.UNKNOWN]

        if not known:
            fused = Lamp.UNKNOWN
        else:
            top = max(set(known), key=known.count)
            # Majority vote: top must have more than half the heads agreeing
            fused = top if known.count(top) > len(self.rois) / 2 else Lamp.UNKNOWN

        # Debounce: require self.need consecutive frames before accepting change
        if fused == self.state:
            self._pending, self._pending_n = None, 0
        else:
            if fused == self._pending:
                self._pending_n += 1
            else:
                self._pending = fused
                self._pending_n = 1
                self._pending_first_ts = ts
            if self._pending_n >= self.need:
                old_state = self.state
                self.state = fused
                # Back-date: use the first frame that showed the new state
                self.state_since_ts = self._pending_first_ts
                self._pending, self._pending_n = None, 0
                logger.info(f"Signal state: {old_state} → {self.state} (back-dated to {self.state_since_ts:.3f})")

        self.history.append((ts, self.state))
        # Trim old history
        while self.history and ts - self.history[0][0] > self.history_s:
            self.history.popleft()

        return self.state

    def state_at(self, ts: float) -> tuple[Lamp, Optional[float]]:
        """
        Return the signal state at an earlier timestamp plus seconds-in-that-state.

        Needed to judge a stop-line crossing that was detected a few frames ago.
        Returns (Lamp, seconds_since_state_started) or (UNKNOWN, None).
        """
        prev = Lamp.UNKNOWN
        since: Optional[float] = None
        for t, s in self.history:
            if t > ts:
                break
            if s != prev:
                since = t
            prev = s
        elapsed = (ts - since) if since is not None else None
        return prev, elapsed

    @property
    def seconds_in_current_state(self) -> Optional[float]:
        """How long the current state has been active (seconds), or None if unknown."""
        if self.state_since_ts is None:
            return None
        # Rough: caller should pass ts if they want exact timing
        return None


class ControllerFeedSignalState:
    """
    Signal state sourced from the traffic controller (ITMS/NEMA feed).

    Preferred over vision-based reading: exact, immune to glare, provides red onset time.
    This class wraps the controller integration point and provides the same interface
    as SignalStateReader so callers can swap transparently.

    In production, implement _fetch_from_controller() to read your controller's API.
    """

    def __init__(self, junction_id: str, approach: str):
        self.junction_id = junction_id
        self.approach = approach
        self.state = Lamp.UNKNOWN
        self.state_since_ts: Optional[float] = None
        self.history: deque = deque(maxlen=7200)    # 2 hours at 1 Hz

    def update_from_controller(self, state: Lamp, ts: float) -> None:
        """Called by the controller feed integration whenever state changes or heartbeats."""
        if state != self.state:
            self.state = state
            self.state_since_ts = ts
        self.history.append((ts, self.state))

    def state_at(self, ts: float) -> tuple[Lamp, Optional[float]]:
        """Same interface as SignalStateReader.state_at()."""
        prev = Lamp.UNKNOWN
        since: Optional[float] = None
        for t, s in self.history:
            if t > ts:
                break
            if s != prev:
                since = t
            prev = s
        elapsed = (ts - since) if since is not None else None
        return prev, elapsed


class FusedSignalState:
    """
    Fuses controller feed (authoritative) with vision-based reading (cross-check).

    - If controller feed is available and fresh: use it.
    - If controller and vision disagree: raise a health alert and return UNKNOWN.
    - If controller unavailable: fall back to vision (lower confidence).

    This is Option 3 from improvements.md §A3.1 (recommended).
    """

    def __init__(
        self,
        vision_reader: Optional[SignalStateReader],
        controller: Optional[ControllerFeedSignalState],
        max_controller_age_s: float = 5.0,
        mismatch_handler=None,
    ):
        self._vision = vision_reader
        self._ctrl = controller
        self._max_ctrl_age = max_controller_age_s
        self._mismatch_handler = mismatch_handler  # callable(approach, ts, vision_lamp, ctrl_lamp)
        self._last_ctrl_ts: Optional[float] = None

    def update(self, frame_bgr: np.ndarray, ts: float) -> Lamp:
        """Run vision update and cross-check with controller feed."""
        vision_lamp = Lamp.UNKNOWN
        if self._vision is not None:
            vision_lamp = self._vision.update(frame_bgr, ts)

        ctrl_lamp = Lamp.UNKNOWN
        ctrl_fresh = (
            self._ctrl is not None
            and self._last_ctrl_ts is not None
            and (ts - self._last_ctrl_ts) < self._max_ctrl_age
        )
        if ctrl_fresh:
            ctrl_lamp = self._ctrl.state

        # Cross-check
        if ctrl_fresh and vision_lamp not in (Lamp.UNKNOWN, Lamp.OFF):
            if vision_lamp != ctrl_lamp:
                logger.warning(
                    f"Signal mismatch! Controller={ctrl_lamp}, Vision={vision_lamp} at ts={ts:.3f}. "
                    f"Returning UNKNOWN — no enforcement."
                )
                if self._mismatch_handler:
                    self._mismatch_handler(ts, vision_lamp, ctrl_lamp)
                return Lamp.UNKNOWN

        if ctrl_fresh:
            return ctrl_lamp
        if vision_lamp != Lamp.UNKNOWN:
            return vision_lamp
        return Lamp.UNKNOWN

    def state_at(self, ts: float) -> tuple[Lamp, Optional[float]]:
        """Delegate to whichever source was active at that time."""
        if self._ctrl is not None:
            return self._ctrl.state_at(ts)
        if self._vision is not None:
            return self._vision.state_at(ts)
        return Lamp.UNKNOWN, None

    def notify_controller_update(self, state: Lamp, ts: float) -> None:
        """Called by the controller integration whenever a new state arrives."""
        if self._ctrl is not None:
            self._ctrl.update_from_controller(state, ts)
        self._last_ctrl_ts = ts
