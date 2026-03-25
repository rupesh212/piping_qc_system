from typing import Optional
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_isos: int
    total_lines: int
    total_validations: int
    total_errors: int
    pass_rate: float


class ErrorItem(BaseModel):
    id: str
    iso_id: str
    line_number: Optional[str]
    rule_name: str
    message: str
    created_at: str


class LineStatus(BaseModel):
    iso_id: str
    line_number: Optional[str]
    iso_status: str
    validation_status: str
    error_count: int
