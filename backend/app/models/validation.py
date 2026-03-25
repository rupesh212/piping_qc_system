import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RuleResult(str, PyEnum):
    pass_ = "pass"
    fail = "fail"
    warning = "warning"


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iso_id = Column(UUID(as_uuid=True), ForeignKey("iso_drawings.id"), nullable=False)
    line_list_id = Column(UUID(as_uuid=True), ForeignKey("line_list_entries.id"), nullable=True)
    pms_id = Column(UUID(as_uuid=True), ForeignKey("pms_entries.id"), nullable=True)
    rule_name = Column(String, nullable=False)
    result = Column(Enum(RuleResult, values_callable=lambda e: [m.value for m in e]), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    iso = relationship("ISODrawing", back_populates="validation_results")
    line_list_entry = relationship("LineListEntry", back_populates="validation_results")
    pms_entry = relationship("PMSEntry", back_populates="validation_results")
