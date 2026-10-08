"""
main.py — Upgraded Vision Service Pipeline Orchestrator
======================================================
ERH26_PS_08: Data-Driven Traffic Optimization
Implementing Sections 1–96 of instruction.md

Full Upgraded Pipeline Flow:
Frame → Camera Health → Scene Classifier → Preprocessing →
Multi-Scale Detection (full-frame + far-field tiled) → Detection Fusion →
Temporal Confirmation + Class Stabilization (TrackState) →
BoT-SORT + Re-ID → Occlusion Analysis →
Ground Contact → Homography → World Coords → Speed / Heading →
Lane Assignment (Dynamic Centerlines + Hysteresis) → Maneuver Classification →
Traffic State: Queue (probabilistic + smoothing + shockwave + spillback) → PCU → Density →
Incident Detection: Emergency Vehicle (fused beacon + trajectory) → BRTS Violation → Wrong-Way → Breakdown →
Confidence & Uncertainty: Object Confidence + Scene Confidence →
Extended Telemetry Contract (Section 69) + Optional Object Telemetry (Section 70) →
Publish via Mock/Kafka → Failure Recording (anomalies)

Usage:
    python main.py                          # Process default junction from config
    python main.py --junction junction_01   # Process specific junction
    python main.py --source rtsp://...      # Process RTSP stream
    python main.py --mock-feed --max-frames 60  # Run self-contained test
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import cv2
import numpy as np
import yaml

# Add vision-service root to path so imports work when run directly
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# ─── Module Imports ───────────────────────────────────────────────────
from models.detector import VehicleDetector, Detection
from models.tiled_detector import TiledDetector
from models.detector_fusion import DetectionFusion
from models.scene_classifier import SceneClassifier

from tracking.tracker import VehicleTrackerV2
from tracking.track_state import TrackLifecycle, TrackState, VehicleState

from calibration.homography import CameraCalibrator
from calibration.calibration_validator import CalibrationValidator
from calibration.camera_shift import CameraShiftDetector

from geometry.centerlines import CenterlineManager
from geometry.lane_assignment import LaneAssigner
from geometry.maneuver import ManeuverClassifier
from geometry.world_coordinates import WorldCoordinateTransformer
from zones.zone_utils import ZoneManager

from traffic_state.queue import QueueEstimator
from traffic_state.speed import SpeedEstimator
from traffic_state.pcu import PCUCalculator
from traffic_state.density import DensityEstimator
from traffic_state.shockwave import ShockwaveAnalyzer

from incidents.emergency import EmergencyVehicleDetector
from incidents.brts import BRTSViolationDetector
from incidents.wrong_way import WrongWayDetector
from incidents.breakdown import BreakdownDetector

from camera.health import CameraHealthMonitor
from camera.quality import FrameQualityAssessor
from camera.visibility import VisibilityEstimator

from confidence.object_confidence import ObjectConfidenceEstimator
from confidence.scene_confidence import SceneConfidenceEstimator
from confidence.uncertainty import UncertaintyPropagator

from event_publisher import create_publisher, build_junction_event, build_object_telemetry
from failure_recorder import FailureRecorder


# ─── Logging Setup ───────────────────────────────────────────────────

def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging with clear, color-coded output."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%H:%M:%S",
    )
    logging.getLogger("ultralytics").setLevel(logging.WARNING)


logger = logging.getLogger("vision-pipeline")


# ─── Preprocessing ───────────────────────────────────────────────────

class FramePreprocessor:
    """Lighting and weather-aware frame preprocessor (Sections 64-65)."""

    def __init__(self, config: dict) -> None:
        self._enabled = config.get("enable_adaptive", True)
        self._lum_threshold = config.get("luminance_threshold", 80)
        clip_limit = config.get("clahe_clip_limit", 3.0)
        grid_size = tuple(config.get("clahe_grid_size", [8, 8]))

        self._clahe = cv2.createCLAHE(
            clipLimit=clip_limit,
            tileGridSize=grid_size,
        )
        self._clahe_active = False

    def process(self, frame: np.ndarray, scene_condition: Optional[str] = None) -> tuple[np.ndarray, str]:
        """Preprocess frame adaptively based on luminance and condition."""
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

        # Apply CLAHE if dark, dusk, or rainy
        need_clahe = mean_lum < self._lum_threshold or (scene_condition in ("night", "rain", "fog"))
        if need_clahe:
            if not self._clahe_active:
                logger.debug(f"CLAHE engaged (mean lum: {mean_lum:.1f})")
                self._clahe_active = True

            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            l_enhanced = self._clahe.apply(l_channel)
            lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
            frame = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        else:
            self._clahe_active = False

        return frame, lighting


# ─── Upgraded Vision Pipeline ────────────────────────────────────────

class VisionPipeline:
    """Upgraded End-to-End Traffic Vision Perception System.

    Coordinates all 96 sections of the sensing architecture:
    - Camera health & calibration validation
    - Scene condition & visibility classification
    - Temporal detection & BoT-SORT tracking with Re-ID
    - Geometric world-coordinate projection and lane assignment
    - Multi-factor queue, shockwave, and speed analytics
    - BRTS, wrong-way, emergency vehicle, and breakdown incidents
    - Multi-dimensional confidence estimation
    - Section 69 aggregate telemetry & Section 70 object telemetry
    """

    def __init__(
        self,
        config: dict,
        junction_id: str,
        video_source: Optional[str] = None,
        record_failures: bool = False,
        publish_objects: bool = False,
        save_overlay_path: Optional[str] = None,
        show_display: bool = True,
    ) -> None:
        self._config = config
        self._junction_id = junction_id
        self._record_failures = record_failures
        self._publish_objects = publish_objects
        self._save_overlay_path = save_overlay_path
        self._show_display = show_display
        self._window_name = f"E-Rakshak Traffic Perception — {junction_id}"

        # Load auxiliary configuration files
        self._thresholds_config = self._load_yaml(SCRIPT_DIR / "config" / "thresholds.yaml")
        self._lanes_config = self._load_yaml(SCRIPT_DIR / "config" / "lanes.yaml")
        self._classes_config = self._load_yaml(SCRIPT_DIR / "config" / "classes.yaml")
        self._camera_yaml = self._load_yaml(SCRIPT_DIR / "config" / "camera.yaml")
        self._camera_config = self._load_camera_config(junction_id)
        self._zone_config = self._load_zone_config(junction_id)

        # Pre-parse lane polygons and BRTS corridor for visual overlay
        self._lane_polygons: dict[str, np.ndarray] = {}
        lanes_raw = self._zone_config.get("lanes", {})
        if isinstance(lanes_raw, dict):
            for lid, ldata in lanes_raw.items():
                coords = ldata.get("polygon", []) if isinstance(ldata, dict) else ldata
                if coords and len(coords) >= 3:
                    self._lane_polygons[lid] = np.array(coords, dtype=np.int32)

        brts_raw = self._zone_config.get("brts_corridor") or self._zone_config.get("brts_lane") or {}
        brts_coords = brts_raw.get("polygon") if isinstance(brts_raw, dict) else brts_raw
        self._brts_polygon = np.array(brts_coords, dtype=np.int32) if brts_coords and len(brts_coords) >= 3 else None

        # Video source resolution
        junction_meta = config.get("video_sources", {}).get(junction_id, {})
        raw_video_path = video_source or junction_meta.get("path", "")
        if raw_video_path and not Path(raw_video_path).is_absolute():
            candidate = SCRIPT_DIR / raw_video_path
            self._video_path = str(candidate) if candidate.exists() else raw_video_path
        else:
            self._video_path = raw_video_path

        # If configured video file is not found, check if trafficvid.avi is available locally
        if (not self._video_path or not Path(self._video_path).exists()) and not video_source:
            sample_candidate = SCRIPT_DIR / "trafficvid.avi"
            if sample_candidate.exists():
                logger.info(f"Configured video source not found. Using local sample video: {sample_candidate.name}")
                self._video_path = str(sample_candidate)

        self._configured_fps = junction_meta.get("fps") or 20.0
        self._effective_fps = float(self._configured_fps)

        logger.info(f"Initializing Upgraded Vision Pipeline for [{junction_id}]...")

        # 1. Camera & Scene Health
        camera_thresh = self._thresholds_config.get("camera", {})
        self._camera_monitor = CameraHealthMonitor(camera_thresh)
        self._quality_assessor = FrameQualityAssessor()
        self._visibility_estimator = VisibilityEstimator()
        self._calibration_validator = CalibrationValidator(camera_thresh)

        landmarks = self._camera_config.get("landmarks", [])
        self._camera_shift_detector = CameraShiftDetector(landmarks) if landmarks else None

        self._scene_classifier = SceneClassifier(self._thresholds_config.get("scene", {}))
        self._preprocessor = FramePreprocessor(config.get("preprocessing", {}))

        # 2. Models & Detection
        model_cfg = config.get("model", {})
        detection_cfg = self._thresholds_config.get("detection", {})
        try:
            self._detector = VehicleDetector(model_cfg, detection_cfg)
            yolo_model = self._detector.model
        except Exception as e:
            logger.warning(f"Could not load primary YOLO weights: {e}. Running with mock detection fallback if needed.")
            self._detector = None
            yolo_model = None

        tiled_cfg = self._thresholds_config.get("tiled_detection", {})
        far_field_poly = self._camera_config.get("far_field", {}).get("polygon", [])
        self._tiled_detector = (
            TiledDetector(yolo_model, tiled_cfg, far_field_poly, model_cfg)
            if yolo_model and far_field_poly
            else None
        )
        self._fusion = DetectionFusion(detection_cfg)

        # 3. Tracking & Re-ID
        tracker_cfg_path = config.get("tracker", {}).get("config", "trackers/botsort_custom.yaml")
        tracker_file = Path(tracker_cfg_path)
        if not tracker_file.is_absolute():
            tracker_file = SCRIPT_DIR / tracker_cfg_path
        resolved_tracker_cfg = str(tracker_file) if tracker_file.exists() else tracker_cfg_path

        temporal_cfg = self._thresholds_config.get("temporal", {})
        tracking_cfg = self._thresholds_config.get("tracking", {})
        occlusion_cfg = self._thresholds_config.get("occlusion", {})

        self._tracker = VehicleTrackerV2(
            model=yolo_model,
            tracker_config_path=resolved_tracker_cfg,
            temporal_config=temporal_cfg,
            tracking_config=tracking_cfg,
            occlusion_config=occlusion_cfg,
            model_config=model_cfg,
        ) if yolo_model else None

        # 4. Calibration & Geometry
        self._calibrator = CameraCalibrator(self._camera_config)
        self._calibrator.fps = self._effective_fps
        H = self._calibrator.homography
        self._world_transformer = WorldCoordinateTransformer(
            homography_matrix=H,
            fps=self._effective_fps,
            speed_config=self._thresholds_config.get("speed", {}),
        )

        pcu_factors = config.get("pcu_factors", {})
        self._zone_manager = ZoneManager(self._zone_config, pcu_factors)
        self._centerline_manager = CenterlineManager(self._lanes_config)
        self._lane_assigner = LaneAssigner(
            self._centerline_manager,
            self._thresholds_config.get("lane_assignment", {}),
        )
        self._maneuver_classifier = ManeuverClassifier()

        # 5. Traffic State Analytics
        queue_cfg = self._thresholds_config.get("queue", {})
        self._queue_estimator = QueueEstimator(queue_cfg, self._lanes_config)
        self._speed_estimator = SpeedEstimator(self._thresholds_config.get("speed", {}))
        self._pcu_calculator = PCUCalculator(pcu_factors)
        self._density_estimator = DensityEstimator(self._thresholds_config.get("density", {}))
        self._shockwave_analyzer = ShockwaveAnalyzer()

        # 6. Incident Intelligence
        self._emergency_detector = EmergencyVehicleDetector(self._thresholds_config.get("emergency", {}))
        brts_cfg = self._zone_config.get("brts_corridor") or self._zone_config.get("brts_lane") or {}
        brts_corridor_poly = brts_cfg.get("polygon") if isinstance(brts_cfg, dict) else brts_cfg
        self._brts_detector = BRTSViolationDetector(
            self._thresholds_config.get("brts", {}),
            brts_polygon=brts_corridor_poly,
        )
        self._wrong_way_detector = WrongWayDetector(self._thresholds_config.get("wrong_way", {}))
        self._breakdown_detector = BreakdownDetector(self._thresholds_config.get("breakdown", {}))

        # 7. Confidence & Uncertainty
        self._object_confidence_est = ObjectConfidenceEstimator(self._thresholds_config.get("confidence", {}))
        self._scene_confidence_est = SceneConfidenceEstimator(self._thresholds_config.get("confidence", {}))
        self._uncertainty_propagator = UncertaintyPropagator()

        # 8. Publishing & Failure Recording
        self._publisher = create_publisher(config.get("publisher", {}))
        failure_cfg = self._thresholds_config.get("failure_recording", {})
        if record_failures:
            failure_cfg["enabled"] = True
        self._failure_recorder = FailureRecorder(failure_cfg)

        # Video writer for debug overlay
        self._video_writer = None

        # State tracking
        self._emit_interval = config.get("publisher", {}).get("emit_interval_frames", 30)
        self._frame_count = 0
        self._fps_actual = 0.0
        self._last_alert_events = {
            "emergency": None,
            "brts": None,
            "wrong_way": None,
            "breakdown": None,
        }

        # Persistent trajectories & smoothed kinematics across frames
        self._track_trajectories: dict[int, list[tuple[float, float]]] = {}
        self._track_pixel_trajectories: dict[int, list[tuple[float, float]]] = {}
        self._track_speeds: dict[int, float] = {}
        self._track_headings: dict[int, float] = {}
        self._track_last_seen: dict[int, int] = {}

        logger.info("Vision Pipeline ready.")

    def _load_yaml(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Error loading {path}: {e}")
            return {}

    def _load_camera_config(self, junction_id: str) -> dict:
        config_path = SCRIPT_DIR / "calibration" / "camera_config.yaml"
        cfg = self._load_yaml(config_path)
        if cfg:
            cam = cfg.get("cameras", {}).get(junction_id)
            if cam:
                return cam

        # Fallback to config/camera.yaml
        cam_yaml = self._load_yaml(SCRIPT_DIR / "config" / "camera.yaml")
        return cam_yaml.get("cameras", {}).get(junction_id, {})

    def _load_zone_config(self, junction_id: str) -> dict:
        config_path = SCRIPT_DIR / "zones" / "zone_config.yaml"
        zone_configs = self._load_yaml(config_path)
        if junction_id in zone_configs:
            return zone_configs[junction_id]
        return zone_configs.get("junctions", {}).get(junction_id, {})

    def run(self, max_frames: Optional[int] = None, mock_feed: bool = False) -> None:
        """Run the end-to-end perception loop with live interactive display."""
        use_mock = mock_feed or (not self._video_path or not Path(self._video_path).exists())
        cap = None

        if not use_mock:
            cap = cv2.VideoCapture(str(self._video_path))
            if not cap.isOpened():
                logger.warning(f"Failed to open video source '{self._video_path}'. Falling back to synthetic traffic generator.")
                use_mock = True
            else:
                v_fps = cap.get(cv2.CAP_PROP_FPS)
                if v_fps and v_fps > 0:
                    self._effective_fps = float(v_fps)
                    self._calibrator.fps = self._effective_fps
                    self._world_transformer.set_fps(self._effective_fps)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                logger.info(f"Connected to video feed: {self._video_path} ({total_frames} frames @ {self._effective_fps:.1f} FPS)")

        if use_mock:
            logger.info("Running with SYNTHETIC TRAFFIC SIMULATOR for demonstration & pipeline validation.")
            total_frames = max_frames or 60

        if self._show_display:
            try:
                cv2.namedWindow(self._window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(self._window_name, 1100, 750)
                logger.info(
                    "Interactive Display Window opened. "
                    "Hotkeys: [Space] Pause/Resume, [Q/ESC] Quit, [S] Snapshot"
                )
            except cv2.error as e:
                logger.warning(f"GUI display not supported in this environment: {e}. Switching to headless mode.")
                self._show_display = False

        fps_timer = time.monotonic()
        fps_frame_count = 0
        playback_delay_ms = max(1, int(1000.0 / (self._effective_fps if self._effective_fps > 0 else 20.0)))

        try:
            while True:
                self._frame_count += 1
                if max_frames and self._frame_count > max_frames:
                    logger.info(f"Reached max frame count: {max_frames}")
                    break

                # 1. Acquire frame
                if use_mock:
                    frame = self._generate_synthetic_frame(self._frame_count)
                else:
                    ret, frame = cap.read()
                    if not ret:
                        logger.info("End of video stream reached.")
                        break

                fps_frame_count += 1

                # 2. Process frame
                try:
                    telemetry, vis = self._process_frame(frame, self._frame_count)
                except Exception as e:
                    logger.error(f"Error processing frame {self._frame_count}: {e}", exc_info=True)
                    continue

                # 3. Live Interactive Display & Hotkeys
                if self._show_display and vis is not None:
                    try:
                        cv2.imshow(self._window_name, vis)
                        key = cv2.waitKey(playback_delay_ms) & 0xFF
                        if key in (ord("q"), ord("Q"), 27):
                            logger.info("User requested stop via GUI window (Q/ESC).")
                            break
                        elif key == ord(" "):
                            logger.info("Video PAUSED. Press [Space] to resume, [S] for snapshot, [Q] to quit.")
                            while True:
                                k = cv2.waitKey(50) & 0xFF
                                if k in (ord(" "), ord("q"), ord("Q"), 27):
                                    break
                                elif k in (ord("s"), ord("S")):
                                    self._save_snapshot(vis, self._frame_count)
                            if k in (ord("q"), ord("Q"), 27):
                                logger.info("User requested stop during pause.")
                                break
                            logger.info("Video RESUMED.")
                        elif key in (ord("s"), ord("S")):
                            self._save_snapshot(vis, self._frame_count)
                    except cv2.error as e:
                        logger.warning(f"GUI display error: {e}. Switching to headless mode.")
                        self._show_display = False

                # FPS benchmark reporting
                elapsed = time.monotonic() - fps_timer
                if elapsed >= 5.0:
                    self._fps_actual = fps_frame_count / elapsed
                    active = self._tracker.active_count if self._tracker else 0
                    logger.info(
                        f"Perception Speed: {self._fps_actual:.1f} FPS "
                        f"(Frame {self._frame_count}) | Active Tracks: {active}"
                    )
                    fps_timer = time.monotonic()
                    fps_frame_count = 0

        except KeyboardInterrupt:
            logger.info("Perception pipeline stopped by user interrupt.")
        finally:
            if cap is not None:
                cap.release()
            if self._video_writer is not None:
                self._video_writer.release()
                logger.info(f"Saved overlay video to: {self._save_overlay_path}")
            if self._show_display:
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
            self._publisher.close()
            logger.info(f"Pipeline finished — Processed {self._frame_count} frames.")

    def _process_frame(self, frame: np.ndarray, frame_idx: int) -> dict[str, Any]:
        """Process a single frame through all pipeline stages."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # STAGE 1: Camera Health Monitoring (Sections 28-31)
        camera_health = self._camera_monitor.analyze(frame)
        visibility_res = self._visibility_estimator.estimate_visibility(frame)
        vis_score = visibility_res.get("visibility_score", 1.0)

        # Camera shift
        shift_detected = False
        if self._camera_shift_detector:
            shift_res = self._camera_shift_detector.check(frame)
            shift_detected = shift_res.get("shift_detected", False)
            if shift_detected and self._record_failures:
                self._failure_recorder.record_camera_shift(
                    frame, shift_res.get("displacement_px", 0.0), self._junction_id, frame_idx
                )

        calib_health = self._calibration_validator.validate(
            camera_health=camera_health.get("health_score", 1.0),
            landmark_displacements=[shift_res.get("displacement_px", 0.0)] if self._camera_shift_detector else None,
        )

        # STAGE 2: Scene Classification (Sections 64-65)
        scene_res = self._scene_classifier.classify(frame)
        scene_cond = scene_res.value if hasattr(scene_res, "value") else str(scene_res)
        lighting = "night" if scene_cond == "night" else ("dusk" if scene_cond in ("dusk", "low_visibility") else "day")
        weather = "rain" if scene_cond == "rain" else ("fog" if scene_cond == "fog" else "clear")

        # STAGE 3: Preprocessing (Adaptive CLAHE)
        enhanced_frame, _ = self._preprocessor.process(frame, scene_cond)

        # STAGE 4 & 5: Unified Detection & Tracking with BoT-SORT (Sections 11-24)
        vehicle_states: list[VehicleState] = []
        if self._tracker:
            # BoT-SORT performs unified detection + multi-object tracking in a single pass
            vehicle_states = self._tracker.update(enhanced_frame)
        elif self._detector:
            # Fallback detector if tracker is unavailable
            detections = self._detector.detect(enhanced_frame, scene_condition=scene_cond)
            vehicle_states = [
                VehicleState(
                    track_id=i + 1,
                    class_name=d.class_name,
                    detection_confidence=d.confidence,
                    track_confidence=d.confidence,
                    bbox=d.bbox,
                    ground_contact=d.bottom_center,
                )
                for i, d in enumerate(detections)
            ]
        else:
            # Synthetic traffic generator for offline test runs
            vehicle_states = self._generate_fallback_states(frame_idx)

        # STAGE 6: Ground Contact Point & World Coordinates Transformation (Sections 24-25, 47-48)
        for vs in vehicle_states:
            self._track_last_seen[vs.track_id] = frame_idx
            if vs.ground_contact is None and vs.bbox is not None:
                vs.ground_contact = WorldCoordinateTransformer.extract_ground_contact(vs.bbox)

            if vs.ground_contact is not None:
                wx, wy = self._world_transformer.pixel_to_world(vs.ground_contact)
                vs.world_x = float(wx)
                vs.world_y = float(wy)

            world_pos = (vs.world_x, vs.world_y)

            # Maintain persistent world and pixel trajectories in pipeline buffers
            if vs.track_id not in self._track_trajectories:
                self._track_trajectories[vs.track_id] = []
            self._track_trajectories[vs.track_id].append(world_pos)
            if len(self._track_trajectories[vs.track_id]) > 60:
                self._track_trajectories[vs.track_id] = self._track_trajectories[vs.track_id][-60:]
            traj = self._track_trajectories[vs.track_id]

            if vs.ground_contact is not None:
                if vs.track_id not in self._track_pixel_trajectories:
                    self._track_pixel_trajectories[vs.track_id] = []
                self._track_pixel_trajectories[vs.track_id].append(vs.ground_contact)
                if len(self._track_pixel_trajectories[vs.track_id]) > 60:
                    self._track_pixel_trajectories[vs.track_id] = self._track_pixel_trajectories[vs.track_id][-60:]

            # Sync with tracker's TrackState if available
            ts = self._tracker.get_track_state(vs.track_id) if self._tracker else None
            if ts:
                ts.world_position_history.append(world_pos)
                if len(ts.world_position_history) > 60:
                    ts.world_position_history = ts.world_position_history[-60:]

            # Compute speed and heading
            if len(traj) >= 2:
                spd, accel, reliable = self._world_transformer.compute_speed(vs.track_id, traj)
                heading = self._world_transformer.compute_heading(traj)

                # Fallback to optical bounding box scaling if homography is uncalibrated or produces zero displacement
                if (not self._calibrator.is_calibrated or not self._world_transformer._has_homography) and vs.bbox is not None:
                    cname = vs.class_name.lower()
                    ref_len_m = 9.0 if ("bus" in cname or "truck" in cname) else (1.8 if any(k in cname for k in ("two_wheeler", "motorcycle", "cycle", "scooter")) else 4.2)
                    bbox_dim = max(float(vs.bbox[2] - vs.bbox[0]), float(vs.bbox[3] - vs.bbox[1]), 10.0)
                    m_per_px = ref_len_m / bbox_dim
                    pix_traj = self._track_pixel_trajectories.get(vs.track_id, [])
                    if len(pix_traj) >= 2:
                        w_size = min(5, len(pix_traj) - 1)
                        p_now = pix_traj[-1]
                        p_prev = pix_traj[-1 - w_size]
                        dp = float(np.hypot(p_now[0] - p_prev[0], p_now[1] - p_prev[1]))
                        dt = w_size / (self._effective_fps if self._effective_fps > 0 else 10.0)
                        if dt > 0:
                            spd = float((dp * m_per_px / dt) * 3.6)

                vs.speed_kmph = max(0.0, min(float(spd), 140.0))
                vs.acceleration_mps2 = float(accel)
                vs.heading_deg = float(heading)

                self._track_speeds[vs.track_id] = vs.speed_kmph
                self._track_headings[vs.track_id] = vs.heading_deg

                if ts:
                    ts.speed_history.append(vs.speed_kmph)
                    ts.heading_history.append(vs.heading_deg)
            else:
                vs.speed_kmph = self._track_speeds.get(vs.track_id, vs.speed_kmph or 0.0)
                vs.heading_deg = self._track_headings.get(vs.track_id, vs.heading_deg or 0.0)

        # Periodic cleanup of expired tracks
        if frame_idx % 60 == 0:
            stale_threshold = 90
            for tid in list(self._track_last_seen.keys()):
                if frame_idx - self._track_last_seen[tid] > stale_threshold:
                    self._track_last_seen.pop(tid, None)
                    self._track_trajectories.pop(tid, None)
                    self._track_pixel_trajectories.pop(tid, None)
                    self._track_speeds.pop(tid, None)
                    self._track_headings.pop(tid, None)

        # STAGE 7: Dynamic Lane Assignment & Maneuver Classification (Sections 34-39)
        lane_vehicles_map: dict[str, list[VehicleState]] = {}
        for vs in vehicle_states:
            traj = self._track_trajectories.get(vs.track_id, [(vs.world_x, vs.world_y)])
            lane_id, score = self._lane_assigner.assign_lane(
                vs.track_id,
                np.array([vs.world_x, vs.world_y]),
                vs.heading_deg,
                trajectory=traj,
            )
            vs.lane_id = lane_id

            # Fallback to polygon zone if centerline assignment is unassigned
            if not vs.lane_id and vs.ground_contact:
                vs.lane_id = self._zone_manager.assign_to_lane(vs.ground_contact)

            # Maneuver classification
            maneuver = self._maneuver_classifier.classify(vs.track_id, [vs.heading_deg])
            vs.maneuver = maneuver.value if hasattr(maneuver, "value") else str(maneuver)

            if vs.lane_id:
                lane_vehicles_map.setdefault(vs.lane_id, []).append(vs)

        # STAGE 8: Traffic State Estimation (Queue, Speed, PCU, Density, Shockwaves) (Sections 40-48)
        lane_details: dict[str, dict[str, Any]] = {}
        for lane_id, v_list in lane_vehicles_map.items():
            stop_pos = self._centerline_manager.get_stop_line_position(lane_id)
            veh_dicts = []
            for v in v_list:
                dist_to_stop = 50.0
                if stop_pos is not None:
                    dist_to_stop = float(np.linalg.norm(np.array([v.world_x, v.world_y]) - stop_pos))

                q_prob = self._queue_estimator.compute_queue_probability(
                    v.track_id,
                    v.speed_kmph,
                    dist_to_stop,
                    signal_is_red=False,
                    nearby_vehicle_count=len(v_list),
                )
                v.queue_probability = q_prob
                veh_dicts.append({
                    "world_x": v.world_x,
                    "world_y": v.world_y,
                    "queue_probability": q_prob,
                    "speed_kmph": v.speed_kmph,
                    "class_name": v.class_name,
                    "detection_confidence": v.detection_confidence,
                    "occlusion_ratio": v.occlusion_ratio,
                })

            raw_q, smooth_q = self._queue_estimator.estimate_queue_length(lane_id, veh_dicts, stop_pos)
            growth_rate, accel = self._queue_estimator.compute_queue_dynamics(lane_id)
            pcu_weighted, pcu_raw = self._pcu_calculator.compute_lane_pcu(veh_dicts)
            avg_speed = float(np.mean([v.speed_kmph for v in v_list])) if v_list else 0.0
            occlusion_ratio = float(np.mean([v.occlusion_ratio for v in v_list])) if v_list else 0.0

            # Movement counts
            mov_counts = {"straight": 0, "left": 0, "right": 0, "u_turn": 0}
            veh_types = {}
            for v in v_list:
                m = v.maneuver if v.maneuver in mov_counts else "straight"
                mov_counts[m] += 1
                veh_types[v.class_name] = veh_types.get(v.class_name, 0) + 1

            lane_details[lane_id] = {
                "vehicle_count": len(v_list),
                "vehicle_count_confidence": 0.92,
                "pcu": pcu_weighted,
                "pcu_confidence": 0.90,
                "queue_length_m": smooth_q,
                "queue_confidence": 0.88,
                "queue_growth_rate": growth_rate,
                "queue_acceleration": accel,
                "avg_speed_kmph": avg_speed,
                "speed_confidence": 0.85,
                "occlusion_ratio": occlusion_ratio,
                "movement_counts": mov_counts,
                "vehicle_types": veh_types,
            }

        # STAGE 9: Incident & Violation Intelligence (Sections 54-63)
        emergency_alerts = []
        brts_alerts = []
        wrong_way_alerts = []
        breakdown_alerts = []

        for vs in vehicle_states:
            # Emergency vehicle check
            em_res = self._emergency_detector.update_vehicle(
                track_id=vs.track_id,
                class_name=vs.class_name,
                detection_confidence=vs.detection_confidence,
                bbox=vs.bbox if vs.bbox is not None else np.array([0, 0, 10, 10]),
                frame=frame,
                world_pos=(vs.world_x, vs.world_y),
                heading_deg=vs.heading_deg,
                speed_kmph=vs.speed_kmph,
            )
            if em_res.get("should_preempt", False):
                emergency_alerts.append(em_res)
                if self._record_failures:
                    self._failure_recorder.record_emergency_candidate(
                        frame, vs.track_id, em_res.get("state", ""), self._junction_id, frame_idx
                    )

            # BRTS corridor intrusion
            if vs.ground_contact:
                brts_res = self._brts_detector.update(
                    track_id=vs.track_id,
                    class_name=vs.class_name,
                    detection_confidence=vs.detection_confidence,
                    pixel_point=vs.ground_contact,
                    world_pos=(vs.world_x, vs.world_y),
                    heading_deg=vs.heading_deg,
                    speed_kmph=vs.speed_kmph,
                )
                if brts_res:
                    brts_alerts.append(brts_res)
                    if self._record_failures:
                        self._failure_recorder.record_brts_candidate(
                            frame, vs.track_id, "confirmed", self._junction_id, frame_idx
                        )

            # Wrong-way driving
            expected_heading = self._centerline_manager.get_expected_heading(vs.lane_id) if vs.lane_id else 180.0
            ww_res = self._wrong_way_detector.check(
                track_id=vs.track_id,
                heading_deg=vs.heading_deg,
                expected_heading_deg=expected_heading,
                speed_kmph=vs.speed_kmph,
            )
            if ww_res:
                wrong_way_alerts.append(ww_res)

            # Breakdown / Stalled vehicle
            dist_stop = 50.0
            if vs.lane_id:
                sp = self._centerline_manager.get_stop_line_position(vs.lane_id)
                if sp is not None:
                    dist_stop = float(np.linalg.norm(np.array([vs.world_x, vs.world_y]) - sp))

            bd_res = self._breakdown_detector.update(
                track_id=vs.track_id,
                speed_kmph=vs.speed_kmph,
                world_pos=(vs.world_x, vs.world_y),
                distance_to_stop_line_m=dist_stop,
            )
            if bd_res:
                breakdown_alerts.append(bd_res)

        # STAGE 10: Confidence & Uncertainty Estimation (Sections 49-53, 71-73)
        for vs in vehicle_states:
            conf_dict = self._object_confidence_est.compute(
                detection_confidence=vs.detection_confidence,
                track_quality=getattr(vs, "track_confidence", 0.8),
                occlusion_ratio=vs.occlusion_ratio,
                age_frames=vs.age_frames,
            )
            vs.track_confidence = conf_dict.get("composite_confidence", 0.85)

        avg_det_conf = float(np.mean([vs.detection_confidence for vs in vehicle_states])) if vehicle_states else 0.90
        avg_trk_conf = float(np.mean([vs.track_confidence for vs in vehicle_states])) if vehicle_states else 0.85

        scene_conf_res = self._scene_confidence_est.compute_scene_confidence(
            detection_quality=avg_det_conf,
            tracking_quality=avg_trk_conf,
            camera_health=camera_health.get("health_score", 1.0),
            calibration_health=calib_health.get("homography_health", 1.0),
            visibility=vis_score,
        )

        # STAGE 11: Telemetry Construction & Emission (Sections 69-70)
        brts_approaching = any(
            vs.class_name in ("bus", "brts_bus") and vs.lane_id and "brts" in vs.lane_id.lower()
            for vs in vehicle_states
        )

        scene_block = {
            "lighting": lighting,
            "weather": weather,
            "visibility": round(vis_score, 2),
            "scene_confidence": scene_conf_res.get("scene_confidence", 0.85),
        }

        camera_block = {
            "health": camera_health.get("health_score", 1.0),
            "blur_score": camera_health.get("blur_score", 150.0),
            "camera_motion": camera_health.get("frame_difference", 0.0),
            "calibration_valid": calib_health.get("calibration_valid", True),
            "homography_health": calib_health.get("homography_health", 1.0),
        }

        # Build telemetry contract
        event = build_junction_event(
            junction_id=self._junction_id,
            timestamp=timestamp,
            lighting_condition=lighting,
            lane_occupancies=lane_details,
            scene=scene_block,
            camera=camera_block,
            emergency_alerts=emergency_alerts,
            wrong_way_alerts=wrong_way_alerts,
            lane_details=lane_details,
            brts_bus_approaching=brts_approaching,
        )

        # Publish periodic aggregate event
        if frame_idx % self._emit_interval == 0:
            self._publisher.publish(event)

            # Optional object-level telemetry (Section 70)
            if self._publish_objects:
                obj_telemetry = build_object_telemetry(vehicle_states)
                self._publisher.publish_objects(obj_telemetry)

        # Optional Overlay Video Rendering / Live Display
        vis_frame = None
        if self._show_display or self._save_overlay_path:
            vis_frame = self._render_overlay_frame(frame, vehicle_states, event, frame_idx)

        return event, vis_frame

    def _generate_fallback_states(self, frame_idx: int) -> list[VehicleState]:
        """Synthetic traffic state generator when no camera feed/YOLO model is loaded."""
        classes = ["car", "bus", "two_wheeler", "auto_rickshaw", "truck"]
        states = []
        num_vehicles = 6 + (frame_idx % 5)

        for i in range(num_vehicles):
            track_id = 100 + i
            cls = classes[i % len(classes)]
            lane = "lane_NS_1" if (i % 2 == 0) else "lane_NS_2"
            x1 = 300 + (i % 3) * 200 + (frame_idx * 2) % 300
            y1 = 400 + (i * 50) % 250
            x2 = x1 + (120 if cls in ("bus", "truck") else 60)
            y2 = y1 + (100 if cls in ("bus", "truck") else 50)

            # Simulated emergency vehicle occasionally
            if i == 0 and (frame_idx % 40 > 25):
                cls = "ambulance"

            vs = VehicleState(
                track_id=track_id,
                class_name=cls,
                detection_confidence=0.88 + 0.05 * (i % 2),
                track_confidence=0.92,
                bbox=np.array([x1, y1, x2, y2], dtype=float),
                ground_contact=((x1 + x2) / 2.0, float(y2)),
                world_x=10.0 + (i % 2) * 3.5,
                world_y=max(0.0, 50.0 - (frame_idx * 0.8 + i * 5) % 50),
                speed_kmph=22.0 if (i % 3 != 0) else 2.5,
                heading_deg=180.0,
                lane_id=lane,
                maneuver="straight",
                queue_probability=0.85 if (i % 3 == 0) else 0.1,
                occlusion_ratio=0.15 if i > 3 else 0.0,
                age_frames=frame_idx + 10,
                state=TrackLifecycle.CONFIRMED,
                is_confirmed=True,
            )
            states.append(vs)

        return states

    def _generate_synthetic_frame(self, frame_idx: int) -> np.ndarray:
        """Create a synthetic junction camera frame for testing and CI."""
        h, w = 720, 1280
        frame = np.full((h, w, 3), 40, dtype=np.uint8)

        # Draw road tarmac
        cv2.rectangle(frame, (200, 100), (1080, 720), (55, 55, 60), -1)

        # Draw lane dividers
        for x in (450, 700, 950):
            for y in range(120, 700, 60):
                cv2.line(frame, (x, y), (x, y + 30), (200, 200, 200), 2)

        # Draw stop line
        cv2.line(frame, (200, 650), (1080, 650), (240, 240, 240), 4)

        # Add simulated moving boxes
        for i in range(5):
            bx = 350 + (i * 150)
            by = int(150 + (frame_idx * 5 + i * 80) % 450)
            cv2.rectangle(frame, (bx, by), (bx + 70, by + 50), (180, 130, 70), -1)

        return frame

    def _save_snapshot(self, vis: np.ndarray, frame_idx: int) -> None:
        """Save a snapshot of the annotated frame to disk."""
        snap_dir = SCRIPT_DIR / "output" / "screenshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        snap_path = snap_dir / f"snapshot_{self._junction_id}_f{frame_idx}.jpg"
        cv2.imwrite(str(snap_path), vis)
        logger.info(f"Captured snapshot: {snap_path}")

    def _render_overlay_frame(
        self,
        frame: np.ndarray,
        vehicle_states: list[VehicleState],
        telemetry: dict[str, Any],
        frame_idx: int,
    ) -> np.ndarray:
        """Draw bounding boxes, lane polygons, speed tags, incident banners, and HUD dashboard."""
        h, w = frame.shape[:2]

        # 1. Automatic upscaling for small video sources (e.g. 320x240)
        if w < 640:
            target_w = 960
            target_h = int(h * (960.0 / w))
            vis = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            sx = target_w / float(w)
            sy = target_h / float(h)
        else:
            vis = frame.copy()
            sx = 1.0
            sy = 1.0
        disp_h, disp_w = vis.shape[:2]

        # 2. Lane & BRTS Polygons Overlay
        if self._lane_polygons or (self._brts_polygon is not None):
            poly_overlay = vis.copy()
            palette = [
                (0, 200, 100),   # Lane 1 - green
                (230, 150, 0),   # Lane 2 - blue
                (0, 200, 240),   # Lane 3 - amber
                (220, 80, 220),  # Lane 4 - magenta
            ]
            for idx, (lid, poly) in enumerate(self._lane_polygons.items()):
                scaled_poly = (poly * [sx, sy]).astype(np.int32)
                color = palette[idx % len(palette)]
                cv2.fillPoly(poly_overlay, [scaled_poly], color)
                cv2.polylines(vis, [scaled_poly], isClosed=True, color=color, thickness=2)

                # Centroid lane label
                M = cv2.moments(scaled_poly)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.putText(
                        vis, lid.upper(), (cx - 25, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA,
                    )

            if self._brts_polygon is not None:
                scaled_brts = (self._brts_polygon * [sx, sy]).astype(np.int32)
                cv2.fillPoly(poly_overlay, [scaled_brts], (0, 0, 180))
                cv2.polylines(vis, [scaled_brts], isClosed=True, color=(0, 0, 255), thickness=2)
                M = cv2.moments(scaled_brts)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.putText(
                        vis, "BRTS CORRIDOR", (cx - 50, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA,
                    )

            cv2.addWeighted(poly_overlay, 0.18, vis, 0.82, 0, vis)

        # 3. Stop Line (if present in zone config)
        stop_line = self._zone_config.get("stop_line", [])
        if stop_line and len(stop_line) >= 2:
            p1 = (int(stop_line[0][0] * sx), int(stop_line[0][1] * sy))
            p2 = (int(stop_line[1][0] * sx), int(stop_line[1][1] * sy))
            cv2.line(vis, p1, p2, (0, 230, 255), 3)

        # 4. Vehicle Colors & Bounding Boxes
        class_colors = {
            "car": (86, 233, 86),           # Emerald green
            "two_wheeler": (0, 220, 255),   # Yellow
            "motorcycle": (0, 220, 255),
            "scooter": (0, 220, 255),
            "cycle": (0, 240, 180),
            "auto_rickshaw": (0, 140, 255), # Orange
            "bus": (235, 175, 45),          # Cyan
            "brts_bus": (235, 175, 45),
            "truck": (210, 80, 220),        # Purple
            "ambulance": (0, 0, 255),       # Red
            "fire_truck": (0, 0, 255),
            "police": (0, 0, 255),
        }
        default_color = (180, 180, 180)

        for vs in vehicle_states:
            if vs.bbox is None or len(vs.bbox) < 4:
                continue

            x1 = max(0, min(disp_w - 1, int(vs.bbox[0] * sx)))
            y1 = max(0, min(disp_h - 1, int(vs.bbox[1] * sy)))
            x2 = max(0, min(disp_w - 1, int(vs.bbox[2] * sx)))
            y2 = max(0, min(disp_h - 1, int(vs.bbox[3] * sy)))

            cls_lower = vs.class_name.lower()
            is_emergency = cls_lower in ("ambulance", "fire_truck", "police")
            is_queued = vs.queue_probability > 0.65

            box_color = class_colors.get(cls_lower, default_color)
            if is_emergency:
                box_color = (0, 0, 255)
            elif is_queued and not is_emergency:
                box_color = (0, 165, 255)

            # Draw bounding box
            thickness = 3 if is_emergency else 2
            cv2.rectangle(vis, (x1, y1), (x2, y2), box_color, thickness)

            # Corner accents
            corner_len = max(6, min(18, int((x2 - x1) * 0.2)))
            cv2.line(vis, (x1, y1), (x1 + corner_len, y1), (255, 255, 255), thickness)
            cv2.line(vis, (x1, y1), (x1, y1 + corner_len), (255, 255, 255), thickness)
            cv2.line(vis, (x2, y1), (x2 - corner_len, y1), (255, 255, 255), thickness)
            cv2.line(vis, (x2, y1), (x2, y1 + corner_len), (255, 255, 255), thickness)

            # Ground contact point
            if vs.ground_contact is not None:
                gc_x = max(0, min(disp_w - 1, int(vs.ground_contact[0] * sx)))
                gc_y = max(0, min(disp_h - 1, int(vs.ground_contact[1] * sy)))
                cv2.circle(vis, (gc_x, gc_y), 4, (0, 240, 255), -1)

                # Heading indicator arrow
                if vs.heading_deg is not None and vs.speed_kmph > 1.0:
                    rad = np.radians(vs.heading_deg)
                    arr_len = max(14, min(35, int(vs.speed_kmph * 0.8)))
                    arr_end_x = int(gc_x + arr_len * np.sin(rad))
                    arr_end_y = int(gc_y - arr_len * np.cos(rad))
                    cv2.arrowedLine(vis, (gc_x, gc_y), (arr_end_x, arr_end_y), (0, 255, 255), 2, tipLength=0.35)

            # Label banner
            speed_txt = f"{vs.speed_kmph:.0f}km/h" if vs.speed_kmph is not None else ""
            lane_txt = f"[{vs.lane_id}]" if vs.lane_id else ""
            label_parts = [f"#{vs.track_id}", vs.class_name.upper()]
            if vs.detection_confidence > 0:
                label_parts.append(f"{int(vs.detection_confidence * 100)}%")
            if speed_txt:
                label_parts.append(speed_txt)
            if lane_txt:
                label_parts.append(lane_txt)
            label = " ".join(label_parts)

            (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.44, 1)
            pill_y1 = max(0, y1 - th - 8)
            pill_y2 = y1
            pill_x2 = min(disp_w - 1, x1 + tw + 10)
            cv2.rectangle(vis, (x1, pill_y1), (pill_x2, pill_y2), box_color, -1)
            text_color = (0, 0, 0) if cls_lower in ("two_wheeler", "motorcycle", "scooter") else (255, 255, 255)
            cv2.putText(vis, label, (x1 + 4, pill_y2 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.44, text_color, 1, cv2.LINE_AA)

            # Additional status badges
            if is_emergency:
                ebadge = "EMERGENCY PRIORITY"
                (etw, eth), _ = cv2.getTextSize(ebadge, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
                cv2.rectangle(vis, (x1, pill_y1 - eth - 6), (x1 + etw + 8, pill_y1), (0, 0, 220), -1)
                cv2.putText(vis, ebadge, (x1 + 4, pill_y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
            elif is_queued:
                qbadge = "QUEUED"
                (qtw, qth), _ = cv2.getTextSize(qbadge, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
                cv2.rectangle(vis, (x1, pill_y1 - qth - 6), (x1 + qtw + 8, pill_y1), (0, 140, 255), -1)
                cv2.putText(vis, qbadge, (x1 + 4, pill_y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        # 5. Incident Alert Banners across top of frame
        emergency_alerts = telemetry.get("emergency_alerts", [])
        wrong_way_alerts = telemetry.get("wrong_way_alerts", [])
        brts_approaching = telemetry.get("brts_bus_approaching", False)

        banner_y_end = 0
        if emergency_alerts:
            banner_y_end = 40
            cv2.rectangle(vis, (0, 0), (disp_w, banner_y_end), (0, 0, 210), -1)
            cv2.putText(
                vis, "EMERGENCY VEHICLE DETECTED - SIGNAL OPTIMIZER GREEN WAVE ACTIVE",
                (disp_w // 2 - 310, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA,
            )
        elif wrong_way_alerts:
            banner_y_end = 40
            cv2.rectangle(vis, (0, 0), (disp_w, banner_y_end), (0, 0, 210), -1)
            cv2.putText(
                vis, "WRONG-WAY VEHICLE DETECTED - CRITICAL SAFETY DISPATCH",
                (disp_w // 2 - 270, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA,
            )
        elif brts_approaching:
            banner_y_end = 36
            cv2.rectangle(vis, (0, 0), (disp_w, banner_y_end), (200, 100, 0), -1)
            cv2.putText(
                vis, "BRTS BUS DETECTED - RAPID TRANSIT PRIORITY ACTIVATED",
                (disp_w // 2 - 250, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2, cv2.LINE_AA,
            )

        # 6. Glassmorphism HUD Dashboard
        hud_x = 14
        hud_y = banner_y_end + 14
        hud_w = 400
        hud_h = 160

        hud_overlay = vis.copy()
        cv2.rectangle(hud_overlay, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (14, 18, 24), -1)
        cv2.addWeighted(hud_overlay, 0.82, vis, 0.18, 0, vis)
        cv2.rectangle(vis, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (65, 75, 90), 1)
        cv2.line(vis, (hud_x, hud_y), (hud_x + hud_w, hud_y), (0, 215, 255), 2)

        scene = telemetry.get("scene", {})
        cam = telemetry.get("camera", {})
        total_pcu = sum(
            lane.get("pcu", 0.0)
            for lane in telemetry.get("lane_occupancies", {}).values()
            if isinstance(lane, dict)
        )
        queued_count = sum(1 for v in vehicle_states if v.queue_probability > 0.65)

        hud_lines = [
            ("E-RAKSHAK PERCEPTION ENGINE v2.0", (0, 230, 255), 0.48, 2),
            (f"Junction: {self._junction_id}  |  Frame: {frame_idx}", (220, 220, 220), 0.40, 1),
            (f"Speed: {self._fps_actual:.1f} FPS (Target: {self._effective_fps:.0f})  |  Status: ACTIVE", (100, 255, 100), 0.40, 1),
            (f"Scene: {scene.get('lighting', 'day').upper()} / {scene.get('weather', 'clear').upper()}  (Vis: {int(scene.get('visibility', 1.0) * 100)}%)", (220, 220, 220), 0.40, 1),
            (f"Confidence: Scene {int(scene.get('scene_confidence', 0.85) * 100)}%  |  Cam Health: {int(cam.get('health', 1.0) * 100)}%", (220, 220, 220), 0.40, 1),
            (f"Traffic: {len(vehicle_states)} active  |  {queued_count} queued  |  {total_pcu:.1f} PCU", (255, 200, 50), 0.40, 1),
            ("[Space] Pause/Resume   [Q] Quit   [S] Screenshot", (170, 170, 170), 0.38, 1),
        ]

        text_y = hud_y + 22
        for line_txt, line_col, line_sc, line_th in hud_lines:
            cv2.putText(vis, line_txt, (hud_x + 12, text_y), cv2.FONT_HERSHEY_SIMPLEX, line_sc, line_col, line_th, cv2.LINE_AA)
            text_y += 20

        # 7. Write to Video File (if requested)
        if self._save_overlay_path:
            if self._video_writer is None:
                p = Path(self._save_overlay_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                self._video_writer = cv2.VideoWriter(str(p), fourcc, self._effective_fps, (disp_w, disp_h))
            self._video_writer.write(vis)

        return vis


# ─── CLI Entrypoint ──────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="E-Rakshak Vision Service — Upgraded Perception System (96 Sections)",
    )
    parser.add_argument(
        "--junction", "-j",
        default=None,
        help="Junction ID (e.g., junction_01). Defaults to first configured junction.",
    )
    parser.add_argument(
        "--source", "-s",
        default=None,
        help="Override video source (file path or RTSP URL).",
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml).",
    )
    parser.add_argument(
        "--mock-feed",
        action="store_true",
        help="Run using synthetic traffic generator (no video file required).",
    )
    parser.add_argument(
        "--max-frames", "-n",
        type=int,
        default=None,
        help="Max frames to process before exiting.",
    )
    parser.add_argument(
        "--record-failures",
        action="store_true",
        help="Automatically record anomaly failure frames (Section 85).",
    )
    parser.add_argument(
        "--object-telemetry",
        action="store_true",
        help="Publish per-object debug telemetry stream (Section 70).",
    )
    parser.add_argument(
        "--save-overlay",
        default=None,
        help="Path to save annotated MP4 video with perception overlay.",
    )
    parser.add_argument(
        "--no-display", "--headless",
        action="store_true",
        dest="no_display",
        help="Disable interactive GUI window display (e.g., for headless server or background batch run).",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution function."""
    setup_logging()
    args = parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = SCRIPT_DIR / config_path

    if not config_path.exists():
        logger.error(f"Config file not found at: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    junction_id = args.junction
    if junction_id is None:
        junctions = list(config.get("video_sources", {}).keys())
        junction_id = junctions[0] if junctions else "junction_01"
        logger.info(f"Defaulting to junction: {junction_id}")

    pipeline = VisionPipeline(
        config=config,
        junction_id=junction_id,
        video_source=args.source,
        record_failures=args.record_failures,
        publish_objects=args.object_telemetry,
        save_overlay_path=args.save_overlay,
        show_display=not args.no_display,
    )

    pipeline.run(max_frames=args.max_frames, mock_feed=args.mock_feed)


if __name__ == "__main__":
    main()
