import os
import sys
import subprocess
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

SCRIPT_DIR = Path(__file__).resolve().parent
PUBLIC_VIDEOS = SCRIPT_DIR.parent / "frontend" / "public" / "videos"
PUBLIC_VIDEOS.mkdir(parents=True, exist_ok=True)

MODEL_PATH = SCRIPT_DIR / "yolo26s.pt"
print(f"Loading YOLO model from {MODEL_PATH}...")
model = YOLO(str(MODEL_PATH))

# Vehicle class map in COCO: 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = {
    1: ("bicycle", (255, 180, 0)),
    2: ("car", (0, 240, 120)),
    3: ("motorcycle", (255, 120, 0)),
    5: ("bus", (50, 220, 255)),
    7: ("truck", (220, 80, 255)),
}

VIDEOS_TO_PROCESS = [
    {
        "name": "traffic1",
        "input": PUBLIC_VIDEOS / "traffic_demo.mp4",
        "output": PUBLIC_VIDEOS / "traffic1.mp4",
        "max_frames": 400,
    },
    {
        "name": "traffic3",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic3.mp4",
        "output": PUBLIC_VIDEOS / "traffic3.mp4",
        "max_frames": 141,
    },
    {
        "name": "traffic4",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic4.mp4",
        "output": PUBLIC_VIDEOS / "traffic4.mp4",
        "max_frames": 141,
    },
    {
        "name": "traffic5",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic5.mp4",
        "output": PUBLIC_VIDEOS / "traffic5.mp4",
        "max_frames": 141,
    },
]

def annotate_video(cfg):
    input_path = str(cfg["input"])
    output_path = str(cfg["output"])
    temp_avi = str(SCRIPT_DIR / f"temp_{cfg['name']}.avi")

    print(f"\nProcessing {cfg['name']} from {input_path}...")
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open {input_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    limit = min(total_frames, cfg["max_frames"])

    # Scale polygon coordinates from 1920x1080 native standard
    sx = width / 1920.0
    sy = height / 1080.0

    brts_pts = np.array([
        [int(747 * sx), int(113 * sy)],
        [int(827 * sx), int(116 * sy)],
        [int(791 * sx), int(1029 * sy)],
        [int(250 * sx), int(1006 * sy)]
    ], dtype=np.int32)

    lane_1_pts = np.array([
        [int(849 * sx), int(145 * sy)],
        [int(928 * sx), int(144 * sy)],
        [int(1376 * sx), int(976 * sy)],
        [int(967 * sx), int(1027 * sy)]
    ], dtype=np.int32)

    lane_2_pts = np.array([
        [int(909 * sx), int(103 * sy)],
        [int(967 * sx), int(103 * sy)],
        [int(1728 * sx), int(948 * sy)],
        [int(1431 * sx), int(1015 * sy)]
    ], dtype=np.int32)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(temp_avi, fourcc, fps, (width, height))

    frame_idx = 0
    while frame_idx < limit:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Draw Lane Polygons (Semi-Transparent Overlays)
        overlay = frame.copy()

        # BRTS Corridor: Red
        cv2.fillPoly(overlay, [brts_pts], (0, 0, 255))
        cv2.polylines(frame, [brts_pts], isClosed=True, color=(0, 0, 255), thickness=3)

        # Lane 1: Green
        cv2.fillPoly(overlay, [lane_1_pts], (0, 220, 0))
        cv2.polylines(frame, [lane_1_pts], isClosed=True, color=(0, 220, 0), thickness=2)

        # Lane 2: Sky Blue / Cyan
        cv2.fillPoly(overlay, [lane_2_pts], (255, 140, 0))
        cv2.polylines(frame, [lane_2_pts], isClosed=True, color=(255, 140, 0), thickness=2)

        # Blend semi-transparent lane color fill (15% opacity)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

        # Centroid Labels
        M_b = cv2.moments(brts_pts)
        if M_b["m00"] != 0:
            cx, cy = int(M_b["m10"] / M_b["m00"]), int(M_b["m01"] / M_b["m00"])
            cv2.putText(frame, "BRTS", (cx - int(25 * sx), cy), cv2.FONT_HERSHEY_SIMPLEX, 0.75 * sy, (255, 255, 255), 2, cv2.LINE_AA)

        M_1 = cv2.moments(lane_1_pts)
        if M_1["m00"] != 0:
            cx, cy = int(M_1["m10"] / M_1["m00"]), int(M_1["m01"] / M_1["m00"])
            cv2.putText(frame, "LANE 1", (cx - int(30 * sx), cy), cv2.FONT_HERSHEY_SIMPLEX, 0.65 * sy, (255, 255, 255), 2, cv2.LINE_AA)

        M_2 = cv2.moments(lane_2_pts)
        if M_2["m00"] != 0:
            cx, cy = int(M_2["m10"] / M_2["m00"]), int(M_2["m01"] / M_2["m00"])
            cv2.putText(frame, "LANE 2", (cx - int(30 * sx), cy), cv2.FONT_HERSHEY_SIMPLEX, 0.65 * sy, (255, 255, 255), 2, cv2.LINE_AA)

        # 2. Run Real YOLO Inference for Vehicles
        results = model(frame, conf=0.28, iou=0.45, verbose=False)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue

            cls_name, color = VEHICLE_CLASSES[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Clamp coordinates
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width - 1, x2), min(height - 1, y2)

            # Draw real bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label pill
            label = f"{cls_name} {int(conf * 100)}%"
            (tw, th), bl = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            bg_y1 = max(0, y1 - th - 6)
            bg_y2 = y1
            cv2.rectangle(frame, (x1, bg_y1), (x1 + tw + 6, bg_y2), (18, 18, 22), -1)
            cv2.rectangle(frame, (x1, bg_y1), (x1 + tw + 6, bg_y2), color, 1)
            cv2.putText(
                frame,
                label,
                (x1 + 3, bg_y2 - 3),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        out.write(frame)
        frame_idx += 1
        if frame_idx % 40 == 0:
            print(f"  Frame {frame_idx}/{limit} annotated...")

    cap.release()
    out.release()
    print(f"Finished YOLO + Lane polygon annotation of {frame_idx} frames. Transcoding with ffmpeg to {output_path}...")

    # Transcode to high-compatibility browser H.264
    cmd = [
        "ffmpeg", "-y", "-i", temp_avi,
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"SUCCESS: {cfg['name']} written to {output_path}")
    else:
        print(f"FFmpeg transcode error: {res.stderr.decode('utf-8', errors='ignore')}")

    if os.path.exists(temp_avi):
        os.remove(temp_avi)

for cfg in VIDEOS_TO_PROCESS:
    annotate_video(cfg)

print("\nALL CAMERA VIDEOS ANNOTATED WITH REAL YOLO DETECTIONS AND LANE BORDERS COMPLETE!")
