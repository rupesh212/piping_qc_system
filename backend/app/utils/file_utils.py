import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/tiff"}
ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_EXCEL_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}

# Extension → set of allowed content-types
_EXT_TO_CONTENT_TYPES: dict[str, set[str]] = {
    ".jpg": ALLOWED_IMAGE_TYPES,
    ".jpeg": ALLOWED_IMAGE_TYPES,
    ".png": ALLOWED_IMAGE_TYPES,
    ".tif": ALLOWED_IMAGE_TYPES,
    ".tiff": ALLOWED_IMAGE_TYPES,
    ".pdf": ALLOWED_PDF_TYPES,
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    ".xls": {"application/vnd.ms-excel"},
}

# Magic-byte signatures: (offset, bytes)
_MAGIC_SIGNATURES: list[tuple[int, bytes, set[str]]] = [
    (0, b"\xff\xd8\xff", ALLOWED_IMAGE_TYPES),                      # JPEG
    (0, b"\x89PNG\r\n\x1a\n", ALLOWED_IMAGE_TYPES),                 # PNG
    (0, b"II\x2a\x00", ALLOWED_IMAGE_TYPES),                        # TIFF little-endian
    (0, b"MM\x00\x2a", ALLOWED_IMAGE_TYPES),                        # TIFF big-endian
    (0, b"%PDF-", ALLOWED_PDF_TYPES),                               # PDF
    (0, b"PK\x03\x04", {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}),  # xlsx (ZIP)
    (0, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", {"application/vnd.ms-excel"}),  # xls (OLE2)
]

_PEEK_SIZE = 16


def _detect_magic(header: bytes) -> set[str]:
    """Return the set of allowed content-types that match the file's magic bytes."""
    for offset, magic, types in _MAGIC_SIGNATURES:
        end = offset + len(magic)
        if len(header) >= end and header[offset:end] == magic:
            return types
    return set()


def save_upload_file(upload_file: UploadFile, subfolder: str) -> str:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    dest_dir = Path(settings.UPLOAD_DIR) / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(upload_file.filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    dest_path = dest_dir / unique_name

    size = 0
    with open(dest_path, "wb") as f:
        for chunk in iter(lambda: upload_file.file.read(1024 * 1024), b""):
            size += len(chunk)
            if size > max_bytes:
                f.close()
                os.remove(dest_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB} MB.",
                )
            f.write(chunk)

    return str(dest_path)


def validate_file_type(upload_file: UploadFile, allowed_types: set[str]) -> None:
    # 1. Check client-supplied content-type
    if upload_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{upload_file.content_type}'. Allowed: {allowed_types}",
        )

    # 2. Validate file extension is consistent with content-type
    ext = Path(upload_file.filename or "").suffix.lower()
    allowed_for_ext = _EXT_TO_CONTENT_TYPES.get(ext, set())
    if allowed_for_ext and upload_file.content_type not in allowed_for_ext:
        raise HTTPException(
            status_code=415,
            detail=(
                f"File extension '{ext}' is inconsistent with "
                f"content type '{upload_file.content_type}'."
            ),
        )

    # 3. Inspect magic bytes (read peek, then seek back)
    header = upload_file.file.read(_PEEK_SIZE)
    upload_file.file.seek(0)
    if header:
        detected = _detect_magic(header)
        if detected and upload_file.content_type not in detected:
            raise HTTPException(
                status_code=415,
                detail=(
                    f"File content does not match declared type "
                    f"'{upload_file.content_type}'."
                ),
            )
