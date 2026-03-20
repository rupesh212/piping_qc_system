"""
Excel parsing service for Line List and PMS uploads.
Handles flexible header detection and data normalization.
"""
from typing import Any

import pandas as pd


def _normalize_col(col: str) -> str:
    return str(col).strip().lower().replace(" ", "_").replace("-", "_")


def parse_line_list(file_path: str) -> list[dict[str, Any]]:
    """
    Parse a Line List Excel file.
    Expected columns (case-insensitive):
      Line Number / Line No
      Size / Pipe Size
      Spec / Piping Class
      From / From Equipment
      To / To Equipment
      Fluid / Service
    """
    df = pd.read_excel(file_path, engine="openpyxl")
    df.columns = [_normalize_col(c) for c in df.columns]
    df = df.dropna(how="all")

    # Column mapping — flexible header resolution
    col_map = {
        "line_number": ["line_number", "line_no", "line"],
        "pipe_size": ["pipe_size", "size", "nominal_size", "pipe_size_inch"],
        "spec": ["spec", "piping_class", "piping_spec", "specification"],
        "from_equipment": ["from_equipment", "from", "from_node"],
        "to_equipment": ["to_equipment", "to", "to_node"],
        "fluid": ["fluid", "service", "medium"],
    }

    def resolve(key: str, columns: list[str]) -> str | None:
        for candidate in col_map[key]:
            if candidate in columns:
                return candidate
        return None

    cols = list(df.columns)
    mapping = {key: resolve(key, cols) for key in col_map}

    entries = []
    for _, row in df.iterrows():
        line_number = str(row[mapping["line_number"]]).strip() if mapping["line_number"] else ""
        pipe_size = str(row[mapping["pipe_size"]]).strip() if mapping["pipe_size"] else ""
        spec = str(row[mapping["spec"]]).strip() if mapping["spec"] else ""

        # Skip empty or header rows
        if not line_number or line_number.lower() in ("nan", "line number", "line no"):
            continue

        entry = {
            "line_number": line_number,
            "pipe_size": pipe_size,
            "spec": spec,
            "from_equipment": str(row[mapping["from_equipment"]]).strip() if mapping["from_equipment"] else None,
            "to_equipment": str(row[mapping["to_equipment"]]).strip() if mapping["to_equipment"] else None,
            "fluid": str(row[mapping["fluid"]]).strip() if mapping["fluid"] else None,
        }
        # Normalize "nan" strings
        for k, v in entry.items():
            if v == "nan":
                entry[k] = None
        entries.append(entry)

    return entries


def parse_pms(file_path: str) -> list[dict[str, Any]]:
    """
    Parse a PMS (Piping Material Specification) Excel file.
    Expected columns (case-insensitive):
      Spec / Spec Code / Piping Class
      Material
      Rating / Pressure Rating
      Size Range
      End Connection / End Conn
    """
    df = pd.read_excel(file_path, engine="openpyxl")
    df.columns = [_normalize_col(c) for c in df.columns]
    df = df.dropna(how="all")

    col_map = {
        "spec_code": ["spec_code", "spec", "piping_class", "class"],
        "material": ["material", "material_desc", "pipe_material"],
        "rating": ["rating", "pressure_rating", "class_rating"],
        "size_range": ["size_range", "size", "nominal_size"],
        "end_conn": ["end_conn", "end_connection", "connection_type"],
    }

    cols = list(df.columns)

    def resolve(key: str) -> str | None:
        for candidate in col_map[key]:
            if candidate in cols:
                return candidate
        return None

    mapping = {key: resolve(key) for key in col_map}

    entries = []
    for _, row in df.iterrows():
        spec_code = str(row[mapping["spec_code"]]).strip() if mapping["spec_code"] else ""
        material = str(row[mapping["material"]]).strip() if mapping["material"] else ""
        rating = str(row[mapping["rating"]]).strip() if mapping["rating"] else ""

        if not spec_code or spec_code.lower() in ("nan", "spec", "spec code"):
            continue

        entry = {
            "spec_code": spec_code,
            "material": material if material != "nan" else "",
            "rating": rating if rating != "nan" else "",
            "size_range": str(row[mapping["size_range"]]).strip() if mapping["size_range"] else None,
            "end_conn": str(row[mapping["end_conn"]]).strip() if mapping["end_conn"] else None,
        }
        for k, v in entry.items():
            if v == "nan":
                entry[k] = None
        entries.append(entry)

    return entries
