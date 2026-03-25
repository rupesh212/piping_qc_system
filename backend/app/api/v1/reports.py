"""
Reports router: CSV export endpoints for validation results and line list entries.
"""
import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.iso import ISODrawing
from app.models.line_list import LineListEntry
from app.models.user import User
from app.models.validation import ValidationResult

router = APIRouter()


@router.get("/validation-summary")
def validation_summary_csv(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Export all validation results as a CSV file.

    Columns: iso_id, line_number, pipe_size, spec, rule_name, result, message, created_at
    """
    results = (
        db.query(ValidationResult)
        .order_by(ValidationResult.created_at.desc())
        .all()
    )

    # Pre-fetch ISO data keyed by id to avoid N+1
    iso_ids = list({r.iso_id for r in results})
    isos_by_id: dict = {}
    for iso in db.query(ISODrawing).filter(ISODrawing.id.in_(iso_ids)).all():
        isos_by_id[iso.id] = iso

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["iso_id", "line_number", "pipe_size", "spec", "rule_name", "result", "message", "created_at"]
    )

    for r in results:
        iso = isos_by_id.get(r.iso_id)
        writer.writerow([
            str(r.iso_id),
            iso.line_number if iso else "",
            iso.pipe_size if iso else "",
            iso.spec if iso else "",
            r.rule_name,
            r.result.value if hasattr(r.result, "value") else str(r.result),
            r.message,
            r.created_at.isoformat() if r.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=validation_summary.csv"},
    )


@router.get("/line-list-export/{batch_id}")
def line_list_export_csv(
    batch_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Export all line list entries for a given batch as a CSV file.

    Columns: id, batch_id, line_number, pipe_size, spec,
             from_equipment, to_equipment, fluid, validation_status, created_at
    """
    entries = (
        db.query(LineListEntry)
        .filter(LineListEntry.batch_id == batch_id)
        .order_by(LineListEntry.created_at)
        .all()
    )

    if not entries:
        raise HTTPException(status_code=404, detail="Batch not found")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "batch_id", "line_number", "pipe_size", "spec",
        "from_equipment", "to_equipment", "fluid", "validation_status", "created_at",
    ])

    for entry in entries:
        writer.writerow([
            str(entry.id),
            entry.batch_id,
            entry.line_number,
            entry.pipe_size,
            entry.spec,
            entry.from_equipment or "",
            entry.to_equipment or "",
            entry.fluid or "",
            entry.validation_status.value if hasattr(entry.validation_status, "value") else str(entry.validation_status),
            entry.created_at.isoformat() if entry.created_at else "",
        ])

    output.seek(0)
    safe_batch_id = batch_id.replace("/", "_").replace("\\", "_")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=line_list_{safe_batch_id}.csv"
        },
    )
