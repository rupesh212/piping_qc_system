from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_qa_or_admin
from app.database import get_db
from app.models.iso import ISODrawing, ISOStatus
from app.models.user import User
from app.models.validation import ValidationResult, RuleResult
from app.schemas.iso import ISOListOut, ISOOut
from app.services import ocr_service, rule_engine
from app.services.audit_service import log_action
from app.utils.file_utils import (
    ALLOWED_IMAGE_TYPES,
    ALLOWED_PDF_TYPES,
    save_upload_file,
    validate_file_type,
)

router = APIRouter()

ALLOWED_ISO_TYPES = ALLOWED_PDF_TYPES | ALLOWED_IMAGE_TYPES


@router.post("/upload", response_model=ISOOut)
def upload_iso(
    file: UploadFile = File(...),
    project_name: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_qa_or_admin),
):
    validate_file_type(file, ALLOWED_ISO_TYPES)
    file_path = save_upload_file(file, "iso")

    iso = ISODrawing(
        file_name=file.filename,
        file_path=file_path,
        uploaded_by=current_user.id,
        project_name=project_name,
        status=ISOStatus.pending,
    )
    db.add(iso)
    db.commit()
    db.refresh(iso)

    # Run OCR
    try:
        raw_text = ocr_service.extract_text(file_path)
        parsed = ocr_service.parse_iso_data(raw_text)
        iso.raw_ocr_text = raw_text
        iso.line_number = parsed.get("line_number")
        iso.pipe_size = parsed.get("pipe_size")
        iso.spec = parsed.get("spec")
        iso.weld_count = parsed.get("weld_count")
        iso.status = ISOStatus.processed
        iso.processed_at = datetime.utcnow()
    except Exception as e:
        iso.status = ISOStatus.error
        iso.raw_ocr_text = str(e)

    db.commit()
    db.refresh(iso)

    log_action(db, action="ISO_UPLOAD", entity_type="iso", user_id=current_user.id,
               entity_id=str(iso.id),
               details={"file_name": iso.file_name, "project_name": iso.project_name, "status": iso.status.value})
    return iso


@router.get("/", response_model=ISOListOut)
def list_isos(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(ISODrawing)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            ISODrawing.line_number.ilike(pattern) | ISODrawing.project_name.ilike(pattern)
        )

    if status:
        try:
            status_enum = ISOStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status value: '{status}'")
        query = query.filter(ISODrawing.status == status_enum)

    total = query.count()
    items = query.order_by(ISODrawing.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/navisworks-sync")
def navisworks_sync(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    isos = db.query(ISODrawing).order_by(ISODrawing.created_at.desc()).all()

    iso_data = []
    for iso in isos:
        validation_results = (
            db.query(ValidationResult)
            .filter(ValidationResult.iso_id == iso.id)
            .all()
        )
        total_rules = len(validation_results)
        if total_rules > 0:
            pass_count = sum(
                1 for vr in validation_results if vr.result == RuleResult.pass_
            )
            pass_rate = round((pass_count / total_rules) * 100.0, 2)
        else:
            pass_rate = 0.0

        iso_data.append(
            {
                "id": str(iso.id),
                "file_name": iso.file_name,
                "line_number": iso.line_number or "",
                "pipe_size": iso.pipe_size or "",
                "spec": iso.spec or "",
                "weld_count": iso.weld_count if iso.weld_count is not None else 0,
                "status": iso.status.value,
                "validation_pass_rate": pass_rate,
            }
        )

    return {
        "sync_timestamp": datetime.now(timezone.utc).isoformat(),
        "isos": iso_data,
    }


@router.get("/{iso_id}", response_model=ISOOut)
def get_iso(
    iso_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    iso = db.query(ISODrawing).filter(ISODrawing.id == iso_id).first()
    if not iso:
        raise HTTPException(status_code=404, detail="ISO not found")
    return iso


@router.post("/{iso_id}/validate")
def validate_iso(
    iso_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_qa_or_admin),
):
    iso = db.query(ISODrawing).filter(ISODrawing.id == iso_id).first()
    if not iso:
        raise HTTPException(status_code=404, detail="ISO not found")
    if iso.status != ISOStatus.processed:
        raise HTTPException(status_code=400, detail="ISO must be in 'processed' state before validation")

    # Remove previous validation results for this ISO
    db.query(ValidationResult).filter(ValidationResult.iso_id == iso_id).delete()
    db.commit()

    result_dicts = rule_engine.run_validation(iso, db)

    saved = []
    for rd in result_dicts:
        vr = ValidationResult(**rd)
        db.add(vr)
        saved.append(rd)

    db.commit()

    pass_count = sum(1 for r in saved if r["result"] == RuleResult.pass_.value)
    fail_count = sum(1 for r in saved if r["result"] == RuleResult.fail.value)
    warn_count = sum(1 for r in saved if r["result"] == "warning")

    log_action(db, action="ISO_VALIDATE", entity_type="iso", user_id=current_user.id,
               entity_id=str(iso_id),
               details={"passed": pass_count, "failed": fail_count, "warnings": warn_count})
    return {
        "iso_id": str(iso_id),
        "total_rules": len(saved),
        "passed": pass_count,
        "failed": fail_count,
        "warnings": warn_count,
        "results": saved,
    }
