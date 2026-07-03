import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from backend.app.database import Base

class EventType(enum.Enum):
    CONSULTATION = "CONSULTATION"
    REPORT = "REPORT"
    PRESCRIPTION = "PRESCRIPTION"
    LAB = "LAB"
    MEDICATION = "MEDICATION"
    NOTE = "NOTE"

class HealthEvent(Base):
    __tablename__ = "health_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String, index=True, nullable=False) # Maps to Firebase UID
    event_type = Column(Enum(EventType), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    event_date = Column(DateTime, default=datetime.utcnow, index=True)
    metadata_json = Column(JSON, nullable=True) # Any additional context, original ID reference, etc
    created_at = Column(DateTime, default=datetime.utcnow)

class HealthInsight(Base):
    __tablename__ = "health_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False) # e.g. TREND, RISK, RECOMMENDATION, COMPARISON
    confidence = Column(Float, default=0.0) # 0 to 1
    created_at = Column(DateTime, default=datetime.utcnow)
