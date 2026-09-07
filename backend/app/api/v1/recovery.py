"""Recovery API router - Strategy generation, options comparison, approval, execution, and rejection."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from app.database import get_db
from app.models.user import User, TravelerPreference
from app.models.journey import Journey, JourneyNode
from app.models.disruption import Disruption, ImpactAnalysis
from app.models.recovery import RecoveryStrategy, RecoveryAction
from app.core.security import get_current_user
from app.engines.recovery_optimizer import RecoveryOptimizer
from app.engines.resilience_scorer import ResilienceScorer
from app.services.journey_service import JourneyService
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService

router = APIRouter()
optimizer = RecoveryOptimizer()
journey_service = JourneyService()
resilience_scorer = ResilienceScorer()
notif_service = NotificationService()
audit_service = AuditService()


@router.post("/journeys/{journey_id}/recovery-options")
def get_recovery_options(
    journey_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate or retrieve recovery strategies for the active disruption on a journey."""
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    disruption = db.query(Disruption).filter(
        Disruption.journey_id == journey_id
    ).order_by(Disruption.detected_at.desc()).first()

    if not disruption:
        raise HTTPException(status_code=404, detail="No disruption found for this journey")

    # Check if strategies already exist in database
    existing_strategies = db.query(RecoveryStrategy).filter(
        RecoveryStrategy.disruption_id == disruption.id
    ).order_by(RecoveryStrategy.rank.asc()).all()

    if existing_strategies:
        return [
            {
                "id": s.id,
                "disruption_id": s.disruption_id,
                "journey_id": s.journey_id,
                "title": s.title,
                "description": s.description,
                "changed_components": s.changed_components or [],
                "preserved_components": s.preserved_components or [],
                "additional_cost": s.additional_cost,
                "currency": s.currency,
                "time_saved_minutes": s.time_saved_minutes,
                "num_changes": s.num_changes,
                "feasibility_score": s.feasibility_score,
                "comfort_score": s.comfort_score,
                "urgency_score": s.urgency_score,
                "financial_impact_score": s.financial_impact_score,
                "recovery_confidence": s.recovery_confidence,
                "overall_score": s.overall_score,
                "explanation": s.explanation,
                "is_recommended": s.is_recommended,
                "rank": s.rank,
                "status": s.status,
                "actions": s.actions_detail or []
            }
            for s in existing_strategies
        ]

    # Otherwise generate fresh strategies
    dt = journey_service.get_digital_twin(db, journey_id)
    impact = db.query(ImpactAnalysis).filter(ImpactAnalysis.disruption_id == disruption.id).first()
    preferences = db.query(TravelerPreference).filter(TravelerPreference.user_id == current_user.id).first()

    strategies_data = optimizer.generate_strategies(
        disruption, impact, dt["journey"], dt["nodes"], dt["dependencies"], preferences, None
    )

    return strategies_data


@router.get("/{strategy_id}")
def get_strategy_detail(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific recovery strategy."""
    strategy = db.query(RecoveryStrategy).filter(RecoveryStrategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Recovery strategy not found")
    
    actions = db.query(RecoveryAction).filter(RecoveryAction.strategy_id == strategy_id).all()

    return {
        "id": strategy.id,
        "disruption_id": strategy.disruption_id,
        "journey_id": strategy.journey_id,
        "title": strategy.title,
        "description": strategy.description,
        "changed_components": strategy.changed_components or [],
        "preserved_components": strategy.preserved_components or [],
        "additional_cost": strategy.additional_cost,
        "currency": strategy.currency,
        "time_saved_minutes": strategy.time_saved_minutes,
        "num_changes": strategy.num_changes,
        "feasibility_score": strategy.feasibility_score,
        "comfort_score": strategy.comfort_score,
        "urgency_score": strategy.urgency_score,
        "overall_score": strategy.overall_score,
        "explanation": strategy.explanation,
        "is_recommended": strategy.is_recommended,
        "rank": strategy.rank,
        "status": strategy.status,
        "actions": [
            {
                "id": a.id,
                "action_type": a.action_type,
                "description": a.description,
                "cost_difference": a.cost_difference,
                "status": a.status,
                "old_details": a.old_details,
                "new_details": a.new_details
            }
            for a in actions
        ]
    }


@router.post("/{strategy_id}/approve")
def approve_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a recovery strategy."""
    strategy = db.query(RecoveryStrategy).filter(RecoveryStrategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.status = "approved"
    disruption = db.query(Disruption).filter(Disruption.id == strategy.disruption_id).first()
    if disruption:
        disruption.status = "recovery_approved"

    db.commit()

    notif_service.create_notification(
        db, current_user.id, strategy.journey_id, "recovery_approved",
        "Recovery Strategy Approved ✅",
        f"Approved '{strategy.title}'. System ready to execute itinerary rebuild.",
        "high"
    )
    audit_service.log(
        db, current_user.id, strategy.journey_id, "recovery_approved",
        f"User approved strategy: {strategy.title}",
        {"strategy_id": strategy.id, "score": strategy.overall_score}
    )

    return {"status": "approved", "strategy_id": strategy_id, "message": "Strategy approved successfully."}


@router.post("/{strategy_id}/execute")
def execute_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute an approved recovery strategy and rebuild the journey itinerary."""
    strategy = db.query(RecoveryStrategy).filter(RecoveryStrategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    journey = db.query(Journey).filter(Journey.id == strategy.journey_id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    strategy.status = "executing"
    db.flush()

    # Process recovery actions
    actions = db.query(RecoveryAction).filter(RecoveryAction.strategy_id == strategy.id).all()
    for action in actions:
        if action.original_node_id:
            orig_node = db.query(JourneyNode).filter(JourneyNode.id == action.original_node_id).first()
            if orig_node:
                orig_node.status = "recovered"
                if action.new_details:
                    new_provider = action.new_details.get("provider")
                    if new_provider:
                        orig_node.provider = new_provider
                    if "cost" in action.new_details:
                        orig_node.cost = action.new_details["cost"]
        action.status = "completed"
        action.executed_at = datetime.utcnow()

    # Update all nodes in journey that were affected to recovered
    nodes = db.query(JourneyNode).filter(JourneyNode.journey_id == journey.id).all()
    for n in nodes:
        if n.status in ["affected", "at_risk"]:
            n.status = "recovered"

    # Recalculate resilience score
    deps = journey.dependencies
    resilience_result = resilience_scorer.calculate_score(journey, nodes, deps)
    journey.resilience_score = resilience_result["score"]
    journey.status = "recovered"

    disruption = db.query(Disruption).filter(Disruption.id == strategy.disruption_id).first()
    if disruption:
        disruption.status = "recovered"
        disruption.resolved_at = datetime.utcnow()

    strategy.status = "completed"
    db.commit()

    notif_service.create_notification(
        db, current_user.id, journey.id, "recovery_completed",
        "Journey Recovered Successfully! 🎉",
        f"Executed strategy '{strategy.title}'. All components recovered. Journey resilience score: {journey.resilience_score}/100.",
        "high"
    )
    audit_service.log(
        db, current_user.id, journey.id, "recovery_executed",
        f"Recovery executed: {strategy.title}",
        {"strategy_id": strategy.id, "actions_completed": len(actions), "new_resilience_score": journey.resilience_score}
    )

    return {
        "status": "completed",
        "journey_id": journey.id,
        "journey_status": "recovered",
        "resilience_score": journey.resilience_score,
        "message": f"Strategy '{strategy.title}' executed successfully. Journey rebuilt!"
    }


@router.post("/{strategy_id}/reject")
def reject_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a recovery strategy."""
    strategy = db.query(RecoveryStrategy).filter(RecoveryStrategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.status = "rejected"
    db.commit()

    audit_service.log(
        db, current_user.id, strategy.journey_id, "recovery_rejected",
        f"User rejected strategy: {strategy.title}",
        {"strategy_id": strategy.id}
    )

    return {"status": "rejected", "strategy_id": strategy_id, "message": "Strategy rejected."}
