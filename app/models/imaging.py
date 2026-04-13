from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class ImagingStatus(str, enum.Enum):
    ordered = "ordered"
    performed = "performed"
    reviewed = "reviewed"
    cancelled = "cancelled"

class ImagingStudy(Base):
    __tablename__ = "imaging_studies"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    clinical_record_id = Column(BINARY(16), ForeignKey("clinical_records.id", ondelete="SET NULL"), nullable=True)
    study_type = Column(String(100), nullable=False)
    body_part = Column(String(100), nullable=True)
    ordered_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_datetime = Column(DateTime, nullable=False, server_default=func.now())
    performed_at = Column(DateTime, nullable=True)
    result_summary = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    dicom_url = Column(String(500), nullable=True)
    status = Column(SQLEnum(ImagingStatus), nullable=False, default="ordered")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_img_patient", "patient_id"),
        Index("idx_img_tenant", "tenant_id"),
        Index("idx_img_status", "tenant_id", "status"),
    )