from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.pms import PMSValidationStatus


class PMSEntryOut(BaseModel):
    id: UUID
    batch_id: str
    spec_code: str
    material: str
    rating: str
    size_range: Optional[str]
    end_conn: Optional[str]
    validation_status: PMSValidationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class PMSBatchOut(BaseModel):
    batch_id: str
    total: int
    skip: int = 0
    limit: int = 50
    items: list[PMSEntryOut]
