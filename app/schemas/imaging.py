from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.imaging import ImagingStatus
from app.schemas.common import ORMModel, StrippedStringMixin


class ImagingStudyBase(StrippedStringMixin, ORMModel):
    patient_id: UUID
    tenant_id: str = Field(max_length=50)
    clinical_record_id: UUID | None = None
    study_type: str = Field(min_length=1, max_length=100)
    body_part: str | None = Field(default=None, max_length=100)
    ordered_by: UUID | None = None
    order_datetime: datetime | None = None
    performed_at: datetime | None = None
    result_summary: str | None = None
    pdf_url: str | None = Field(default=None, max_length=500)
    dicom_url: str | None = Field(default=None, max_length=500)
    status: ImagingStatus = ImagingStatus.ordered


class ImagingStudyCreate(ImagingStudyBase):
    pass


class ImagingStudyUpdate(StrippedStringMixin, ORMModel):
    performed_at: datetime | None = None
    result_summary: str | None = None
    pdf_url: str | None = Field(default=None, max_length=500)
    dicom_url: str | None = Field(default=None, max_length=500)
    status: ImagingStatus | None = None


class ImagingStudyRead(ImagingStudyBase):
    id: UUID
    created_at: datetime


class ImagingReportBase(StrippedStringMixin, ORMModel):
    imaging_study_id: UUID
    tenant_id: str = Field(max_length=50)
    radiologist_id: UUID | None = None
    radiologist_name: str | None = Field(default=None, max_length=255)
    findings: str | None = None
    impression: str | None = None
    recommendations: str | None = None
    signed_at: datetime | None = None


class ImagingReportCreate(ImagingReportBase):
    pass


class ImagingReportRead(ImagingReportBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class ImagingAttachmentBase(StrippedStringMixin, ORMModel):
    imaging_study_id: UUID
    tenant_id: str = Field(max_length=50)
    file_url: str = Field(min_length=1, max_length=500)
    file_type: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    uploaded_by: UUID | None = None


class ImagingAttachmentCreate(ImagingAttachmentBase):
    pass


class ImagingAttachmentRead(ImagingAttachmentBase):
    id: UUID
    created_at: datetime


class ImagingStudyDetail(ImagingStudyRead):
    reports: list[ImagingReportRead] = Field(default_factory=list)
    attachments: list[ImagingAttachmentRead] = Field(default_factory=list)
