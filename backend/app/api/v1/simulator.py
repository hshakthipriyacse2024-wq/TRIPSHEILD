"""What-If Simulation Router - Non-destructive disruption testing and analysis."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import Dict, Any

from app.database import get_db
from app.models.user import User, TravelerPreference
from app.models.journey import Journey, JourneyNode
from app.models.operational import Simulation
from app.core.security import get_current_user
from app.engines.ripple_impact import RippleImpactEngine
from app.engines.recovery_optimizer import RecoveryOptimizer
from app.engines.resilience_scorer import ResilienceScorer
from app.services.journey_service import JourneyService
from app.schemas.disruption import SimulationRequest

router = APIRouter()
impact_engine = RippleImpactEngine()
recovery_optimizer = RecoveryOptimizer()
resilience_scorer = ResilienceScorer()
journey_service = JourneyService()


class VirtualDisruption:
    def __init__(self, node_id: str, delay_minutes: int):
        self.id = str(uuid.uuid4())
        self.journey_id = ""
        self.affected_node_id = node_id
        self.delay_minutes = delay_minutes


@router.post("/journeys/{journey_id}/simulate")
def run_simulation(
    journey_id: str,
    data: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run a non-destructive What-If simulation on a journey."""
    journey = db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == current_user.id).first()
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")

    nodes = db.query(JourneyNode).filter(JourneyNode.journey_id == journey_id).order_by(JourneyNode.sequence_order).all()
    if not nodes:
        raise HTTPException(status_code=400, detail="Journey has no components to simulate")

    deps = journey.dependencies

    # Determine affected node (default to first flight or first node)
    target_node = next((n for n in nodes if n.type == "flight"), nodes[0])
    delay_minutes = (data.parameters or {}).get("delay_minutes", 240)
    if data.disruption_type == "flight_cancellation":
        delay_minutes = 720  # Max delay for cancellations

    # Virtual Disruption instance
    v_disruption = VirtualDisruption(target_node.id, delay_minutes)
    v_disruption.journey_id = journey.id

    # Calculate impact non-destructively
    impact_result = impact_engine.calculate_impact(v_disruption, journey, nodes, deps)

    # Calculate resilience score before and after
    resilience_before = resilience_scorer.calculate_score(journey, nodes, deps)["score"]
    
    # Estimate resilience after disruption
    resilience_after = max(10, resilience_before - int(impact_result.impact_score * 0.5))

    # Generate recovery options
    preferences = db.query(TravelerPreference).filter(TravelerPreference.user_id == current_user.id).first()
    recovery_options = recovery_optimizer.generate_strategies(
        v_disruption, impact_result, journey, nodes, deps, preferences, None
    )

    # Save Simulation record
    simulation = Simulation(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        user_id=current_user.id,
        disruption_type=data.disruption_type,
        parameters=data.parameters or {},
        impact_result={
            "impact_score": impact_result.impact_score,
            "severity_class": impact_result.severity_class,
            "nodes_affected": len(impact_result.directly_affected) + len(impact_result.indirectly_affected),
            "financial_exposure": impact_result.financial_exposure,
            "time_impact_minutes": impact_result.time_impact_minutes,
            "affected_details": [
                {
                    "node_id": info.node_id,
                    "node_type": info.node_type,
                    "provider": info.provider,
                    "impact_type": info.impact_type,
                    "reason": info.reason
                }
                for info in impact_result.affected_details
            ]
        },
        recovery_options=recovery_options,
        resilience_score_before=resilience_before,
        resilience_score_after=resilience_after,
        status="completed",
        created_at=datetime.utcnow()
    )
    db.add(simulation)
    db.commit()

    return {
        "simulation_id": simulation.id,
        "journey_id": journey.id,
        "disruption_type": data.disruption_type,
        "target_node": {
            "id": target_node.id,
            "type": target_node.type,
            "provider": target_node.provider
        },
        "impact": simulation.impact_result,
        "recovery_options": recovery_options,
        "resilience_score_before": resilience_before,
        "resilience_score_after": resilience_after,
        "status": "completed",
        "message": f"Simulation complete. Simulated {delay_minutes}min delay on {target_node.provider or target_node.type}."
    }


@router.post("/simulations/{simulation_id}/apply")
def apply_simulation(
    simulation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply a simulation result to make it a real disruption on the journey."""
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulation.status = "applied"
    db.commit()

    return {
        "status": "applied",
        "simulation_id": simulation_id,
        "journey_id": simulation.journey_id,
        "message": "Simulation applied to journey."
    }


@router.post("/simulations/{simulation_id}/discard")
def discard_simulation(
    simulation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Discard a simulation."""
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    simulation.status = "discarded"
    db.commit()

    return {"status": "discarded", "simulation_id": simulation_id}
