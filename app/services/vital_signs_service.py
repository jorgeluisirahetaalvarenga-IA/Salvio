from datetime import timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.clinical import VitalSign
from app.schemas.clinical import VitalSignCreate
from app.schemas.common import ClinicalAlert
from app.services._utils import audit, commit_or_409, data_for_model, model_to_dict


def calculate_glasgow(ocular: int | None, verbal: int | None, motor: int | None) -> int | None:
    if ocular is None or verbal is None or motor is None:
        return None
    return ocular + verbal + motor


def calculate_bmi(weight_kg: Decimal | None, height_cm: Decimal | None) -> Decimal | None:
    if weight_kg is None or height_cm is None or weight_kg <= 0 or height_cm <= 0:
        return None
    height_m = Decimal(str(height_cm)) / Decimal("100")
    bmi = Decimal(str(weight_kg)) / (height_m**2)
    return bmi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _append(alert: ClinicalAlert, alert_type: str, message: str) -> None:
    alert.alert_triggered = True
    alert.alert_type.append(alert_type)
    alert.alert_messages.append(message)


def evaluate_vital_alerts(
    *,
    glasgow_total: int | None = None,
    bp_systolic: int | None = None,
    bp_diastolic: int | None = None,
    spo2: int | None = None,
    temperature: Decimal | None = None,
    glucometria: int | None = None,
) -> ClinicalAlert:
    alert = ClinicalAlert()
    if glasgow_total is not None and glasgow_total < 12:
        _append(alert, "glasgow_low", "Glasgow below 12 - urgent review required")
    if bp_systolic is not None and bp_systolic > 180:
        _append(alert, "hypertensive_crisis", "Systolic BP above 180 mmHg")
    if bp_diastolic is not None and bp_diastolic > 120:
        _append(alert, "hypertensive_crisis", "Diastolic BP above 120 mmHg")
    if spo2 is not None and spo2 < 88:
        _append(alert, "spo2_critical", "SpO2 below 88%")
    if temperature is not None and temperature >= Decimal("39.5"):
        _append(alert, "fever_high", "Temperature at or above 39.5 C")
    if temperature is not None and temperature < Decimal("35.0"):
        _append(alert, "hypothermia", "Temperature below 35.0 C")
    if glucometria is not None and glucometria < 54:
        _append(alert, "glucose_critical_low", "Glucometry below 54 mg/dL")
    if glucometria is not None and glucometria > 400:
        _append(alert, "glucose_critical_high", "Glucometry above 400 mg/dL")
    return alert


def create_vital_sign(db: Session, tenant_id: str, data: VitalSignCreate, user_id: bytes) -> tuple[VitalSign, ClinicalAlert]:
    glasgow_total = calculate_glasgow(data.glasgow_ocular, data.glasgow_verbal, data.glasgow_motor)
    bmi = calculate_bmi(data.weight, data.height)
    alert = evaluate_vital_alerts(
        glasgow_total=glasgow_total,
        bp_systolic=data.bp_systolic,
        bp_diastolic=data.bp_diastolic,
        spo2=data.spo2,
        temperature=data.temperature,
        glucometria=data.glucometria,
    )
    payload = data_for_model(data, VitalSign, exclude={"alert", "bmi_calculated"}, tenant_id=tenant_id)
    payload["glasgow_total"] = glasgow_total
    vital_sign = VitalSign(**payload)
    db.add(vital_sign)
    db.flush()
    audit(db, user_id=user_id, tenant_id=tenant_id, action="INSERT", table_name="vital_signs", record_id=vital_sign.id, new_values=model_to_dict(vital_sign))
    commit_or_409(db)
    db.refresh(vital_sign)
    return vital_sign, alert
