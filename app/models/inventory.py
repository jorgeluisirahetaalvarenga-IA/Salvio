from sqlalchemy import Column, String, Boolean, DateTime, Date, Enum as SQLEnum, ForeignKey, Text, DECIMAL, Index
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.sql import func
from app.database import Base
import enum

class InventoryMovementType(str, enum.Enum):
    purchase = "purchase"
    dispensing = "dispensing"
    adjustment = "adjustment"
    transfer = "transfer"
    return_in = "return_in"
    waste = "waste"

class MedicationCatalog(Base):
    __tablename__ = "medication_catalog"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=True)
    medication_code = Column(String(50), nullable=True)
    generic_name = Column(String(255), nullable=False)
    brand_name = Column(String(255), nullable=True)
    concentration = Column(String(100), nullable=True)
    pharmaceutical_form = Column(String(100), nullable=True)
    route = Column(String(100), nullable=True)
    is_controlled = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_medcat_tenant", "tenant_id"),
        Index("idx_medcat_code", "medication_code"),
        Index("idx_medcat_name", "generic_name", "brand_name"),
    )

class MedicationInventory(Base):
    __tablename__ = "medication_inventory"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    medication_id = Column(BINARY(16), ForeignKey("medication_catalog.id", ondelete="RESTRICT"), nullable=False)
    facility_id = Column(BINARY(16), ForeignKey("facilities.id", ondelete="SET NULL"), nullable=True)
    lot_number = Column(String(100), nullable=True)
    expiration_date = Column(Date, nullable=True)
    quantity_on_hand = Column(DECIMAL(12,2), nullable=False, default=0)
    minimum_stock = Column(DECIMAL(12,2), nullable=False, default=0)
    unit = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_medinv_tenant", "tenant_id"),
        Index("idx_medinv_medication", "medication_id"),
        Index("idx_medinv_expiration", "tenant_id", "expiration_date"),
        Index("idx_medinv_lot", "tenant_id", "lot_number"),
    )

class MedicationInventoryMovement(Base):
    __tablename__ = "medication_inventory_movements"
    id = Column(BINARY(16), primary_key=True, server_default="UUID_TO_BIN(UUID())")
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    inventory_id = Column(BINARY(16), ForeignKey("medication_inventory.id", ondelete="CASCADE"), nullable=False)
    prescription_item_id = Column(BINARY(16), ForeignKey("prescription_items.id", ondelete="SET NULL"), nullable=True)
    movement_type = Column(SQLEnum(InventoryMovementType), nullable=False)
    quantity = Column(DECIMAL(12,2), nullable=False)
    reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(BINARY(16), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_medmov_tenant", "tenant_id"),
        Index("idx_medmov_inventory", "inventory_id"),
        Index("idx_medmov_type", "tenant_id", "movement_type", "created_at"),
    )
