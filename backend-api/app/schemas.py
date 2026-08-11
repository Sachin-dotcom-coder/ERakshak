from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Any

# Lane Schemas
class LaneBase(BaseModel):
    id: str
    lane_name: str
    direction: str
    is_brts: bool
    polygon_coords: Optional[List[List[float]]] = None

class LaneCreate(LaneBase):
    junction_id: str

class Lane(LaneBase):
    model_config = ConfigDict(from_attributes=True)
    junction_id: str

# Junction Schemas
class JunctionBase(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    signal_mode: str
    current_phase: str
    cycle_length: int

class JunctionCreate(JunctionBase):
    pass

class Junction(JunctionBase):
    model_config = ConfigDict(from_attributes=True)
    lanes: List[Lane] = []

# TrafficMetric Schemas
class TrafficMetricBase(BaseModel):
    lane_id: str
    vehicle_count: int
    queue_length_m: float
    occupancy_ratio: float
    average_speed_kmh: float

class TrafficMetricCreate(TrafficMetricBase):
    pass

class TrafficMetric(TrafficMetricBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime

# Violation Schemas
class ViolationBase(BaseModel):
    lane_id: str
    violation_type: str
    vehicle_type: str
    snapshot_url: Optional[str] = None

class ViolationCreate(ViolationBase):
    pass

class Violation(ViolationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
    lane: Optional[LaneBase] = None

# Recommendation Schemas
class RecommendationBase(BaseModel):
    junction_id: str
    issue_type: str
    severity: str
    description: str
    suggested_action: str
    status: str = "pending"

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime

# Live dashboard update format (WebSocket / Live API)
class LiveJunctionState(BaseModel):
    junction_id: str
    name: str
    latitude: float
    longitude: float
    signal_mode: str
    current_phase: str
    cycle_length: int
    total_vehicles: int
    avg_queue_length_m: float
    brts_intrusion_count: int
    lanes: List[Any] = []

# Compare Fixed vs Adaptive simulation schema
class PerformanceComparison(BaseModel):
    junction_id: str
    simulation_step: int
    fixed_avg_wait_time_sec: float
    adaptive_avg_wait_time_sec: float
    fixed_throughput_veh: int
    adaptive_throughput_veh: int
