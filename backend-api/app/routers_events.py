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

    # Map vision service default junction IDs to seeded Surat DB IDs
    id_mapping = {"junction_01": "J001", "junction_02": "J002"}
    db_junction_id = id_mapping.get(junction_id, junction_id)

    junction = db.query(Junction).filter(Junction.id == db_junction_id).first()
    if not junction:
        junction = Junction(
            id=db_junction_id,
            name=event.get("junction_name", f"Junction {db_junction_id}"),
            latitude=21.1825,
            longitude=72.8210,
            signal_mode="adaptive",
            current_phase="Phase 1: North-South Green"
        )
        db.add(junction)
        db.commit()
    
    junction_id = db_junction_id

    lanes_data = event.get("lanes", [])
    total_vehicles = 0
    total_queue = 0.0

    # Map vision service generic lane IDs to DB lane IDs for J001/J002
    lane_map = {"lane_1": f"{junction_id}_L1", "lane_2": f"{junction_id}_L2", "lane_3": f"{junction_id}_L3", "lane_4": f"{junction_id}_L4"}
    if junction_id == "J001":
        lane_map = {"lane_1": "L001", "lane_2": "L002", "lane_3": "L003", "lane_4": "L004"}

    try:
        for l_data in lanes_data:
            raw_lane_id = l_data.get("lane_id", "lane_1")
            lane_id = lane_map.get(raw_lane_id, raw_lane_id)

            lane = db.query(Lane).filter(Lane.id == lane_id).first()
            if not lane:
                lane = Lane(
                    id=lane_id,
                    junction_id=junction_id,
                    lane_name=f"Lane {raw_lane_id}",
                    direction=raw_lane_id.split("_")[-1] if "_" in raw_lane_id else "N",
                    is_brts="brts" in raw_lane_id.lower()
                )
                db.add(lane)
                db.commit()

            v_count = l_data.get("vehicle_count", 0)
            q_len = l_data.get("queue_length_m", 0.0)
            avg_speed = l_data.get("avg_speed_kmph", 24.5)
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
            viol_lane_id = brts_lane.id if brts_lane else "L004"

            violation = Violation(
                lane_id=viol_lane_id,
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
        try:
            await run_recommendation_engine(db, junction_id)
        except Exception as rec_err:
            print(f"Recommendation check error: {rec_err}")

    except Exception as e:
        db.rollback()
        print(f"Error processing vision event: {e}")

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
