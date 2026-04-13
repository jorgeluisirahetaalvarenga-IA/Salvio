from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Text, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base

# =====================================================================
# 019 · PATIENT DEVELOPMENT RECORDS (hitos individuales)
# =====================================================================
class PatientDevelopmentRecord(Base):
    __tablename__ = "patient_development_records"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    milestone_id = Column(BINARY(16), ForeignKey("development_milestones_config.id", ondelete="RESTRICT"), nullable=False)
    achieved_at = Column(Date, nullable=True)
    delay_alert = Column(Boolean, nullable=False, default=False)
    recorded_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_devrec_patient", "patient_id"),
        Index("idx_devrec_milestone", "milestone_id"),
        Index("idx_devrec_delay", "delay_alert"),
        Index("idx_devrec_tenant", "tenant_id"),
    )