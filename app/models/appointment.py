from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, SmallInteger, Index
from sqlalchemy.dialects.mysql import BINARY, TINYINT
from sqlalchemy.sql import func
from app.database import Base
import enum

class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    checked_in = "checked_in"
    in_consultation = "in_consultation"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"
    rescheduled = "rescheduled"

class AdmissionStatus(str, enum.Enum):
    active = "active"
    discharged = "discharged"
    transferred = "transferred"

class TriagePriority(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    doctor_id = Column(BINARY(16), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    appointment_type = Column(String(100), nullable=True)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default="scheduled")
    notes = Column(Text, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_appt_patient", "patient_id"),
        Index("idx_appt_tenant", "tenant_id"),
        Index("idx_appt_doctor_date", "doctor_id", "scheduled_at"),
        Index("idx_appt_tenant_status", "tenant_id", "status", "scheduled_at"),
        Index("idx_appt_deleted", "deleted_at"),
    )

class PatientAdmission(Base):
    __tablename__ = "patient_admissions"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    admission_datetime = Column(DateTime, nullable=False)
    discharge_datetime = Column(DateTime, nullable=True)
    service = Column(String(100), nullable=True)
    bed_number = Column(String(20), nullable=True)
    admitting_doctor = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    admitting_doctor_name = Column(String(255), nullable=True)
    diagnosis_on_admission = Column(Text, nullable=True)
    discharge_diagnosis_cie10 = Column(String(10), nullable=True)
    status = Column(SQLEnum(AdmissionStatus), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_admissions_patient", "patient_id"),
        Index("idx_admissions_tenant", "tenant_id"),
        Index("idx_admissions_status", "tenant_id", "status"),
        Index("idx_admissions_service", "tenant_id", "service"),
    )

class TriageRecord(Base):
    __tablename__ = "triage_records"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    appointment_id = Column(BINARY(16), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    admission_id = Column(BINARY(16), ForeignKey("patient_admissions.id", ondelete="SET NULL"), nullable=True)
    received_at = Column(DateTime, nullable=False)
    triage_at = Column(DateTime, nullable=True)
    nursing_prep_at = Column(DateTime, nullable=True)
    priority = Column(SQLEnum(TriagePriority), nullable=False)
    area = Column(String(100), nullable=True)
    systolic_bp = Column(SmallInteger, nullable=True)
    diastolic_bp = Column(SmallInteger, nullable=True)
    heart_rate = Column(SmallInteger, nullable=True)
    resp_rate = Column(TINYINT, nullable=True)
    temperature = Column(DECIMAL(4,1), nullable=True)
    spo2 = Column(TINYINT, nullable=True)
    glasgow_total = Column(TINYINT, nullable=True)
    chief_complaint = Column(Text, nullable=True)
    created_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_triage_patient", "patient_id"),
        Index("idx_triage_tenant", "tenant_id"),
        Index("idx_triage_priority", "tenant_id", "priority", "received_at"),
        Index("idx_triage_received", "received_at"),
    )