import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ValidationStatus(str, PyEnum):
    pending = "pending"
    valid = "valid"
    mismatch = "mismatch"


class LineListEntry(Base):
    __tablename__ = "line_list_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iso_id = Column(UUID(as_uuid=True), ForeignKey("iso_drawings.id"), nullable=True)
    batch_id = Column(String, nullable=False, index=True)
    line_number = Column(String, nullable=False, index=True)
    pipe_size = Column(String, nullable=False)
    spec = Column(String, nullable=False)
    from_equipment = Column(String, nullable=True)
    to_equipment = Column(String, nullable=True)
    fluid = Column(String, nullable=True)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.pending)
    mismatch_fields = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    iso = relationship("ISODrawing", back_populates="line_list_entries")
    validation_results = relationship("ValidationResult", back_populates="line_list_entry")
