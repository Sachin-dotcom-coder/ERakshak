# Vision Service — ERH26_PS_08

**Computer-Vision Traffic Sensing Layer** for the E-Rakshak Hackathon 2026 project:
*Data-Driven Traffic Optimization & Adaptive Infrastructure Intelligence*.

This module handles real-time vehicle detection, tracking, per-lane queue estimation,
lane-discipline/BRTS-intrusion violations, and incident detection from junction
camera feeds. It publishes structured JSON events consumed by the signal-optimizer,
backend-api, and dashboard modules.

---

## Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Detector | **YOLO26** (Ultralytics, Jan 2026) | NMS-free, DFL-free, STAL for small/distant vehicles |
| Tracker | **BoT-SORT** | Appearance re-ID + occlusion recovery for dense Indian traffic |
| Auto-labeling | **SAM 3.1** (Meta, Mar 2026) | Text-prompted concept segmentation on raw footage |
| Calibration | **Homography** (cv2.findHomography) | Pixel → real-world meters for queue length, speed |
| Custom classes | car, bus, brts_bus, truck, two_wheeler, auto_rickshaw, cycle | Indian traffic, not stock COCO |

---

## Folder Structure

```
vision-service/
├── main.py                     # Entry point: reads video, runs full pipeline
├── detector.py                 # YOLO26 model loading + inference wrapper
├── tracker.py                  # BoT-SORT tracking wrapper + track history
├── calibration/
│   ├── homography.py           # Pixel ↔ real-world-meter transform
│   └── camera_config.yaml      # Per-camera reference points (FILL IN)
├── zones/
│   ├── zone_config.yaml        # Per-junction lane polygons + BRTS corridor (FILL IN)
│   └── zone_utils.py           # Point-in-polygon, lane occupancy, PCU counting
├── violations.py               # Lane-discipline + BRTS-intrusion detection
├── incidents.py                # Stall/breakdown detection
├── event_publisher.py          # JSON event contract builder + Mock/Kafka publisher
├── data_pipeline/
│   ├── auto_label.py           # SAM 3.1 text-prompted auto-labeling
│   ├── review_helpers.py       # Frame sampling + Roboflow export
│   └── finetune.py             # Fine-tune YOLO26 on corrected Surat labels
├── evaluation/
│   └── evaluate.py             # Precision/recall/mAP/count-MAE report
├── trackers/
│   └── botsort_custom.yaml     # Custom BoT-SORT config for dense traffic
├── models/                     # Fine-tuned weights land here
├── sample_videos/raw/          # Raw Surat CCTV footage (AVI)
├── config.yaml                 # All thresholds, paths, and config
├── requirements.txt
└── README.md                   # This file
```

---

## How to Run Each Stage

### 0. Setup

```bash
cd vision-service
pip install -r requirements.txt
```

### 1. Probe Video Files

Get codec, resolution, FPS, and duration for each video — fill these into `config.yaml`:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,duration \
  -of default=noprint_wrappers=1 \
  "sample_videos/raw/<video_file>.avi"
```

If a video's codec causes issues, convert it:

```bash
ffmpeg -i input.avi -c:v libx264 -preset slow -crf 18 -c:a copy output.mp4
```

### 2. Auto-Label (Data Pipeline — Phase 2)

Extract frames and run SAM 3.1 auto-labeling:

```bash
python -m data_pipeline.auto_label \
  --video_dir sample_videos/raw \
  --output_dir data_pipeline/labels_draft \
  --every_n 30 \
  --max_frames_per_video 200
```

> **Note:** If SAM 3.1 exceeds local VRAM, run this step on Colab/Kaggle.
> The script is portable — no hardcoded local paths.

### 3. Review & Correct Labels

Sample frames and export for Roboflow:

```bash
python -m data_pipeline.review_helpers \
  --draft_dir data_pipeline/labels_draft \
  --output_dir data_pipeline/review_export \
  --n_samples 400 \
  --spot_check
```

Then:
1. Upload `data_pipeline/review_export/` to [Roboflow](https://roboflow.com)
2. Review/correct annotations in the web editor
3. Export as "YOLOv5 PyTorch" format
4. Download to `data_pipeline/labels_corrected/`

### 4. Fine-Tune YOLO26

```bash
python -m data_pipeline.finetune \
  --data data_pipeline/labels_corrected \
  --base_model yolo26s.pt \
  --epochs 50 \
  --batch 8
```

Then update `config.yaml` → `model.weights` to point to the fine-tuned weights.

### 5. Fill in Calibration & Zones

1. Fill in `calibration/camera_config.yaml` with reference points per camera
2. Fill in `zones/zone_config.yaml` with lane polygons and BRTS corridor

### 6. Run the Pipeline

```bash
# Process first junction (default)
python main.py

# Process a specific junction
python main.py --junction junction_01

# Process a custom video/RTSP stream
python main.py --source "rtsp://camera_ip/stream"
```

Events are written to `output/events.jsonl` (mock mode) or Kafka (production mode).

### 7. Evaluate

```bash
python -m evaluation.evaluate \
  --weights models/surat_yolo26s_finetuned.pt \
  --test_dir models/dataset/test
```

Produces `evaluation/results_report.md` (for pitch deck) and `evaluation/results.json`.

---

## Implementation Status

| Module | Status | Notes |
|--------|--------|-------|
| `detector.py` | ✅ Working | Stock COCO model runs; fine-tuned model ready after Phase 2 |
| `tracker.py` | ✅ Working | BoT-SORT with custom config |
| `calibration/` | ⏳ Scaffolded | Needs reference points from user |
| `zones/` | ⏳ Scaffolded | Needs polygon coordinates from user |
| `violations.py` | ✅ Working | Logic complete; needs zones to test end-to-end |
| `incidents.py` | ✅ Working | Logic complete; needs calibration for real speed values |
| `event_publisher.py` | ✅ Working | Mock publisher functional; Kafka ready when backend is |
| `main.py` | ✅ Working | Full pipeline orchestrator with CLAHE preprocessing |
| `auto_label.py` | ⏳ Needs SAM 3.1 | Falls back to placeholders if SAM not installed |
| `review_helpers.py` | ✅ Working | Roboflow export ready |
| `finetune.py` | ✅ Working | Needs corrected labels to run |
| `evaluate.py` | ✅ Working | Needs fine-tuned model + test set |

---

## Event Contract (Section 7)

Published per junction per detection cycle:

```json
{
  "junction_id": "junction_01",
  "timestamp": "2026-07-08T10:15:32Z",
  "lighting_condition": "day",
  "lanes": [
    {
      "lane_id": "lane_1",
      "vehicle_count": 12,
      "pcu_weighted_count": 15.4,
      "queue_length_m": 46.2,
      "avg_speed_kmph": 4.1,
      "vehicle_types": {"car": 6, "two_wheeler": 3, "auto_rickshaw": 2, "bus": 1},
      "detection_confidence": 0.91
    }
  ],
  "brts_violation": false,
  "brts_bus_approaching": true,
  "lane_intrusion": null,
  "stall_alert": null
}
```

**Do not change this shape without team discussion.** B, C, and D are building against it.

---

## Known Limitations

- **Calibration**: Queue length and speed values require homography reference points
  that must be manually identified per camera. Until filled in, these fields default to 0.
- **BRTS bus detection**: Depends on visual distinguishability — needs confirmation from footage.
- **Night footage**: CLAHE preprocessing helps, but accuracy will degrade. The evaluation
  report will state this honestly.
- **SAM 3.1 local**: May require cloud GPU for auto-labeling step (8GB VRAM may be tight
  for SAM 3.1 + inference).
