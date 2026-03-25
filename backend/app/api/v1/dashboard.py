from fastapi import APIRouter, Depends
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
    results = (
        db.query(ValidationResult)
        .filter(ValidationResult.result == RuleResult.fail.value)
        .order_by(ValidationResult.created_at.desc())
        .limit(limit)
        .all()
    )

    out = []
    for r in results:
        iso = db.query(ISODrawing).filter(ISODrawing.id == r.iso_id).first()
        out.append({
            "id": str(r.id),
            "iso_id": str(r.iso_id),
            "line_number": iso.line_number if iso else None,
            "rule_name": r.rule_name,
            "message": r.message,
            "created_at": r.created_at.isoformat(),
        })
    return out


@router.get("/line-status")
def line_status(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    isos = db.query(ISODrawing).order_by(ISODrawing.created_at.desc()).limit(100).all()
    out = []
    for iso in isos:
        error_count = (
            db.query(ValidationResult)
            .filter(
                ValidationResult.iso_id == iso.id,
                ValidationResult.result == RuleResult.fail.value,
            )
            .count()
        )
        line_entry = None
        if iso.line_number:
            line_entry = (
                db.query(LineListEntry)
                .filter(LineListEntry.line_number == iso.line_number)
                .first()
            )
        out.append({
            "iso_id": str(iso.id),
            "line_number": iso.line_number,
            "iso_status": iso.status.value,
            "validation_status": line_entry.validation_status.value if line_entry else "no_line_list",
            "error_count": error_count,
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
