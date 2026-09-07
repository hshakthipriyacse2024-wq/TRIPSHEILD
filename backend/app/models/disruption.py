import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Disruption(Base):
    __tablename__ = "disruptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    affected_node_id = Column(String(36), ForeignKey("journey_nodes.id"))
    type = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=True)
    description = Column(String(1000), nullable=True)
    delay_minutes = Column(Integer, default=0)
    is_simulated = Column(Boolean, default=True)
    status = Column(String(50), default='detected')
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)

    journey = relationship("Journey", back_populates="disruptions")
    impact_analysis = relationship("ImpactAnalysis", back_populates="disruption", uselist=False, cascade="all, delete-orphan")

class ImpactAnalysis(Base):
    __tablename__ = "impact_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    disruption_id = Column(String(36), ForeignKey("disruptions.id"))
    journey_id = Column(String(36), ForeignKey("journeys.id"))
    impact_score = Column(Integer, nullable=True)
    severity_class = Column(String(50), nullable=True)
    nodes_affected = Column(Integer, default=0)
    financial_exposure = Column(Float, default=0)
    currency = Column(String(10), default='INR')
    time_impact_minutes = Column(Integer, default=0)
    scoring_breakdown = Column(JSON, default=dict)
    affected_nodes_detail = Column(JSON, default=list)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    disruption = relationship("Disruption", back_populates="impact_analysis")
    impacted_nodes = relationship("ImpactedNode", back_populates="impact_analysis", cascade="all, delete-orphan")

class ImpactedNode(Base):
    __tablename__ = "impacted_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    impact_analysis_id = Column(String(36), ForeignKey("impact_analyses.id"))
    node_id = Column(String(36), ForeignKey("journey_nodes.id"))
    impact_type = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=True)
    severity_contribution = Column(Integer, default=0)

    impact_analysis = relationship("ImpactAnalysis", back_populates="impacted_nodes")
