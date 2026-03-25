"""
AI Anomaly Detection Service: uses rule-based heuristics to detect anomalies
in piping QA/QC data without requiring external ML libraries.
"""
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.iso import ISODrawing
from app.models.line_list import LineListEntry
from app.models.pms import PMSEntry


class AnomalyDetector:
    """
    Detects anomalies in piping ISO, Line List, and PMS data using
    deterministic heuristic rules.
    """

    def analyze_iso(
        self,
        iso_drawing: ISODrawing,
        line_list_entries: list,
        pms_entries: list,
    ) -> dict:
        """
        Detect anomalies for a single ISO drawing.

        Heuristics applied:
        1. Weld count anomaly   — weld_count > 2 * average weld_count for same spec
        2. Spec mismatch pattern — same line_number appears with different specs across line list entries
        3. Missing critical fields — spec or pipe_size is empty/None on the ISO
        4. PMS coverage gap — spec from ISO not found in any provided PMS entry

        Returns:
            {
                "anomalies": [{"type": str, "severity": "high/medium/low", "message": str}],
                "risk_score": float (0-100),
                "recommendation": str,
            }
        """
        anomalies: list[dict[str, str]] = []

        # --- Heuristic 1: Weld count anomaly ---
        if iso_drawing.weld_count is not None and iso_drawing.spec:
            same_spec_isos = [
                ll for ll in line_list_entries
                if hasattr(ll, "spec") and ll.spec and ll.spec.strip().upper() == iso_drawing.spec.strip().upper()
            ]
            # Gather weld counts from the ISO drawing itself and any ISOs with same spec
            # We only have the current iso here, so use pms_entries as a proxy for
            # "known entries". For the weld count we use the iso's own value compared
            # to a simple threshold derived from the line list count.
            # A more realistic implementation would compare across all ISOs; the
            # service is intentionally self-contained per-ISO call, so we use a
            # configurable multiplier check instead.
            spec_weld_counts = [
                iso_drawing.weld_count
            ]
            # Also look for any numeric weld_count hints stored in pms size_range
            # (not applicable here — just use the direct list)
            if len(spec_weld_counts) > 0:
                avg = sum(spec_weld_counts) / len(spec_weld_counts)
                # Flag if this ISO's weld count is more than 2x the average of its peers.
                # Since we only have one value, escalate if it exceeds a hard ceiling of 100
                # welds (a common industry threshold for complex spools).
                HARD_CEILING = 100
                if iso_drawing.weld_count > HARD_CEILING:
                    anomalies.append({
                        "type": "weld_count_anomaly",
                        "severity": "high",
                        "message": (
                            f"ISO '{iso_drawing.file_name}' has {iso_drawing.weld_count} welds, "
                            f"which exceeds the high-complexity threshold of {HARD_CEILING}."
                        ),
                    })
                elif iso_drawing.weld_count > HARD_CEILING * 0.5:
                    anomalies.append({
                        "type": "weld_count_anomaly",
                        "severity": "medium",
                        "message": (
                            f"ISO '{iso_drawing.file_name}' has {iso_drawing.weld_count} welds, "
                            f"which is elevated (>{HARD_CEILING * 0.5})."
                        ),
                    })

        # --- Heuristic 2: Spec mismatch pattern ---
        # Check whether the same line_number appears with different specs in line_list_entries
        if iso_drawing.line_number and line_list_entries:
            matching_ll = [
                ll for ll in line_list_entries
                if ll.line_number == iso_drawing.line_number
            ]
            specs_seen = {ll.spec.strip().upper() for ll in matching_ll if ll.spec}
            if len(specs_seen) > 1:
                anomalies.append({
                    "type": "spec_mismatch_pattern",
                    "severity": "high",
                    "message": (
                        f"Line number '{iso_drawing.line_number}' appears with multiple "
                        f"different specs across batches: {sorted(specs_seen)}."
                    ),
                })
            elif specs_seen and iso_drawing.spec:
                iso_spec_norm = iso_drawing.spec.strip().upper()
                if iso_spec_norm not in specs_seen:
                    anomalies.append({
                        "type": "spec_mismatch_pattern",
                        "severity": "high",
                        "message": (
                            f"ISO spec '{iso_drawing.spec}' does not match any Line List spec "
                            f"for line number '{iso_drawing.line_number}': {sorted(specs_seen)}."
                        ),
                    })

        # --- Heuristic 3: Missing critical fields ---
        missing: list[str] = []
        if not iso_drawing.spec or not iso_drawing.spec.strip():
            missing.append("spec")
        if not iso_drawing.pipe_size or not iso_drawing.pipe_size.strip():
            missing.append("pipe_size")
        if missing:
            severity = "high" if len(missing) > 1 else "medium"
            anomalies.append({
                "type": "missing_critical_fields",
                "severity": severity,
                "message": (
                    f"ISO '{iso_drawing.file_name}' is missing critical field(s): "
                    f"{', '.join(missing)}."
                ),
            })

        # --- Heuristic 4: PMS coverage gap ---
        iso_spec = iso_drawing.spec.strip().upper() if iso_drawing.spec else None
        if iso_spec:
            pms_spec_codes = {
                e.spec_code.strip().upper() for e in pms_entries if e.spec_code
            }
            if iso_spec not in pms_spec_codes:
                anomalies.append({
                    "type": "pms_coverage_gap",
                    "severity": "high",
                    "message": (
                        f"Spec '{iso_drawing.spec}' from ISO '{iso_drawing.file_name}' "
                        f"is not covered by any PMS entry."
                    ),
                })
        else:
            # No spec to look up — already flagged in heuristic 3 if missing
            pass

        # --- Compute risk score (0–100) ---
        severity_weights = {"high": 30, "medium": 15, "low": 5}
        raw_score = sum(severity_weights.get(a["severity"], 5) for a in anomalies)
        risk_score = min(100.0, float(raw_score))

        # --- Recommendation ---
        if risk_score >= 60:
            recommendation = (
                "High risk detected. Immediately review all flagged anomalies before "
                "proceeding with fabrication or installation."
            )
        elif risk_score >= 30:
            recommendation = (
                "Moderate risk detected. Investigate flagged items and resolve spec or "
                "field discrepancies prior to sign-off."
            )
        elif risk_score > 0:
            recommendation = (
                "Low risk. Minor issues detected — verify and document resolutions."
            )
        else:
            recommendation = "No anomalies detected. ISO data appears consistent."

        return {
            "anomalies": anomalies,
            "risk_score": risk_score,
            "recommendation": recommendation,
        }

    def analyze_all(
        self,
        isos: list,
        line_list_entries: list,
        pms_entries: list,
    ) -> dict:
        """
        Run anomaly detection across a collection of ISO drawings.

        Additionally checks for a cross-ISO weld count anomaly: flags any ISO
        whose weld_count exceeds 2x the average weld_count of all ISOs that share
        the same spec.

        Returns:
            {
                "total_isos_analysed": int,
                "total_anomalies": int,
                "high_risk_isos": int,
                "results": [per-ISO result dicts with iso_id and file_name added],
                "overall_risk_score": float,
                "summary": str,
            }
        """
        # Build spec -> list of weld counts map for cross-ISO heuristic 1
        spec_weld_map: dict[str, list[int]] = {}
        for iso in isos:
            if iso.spec and iso.weld_count is not None:
                key = iso.spec.strip().upper()
                spec_weld_map.setdefault(key, []).append(iso.weld_count)

        results = []
        for iso in isos:
            per_iso = self.analyze_iso(iso, line_list_entries, pms_entries)

            # Augment heuristic 1 with cross-ISO average if we have peers
            if iso.spec and iso.weld_count is not None:
                key = iso.spec.strip().upper()
                peers = spec_weld_map.get(key, [])
                if len(peers) > 1:
                    avg_weld = sum(peers) / len(peers)
                    if iso.weld_count > 2 * avg_weld:
                        cross_anomaly = {
                            "type": "weld_count_anomaly",
                            "severity": "high",
                            "message": (
                                f"ISO '{iso.file_name}' weld count {iso.weld_count} is more than "
                                f"2x the average ({avg_weld:.1f}) for spec '{iso.spec}'."
                            ),
                        }
                        # Only add if not already flagged by the same type
                        existing_types = {a["type"] for a in per_iso["anomalies"]}
                        if "weld_count_anomaly" not in existing_types:
                            per_iso["anomalies"].append(cross_anomaly)
                            # Recompute risk score
                            severity_weights = {"high": 30, "medium": 15, "low": 5}
                            raw = sum(
                                severity_weights.get(a["severity"], 5)
                                for a in per_iso["anomalies"]
                            )
                            per_iso["risk_score"] = min(100.0, float(raw))

            per_iso["iso_id"] = str(iso.id)
            per_iso["file_name"] = iso.file_name
            results.append(per_iso)

        total_anomalies = sum(len(r["anomalies"]) for r in results)
        high_risk_count = sum(1 for r in results if r["risk_score"] >= 60)
        overall_risk = (
            sum(r["risk_score"] for r in results) / len(results) if results else 0.0
        )

        if overall_risk >= 60:
            summary = "System-wide high risk. Immediate review required across multiple ISOs."
        elif overall_risk >= 30:
            summary = "Moderate system risk. Several ISOs require attention before sign-off."
        elif overall_risk > 0:
            summary = "Low system risk. Spot-check flagged ISOs."
        else:
            summary = "No anomalies detected across all ISOs."

        return {
            "total_isos_analysed": len(isos),
            "total_anomalies": total_anomalies,
            "high_risk_isos": high_risk_count,
            "results": results,
            "overall_risk_score": round(overall_risk, 2),
            "summary": summary,
        }
