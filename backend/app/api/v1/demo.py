"""Demo endpoints for hackathon demonstration."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, TravelerPreference
from app.models.journey import Journey, JourneyNode, JourneyDependency
from app.models.disruption import Disruption, ImpactAnalysis, ImpactedNode
from app.models.recovery import RecoveryStrategy, RecoveryAction
from app.core.security import get_current_user
from app.engines.ripple_impact import RippleImpactEngine
from app.engines.recovery_optimizer import RecoveryOptimizer
from app.engines.resilience_scorer import ResilienceScorer
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

impact_engine = RippleImpactEngine()
recovery_optimizer = RecoveryOptimizer()
resilience_scorer = ResilienceScorer()
notif_service = NotificationService()
audit_service = AuditService()


@router.post("/load")
def load_demo_journey(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Load the complete demo journey: Chennai → Delhi → Paris with all nodes and dependencies."""
    
    # Delete existing demo journeys for this user
    existing = db.query(Journey).filter(Journey.user_id == current_user.id, Journey.is_demo == True).all()
    for j in existing:
        db.delete(j)
    db.commit()

    # Create journey
    base_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=3)
    
    journey = Journey(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title="Chennai → Delhi → Paris Adventure",
        description="A multi-city journey from Chennai to Delhi (domestic) then onward to Paris (international). "
                    "Includes sightseeing, dining, and cultural experiences across three days.",
        origin="Chennai",
        destination="Paris",
        start_date=base_date + timedelta(hours=6),
        end_date=base_date + timedelta(days=3, hours=22),
        status="active",
        is_demo=True,
    )
    db.add(journey)
    db.flush()

    # --- Create Nodes ---
    nodes = []

    # Node 1: Flight Chennai → Delhi
    n1 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="flight",
        provider="Air India", location="Chennai (MAA)",
        latitude=12.9941, longitude=80.1709,
        destination_location="Delhi (DEL)",
        dest_latitude=28.5562, dest_longitude=77.1000,
        start_time=base_date + timedelta(hours=6),
        end_time=base_date + timedelta(hours=8, minutes=30),
        status="confirmed", cost=5500.0, currency="INR",
        booking_reference="AI-542-DEMO",
        flexibility="low", importance="critical",
        cancellation_policy={"refundable": False, "change_fee": 2000},
        details={"flight_number": "AI-542", "airline": "Air India",
                 "departure_terminal": "T1", "arrival_terminal": "T3",
                 "class": "Economy", "seat": "14A"},
        sequence_order=1,
    )
    nodes.append(n1)

    # Node 2: Airport Transfer Delhi
    n2 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="airport_transfer",
        provider="Uber Premier", location="Delhi Airport (DEL)",
        latitude=28.5562, longitude=77.1000,
        destination_location="The Imperial, New Delhi",
        dest_latitude=28.6253, dest_longitude=77.2190,
        start_time=base_date + timedelta(hours=9),
        end_time=base_date + timedelta(hours=9, minutes=45),
        status="confirmed", cost=800.0, currency="INR",
        booking_reference="UBER-DEL-001",
        flexibility="high", importance="high",
        cancellation_policy={"refundable": True, "cancel_before_minutes": 5},
        details={"vehicle_type": "Premier Sedan", "driver": "Assigned on pickup"},
        sequence_order=2,
    )
    nodes.append(n2)

    # Node 3: Hotel Delhi
    n3 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="hotel",
        provider="The Imperial New Delhi", location="New Delhi",
        latitude=28.6253, longitude=77.2190,
        start_time=base_date + timedelta(hours=10),
        end_time=base_date + timedelta(days=1, hours=6),
        status="confirmed", cost=12000.0, currency="INR",
        booking_reference="IMP-2024-DEMO",
        flexibility="medium", importance="high",
        cancellation_policy={"refundable": True, "cancel_before_hours": 24, "penalty": 6000},
        details={"room_type": "Deluxe Room", "check_in": "10:00 AM", "check_out": "6:00 AM",
                 "amenities": ["WiFi", "Breakfast", "Pool", "Spa"]},
        sequence_order=3,
    )
    nodes.append(n3)

    # Node 4: Activity - Red Fort Tour
    n4 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="activity",
        provider="Delhi Heritage Tours", location="Red Fort, Delhi",
        latitude=28.6562, longitude=77.2410,
        start_time=base_date + timedelta(hours=14),
        end_time=base_date + timedelta(hours=17),
        status="confirmed", cost=1500.0, currency="INR",
        booking_reference="DHT-RF-001",
        flexibility="medium", importance="medium",
        cancellation_policy={"refundable": True, "cancel_before_hours": 12},
        details={"activity_name": "Red Fort Heritage Walk", "guide": "English",
                 "group_size": 8, "includes": ["Entry ticket", "Audio guide"]},
        sequence_order=4,
    )
    nodes.append(n4)

    # Node 5: Restaurant - Bukhara
    n5 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="restaurant",
        provider="Bukhara, ITC Maurya", location="ITC Maurya, New Delhi",
        latitude=28.5974, longitude=77.1724,
        start_time=base_date + timedelta(hours=19, minutes=30),
        end_time=base_date + timedelta(hours=21, minutes=30),
        status="confirmed", cost=3000.0, currency="INR",
        booking_reference="BUK-RES-001",
        flexibility="low", importance="medium",
        cancellation_policy={"refundable": False, "no_show_charge": 1000},
        details={"cuisine": "North Indian", "party_size": 2,
                 "reservation_code": "BUK2024", "dress_code": "Smart Casual"},
        sequence_order=5,
    )
    nodes.append(n5)

    # Node 6: Flight Delhi → Paris
    n6 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="flight",
        provider="Air France", location="Delhi (DEL)",
        latitude=28.5562, longitude=77.1000,
        destination_location="Paris (CDG)",
        dest_latitude=49.0097, dest_longitude=2.5479,
        start_time=base_date + timedelta(days=1, hours=7),
        end_time=base_date + timedelta(days=1, hours=13),
        status="confirmed", cost=35000.0, currency="INR",
        booking_reference="AF-226-DEMO",
        flexibility="none", importance="critical",
        cancellation_policy={"refundable": False, "change_fee": 8000},
        details={"flight_number": "AF-226", "airline": "Air France",
                 "departure_terminal": "T3", "arrival_terminal": "2E",
                 "class": "Economy Plus", "seat": "22C", "meal": "Included"},
        sequence_order=6,
    )
    nodes.append(n6)

    # Node 7: Airport Transfer Paris
    n7 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="airport_transfer",
        provider="Paris Airport Shuttle", location="Paris CDG Airport",
        latitude=49.0097, longitude=2.5479,
        destination_location="Le Marais, Paris",
        dest_latitude=48.8566, dest_longitude=2.3522,
        start_time=base_date + timedelta(days=1, hours=13, minutes=30),
        end_time=base_date + timedelta(days=1, hours=14, minutes=30),
        status="confirmed", cost=1875.0, currency="INR",  # ~€25
        booking_reference="PAS-CDG-001",
        flexibility="high", importance="high",
        cancellation_policy={"refundable": True, "cancel_before_hours": 2},
        details={"vehicle_type": "Shared Shuttle", "service": "Paris Airport Shuttle",
                 "currency_local": "EUR", "cost_local": 25},
        sequence_order=7,
    )
    nodes.append(n7)

    # Node 8: Hotel Paris
    n8 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="hotel",
        provider="Hôtel Le Marais", location="Le Marais, Paris",
        latitude=48.8566, longitude=2.3522,
        start_time=base_date + timedelta(days=1, hours=15),
        end_time=base_date + timedelta(days=3, hours=11),
        status="confirmed", cost=27000.0, currency="INR",  # ~€180 * 2 nights
        booking_reference="HLM-PAR-DEMO",
        flexibility="low", importance="high",
        cancellation_policy={"refundable": True, "cancel_before_hours": 48, "penalty_pct": 50},
        details={"room_type": "Superior Double", "check_in": "3:00 PM", "check_out": "11:00 AM",
                 "amenities": ["WiFi", "Breakfast", "Concierge"],
                 "currency_local": "EUR", "cost_per_night_local": 180},
        sequence_order=8,
    )
    nodes.append(n8)

    # Node 9: Activity - Eiffel Tower
    n9 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="activity",
        provider="Tour Eiffel", location="Eiffel Tower, Paris",
        latitude=48.8584, longitude=2.2945,
        start_time=base_date + timedelta(days=1, hours=16),
        end_time=base_date + timedelta(days=1, hours=18),
        status="confirmed", cost=1875.0, currency="INR",  # ~€25
        booking_reference="ET-VIS-001",
        flexibility="low", importance="high",
        cancellation_policy={"refundable": False},
        details={"activity_name": "Eiffel Tower Summit Visit", "level": "Summit",
                 "time_slot": "4:00 PM", "currency_local": "EUR", "cost_local": 25},
        sequence_order=9,
    )
    nodes.append(n9)

    # Node 10: Restaurant - Le Comptoir
    n10 = JourneyNode(
        id=str(uuid.uuid4()), journey_id=journey.id, type="restaurant",
        provider="Le Comptoir du Panthéon", location="Latin Quarter, Paris",
        latitude=48.8462, longitude=2.3464,
        start_time=base_date + timedelta(days=1, hours=20),
        end_time=base_date + timedelta(days=1, hours=22),
        status="confirmed", cost=3750.0, currency="INR",  # ~€50
        booking_reference="LCP-RES-001",
        flexibility="medium", importance="low",
        cancellation_policy={"refundable": True, "cancel_before_hours": 4},
        details={"cuisine": "French Bistro", "party_size": 2,
                 "reservation_code": "LCP2024", "currency_local": "EUR", "cost_local": 50},
        sequence_order=10,
    )
    nodes.append(n10)

    for n in nodes:
        db.add(n)
    db.flush()

    # --- Create Dependencies ---
    deps = [
        # Flight 1 → Airport Transfer 1 (critical connection)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n1.id, target_node_id=n2.id,
            relationship_type="connects_to", buffer_minutes=30, is_critical=True,
        ),
        # Airport Transfer 1 → Hotel Delhi
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n2.id, target_node_id=n3.id,
            relationship_type="depends_on", buffer_minutes=15, is_critical=False,
        ),
        # Hotel Delhi → Activity (Red Fort)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n3.id, target_node_id=n4.id,
            relationship_type="precedes", buffer_minutes=240, is_critical=False,
        ),
        # Activity → Restaurant (Bukhara)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n4.id, target_node_id=n5.id,
            relationship_type="precedes", buffer_minutes=150, is_critical=False,
        ),
        # Hotel Delhi → Flight 2 (critical: must check out before flight)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n3.id, target_node_id=n6.id,
            relationship_type="depends_on", buffer_minutes=60, is_critical=True,
        ),
        # Flight 2 → Airport Transfer Paris (critical connection)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n6.id, target_node_id=n7.id,
            relationship_type="connects_to", buffer_minutes=30, is_critical=True,
        ),
        # Airport Transfer Paris → Hotel Paris
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n7.id, target_node_id=n8.id,
            relationship_type="depends_on", buffer_minutes=30, is_critical=False,
        ),
        # Hotel Paris → Activity (Eiffel Tower)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n8.id, target_node_id=n9.id,
            relationship_type="precedes", buffer_minutes=60, is_critical=False,
        ),
        # Activity (Eiffel Tower) → Restaurant (Le Comptoir)
        JourneyDependency(
            id=str(uuid.uuid4()), journey_id=journey.id,
            source_node_id=n9.id, target_node_id=n10.id,
            relationship_type="precedes", buffer_minutes=120, is_critical=False,
        ),
    ]
    for dep in deps:
        db.add(dep)

    # Create default traveler preferences if not exist
    pref = db.query(TravelerPreference).filter(TravelerPreference.user_id == current_user.id).first()
    if not pref:
        pref = TravelerPreference(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            budget_priority=50,
            speed_priority=70,
            comfort_priority=60,
            minimal_changes_priority=50,
        )
        db.add(pref)

    # Calculate resilience score
    score_result = resilience_scorer.calculate_score(journey, nodes, deps)
    journey.resilience_score = score_result["score"]

    db.commit()
    db.refresh(journey)

    # Create audit log
    audit_service.log(db, current_user.id, journey.id, "demo_loaded",
                      "Demo journey loaded: Chennai → Delhi → Paris",
                      {"nodes_count": len(nodes), "dependencies_count": len(deps)})
    
    # Create notification
    notif_service.create_notification(
        db, current_user.id, journey.id, "info",
        "Demo Journey Loaded! 🌍",
        f"Your Chennai → Delhi → Paris adventure has been created with {len(nodes)} components and {len(deps)} dependencies.",
        "medium"
    )

    logger.info(f"Demo journey loaded: {journey.id} with {len(nodes)} nodes and {len(deps)} dependencies")

    return {
        "journey_id": journey.id,
        "title": journey.title,
        "nodes_count": len(nodes),
        "dependencies_count": len(deps),
        "resilience_score": journey.resilience_score,
        "message": "Demo journey loaded successfully! Click on the journey to explore the Digital Twin.",
        "demo_label": "Demo / Simulated Data"
    }


@router.post("/simulate-delay")
def simulate_delay(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simulate a 4-hour flight delay on the first flight of the demo journey."""
    
    # Find demo journey
    journey = db.query(Journey).filter(
        Journey.user_id == current_user.id, Journey.is_demo == True
    ).first()
    if not journey:
        raise HTTPException(status_code=404, detail="No demo journey found. Load a demo journey first.")

    nodes = db.query(JourneyNode).filter(JourneyNode.journey_id == journey.id).order_by(JourneyNode.sequence_order).all()
    deps = db.query(JourneyDependency).filter(JourneyDependency.journey_id == journey.id).all()
    
    # Find first flight
    first_flight = next((n for n in nodes if n.type == "flight"), None)
    if not first_flight:
        raise HTTPException(status_code=404, detail="No flight found in demo journey.")

    # Create disruption
    disruption = Disruption(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        affected_node_id=first_flight.id,
        type="flight_delay",
        severity=None,  # Will be calculated
        description=f"Flight {first_flight.details.get('flight_number', 'AI-542')} from "
                    f"{first_flight.location} to {first_flight.destination_location} "
                    f"delayed by 4 hours due to technical issues.",
        delay_minutes=240,
        is_simulated=True,
        status="detected",
        detected_at=datetime.utcnow(),
    )
    db.add(disruption)
    db.flush()

    # Run Ripple Impact Engine
    impact_result = impact_engine.calculate_impact(disruption, journey, nodes, deps)
    
    # Store impact analysis
    impact_analysis = ImpactAnalysis(
        id=str(uuid.uuid4()),
        disruption_id=disruption.id,
        journey_id=journey.id,
        impact_score=impact_result.impact_score,
        severity_class=impact_result.severity_class,
        nodes_affected=len(impact_result.directly_affected) + len(impact_result.indirectly_affected),
        financial_exposure=impact_result.financial_exposure,
        currency=impact_result.currency,
        time_impact_minutes=impact_result.time_impact_minutes,
        scoring_breakdown=impact_result.scoring_breakdown,
        affected_nodes_detail=[
            {
                "node_id": info.node_id,
                "node_type": info.node_type,
                "provider": info.provider,
                "impact_type": info.impact_type,
                "reason": info.reason,
                "cost_at_risk": info.cost_at_risk,
            }
            for info in impact_result.affected_details
        ],
        analyzed_at=datetime.utcnow(),
    )
    db.add(impact_analysis)

    # Store impacted nodes
    for info in impact_result.affected_details:
        impacted = ImpactedNode(
            id=str(uuid.uuid4()),
            impact_analysis_id=impact_analysis.id,
            node_id=info.node_id,
            impact_type=info.impact_type,
            reason=info.reason,
            severity_contribution=info.severity_contribution,
        )
        db.add(impacted)

    # Update disruption severity
    disruption.severity = impact_result.severity_class
    disruption.status = "analyzing"

    # Update affected node statuses
    first_flight.status = "affected"
    for node_id in impact_result.directly_affected:
        node = next((n for n in nodes if n.id == node_id), None)
        if node and node.id != first_flight.id:
            node.status = "affected"
    for node_id in impact_result.indirectly_affected:
        node = next((n for n in nodes if n.id == node_id), None)
        if node:
            node.status = "at_risk"

    # Update journey status
    journey.status = "disrupted"

    # Get traveler preferences
    preferences = db.query(TravelerPreference).filter(
        TravelerPreference.user_id == current_user.id
    ).first()

    # Generate recovery strategies
    recovery_strategies = recovery_optimizer.generate_strategies(
        disruption, impact_result, journey, nodes, deps, preferences, None
    )

    # Store recovery strategies
    stored_strategies = []
    for s_data in recovery_strategies:
        strategy = RecoveryStrategy(
            id=str(uuid.uuid4()),
            disruption_id=disruption.id,
            journey_id=journey.id,
            title=s_data["title"],
            description=s_data["description"],
            changed_components=s_data["changed_components"],
            preserved_components=s_data["preserved_components"],
            additional_cost=s_data["additional_cost"],
            currency=s_data["currency"],
            time_saved_minutes=s_data["time_saved_minutes"],
            num_changes=s_data["num_changes"],
            feasibility_score=s_data["feasibility_score"],
            comfort_score=s_data["comfort_score"],
            urgency_score=s_data["urgency_score"],
            financial_impact_score=s_data["financial_impact_score"],
            recovery_confidence=s_data["recovery_confidence"],
            overall_score=s_data["overall_score"],
            explanation=s_data["explanation"],
            is_recommended=s_data["is_recommended"],
            rank=s_data["rank"],
            status="proposed",
            actions_detail=s_data["actions"],
            created_at=datetime.utcnow(),
        )
        db.add(strategy)
        stored_strategies.append(strategy)

        # Store recovery actions
        for a_data in s_data["actions"]:
            action = RecoveryAction(
                id=str(uuid.uuid4()),
                strategy_id=strategy.id,
                original_node_id=a_data.get("original_node_id"),
                action_type=a_data["action_type"],
                description=a_data["description"],
                old_details=a_data.get("old_details", {}),
                new_details=a_data.get("new_details", {}),
                cost_difference=a_data.get("cost_difference", 0),
                status="pending",
            )
            db.add(action)

    disruption.status = "recovery_generated"

    db.commit()

    # Notifications
    notif_service.create_notification(
        db, current_user.id, journey.id, "disruption",
        f"⚠️ Flight Delay Detected!",
        f"Flight {first_flight.details.get('flight_number', 'AI-542')} has been delayed by 4 hours. "
        f"Impact Score: {impact_result.impact_score}/100 ({impact_result.severity_class}). "
        f"{len(impact_result.directly_affected) + len(impact_result.indirectly_affected)} downstream bookings affected.",
        "critical"
    )
    notif_service.create_notification(
        db, current_user.id, journey.id, "recovery_recommendation",
        f"🔄 Recovery Options Ready",
        f"{len(recovery_strategies)} recovery strategies generated. "
        f"Recommended: {recovery_strategies[0]['title']} (Score: {recovery_strategies[0]['overall_score']}/100).",
        "high"
    )

    # Audit
    audit_service.log(db, current_user.id, journey.id, "disruption_simulated",
                      f"4-hour flight delay simulated on {first_flight.details.get('flight_number', 'AI-542')}",
                      {"delay_minutes": 240, "impact_score": impact_result.impact_score,
                       "nodes_affected": len(impact_result.directly_affected) + len(impact_result.indirectly_affected),
                       "strategies_generated": len(recovery_strategies)})

    db.refresh(disruption)

    return {
        "disruption_id": disruption.id,
        "journey_id": journey.id,
        "description": disruption.description,
        "impact": {
            "impact_score": impact_result.impact_score,
            "severity_class": impact_result.severity_class,
            "nodes_affected": len(impact_result.directly_affected) + len(impact_result.indirectly_affected),
            "directly_affected": len(impact_result.directly_affected),
            "indirectly_affected": len(impact_result.indirectly_affected),
            "financial_exposure": impact_result.financial_exposure,
            "time_impact_minutes": impact_result.time_impact_minutes,
            "scoring_breakdown": impact_result.scoring_breakdown,
            "affected_details": [
                {
                    "node_id": info.node_id,
                    "node_type": info.node_type,
                    "provider": info.provider,
                    "impact_type": info.impact_type,
                    "reason": info.reason,
                }
                for info in impact_result.affected_details
            ],
        },
        "recovery_strategies": recovery_strategies,
        "message": f"Disruption simulated! {impact_result.impact_score}/100 impact. "
                   f"{len(recovery_strategies)} recovery options generated.",
        "demo_label": "Demo / Simulated Data"
    }


@router.post("/simulate-cancellation")
def simulate_cancellation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simulate a flight cancellation on the first flight of the demo journey."""
    
    journey = db.query(Journey).filter(
        Journey.user_id == current_user.id, Journey.is_demo == True
    ).first()
    if not journey:
        raise HTTPException(status_code=404, detail="No demo journey found. Load a demo journey first.")

    nodes = db.query(JourneyNode).filter(JourneyNode.journey_id == journey.id).order_by(JourneyNode.sequence_order).all()
    deps = db.query(JourneyDependency).filter(JourneyDependency.journey_id == journey.id).all()
    
    first_flight = next((n for n in nodes if n.type == "flight"), None)
    if not first_flight:
        raise HTTPException(status_code=404, detail="No flight found in demo journey.")

    # Create cancellation disruption (treated as max delay for impact)
    disruption = Disruption(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        affected_node_id=first_flight.id,
        type="flight_cancellation",
        description=f"Flight {first_flight.details.get('flight_number', 'AI-542')} from "
                    f"{first_flight.location} to {first_flight.destination_location} "
                    f"has been CANCELLED due to operational reasons.",
        delay_minutes=720,  # 12 hours equivalent for cancellation
        is_simulated=True,
        status="detected",
        detected_at=datetime.utcnow(),
    )
    db.add(disruption)
    db.flush()

    # Run impact analysis
    impact_result = impact_engine.calculate_impact(disruption, journey, nodes, deps)
    disruption.severity = impact_result.severity_class

    # Store impact analysis
    impact_analysis = ImpactAnalysis(
        id=str(uuid.uuid4()),
        disruption_id=disruption.id, journey_id=journey.id,
        impact_score=impact_result.impact_score, severity_class=impact_result.severity_class,
        nodes_affected=len(impact_result.directly_affected) + len(impact_result.indirectly_affected),
        financial_exposure=impact_result.financial_exposure, currency="INR",
        time_impact_minutes=impact_result.time_impact_minutes,
        scoring_breakdown=impact_result.scoring_breakdown,
        affected_nodes_detail=[{"node_id": i.node_id, "impact_type": i.impact_type, "reason": i.reason}
                                for i in impact_result.affected_details],
        analyzed_at=datetime.utcnow(),
    )
    db.add(impact_analysis)

    # Update statuses
    first_flight.status = "cancelled"
    for nid in impact_result.directly_affected + impact_result.indirectly_affected:
        node = next((n for n in nodes if n.id == nid), None)
        if node and node.id != first_flight.id:
            node.status = "affected"
    journey.status = "disrupted"
    disruption.status = "recovery_generated"

    db.commit()

    notif_service.create_notification(
        db, current_user.id, journey.id, "disruption",
        "🚨 Flight CANCELLED!",
        f"Flight {first_flight.details.get('flight_number', 'AI-542')} has been cancelled. "
        f"Impact Score: {impact_result.impact_score}/100 ({impact_result.severity_class}). "
        f"Go to Recovery Center for options.",
        "critical"
    )
    audit_service.log(db, current_user.id, journey.id, "disruption_simulated",
                      "Flight cancellation simulated", {"type": "flight_cancellation"})

    return {
        "disruption_id": disruption.id,
        "journey_id": journey.id,
        "description": disruption.description,
        "impact_score": impact_result.impact_score,
        "severity": impact_result.severity_class,
        "nodes_affected": len(impact_result.directly_affected) + len(impact_result.indirectly_affected),
        "message": "Flight cancellation simulated! Check Recovery Center for options.",
        "demo_label": "Demo / Simulated Data"
    }
