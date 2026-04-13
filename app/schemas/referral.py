from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import Field, model_validator

from app.models.referral import InterconsultStatus, ReferralStatus, ReferralType
from app.schemas.common import ORMModel, StrippedStringMixin


class InterconsultBase(StrippedStringMixin, ORMModel):
    patient_id: UUID
    tenant_id: str = Field(max_length=50)
    clinical_record_id: UUID | None = None
    requesting_doctor: UUID
    requesting_doctor_name: str = Field(min_length=1, max_length=255)
    consulting_specialty: str = Field(min_length=1, max_length=100)
    reason: str | None = None
    requested_at: datetime | None = None
    response: str | None = None
    responded_at: datetime | None = None
    status: InterconsultStatus = InterconsultStatus.pending


class InterconsultCreate(InterconsultBase):
    pass


class InterconsultRespond(StrippedStringMixin, ORMModel):
    response: str = Field(min_length=1)
    responded_at: datetime | None = None
    status: InterconsultStatus = InterconsultStatus.completed


class InterconsultRead(InterconsultBase):
    id: UUID
    created_at: datetime


class ReferralBase(StrippedStringMixin, ORMModel):
    patient_id: UUID
    tenant_id: str = Field(max_length=50)
    clinical_record_id: UUID | None = None
    referral_type: ReferralType
    source_service: str | None = Field(default=None, max_length=100)
    destination_area: str | None = Field(default=None, max_length=100)
    transfer_reason: str | None = None
    referred_by: UUID | None = None
    referred_by_name: str | None = Field(default=None, max_length=255)
    target_tenant_id: str | None = Field(default=None, max_length=50)
    status: ReferralStatus = ReferralStatus.pending

    @model_validator(mode="after")
    def validate_referral_type_fields(self):
        if self.referral_type == ReferralType.internal_transfer:
            if not self.source_service or not self.destination_area or not self.transfer_reason:
                raise ValueError("internal_transfer referrals require source_service, destination_area and transfer_reason.")
        if self.referral_type == ReferralType.cross_tenant and not self.target_tenant_id:
            raise ValueError("cross_tenant referrals require target_tenant_id.")
        return self


class ReferralCreate(ReferralBase):
    pass


class ReferralUpdate(StrippedStringMixin, ORMModel):
    source_service: str | None = Field(default=None, max_length=100)
    destination_area: str | None = Field(default=None, max_length=100)
    transfer_reason: str | None = None
    target_tenant_id: str | None = Field(default=None, max_length=50)
    status: ReferralStatus | None = None


class ReferralRead(ReferralBase):
    id: UUID
    created_at: datetime


class PublicAccessTokenCreate(ORMModel):
    referral_id: UUID | None = None
    patient_id: UUID
    clinical_record_id: UUID
    token: str = Field(min_length=32, max_length=255)
    expires_at: datetime

    @model_validator(mode="after")
    def validate_max_72h(self):
        if self.expires_at > datetime.now(timezone.utc) + timedelta(hours=72):
            raise ValueError("public access tokens cannot expire more than 72 hours from now.")
        return self


class PublicAccessTokenRead(PublicAccessTokenCreate):
    id: UUID
    created_at: datetime
