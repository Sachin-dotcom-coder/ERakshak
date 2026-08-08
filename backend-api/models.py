from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, BigInteger, ForeignKey, Text
from datetime import datetime
from database import Base

class Junction(Base):
    __tablename__ = "junctions"

    id = Column(BigInteger, primary_key=True, index=True)
    junction_id = Column(String, unique=True, nullable=False, index=True)
    junction_name = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class Lane(Base):
    __tablename__ = "lanes"

    id = Column(BigInteger, primary_key=True, index=True)
    junction_id = Column(
        String,
        ForeignKey("junctions.junction_id"),
        nullable=False,
    )
    lane_id = Column(String, unique=True, nullable=False)
    direction = Column(String)
    lane_type = Column(String)
    is_brts = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LaneEvent(Base):
    __tablename__ = "lane_events"

    id = Column(BigInteger, primary_key=True, index=True)

    junction_id = Column(
        String,
        ForeignKey("junctions.junction_id"),
        nullable=False,
        index=True,
    )

    lane_id = Column(
        String,
        ForeignKey("lanes.lane_id"),
        nullable=False,
    )

    vehicle_count = Column(Integer)

    pcu_weighted_count = Column(Float)

    queue_length_m = Column(Float)

    avg_speed_kmph = Column(Float)

    vehicle_types = Column(JSON)

    detection_confidence = Column(Float)

    lighting_condition = Column(String)

    recorded_at = Column(DateTime, default=datetime.utcnow)

    timestamp = Column(DateTime)

class BRTSIntrusion(Base):
    __tablename__ = "brts_intrusions"

    id = Column(BigInteger, primary_key=True, index=True)

    junction_id = Column(
        String,
        ForeignKey("junctions.junction_id"),
        nullable=False,
    )

    lane_id = Column(
        String,
        ForeignKey("lanes.lane_id"),
        nullable=False,
    )

    vehicle_type = Column(String)

    vehicle_number = Column(String, nullable=True)

    confidence = Column(Float)

    bus_approaching = Column(Boolean, default=False)

    intrusion_type = Column(String)

    image_url = Column(Text, nullable=True)

    video_url = Column(Text, nullable=True)

    resolved = Column(Boolean, default=False)

    recorded_at = Column(DateTime, default=datetime.utcnow)

class SignalStatus(Base):
    __tablename__ = "signal_status"

    id = Column(BigInteger, primary_key=True, index=True)

    junction_id = Column(
        String,
        ForeignKey("junctions.junction_id"),
        unique=True,
        nullable=False,
    )

    current_phase = Column(String)

    recommended_green_time = Column(Integer)

    actual_green_time = Column(Integer)

    traffic_density = Column(Float)

    updated_at = Column(DateTime, default=datetime.utcnow) 
