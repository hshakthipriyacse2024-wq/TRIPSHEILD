"""Disruptions API Router - Disruption reporting, listing, and detailed impact retrieval."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.models.user import User
from app.models.journey import Journey
from app.models.disruption import Disruption, ImpactAnalysis
from app.schemas.disruption import DisruptionCreate, DisruptionResponse
from app.core.security import get_current_user
from app.engines.ripple_impact import RippleImpactEngine
from app.services.journey_service import JourneyService
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService

router = APIRouter()
impact_engine = RippleImpactEngine()
journey_service = JourneyService()
notif_service = NotificationService()
audit_service = AuditService()


@router.get("", response_model=List[DisruptionResponse])
@router.get("/", response_model=List[DisruptionResponse])
def list_disruptions(
    journey_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all disruptions for the current user's journeys, sorted by detected_at descending."""
    user_journeys = db.query(Journey).filter(Journey.user_id == current_user.id).all()
    journey_map = {j.id: j.title for j in user_journeys}
    journey_ids = list(journey_map.keys())

    if not journey_ids:
        return []

    query = db.query(Disruption).options(joinedload(Disruption.impact_analysis)).filter(Disruption.journey_id.in_(journey_ids))
    if journey_id:
        query = query.filter(Disruption.journey_id == journey_id)

    disruptions = query.order_by(Disruption.detected_at.desc()).all()
    for d in disruptions:
        d.journey_title = journey_map.get(d.journey_id, "Journey")

    return disruptions


@router.post("", response_model=DisruptionResponse)
@router.post("/", response_model=DisruptionResponse)
def create_disruption(
    data: DisruptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new disruption and run instant impact analysis."""
    journey = db.query(Journey).filter(Journey.id == data.journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    d = Disruption(
        id=str(uuid.uuid4()),
        journey_id=data.journey_id,
        affected_node_id=data.affected_node_id,
        type=data.type,
        description=data.description or f"Disruption on journey {data.journey_id}",
        delay_minutes=data.delay_minutes,
        is_simulated=data.is_simulated,
        status="detected",
        detected_at=datetime.utcnow()
    )
    db.add(d)
    db.flush()

    # Calculate Impact
    dt = journey_service.get_digital_twin(db, d.journey_id)
    impact_result = impact_engine.calculate_impact(d, dt['journey'], dt['nodes'], dt['dependencies'])

    d.severity = impact_result.severity_class
    d.status = "recovery_generated"
    journey.status = "disrupted"
    db.commit()
    db.refresh(d)

    notif_service.create_notification(
        db, current_user.id, d.journey_id, "disruption",
        f"⚠️ Disruption Reported ({impact_result.severity_class.upper()})",
        d.description, "critical"
    )
    audit_service.log(db, current_user.id, d.journey_id, "disruption_created", f"Created disruption: {d.type}")

    return d


@router.get("/{id}", response_model=DisruptionResponse)
def get_disruption(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get disruption details by ID."""
    d = db.query(Disruption).filter(Disruption.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Disruption not found")
    return d
