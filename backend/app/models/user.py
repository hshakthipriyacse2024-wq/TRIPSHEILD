import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(String(50), default="traveler")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    preferences = relationship("TravelerPreference", back_populates="user", uselist=False)

class TravelerPreference(Base):
    __tablename__ = "traveler_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    budget_priority = Column(Integer, default=50)
    speed_priority = Column(Integer, default=70)
    comfort_priority = Column(Integer, default=60)
    minimal_changes_priority = Column(Integer, default=50)
    preferred_airlines = Column(JSON, default=list)
    preferred_transport = Column(JSON, default=list)
    max_connections = Column(Integer, default=2)
    preferred_hotel_category = Column(String(50), nullable=True)
    accessibility_requirements = Column(JSON, default=list)
    important_activities = Column(JSON, default=list)
    non_negotiable_bookings = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")
