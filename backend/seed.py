"""Database seeding script for TripShield AI - populates demo users, preferences, journeys, nodes, dependencies, disruptions, recoveries, notifications, and audit logs."""
import sys
import os
import uuid
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal, init_db
from app.models.user import User, TravelerPreference
from app.models.journey import Journey, JourneyNode, JourneyDependency
from app.models.disruption import Disruption, ImpactAnalysis, ImpactedNode
from app.models.recovery import RecoveryStrategy, RecoveryAction
from app.models.operational import Notification, AuditLog, Provider, RiskAssessment
from app.core.security import get_password_hash
from app.engines.resilience_scorer import ResilienceScorer
from app.engines.ripple_impact import RippleImpactEngine
from app.engines.recovery_optimizer import RecoveryOptimizer

resilience_scorer = ResilienceScorer()
impact_engine = RippleImpactEngine()
recovery_optimizer = RecoveryOptimizer()


def seed_database():
    print("[+] Initializing Database Schema...")
    init_db()
    db = SessionLocal()

    try:
        print("[+] Creating/Updating Demo Users...")
        # 1. Traveler User
        traveler = db.query(User).filter(User.email == "harini@gmail.com").first()
        if not traveler:
            traveler = User(
                id=str(uuid.uuid4()),
                email="harini@gmail.com",
                password_hash=get_password_hash("Password123!"),
                full_name="Harini S",
                phone="+91-9876543210",
                role="traveler",
                is_active=True
            )
            db.add(traveler)
        else:
            traveler.password_hash = get_password_hash("Password123!")
        db.flush()

        # 2. Ops Admin User
        ops_user = db.query(User).filter(User.email == "ops@tripshield.ai").first()
        if not ops_user:
            ops_user = User(
                id=str(uuid.uuid4()),
                email="ops@tripshield.ai",
                password_hash=get_password_hash("OpsPass123!"),
                full_name="Operations Admin",
                phone="+91-9876543211",
                role="ops_admin",
                is_active=True
            )
            db.add(ops_user)
        else:
            ops_user.password_hash = get_password_hash("OpsPass123!")
        db.flush()

        # 3. System Admin User
        admin_user = db.query(User).filter(User.email == "admin@tripshield.ai").first()
        if not admin_user:
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@tripshield.ai",
                password_hash=get_password_hash("AdminPass123!"),
                full_name="System Administrator",
                phone="+91-9876543212",
                role="sys_admin",
                is_active=True
            )
            db.add(admin_user)
        else:
            admin_user.password_hash = get_password_hash("AdminPass123!")
        db.flush()

        print("[+] Creating Traveler Preferences...")
        pref = db.query(TravelerPreference).filter(TravelerPreference.user_id == traveler.id).first()
        if not pref:
            pref = TravelerPreference(
                id=str(uuid.uuid4()),
                user_id=traveler.id,
                budget_priority=50,
                speed_priority=80,
                comfort_priority=70,
                minimal_changes_priority=60,
                preferred_airlines=["Air India", "IndiGo", "Air France", "Vistara"],
                preferred_transport=["Uber", "Airport Shuttle", "Metro"],
                max_connections=2,
                preferred_hotel_category="4-Star Luxury",
                important_activities=["Heritage Tours", "Eiffel Tower Visit", "Bukhara Dining"]
            )
            db.add(pref)

        print("[+] Registering Mock Service Providers...")
        provider_names = [
            ("Air India", "flight"),
            ("Air France", "flight"),
            ("IndiGo", "flight"),
            ("The Imperial New Delhi", "hotel"),
            ("Hôtel Le Marais Paris", "hotel"),
            ("Uber India", "transport"),
            ("Paris Airport Shuttle", "transport"),
            ("Delhi Heritage Tours", "activity"),
            ("Tour Eiffel", "activity"),
            ("OpenWeatherMap Sync", "weather")
        ]
        for p_name, p_type in provider_names:
            if not db.query(Provider).filter(Provider.name == p_name).first():
                db.add(Provider(
                    id=str(uuid.uuid4()),
                    name=p_name,
                    type=p_type,
                    is_mock=True,
                    status="active",
                    last_health_check=datetime.utcnow()
                ))

        print("[+] Creating Chennai -> Delhi -> Paris Demo Journey...")
        existing_journey = db.query(Journey).filter(
            Journey.user_id == traveler.id,
            Journey.title == "Chennai → Delhi → Paris Adventure"
        ).first()

        if existing_journey:
            db.delete(existing_journey)
            db.flush()

        base_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=3)

        journey = Journey(
            id=str(uuid.uuid4()),
            user_id=traveler.id,
            title="Chennai → Delhi → Paris Adventure",
            description="Multi-leg international journey with connected flights, luxury hotel stays, heritage walks, and dining reservations.",
            origin="Chennai",
            destination="Paris",
            start_date=base_date + timedelta(hours=6),
            end_date=base_date + timedelta(days=3, hours=22),
            status="active",
            is_demo=True,
        )
        db.add(journey)
        db.flush()

        # Nodes
        nodes = []

        # 1. Flight MAA -> DEL
        n1 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="flight",
            provider="Air India", location="Chennai (MAA)",
            latitude=12.9941, longitude=80.1709,
            destination_location="Delhi (DEL)", dest_latitude=28.5562, dest_longitude=77.1000,
            start_time=base_date + timedelta(hours=6), end_time=base_date + timedelta(hours=8, minutes=30),
            status="confirmed", cost=5500.0, currency="INR", booking_reference="AI-542-DEMO",
            flexibility="low", importance="critical",
            details={"flight_number": "AI-542", "airline": "Air India", "terminal": "T1", "seat": "14A"},
            sequence_order=1
        )
        nodes.append(n1)

        # 2. Transfer DEL
        n2 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="airport_transfer",
            provider="Uber Premier", location="Delhi Airport (DEL)",
            latitude=28.5562, longitude=77.1000,
            destination_location="The Imperial, New Delhi", dest_latitude=28.6253, dest_longitude=77.2190,
            start_time=base_date + timedelta(hours=9), end_time=base_date + timedelta(hours=9, minutes=45),
            status="confirmed", cost=800.0, currency="INR", booking_reference="UBER-DEL-001",
            flexibility="high", importance="high",
            details={"vehicle_type": "Premier Sedan"}, sequence_order=2
        )
        nodes.append(n2)

        # 3. Hotel Delhi
        n3 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="hotel",
            provider="The Imperial New Delhi", location="New Delhi",
            latitude=28.6253, longitude=77.2190,
            start_time=base_date + timedelta(hours=10), end_time=base_date + timedelta(days=1, hours=6),
            status="confirmed", cost=12000.0, currency="INR", booking_reference="IMP-2024-DEMO",
            flexibility="medium", importance="high",
            details={"room_type": "Deluxe Room", "check_in": "10:00 AM"}, sequence_order=3
        )
        nodes.append(n3)

        # 4. Activity - Red Fort
        n4 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="activity",
            provider="Delhi Heritage Tours", location="Red Fort, Delhi",
            latitude=28.6562, longitude=77.2410,
            start_time=base_date + timedelta(hours=14), end_time=base_date + timedelta(hours=17),
            status="confirmed", cost=1500.0, currency="INR", booking_reference="DHT-RF-001",
            flexibility="medium", importance="medium",
            details={"activity_name": "Red Fort Heritage Walk"}, sequence_order=4
        )
        nodes.append(n4)

        # 5. Restaurant - Bukhara
        n5 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="restaurant",
            provider="Bukhara, ITC Maurya", location="ITC Maurya, New Delhi",
            latitude=28.5974, longitude=77.1724,
            start_time=base_date + timedelta(hours=19, minutes=30), end_time=base_date + timedelta(hours=21, minutes=30),
            status="confirmed", cost=3000.0, currency="INR", booking_reference="BUK-RES-001",
            flexibility="low", importance="medium",
            details={"cuisine": "North Indian", "party_size": 2}, sequence_order=5
        )
        nodes.append(n5)

        # 6. Flight DEL -> CDG
        n6 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="flight",
            provider="Air France", location="Delhi (DEL)",
            latitude=28.5562, longitude=77.1000,
            destination_location="Paris (CDG)", dest_latitude=49.0097, dest_longitude=2.5479,
            start_time=base_date + timedelta(days=1, hours=7), end_time=base_date + timedelta(days=1, hours=13),
            status="confirmed", cost=35000.0, currency="INR", booking_reference="AF-226-DEMO",
            flexibility="none", importance="critical",
            details={"flight_number": "AF-226", "airline": "Air France", "terminal": "T3"}, sequence_order=6
        )
        nodes.append(n6)

        # 7. Transfer CDG
        n7 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="airport_transfer",
            provider="Paris Airport Shuttle", location="Paris CDG Airport",
            latitude=49.0097, longitude=2.5479,
            destination_location="Le Marais, Paris", dest_latitude=48.8566, dest_longitude=2.3522,
            start_time=base_date + timedelta(days=1, hours=13, minutes=30), end_time=base_date + timedelta(days=1, hours=14, minutes=30),
            status="confirmed", cost=1875.0, currency="INR", booking_reference="PAS-CDG-001",
            flexibility="high", importance="high",
            details={"vehicle_type": "Shared Shuttle"}, sequence_order=7
        )
        nodes.append(n7)

        # 8. Hotel Paris
        n8 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="hotel",
            provider="Hôtel Le Marais", location="Le Marais, Paris",
            latitude=48.8566, longitude=2.3522,
            start_time=base_date + timedelta(days=1, hours=15), end_time=base_date + timedelta(days=3, hours=11),
            status="confirmed", cost=27000.0, currency="INR", booking_reference="HLM-PAR-DEMO",
            flexibility="low", importance="high",
            details={"room_type": "Superior Double"}, sequence_order=8
        )
        nodes.append(n8)

        # 9. Activity - Eiffel Tower
        n9 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="activity",
            provider="Tour Eiffel", location="Eiffel Tower, Paris",
            latitude=48.8584, longitude=2.2945,
            start_time=base_date + timedelta(days=1, hours=16), end_time=base_date + timedelta(days=1, hours=18),
            status="confirmed", cost=1875.0, currency="INR", booking_reference="ET-VIS-001",
            flexibility="low", importance="high",
            details={"activity_name": "Eiffel Tower Summit Visit"}, sequence_order=9
        )
        nodes.append(n9)

        # 10. Restaurant - Le Comptoir
        n10 = JourneyNode(
            id=str(uuid.uuid4()), journey_id=journey.id, type="restaurant",
            provider="Le Comptoir du Panthéon", location="Latin Quarter, Paris",
            latitude=48.8462, longitude=2.3464,
            start_time=base_date + timedelta(days=1, hours=20), end_time=base_date + timedelta(days=1, hours=22),
            status="confirmed", cost=3750.0, currency="INR", booking_reference="LCP-RES-001",
            flexibility="medium", importance="low",
            details={"cuisine": "French Bistro"}, sequence_order=10
        )
        nodes.append(n10)

        for n in nodes:
            db.add(n)
        db.flush()

        # Dependencies
        deps = [
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n1.id, target_node_id=n2.id, relationship_type="connects_to", buffer_minutes=30, is_critical=True),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n2.id, target_node_id=n3.id, relationship_type="depends_on", buffer_minutes=15, is_critical=False),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n3.id, target_node_id=n4.id, relationship_type="precedes", buffer_minutes=240, is_critical=False),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n4.id, target_node_id=n5.id, relationship_type="precedes", buffer_minutes=150, is_critical=False),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n3.id, target_node_id=n6.id, relationship_type="depends_on", buffer_minutes=60, is_critical=True),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n6.id, target_node_id=n7.id, relationship_type="connects_to", buffer_minutes=30, is_critical=True),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n7.id, target_node_id=n8.id, relationship_type="depends_on", buffer_minutes=30, is_critical=False),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n8.id, target_node_id=n9.id, relationship_type="precedes", buffer_minutes=60, is_critical=False),
            JourneyDependency(id=str(uuid.uuid4()), journey_id=journey.id, source_node_id=n9.id, target_node_id=n10.id, relationship_type="precedes", buffer_minutes=120, is_critical=False),
        ]
        for dep in deps:
            db.add(dep)

        # Resilience score
        res_res = resilience_scorer.calculate_score(journey, nodes, deps)
        journey.resilience_score = res_res["score"]

        print("[+] Creating Initial System Notifications...")
        db.add(Notification(
            id=str(uuid.uuid4()), user_id=traveler.id, journey_id=journey.id,
            type="info", title="TripShield Guardian Active",
            message=f"Monitoring '{journey.title}'. Journey Resilience Score: {journey.resilience_score}/100 ({res_res['classification']}).",
            priority="medium", is_read=False, created_at=datetime.utcnow()
        ))

        print("[+] Generating Audit Log Records...")
        db.add(AuditLog(
            id=str(uuid.uuid4()), user_id=traveler.id, journey_id=journey.id,
            event_type="journey_created",
            description=f"Journey '{journey.title}' created with {len(nodes)} components and {len(deps)} dependencies.",
            details={"nodes_count": len(nodes), "resilience_score": journey.resilience_score},
            created_at=datetime.utcnow()
        ))

        db.commit()
        print("[SUCCESS] Database seeding successfully completed!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding error: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
