from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Index, SmallInteger
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    country = Column(String(2), nullable=False, default="SV")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    clinic_admin = "clinic_admin"
    doctor = "doctor"
    resident = "resident"
    nurse = "nurse"
    receptionist = "receptionist"
    accountant = "accountant"
    patient = "patient"

class User(Base):
    __tablename__ = "users"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        Index("idx_users_tenant", "tenant_id"),
        Index("idx_users_tenant_role", "tenant_id", "role"),
        Index("idx_users_deleted", "deleted_at"),
    )

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    jti = Column(String(255), nullable=False, unique=True)
    user_id = Column(BINARY(16), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    __table_args__ = (Index("idx_revtok_exp", "expires_at"),)

class OtpTokenSms(Base):
    __tablename__ = "otp_tokens_sms"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    user_id = Column(BINARY(16), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(30), nullable=False)
    otp_code_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    __table_args__ = (
        Index("idx_otp_user", "user_id"),
        Index("idx_otp_expires", "expires_at"),
    )

class HcTemplate(Base):
    __tablename__ = "hc_templates"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    specialty = Column(String(100), nullable=False)
    require_insurance_affiliation = Column(Boolean, nullable=False, default=False)
    require_labor_data = Column(Boolean, nullable=False, default=False)
    require_attention_number = Column(Boolean, nullable=False, default=False)
    show_glasgow_scale = Column(Boolean, nullable=False, default=False)
    show_triage = Column(Boolean, nullable=False, default=False)
    show_pediatric_perinatal = Column(Boolean, nullable=False, default=False)
    show_clinical_scales = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    __table_args__ = (Index("uq_hctpl_tenant_specialty", "tenant_id", "specialty", unique=True),)