from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.iso import ISOStatus


class ISOOut(BaseModel):
    id: UUID
    file_name: str
    project_name: str
    line_number: Optional[str]
    pipe_size: Optional[str]
    spec: Optional[str]
    weld_count: Optional[int]
    status: ISOStatus
    created_at: datetime
    processed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ISOListOut(BaseModel):
    total: int
    items: list[ISOOut]
