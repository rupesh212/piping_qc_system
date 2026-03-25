import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_qa_or_admin
from app.database import get_db
from app.models.line_list import LineListEntry, ValidationStatus
from app.models.user import User
from app.schemas.line_list import LineListBatchOut, LineListEntryOut
from app.services.excel_service import parse_line_list
from app.utils.file_utils import ALLOWED_EXCEL_TYPES, save_upload_file, validate_file_type

router = APIRouter()


@router.post("/upload", response_model=LineListBatchOut)
def upload_line_list(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_qa_or_admin),
):
    validate_file_type(file, ALLOWED_EXCEL_TYPES)
    file_path = save_upload_file(file, "linelist")

    try:
        rows = parse_line_list(file_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse Excel file: {e}")

    if not rows:
        raise HTTPException(status_code=422, detail="No valid rows found in the Excel file")

    batch_id = str(uuid.uuid4())
    entries = []
    for row in rows:
        entry = LineListEntry(batch_id=batch_id, **row)
        db.add(entry)
        entries.append(entry)

    db.commit()
    for e in entries:
        db.refresh(e)

    return {"batch_id": batch_id, "total": len(entries), "items": entries}


@router.get("/", response_model=list[dict])
def list_batches(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (
        db.query(LineListEntry.batch_id)
        .distinct()
        .order_by(LineListEntry.batch_id)
        .all()
    )
    return [{"batch_id": r.batch_id} for r in rows]


@router.get("/{batch_id}", response_model=LineListBatchOut)
def get_batch(
    batch_id: str,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(LineListEntry).filter(LineListEntry.batch_id == batch_id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(LineListEntry.line_number.ilike(pattern))

    if status:
        try:
            status_enum = ValidationStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status value: '{status}'")
        query = query.filter(LineListEntry.validation_status == status_enum)

    total = query.count()
    if total == 0 and not search and not status:
        raise HTTPException(status_code=404, detail="Batch not found")

    entries = query.order_by(LineListEntry.created_at).offset(skip).limit(limit).all()
    return {"batch_id": batch_id, "total": total, "skip": skip, "limit": limit, "items": entries}
