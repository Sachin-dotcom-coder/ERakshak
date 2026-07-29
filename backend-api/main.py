from types import LambdaType
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from sqlalchemy.orm import Session
import database
from models import LaneEvent
from database import get_db

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


from datetime import datetime
from typing import Optional, Dict, Any

class LaneTraffic(BaseModel):
    junction_id: str
    lane_id: str
    vehicle_count: int
    pcu_weighted_count: float
    queue_length_m: float
    avg_speed_kmph: float
    vehicle_types: Dict[str, Any]
    detection_confidence: float
    brts_violation: Optional[bool] = False
    brts_bus_approaching: Optional[bool] = False
    lane_intrusion: Optional[str] = None
    stall_alert: Optional[str] = None
    lighting_condition: str
    timestamp: datetime

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/signal/{junction_id}/status")
def signal_status(junction_id: str):
    return {
        "junction_id": junction_id,
        "current_signal_phase": "green",
        "recommended_signal_time": 35,
    }

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/events/{junction_id}")
def get_junction_data(junction_id: str,db: Session = Depends(get_db)):
    events=(
        db.query(LaneEvent)
        .filter(LaneEvent.junction_id==junction_id)
        .order_by(LaneEvent.recorded_at.desc())
        .limit(1)
        .all()
    ) 
    return events

@app.get("/events_all")
def get_all_junction_data(db: Session = Depends(get_db)):
    events=(
        db.query(LaneEvent).order_by(LaneEvent.recorded_at.desc()).all()
    )
    return events

@app.post("/events/junction")
def post_junction_data(event: LaneTraffic, db: Session = Depends(get_db)):
    lane_event = LaneEvent(
        junction_id=event.junction_id,
        lane_id=event.lane_id,
        vehicle_count=event.vehicle_count,
        pcu_weighted_count=event.pcu_weighted_count,
        queue_length_m=event.queue_length_m,
        avg_speed_kmph=event.avg_speed_kmph,
        vehicle_types=event.vehicle_types,
        detection_confidence=event.detection_confidence,
        brts_violation=event.brts_violation,
        brts_bus_approaching=event.brts_bus_approaching,
        lane_intrusion=event.lane_intrusion,
        stall_alert=event.stall_alert,
        lighting_condition=event.lighting_condition,
        timestamp=event.timestamp,
    )
    db.add(lane_event)
    db.commit()
    db.refresh(lane_event)
    return {"status": "received", "junction_id": event.junction_id, "id": lane_event.id}

@app.put("/events/{event_id}")
def update_event(event_id: int, updated_data: LaneTraffic, db: Session = Depends(get_db)):
    lane_event = db.query(LaneEvent).filter(LaneEvent.id == event_id).first()
    if not lane_event:
        return {"error": "Event not found"}
    
    # Update fields
    lane_event.vehicle_count = updated_data.vehicle_count
    lane_event.pcu_weighted_count = updated_data.pcu_weighted_count
    lane_event.queue_length_m = updated_data.queue_length_m
    lane_event.avg_speed_kmph = updated_data.avg_speed_kmph
    lane_event.vehicle_types = updated_data.vehicle_types
    lane_event.detection_confidence = updated_data.detection_confidence
    lane_event.brts_violation = updated_data.brts_violation
    lane_event.brts_bus_approaching = updated_data.brts_bus_approaching
    lane_event.lane_intrusion = updated_data.lane_intrusion
    lane_event.stall_alert = updated_data.stall_alert
    lane_event.lighting_condition = updated_data.lighting_condition
    lane_event.timestamp = updated_data.timestamp
    
    db.commit()
    db.refresh(lane_event)
    return {"status": "updated", "junction_id": lane_event.junction_id, "id": lane_event.id}

@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    lane_event = db.query(LaneEvent).filter(LaneEvent.id == event_id).first()
    if not lane_event:
        return {"error": "Event not found"}
    
    db.delete(lane_event)
    db.commit()
    return {"status": "deleted", "id": event_id}

