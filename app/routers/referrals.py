from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_roles
from app.dependencies.db import get_db
from app.models.appointment import AdmissionStatus, PatientAdmission
from app.models.referral import Interconsult, PublicAccessToken, Referral, ReferralStatus, ReferralType
from app.models.tenant import User, UserRole
from app.routers._utils import audit_mutation, commit_or_409, data_for_create, data_for_model, get_by_id_or_404, model_to_dict
from app.schemas.referral import InterconsultCreate, InterconsultRead, ReferralCreate, ReferralRead
from app.services.referral_service import create_referral as svc_create_referral

router = APIRouter(prefix="/api/v1/referrals", tags=["Referrals"])


@router.post("/interconsults", response_model=InterconsultRead, status_code=status.HTTP_201_CREATED)
def create_interconsult(
    data: InterconsultCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.doctor, UserRole.resident)),
):
    interconsult = Interconsult(**data_for_create(data, Interconsult, tenant_id=current_user.tenant_id))
    db.add(interconsult)
    db.flush()
    audit_mutation(db, request, current_user, action="create", table_name="interconsults", record_id=interconsult.id, new_values=model_to_dict(interconsult))
    commit_or_409(db)
    db.refresh(interconsult)
    return interconsult


@router.post("", response_model=ReferralRead, status_code=status.HTTP_201_CREATED)
def create_referral(
    data: ReferralCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.doctor, UserRole.resident)),
):
    return svc_create_referral(db, current_user.tenant_id, data, current_user.id)


@router.get("/{referral_id}", response_model=ReferralRead)
def get_referral(referral_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_by_id_or_404(db, Referral, referral_id, current_user.tenant_id)
