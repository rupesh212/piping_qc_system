from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.iso import ISODrawing
from app.models.line_list import LineListEntry
from app.models.pms import PMSEntry
from app.models.user import User
from app.models.validation import ValidationResult, RuleResult
from app.schemas.dashboard import DashboardSummary
from app.services.ai_service import AnomalyDetector

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total_isos = db.query(ISODrawing).count()
    total_lines = db.query(LineListEntry).count()
    total_validations = db.query(ValidationResult).count()
    total_errors = (
        db.query(ValidationResult)
        .filter(ValidationResult.result == RuleResult.fail.value)
        .count()
    )
    pass_count = (
        db.query(ValidationResult)
        .filter(ValidationResult.result == RuleResult.pass_.value)
        .count()
    )
    pass_rate = round((pass_count / total_validations * 100), 1) if total_validations > 0 else 0.0

    return DashboardSummary(
        total_isos=total_isos,
        total_lines=total_lines,
        total_validations=total_validations,
        total_errors=total_errors,
        pass_rate=pass_rate,
    )


@router.get("/errors")
def errors(
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Single join query — no N+1
    rows = (
        db.query(ValidationResult, ISODrawing.line_number)
        .outerjoin(ISODrawing, ISODrawing.id == ValidationResult.iso_id)
        .filter(ValidationResult.result == RuleResult.fail.value)
        .order_by(ValidationResult.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(r.id),
            "iso_id": str(r.iso_id),
            "line_number": line_number,
            "rule_name": r.rule_name,
            "message": r.message,
            "created_at": r.created_at.isoformat(),
        }
        for r, line_number in rows
    ]


@router.get("/line-status")
def line_status(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    # Aggregate error counts per ISO in one query
    error_counts_q = (
        db.query(
            ValidationResult.iso_id,
            func.count(ValidationResult.id).label("error_count"),
        )
        .filter(ValidationResult.result == RuleResult.fail.value)
        .group_by(ValidationResult.iso_id)
        .subquery()
    )

    # Fetch the most recent LineListEntry per line_number via a lateral/subquery
    # (simple approach: load distinct line_numbers from top-100 ISOs, then do a
    # single IN query for matching line entries)
    isos = db.query(ISODrawing).order_by(ISODrawing.created_at.desc()).limit(100).all()

    line_numbers = {iso.line_number for iso in isos if iso.line_number}
    line_entries_by_ln: dict[str, LineListEntry] = {}
    if line_numbers:
        rows = (
            db.query(LineListEntry)
            .filter(LineListEntry.line_number.in_(line_numbers))
            .order_by(LineListEntry.created_at.desc())
            .all()
        )
        for le in rows:
            # Keep only the first (most recent) entry per line_number
            if le.line_number not in line_entries_by_ln:
                line_entries_by_ln[le.line_number] = le

    # Build error count lookup from aggregate subquery
    error_count_lookup: dict[str, int] = {
        str(row.iso_id): row.error_count
        for row in db.query(error_counts_q).all()
    }

    out = []
    for iso in isos:
        line_entry = line_entries_by_ln.get(iso.line_number) if iso.line_number else None
        out.append({
            "iso_id": str(iso.id),
            "line_number": iso.line_number,
            "iso_status": iso.status.value,
            "validation_status": line_entry.validation_status.value if line_entry else "no_line_list",
            "error_count": error_count_lookup.get(str(iso.id), 0),
        })
    return out


@router.get("/anomaly-report")
def anomaly_report(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Run heuristic anomaly detection across all ISO drawings and return a summary
    report with per-ISO risk scores and detected anomalies.
    """
    isos = db.query(ISODrawing).order_by(ISODrawing.created_at.desc()).all()
    line_list_entries = db.query(LineListEntry).all()
    pms_entries = db.query(PMSEntry).all()

    detector = AnomalyDetector()
    report = detector.analyze_all(isos, line_list_entries, pms_entries)
    return report
