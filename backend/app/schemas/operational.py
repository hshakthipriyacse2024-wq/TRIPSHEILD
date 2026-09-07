from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    journey_id: Optional[str]
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PreferenceUpdate(BaseModel):
    budget_priority: Optional[int] = None
    speed_priority: Optional[int] = None
    comfort_priority: Optional[int] = None
    minimal_changes_priority: Optional[int] = None

class PreferenceResponse(BaseModel):
    budget_priority: int
    speed_priority: int
    comfort_priority: int
    minimal_changes_priority: int
    preferred_airlines: List[str]
    preferred_transport: List[str]
    max_connections: int

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: str
    event_type: str
    description: Optional[str]
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    total_journeys: int
    total_disruptions: int
    total_recoveries: int
    money_saved: float
    time_saved_minutes: int
    avg_resilience_score: float

class GuardianChatRequest(BaseModel):
    message: str
    journey_id: Optional[str] = None

class GuardianChatResponse(BaseModel):
    response: str
    context_used: Dict[str, Any]
