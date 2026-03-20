import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PMSValidationStatus(str, PyEnum):
    pending = "pending"
    valid = "valid"
    mismatch = "mismatch"


class PMSEntry(Base):
    __tablename__ = "pms_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(String, nullable=False, index=True)
    spec_code = Column(String, nullable=False, index=True)
    material = Column(String, nullable=False)
    rating = Column(String, nullable=False)
    size_range = Column(String, nullable=True)
    end_conn = Column(String, nullable=True)
    validation_status = Column(Enum(PMSValidationStatus), default=PMSValidationStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    validation_results = relationship("ValidationResult", back_populates="pms_entry")
