"""
event_publisher.py — Event Contract Builder & Publisher
========================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Builds and publishes the JSON event contract (Section 7 of the brief)
that Persons B, C, and D all consume. This is the interface boundary —
the exact shape must not change without team discussion.

Two publisher backends:
- MockPublisher: writes JSON to stdout + rotated JSONL file (for local dev/testing)
- KafkaPublisher: publishes to a Kafka topic (for integration with Person C's backend)

The event contract shape:
{
  "junction_id": "junction_01",
  "timestamp": "2026-07-08T10:15:32Z",
  "lighting_condition": "day",
  "lanes": [...],
  "brts_violation": false,
  "brts_bus_approaching": true,
  "lane_intrusion": {...} | null,
  "stall_alert": {...} | null
}

Usage:
    from event_publisher import create_publisher, build_junction_event
    publisher = create_publisher(config["publisher"])
    event = build_junction_event(junction_id, timestamp, lane_data, violations, incidents)
    publisher.publish(event)
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from zones.zone_utils import LaneOccupancy

logger = logging.getLogger(__name__)


# ─── Event Building ──────────────────────────────────────────────────

def build_junction_event(
    junction_id: str,
    timestamp: str,
    lighting_condition: str,
    lane_occupancies: dict[str, LaneOccupancy],
    queue_lengths: dict[str, Optional[float]],
    avg_speeds: dict[str, Optional[float]],
    brts_intrusions: list,
    lane_violations: list,
    stall_alerts: list,
    brts_bus_approaching: bool = False,
) -> dict[str, Any]:
    """Build the exact JSON event contract from Section 7.

    This function is the single source of truth for the event shape.
    Every field is documented; nothing is faked or hardcoded.

    Args:
        junction_id: Junction identifier (e.g., "junction_01").
        timestamp: ISO-8601 timestamp string.
        lighting_condition: "day", "dusk", or "night" (from preprocessing).
        lane_occupancies: Per-lane LaneOccupancy objects from ZoneManager.
        queue_lengths: Per-lane queue length in meters (from CameraCalibrator).
        avg_speeds: Per-lane average speed in km/h.
        brts_intrusions: List of BRTSIntrusion objects from ViolationDetector.
        lane_violations: List of LaneViolation objects from ViolationDetector.
        stall_alerts: List of StallAlert objects from IncidentDetector.
        brts_bus_approaching: Whether a BRTS bus is currently detected
                               approaching the junction.

    Returns:
        Dict matching the exact contract shape from Section 7.
    """
    # Build per-lane data
    lanes_data = []
    for lane_id, occ in lane_occupancies.items():
        has_vehicles = occ.vehicle_count > 0
        lane_entry = {
            "lane_id": lane_id,
            "vehicle_count": occ.vehicle_count,
            "pcu_weighted_count": round(occ.pcu_weighted_count, 1) if has_vehicles else 0.0,
            "queue_length_m": (
                round(queue_lengths.get(lane_id, 0.0) or 0.0, 1) if has_vehicles else 0.0
            ),
            "avg_speed_kmph": (
                round(avg_speeds.get(lane_id, 0.0) or 0.0, 1) if has_vehicles else 0.0
            ),
            "vehicle_types": occ.vehicle_types if has_vehicles else {},
            "detection_confidence": round(occ.avg_confidence, 2) if has_vehicles else 0.0,
        }
        lanes_data.append(lane_entry)

    # Build lane_intrusion sub-schema (most recent violation, or null)
    lane_intrusion_data = None
    if lane_violations:
        lv = lane_violations[-1]  # Most recent
        lane_intrusion_data = {
            "track_id": lv.track_id,
            "vehicle_class": lv.vehicle_class,
            "from_lane": lv.from_lane,
            "to_lane": lv.to_lane,
            "dwell_time_s": lv.dwell_time_s,
            "timestamp": lv.timestamp,
        }

    # Build stall_alert sub-schema (most recent alert, or null)
    stall_alert_data = None
    if stall_alerts:
        sa = stall_alerts[-1]  # Most recent
        stall_alert_data = {
            "track_id": sa.track_id,
            "vehicle_class": sa.vehicle_class,
            "lane_id": sa.lane_id,
            "location_m": list(sa.location_m) if sa.location_m else None,
            "stall_duration_s": sa.stall_duration_s,
            "confidence": sa.confidence,
            "timestamp": sa.timestamp,
        }

    event = {
        "junction_id": junction_id,
        "timestamp": timestamp,
        "lighting_condition": lighting_condition,
        "lanes": lanes_data,
        "brts_violation": len(brts_intrusions) > 0,
        "brts_bus_approaching": brts_bus_approaching,
        "lane_intrusion": lane_intrusion_data,
        "stall_alert": stall_alert_data,
    }

    return event


# ─── Publisher Backends ──────────────────────────────────────────────

class EventPublisher(ABC):
    """Abstract base for event publishers."""

    @abstractmethod
    def publish(self, event: dict[str, Any]) -> None:
        """Publish a single junction event."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Clean up resources (close files, disconnect, etc.)."""
        ...


class MockPublisher(EventPublisher):
    """Writes events to stdout and a JSONL file for local testing.

    Person C can write a trivial consumer that reads the JSONL file
    to sanity-check the event stream without running the full pipeline.

    Args:
        config: Dict from config.yaml under 'publisher.mock'.
    """

    def __init__(self, config: dict) -> None:
        self._pretty = config.get("pretty_print", True)
        output_file = config.get("output_file", "output/events.jsonl")

        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._output_path = output_path
        self._file = open(output_path, "a", encoding="utf-8")
        self._event_count = 0

        logger.info(f"MockPublisher writing to: {output_path}")

    def publish(self, event: dict[str, Any]) -> None:
        """Write event as JSON to file and optionally to stdout."""
        try:
            # Always write compact JSON to file (one line per event)
            json_line = json.dumps(event, ensure_ascii=False)
            self._file.write(json_line + "\n")
            self._file.flush()

            self._event_count += 1

            # Pretty-print to stdout periodically (not every frame — too noisy)
            if self._pretty and self._event_count % 10 == 1:
                pretty = json.dumps(event, indent=2, ensure_ascii=False)
                print(f"\n{'='*60}")
                print(f"EVENT #{self._event_count}:")
                print(pretty)
                print(f"{'='*60}")

        except Exception as e:
            logger.error(f"MockPublisher failed to write event: {e}")

    def close(self) -> None:
        """Close the output file."""
        if self._file and not self._file.closed:
            self._file.close()
            logger.info(
                f"MockPublisher closed — {self._event_count} events written "
                f"to {self._output_path}"
            )


class KafkaPublisher(EventPublisher):
    """Publishes events to a Kafka topic for integration with Person C's backend.

    Args:
        config: Dict from config.yaml under 'publisher.kafka'.
    """

    def __init__(self, config: dict) -> None:
        self._broker = config.get("broker", "localhost:9092")
        self._topic = config.get("topic", "vision_events")
        self._producer = None

        try:
            from kafka import KafkaProducer

            self._producer = KafkaProducer(
                bootstrap_servers=self._broker,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=3,
            )
            logger.info(f"KafkaPublisher connected to {self._broker}, topic: {self._topic}")

        except ImportError:
            logger.error(
                "kafka-python not installed. Install with: pip install kafka-python\n"
                "Or switch to 'mock' mode in config.yaml → publisher.mode"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Kafka broker at {self._broker}: {e}")

    def publish(self, event: dict[str, Any]) -> None:
        """Publish event to Kafka topic."""
        if self._producer is None:
            logger.warning("Kafka producer not available — event dropped")
            return

        try:
            self._producer.send(self._topic, value=event)
        except Exception as e:
            logger.error(f"Kafka publish failed: {e}")

    def close(self) -> None:
        """Flush and close the Kafka producer."""
        if self._producer is not None:
            try:
                self._producer.flush()
                self._producer.close()
                logger.info("KafkaPublisher closed")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")


class HTTPRestPublisher(EventPublisher):
    """Publishes events via HTTP POST to the backend REST ingestion endpoint."""

    def __init__(self, config: dict) -> None:
        self._url = config.get("url", "http://localhost:8000/api/events/")
        logger.info(f"HTTPRestPublisher initialized for endpoint: {self._url}")

    def publish(self, event: dict[str, Any]) -> None:
        try:
            import urllib.request
            data = json.dumps(event).encode("utf-8")
            req = urllib.request.Request(self._url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
            
            lanes = event.get("lanes", [])
            total_v = sum(l.get("vehicle_count", 0) for l in lanes)
            has_brts_violation = event.get("brts_violation", False)
            logger.info(
                f"[VISION PIPELINE -> BACKEND] Published Event for {event.get('junction_id')} "
                f"| Vehicles Detected: {total_v} | BRTS Intrusion: {has_brts_violation}"
            )
        except Exception as e:
            logger.error(f"HTTPRestPublisher failed to POST event to {self._url}: {e}")

    def close(self) -> None:
        logger.info("HTTPRestPublisher closed")


# ─── Factory ─────────────────────────────────────────────────────────

def create_publisher(config: dict) -> EventPublisher:
    """Create the appropriate publisher based on config.

    Args:
        config: Dict from config.yaml under 'publisher' key.

    Returns:
        EventPublisher instance (MockPublisher, KafkaPublisher, or HTTPRestPublisher).
    """
    mode = config.get("mode", "http")

    if mode == "kafka":
        return KafkaPublisher(config.get("kafka", {}))
    elif mode == "http" or mode == "rest":
        return HTTPRestPublisher(config.get("http", {}))
    else:
        return MockPublisher(config.get("mock", {}))

