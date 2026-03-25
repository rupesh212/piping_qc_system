import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_qa_or_admin
from app.database import get_db
from app.models.pms import PMSEntry
from app.models.user import User
from app.schemas.pms import PMSBatchOut, PMSEntryOut
from app.services.excel_service import parse_pms
from app.utils.file_utils import ALLOWED_EXCEL_TYPES, save_upload_file, validate_file_type

router = APIRouter()


@router.post("/upload", response_model=PMSBatchOut)
def upload_pms(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_qa_or_admin),
):
    validate_file_type(file, ALLOWED_EXCEL_TYPES)
    file_path = save_upload_file(file, "pms")

    try:
        rows = parse_pms(file_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse PMS Excel file: {e}")

    if not rows:
        raise HTTPException(status_code=422, detail="No valid rows found in the PMS Excel file")

    batch_id = str(uuid.uuid4())
    entries = []
    for row in rows:
        # Normalize spec_code to uppercase for consistent matching
        row["spec_code"] = row["spec_code"].upper()
        entry = PMSEntry(batch_id=batch_id, **row)
        db.add(entry)
        entries.append(entry)

    db.commit()
    for e in entries:
        db.refresh(e)

    return {"batch_id": batch_id, "total": len(entries), "items": entries}


@router.get("/", response_model=list[dict])
def list_batches(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (
        db.query(PMSEntry.batch_id)
        .distinct()
        .order_by(PMSEntry.batch_id)
        .all()
    )
    return [{"batch_id": r.batch_id} for r in rows]


@router.get("/{batch_id}", response_model=PMSBatchOut)
def get_batch(
    batch_id: str,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(PMSEntry).filter(PMSEntry.batch_id == batch_id)

    if search:
        pattern = f"%{search}%"
        query = query.filter(PMSEntry.spec_code.ilike(pattern))

    total = query.count()
    if total == 0 and not search:
        raise HTTPException(status_code=404, detail="PMS batch not found")

    entries = query.order_by(PMSEntry.created_at).offset(skip).limit(limit).all()
    return {"batch_id": batch_id, "total": total, "skip": skip, "limit": limit, "items": entries}
