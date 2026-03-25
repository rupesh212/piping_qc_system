"""
OCR service: extracts structured piping data from ISO drawings (PDF or image).
Uses pdf2image + pytesseract for text extraction, then applies regex patterns
to pull out line_number, pipe_size, spec, and weld_count.
"""
import re
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def _extract_text_from_pdf(file_path: str) -> str:
    images = convert_from_path(file_path, dpi=200)
    texts = []
    for img in images:
        texts.append(pytesseract.image_to_string(img))
    return "\n".join(texts)


def _extract_text_from_image(file_path: str) -> str:
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)


def extract_text(file_path: str) -> str:
    if not OCR_AVAILABLE:
        return ""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return _extract_text_from_pdf(file_path)
    return _extract_text_from_image(file_path)


def _find_first(pattern: str, text: str, flags: int = re.IGNORECASE) -> Optional[str]:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def parse_iso_data(raw_text: str) -> dict:
    """
    Attempt to extract piping-specific fields from raw OCR text.

    Expected patterns in piping ISO title blocks:
      LINE NO:  2"-PW-1001-A1A
      SIZE:     2" / 2 INCH / DN50
      SPEC:     A1A / P1B
      WELDS:    12 / WELD COUNT: 12
    """
    line_number = (
        _find_first(r"LINE\s*(?:NO|NUMBER|NUM)[:\s]+([A-Z0-9\-\"'./]+)", raw_text)
        or _find_first(r"\b(\d+\"-[A-Z]{2,4}-\d{4,}-[A-Z0-9]+)\b", raw_text)
    )

    pipe_size = (
        _find_first(r"SIZE[:\s]+([0-9]+(?:\.[0-9]+)?\"?(?:\s*INCH)?(?:\s*DN\d+)?)", raw_text)
        or _find_first(r"\b(DN\s*\d+|\d+(?:\.\d+)?\s*\")\b", raw_text)
    )

    spec = (
        _find_first(r"SPEC(?:IFICATION)?[:\s]+([A-Z0-9]{2,10})", raw_text)
        or _find_first(r"PIPING\s+CLASS[:\s]+([A-Z0-9]{2,10})", raw_text)
    )

    weld_count_str = (
        _find_first(r"WELD\s+(?:COUNT|NO|QTY)[:\s]+(\d+)", raw_text)
        or _find_first(r"(?:TOTAL\s+)?WELDS?[:\s]+(\d+)", raw_text)
    )
    weld_count = int(weld_count_str) if weld_count_str and weld_count_str.isdigit() else None

    return {
        "line_number": line_number,
        "pipe_size": pipe_size,
        "spec": spec,
        "weld_count": weld_count,
    }
