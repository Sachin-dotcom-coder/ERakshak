# E-Rakshak: Smart Adaptive Traffic Control & Infrastructure Intelligence

Welcome to the **E-Rakshak** repository — an AI-powered, data-driven adaptive traffic signal optimization platform designed for modern Indian cities.

---

## Comprehensive Project Documentation

We have provided two in-depth technical documentation files detailing the entire system architecture and computer vision pipeline:

1. 📘 **[PROJECT_OVERVIEW.md](file:///c:/Users/visha/OneDrive/Desktop/E_rakshak/ERakshak/PROJECT_OVERVIEW.md)** (or in `docs/` at [docs/PROJECT_OVERVIEW.md](file:///c:/Users/visha/OneDrive/Desktop/E_rakshak/ERakshak/docs/PROJECT_OVERVIEW.md))
   - **Full Project Specification**: System architecture, end-to-end data flow (Mermaid diagrams), all 5 subsystems (`vision-service`, `signal-optimizer`, `backend-api`, `dashboard`, `frontend`), mathematical formulations (PCU weighting, Homography, Max-Pressure, Webster cycle calculation), data contracts, DB ER diagrams, and step-by-step installation/running instructions.

2. 👁️ **[DETECTION_SYSTEM_DETAILS.md](file:///c:/Users/visha/OneDrive/Desktop/E_rakshak/ERakshak/DETECTION_SYSTEM_DETAILS.md)** (or in `docs/` at [docs/DETECTION_SYSTEM_DETAILS.md](file:///c:/Users/visha/OneDrive/Desktop/E_rakshak/ERakshak/docs/DETECTION_SYSTEM_DETAILS.md))
   - **Detection Subsystem Deep Dive**: In-depth technical breakdown of `vision-service`, including YOLO26 object detection with STAL, BoT-SORT multi-object tracking with Re-ID, planar homography transformation, spatial zone geometry, Passenger Car Unit (PCU) calculation, BRTS corridor intrusion detection, stalled vehicle incident sensing, SAM 3.1 auto-labeling pipeline, and edge-case mitigations.

3. ⚡ **[DETECTION_AND_POST_DETECTION_WORKFLOW.md](file:///c:/Users/visha/OneDrive/Desktop/E_rakshak/ERakshak/DETECTION_AND_POST_DETECTION_WORKFLOW.md)** (or in `docs/` at [docs/DETECTION_AND_POST_DETECTION_WORKFLOW.md](file:///c:/Users/visha/OneDrive/Desktop/E_rakshak/ERakshak/docs/DETECTION_AND_POST_DETECTION_WORKFLOW.md))
   - **End-to-End Perception & Action Manual**: Highlights the 2026 computer vision detection engine (YOLO26, BoT-SORT Re-ID, Homography, Zone PCU counts) AND the complete post-detection workflow (FastAPI ingestion, relational DB persistence, Redis Pub/Sub event bus, multi-factor Max-Pressure adaptive signal control, emergency & BRTS priority preemption, safety validator checks, infrastructure recommendation engine, automated e-Challan fine generation, real-time WebSocket dashboard streaming, and SUMO/ITMS traffic signal actuation).

---

## Subsystems Overview

- `vision-service/`: YOLO26 + BoT-SORT real-time computer vision telemetry pipeline.
- `signal-optimizer/`: Multi-factor Max-Pressure & Webster adaptive signal controller.
- `backend-api/`: FastAPI backend with WebSockets, SQLite/PostgreSQL, and event bus ingestion.
- `dashboard/` & `frontend/`: Command center Web UI with live map, signal countdowns, and video streams.
- `docs/` & `scripts/`: SUMO traffic simulation scenarios and performance benchmarking scripts.
