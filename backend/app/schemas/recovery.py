from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class RecoveryActionResponse(BaseModel):
    id: str
    strategy_id: str
    original_node_id: Optional[str]
    replacement_node_id: Optional[str]
    action_type: str
    description: Optional[str]
    old_details: Dict[str, Any]
    new_details: Dict[str, Any]
    cost_difference: float
    status: str

    class Config:
        from_attributes = True

class RecoveryStrategyResponse(BaseModel):
    id: str
    disruption_id: str
    journey_id: str
    title: str
    description: Optional[str]
    changed_components: List[str]
    preserved_components: List[str]
    additional_cost: float
    currency: str
    time_saved_minutes: int
    num_changes: int
    feasibility_score: float
    comfort_score: float
    urgency_score: float
    financial_impact_score: float
    recovery_confidence: float
    overall_score: float
    explanation: Optional[str]
    is_recommended: bool
    rank: Optional[int]
    status: str
    actions: List[RecoveryActionResponse] = []

    class Config:
        from_attributes = True

class RecoveryApproveRequest(BaseModel):
    strategy_id: str

class RecoveryComparisonResponse(BaseModel):
    strategies: List[RecoveryStrategyResponse]
