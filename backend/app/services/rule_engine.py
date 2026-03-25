"""
Rule Engine: applies validation rules against ISO drawing data,
Line List entries, and PMS entries.

Each rule returns a list of ValidationResult-compatible dicts.
"""
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.iso import ISODrawing
from app.models.line_list import LineListEntry, ValidationStatus
from app.models.pms import PMSEntry, PMSValidationStatus
from app.models.validation import ValidationResult, RuleResult


def _make_result(iso_id, rule_name: str, result: str, message: str,
                 line_list_id=None, pms_id=None) -> dict:
    return {
        "iso_id": iso_id,
        "line_list_id": line_list_id,
        "pms_id": pms_id,
        "rule_name": rule_name,
        "result": result,
        "message": message,
    }


def run_validation(iso: ISODrawing, db: Session) -> list[dict[str, Any]]:
    """
    Run all validation rules for the given ISO drawing.
    Returns a list of result dicts ready to be stored.
    """
    results = []

    # Find matching line list entry by line number
    line_entry: LineListEntry | None = None
    if iso.line_number:
        line_entry = (
            db.query(LineListEntry)
            .filter(LineListEntry.line_number == iso.line_number)
            .order_by(LineListEntry.created_at.desc())
            .first()
        )

    # --- Rule 1: spec_match ---
    if line_entry:
        if iso.spec and line_entry.spec:
            if iso.spec.strip().upper() == line_entry.spec.strip().upper():
                results.append(_make_result(
                    iso.id, "spec_match", RuleResult.pass_.value,
                    f"Spec '{iso.spec}' matches Line List spec.",
                    line_list_id=line_entry.id,
                ))
            else:
                results.append(_make_result(
                    iso.id, "spec_match", RuleResult.fail.value,
                    f"Spec mismatch: ISO='{iso.spec}' vs LineList='{line_entry.spec}'.",
                    line_list_id=line_entry.id,
                ))
        else:
            results.append(_make_result(
                iso.id, "spec_match", RuleResult.warning.value,
                "Spec missing in ISO or Line List — cannot compare.",
                line_list_id=line_entry.id,
            ))
    else:
        results.append(_make_result(
            iso.id, "spec_match", RuleResult.warning.value,
            f"No Line List entry found for line number '{iso.line_number}'.",
        ))

    # --- Rule 2: size_match ---
    if line_entry:
        if iso.pipe_size and line_entry.pipe_size:
            iso_size = _normalize_size(iso.pipe_size)
            ll_size = _normalize_size(line_entry.pipe_size)
            if iso_size == ll_size:
                results.append(_make_result(
                    iso.id, "size_match", RuleResult.pass_.value,
                    f"Pipe size '{iso.pipe_size}' matches Line List.",
                    line_list_id=line_entry.id,
                ))
            else:
                results.append(_make_result(
                    iso.id, "size_match", RuleResult.fail.value,
                    f"Size mismatch: ISO='{iso.pipe_size}' vs LineList='{line_entry.pipe_size}'.",
                    line_list_id=line_entry.id,
                ))
        else:
            results.append(_make_result(
                iso.id, "size_match", RuleResult.warning.value,
                "Pipe size missing in ISO or Line List — cannot compare.",
                line_list_id=line_entry.id,
            ))
    else:
        results.append(_make_result(
            iso.id, "size_match", RuleResult.warning.value,
            f"No Line List entry found for line number '{iso.line_number}' — cannot compare size.",
        ))

    # --- Rule 3: pms_spec_exists ---
    spec_to_check = (line_entry.spec if line_entry else None) or iso.spec
    pms_entry: PMSEntry | None = None
    if spec_to_check:
        pms_entry = (
            db.query(PMSEntry)
            .filter(PMSEntry.spec_code == spec_to_check.strip().upper())
            .order_by(PMSEntry.created_at.desc())
            .first()
        )
        if pms_entry:
            results.append(_make_result(
                iso.id, "pms_spec_exists", RuleResult.pass_.value,
                f"Spec '{spec_to_check}' found in PMS.",
                line_list_id=line_entry.id if line_entry else None,
                pms_id=pms_entry.id,
            ))
        else:
            results.append(_make_result(
                iso.id, "pms_spec_exists", RuleResult.fail.value,
                f"Spec '{spec_to_check}' NOT found in PMS.",
                line_list_id=line_entry.id if line_entry else None,
            ))
    else:
        results.append(_make_result(
            iso.id, "pms_spec_exists", RuleResult.warning.value,
            "No spec available to check against PMS.",
        ))

    # --- Rule 4: pms_material_valid ---
    if pms_entry:
        if pms_entry.material and pms_entry.material.strip():
            results.append(_make_result(
                iso.id, "pms_material_valid", RuleResult.pass_.value,
                f"PMS material '{pms_entry.material}' is valid for spec '{spec_to_check}'.",
                line_list_id=line_entry.id if line_entry else None,
                pms_id=pms_entry.id,
            ))
        else:
            results.append(_make_result(
                iso.id, "pms_material_valid", RuleResult.fail.value,
                f"PMS material is empty for spec '{spec_to_check}'.",
                pms_id=pms_entry.id,
            ))

    # --- Rule 5: pms_rating_check ---
    if pms_entry:
        if pms_entry.rating and pms_entry.rating.strip():
            results.append(_make_result(
                iso.id, "pms_rating_check", RuleResult.pass_.value,
                f"PMS rating '{pms_entry.rating}' is defined for spec '{spec_to_check}'.",
                line_list_id=line_entry.id if line_entry else None,
                pms_id=pms_entry.id,
            ))
        else:
            results.append(_make_result(
                iso.id, "pms_rating_check", RuleResult.fail.value,
                f"PMS rating is empty for spec '{spec_to_check}'.",
                pms_id=pms_entry.id,
            ))

    # Update line_entry validation status based on results
    if line_entry:
        has_fail = any(r["result"] == RuleResult.fail.value for r in results)
        line_entry.validation_status = ValidationStatus.mismatch if has_fail else ValidationStatus.valid
        if has_fail:
            line_entry.mismatch_fields = [
                r["rule_name"] for r in results if r["result"] == RuleResult.fail.value
            ]
        else:
            line_entry.mismatch_fields = []
        db.add(line_entry)

    return results


def _normalize_size(size: str) -> str:
    """Normalize pipe size strings for comparison (strip quotes, spaces, lowercase)."""
    return size.strip().lower().replace('"', '').replace("'", "").replace(" ", "")
