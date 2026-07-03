from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from backend.app.database import Base

class PrescriptionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MedicationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String, index=True, nullable=False) # Maps to Firebase sub
    doctor_name = Column(String, nullable=True)
    hospital_name = Column(String, nullable=True)
    prescription_date = Column(DateTime(timezone=True), nullable=True)
    image_path = Column(String, nullable=False)
    
    status = Column(SQLEnum(PrescriptionStatus), default=PrescriptionStatus.PENDING)
    summary = Column(Text, nullable=True) # JSON containing summary, interactions, warnings
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    medicines = relationship("PrescriptionMedicine", back_populates="prescription", cascade="all, delete-orphan")

class PrescriptionMedicine(Base):
    __tablename__ = "prescription_medicines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False)
    
    medicine_name = Column(String, nullable=False)
    strength = Column(String, nullable=True) # e.g. 500mg
    unit = Column(String, nullable=True) # e.g. tablets
    frequency = Column(String, nullable=True) # e.g. 1-0-1 or twice a day
    duration = Column(String, nullable=True) # e.g. 5 days
    route = Column(String, nullable=True) # e.g. Oral
    instructions = Column(Text, nullable=True) # e.g. After meals
    
    # AI generated educational info
    educational_explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prescription = relationship("Prescription", back_populates="medicines")

class MedicationHistory(Base):
    __tablename__ = "medication_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String, index=True, nullable=False) # Maps to Firebase sub
    
    medicine_name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(MedicationStatus), default=MedicationStatus.ACTIVE)
    
    # Store source prescription if applicable
    source_prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
