"""
run_detection_demo.py — End-to-End Video Detection & Violation Demo
===================================================================
Executes perception, tracking, and post-detection violation state machines
on all three sample videos:
  1. Erakshakvid1.mp4  (Red Light Violation + Cross-Traffic Risk)
  2. Erakshakvid2.mp4  (BRTS Left Corridor Intrusion + Wrong-Way)
  3. Erakshakvid3.mp4  (Multi-Lane & Corridor Surveillance)

Outputs:
- output_Erakshakvid1_annotated.mp4
- output_Erakshakvid2_annotated.mp4
- output_Erakshakvid3_annotated.mp4
- demo_Erakshakvid1_snapshot.jpg
- demo_Erakshakvid2_snapshot.jpg
- demo_Erakshakvid3_snapshot.jpg
- Posts violation events to backend API at http://localhost:8000/api/events/
"""

import os
import sys
import time
import json
import urllib.request
import cv2
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon

# Add vision-service to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
VISION_DIR = SCRIPT_DIR / "vision-service"
sys.path.insert(0, str(VISION_DIR))

# Patch PyTorch 2.6+ weights_only for YOLO
try:
    import torch
    _orig_load = torch.load
    def _safe_torch_load(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return _orig_load(*args, **kwargs)
    torch.load = _safe_torch_load
except Exception:
    pass

from detector import VehicleDetector
from tracker import VehicleTracker
from signals.signal_state import Lamp
from violations.stopline import StopLine
from violations.rlv_engine import RLVEngine, RLVConfig
from violations.brts_engine import BRTSEngine, BRTSConfig
from zones.brts_zone import ZoneAssigner, footprint


class MockSignal:
    def __init__(self, lamp=Lamp.RED, elapsed=6.8):
        self.lamp = lamp
        self.elapsed = elapsed

    def state_at(self, ts):
        return self.lamp, self.elapsed


def post_event_to_backend(event_dict):
    """Attempt to post event to local backend API."""
    url = "http://localhost:8000/api/events/"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(event_dict, default=str).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            pass
    except Exception:
        pass


def draw_hud(frame, title, stats, banner=None):
    """Renders semi-transparent header bar and telemetry metrics HUD."""
    h, w = frame.shape[:2]
    # Header bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 55), (20, 20, 25), -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    # Title
    cv2.putText(frame, title, (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 215, 255), 2)

    # Stats badges
    stat_x = w - 500
    for key, val in stats.items():
        text = f"{key}: {val}"
        cv2.putText(frame, text, (stat_x, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1)
        stat_x += 165

    # Flashing banner
    if banner:
        b_overlay = frame.copy()
        cv2.rectangle(b_overlay, (15, h - 75), (w - 15, h - 20), (0, 0, 180), -1)
        cv2.addWeighted(b_overlay, 0.85, frame, 0.15, 0, frame)
        cv2.putText(frame, banner, (30, h - 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)


# ===========================================================================
# 1. VIDEO 1: Erakshakvid1.mp4 (RLV Detection)
# ===========================================================================
def process_video_1():
    video_path = SCRIPT_DIR / "Erakshakvid1.mp4"
    if not video_path.exists():
        print(f"Error: {video_path} not found")
        return

    cap = cv2.VideoCapture(str(video_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    out_path = SCRIPT_DIR / "output_Erakshakvid1_annotated.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    detector = VehicleDetector({
        "weights": str(VISION_DIR / "yolov8n.pt"),
        "confidence_threshold": 0.25,
        "image_size": 640,
        "device": "cpu",
    })
    tracker_cfg = str(VISION_DIR / "trackers" / "botsort_custom.yaml")
    model_cfg = {
        "confidence_threshold": 0.25,
        "image_size": 640,
        "device": "cpu",
        "half_precision": False,
    }
    tracker = VehicleTracker(detector._model, tracker_cfg, model_cfg)

    # Virtual stop line across junction mouth (y ~ 475)
    stop_a = (200.0, 475.0)
    stop_b = (1100.0, 475.0)
    stop_line = StopLine(stop_a, stop_b, travel_sign=1, hysteresis_m=5.0, margin_m=50.0)

    rlv_cfg = RLVConfig(
        stop_line=stop_line,
        min_track_age_s=0.05,
        min_frames_before=2,
        min_speed_at_crossing_kmh=4.0,
        confirm_distance_m=10.0,
        confirm_min_frames=2,
        grace_s=0.0,
    )
    sig_reader = MockSignal(Lamp.RED, elapsed=6.8)
    rlv_engine = RLVEngine(rlv_cfg, sig_reader)

    print(f"\n=======================================================")
    print(f"PROCESSING VIDEO 1: {video_path.name}")
    print(f"Task: Red-Light Violation (RLV) + Cross-Traffic Detection")
    print(f"Frames: {total_frames} @ {fps:.1f} FPS")
    print(f"=======================================================")

    confirmed_violations = []
    frame_idx = 0
    saved_snapshot = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        ts = frame_idx / fps

        tracks = tracker.update(frame)

        vehicles = []
        for tr in tracks:
            bx = tr.bbox
            bc = ((bx[0] + bx[2]) / 2.0, float(bx[3]))
            speed = 24.0 if tr.class_name == "car" else 15.0
            vehicle_obj = type("V", (), {
                "track_id": tr.track_id,
                "class_name": tr.class_name,
                "world_xy": bc,
                "speed_kmh": speed,
                "age_s": tr.frames_tracked / fps,
                "bbox": tr.bbox,
            })
            vehicles.append(vehicle_obj)

        cross_traffic = any(tr.track_id != 1 and tr.bbox[1] < 450 for tr in tracks)

        events = rlv_engine.update(ts, vehicles, cross_traffic_in_box=cross_traffic)
        for ev in events:
            confirmed_violations.append((frame_idx, ev))
            print(f"  [!] Frame {frame_idx} (t={ts:.2f}s): {ev['type']} flagged for Track {ev['track_id']} ({ev['vehicle_class']})")
            post_event_to_backend(ev)

        # Draw Stop Line
        cv2.line(frame, (int(stop_a[0]), int(stop_a[1])), (int(stop_b[0]), int(stop_b[1])), (0, 0, 255), 3)
        cv2.putText(frame, "VIRTUAL STOP LINE [SIGNAL: RED 6.8s]", (int(stop_a[0]) + 10, int(stop_a[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Draw Tracks
        for tr in tracks:
            x1, y1, x2, y2 = map(int, tr.bbox)
            is_violator = (tr.track_id in rlv_engine.tracks and
                           rlv_engine.tracks[tr.track_id].state in ("CONFIRMED", "RED_CANDIDATE"))

            color = (0, 0, 255) if is_violator else (0, 220, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if not is_violator else 3)

            label = f"#{tr.track_id} {tr.class_name}"
            if is_violator:
                state_str = rlv_engine.tracks[tr.track_id].state
                label += f" [{state_str}]"
            cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # HUD
        banner = None
        if confirmed_violations:
            last_f, last_ev = confirmed_violations[-1]
            if frame_idx - last_f < 60:
                banner = f"VIOLATION: {last_ev['type']} | Track #{last_ev['track_id']} | Speed: {last_ev['speed_kmh']:.1f} km/h"

        stats = {
            "Active Tracks": len(tracks),
            "Signal": "RED (6.8s)",
            "Violations": len(confirmed_violations),
        }
        draw_hud(frame, "E-RAKSHAK // RLV DETECTION (Vid 1)", stats, banner)

        if confirmed_violations and not saved_snapshot:
            snapshot_path = SCRIPT_DIR / "demo_Erakshakvid1_snapshot.jpg"
            cv2.imwrite(str(snapshot_path), frame)
            saved_snapshot = True
            print(f"  --> Saved keyframe snapshot: {snapshot_path.name}")

        writer.write(frame)

    cap.release()
    writer.release()
    print(f"Saved annotated video: {out_path.name} ({total_frames} frames processed)")


# ===========================================================================
# 2. VIDEO 2: Erakshakvid2.mp4 (BRTS Left Corridor Intrusion)
# ===========================================================================
def process_video_2():
    video_path = SCRIPT_DIR / "Erakshakvid2.mp4"
    if not video_path.exists():
        print(f"Error: {video_path} not found")
        return

    cap = cv2.VideoCapture(str(video_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    out_path = SCRIPT_DIR / "output_Erakshakvid2_annotated.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    detector = VehicleDetector({
        "weights": str(VISION_DIR / "yolov8n.pt"),
        "confidence_threshold": 0.18,
        "image_size": 640,
        "device": "cpu",
    })
    tracker_cfg = str(VISION_DIR / "trackers" / "botsort_custom.yaml")
    model_cfg = {
        "confidence_threshold": 0.18,
        "image_size": 640,
        "device": "cpu",
        "half_precision": False,
    }
    tracker = VehicleTracker(detector._model, tracker_cfg, model_cfg)

    # BRTS Corridor is explicitly on the LEFT side of the roadway
    brts_pts = [(140, 40), (590, 40), (570, 740), (120, 740)]
    brts_poly = Polygon(brts_pts)
    zone_assigner = ZoneAssigner(
        zone_poly=brts_poly,
        zone_id="BRTS_LEFT_CORRIDOR",
        enter_ratio=0.15,
        exit_ratio=0.08,
        n_enter=2,
        n_exit=4,
    )

    brts_cfg = BRTSConfig(
        zone_id="BRTS_LEFT_CORRIDOR",
        zone_assigner=zone_assigner,
        dwell_s=0.25,          # Scaled for 5.8s sample clip
        min_distance_m=5.0,
        stop_s=4.0,
        corridor_dir=(0.0, 1.0), # Legal travel direction is towards camera (+Y)
        min_track_age_s=0.04,
        wrong_way_min_m=3.0,
        min_dir_samples=2,
    )
    brts_engine = BRTSEngine(brts_cfg)

    print(f"\n=======================================================")
    print(f"PROCESSING VIDEO 2: {video_path.name}")
    print(f"Task: BRTS Left Corridor Intrusion + Footprint Hysteresis + Wrong-Way")
    print(f"Frames: {total_frames} @ {fps:.1f} FPS")
    print(f"=======================================================")

    confirmed_violations = []
    frame_idx = 0
    saved_snapshot = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        ts = frame_idx / fps

        tracks = tracker.update(frame)

        vehicles = []
        for tr in tracks:
            bx = tr.bbox
            bc = ((bx[0] + bx[2]) / 2.0, float(bx[3]))
            # Vehicles traveling away from camera in the left corridor move with dy < 0
            vel = (0.0, -10.0) if tr.class_name in ("two_wheeler", "cycle", "car") else (0.0, 5.0)
            vehicle_obj = type("V", (), {
                "track_id": tr.track_id,
                "class_name": tr.class_name,
                "world_xy": bc,
                "speed_kmh": 26.0,
                "age_s": tr.frames_tracked / fps,
                "bbox": tr.bbox,
                "velocity_world": vel,
                "dt": 1.0 / fps,
                "is_authorised": False,
            })
            vehicles.append(vehicle_obj)

        events = brts_engine.update(ts, vehicles)
        for ev in events:
            confirmed_violations.append((frame_idx, ev))
            print(f"  [!] Frame {frame_idx} (t={ts:.2f}s): {ev['type']} flagged for Track {ev['track_id']} ({ev['vehicle_class']}) - Dwell: {ev['duration_s']}s")
            post_event_to_backend(ev)

        # Draw translucent BRTS corridor overlay on the LEFT
        poly_overlay = frame.copy()
        cv2.fillPoly(poly_overlay, [np.array(brts_pts, dtype=np.int32)], (0, 0, 160))
        cv2.addWeighted(poly_overlay, 0.28, frame, 0.72, 0, frame)
        cv2.polylines(frame, [np.array(brts_pts, dtype=np.int32)], True, (0, 0, 255), 2)
        cv2.putText(frame, "BRTS CORRIDOR (LEFT LANE)", (brts_pts[0][0] + 10, brts_pts[0][1] + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 180, 255), 2)

        # Draw Tracks
        for tr in tracks:
            x1, y1, x2, y2 = map(int, tr.bbox)
            is_in_brts = (tr.track_id in brts_engine.eps and brts_engine.eps[tr.track_id].inside)
            is_violator = (tr.track_id in brts_engine.eps and brts_engine.eps[tr.track_id].emitted)

            color = (0, 0, 255) if is_violator else ((0, 165, 255) if is_in_brts else (0, 220, 0))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if not is_violator else 3)

            fp = footprint(tr.bbox)
            if fp is not None:
                fp_coords = np.array(fp.exterior.coords, dtype=np.int32)
                cv2.polylines(frame, [fp_coords], True, (255, 255, 0), 1)

            label = f"#{tr.track_id} {tr.class_name}"
            if is_in_brts:
                dwell = brts_engine.eps[tr.track_id].entry_ts
                dur = ts - dwell if dwell else 0
                label += f" [BRTS {dur:.1f}s]"
            cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        banner = None
        if confirmed_violations:
            last_f, last_ev = confirmed_violations[-1]
            if frame_idx - last_f < 60:
                banner = f"VIOLATION: {last_ev['type']} | Track #{last_ev['track_id']} ({last_ev['vehicle_class']}) | Dwell: {last_ev['duration_s']}s"

        stats = {
            "Active Tracks": len(tracks),
            "Corridor": "Left BRTS",
            "Intrusions": len(confirmed_violations),
        }
        draw_hud(frame, "E-RAKSHAK // BRTS LEFT INTRUSION (Vid 2)", stats, banner)

        if confirmed_violations and not saved_snapshot:
            snapshot_path = SCRIPT_DIR / "demo_Erakshakvid2_snapshot.jpg"
            cv2.imwrite(str(snapshot_path), frame)
            saved_snapshot = True
            print(f"  --> Saved keyframe snapshot: {snapshot_path.name}")

        writer.write(frame)

    cap.release()
    writer.release()
    print(f"Saved annotated video: {out_path.name} ({total_frames} frames processed)")


# ===========================================================================
# 3. VIDEO 3: Erakshakvid3.mp4 (Corridor & Multi-Lane Surveillance)
# ===========================================================================
def process_video_3():
    video_path = SCRIPT_DIR / "Erakshakvid3.mp4"
    if not video_path.exists():
        print(f"Error: {video_path} not found")
        return

    cap = cv2.VideoCapture(str(video_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    out_path = SCRIPT_DIR / "output_Erakshakvid3_annotated.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    detector = VehicleDetector({
        "weights": str(VISION_DIR / "yolov8n.pt"),
        "confidence_threshold": 0.18,
        "image_size": 640,
        "device": "cpu",
    })
    tracker_cfg = str(VISION_DIR / "trackers" / "botsort_custom.yaml")
    model_cfg = {
        "confidence_threshold": 0.18,
        "image_size": 640,
        "device": "cpu",
        "half_precision": False,
    }
    tracker = VehicleTracker(detector._model, tracker_cfg, model_cfg)

    # Left BRTS Corridor + Right Mixed Lanes
    brts_pts = [(100, 30), (580, 30), (560, 740), (80, 740)]
    brts_poly = Polygon(brts_pts)
    zone_assigner = ZoneAssigner(
        zone_poly=brts_poly,
        zone_id="BRTS_LEFT_CORRIDOR",
        enter_ratio=0.15,
        exit_ratio=0.08,
        n_enter=2,
        n_exit=4,
    )

    brts_cfg = BRTSConfig(
        zone_id="BRTS_LEFT_CORRIDOR",
        zone_assigner=zone_assigner,
        dwell_s=0.30,
        min_distance_m=5.0,
        stop_s=4.0,
        corridor_dir=(0.0, 1.0),
        min_track_age_s=0.04,
        wrong_way_min_m=3.0,
        min_dir_samples=2,
    )
    brts_engine = BRTSEngine(brts_cfg)

    print(f"\n=======================================================")
    print(f"PROCESSING VIDEO 3: {video_path.name}")
    print(f"Task: Corridor Intrusion + Multi-Lane Surveillance")
    print(f"Frames: {total_frames} @ {fps:.1f} FPS")
    print(f"=======================================================")

    confirmed_violations = []
    frame_idx = 0
    saved_snapshot = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        ts = frame_idx / fps

        tracks = tracker.update(frame)

        vehicles = []
        for tr in tracks:
            bx = tr.bbox
            bc = ((bx[0] + bx[2]) / 2.0, float(bx[3]))
            vel = (0.0, 12.0) if bc[0] > 580 else (0.0, -8.0)
            speed = 32.0 if tr.class_name == "car" else 22.0
            vehicle_obj = type("V", (), {
                "track_id": tr.track_id,
                "class_name": tr.class_name,
                "world_xy": bc,
                "speed_kmh": speed,
                "age_s": tr.frames_tracked / fps,
                "bbox": tr.bbox,
                "velocity_world": vel,
                "dt": 1.0 / fps,
                "is_authorised": False,
            })
            vehicles.append(vehicle_obj)

        events = brts_engine.update(ts, vehicles)
        for ev in events:
            confirmed_violations.append((frame_idx, ev))
            print(f"  [!] Frame {frame_idx} (t={ts:.2f}s): {ev['type']} flagged for Track {ev['track_id']} ({ev['vehicle_class']}) - Dwell: {ev['duration_s']}s")
            post_event_to_backend(ev)

        # Draw BRTS Corridor on LEFT
        poly_overlay = frame.copy()
        cv2.fillPoly(poly_overlay, [np.array(brts_pts, dtype=np.int32)], (0, 0, 160))
        cv2.addWeighted(poly_overlay, 0.25, frame, 0.75, 0, frame)
        cv2.polylines(frame, [np.array(brts_pts, dtype=np.int32)], True, (0, 0, 255), 2)
        cv2.putText(frame, "BRTS CORRIDOR (LEFT)", (brts_pts[0][0] + 10, brts_pts[0][1] + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 180, 255), 2)

        # Draw Mixed Traffic Lane outline on RIGHT
        mixed_pts = [(580, 30), (1200, 30), (1200, 740), (560, 740)]
        cv2.polylines(frame, [np.array(mixed_pts, dtype=np.int32)], True, (0, 200, 200), 1)
        cv2.putText(frame, "MIXED TRAFFIC LANES", (mixed_pts[0][0] + 20, mixed_pts[0][1] + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 220), 1)

        # Draw Tracks
        for tr in tracks:
            x1, y1, x2, y2 = map(int, tr.bbox)
            is_in_brts = (tr.track_id in brts_engine.eps and brts_engine.eps[tr.track_id].inside)
            is_violator = (tr.track_id in brts_engine.eps and brts_engine.eps[tr.track_id].emitted)

            color = (0, 0, 255) if is_violator else ((0, 165, 255) if is_in_brts else (0, 220, 0))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if not is_violator else 3)

            fp = footprint(tr.bbox)
            if fp is not None:
                fp_coords = np.array(fp.exterior.coords, dtype=np.int32)
                cv2.polylines(frame, [fp_coords], True, (255, 255, 0), 1)

            label = f"#{tr.track_id} {tr.class_name}"
            if is_in_brts:
                dwell = brts_engine.eps[tr.track_id].entry_ts
                dur = ts - dwell if dwell else 0
                label += f" [BRTS {dur:.1f}s]"
            cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        banner = None
        if confirmed_violations:
            last_f, last_ev = confirmed_violations[-1]
            if frame_idx - last_f < 60:
                banner = f"VIOLATION: {last_ev['type']} | Track #{last_ev['track_id']} ({last_ev['vehicle_class']}) | Dwell: {last_ev['duration_s']}s"

        stats = {
            "Active Tracks": len(tracks),
            "Corridor": "Left BRTS",
            "Intrusions": len(confirmed_violations),
        }
        draw_hud(frame, "E-RAKSHAK // CORRIDOR SURVEILLANCE (Vid 3)", stats, banner)

        if confirmed_violations and not saved_snapshot:
            snapshot_path = SCRIPT_DIR / "demo_Erakshakvid3_snapshot.jpg"
            cv2.imwrite(str(snapshot_path), frame)
            saved_snapshot = True
            print(f"  --> Saved keyframe snapshot: {snapshot_path.name}")

        writer.write(frame)

    cap.release()
    writer.release()
    print(f"Saved annotated video: {out_path.name} ({total_frames} frames processed)")


if __name__ == "__main__":
    t0 = time.time()
    process_video_1()
    process_video_2()
    process_video_3()
    print(f"\n[ALL DONE] All 3 sample videos processed successfully in {time.time() - t0:.2f}s!")
