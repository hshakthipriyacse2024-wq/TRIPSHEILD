from sqlalchemy.orm import Session
from app.models.operational import AuditLog

class AuditService:
    def log(self, db: Session, user_id: str, journey_id: str, event_type: str, description: str, details: dict = None, ip_address: str = None):
        log_entry = AuditLog(
            user_id=user_id,
            journey_id=journey_id,
            event_type=event_type,
            description=description,
            details=details or {},
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        return log_entry
