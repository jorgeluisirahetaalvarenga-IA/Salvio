from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth import require_roles
from app.dependencies.db import get_db
from app.models.clinical import ClinicalRecord, ClinicalRecordStatus, RecordDiagnosis
from app.models.tenant import User, UserRole
from app.routers._utils import audit_mutation, commit_or_409, data_for_create, data_for_model, get_by_id_or_404, model_to_dict, uuid_bytes
from app.schemas.clinical import RecordDiagnosisCreate, RecordDiagnosisRead, RecordDiagnosisUpdate
from app.services.clinical_service import verify_primary_diagnosis

router = APIRouter(prefix="/api/v1/record-diagnoses", tags=["Diagnoses"])


def _clinical_record_for_diagnosis(db: Session, clinical_record_id: UUID, tenant_id: str) -> ClinicalRecord:
    record = get_by_id_or_404(db, ClinicalRecord, clinical_record_id, tenant_id)
    if record.status == ClinicalRecordStatus.signed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Signed clinical records are immutable.")
    return record


def _ensure_single_primary(db: Session, data_primary: bool | None, clinical_record_id: bytes, tenant_id: str, exclude_id: bytes | None = None) -> None:
    if not data_primary:
        return
    query = db.query(RecordDiagnosis).filter(
        RecordDiagnosis.clinical_record_id == clinical_record_id,
        RecordDiagnosis.tenant_id == tenant_id,
        RecordDiagnosis.is_primary_diagnosis.is_(True),
    )
    if exclude_id is not None:
        query = query.filter(RecordDiagnosis.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only one primary diagnosis is allowed per clinical record.")


@router.post("", response_model=RecordDiagnosisRead, status_code=status.HTTP_201_CREATED)
def create_diagnosis(
    data: RecordDiagnosisCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.doctor, UserRole.resident)),
):
    record = _clinical_record_for_diagnosis(db, data.clinical_record_id, current_user.tenant_id)
    _ensure_single_primary(db, data.is_primary_diagnosis, record.id, current_user.tenant_id)
    diagnosis = RecordDiagnosis(**data_for_create(data, RecordDiagnosis, tenant_id=current_user.tenant_id))
    db.add(diagnosis)
    db.flush()
    audit_mutation(db, request, current_user, action="create", table_name="record_diagnoses", record_id=diagnosis.id, new_values=model_to_dict(diagnosis))
    commit_or_409(db)
    db.refresh(diagnosis)
    return diagnosis


@router.patch("/{diagnosis_id}", response_model=RecordDiagnosisRead)
def update_diagnosis(
    diagnosis_id: UUID,
    data: RecordDiagnosisUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.doctor, UserRole.resident)),
):
    diagnosis = (
        db.query(RecordDiagnosis)
        .filter(RecordDiagnosis.id == uuid_bytes(diagnosis_id), RecordDiagnosis.tenant_id == current_user.tenant_id)
        .first()
    )
    if not diagnosis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis not found.")
    _clinical_record_for_diagnosis(db, __import__("uuid").UUID(bytes=diagnosis.clinical_record_id), current_user.tenant_id)
    _ensure_single_primary(db, data.is_primary_diagnosis, diagnosis.clinical_record_id, current_user.tenant_id, exclude_id=diagnosis.id)
    old = model_to_dict(diagnosis)
    for key, value in data_for_model(data, RecordDiagnosis).items():
        setattr(diagnosis, key, value)
    audit_mutation(db, request, current_user, action="update", table_name="record_diagnoses", record_id=diagnosis.id, old_values=old, new_values=model_to_dict(diagnosis))
    commit_or_409(db)
    db.refresh(diagnosis)
    return diagnosis
