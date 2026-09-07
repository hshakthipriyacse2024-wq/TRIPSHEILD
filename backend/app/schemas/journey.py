from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NodeCreate(BaseModel):
    type: str
    provider: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    destination_location: Optional[str] = None
    dest_latitude: Optional[float] = None
    dest_longitude: Optional[float] = None
    start_time: datetime
    end_time: datetime
    cost: Optional[float] = None
    currency: str = 'INR'
    booking_reference: Optional[str] = None
    cancellation_policy: Dict[str, Any] = {}
    flexibility: Optional[str] = None
    importance: Optional[str] = None
    details: Dict[str, Any] = {}
    sequence_order: int = 0

class NodeUpdate(BaseModel):
    type: Optional[str] = None
    provider: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    cost: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class NodeResponse(NodeCreate):
    id: str
    journey_id: str
    status: str
    traveler_preference_weight: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DependencyCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str
    buffer_minutes: int = 60
    is_critical: bool = True

class DependencyResponse(DependencyCreate):
    id: str
    journey_id: str

    class Config:
        from_attributes = True

class JourneyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    origin: str
    destination: str
    start_date: datetime
    end_date: datetime

class JourneyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class JourneyResponse(JourneyCreate):
    id: str
    user_id: str
    status: str
    resilience_score: Optional[int]
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    nodes: List[NodeResponse] = []
    dependencies: List[DependencyResponse] = []

    class Config:
        from_attributes = True

class DigitalTwinResponse(BaseModel):
    journey: JourneyResponse
    nodes: List[NodeResponse]
    dependencies: List[DependencyResponse]
    resilience_score: Optional[int]
