from sqlalchemy.orm import Session
from app.models.operational import Notification

class NotificationService:
    def create_notification(self, db: Session, user_id: str, journey_id: str, type: str, title: str, message: str, priority: str = 'medium'):
        notif = Notification(
            user_id=user_id,
            journey_id=journey_id,
            type=type,
            title=title,
            message=message,
            priority=priority
        )
        db.add(notif)
        db.commit()
        return notif
