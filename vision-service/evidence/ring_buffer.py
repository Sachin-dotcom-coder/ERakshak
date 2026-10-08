"""
ring_buffer.py — Fixed-size frame ring buffer for violation evidence
=====================================================================
Maintains a rolling window of the last N seconds of compressed frames.
When a violation is confirmed, the relevant window is extracted and
handed to the evidence builder.

Design (improvements.md §A7.1):
- Holds the last `seconds` worth of JPEG-compressed frames in memory
- push() on every frame; window() extracts a time slice
- Memory-bounded: deque with maxlen ensures oldest frames drop automatically

Usage:
    buf = RingBuffer(seconds=10, fps=12, jpeg_quality=80)
    buf.push(capture_ts, frame_bgr)
    # ... violation confirmed at cross_ts ...
    frames = buf.window(cross_ts - 4.0, cross_ts + 4.0)
"""

import cv2
import logging
from collections import deque

logger = logging.getLogger(__name__)


class RingBuffer:
    """
    Fixed-size rolling frame buffer storing JPEG-compressed frames.

    Args:
        seconds: Length of the rolling window in seconds.
        fps: Expected frame rate. Determines maxlen of the deque.
        jpeg_quality: JPEG compression quality (0–100). Lower = smaller memory.
    """

    def __init__(self, seconds: float = 10.0, fps: float = 12.0, jpeg_quality: int = 80):
        self.max_frames = max(1, int(seconds * fps))
        self.buf: deque = deque(maxlen=self.max_frames)
        self.q = int(jpeg_quality)
        logger.debug(
            f"RingBuffer: {seconds:.0f}s × {fps:.0f}fps = {self.max_frames} frames, "
            f"JPEG quality={self.q}"
        )

    def push(self, ts: float, frame_bgr) -> None:
        """
        Add a frame to the ring buffer.

        Args:
            ts: Capture timestamp in seconds (NTP-synced float).
            frame_bgr: BGR numpy array (from cv2).
        """
        ok, jpg = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, self.q])
        if ok:
            self.buf.append((ts, jpg.tobytes()))
        else:
            logger.warning(f"RingBuffer: Failed to JPEG-encode frame at ts={ts:.3f}")

    def window(self, t_start: float, t_end: float) -> list:
        """
        Extract all frames in the time window [t_start, t_end].

        Args:
            t_start: Start of the window (seconds).
            t_end: End of the window (seconds).

        Returns:
            List of (ts, jpeg_bytes) tuples in chronological order.
        """
        return [(t, j) for t, j in self.buf if t_start <= t <= t_end]

    def latest_ts(self) -> float:
        """Return the timestamp of the most recent frame, or 0.0 if empty."""
        return self.buf[-1][0] if self.buf else 0.0

    def oldest_ts(self) -> float:
        """Return the timestamp of the oldest frame still in the buffer, or 0.0 if empty."""
        return self.buf[0][0] if self.buf else 0.0

    def __len__(self) -> int:
        return len(self.buf)
