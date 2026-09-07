"""Guardian API router - TripShield Guardian Chat Endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.disruption import Disruption
from app.models.recovery import RecoveryStrategy
from app.core.security import get_current_user
from app.schemas.operational import GuardianChatRequest, GuardianChatResponse
from app.ai.guardian import TripShieldGuardian, MockLLMProvider
from app.services.journey_service import JourneyService

router = APIRouter()
llm = MockLLMProvider()
guardian = TripShieldGuardian(llm)
journey_service = JourneyService()


@router.post("/chat", response_model=GuardianChatResponse)
def chat(
    req: GuardianChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    j_data = {}
    disruptions = []
    recoveries = []

    if req.journey_id:
        dt = journey_service.get_digital_twin(db, req.journey_id)
        if dt:
            j_data = dt
        disruptions = db.query(Disruption).filter(Disruption.journey_id == req.journey_id).all()
        recoveries = db.query(RecoveryStrategy).filter(RecoveryStrategy.journey_id == req.journey_id).all()

    result = guardian.chat(req.message, j_data, disruptions, recoveries)
    return GuardianChatResponse(
        response=result["response"],
        context_used=result["context_used"]
    )
