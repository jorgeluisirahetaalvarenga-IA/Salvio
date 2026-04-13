from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class WaMessageStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    delivered = "delivered"
    read = "read"

class WaMessage(Base):
    __tablename__ = "wa_messages"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    patient_id = Column(BINARY(16), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    appointment_id = Column(BINARY(16), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    message_type = Column(String(50), nullable=True)
    template_name = Column(String(100), nullable=True)
    status = Column(SQLEnum(WaMessageStatus), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_wa_patient", "patient_id"),
        Index("idx_wa_tenant", "tenant_id"),
        Index("idx_wa_status", "tenant_id", "status", "created_at"),
    )