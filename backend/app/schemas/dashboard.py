from typing import Any
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_isos: int
    total_lines: int
    total_validations: int
    total_errors: int
    pass_rate: float


class ErrorItem(BaseModel):
    iso_id: str
    line_number: str | None
    rule_name: str
    message: str
    created_at: str


class LineStatus(BaseModel):
    line_number: str
    iso_status: str
    validation_status: str
    error_count: int
