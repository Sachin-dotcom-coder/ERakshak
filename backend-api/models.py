from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON
from datetime import datetime
from database import Base

class LaneEvent(Base):
    __tablename__ = "lane_events"

    id = Column(Integer, primary_key=True, index=True)
    junction_id = Column(String, index=True)
    lane_id = Column(String)
    vehicle_count = Column(Integer)
    pcu_weighted_count = Column(Float)
    queue_length_m = Column(Float)
    avg_speed_kmph = Column(Float)
    vehicle_types = Column(JSON)  
    detection_confidence = Column(Float)
    brts_violation = Column(Boolean, default=False)
    brts_bus_approaching = Column(Boolean, default=False)
    lane_intrusion = Column(String, nullable=True)
    stall_alert = Column(String, nullable=True)
    lighting_condition = Column(String)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    timestamp = Column(DateTime)  
