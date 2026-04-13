from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Index, DECIMAL
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

class SpecimenStatus(str, enum.Enum):
    pending = "pending"
    collected = "collected"
    rejected = "rejected"
    received = "received"

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

class LabOrderItem(Base):
    __tablename__ = "lab_order_items"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    lab_order_id = Column(BINARY(16), ForeignKey("lab_orders.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    lab_test_id = Column(BINARY(16), ForeignKey("lab_tests_catalog.id", ondelete="SET NULL"), nullable=True)
    test_code = Column(String(20), nullable=True)
    test_name = Column(String(255), nullable=False)
    specimen_type = Column(String(100), nullable=True)
    status = Column(SQLEnum(LabOrderStatus), nullable=False, default="ordered")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_labitem_order", "lab_order_id"),
        Index("idx_labitem_tenant", "tenant_id"),
        Index("idx_labitem_status", "tenant_id", "status"),
    )

class LabSpecimen(Base):
    __tablename__ = "lab_specimens"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    lab_order_id = Column(BINARY(16), ForeignKey("lab_orders.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    specimen_type = Column(String(100), nullable=False)
    barcode = Column(String(100), nullable=True)
    collected_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    collected_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    status = Column(SQLEnum(SpecimenStatus), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_specimen_order", "lab_order_id"),
        Index("idx_specimen_tenant", "tenant_id"),
        Index("idx_specimen_barcode", "barcode"),
    )

class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    lab_order_id = Column(BINARY(16), ForeignKey("lab_orders.id", ondelete="RESTRICT"), nullable=False)
    lab_order_item_id = Column(BINARY(16), ForeignKey("lab_order_items.id", ondelete="SET NULL"), nullable=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    analyte_name = Column(String(255), nullable=True)
    result_value = Column(String(255), nullable=True)
    numeric_value = Column(DECIMAL(12,4), nullable=True)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(255), nullable=True)
    is_abnormal = Column(Boolean, nullable=True)
    abnormal_flag = Column(String(20), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    resulted_at = Column(DateTime, nullable=True)
    verified_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_labres_order", "lab_order_id"),
        Index("idx_labres_item", "lab_order_item_id"),
        Index("idx_labres_tenant", "tenant_id"),
    )
