from sqlalchemy.orm import Session
from app.models.journey import Journey, JourneyNode, JourneyDependency
from app.schemas.journey import JourneyCreate

class JourneyService:
    def create_journey(self, db: Session, user_id: str, data: JourneyCreate) -> Journey:
        journey = Journey(
            user_id=user_id,
            title=data.title,
            description=data.description,
            origin=data.origin,
            destination=data.destination,
            start_date=data.start_date,
            end_date=data.end_date
        )
        db.add(journey)
        db.commit()
        db.refresh(journey)
        return journey

    def get_journey(self, db: Session, journey_id: str, user_id: str) -> Journey:
        return db.query(Journey).filter(Journey.id == journey_id, Journey.user_id == user_id).first()
        
    def get_digital_twin(self, db: Session, journey_id: str) -> dict:
        journey = db.query(Journey).filter(Journey.id == journey_id).first()
        if not journey: return None
        return {
            "journey": journey,
            "nodes": journey.nodes,
            "dependencies": journey.dependencies,
            "resilience_score": journey.resilience_score
        }
