"""
Audit Service: creates audit log entries for significant system actions.
"""
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    action: str,
    entity_type: str,
    user_id: Optional[Any] = None,
    entity_id: Optional[str] = None,
    details: Optional[dict] = None,
) -> AuditLog:
    """
    Create an audit log entry and persist it to the database.

    Args:
        db: SQLAlchemy session.
        action: Short action label, e.g. "ISO_UPLOAD", "USER_UPDATED".
        entity_type: Domain object type, e.g. "iso", "user", "line_list".
        user_id: UUID of the acting user (None for system actions).
        entity_id: String representation of the affected entity's primary key.
        details: Arbitrary JSON-serialisable dict with extra context.

    Returns:
        The persisted AuditLog instance.
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
