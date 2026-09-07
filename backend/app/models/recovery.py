import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database import Base

class RecoveryStrategy(Base):
    __tablename__ = "recovery_strategies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    disruption_id = Column(String(36), ForeignKey("disruptions.id"))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    changed_components = Column(JSON, default=list)
    preserved_components = Column(JSON, default=list)
    additional_cost = Column(Float, default=0)
    currency = Column(String(10), default='INR')
    time_saved_minutes = Column(Integer, default=0)
    num_changes = Column(Integer, default=0)
    feasibility_score = Column(Float, default=0)
    comfort_score = Column(Float, default=0)
    urgency_score = Column(Float, default=0)
    financial_impact_score = Column(Float, default=0)
    recovery_confidence = Column(Float, default=0)
    overall_score = Column(Float, default=0)
    explanation = Column(Text, nullable=True)
    is_recommended = Column(Boolean, default=False)
    rank = Column(Integer, nullable=True)
    status = Column(String(50), default='proposed')
    actions_detail = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    actions = relationship("RecoveryAction", back_populates="strategy", cascade="all, delete-orphan")

class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String(36), ForeignKey("recovery_strategies.id"))
    original_node_id = Column(String(36), ForeignKey("journey_nodes.id"), nullable=True)
    replacement_node_id = Column(String(36), ForeignKey("journey_nodes.id"), nullable=True)
    action_type = Column(String(50), nullable=False)
    description = Column(String(1000), nullable=True)
    old_details = Column(JSON, default=dict)
    new_details = Column(JSON, default=dict)
    cost_difference = Column(Float, default=0)
    status = Column(String(50), default='pending')
    executed_at = Column(DateTime, nullable=True)

    strategy = relationship("RecoveryStrategy", back_populates="actions")
