"""
event_publisher.py — Event Contract Builder & Publisher (Upgraded Section 69-70)
==============================================================================
ERH26_PS_08: Data-Driven Traffic Optimization

Builds and publishes the JSON event contracts:
- Real-time aggregate telemetry (Section 69 of instruction.md)
- Optional object-level debug telemetry (Section 70 of instruction.md)

Preserves backward compatibility with legacy consumers (Section 7 of original brief)
while providing the complete extended schema with scene, camera health, and per-lane
confidence + movement breakdowns.

Two publisher backends:
- MockPublisher: writes JSON to stdout + rotated JSONL file (for local dev/testing)
- KafkaPublisher: publishes to Kafka topics (aggregate + optional object telemetry)
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ─── Aggregate Event Building (Section 69) ──────────────────────────────

def build_junction_event(
    junction_id: str,
    timestamp: str,
    lighting_condition: str = "day",
    lane_occupancies: Optional[dict[str, Any]] = None,
    queue_lengths: Optional[dict[str, Optional[float]]] = None,
    avg_speeds: Optional[dict[str, Optional[float]]] = None,
    brts_intrusions: Optional[list] = None,
    lane_violations: Optional[list] = None,
    stall_alerts: Optional[list] = None,
    brts_bus_approaching: bool = False,
    scene: Optional[dict[str, Any]] = None,
    camera: Optional[dict[str, Any]] = None,
    emergency_alerts: Optional[list] = None,
    wrong_way_alerts: Optional[list] = None,
    lane_details: Optional[dict[str, dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Build the JSON event contract with Section 69 extensions.

    Backward-compatible: Existing fields (vehicle_count, pcu_weighted_count,
    queue_length_m, avg_speed_kmph, vehicle_types, detection_confidence,
    brts_violation, brts_bus_approaching, lane_intrusion, stall_alert) are always present.

    Extended fields (Section 69):
    - "scene": {lighting, weather, visibility, scene_confidence}
    - "camera": {health, blur_score, camera_motion, calibration_valid, homography_health}
    - per-lane: {pcu, pcu_confidence, queue_confidence, queue_growth_rate,
                 queue_acceleration, speed_confidence, occlusion_ratio,
                 movement_counts, vehicle_count_confidence}
    - "emergency_vehicle": {...} | null
    - "wrong_way": {...} | null

    Args:
        junction_id: Junction identifier (e.g. "junction_01").
        timestamp: ISO-8601 timestamp string.
        lighting_condition: "day", "dusk", or "night".
        lane_occupancies: Per-lane LaneOccupancy objects or dicts.
        queue_lengths: Per-lane queue lengths in meters.
        avg_speeds: Per-lane average speeds in km/h.
        brts_intrusions: List of BRTS intrusion events.
        lane_violations: List of lane violations.
        stall_alerts: List of stall/breakdown alerts.
        brts_bus_approaching: Whether a BRTS bus is approaching.
        scene: Scene status dict (lighting, weather, visibility, scene_confidence).
        camera: Camera status dict (health, blur_score, camera_motion, calibration_valid, homography_health).
        emergency_alerts: List of active emergency vehicle events.
        wrong_way_alerts: List of active wrong-way vehicle events.
        lane_details: Extra lane metrics (growth rate, acceleration, movement counts, confidence).

    Returns:
        Telemetry dictionary conforming to Section 69 and legacy contract.
    """
    lane_occupancies = lane_occupancies or {}
    queue_lengths = queue_lengths or {}
    avg_speeds = avg_speeds or {}
    brts_intrusions = brts_intrusions or []
    lane_violations = lane_violations or []
    stall_alerts = stall_alerts or []
    emergency_alerts = emergency_alerts or []
    wrong_way_alerts = wrong_way_alerts or []
    lane_details = lane_details or {}

    # Build per-lane data
    lanes_data = []
    # Collect all known lane IDs
    all_lane_ids = set(lane_occupancies.keys()) | set(queue_lengths.keys()) | set(avg_speeds.keys()) | set(lane_details.keys())

    for lane_id in sorted(all_lane_ids):
        occ = lane_occupancies.get(lane_id)
        details = lane_details.get(lane_id, {})

        if occ is not None:
            if hasattr(occ, "vehicle_count"):
                vehicle_count = occ.vehicle_count
                pcu = getattr(occ, "pcu_weighted_count", float(vehicle_count))
                vehicle_types = getattr(occ, "vehicle_types", {})
                det_conf = getattr(occ, "avg_confidence", 0.85)
            elif isinstance(occ, dict):
                vehicle_count = occ.get("vehicle_count", 0)
                pcu = occ.get("pcu_weighted_count", occ.get("pcu", float(vehicle_count)))
                vehicle_types = occ.get("vehicle_types", {})
                det_conf = occ.get("detection_confidence", 0.85)
            else:
                vehicle_count = 0
                pcu = 0.0
                vehicle_types = {}
                det_conf = 0.0
        else:
            vehicle_count = details.get("vehicle_count", 0)
            pcu = details.get("pcu", float(vehicle_count))
            vehicle_types = details.get("vehicle_types", {})
            det_conf = details.get("vehicle_count_confidence", 0.85)

        has_vehicles = vehicle_count > 0

        q_len = details.get("queue_length_m", queue_lengths.get(lane_id, 0.0) or 0.0)
        speed = details.get("avg_speed_kmph", avg_speeds.get(lane_id, 0.0) or 0.0)

        lane_entry = {
            "lane_id": lane_id,
            "vehicle_count": int(vehicle_count),
            "vehicle_count_confidence": round(details.get("vehicle_count_confidence", det_conf if has_vehicles else 0.95), 2),
            "pcu": round(float(pcu), 1),
            "pcu_weighted_count": round(float(pcu), 1),  # Legacy compatibility
            "pcu_confidence": round(details.get("pcu_confidence", 0.90 if has_vehicles else 0.95), 2),
            "queue_length_m": round(float(q_len), 1),
            "queue_length": round(float(q_len), 1),       # Legacy compatibility
            "queue_confidence": round(details.get("queue_confidence", 0.88), 2),
            "queue_growth_rate": round(details.get("queue_growth_rate", 0.0), 3),
            "queue_acceleration": round(details.get("queue_acceleration", 0.0), 3),
            "avg_speed_kmph": round(float(speed), 1),
            "speed_confidence": round(details.get("speed_confidence", 0.85), 2),
            "occlusion_ratio": round(details.get("occlusion_ratio", 0.0), 2),
            "movement_counts": details.get("movement_counts", {"straight": int(vehicle_count), "left": 0, "right": 0}),
            "vehicle_types": vehicle_types if has_vehicles else {},
            "detection_confidence": round(float(det_conf), 2) if has_vehicles else 0.0,
        }
        lanes_data.append(lane_entry)

    # Build lane_intrusion sub-schema
    lane_intrusion_data = None
    if lane_violations:
        lv = lane_violations[-1]
        if hasattr(lv, "track_id"):
            lane_intrusion_data = {
                "track_id": lv.track_id,
                "vehicle_class": getattr(lv, "vehicle_class", "unknown"),
                "from_lane": getattr(lv, "from_lane", ""),
                "to_lane": getattr(lv, "to_lane", ""),
                "dwell_time_s": getattr(lv, "dwell_time_s", 0.0),
                "timestamp": getattr(lv, "timestamp", timestamp),
            }
        elif isinstance(lv, dict):
            lane_intrusion_data = lv

    # Build stall_alert sub-schema
    stall_alert_data = None
    if stall_alerts:
        sa = stall_alerts[-1]
        if hasattr(sa, "track_id"):
            loc = getattr(sa, "location_m", None)
            stall_alert_data = {
                "track_id": sa.track_id,
                "vehicle_class": getattr(sa, "vehicle_class", "unknown"),
                "lane_id": getattr(sa, "lane_id", None),
                "location_m": list(loc) if loc else None,
                "stall_duration_s": getattr(sa, "stall_duration_s", 0.0),
                "confidence": getattr(sa, "confidence", 0.8),
                "timestamp": getattr(sa, "timestamp", timestamp),
            }
        elif isinstance(sa, dict):
            stall_alert_data = sa

    # Build emergency_vehicle sub-schema
    emergency_vehicle_data = None
    if emergency_alerts:
        ea = emergency_alerts[-1]
        if hasattr(ea, "track_id"):
            emergency_vehicle_data = {
                "track_id": ea.track_id,
                "vehicle_class": getattr(ea, "class_name", "ambulance"),
                "lane_id": getattr(ea, "lane_id", None),
                "confidence": getattr(ea, "emergency_confidence", 0.9),
                "state": getattr(ea, "state", "CONFIRMED"),
                "distance_to_stopline_m": getattr(ea, "distance_to_stopline_m", 0.0),
                "preemption_requested": getattr(ea, "preemption_requested", False),
            }
        elif isinstance(ea, dict):
            emergency_vehicle_data = ea

    # Build wrong_way sub-schema
    wrong_way_data = None
    if wrong_way_alerts:
        ww = wrong_way_alerts[-1]
        if hasattr(ww, "track_id"):
            wrong_way_data = {
                "track_id": ww.track_id,
                "vehicle_class": getattr(ww, "class_name", "unknown"),
                "lane_id": getattr(ww, "lane_id", None),
                "heading_deg": getattr(ww, "heading_deg", 0.0),
                "confidence": getattr(ww, "confidence", 0.85),
            }
        elif isinstance(ww, dict):
            wrong_way_data = ww

    # Default scene structure if not provided
    scene_data = scene or {
        "lighting": lighting_condition,
        "weather": "clear",
        "visibility": 1.0,
        "scene_confidence": 0.90,
    }

    # Default camera structure if not provided
    camera_data = camera or {
        "health": 1.0,
        "blur_score": 0.1,
        "camera_motion": 0.0,
        "calibration_valid": True,
        "homography_health": 1.0,
    }

    event = {
        "junction_id": junction_id,
        "timestamp": timestamp,
        "lighting_condition": lighting_condition,
        "scene": scene_data,
        "camera": camera_data,
        "lanes": lanes_data,
        "brts_violation": len(brts_intrusions) > 0,
        "brts_bus_approaching": brts_bus_approaching,
        "lane_intrusion": lane_intrusion_data,
        "stall_alert": stall_alert_data,
        "emergency_vehicle": emergency_vehicle_data,
        "wrong_way": wrong_way_data,
    }

    return event


# ─── Object-Level Telemetry (Section 70) ────────────────────────────────

def build_object_telemetry(vehicle_states: list[Any]) -> list[dict[str, Any]]:
    """Build object-level telemetry for debugging and research (Section 70).

    Args:
        vehicle_states: List of VehicleState objects or dicts.

    Returns:
        List of per-vehicle telemetry dictionaries.
    """
    telemetry_list = []
    for vs in vehicle_states:
        if hasattr(vs, "track_id"):
            bbox = vs.bbox
            bbox_list = [int(x) for x in bbox] if bbox is not None and len(bbox) >= 4 else []
            entry = {
                "track_id": int(vs.track_id),
                "class": vs.class_name,
                "bbox": bbox_list,
                "world_position": [round(float(vs.world_x), 2), round(float(vs.world_y), 2)],
                "speed_kmph": round(float(vs.speed_kmph), 1),
                "heading_deg": round(float(vs.heading_deg), 1),
                "lane_id": vs.lane_id,
                "maneuver": vs.maneuver,
                "queue_probability": round(float(vs.queue_probability), 2),
                "occlusion_ratio": round(float(vs.occlusion_ratio), 2),
                "track_confidence": round(float(getattr(vs, "track_confidence", vs.detection_confidence)), 2),
            }
        elif isinstance(vs, dict):
            entry = vs
        else:
            continue
        telemetry_list.append(entry)

    return telemetry_list


# ─── Publisher Backends ──────────────────────────────────────────────

class EventPublisher(ABC):
    """Abstract base for event publishers."""

    @abstractmethod
    def publish(self, event: dict[str, Any]) -> None:
        """Publish a single junction event."""
        ...

    def publish_objects(self, objects: list[dict[str, Any]]) -> None:
        """Optional publish for object-level telemetry."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Clean up resources (close files, disconnect, etc.)."""
        ...


class MockPublisher(EventPublisher):
    """Writes events to stdout and a JSONL file for local testing."""

    def __init__(self, config: dict) -> None:
        self._pretty = config.get("pretty_print", True)
        output_file = config.get("output_file", "output/events.jsonl")
        self._obj_file_path = config.get("object_output_file", "output/objects.jsonl")

        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._output_path = output_path
        self._file = open(output_path, "a", encoding="utf-8")
        self._obj_file = None
        self._event_count = 0

        logger.info(f"MockPublisher writing to: {output_path}")

    def publish(self, event: dict[str, Any]) -> None:
        """Write event as JSON to file and optionally to stdout."""
        try:
            json_line = json.dumps(event, ensure_ascii=False)
            self._file.write(json_line + "\n")
            self._file.flush()

            self._event_count += 1

            if self._pretty and self._event_count % 10 == 1:
                pretty = json.dumps(event, indent=2, ensure_ascii=False)
                print(f"\n{'='*60}")
                print(f"EVENT #{self._event_count}:")
                print(pretty)
                print(f"{'='*60}")

        except Exception as e:
            logger.error(f"MockPublisher failed to write event: {e}")

    def publish_objects(self, objects: list[dict[str, Any]]) -> None:
        """Write object telemetry to separate JSONL file."""
        if not objects:
            return
        try:
            if self._obj_file is None:
                p = Path(self._obj_file_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                self._obj_file = open(p, "a", encoding="utf-8")

            line = json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "vehicles": objects}, ensure_ascii=False)
            self._obj_file.write(line + "\n")
            self._obj_file.flush()
        except Exception as e:
            logger.debug(f"MockPublisher failed to write object telemetry: {e}")

    def close(self) -> None:
        """Close output files."""
        if self._file and not self._file.closed:
            self._file.close()
            logger.info(
                f"MockPublisher closed — {self._event_count} events written "
                f"to {self._output_path}"
            )
        if self._obj_file and not self._obj_file.closed:
            self._obj_file.close()


class KafkaPublisher(EventPublisher):
    """Publishes events to Kafka topics for integration."""

    def __init__(self, config: dict) -> None:
        self._broker = config.get("broker", "localhost:9092")
        self._topic = config.get("topic", "vision_events")
        self._obj_topic = config.get("object_topic", "vision_objects")
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
            logger.warning(
                "kafka-python not installed. Falling back to mock-like behavior or switch to 'mock' mode."
            )
        except Exception as e:
            logger.error(f"Failed to connect to Kafka broker at {self._broker}: {e}")

    def publish(self, event: dict[str, Any]) -> None:
        """Publish event to Kafka topic."""
        if self._producer is None:
            return

        try:
            self._producer.send(self._topic, value=event)
        except Exception as e:
            logger.error(f"Kafka publish failed: {e}")

    def publish_objects(self, objects: list[dict[str, Any]]) -> None:
        """Publish object telemetry to Kafka object topic."""
        if self._producer is None or not objects:
            return

        try:
            self._producer.send(self._obj_topic, value=objects)
        except Exception as e:
            logger.debug(f"Kafka object publish failed: {e}")

    def close(self) -> None:
        """Flush and close the Kafka producer."""
        if self._producer is not None:
            try:
                self._producer.flush()
                self._producer.close()
                logger.info("KafkaPublisher closed")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")


# ─── Factory ─────────────────────────────────────────────────────────

def create_publisher(config: dict) -> EventPublisher:
    """Create publisher based on config."""
    mode = config.get("mode", "mock")
    if mode == "kafka":
        return KafkaPublisher(config.get("kafka", {}))
    return MockPublisher(config.get("mock", {}))
