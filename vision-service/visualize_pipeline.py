"""
visualize_pipeline.py — Annotated Video Visualization Tool
===========================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Runs the full detection → tracking → calibration → zone → violation pipeline
and draws rich overlays on every frame for visual debugging and demo purposes.

Features:
- Bounding boxes color-coded by lane assignment
- Vehicle class, track ID, and speed labels
- Semi-transparent lane polygon and BRTS corridor outlines
- Violation/incident banners that flash on-screen
- Live cv2.imshow preview with q-to-quit and spacebar-to-pause
- Simultaneous H.264 .mp4 output written alongside the live preview
- Real-time-paced playback (cv2.waitKey tuned to source FPS)

This is SEPARATE from the production pipeline — it does NOT modify main.py,
event_publisher.py, or the JSONL output. It reuses existing modules and adds
a rendering + display layer on top.

Usage:
    python visualize_pipeline.py --junction junction_01
    python visualize_pipeline.py --junction junction_02
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
from tracker import VehicleTracker, TrackedVehicle
from calibration.homography import CameraCalibrator
from zones.zone_utils import ZoneManager
from violations import ViolationDetector
from incidents import IncidentDetector
from event_publisher import create_publisher, build_junction_event

# ─── Logging ─────────────────────────────────────────────────────────

def setup_logging() -> None:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%H:%M:%S")
    logging.getLogger("ultralytics").setLevel(logging.WARNING)

logger = logging.getLogger("visualize-pipeline")

# ─── Color Palette ───────────────────────────────────────────────────

# Lane colors: distinct, high-contrast BGR tuples
LANE_COLORS = {
    "lane_1": (86, 233, 86),      # Green
    "lane_2": (255, 165, 0),       # Orange-ish (BGR: blue=255, green=165, red=0 → actually cyan)
    "lane_3": (80, 180, 255),      # Warm yellow-orange
    "lane_4": (200, 100, 255),     # Pink
}
# Fallback for unknown lanes
DEFAULT_LANE_COLOR = (200, 200, 200)  # Light gray
BRTS_COLOR = (0, 0, 255)             # Red for BRTS corridor
UNASSIGNED_COLOR = (180, 180, 180)    # Gray for no lane assignment

# Better contrasting palette (BGR)
LANE_PALETTE = [
    (0, 220, 0),       # Lane 1 — bright green
    (255, 140, 0),     # Lane 2 — deep sky blue (BGR)
    (0, 200, 255),     # Lane 3 — amber/yellow
    (255, 0, 200),     # Lane 4 — magenta
    (0, 255, 255),     # Lane 5 — yellow
]


def get_lane_color(lane_id: Optional[str]) -> tuple[int, int, int]:
    """Return a consistent BGR color for a given lane_id."""
    if lane_id is None:
        return UNASSIGNED_COLOR
    # Extract lane number for indexing
    try:
        idx = int(lane_id.split("_")[-1]) - 1
        return LANE_PALETTE[idx % len(LANE_PALETTE)]
    except (ValueError, IndexError):
        return DEFAULT_LANE_COLOR


# ─── Overlay Renderer ───────────────────────────────────────────────

class FrameRenderer:
    """Draws all visualization overlays onto a frame.

    Handles polygon drawing, bounding boxes, labels, banners, and
    frame counter/FPS overlay.
    """

    def __init__(
        self,
        zone_manager: ZoneManager,
        zone_config: dict,
        frame_width: int,
        frame_height: int,
    ) -> None:
        self._zone_manager = zone_manager
        self._frame_w = frame_width
        self._frame_h = frame_height

        # Pre-compute polygon point arrays for drawing
        self._lane_polygon_pts: dict[str, np.ndarray] = {}
        self._brts_polygon_pts: Optional[np.ndarray] = None

        self._parse_polygons(zone_config)

        # Violation banner state: list of (message, frames_remaining)
        self._banners: list[tuple[str, int]] = []
        self._banner_duration = 40  # frames to show each banner

    def _parse_polygons(self, zone_config: dict) -> None:
        """Convert zone_config polygon lists into numpy arrays for cv2 drawing."""
        lanes_config = zone_config.get("lanes", {})
        for lane_id, lane_data in lanes_config.items():
            coords = lane_data.get("polygon", [])
            if coords and len(coords) >= 3:
                pts = np.array(coords, dtype=np.int32)
                self._lane_polygon_pts[lane_id] = pts

        brts_config = zone_config.get("brts_corridor", {})
        brts_coords = brts_config.get("polygon") if brts_config else None
        if brts_coords and len(brts_coords) >= 3:
            self._brts_polygon_pts = np.array(brts_coords, dtype=np.int32)

    def add_banner(self, message: str) -> None:
        """Queue a violation/incident banner to flash on screen."""
        self._banners.append((message, self._banner_duration))

    def render(
        self,
        frame: np.ndarray,
        tracked_vehicles: list[TrackedVehicle],
        calibrator: CameraCalibrator,
        fps: float,
        frame_idx: int,
        total_frames: int,
        processing_fps: float,
        lighting: str,
    ) -> np.ndarray:
        """Draw all overlays onto a frame and return the annotated copy."""
        annotated = frame.copy()

        # 1. Draw zone polygons (semi-transparent)
        self._draw_polygons(annotated)

        # 2. Draw bounding boxes + labels for each vehicle
        for vehicle in tracked_vehicles:
            self._draw_vehicle(annotated, vehicle, calibrator, fps)

        # 3. Draw frame counter / FPS overlay
        self._draw_hud(annotated, frame_idx, total_frames, processing_fps, lighting, len(tracked_vehicles))

        # 4. Draw violation banners
        self._draw_banners(annotated)

        return annotated

    def _draw_polygons(self, frame: np.ndarray) -> None:
        """Draw lane polygons and BRTS corridor as semi-transparent overlays."""
        overlay = frame.copy()

        # Lane polygons: filled with transparency
        for lane_id, pts in self._lane_polygon_pts.items():
            color = get_lane_color(lane_id)
            cv2.fillPoly(overlay, [pts], color)
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)

            # Lane label at centroid
            M = cv2.moments(pts)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(
                    frame, lane_id.upper(),
                    (cx - 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 2, cv2.LINE_AA,
                )

        # BRTS corridor: filled red
        if self._brts_polygon_pts is not None:
            cv2.fillPoly(overlay, [self._brts_polygon_pts], BRTS_COLOR)
            cv2.polylines(frame, [self._brts_polygon_pts], isClosed=True, color=BRTS_COLOR, thickness=3)

            M = cv2.moments(self._brts_polygon_pts)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(
                    frame, "BRTS",
                    (cx - 25, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2, cv2.LINE_AA,
                )

        # Blend overlay (semi-transparent fill)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    def _draw_vehicle(
        self,
        frame: np.ndarray,
        vehicle: TrackedVehicle,
        calibrator: CameraCalibrator,
        fps: float,
    ) -> None:
        """Draw bounding box, label, and speed for one tracked vehicle."""
        x1, y1, x2, y2 = vehicle.bbox.astype(int)

        # Determine lane assignment for color coding
        current_lane = vehicle.lane_history[-1] if vehicle.lane_history else None
        in_brts = self._zone_manager.is_in_brts_corridor(vehicle.bottom_center)

        if in_brts:
            box_color = BRTS_COLOR
            thickness = 3
        else:
            box_color = get_lane_color(current_lane)
            thickness = 2

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, thickness)

        # Compute speed
        speed = calibrator.compute_speed(vehicle.trajectory_world, fps)
        speed_str = f"{speed:.0f} km/h" if speed is not None else "-- km/h"

        # Build label: "car #47 | 42 km/h"
        label = f"{vehicle.class_name} #{vehicle.track_id} | {speed_str}"

        # Draw label background
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_y = max(y1 - 8, th + 4)
        cv2.rectangle(
            frame,
            (x1, label_y - th - 4),
            (x1 + tw + 6, label_y + 4),
            box_color, -1,
        )

        # Label text (white on colored background)
        cv2.putText(
            frame, label,
            (x1 + 3, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (255, 255, 255), 1, cv2.LINE_AA,
        )

        # Draw BRTS warning icon if inside corridor
        if in_brts and vehicle.class_name not in ("bus", "brts_bus"):
            cv2.putText(
                frame, "!! BRTS !!",
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 0, 255), 2, cv2.LINE_AA,
            )

    def _draw_hud(
        self,
        frame: np.ndarray,
        frame_idx: int,
        total_frames: int,
        processing_fps: float,
        lighting: str,
        active_tracks: int,
    ) -> None:
        """Draw frame counter, FPS, and status info in the top-left corner."""
        # Semi-transparent dark background
        hud_h = 120
        hud_w = 380
        overlay = frame.copy()
        cv2.rectangle(overlay, (8, 8), (8 + hud_w, 8 + hud_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        y_offset = 30
        line_height = 22

        lines = [
            f"Frame: {frame_idx}/{total_frames}",
            f"Processing: {processing_fps:.1f} FPS",
            f"Active Tracks: {active_tracks}",
            f"Lighting: {lighting}",
            f"ERakshak Vision | Demo Overlay",
        ]

        for i, line in enumerate(lines):
            cv2.putText(
                frame, line,
                (18, y_offset + i * line_height),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 255, 200), 1, cv2.LINE_AA,
            )

    def _draw_banners(self, frame: np.ndarray) -> None:
        """Draw and tick down violation/incident banners."""
        updated_banners = []
        y_pos = self._frame_h - 60

        for msg, remaining in self._banners:
            if remaining > 0:
                # Flash effect: alternate intensity
                alpha = 0.7 if (remaining % 6) < 3 else 0.9

                # Red banner bar at bottom
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, y_pos - 10), (self._frame_w, y_pos + 40), (0, 0, 200), -1)
                cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

                cv2.putText(
                    frame, msg,
                    (20, y_pos + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2, cv2.LINE_AA,
                )
                y_pos -= 55
                updated_banners.append((msg, remaining - 1))

        self._banners = updated_banners


# ─── Preprocessing (duplicated from main.py to avoid coupling) ───────

class FramePreprocessor:
    """Lighting-aware frame preprocessor (same logic as main.py)."""

    def __init__(self, config: dict) -> None:
        self._enabled = config.get("enable_adaptive", True)
        self._lum_threshold = config.get("luminance_threshold", 80)
        clip_limit = config.get("clahe_clip_limit", 3.0)
        grid_size = tuple(config.get("clahe_grid_size", [8, 8]))
        self._clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
        self._clahe_active = False

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, str]:
        if not self._enabled:
            return frame, "day"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_lum = float(np.mean(gray))

        if mean_lum > self._lum_threshold:
            lighting = "day"
        elif mean_lum > self._lum_threshold * 0.5:
            lighting = "dusk"
        else:
            lighting = "night"

        if mean_lum < self._lum_threshold:
            self._clahe_active = True
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_ch, a_ch, b_ch = cv2.split(lab)
            l_enhanced = self._clahe.apply(l_ch)
            lab_enhanced = cv2.merge([l_enhanced, a_ch, b_ch])
            frame = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        else:
            self._clahe_active = False

        return frame, lighting


# ─── Visualization Pipeline ─────────────────────────────────────────

class VisualizationPipeline:
    """Full pipeline with live preview and annotated video output.

    Reuses existing detector, tracker, calibrator, zone manager, violation
    detector, and incident detector. Adds a rendering layer that draws
    overlays onto each frame and writes the result to both a live window
    and an output .mp4 file.
    """

    def __init__(self, config: dict, junction_id: str) -> None:
        self._config = config
        self._junction_id = junction_id

        # Resolve video source
        junction_config = config["video_sources"].get(junction_id, {})
        self._video_path = junction_config.get("path", "")
        self._configured_fps = junction_config.get("fps")

        if not self._video_path:
            raise ValueError(f"No video source for junction '{junction_id}'")

        # Initialize pipeline components (same as main.py VisionPipeline)
        logger.info(f"Initializing visualization pipeline for: {junction_id}")

        self._preprocessor = FramePreprocessor(config.get("preprocessing", {}))
        self._detector = VehicleDetector(config["model"])

        tracker_config = config.get("tracker", {}).get("config", "trackers/botsort_custom.yaml")
        self._tracker = VehicleTracker(
            model=self._detector.model,
            tracker_config=tracker_config,
            model_config=config["model"],
        )

        camera_config = self._load_camera_config(junction_id)
        self._calibrator = CameraCalibrator(camera_config)

        zone_config = self._load_zone_config(junction_id)
        pcu_factors = config.get("pcu_factors", {})
        self._zone_manager = ZoneManager(zone_config, pcu_factors)

        self._violation_detector = ViolationDetector(
            config.get("violations", {}),
            self._zone_manager,
        )
        self._incident_detector = IncidentDetector(config.get("incidents", {}))

        if camera_config.get("stop_line_world"):
            stop_line = camera_config["stop_line_world"]
            self._incident_detector.set_stop_line_positions(
                [tuple(stop_line)] if stop_line else []
            )

        self._zone_config_raw = zone_config  # Keep for polygon drawing
        self._publisher = create_publisher(config.get("publisher", {}))

    def _load_camera_config(self, junction_id: str) -> dict:
        config_path = SCRIPT_DIR / "calibration" / "camera_config.yaml"
        if not config_path.exists():
            return {}
        with open(config_path, "r", encoding="utf-8") as f:
            camera_configs = yaml.safe_load(f) or {}
        return camera_configs.get("cameras", {}).get(junction_id, {})

    def _load_zone_config(self, junction_id: str) -> dict:
        config_path = SCRIPT_DIR / "zones" / "zone_config.yaml"
        if not config_path.exists():
            return {}
        with open(config_path, "r", encoding="utf-8") as f:
            zone_configs = yaml.safe_load(f) or {}
        if junction_id in zone_configs:
            return zone_configs[junction_id]
        return zone_configs.get("junctions", {}).get(junction_id, {})

    def run(self) -> None:
        """Run the visualization pipeline with live preview and file output."""
        logger.info(f"Opening video: {self._video_path}")

        cap = cv2.VideoCapture(str(self._video_path))
        if not cap.isOpened():
            logger.error(f"Failed to open video: {self._video_path}")
            return

        # Video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        effective_fps = self._configured_fps or video_fps or 20.0
        self._calibrator.fps = effective_fps

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"Video: {total_frames} frames, {frame_w}x{frame_h}, FPS: {effective_fps}")

        # Frame delay for real-time-ish playback (ms)
        frame_delay_ms = max(1, int(1000.0 / effective_fps))

        # Output video writer
        output_dir = SCRIPT_DIR / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{self._junction_id}_annotated.mp4"

        # Try mp4v codec (widely supported). Fall back to XVID if needed.
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fourcc, effective_fps, (frame_w, frame_h))

        if not writer.isOpened():
            logger.error(f"Failed to open VideoWriter at {output_path}")
            cap.release()
            return

        logger.info(f"Output video: {output_path}")

        # Initialize renderer
        renderer = FrameRenderer(
            self._zone_manager,
            self._zone_config_raw,
            frame_w,
            frame_h,
        )

        # Pipeline state
        frame_count = 0
        lane_speeds: dict[str, list[float]] = {}
        fps_timer = time.monotonic()
        fps_frame_count = 0
        processing_fps = 0.0
        paused = False

        window_name = f"ERakshak Vision — {self._junction_id}"

        try:
            while True:
                # Handle pause
                if paused:
                    key = cv2.waitKey(50) & 0xFF
                    if key == ord(" "):
                        paused = False
                        logger.info("Resumed")
                    elif key == ord("q"):
                        logger.info("Quit by user (q)")
                        break
                    continue

                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video stream")
                    break

                # Frame skipping (skip 2 frames for fast real-time CPU performance)
                for _ in range(2):
                    cap.grab()

                frame_count += 3
                fps_frame_count += 3
                timestamp = datetime.now(timezone.utc).isoformat()

                # 1. Preprocess
                processed, lighting = self._preprocessor.process(frame)

                # 2. Detect + Track
                tracked_vehicles = self._tracker.update(processed)

                # 3. Calibrate + Zone assign
                for vehicle in tracked_vehicles:
                    world_pos = self._calibrator.project_ground_contact(vehicle.bbox)
                    if world_pos is not None:
                        vehicle.trajectory_world.append(world_pos)

                    lane_id = self._zone_manager.assign_to_lane(vehicle.bottom_center)
                    vehicle.lane_history.append(lane_id)

                    if vehicle.trajectory_world and lane_id is not None:
                        speed = self._calibrator.compute_speed(
                            vehicle.trajectory_world, effective_fps
                        )
                        if speed is not None:
                            lane_speeds.setdefault(lane_id, []).append(speed)

                # 4. Check violations
                lane_violations, brts_intrusions = self._violation_detector.check(
                    tracked_vehicles, effective_fps, timestamp
                )

                # 5. Check incidents
                stall_alerts = self._incident_detector.check(
                    tracked_vehicles, effective_fps, timestamp
                )

                # Queue banners for violations/incidents
                for lv in lane_violations:
                    renderer.add_banner(
                        f"LANE VIOLATION: {lv.vehicle_class} #{lv.track_id} "
                        f"{lv.from_lane} -> {lv.to_lane}"
                    )
                for bi in brts_intrusions:
                    renderer.add_banner(
                        f"BRTS INTRUSION: {bi.vehicle_class} #{bi.track_id} "
                        f"({bi.dwell_time_s:.1f}s)"
                    )
                for sa in stall_alerts:
                    renderer.add_banner(
                        f"STALL ALERT: {sa.vehicle_class} #{sa.track_id} "
                        f"in {sa.lane_id or 'unknown'}"
                    )

                # 6. Render overlays
                annotated = renderer.render(
                    frame=frame,
                    tracked_vehicles=tracked_vehicles,
                    calibrator=self._calibrator,
                    fps=effective_fps,
                    frame_idx=frame_count,
                    total_frames=total_frames,
                    processing_fps=processing_fps,
                    lighting=lighting,
                )

                # 7. Write to output file
                writer.write(annotated)

                # 8. Show live preview
                cv2.imshow(window_name, annotated)

                # Handle keyboard input with frame-rate-paced delay
                key = cv2.waitKey(frame_delay_ms) & 0xFF
                if key == ord("q"):
                    logger.info("Quit by user (q)")
                    break
                elif key == ord(" "):
                    paused = True
                    logger.info("Paused — press SPACE to resume, Q to quit")

                # FPS benchmark (every 5 seconds of wall-clock time)
                elapsed = time.monotonic() - fps_timer
                if elapsed >= 5.0:
                    processing_fps = fps_frame_count / elapsed
                    fps_timer = time.monotonic()
                    fps_frame_count = 0

                # Console progress (every 100 frames)
                if frame_count % 100 == 0:
                    pct = frame_count / total_frames * 100
                    logger.info(
                        f"Progress: {frame_count}/{total_frames} ({pct:.0f}%) | "
                        f"{processing_fps:.1f} FPS | Tracks: {self._tracker.active_count}"
                    )

                # Publish event contract at emit interval
                emit_interval = self._config.get("publisher", {}).get("emit_interval_frames", 30)
                if frame_count % emit_interval == 0:
                    vehicles_for_zone = [
                        {
                            "pixel_point": v.bottom_center,
                            "world_point": v.trajectory_world[-1] if v.trajectory_world else None,
                            "class_name": v.class_name,
                            "confidence": v.confidence,
                        }
                        for v in tracked_vehicles
                    ]
                    lane_occupancies = self._zone_manager.get_lane_occupancy(vehicles_for_zone)
                    queue_lengths = {lid: self._calibrator.compute_queue_length(occ.vehicle_positions) for lid, occ in lane_occupancies.items()}
                    avg_speeds = {lid: (sum(speeds)/len(speeds) if speeds else 0.0) for lid, speeds in lane_speeds.items()}
                    
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
                    )
                    self._publisher.publish(event)
                    lane_speeds.clear()

        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user (Ctrl+C)")

        finally:
            cap.release()
            writer.release()
            cv2.destroyAllWindows()
            logger.info(
                f"Visualization complete — {frame_count} frames processed. "
                f"Output saved to: {output_path}"
            )


# ─── CLI ─────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ERakshak Vision — Annotated Video Visualization Tool",
    )
    parser.add_argument(
        "--junction", "-j",
        required=True,
        help="Junction ID (e.g., junction_01, junction_02).",
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml in script dir).",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = SCRIPT_DIR / config_path

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    try:
        pipeline = VisualizationPipeline(config, args.junction)
        pipeline.run()
    except Exception as e:
        logger.error(f"Visualization pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
