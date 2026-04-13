import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.appointment import AdmissionStatus, PatientAdmission
from app.models.referral import PublicAccessToken, Referral, ReferralStatus, ReferralType
from app.schemas.referral import ReferralCreate
from app.services._utils import audit, commit_or_409, data_for_model, model_to_dict, new_uuid_bytes, not_found


def create_referral(db: Session, tenant_id: str, data: ReferralCreate, user_id: bytes) -> Referral:
    referral = Referral(**data_for_model(data, Referral, tenant_id=tenant_id))
    referral.id = new_uuid_bytes()
    db.add(referral)
    db.flush()
    if referral.referral_type == ReferralType.public:
        generate_public_token(db, referral.id, referral.patient_id, referral.clinical_record_id)
    audit(db, user_id=user_id, tenant_id=tenant_id, action="INSERT", table_name="referrals", record_id=referral.id, new_values=model_to_dict(referral))
    commit_or_409(db)
    db.refresh(referral)
    return referral


def generate_public_token(db: Session, referral_id: bytes, patient_id: bytes, clinical_record_id: bytes) -> PublicAccessToken:
    token = PublicAccessToken(
        id=new_uuid_bytes(),
        referral_id=referral_id,
        patient_id=patient_id,
        clinical_record_id=clinical_record_id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=72),
    )
    db.add(token)
    return token


def accept_internal_transfer(db: Session, referral_id: bytes, tenant_id: str, user_id: bytes) -> Referral:
    referral = db.query(Referral).filter(Referral.id == referral_id, Referral.tenant_id == tenant_id).first()
    if not referral:
        raise not_found("Referral not found.")
    if referral.referral_type != ReferralType.internal_transfer:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Referral is not an internal transfer.")
    old_referral = model_to_dict(referral)
    admission = (
        db.query(PatientAdmission)
        .filter(PatientAdmission.patient_id == referral.patient_id, PatientAdmission.tenant_id == tenant_id, PatientAdmission.status == AdmissionStatus.active)
        .first()
    )
    if admission:
        old_admission = model_to_dict(admission)
        admission.service = referral.destination_area
        audit(db, user_id=user_id, tenant_id=tenant_id, action="UPDATE", table_name="patient_admissions", record_id=admission.id, old_values=old_admission, new_values=model_to_dict(admission))
    referral.status = ReferralStatus.accepted
    audit(db, user_id=user_id, tenant_id=tenant_id, action="UPDATE", table_name="referrals", record_id=referral.id, old_values=old_referral, new_values=model_to_dict(referral))
    commit_or_409(db)
    db.refresh(referral)
    return referral
