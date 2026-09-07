import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Journey(Base):
    __tablename__ = "journeys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), default='draft') # draft/active/disrupted/recovering/recovered/completed/cancelled
    resilience_score = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    nodes = relationship("JourneyNode", back_populates="journey", cascade="all, delete-orphan")
    dependencies = relationship("JourneyDependency", back_populates="journey", cascade="all, delete-orphan")
    disruptions = relationship("Disruption", back_populates="journey", cascade="all, delete-orphan")

class JourneyNode(Base):
    __tablename__ = "journey_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    type = Column(String(50), nullable=False)
    provider = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    destination_location = Column(String(255), nullable=True)
    dest_latitude = Column(Float, nullable=True)
    dest_longitude = Column(Float, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), default='confirmed')
    cost = Column(Float, nullable=True)
    currency = Column(String(10), default='INR')
    booking_reference = Column(String(100), nullable=True)
    cancellation_policy = Column(JSON, default=dict)
    flexibility = Column(String(50), nullable=True)
    importance = Column(String(50), nullable=True)
    traveler_preference_weight = Column(Float, default=1.0)
    details = Column(JSON, default=dict)
    sequence_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    journey = relationship("Journey", back_populates="nodes")
    source_dependencies = relationship("JourneyDependency", foreign_keys="[JourneyDependency.source_node_id]", back_populates="source_node")
    target_dependencies = relationship("JourneyDependency", foreign_keys="[JourneyDependency.target_node_id]", back_populates="target_node")

class JourneyDependency(Base):
    __tablename__ = "journey_dependencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    source_node_id = Column(String(36), ForeignKey("journey_nodes.id"))
    target_node_id = Column(String(36), ForeignKey("journey_nodes.id"))
    relationship_type = Column(String(50), nullable=False)
    buffer_minutes = Column(Integer, default=60)
    is_critical = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSON, default=dict)

    journey = relationship("Journey", back_populates="dependencies")
    source_node = relationship("JourneyNode", foreign_keys=[source_node_id], back_populates="source_dependencies")
    target_node = relationship("JourneyNode", foreign_keys=[target_node_id], back_populates="target_dependencies")
