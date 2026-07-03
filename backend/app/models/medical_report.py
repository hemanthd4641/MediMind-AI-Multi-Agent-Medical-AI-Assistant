from sqlalchemy import Column, String, DateTime, Text, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from backend.app.database import Base

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ParameterStatus(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String, index=True, nullable=False) # Maps to Firebase sub
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    summary = Column(Text, nullable=True)
    educational_notes = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    file_path = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("MedicalReportItem", back_populates="report", cascade="all, delete-orphan")

class MedicalReportItem(Base):
    __tablename__ = "medical_report_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("medical_reports.id"), nullable=False)
    
    parameter_name = Column(String, nullable=False)
    observed_value = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    
    reference_min = Column(Float, nullable=True)
    reference_max = Column(Float, nullable=True)
    
    status = Column(SQLEnum(ParameterStatus), default=ParameterStatus.NORMAL)
    explanation = Column(Text, nullable=True) # Educational explanation for this specific param
    page_number = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("MedicalReport", back_populates="items")
