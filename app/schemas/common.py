from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MessageResponse(ORMModel):
    message: str = "OK"


class PaginationParams(ORMModel):
    q: str | None = Field(default=None, min_length=1, max_length=255)
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=25, ge=1, le=100)


class PaginatedResponse(ORMModel, Generic[T]):
    data: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)


class ClinicalAlert(ORMModel):
    alert_triggered: bool = False
    alert_type: list[str] = Field(default_factory=list)
    alert_messages: list[str] = Field(default_factory=list)


class IdResponse(ORMModel):
    id: UUID
    created_at: datetime | None = None


class UpdatedResponse(ORMModel):
    id: UUID
    updated_at: datetime | None = None


class TimestampMixin(ORMModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SoftDeleteMixin(ORMModel):
    deleted_at: datetime | None = None


class TenantMixin(ORMModel):
    tenant_id: str = Field(min_length=1, max_length=50)


def quantize_decimal(value: Decimal | float | int | None, places: str = "0.01") -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def calculate_bmi(weight: Decimal | float | int | None, height: Decimal | float | int | None) -> Decimal | None:
    if weight is None or height is None:
        return None
    weight_decimal = Decimal(str(weight))
    height_decimal = Decimal(str(height))
    if weight_decimal <= 0 or height_decimal <= 0:
        return None
    height_meters = height_decimal / Decimal("100") if height_decimal > 3 else height_decimal
    bmi = weight_decimal / (height_meters * height_meters)
    return quantize_decimal(bmi)


def append_alert(alert: ClinicalAlert, alert_type: str, message: str) -> None:
    alert.alert_triggered = True
    alert.alert_type.append(alert_type)
    alert.alert_messages.append(message)


def vital_alerts(
    *,
    glasgow_total: int | None = None,
    bp_systolic: int | None = None,
    bp_diastolic: int | None = None,
    spo2: int | None = None,
    temperature: Decimal | float | int | None = None,
    glucometria: int | None = None,
) -> ClinicalAlert:
    alert = ClinicalAlert()
    if glasgow_total is not None and glasgow_total < 12:
        append_alert(alert, "glasgow_low", "Glasgow below 12 requires urgent clinical review.")
    if bp_systolic is not None and bp_systolic > 180:
        append_alert(alert, "hypertensive_crisis", "Systolic blood pressure above 180 mmHg.")
    if bp_diastolic is not None and bp_diastolic > 120:
        append_alert(alert, "hypertensive_crisis", "Diastolic blood pressure above 120 mmHg.")
    if spo2 is not None and spo2 < 88:
        append_alert(alert, "spo2_critical", "Oxygen saturation below 88%.")
    if temperature is not None:
        temp = Decimal(str(temperature))
        if temp >= Decimal("39.5"):
            append_alert(alert, "fever_high", "Temperature at or above 39.5 C.")
        elif temp < Decimal("35.0"):
            append_alert(alert, "hypothermia", "Temperature below 35.0 C.")
    if glucometria is not None:
        if glucometria < 54:
            append_alert(alert, "glucose_low", "Glucometria below 54 mg/dL.")
        elif glucometria > 400:
            append_alert(alert, "glucose_high", "Glucometria above 400 mg/dL.")
    return alert


def patient_age_years(date_of_birth: date) -> int:
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))


class StrippedStringMixin(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def strip_strings(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value
