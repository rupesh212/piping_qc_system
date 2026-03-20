from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.line_list import ValidationStatus


class LineListEntryOut(BaseModel):
    id: UUID
    batch_id: str
    iso_id: Optional[UUID]
    line_number: str
    pipe_size: str
    spec: str
    from_equipment: Optional[str]
    to_equipment: Optional[str]
    fluid: Optional[str]
    validation_status: ValidationStatus
    mismatch_fields: Optional[Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class LineListBatchOut(BaseModel):
    batch_id: str
    total: int
    items: list[LineListEntryOut]
