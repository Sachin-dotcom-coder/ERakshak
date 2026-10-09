import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from shapely.geometry import Point, Polygon

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
PUBLIC_VIDEOS = ROOT_DIR / "frontend" / "public" / "videos"
OUTPUT_JSON = ROOT_DIR / "frontend" / "public" / "data" / "video_detections.json"
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

MODEL_PATH = SCRIPT_DIR / "yolo26s.pt"
print(f"Loading YOLO model from {MODEL_PATH}...")
model = YOLO(str(MODEL_PATH))

# Vehicle class map in COCO
COCO_VEHICLES = {
    1: "two-wheeler",  # bicycle
    2: "car",
    3: "two-wheeler",  # motorcycle
    5: "bus",
    7: "truck",
}

# Polygons for each video
CONFIGS = {
    "traffic9.mp4": {
        "brts": Polygon([[554, 18], [627, 20], [600, 732], [162, 706]]),
        "lanes": {
            "Lane 1": Polygon([[648, 13], [699, 10], [1084, 728], [752, 754]]),
            "Lane 2": Polygon([[706, 12], [760, 7], [1391, 689], [1127, 751]]),
        }
    },
    "traffic1.mp4": {
        "brts": Polygon([[747, 113], [827, 116], [791, 1029], [250, 1006]]),
        "lanes": {
            "Lane 1": Polygon([[849, 145], [928, 144], [1376, 976], [967, 1027]]),
            "Lane 2": Polygon([[909, 103], [967, 103], [1728, 948], [1431, 1015]]),
        }
    },
    "traffic2.mp4": {
        "brts": Polygon([[382, 181], [602, 193], [459, 315], [118, 291]]),
        "lanes": {
            "Lane 1": Polygon([[689, 181], [797, 188], [618, 1044], [44, 1044]]),
            "Lane 2": Polygon([[802, 200], [915, 204], [1206, 1053], [656, 1054]]),
            "Lane 3": Polygon([[915, 205], [986, 205], [1667, 1037], [1253, 1068]]),
        }
    },
    "traffic6.mp4": {
        "brts": None,
        "lanes": {
            "Lane 1": Polygon([[191, 157], [211, 159], [54, 460], [2, 343]]),
            "Lane 2": Polygon([[222, 149], [249, 150], [302, 730], [4, 611]]),
            "Lane 3": Polygon([[255, 146], [280, 142], [701, 694], [328, 707]]),
        }
    },
    "traffic7.mp4": {
        "brts": None,
        "lanes": {
            "Lane 1": Polygon([[421, 389], [459, 386], [251, 625], [63, 513]]),
            "Lane 2": Polygon([[465, 385], [506, 388], [801, 712], [210, 696]]),
            "Lane 3": Polygon([[520, 396], [558, 393], [1264, 594], [828, 684]]),
        }
    },
    "traffic8.mp4": {
        "brts": None,
        "lanes": {
            "Lane 1": Polygon([[666, 488], [708, 494], [545, 745], [152, 690]]),
            "Lane 2": Polygon([[718, 491], [772, 489], [998, 640], [584, 726]]),
            "Lane 3": Polygon([[780, 488], [818, 480], [1008, 535], [951, 593]]),
        }
    },
}

all_video_detections = {}

video_files = list(PUBLIC_VIDEOS.glob("traffic*.mp4"))
print(f"Found {len(video_files)} videos in {PUBLIC_VIDEOS}...")

for vpath in video_files:
    fname = vpath.name
    print(f"\nExtracting detections for {fname}...")
    cap = cv2.VideoCapture(str(vpath))
    if not cap.isOpened():
        print(f"Could not open {vpath}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cfg = CONFIGS.get(fname, {
        "brts": None,
        "lanes": {
            "Lane 1": Polygon([[0, 0], [width, 0], [width, height], [0, height]])
        }
    })

    # Scale polygons if needed (CONFIGS are in 1920x1080 native except traffic9 which is 1536x768)
    native_w = 1536 if fname == "traffic9.mp4" else 1920
    native_h = 768 if fname == "traffic9.mp4" else 1080
    sx = width / float(native_w)
    sy = height / float(native_h)

    def scale_poly(p):
        if not p: return None
        coords = np.array(p.exterior.coords)
        scaled = coords * [sx, sy]
        return Polygon(scaled)

    brts_poly = scale_poly(cfg.get("brts"))
    lanes_polys = {lname: scale_poly(lp) for lname, lp in cfg.get("lanes", {}).items()}

    timeline = []
    frame_step = max(4, int(fps * 0.35)) # Sample every ~0.35 seconds
    frame_idx = 0

    while frame_idx < total_frames and frame_idx < 300:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret: break

        t_sec = round(frame_idx / fps, 2)
        results = model(frame, conf=0.25, iou=0.45, verbose=False)[0]

        frame_events = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in COCO_VEHICLES:
                continue

            obj_class = COCO_VEHICLES[cls_id]
            conf = int(float(box.conf[0]) * 100)
            x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
            bottom_center = Point((x1 + x2) / 2.0, y2)

            # Determine lane / zone (Strict: Lane 1, Lane 2, Lane 3, or BRTS Corridor — never Carriageway)
            assigned_lane = None
            is_brts = False

            if brts_poly and brts_poly.contains(bottom_center):
                assigned_lane = "BRTS Corridor"
                is_brts = True
            else:
                for lname, lp in lanes_polys.items():
                    if lp and lp.contains(bottom_center):
                        assigned_lane = lname
                        break

            # If outside polygons, snap to nearest designated road lane
            if not assigned_lane:
                best_d = float("inf")
                best_lane = "Lane 1"
                for lname, lp in lanes_polys.items():
                    if lp:
                        d = lp.distance(bottom_center)
                        if d < best_d:
                            best_d = d
                            best_lane = lname
                assigned_lane = best_lane

            # Determine event type
            if is_brts:
                if obj_class == "bus":
                    event_type = "vehicle_entry"
                    note = "Authorized BRTS Transit"
                else:
                    event_type = "brts_intrusion"
                    note = f"⚠️ Corridor Intrusion • {assigned_lane}"
            else:
                event_type = "vehicle_entry"
                note = f"{assigned_lane} • Active Flow"

            frame_events.append({
                "timeSec": t_sec,
                "frame": frame_idx,
                "event": event_type,
                "objectClass": obj_class,
                "confidence": conf,
                "lane": assigned_lane,
                "note": note,
            })

        if frame_events:
            timeline.append({
                "timeSec": t_sec,
                "events": frame_events
            })

        frame_idx += frame_step

    cap.release()
    all_video_detections[fname.replace(".mp4", "")] = timeline
    print(f"Captured {len(timeline)} time checkpoints for {fname}")

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_video_detections, f, indent=2)

print(f"\nAll detections saved to {OUTPUT_JSON} (size: {OUTPUT_JSON.stat().st_size} bytes)")
