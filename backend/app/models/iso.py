import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ISOStatus(str, PyEnum):
    pending = "pending"
    processed = "processed"
    error = "error"


class ISODrawing(Base):
    __tablename__ = "iso_drawings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_name = Column(String, nullable=False, default="")
    line_number = Column(String, nullable=True)
    pipe_size = Column(String, nullable=True)
    spec = Column(String, nullable=True)
    weld_count = Column(Integer, nullable=True)
    raw_ocr_text = Column(Text, nullable=True)
    status = Column(Enum(ISOStatus), default=ISOStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    uploader = relationship("User", back_populates="iso_drawings")
    validation_results = relationship("ValidationResult", back_populates="iso")
    line_list_entries = relationship("LineListEntry", back_populates="iso")
