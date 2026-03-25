from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    entity_type: str
    entity_id: Optional[str]
    details: Optional[Any]
    created_at: datetime

    model_config = {"from_attributes": True}
