from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.journey import JourneyCreate, JourneyResponse, DigitalTwinResponse
from app.services.journey_service import JourneyService
from app.engines.resilience_scorer import ResilienceScorer
from app.engines.risk_assessor import RiskAssessor

router = APIRouter()
journey_service = JourneyService()
resilience_scorer = ResilienceScorer()
risk_assessor = RiskAssessor()

@router.post("", response_model=JourneyResponse)
def create_journey(data: JourneyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return journey_service.create_journey(db, current_user.id, data)

@router.get("", response_model=List[JourneyResponse])
def get_user_journeys(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.journey import Journey
    return db.query(Journey).filter(Journey.user_id == current_user.id).all()

@router.get("/{id}", response_model=JourneyResponse)
def get_journey(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    j = journey_service.get_journey(db, id, current_user.id)
    if not j: raise HTTPException(status_code=404, detail="Not found")
    return j

@router.get("/{id}/digital-twin")
def get_digital_twin(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return journey_service.get_digital_twin(db, id)

@router.get("/{id}/resilience-score")
def get_resilience(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dt = journey_service.get_digital_twin(db, id)
    return resilience_scorer.calculate_score(dt['journey'], dt['nodes'], dt['dependencies'])

@router.get("/{id}/risk-assessment")
def assess_risk(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dt = journey_service.get_digital_twin(db, id)
    return risk_assessor.assess_journey(dt['journey'], dt['nodes'], dt['dependencies'])
