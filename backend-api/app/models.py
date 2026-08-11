import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db import Base

class Junction(Base):
    __tablename__ = "junctions"

    id = Column(String, primary_key=True, index=True)  # e.g., "J001"
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    signal_mode = Column(String, default="fixed")  # "fixed" or "adaptive"
    current_phase = Column(String, default="All Red")
    cycle_length = Column(Integer, default=120)

    lanes = relationship("Lane", back_populates="junction", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="junction", cascade="all, delete-orphan")


class Lane(Base):
    __tablename__ = "lanes"

    id = Column(String, primary_key=True, index=True)  # e.g., "J001_L_N"
    junction_id = Column(String, ForeignKey("junctions.id"), nullable=False)
    lane_name = Column(String, nullable=False)  # e.g., "Northbound Left"
    direction = Column(String, nullable=False)  # "N", "S", "E", "W"
    is_brts = Column(Boolean, default=False)
    polygon_coords = Column(JSON, nullable=True)  # List of [lat, lng] for rendering on map

    junction = relationship("Junction", back_populates="lanes")
    metrics = relationship("TrafficMetric", back_populates="lane", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="lane", cascade="all, delete-orphan")


class TrafficMetric(Base):
    __tablename__ = "traffic_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lane_id = Column(String, ForeignKey("lanes.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    vehicle_count = Column(Integer, default=0)
    queue_length_m = Column(Float, default=0.0)
    occupancy_ratio = Column(Float, default=0.0)  # 0.0 to 1.0
    average_speed_kmh = Column(Float, default=40.0)

    lane = relationship("Lane", back_populates="metrics")


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lane_id = Column(String, ForeignKey("lanes.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    violation_type = Column(String, nullable=False)  # "brts_intrusion" or "lane_discipline"
    vehicle_type = Column(String, nullable=False)  # "auto", "car", "bike", "truck"
    snapshot_url = Column(String, nullable=True)  # path or url to detection snapshot image

    lane = relationship("Lane", back_populates="violations")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    junction_id = Column(String, ForeignKey("junctions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    issue_type = Column(String, nullable=False)  # "brts_intrusion_heavy", "queue_spillback", "asymmetric_flow"
    severity = Column(String, nullable=False)  # "low", "medium", "high", "critical"
    description = Column(String, nullable=False)
    suggested_action = Column(String, nullable=False)
    status = Column(String, default="pending")  # "pending", "applied", "dismissed"

    junction = relationship("Junction", back_populates="recommendations")
