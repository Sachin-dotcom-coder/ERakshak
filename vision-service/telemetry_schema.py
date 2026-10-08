"""
telemetry_schema.py — Telemetry contract v2 with Pydantic validation
======================================================================
P0-13 FIX: Replaced single top-level `brts_violation` boolean and single
`lane_intrusion` object with an `events[]` array that can carry any number
of events per frame.

Changes from v1 → v2 (improvements.md §4):
- Added `schema_version`, `message_id`, `seq` for versioning and idempotency
- Added `camera_id`, `model_version`, `calibration_version`
- Added `capture_ts` and `publish_ts` (both needed for latency measurement)
- Added `health` block (fps, dropped_frames, mean_confidence, visibility_score)
- Added `observed_signal` block (for red-light violation cross-checking)
- Added `movements[]` array for per-movement metrics (Max-Pressure needs this)
- Changed single-slot violation fields → `events[]` array (P0-13)
- Each event has `event_id` for idempotent handling on the consumer side

All messages must be validated against this schema on ingestion.
Invalid messages are rejected and counted (never silently dropped).

Usage:
    from telemetry_schema import TelemetryMessage, VisionEvent
    msg = TelemetryMessage(**raw_dict)    # validates on construction
    msg_json = msg.model_dump_json()
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class HealthBlock(BaseModel):
    """Camera / pipeline health metrics for this telemetry message."""
    fps: float = Field(..., ge=0, description="Measured processing FPS for this camera")
    dropped_frames: int = Field(0, ge=0, description="Frames dropped since last message")
    mean_confidence: float = Field(..., ge=0.0, le=1.0, description="Mean detection confidence")
    visibility_score: float = Field(1.0, ge=0.0, le=1.0, description="0=invisible, 1=perfect")


class ObservedSignal(BaseModel):
    """Signal state observed by vision (or from controller feed)."""
    phase: str = Field(..., description="Active signal phase name (e.g. 'NS_THROUGH')")
    state: Literal["RED", "YELLOW", "GREEN", "UNKNOWN"] = Field(...)
    elapsed_s: float = Field(..., ge=0, description="Seconds in current state")
    source: Literal["vision", "controller", "vision+controller"] = Field("vision")


class Movement(BaseModel):
    """
    Per-movement metrics for one approach-direction group.
    Max-Pressure works at movement level — per-lane rollup not sufficient (P0-7 fix).
    """
    movement_id: str = Field(..., description="e.g. 'N_through', 'E_left'")
    lane_ids: list[str] = Field(default_factory=list)
    vehicle_count: int = Field(0, ge=0)
    pcu: float = Field(0.0, ge=0, description="Total passenger car units")
    queue_m: float = Field(0.0, ge=0, description="Queue length in metres (contiguous definition)")
    queue_pcu: float = Field(0.0, ge=0, description="Queue in PCU (for Max-Pressure input)")
    avg_speed_kmh: float = Field(0.0, ge=0)
    arrival_flow_pcu_per_min: float = Field(0.0, ge=0)
    # P0-4 FIX: renamed from occupancy_ratio to time_occupancy_pct
    time_occupancy_pct: float = Field(
        0.0, ge=0, le=100,
        description="Fraction of time a detector point is occupied (%); "
                    "NOT the same as queue_fill_ratio. See improvements.md P0-4."
    )
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class PlateRead(BaseModel):
    """ANPR output for a vehicle involved in a violation."""
    text: Optional[str] = Field(None, description="Plate string, None if not read")
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class VisionEvent(BaseModel):
    """
    One violation or significant event detected in this frame.

    P0-13 FIX: Multiple events in the same frame are now properly handled
    via the `events[]` list in TelemetryMessage.
    """
    event_id: str = Field(
        default_factory=lambda: f"e-{uuid.uuid4().hex[:8]}",
        description="Unique ID for idempotent consumer handling"
    )
    type: str = Field(
        ...,
        description=(
            "Event type. Standard values: RED_LIGHT_VIOLATION, "
            "RED_LIGHT_VIOLATION_HIGH_RISK, STOP_LINE_ENCROACHMENT, YELLOW_ENTRY, "
            "BRTS_INTRUSION, BRTS_WRONG_WAY, BRTS_PARKING_STOP, BRTS_CUT_IN_AT_GAP, "
            "EMERGENCY_VEHICLE_REQUEST, LANE_DISCIPLINE_VIOLATION"
        )
    )
    track_id: Optional[int] = None
    vehicle_class: Optional[str] = None
    zone_id: Optional[str] = None
    approach: Optional[str] = None                  # for EMERGENCY_VEHICLE_REQUEST
    duration_s: Optional[float] = Field(None, ge=0)
    distance_inside_m: Optional[float] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    evidence_uri: Optional[str] = None             # object-storage path
    plate: Optional[PlateRead] = None
    # Extra type-specific fields
    extra: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Top-level telemetry message
# ---------------------------------------------------------------------------

class TelemetryMessage(BaseModel):
    """
    Telemetry contract v2.

    Every message from the vision-service must conform to this schema.
    Validated on ingestion by the backend — invalid messages are rejected
    and counted. `message_id` ensures idempotent consumer processing.
    """
    schema_version: Literal["2.0"] = Field("2.0")
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID for idempotent consumer handling — retries do not double-count"
    )
    seq: int = Field(..., ge=0, description="Monotonically increasing per-camera sequence number")
    junction_id: str = Field(..., description="Provisioned junction ID (no auto-creation — P0-10)")
    camera_id: str = Field(..., description="Camera identifier, e.g. 'J001-N-01'")
    capture_ts: str = Field(
        ...,
        description="ISO-8601 UTC timestamp of frame capture (NTP-synced on edge device)"
    )
    publish_ts: str = Field(
        ...,
        description="ISO-8601 UTC timestamp when message was published to broker"
    )
    model_version: str = Field(..., description="Detector model version string")
    calibration_version: str = Field(..., description="Camera calibration version string")

    health: HealthBlock
    observed_signal: Optional[ObservedSignal] = Field(
        None,
        description=(
            "Observed signal state — required for red-light violation detection. "
            "Prefer controller feed; vision is fallback."
        )
    )

    movements: list[Movement] = Field(
        default_factory=list,
        description="Per-movement metrics. Max-Pressure input. One entry per approach group."
    )

    # P0-13 FIX: events list (was: single brts_violation bool + single lane_intrusion object)
    events: list[VisionEvent] = Field(
        default_factory=list,
        description=(
            "Violation and significant events detected this frame. "
            "Multiple events per frame are supported (P0-13 fix). "
            "Each event has a unique event_id for idempotent consumer handling."
        )
    )

    @model_validator(mode="after")
    def validate_timestamps(self) -> "TelemetryMessage":
        """Capture timestamp must be before or equal to publish timestamp."""
        try:
            ct = datetime.fromisoformat(self.capture_ts.replace("Z", "+00:00"))
            pt = datetime.fromisoformat(self.publish_ts.replace("Z", "+00:00"))
            if ct > pt:
                raise ValueError(
                    f"capture_ts ({self.capture_ts}) is after publish_ts ({self.publish_ts})"
                )
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Timestamp validation failed: {exc}") from exc
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "schema_version": "2.0",
                "message_id": "b3f1c9e0-5d4a-4a6e-9a0f-2c1d7e8a1111",
                "seq": 184220,
                "junction_id": "J001",
                "camera_id": "J001-N-01",
                "capture_ts": "2026-10-08T20:18:00.120Z",
                "publish_ts": "2026-10-08T20:18:00.165Z",
                "model_version": "yolo26s-surat-2026.10.1",
                "calibration_version": "J001-N-01-v3",
                "health": {
                    "fps": 14.8,
                    "dropped_frames": 0,
                    "mean_confidence": 0.81,
                    "visibility_score": 0.9,
                },
                "observed_signal": {
                    "phase": "NS_THROUGH",
                    "state": "GREEN",
                    "elapsed_s": 17.4,
                    "source": "controller",
                },
                "movements": [
                    {
                        "movement_id": "N_through",
                        "lane_ids": ["J001-N-L1", "J001-N-L2"],
                        "vehicle_count": 14,
                        "pcu": 18.5,
                        "queue_m": 42.0,
                        "queue_pcu": 11.0,
                        "avg_speed_kmh": 18.2,
                        "arrival_flow_pcu_per_min": 21.0,
                        "time_occupancy_pct": 38.0,
                        "confidence": 0.84,
                    }
                ],
                "events": [
                    {
                        "event_id": "e-9912",
                        "type": "BRTS_INTRUSION",
                        "track_id": 402,
                        "vehicle_class": "car",
                        "zone_id": "J001-BRTS-1",
                        "duration_s": 4.2,
                        "confidence": 0.9,
                        "evidence_uri": "s3://evidence/J001/2026-10-08/e-9912/",
                        "plate": {"text": "GJ05XX1234", "confidence": 0.77},
                    },
                    {
                        "event_id": "e-9913",
                        "type": "EMERGENCY_VEHICLE_REQUEST",
                        "approach": "N",
                        "confidence": 0.88,
                        "extra": {"eta_s": 11.0, "evidence": ["vision"]},
                    },
                ],
            }
        }
