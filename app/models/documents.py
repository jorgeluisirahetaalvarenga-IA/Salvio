from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class DocumentCategory(str, enum.Enum):
    identity = "identity"
    consent = "consent"
    clinical = "clinical"
    lab = "lab"
    imaging = "imaging"
    billing = "billing"
    referral = "referral"
    other = "other"

class PatientDocument(Base):
    __tablename__ = "patient_documents"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    clinical_record_id = Column(BINARY(16), ForeignKey("clinical_records.id", ondelete="SET NULL"), nullable=True)
    category = Column(SQLEnum(DocumentCategory), nullable=False, default="other")
    title = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    checksum = Column(String(128), nullable=True)
    uploaded_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_confidential = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_docs_patient", "patient_id"),
        Index("idx_docs_tenant", "tenant_id"),
        Index("idx_docs_record", "clinical_record_id"),
        Index("idx_docs_category", "tenant_id", "category"),
        Index("idx_docs_deleted", "deleted_at"),
    )
