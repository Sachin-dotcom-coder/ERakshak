# E-Rakshak Detection System --- Major Upgrade & Implementation Guide

## Purpose

This document is a practical implementation plan for significantly
improving the E-Rakshak Computer Vision Sensing Layer.

The current sensing architecture is:

``` text
CCTV / RTSP
    ↓
CLAHE preprocessing
    ↓
YOLO26 vehicle detector
    ↓
BoT-SORT + Re-ID
    ↓
Bottom-center point
    ↓
Homography
    ↓
Polygon-based lane assignment
    ↓
PCU / speed / queue estimation
    ↓
BRTS violation / incident detection
    ↓
Telemetry
    ↓
Signal optimizer
```

The existing design already includes seven Indian traffic classes,
BoT-SORT tracking with Re-ID, homography-based world coordinates,
polygon zones, PCU weighting, queue metrics, BRTS intrusion sensing,
stalled-vehicle detection, emergency-vehicle sensing, SAM-assisted
labeling, and a Kafka telemetry contract.

The goal of this upgrade is **not simply to replace YOLO with another
model**. The goal is to transform the perception layer from a mostly
frame-by-frame detector into a:

> **Temporal, multi-scale, geometry-aware, uncertainty-aware traffic
> perception system designed specifically for heterogeneous Indian
> traffic.**

------------------------------------------------------------------------

# 1. Target Architecture

The upgraded pipeline should be:

``` text
                         CCTV / RTSP
                              │
                              ▼
                  ┌──────────────────────┐
                  │ Camera Health Monitor│
                  └──────────┬───────────┘
                             │
                             ▼
                  Scene / Weather Classifier
                             │
                             ▼
                 Condition-Aware Preprocessing
                             │
                             ▼
                ┌──────────────────────────┐
                │ Multi-Scale Detection    │
                │                          │
                │ Full-frame detector      │
                │ + Far-queue tiled model  │
                └────────────┬─────────────┘
                             │
                             ▼
                    Detection Fusion
                             │
                             ▼
                Temporal Detection Filter
                             │
                             ▼
                    BoT-SORT + Re-ID
                             │
                             ▼
                  Occlusion State Machine
                             │
                             ▼
             ┌──────────────────────────────┐
             │ Vehicle State Estimator     │
             │                             │
             │ class                       │
             │ confidence                  │
             │ position                    │
             │ velocity                    │
             │ acceleration                │
             │ heading                     │
             │ trajectory                  │
             │ occlusion                   │
             └──────────────┬───────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
      Segmentation / OBB             Standard BBox
      difficult cases                normal cases
              │                           │
              └─────────────┬─────────────┘
                            ▼
                   Ground Contact Point
                            │
                            ▼
                       Homography
                            │
                            ▼
                  World Coordinates (m)
                            │
                            ▼
                 Dynamic Lane Assignment
                            │
                            ▼
                 Movement Classification
               /       |        |        \
              /        |        |         \
             ▼         ▼        ▼          ▼
          Queue     Speed     BRTS      Incidents
         Analysis   Analysis  Violations
             \        |        |         /
              \       |        |        /
               └──────┴────────┴───────┘
                            │
                            ▼
                   Confidence Fusion
                            │
                            ▼
                   Traffic Telemetry
                            │
                            ▼
                  Signal Optimizer
```

------------------------------------------------------------------------

# 2. Implementation Strategy

Do not implement everything at once.

Use five phases:

``` text
Phase 1 — Detection quality
Phase 2 — Tracking and temporal perception
Phase 3 — Geometry and traffic-state perception
Phase 4 — Uncertainty and incident intelligence
Phase 5 — Evaluation and continuous learning
```

Recommended order:

1.  Build a proper local dataset.
2.  Add hard-example mining.
3.  Implement tiled far-field detection.
4.  Improve temporal confirmation.
5.  Strengthen BoT-SORT state management.
6.  Replace static lane assignment with centerline/trajectory reasoning.
7.  Improve queue estimation.
8.  Add camera-health monitoring.
9.  Add uncertainty estimation.
10. Improve emergency/BRTS/incident detection.
11. Add segmentation/OBB only for difficult cases.
12. Build a complete perception benchmark.
13. Feed confidence and uncertainty into the signal optimizer.

------------------------------------------------------------------------

# 3. Project Structure

Refactor the current `vision-service` into something close to:

``` text
vision-service/
│
├── main.py
│
├── config/
│   ├── classes.yaml
│   ├── camera.yaml
│   ├── zones.yaml
│   ├── lanes.yaml
│   └── thresholds.yaml
│
├── models/
│   ├── detector.py
│   ├── tiled_detector.py
│   ├── detector_fusion.py
│   ├── segmentation_refiner.py
│   ├── obb_refiner.py
│   └── scene_classifier.py
│
├── tracking/
│   ├── tracker.py
│   ├── track_state.py
│   ├── occlusion.py
│   └── reid.py
│
├── calibration/
│   ├── homography.py
│   ├── calibration_validator.py
│   └── camera_shift.py
│
├── geometry/
│   ├── world_coordinates.py
│   ├── lane_assignment.py
│   ├── centerlines.py
│   └── maneuver.py
│
├── traffic_state/
│   ├── speed.py
│   ├── queue.py
│   ├── pcu.py
│   ├── density.py
│   └── shockwave.py
│
├── incidents/
│   ├── emergency.py
│   ├── breakdown.py
│   ├── brts.py
│   └── wrong_way.py
│
├── confidence/
│   ├── object_confidence.py
│   ├── scene_confidence.py
│   ├── uncertainty.py
│   └── calibration.py
│
├── camera/
│   ├── health.py
│   ├── visibility.py
│   └── quality.py
│
├── data_pipeline/
│   ├── extract_frames.py
│   ├── auto_label.py
│   ├── hard_negative_mining.py
│   ├── active_learning.py
│   ├── review_helpers.py
│   └── dataset_split.py
│
├── evaluation/
│   ├── detection_metrics.py
│   ├── tracking_metrics.py
│   ├── traffic_metrics.py
│   └── event_metrics.py
│
└── event_publisher.py
```

------------------------------------------------------------------------

# 4. Phase 1 --- Build a Strong Indian Traffic Dataset

## 4.1 Why this should be the first step

A better model cannot compensate for a weak dataset.

The current project uses SAM-assisted auto-labeling and a small
human-reviewed frame sample. That is useful for bootstrapping, but the
upgraded system needs a larger, deliberately constructed dataset.

The important idea is:

> Do not collect random images. Collect the situations where your
> current detector fails.

------------------------------------------------------------------------

# 5. Dataset Taxonomy

Create separate subsets.

``` text
dataset/
├── train/
├── val/
└── test/
```

Within the metadata, tag each frame:

``` text
weather:
    clear
    rain
    fog

lighting:
    day
    night
    dawn
    dusk

traffic_density:
    low
    medium
    high
    extreme

occlusion:
    low
    medium
    high

camera_quality:
    clear
    blurred
    vibrating
    partially_blocked
```

Also record:

``` text
junction_id
camera_id
time_of_day
vehicle_classes_present
```

------------------------------------------------------------------------

# 6. Data Collection Priorities

Prioritize:

  Scenario                    Priority
  ------------------------ -----------
  Heavy congestion           Very High
  Small distant vehicles     Very High
  Two-wheeler crowds         Very High
  Auto-rickshaw crowds       Very High
  Vehicle occlusion          Very High
  Monsoon                    Very High
  Night                      Very High
  BRTS corridor              Very High
  Emergency vehicles         Very High
  Wrong-way movement              High
  Camera vibration                High
  Headlight glare                 High
  Normal daylight                 High
  Fog                           Medium

The dataset should intentionally contain difficult examples.

------------------------------------------------------------------------

# 7. Avoid Video-Leakage in Dataset Splitting

Do NOT randomly split adjacent video frames.

Bad:

``` text
video.mp4

frames 1–800 → train
frames 801–900 → validation
```

This can produce highly similar frames in both sets.

Instead:

``` text
Camera A, Monday → train
Camera A, Tuesday → train

Camera B → validation

Camera C → test
```

Even better:

``` text
different junctions/cameras → different splits
```

This tests whether the model generalizes to unseen scenes.

------------------------------------------------------------------------

# 8. Annotation Requirements

For each vehicle annotate:

``` text
class
bounding box
occlusion level
truncation level
```

For advanced versions:

``` text
instance mask
vehicle orientation
```

For traffic analytics annotate:

``` text
lane/movement
queue membership
BRTS lane membership
emergency status
```

Do not necessarily annotate every advanced label from day one. Start
with bounding boxes and classes, then add specialized labels.

------------------------------------------------------------------------

# 9. Hard-Negative Mining

Create an automatic process:

``` text
Video
  ↓
Current detector
  ↓
Collect suspicious detections
  ↓
Human review
  ↓
Add mistakes to dataset
  ↓
Retrain
```

Suspicious frames include:

``` text
confidence < 0.50
```

or:

``` text
class changes repeatedly
```

or:

``` text
track repeatedly lost
```

or:

``` text
two detectors disagree
```

or:

``` text
large queue but unusually low detected count
```

Example:

``` python
if detection.confidence < 0.5:
    save_frame(frame, "hard_cases/low_confidence")

if track.class_changed_recently:
    save_frame(frame, "hard_cases/class_instability")

if track.id_switch_suspected:
    save_frame(frame, "hard_cases/tracking")
```

The exact thresholds should be configurable.

------------------------------------------------------------------------

# 10. Active Learning

Instead of asking a human to label random frames, calculate:

``` text
uncertainty_score
```

For example:

``` text
uncertainty =
    0.30 * low_detection_confidence
  + 0.20 * class_instability
  + 0.20 * tracking_instability
  + 0.15 * occlusion
  + 0.15 * detector_disagreement
```

Sort frames by uncertainty.

Send the top N frames to the annotator.

This makes labeling substantially more efficient.

------------------------------------------------------------------------

# 11. Phase 2 --- Multi-Scale Detection

## 11.1 Problem

The far end of a traffic approach contains tiny vehicles.

A full-frame detector might see:

``` text
1920 × 1080 frame

far vehicle:
12 × 10 pixels
```

That is difficult to classify reliably.

------------------------------------------------------------------------

# 12. Full-Frame + Tiled Detection

Run two detection paths.

``` text
                  FRAME
                    │
           ┌────────┴────────┐
           │                 │
      Full-frame          Queue ROI
       detector            detector
           │                 │
           │            tile into crops
           │                 │
           │         ┌───┬───┬───┐
           │         │ 1 │ 2 │ 3 │
           │         ├───┼───┼───┤
           │         │ 4 │ 5 │ 6 │
           │         └───┴───┴───┘
           │                 │
           └────────┬────────┘
                    ▼
             Detection Fusion
```

------------------------------------------------------------------------

# 13. Defining the Far-Field ROI

Do not hard-code an arbitrary rectangle.

Configure a polygon:

``` yaml
far_field:
  polygon:
    - [250, 300]
    - [1650, 300]
    - [1900, 720]
    - [100, 720]
```

This should cover the road approaches where vehicles become small.

------------------------------------------------------------------------

# 14. Tiling Algorithm

Conceptually:

``` python
def generate_tiles(frame, roi, tile_size=640, overlap=0.20):
    # crop ROI
    # divide into overlapping tiles
    # retain mapping from tile coordinates to original coordinates
    return tiles
```

For every tile:

``` python
results = model(tile)
```

Convert tile detections:

``` text
tile coordinates
        ↓
original frame coordinates
```

If a tile begins at:

``` text
x_offset = 800
y_offset = 300
```

and a vehicle is:

``` text
x1=100, y1=50
```

then:

``` text
global_x1 = 900
global_y1 = 350
```

------------------------------------------------------------------------

# 15. Fuse Duplicate Detections

Overlapping tiles can detect the same vehicle.

Use box matching based on IoU.

For boxes A and B:

\[ IoU(A,B)=`\frac{|A\cap B|}{|A\cup B|}`{=tex} \]

If:

``` text
IoU > threshold
```

treat them as candidates for the same object.

Keep the strongest detection or fuse coordinates.

The fusion layer must happen **before tracking**.

------------------------------------------------------------------------

# 16. Adaptive Tiled Inference

Do not run expensive tiled inference on every frame.

Use:

``` text
normal frame
   ↓
full-frame detector
   ↓
far-field confidence good?
   ├── YES → finish
   └── NO  → tiled inference
```

Trigger tiled inference when:

``` text
far-field object count drops unexpectedly
```

or:

``` text
small-object confidence is low
```

or:

``` text
queue estimate is inconsistent
```

This keeps real-time performance manageable.

------------------------------------------------------------------------

# 17. Phase 3 --- Temporal Detection

A traffic object should not be accepted solely because it appears in one
frame.

Create a detection confirmation layer.

``` text
raw detection
     ↓
candidate
     ↓
seen across N frames?
     ↓
YES
     ↓
confirmed track
```

For example:

``` text
Frame 1: 0.78
Frame 2: 0.84
Frame 3: 0.81

→ confirmed
```

But:

``` text
Frame 1: 0.51
Frame 2: absent
Frame 3: absent

→ discard
```

Use configurable parameters:

``` yaml
temporal:
  confirmation_frames: 3
  max_missing_frames: 15
  class_switch_window: 10
```

------------------------------------------------------------------------

# 18. Detection History

For every track maintain:

``` python
class TrackState:
    track_id
    class_history
    confidence_history
    bbox_history
    world_position_history
    speed_history
    heading_history
    timestamp_history
```

Then calculate:

``` python
mean_confidence
confidence_variance
class_stability
motion_stability
```

------------------------------------------------------------------------

# 19. Class Stabilization

A vehicle should not oscillate:

``` text
car
truck
car
bus
car
```

across frames.

Maintain class votes.

Example:

``` python
class_scores = {
    "car": 8,
    "truck": 1,
    "bus": 0
}
```

Choose the dominant stable class unless new evidence is substantially
stronger.

For important classes such as:

``` text
ambulance
fire_truck
brts_bus
```

require stronger temporal confirmation.

------------------------------------------------------------------------

# 20. Phase 4 --- BoT-SORT State Upgrade

The current BoT-SORT design is a good foundation.

Do not replace it immediately.

Instead, create a richer state machine.

``` text
NEW
 ↓
TENTATIVE
 ↓
CONFIRMED
 ↓
VISIBLE
 ↓
PARTIALLY_OCCLUDED
 ↓
HEAVILY_OCCLUDED
 ↓
PREDICTED
 ↓
REAPPEARED
 ↓
LOST
```

------------------------------------------------------------------------

# 21. Occlusion Detection

Estimate occlusion using:

``` text
bbox overlap
+
mask overlap if available
+
sudden area reduction
+
neighboring vehicles
```

If another vehicle overlaps a large portion of the object:

``` python
occlusion_ratio = intersection_area / vehicle_area
```

Then:

``` text
< 0.20 → visible
0.20–0.50 → partial
> 0.50 → heavy
```

Thresholds should be tuned on your data.

------------------------------------------------------------------------

# 22. Track Reappearance

When an object disappears:

``` text
track remains alive for N frames
```

Use:

``` text
Kalman prediction
+
Re-ID embedding
+
vehicle class
+
world-space position
+
heading
```

to match a reappearing detection.

Do not create a new vehicle count immediately.

This prevents:

``` text
one real vehicle
→ two track IDs
→ two counted vehicles
```

------------------------------------------------------------------------

# 23. Track Quality Score

For every track calculate:

\[ T = w_1C_d+w_2C_r+w_3C_m+w_4C_c \]

where:

-   (C_d): detection confidence
-   (C_r): Re-ID confidence
-   (C_m): motion consistency
-   (C_c): class consistency

Normalize:

``` text
0 → unreliable
1 → highly reliable
```

This becomes an input to downstream traffic-state confidence.

------------------------------------------------------------------------

# 24. Phase 5 --- Vehicle State Estimation

Do not store only:

``` text
bbox
class
confidence
```

Store:

``` python
VehicleState:
    track_id
    class_name
    detection_confidence
    track_confidence
    bbox
    ground_contact
    world_x
    world_y
    speed
    acceleration
    heading
    lane_id
    maneuver
    queue_probability
    occlusion_ratio
    age
    state
```

This object becomes the fundamental unit of the perception layer.

------------------------------------------------------------------------

# 25. Ground Contact Point Improvement

The current bottom-center point is:

\[ x=`\frac{x_1+x_2}{2}`{=tex} \]

\[ y=y_2 \]

Keep this as the default.

However, for difficult detections use segmentation.

``` text
normal vehicle
    ↓
bottom-center bbox

difficult / tall / heavily occluded
    ↓
mask refinement
    ↓
bottom-most reliable road contact
```

Do not run segmentation on every vehicle unless your hardware supports
it.

Use it selectively.

------------------------------------------------------------------------

# 26. Optional Segmentation Refinement

Trigger segmentation when:

``` text
vehicle is large
AND
occlusion is high
```

or:

``` text
vehicle class = bus/truck
```

or:

``` text
bottom-center confidence is low
```

The segmentation output can improve:

``` text
ground contact
vehicle area
occlusion estimation
lane boundary interaction
```

SAM can remain primarily an annotation tool; a lighter operational
segmentation model can be used for real-time refinement if required.

------------------------------------------------------------------------

# 27. Optional Oriented Bounding Boxes

For vehicles where orientation matters, represent:

``` text
(x, y, width, height, angle)
```

Use orientation for:

``` text
heading
wrong-way detection
lane alignment
turn classification
```

Do not force OBB onto every vehicle if it adds too much latency.

------------------------------------------------------------------------

# 28. Phase 6 --- Camera Health Monitoring

Create:

``` text
camera/health.py
```

The module should calculate:

``` text
frame_received
frame_timestamp
fps
brightness
blur
contrast
camera_motion
visibility
rain_score
occlusion_score
```

------------------------------------------------------------------------

# 29. Frozen Camera Detection

Calculate frame difference:

\[ D_t = mean(\|I_t-I\_{t-1}\|) \]

If:

``` text
D_t ≈ 0
```

for a long period while timestamps continue changing, suspect a frozen
stream.

Example:

``` python
if frame_difference < freeze_threshold:
    frozen_counter += 1
else:
    frozen_counter = 0
```

------------------------------------------------------------------------

# 30. Blur Detection

Use variance of Laplacian:

``` python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
```

Low values indicate blur.

Do not treat one threshold as universal. Calibrate it using actual
junction footage.

------------------------------------------------------------------------

# 31. Camera Vibration

Estimate global image motion using feature matching or optical flow.

If many independent features move similarly:

``` text
global motion
```

is likely camera motion rather than vehicle motion.

Use this information for:

``` text
camera health
homography validity
tracking confidence
```

BoT-SORT CMC can still handle tracking compensation.

------------------------------------------------------------------------

# 32. Camera Shift Detection

The most dangerous case is not small vibration.

It is:

``` text
camera physically moved
```

After calibration, define stable road landmarks.

Example:

``` text
lane marking
stop line
curb
traffic island
road edge
```

Compare their current positions against the calibrated positions.

If:

``` text
mean landmark displacement > threshold
```

mark:

``` text
calibration_valid = false
```

Do not silently continue producing metric queue lengths after a major
camera shift.

------------------------------------------------------------------------

# 33. Calibration Health

Publish:

``` json
{
  "camera_health": 0.94,
  "homography_health": 0.91,
  "camera_shift_detected": false,
  "calibration_valid": true
}
```

This is critical because an incorrect homography can corrupt:

``` text
speed
queue length
lane assignment
BRTS detection
```

simultaneously.

------------------------------------------------------------------------

# 34. Phase 7 --- Improve Lane Assignment

The current polygon approach is simple and useful:

``` text
vehicle point ∈ polygon
```

Keep polygons as a safety fallback.

But make the primary lane representation a **centerline corridor**.

Example:

``` text
lane centerline:

        ●
       ●
      ●
     ●
    ●
   ●
```

Represent the lane as:

``` text
centerline + width
```

------------------------------------------------------------------------

# 35. Centerline Distance

For a vehicle position (P), calculate the shortest distance to the lane
centerline:

\[ d(P,L)=`\min`{=tex}\_{x`\in `{=tex}L}\|P-x\| \]

If:

``` text
distance < lane_width / 2
```

the vehicle is a candidate for that lane.

Then combine with heading.

------------------------------------------------------------------------

# 36. Lane Assignment Score

For each lane:

\[ S\_{lane} = w_1(1-d\_{norm}) +w_2H\_{match} +w_3T\_{match} \]

where:

-   (d\_{norm}): normalized distance from centerline
-   (H\_{match}): heading similarity
-   (T\_{match}): trajectory compatibility

Select the highest score.

This is much better than relying only on instantaneous polygon
membership.

------------------------------------------------------------------------

# 37. Lane Hysteresis

A vehicle near a lane boundary can oscillate:

``` text
NS_1
NS_2
NS_1
NS_2
```

Prevent this with hysteresis.

Keep the current lane unless another lane exceeds it by a meaningful
margin.

Example:

``` python
if new_score > current_score + lane_switch_margin:
    switch_lane()
```

This stabilizes telemetry.

------------------------------------------------------------------------

# 38. Phase 8 --- Movement / Maneuver Classification

Instead of only:

``` text
lane = NS_1
```

classify:

``` text
straight
left
right
u-turn
```

Use trajectory.

Example:

``` text
               LEFT
                 ↖
                ●
              ●
            ●
          ●
        ●
────────●────────────
```

Track heading changes over time.

A simple first implementation:

``` text
heading at entry
+
heading near intersection
+
exit direction
```

Then classify.

------------------------------------------------------------------------

# 39. Why Maneuver Classification Matters

Your signal optimizer can use:

``` text
NS straight = 12 PCU
NS left = 7 PCU
NS right = 3 PCU
```

instead of:

``` text
NS = 22 PCU
```

This makes phase pressure more accurate.

------------------------------------------------------------------------

# 40. Phase 9 --- Better Queue Detection

The current queue definition uses stationary vehicles under a speed
threshold.

Upgrade it to a probability.

For vehicle (i):

\[ Q_i = w_1S_i+ w_2D_i+ w_3R_i+ w_4F_i+ w_5T_i+ w_6G_i \]

where:

-   (S_i): low-speed evidence
-   (D_i): distance to stop line
-   (R_i): red-signal evidence
-   (F_i): following-vehicle density
-   (T_i): stop duration
-   (G_i): group/queue continuity

Normalize to:

``` text
0–1
```

------------------------------------------------------------------------

# 41. Queue Membership Example

Vehicle A:

``` text
speed = 2 km/h
distance to stop line = 8m
red phase = true
stopped = 12s
many vehicles behind = true
```

Queue probability:

``` text
0.96
```

Vehicle B:

``` text
speed = 2 km/h
distance = 80m
red = false
stopped = 2s
few vehicles nearby
```

Queue probability:

``` text
0.28
```

This avoids calling every slow vehicle a queue vehicle.

------------------------------------------------------------------------

# 42. Queue Length

Instead of simply taking the farthest stationary vehicle:

1.  Identify vehicles with queue probability above threshold.
2.  Project them into world coordinates.
3.  Identify the stop-line distance.
4.  Find the farthest reliable queue member.
5.  Smooth the resulting queue boundary.

Example:

``` python
queue_vehicles = [
    v for v in lane_vehicles
    if v.queue_probability > 0.7
]

queue_length = max(
    stopline_distance(v)
    for v in queue_vehicles
)
```

------------------------------------------------------------------------

# 43. Queue Smoothing

Raw queue length will fluctuate.

Use:

``` text
EMA
or
median filter
```

but do not smooth so heavily that the system reacts too slowly.

For example:

\[ Q_t\^{smooth} = `\alpha `{=tex}Q_t+
(1-`\alpha`{=tex})Q\_{t-1}\^{smooth} \]

Tune (`\alpha`{=tex}) experimentally.

------------------------------------------------------------------------

# 44. Queue Shockwave Detection

Store:

``` text
queue_length(t)
```

Then:

\[ v_q=`\frac{Q_t-Q_{t-\Delta t}}{\Delta t}`{=tex} \]

and:

\[ a_q=`\frac{v_q(t)-v_q(t-\Delta t)}{\Delta t}`{=tex} \]

The current optimizer already uses queue growth and acceleration. The
upgraded vision layer should make these values more reliable by basing
them on stable queue-boundary tracking.

------------------------------------------------------------------------

# 45. Queue Spillback Detection

Define a lane's usable queue capacity:

``` text
maximum_safe_queue_length
```

Then:

``` text
if predicted_queue_length > capacity:
    spillback_risk = HIGH
```

Better:

``` text
current queue
+
queue growth rate
+
available road length
```

Estimate time to spillback:

\[ T\_{spill} = `\frac{L_{available}-Q}{v_q}`{=tex} \]

when (v_q\>0).

If the time is small, notify the optimizer early.

------------------------------------------------------------------------

# 46. Phase 10 --- PCU Improvements

The current system uses class-specific PCU weights.

Keep that.

But add confidence weighting:

\[ PCU\_{effective} = `\sum`{=tex}*i w*{class(i)} C_i \]

where (C_i) is the confidence of the vehicle classification.

This prevents uncertain detections from contributing the same amount as
highly reliable detections.

For example:

``` text
car, PCU=1.0, confidence=.95
```

contributes approximately:

``` text
0.95
```

while:

``` text
truck, PCU=3.0, confidence=.55
```

contributes less than an unquestioned truck detection.

The exact policy should be validated against ground truth.

------------------------------------------------------------------------

# 47. Phase 11 --- Speed Estimation

The current system converts pixel coordinates to world coordinates and
estimates displacement over a frame window, then smooths using EMA.

Keep this architecture.

Improve it by using a longer, adaptive window.

If:

``` text
vehicle moving fast
```

use a shorter window.

If:

``` text
vehicle nearly stationary
```

use a longer window to reduce jitter.

------------------------------------------------------------------------

# 48. Speed Outlier Rejection

Reject physically impossible changes.

For example:

``` text
previous speed = 4 km/h
new speed = 120 km/h
```

This is likely an estimation error.

Use acceleration limits:

``` python
if abs(new_speed - old_speed) / dt > max_acceleration:
    mark_speed_uncertain()
```

Do not simply clamp it silently; record the uncertainty.

------------------------------------------------------------------------

# 49. Phase 12 --- Object-Level Confidence

For every vehicle calculate:

``` text
detection_confidence
tracking_confidence
class_confidence
position_confidence
speed_confidence
lane_confidence
```

Example:

``` json
{
  "track_id": 183,
  "class": "two_wheeler",
  "detection_confidence": 0.91,
  "tracking_confidence": 0.96,
  "class_confidence": 0.93,
  "position_confidence": 0.89,
  "speed_confidence": 0.82,
  "lane_confidence": 0.94
}
```

------------------------------------------------------------------------

# 50. Scene-Level Confidence

Calculate:

``` text
scene_confidence =
    detection quality
    × tracking quality
    × camera health
    × calibration health
    × visibility
```

A practical first version can use a weighted average rather than a
strict product.

Example:

\[ C\_{scene} = 0.30C\_{det} +0.20C\_{track} +0.15C\_{camera}
+0.15C\_{calib} +0.20C\_{visibility} \]

Tune weights using validation data.

------------------------------------------------------------------------

# 51. Occlusion Ratio

Calculate:

\[ O = `\frac{\text{estimated occluded area}}`{=tex}
{`\text{vehicle area}`{=tex}} \]

Aggregate by lane:

``` text
lane_occlusion_ratio
```

This tells the optimizer whether:

``` text
vehicle_count = 20
```

is highly trustworthy or potentially missing many vehicles.

------------------------------------------------------------------------

# 52. Estimating Missed Vehicles

Do not pretend to know the exact number of missed vehicles.

Instead report an uncertainty interval.

Example:

``` text
detected = 40
scene confidence = 0.78
occlusion = high
```

You might report:

``` text
estimated count = 40
confidence = 0.78
```

and, after calibrating the estimator on validation data:

``` text
estimated range = 35–49
```

The interval should come from empirical validation rather than an
arbitrary formula.

------------------------------------------------------------------------

# 53. Confidence Calibration

Raw neural-network confidence is not necessarily a calibrated
probability.

Use a held-out validation set.

Compare:

``` text
predicted confidence
vs
actual correctness
```

Generate a reliability diagram.

Possible calibration methods include:

``` text
temperature scaling
isotonic regression
Platt-style calibration
```

Use the simplest method that performs well on your validation data.

------------------------------------------------------------------------

# 54. Phase 13 --- Emergency Vehicle Detection

This subsystem deserves special treatment because a false emergency
trigger can disrupt an intersection.

Current detection uses dedicated emergency classes and beacon
heuristics.

Upgrade to multi-signal fusion.

``` text
             Vision
               │
               ▼
       emergency vehicle
        classification
               │
               ├──────────────┐
               ▼              ▼
          beacon score    trajectory
               │              │
               └──────┬───────┘
                      ▼
                optional audio
                      │
                      ▼
               temporal fusion
                      │
                      ▼
              emergency score
```

------------------------------------------------------------------------

# 55. Emergency Temporal Logic

Never trigger based on a single frame.

Example state:

``` text
CANDIDATE
   ↓
CONFIRMED
   ↓
APPROACHING
   ↓
PREEMPTION_REQUESTED
   ↓
PASSED
   ↓
CLEAR
```

Require persistence.

For example:

``` text
detected for ≥ N frames
```

before automatic action, unless an operator-defined safety policy says
otherwise.

------------------------------------------------------------------------

# 56. Emergency Features

Use:

``` text
vehicle class
appearance
beacon
trajectory
speed
heading
distance to junction
temporal persistence
```

Optional:

``` text
audio siren
```

If audio is added:

``` text
microphone
    ↓
audio feature extraction
    ↓
siren classifier
    ↓
siren confidence
```

Then fuse vision and audio.

------------------------------------------------------------------------

# 57. Emergency Confidence

Example:

\[ E = 0.35V+ 0.20B+ 0.20T+ 0.15H+ 0.10A \]

where:

-   (V): visual class confidence
-   (B): beacon confidence
-   (T): temporal confidence
-   (H): heading/approach confidence
-   (A): audio confidence

If audio is unavailable, redistribute weights rather than inserting zero
blindly.

The actual preemption thresholds must be validated and governed by
safety rules.

------------------------------------------------------------------------

# 58. Phase 14 --- BRTS Violation Detection

Current logic:

``` text
vehicle enters BRTS polygon
→ non-BRTS vehicle
→ remains ≥ 3 seconds
→ violation
```

Keep this as a baseline.

Upgrade to trajectory-based evidence.

Calculate:

``` text
entry point
entry direction
distance traveled inside BRTS corridor
dwell time
exit point
heading
```

------------------------------------------------------------------------

# 59. BRTS Violation Score

Example:

\[ V = w_1Dwell+ w_2Distance+ w_3Trajectory+ w_4ClassConfidence \]

Use a state machine:

``` text
OUTSIDE
   ↓
ENTERED
   ↓
POTENTIAL_VIOLATION
   ↓
CONFIRMED
   ↓
EXITED
```

This prevents a one-frame polygon intersection from becoming a formal
violation.

------------------------------------------------------------------------

# 60. BRTS False Positive Reduction

Do not flag:

``` text
vehicle briefly crossing boundary
```

as a full violation.

Consider:

``` text
dwell time
+
distance
+
direction
```

before confirmation.

Store:

``` json
{
  "track_id": 123,
  "violation_type": "BRTS_INTRUSION",
  "duration_sec": 7.4,
  "distance_inside_m": 28.2,
  "confidence": 0.93
}
```

------------------------------------------------------------------------

# 61. Phase 15 --- Wrong-Way Detection

Current dot-product logic is a good starting point.

Upgrade it with:

``` text
expected lane direction
+
vehicle heading
+
trajectory direction
+
world-space displacement
```

Calculate:

\[ `\cos`{=tex}`\theta `{=tex}=
`\frac{\vec v_{vehicle}\cdot\vec v_{lane}}`{=tex}
{\|`\vec `{=tex}v\_{vehicle}\|\|`\vec `{=tex}v\_{lane}\|} \]

A strongly negative value indicates opposite direction.

But require persistence.

Example:

``` text
wrong-way candidate
→ persists for 1 second
→ trajectory consistent
→ confirmed
```

This avoids false alerts from turning vehicles.

------------------------------------------------------------------------

# 62. Phase 16 --- Breakdown Detection

The current rule:

``` text
position almost unchanged
>45 seconds
signal GREEN
```

is useful but not enough.

Classify stationary states:

``` text
NORMAL_QUEUE
PICKUP_DROPOFF
PARKED
BLOCKED
BREAKDOWN
```

Features:

``` text
speed
duration
signal state
lane location
surrounding vehicle motion
hazard indicators
vehicle behavior before stopping
```

------------------------------------------------------------------------

# 63. Breakdown State Machine

``` text
MOVING
  ↓
SLOWING
  ↓
STOPPED_CANDIDATE
  ↓
CONTEXT_CHECK
  ├── queue → NORMAL_QUEUE
  ├── roadside → PARKED
  ├── short stop → PICKUP
  └── persistent blockage → BREAKDOWN
```

This is more useful than one hard-coded 45-second rule.

------------------------------------------------------------------------

# 64. Phase 17 --- Scene Condition Classification

Classify:

``` text
day
night
rain
fog
glare
low visibility
```

A lightweight classifier or rule-based image-quality layer can initially
be used.

Example:

``` text
brightness
contrast
saturation
rain features
headlight intensity
```

Then choose preprocessing.

------------------------------------------------------------------------

# 65. Condition-Aware Preprocessing

``` text
                FRAME
                  │
          Scene classifier
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
      DAY       NIGHT       RAIN
       │          │          │
    normal      CLAHE     denoise/
                            contrast
       └──────────┬──────────┘
                  ▼
               detector
```

Avoid aggressive CLAHE on every frame because preprocessing can amplify
noise.

------------------------------------------------------------------------

# 66. Phase 18 --- Dynamic Thresholds

Do not use one confidence threshold for every condition.

Example:

``` yaml
thresholds:
  day: 0.45
  night: 0.35
  rain: 0.40
  fog: 0.30
```

These numbers are examples only.

Derive actual values from the validation dataset.

Optimize for:

``` text
precision-recall tradeoff
```

for each scene condition.

------------------------------------------------------------------------

# 67. Phase 19 --- Test-Time Enhancement for Difficult Frames

For low-confidence frames only:

``` text
original frame
contrast-enhanced frame
brightness-adjusted frame
```

Run inference.

Fuse predictions.

Do not use this on every frame unless performance permits.

------------------------------------------------------------------------

# 68. Phase 20 --- Secondary Detector for Uncertain Cases

A secondary detector can be used only when:

``` text
primary detector uncertain
```

Example:

``` text
YOLO26:
car 0.48

secondary model:
two_wheeler 0.79

tracker:
trajectory consistent with two_wheeler

→ final two_wheeler confidence increases
```

This is preferable to running two heavy detectors continuously.

------------------------------------------------------------------------

# 69. Phase 21 --- Perception Telemetry Redesign

The current lane telemetry should be extended.

Suggested structure:

``` json
{
  "junction_id": "junction_01",
  "timestamp": "2026-09-03T15:30:00Z",

  "scene": {
    "lighting": "night",
    "weather": "rain",
    "visibility": 0.72,
    "scene_confidence": 0.81
  },

  "camera": {
    "health": 0.95,
    "blur_score": 0.41,
    "camera_motion": 0.06,
    "calibration_valid": true,
    "homography_health": 0.93
  },

  "lanes": [
    {
      "lane_id": "lane_NS_1",

      "vehicle_count": 14,
      "vehicle_count_confidence": 0.92,

      "pcu": 16.3,
      "pcu_confidence": 0.90,

      "queue_length_m": 42.5,
      "queue_confidence": 0.87,

      "queue_growth_rate": 0.12,
      "queue_acceleration": 0.03,

      "avg_speed_kmph": 3.8,
      "speed_confidence": 0.82,

      "occlusion_ratio": 0.29,

      "movement_counts": {
        "straight": 9,
        "left": 3,
        "right": 2
      }
    }
  ]
}
```

------------------------------------------------------------------------

# 70. Object-Level Telemetry

For debugging, optionally publish detailed tracks separately:

``` json
{
  "track_id": 183,
  "class": "two_wheeler",
  "bbox": [100, 200, 140, 250],
  "world_position": [21.17, 72.83],
  "speed_kmph": 5.2,
  "heading_deg": 178,
  "lane_id": "NS_1",
  "maneuver": "straight",
  "queue_probability": 0.91,
  "occlusion_ratio": 0.18,
  "track_confidence": 0.96
}
```

Do not necessarily send every object at high frequency to Kafka in
production. Separate:

``` text
real-time aggregate telemetry
```

from:

``` text
debug/object telemetry
```

------------------------------------------------------------------------

# 71. Phase 22 --- Confidence-Aware Signal Optimization

This is where the detection upgrade becomes a system-level innovation.

Current signal optimization uses traffic state such as queue, growth
rate, acceleration, prediction and pressure.

Add perception confidence.

For a lane:

\[ Q\_{effective}=C_Q Q \]

where:

-   \(Q\) = estimated queue
-   (C_Q) = queue confidence

Similarly:

\[ PCU\_{effective}=C_P PCU \]

Then pressure can use confidence-aware inputs.

------------------------------------------------------------------------

# 72. Risk-Aware Pressure

A more advanced formulation is:

\[ P\_{safe}(p) = E\[P(p)\] - `\lambda`{=tex}`\sqrt{Var(P(p))}`{=tex} \]

Interpretation:

``` text
high expected pressure
+
low uncertainty
→ strong decision

high expected pressure
+
high uncertainty
→ cautious decision
```

This prevents a noisy camera from causing extreme signal changes.

------------------------------------------------------------------------

# 73. Historical Fallback

When scene confidence becomes low:

``` text
camera telemetry
        ↓
confidence check
        ↓
┌───────────────┬─────────────────┐
│ high          │ low             │
│ confidence    │ confidence      │
▼               ▼
live state      blend with
                historical state
```

Your current optimizer already has historical blending and cautious
mode. The upgrade is to make the transition depend on multiple
perception-health signals rather than only one global detection
confidence.

------------------------------------------------------------------------

# 74. Phase 23 --- Evaluation Framework

This is essential.

Do not claim the detection system is improved without measurement.

Create a manually annotated test set.

Evaluate:

## Detection

``` text
Precision
Recall
F1
mAP@50
mAP@50:95
```

## Small objects

``` text
small-object recall
small-object precision
```

## Classes

``` text
car recall
bus recall
truck recall
two-wheeler recall
auto recall
BRTS recall
emergency recall
```

------------------------------------------------------------------------

# 75. Tracking Metrics

Use:

``` text
HOTA
IDF1
MOTA
ID switches
track fragmentation
```

The most important practical tracking metrics for your application are:

``` text
IDF1
HOTA
ID switches
```

because identity continuity affects counting and trajectories.

------------------------------------------------------------------------

# 76. Traffic-State Metrics

Measure:

### Vehicle count

\[ MAE = `\frac{1}{N}`{=tex}`\sum `{=tex}\|predicted-actual\| \]

### Queue length

\[ MAE_Q = `\frac{1}{N}`{=tex}`\sum `{=tex}\|Q\_{pred}-Q\_{actual}\| \]

### Speed

\[ MAE_V = `\frac{1}{N}`{=tex}`\sum `{=tex}\|V\_{pred}-V\_{actual}\| \]

### Lane assignment

``` text
correct lane assignments / total assignments
```

------------------------------------------------------------------------

# 77. Event Metrics

For BRTS:

``` text
precision
recall
F1
false alerts/hour
detection latency
```

For emergency:

``` text
precision
recall
false preemption rate
detection latency
```

For breakdown:

``` text
precision
recall
time-to-detection
```

------------------------------------------------------------------------

# 78. Latency Benchmark

Measure every stage:

``` text
preprocessing
detector
tiled detector
fusion
tracking
geometry
analytics
event serialization
```

Example:

``` text
Preprocessing       2 ms
YOLO                11 ms
Tiled inference     7 ms
Fusion              1 ms
Tracking             4 ms
Geometry             1 ms
Analytics            1 ms
-------------------------
Total               27 ms
```

The numbers above are examples. Measure your actual system.

------------------------------------------------------------------------

# 79. Ablation Study

This is extremely important for a project report.

Run:

``` text
Baseline
```

Then:

``` text
Baseline + tiled detection
Baseline + temporal filtering
Baseline + improved lane assignment
Baseline + queue model
Baseline + uncertainty
```

Compare each.

Example table:

  System             Vehicle Recall   Queue MAE   IDF1
  ---------------- ---------------- ----------- ------
  Baseline                      ...         ...    ...
  \+ Tiling                     ...         ...    ...
  \+ Temporal                   ...         ...    ...
  \+ Lane model                 ...         ...    ...
  \+ Queue model                ...         ...    ...
  Full system                   ...         ...    ...

This demonstrates that each engineering improvement actually helps.

------------------------------------------------------------------------

# 80. Stress Testing

Create dedicated test groups:

``` text
Test A: daylight
Test B: night
Test C: rain
Test D: heavy congestion
Test E: severe occlusion
Test F: small vehicles
Test G: camera vibration
Test H: BRTS
Test I: emergency
```

Report performance separately.

A model that performs well overall but fails badly at night is not
sufficient for your application.

------------------------------------------------------------------------

# 81. Recommended Implementation Order

## Sprint 1 --- Dataset

Implement:

``` text
frame extraction
dataset metadata
train/val/test split
hard-case collection
annotation workflow
```

Deliverable:

``` text
versioned dataset
```

------------------------------------------------------------------------

## Sprint 2 --- Detector

Implement:

``` text
full-frame YOLO26
far-field ROI
tiled detection
coordinate remapping
duplicate fusion
```

Deliverable:

``` text
better small-object recall
```

------------------------------------------------------------------------

## Sprint 3 --- Temporal Tracking

Implement:

``` text
track state
class history
confidence history
occlusion state
track confirmation
lost/reappeared logic
```

Deliverable:

``` text
stable vehicle IDs
```

------------------------------------------------------------------------

## Sprint 4 --- Geometry

Implement:

``` text
world coordinates
lane centerlines
lane distance
heading matching
lane hysteresis
```

Deliverable:

``` text
stable lane assignment
```

------------------------------------------------------------------------

## Sprint 5 --- Traffic State

Implement:

``` text
queue probability
queue boundary
queue smoothing
movement classification
speed confidence
PCU confidence
```

Deliverable:

``` text
more accurate traffic telemetry
```

------------------------------------------------------------------------

## Sprint 6 --- Incidents

Implement:

``` text
BRTS trajectory detection
wrong-way persistence
breakdown classification
emergency state machine
```

Deliverable:

``` text
high-quality event detection
```

------------------------------------------------------------------------

## Sprint 7 --- Camera Health

Implement:

``` text
blur
freeze
brightness
camera motion
visibility
calibration drift
```

Deliverable:

``` text
camera health score
```

------------------------------------------------------------------------

## Sprint 8 --- Uncertainty

Implement:

``` text
object confidence
track confidence
lane confidence
queue confidence
scene confidence
confidence calibration
```

Deliverable:

``` text
uncertainty-aware telemetry
```

------------------------------------------------------------------------

## Sprint 9 --- Optimizer Integration

Modify optimizer input:

``` text
raw traffic state
+
confidence
+
uncertainty
```

Deliverable:

``` text
confidence-aware adaptive control
```

------------------------------------------------------------------------

# 82. Configuration Design

Do not hard-code thresholds.

Create:

``` yaml
detection:
  confidence_threshold: 0.45
  small_object_threshold: 0.35

tracking:
  confirmation_frames: 3
  max_missing_frames: 15
  reid_threshold: 0.70

queue:
  speed_threshold_kmph: 5
  probability_threshold: 0.70
  smoothing_alpha: 0.30

brts:
  minimum_dwell_sec: 3.0
  confirmation_probability: 0.80

camera:
  blur_threshold: 100.0
  freeze_threshold: 0.001

confidence:
  cautious_mode_threshold: 0.60
```

All thresholds should ultimately be learned/tuned from your validation
set.

------------------------------------------------------------------------

# 83. Logging

Every important decision should be explainable.

Example:

``` text
[21:31:04]
Track 183
class=two_wheeler
detection=0.91
tracking=0.96
lane=NS_1
lane_confidence=0.94
speed=4.1
queue_probability=0.91
```

For BRTS:

``` text
Track 201
entered BRTS zone
dwell=4.2s
distance=18.4m
trajectory=consistent
violation_confidence=0.92
```

For camera:

``` text
Camera junction_01
blur=low
motion=normal
visibility=0.81
calibration=valid
```

------------------------------------------------------------------------

# 84. Debug Visualization

The existing visualization tool should be upgraded to display:

``` text
BBox
Track ID
Class
Confidence
Heading
Speed
Lane
Queue probability
Occlusion
```

For example:

``` text
┌──────────────────────────────┐
│ CAR #183                     │
│ conf: 0.94                   │
│ track: 0.97                  │
│ speed: 4.2 km/h              │
│ lane: NS_1                   │
│ queue: 0.92                  │
│ occlusion: 18%               │
└──────────────────────────────┘
```

Also display:

``` text
queue boundary
lane centerlines
stop line
BRTS polygon
trajectory
camera-health warning
```

This will be extremely useful during development.

------------------------------------------------------------------------

# 85. Failure-Case Recorder

Automatically save frames when:

``` text
low confidence
ID switch suspected
lane switch instability
BRTS candidate
emergency candidate
camera shift
queue inconsistency
```

Store:

``` text
frame
timestamp
junction
track IDs
model output
reason
```

Directory:

``` text
failure_cases/
├── detection/
├── tracking/
├── lane/
├── queue/
├── brts/
├── emergency/
└── camera/
```

This creates the data needed for the next training cycle.

------------------------------------------------------------------------

# 86. Continuous Learning Loop

The final system should operate as:

``` text
                 DEPLOYMENT
                     │
                     ▼
                  CCTV
                     │
                     ▼
                 Detector
                     │
                     ▼
                  Tracking
                     │
                     ▼
                Analytics
                     │
                     ▼
             Failure detection
                     │
                     ▼
              Failure cases
                     │
                     ▼
              Human review
                     │
                     ▼
              New training data
                     │
                     ▼
                Retraining
                     │
                     ▼
                Evaluation
                     │
              ┌──────┴──────┐
              │             │
           better         reject
           model
              │
              ▼
           deployment
```

Never automatically deploy a newly trained model without evaluation.

------------------------------------------------------------------------

# 87. Model Versioning

Use:

``` text
model_v1
model_v2
model_v3
```

Record:

``` text
dataset version
training configuration
validation metrics
test metrics
date
```

Example:

``` yaml
model:
  name: erakshak_yolo26
  version: 2.3

dataset:
  version: 4.1

metrics:
  mAP50: ...
  recall: ...
  small_object_recall: ...
```

------------------------------------------------------------------------

# 88. What NOT to Do

## Do not simply change YOLO models

A new detector without a better dataset and benchmark does not guarantee
improvement.

## Do not optimize only mAP

Traffic applications care about:

``` text
count
queue
speed
lane
tracking
events
latency
```

## Do not run expensive segmentation everywhere

Use selective refinement.

## Do not trust one-frame emergency detections

Use temporal confirmation and safety rules.

## Do not treat raw confidence as probability

Calibrate it.

## Do not rely only on static polygons

Use trajectory and centerline reasoning.

## Do not randomly split adjacent video frames

Avoid data leakage.

------------------------------------------------------------------------

# 89. Minimum Viable Upgrade

If implementation time is limited, implement these first:

### Priority 1

``` text
1. Larger Indian traffic dataset
2. Hard-negative mining
3. Tiled far-field detection
4. Temporal confirmation
5. Improved track state
```

### Priority 2

``` text
6. Centerline lane assignment
7. Queue probability
8. Camera health
9. Confidence estimation
```

### Priority 3

``` text
10. BRTS trajectory detection
11. Emergency temporal fusion
12. Segmentation refinement
13. OBB
14. Audio emergency sensing
```

------------------------------------------------------------------------

# 90. Best "Advanced Project" Version

If you have enough time and compute, the final perception stack should
be:

``` text
YOLO26
+
small-object tiled inference
+
hard-example training
+
active learning
+
temporal detection confirmation
+
BoT-SORT/Re-ID
+
occlusion state machine
+
segmentation refinement
+
optional OBB
+
homography
+
dynamic lane centerlines
+
trajectory-based maneuver classification
+
queue probability model
+
queue shockwave detection
+
camera health
+
calibration drift detection
+
emergency multimodal fusion
+
BRTS trajectory reasoning
+
confidence calibration
+
uncertainty-aware telemetry
+
continuous evaluation
```

------------------------------------------------------------------------

# 91. Recommended Final Data Flow

The final object-level flow should be:

``` text
Raw Frame
   ↓
Quality Check
   ↓
Scene Condition
   ↓
Preprocessing
   ↓
YOLO26
   ↓
Small-Object Tiled Detector if required
   ↓
Detection Fusion
   ↓
Temporal Confirmation
   ↓
BoT-SORT + Re-ID
   ↓
Track State
   ↓
Occlusion Analysis
   ↓
Segmentation/OBB refinement when required
   ↓
Ground Contact Point
   ↓
Homography
   ↓
World Coordinates
   ↓
Velocity / Heading / Acceleration
   ↓
Dynamic Lane Assignment
   ↓
Movement Classification
   ↓
Queue Probability
   ↓
PCU
   ↓
BRTS / Wrong-Way / Emergency / Breakdown
   ↓
Object + Scene Confidence
   ↓
Aggregated Traffic State
   ↓
Kafka
   ↓
Signal Optimizer
```

------------------------------------------------------------------------

# 92. Final Recommended Architecture

The strongest version of E-Rakshak should conceptually have four
perception levels:

## Level 1 --- Perception

``` text
What objects are present?
```

YOLO26 / tiled detection / segmentation.

## Level 2 --- Tracking

``` text
Which object is which?
Where is it going?
```

BoT-SORT / Re-ID / temporal state.

## Level 3 --- Traffic understanding

``` text
Which lane?
Which movement?
Is it queued?
Is it violating?
Is it an incident?
```

Geometry + trajectories + traffic-state models.

## Level 4 --- Uncertainty

``` text
How much should the system trust this information?
```

Detection confidence + tracking confidence + camera health +
calibration + occlusion + scene confidence.

That fourth layer is what allows the perception system to safely
influence adaptive signal control.

------------------------------------------------------------------------

# 93. The Most Important Implementation Principle

Do not think of the project as:

``` text
"Improve YOLO."
```

Think of it as:

``` text
"Improve the accuracy of the traffic state estimated from CCTV."
```

That changes what you optimize.

The final objective is:

\[ `\boxed{
\text{CCTV}
\rightarrow
\text{Reliable Vehicle States}
\rightarrow
\text{Reliable Traffic State}
\rightarrow
\text{Reliable Signal Decision}
}`{=tex} \]

A detector with slightly better mAP but poor queue estimation is less
valuable than a detector/tracker/geometry system that produces highly
accurate queue, speed, lane and movement estimates.

------------------------------------------------------------------------

# 94. Recommended Development Milestone

Your strongest demonstrable milestone should be:

``` text
ONE REAL JUNCTION
        ↓
ONE CAMERA
        ↓
DAY + NIGHT + RAIN DATA
        ↓
VEHICLE DETECTION
        ↓
STABLE TRACK IDs
        ↓
WORLD-SPACE TRAJECTORIES
        ↓
LANE ASSIGNMENT
        ↓
QUEUE LENGTH
        ↓
PCU
        ↓
BRTS VIOLATION
        ↓
EMERGENCY DETECTION
        ↓
CONFIDENCE
        ↓
SIGNAL OPTIMIZER
```

Make this pipeline extremely reliable before scaling to multiple
junctions.

------------------------------------------------------------------------

# 95. Final Implementation Checklist

## Dataset

-   [ ] Collect local Indian traffic footage
-   [ ] Separate day/night/rain/fog
-   [ ] Include heavy congestion
-   [ ] Include small vehicles
-   [ ] Include severe occlusion
-   [ ] Include BRTS
-   [ ] Include emergency vehicles
-   [ ] Split by camera/video, not adjacent frames
-   [ ] Create hard-negative dataset
-   [ ] Create active-learning workflow

## Detection

-   [ ] YOLO26 baseline
-   [ ] Full-frame inference
-   [ ] Far-field ROI
-   [ ] Tiled inference
-   [ ] Detection fusion
-   [ ] Dynamic thresholds
-   [ ] Temporal confirmation

## Tracking

-   [ ] BoT-SORT
-   [ ] Re-ID
-   [ ] Track state
-   [ ] Occlusion state
-   [ ] Class history
-   [ ] Confidence history
-   [ ] Lost/reappeared logic

## Geometry

-   [ ] Bottom-center baseline
-   [ ] Segmentation refinement
-   [ ] Homography
-   [ ] Calibration validation
-   [ ] Lane centerlines
-   [ ] Lane hysteresis
-   [ ] Heading estimation
-   [ ] Maneuver classification

## Traffic State

-   [ ] Speed
-   [ ] Speed confidence
-   [ ] Queue probability
-   [ ] Queue length
-   [ ] Queue smoothing
-   [ ] Queue growth
-   [ ] Queue shockwave
-   [ ] Spillback prediction
-   [ ] Confidence-weighted PCU

## Events

-   [ ] BRTS trajectory detection
-   [ ] Wrong-way persistence
-   [ ] Breakdown state machine
-   [ ] Emergency temporal fusion
-   [ ] Optional audio siren sensing

## Camera

-   [ ] FPS monitoring
-   [ ] Freeze detection
-   [ ] Blur detection
-   [ ] Brightness
-   [ ] Visibility
-   [ ] Vibration
-   [ ] Camera shift
-   [ ] Homography health

## Uncertainty

-   [ ] Detection confidence
-   [ ] Classification confidence
-   [ ] Track confidence
-   [ ] Lane confidence
-   [ ] Queue confidence
-   [ ] Camera confidence
-   [ ] Scene confidence
-   [ ] Confidence calibration

## Evaluation

-   [ ] mAP
-   [ ] Precision
-   [ ] Recall
-   [ ] Small-object recall
-   [ ] HOTA
-   [ ] IDF1
-   [ ] ID switches
-   [ ] Count MAE
-   [ ] Queue MAE
-   [ ] Speed MAE
-   [ ] Lane accuracy
-   [ ] BRTS F1
-   [ ] Emergency F1
-   [ ] Detection latency
-   [ ] End-to-end latency
-   [ ] Ablation study
-   [ ] Day/night/rain stress testing

------------------------------------------------------------------------

# 96. Bottom Line

The current E-Rakshak vision architecture is already a solid foundation.
The major improvement should be to move from:

``` text
DETECT → TRACK → COUNT
```

to:

``` text
DETECT
   ↓
TRACK
   ↓
UNDERSTAND MOTION
   ↓
UNDERSTAND ROAD GEOMETRY
   ↓
UNDERSTAND QUEUES
   ↓
UNDERSTAND INCIDENTS
   ↓
ESTIMATE UNCERTAINTY
   ↓
PRODUCE RELIABLE TRAFFIC STATE
```

The highest-impact implementation path is:

``` text
Indian dataset
     ↓
hard-negative mining
     ↓
multi-scale detection
     ↓
temporal tracking
     ↓
dynamic lane assignment
     ↓
queue-state estimation
     ↓
camera health
     ↓
confidence/uncertainty
     ↓
incident intelligence
     ↓
confidence-aware signal optimization
```

This gives E-Rakshak a much stronger technical contribution than merely
claiming that a newer YOLO model is being used.
