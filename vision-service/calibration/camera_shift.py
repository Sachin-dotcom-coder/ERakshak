"""
calibration/camera_shift.py — Camera Shift Detection (Section 32)
==================================================================
Detects physical camera movement by tracking reference landmark positions.

After calibration, stable road landmarks (stop line, curb, lane markings)
are defined. If their positions shift beyond a threshold, the calibration
is invalidated.

This is critical because an incorrect homography corrupts:
  speed, queue length, lane assignment, BRTS detection simultaneously.
"""

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraShiftDetector:
    """Detect camera physical movement via landmark tracking.

    Args:
        landmarks: List of dicts with 'name', 'pixel' (reference position),
                   and 'tolerance_px' from camera config.
        config: Dict with shift detection settings.
    """

    def __init__(
        self,
        landmarks: Optional[list[dict]] = None,
        config: Optional[dict] = None,
    ) -> None:
        cfg = config or {}
        self._shift_threshold: float = cfg.get("shift_threshold", 15.0)
        self._landmarks = landmarks or []

        # Store reference positions
        self._reference_positions: dict[str, np.ndarray] = {}
        self._tolerances: dict[str, float] = {}
        for lm in self._landmarks:
            name = lm.get("name", "")
            pixel = lm.get("pixel", [0, 0])
            self._reference_positions[name] = np.array(pixel, dtype=np.float32)
            self._tolerances[name] = lm.get("tolerance_px", 10)

        # Template matching for landmark tracking
        self._templates: dict[str, np.ndarray] = {}
        self._template_initialized: bool = False

    def initialize_templates(self, frame: np.ndarray) -> None:
        """Capture reference landmark templates from the calibration frame.

        Should be called once when calibration is performed.

        Args:
            frame: BGR calibration frame.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for name, pos in self._reference_positions.items():
            x, y = int(pos[0]), int(pos[1])
            half = 30  # Template size: 60x60 pixels

            # Clamp to frame bounds
            h, w = gray.shape
            y1 = max(0, y - half)
            y2 = min(h, y + half)
            x1 = max(0, x - half)
            x2 = min(w, x + half)

            template = gray[y1:y2, x1:x2]
            if template.size > 0:
                self._templates[name] = template.copy()

        self._template_initialized = bool(self._templates)
        if self._template_initialized:
            logger.info(
                f"Camera shift detector initialized with "
                f"{len(self._templates)} landmarks"
            )

    def check_shift(self, frame: np.ndarray) -> dict:
        """Check for camera shift by tracking landmark positions.

        Args:
            frame: Current BGR frame.

        Returns:
            Dict with shift detection results.
        """
        if not self._template_initialized:
            return {
                "shift_detected": False,
                "mean_displacement_px": 0.0,
                "displacements": {},
                "landmarks_tracked": 0,
            }

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        displacements: dict[str, float] = {}

        for name, template in self._templates.items():
            ref_pos = self._reference_positions.get(name)
            if ref_pos is None:
                continue

            # Search region around reference position
            search_margin = 50
            x, y = int(ref_pos[0]), int(ref_pos[1])
            h, w = gray.shape
            th, tw = template.shape

            y1 = max(0, y - search_margin)
            y2 = min(h - th, y + search_margin)
            x1 = max(0, x - search_margin)
            x2 = min(w - tw, x + search_margin)

            if y2 <= y1 or x2 <= x1:
                continue

            search_region = gray[y1:y2 + th, x1:x2 + tw]
            if (
                search_region.shape[0] < th
                or search_region.shape[1] < tw
            ):
                continue

            # Template matching
            try:
                result = cv2.matchTemplate(
                    search_region, template, cv2.TM_CCOEFF_NORMED
                )
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > 0.5:  # Match quality threshold
                    found_x = x1 + max_loc[0] + tw // 2
                    found_y = y1 + max_loc[1] + th // 2
                    displacement = float(np.sqrt(
                        (found_x - ref_pos[0]) ** 2
                        + (found_y - ref_pos[1]) ** 2
                    ))
                    displacements[name] = displacement
            except Exception:
                continue

        # Compute shift metrics
        if displacements:
            mean_disp = float(np.mean(list(displacements.values())))
            max_disp = float(np.max(list(displacements.values())))
            shift_detected = mean_disp > self._shift_threshold
        else:
            mean_disp = 0.0
            max_disp = 0.0
            shift_detected = False

        return {
            "shift_detected": shift_detected,
            "mean_displacement_px": round(mean_disp, 2),
            "max_displacement_px": round(max_disp, 2),
            "displacements": {
                k: round(v, 2) for k, v in displacements.items()
            },
            "landmarks_tracked": len(displacements),
        }
