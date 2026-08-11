from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime
from app.db import get_db
from app.models import Junction, Lane, TrafficMetric, Violation
from app.event_bus import event_bus
from app.recommendations import run_recommendation_engine

router = APIRouter(
    prefix="/api/events",
    tags=["Ingest Events"]
)

@router.post("/")
async def ingest_vision_event(event: dict, db: Session = Depends(get_db)):
    """
    Ingests live junction event contract posted by Person A's YOLO Vision Service.
    Saves metrics and violations into DB and publishes live WebSocket updates.
    """
    junction_id = event.get("junction_id")
    if not junction_id:
        raise HTTPException(status_code=400, detail="Missing junction_id")

    junction = db.query(Junction).filter(Junction.id == junction_id).first()
    if not junction:
        # Create junction if not existing
        junction = Junction(
            id=junction_id,
            name=event.get("junction_name", f"Junction {junction_id}"),
            latitude=21.1702,
            longitude=72.8311,
            signal_mode="adaptive",
            current_phase="Phase 1: North-South Green"
        )
        db.add(junction)
        db.commit()

    lanes_data = event.get("lanes", [])
    total_vehicles = 0
    total_queue = 0.0

    for l_data in lanes_data:
        lane_id = l_data.get("lane_id")
        if not lane_id:
            continue

        lane = db.query(Lane).filter(Lane.id == lane_id).first()
        if not lane:
            lane = Lane(
                id=lane_id,
                junction_id=junction_id,
                lane_name=f"Lane {lane_id}",
                direction=lane_id.split("_")[-1] if "_" in lane_id else "N",
                is_brts="brts" in lane_id.lower()
            )
            db.add(lane)
            db.commit()

        v_count = l_data.get("vehicle_count", 0)
        q_len = l_data.get("queue_length_m", 0.0)
        avg_speed = l_data.get("avg_speed_kmph", 40.0)
        occupancy = min(1.0, q_len / 120.0)

        metric = TrafficMetric(
            lane_id=lane_id,
            timestamp=datetime.datetime.utcnow(),
            vehicle_count=v_count,
            queue_length_m=q_len,
            occupancy_ratio=occupancy,
            average_speed_kmh=avg_speed
        )
        db.add(metric)
        total_vehicles += v_count
        total_queue += q_len

    db.commit()

    # Handle BRTS Intrusions
    if event.get("brts_violation"):
        intrusion_data = event.get("lane_intrusion", {}) or {}
        vehicle_type = intrusion_data.get("vehicle_class", "car")
        
        # Pick BRTS lane
        brts_lane = db.query(Lane).filter(Lane.junction_id == junction_id, Lane.is_brts == True).first()
        lane_id = brts_lane.id if brts_lane else (lanes_data[0]["lane_id"] if lanes_data else "L001")

        violation = Violation(
            lane_id=lane_id,
            timestamp=datetime.datetime.utcnow(),
            violation_type="brts_intrusion",
            vehicle_type=vehicle_type,
            snapshot_url=f"/snapshots/vision_{vehicle_type}_{int(datetime.datetime.utcnow().timestamp())}.jpg"
        )
        db.add(violation)
        db.commit()

        await event_bus.publish("traffic_live_events", {
            "type": "new_violation",
            "id": violation.id,
            "lane_id": violation.lane_id,
            "timestamp": violation.timestamp.isoformat(),
            "violation_type": violation.violation_type,
            "vehicle_type": violation.vehicle_type,
            "snapshot_url": violation.snapshot_url,
            "junction_name": junction.name
        })

    # Trigger recommendation check
    await run_recommendation_engine(db, junction_id)

    # Publish WebSocket junction update
    avg_q = total_queue / len(lanes_data) if lanes_data else 0.0
    await event_bus.publish("traffic_live_events", {
        "type": "junction_update",
        "junction_id": junction_id,
        "name": junction.name,
        "latitude": junction.latitude,
        "longitude": junction.longitude,
        "signal_mode": junction.signal_mode,
        "current_phase": junction.current_phase,
        "cycle_length": junction.cycle_length,
        "total_vehicles": total_vehicles,
        "avg_queue_length_m": round(avg_q, 1),
        "lanes": lanes_data
    })

    return {"status": "success", "message": "Event processed successfully"}
