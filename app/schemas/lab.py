from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, model_validator

from app.models.lab import LabOrderStatus, SpecimenStatus
from app.schemas.common import ClinicalAlert, ORMModel, StrippedStringMixin


class LabOrderBase(StrippedStringMixin, ORMModel):
    patient_id: UUID
    tenant_id: str = Field(max_length=50)
    clinical_record_id: UUID | None = None
    ordered_by: UUID
    lab_test_id: UUID | None = None
    test_name: str = Field(min_length=1, max_length=255)
    order_datetime: datetime | None = None
    status: LabOrderStatus = LabOrderStatus.ordered
    notes: str | None = None


class LabOrderCreate(LabOrderBase):
    items: list["LabOrderItemCreate"] = Field(default_factory=list)


class LabOrderUpdate(StrippedStringMixin, ORMModel):
    status: LabOrderStatus | None = None
    notes: str | None = None


class LabOrderRead(LabOrderBase):
    id: UUID
    created_at: datetime


class LabOrderItemBase(StrippedStringMixin, ORMModel):
    lab_order_id: UUID | None = None
    tenant_id: str = Field(max_length=50)
    lab_test_id: UUID | None = None
    test_code: str | None = Field(default=None, max_length=20)
    test_name: str = Field(min_length=1, max_length=255)
    specimen_type: str | None = Field(default=None, max_length=100)
    status: LabOrderStatus = LabOrderStatus.ordered
    notes: str | None = None


class LabOrderItemCreate(LabOrderItemBase):
    pass


class LabOrderItemRead(LabOrderItemBase):
    id: UUID
    lab_order_id: UUID
    created_at: datetime


class LabSpecimenBase(StrippedStringMixin, ORMModel):
    lab_order_id: UUID
    tenant_id: str = Field(max_length=50)
    specimen_type: str = Field(min_length=1, max_length=100)
    barcode: str | None = Field(default=None, max_length=100)
    collected_by: UUID | None = None
    collected_at: datetime | None = None
    received_at: datetime | None = None
    rejection_reason: str | None = None
    status: SpecimenStatus = SpecimenStatus.pending


class LabSpecimenCreate(LabSpecimenBase):
    pass


class LabSpecimenRead(LabSpecimenBase):
    id: UUID
    created_at: datetime


class LabResultBase(StrippedStringMixin, ORMModel):
    lab_order_id: UUID
    lab_order_item_id: UUID | None = None
    tenant_id: str = Field(max_length=50)
    analyte_name: str | None = Field(default=None, max_length=255)
    result_value: str | None = Field(default=None, max_length=255)
    numeric_value: Decimal | None = None
    unit: str | None = Field(default=None, max_length=50)
    reference_range: str | None = Field(default=None, max_length=255)
    is_abnormal: bool | None = None
    abnormal_flag: str | None = Field(default=None, max_length=20)
    pdf_url: str | None = Field(default=None, max_length=500)
    resulted_at: datetime | None = None
    verified_by: UUID | None = None
    verified_at: datetime | None = None
    critical_low: Decimal | None = None
    critical_high: Decimal | None = None
    alert: ClinicalAlert = Field(default_factory=ClinicalAlert)

    @model_validator(mode="after")
    def calculate_lab_alert(self):
        if self.numeric_value is not None:
            if self.critical_low is not None and self.numeric_value < self.critical_low:
                self.is_abnormal = True
                self.abnormal_flag = self.abnormal_flag or "critical_low"
                self.alert.alert_triggered = True
                self.alert.alert_type.append("lab_critical_low")
                self.alert.alert_messages.append("Lab result is below the configured critical low threshold.")
            if self.critical_high is not None and self.numeric_value > self.critical_high:
                self.is_abnormal = True
                self.abnormal_flag = self.abnormal_flag or "critical_high"
                self.alert.alert_triggered = True
                self.alert.alert_type.append("lab_critical_high")
                self.alert.alert_messages.append("Lab result is above the configured critical high threshold.")
        return self


class LabResultCreate(LabResultBase):
    pass


class LabResultRead(LabResultBase):
    id: UUID
    created_at: datetime


class LabOrderDetail(LabOrderRead):
    items: list[LabOrderItemRead] = Field(default_factory=list)
    specimens: list[LabSpecimenRead] = Field(default_factory=list)
    results: list[LabResultRead] = Field(default_factory=list)
