import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON, Text
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    journey_id = Column(String(36), ForeignKey("journeys.id"), nullable=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(50), default='medium')
    is_read = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    journey_id = Column(String(36), ForeignKey("journeys.id"), nullable=True)
    event_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    disruption_type = Column(String(50), nullable=False)
    parameters = Column(JSON, default=dict)
    impact_result = Column(JSON, default=dict)
    recovery_options = Column(JSON, default=list)
    resilience_score_before = Column(Integer, nullable=True)
    resilience_score_after = Column(Integer, nullable=True)
    status = Column(String(50), default='running')
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    node_id = Column(String(36), ForeignKey("journey_nodes.id"), nullable=True)
    weather_risk = Column(Float, nullable=True)
    delay_history_risk = Column(Float, nullable=True)
    congestion_risk = Column(Float, nullable=True)
    connection_buffer_risk = Column(Float, nullable=True)
    route_risk = Column(Float, nullable=True)
    provider_reliability = Column(Float, nullable=True)
    overall_risk = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    explanation = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=True)
    assessed_at = Column(DateTime, default=datetime.utcnow)

class Provider(Base):
    __tablename__ = "providers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    is_mock = Column(Boolean, default=True)
    api_endpoint = Column(String(255), nullable=True)
    config = Column(JSON, default=dict)
    status = Column(String(50), default='active')
    last_health_check = Column(DateTime, nullable=True)
