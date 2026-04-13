from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class LabOrderStatus(str, enum.Enum):
    ordered = "ordered"
    collected = "collected"
    processing = "processing"
    completed = "completed"
    cancelled = "cancelled"

class LabOrder(Base):
    __tablename__ = "lab_orders"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    clinical_record_id = Column(BINARY(16), ForeignKey("clinical_records.id", ondelete="SET NULL"), nullable=True)
    ordered_by = Column(BINARY(16), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    lab_test_id = Column(BINARY(16), ForeignKey("lab_tests_catalog.id", ondelete="SET NULL"), nullable=True)
    test_name = Column(String(255), nullable=False)
    order_datetime = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(SQLEnum(LabOrderStatus), nullable=False, default="ordered")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_labord_patient", "patient_id"),
        Index("idx_labord_tenant", "tenant_id"),
        Index("idx_labord_status", "tenant_id", "status", "order_datetime"),
    )

class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    lab_order_id = Column(BINARY(16), ForeignKey("lab_orders.id", ondelete="RESTRICT"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    result_value = Column(String(255), nullable=True)
    reference_range = Column(String(255), nullable=True)
    is_abnormal = Column(Boolean, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    resulted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_labres_order", "lab_order_id"),
        Index("idx_labres_tenant", "tenant_id"),
    )