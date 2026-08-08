from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


# Junction

class JunctionBase(BaseModel):
    junction_id: str
    junction_name: str
    latitude: float
    longitude: float
    city: str
    status: Optional[str] = "active"

class JunctionCreate(JunctionBase):
    pass

class JunctionResponse(JunctionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Lane

class LaneBase(BaseModel):
    junction_id: str
    lane_id: str
    direction: str
    lane_type: str
    is_brts: bool = False

class LaneCreate(LaneBase):
    pass

class LaneResponse(LaneBase):
    id: int

    class Config:
        from_attributes = True

# Lane Events

class LaneEventBase(BaseModel):
    junction_id: str
    lane_id: str

    vehicle_count: int

    pcu_weighted_count: float

    queue_length_m: float

    avg_speed_kmph: float

    vehicle_types: Dict[str, Any]

    detection_confidence: float

    lighting_condition: str

    timestamp: datetime

class LaneEventCreate(LaneEventBase):
    pass

class LaneEventResponse(LaneEventBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True

# BRTS Intrusion

class IntrusionBase(BaseModel):
    junction_id: str
    lane_id: str

    vehicle_type: str

    vehicle_number: Optional[str] = None

    confidence: float

    bus_approaching: bool = False

    intrusion_type: str

    image_url: Optional[str] = None

    video_url: Optional[str] = None

    resolved: bool = False

class IntrusionCreate(IntrusionBase):
    pass

class IntrusionResponse(IntrusionBase):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True

# Signal Status

class SignalBase(BaseModel):
    junction_id: str

    current_phase: str

    recommended_green_time: int

    actual_green_time: int

    traffic_density: float

class SignalCreate(SignalBase):
    pass

class SignalResponse(SignalBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True