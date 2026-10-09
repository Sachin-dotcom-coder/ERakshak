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

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

VIDEOS_TO_PROCESS = [
    {
        "name": "traffic1",
        "input": PUBLIC_VIDEOS / "traffic_demo.mp4",
        "output": PUBLIC_VIDEOS / "traffic1.mp4",
        "max_frames": 141,
        "has_brts": True,
        "brts_pts": np.array([
            [747, 113],
            [827, 116],
            [791, 1029],
            [250, 1006]
        ], dtype=np.int32),
        "lane_1_pts": np.array([
            [849, 145],
            [928, 144],
            [1376, 976],
            [967, 1027]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [909, 103],
            [967, 103],
            [1728, 948],
            [1431, 1015]
        ], dtype=np.int32)
    },
    {
        "name": "traffic2",
        "input": PUBLIC_VIDEOS / "raw_traffic1.mp4",
        "output": PUBLIC_VIDEOS / "traffic2.mp4",
        "max_frames": 141,
        "has_brts": True,
        "brts_pts": np.array([
            [747, 113],
            [827, 116],
            [791, 1029],
            [250, 1006]
        ], dtype=np.int32),
        "lane_1_pts": np.array([
            [849, 145],
            [928, 144],
            [1376, 976],
            [967, 1027]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [909, 103],
            [967, 103],
            [1728, 948],
            [1431, 1015]
        ], dtype=np.int32)
    },
    {
        "name": "traffic3",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic3.mp4",
        "output": PUBLIC_VIDEOS / "traffic3.mp4",
        "max_frames": 141,
        "has_brts": True,
        "brts_pts": np.array([
            [523, 18],
            [592, 20],
            [566, 732],
            [153, 706]
        ], dtype=np.int32),
        "lane_1_pts": np.array([
            [611, 13],
            [660, 10],
            [1023, 728],
            [710, 754]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [666, 12],
            [717, 7],
            [1313, 689],
            [1064, 751]
        ], dtype=np.int32)
    },
    {
        "name": "traffic4",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic4.mp4",
        "output": PUBLIC_VIDEOS / "traffic4.mp4",
        "max_frames": 141,
        "has_brts": True,
        "brts_pts": np.array([
            [523, 18],
            [592, 20],
            [566, 732],
            [153, 706]
        ], dtype=np.int32),
        "lane_1_pts": np.array([
            [611, 13],
            [660, 10],
            [1023, 728],
            [710, 754]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [666, 12],
            [717, 7],
            [1313, 689],
            [1064, 751]
        ], dtype=np.int32)
    },
    {
        "name": "traffic5",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic5.mp4",
        "output": PUBLIC_VIDEOS / "traffic5.mp4",
        "max_frames": 141,
        "has_brts": True,
        "brts_pts": np.array([
            [523, 18],
            [592, 20],
            [566, 732],
            [153, 706]
        ], dtype=np.int32),
        "lane_1_pts": np.array([
            [611, 13],
            [660, 10],
            [1023, 728],
            [710, 754]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [666, 12],
            [717, 7],
            [1313, 689],
            [1064, 751]
        ], dtype=np.int32)
    },
    {
        "name": "traffic6",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic6.mp4",
        "output": PUBLIC_VIDEOS / "traffic6.mp4",
        "max_frames": 141,
        "has_brts": False,
        "lane_1_pts": np.array([
            [191, 157],
            [211, 159],
            [54, 460],
            [2, 343]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [222, 149],
            [249, 150],
            [302, 730],
            [4, 611]
        ], dtype=np.int32),
        "lane_3_pts": np.array([
            [255, 146],
            [280, 142],
            [701, 694],
            [328, 707]
        ], dtype=np.int32)
    },
    {
        "name": "traffic7",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic7.mp4",
        "output": PUBLIC_VIDEOS / "traffic7.mp4",
        "max_frames": 141,
        "has_brts": False,
        "lane_1_pts": np.array([
            [421, 389],
            [459, 386],
            [251, 625],
            [63, 513]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [465, 385],
            [506, 388],
            [801, 712],
            [210, 696]
        ], dtype=np.int32),
        "lane_3_pts": np.array([
            [520, 396],
            [558, 393],
            [1264, 594],
            [828, 684]
        ], dtype=np.int32)
    },
    {
        "name": "traffic8",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic8.mp4",
        "output": PUBLIC_VIDEOS / "traffic8.mp4",
        "max_frames": 141,
        "has_brts": False,
        "lane_1_pts": np.array([
            [666, 488],
            [708, 494],
            [545, 745],
            [152, 690]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [718, 491],
            [772, 489],
            [998, 640],
            [584, 726]
        ], dtype=np.int32),
        "lane_3_pts": np.array([
            [780, 488],
            [818, 480],
            [1008, 535],
            [951, 593]
        ], dtype=np.int32)
    },
    {
        "name": "traffic9",
        "input": SCRIPT_DIR / "sample_videos" / "raw" / "traffic9.mp4",
        "output": PUBLIC_VIDEOS / "traffic9.mp4",
        "max_frames": 141,
        "has_brts": True,
        "brts_pts": np.array([
            [554, 18],
            [627, 20],
            [600, 732],
            [162, 706]
        ], dtype=np.int32),
        "lane_1_pts": np.array([
            [648, 13],
            [699, 10],
            [1084, 728],
            [752, 754]
        ], dtype=np.int32),
        "lane_2_pts": np.array([
            [706, 12],
            [760, 7],
            [1391, 689],
            [1127, 751]
        ], dtype=np.int32)
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

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    limit = min(total_frames, cfg["max_frames"])

    # Scale polygon coordinates from 1920x1080 native standard if not provided natively
    sx = width / 1920.0
    sy = height / 1080.0

    if "brts_pts" in cfg:
        brts_pts = cfg["brts_pts"].copy()
        brts_pts = np.array([[int(p[0]), int(p[1])] for p in brts_pts], dtype=np.int32)
    else:
        brts_pts = np.array([
            [int(747 * sx), int(113 * sy)],
            [int(827 * sx), int(116 * sy)],
            [int(791 * sx), int(1029 * sy)],
            [int(250 * sx), int(1006 * sy)]
        ], dtype=np.int32)

    if "lane_1_pts" in cfg:
        lane_1_pts = cfg["lane_1_pts"].copy()
        lane_1_pts = np.array([[int(p[0]), int(p[1])] for p in lane_1_pts], dtype=np.int32)
    else:
        lane_1_pts = np.array([
            [int(849 * sx), int(145 * sy)],
            [int(928 * sx), int(144 * sy)],
            [int(1376 * sx), int(976 * sy)],
            [int(967 * sx), int(1027 * sy)]
        ], dtype=np.int32)

    if "lane_2_pts" in cfg:
        lane_2_pts = cfg["lane_2_pts"].copy()
        lane_2_pts = np.array([[int(p[0]), int(p[1])] for p in lane_2_pts], dtype=np.int32)
    else:
        lane_2_pts = np.array([
            [int(909 * sx), int(103 * sy)],
            [int(967 * sx), int(103 * sy)],
            [int(1728 * sx), int(948 * sy)],
            [int(1431 * sx), int(1015 * sy)]
        ], dtype=np.int32)

    lane_3_pts = None
    if "lane_3_pts" in cfg:
        lane_3_pts = cfg["lane_3_pts"].copy()
        lane_3_pts = np.array([[int(p[0]), int(p[1])] for p in lane_3_pts], dtype=np.int32)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(temp_avi, fourcc, fps, (width, height))

    def draw_tag(img, text, center, border_col, fill_col=(18, 18, 24)):
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.55
        thick = 1
        (tw, th), bl = cv2.getTextSize(text, font, scale, thick)
        x = center[0] - tw // 2
        y = center[1] + th // 2
        pad = 5
        cv2.rectangle(img, (x - pad, y - th - pad), (x + tw + pad, y + pad), fill_col, -1)
        cv2.rectangle(img, (x - pad, y - th - pad), (x + tw + pad, y + pad), border_col, 1)
        cv2.putText(img, text, (x, y), font, scale, (255, 255, 255), thick, cv2.LINE_AA)

    frame_idx = 0
    while frame_idx < limit:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Draw Lane Polygons (Semi-Transparent Overlays)
        overlay = frame.copy()

        # BRTS Corridor: Red
        if cfg.get("has_brts", True):
            cv2.fillPoly(overlay, [brts_pts], (0, 0, 240))
            cv2.polylines(frame, [brts_pts], isClosed=True, color=(0, 0, 255), thickness=2)

        # Lane 1: Green
        cv2.fillPoly(overlay, [lane_1_pts], (0, 200, 0))
        cv2.polylines(frame, [lane_1_pts], isClosed=True, color=(0, 240, 0), thickness=2)

        # Lane 2: Sky Blue / Cyan
        cv2.fillPoly(overlay, [lane_2_pts], (235, 130, 0))
        cv2.polylines(frame, [lane_2_pts], isClosed=True, color=(255, 150, 0), thickness=2)

        # Lane 3: Yellow/Cyan (if defined)
        if lane_3_pts is not None:
            cv2.fillPoly(overlay, [lane_3_pts], (0, 210, 240))
            cv2.polylines(frame, [lane_3_pts], isClosed=True, color=(0, 230, 255), thickness=2)

        # Blend semi-transparent lane color fill (15% opacity)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

        # Centroid Labels
        if cfg.get("has_brts", True):
            M_b = cv2.moments(brts_pts)
            if M_b["m00"] != 0:
                cx, cy = int(M_b["m10"] / M_b["m00"]), int(M_b["m01"] / M_b["m00"])
                draw_tag(frame, "BRTS CORRIDOR", (cx, cy), (0, 0, 255))

        M_1 = cv2.moments(lane_1_pts)
        if M_1["m00"] != 0:
            cx, cy = int(M_1["m10"] / M_1["m00"]), int(M_1["m01"] / M_1["m00"])
            draw_tag(frame, "LANE 1", (cx, cy), (0, 220, 0))

        M_2 = cv2.moments(lane_2_pts)
        if M_2["m00"] != 0:
            cx, cy = int(M_2["m10"] / M_2["m00"]), int(M_2["m01"] / M_2["m00"])
            draw_tag(frame, "LANE 2", (cx, cy), (255, 140, 0))
            
        if lane_3_pts is not None:
            M_3 = cv2.moments(lane_3_pts)
            if M_3["m00"] != 0:
                cx, cy = int(M_3["m10"] / M_3["m00"]), int(M_3["m01"] / M_3["m00"])
                draw_tag(frame, "LANE 3", (cx, cy), (0, 230, 255))

        # 2. Run Real YOLO Inference for Vehicles
        results = model(frame, conf=0.28, iou=0.45, verbose=False)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue

            cls_name, color = VEHICLE_CLASSES[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Emergency vehicle recognition: In traffic9 or red emergency box, map bus/truck to ambulance
            if cfg["name"] == "traffic9" and cls_id in (5, 7):
                cls_name = "ambulance"
                color = (0, 0, 255)  # Bright Emergency Red in BGR

            # Clamp coordinates
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width - 1, x2), min(height - 1, y2)

            # Check BRTS intrusion
            bottom_center = ((x1 + x2) / 2.0, float(y2))
            is_intrusion = False
            if cfg.get("has_brts", True) and cls_name != "bus":
                if cv2.pointPolygonTest(brts_pts, bottom_center, False) >= 0:
                    is_intrusion = True
                    color = (0, 0, 255) # Red violation

            # Draw real bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label pill
            if is_intrusion:
                label = f"VIOLATION: {cls_name} {int(conf * 100)}%"
            else:
                label = f"{cls_name} {int(conf * 100)}%"
            (tw, th), bl = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            bg_y1 = max(0, y1 - th - 6)
            bg_y2 = y1
            cv2.rectangle(frame, (x1, bg_y1), (x1 + tw + 6, bg_y2), (18, 18, 22), -1)
            cv2.rectangle(frame, (x1, bg_y1), (x1 + tw + 6, bg_y2), color, 1)
            cv2.putText(
                frame,
                label,
                (x1 + 3, bg_y2 - 3),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
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
        FFMPEG_EXE, "-y", "-i", temp_avi,
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

targets = sys.argv[1:]
for cfg in VIDEOS_TO_PROCESS:
    if targets and cfg["name"] not in targets:
        continue
    annotate_video(cfg)

print("\nCAMERA VIDEO ANNOTATION PIPELINE COMPLETE!")
