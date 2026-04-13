from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, require_roles
from app.dependencies.db import get_db
from app.models.patient import PatientConsent, PatientConsentType
from app.models.tenant import User, UserRole
from app.models.wa import WaMessage
from app.routers._utils import audit_mutation, commit_or_409, data_for_create, model_to_dict, uuid_bytes
from app.schemas.wa import WaMessageCreate, WaMessageRead
from app.services.wa_service import enqueue_wa_message
from app.services.notification_service import enqueue_whatsapp_message as svc_enqueue_whatsapp_message

router = APIRouter(prefix="/api/v1/wa-messages", tags=["WhatsApp"])


@router.post("", response_model=WaMessageRead, status_code=status.HTTP_201_CREATED)
def create_wa_message(
    data: WaMessageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.clinic_admin, UserRole.doctor, UserRole.receptionist)),
):
    message = svc_enqueue_whatsapp_message(db, current_user.tenant_id, data, current_user.id)
    enqueue_wa_message(message)
    return message


@router.get("", response_model=list[WaMessageRead])
def list_wa_messages(
    patient_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(WaMessage).filter(WaMessage.tenant_id == current_user.tenant_id)
    if patient_id:
        query = query.filter(WaMessage.patient_id == uuid_bytes(patient_id))
    return query.order_by(WaMessage.created_at.desc()).all()
