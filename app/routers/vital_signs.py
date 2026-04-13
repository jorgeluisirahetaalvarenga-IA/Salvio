from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_roles
from app.dependencies.db import get_db
from app.models.clinical import ClinicalRecord, ClinicalRecordStatus, VitalSign
from app.models.patient import Patient
from app.models.tenant import User, UserRole
from app.routers._utils import audit_mutation, commit_or_409, data_for_create, ensure_patient_exists, get_by_id_or_404, model_to_dict, uuid_bytes
from app.schemas.clinical import VitalSignCreate, VitalSignRead
from app.services.vital_signs_service import create_vital_sign as svc_create_vital_sign

router = APIRouter(prefix="/api/v1/vital-signs", tags=["Vital Signs"])


@router.post("", response_model=VitalSignRead, status_code=status.HTTP_201_CREATED)
def create_vital_sign(
    data: VitalSignCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.doctor, UserRole.resident, UserRole.nurse)),
):
    ensure_patient_exists(db, Patient, data.patient_id, current_user.tenant_id)
    if data.clinical_record_id:
        record = get_by_id_or_404(db, ClinicalRecord, data.clinical_record_id, current_user.tenant_id)
        if record.status == ClinicalRecordStatus.signed:
            raise __import__("fastapi").HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Signed clinical records are immutable.")
    vital, _alert = svc_create_vital_sign(db, current_user.tenant_id, data, current_user.id)
    return vital


@router.get("", response_model=list[VitalSignRead])
def list_vital_signs(
    patient_id: UUID = Query(...),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_patient_exists(db, Patient, patient_id, current_user.tenant_id)
    return (
        db.query(VitalSign)
        .filter(VitalSign.patient_id == uuid_bytes(patient_id), VitalSign.tenant_id == current_user.tenant_id)
        .order_by(VitalSign.recorded_at.desc())
        .limit(limit)
        .all()
    )
