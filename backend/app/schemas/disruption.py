from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DisruptionCreate(BaseModel):
    journey_id: str
    affected_node_id: str
    type: str
    description: Optional[str] = None
    delay_minutes: int = 0
    is_simulated: bool = True

class ImpactAnalysisResponse(BaseModel):
    id: str
    impact_score: Optional[int]
    severity_class: Optional[str]
    nodes_affected: int
    financial_exposure: float
    time_impact_minutes: int
    scoring_breakdown: Dict[str, Any]
    affected_nodes_detail: List[Dict[str, Any]]
    analyzed_at: datetime

    class Config:
        from_attributes = True

class DisruptionResponse(BaseModel):
    id: str
    journey_id: str
    affected_node_id: str
    type: str
    severity: Optional[str]
    description: Optional[str]
    delay_minutes: int
    is_simulated: bool
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime]
    impact_analysis: Optional[ImpactAnalysisResponse] = None
    journey_title: Optional[str] = None

    class Config:
        from_attributes = True

class SimulationRequest(BaseModel):
    disruption_type: str
    parameters: Dict[str, Any]

class SimulationResponse(BaseModel):
    id: str
    journey_id: str
    disruption_type: str
    impact_result: Dict[str, Any]
    recovery_options: List[Dict[str, Any]]
    resilience_score_before: Optional[int]
    resilience_score_after: Optional[int]

    class Config:
        from_attributes = True
