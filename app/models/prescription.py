from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class PrescriptionStatus(str, enum.Enum):
    active = "active"
    dispensed = "dispensed"
    cancelled = "cancelled"

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    clinical_record_id = Column(BINARY(16), ForeignKey("clinical_records.id", ondelete="SET NULL"), nullable=True)
    prescribed_by = Column(BINARY(16), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    prescribed_by_name = Column(String(255), nullable=False)
    prescribed_at = Column(DateTime, nullable=False, server_default=func.now())
    pdf_url = Column(String(500), nullable=True)
    status = Column(SQLEnum(PrescriptionStatus), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_rx_patient", "patient_id"),
        Index("idx_rx_tenant", "tenant_id"),
        Index("idx_rx_status", "tenant_id", "status"),
    )