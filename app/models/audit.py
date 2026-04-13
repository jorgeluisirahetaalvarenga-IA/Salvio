from sqlalchemy import Column, String, DateTime, JSON, Text, Index
from sqlalchemy.dialects.mysql import BINARY, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    tenant_id = Column(String(50), nullable=True)
    user_id = Column(BINARY(16), nullable=True)
    action = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(BINARY(16), nullable=True)   # ← BINARY(16) en lugar de String(36)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    __table_args__ = (
        Index("idx_audit_tenant", "tenant_id"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_table", "table_name"),
        Index("idx_audit_record", "record_id"),
        Index("idx_audit_created", "created_at"),
        Index("idx_audit_user_action", "user_id", "action", "created_at"),
        # Particionamiento se define en la migración raw, no en SQLAlchemy
    )