"""
main.py — Vision Service Pipeline Entry Point
===============================================
ERH26_PS_08: Data-Driven Traffic Optimization

Reads video (file or RTSP stream), runs the full detection → tracking →
calibration → zone assignment → violation/incident check → event publish
pipeline for a single junction.

This is the top-level orchestrator. Each stage is a separate module:
  detector.py → tracker.py → calibration/ → zones/ → violations.py
  → incidents.py → event_publisher.py

Key features:
- Lighting-aware preprocessing (CLAHE engages automatically when dark)
- Per-video FPS from config (not hardcoded — CCTV exports vary widely)
- Graceful error handling (no single corrupt frame crashes the pipeline)
- FPS benchmarking logged at regular intervals

Usage:
    python main.py                          # Process default junction from config
    python main.py --junction junction_01   # Process specific junction
    python main.py --source rtsp://...      # Process RTSP stream
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import yaml

# Add vision-service root to path so imports work when run directly
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from detector import VehicleDetector
from tracker import VehicleTracker
from calibration.homography import CameraCalibrator
from zones.zone_utils import ZoneManager
from violations import ViolationDetector
from incidents import IncidentDetector
from event_publisher import create_publisher, build_junction_event

# ─── Logging Setup ───────────────────────────────────────────────────

def setup_logging() -> None:
    """Configure logging with clear, color-coded output."""
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt="%H:%M:%S",
    )
    # Suppress noisy ultralytics logs
    logging.getLogger("ultralytics").setLevel(logging.WARNING)


logger = logging.getLogger("vision-pipeline")


# ─── Preprocessing ───────────────────────────────────────────────────

class FramePreprocessor:
    """Lighting-aware frame preprocessor.

    Automatically engages CLAHE (Contrast Limited Adaptive Histogram
    Equalization) when the average frame luminance drops below a threshold.
    This improves detection accuracy on dusk/night footage without
    degrading daytime performance.

    Args:
        config: Dict from config.yaml under 'preprocessing' key.
    """

    def __init__(self, config: dict) -> None:
        self._enabled = config.get("enable_adaptive", True)
        self._lum_threshold = config.get("luminance_threshold", 80)
        clip_limit = config.get("clahe_clip_limit", 3.0)
        grid_size = tuple(config.get("clahe_grid_size", [8, 8]))

        self._clahe = cv2.createCLAHE(
            clipLimit=clip_limit,
            tileGridSize=grid_size,
        )

        self._clahe_active = False  # Track whether CLAHE is currently engaged

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, str]:
        """Preprocess a frame with adaptive lighting correction.

        Args:
            frame: BGR image from cv2.VideoCapture.

        Returns:
            Tuple of (processed_frame, lighting_condition).
            lighting_condition is "day", "dusk", or "night" based on luminance.
        """
        if not self._enabled:
            return frame, "day"

        # Compute mean luminance from the value channel (HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_lum = float(np.mean(gray))

        # Classify lighting condition
        if mean_lum > self._lum_threshold:
            lighting = "day"
        elif mean_lum > self._lum_threshold * 0.5:
            lighting = "dusk"
        else:
            lighting = "night"

        # Engage CLAHE for low-light frames
        if mean_lum < self._lum_threshold:
            if not self._clahe_active:
                logger.info(
                    f"CLAHE engaged — mean luminance {mean_lum:.0f} "
                    f"< threshold {self._lum_threshold}"
                )
                self._clahe_active = True

            # Apply CLAHE to the L channel in LAB color space
            # (preserves color better than applying to individual BGR channels)
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            l_enhanced = self._clahe.apply(l_channel)
            lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
            frame = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        else:
            if self._clahe_active:
                logger.info(
                    f"CLAHE disengaged — mean luminance {mean_lum:.0f} "
                    f">= threshold {self._lum_threshold}"
                )
                self._clahe_active = False

        return frame, lighting


# ─── Pipeline ────────────────────────────────────────────────────────

class VisionPipeline:
    """Full vision processing pipeline for a single junction.

    Orchestrates: preprocess → detect/track → calibrate → zone assign →
    violation check → incident check → build event → publish.

    Args:
        config: Full parsed config.yaml dict.
        junction_id: Which junction to process (key in config.video_sources).
        video_source: Override video source path (for RTSP or custom path).
    """

    def __init__(
        self,
        config: dict,
        junction_id: str,
        video_source: Optional[str] = None,
    ) -> None:
        self._config = config
        self._junction_id = junction_id

        # Resolve video source
        junction_config = config["video_sources"].get(junction_id, {})
        self._video_path = video_source or junction_config.get("path", "")
        self._configured_fps = junction_config.get("fps")

        if not self._video_path:
            raise ValueError(
                f"No video source for junction '{junction_id}'. "
                f"Set it in config.yaml → video_sources.{junction_id}.path"
            )

        # Initialize pipeline components
        logger.info(f"Initializing pipeline for junction: {junction_id}")

        self._preprocessor = FramePreprocessor(config.get("preprocessing", {}))
        self._detector = VehicleDetector(config["model"])

        tracker_config = config.get("tracker", {}).get("config", "trackers/botsort_custom.yaml")
        self._tracker = VehicleTracker(
            model=self._detector.model,
            tracker_config=tracker_config,
            model_config=config["model"],
        )

        # Load camera calibration
        camera_config = self._load_camera_config(junction_id)
        self._calibrator = CameraCalibrator(camera_config)

        # Load zone configuration
        zone_config = self._load_zone_config(junction_id)
        pcu_factors = config.get("pcu_factors", {})
        self._zone_manager = ZoneManager(zone_config, pcu_factors)

        # Initialize violation/incident detectors
        self._violation_detector = ViolationDetector(
            config.get("violations", {}),
            self._zone_manager,
        )
        self._incident_detector = IncidentDetector(config.get("incidents", {}))

        # Register stop-line positions for incident detector
        if camera_config.get("stop_line_world"):
            stop_line = camera_config["stop_line_world"]
            self._incident_detector.set_stop_line_positions(
                [tuple(stop_line)] if stop_line else []
            )

        # Event publisher
        self._publisher = create_publisher(config.get("publisher", {}))

        # Pipeline state
        self._emit_interval = config.get("publisher", {}).get("emit_interval_frames", 30)
        self._frame_count = 0
        self._fps_actual = 0.0

        logger.info(f"Pipeline initialized — video: {self._video_path}")

    def _load_camera_config(self, junction_id: str) -> dict:
        """Load camera calibration config for this junction."""
        config_path = SCRIPT_DIR / "calibration" / "camera_config.yaml"
        if not config_path.exists():
            logger.warning(f"Camera config not found at {config_path}")
            return {}

        with open(config_path, "r", encoding="utf-8") as f:
            camera_configs = yaml.safe_load(f) or {}

        return camera_configs.get("cameras", {}).get(junction_id, {})

    def _load_zone_config(self, junction_id: str) -> dict:
        """Load zone/lane polygon config for this junction."""
        config_path = SCRIPT_DIR / "zones" / "zone_config.yaml"
        if not config_path.exists():
            logger.warning(f"Zone config not found at {config_path}")
            return {}

        with open(config_path, "r", encoding="utf-8") as f:
            zone_configs = yaml.safe_load(f) or {}

        if junction_id in zone_configs:
            return zone_configs[junction_id]
        return zone_configs.get("junctions", {}).get(junction_id, {})

    def run(self) -> None:
        """Run the pipeline on the configured video source.

        Reads frames in a loop, processes each through the full pipeline,
        and publishes events at the configured interval. Handles errors
        gracefully — a single corrupt frame doesn't crash the pipeline.
        """
        logger.info(f"Opening video source: {self._video_path}")

        cap = cv2.VideoCapture(str(self._video_path))
        if not cap.isOpened():
            logger.error(
                f"Failed to open video: {self._video_path}\n"
                f"If the codec is unsupported, convert with:\n"
                f"  ffmpeg -i input.avi -c:v libx264 -preset slow -crf 18 output.mp4"
            )
            return

        # Determine FPS: prefer config value, fall back to video metadata
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        effective_fps = self._configured_fps or video_fps or 10.0

        if self._configured_fps:
            logger.info(f"Using configured FPS: {effective_fps}")
        else:
            logger.warning(
                f"FPS not set in config — using video metadata FPS: {video_fps}. "
                f"For accurate speed computation, set fps in config.yaml from ffprobe output."
            )

        # Update calibrator's FPS
        self._calibrator.fps = effective_fps

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(
            f"Video opened — {total_frames} frames, "
            f"effective FPS: {effective_fps}"
        )

        # Per-lane speed accumulators (for averaging over emit interval)
        lane_speeds: dict[str, list[float]] = {}

        fps_timer = time.monotonic()
        fps_frame_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video stream")
                    break

                self._frame_count += 1
                fps_frame_count += 1

                try:
                    self._process_frame(
                        frame, effective_fps, lane_speeds
                    )
                except Exception as e:
                    # Graceful degradation: log and continue, don't crash
                    logger.error(
                        f"Error processing frame {self._frame_count}: {e}",
                        exc_info=True,
                    )
                    continue

                # FPS benchmark logging (every 5 seconds)
                elapsed = time.monotonic() - fps_timer
                if elapsed >= 5.0:
                    self._fps_actual = fps_frame_count / elapsed
                    logger.info(
                        f"Performance: {self._fps_actual:.1f} FPS "
                        f"(frame {self._frame_count}/{total_frames}) "
                        f"| Active tracks: {self._tracker.active_count}"
                    )
                    fps_timer = time.monotonic()
                    fps_frame_count = 0

        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user (Ctrl+C)")

        finally:
            cap.release()
            self._publisher.close()
            logger.info(
                f"Pipeline complete — processed {self._frame_count} frames "
                f"at ~{self._fps_actual:.1f} FPS"
            )

    def _process_frame(
        self,
        frame: np.ndarray,
        fps: float,
        lane_speeds: dict[str, list[float]],
    ) -> None:
        """Process a single frame through the full pipeline.

        Args:
            frame: BGR image from video capture.
            fps: Effective FPS for speed computation.
            lane_speeds: Accumulator for per-lane speeds between event emissions.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # 1. Preprocess (adaptive CLAHE if dark)
        processed_frame, lighting = self._preprocessor.process(frame)

        # 2. Detect + Track (combined via model.track())
        tracked_vehicles = self._tracker.update(processed_frame)

        # 3. Calibrate: project each vehicle to ground plane, compute speed
        for vehicle in tracked_vehicles:
            # Project bottom-center to world coordinates
            world_pos = self._calibrator.project_ground_contact(vehicle.bbox)
            if world_pos is not None:
                vehicle.trajectory_world.append(world_pos)

            # Assign to lane (pass pixel ground-contact point matching zone_config polygons)
            lane_id = self._zone_manager.assign_to_lane(vehicle.bottom_center)
            vehicle.lane_history.append(lane_id)

            if vehicle.trajectory_world and lane_id is not None:
                # Accumulate speed per lane
                speed = self._calibrator.compute_speed(
                    vehicle.trajectory_world, fps
                )
                if speed is not None:
                    if lane_id not in lane_speeds:
                        lane_speeds[lane_id] = []
                    lane_speeds[lane_id].append(speed)

        # 4. Check violations (every frame, but violations only flagged on threshold)
        lane_violations, brts_intrusions = self._violation_detector.check(
            tracked_vehicles, fps, timestamp
        )

        # 5. Check incidents (stalls/breakdowns)
        stall_alerts = self._incident_detector.check(
            tracked_vehicles, fps, timestamp
        )

        # 6. Publish event at configured interval
        if self._frame_count % self._emit_interval == 0:
            self._publish_event(
                timestamp, lighting, tracked_vehicles,
                lane_speeds, lane_violations, brts_intrusions,
                stall_alerts,
            )
            # Reset speed accumulators after publishing
            lane_speeds.clear()

    def _publish_event(
        self,
        timestamp: str,
        lighting: str,
        tracked_vehicles: list,
        lane_speeds: dict[str, list[float]],
        lane_violations: list,
        brts_intrusions: list,
        stall_alerts: list,
    ) -> None:
        """Build and publish a junction event."""
        # Build vehicle list for zone manager
        vehicles_for_zone = []
        for v in tracked_vehicles:
            vehicles_for_zone.append({
                "pixel_point": v.bottom_center,
                "world_point": v.trajectory_world[-1] if v.trajectory_world else None,
                "class_name": v.class_name,
                "confidence": v.confidence,
            })

        # Get per-lane occupancy
        lane_occupancies = self._zone_manager.get_lane_occupancy(vehicles_for_zone)

        # Compute per-lane queue lengths
        queue_lengths: dict[str, Optional[float]] = {}
        for lane_id, occ in lane_occupancies.items():
            queue_lengths[lane_id] = self._calibrator.compute_queue_length(
                occ.vehicle_positions
            )

        # Compute per-lane average speeds
        avg_speeds: dict[str, Optional[float]] = {}
        for lane_id, speeds in lane_speeds.items():
            if speeds:
                avg_speeds[lane_id] = sum(speeds) / len(speeds)

        # Check if a BRTS bus is approaching
        brts_approaching = any(
            v.class_name in ("bus", "brts_bus")
            and self._zone_manager.is_in_brts_corridor(v.trajectory_world[-1])
            for v in tracked_vehicles
            if v.trajectory_world
        )

        # Build and publish the contract event
        event = build_junction_event(
            junction_id=self._junction_id,
            timestamp=timestamp,
            lighting_condition=lighting,
            lane_occupancies=lane_occupancies,
            queue_lengths=queue_lengths,
            avg_speeds=avg_speeds,
            brts_intrusions=brts_intrusions,
            lane_violations=lane_violations,
            stall_alerts=stall_alerts,
            brts_bus_approaching=brts_approaching,
        )

        self._publisher.publish(event)


# ─── CLI ─────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Vision Service — ERH26_PS_08 Traffic Detection Pipeline",
    )
    parser.add_argument(
        "--junction", "-j",
        default=None,
        help="Junction ID from config.yaml (e.g., junction_01). "
             "Defaults to first junction in config.",
    )
    parser.add_argument(
        "--source", "-s",
        default=None,
        help="Override video source (file path or RTSP URL).",
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml in script dir).",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    setup_logging()
    args = parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = SCRIPT_DIR / config_path

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Determine junction
    junction_id = args.junction
    if junction_id is None:
        # Default to first configured junction
        junctions = list(config.get("video_sources", {}).keys())
        if not junctions:
            logger.error("No video sources configured in config.yaml")
            sys.exit(1)
        junction_id = junctions[0]
        logger.info(f"No junction specified — defaulting to: {junction_id}")

    # Run pipeline
    try:
        pipeline = VisionPipeline(
            config=config,
            junction_id=junction_id,
            video_source=args.source,
        )
        pipeline.run()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
